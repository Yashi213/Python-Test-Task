from __future__ import annotations

from typing import Tuple

from DataLayer.MarketDataProtocol import MarketData
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.OrderBook import OrderBook


class PlainBooksView:
    def get_view_books(
        self,
        market_data: MarketData,
        execution: ExecutionSimulator,
    ) -> Tuple[OrderBook, OrderBook]:
        return market_data.get_books()


