import time
import os
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
        client = binance_client.get_klines(symbol=symbol, interval=interval)
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
