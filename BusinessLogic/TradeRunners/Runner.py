from __future__ import annotations

from abc import ABC, abstractmethod

from DataLayer.MarketDataProtocol import MarketData
from BusinessLogic.ArbStrategy import ArbStrategy
from BusinessLogic.ExecutionSimulator import ExecutionSimulator


class Runner(ABC):
    @abstractmethod
    def run(
        self,
        market_data: MarketData,
        strategy: ArbStrategy,
        execution: ExecutionSimulator,
        verbose: bool = True,
    ) -> None:
        ...


