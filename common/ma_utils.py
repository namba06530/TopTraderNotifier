import talib
from datetime import datetime
from data.candles_data import get_candles_data
from common.bb_utils import calculate_bollinger_bands, calculate_bollinger_band_width


def calculate_ma(closes, ma_func, ma_args, ema_args):
    # Calculate last moving average
    ma1 = ma_func(closes, ma_args[0])
    ma2 = ma_func(closes, ma_args[1])
    ema1 = talib.EMA(closes, ema_args[0])
    ema2 = talib.EMA(closes, ema_args[1])

    start_ma1 = ma1[-3]
    start_ma2 = ma2[-3]
    start_ema1 = ema1[-3]
    start_ema2 = ema2[-3]

    last_ma1 = ma1[-2]
    last_ma2 = ma2[-2]
    last_ema1 = ema1[-2]
    last_ema2 = ema2[-2]
    prev_ema1 = ema1[-3]
    prev_ema2 = ema2[-3]

    last_emas = {'ema1': last_ema1, 'ema2': last_ema2, 'ema1_prev': prev_ema1, 'ema2_prev': prev_ema2}

    last_mas = {'ma1': last_ma1, 'ma2': last_ma2}

    return start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, prev_ema1, prev_ema2, \
        ma1, ma2, ema1, ema2


def get_ma_position(candle, mas, margin_percent=0.1):
    margin = candle['close'] * (margin_percent / 100)

    if candle['close'] >= mas['ma1'] + margin and candle['close'] >= mas['ma2'] + margin or \
            candle['close'] >= mas['ma2'] + margin and candle['close'] >= mas['ma1'] + margin:
        return 'above'
    elif candle['close'] <= mas['ma1'] - margin and candle['close'] <= mas['ma2'] - margin or \
            candle['close'] <= mas['ma2'] - margin and candle['close'] <= mas['ma1'] - margin:
        return 'below'


"""def update_ma_ema_positions(pair, interval, ma_func, ma_args, ema_args, last_positions, last_candles, last_mas,
                            last_emas):
    start_candle, last_candle, opens, closes, highs, lows, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, \
        last_ema2, prev_ema1, prev_ema2 = get_last_candle_and_ma(pair, interval, ma_func, ma_args, ema_args)

    print(f"timestamp last_candle = {last_candle['timestamp']}")
    print(f"timestamp last_candles[pair] = {last_candles[pair]['timestamp']}")

    if last_candles[pair]['timestamp'] != last_candle['timestamp']:
        last_candles[pair] = last_candle
        # print(f"Last candle {pair} = {last_candles[pair]}")
        last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
        last_emas[pair] = {'ema1': last_ema1, 'ema1_prev': prev_ema1, 'ema2': last_ema2, 'ema2_prev': prev_ema2}

        # Compute the position of the last candle with respect to the MAs
        # Check if last candle close is above or below MAs
        last_position = get_ma_position(last_candle, last_mas[pair])
        print(f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
              f"Last Position: {last_position} for {pair}")

        if last_position is None:
            last_position = last_positions[pair]['ma_position']
            print(f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                  f"Last Position: {last_position} for {pair}")

        if pair not in last_positions:
            last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

    return last_positions, last_candles, last_mas, last_emas, last_position, last_candle"""


def check_ema_conditions(pair, last_emas, last_mas):
    ema_position = None
    # Check if EMAs are close to each other
    if abs((last_emas[pair]['ema1'] - last_emas[pair]['ema2']) / last_emas[pair]['ema1']) <= 0.003 or \
            abs((last_emas[pair]['ema2'] - last_emas[pair]['ema1']) / last_emas[pair]['ema2']) <= 0.003:
        ema_close = True
        ema_position = 'close'
    else:
        ema_close = False

    # Check if EMAs have crossed
    if last_emas[pair]['ema1'] > last_emas[pair]['ema2'] and last_emas[pair]['ema1_prev'] <= last_emas[pair][
        'ema2_prev']:
        ema_crossed = True
        ema_position = 'crossed'
    elif last_emas[pair]['ema1'] < last_emas[pair]['ema2'] and last_emas[pair]['ema1_prev'] >= last_emas[pair][
        'ema2_prev']:
        ema_crossed = True
        ema_position = 'crossed'
    else:
        ema_crossed = False

    # Check if EMAs are below MAs
    if last_emas[pair]['ema1'] < last_mas[pair]['ma1'] and last_emas[pair]['ema2'] < last_mas[pair]['ma2']:
        ema_below_ma = True
    else:
        ema_below_ma = False

    # Check if EMAs are above MAs
    if last_emas[pair]['ema1'] > last_mas[pair]['ma1'] and last_emas[pair]['ema2'] > last_mas[pair]['ma2']:
        ema_above_ma = True
    else:
        ema_above_ma = False

    return ema_close, ema_crossed, ema_position, ema_below_ma, ema_above_ma


def check_ma_conditions(pair, last_mas):
    ma1 = last_mas[pair]['ma1']
    ma2 = last_mas[pair]['ma2']
    # print(f"{pair} MA1: {ma1}, MA2: {ma2}")

    ma_diff_1 = abs((ma1 - ma2) / ma1)
    ma_diff_2 = abs((ma2 - ma1) / ma2)
    # print(f"{pair} MA Difference Ratios: {ma_diff_1}, {ma_diff_2}")

    # Check if MAs are close to each other
    if ma_diff_1 <= 0.003 or ma_diff_2 <= 0.003:
        ma_close = True
    else:
        ma_close = False

    # print(f"{pair} MAs Close: {ma_close}")
    return ma_close


def get_last_candle_and_ma(symbol, interval, ma_func, ma_args, ema_args):
    start_candle, last_candle, opens, closes, highs, lows = get_candles_data(symbol, interval)
    start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, prev_ema1, prev_ema2, ma1, \
        ma2, ema1, ema2 = calculate_ma(closes, ma_func, ma_args, ema_args)

    # Calculate Bollinger Bands for the last two candles
    prev_upper_band, prev_middle_band, prev_lower_band = calculate_bollinger_bands(closes[:-1], period=130, std_dev=2)
    last_upper_band, last_middle_band, last_lower_band = calculate_bollinger_bands(closes, period=130, std_dev=2)

    # Calculate Bollinger Band widths for the last two candles
    prev_band_width = calculate_bollinger_band_width(prev_upper_band, prev_lower_band)
    last_band_width = calculate_bollinger_band_width(last_upper_band, last_lower_band)

    return start_candle, last_candle, opens, closes, highs, lows, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, \
        last_ema1, last_ema2, prev_ema1, prev_ema2, prev_band_width, last_band_width, ma1, ma2, ema1, ema2
