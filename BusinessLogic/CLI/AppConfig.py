from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from BusinessLogic.ArbStrategy import ArbStrategy
from BusinessLogic.BooksViews.PlainBooksView import PlainBooksView
from BusinessLogic.BooksViews.VirtualBooksView import VirtualBooksView
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.OrderShedulers.HeapOrderScheduler import HeapScheduler
from BusinessLogic.OrderShedulers.SingleOrderScheduler import SinglePendingScheduler
from DataLayer.SynchronizedMarketData import SynchronizedMarketData
from BusinessLogic.TradeRunners.RealtimeRunner import RealtimeRunner
from BusinessLogic.TradeRunners.DeterministicRunner import DeterministicRunner
from BusinessLogic.TradeRunners.Runner import Runner

@dataclass
class AppConfig:
    exchange_a: str
    exchange_b: str
    symbol: str
    file_a: str
    file_b: str
    fee_a: float
    fee_b: float
    desired_qty: float
    min_net_pnl: float
    max_latency_ns: int
    scheduler_type: str
    books_view_type: str
    runner_type: str

    def build(
        self,
    ) -> tuple[SynchronizedMarketData, ArbStrategy, ExecutionSimulator, Runner]:
        fee_rates: Dict[str, float] = {self.exchange_a: self.fee_a, self.exchange_b: self.fee_b}

        df_a = pd.read_parquet(self.file_a) if self.file_a.endswith(".parquet") else pd.read_csv(self.file_a)
        df_b = pd.read_parquet(self.file_b) if self.file_b.endswith(".parquet") else pd.read_csv(self.file_b)
        df_a["exchange"] = self.exchange_a
        df_b["exchange"] = self.exchange_b

        feed = SynchronizedMarketData(
            dataframe_a=df_a,
            dataframe_b=df_b,
            exchange_a_name=self.exchange_a,
            exchange_b_name=self.exchange_b,
            symbol=self.symbol,
        )

        strategy = ArbStrategy(
            symbol=self.symbol,
            desired_quantity=self.desired_qty,
            min_expected_net_pnl=self.min_net_pnl,
            fee_rates_by_exchange=fee_rates,
            max_latency_ns=self.max_latency_ns,
        )

        ob_a, ob_b = feed.get_books()
        orderbooks = {self.exchange_a: ob_a, self.exchange_b: ob_b}

        scheduler: object
        if self.scheduler_type == "heap":
            scheduler = HeapScheduler()
        elif self.scheduler_type == "single":
            scheduler = SinglePendingScheduler()
        else:
            raise ValueError(f"Unknown scheduler_type: {self.scheduler_type}")
        execution = ExecutionSimulator(orderbooks, fee_rates, default_latency_ns=self.max_latency_ns, scheduler=scheduler)

        if self.books_view_type == "virtual":
            books_view = VirtualBooksView()
        elif self.books_view_type == "plain":
            books_view = PlainBooksView()
        else:
            raise ValueError(f"Unknown books_view_type: {self.books_view_type}")

        if self.runner_type == "realtime":
            runner: Runner = RealtimeRunner(books_view=books_view)
        elif self.runner_type == "deterministic":
            runner = DeterministicRunner(books_view=books_view)
        else:
            raise ValueError(f"Unknown runner_type: {self.runner_type}")
        return feed, strategy, execution, runner


