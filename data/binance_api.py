from binance.client import Client as BinanceClient
import json

# Load configuration
with open("./config.json", 'r') as f:
    config = json.load(f)

# Initialize Binance API client
binance_client = BinanceClient(config["binance_api_key"], config["binance_api_secret"])


# Get klines data
def get_klines_data(symbol, interval):
    client = binance_client.get_klines(symbol=symbol, interval=interval)
    return client
