# Simulation of bid/ask futures arbitrage

Разработать симулятор арбитражной HFT-стратегии, которая анализирует фьючерсные стаканы (L2) на двух биржах (например, Binance и Bybit) и выявляет мгновенные арбитражные возможности на основе разницы между best bid / best ask. 

Стратегия: Cross-Exchange Futures Arbitrage 

    Торговая пара: BTCUSDT-PERP (или ETHUSDT-PERP).
    Сигнал: spread = best_bid_exchange2 - best_ask_exchange1
    Если spread > threshold (с учётом комиссий и latency) → арбитраж вверх.
    Если best_bid_exchange1 - best_ask_exchange2 > threshold → арбитраж вниз.
    Учитывать комиссии, размер ликвидности, latency, timeout ордеров.

Ввод: Датасеты за 1 день (24 часа) 
Формат данных 

Каждая биржа предоставляет L2 updates (incremental feed) в формате MBO (Market by Order) или MBP (Market by Price). Мы используем MBP-10 (топ-10 уровней). 
Структура файла (CSV или Parquet): 

    timestamp_ns, exchange, event_type, symbol, bids, asks
    1712000000000000, binance, snapshot, BTCUSDT_PERP, "[[60100,10],[60090,15],...]", "[[60110,8],[60120,12],...]"
    1712000000001234, binance, update, BTCUSDT_PERP, "[[60105]][[20]]", "[[60110]][[3]]"
    
- timestamp_ns: Unix timestamp в наносекундах.
- bids, asks: JSON-массивы [price, size].
- event_type: snapshot (полный стакан) или update (дельта).

Данные по 2 биржам будут генерироваться синтетически, с помощью simulation.py.

Результаты 

PnL, Sharpe, график кумулятивного профита.
     
