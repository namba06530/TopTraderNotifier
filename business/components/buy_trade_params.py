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


def calculate_buy_stop_loss(last_ma1, last_ma2, last_ema1, last_ema2, lows):
    # Get the last lowest low
    lowest_low = min(lows[:-1])

    # Create a list of all the values to search for the last point below
    values = [lowest_low, last_ma1, last_ma2, last_ema1, last_ema2]

    # Reverse the list to search from the end
    values.reverse()

    # Search for the last point below all the MAs and EMAs
    stop_loss = lowest_low
    for value in values:
        if value < stop_loss:
            stop_loss = value

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
