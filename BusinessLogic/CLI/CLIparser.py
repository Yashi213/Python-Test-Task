from __future__ import annotations

import argparse
from typing import Optional

from BusinessLogic.CLI.AppConfig import AppConfig


class CliParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(add_help=True)
        self._init_args()

    def _init_args(self) -> None:
        self.parser.add_argument("--ex-a", dest="exchange_a", required=True)
        self.parser.add_argument("--ex-b", dest="exchange_b", required=True)
        self.parser.add_argument("--symbol", required=True)
        self.parser.add_argument("--file-a", dest="file_a", required=True)
        self.parser.add_argument("--file-b", dest="file_b", required=True)
        self.parser.add_argument("--fee-a", dest="fee_a", type=float, required=True)
        self.parser.add_argument("--fee-b", dest="fee_b", type=float, required=True)
        self.parser.add_argument("--qty", dest="desired_qty", type=float, required=True)
        self.parser.add_argument("--min-net", dest="min_net_pnl", type=float, default=0.0)
        self.parser.add_argument("--latency", dest="max_latency_ns", type=int, default=1_000_000)
        self.parser.add_argument(
            "--scheduler",
            dest="scheduler_type",
            choices=["heap", "single"],
            default="heap",
            help="Тип планировщика заявок",
        )
        self.parser.add_argument(
            "--books-view",
            dest="books_view_type",
            choices=["plain", "virtual"],
            default="plain",
            help="Тип представления стаканов",
        )
        self.parser.add_argument(
            "--runner",
            dest="runner_type",
            choices=["realtime", "deterministic"],
            default="realtime",
            help="Тип раннера",
        )

    def parse(self, args: Optional[list[str]] = None) -> AppConfig:
        p = self.parser.parse_args(args=args)
        return AppConfig(
            exchange_a=p.exchange_a,
            exchange_b=p.exchange_b,
            symbol=p.symbol,
            file_a=p.file_a,
            file_b=p.file_b,
            fee_a=p.fee_a,
            fee_b=p.fee_b,
            desired_qty=p.desired_qty,
            min_net_pnl=p.min_net_pnl,
            max_latency_ns=p.max_latency_ns,
            scheduler_type=p.scheduler_type,
            books_view_type=p.books_view_type,
            runner_type=p.runner_type,
        )



