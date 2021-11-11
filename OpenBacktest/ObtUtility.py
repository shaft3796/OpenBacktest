from decimal import Decimal
from binance.client import Client
from datetime import datetime
import pandas as pd


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
    return float(Decimal(a) / Decimal(b))


# used to apply the fees of a transaction to an amount of coins
def remove_fees(coin, fees):
    fee = coin * fees
    return fee


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


# Used to pull the value of a list or the value of a var if it's not a list
def pull(var, index):
    if isinstance(var, list):
        return var[index]
    else:
        return var


# create a blank dataframe
def initialise_dataframe(columns):
    data = {}
    for col in columns:
        data[col] = []
    return pd.DataFrame(data)


# append a row to the dataframe
def append_dataframe(dataframe, values):
    return dataframe.append(values, ignore_index=True)


# return the last row of the dataframe
def get_last_row(dataframe):
    return dataframe.iloc[-1]


# check if the wallet_frame is symmetric or asymmetric
def check_wallet_frame(wallet_frame):
    first = wallet_frame.iloc[1]["order_type"]
    last = None
    last_amount = 0
    for index, row in wallet_frame.iterrows():
        if row["order_type"] != "blank":
            if last is None:
                last = row["order_type"]
                last_amount = round(row["size"], 2)
                if last != first:
                    return False
            elif last == row["order_type"] or last_amount != round(row["size"], 2):
                print("returning because other")
                return False
            else:
                last = None
                last_amount = 0
    return True

