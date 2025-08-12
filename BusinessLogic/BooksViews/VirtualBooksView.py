from __future__ import annotations

from typing import Tuple

from DataLayer.MarketDataProtocol import MarketData
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.OrderBook import OrderBook


class VirtualBooksView:
    def get_view_books(
        self,
        market_data: MarketData,
        execution: ExecutionSimulator,
    ) -> Tuple[OrderBook, OrderBook]:
        base_a, base_b = market_data.get_books()
        ob_a = base_a.clone()
        ob_b = base_b.clone()
        for p in execution.scheduler.list_pending():
            intent = p.intent
            if intent.buy_exchange == market_data.exchange_a_name:
                ob_a.take_market_order("buy", intent.desired_qty)
            elif intent.buy_exchange == market_data.exchange_b_name:
                ob_b.take_market_order("buy", intent.desired_qty)
            if intent.sell_exchange == market_data.exchange_a_name:
                ob_a.take_market_order("sell", intent.desired_qty)
            elif intent.sell_exchange == market_data.exchange_b_name:
                ob_b.take_market_order("sell", intent.desired_qty)
        return ob_a, ob_b


