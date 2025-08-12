from dataclasses import dataclass, field


@dataclass
class PairOrderIntent:
    placed_ts: int
    symbol: str
    buy_exchange: str
    sell_exchange: str
    desired_qty: float = 1.0
    max_latency_ns: int = 1_000_000
    timeout_ns: int = 5_000_000


@dataclass(order=True)
class PendingPairOrder:
    exec_ts: int
    id: int = field(compare=False)
    intent: PairOrderIntent = field(compare=False)
    submit_ts: int = field(compare=False)


