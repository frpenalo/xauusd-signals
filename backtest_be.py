"""Manejo «stop a entrada a los N minutos» medido con precios de salida reales y costos.

Hasta el 17-nov-2026 verifier/sim.py cerraba el manejo be_after_min al precio de entrada
exacto (hoy ya usa la regla be_ok de abajo). Eso regalaba dos cosas que en una cuenta
real no existen:
- si a los N minutos la operación va perdiendo, el stop «en entrada» quedaría del lado
  equivocado del mercado y no se puede poner; el simulador la cierra igual en 0R;
- un stop es una orden a mercado: sale al precio del tick que lo dispara, no al nivel.

Aquí se miden, sobre las mismas señales de backtest_years.py (variantes momentum, puntos
fijos y escalados a la volatilidad), tres manejos con posición completa:
- nobe: sin mover el stop. Sale en TP3 (orden límite, al nivel) o en el stop (al precio
  del tick que lo dispara).
- be_ok: desde el minuto N, en cuanto la operación está en ganancia el stop pasa a la
  entrada; mientras vaya perdiendo sigue el stop original. Es lo que se puede hacer de verdad.
- be_mkt: igual, pero si en el minuto N va perdiendo se cierra a mercado. Son las mismas
  decisiones que tomaba el simulador viejo, con el precio real de salida.

Las que siguen abiertas a las 24 h se cierran al último precio. El costo extra (comisión
o un spread peor que el de Dukascopy) se aplica ensanchando el spread de cada tick, así
que también retrasa las entradas y adelanta los stops.

Antes de creerle, el reporte incluye una sección de control: con costo 0 y las reglas del
simulador viejo (las claves leg_*) debe dar los mismos números que reports/backtest_3y.md.

Uso:
    python backtest_be.py --candles data/candles/XAUUSD_1m_3y.csv \
        --periods 2023-11-13:2024-11-12,2024-11-13:2025-11-12,2025-11-13:2026-05-10,2026-05-11:2026-11-06 \
        --reference 2026-05-11:2026-11-06
"""
from __future__ import annotations

import argparse
import csv
import ctypes
import itertools
import lzma
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np

import backtest as bt
from backtest_years import LIVE, adr_before, daily_ranges
from verifier.dukascopy import fetch_hour
from verifier.signals import Signal

TICK_DTYPE = np.dtype([("ms", ">u4"), ("ask", ">u4"), ("bid", ">u4"), ("av", ">f4"), ("bv", ">f4")])
FILL_MS = int(bt.FILL_WINDOW.total_seconds() * 1000)
LEGACY_BE_MIN = 10  # el be_after de verifier/sim.py, para la sección de control


def load_ticks(start: datetime, end: datetime, root: Path = bt.TICKS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ticks de [start, end) como arreglos (ms desde época, bid, ask)."""
    ts, bids, asks = [], [], []
    hour = start.replace(minute=0, second=0, microsecond=0)
    while hour < end:
        raw = fetch_hour("XAUUSD", hour, root)
        if raw:
            data = lzma.decompress(raw)
            a = np.frombuffer(data[:len(data) - len(data) % TICK_DTYPE.itemsize], dtype=TICK_DTYPE)
            ts.append(int(hour.timestamp() * 1000) + a["ms"].astype(np.int64))
            bids.append(a["bid"] / 1000.0)
            asks.append(a["ask"] / 1000.0)
        hour += timedelta(hours=1)
    if not ts:
        return np.empty(0, np.int64), np.empty(0), np.empty(0)
    t, bid, ask = np.concatenate(ts), np.concatenate(bids), np.concatenate(asks)
    keep = (t >= int(start.timestamp() * 1000)) & (t < int(end.timestamp() * 1000))
    t, bid, ask = t[keep], bid[keep], ask[keep]
    if np.any(np.diff(t) < 0):
        raise ValueError("ticks fuera de orden entre %s y %s" % (start, end))
    return t, bid, ask


def _first(mask: np.ndarray) -> int:
    """Índice del primer True, o len(mask) si no hay ninguno."""
    if mask.size == 0:
        return 0
    i = int(mask.argmax())
    return i if mask[i] else mask.size


def trade(sig: Signal, t: np.ndarray, bid: np.ndarray, ask: np.ndarray,
          be_minutes: tuple[int, ...]) -> dict[tuple[str, int], tuple[str, float]] | None:
    """Resultado (salida, R) de cada manejo, o None si la señal no se llenó.

    Mismas reglas de llenado que verifier/sim.py para señales con hora conocida.
    Claves: ("nobe", 0), ("be_ok", N), ("be_mkt", N) y, para el control contra el simulador
    viejo, ("leg_res" | "leg_open", 0) y ("leg_be", N) con salidas al nivel exacto.
    """
    sell = sig.direction == "SELL"
    entry, exit_side = (bid, ask) if sell else (ask, bid)
    n_fill = int(np.searchsorted(t, int(sig.start_utc.timestamp() * 1000) + FILL_MS))
    e = entry[:n_fill]
    i = _first(e >= sig.entry_low if sell else e <= sig.entry_high)
    if i == n_fill:
        return None
    fill = float(entry[i])
    if (fill >= sig.stop_loss) if sell else (fill <= sig.stop_loss):
        return None  # invalidada: el precio ya estaba más allá del stop
    risk = abs(fill - sig.stop_loss)
    x, tt = exit_side[i + 1:], t[i + 1:]
    n = x.size
    if n == 0:
        return None

    def r_at(price: float) -> float:
        return ((fill - price) if sell else (price - fill)) / risk

    tp3 = sig.tps[-1]
    r_tp, r_open = r_at(tp3), r_at(float(x[-1]))
    at_be = x >= fill if sell else x <= fill  # ticks en los que saltaría un stop puesto en la entrada
    i_sl = _first(x >= sig.stop_loss if sell else x <= sig.stop_loss)
    i_tp = _first(x <= tp3 if sell else x >= tp3)
    out: dict[tuple[str, int], tuple[str, float]] = {}

    if i_tp < i_sl:
        out["nobe", 0] = out["leg_res", 0] = ("TP", r_tp)
    elif i_sl < n:
        out["nobe", 0] = ("SL", r_at(float(x[i_sl])))
        out["leg_res", 0] = ("SL", -1.0)
    else:
        out["nobe", 0] = out["leg_open", 0] = ("open", r_open)

    for m in be_minutes:
        j = int(np.searchsorted(tt, int(t[i]) + m * 60_000))  # primer tick con N minutos desde el llenado
        # be_mkt y simulador viejo: desde j el stop está en la entrada, se pueda o no
        if i_sl < j:
            stop_i, stop_kind = i_sl, "SL"
        else:
            stop_i, stop_kind = j + _first(at_be[j:]), "BE"
        if i_tp < stop_i:
            out["be_mkt", m] = ("TP", r_tp)
            leg = ("TP", r_tp)
        elif stop_i < n:
            out["be_mkt", m] = (stop_kind, r_at(float(x[stop_i])))
            leg = (stop_kind, -1.0 if stop_kind == "SL" else 0.0)
        else:
            out["be_mkt", m] = ("open", r_open)
            leg = None
        if leg is not None and ("leg_res", 0) in out:
            out["leg_be", m] = leg
        # be_ok: el stop pasa a la entrada en el primer tick en ganancia desde j
        k = j + _first(~at_be[j:])
        if i_sl < k:
            stop_i, stop_kind = i_sl, "SL"
        else:
            stop_i, stop_kind = (k + 1 + _first(at_be[k + 1:]), "BE") if k < n else (n, "BE")
        if i_tp < stop_i:
            out["be_ok", m] = ("TP", r_tp)
        elif stop_i < n:
            out["be_ok", m] = (stop_kind, r_at(float(x[stop_i])))
        else:
            out["be_ok", m] = ("open", r_open)
    return out


@dataclass
class Stat:
    n: int = 0
    r: float = 0.0
    tp: int = 0
    sl: int = 0
    be: int = 0
    opened: int = 0
    peak: float = 0.0
    dd: float = 0.0

    def add(self, kind: str, r: float) -> None:
        self.n += 1
        self.r += r
        if kind == "TP":
            self.tp += 1
        elif kind == "SL":
            self.sl += 1
        elif kind == "BE":
            self.be += 1
        else:
            self.opened += 1
        self.peak = max(self.peak, self.r)
        self.dd = max(self.dd, self.peak - self.r)


MGMT = (("nobe", "Sin mover el stop"), ("be_ok", "Stop a entrada cuando se puede"),
        ("be_mkt", "Cierre a mercado si va perdiendo"))


def _cell(stats, fam, cost, be, mgmt, p, variants) -> str:
    rs = sorted(stats[fam, cost, 0 if mgmt == "nobe" else be, mgmt, p, v].r for v in variants)
    live = stats[fam, cost, 0 if mgmt == "nobe" else be, mgmt, p, LIVE]
    return "%+.1f | %d/%d | %+.1f" % (live.r, sum(r > 0 for r in rs), len(rs), rs[len(rs) // 2])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candles", type=Path, required=True)
    ap.add_argument("--periods", required=True, help="tramos inicio:fin separados por coma, en orden")
    ap.add_argument("--reference", required=True, help="periodo inicio:fin donde se eligieron los puntos")
    ap.add_argument("--costs", default="0,0.1,0.2,0.3,0.5", help="costo extra por operación, en puntos de precio")
    ap.add_argument("--be", default="5,10,20", help="minutos tras el llenado para mover el stop")
    ap.add_argument("--be-main", type=int, default=10)
    ap.add_argument("--out", type=Path, default=bt.ROOT / "reports" / "backtest_be.md")
    ap.add_argument("--trades-out", type=Path, help="CSV con el resultado diario de cada variante (para overfit_check.py)")
    args = ap.parse_args(argv)

    if sys.platform == "win32":  # que la laptop no se duerma a media corrida
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    periods = [tuple(date.fromisoformat(x) for x in p.split(":")) for p in args.periods.split(",")]
    ref_a, ref_b = (date.fromisoformat(x) for x in args.reference.split(":"))
    costs = [float(c) for c in args.costs.split(",")]
    bes = tuple(sorted({int(b) for b in args.be.split(",")} | {LEGACY_BE_MIN, args.be_main}))
    start, end = periods[0][0], periods[-1][1]
    variants = [bt.Variant("momentum", p, s, m) for p, s, m in itertools.product(bt.PULLS, bt.STOPS, bt.MIN_MOVES)]
    contexts = bt.load_day_contexts(args.candles, start, end)
    adr = adr_before(daily_ranges(args.candles))
    ref = [r for d, r in adr.items() if ref_a <= d <= ref_b]
    adr_ref = sum(ref) / len(ref)

    trades = None
    if args.trades_out:
        args.trades_out.parent.mkdir(parents=True, exist_ok=True)
        trades_file = args.trades_out.open("w", encoding="utf-8", newline="")
        trades = csv.writer(trades_file)
        trades.writerow(["day", "family", "cost", "variant", "side", "nobe_kind", "nobe_r", "be_kind", "be_r"])

    stats: dict[tuple, Stat] = defaultdict(Stat)
    days = [0] * len(periods)
    spreads: list[list[float]] = [[] for _ in periods]
    risks: dict[str, list[list[float]]] = {k: [[] for _ in periods] for k in ("fijo", "escalado")}
    print("%d días, %d variantes momentum, costos %s, minutos %s" % (len(contexts), len(variants), costs, bes), flush=True)

    for row, ctx in enumerate(contexts, start=1):
        idx = next((k for k, (a, b) in enumerate(periods) if a <= ctx.day <= b), None)
        if idx is None or ctx.day not in adr:
            continue
        f = adr[ctx.day] / adr_ref
        days[idx] += 1
        t, bid, ask = load_ticks(ctx.cutoff, ctx.cutoff + bt.HORIZON)
        if t.size:
            spreads[idx].append(float(np.median(ask - bid)))
        sigs = {"fijo": [(v, bt.build_signal(ctx, v, row=row)) for v in variants],
                "escalado": [(v, bt.build_signal(ctx, bt.Variant(v.rule, v.pull * f, v.sl * f, v.min_move * f),
                                                 row=row, width=bt.ZONE_WIDTH * f)) for v in variants]}
        for fam, lst in sigs.items():
            sig = dict(lst)[LIVE]
            if sig is not None:
                risks[fam][idx].append(abs(sig.entry_used - sig.stop_loss))
        for cost in costs:
            b, a = bid - cost / 2, ask + cost / 2
            for fam, lst in sigs.items():
                for v, sig in lst:
                    res = trade(sig, t, b, a, bes) if sig is not None else None
                    if trades is not None:  # una fila por día y variante, operara o no
                        nb = res["nobe", 0] if res else ("none", 0.0)
                        bk = res["be_ok", args.be_main] if res else ("none", 0.0)
                        trades.writerow([ctx.day, fam, "%g" % cost, v.name, sig.direction if sig is not None else "",
                                         nb[0], "%.4f" % nb[1], bk[0], "%.4f" % bk[1]])
                    if res is None:
                        continue
                    for (mgmt, be), (kind, r) in res.items():
                        stats[fam, cost, be, mgmt, idx, v].add(kind, r)
                        stats[fam, cost, be, mgmt, -1, v].add(kind, r)
        print("%s  %d ticks  factor %.2f" % (ctx.day, t.size, f), flush=True)
    if trades is not None:
        trades_file.close()

    rows =[("%s a %s" % p, k) for k, p in enumerate(periods)] + [("Total", -1)]
    bm = args.be_main
    L = ["# Stop a entrada a los %d minutos, con precios reales y costos · %s a %s" % (bm, start, end), "",
         "Variantes momentum de backtest.py, corte 7:00 AM ET, posición completa, TP3 a 3R. Las abiertas a las 24 h se "
         "cierran al último precio. R = múltiplos del riesgo. Cada celda de manejo trae tres números: R de la variante "
         "del servidor (%s), cuántas de las %d variantes momentum quedan en positivo, y la mediana de R entre ellas." % (
             LIVE.name, len(variants)), "",
         "Días por tramo: %s." % "; ".join("%s: %d" % (lab, days[k]) for lab, k in rows[:-1]),
         "Spread de Dukascopy (mediana diaria, promedio del tramo, en puntos): %s." % "; ".join(
             "%s: %.2f" % (lab, sum(spreads[k]) / len(spreads[k])) for lab, k in rows[:-1] if spreads[k]),
         "Riesgo medio por operación de la variante del servidor (puntos, entrada al stop): %s." % "; ".join(
             "%s: fijo %.1f, escalado %.1f" % (lab, sum(risks["fijo"][k]) / max(1, len(risks["fijo"][k])),
                                              sum(risks["escalado"][k]) / max(1, len(risks["escalado"][k])))
             for lab, k in rows[:-1]), ""]
    for fam, title in (("escalado", "Puntos escalados a la volatilidad"), ("fijo", "Puntos fijos (la regla tal como corre hoy)")):
        L += ["## %s" % title, ""]
        for cost in costs:
            L += ["### Costo extra por operación: %.2f puntos%s" % (cost, " (solo el spread de Dukascopy)" if cost == 0 else ""), "",
                  "| Tramo | Operaciones | " + " | ".join("%s: R servidor | en positivo | mediana" % lab for _, lab in MGMT) + " |",
                  "|---|---|" + "---|---|---|" * len(MGMT)]
            for lab, p in rows:
                L.append("| %s | %d | %s |" % (lab, stats[fam, cost, 0, "nobe", p, LIVE].n,
                                               " | ".join(_cell(stats, fam, cost, bm, m, p, variants) for m, _ in MGMT)))
            L.append("")
        L += ["### Cómo terminan las operaciones de la variante del servidor (total, por costo)", "",
              "| Costo | Manejo | Operaciones | TP3 | Stop | En entrada | Abiertas a 24 h | R total | R por operación | Drawdown máx |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for cost in costs:
            for m, lab in MGMT:
                s = stats[fam, cost, 0 if m == "nobe" else bm, m, -1, LIVE]
                L.append("| %.2f | %s | %d | %d | %d | %d | %d | %+.1f | %+.3f | %.1fR |" % (
                    cost, lab, s.n, s.tp, s.sl, s.be, s.opened, s.r, s.r / s.n if s.n else 0.0, s.dd))
        L += ["", "### Sensibilidad a los minutos (total; mismas tres cifras por celda)", "",
              "| Costo | Minutos | " + " | ".join("%s: R servidor | en positivo | mediana" % lab for _, lab in MGMT[1:]) + " |",
              "|---|---|" + "---|---|---|" * (len(MGMT) - 1)]
        for cost in costs:
            for be in bes:
                L.append("| %.2f | %d | %s |" % (cost, be, " | ".join(_cell(stats, fam, cost, be, m, -1, variants) for m, _ in MGMT[1:])))
        L.append("")
    L += ["## Control contra el simulador viejo (costo 0, salidas al nivel exacto, variante del servidor)", "",
          "Debe coincidir con reports/backtest_3y.md: resueltas y su R, abiertas y su R, y la columna «R BE10».", "",
          "| Familia | Tramo | Resueltas | R resueltas | Abiertas a 24 h | R de las abiertas | R BE10 viejo |",
          "|---|---|---|---|---|---|---|"]
    for fam in ("fijo", "escalado"):
        for lab, p in rows:
            a, o, b = (stats[fam, 0.0, 0, "leg_res", p, LIVE], stats[fam, 0.0, 0, "leg_open", p, LIVE],
                       stats[fam, 0.0, LEGACY_BE_MIN, "leg_be", p, LIVE])
            L.append("| %s | %s | %d | %+.1f | %d | %+.1f | %+.1f |" % (fam, lab, a.n, a.r, o.n, o.r, b.r))
    text = "\n".join(L) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
