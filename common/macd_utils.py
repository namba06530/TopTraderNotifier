import talib


def calculate_macd(closes, fastperiod=12, slowperiod=26, signalperiod=9):
    # Calculate the MACD, MACD signal, and MACD histogram using TA-Lib
    macd, macd_signal, macd_hist = talib.MACD(closes, fastperiod, slowperiod, signalperiod)

    return macd, macd_signal, macd_hist
