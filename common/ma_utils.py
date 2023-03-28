import talib
from datetime import datetime
from data.candles_data import get_candles_data


def calculate_ma(opens, closes, ma_func, ma_args, ema_args, last_emas, last_mas):
    # Calculate start moving average
    ma1_start = ma_func(opens, ma_args[0])
    ma2_start = ma_func(opens, ma_args[1])
    ema1_start = talib.EMA(opens, ema_args[0])
    ema2_start = talib.EMA(opens, ema_args[1])

    start_ma1 = ma1_start[-1]
    start_ma2 = ma2_start[-1]
    start_ema1 = ema1_start[-1]
    start_ema2 = ema2_start[-1]

    # Calculate last moving average
    ma1 = ma_func(closes, ma_args[0])
    ma2 = ma_func(closes, ma_args[1])
    ema1 = talib.EMA(closes, ema_args[0])
    ema2 = talib.EMA(closes, ema_args[1])

    last_ma1 = ma1[-1]
    last_ma2 = ma2[-1]
    last_ema1 = ema1[-1]
    last_ema2 = ema2[-1]
    prev_ema1 = ema1[-2]
    prev_ema2 = ema2[-2]

    last_emas['ema1_prev'], last_emas['ema2_prev'] = prev_ema1, prev_ema2
    last_emas['ema1'], last_emas['ema2'] = last_ema1, last_ema2

    last_mas['ma1'], last_mas['ma2'] = last_ma1, last_ma2

    return start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, last_emas, last_mas


def get_ma_position(candle, mas):
    if candle['close'] >= mas['ma1'] and candle['close'] >= mas['ma2'] or \
            candle['close'] >= mas['ma2'] and candle['close'] >= mas['ma1']:
        return 'above'
    elif candle['close'] <= mas['ma1'] and candle['close'] <= mas['ma2'] or \
            candle['close'] <= mas['ma2'] and candle['close'] <= mas['ma1']:
        return 'below'


def update_ma_ema_positions(pair, interval, ma_func, ma_args, ema_args, last_positions, last_candles):
    last_position = last_positions[pair]['ma_position']

    start_candle, last_candle, opens, closes, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, last_emas, last_mas = get_last_candle_and_ma(
        pair, interval, ma_func, ma_args, ema_args)

    if last_candles[pair]['timestamp'] != last_candle['timestamp']:
        last_candles[pair] = last_candle
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Last Candle {pair}: {last_candles[pair]}")
        last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
        last_emas[pair] = {'ema1': last_ema1, 'ema2': last_ema2}

        # Compute the position of the last candle with respect to the MAs
        # Permet de savoir si la dernière clôtue est au dessus ou en dessous des MM (100 et 130)
        last_position = get_ma_position(last_candle, last_mas[pair])
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Last Position: {last_position} for {pair}")

        if last_position is None:
            last_position = last_positions[pair]['ma_position']
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Last Position: {last_position} for {pair}")

        if pair not in last_positions:
            last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

        # last_positions[pair]['ma_position'] = last_position

    return last_positions, last_candles, last_mas, last_emas, last_position, last_candle


def check_ema_conditions(last_emas, last_mas):
    ema_position = None
    # Check if EMAs are close to each other
    if abs((last_emas['ema1'] - last_emas['ema2']) / last_emas['ema1']) <= 0.0005 or \
            abs((last_emas['ema2'] - last_emas['ema1']) / last_emas['ema2']) <= 0.0005:
        ema_close = True
        ema_position = 'close'
    else:
        ema_close = None

    # Check if EMAs have crossed
    if last_emas['ema1'] > last_emas['ema2'] and last_emas['ema1_prev'] <= last_emas['ema2_prev']:
        ema_crossed = True
        ema_position = 'crossed'
    elif last_emas['ema1'] < last_emas['ema2'] and last_emas['ema1_prev'] >= last_emas['ema2_prev']:
        ema_crossed = True
        ema_position = 'crossed'
    else:
        ema_crossed = False

    # Check if EMAs are below MAs
    if last_emas['ema1'] < last_mas['ma1'] and last_emas['ema2'] < last_mas['ma2']:
        ema_below_ma = True
    else:
        ema_below_ma = False

    # Check if EMAs are above MAs
    if last_emas['ema1'] > last_mas['ma1'] and last_emas['ema2'] > last_mas['ma2']:
        ema_above_ma = True
    else:
        ema_above_ma = False

    return ema_close, ema_crossed, ema_position, ema_below_ma, ema_above_ma


def get_last_candle_and_ma(symbol, interval, ma_func, ma_args, ema_args):
    start_candle, last_candle, opens, closes = get_candles_data(symbol, interval)
    last_emas = {}
    last_mas = {}
    start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, last_emas, last_mas = \
        calculate_ma(opens, closes, ma_func, ma_args, ema_args, last_emas, last_mas)

    return start_candle, last_candle, opens, closes, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, \
        last_ema1, last_ema2, last_emas, last_mas
