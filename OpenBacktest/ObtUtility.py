from decimal import Decimal
from binance.client import Client
from datetime import datetime


# --------------------------
# Data
# --------------------------

# Define console colors
class Colors:
    YELLOW = '\33[33m'
    LIGHT_YELLOW = '\33[93m'
    BLUE = '\33[34m'
    LIGHT_BLUE = '\33[94m'
    RED = '\33[31m'
    LIGHT_RED = '\33[91m'
    CYAN = '\33[36m'
    LIGHT_CYAN = '\33[96m'
    GREEN = '\33[32m'
    LIGHT_GREEN = '\33[92m'
    PURPLE = '\33[35m'
    LIGHT_PURPLE = '\33[95m'


# Define all binance timeframes
timeframes = {
    "1m": Client.KLINE_INTERVAL_1MINUTE,
    "3m": Client.KLINE_INTERVAL_3MINUTE,
    "5m": Client.KLINE_INTERVAL_5MINUTE,
    "15m": Client.KLINE_INTERVAL_15MINUTE,
    "30m": Client.KLINE_INTERVAL_30MINUTE,
    "1h": Client.KLINE_INTERVAL_1HOUR,
    "2h": Client.KLINE_INTERVAL_2HOUR,
    "4h": Client.KLINE_INTERVAL_4HOUR,
    "6h": Client.KLINE_INTERVAL_6HOUR,
    "8h": Client.KLINE_INTERVAL_8HOUR,
    "12h": Client.KLINE_INTERVAL_12HOUR,
    "1d": Client.KLINE_INTERVAL_1DAY,
    "3d": Client.KLINE_INTERVAL_3DAY,
    "1w": Client.KLINE_INTERVAL_1WEEK,
    "1M": Client.KLINE_INTERVAL_1MONTH,
}


# --------------------------
# Functions
# --------------------------

# Used to divide two float numbers properly
def divide(a, b):
    if b == 0:
        return None
    return float(Decimal(a)/Decimal(b))


# used to apply the fees of a transaction to an amount of coins
def remove_fees(coin, fees, wallet=None):
    fee = coin * fees
    if wallet is not None:
        wallet.total_fees += fee
    return coin - fee


# Used to parse timestamp into human readable date
def parse_timestamp(timestamp, strftime=None):
    # check if timestamp is in milliseconds
    if len(list(str(timestamp))) == 13:
        timestamp = divide(int(timestamp), 1000)

    # convert timestamp into date
    date = datetime.fromtimestamp(timestamp)

    # formatting date
    if strftime is not None:
        date = date.strftime(strftime)

    return str(date)
