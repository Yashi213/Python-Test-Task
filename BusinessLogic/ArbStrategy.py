from typing import Dict, Optional

from BusinessLogic.DataObjects.Models import PairOrderIntent
from BusinessLogic.OrderBook import OrderBook


class ArbStrategy:
    def __init__(
        self,
        symbol: str,
        desired_quantity: float,
        min_expected_net_pnl: float,
        fee_rates_by_exchange: Dict[str, float],
        max_depth_levels: int = 10,
        max_latency_ns: int = 1_000_000,
    ):
        self.symbol = symbol
        self.desired_quantity = desired_quantity
        self.min_expected_net_pnl = min_expected_net_pnl
        self.fee_rates_by_exchange = fee_rates_by_exchange
        self.max_depth_levels = max_depth_levels
        self.max_latency_ns = max_latency_ns
        self.log_rejections = False

    def on_order_books(
        self,
        exchange_a_name: str,
        order_book_a: OrderBook,
        exchange_b_name: str,
        order_book_b: OrderBook,
        timestamp_ns: int,
    ) -> Optional[PairOrderIntent]:
        best_ask_a, _ = order_book_a.best_ask()
        best_ask_b, _ = order_book_b.best_ask()
        best_bid_a, _ = order_book_a.best_bid()
        best_bid_b, _ = order_book_b.best_bid()


        if best_ask_b is None or (best_ask_a is not None and best_ask_a <= best_ask_b):
            buy_exchange, buy_book = exchange_a_name, order_book_a
            sell_exchange, sell_book = exchange_b_name, order_book_b
        else:
            buy_exchange, buy_book = exchange_b_name, order_book_b
            sell_exchange, sell_book = exchange_a_name, order_book_a

        _, simulated_buy_filled = buy_book.simulate_market_fill("buy", self.desired_quantity)
        _, simulated_sell_filled = sell_book.simulate_market_fill("sell", self.desired_quantity)
        available_quantity = min(simulated_buy_filled, simulated_sell_filled)
        if available_quantity <= 0:
            return None
        trade_quantity = min(self.desired_quantity, available_quantity)

        buy_avg, buy_filled = buy_book.simulate_market_fill("buy", trade_quantity)
        sell_avg, sell_filled = sell_book.simulate_market_fill("sell", trade_quantity)

        fee_buy = self.fee_rates_by_exchange.get(buy_exchange, 0.0)
        fee_sell = self.fee_rates_by_exchange.get(sell_exchange, 0.0)
        est_buy_cost = buy_avg * trade_quantity
        est_sell_proceed = sell_avg * trade_quantity
        est_fees = est_buy_cost * fee_buy + est_sell_proceed * fee_sell
        est_gross = est_sell_proceed - est_buy_cost
        est_net = est_gross - est_fees

        if est_net < self.min_expected_net_pnl:
            return None

        intent = PairOrderIntent(
            placed_ts=timestamp_ns,
            symbol=self.symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            desired_qty=trade_quantity,
            max_latency_ns=self.max_latency_ns,
            timeout_ns=self.max_latency_ns * 5,
        )
        return intent


