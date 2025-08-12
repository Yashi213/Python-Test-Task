from typing import List
import numpy as np
import matplotlib.pyplot as plt


class PnL:
    def __init__(self):
        self.pnl_history: List[float] = []

    def total_pnl(self) -> float:
        arr = np.array(self.pnl_history)
        return float(arr.sum()) if arr.size > 0 else 0.0

    def sharpe_ratio(self) -> float:
        arr = np.array(self.pnl_history)
        if arr.size == 0 or arr.std() == 0:
            return 0.0
        return float(arr.mean() / arr.std() * np.sqrt(len(arr)))

    def plot_cum_pnl(self):
        pnl = np.array(self.pnl_history)
        cum_sum = np.cumsum(pnl)
        plt.figure(figsize=(10, 4))
        plt.plot(cum_sum)
        plt.title("Cumulative PnL")
        plt.xlabel("Trade")
        plt.ylabel("PnL")
        plt.grid(True)
        plt.show()


