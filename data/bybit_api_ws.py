import os
from pybit.usdt_perpetual import WebSocket

# Load configuration
bybit_testnet_api_key = os.environ['BYBIT_TESTNET_API_KEY']
bybit_testnet_api_secret = os.environ['BYBIT_TESTNET_API_SECRET']

API_KEY = bybit_testnet_api_key
API_SECRET = bybit_testnet_api_secret
TESTNET = True
CHANNEL_WS = "linear"
CHANNEL_WS_PRIVATE = "private"


ws = WebSocket(testnet=TESTNET, channel_type=CHANNEL_WS)
ws_private = WebSocket(testnet=TESTNET, channel_type=CHANNEL_WS_PRIVATE, api_key=API_KEY, api_secret=API_SECRET)
