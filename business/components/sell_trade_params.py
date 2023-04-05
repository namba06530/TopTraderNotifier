from common.bb_utils import calculate_bollinger_bands


def calculate_sell_entry_price(last_ma1, last_ma2, last_candle):
    # Get the last open price
    last_open = last_candle['open']

    # Calculate the difference between the last open price and the two MAs
    diff1 = abs(last_open - last_ma1)
    diff2 = abs(last_open - last_ma2)

    # Select the MA that is the closest to the last open price
    if diff1 <= diff2:
        entry_price = last_ma1
    else:
        entry_price = last_ma2

    return entry_price


def calculate_sell_stop_loss(ma1, ma2, ema1, ema2, highs):
    # Find the index of the last candle where high is above all MAs and EMAs
    last_candle_above_mas_emas = -1
    for i in range(len(highs) - 1, -1, -1):  # We start from the last element (the most recent candle)
        if highs[i] > ma1[i] and highs[i] > ma2[i] and highs[i] > ema1[i] and highs[i] > ema2[i]:
            last_candle_above_mas_emas = i
            break

    # If there is no such candle, return None
    if last_candle_above_mas_emas == -1:
        return None

    stop_loss = highs[last_candle_above_mas_emas]

    # Set the stop loss slightly above the last point above the MAs and EMAs
    stop_loss = stop_loss + (stop_loss * 0.005)

    return stop_loss


def calculate_sell_tp1(entry_price, stop_loss):
    tp1_sell_signal = entry_price - (stop_loss - entry_price)
    return tp1_sell_signal


def calculate_sell_tp2(close_prices, period, std_dev):
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices, period=period, std_dev=std_dev)
    tp2_sell_signal = lower_band[-1]
    return tp2_sell_signal
