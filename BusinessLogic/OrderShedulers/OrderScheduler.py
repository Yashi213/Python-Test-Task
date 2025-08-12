from __future__ import annotations

from typing import List, Protocol, Optional

from BusinessLogic.DataObjects.Models import PendingPairOrder


class OrderScheduler(Protocol):
    def add(self, pending: PendingPairOrder) -> None:
        ...

    def has_pending(self) -> bool:
        ...

    def next_exec_ts(self) -> Optional[int]:
        ...

    def pop_due(self, current_ts: int) -> List[PendingPairOrder]:
        ...

    def pop_timeouts(self, current_ts: int) -> List[PendingPairOrder]:
        ...

    def submission_quota(self, current_ts: int) -> int:
        """Сколько новых заявок можно принять сейчас. 0 — нельзя, >0 — лимит, большое число — безлимит."""
        ...

    def list_pending(self) -> List[PendingPairOrder]:
        """Текущий список pending-заявок (для построения виртуальных стаканов)."""
        ...


