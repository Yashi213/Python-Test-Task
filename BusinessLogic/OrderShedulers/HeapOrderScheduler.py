from __future__ import annotations

import heapq
from typing import List, Optional, Tuple

from BusinessLogic.DataObjects.Models import PendingPairOrder
from BusinessLogic.OrderShedulers.OrderScheduler import OrderScheduler


class HeapScheduler(OrderScheduler):
    def __init__(self, max_concurrent:int | None = None, max_submits_per_tick:int | None = None) -> None:
        self._by_exec: List[Tuple[int, PendingPairOrder]] = []
        self._by_expiry: List[Tuple[int, PendingPairOrder]] = []
        self._max_concurrent = max_concurrent
        self._max_submits_per_tick = max_submits_per_tick
        self._submitted_this_tick_ts: Optional[int] = None
        self._submitted_this_tick_count: int = 0

    def add(self, pending: PendingPairOrder) -> None:
        intent = pending.intent
        expiry_ts = intent.placed_ts + intent.timeout_ns
        heapq.heappush(self._by_exec, (pending.exec_ts, pending))
        heapq.heappush(self._by_expiry, (expiry_ts, pending))
        if self._submitted_this_tick_ts != pending.intent.placed_ts:
            self._submitted_this_tick_ts = pending.intent.placed_ts
            self._submitted_this_tick_count = 0
        self._submitted_this_tick_count += 1

    def has_pending(self) -> bool:
        return len(self._by_exec) > 0

    def next_exec_ts(self) -> Optional[int]:
        if not self._by_exec:
            return None
        return self._by_exec[0][0]

    def pop_due(self, current_ts: int) -> List[PendingPairOrder]:
        due: List[PendingPairOrder] = []
        while self._by_exec and self._by_exec[0][0] <= current_ts:
            _, p = heapq.heappop(self._by_exec)
            due.append(p)
        return due

    def pop_timeouts(self, current_ts: int) -> List[PendingPairOrder]:
        cancelled: List[PendingPairOrder] = []
        while self._by_expiry and self._by_expiry[0][0] <= current_ts:
            _, p = heapq.heappop(self._by_expiry)
            cancelled.append(p)
        return cancelled

    def _current_concurrent(self) -> int:
        return len(self._by_exec)

    def submission_quota(self, current_ts: int) -> int:
        if self._max_concurrent is not None and self._current_concurrent() >= self._max_concurrent:
            return 0

        if self._max_submits_per_tick is not None and self._submitted_this_tick_ts is not None:
            if self._submitted_this_tick_count >= self._max_submits_per_tick:
                return 0
        return 10**9

    def list_pending(self) -> List[PendingPairOrder]:
        return [p for _, p in self._by_exec]


