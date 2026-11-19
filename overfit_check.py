"""¿Ventaja o suerte? Pruebas estadísticas sobre el backtest de tres años y sobre el agente.

Lee el resultado diario de cada variante que deja `backtest_be.py --trades-out` (R por día,
0 los días sin operación; stop al precio real del tick, abiertas cerradas a las 24 h) y responde:

1. Reality Check / SPA de Hansen (librería arch): si ninguna variante tuviera ventaja real,
   ¿qué tan seguido la MEJOR de las 18 se vería tan bien como la que encontramos? Es la prueba
   que corrige por haber probado muchas variantes. p bajo (< 0.05) = difícil de explicar por suerte.
2. Probabilidad de sobreajuste (PBO, Bailey y otros, validación cruzada combinatoria): se parte
   la historia en 16 tramos, se elige la mejor variante en la mitad de ellos y se mira en qué
   puesto queda en la otra mitad, para las 12,870 formas de partir. PBO = fracción de veces que
   la elegida queda en la mitad de abajo fuera de muestra. 50 % = elegir no sirve de nada.
3. Intervalo de confianza del resultado de la variante del servidor (bootstrap por bloques).
4. Agente: con la dispersión de sus señales del replay, cuántas señales cerradas hacen falta
   para distinguir una ventaja dada de cero.

Necesita numpy, pandas, scipy y arch: correr con .venv-stats (ver README de este reporte).

Uso:
    .venv-stats/Scripts/python overfit_check.py --trades data/derived/trades_3y.csv
"""
from __future__ import annotations

import argparse
import itertools
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from arch.bootstrap import SPA, StationaryBootstrap
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent
LIVE = "momentum pull 5.5 sl 10 min 0"  # la variante que corre en el servidor
BLOCK = 10      # días por bloque del bootstrap: respeta rachas de hasta dos semanas
REPS = 5000
SEED = 20261118
CSCV_BLOCKS = 16


def spa_pvalues(r: np.ndarray) -> tuple[float, float]:
    """p del SPA contra no operar (pérdida = -R, referencia = 0): (consistente, conservador).

    El conservador («upper») equivale al Reality Check de White. Calibrado con azar puro (18
    variantes correlacionadas, 750 días, 200 simulaciones): el consistente da p < 0.05 el 8 % de
    las veces en vez del 5 %, así que para afirmar una ventaja se mira el conservador.
    """
    spa = SPA(np.zeros(r.shape[0]), -r, block_size=BLOCK, reps=REPS, bootstrap="stationary", seed=SEED)
    spa.compute()
    return float(spa.pvalues["consistent"]), float(spa.pvalues["upper"])


def pbo(r: np.ndarray, blocks: int = CSCV_BLOCKS) -> dict[str, float]:
    """Probabilidad de sobreajuste por validación cruzada combinatoria (CSCV), con R medio por día."""
    t, n = r.shape
    parts = np.array_split(np.arange(t), blocks)
    sums = np.stack([r[p].sum(axis=0) for p in parts])
    sizes = np.array([len(p) for p in parts])
    total = sums.sum(axis=0)
    below = 0
    is_best, oos_best, oos_median = [], [], []
    combos = list(itertools.combinations(range(blocks), blocks // 2))
    for comb in combos:
        idx = list(comb)
        is_sum = sums[idx].sum(axis=0)
        oos_sum = total - is_sum
        n_is = sizes[idx].sum()
        best = int(np.argmax(is_sum))
        rank = (oos_sum < oos_sum[best]).sum() + 0.5 * ((oos_sum == oos_sum[best]).sum() - 1) + 1
        below += rank / (n + 1) <= 0.5
        is_best.append(is_sum[best] / n_is)
        oos_best.append(oos_sum[best] / (t - n_is))
        oos_median.append(np.median(oos_sum) / (t - n_is))
    oos_best = np.array(oos_best)
    return {"pbo": below / len(combos), "is": float(np.mean(is_best)), "oos": float(oos_best.mean()),
            "oos_median_variant": float(np.mean(oos_median)), "p_loss": float((oos_best < 0).mean()), "combos": len(combos)}


def total_ci(x: np.ndarray) -> tuple[float, float, float]:
    """IC 95 % del R total y probabilidad de que el total sea <= 0 (bootstrap estacionario)."""
    bs = StationaryBootstrap(BLOCK, x, seed=SEED)
    sims = bs.apply(lambda v: np.array([v.sum()]), REPS)[:, 0]
    return float(np.percentile(sims, 2.5)), float(np.percentile(sims, 97.5)), float((sims <= 0).mean())


def needed(mu: float, sd: float, alpha: float = 0.05, power: float = 0.80) -> float:
    """Señales cerradas para detectar una media mu > 0 (una cola, 5 %) con 80 % de potencia."""
    return ((norm.ppf(1 - alpha) + norm.ppf(power)) * sd / mu) ** 2 if mu > 0 else float("inf")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--trades", type=Path, default=ROOT / "data" / "derived" / "trades_3y.csv")
    ap.add_argument("--replay", type=Path, default=ROOT / "data" / "replay_signals.csv")
    ap.add_argument("--selection-start", type=date.fromisoformat, default=date(2026, 5, 11),
                    help="primer día de la ventana donde se eligió la variante del servidor")
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "overfit_check.md")
    args = ap.parse_args(argv)

    df = pd.read_csv(args.trades, parse_dates=["day"])
    sel = pd.Timestamp(args.selection_start)
    names = {"fijo": "Puntos fijos (la regla tal como corre hoy)", "escalado": "Puntos escalados a la volatilidad"}
    mgmts = {"nobe_r": "sin mover el stop", "be_r": "stop a entrada a los 10 min"}
    L = ["# ¿Ventaja o suerte? · pruebas sobre %s a %s" % (df.day.min().date(), df.day.max().date()), "",
         "R diario de las 18 variantes momentum (0 los días sin operación), stop al precio real del tick y abiertas "
         "cerradas a las 24 h. Bootstrap estacionario con bloques de %d días, %d repeticiones, semilla %d. "
         "La variante del servidor es «%s»." % (BLOCK, REPS, SEED, LIVE), "",
         "Cómo leerlo: **p del Reality Check** = probabilidad de ver una mejor variante así de buena si ninguna tuviera "
         "ventaja real (menos de 0.05 = difícil de explicar por suerte). **PBO** = de todas las formas de partir la "
         "historia en dos mitades, en qué fracción la variante elegida en una mitad queda en la mitad de abajo del "
         "ranking en la otra (50 % = elegir no sirve).", ""]

    for (fam, cost), g in df.groupby(["family", "cost"], sort=True):
        L += ["## %s · costo extra %.2f puntos" % (names.get(fam, fam), cost), ""]
        for col, mg in mgmts.items():
            m = g.pivot(index="day", columns="variant", values=col).sort_index().fillna(0.0)
            r = m.to_numpy()
            live = m[LIVE].to_numpy()
            windows = [("Tres años completos", np.ones(len(m), bool)),
                       ("Antes de la ventana de selección (hasta %s)" % (sel - pd.Timedelta(days=1)).date(), (m.index < sel)),
                       ("Ventana de selección (desde %s)" % sel.date(), (m.index >= sel))]
            L += ["### Manejo: %s" % mg, "",
                  "| Tramo | Días | Mejor variante: R total | Mediana de las 18 | p del Reality Check | p conservador | Variante del servidor: R total | IC 95 % | Prob. de total ≤ 0 |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for label, mask in windows:
                rr, lv = r[mask], live[mask]
                tot = rr.sum(axis=0)
                lo, hi, p0 = total_ci(lv)
                pc, pu = spa_pvalues(rr)
                L.append("| %s | %d | %+.1f | %+.1f | %.3f | %.3f | %+.1f | %+.1f a %+.1f | %.0f%% |" % (
                    label, mask.sum(), tot.max(), np.median(tot), pc, pu, lv.sum(), lo, hi, 100 * p0))
            if col == "nobe_r":
                gl = g[g["variant"] == LIVE]
                L += ["", "Variante del servidor por dirección (el oro pasó de unos 1,950 a más de 4,000 en estos tres años, "
                      "así que comprar con stop ancho y cerrar a las 24 h gana aunque la señal no aporte nada):", "",
                      "| Tramo | Dirección | Días | Operaciones | R total | IC 95 % | Prob. de total ≤ 0 | Abiertas a 24 h | R de las abiertas |",
                      "|---|---|---|---|---|---|---|---|---|"]
                for label, mask in windows:
                    for side, name in (("BUY", "Compras"), ("SELL", "Ventas")):
                        x = gl[gl["side"] == side].set_index("day").reindex(m.index[mask]).dropna(subset=["nobe_r"])
                        op = x[x["nobe_kind"] == "open"]
                        lo, hi, p0 = total_ci(x["nobe_r"].to_numpy())
                        L.append("| %s | %s | %d | %d | %+.1f | %+.1f a %+.1f | %.0f%% | %d | %+.1f |" % (
                            label, name, len(x), (x["nobe_kind"] != "none").sum(), x["nobe_r"].sum(), lo, hi, 100 * p0,
                            len(op), op["nobe_r"].sum()))
            o = pbo(r)
            L += ["", "Sobreajuste (CSCV, %d tramos, %d particiones): **PBO %.0f%%**. La variante elegida en la mitad de "
                  "entrenamiento rinde %+.3f R por día ahí y %+.3f R por día en la otra mitad (la variante mediana rinde "
                  "%+.3f fuera de muestra); en el %.0f%% de las particiones la elegida pierde fuera de muestra." % (
                      CSCV_BLOCKS, o["combos"], 100 * o["pbo"], o["is"], o["oos"], o["oos_median_variant"], 100 * o["p_loss"]), ""]

    if args.replay.exists():
        rp = pd.read_csv(args.replay)
        closed = rp[rp["status"].astype(str).str.startswith("closed")]
        x = closed["result_r"].astype(float).to_numpy()
        rng = np.random.default_rng(SEED)
        sims = rng.choice(x, size=(REPS, len(x)), replace=True).mean(axis=1)
        mu, sd = float(x.mean()), float(x.std(ddof=1))
        span = pd.to_datetime(rp["signal_date"])
        weekdays = np.busday_count(span.min().date(), span.max().date()) + 1
        per_month = len(x) / weekdays * 21
        L += ["## Agente · cuántas señales hacen falta", "",
              "Replay del agente (%s a %s): %d señales emitidas en %d días hábiles, %d cerradas (%d ganadas, %d perdidas), "
              "%+.2f R en total. Media %+.3f R por señal cerrada, desviación %.2f R. IC 95 %% de la media (bootstrap): "
              "%+.2f a %+.2f R; probabilidad de que la media real sea ≤ 0: %.0f%%." % (
                  span.min().date(), span.max().date(), len(rp), weekdays, len(x), (x > 0).sum(), (x < 0).sum(), x.sum(),
                  mu, sd, np.percentile(sims, 2.5), np.percentile(sims, 97.5), 100 * (sims <= 0).mean()), "",
              "Señales cerradas necesarias para distinguir de cero una ventaja real dada (prueba de una cola al 5 %%, "
              "80 %% de probabilidad de detectarla), con esa desviación y a %.1f señales cerradas por mes:" % per_month, "",
              "| Ventaja real por señal | Señales cerradas | Meses |", "|---|---|---|"]
        for label, m_ in [("%+.2f R (la observada en el replay)" % mu, mu), ("+0.10 R", 0.10), ("+0.20 R", 0.20),
                          ("+0.30 R", 0.30), ("+0.50 R", 0.50)]:
            n = needed(m_, sd)
            L.append("| %s | %s | %s |" % (label, "%.0f" % n if np.isfinite(n) else "no aplica",
                                           "%.0f" % (n / per_month) if np.isfinite(n) else "no aplica"))
        L.append("")

    text = "\n".join(L) + "\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(text.encode("utf-8"))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
