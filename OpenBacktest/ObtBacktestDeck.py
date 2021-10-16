import pandas as pd
from binance.client import Client

# define a deck
from OpenBacktest.ObtUtility import Colors, timeframes
from OpenBacktest.ObtWallet import Wallet


class BackTestDeck:
    # Initialising the class
    def __init__(self, market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1DAY, path=None,
                 output=True):
        print(Colors.PURPLE + "Initialising BackTest Deck")

        # python-binance client
        self.client = Client()
        self.buy_condition = None
        self.sell_condition = None
        self.wallet = None

        # Case 1, get new data
        if path is None:
            # pairName = "ETHUSDT"
            self.pair = market_pair
            # "01 january 2021"
            self.start = start
            # Client.KLINE_INTERVAL_1DAY
            self.timeframe = timeframe
            # Load data
            if output:
                print("Getting Data. .")
            self.data = self.client.get_historical_klines(self.pair, self.timeframe, self.start)
            if output:
                print("Parsing Data. .")
            # parsing
            self.dataframe = pd.DataFrame(self.data,
                                          columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                                   'quote_av', 'trades',
                                                   'tb_base_av', 'tb_quote_av', 'ignore'])

            self.dataframe['close'] = pd.to_numeric(self.dataframe['close'])
            self.dataframe['high'] = pd.to_numeric(self.dataframe['high'])
            self.dataframe['low'] = pd.to_numeric(self.dataframe['low'])
            self.dataframe['open'] = pd.to_numeric(self.dataframe['open'])
            if output:
                print(
                    Colors.LIGHT_GREEN + "Data loaded for " + market_pair + " from " + start + " timeframe: " + timeframe + Colors.LIGHT_YELLOW)
        # Case 2, from file
        else:
            if output:
                print("Loading data from file. .")
            self.parse_file_name(path)
            self.data = None
            self.dataframe = pd.read_csv(path)
            if output:
                print(
                    Colors.LIGHT_GREEN + "Data loaded for " + self.pair + " from " + self.start + " timeframe: " + self.timeframe + Colors.LIGHT_YELLOW)

        self.max_index = len(self.dataframe['close']) - 1

    # Save the market data into a file
    def save(self, path=None, output=True):
        if path is None:
            path = self.make_file_name()
        self.dataframe.to_csv(path, index=False)
        if output:
            print(Colors.LIGHT_GREEN + "Saved dataframe as file")

    # create with class data a file name
    def make_file_name(self):
        return BackTestDeck.make_name(self.pair, self.start, self.timeframe)

    # make with file name class data
    def parse_file_name(self, path):
        name = path.split("/")[len(path.split("/")) - 1]
        parsed = BackTestDeck.parse_name(name)
        self.pair = parsed[0]
        self.start = parsed[1]
        self.timeframe = parsed[2]

    # def backtest parameters to run a simple strategy with buy & sell condition
    def register(self, buy_condition, sell_condition):
        self.buy_condition = buy_condition
        self.sell_condition = sell_condition

    # run a simple strategy
    def run(self, coin_name, token_name, coin_balance, token_balance, taker, maker, sell_all=True):
        self.wallet = Wallet(coin_name, token_name, coin_balance, token_balance, taker, maker, self.dataframe)
        index = 0
        last_price = 0
        while index <= self.max_index:

            if self.buy_condition(self.dataframe, index) and self.wallet.coin_balance > 0:
                self.wallet.buy_all(self.dataframe['close'][index], dataframe=self.dataframe, index=index)
            elif self.sell_condition(self.dataframe, index) and self.wallet.token_balance > 0:
                self.wallet.sell_all(self.dataframe['close'][index], dataframe=self.dataframe, index=index)
            last_price = self.dataframe['close'][index]

            # end
            index += 1

        # Sell all remaining coins
        if self.wallet.token_balance > 0 and sell_all:
            self.wallet.sell_all(last_price)

    # read and parse a csv file
    @staticmethod
    def read(path):
        return pd.read_csv(path)

    # make_file_name core method
    @staticmethod
    def make_name(market_pair, start, timeframe):
        start = start.replace(" ", "#")
        return market_pair + "-" + start + "-" + timeframe + "-.csv"

    # parse_file_name core method
    @staticmethod
    def parse_name(name):
        part = name.split("-")
        market_pair = part[0]
        start = part[1].replace("#", " ")
        timeframe = timeframes[part[2]]
        return market_pair, start, timeframe
