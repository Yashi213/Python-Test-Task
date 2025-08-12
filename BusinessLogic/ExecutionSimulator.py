from typing import Dict, List, Optional, Tuple

from BusinessLogic.DataObjects.Models import PairOrderIntent, PendingPairOrder
from BusinessLogic.OrderShedulers.OrderScheduler import OrderScheduler
from BusinessLogic.OrderShedulers.SingleOrderScheduler import SinglePendingScheduler
from BusinessLogic.OrderBook import OrderBook


class ExecutionSimulator:
    def __init__(
        self,
        orderbooks: Dict[str, OrderBook],
        fee_rates: Dict[str, float],
        default_latency_ns: int = 1_000_000,
        scheduler: Optional[OrderScheduler] = None,
    ):
        self.orderbooks = orderbooks
        self.fee_rates = fee_rates
        self.default_latency_ns = default_latency_ns
        self.scheduler: OrderScheduler = scheduler if scheduler is not None else SinglePendingScheduler()
        self._id_counter = 1
        self.trade_log: List[dict] = []

    def has_pending(self) -> bool:
        return self.scheduler.has_pending()

    def submit_pair_order(self, intent: PairOrderIntent) -> int:
        latency = intent.max_latency_ns if intent.max_latency_ns else self.default_latency_ns
        exec_ts = intent.placed_ts + latency
        pid = self._id_counter
        self._id_counter += 1
        pending = PendingPairOrder(exec_ts, pid, intent, intent.placed_ts)
        self.scheduler.add(pending)
        return pid

    @staticmethod
    def hedge(
        action: str,
        ob: OrderBook,
        base_avg: Optional[float],
        excess: float,
        fee_rate: float,
    ) -> Tuple[float, float, float]:
        close_avg, close_filled = ob.take_market_order(action, excess)
        if close_filled <= 0:
            return 0.0, 0.0, 0.0
        close_notional = close_avg * close_filled
        base_notional = base_avg * close_filled

        is_sell = (action == "sell")
        proceeds = (base_notional, close_notional)[is_sell]
        cost = (close_notional, base_notional)[is_sell]
        fee_close = close_notional * fee_rate
        residual_pnl = proceeds - cost - fee_close
        print("WARNING: Hedge")
        return residual_pnl

    def process_pending_up_to(self, current_ts: int):
        cancelled = self.scheduler.pop_timeouts(current_ts)
        for p in cancelled:
            intent = p.intent
            self.trade_log.append(
                {
                    "id": p.id,
                    "placed_ts": p.submit_ts,
                    "cancel_ts": current_ts,
                    "status": "timeout_cancelled",
                    "buy_exchange": intent.buy_exchange,
                    "sell_exchange": intent.sell_exchange,
                    "desired_qty": intent.desired_qty,
                    "total_pnl": 0.0,
                }
            )

        due = self.scheduler.pop_due(current_ts)
        for p in due:
            intent = p.intent
            buy_ob = self.orderbooks[intent.buy_exchange]
            sell_ob = self.orderbooks[intent.sell_exchange]

            buy_avg, buy_filled = buy_ob.take_market_order("buy", intent.desired_qty)
            sell_avg, sell_filled = sell_ob.take_market_order("sell", intent.desired_qty)

            matched_qty = min(buy_filled, sell_filled)

            fee_buy = self.fee_rates.get(intent.buy_exchange, 0.0)
            fee_sell = self.fee_rates.get(intent.sell_exchange, 0.0)

            matched_buy_cost = (buy_avg * matched_qty) if buy_avg is not None else 0.0
            matched_sell_proceed = (sell_avg * matched_qty) if sell_avg is not None else 0.0
            fees_matched = matched_buy_cost * fee_buy + matched_sell_proceed * fee_sell
            gross_pnl_matched = matched_sell_proceed - matched_buy_cost
            net_pnl = gross_pnl_matched - fees_matched

            buy_excess = buy_filled - matched_qty
            sell_excess = sell_filled - matched_qty
            if buy_excess > 0 or sell_excess > 0:
                if buy_excess > 0:
                    action, ob, base_avg, excess, fee_rate = "sell", buy_ob, buy_avg, buy_excess, fee_buy
                else:
                    action, ob, base_avg, excess, fee_rate = "buy", sell_ob, sell_avg, sell_excess, fee_sell
                res_pnl = self.hedge(action, ob, base_avg, excess, fee_rate)
                net_pnl += res_pnl

            log = {
                "id": p.id,
                "placed_ts": p.submit_ts,
                "exec_ts": p.exec_ts,
                "buy_exchange": intent.buy_exchange,
                "sell_exchange": intent.sell_exchange,
                "desired_qty": intent.desired_qty,
                "buy_filled": buy_filled,
                "sell_filled": sell_filled,
                "matched_qty": matched_qty,
                "buy_avg": buy_avg,
                "sell_avg": sell_avg,
                "gross_pnl_matched": gross_pnl_matched,
                "fees_matched": fees_matched,
                "total_pnl": net_pnl,
                "status": "filled",
            }
            self.trade_log.append(log)


