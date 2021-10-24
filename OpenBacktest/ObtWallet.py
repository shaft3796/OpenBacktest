from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from OpenBacktest.ObtUtility import divide, Colors, remove_fees, parse_timestamp
from OpenBacktest.ObtPositions import PositionBook, LongPosition


# ----------------------------------------------------------------------------------------------
# This class represent a wallet and is used to pass buy and sell orders of a symmetric strategy
# ----------------------------------------------------------------------------------------------
class Wallet:
    def __init__(self, coin_name, token_name, coin_balance, token_balance, taker, maker, dataframe):
        # Initial coin balance ( will not be modified )
        self.ini_coin_balance = coin_balance
        # Initial token balance ( will not be modified )
        self.ini_token_balance = token_balance
        # Current coin balance ( should be modified )
        self.coin_balance = coin_balance
        # Current token balance
        self.token_balance = token_balance

        # name of the coin
        self.coin_name = coin_name
        # symbol of the token
        self.token_name = token_name

        # Taker fees
        self.taker = divide(taker, 100.0)
        # Maker fees
        self.maker = divide(maker, 100.0)

        # Represent the current trade if there is an opened position
        self.last_trade = None
        # Represent all trades
        self.position_book = PositionBook()
        # Dataframe
        self.dataframe = dataframe

        # total fees
        self.total_fees = 0

        # data handler
        self.data_handler = DataHandler(self)

    def buy(self, index, amount=None, percent_amount=None):

        if self.position_book.last_position is not None and not self.position_book.last_position.closed:
            print(Colors.YELLOW, "Advert, buy order is not placeable because a long position is already opened")
            return

        if amount is None:
            if percent_amount is None:
                amount = self.coin_balance
            else:
                amount = self.coin_balance * divide(percent_amount, 100)
        else:
            if amount > self.coin_balance:
                amount = self.coin_balance

        # Updating Position Book
        # opening a new Position
        position = LongPosition()
        position.open(self.dataframe["timestamp"][index], self.dataframe["close"][index], self.coin_balance, amount)
        self.position_book.add_position(position)

        # Buying
        self.token_balance = remove_fees(divide(amount, self.dataframe["close"][index]), self.taker, self)
        self.coin_balance = self.coin_balance - amount

    def sell(self, index, amount=None, percent_amount=None):
        if self.position_book.last_position is None or self.position_book.last_position.closed:
            print(Colors.YELLOW, "Advert, sell order is not placeable because there is no opened long position")
            return

        if amount is None:
            if percent_amount is None:
                amount = self.token_balance
            else:
                amount = self.token_balance * divide(percent_amount, 100)
        else:
            if amount > self.token_balance:
                amount = self.token_balance

        # Selling
        old_coin_balance = self.coin_balance
        self.coin_balance = remove_fees(self.token_balance * self.dataframe["close"][index], self.taker, self)
        self.token_balance = self.token_balance - amount

        # Updating Position Book
        # loading current Position
        position = self.position_book.last_position
        # closing the position
        position.close(self.dataframe["timestamp"][index], self.dataframe["close"][index], self.coin_balance,
                       self.coin_balance - old_coin_balance)


# -------------------------------------------------------------------------------
# This class is used to summarize backtest result of a symmetric strategy
# -------------------------------------------------------------------------------
class DataHandler:
    def __init__(self, wallet):
        self.wallet = wallet

        # Informative values, these values are initialized but will be calculated by make_data() function
        # coin profit
        self.profit = 0
        # coin profit in %
        self.percent_profit = 0
        # number of total trades
        self.total_trades = 0
        # number of total positive trades
        self.total_positives_trades = 0
        # number of total negative trades
        self.total_negatives_trades = 0
        # Ratio of positive trades against number of total trades ( winrate )
        self.positives_trades_ratio = 0
        # number of total negative trades
        self.negatives_trades_ratio = 0
        # Worst trade
        self.worst_trade = None
        # Best
        self.best_trade = None
        # Average positive trades profit
        self.average_positive_trades = 0
        # Average negative trades profit
        self.average_negative_trades = 0
        # Average trades profit
        self.average_profit_per_trades = 0
        # Last close time
        self.end = None
        # First close time
        self.start = None
        # total day of backtest
        self.total_inday_trading_time = None
        # first close price
        self.first_price = None
        # last close price
        self.last_price = None
        # Buy & hold profit from start time to end time
        self.buy_and_hold_profit = None
        # Buy & hold profit in % from start time to end time
        self.buy_and_hold_percent_profit = None
        # Strategy profit vs buy & hold profit
        self.strategy_vs_buy_and_hold = None
        # Strategy profit vs buy & hold profit in %
        self.strategy_vs_buy_and_hold_percent = None
        # Average profit per day
        self.average_profit_per_day = None
        # aver profit per day in %
        self.average_percent_profit_per_day = None
        # exposure time
        self.exposure_time = 0
        # exposure time in %
        self.percent_exposure_time = None
        # average exposure time per trades
        self.average_exposure_time = None
        # average exposure time per trades in %
        self.average_percent_exposure_time = None

    # Make the required data to display wallet
    def make_data(self):
        # Total number of trades
        self.total_trades = self.wallet.position_book.last_position_index + 1
        # return if there were no trades
        if self.total_trades == 0:
            return

        # --- Total Profit ---
        self.profit = self.wallet.coin_balance - self.wallet.ini_coin_balance
        # Profit in percent depending of initial coin balance
        self.percent_profit = divide(100 * self.profit, self.wallet.ini_coin_balance)

        # --- Trades ---

        # Ini
        positive_trades_profit = []
        positive_trades_percent_profit = []
        negative_trades_profit = []
        negative_trades_percent_profit = []
        trades_profit = []
        trades_percent_profit = []
        exposures = []

        for position in self.wallet.position_book.book:

            # Count positive & negative trades and collect data to make average positive & negative trades profit
            if position.trade_profit > 0:
                positive_trades_profit.append(position.trade_profit)
                positive_trades_percent_profit.append(position.percent_trade_profit)
                self.total_positives_trades += 1
            elif position.trade_profit < 0:
                negative_trades_profit.append(position.trade_profit)
                negative_trades_percent_profit.append(position.percent_trade_profit)
                self.total_negatives_trades += 1

            # Collect data to make average positive & negative trades profit
            trades_profit.append(position.trade_profit)
            trades_percent_profit.append(position.percent_trade_profit)

            # Initializing worst_trade & best_trade values with the first trade
            if self.worst_trade is None or self.best_trade is None:
                self.worst_trade = position
                self.best_trade = position
            # Updating best_trade
            if position.percent_trade_profit > self.best_trade.percent_trade_profit:
                self.best_trade = position
            # Updating worst_trade
            if position.percent_trade_profit < self.worst_trade.percent_trade_profit:
                self.worst_trade = position

            # Filling exposures list and incrementing total exposure time
            self.exposure_time += position.position_time
            exposures.append(position.position_time)

        # positive trades ratio depending of total numbers of trades
        self.positives_trades_ratio = divide(100 * self.total_positives_trades, self.total_trades)
        # negative trades ratio depending of total numbers of trades
        self.negatives_trades_ratio = divide(100 * self.total_negatives_trades, self.total_trades)
        # Average positive trades
        if len(positive_trades_profit) == 0:
            positive_trades_profit.append(0)
            positive_trades_percent_profit.append(0)
        self.average_positive_trades = (
            round(mean(positive_trades_profit), 2), round(mean(positive_trades_percent_profit), 2))
        # Average negative trades
        if len(negative_trades_profit) == 0:
            negative_trades_profit.append(0)
            negative_trades_percent_profit.append(0)
        self.average_negative_trades = (
            round(mean(negative_trades_profit), 2), round(mean(negative_trades_percent_profit), 2))
        # Average profit per trades
        if len(trades_profit) == 0:
            trades_profit.append(0)
            trades_percent_profit.append(0)
        self.average_profit_per_trades = (
            round(mean(trades_profit), 2), round(mean(trades_percent_profit), 2))

        # Last timestamp of the period
        self.end = self.wallet.dataframe['timestamp'][len(self.wallet.dataframe['timestamp']) - 1]
        # First timestamp of the period
        self.start = self.wallet.dataframe['timestamp'][0]
        # Total days from first timestamp to the last one
        self.total_inday_trading_time = divide(int(self.end - self.start), 86400000)
        # First close price of the dataframe
        self.first_price = self.wallet.dataframe['close'][0]
        # Last close price of the dataframe
        self.last_price = self.wallet.dataframe['close'][len(self.wallet.dataframe['close']) - 1]
        # Profit with buy & hold
        self.buy_and_hold_profit = divide(self.wallet.ini_coin_balance * self.last_price, self.first_price)
        # Profit with buy & hold in %
        self.buy_and_hold_percent_profit = divide(100 * self.last_price, self.first_price)
        # Strategy performance vs buy & hold
        self.strategy_vs_buy_and_hold = self.profit - self.buy_and_hold_profit
        # Strategy performance vs buy & hold in %
        self.strategy_vs_buy_and_hold_percent = self.percent_profit - self.buy_and_hold_percent_profit
        # Average profit generated per day
        self.average_profit_per_day = divide(self.profit, self.total_inday_trading_time)
        # Average profit generated per day in %
        self.average_percent_profit_per_day = divide(self.percent_profit, self.total_inday_trading_time)
        # Average exposure time that mean average time of a trade
        self.average_exposure_time = mean(exposures)
        # Average exposure time that mean average time of a trade in %
        self.average_percent_exposure_time = divide(100 * self.average_exposure_time, self.total_inday_trading_time)
        # Total exposure time in %
        self.percent_exposure_time = divide(100 * self.exposure_time, self.total_inday_trading_time)

    # Summarize all trades & wallet evolution, strategy stats
    def display_wallet(self):
        # Build all required data
        self.make_data()
        # If there were no trades
        if self.total_trades == 0:
            print(Colors.YELLOW, "This strategy didn't traded")
            return

        # --- Intro ---

        print(Colors.PURPLE + "----------------------------------------------------")
        print("Data from", parse_timestamp(self.start), "to", parse_timestamp(self.end))
        print("Total trading time:", str(round(self.total_inday_trading_time, 2)), "day(s)")
        print("----------------------------------------------------")

        # --- Wallet data ---
        # title
        print(Colors.YELLOW + "[-Wallet-]")
        # Initial coin balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.coin_name, round(float(self.wallet.ini_coin_balance), 3))
        # Final coin balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.coin_name, round(float(self.wallet.coin_balance), 3))
        # Initial token balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.token_name, round(float(self.wallet.ini_token_balance), 3))
        # Final token balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.token_name, round(float(self.wallet.token_balance), 6))

        # Profit
        if self.profit == 0:
            print(Colors.CYAN, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), )) + "%")
        elif self.profit < 0:
            print(Colors.RED, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), )) + "%")
        else:
            print(Colors.GREEN, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), )) + "%")

        # Average profit per trades
        print(" Average profit per trades: ", self.average_profit_per_trades[0], "/",
              str(self.average_profit_per_trades[1]) + "%")

        # Average profit per day
        print(" Average profit per day: ", round(self.average_profit_per_day, 2), "/",
              str(round(self.average_percent_profit_per_day, 2)) + "%")

        # Fees
        print(Colors.LIGHT_RED, "Fees: ", round(float(self.wallet.total_fees), 3), self.wallet.coin_name, "/",
              str(round(divide(100 * float(self.wallet.total_fees), self.wallet.coin_balance), 2)) + "%")

        # Buy & hold profit
        if self.buy_and_hold_profit == 0:
            print(Colors.CYAN, "Buy & hold profit: ", round(float(self.buy_and_hold_profit), 2), "/",
                  str(round(float(self.buy_and_hold_percent_profit), )) + "%")
        elif self.buy_and_hold_profit < 0:
            print(Colors.RED, "Buy & hold profit: ", round(float(self.buy_and_hold_profit), 2), "/",
                  str(round(float(self.buy_and_hold_percent_profit), )) + "%")
        else:
            print(Colors.GREEN, "Buy & hold profit: ", round(float(self.buy_and_hold_profit), 2), "/",
                  str(round(float(self.buy_and_hold_percent_profit), )) + "%")

        # Strategy vs Buy & Hold
        if self.strategy_vs_buy_and_hold == 0:
            print(Colors.CYAN, "Strategy vs buy & hold: ", round(float(self.strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(self.strategy_vs_buy_and_hold_percent), )) + "%")
        elif self.strategy_vs_buy_and_hold < 0:
            print(Colors.RED, "Strategy vs buy & hold: ", round(float(self.strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(self.strategy_vs_buy_and_hold_percent), )) + "%")
        else:
            print(Colors.GREEN, "Strategy vs buy & hold: ", round(float(self.strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(self.strategy_vs_buy_and_hold_percent), )) + "%")

        print("")

        # --- Trades data ---
        print(Colors.YELLOW + "[-Trades-]")
        # Total number of trades
        print(Colors.BLUE, "Total trades:", self.total_trades)
        # Total number of positive trades
        print(Colors.GREEN, "Total positive trades:", self.total_positives_trades, "/",
              str(round(self.positives_trades_ratio)) + "%")
        # Total number of negative trades
        print(Colors.RED, "Total negative trades:", self.total_negatives_trades, "/",
              str(round(self.negatives_trades_ratio)) + "%")
        # Average positive trades
        print(Colors.GREEN, "Average positive trades profit: " + "+" + str(self.average_positive_trades[0]), "/",
              "+" + str(self.average_positive_trades[1]) + "%")
        # Average positive trades
        print(Colors.RED, "Average negative trades profit: " + str(self.average_negative_trades[0]), "/",
              str(self.average_negative_trades[1]) + "%")
        # Best trade data
        print(Colors.GREEN, "Best trade: +" + str(round(self.best_trade.trade_profit, 2)) + " / +" +
              str(round(self.best_trade.percent_trade_profit)) + "%" + "  " +
              str(parse_timestamp(self.best_trade.sell_timestamp)))
        # Worst trade data
        print(Colors.RED, "Worst trade: " + str(round(self.worst_trade.trade_profit, 2)) + " / " +
              str(round(self.worst_trade.percent_trade_profit)) + "%" + "  " +
              str(parse_timestamp(self.worst_trade.sell_timestamp)))
        # total exposure time
        print(Colors.BLUE, "Total exposure time in days: " + str(round(self.exposure_time, 2)) + " / " +
              str(round(self.percent_exposure_time)) + "%")
        # average exposure time per day
        print(Colors.BLUE,
              "Average exposure time per trade in days: " + str(round(self.average_exposure_time, 2)) + " / " +
              str(round(self.average_percent_exposure_time)) + "%")

    # Make Balance and Token price graphs
    def plot_wallet(self, size=100):
        # Total number of trades
        self.total_trades = self.wallet.position_book.last_position_index + 1
        # Just create a simple graph price if the strategy didn't traded
        if self.total_trades == 0:
            # main
            plt.plot(self.wallet.dataframe["timestamp"], self.wallet.dataframe["close"], zorder=1)

            # linear regression
            x, y = np.array(self.wallet.dataframe["timestamp"]), np.array(self.wallet.dataframe["close"])
            m, b = np.polyfit(x, y, 1)
            plt.plot(x, m * x + b)

            # labels
            plt.title("Price " + self.wallet.token_name + "/" + self.wallet.coin_name)
            plt.ylabel("price (" + self.wallet.coin_name + ")")
            plt.xlabel("Time (timestamps)")
            plt.show()
            return

        # Sell orders timestamps
        sell_timestamps = []
        # Sell timestamps with the first timestamp
        sell_timestamps_wallet = [self.start]
        # Balance at sell orders
        sell_balance = [self.wallet.ini_coin_balance]

        # Buy orders timestamps
        buy_timestamps = []
        # Price at sell orders
        sell_prices = []
        # Price at buy orders
        buy_prices = []

        # Append lists
        for trade in self.wallet.position_book.book:
            sell_timestamps.append(trade.sell_timestamp)
            sell_timestamps_wallet.append(trade.sell_timestamp)
            sell_balance.append(trade.balance_at_selling)
            buy_timestamps.append(trade.buy_timestamp)
            sell_prices.append(trade.sell_price)
            buy_prices.append(trade.buy_price)

        # figure 1, balance
        plt.figure(1)
        plt.plot(sell_timestamps_wallet, sell_balance)

        # linear regression
        x, y = np.array(sell_timestamps_wallet), np.array(sell_balance)
        m, b = np.polyfit(x, y, 1)
        plt.plot(x, m * x + b)

        # labels
        plt.title("Balance")
        plt.ylabel("balance (" + self.wallet.coin_name + ")")
        plt.xlabel("Time (timestamps)")

        # figure 2, price
        if self.wallet.dataframe is not None:
            plt.figure(2)
            # main
            plt.plot(self.wallet.dataframe["timestamp"], self.wallet.dataframe["close"], zorder=1)

            # scatter
            plt.scatter(buy_timestamps, buy_prices, color="green", marker="^", s=size, zorder=3)
            plt.scatter(sell_timestamps, sell_prices, color="red", marker="v", s=size, zorder=2)

            # linear regression
            x, y = np.array(self.wallet.dataframe["timestamp"]), np.array(self.wallet.dataframe["close"])
            m, b = np.polyfit(x, y, 1)
            plt.plot(x, m * x + b)
            # labels
            plt.title("Price " + self.wallet.token_name + "/" + self.wallet.coin_name)
            plt.ylabel("price (" + self.wallet.coin_name + ")")
            plt.xlabel("Time (timestamps)")

        plt.show()
