"""Backtest mecánico del estilo de señal del agente, sobre los seis meses de ticks.

Reglas (derivadas de las señales del replay): a la hora del corte (7:00 AM hora
del Este) se mira el movimiento desde el cierre del día anterior. Con la regla
"momentum" se va a favor de ese movimiento, con "contra" en contra. La zona de
entrada se pone a `pull` puntos de retroceso desde el precio, con 3 puntos de
ancho; el stop a `sl` puntos del borde lejano; TP1/TP2/TP3 a 1R, 2R y 3R. El
umbral `min_move` exige un movimiento mínimo para operar (0 = siempre).

Cada variante se califica con el mismo simulador tick a tick de verify.py
(llenado en 4 h, horizonte 24 h; manejos sin BE, BE a los 10 min, BE tras TP1).

Uso:
    python backtest.py --start 2026-05-11 --end 2026-11-06
    python backtest.py --start 2026-09-01 --end 2026-10-31 --out reports/backtest_sep_oct.md
"""
from __future__ import annotations

import argparse
import csv
import itertools
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from verifier.dukascopy import iter_ticks
from verifier.signals import Signal, eastern_to_utc
from verifier.sim import simulate

ROOT = Path(__file__).resolve().parent
CANDLES = ROOT / "data" / "candles" / "XAUUSD_1m.csv"
TICKS = ROOT / "data" / "ticks"
CUTOFF_ET = (7, 0)
ZONE_WIDTH = 3.0

PULLS = (3.0, 5.5, 8.0)
STOPS = (6.0, 8.0, 10.0)
RULES = ("momentum", "contra")
MIN_MOVES = (0.0, 10.0)


@dataclass(frozen=True)
class Variant:
    rule: str
    pull: float
    sl: float
    min_move: float

    @property
    def name(self) -> str:
        return "%s pull %g sl %g min %g" % (self.rule, self.pull, self.sl, self.min_move)


@dataclass
class DayContext:
    day: date
    cutoff: datetime
    live: float
    y_close: float


def load_day_contexts(path: Path, start: date, end: date) -> list[DayContext]:
    """Precio al corte y cierre del día UTC anterior, para cada día hábil con velas antes del corte."""
    closes: dict[str, float] = {}
    at_cutoff: dict[str, float] = {}
    cutoffs = {d.isoformat(): eastern_to_utc(d, *CUTOFF_ET).strftime("%Y-%m-%dT%H:%M:%SZ")
               for d in _weekdays(start - timedelta(days=4), end)}
    with path.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            ts = line[:20]
            d = ts[:10]
            close = float(line.split(",")[4])
            closes[d] = close
            lim = cutoffs.get(d)
            if lim and ts < lim:
                at_cutoff[d] = close
    days = sorted(closes)
    out = []
    for d in _weekdays(start, end):
        key = d.isoformat()
        if key not in at_cutoff:
            continue
        prev = [x for x in days if x < key]
        if not prev:
            continue
        out.append(DayContext(d, eastern_to_utc(d, *CUTOFF_ET), at_cutoff[key], closes[prev[-1]]))
    return out


def _weekdays(start: date, end: date) -> list[date]:
    return [start + timedelta(days=i) for i in range((end - start).days + 1) if (start + timedelta(days=i)).weekday() < 5]


def build_signal(ctx: DayContext, v: Variant, row: int = 0) -> Signal | None:
    move = ctx.live - ctx.y_close
    if abs(move) < v.min_move or move == 0:
        return None
    up = move > 0
    buy = up if v.rule == "momentum" else not up
    mid = ctx.live - v.pull if buy else ctx.live + v.pull
    lo, hi = round(mid - ZONE_WIDTH / 2, 2), round(mid + ZONE_WIDTH / 2, 2)
    sl = round(lo - v.sl, 2) if buy else round(hi + v.sl, 2)
    risk = abs(mid - sl)
    sign = 1 if buy else -1
    tps = [round(mid + sign * risk * k, 2) for k in (1, 2, 3)]
    return Signal(row=row, signal_date=ctx.day, direction="BUY" if buy else "SELL", entry_low=lo, entry_high=hi,
                  entry_used=round(mid, 2), stop_loss=sl, tps=tps, start_utc=ctx.cutoff, time_basis="explicit_utc")


@dataclass
class Tally:
    n: int = 0
    filled: int = 0
    wins: int = 0
    losses: int = 0
    r_full: float = 0.0
    r_thirds: float = 0.0
    r_be10: float = 0.0
    r_be_tp1: float = 0.0
    streak: int = 0
    worst_streak: int = 0
    peak: float = 0.0
    max_dd: float = 0.0

    def add(self, res) -> None:
        self.n += 1
        if res.status != "filled":
            return
        nb = res.paths["no_be"]
        if nb.outcome == "open" or nb.r_full is None:
            return
        self.filled += 1
        self.r_full += nb.r_full
        self.r_thirds += nb.r_thirds or 0.0
        self.r_be10 += res.paths["be_after_min"].r_full or 0.0
        self.r_be_tp1 += res.paths["be_after_tp1"].r_full or 0.0
        if nb.r_full > 0:
            self.wins += 1
            self.streak = 0
        elif nb.r_full < 0:
            self.losses += 1
            self.streak += 1
            self.worst_streak = max(self.worst_streak, self.streak)
        self.peak = max(self.peak, self.r_full)
        self.max_dd = max(self.max_dd, self.peak - self.r_full)


EVENTS = ROOT / "data" / "events.csv"
FILL_WINDOW = timedelta(hours=4)
HORIZON = timedelta(hours=24)


def load_events(path: Path = EVENTS) -> list[tuple[datetime, str]]:
    """Eventos de alto impacto (date, time_et, event, stars) como (hora UTC, nombre)."""
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            h, m = r["time_et"].split(":")
            out.append((eastern_to_utc(date.fromisoformat(r["date"]), int(h), int(m)), r["event"]))
    return sorted(out)


def news_in(start: datetime, events: list[tuple[datetime, str]]) -> tuple[str, str]:
    """('ventana', nombres) si hay evento dentro de la ventana de llenado tras `start`,
    ('horizonte', nombres) si solo dentro del horizonte de 24 h, ('normal', '') si ninguno."""
    window = [n for t, n in events if start <= t < start + FILL_WINDOW]
    if window:
        return "ventana", ", ".join(window)
    horizon = [n for t, n in events if start + FILL_WINDOW <= t < start + HORIZON]
    if horizon:
        return "horizonte", ", ".join(horizon)
    return "normal", ""


def run(contexts: list[DayContext], variants: list[Variant], tick_root: Path = TICKS,
        events: list[tuple[datetime, str]] | None = None) -> dict[Variant, dict[str, Tally]]:
    """Por variante: conteo 'total' y uno por tipo de día (normal / ventana / horizonte)."""
    events = events or []
    tallies = {v: {k: Tally() for k in ("total", "normal", "ventana", "horizonte")} for v in variants}
    for i, ctx in enumerate(contexts, start=1):
        kind, _ = news_in(ctx.cutoff, events)
        ticks = list(iter_ticks("XAUUSD", ctx.cutoff, ctx.cutoff + HORIZON, tick_root))
        for v in variants:
            sig = build_signal(ctx, v, row=i)
            if sig is None:
                continue
            res = simulate(sig, ticks)
            tallies[v]["total"].add(res)
            tallies[v][kind].add(res)
        print("%s  %d ticks  %s" % (ctx.day, len(ticks), kind), flush=True)
    return tallies


def report(tallies: dict[Variant, dict[str, Tally]], start: date, end: date, days: int) -> str:
    lines = ["# Backtest mecánico XAUUSD · %s a %s" % (start, end), "",
             "%d días hábiles con mercado al corte (7:00 AM ET). Zona de 3 puntos; TP a 1R/2R/3R. "
             "R = resultado en múltiplos del riesgo, posición completa sin BE salvo donde se indica." % days, "",
             "| Variante | Señales | Llenadas | Gana | Pierde | % acierto | R total | R/señal | R tercios | R BE10 | R BE tras TP1 | Peor racha | Drawdown máx |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    ranked = sorted(tallies.items(), key=lambda kv: kv[1]["total"].r_full, reverse=True)
    for v, by in ranked:
        t = by["total"]
        pct = 100.0 * t.wins / t.filled if t.filled else 0.0
        per = t.r_full / t.filled if t.filled else 0.0
        lines.append("| %s | %d | %d | %d | %d | %.0f%% | %+.1f | %+.2f | %+.1f | %+.1f | %+.1f | %d | %.1fR |" % (
            v.name, t.n, t.filled, t.wins, t.losses, pct, t.r_full, per, t.r_thirds, t.r_be10, t.r_be_tp1,
            t.worst_streak, t.max_dd))
    rs = sorted(by["total"].r_full for by in tallies.values())
    median = rs[len(rs) // 2] if rs else 0.0
    lines += ["", "Mediana de R total entre las %d variantes: %+.1f. Con %d variantes probadas, la mejor fila "
              "siempre luce bien por azar: lo que cuenta es si la mayoría está por encima de cero." % (len(rs), median, len(rs))]

    lines += ["", "## Por tipo de día (variantes momentum)", "",
              "Ventana = evento de 3 estrellas dentro de las 4 h de llenado (CPI, PPI, nóminas a las 8:30 ET). "
              "Horizonte = evento más tarde en las 24 h (FOMC a las 14:00). Normal = sin evento.", "",
              "| Variante | Normal: llenadas / R | R por señal | Ventana: llenadas / R | R por señal | Horizonte: llenadas / R | R por señal |",
              "|---|---|---|---|---|---|---|"]
    for v, by in ranked:
        if v.rule != "momentum":
            continue
        cells = []
        for k in ("normal", "ventana", "horizonte"):
            t = by[k]
            cells.append("%d / %+.1f | %+.2f" % (t.filled, t.r_full, t.r_full / t.filled if t.filled else 0.0))
        lines.append("| %s | %s |" % (v.name, " | ".join(cells)))
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "backtest_mecanico.md")
    ap.add_argument("--candles", type=Path, default=CANDLES, help="CSV de velas de 1 minuto a usar")
    args = ap.parse_args(argv)

    contexts = load_day_contexts(args.candles, args.start, args.end)
    variants = [Variant(r, p, s, m) for r, p, s, m in itertools.product(RULES, PULLS, STOPS, MIN_MOVES)]
    events = load_events()
    print("%d días, %d variantes, %d eventos" % (len(contexts), len(variants), len(events)), flush=True)
    tallies = run(contexts, variants, events=events)
    text = report(tallies, args.start, args.end, len(contexts))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
