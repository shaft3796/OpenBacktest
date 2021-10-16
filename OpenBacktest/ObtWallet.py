from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from OpenBacktest.ObtUtility import divide, Colors, remove_fees, parse_timestamp
from datetime import datetime


class Wallet:
    def __init__(self, coin_name, token_name, coin_balance, token_balance, taker, maker, dataframe=None):
        # Initial coin balance ( will not be modified )
        self.ini_coin_balance = coin_balance
        # Initial token balance ( will not be modified )
        self.ini_token_balance = token_balance
        # Current coin balance ( should be modified )
        self.coin_balance = coin_balance
        # Current token balance
        self.token_balance = token_balance
        # Taker fees
        self.taker = divide(taker, 100.0)
        # Maker fees
        self.maker = divide(maker, 100.0)
        # Represent the current trade if there is an opened position
        self.last_trade = None
        # Represent all trades
        self.trades_list = []
        # Dataframe
        self.dataframe = dataframe

        # Informative values, these values are initialized but will be calculated by make_data() function
        self.coin_name = coin_name
        self.token_name = token_name
        self.profit = 0
        self.percent_profit = 0
        self.total_fees = 0
        self.total_trades = 0
        self.total_positives_trades = 0
        self.total_negatives_trades = 0
        self.positives_trades_ratio = 0
        self.negatives_trades_ratio = 0
        self.worst_trade = 0
        self.best_trade = 0
        self.average_positive_trades = 0
        self.average_negative_trades = 0
        self.average_profit_per_trades = 0

    def buy_all(self, price, dataframe=None, index=None):
        # Updating data
        if dataframe is not None and index is not None:
            self.last_trade = {"buy": {"timestamp": dataframe["timestamp"][index], "price": dataframe["close"][index],
                                       "balance": self.coin_balance}}

        # Buying
        self.token_balance = remove_fees(divide(self.coin_balance, price), self.maker, self)
        self.coin_balance = 0.0

    def sell_all(self, price, dataframe=None, index=None):
        # Selling
        self.coin_balance = remove_fees(self.token_balance * price, self.maker, self)
        self.token_balance = 0.0

        # Updating data
        if dataframe is not None and index is not None:
            self.last_trade["sell"] = {"timestamp": dataframe["timestamp"][index], "price": dataframe["close"][index],
                                       "balance": self.coin_balance}
            # closing trade
            self.trades_list.append(self.last_trade)

    # Make the required data to display wallet
    def make_data(self):
        # Total number of trades
        self.total_trades = len(self.trades_list)
        # return if there were no trades
        if self.total_trades == 0:
            return

        # --- Profit ---
        self.profit = (self.ini_coin_balance - self.coin_balance) * -1
        # Profit in percent depending of initial coin balance
        self.percent_profit = divide(100 * self.profit, self.ini_coin_balance)

        # --- Trades ---

        # Ini
        positive_trades_profit = []
        positive_trades_percent_profit = []
        negative_trades_profit = []
        negative_trades_percent_profit = []
        trades_profit = []
        trades_percent_profit = []

        for trade in self.trades_list:
            # Profit of the current trade
            trade_profit = (trade["buy"]["balance"] - trade["sell"]["balance"]) * -1
            # Profit of the current trade in percent
            percent_trade_profit = divide(100 * trade_profit, trade["buy"]["balance"])

            # Count positive & negative trades and collect data to make average positive & negative trades profit
            if trade_profit > 0:
                positive_trades_profit.append(trade_profit)
                positive_trades_percent_profit.append(percent_trade_profit)
                self.total_positives_trades += 1
            elif trade_profit < 0:
                negative_trades_profit.append(trade_profit)
                negative_trades_percent_profit.append(percent_trade_profit)
                self.total_negatives_trades += 1

            # Collect data to make average positive & negative trades profit
            trades_profit.append(trade_profit)
            trades_percent_profit.append(percent_trade_profit)

            # Initializing worst_trade & best_trade values with the first trade
            if self.worst_trade == 0 or self.best_trade == 0:
                self.worst_trade = {"timestamp": (trade["buy"]["timestamp"], trade["sell"]["timestamp"]),
                                    "profit": (trade_profit, percent_trade_profit)}
                self.best_trade = {"timestamp": (trade["buy"]["timestamp"], trade["sell"]["timestamp"]),
                                   "profit": (trade_profit, percent_trade_profit)}
            # Updating best_trade
            if percent_trade_profit > self.best_trade["profit"][1]:
                self.best_trade = {"timestamp": (trade["buy"]["timestamp"], trade["sell"]["timestamp"]),
                                   "profit": (trade_profit, percent_trade_profit)}
            # Updating worst_trade
            if percent_trade_profit < self.worst_trade["profit"][1]:
                self.worst_trade = {"timestamp": (trade["buy"]["timestamp"], trade["sell"]["timestamp"]),
                                    "profit": (trade_profit, percent_trade_profit)}

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

    # Summarize all trades & wallet evolutions, strategy stats
    def display_wallet(self):
        # Build all required data
        self.make_data()
        # If there were no trades
        if self.total_trades == 0:
            print(Colors.YELLOW, "This strategy didn't traded")
            return

        # Calculate / initialising some data
        end = self.dataframe['timestamp'][len(self.dataframe['timestamp']) - 1]
        start = self.dataframe['timestamp'][0]
        total_inday_trading_time = divide(int(end - start), 86400000)
        first_price = self.dataframe['close'][0]
        last_price = self.dataframe['close'][len(self.dataframe['close']) - 1]
        buy_and_hold_profit = divide(self.ini_coin_balance*last_price, first_price)
        buy_and_hold_percent_profit = divide(100*last_price, first_price)
        strategy_vs_buy_and_hold = self.profit - buy_and_hold_profit
        strategy_vs_buy_and_hold_percent = self.percent_profit - buy_and_hold_percent_profit
        average_profit_per_day = divide(self.profit, total_inday_trading_time)
        average_percent_profit_per_day = divide(self.percent_profit, total_inday_trading_time)

        # --- Intro ---

        print(Colors.PURPLE + "----------------------------------------------------")
        print("Data from", parse_timestamp(start), "to", parse_timestamp(end))
        print("Total trading time:", str(round(total_inday_trading_time, 2)), "day(s)")
        print("----------------------------------------------------")

        # --- Wallet data ---
        # title
        print(Colors.YELLOW + "[-Wallet-]")
        # Initial coin balance
        print(Colors.LIGHT_BLUE, "Initial", self.coin_name, round(float(self.ini_coin_balance), 3))
        # Final coin balance
        print(Colors.LIGHT_BLUE, "Final", self.coin_name, round(float(self.coin_balance), 3))
        # Initial token balance
        print(Colors.LIGHT_BLUE, "Initial", self.token_name, round(float(self.ini_token_balance), 3))
        # Final token balance
        print(Colors.LIGHT_BLUE, "Final", self.token_name, round(float(self.token_balance), 6))

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
        print(" Average profit per day: ", round(average_profit_per_day, 2), "/",
              str(round(average_percent_profit_per_day, 2)) + "%")

        # Fees
        print(Colors.LIGHT_RED, "Fees: ", round(float(self.total_fees), 3), self.coin_name, "/",
              str(round(divide(100 * float(self.total_fees), self.coin_balance), 2)) + "%")

        # Buy & hold profit
        if buy_and_hold_profit == 0:
            print(Colors.CYAN, "Buy & hold profit: ", round(float(buy_and_hold_profit), 2), "/",
                  str(round(float(buy_and_hold_percent_profit), )) + "%")
        elif buy_and_hold_profit < 0:
            print(Colors.RED, "Buy & hold profit: ", round(float(buy_and_hold_profit), 2), "/",
                  str(round(float(buy_and_hold_percent_profit), )) + "%")
        else:
            print(Colors.GREEN, "Buy & hold profit: ", round(float(buy_and_hold_profit), 2), "/",
                  str(round(float(buy_and_hold_percent_profit), )) + "%")

        # Strategy vs Buy & Hold
        if strategy_vs_buy_and_hold == 0:
            print(Colors.CYAN, "Strategy vs buy & hold: ", round(float(strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(strategy_vs_buy_and_hold_percent), )) + "%")
        elif strategy_vs_buy_and_hold < 0:
            print(Colors.RED, "Strategy vs buy & hold: ", round(float(strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(strategy_vs_buy_and_hold_percent), )) + "%")
        else:
            print(Colors.GREEN, "Strategy vs buy & hold: ", round(float(strategy_vs_buy_and_hold), 2), "/",
                  str(round(float(strategy_vs_buy_and_hold_percent), )) + "%")

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
        print(Colors.GREEN, "Best trade: +" + str(round(self.best_trade["profit"][0], 2)) + " / +" +
              str(round(self.best_trade["profit"][1])) + "%" + "  " + str(
            parse_timestamp(self.best_trade["timestamp"][0])))
        # Worst trade data
        print(Colors.RED, "Worst trade: " + str(round(self.worst_trade["profit"][0], 2)) + " / " +
              str(round(self.worst_trade["profit"][1])) + "%" + "  " + str(
            parse_timestamp(self.worst_trade["timestamp"][0])))

    # Make Balance and Token price graphs
    def plot_wallet(self, dataframe=None, size=100):
        # Total number of trades
        self.total_trades = len(self.trades_list)
        # Just create a simple graph price if the strategy didn't traded
        if self.total_trades == 0:
            if dataframe is not None:
                # main
                plt.plot(dataframe["timestamp"], dataframe["close"], zorder=1)

                # linear regression
                x, y = np.array(dataframe["timestamp"]), np.array(dataframe["close"])
                m, b = np.polyfit(x, y, 1)
                plt.plot(x, m * x + b)

                # labels
                plt.title("Price " + self.token_name + "/" + self.coin_name)
                plt.ylabel("price (" + self.coin_name + ")")
                plt.xlabel("Time (timestamps)")
            plt.show()
            return

        # Timestamps list
        timestamps = []
        # Prices list
        prices = []
        # Sell orders timestamps
        sell_timestamps = []
        # Buy orders timestamps
        buy_timestamps = []
        # Sell orders prices
        sell_prices = []
        # Buy orders prices
        buy_prices = []

        # Append lists
        for trade in self.trades_list:
            prices.append(trade["sell"]["balance"])
            timestamps.append(trade["sell"]["timestamp"])
            sell_timestamps.append(trade["sell"]["timestamp"])
            buy_timestamps.append(trade["buy"]["timestamp"])
            sell_prices.append(trade["sell"]["price"])
            buy_prices.append(trade["buy"]["price"])

        # figure 1, balance
        plt.figure(1)
        plt.plot(timestamps, prices)

        # linear regression
        x, y = np.array(timestamps), np.array(prices)
        m, b = np.polyfit(x, y, 1)
        plt.plot(x, m * x + b)

        # labels
        plt.title("Balance")
        plt.ylabel("balance (" + self.coin_name + ")")
        plt.xlabel("Time (timestamps)")

        # figure 2, price
        if dataframe is not None:
            plt.figure(2)
            # main
            plt.plot(dataframe["timestamp"], dataframe["close"], zorder=1)

            # scatter
            plt.scatter(buy_timestamps, buy_prices, color="green", marker="^", s=size, zorder=3)
            plt.scatter(sell_timestamps, sell_prices, color="red", marker="v", s=size, zorder=2)

            # linear regression
            x, y = np.array(dataframe["timestamp"]), np.array(dataframe["close"])
            m, b = np.polyfit(x, y, 1)
            plt.plot(x, m * x + b)

            # labels
            plt.title("Price " + self.token_name + "/" + self.coin_name)
            plt.ylabel("price (" + self.coin_name + ")")
            plt.xlabel("Time (timestamps)")
        plt.show()


"""
TODO:
add average position time
add total time in positions / in percent
"""
