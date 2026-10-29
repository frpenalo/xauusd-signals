"""Métricas y reporte en Markdown a partir de los resultados de simulación."""
from __future__ import annotations

import csv
import statistics as st
from datetime import datetime
from pathlib import Path

from .signals import Skipped
from .sim import SimResult

PATH_LABELS = {
    "no_be": "Sin break-even",
    "be_after_min": "BE a los 10 min (manejo del canal)",
    "be_after_tp1": "BE al tocar TP1",
}

# Lo que el canal dijo que pasó, traducido a qué debería verse en el mercado.
CLAIM_BY_STATUS = {
    "closed_sl": "SL",
    "closed_tp3": "TP3",
    "closed_be": "BE",
    "closed_be_with_no_be_tp1_comparison": "BE",
    "closed_ambiguous_management": "BE",
    "tp1_reported": "TP1+",
    "tp1_reported_open": "TP1+",
}


def _fmt_t(t: datetime | None) -> str:
    return t.strftime("%Y-%m-%d %H:%M:%SZ") if t else ""


def claim_check(r: SimResult) -> str:
    claim = CLAIM_BY_STATUS.get(r.signal.status, "")
    if not claim or r.status != "filled":
        return "sin verificar"
    be = r.paths["be_after_min"]
    nb = r.paths["no_be"]
    if claim == "TP1+":
        return "coincide" if r.tp_times and r.tp_times[0] else "NO coincide"
    if claim == "SL":
        return "coincide" if nb.outcome == "SL" else "NO coincide (mercado: %s)" % nb.outcome
    if claim == "TP3":
        return "coincide" if nb.outcome.startswith("TP") and nb.outcome == "TP%d" % len(r.signal.tps) else "NO coincide (mercado: %s)" % nb.outcome
    if claim == "BE":
        return "coincide" if be.outcome == "BE" else "NO coincide (mercado con BE: %s)" % be.outcome
    return "sin verificar"


def metrics(rs: list[float]) -> dict:
    if not rs:
        return {}
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x < 0]
    bes = [x for x in rs if x == 0]
    mx = cur = 0
    for x in rs:
        cur = cur + 1 if x < 0 else 0
        mx = max(mx, cur)
    return {
        "n": len(rs), "wins": len(wins), "losses": len(losses), "be": len(bes),
        "sum": round(sum(rs), 2), "avg": round(st.mean(rs), 3), "median": round(st.median(rs), 3),
        "payoff": round(st.mean(wins) / abs(st.mean(losses)), 2) if wins and losses else None,
        "max_consec_loss": mx,
    }


def write_results_csv(results: list[SimResult], path: Path) -> None:
    cols = ["row", "date", "direction", "entry_zone", "stop_loss", "tps", "start_utc", "time_basis",
            "status", "fill_time", "fill_price", "risk_pts", "tp1_time", "tp2_time", "tp3_time", "sl_time",
            "first_event", "mfe_r", "mae_r",
            "no_be_outcome", "no_be_r", "no_be_r_thirds",
            "be10_outcome", "be10_r", "be10_r_thirds",
            "be_tp1_outcome", "be_tp1_r", "be_tp1_r_thirds",
            "channel_status", "channel_claim_check", "note"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in results:
            s = r.signal
            tpt = list(r.tp_times) + [None] * (3 - len(r.tp_times))
            p = lambda k, a: getattr(r.paths[k], a) if k in r.paths else ""
            w.writerow([
                s.row, s.signal_date, s.direction, "%g-%g" % (s.entry_low, s.entry_high), s.stop_loss,
                "/".join("%g" % t for t in s.tps), _fmt_t(s.start_utc), s.time_basis,
                r.status, _fmt_t(r.fill_time), r.fill_price and round(r.fill_price, 3), r.risk and round(r.risk, 3),
                _fmt_t(tpt[0]), _fmt_t(tpt[1]), _fmt_t(tpt[2]), _fmt_t(r.sl_time),
                r.first_event, r.mfe_r, r.mae_r,
                p("no_be", "outcome"), p("no_be", "r_full"), p("no_be", "r_thirds"),
                p("be_after_min", "outcome"), p("be_after_min", "r_full"), p("be_after_min", "r_thirds"),
                p("be_after_tp1", "outcome"), p("be_after_tp1", "r_full"), p("be_after_tp1", "r_thirds"),
                s.status, claim_check(r), r.note,
            ])


def _metrics_table(results: list[SimResult]) -> list[str]:
    lines = ["| Manejo | n | Gana | Pierde | BE | R total | R prom | R mediana | Payoff | Máx. pérdidas seguidas |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for key, label in PATH_LABELS.items():
        for variant, suffix in (("r_full", "posición completa"), ("r_thirds", "en tercios")):
            rs = [getattr(r.paths[key], variant) for r in results
                  if r.status == "filled" and r.paths[key].outcome != "open" and getattr(r.paths[key], variant) is not None]
            m = metrics(rs)
            if not m:
                continue
            lines.append("| %s, %s | %d | %d | %d | %d | %+.2f | %+.3f | %+.3f | %s | %d |" % (
                label, suffix, m["n"], m["wins"], m["losses"], m["be"], m["sum"], m["avg"], m["median"],
                m["payoff"] if m["payoff"] is not None else "n/a", m["max_consec_loss"]))
    return lines


def write_report_md(results: list[SimResult], skipped: list[Skipped], path: Path, *, symbol: str,
                    tracker: Path, be_minutes: int) -> None:
    filled = [r for r in results if r.status == "filled"]
    closed_all = [r for r in filled if all(p.outcome != "open" for p in r.paths.values())]
    checks = [claim_check(r) for r in results]
    agree = sum(1 for c in checks if c == "coincide")
    disagree = sum(1 for c in checks if c.startswith("NO"))
    lines = [
        "# Verificación de señales XAUUSD contra el mercado",
        "",
        "Fuente de precios: ticks bid/ask de Dukascopy (%s spot). Tracker: `%s`. Generado %s." % (
            symbol, tracker.name, datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")),
        "",
        "## Resumen",
        "",
        "- Señales en el tracker: %d. Verificables (dirección + zona + SL + TP): %d. Omitidas: %d." % (
            len(results) + len(skipped), len(results), len(skipped)),
        "- Llenadas en el mercado: %d de %d. Con desenlace cerrado en todos los manejos: %d." % (
            len(filled), len(results), len(closed_all)),
        "- Reportes del canal contrastados: %d coinciden, %d no coinciden, %d sin verificar." % (
            agree, disagree, len(checks) - agree - disagree),
        "- Horas con base `eastern_assumed` o `date_only` tienen menos certeza sobre el momento exacto de la señal; `date_only` arranca a las 00:00 UTC del día y puede llenarse antes de que la señal existiera.",
        "",
        "## Métricas (solo señales llenadas y cerradas)",
        "",
    ]
    lines += _metrics_table(results)
    lines += ["", "Lectura: R = resultado dividido entre el riesgo (entrada a stop). 'En tercios' cierra un tercio en cada TP y el resto al stop vigente. BE a los %d min replica lo que hace el canal." % be_minutes, ""]
    lines += ["## Señal por señal", "",
              "| # | Fecha | Dir | Zona | SL | TPs | Inicio (UTC) | Base hora | Llenado | Riesgo | 1er evento | TP1 | TP2 | TP3 | SL | MFE R | MAE R | Sin BE | BE 10m | BE tras TP1 | Canal dijo | Contraste |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        s = r.signal
        tpt = list(r.tp_times) + [None] * (3 - len(r.tp_times))
        def po(k):
            p = r.paths.get(k)
            if not p:
                return "-"
            return p.outcome if p.r_full is None else "%s %+.2fR" % (p.outcome, p.r_full)
        lines.append("| %d | %s | %s | %g-%g | %g | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            s.row, s.signal_date, s.direction, s.entry_low, s.entry_high, s.stop_loss,
            "/".join("%g" % t for t in s.tps), s.start_utc.strftime("%m-%d %H:%M"), s.time_basis,
            ("%s @%.2f" % (r.fill_time.strftime("%H:%M"), r.fill_price)) if r.fill_time else r.status,
            ("%.1f" % r.risk) if r.risk else "", r.first_event or "",
            tpt[0].strftime("%H:%M") if tpt[0] else "", tpt[1].strftime("%H:%M") if tpt[1] else "",
            tpt[2].strftime("%H:%M") if tpt[2] else "", r.sl_time.strftime("%H:%M") if r.sl_time else "",
            r.mfe_r if r.mfe_r is not None else "", r.mae_r if r.mae_r is not None else "",
            po("no_be"), po("be_after_min"), po("be_after_tp1"), s.status, claim_check(r)))
    if skipped:
        lines += ["", "## Omitidas", ""]
        for k in skipped:
            lines.append("- Fila %d (%s): %s" % (k.row, k.signal_date, k.reason))
    lines += ["", "## Lo que esto no es", "",
              "- No es una recomendación de operar. Es la verificación de lo que el mercado hizo después de cada señal publicada.",
              "- Los llenados asumen que la orden se ejecuta en cuanto el precio toca la zona, sin deslizamiento.",
              "- La muestra sigue siendo chica; ninguna métrica aquí es estadísticamente concluyente.", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
