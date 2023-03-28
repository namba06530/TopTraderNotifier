import time
from service.my_telegram_bot import *
from common.utils import interval_to_seconds
from common.ma_utils import get_ma_position, update_ma_ema_positions, get_last_candle_and_ma, check_ema_conditions
from datetime import datetime


def monitor_ma_crossover(pairs, interval, ma_func, ma_args, ema_args, dispatcher):
    # Convert interval to seconds
    seconds = interval_to_seconds(interval)

    start_positions = {}
    start_candles = {}  # Store start candle for each pair
    start_mas = {}
    start_emas = {}

    last_positions = {}  # Store last position (above/below) of the price relative to the MAs for each pair

    for pair in pairs:
        start_positions[pair] = {}
        start_candles[pair] = {}
        start_mas[pair] = {}
        start_emas[pair] = {}
        last_positions[pair] = {}

        # Get start candle for the first loop
        start_candle, last_candle, opens, closes, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, last_emas, last_mas = get_last_candle_and_ma(
            pair, interval, ma_func, ma_args, ema_args)
        start_candles[pair] = start_candle
        start_mas[pair] = {'ma1': start_ma1, 'ma2': start_ma2}
        start_emas[pair] = {'ema1': start_ema1, 'ema2': start_ema2}

        # Permet de connaitre la position de la bougie de départ (above or below)
        start_position = get_ma_position(start_candle, start_mas[pair])
        start_positions[pair] = {'ma_position': start_position, 'ema_position': None}

    print(
        f"{datetime.fromtimestamp(start_candles['BTCUSDT']['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
        f"BTCUSDT Start Candle: Open = {start_candles['BTCUSDT']['open']}, Close = {start_candles['BTCUSDT']['close']}, "
        f"Timestamp = {start_candles['BTCUSDT']['timestamp']}, Volume = {start_candles['BTCUSDT']['volume']}"
    )

    # Initialize last_position for the first loop
    last_positions = start_positions
    last_candles = start_candles  # Store last candle for each pair
    last_mas = start_mas  # Store last MA values for each pair
    last_emas = start_emas

    while True:
        for pair in pairs:
            """start_candle, last_candle, opens, closes, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, last_ema2, last_emas, last_mas = get_last_candle_and_ma(
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
                    last_positions[pair] = {'ma_position': last_position, 'ema_position': None}"""

            last_positions, last_candles, last_mas, last_emas, last_position, last_candle = update_ma_ema_positions(
                pair, interval, ma_func, ma_args, ema_args, last_positions, last_candles)

            # Check MA position
            if last_positions[pair]['ma_position'] != last_position:
                print(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: MA Position change from"
                    f" {last_positions[pair]['ma_position']} to {last_position} for {pair}")
                last_positions[pair]['ma_position'] = last_position

                # Check EMA position
                ema_close, ema_crossed, ema_position, ema_below_ma, ema_above_ma = check_ema_conditions(last_emas,
                                                                                                        last_mas)
                print(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: EMA Close: {ema_close}, EMA Crossed: {ema_crossed}, "
                    f"EMA Position: {ema_position}, EMA Below: {ema_below_ma}, EMA Above: {ema_above_ma} for {pair}")

                if last_positions[pair]['ma_position'] == 'above' and (ema_close or ema_crossed) and ema_below_ma:
                    send_message_to_subscribed_users(dispatcher,
                                                     f"{pair} BUY signal detected at {datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(
                        f"{pair} BUY signal detected at {datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}")

                if last_positions[pair]['ma_position'] == 'below' and (ema_close or ema_crossed) and ema_above_ma:
                    send_message_to_subscribed_users(dispatcher,
                                                     f"{pair} SELL signal detected at {datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(
                        f"{pair} SELL signal detected at {datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}")

                last_positions[pair]['ema_position'] = ema_position
        print(
            f"{datetime.fromtimestamp(last_candles['BTCUSDT']['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
            f"BTCUSDT Last Candle: Open = {last_candles['BTCUSDT']['open']}, Close = {last_candles['BTCUSDT']['close']}, "
            f"Timestamp = {last_candles['BTCUSDT']['timestamp']}, Volume = {last_candles['BTCUSDT']['volume']}"
        )

        # Wait until the end of the candle
        time_to_wait = seconds - (time.time() % seconds)
        time.sleep(time_to_wait)  # Wait for the duration of the candle before checking prices again

        # return last_positions, last_candles, last_mas, last_emas
