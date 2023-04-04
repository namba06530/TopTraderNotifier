import time
from service.my_telegram_bot import *
from common.utils import interval_to_seconds
from common.ma_utils import get_ma_position, update_ma_ema_positions, get_last_candle_and_ma, check_ema_conditions, \
    check_ma_conditions
from common.messages_utils import signal_message, general_message
from business.components.buy_trade_params import calculate_buy_entry_price, calculate_buy_stop_loss, calculate_buy_tp1, \
    calculate_buy_tp2
from business.components.sell_trade_params import calculate_sell_entry_price, calculate_sell_stop_loss, \
    calculate_sell_tp1, calculate_sell_tp2
from datetime import datetime
from colorama import Fore, Style


def monitor_ma_crossover(pairs, interval, ma_func, ma_args, ema_args, dispatcher):
    # Convert interval to seconds
    seconds = interval_to_seconds(interval)

    start_positions = {}
    start_candles = {}
    start_mas = {}
    start_emas = {}

    last_positions = {}
    last_mas = {}
    last_emas = {}
    last_band_widths = {}

    for pair in pairs:
        # Get start candle for the first loop
        start_candle, last_candle, opens, closes, highs, lows, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, \
            last_ema2, prev_ema1, prev_ema2, prev_band_width, last_band_width = get_last_candle_and_ma(pair, interval, ma_func, ma_args, ema_args)

        start_candles[pair] = start_candle
        start_mas[pair] = {'ma1': start_ma1, 'ma2': start_ma2}
        start_emas[pair] = {'ema1': start_ema1, 'ema2': start_ema2}

        # Permet de connaitre la position de la bougie de départ (above or below)
        start_position = get_ma_position(start_candle, start_mas[pair])
        start_positions[pair] = {'ma_position': start_position, 'ema_position': None}

        last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
        last_emas[pair] = {'ema1': last_ema1, 'ema1_prev': prev_ema1, 'ema2': last_ema2, 'ema2_prev': prev_ema2}

        last_position = get_ma_position(last_candle, last_mas[pair])
        last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

        last_band_widths[pair] = {'prev_band_width': prev_band_width, 'last_band_width': last_band_width}

        # start_message = general_message(pair, start_candles, "Start Candle")
        # print(start_message)

    last_candles = start_candles

    while True:
        for pair in pairs:
            start_candle, last_candle, opens, closes, highs, lows, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, \
                last_ema2, prev_ema1, prev_ema2, prev_band_width, last_band_width = get_last_candle_and_ma(pair, interval, ma_func, ma_args, ema_args)

            if last_candles[pair]['timestamp'] != last_candle['timestamp']:
                # print(f"timestamp last_candle {pair} = {last_candle['timestamp']}")
                # print(f"timestamp last_candles[pair] {pair} = {last_candles[pair]['timestamp']}")

                last_candles[pair] = last_candle
                # print(f"Last candle {pair} = {last_candles[pair]}")
                last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
                last_emas[pair] = {'ema1': last_ema1, 'ema1_prev': prev_ema1, 'ema2': last_ema2, 'ema2_prev': prev_ema2}

                last_band_widths[pair] = {'prev_band_width': prev_band_width, 'last_band_width': last_band_width}

                # Compute the position of the last candle with respect to the MAs
                # Check if last candle close is above or below MAs
                last_position = get_ma_position(last_candle, last_mas[pair])
                print(f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                      f"{pair} Last Position: {last_position}")

                if last_position is None:
                    last_position = last_positions[pair]['ma_position']
                    print(f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                          f"{pair} Last Position: {last_position}")

                if pair not in last_positions:
                    last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

                # Check if MA position has changed
                if last_positions[pair]['ma_position'] != last_position:
                    print(
                        f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                        f"{pair} MA Position: Change from {last_positions[pair]['ma_position']} to {last_position}")

                    last_positions[pair]['ma_position'] = last_position

                    # Check if MAs are close to each other
                    ma_close = check_ma_conditions(pair, last_mas)
                    if ma_close:
                        print(
                            f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                            f"{pair} MAs Close = True")

                        # Check EMA position
                        ema_close, ema_crossed, ema_position, ema_below_ma, ema_above_ma = check_ema_conditions(pair,
                                                                                                                last_emas,
                                                                                                                last_mas)
                        last_positions[pair]['ema_position'] = ema_position

                        print(
                            f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                            f"{pair} EMAs Close: {ema_close}, EMAs Crossed: {ema_crossed}, "
                            f"EMAs Position: {ema_position}, EMAs Below: {ema_below_ma}, EMAs Above: {ema_above_ma}")

                        if last_positions[pair]['ma_position'] == 'above':
                            if ema_below_ma:
                                if ema_close or ema_crossed:
                                    entry_price = calculate_buy_entry_price(last_ma1, last_ma2, last_candle)
                                    stop_loss = calculate_buy_stop_loss(last_ma1, last_ma2, last_ema1, last_ema2, lows)
                                    tp1 = calculate_buy_tp1(entry_price, stop_loss)
                                    tp2 = calculate_buy_tp2(closes, period=130, std_dev=2)
                                    buy_message = signal_message(pair, 'buy', last_candle, entry_price,
                                                                 stop_loss, tp1, tp2)
                                    print(Fore.GREEN + buy_message)
                                    send_message_to_subscribed_users(dispatcher, buy_message)

                        if last_positions[pair]['ma_position'] == 'below':
                            if ema_above_ma:
                                if ema_close or ema_crossed:
                                    entry_price = calculate_sell_entry_price(last_ma1, last_ma2, last_candle)
                                    stop_loss = calculate_sell_stop_loss(last_ma1, last_ma2, last_ema1, last_ema2, highs)
                                    tp1 = calculate_sell_tp1(entry_price, stop_loss)
                                    tp2 = calculate_sell_tp2(closes, period=130, std_dev=2)
                                    sell_message = signal_message(pair, 'sell', last_candle, entry_price,
                                                                  stop_loss, tp1, tp2)
                                    print(Fore.RED + sell_message)
                                    send_message_to_subscribed_users(dispatcher, sell_message)
                    else:
                        print(
                            f"{datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: "
                            f"{pair} MAs Close = False")

                last_message = general_message(pair, last_candles, "Last Candle")
                print(last_message)

        # Wait until the end of the candle
        time_to_wait = seconds - (time.time() % seconds) + 10
        time.sleep(time_to_wait)  # Wait for the duration of the candle before checking prices again