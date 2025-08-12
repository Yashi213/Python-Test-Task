from __future__ import annotations

from typing import Protocol, Tuple, Optional

from BusinessLogic.OrderBook import OrderBook


class MarketData(Protocol):
    exchange_a_name: str
    exchange_b_name: str

    def peek_next_ts(self) -> Optional[int]:
        ...

    def finished(self) -> bool:
        ...

    def advance_to(self, target_ts: int) -> None:
        ...

    def get_books(self) -> Tuple[OrderBook, OrderBook]:
        ...


