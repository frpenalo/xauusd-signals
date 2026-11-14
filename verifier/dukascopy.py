"""Descarga y decodificación de ticks de Dukascopy (gratis, sin cuenta).

Formato: un archivo .bi5 por hora UTC, comprimido con LZMA. Cada tick son 20
bytes big-endian: ms desde el inicio de la hora, ask, bid (enteros, escala
1/1000 para XAUUSD), volumen ask, volumen bid (float).

El mes en la URL es 0-indexado (julio = 06). Solo responde por HTTP plano; el
endpoint HTTPS no contesta desde esta red.
"""
from __future__ import annotations

import http.client
import lzma
import os
import struct
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

# Desde la laptop solo responde por HTTP plano; desde el servidor redirige a HTTPS.
BASE_URL = os.environ.get("DUKASCOPY_BASE_URL", "http://datafeed.dukascopy.com/datafeed")
PRICE_SCALE = {"XAUUSD": 1000.0}
TICK_STRUCT = struct.Struct(">3I2f")
USER_AGENT = "Mozilla/5.0 (xauusd-signals verifier)"
REQUEST_PAUSE_S = 1.0
# Dukascopy publica cada hora con retraso. Una hora que terminó hace menos que esto puede venir
# vacía o a medias: se usa pero no se guarda, para no congelar un archivo incompleto en el caché.
SETTLE = timedelta(hours=6)


def is_settled(hour: datetime, now: datetime | None = None) -> bool:
    if hour.tzinfo is None:
        hour = hour.replace(tzinfo=timezone.utc)
    return (now or datetime.now(timezone.utc)) - hour >= timedelta(hours=1) + SETTLE


@dataclass(frozen=True)
class Tick:
    ts: datetime  # UTC
    bid: float
    ask: float


def hour_url(symbol: str, hour: datetime) -> str:
    return "%s/%s/%04d/%02d/%02d/%02dh_ticks.bi5" % (
        BASE_URL, symbol, hour.year, hour.month - 1, hour.day, hour.hour)


def hour_cache_path(root: Path, symbol: str, hour: datetime) -> Path:
    return root.joinpath(symbol, "%04d" % hour.year, "%02d" % hour.month, "%02d" % hour.day,
                         "%02dh_ticks.bi5" % hour.hour)


_conn: tuple[str, str, http.client.HTTPConnection] | None = None


def _close() -> None:
    global _conn
    if _conn is not None:
        try:
            _conn[2].close()
        finally:
            _conn = None


def _get(url: str, timeout: int) -> tuple[int, bytes]:
    """GET por una sola conexión persistente, reutilizada entre pedidos.

    Medido el 14-nov-2026 desde el servidor: Dukascopy castiga cada conexión nueva
    (503 o cuelgue aunque se espere 15 s), y por una conexión reutilizada responde
    en 0.3 s por archivo. Si la conexión se cae, se cierra y el siguiente pedido abre otra.
    """
    global _conn
    parts = urllib.parse.urlsplit(url)
    if _conn is None or _conn[:2] != (parts.scheme, parts.netloc):
        _close()
        cls = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
        _conn = (parts.scheme, parts.netloc, cls(parts.netloc, timeout=timeout))
    try:
        _conn[2].request("GET", parts.path, headers={"User-Agent": USER_AGENT, "Connection": "keep-alive"})
        resp = _conn[2].getresponse()
        return resp.status, resp.read()
    except Exception:
        _close()
        raise


def fetch_hour(symbol: str, hour: datetime, cache_root: Path, retries: int = 10, timeout: int = 30) -> bytes:
    """Devuelve los bytes .bi5 de una hora, usando el caché en disco si existe.

    Una hora sin ticks (fin de semana) se guarda como archivo vacío para no
    volver a pedirla. Ante un 503 o un corte se reintenta con espera creciente,
    y se deja una pausa corta entre pedidos.
    """
    path = hour_cache_path(cache_root, symbol, hour)
    if path.exists():
        return path.read_bytes()
    url = hour_url(symbol, hour)
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            status, raw = _get(url, timeout)
        except (http.client.HTTPException, TimeoutError, OSError) as e:
            last_err = e
        else:
            if status == 200:
                time.sleep(REQUEST_PAUSE_S)
                break
            if status == 404:
                raw = b""
                break
            last_err = RuntimeError("HTTP %d" % status)
        time.sleep(min(90.0, 3.0 * 2 ** attempt))
    else:
        raise RuntimeError("Dukascopy no respondió para %s: %s" % (url, last_err))
    if is_settled(hour):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return raw


def decode_hour(raw: bytes, symbol: str, hour: datetime) -> list[Tick]:
    if not raw:
        return []
    data = lzma.decompress(raw)
    scale = PRICE_SCALE.get(symbol, 1000.0)
    base = hour.replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    ticks = []
    for off in range(0, len(data) - len(data) % TICK_STRUCT.size, TICK_STRUCT.size):
        ms, ask, bid, _av, _bv = TICK_STRUCT.unpack_from(data, off)
        ticks.append(Tick(base + timedelta(milliseconds=ms), bid / scale, ask / scale))
    return ticks


def iter_ticks(symbol: str, start: datetime, end: datetime, cache_root: Path) -> Iterator[Tick]:
    """Itera ticks en [start, end) hora por hora, descargando solo lo necesario."""
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start y end deben ser datetimes con zona (UTC)")
    hour = start.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
    end = end.astimezone(timezone.utc)
    while hour < end:
        for t in decode_hour(fetch_hour(symbol, hour, cache_root), symbol, hour):
            if start <= t.ts < end:
                yield t
        hour += timedelta(hours=1)
