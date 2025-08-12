from __future__ import annotations

from DataLayer.MarketDataProtocol import MarketData
from BusinessLogic.ArbStrategy import ArbStrategy
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.BooksViews.BooksView import BooksView
from BusinessLogic.BooksViews.PlainBooksView import PlainBooksView
from BusinessLogic.TradeRunners.Runner import Runner


class DeterministicRunner(Runner):
    def __init__(self, books_view: BooksView | None = None) -> None:
        self.books_view: BooksView = books_view if books_view is not None else PlainBooksView()

    def run(
        self,
        market_data: MarketData,
        strategy: ArbStrategy,
        execution: ExecutionSimulator,
        verbose: bool = True,
    ) -> None:
        while True:
            next_market_ts = market_data.peek_next_ts()
            next_exec_ts = execution.scheduler.next_exec_ts() if execution.has_pending() else None

            if next_market_ts is None and next_exec_ts is None:
                break

            if next_market_ts is None:
                current_ts = next_exec_ts
            elif next_exec_ts is None:
                current_ts = next_market_ts
            else:
                current_ts = min(next_market_ts, next_exec_ts)

            if next_market_ts is not None and next_market_ts <= current_ts:
                market_data.advance_to(current_ts)

            execution.process_pending_up_to(current_ts)

            ob_a, ob_b = self.books_view.get_view_books(market_data, execution)
            if execution.scheduler.submission_quota(current_ts) > 0:
                intent = strategy.on_order_books(
                    market_data.exchange_a_name, ob_a, market_data.exchange_b_name, ob_b, current_ts
                )
                if intent is not None:
                    pid = execution.submit_pair_order(intent)
                    if verbose:
                        print(
                            f"[{current_ts}] Submitted pair order id={pid} "
                            f"qty={intent.desired_qty} buy@{intent.buy_exchange} sell@{intent.sell_exchange}"
                        )

            if market_data.finished() and not execution.has_pending():
                break


