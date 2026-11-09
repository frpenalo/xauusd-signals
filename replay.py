"""Replay histórico: la señal diaria del agente, día por día, sin ver el futuro.

Para cada día hábil del rango se recorta el CSV de velas de 1 minuto hasta la
hora del corte (7:00 AM hora del Este, la misma de la tarea programada), se
apunta el Data Bridge de Vibe-Trading a ese recorte, se pide la señal al agente
con el mismo prompt del día a día, y se califica enseguida contra los ticks
reales de ese día. El resultado va a data/replay_signals.csv.

Candados contra fugas de información futura:
- El agente solo ve el recorte: local:XAUUSD termina en la hora del corte.
- El caché de datos de Vibe-Trading se apaga y se le niegan las herramientas de
  noticias, web, memoria y shell.
- Al terminar cada corrida se revisa la evidencia que dejó el agente: si leyó
  algún dato que no sea local:XAUUSD o con fecha posterior al corte, la señal
  se marca "leak_suspect" en las notas y no cuenta en el marcador.

Uso:
    python replay.py --start 2026-09-01 --end 2026-10-31
    python replay.py --start 2026-09-01 --end 2026-10-31 --telegram   # manda el marcador final
Es reanudable: los días que ya están en el CSV se saltan.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import daily_signal as ds
from verifier.signals import eastern_to_utc

REPLAY_CSV = ds.ROOT / "data" / "replay_signals.csv"
REPLAY_CANDLES = ds.ROOT / "data" / "candles" / "XAUUSD_1m_replay.csv"
BRIDGE_CONFIG = Path.home() / ".vibe-trading" / "data-bridge" / "config.yaml"
RUNS_DIR = Path.home() / ".vibe-trading" / "runs"
CUTOFF_ET = (7, 0)

REPLAY_ENV = {
    "VIBE_TRADING_DATA_CACHE": "false",
    "CLAUDE_CLI_DENY_TOOL_PREFIXES": ",".join([
        "trading_", "etoro_", "web_search", "read_url", "get_stock_news", "sentiment", "research_papers",
        "search_broker_reports", "get_research_reports", "prediction_market", "get_macro", "screen_market",
        "technical_indicators", "bash", "background_run", "check_background", "read_file", "read_document",
        "write_file", "edit_file", "remember", "session_search", "iwencai", "qveris", "get_sec_filings",
    ]),
}

REPLAY_PREAMBLE = """HISTORICAL REPLAY. Treat {today} {time} UTC as the current moment: nothing after it exists for you.
The local symbol `local:XAUUSD` ends exactly at that moment. When requesting bars, use start={start} and end={today}.
Do not use any data source other than `local:XAUUSD` and the figures in this prompt.

"""


def cutoff_utc(day: date) -> datetime:
    return eastern_to_utc(day, *CUTOFF_ET)


def weekdays(start: date, end: date) -> list[date]:
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def truncate_candles(src: Path, dst: Path, cutoff: datetime) -> tuple[int, float | None, datetime | None]:
    """Copia a dst las velas con fecha anterior al corte. Devuelve (filas, último cierre, hora del último cierre)."""
    limit = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    n, last_close, last_ts = 0, None, None
    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8", newline="") as fout:
        fout.write(next(fin))
        for line in fin:
            if line[:20] >= limit:
                break
            fout.write(line)
            n += 1
            p = line.rstrip("\n").split(",")
            last_close = float(p[4])
            last_ts = datetime.strptime(p[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return n, last_close, last_ts


def swap_bridge_path(config_text: str, original: Path, replacement: Path) -> str:
    """Apunta la fuente XAUUSD del Data Bridge al recorte. Falla si la ruta original no está."""
    orig = original.as_posix()
    if orig not in config_text:
        raise RuntimeError("La config del Data Bridge no apunta a %s" % orig)
    return config_text.replace(orig, replacement.as_posix())


def leak_check(evidence: dict, cutoff: datetime) -> str:
    """'' si toda la evidencia es local:XAUUSD anterior al corte; si no, el motivo."""
    problems = []
    for e in evidence.get("evidence", []):
        if e.get("source") != "local" or str(e.get("symbol", "")).upper() != "XAUUSD":
            problems.append("%s %s/%s" % (e.get("tool"), e.get("source"), e.get("symbol")))
            continue
        ts = e.get("timestamp")
        if ts and datetime.fromisoformat(ts).replace(tzinfo=timezone.utc) >= cutoff:
            problems.append("dato de %s posterior al corte" % ts)
    return "; ".join(sorted(set(problems))[:3])


def newest_run_evidence(since: float) -> dict:
    runs = [p for p in RUNS_DIR.iterdir() if p.is_dir() and p.stat().st_mtime >= since] if RUNS_DIR.exists() else []
    if not runs:
        return {}
    ev = max(runs, key=lambda p: p.stat().st_mtime) / "artifacts" / "grounding_evidence.json"
    return json.loads(ev.read_text(encoding="utf-8")) if ev.exists() else {}


def replay_day(day: date) -> str:
    cutoff = cutoff_utc(day)
    n, live, last_ts = truncate_candles(ds.CANDLES, REPLAY_CANDLES, cutoff)
    if live is None or last_ts is None or cutoff - last_ts > timedelta(hours=12):
        return "%s: sin mercado antes del corte, se salta" % day
    daily = ds.recent_daily_bars(path=REPLAY_CANDLES)
    prompt = REPLAY_PREAMBLE.format(today=day.isoformat(), time=cutoff.strftime("%H:%M"),
                                    start=(day - timedelta(days=14)).isoformat()) + ds.build_prompt(live, daily, cutoff)
    sig, reason, leak = None, "", ""
    for attempt in range(2):
        started = time.time()
        out = ds.run_agent(prompt if attempt == 0 else prompt + "\n\nYour previous answer was rejected: %s. Fix it." % reason,
                           extra_env=REPLAY_ENV)
        leak = leak_check(newest_run_evidence(started), cutoff)
        sig = ds.extract_signal(out)
        if sig is None:
            reason = "no JSON signal found in the answer"
            continue
        reason = ds.validate_signal(sig, live)
        if not reason:
            break
    if sig is None or reason:
        return "%s: sin señal válida (%s)" % (day, reason)
    if str(sig["direction"]).upper() == "NO_TRADE":
        return "%s: NO_TRADE. %s" % (day, sig.get("rationale", ""))
    row = ds.append_signal(sig, live, cutoff, path=REPLAY_CSV, source_channel="replay")
    if leak:
        rows = ds.read_rows(REPLAY_CSV)
        rows[-1]["notes"] = "leak_suspect: %s | %s" % (leak, rows[-1]["notes"])
        rows[-1]["status"] = "leak_suspect"
        ds.write_rows(rows, REPLAY_CSV)
        return "%s: %s %s-%s DESCARTADA por fuga (%s)" % (day, row["direction"], row["entry_low"], row["entry_high"], leak)
    scored = ds.score_pending(day + timedelta(days=2), False, path=REPLAY_CSV)
    return scored[-1] if scored else "%s: %s %s-%s sigue abierta" % (day, row["direction"], row["entry_low"], row["entry_high"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=date.fromisoformat, required=True)
    ap.add_argument("--end", type=date.fromisoformat, required=True)
    ap.add_argument("--telegram", action="store_true")
    args = ap.parse_args(argv)

    done = {r["signal_date"] for r in ds.read_rows(REPLAY_CSV)}
    days = [d for d in weekdays(args.start, args.end) if d.isoformat() not in done]
    print("Replay de %d días (%d ya hechos)" % (len(days), len(done)), flush=True)

    original = BRIDGE_CONFIG.read_text(encoding="utf-8")
    BRIDGE_CONFIG.write_text(swap_bridge_path(original, ds.CANDLES, REPLAY_CANDLES), encoding="utf-8")
    try:
        for day in days:
            print(replay_day(day), flush=True)
    finally:
        BRIDGE_CONFIG.write_text(original, encoding="utf-8")
        if REPLAY_CANDLES.exists():
            REPLAY_CANDLES.unlink()

    board = ds.scoreboard(REPLAY_CSV)
    print(board, flush=True)
    if args.telegram:
        ds.telegram_send("Replay %s a %s\n%s" % (args.start, args.end, board))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
