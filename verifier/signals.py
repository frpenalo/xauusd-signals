"""Lectura del tracker de señales (CSV) y normalización de tiempos a UTC."""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo  # necesita tzdata en Windows
    _ET = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover - fallback sin base de zonas horarias
    _ET = None


def _eastern_offset(d: date) -> timedelta:
    """Horario del Este de EE.UU.: EDT (-4) del 2º domingo de marzo al 1er domingo de noviembre."""
    def nth_sunday(year: int, month: int, n: int) -> date:
        first = date(year, month, 1)
        first_sunday = first + timedelta(days=(6 - first.weekday()) % 7)
        return first_sunday + timedelta(weeks=n - 1)
    start = nth_sunday(d.year, 3, 2)
    end = nth_sunday(d.year, 11, 1)
    return timedelta(hours=-4) if start <= d < end else timedelta(hours=-5)


def eastern_to_utc(d: date, hour: int, minute: int) -> datetime:
    naive = datetime(d.year, d.month, d.day, hour, minute)
    if _ET is not None:
        return naive.replace(tzinfo=_ET).astimezone(timezone.utc)
    return (naive - _eastern_offset(d)).replace(tzinfo=timezone.utc)


_AMPM = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*([AaPp][Mm])\s*$")
_UTC = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*(?:UTC|utc|Z)\s*$")


@dataclass
class Signal:
    row: int
    signal_date: date
    direction: str  # SELL | BUY
    entry_low: float
    entry_high: float
    entry_used: float | None
    stop_loss: float
    tps: list[float]
    start_utc: datetime
    time_basis: str  # explicit_utc | eastern_assumed | received_at | date_only
    source: str = ""
    trader: str = ""
    status: str = ""
    outcome: str = ""
    result_r_text: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def label(self) -> str:
        return "#%02d %s %s %g-%g SL %g" % (self.row, self.signal_date, self.direction,
                                            self.entry_low, self.entry_high, self.stop_loss)


@dataclass
class Skipped:
    row: int
    signal_date: str
    reason: str
    raw: dict


def _num(v: str) -> float | None:
    v = (v or "").strip()
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_start(signal_date: date, signal_time: str, received_at: str) -> tuple[datetime, str]:
    m = _UTC.match(signal_time or "")
    if m:
        return datetime(signal_date.year, signal_date.month, signal_date.day,
                        int(m.group(1)), int(m.group(2)), tzinfo=timezone.utc), "explicit_utc"
    m = _AMPM.match(signal_time or "")
    if m:
        h = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
        return eastern_to_utc(signal_date, h, int(m.group(2))), "eastern_assumed"
    if received_at:
        try:
            r = datetime.fromisoformat(received_at.replace("Z", "+00:00")).astimezone(timezone.utc)
            if r.date() == signal_date and (r.hour, r.minute, r.second) != (0, 0, 0):
                return r, "received_at"
        except ValueError:
            pass
    return datetime(signal_date.year, signal_date.month, signal_date.day, tzinfo=timezone.utc), "date_only"


def load_tracker(path: Path) -> tuple[list[Signal], list[Skipped]]:
    signals: list[Signal] = []
    skipped: list[Skipped] = []
    with path.open(encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), start=1):
            d = (r.get("signal_date") or "").strip()
            direction = (r.get("direction") or "").strip().upper()
            lo, hi, sl = _num(r.get("entry_low")), _num(r.get("entry_high")), _num(r.get("stop_loss"))
            tps = [t for t in (_num(r.get(k)) for k in ("tp1", "tp2", "tp3")) if t is not None]
            if direction not in ("SELL", "BUY"):
                skipped.append(Skipped(i, d, "sin dirección (actualización huérfana)", r)); continue
            if lo is None or hi is None or sl is None or not tps:
                skipped.append(Skipped(i, d, "faltan entry/SL/TP", r)); continue
            if lo == hi == sl:
                skipped.append(Skipped(i, d, "entrada igual al stop (registro de break-even, no señal)", r)); continue
            if lo > hi:
                lo, hi = hi, lo
            sd = date.fromisoformat(d)
            start, basis = parse_start(sd, r.get("signal_time") or "", r.get("received_at_utc") or "")
            signals.append(Signal(
                row=i, signal_date=sd, direction=direction, entry_low=lo, entry_high=hi,
                entry_used=_num(r.get("entry_used")), stop_loss=sl, tps=tps,
                start_utc=start, time_basis=basis,
                source=(r.get("source_channel") or "").strip(), trader=(r.get("trader") or "").strip(),
                status=(r.get("status") or "").strip(), outcome=(r.get("outcome") or "").strip(),
                result_r_text=(r.get("result_r") or "").strip(), raw=r))
    return signals, skipped
