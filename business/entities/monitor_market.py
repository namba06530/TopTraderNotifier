import time
from common.bb_utils import calculate_bollinger_bands, calculate_bollinger_band_width, \
    calculate_bollinger_band_relative_width
from common.macd_utils import calculate_macd
from service.my_telegram_bot import send_message_to_subscribed_users
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
from data.bybit_api import create_bybit_session
from business.entities.bybit_order import place_order, calculate_order_quantity


def monitor_ma_crossover(pairs, interval, ma_func, ma_args, ema_args, dispatcher):  # dispatcher
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
            last_ema2, prev_ema1, prev_ema2, prev_band_width, last_band_width, ma1, ma2, ema1, ema2 = get_last_candle_and_ma(
            pair, interval, ma_func, ma_args, ema_args)

        start_candles[pair] = start_candle
        start_mas[pair] = {'ma1': start_ma1, 'ma2': start_ma2}
        start_emas[pair] = {'ema1': start_ema1, 'ema2': start_ema2}

        # To know the starting candle position (above or below)
        start_position = get_ma_position(start_candle, start_mas[pair])
        start_positions[pair] = {'ma_position': start_position, 'ema_position': None}

        last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
        last_emas[pair] = {'ema1': last_ema1, 'ema1_prev': prev_ema1, 'ema2': last_ema2, 'ema2_prev': prev_ema2}

        last_position = get_ma_position(last_candle, last_mas[pair])
        last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

        last_band_widths[pair] = {'prev_band_width': prev_band_width, 'last_band_width': last_band_width}

    last_candles = start_candles

    while True:
        for pair in pairs:
            start_candle, last_candle, opens, closes, highs, lows, start_ma1, start_ma2, start_ema1, start_ema2, last_ma1, last_ma2, last_ema1, \
                last_ema2, prev_ema1, prev_ema2, prev_band_width, last_band_width, ma1, ma2, ema1, ema2 = get_last_candle_and_ma(
                pair, interval, ma_func, ma_args, ema_args)

            if last_candles[pair]['timestamp'] != last_candle['timestamp']:

                last_candles[pair] = last_candle
                last_mas[pair] = {'ma1': last_ma1, 'ma2': last_ma2}
                last_emas[pair] = {'ema1': last_ema1, 'ema1_prev': prev_ema1, 'ema2': last_ema2, 'ema2_prev': prev_ema2}

                last_band_widths[pair] = {'prev_band_width': prev_band_width, 'last_band_width': last_band_width}

                # Calculate the new MACD values
                macd, macd_signal, macd_hist = calculate_macd(closes)

                lookback_period = 5

                # Calculate the slope of the MACD line
                macd_slope = macd[-1] - macd[-lookback_period]
                macd_slope_positive = macd_slope > 0
                macd_slope_negative = macd_slope < 0

                # Calculate the slope of the MACD signal line
                macd_signal_slope = macd_signal[-1] - macd_signal[-lookback_period]
                macd_signal_slope_positive = macd_signal_slope > 0
                macd_signal_slope_negative = macd_signal_slope < 0

                # Check if MACD conditions are met within the last 5 candles
                macd_cross_above = any(
                    macd[i] > macd_signal[i] and macd[i - 1] <= macd_signal[i - 1] for i in range(-1, -6, -1))
                macd_cross_below = any(
                    macd[i] < macd_signal[i] and macd[i - 1] >= macd_signal[i - 1] for i in range(-1, -6, -1))

                # Calculate Bollinger Bands
                upper_band, middle_band, lower_band = calculate_bollinger_bands(closes)

                # Calculate Bollinger Band width and relative width
                band_width = calculate_bollinger_band_width(upper_band, lower_band)
                relative_band_width = calculate_bollinger_band_relative_width(upper_band, lower_band, middle_band)

                # Define the threshold for low volatility
                low_volatility_threshold = 0.03

                # Compute the position of the last candle with respect to the MAs
                # Check if last candle close is above or below MAs
                last_position = get_ma_position(last_candle, last_mas[pair])

                # If last_position is None, use the previous stored value
                if last_position is None:
                    last_position = last_positions[pair]['ma_position']

                # If the pair is not already in last_positions, add it with the current values
                if pair not in last_positions:
                    last_positions[pair] = {'ma_position': last_position, 'ema_position': None}

                # Check if MA position has changed
                if last_positions[pair]['ma_position'] != last_position and last_positions[pair]['ma_position'] is not None:
                    timestamp = datetime.fromtimestamp(last_candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    print(
                        f"{timestamp} {pair} MA Position: Change from {last_positions[pair]['ma_position']} to {last_position}")

                    # Update the stored MA position
                    last_positions[pair]['ma_position'] = last_position

                    # Check if the relative band width is above the low volatility threshold
                    volatility = relative_band_width[-1] * 100
                    threshold = low_volatility_threshold * 100
                    print(f"{timestamp} {pair} Volatility: {round(volatility, 2)}% Threshold: {threshold}%")

                    if volatility > threshold:
                        # Check if MAs are close to each other
                        ma_close = check_ma_conditions(pair, last_mas)
                        print(f"{timestamp} {pair} MAs Close: {ma_close}")

                        if ma_close:
                            # Check EMA position
                            ema_close, ema_crossed, ema_position, ema_below_ma, ema_above_ma = check_ema_conditions(
                                pair,
                                last_emas,
                                last_mas)
                            last_positions[pair]['ema_position'] = ema_position

                            print(f"{timestamp} {pair} EMAs Position: {ema_position} EMAs Close: {ema_close} EMAs "
                                  f"Crossed: {ema_crossed} EMAs Above MAs: {ema_above_ma} EMAs Below MAs: {ema_below_ma}")

                            if last_positions[pair][
                                'ma_position'] == 'above' and macd_cross_above and macd_slope_positive and macd_signal_slope_positive:

                                print(f"{timestamp} {pair} MAs Position: {last_positions[pair]['ma_position']} "
                                      f"MACD Cross Above: {macd_cross_above} MACD Slope Positive: {macd_slope_positive} "
                                      f"MACD Signal Slope Positive: {macd_signal_slope_positive}")

                                print(f"{timestamp} {pair} EMAs Below MAs: {ema_below_ma}")

                                if ema_below_ma:
                                    print(f"{timestamp} {pair} EMAs Closes: {ema_close} EMAs Crossed: {ema_crossed}")

                                    if ema_close or ema_crossed:
                                        entry_price = calculate_buy_entry_price(last_ma1, last_ma2, last_candle)
                                        stop_loss = calculate_buy_stop_loss(lows, closes)
                                        print(f"{timestamp} {pair} Stop Loss: {stop_loss}")

                                        if stop_loss is not None:
                                            tp1 = calculate_buy_tp1(entry_price, stop_loss)
                                            tp2 = calculate_buy_tp2(closes)
                                            print(f"{timestamp} {pair} TP1: {tp1} TP2: {tp2}")

                                            if tp1 < tp2:
                                                print(f"{timestamp} {pair} TP1 < TP2 Buy Signal Validated !")
                                                buy_message = signal_message(pair, 'buy', last_candle, entry_price,
                                                                             stop_loss, tp1, tp2)
                                                print(Fore.GREEN + buy_message)
                                                print(Style.RESET_ALL)
                                                send_message_to_subscribed_users(dispatcher, buy_message)

                                                # Place the buy order with stop loss and take profits
                                                session = create_bybit_session()
                                                qty = calculate_order_quantity(session)
                                                entry_order, stop_order, tp_orders = place_order(session, pair, 'Buy',
                                                                                                 qty,
                                                                                                 entry_price, stop_loss,
                                                                                                 tp1,
                                                                                                 tp2, interval)
                                                print("Order placed:", entry_order)

                            if last_positions[pair][
                                'ma_position'] == 'below' and macd_cross_below and not macd_slope_negative and not macd_signal_slope_negative:

                                print(f"{timestamp} {pair} MAs Position: {last_positions[pair]['ma_position']} "
                                      f"MACD Cross Below: {macd_cross_below} MACD Slope Negative: {macd_slope_negative} "
                                      f"MACD Signal Slope Negative: {macd_signal_slope_negative}")

                                print(f"{timestamp} {pair} EMAs Above MAs: {ema_above_ma}")

                                if ema_above_ma:

                                    print(f"{timestamp} {pair} EMAs Closes: {ema_close} EMAs Crossed: {ema_crossed}")

                                    if ema_close or ema_crossed:
                                        entry_price = calculate_sell_entry_price(last_ma1, last_ma2, last_candle)
                                        stop_loss = calculate_sell_stop_loss(highs, closes)
                                        print(f"{timestamp} {pair} Stop Loss: {stop_loss}")

                                        if stop_loss is not None:
                                            tp1 = calculate_sell_tp1(entry_price, stop_loss)
                                            tp2 = calculate_sell_tp2(closes)
                                            print(f"{timestamp} {pair} TP1: {tp1} TP2: {tp2}")

                                            if tp1 > tp2:
                                                print(f"{timestamp} {pair} TP1 > TP2 Sell Signal Validated !")
                                                sell_message = signal_message(pair, 'sell', last_candle, entry_price,
                                                                              stop_loss, tp1, tp2)
                                                print(Fore.RED + sell_message)
                                                print(Style.RESET_ALL)
                                                send_message_to_subscribed_users(dispatcher, sell_message)

                                                # Place the sell order with stop loss and take profits
                                                session = create_bybit_session()
                                                qty = calculate_order_quantity(session)
                                                entry_order, stop_order, tp_orders = place_order(session, pair, 'Sell',
                                                                                                 qty,
                                                                                                 entry_price, stop_loss,
                                                                                                 tp1,
                                                                                                 tp2, interval)
                                                print("Order placed:", entry_order)
                if last_position is not None:
                    last_positions[pair]['ma_position'] = last_position

        # Wait until the end of the candle
        time_to_wait = seconds - (time.time() % seconds) + 10
        time.sleep(time_to_wait)  # Wait for the duration of the candle before checking prices again
