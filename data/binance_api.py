import time
import os
import json
from binance.client import Client as BinanceClient
from binance.exceptions import BinanceAPIException

# Load configuration
binance_api_key = os.environ['BINANCE_API_KEY']
binance_api_secret = os.environ['BINANCE_API_SECRET']

# Initialize Binance API client
binance_client = BinanceClient(binance_api_key, binance_api_secret)


# Get klines data
def get_klines_data(symbol, interval, retry_on_error=True):
    try:
        # client = binance_client.get_klines(symbol=symbol, interval=interval)
        client = binance_client.futures_klines(symbol=symbol, interval=interval)
    except BinanceAPIException as e:
        print(f"Error: {e}")
        if retry_on_error:
            # Get the time remaining until the end of the current interval
            interval_ms = int(interval[:-1]) * 1000
            server_time = binance_client.get_server_time()
            timestamp = server_time['serverTime'] // 1000 * 1000
            time_remaining = interval_ms - (server_time['serverTime'] - timestamp)

            print(f"Retrying in {time_remaining} ms")
            time.sleep(time_remaining / 1000)
            return get_klines_data(symbol, interval, retry_on_error=True)
        else:
            return None

    return client


def get_usdt_perpetual_symbols():
    exchange_info = binance_client.futures_exchange_info()
    symbols = exchange_info['symbols']
    usdt_perpetual_symbols = [symbol['symbol'] for symbol in symbols if
                              symbol['quoteAsset'] == 'USDT' and symbol['contractType'] == 'PERPETUAL']
    return usdt_perpetual_symbols  # sorted Sort the symbols alphabetically


def update_config_file(config_file, new_pairs):
    # Open the configuration file for reading
    with open(config_file, 'r') as file:
        config_data = json.load(file)

    # Replace the existing pairs with the new pairs
    updated_pairs = new_pairs

    # Get the existing pairs from the configuration file
    # existing_pairs = set(config_data["pairs_to_monitor"])
    # new_pairs_set = set(new_pairs)

    # Add only the pairs that do not already exist in the configuration file
    # updated_pairs = list(existing_pairs.union(new_pairs_set))

    # Sort the pairs alphabetically
    # updated_pairs.sort()

    # Update the configuration file with the new list of pairs
    config_data["pairs_to_monitor"] = updated_pairs

    # Save the updated configuration file
    with open(config_file, 'w') as file:
        json.dump(config_data, file, indent=2)


def get_top_volume_symbols(interval, number_of_candles, top_pairs):
    usdt_perpetual_symbols = get_usdt_perpetual_symbols()
    symbol_volumes = []

    for symbol in usdt_perpetual_symbols:
        klines = get_klines_data(symbol, interval, retry_on_error=True)
        # Sum the volume (quote asset volume) of the last number_of_candles candles
        volume = sum([float(kline[7]) for kline in klines[-number_of_candles:]])
        symbol_volumes.append((symbol, volume))

    sorted_symbol_volumes = sorted(symbol_volumes, key=lambda x: x[1], reverse=True)
    top_volume_symbols = [symbol_volume[0] for symbol_volume in sorted_symbol_volumes[:top_pairs]]

    return top_volume_symbols
