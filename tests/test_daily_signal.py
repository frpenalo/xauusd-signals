"""Pruebas sin red de la señal diaria: extracción y validación del JSON del agente."""
import unittest

import daily_signal
from daily_signal import extract_signal, validate_signal

GOOD_SELL = {"direction": "SELL", "entry_low": 4063, "entry_high": 4065, "stop_loss": 4072,
             "tp1": 4056, "tp2": 4050, "tp3": 4046, "rationale": "x"}


class ExtractSignal(unittest.TestCase):
    def test_takes_last_json_with_direction(self):
        text = 'thinking {"direction": "BUY"} ... final:\n' + \
               '{"direction": "SELL", "entry_low": 1, "entry_high": 2, "stop_loss": 3, "tp1": 0, "tp2": 0, "tp3": 0, "rationale": "r"}'
        self.assertEqual(extract_signal(text)["direction"], "SELL")

    def test_none_when_absent(self):
        self.assertIsNone(extract_signal("no signal here {\"foo\": 1}"))


class ValidateSignal(unittest.TestCase):
    def test_good_sell(self):
        self.assertEqual(validate_signal(GOOD_SELL, live=4060), "")

    def test_no_trade_is_valid(self):
        self.assertEqual(validate_signal({"direction": "NO_TRADE"}, live=4060), "")

    def test_rejects_wide_zone(self):
        self.assertIn("zona", validate_signal({**GOOD_SELL, "entry_low": 4055}, live=4060))

    def test_rejects_far_from_live(self):
        self.assertIn("precio en vivo", validate_signal(GOOD_SELL, live=4100))

    def test_rejects_targets_on_wrong_side(self):
        bad = {**GOOD_SELL, "tp1": 4070, "tp2": 4075, "tp3": 4080}
        self.assertIn("objetivos", validate_signal(bad, live=4060))

    def test_rejects_stop_too_tight(self):
        self.assertIn("stop", validate_signal({**GOOD_SELL, "stop_loss": 4066}, live=4060))

    def test_rejects_tp1_not_about_1r(self):
        self.assertIn("TP1", validate_signal({**GOOD_SELL, "tp1": 4040, "tp2": 4035, "tp3": 4030}, live=4060))

    def test_buy_ordering(self):
        buy = {"direction": "BUY", "entry_low": 3974, "entry_high": 3976, "stop_loss": 3965,
               "tp1": 3984, "tp2": 3995, "tp3": 4005}
        self.assertEqual(validate_signal(buy, live=3978), "")




class FormatSignalTests(unittest.TestCase):
    ROW = {"direction": "BUY", "entry_low": "4112.0", "entry_high": "4115.0", "stop_loss": "4102.5",
           "tp1": "4124.5", "tp2": "4135.5", "tp3": "4146.5", "signal_date": "2026-11-09",
           "signal_time": "03:21 UTC", "notes": "live 4120.20 | x"}

    def test_channel_format_pending_when_price_outside_zone(self):
        msg = daily_signal.format_signal(self.ROW, 4120.20)
        self.assertTrue(msg.startswith("BUY XAUUSD — Entrada pendiente en zona ⏳\n\n✔️ Entrada: 4115-4112\n"))
        self.assertIn("🚫 SL: 4102.5\n💰 TP1: 4124.5\n💰 TP2: 4135.5\n💰 TP3: 4146.5", msg)

    def test_entrada_ahora_when_price_inside_zone_and_sell_order(self):
        row = dict(self.ROW, direction="SELL", entry_low="4186", entry_high="4188", stop_loss="4196",
                   tp1="4180", tp2="4175", tp3="4170")
        msg = daily_signal.format_signal(row, 4187.0)
        self.assertTrue(msg.startswith("SELL XAUUSD — Entrada ahora 🔴\n\n✔️ Entrada: 4186-4188\n"))


class RedactedTargets(unittest.TestCase):
    def test_fills_omitted_targets_from_zone_and_stop(self):
        text = 'answer: {"direction": "SELL", "entry_low": 4395.5, "entry_high": 4397.5, "stop_loss": 4405.5, ' \
               '"tp1": (omitted※), "tp2": (omitted※), "tp3": (omitted※), "rationale": "x"}'
        sig = extract_signal(text)
        self.assertEqual([sig["tp1"], sig["tp2"], sig["tp3"]], [4387.5, 4378.5, 4369.5])  # R = 9 desde 4396.5
        self.assertEqual(validate_signal(sig, 4390.0), "")

    def test_omitted_stop_is_rejected_not_invented(self):
        text = '{"direction": "BUY", "entry_low": 4150.0, "entry_high": 4152.0, "stop_loss": (omitted※), ' \
               '"tp1": (omitted※), "tp2": (omitted※), "tp3": (omitted※), "rationale": "x"}'
        sig = extract_signal(text)
        self.assertIsNone(sig["stop_loss"])
        self.assertEqual(validate_signal(sig, 4155.0), "faltan números")


class MechanicalSignal(unittest.TestCase):
    NOW = daily_signal.datetime(2026, 11, 9, 12, 0, tzinfo=daily_signal.timezone.utc)
    DAILY = [("2026-11-05", 4050.0, 4080.0, 4040.0, 4075.0),
             ("2026-11-06", 4075.0, 4110.0, 4060.0, 4069.5),
             ("2026-11-09", 4070.0, 4125.0, 4068.0, 4120.0)]  # día de hoy, parcial: no se usa como cierre

    def test_follows_move_from_last_complete_close(self):
        sig, note = daily_signal.mechanical_signal(4120.0, self.DAILY, self.NOW)
        self.assertEqual(note, "")
        self.assertEqual(sig["direction"], "BUY")
        self.assertEqual((sig["entry_low"], sig["entry_high"], sig["stop_loss"]), (4113.0, 4116.0, 4103.0))
        self.assertEqual((sig["tp1"], sig["tp2"], sig["tp3"]), (4126.0, 4137.5, 4149.0))  # R = 11.5
        self.assertIn("cierre 2026-11-06 4069.50", sig["rationale"])
        self.assertEqual(daily_signal.validate_signal(sig, 4120.0), "")

    def test_no_previous_day(self):
        sig, note = daily_signal.mechanical_signal(4120.0, self.DAILY[-1:], self.NOW)
        self.assertIsNone(sig)
        self.assertIn("sin cierre", note)


class ServerMode(unittest.TestCase):
    def test_prev_close_is_last_tick_before_midnight_utc(self):
        import lzma, struct, tempfile
        from pathlib import Path
        from verifier.dukascopy import hour_cache_path
        now = daily_signal.datetime(2026, 11, 9, 12, 0, tzinfo=daily_signal.timezone.utc)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Domingo 8-nov 23:00 UTC con dos ticks; el último bid es el cierre que usa la regla.
            hour = daily_signal.datetime(2026, 11, 8, 23, 0, tzinfo=daily_signal.timezone.utc)
            raw = lzma.compress(struct.pack(">3I2f", 1000, 4070300, 4070000, 1.0, 1.0)
                                + struct.pack(">3I2f", 3599000, 4069845, 4069545, 1.0, 1.0))
            p = hour_cache_path(root, "XAUUSD", hour)
            p.parent.mkdir(parents=True)
            p.write_bytes(raw)
            self.assertEqual(daily_signal.prev_close_from_ticks(now, root), ("2026-11-08", 4069.545))

    def test_prune_ticks_removes_only_old_files(self):
        import os, tempfile, time
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            old, new = Path(tmp) / "a" / "00h_ticks.bi5", Path(tmp) / "b" / "00h_ticks.bi5"
            for f in (old, new):
                f.parent.mkdir()
                f.write_bytes(b"x")
            os.utime(old, (time.time() - 20 * 86400,) * 2)
            self.assertEqual(daily_signal.prune_ticks(Path(tmp), keep_days=10), 1)
            self.assertTrue(new.exists() and not old.exists())


if __name__ == "__main__":
    unittest.main()
