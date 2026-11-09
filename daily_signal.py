"""Señal diaria de XAUUSD generada por el agente de Vibe-Trading, con marcador.

Cada corrida hace dos cosas, en este orden:
1. Califica las señales pendientes de días anteriores contra ticks reales
   (mismo simulador que verify.py) y actualiza data/agent_signals.csv.
2. Pide al agente una señal para hoy con el precio en vivo y las velas
   locales, la valida, la guarda como "pending" y la manda por Telegram junto
   con el marcador acumulado.

Uso:
    python daily_signal.py                   # calificar + generar + Telegram
    python daily_signal.py --score-only      # solo calificar pendientes
    python daily_signal.py --no-refresh      # no actualizar las velas antes
    python daily_signal.py --dry-run         # no guardar ni mandar nada
    python daily_signal.py --telegram-chat-id  # ayuda para configurar el bot

Config de Telegram en config/telegram.env (ver config/telegram.env.example).
Esto es un experimento de medición: nadie opera estas señales.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from verifier.dukascopy import iter_ticks
from verifier.signals import Signal, load_tracker
from verifier.sim import simulate

ROOT = Path(__file__).resolve().parent
VIBE_DIR = ROOT.parent / "vibe-trading"
VIBE_EXE = VIBE_DIR / ".venv" / "Scripts" / "vibe-trading.exe"
CANDLES = ROOT / "data" / "candles" / "XAUUSD_1m.csv"
AGENT_CSV = ROOT / "data" / "agent_signals.csv"
TELEGRAM_ENV = ROOT / "config" / "telegram.env"
LOG = ROOT / "logs" / "daily_signal.log"
LIVE_URL = "https://api.gold-api.com/price/XAU"

TRACKER_COLUMNS = ["received_at_utc", "signal_date", "signal_time", "source_channel", "trader", "instrument",
                   "direction", "entry_low", "entry_high", "entry_used", "stop_loss", "tp1", "tp2", "tp3",
                   "management_updates", "outcome", "status", "result_r", "notes", "image_path"]

PROMPT = """You are generating ONE intraday trading signal for spot gold (XAUUSD) for today's New York session, in the exact style of a scalping signal channel. This is a research experiment: the signal is logged and scored later against real tick data. Nobody trades it.

Live context (UTC now {now}):
- Live spot price: {live} USD
- Recent daily bars (bid, UTC day):
{daily}
- Yesterday's range: {y_low} - {y_high}, close {y_close}

Data you may analyze with your tools: the local symbol `local:XAUUSD` has 1-minute bid bars for the last months (request e.g. interval 15m for the last 10 days). Use it to find the nearest intraday support/resistance, the recent swing structure and the typical pullback size before deciding.

Signal rules (hard constraints):
- direction: SELL or BUY, or NO_TRADE if there is no clean setup.
- entry zone: 2 to 4 points wide, placed where you expect a pullback to fill within the next 4 hours. It must be at most 15 points from the live price.
- stop_loss: 6 to 12 points beyond the far edge of the zone.
- tp1, tp2, tp3: about 1R, 2R and 3R from the zone midpoint (R = distance from midpoint to stop), in the trade direction, strictly ordered.
- rationale: at most 2 sentences, naming the levels you used.

Reply with ONLY this JSON object as your final answer, no prose before or after:
{{"direction": "SELL|BUY|NO_TRADE", "entry_low": 0.0, "entry_high": 0.0, "stop_loss": 0.0, "tp1": 0.0, "tp2": 0.0, "tp3": 0.0, "rationale": "..."}}
"""


def log(msg: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = "%s %s" % (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"), msg)
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------- Telegram ----------

def load_telegram() -> tuple[str, str]:
    if not TELEGRAM_ENV.exists():
        return "", ""
    vals = {}
    for line in TELEGRAM_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return vals.get("TELEGRAM_BOT_TOKEN", ""), vals.get("TELEGRAM_CHAT_ID", "")


def telegram_send(text: str) -> bool:
    token, chat_id = load_telegram()
    if not token or not chat_id:
        log("Telegram sin configurar; mensaje no enviado:\n" + text)
        return False
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request("https://api.telegram.org/bot%s/sendMessage" % token, data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except Exception as e:  # noqa: BLE001
        log("Telegram falló: %s" % e)
        return False


def telegram_print_chat_ids() -> None:
    token, _ = load_telegram()
    if not token:
        print("Falta TELEGRAM_BOT_TOKEN en %s" % TELEGRAM_ENV)
        return
    with urllib.request.urlopen("https://api.telegram.org/bot%s/getUpdates" % token, timeout=30) as resp:
        updates = json.load(resp).get("result", [])
    seen = {}
    for u in updates:
        m = u.get("message") or u.get("channel_post") or {}
        chat = m.get("chat") or {}
        if chat.get("id"):
            seen[chat["id"]] = chat.get("username") or chat.get("title") or chat.get("first_name", "")
    if not seen:
        print("Ningún mensaje recibido todavía: escríbele algo al bot y vuelve a correr esto.")
    for cid, name in seen.items():
        print("TELEGRAM_CHAT_ID=%s  (%s)" % (cid, name))


# ---------- Datos ----------

def live_price() -> float:
    req = urllib.request.Request(LIVE_URL, headers={"User-Agent": "xauusd-signals"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return float(json.load(resp)["price"])


def recent_daily_bars(n: int = 5) -> list[tuple[str, float, float, float, float]]:
    """Barras diarias (día UTC) a partir del CSV de 1 minuto, últimos n días con datos."""
    if not CANDLES.exists():
        return []
    days: dict[str, list[float]] = {}
    with CANDLES.open("rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 2_000_000))  # ~2 semanas de velas de 1 minuto
        tail = f.read().decode("utf-8", errors="ignore").splitlines()[1:]
    for line in tail:
        p = line.split(",")
        if len(p) < 6 or not p[0][:4].isdigit():
            continue
        d = p[0][:10]
        o, h, lo, c = float(p[1]), float(p[2]), float(p[3]), float(p[4])
        if d not in days:
            days[d] = [o, h, lo, c]
        else:
            days[d][1] = max(days[d][1], h)
            days[d][2] = min(days[d][2], lo)
            days[d][3] = c
    out = [(d, *v) for d, v in sorted(days.items())][-n:]
    return out


def refresh_candles() -> None:
    log("Actualizando velas locales...")
    r = subprocess.run([sys.executable, str(ROOT / "export_candles.py")], cwd=ROOT, capture_output=True, text=True,
                       timeout=3600, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    log("export_candles: " + (r.stdout.strip().splitlines() or ["(sin salida)"])[-1])


# ---------- Agente ----------

def build_prompt(live: float, daily: list) -> str:
    rows = "\n".join("  %s  O %.2f  H %.2f  L %.2f  C %.2f" % r for r in daily) or "  (sin velas locales todavía)"
    y = daily[-1] if daily else ("", live, live, live, live)
    return PROMPT.format(now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), live="%.2f" % live, daily=rows,
                         y_low="%.2f" % y[3], y_high="%.2f" % y[2], y_close="%.2f" % y[4])


def run_agent(prompt: str, timeout_s: int = 900) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    r = subprocess.run([str(VIBE_EXE), "run", "--no-rich", "-p", prompt], cwd=VIBE_DIR, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=timeout_s, env=env)
    return (r.stdout or "") + "\n" + (r.stderr or "")


def extract_signal(text: str) -> dict | None:
    """Último objeto JSON del texto que tenga el campo direction."""
    found = None
    for m in re.finditer(r"\{[^{}]*\"direction\"[^{}]*\}", text, flags=re.S):
        try:
            found = json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
    return found


def validate_signal(sig: dict, live: float) -> str:
    """Devuelve '' si la señal cumple las reglas, o el motivo del rechazo."""
    d = str(sig.get("direction", "")).upper()
    if d == "NO_TRADE":
        return ""
    if d not in ("SELL", "BUY"):
        return "direction inválida"
    try:
        lo, hi, sl = float(sig["entry_low"]), float(sig["entry_high"]), float(sig["stop_loss"])
        tps = [float(sig["tp1"]), float(sig["tp2"]), float(sig["tp3"])]
    except (KeyError, TypeError, ValueError):
        return "faltan números"
    if lo > hi:
        lo, hi = hi, lo
    width = hi - lo
    if not 1.5 <= width <= 5:
        return "zona de %.1f puntos (debe ser 2-4)" % width
    mid = (lo + hi) / 2
    if abs(mid - live) > 20:
        return "zona a %.1f puntos del precio en vivo (máx 15)" % abs(mid - live)
    if d == "SELL":
        sl_dist = sl - hi
        ok_dir = all(t < lo for t in tps) and tps[0] > tps[1] > tps[2]
    else:
        sl_dist = lo - sl
        ok_dir = all(t > hi for t in tps) and tps[0] < tps[1] < tps[2]
    if not 4 <= sl_dist <= 15:
        return "stop a %.1f puntos del borde de la zona (debe ser 6-12)" % sl_dist
    if not ok_dir:
        return "objetivos en el lado o el orden equivocado"
    risk = abs(mid - sl)
    r1 = abs(tps[0] - mid) / risk
    if not 0.6 <= r1 <= 1.6:
        return "TP1 a %.2fR (debe ser ~1R)" % r1
    return ""


# ---------- Tracker del agente ----------

def read_rows() -> list[dict]:
    if not AGENT_CSV.exists():
        return []
    with AGENT_CSV.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(rows: list[dict]) -> None:
    AGENT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with AGENT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TRACKER_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def append_signal(sig: dict, live: float, now: datetime) -> dict:
    row = {c: "" for c in TRACKER_COLUMNS}
    row.update({
        "received_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "signal_date": now.strftime("%Y-%m-%d"),
        "signal_time": now.strftime("%H:%M UTC"), "source_channel": "vibe-trading", "trader": "agente",
        "instrument": "XAUUSD", "direction": sig["direction"].upper(),
        "entry_low": sig["entry_low"], "entry_high": sig["entry_high"],
        "entry_used": round((float(sig["entry_low"]) + float(sig["entry_high"])) / 2, 2),
        "stop_loss": sig["stop_loss"], "tp1": sig["tp1"], "tp2": sig["tp2"], "tp3": sig["tp3"],
        "status": "pending", "notes": "live %.2f | %s" % (live, sig.get("rationale", "")),
    })
    rows = read_rows()
    rows.append(row)
    write_rows(rows)
    return row


def score_pending(today: date, dry_run: bool) -> list[str]:
    """Califica señales pendientes con fecha anterior a hoy. Devuelve líneas para el mensaje."""
    rows = read_rows()
    if not rows:
        return []
    signals, _ = load_tracker(AGENT_CSV)
    by_row = {s.row: s for s in signals}
    lines = []
    for i, row in enumerate(rows, start=1):
        if row.get("status") != "pending" or row.get("signal_date", "") >= today.isoformat():
            continue
        s = by_row.get(i)
        if s is None:
            continue
        ticks = iter_ticks("XAUUSD", s.start_utc, s.start_utc + timedelta(hours=24), ROOT / "data" / "ticks")
        r = simulate(s, ticks)
        if r.status != "filled":
            row["status"] = "not_filled" if r.status == "not_filled" else r.status
            row["outcome"] = r.status
            row["result_r"] = "0"
            lines.append("%s %s %s-%s: no se llenó" % (s.signal_date, s.direction, s.entry_low, s.entry_high))
            continue
        nb = r.paths["no_be"]
        if nb.outcome == "open":
            continue  # sigue abierta dentro del horizonte; se califica otro día
        row["status"] = {"SL": "closed_sl", "BE": "closed_be"}.get(nb.outcome, "closed_" + nb.outcome.lower())
        row["outcome"] = "%s | sin BE %+.2fR, tercios %+.2fR, BE10 %+.2fR" % (
            nb.outcome, nb.r_full, nb.r_thirds, r.paths["be_after_min"].r_full)
        row["result_r"] = "%.3f" % nb.r_full
        lines.append("%s %s %s-%s → %s %+.2fR (tercios %+.2fR)" % (
            s.signal_date, s.direction, s.entry_low, s.entry_high, nb.outcome, nb.r_full, nb.r_thirds))
    if not dry_run:
        write_rows(rows)
    return lines


def scoreboard() -> str:
    rows = [r for r in read_rows() if r.get("status", "").startswith("closed")]
    if not rows:
        return "Marcador: sin señales cerradas todavía."
    rs = [float(r["result_r"]) for r in rows if r.get("result_r")]
    wins = sum(1 for x in rs if x > 0)
    losses = sum(1 for x in rs if x < 0)
    bes = len(rs) - wins - losses
    return "Marcador (sin BE, posición completa): %d ganadas, %d perdidas, %d BE | %+.2fR en %d señales" % (
        wins, losses, bes, sum(rs), len(rs))


def _num(v) -> str:
    return "%g" % float(v)


def format_signal(row: dict, live: float) -> str:
    """Mismo formato que las señales del canal. "Entrada ahora" solo si el precio
    en vivo ya está dentro de la zona; si no, es una entrada pendiente en la zona."""
    lo, hi = float(row["entry_low"]), float(row["entry_high"])
    buy = row["direction"] == "BUY"
    zona = "%s-%s" % ((_num(hi), _num(lo)) if buy else (_num(lo), _num(hi)))
    modo = "Entrada ahora 🔴" if lo <= live <= hi else "Entrada pendiente en zona ⏳"
    return ("%s XAUUSD — %s\n\n✔️ Entrada: %s\n\n🚫 SL: %s\n💰 TP1: %s\n💰 TP2: %s\n💰 TP3: %s\n\nPrecio en vivo: %.2f"
            % (row["direction"], modo, zona, _num(row["stop_loss"]), _num(row["tp1"]), _num(row["tp2"]),
               _num(row["tp3"]), live))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--no-refresh", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--telegram-chat-id", action="store_true")
    args = ap.parse_args(argv)

    if args.telegram_chat_id:
        telegram_print_chat_ids()
        return 0

    now = datetime.now(timezone.utc)
    try:
        if not args.no_refresh:
            refresh_candles()
        scored = score_pending(now.date(), args.dry_run)
        for ln in scored:
            log("calificada: " + ln)
        if args.score_only:
            msg = "Resultados:\n" + "\n".join(scored) + "\n\n" + scoreboard() if scored else scoreboard()
            if not args.dry_run:
                telegram_send(msg)
            return 0

        live = live_price()
        daily = recent_daily_bars()
        prompt = build_prompt(live, daily)
        sig = None
        reason = ""
        for attempt in range(2):
            out = run_agent(prompt if attempt == 0 else prompt + "\n\nYour previous answer was rejected: %s. Fix it." % reason)
            sig = extract_signal(out)
            if sig is None:
                reason = "no JSON signal found in the answer"
                log("intento %d: sin JSON en la respuesta" % (attempt + 1))
                continue
            reason = validate_signal(sig, live)
            if not reason:
                break
            log("intento %d: rechazada (%s): %s" % (attempt + 1, reason, json.dumps(sig)))
        if sig is None or reason:
            msg = "XAUUSD %s: el agente no produjo una señal válida (%s).\n%s" % (now.strftime("%Y-%m-%d"), reason, scoreboard())
            log(msg)
            if not args.dry_run:
                telegram_send(msg)
            return 1
        if str(sig["direction"]).upper() == "NO_TRADE":
            msg = "XAUUSD %s: sin setup hoy. %s\n%s" % (now.strftime("%Y-%m-%d"), sig.get("rationale", ""), scoreboard())
            log(msg)
            if not args.dry_run:
                telegram_send(msg)
            return 0
        if args.dry_run:
            log("dry-run, señal válida: " + json.dumps(sig))
            return 0
        row = append_signal(sig, live, now)
        msg = format_signal(row, live)
        if scored:
            msg += "\n\nResultados de ayer:\n" + "\n".join(scored)
        msg += "\n\n" + scoreboard()
        log("señal guardada: " + json.dumps(sig))
        telegram_send(msg)
        return 0
    except Exception as e:  # noqa: BLE001
        log("ERROR: %r" % e)
        if not args.dry_run:
            telegram_send("XAUUSD señal diaria: falló (%s). Revisa logs/daily_signal.log" % e)
        raise


if __name__ == "__main__":
    sys.exit(main())
