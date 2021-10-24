import os

import pandas as pd
from binance.client import Client

from OpenBacktest.ObtPositions import Stop
from OpenBacktest.ObtUtility import Colors, timeframes
from OpenBacktest.ObtWallet import Wallet


# define an backtest engine
class Engine:
    # Initialising the class
    def __init__(self, container, output=True):
        if output:
            print(Colors.PURPLE + "Initialising BackTest Engine")

        # Container
        self.container = container
        self.container.load_all(output=output)

        # python-binance client
        self.client = Client()

        # Used to run a backtest
        self.strategy_function = None
        self.buy_condition = None
        self.sell_condition = None
        self.wallet = None

        # TP & SL
        self.tp = None
        self.sl = None

    def main_dataframe(self):
        return self.container.main.dataframe

    def alt_dataframe(self, name):
        return self.container.get_pair(name).dataframe

    # -------------------------------------------------------------------------------
    # def backtest parameters to run a simple strategy with buy & sell condition
    def register_sell_and_buy_condition(self, buy_condition, sell_condition):
        self.buy_condition = buy_condition
        self.sell_condition = sell_condition

    # run a simple backtest with buy & sell condition
    def run_sell_and_buy_condition(self, coin_name, token_name, coin_balance, token_balance, taker, maker, finish=True):
        # condition not None test
        if self.buy_condition is None or self.sell_condition is None:
            print(Colors.RED + "Error, you can't run a backtest because you don't have buy & sell condition functions "
                               "registered")
            return

        # Wallet initialisation
        self.wallet = Wallet(coin_name, token_name, coin_balance, token_balance, taker, maker,
                             self.main_dataframe())
        # Ini
        index = 0

        # Main loop
        while index <= self.container.main.max_index:

            if self.buy_condition(self.main_dataframe(), index) and self.wallet.coin_balance > 0:
                self.wallet.buy(index)
            elif self.sell_condition(self.main_dataframe(), index) and self.wallet.token_balance > 0:
                self.wallet.sell(index)

            # update tp & sl
            self.update_tp_sl(index)

            # end
            index += 1

        # Sell all remaining coins
        if self.wallet.token_balance > 0 and finish:
            self.wallet.sell(self.container.main.max_index)
    # -------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------
    # def backtest parameters to run a more advanced strategy with just one function to handle conditions
    def __register_mono_function(self, strategy_function):
        self.strategy_function = strategy_function

    # run a more advanced backtest with just one function to handle conditions
    def __run_mono_function(self, coin_name, token_name, coin_balance, token_balance, taker, maker, finish=True):
        # condition not None test
        if self.strategy_function is None:
            print(Colors.RED + "Error, you can't run a backtest because you don't have strategy function registered")
            return

        # Wallet initialisation
        self.wallet = Wallet(coin_name, token_name, coin_balance, token_balance, taker, maker,
                             self.main_dataframe())
        # Ini
        index = 0

        # Main loop
        while index <= self.container.main.max_index:

            report = self.strategy_function(self.main_dataframe(), index)

            if report is not None:
                if not isinstance(report, Report):
                    print(Colors.RED, "Error, your strategy function have to return an instance of Report")

                if report.order == "buy":
                    self.wallet.buy(index, report.amount, report.percent_amount)
                elif report.order == "sell":
                    self.wallet.sell(index, report.amount, report.percent_amount)
                else:
                    print(Colors.RED, "Error, the order value of a report have to be 'sell' or 'buy'")

            # update tp & sl
            self.update_tp_sl(index)

            # end
            index += 1

        # Sell all remaining coins
        if self.wallet.token_balance > 0 and finish:
            self.wallet.sell(self.container.main.max_index)
    # -------------------------------------------------------------------------------

    # place a take profit order
    def set_take_profit(self, target_price, amount=None, percent_amount=None):
        self.tp = Stop(self.wallet, "up", target_price, amount, percent_amount)

    # cancel a take profit order
    def cancel_take_profit(self):
        self.tp = None

    # place a stop loss order
    def set_stop_loss(self, target_price, amount=None, percent_amount=None):
        self.sl = Stop(self.wallet, "down", target_price, amount, percent_amount)

    # cancel a take profit order
    def cancel_stop_loss(self):
        self.sl = None

    # update tp & sl
    def update_tp_sl(self, index):
        if self.tp is not None:
            self.tp.update(index)

        if self.sl is not None:
            self.sl.update(index)


# define a pair
class Pair:
    def __init__(self, market_pair, start, timeframe, name="Default Name", path=""):

        self.pair = market_pair
        self.start = start
        self.timeframe = timeframe

        self.name = name

        self.dataframe = None
        self.max_index = None

        self.timestamps_with_index = None

        # First errors test
        ok = False
        for pair in Client().get_exchange_info()["symbols"]:
            if pair["symbol"] == self.pair:
                ok = True
                break
        if not ok:
            print(Colors.RED + "Error ! The trade pair", self.pair, "doesn't exist !")
            return

        ok = False
        for tf in timeframes:
            if timeframes[tf] == self.timeframe:
                ok = True
                break
        if not ok:
            print(Colors.RED + "Error ! The timeframe", self.timeframe, "doesn't exist !")
            return

        self.path = path + self.make_file_name()

    # Load / download the pair's dataframe
    def load(self, client=Client(), output=True):
        if os.path.isfile(self.path):
            # Loading from path
            if output:
                print(
                    "Loading data from a file for " + self.pair + " from " + self.start + " timeframe: " + self.timeframe)
            self.dataframe = pd.read_csv(self.path)
            if output:
                print(Colors.LIGHT_GREEN + "Data loaded successfully")
        else:
            # Downloading from API
            if output:
                print(
                    "Downloading data from API for " + self.pair + " from " + self.start + " timeframe: " + self.timeframe)
            self.dataframe = pd.DataFrame(client.get_historical_klines(self.pair, self.timeframe,
                                                                       self.start),
                                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                                   'close_time',
                                                   'quote_av', 'trades',
                                                   'tb_base_av', 'tb_quote_av', 'ignore'])
            # Parsing it
            self.dataframe['close'] = pd.to_numeric(self.dataframe['close'])
            self.dataframe['high'] = pd.to_numeric(self.dataframe['high'])
            self.dataframe['low'] = pd.to_numeric(self.dataframe['low'])
            self.dataframe['open'] = pd.to_numeric(self.dataframe['open'])
            if output:
                print(Colors.LIGHT_GREEN + "Data downloaded successfully")

        self.max_index = len(self.dataframe["close"]) - 1
        self.timestamps_with_index = {key: i for i, key in enumerate(self.dataframe["timestamp"])}

    # Save the market data into file(s)
    def save(self, default_path="", output=True):
        path = default_path + self.make_file_name()
        self.dataframe.to_csv(path, index=False)
        if output:
            print(
                Colors.LIGHT_GREEN + "Saved dataframe as file for " + self.pair + " from " + self.start + " timeframe: " + self.timeframe)

    # create with class data a file name
    def make_file_name(self):
        return Pair.make_name(self.pair, self.start, self.timeframe)

    # find the index of a given timestamp
    def get_index(self, timestamp):

        absolute_difference_function = lambda list_value: abs(list_value - timestamp)

        closest_value = min(self.dataframe["timestamp"], key=absolute_difference_function)

        if closest_value <= timestamp:
            index = self.timestamps_with_index[closest_value]
        else:
            index = self.timestamps_with_index[closest_value] - 1

        if index < 0:
            print(Colors.RED + "Error ! The row you are trying to get the equivalent index of an alt dataframe is "
                               "older than the beginning of this dataframe")
            exit()

        return index

    # make_file_name core method
    @staticmethod
    def make_name(market_pair, start, timeframe):
        start = start.replace(" ", "#")
        return market_pair + "-" + start + "-" + timeframe + "-.csv"

    # parse_file_name core method ( Currently useless )
    @staticmethod
    def parse_name(name):
        first_split = name.split("/")
        second_split = first_split[len(first_split) - 1].split("-")
        market_pair = second_split[0]
        start = second_split[1].replace("#", " ")
        timeframe = timeframes[second_split[2]]
        return market_pair, start, timeframe


# Define pairs data container
class Container:
    def __init__(self, client=Client()):
        self.pairs = {}
        self.main = None
        self.client = client

    def add_pair(self, pair):
        self.pairs[pair.name] = pair
        if self.main is None:
            self.main = pair

    def add_main_pair(self, pair):
        self.pairs[pair.name] = pair
        self.main = pair

    def get_pair(self, name):
        return self.pairs[name]

    def load_all(self, output=True):
        current_pair = 1
        total_pairs = len(self.pairs)
        for pair in self.pairs:
            pair = self.pairs[pair]
            if output:
                print(Colors.PURPLE + "Pair", current_pair, "/", total_pairs)
            pair.load(self.client)
            current_pair += 1

    def save_all(self, default_path="", output=True):
        current_pair = 1
        total_pairs = len(self.pairs)
        for pair in self.pairs:
            pair = self.pairs[pair]
            if output:
                print(Colors.PURPLE + "Pair", current_pair, "/", total_pairs)
            pair.save(default_path=default_path, output=output)
            current_pair += 1


# Define a report to decide of what to do
class Report:
    def __init__(self, order, amount=None, percent_amount=None):
        self.order = order
        self.amount = amount
        self.percent_amount = percent_amount
