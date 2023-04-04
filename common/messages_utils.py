from datetime import datetime


def general_message(pair, candles, candle_name=str):
    message = f"{datetime.fromtimestamp(candles[pair]['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}: " \
              f"{pair} {candle_name}: Open = {candles[pair]['open']}, Close = {candles[pair]['close']}, " \
              f"Timestamp = {candles[pair]['timestamp']}, Volume = {candles[pair]['volume']}"
    return message


def signal_message(pair, signal_type, candle, entry_price, stop_loss, tp1, tp2):
    message = ""

    if signal_type == 'buy':
        message = f"{datetime.fromtimestamp(candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n" \
                  f"{pair} BUY signal detected !\n " \
                  f"Entry Price = {entry_price}\n" \
                  f"Stop Loss = {stop_loss}\n" \
                  f"TP1 = {tp1}\n" \
                  f"TP2 = {tp2}"

    elif signal_type == 'sell':
        message = f"{datetime.fromtimestamp(candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n" \
                  f"{pair} SELL signal detected !\n " \
                  f"Entry Price = {entry_price}\n" \
                  f"Stop Loss = {stop_loss}\n" \
                  f"TP1 = {tp1}\n" \
                  f"TP2 = {tp2}"

    return message
