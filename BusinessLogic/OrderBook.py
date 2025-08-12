from typing import List, Tuple, Optional


class OrderBook:
    def __init__(self, symbol: str, max_levels: int = 10):
        self.symbol = symbol
        self.max_levels = max_levels
        self.bids: List[Tuple[float, float]] = []
        self.asks: List[Tuple[float, float]] = []

    def clone(self) -> "OrderBook":
        ob = OrderBook(self.symbol, self.max_levels)
        ob.bids = list(self.bids)
        ob.asks = list(self.asks)
        return ob

    def update_snapshot(self, bids: List[Tuple[float, float]], asks: List[Tuple[float, float]]):
        self.bids = sorted([(float(p), float(s)) for p, s in bids], key=lambda x: x[0], reverse=True)[: self.max_levels]
        self.asks = sorted([(float(p), float(s)) for p, s in asks], key=lambda x: x[0])[: self.max_levels]

    def update_incremental(self, bids_delta: List[Tuple[float, float]], asks_delta: List[Tuple[float, float]]):
        self.bids = self._apply_delta(self.bids, bids_delta, reverse=True)
        self.asks = self._apply_delta(self.asks, asks_delta, reverse=False)

    @staticmethod
    def _apply_delta(levels: List[Tuple[float, float]], delta: List[Tuple[float, float]], reverse: bool) -> List[Tuple[float, float]]:
        price_to_size = {float(p): float(s) for p, s in levels}
        for price, size in delta:
            price = float(price)
            size = float(size)
            if size == 0:
                price_to_size.pop(price, None)
            else:
                price_to_size[price] = size
        sorted_levels = sorted(price_to_size.items(), key=lambda x: x[0], reverse=reverse)
        return sorted_levels

    def best_bid(self) -> Tuple[Optional[float], float]:
        return (self.bids[0][0], self.bids[0][1]) if self.bids else (None, 0.0)

    def best_ask(self) -> Tuple[Optional[float], float]:
        return (self.asks[0][0], self.asks[0][1]) if self.asks else (None, 0.0)

    def total_volume(self, side: str, max_levels: Optional[int] = None) -> float:
        levels = self.bids if side == "sell" else self.asks
        top = levels[:max_levels] if max_levels else levels
        return sum(size for _, size in top)

    def simulate_market_fill(self, side: str, qty: float) -> Tuple[Optional[float], float]:
        levels = self.asks if side == "buy" else self.bids
        avg_price, filled, _ = self._fill_levels(levels, qty)
        return avg_price, filled

    def take_market_order(self, side: str, qty: float) -> Tuple[Optional[float], float]:
        levels = self.asks if side == "buy" else self.bids
        avg_price, filled, new_levels = self._fill_levels(levels, qty)
        if side == "buy":
            self.asks = new_levels
        else:
            self.bids = new_levels
        return avg_price, filled

    @staticmethod
    def _fill_levels(levels: List[Tuple[float, float]], qty: float) -> Tuple[Optional[float], float, List[Tuple[float, float]]]:
        remaining = qty
        cost = 0.0
        new_levels: List[Tuple[float, float]] = []
        for price, size in levels:
            if remaining <= 0:
                new_levels.append((price, size))
                continue
            take = min(size, remaining)
            remaining -= take
            cost += take * price
            leftover = size - take
            if leftover != 0:
                new_levels.append((price, leftover))
        filled = qty - remaining
        avg_price = (cost / filled) if filled > 0 else None
        return avg_price, filled, new_levels


