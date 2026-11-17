"""Pruebas sin red de backtest_be.trade sobre ticks sintéticos."""
import unittest
from datetime import date, datetime, timezone

import numpy as np

from backtest_be import trade
from verifier.signals import Signal

T0 = datetime(2026, 7, 13, 11, 0, tzinfo=timezone.utc)
SPREAD = 0.2


def arrays(bids, step_s=60):
    """bids = precios bid, un tick por minuto; el ask va SPREAD arriba."""
    t = int(T0.timestamp() * 1000) + np.arange(len(bids), dtype=np.int64) * step_s * 1000
    bid = np.array(bids, dtype=float)
    return t, bid, bid + SPREAD


def buy_signal():
    # zona 4000-4003, stop 3990, TP3 4031.5 (3R desde el centro de la zona)
    return Signal(row=1, signal_date=date(2026, 7, 13), direction="BUY", entry_low=4000, entry_high=4003,
                  entry_used=4001.5, stop_loss=3990, tps=[4011.5, 4021.5, 4031.5], start_utc=T0,
                  time_basis="explicit_utc")


class BuyManagement(unittest.TestCase):
    def test_not_filled_returns_none(self):
        self.assertIsNone(trade(buy_signal(), *arrays([4010, 4012, 4015]), (10,)))

    def test_stop_exits_at_tick_price_not_at_level(self):
        # llena en ask 4002.2, cae de golpe a bid 3988: el stop de 3990 sale en 3988
        res = trade(buy_signal(), *arrays([4005, 4002, 4001, 3988]), (10,))
        kind, r = res["nobe", 0]
        self.assertEqual(kind, "SL")
        self.assertAlmostEqual(r, (3988 - 4002.2) / (4002.2 - 3990))
        self.assertEqual(res["leg_res", 0], ("SL", -1.0))

    def test_losing_at_minute_n_keeps_original_stop_or_closes_at_market(self):
        # a los 10 minutos va perdiendo (bid 3996) y después salta el stop original
        path = [4005, 4002] + [3996] * 11 + [3989]
        res = trade(buy_signal(), *arrays(path), (10,))
        self.assertEqual(res["be_ok", 10][0], "SL")
        self.assertAlmostEqual(res["be_ok", 10][1], (3989 - 4002.2) / (4002.2 - 3990))
        kind, r = res["be_mkt", 10]
        self.assertEqual(kind, "BE")
        self.assertAlmostEqual(r, (3996 - 4002.2) / (4002.2 - 3990))
        self.assertEqual(res["leg_be", 10], ("BE", 0.0))  # el simulador viejo la daba en 0R

    def test_stop_moves_to_entry_once_in_profit_and_exits_with_slippage(self):
        # pierde al minuto 10, pasa a ganancia (stop a entrada) y vuelve a caer por debajo
        path = [4005, 4002] + [3996] * 11 + [4006, 4001.5, 3989]
        res = trade(buy_signal(), *arrays(path), (10,))
        kind, r = res["be_ok", 10]
        self.assertEqual(kind, "BE")
        self.assertAlmostEqual(r, (4001.5 - 4002.2) / (4002.2 - 3990))

    def test_winner_untouched_by_break_even(self):
        path = [4005, 4002] + [4008] * 11 + [4020, 4032]
        res = trade(buy_signal(), *arrays(path), (10,))
        r_tp = (4031.5 - 4002.2) / (4002.2 - 3990)
        for key in (("nobe", 0), ("be_ok", 10), ("be_mkt", 10)):
            self.assertEqual(res[key][0], "TP")
            self.assertAlmostEqual(res[key][1], r_tp)

    def test_open_trade_is_marked_at_last_price(self):
        res = trade(buy_signal(), *arrays([4005, 4002, 4004, 4007]), (10,))
        self.assertEqual(res["nobe", 0][0], "open")
        self.assertAlmostEqual(res["nobe", 0][1], (4007 - 4002.2) / (4002.2 - 3990))
        self.assertEqual(res["be_ok", 10][0], "open")


if __name__ == "__main__":
    unittest.main()
