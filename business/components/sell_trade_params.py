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


def calculate_sell_stop_loss(last_ma1, last_ma2, last_ema1, last_ema2, highs):
    # Get the last highest high
    highest_high = max(highs[:-1])

    # Create a list of all the values to search for the last point below
    values = [highest_high, last_ma1, last_ma2, last_ema1, last_ema2]

    # Reverse the list to search from the end
    values.reverse()

    # Search for the last point above all the MAs and EMAs
    stop_loss = highest_high
    for value in values:
        if value > stop_loss:
            stop_loss = value

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
