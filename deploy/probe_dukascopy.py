"""Sonda de solo lectura: mide cómo limita Dukascopy los pedidos desde esta máquina.

No escribe nada en disco. Hace unos 21 pedidos de archivos chicos (un día viejo de
octubre de 2026) y tarda entre 3 y 7 minutos. Sirve para elegir la pausa entre
pedidos y saber si una sola conexión persistente evita los cuelgues.

Uso: python3 probe_dukascopy.py
"""
import http.client
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (xauusd-signals verifier)"
HOST = "datafeed.dukascopy.com"
TIMEOUT = 12
RESET_S = 40  # espera entre series para que el limitador se olvide de la anterior


def path(i: int) -> str:
    # El mes va 0-indexado: 09 = octubre. Jueves 1-oct-2026, una hora distinta por pedido.
    return "/datafeed/XAUUSD/2026/09/01/%02dh_ticks.bi5" % (i % 24)


def one_shot(i: int) -> tuple[str, int, float]:
    t = time.time()
    try:
        req = urllib.request.Request("https://%s%s" % (HOST, path(i)), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read()
            return str(r.status), len(body), time.time() - t
    except urllib.error.HTTPError as e:
        return str(e.code), 0, time.time() - t
    except Exception as e:  # noqa: BLE001
        return type(e).__name__, 0, time.time() - t


def series_new_connections(pause: float, start: int, n: int = 5) -> None:
    print("\nConexión nueva por pedido, pausa %g s:" % pause, flush=True)
    ok = 0
    for k in range(n):
        code, size, took = one_shot(start + k)
        ok += code == "200"
        print("  pedido %d: %s  %6d bytes  %.1f s" % (k + 1, code, size, took), flush=True)
        if k < n - 1:
            time.sleep(pause)
    print("  -> %d de %d respondieron 200" % (ok, n), flush=True)


def series_persistent(start: int, n: int = 6, pause: float = 1.0) -> None:
    print("\nUna sola conexión persistente, pausa %g s:" % pause, flush=True)
    ok = 0
    conn = http.client.HTTPSConnection(HOST, timeout=TIMEOUT)
    try:
        for k in range(n):
            t = time.time()
            try:
                conn.request("GET", path(start + k), headers={"User-Agent": UA, "Connection": "keep-alive"})
                r = conn.getresponse()
                size = len(r.read())
                code = str(r.status)
            except Exception as e:  # noqa: BLE001
                code, size = type(e).__name__, 0
                conn.close()
                conn = http.client.HTTPSConnection(HOST, timeout=TIMEOUT)
            ok += code == "200"
            print("  pedido %d: %s  %6d bytes  %.1f s" % (k + 1, code, size, time.time() - t), flush=True)
            if k < n - 1:
                time.sleep(pause)
    finally:
        conn.close()
    print("  -> %d de %d respondieron 200" % (ok, n), flush=True)


if __name__ == "__main__":
    series_persistent(start=0)
    for idx, pause in enumerate((3.0, 8.0, 15.0)):
        time.sleep(RESET_S)
        series_new_connections(pause, start=6 + idx * 5)
