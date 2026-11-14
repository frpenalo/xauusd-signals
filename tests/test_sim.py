"""Pruebas sin red: simulación sobre ticks sintéticos y lectura del tracker."""
import csv
import io
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from verifier.dukascopy import Tick
from verifier.signals import Signal, load_tracker, parse_start
from verifier.sim import simulate

T0 = datetime(2026, 7, 13, 11, 0, tzinfo=timezone.utc)
SPREAD = 0.9


def ticks(path, step_s=30, start=T0):
    """path = lista de precios bid; el ask va SPREAD arriba."""
    return [Tick(start + timedelta(seconds=i * step_s), p, p + SPREAD) for i, p in enumerate(path)]


def sell_signal(**kw):
    base = dict(row=1, signal_date=date(2026, 7, 13), direction="SELL", entry_low=4063, entry_high=4065,
                entry_used=4064, stop_loss=4072, tps=[4056, 4050, 4046], start_utc=T0, time_basis="explicit_utc")
    base.update(kw)
    return Signal(**base)


class SellPaths(unittest.TestCase):
    def test_runs_to_tp3_without_be(self):
        # sube a la zona, baja a TP3 sin volver a la entrada
        s = sell_signal()
        r = simulate(s, ticks([4060, 4063.5, 4058, 4055, 4049, 4045]))
        self.assertEqual(r.status, "filled")
        self.assertEqual(r.fill_price, 4063.5)
        self.assertEqual(r.paths["no_be"].outcome, "TP3")
        self.assertAlmostEqual(r.paths["no_be"].r_full, (4063.5 - 4046) / (4072 - 4063.5), places=3)
        self.assertEqual(r.first_event, "TP1")

    def test_be_after_minutes_turns_win_into_zero(self):
        # a los 10 min el stop pasa a la entrada; el precio vuelve y toca BE, luego cae a TP3
        s = sell_signal()
        path = [4060, 4064] + [4061] * 25 + [4063.5, 4055, 4049, 4045]  # 25 ticks de 30s = 12.5 min
        r = simulate(s, ticks(path))
        self.assertEqual(r.paths["no_be"].outcome, "TP3")
        self.assertEqual(r.paths["be_after_min"].outcome, "BE")
        self.assertEqual(r.paths["be_after_min"].r_full, 0.0)
        self.assertEqual(r.paths["be_after_tp1"].outcome, "TP3")

    def test_stop_uses_ask(self):
        # el bid nunca llega al stop pero el ask sí (spread)
        s = sell_signal()
        r = simulate(s, ticks([4064, 4071.5, 4060]))
        self.assertEqual(r.paths["no_be"].outcome, "SL")
        self.assertEqual(r.paths["no_be"].r_full, -1.0)

    def test_thirds_after_tp1_then_be(self):
        s = sell_signal()
        path = [4064, 4055.5, 4064.5, 4070]  # TP1 (ask 4056.4 <= 4056? no) -> usar 4055
        path = [4064, 4055, 4064.5, 4070]
        r = simulate(s, ticks(path))
        p = r.paths["be_after_tp1"]
        self.assertEqual(p.outcome, "BE")
        risk = 4072 - 4064
        expected = ((4064 - 4056) / risk + 0 + 0) / 3
        self.assertAlmostEqual(p.r_thirds, expected, places=3)

    def test_invalidated_when_already_past_stop(self):
        s = sell_signal()
        r = simulate(s, ticks([4073, 4060]))
        self.assertEqual(r.status, "invalidated")

    def test_not_filled_in_window(self):
        s = sell_signal()
        r = simulate(s, ticks([4050] * 10, step_s=3600))
        self.assertEqual(r.status, "not_filled")

    def test_date_only_waits_for_approach_from_below(self):
        # sin hora: a medianoche el precio ya está por encima del stop; no se invalida,
        # espera a que baje bajo la zona y vuelva a subir a ella
        s = sell_signal(time_basis="date_only")
        r = simulate(s, ticks([4075, 4070, 4062, 4064, 4055, 4064.2, 4050, 4045]))
        self.assertEqual(r.status, "filled")
        # 4062 no basta (no llegó al nivel de TP1 4056); 4055 sí, y el llenado es el 4064.2
        self.assertEqual(r.fill_price, 4064.2)
        self.assertEqual(r.paths["no_be"].outcome, "TP3")

    def test_date_only_does_not_fill_if_already_in_zone(self):
        s = sell_signal(time_basis="date_only")
        r = simulate(s, ticks([4064, 4066, 4073, 4095.9, 4064], step_s=3600))
        self.assertEqual(r.status, "not_filled")

    def test_buy_fills_on_ask(self):
        s = sell_signal(direction="BUY", entry_low=3974, entry_high=3976, stop_loss=3965, tps=[3984, 3995, 4005])
        r = simulate(s, ticks([3978, 3975, 3964.5]))  # ask 3975.9 entra; bid 3964.5 toca SL
        self.assertEqual(r.status, "filled")
        self.assertAlmostEqual(r.fill_price, 3975 + SPREAD)
        self.assertEqual(r.paths["no_be"].outcome, "SL")


class TimeParsing(unittest.TestCase):
    def test_eastern_ampm_in_july_is_edt(self):
        t, basis = parse_start(date(2026, 7, 13), "7:11 AM", "")
        self.assertEqual((t.hour, t.minute, basis), (11, 11, "eastern_assumed"))

    def test_explicit_utc(self):
        t, basis = parse_start(date(2026, 7, 15), "13:07 UTC", "")
        self.assertEqual((t.hour, basis), (13, "explicit_utc"))

    def test_received_at_fallback_and_date_only(self):
        t, basis = parse_start(date(2026, 7, 15), "", "2026-07-15T10:57:00Z")
        self.assertEqual((t.hour, basis), (10, "received_at"))
        t, basis = parse_start(date(2026, 7, 22), "", "2026-07-22T00:00:00Z")
        self.assertEqual((t.hour, basis), (0, "date_only"))


class TrackerLoading(unittest.TestCase):
    def test_skips_partial_rows(self):
        rows = [
            {"signal_date": "2026-07-15", "signal_time": "", "received_at_utc": "", "direction": "SELL",
             "entry_low": "4076", "entry_high": "4079", "entry_used": "", "stop_loss": "", "tp1": "", "tp2": "", "tp3": ""},
            {"signal_date": "2026-07-15", "signal_time": "", "received_at_utc": "", "direction": "",
             "entry_low": "4039.8", "entry_high": "4039.8", "entry_used": "", "stop_loss": "4039.8", "tp1": "", "tp2": "", "tp3": ""},
            {"signal_date": "2026-07-22", "signal_time": "", "received_at_utc": "", "direction": "SELL",
             "entry_low": "4133", "entry_high": "4129", "entry_used": "4131", "stop_loss": "4137", "tp1": "4123", "tp2": "", "tp3": ""},
        ]
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.csv"
            with p.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)
            signals, skipped = load_tracker(p)
        self.assertEqual(len(signals), 1)
        self.assertEqual((signals[0].entry_low, signals[0].entry_high), (4129.0, 4133.0))
        self.assertEqual(len(skipped), 2)




class SettledHours(unittest.TestCase):
    def test_recent_hours_are_not_cacheable(self):
        from datetime import datetime, timezone
        from verifier.dukascopy import is_settled
        now = datetime(2026, 11, 12, 12, 0, tzinfo=timezone.utc)
        self.assertFalse(is_settled(datetime(2026, 11, 12, 11, 0, tzinfo=timezone.utc), now))
        self.assertFalse(is_settled(datetime(2026, 11, 12, 6, 0), now))   # terminó hace 5 h
        self.assertTrue(is_settled(datetime(2026, 11, 12, 5, 0), now))    # terminó hace 6 h


class FetchHour(unittest.TestCase):
    def test_retries_on_cut_and_503_then_caches_settled_hour(self):
        import tempfile
        from datetime import datetime, timezone
        from pathlib import Path
        from unittest import mock
        from verifier import dukascopy
        answers = [ConnectionResetError("corte"), (503, b""), (200, b"datos")]

        def fake_get(url, timeout):
            a = answers.pop(0)
            if isinstance(a, Exception):
                raise a
            return a

        hour = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(dukascopy, "_get", fake_get),                 mock.patch.object(dukascopy.time, "sleep"):
            self.assertEqual(dukascopy.fetch_hour("XAUUSD", hour, Path(tmp)), b"datos")
            self.assertEqual(answers, [])
            self.assertEqual(dukascopy.hour_cache_path(Path(tmp), "XAUUSD", hour).read_bytes(), b"datos")

    def test_404_is_an_empty_hour_and_recent_hours_are_not_cached(self):
        import tempfile
        from datetime import datetime, timedelta, timezone
        from pathlib import Path
        from unittest import mock
        from verifier import dukascopy
        recent = (datetime.now(timezone.utc) - timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(dukascopy, "_get", lambda u, t: (404, b"x")),                 mock.patch.object(dukascopy.time, "sleep"):
            self.assertEqual(dukascopy.fetch_hour("XAUUSD", recent, Path(tmp)), b"")
            self.assertFalse(dukascopy.hour_cache_path(Path(tmp), "XAUUSD", recent).exists())


if __name__ == "__main__":
    unittest.main()
