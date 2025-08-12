from BusinessLogic.CLI.CLIparser import CliParser
from BusinessLogic.PnL import PnL


def main():
    cfg = CliParser().parse()
    feed, strategy, execution, runner = cfg.build()
    runner.run(feed, strategy, execution, verbose=True)

    pnl = PnL()
    pnl.pnl_history = [float(t.get("total_pnl", 0.0)) for t in execution.trade_log]
    pnl.plot_cum_pnl()
    print(f"Total PnL: {pnl.total_pnl():.6f}")
    print(f"Sharpe: {pnl.sharpe_ratio():.4f}")


if __name__ == "__main__":
    main()

