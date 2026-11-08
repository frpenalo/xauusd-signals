"""Exporta velas de 1 minuto (bid) de XAUUSD a CSV a partir de los ticks de Dukascopy.

Uso:
    python export_candles.py --months 6
    python export_candles.py --start 2026-05-01 --end 2026-11-07
    python export_candles.py --months 6 --out data/candles/XAUUSD_1m.csv

El CSV sale con las columnas que espera el cargador local de Vibe-Trading
(date, open, high, low, close, volume) con la fecha en UTC ISO. El volumen es
el número de ticks del minuto (Dukascopy no publica volumen real en spot).

Es reanudable: si el archivo ya existe, continúa desde el día siguiente al
último escrito. Los ticks quedan cacheados en data/ticks/ por el verificador.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from verifier.dukascopy import decode_hour, fetch_hour

ROOT = Path(__file__).resolve().parent
COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def day_candles(symbol: str, day: date, cache_root: Path) -> list[list]:
    rows: list[list] = []
    for h in range(24):
        hour = datetime(day.year, day.month, day.day, h, tzinfo=timezone.utc)
        ticks = decode_hour(fetch_hour(symbol, hour, cache_root), symbol, hour)
        if not ticks:
            continue
        cur = None
        o = hi = lo = c = 0.0
        n = 0
        for t in ticks:
            m = t.ts.replace(second=0, microsecond=0)
            if m != cur:
                if cur is not None:
                    rows.append([cur.strftime("%Y-%m-%dT%H:%M:%SZ"), o, hi, lo, c, n])
                cur, o, hi, lo, c, n = m, t.bid, t.bid, t.bid, t.bid, 0
            hi, lo, c, n = max(hi, t.bid), min(lo, t.bid), t.bid, n + 1
        rows.append([cur.strftime("%Y-%m-%dT%H:%M:%SZ"), o, hi, lo, c, n])
    return rows


def last_written_day(path: Path) -> date | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    with path.open("rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 4096))
        tail = f.read().decode("utf-8", errors="ignore").strip().splitlines()
    for line in reversed(tail):
        if line[:4].isdigit():
            return date.fromisoformat(line[:10])
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--symbol", default="XAUUSD")
    ap.add_argument("--months", type=int, default=6, help="meses hacia atrás desde --end (si no hay --start)")
    ap.add_argument("--start", type=date.fromisoformat)
    ap.add_argument("--end", type=date.fromisoformat, help="último día incluido; por defecto ayer (UTC)")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "candles" / "XAUUSD_1m.csv")
    ap.add_argument("--ticks-cache", type=Path, default=ROOT / "data" / "ticks")
    args = ap.parse_args(argv)

    end = args.end or (datetime.now(timezone.utc).date() - timedelta(days=1))
    start = args.start or (end - timedelta(days=30 * args.months))
    resume_from = last_written_day(args.out)
    if resume_from is not None and resume_from >= start:
        start = resume_from + timedelta(days=1)
        print("Reanudando desde %s (último día en el archivo: %s)" % (start, resume_from), flush=True)
    if start > end:
        print("Nada que exportar: el archivo ya llega hasta %s" % end, flush=True)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    new_file = resume_from is None
    total = 0
    with args.out.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(COLUMNS)
        day = start
        while day <= end:
            rows = day_candles(args.symbol, day, args.ticks_cache)
            w.writerows(rows)
            f.flush()
            total += len(rows)
            print("%s  %5d velas  (acumulado %d)" % (day, len(rows), total), flush=True)
            day += timedelta(days=1)
    print("Listo: %s" % args.out, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
