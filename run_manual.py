import pandas as pd

from BusinessLogic.TradeRunners.RealtimeRunner import RealtimeRunner
from DataLayer.SynchronizedMarketData import SynchronizedMarketData
from BusinessLogic.ArbStrategy import ArbStrategy
from BusinessLogic.ExecutionSimulator import ExecutionSimulator
from BusinessLogic.OrderShedulers.HeapOrderScheduler import HeapScheduler
from BusinessLogic.OrderShedulers.SingleOrderScheduler import SinglePendingScheduler
from BusinessLogic.TradeRunners.DeterministicRunner import DeterministicRunner
from BusinessLogic.BooksViews.PlainBooksView import PlainBooksView
from BusinessLogic.BooksViews.VirtualBooksView import VirtualBooksView
from BusinessLogic.PnL import PnL


def main() -> None:
    exchange_a = "binance"
    exchange_b = "bybit"
    symbol = "BTCUSDT"
    file_a = "data/binance_btc_l2_1d.parquet"
    file_b = "data/bybit_btc_l2_1d.parquet"
    fee_a = 0.0004
    fee_b = 0.0004
    desired_qty = 100
    min_net_pnl = 1.0
    max_latency_ns = 1_000_000
    parallel = True
    virtual_books = True

    df_a = pd.read_parquet(file_a) if file_a.endswith(".parquet") else pd.read_csv(file_a)
    df_b = pd.read_parquet(file_b) if file_b.endswith(".parquet") else pd.read_csv(file_b)

    feed = SynchronizedMarketData(
        dataframe_a=df_a,
        dataframe_b=df_b,
        exchange_a_name=exchange_a,
        exchange_b_name=exchange_b,
        symbol=symbol,
    )

    fee_rates = {exchange_a: fee_a, exchange_b: fee_b}
    strategy = ArbStrategy(
        symbol=symbol,
        desired_quantity=desired_qty,
        min_expected_net_pnl=min_net_pnl,
        fee_rates_by_exchange=fee_rates,
        max_latency_ns=max_latency_ns,
    )

    ob_a, ob_b = feed.get_books()
    orderbooks = {exchange_a: ob_a, exchange_b: ob_b}

    scheduler = HeapScheduler() if parallel else SinglePendingScheduler()
    execution = ExecutionSimulator(orderbooks, fee_rates, default_latency_ns=max_latency_ns, scheduler=scheduler)

    books_view = VirtualBooksView() if virtual_books else PlainBooksView()
    runner = RealtimeRunner(books_view=books_view)

    runner.run(feed, strategy, execution, verbose=False)

    pnl = PnL()
    pnl.pnl_history = [float(t.get("total_pnl", 0.0)) for t in execution.trade_log]
    pnl.plot_cum_pnl()
    print(f"Total PnL: {pnl.total_pnl():.6f}")
    print(f"Sharpe: {pnl.sharpe_ratio():.4f}")


if __name__ == "__main__":
    main()


