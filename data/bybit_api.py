# from pybit.unified_trading import HTTP
import os
import bybit


def create_bybit_session():
    # Load configuration
    bybit_testnet_api_key = os.environ['BYBIT_TESTNET_API_KEY']
    bybit_testnet_api_secret = os.environ['BYBIT_TESTNET_API_SECRET']

    API_KEY = bybit_testnet_api_key
    API_SECRET = bybit_testnet_api_secret
    TESTNET = True

    if TESTNET:
        session = bybit.bybit(test=True, api_key=API_KEY, api_secret=API_SECRET)
    else:
        session = bybit.bybit(test=False, api_key=API_KEY, api_secret=API_SECRET)
    return session

