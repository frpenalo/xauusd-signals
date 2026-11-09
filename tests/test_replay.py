import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

import replay


class CutoffAndCalendar(unittest.TestCase):
    def test_cutoff_follows_eastern_dst(self):
        self.assertEqual(replay.cutoff_utc(date(2026, 9, 1)).hour, 11)   # EDT
        self.assertEqual(replay.cutoff_utc(date(2026, 11, 9)).hour, 12)  # EST

    def test_weekdays_skips_weekends(self):
        days = replay.weekdays(date(2026, 10, 30), date(2026, 11, 3))
        self.assertEqual([d.isoformat() for d in days], ["2026-10-30", "2026-11-02", "2026-11-03"])


class TruncateCandles(unittest.TestCase):
    def test_keeps_only_bars_before_cutoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / "src.csv", Path(tmp) / "dst.csv"
            src.write_text("date,open,high,low,close,volume\n"
                           "2026-10-01T10:58:00Z,1,2,0,10.5,3\n"
                           "2026-10-01T10:59:00Z,1,2,0,11.5,3\n"
                           "2026-10-01T11:00:00Z,1,2,0,99,3\n"
                           "2026-10-01T11:01:00Z,1,2,0,99,3\n", encoding="utf-8")
            cutoff = datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc)
            n, last_close, last_ts = replay.truncate_candles(src, dst, cutoff)
            self.assertEqual((n, last_close), (2, 11.5))
            self.assertEqual(last_ts, datetime(2026, 10, 1, 10, 59, tzinfo=timezone.utc))
            self.assertEqual(dst.read_text(encoding="utf-8").count("\n"), 3)


class BridgeAndLeaks(unittest.TestCase):
    def test_swap_bridge_path_replaces_and_requires_original(self):
        cfg = 'sources:\n  - symbol: "XAUUSD"\n    path: "C:/x/XAUUSD_1m.csv"\n'
        out = replay.swap_bridge_path(cfg, Path("C:/x/XAUUSD_1m.csv"), Path("C:/x/XAUUSD_1m_replay.csv"))
        self.assertIn("XAUUSD_1m_replay.csv", out)
        with self.assertRaises(RuntimeError):
            replay.swap_bridge_path(cfg, Path("C:/other.csv"), Path("C:/x/r.csv"))

    def test_leak_check(self):
        cutoff = datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc)
        clean = {"evidence": [{"tool": "get_market_data", "source": "local", "symbol": "XAUUSD",
                               "timestamp": "2026-10-01T10:45:00"}]}
        self.assertEqual(replay.leak_check(clean, cutoff), "")
        future = {"evidence": [{"tool": "get_market_data", "source": "local", "symbol": "XAUUSD",
                                "timestamp": "2026-10-01T11:00:00"}]}
        self.assertIn("posterior al corte", replay.leak_check(future, cutoff))
        other = {"evidence": [{"tool": "get_market_data", "source": "yahoo", "symbol": "GC=F", "timestamp": None}]}
        self.assertIn("yahoo/GC=F", replay.leak_check(other, cutoff))
        self.assertEqual(replay.leak_check({}, cutoff), "")


if __name__ == "__main__":
    unittest.main()
