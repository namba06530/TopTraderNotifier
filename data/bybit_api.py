from pybit.usdt_perpetual import HTTP
import os


def create_bybit_session(testnet=True):
    # Load configuration
    bybit_testnet_api_key = os.environ['BYBIT_TESTNET_API_KEY']
    bybit_testnet_api_secret = os.environ['BYBIT_TESTNET_API_SECRET']

    API_KEY = bybit_testnet_api_key
    API_SECRET = bybit_testnet_api_secret
    TESTNET = 'https://api-testnet.bybit.com'
    MAINNET = 'https://api.bybit.com'

    endpoint = TESTNET if testnet else MAINNET

    session = HTTP(endpoint=endpoint, api_key=API_KEY, api_secret=API_SECRET)
    return session

