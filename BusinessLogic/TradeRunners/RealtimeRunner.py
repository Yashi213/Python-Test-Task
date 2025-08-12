from __future__ import annotations

import time

from DataLayer.MarketDataProtocol import MarketData
from BusinessLogic.ArbStrategy import ArbStrategy
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.BooksViews.BooksView import BooksView
from BusinessLogic.BooksViews.PlainBooksView import PlainBooksView
from BusinessLogic.TradeRunners.Runner import Runner


class RealtimeRunner(Runner):
    def __init__(self, books_view: BooksView | None = None) -> None:
        self.books_view: BooksView = books_view if books_view is not None else PlainBooksView()

    def run(
        self,
        market_data: MarketData,
        strategy: ArbStrategy,
        execution: ExecutionSimulator,
        verbose: bool = True,
    ) -> None:
        base_market_ts = market_data.peek_next_ts()
        base_wall_ns = time.time_ns()

        while True:
            now_ns = time.time_ns()
            current_ts = base_market_ts + (now_ns - base_wall_ns)

            market_data.advance_to(current_ts)
            ob_a, ob_b = self.books_view.get_view_books(market_data, execution)
            if not market_data.finished():
                if execution.scheduler.submission_quota(current_ts) > 0:
                    intent = strategy.on_order_books(
                        market_data.exchange_a_name, ob_a, market_data.exchange_b_name, ob_b, current_ts
                    )
                    if intent is not None:
                        pid = execution.submit_pair_order(intent)
                        if verbose: #для себя
                            print(
                                f"[{current_ts}] Submitted pair order id={pid} "
                                f"qty={intent.desired_qty} buy@{intent.buy_exchange} sell@{intent.sell_exchange}"
                            )

            execution.process_pending_up_to(current_ts)

            if market_data.finished() and not execution.has_pending():
                break


