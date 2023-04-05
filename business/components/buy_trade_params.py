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


def calculate_buy_stop_loss(ma1, ma2, ema1, ema2, lows):
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

    return stop_loss


def calculate_buy_tp1(entry_price, stop_loss):
    tp1_buy_signal = entry_price + (entry_price - stop_loss)
    return tp1_buy_signal


def calculate_buy_tp2(close_prices, period, std_dev):
    upper_band, middle_band, lower_band = calculate_bollinger_bands(close_prices, period=period, std_dev=std_dev)
    tp2_buy_signal = upper_band[-1]
    return tp2_buy_signal
