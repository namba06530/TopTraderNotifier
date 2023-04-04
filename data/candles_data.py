from data.binance_api import get_klines_data
import numpy as np


def get_candles_data(symbol, interval):
    # Get klines data
    klines = get_klines_data(symbol=symbol, interval=interval, retry_on_error=True)

    # Extract open, close prices, volumes, and timestamps
    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []
    timestamps = []
    for kline in klines:
        opens.append(float(kline[1]))
        closes.append(float(kline[4]))
        highs.append(float(kline[2]))
        lows.append(float(kline[3]))
        volumes.append(float(kline[5]))
        timestamps.append(kline[0])

    # Convert close prices to numpy array
    closes = np.array(closes)
    opens = np.array(opens)
    highs = np.array(highs)
    lows = np.array(lows)

    # Return open candle for the first loop
    start_candle = {'timestamp': timestamps[-3], 'open': opens[-3], 'close': closes[-3], 'volume': volumes[-3],
                    'high': highs[-3], 'low': lows[-3]}

    # Return last candle for the while loops
    last_candle = {'timestamp': timestamps[-2], 'open': opens[-2], 'close': closes[-2], 'volume': volumes[-2],
                   'high': highs[-2], 'low': lows[-2]}

    return start_candle, last_candle, opens, closes, highs, lows
