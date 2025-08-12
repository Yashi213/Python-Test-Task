import json
from typing import Optional, Tuple

import pandas as pd

from BusinessLogic.OrderBook import OrderBook


class SynchronizedMarketData:
    def __init__(
        self,
        dataframe_a: pd.DataFrame,
        dataframe_b: pd.DataFrame,
        exchange_a_name: str,
        exchange_b_name: str,
        symbol: str,
    ) -> None:
        self.df_a = dataframe_a
        self.df_b = dataframe_b
        self.exchange_a_name = exchange_a_name
        self.exchange_b_name = exchange_b_name

        self.index_a = 0
        self.index_b = 0

        self.order_book_a = OrderBook(symbol)
        self.order_book_b = OrderBook(symbol)

    @staticmethod
    def _parse_levels(val):
        if pd.isna(val):
            return []
        if isinstance(val, str):
            return json.loads(val)
        if isinstance(val, list):
            return val
        return []

    def _apply_row(self, row, ob: OrderBook) -> None:
        event_type = row.get("event_type", "update")
        bids = self._parse_levels(row["bids"]) if "bids" in row else []
        asks = self._parse_levels(row["asks"]) if "asks" in row else []
        if event_type == "snapshot":
            ob.update_snapshot(bids, asks)
        else:
            ob.update_incremental(bids, asks)

    def _peek_ts_a(self) -> Optional[int]:
        return int(self.df_a.iloc[self.index_a]["timestamp_ns"]) if self.index_a < len(self.df_a) else None

    def _peek_ts_b(self) -> Optional[int]:
        return int(self.df_b.iloc[self.index_b]["timestamp_ns"]) if self.index_b < len(self.df_b) else None

    def peek_next_ts(self) -> Optional[int]:
        ts_a = self._peek_ts_a()
        ts_b = self._peek_ts_b()
        return ts_a if ts_a is not None else ts_b

    def finished(self) -> bool:
        return self.index_a >= len(self.df_a) or self.index_b >= len(self.df_b)

    def advance_to(self, target_ts: int) -> None:
        while not self.finished():
            ts_a = self._peek_ts_a()
            ts_b = self._peek_ts_b()
            if ts_a is None or ts_b is None:
                break
            step_ts = ts_a if ts_a == ts_b else min(ts_a, ts_b)
            if step_ts > target_ts:
                break

            row_a = self.df_a.iloc[self.index_a]
            row_b = self.df_b.iloc[self.index_b]
            self.index_a += 1
            self.index_b += 1

            self._apply_row(row_a, self.order_book_a)
            self._apply_row(row_b, self.order_book_b)

    def get_books(self) -> Tuple[OrderBook, OrderBook]:
        return self.order_book_a, self.order_book_b


