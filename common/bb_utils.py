import talib


def calculate_bollinger_bands(close_prices, period=130, std_dev=2):
    upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=period, nbdevup=std_dev,
                                                       nbdevdn=std_dev, matype=0)
    return upper_band, middle_band, lower_band


def calculate_bollinger_band_width(upper_band, lower_band):
    return upper_band - lower_band
