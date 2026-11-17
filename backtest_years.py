"""Backtest mecánico por tramos, en una sola pasada sobre los ticks.

Corre las variantes de backtest.py sobre todo el rango y reparte cada señal en el
total y en su tramo (por defecto, un año cada uno), para ver si el resultado se
sostiene año por año o si lo carga un solo periodo. No separa por noticias:
data/events.csv solo cubre 2026.

Dos familias de variantes:
- "fijo": los mismos puntos todo el tiempo (lo que corre en el servidor).
- "escalado": retroceso, ancho de zona, stop y umbral multiplicados por
  rango diario medio de los 20 días previos / rango diario medio del periodo de
  referencia (donde se eligieron los puntos). Sin esto, 10 puntos de stop con el
  oro a 2,000 y rangos de 25 puntos no es la misma regla que con el oro a 4,000 y
  rangos de 80.

Además de las señales resueltas (TP3 o stop en 24 h) cuenta las que seguían
abiertas a las 24 h y las cierra a precio de mercado. backtest.py las descarta, y
eso sesga a la baja los periodos de poca volatilidad: el stop queda a 1R y el TP3
a 3R, así que las perdedoras se resuelven y muchas ganadoras a medias no.

Uso:
    python backtest_years.py --candles data/candles/XAUUSD_1m_3y.csv \
        --periods 2023-11-13:2024-11-12,2024-11-13:2025-11-12,2025-11-13:2026-11-06 \
        --reference 2026-05-11:2026-11-06
"""
from __future__ import annotations

import argparse
import ctypes
import itertools
import sys
from datetime import date
from pathlib import Path

import backtest as bt
from verifier.dukascopy import iter_ticks
from verifier.sim import simulate

LIVE = bt.Variant("momentum", 5.5, 10.0, 0.0)  # la variante que corre en el servidor
ADR_DAYS = 20
FULL_DAY_CANDLES = 600  # menos que esto es domingo o festivo: no cuenta para el rango medio


class Acc:
    """Señales resueltas (Tally de backtest.py) más las que seguían abiertas a las 24 h."""

    def __init__(self) -> None:
        self.t = bt.Tally()
        self.opens = 0
        self.open_r = 0.0

    def add(self, res) -> None:
        self.t.add(res)
        if res.status == "filled" and res.paths["no_be"].outcome == "open" and res.open_r is not None:
            self.opens += 1
            self.open_r += res.open_r

    @property
    def r_all(self) -> float:
        return self.t.r_full + self.open_r


def daily_ranges(path: Path) -> dict[date, float]:
    """Rango (máximo - mínimo) de cada día UTC completo."""
    hi: dict[str, float] = {}
    lo: dict[str, float] = {}
    n: dict[str, int] = {}
    with path.open(encoding="utf-8") as f:
        next(f)
        for line in f:
            d = line[:10]
            p = line.split(",")
            h, l = float(p[2]), float(p[3])
            if d not in n:
                hi[d], lo[d], n[d] = h, l, 0
            hi[d], lo[d], n[d] = max(hi[d], h), min(lo[d], l), n[d] + 1
    return {date.fromisoformat(d): hi[d] - lo[d] for d in n if n[d] >= FULL_DAY_CANDLES}


def adr_before(ranges: dict[date, float]) -> dict[date, float]:
    """Para cada día, rango medio de los ADR_DAYS días completos anteriores (sin mirar el propio día)."""
    days = sorted(ranges)
    out = {}
    for i, d in enumerate(days):
        if i >= ADR_DAYS:
            out[d] = sum(ranges[x] for x in days[i - ADR_DAYS:i]) / ADR_DAYS
    return out


def _table(title: str, note: str, periods, days, parts, total) -> list[str]:
    lines = ["## %s" % title, "", note, "",
             "| Tramo | Días | Momentum en positivo | Mediana momentum | Resueltas | Gana | Pierde | % acierto | R resueltas | Abiertas a 24 h | R de las abiertas | R total | R/señal | Peor racha | Drawdown máx |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for label, n, part in [("%s a %s" % p, n, part) for p, n, part in zip(periods, days, parts)] + [("Total", sum(days), total)]:
        mom = sorted(a.r_all for v, a in part.items() if v.rule == "momentum")
        a = part[LIVE]
        t = a.t
        pct = 100.0 * t.wins / t.filled if t.filled else 0.0
        taken = t.filled + a.opens
        lines.append("| %s | %d | %d/%d | %+.1f | %d | %d | %d | %.0f%% | %+.1f | %d | %+.1f | %+.1f | %+.2f | %d | %.1fR |" % (
            label, n, sum(r > 0 for r in mom), len(mom), mom[len(mom) // 2], t.filled, t.wins, t.losses, pct, t.r_full,
            a.opens, a.open_r, a.r_all, a.r_all / taken if taken else 0.0, t.worst_streak, t.max_dd))
    return lines + [""]


def _detail(part: dict[bt.Variant, Acc], a: date, b: date, n: int) -> str:
    as_tallies = {v: {"total": acc.t, "normal": bt.Tally(), "ventana": bt.Tally(), "horizonte": bt.Tally()}
                  for v, acc in part.items()}
    return bt.report(as_tallies, a, b, n).split("\n## Por tipo de día")[0].rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candles", type=Path, required=True)
    ap.add_argument("--periods", required=True, help="tramos inicio:fin separados por coma, en orden")
    ap.add_argument("--reference", required=True, help="periodo inicio:fin donde se eligieron los puntos")
    ap.add_argument("--out", type=Path, default=bt.ROOT / "reports" / "backtest_3y.md")
    args = ap.parse_args(argv)

    if sys.platform == "win32":  # que la laptop no se duerma a media corrida
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    periods = [tuple(date.fromisoformat(x) for x in p.split(":")) for p in args.periods.split(",")]
    ref_a, ref_b = (date.fromisoformat(x) for x in args.reference.split(":"))
    start, end = periods[0][0], periods[-1][1]
    fixed = [bt.Variant(r, p, s, m) for r, p, s, m in itertools.product(bt.RULES, bt.PULLS, bt.STOPS, bt.MIN_MOVES)]
    scaled = [v for v in fixed if v.rule == "momentum"]
    contexts = bt.load_day_contexts(args.candles, start, end)
    adr = adr_before(daily_ranges(args.candles))
    ref = [r for d, r in adr.items() if ref_a <= d <= ref_b]
    adr_ref = sum(ref) / len(ref)

    fam = {"fijo": fixed, "escalado": scaled}
    total = {k: {v: Acc() for v in vs} for k, vs in fam.items()}
    parts = {k: [{v: Acc() for v in vs} for _ in periods] for k, vs in fam.items()}
    days = [0] * len(periods)
    factors: list[list[float]] = [[] for _ in periods]
    print("%d días, %d variantes fijas, %d escaladas, rango de referencia %.1f" % (
        len(contexts), len(fixed), len(scaled), adr_ref), flush=True)

    for i, ctx in enumerate(contexts, start=1):
        idx = next((k for k, (a, b) in enumerate(periods) if a <= ctx.day <= b), None)
        if idx is None or ctx.day not in adr:
            continue
        f = adr[ctx.day] / adr_ref
        days[idx] += 1
        factors[idx].append(f)
        ticks = list(iter_ticks("XAUUSD", ctx.cutoff, ctx.cutoff + bt.HORIZON, bt.TICKS))
        for v in fixed:
            sig = bt.build_signal(ctx, v, row=i)
            if sig is not None:
                res = simulate(sig, ticks)
                total["fijo"][v].add(res)
                parts["fijo"][idx][v].add(res)
        for v in scaled:
            sig = bt.build_signal(ctx, bt.Variant(v.rule, v.pull * f, v.sl * f, v.min_move * f), row=i,
                                  width=bt.ZONE_WIDTH * f)
            if sig is not None:
                res = simulate(sig, ticks)
                total["escalado"][v].add(res)
                parts["escalado"][idx][v].add(res)
        print("%s  %d ticks  factor %.2f" % (ctx.day, len(ticks), f), flush=True)

    lines = ["# Backtest mecánico XAUUSD por año · %s a %s" % (start, end), "",
             "Corte a las 7:00 AM ET, TP a 1R/2R/3R, posición completa sin BE. Las columnas desde «Resueltas» son la "
             "variante que corre en el servidor (%s). «Resueltas» = TP3 o stop dentro de 24 h; las que seguían abiertas "
             "a las 24 h se cierran a precio de mercado y se suman en «R total»." % LIVE.name, "",
             "Factor de escala por tramo (rango diario medio de 20 días / %.1f puntos del periodo de referencia %s a %s): %s." % (
                 adr_ref, ref_a, ref_b,
                 "; ".join("%s a %s: %.2f medio, %.2f a %.2f" % (a, b, sum(fs) / len(fs), min(fs), max(fs))
                           for (a, b), fs in zip(periods, factors) if fs)), ""]
    lines += _table("Puntos fijos (la regla tal como corre hoy)",
                    "Retroceso, zona y stop en los mismos puntos todos los años.",
                    periods, days, parts["fijo"], total["fijo"])
    lines += _table("Puntos escalados a la volatilidad",
                    "Los mismos parámetros multiplicados por el factor de escala de cada día.",
                    periods, days, parts["escalado"], total["escalado"])
    text = "\n".join(lines)
    for k in ("fijo", "escalado"):
        for (a, b), n, part in zip(periods, days, parts[k]):
            text += "\n## Detalle %s · solo resueltas\n\n" % k + _detail(part, a, b, n).split("\n", 2)[2]
        text += "\n## Detalle %s · total · solo resueltas\n\n" % k + _detail(total[k], start, end, sum(days)).split("\n", 2)[2]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
