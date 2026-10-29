"""Simulación de una señal sobre ticks bid/ask.

Reglas de ejecución (conservadoras, con el lado correcto del spread):
- SELL: se llena cuando el bid entra a la zona (bid >= entry_low); el stop salta
  cuando el ask >= SL; un TP se toca cuando el ask <= TP.
- BUY: se llena cuando el ask entra a la zona (ask <= entry_high); el stop salta
  cuando el bid <= SL; un TP se toca cuando el bid >= TP.
- Si en el primer tick el precio ya está más allá del stop, la señal se
  considera invalidada antes de llenarse.
- Señales sin hora conocida (time_basis = date_only) arrancan a las 00:00 UTC
  y usan una regla de aproximación: solo se llenan cuando el precio llega a la
  zona viniendo del lado favorable (desde el nivel de TP1 o más allá: por
  debajo para SELL, por encima para BUY), y la ventana de llenado es todo el
  horizonte. Evita llenar o invalidar con un
  precio que ya estaba en la zona antes de que la señal existiera.

Se evalúan tres manejos sobre la misma secuencia de ticks:
- no_be: sin mover el stop; cierra en SL o en el último TP.
- be_after_min: a los N minutos del llenado (lo que hace el canal, ~10 min),
  si el trade sigue abierto el stop pasa al precio de entrada.
- be_after_tp1: al tocar TP1 el stop pasa al precio de entrada.

Para cada manejo se reporta R con posición completa y R "en tercios" (un
tercio cerrado en cada TP, el resto al stop vigente).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable

from .dukascopy import Tick
from .signals import Signal


@dataclass
class PathResult:
    name: str
    outcome: str  # SL | BE | TP1 | TP2 | TP3 | open
    exit_time: datetime | None
    exit_price: float | None
    r_full: float | None
    r_thirds: float | None


@dataclass
class SimResult:
    signal: Signal
    status: str  # filled | not_filled | invalidated | no_data
    fill_time: datetime | None = None
    fill_price: float | None = None
    risk: float | None = None
    tp_times: list[datetime | None] = field(default_factory=list)
    sl_time: datetime | None = None
    first_event: str = ""
    mfe_r: float | None = None
    mae_r: float | None = None
    last_tick: datetime | None = None
    open_r: float | None = None
    paths: dict[str, PathResult] = field(default_factory=dict)
    note: str = ""


def _r(signal: Signal, fill: float, risk: float, price: float) -> float:
    pnl = (fill - price) if signal.direction == "SELL" else (price - fill)
    return pnl / risk


def simulate(signal: Signal, ticks: Iterable[Tick], *, fill_window: timedelta = timedelta(hours=4),
             horizon: timedelta = timedelta(hours=24), be_after: timedelta = timedelta(minutes=10)) -> SimResult:
    res = SimResult(signal=signal, status="no_data")
    sell = signal.direction == "SELL"
    needs_approach = signal.time_basis == "date_only"
    armed = not needs_approach  # con hora conocida el precio puede estar ya en la zona
    deadline_fill = signal.start_utc + (horizon if needs_approach else fill_window)
    deadline = signal.start_utc + horizon
    fill: float | None = None
    fill_t: datetime | None = None
    risk = 0.0
    n_tp = len(signal.tps)
    tp_times: list[datetime | None] = [None] * n_tp
    sl_time: datetime | None = None
    mfe = 0.0
    mae = 0.0
    first_event = ""
    # estado de cada manejo: (stop vigente, cerrado?, outcome, exit_t, exit_px, partes cerradas)
    paths = {
        "no_be": {"stop": signal.stop_loss, "done": False, "out": "", "t": None, "px": None, "thirds": []},
        "be_after_min": {"stop": signal.stop_loss, "done": False, "out": "", "t": None, "px": None, "thirds": []},
        "be_after_tp1": {"stop": signal.stop_loss, "done": False, "out": "", "t": None, "px": None, "thirds": []},
    }
    tps_hit = 0
    last_t: datetime | None = None
    last_px: float | None = None

    for tk in ticks:
        if tk.ts >= deadline:
            break
        last_t = tk.ts
        if fill is None:
            if tk.ts >= deadline_fill:
                res.status = "not_filled"
                res.last_tick = last_t
                return res
            entry_side = tk.bid if sell else tk.ask
            if not armed:
                # viene del lado favorable: al menos hasta el nivel de TP1 (un oscilar en el
                # borde de la zona a medianoche no cuenta como aproximación)
                armed = entry_side <= signal.tps[0] if sell else entry_side >= signal.tps[0]
                continue
            beyond_stop = entry_side >= signal.stop_loss if sell else entry_side <= signal.stop_loss
            in_zone = entry_side >= signal.entry_low if sell else entry_side <= signal.entry_high
            if beyond_stop:
                res.status = "invalidated"
                res.note = "precio más allá del stop antes de llenarse (%.2f)" % entry_side
                res.last_tick = last_t
                return res
            if in_zone:
                fill, fill_t = entry_side, tk.ts
                risk = abs(fill - signal.stop_loss)
                if risk <= 0:
                    res.status = "invalidated"
                    res.note = "riesgo cero al llenar"
                    return res
            continue

        exit_side = tk.ask if sell else tk.bid  # precio al que se cierra la posición
        last_px = exit_side
        r_now = _r(signal, fill, risk, exit_side)
        mfe, mae = max(mfe, r_now), min(mae, r_now)

        hit_stop_orig = exit_side >= signal.stop_loss if sell else exit_side <= signal.stop_loss
        if hit_stop_orig and sl_time is None:
            sl_time = tk.ts
            first_event = first_event or "SL"
        while tps_hit < n_tp and ((exit_side <= signal.tps[tps_hit]) if sell else (exit_side >= signal.tps[tps_hit])):
            tp_times[tps_hit] = tk.ts
            first_event = first_event or "TP1"
            tps_hit += 1
            if tps_hit == 1:
                paths["be_after_tp1"]["stop"] = fill
        if paths["be_after_min"]["stop"] == signal.stop_loss and tk.ts - fill_t >= be_after:
            paths["be_after_min"]["stop"] = fill

        for name, p in paths.items():
            if p["done"]:
                continue
            stop = p["stop"]
            hit_stop = exit_side >= stop if sell else exit_side <= stop
            # TPs tocados en este tick cierran tercios antes de evaluar el stop
            while len(p["thirds"]) < tps_hit:
                p["thirds"].append(_r(signal, fill, risk, signal.tps[len(p["thirds"])]))
            if tps_hit == n_tp:
                p.update(done=True, out="TP%d" % n_tp, t=tk.ts, px=signal.tps[-1])
            elif hit_stop:
                out = "BE" if stop == fill else "SL"
                p.update(done=True, out=out, t=tk.ts, px=stop)
        if all(p["done"] for p in paths.values()):
            break

    if fill is None:
        res.status = "no_data" if last_t is None else "not_filled"
        res.last_tick = last_t
        return res

    res.status = "filled"
    res.fill_time, res.fill_price, res.risk = fill_t, fill, risk
    res.tp_times, res.sl_time, res.first_event = tp_times, sl_time, first_event
    res.mfe_r, res.mae_r, res.last_tick = round(mfe, 3), round(mae, 3), last_t
    res.open_r = round(_r(signal, fill, risk, last_px), 3) if last_px is not None else None
    for name, p in paths.items():
        if p["done"]:
            r_full = _r(signal, fill, risk, p["px"])
            closed = list(p["thirds"])
            rest = n_tp - len(closed)
            r_thirds = (sum(closed) + rest * r_full) / n_tp if n_tp else r_full
            res.paths[name] = PathResult(name, p["out"], p["t"], p["px"], round(r_full, 3), round(r_thirds, 3))
        else:
            res.paths[name] = PathResult(name, "open", None, None, None, None)
    return res
