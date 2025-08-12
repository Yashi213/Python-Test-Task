from __future__ import annotations

from typing import List, Optional

from BusinessLogic.DataObjects.Models import PendingPairOrder
from BusinessLogic.OrderShedulers.OrderScheduler import OrderScheduler


class SinglePendingScheduler(OrderScheduler):
    def __init__(self) -> None:
        self._pending: Optional[PendingPairOrder] = None

    def add(self, pending: PendingPairOrder) -> None:
        if self._pending is not None:
            raise RuntimeError("scheduler already has a pending order")
        self._pending = pending

    def has_pending(self) -> bool:
        return self._pending is not None

    def next_exec_ts(self) -> Optional[int]:
        return self._pending.exec_ts if self._pending is not None else None

    def pop_due(self, current_ts: int) -> List[PendingPairOrder]:
        if self._pending is None or self._pending.exec_ts > current_ts:
            return []
        p = self._pending
        self._pending = None
        return [p]

    def pop_timeouts(self, current_ts: int) -> List[PendingPairOrder]:
        if self._pending is None:
            return []
        intent = self._pending.intent
        expiry_ts = intent.placed_ts + intent.timeout_ns
        if current_ts >= expiry_ts:
            p = self._pending
            self._pending = None
            return [p]
        return []

    def submission_quota(self, current_ts: int) -> int:
        return 0 if self._pending is not None else 1

    def list_pending(self) -> List[PendingPairOrder]:
        return [self._pending] if self._pending is not None else []


