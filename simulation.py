import numpy as np
import pandas as pd
import json
from tqdm import tqdm

def generate_synthetic_l2(exchange: str, symbol: str, duration_sec: int = 86400, freq_ms: int = 100):
    ts_start = 1712000000000000  # наносекунды
    price = 120000.0
    data = []

    for i in tqdm(range(0, duration_sec * 1000, freq_ms)):
        ts = ts_start + i * 1_000_000
        noise = np.random.normal(0, 5)  # волатильность
        spread_noise = np.random.uniform(1, 10)
        price += noise

        # Симулируем спред и глубину
        best_bid = round(price - spread_noise / 2, 2)
        best_ask = round(price + spread_noise / 2, 2)

        # Топ-3 уровня
        bids = [[best_bid, np.random.randint(5, 20)],
                [round(best_bid - 1, 2), np.random.randint(3, 15)],
                [round(best_bid - 2, 2), np.random.randint(1, 10)]]

        asks = [[best_ask, np.random.randint(5, 20)],
                [round(best_ask + 1, 2), np.random.randint(3, 15)],
                [round(best_ask + 2, 2), np.random.randint(1, 10)]]

        data.append({
            "timestamp_ns": ts,
            "exchange": exchange,
            "event_type": "update",
            "symbol": symbol,
            "bids": json.dumps(bids),
            "asks": json.dumps(asks)
        })

    return pd.DataFrame(data)

# Генерация
binance_data = generate_synthetic_l2("binance", "BTCUSDT_PERP")
bybit_data = generate_synthetic_l2("bybit", "BTCUSDT_PERP")

# Сохранение
binance_data.to_parquet("data/binance_btc_l2_1d.parquet", index=False)
bybit_data.to_parquet("data/bybit_btc_l2_1d.parquet", index=False)