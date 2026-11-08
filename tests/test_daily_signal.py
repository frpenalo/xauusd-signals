"""Pruebas sin red de la señal diaria: extracción y validación del JSON del agente."""
import unittest

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


if __name__ == "__main__":
    unittest.main()
