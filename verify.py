"""Verifica señales XAUUSD del tracker contra ticks reales de Dukascopy.

Uso:
    python verify.py data/signals_tracker.csv
    python verify.py data/signals_tracker.csv --rows 1,4,10 --horizon-hours 12
    python verify.py data/signals_tracker.csv --out reports/julio

Salida: reports/results.csv y reports/report.md (o la carpeta de --out).
Los ticks descargados quedan en data/ticks/ y no se vuelven a pedir.
"""
from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

from verifier.dukascopy import iter_ticks
from verifier.report import write_report_md, write_results_csv
from verifier.signals import load_tracker
from verifier.sim import simulate

ROOT = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tracker", type=Path)
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--out", type=Path, default=ROOT / "reports")
    ap.add_argument("--ticks-cache", type=Path, default=ROOT / "data" / "ticks")
    ap.add_argument("--rows", help="filas del CSV a verificar, separadas por coma (1 = primera señal)")
    ap.add_argument("--fill-window-hours", type=float, default=4.0, help="horas para que el precio llegue a la zona")
    ap.add_argument("--horizon-hours", type=float, default=24.0, help="horas máximas de seguimiento tras la señal")
    ap.add_argument("--be-minutes", type=int, default=10, help="minutos tras el llenado para mover el stop a BE")
    args = ap.parse_args(argv)

    signals, skipped = load_tracker(args.tracker)
    if args.rows:
        wanted = {int(x) for x in args.rows.split(",")}
        signals = [s for s in signals if s.row in wanted]
    print("Señales verificables: %d | omitidas: %d" % (len(signals), len(skipped)))

    results = []
    for s in signals:
        print("  %s  inicio %s (%s) ..." % (s.label, s.start_utc.strftime("%Y-%m-%d %H:%M"), s.time_basis), end="", flush=True)
        ticks = iter_ticks(args.symbol, s.start_utc, s.start_utc + timedelta(hours=args.horizon_hours), args.ticks_cache)
        r = simulate(s, ticks, fill_window=timedelta(hours=args.fill_window_hours),
                     horizon=timedelta(hours=args.horizon_hours), be_after=timedelta(minutes=args.be_minutes))
        if r.status == "filled":
            print(" llenada %s @%.2f | sin BE: %s %s | BE %dm: %s %s" % (
                r.fill_time.strftime("%H:%M"), r.fill_price,
                r.paths["no_be"].outcome, r.paths["no_be"].r_full, args.be_minutes,
                r.paths["be_after_min"].outcome, r.paths["be_after_min"].r_full))
        else:
            print(" %s %s" % (r.status, r.note))
        results.append(r)

    write_results_csv(results, args.out / "results.csv")
    write_report_md(results, skipped, args.out / "report.md", symbol=args.symbol, tracker=args.tracker,
                    be_minutes=args.be_minutes)
    print("Escrito: %s y %s" % (args.out / "results.csv", args.out / "report.md"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
