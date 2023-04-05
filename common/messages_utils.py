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
                  f"{pair} BUY signal detected !\n" \
                  f"Entry Price = {entry_price:.2f}\n" \
                  f"Stop Loss = {stop_loss:.2f}\n" \
                  f"TP1 = {tp1:.2f}\n" \
                  f"TP2 = {tp2:.2f}"

    elif signal_type == 'sell':
        message = f"{datetime.fromtimestamp(candle['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n" \
                  f"{pair} SELL signal detected !\n" \
                  f"Entry Price = {entry_price:.2f}\n" \
                  f"Stop Loss = {stop_loss:.2f}\n" \
                  f"TP1 = {tp1:.2f}\n" \
                  f"TP2 = {tp2:.2f}"

    return message
