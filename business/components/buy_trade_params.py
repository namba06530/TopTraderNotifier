import numpy as np

from common.bb_utils import calculate_bollinger_bands


def calculate_buy_entry_price(last_ma1, last_ma2, last_candle):
    # Get the last closing price
    last_close = last_candle['close']

    # Calculate the difference between the last closing price and the two MAs
    diff1 = abs(last_close - last_ma1)
    diff2 = abs(last_close - last_ma2)

    # Select the MA that is the closest to the last closing price
    if diff1 <= diff2:
        entry_price = last_ma1
    else:
        entry_price = last_ma2
    return entry_price


"""def calculate_buy_stop_loss(ma1, ma2, ema1, ema2, lows):
    # Find the index of the last candle where low is below all MAs and EMAs
    last_candle_below_mas_emas = -1
    for i in range(len(lows) - 1, -1, -1):  # We start from the last element (the most recent candle)
        if lows[i] < ma1[i] and lows[i] < ma2[i] and lows[i] < ema1[i] and lows[i] < ema2[i]:
            last_candle_below_mas_emas = i
            break

    # If there is no such candle, return None
    if last_candle_below_mas_emas == -1:
        return None

    stop_loss = lows[last_candle_below_mas_emas]

    # Set the stop loss slightly below the last point below the MAs and EMAs
    stop_loss = stop_loss - (stop_loss * 0.005)

    return stop_loss"""


def calculate_buy_stop_loss(lows, close_prices, bollinger_period=130, bollinger_std_dev=2):
    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices, period=bollinger_period,
                                                                    std_dev=bollinger_std_dev)

    # Take the last 12 candles
    last_12_lows = lows[-12:]

    # Find the lowest point of the last 12 candles
    lowest_point = np.min(last_12_lows)

    # Set the stop loss slightly below the lowest point
    stop_loss = lowest_point - (lowest_point * 0.001)

    # Check if the stop loss is within the Bollinger Bands
    last_lower_band = lower_band[-1]
    if stop_loss < last_lower_band:
        stop_loss = None

    return stop_loss


def calculate_buy_tp1(entry_price, stop_loss):
    if stop_loss is None:
        return None
    tp1_buy_signal = entry_price + (entry_price - stop_loss)
    return tp1_buy_signal


def calculate_buy_tp2(close_prices, bollinger_period=130, bollinger_std_dev=2):
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices, period=bollinger_period,
                                                                    std_dev=bollinger_std_dev)
    tp2_buy_signal = upper_band[-1]
    return tp2_buy_signal
