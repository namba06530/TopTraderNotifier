from data.binance_api import get_klines_data
import numpy as np


def get_candles_data(symbol, interval):
    # Get klines data
    klines = get_klines_data(symbol=symbol, interval=interval)

    # Extract open, close prices, volumes, and timestamps
    opens = []
    closes = []
    volumes = []
    timestamps = []
    for kline in klines:
        opens.append(float(kline[1]))
        closes.append(float(kline[4]))
        volumes.append(float(kline[5]))
        timestamps.append(kline[0])

    # Convert close prices to numpy array
    closes = np.array(closes)
    opens = np.array(opens)

    # Return open candle for the first loop
    start_candle = {'timestamp': timestamps[-2], 'open': opens[-2], 'close': closes[-2], 'volume': volumes[-2]}
    # print(f"start candle: timestamp={datetime.fromtimestamp(start_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')},
    # open={start_candle['open']}, volume={start_candle['volume']}")

    # Return last candle for the while loops
    last_candle = {'timestamp': timestamps[-1], 'open': opens[-1], 'close': closes[-1], 'volume': volumes[-1]}
    # print(f"Last candle BTCUSDT: timestamp={datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')},
    # close={last_candle['close']}, volume={last_candle['volume']}")

    return start_candle, last_candle, opens, closes