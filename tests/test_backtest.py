import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import backtest
from verifier.dukascopy import Tick
from verifier.sim import simulate


class BuildSignal(unittest.TestCase):
    CTX = backtest.DayContext(date(2026, 9, 2), datetime(2026, 9, 2, 11, 0, tzinfo=timezone.utc), live=4309.0, y_close=4324.0)

    def test_momentum_sells_after_a_down_move_with_pullback_zone(self):
        sig = backtest.build_signal(self.CTX, backtest.Variant("momentum", 5.0, 8.0, 0.0))
        self.assertEqual(sig.direction, "SELL")
        self.assertEqual((sig.entry_low, sig.entry_high), (4312.5, 4315.5))
        self.assertEqual(sig.stop_loss, 4323.5)           # borde alto + 8
        self.assertEqual(sig.tps, [4304.5, 4295.0, 4285.5])  # 1R, 2R, 3R con R = 9.5
        self.assertEqual(sig.time_basis, "explicit_utc")

    def test_contra_buys_after_a_down_move(self):
        sig = backtest.build_signal(self.CTX, backtest.Variant("contra", 3.0, 6.0, 0.0))
        self.assertEqual(sig.direction, "BUY")
        self.assertEqual((sig.entry_low, sig.entry_high), (4304.5, 4307.5))
        self.assertEqual(sig.stop_loss, 4298.5)

    def test_min_move_filters_small_days(self):
        self.assertIsNone(backtest.build_signal(self.CTX, backtest.Variant("momentum", 5.0, 8.0, 20.0)))


class DayContexts(unittest.TestCase):
    def test_reads_price_at_cutoff_and_previous_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "c.csv"
            p.write_text("date,open,high,low,close,volume\n"
                         "2026-09-01T20:00:00Z,1,1,1,4300,1\n"
                         "2026-09-01T21:59:00Z,1,1,1,4310,1\n"
                         "2026-09-02T10:59:00Z,1,1,1,4290,1\n"
                         "2026-09-02T11:00:00Z,1,1,1,4999,1\n"
                         "2026-09-02T15:00:00Z,1,1,1,4280,1\n", encoding="utf-8")
            ctxs = backtest.load_day_contexts(p, date(2026, 9, 2), date(2026, 9, 2))
        self.assertEqual(len(ctxs), 1)
        self.assertEqual((ctxs[0].live, ctxs[0].y_close), (4290.0, 4310.0))
        self.assertEqual(ctxs[0].cutoff.hour, 11)


class TallyTests(unittest.TestCase):
    def test_tally_tracks_streak_and_drawdown(self):
        ctx = BuildSignal.CTX
        sig = backtest.build_signal(ctx, backtest.Variant("momentum", 5.0, 8.0, 0.0))
        t0 = ctx.cutoff
        # Llena en la zona (bid >= 4312.5) y luego salta el stop (ask >= 4323.5).
        losing = [Tick(t0, 4313.0, 4313.3), Tick(t0.replace(minute=5), 4324.0, 4324.3)]
        # Llena y baja hasta TP3 (ask <= 4285.5).
        winning = [Tick(t0, 4313.0, 4313.3), Tick(t0.replace(minute=5), 4284.0, 4284.3)]
        tally = backtest.Tally()
        tally.add(simulate(sig, losing))
        tally.add(simulate(sig, losing))
        tally.add(simulate(sig, winning))
        self.assertEqual((tally.n, tally.filled, tally.wins, tally.losses), (3, 3, 1, 2))
        self.assertEqual(tally.worst_streak, 2)
        self.assertAlmostEqual(tally.max_dd, 2.0)
        # El llenado es al bid del primer tick en la zona (4313), no al centro: R del TP3 = 27.5 / 10.5.
        self.assertAlmostEqual(tally.r_full, 27.5 / 10.5 - 2.0, places=3)


if __name__ == "__main__":
    unittest.main()
