from statistics import mean
from OpenBacktest.ObtGraph import GraphManager
from OpenBacktest.ObtUtility import append_dataframe, initialise_dataframe, get_last_row, check_wallet_frame, divide, Colors, remove_fees, parse_timestamp


# ------------------------------------------------------------------------------------------------
# This class represent a wallet used to pass buy and sell orders of a symmetric strategy
# ------------------------------------------------------------------------------------------------
class Wallet:
    def __init__(self, coin_name, token_name, coin_balance, token_balance, taker, dataframe):
        # name of the coin
        self.coin_name = coin_name
        # symbol of the token
        self.token_name = token_name
        # Maker fees
        self.taker = divide(taker, 100.0)
        # Dataframe
        self.dataframe = dataframe
        # data handler
        self.data_handler = None
        # initial balances
        self.coin_balance = coin_balance
        self.token_balance = token_balance

        self.wallet_frame = initialise_dataframe(["coin_balance", "token_balance", "total_fees", "order_type",
                                                  "timestamp", "price", "size", "equivalence"])

        # First row
        self.wallet_frame = append_dataframe(self.wallet_frame, {"coin_balance": coin_balance,
                                                                 "token_balance": token_balance,
                                                                 "total_fees": 0.0,
                                                                 "order_type": "blank",
                                                                 "timestamp": "blank",
                                                                 "price": "blank",
                                                                 "size": "blank",
                                                                 "equivalence": "blank"})

    def buy(self, index, amount=None, percent_amount=None):
        last_row = get_last_row(self.wallet_frame)
        coin_balance = last_row["coin_balance"]
        total_fees = last_row["total_fees"]
        token_balance = last_row["token_balance"]

        if amount is None:
            if percent_amount is None:
                amount = coin_balance
            else:
                amount = coin_balance * divide(percent_amount, 100)
        else:
            if amount > coin_balance:
                amount = coin_balance

        if amount == 0:
            return

        fees = remove_fees(amount, self.taker)

        size = divide(100*amount, coin_balance)
        buying_amount = amount - fees

        new_balance = coin_balance - amount
        new_token_balance = token_balance + divide(buying_amount, self.dataframe["close"][index])
        # Updating wallet dataframe
        self.wallet_frame = append_dataframe(self.wallet_frame, {"coin_balance": new_balance,
                                                                 "token_balance": new_token_balance,
                                                                 "total_fees": total_fees + fees,
                                                                 "order_type": "BUY",
                                                                 "timestamp": self.dataframe["timestamp"][index],
                                                                 "price": self.dataframe["close"][index],
                                                                 "size": size,
                                                                 "equivalence": new_balance + new_token_balance *
                                                                                self.dataframe["close"][index]})

    def sell(self, index, amount=None, percent_amount=None):
        last_row = get_last_row(self.wallet_frame)
        coin_balance = last_row["coin_balance"]
        total_fees = last_row["total_fees"]
        token_balance = last_row["token_balance"]

        if amount is None:
            if percent_amount is None:
                amount = token_balance
            else:
                amount = token_balance * divide(percent_amount, 100)
        else:
            if amount > token_balance:
                amount = token_balance

        if amount == 0:
            return

        fees_in_coin = remove_fees(self.dataframe["close"][index] * amount, self.taker)
        fees = remove_fees(amount, self.taker)

        size = divide(100*amount, token_balance)
        selling_amount = amount - fees

        new_balance = coin_balance - amount
        new_token_balance = token_balance + divide(selling_amount, self.dataframe["close"][index])
        # Updating wallet dataframe
        self.wallet_frame = append_dataframe(self.wallet_frame,
                                             {"coin_balance": coin_balance + self.dataframe["close"][
                                                 index] * selling_amount,
                                              "token_balance": token_balance - amount,
                                              "total_fees": total_fees + fees_in_coin,
                                              "order_type": "SELL",
                                              "timestamp": self.dataframe["timestamp"][index],
                                              "price": self.dataframe["close"][index],
                                              "size": size,
                                              "equivalence": new_balance + new_token_balance *
                                                             self.dataframe["close"][index]})

    def get_data_handler(self):
        if self.data_handler is None:
            if check_wallet_frame(self.wallet_frame):
                self.data_handler = SymmetricDataHandler(self)
            else:
                self.data_handler = AsymmetricDataHandler(self)
            return self.data_handler
        return self.data_handler


# -------------------------------------------------------------------------------
# This class is used to summarize backtest result of a symmetric strategy
# -------------------------------------------------------------------------------
class SymmetricDataHandler:
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
        # drawback / drawdown
        self.drawdown = 0
        # drawback / drawdown timestamp
        self.drawdown_timestamp = 0
        # drawback / drawdown balance
        self.balance_at_drawdown = 0
        # last ATH
        self.last_ath = 0
        # last ATH timestamp
        self.last_ath_timestamp = 0
        # used to plot graph, list of all trades percent profit
        self.trades_percent_profit = []

    # Make the required data to display wallet
    def make_data(self):
        # Total number of trades
        self.total_trades = round(divide(len(self.wallet.wallet_frame["timestamp"]) - 1, 2))
        # return if there were no trades
        if self.total_trades == 0:
            return

        # --- Total Profit ---
        self.profit = self.wallet.wallet_frame.iloc[-1]["coin_balance"] - self.wallet.coin_balance

        # Profit in percent depending of initial coin balance
        self.percent_profit = divide(100 * self.profit, self.wallet.coin_balance)

        # --- Splitting ---
        buy_orders = \
            self.wallet.wallet_frame.loc[self.wallet.wallet_frame["order_type"] == "BUY"].reset_index(drop=True)
        sell_orders = \
            self.wallet.wallet_frame.loc[self.wallet.wallet_frame["order_type"] == "SELL"].reset_index(drop=True)

        # --- Trades ---

        # Ini
        positive_trades_profit = []
        positive_trades_percent_profit = []
        negative_trades_profit = []
        negative_trades_percent_profit = []
        trades_profit = []
        exposures = []

        for index, buy_row in buy_orders.iterrows():
            # Get the sell order
            sell_row = sell_orders.iloc[index]

            # Calculate the profit
            trade_profit = sell_row["equivalence"] - buy_row["equivalence"]
            trades_profit.append(trade_profit)

            # Calculate the profit in percent
            trade_percent_profit = float(divide(100 * trade_profit, buy_row["equivalence"]))
            self.trades_percent_profit.append(trade_percent_profit)

            # Calculate the exposure time
            exposure = sell_row["timestamp"] - buy_row["timestamp"]
            self.exposure_time += divide(exposure, 84000000)
            exposures.append(exposure)

            # Check if the trade was positive or negative
            if trade_profit > 0:
                self.total_positives_trades += 1
                positive_trades_profit.append(trade_profit)
                positive_trades_percent_profit.append(trade_percent_profit)
            else:
                self.total_negatives_trades += 1
                negative_trades_profit.append(trade_profit)
                negative_trades_percent_profit.append(trade_percent_profit)

            # Initializing worst_trade & best_trade values with the first trade
            if self.worst_trade is None or self.best_trade is None:
                self.worst_trade = trade_profit, trade_percent_profit, buy_row["timestamp"], sell_row["timestamp"]
                self.best_trade = trade_profit, trade_percent_profit, buy_row["timestamp"], sell_row["timestamp"]
            # Updating best_trade
            elif trade_percent_profit > self.best_trade[1]:
                self.best_trade = trade_profit, trade_percent_profit, buy_row["timestamp"], sell_row["timestamp"]
            # Updating worst_trade
            elif trade_percent_profit < self.worst_trade[1]:
                self.worst_trade = trade_profit, trade_percent_profit, buy_row["timestamp"], sell_row["timestamp"]

        ath = self.wallet.wallet_frame["equivalence"][1]
        ath_timestamp = self.wallet.dataframe["timestamp"][1]

        # Iteration in dataframe
        for index, row in self.wallet.wallet_frame.iterrows():
            if row["timestamp"] != "blank":
                balance = row["equivalence"]
                if balance >= ath:
                    ath = balance
                    ath_timestamp = row["timestamp"]
                else:
                    drawdown = -(divide(100 * (ath - balance), ath))
                    if drawdown < self.drawdown:
                        self.drawdown = drawdown
                        self.balance_at_drawdown = balance
                        self.drawdown_timestamp = row["timestamp"]
                        self.last_ath = ath
                        self.last_ath_timestamp = ath_timestamp

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
            self.trades_percent_profit.append(0)
        self.average_profit_per_trades = (
            round(mean(trades_profit), 2), round(mean(self.trades_percent_profit), 2))

        # Last timestamp of the period
        self.end = self.wallet.wallet_frame.iloc[-1]["timestamp"]
        # First timestamp of the period
        self.start = self.wallet.dataframe.iloc[0]["timestamp"]
        # Total days from first timestamp to the last one
        self.total_inday_trading_time = divide(int(self.end - self.start), 86400000)
        # First close price of the dataframe
        self.first_price = self.wallet.dataframe.iloc[0]["close"]
        # Last close price of the dataframe
        self.last_price = self.wallet.dataframe.iloc[-1]["close"]
        # Profit with buy & hold
        self.buy_and_hold_profit = divide(self.wallet.wallet_frame.iloc[0]["coin_balance"] * self.last_price,
                                          self.first_price)
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
        self.average_exposure_time = divide(mean(exposures), 86400000)
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
        print("Data from", parse_timestamp(int(self.start)), "to", parse_timestamp(int(self.end)))
        print("Total trading time:", str(round(self.total_inday_trading_time, 2)), "day(s)")
        print("----------------------------------------------------")

        # --- Wallet data ---
        # title
        print(Colors.YELLOW + "[-Wallet-]")
        # Initial coin balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.coin_name,
              round(float(self.wallet.wallet_frame.iloc[0]["coin_balance"]), 3))
        # Final coin balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.coin_name,
              round(float(self.wallet.wallet_frame.iloc[-1]["coin_balance"]), 3))
        # Initial token balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.token_name,
              round(float(self.wallet.wallet_frame.iloc[0]["token_balance"]), 6))
        # Final token balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.token_name,
              round(float(self.wallet.wallet_frame.iloc[-1]["token_balance"]), 6))

        # Profit
        if self.profit == 0:
            print(Colors.CYAN, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), 2)) + "%")
        elif self.profit < 0:
            print(Colors.RED, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), 2)) + "%")
        else:
            print(Colors.GREEN, "Strategy profit: ", round(float(self.profit), 2), "/",
                  str(round(float(self.percent_profit), 2)) + "%")

        # Average profit per trades
        print(" Average profit per trades: ", self.average_profit_per_trades[0], "/",
              str(self.average_profit_per_trades[1]) + "%")

        # Average profit per day
        print(" Average profit per day: ", round(self.average_profit_per_day, 2), "/",
              str(round(self.average_percent_profit_per_day, 2)) + "%")

        # Fees
        print(Colors.LIGHT_RED, "Fees: ", round(float(self.wallet.wallet_frame.iloc[-1]["total_fees"]), 3),
              self.wallet.coin_name, "/", str(round(divide(100 * float(self.wallet.wallet_frame.iloc[-1]["total_fees"]),
                                                           self.wallet.wallet_frame.iloc[-1]["coin_balance"]),
                                                    2)) + "%")

        # Drawdown
        print(Colors.LIGHT_RED, "Worst drawDown/drawBack: ", str(round(float(self.drawdown), 2)) + "%")

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
              str(round(self.positives_trades_ratio, 1)) + "%")
        # Total number of negative trades
        print(Colors.RED, "Total negative trades:", self.total_negatives_trades, "/",
              str(round(self.negatives_trades_ratio, 1)) + "%")
        # Average positive trades
        print(Colors.GREEN, "Average positive trades profit: " + "+" + str(self.average_positive_trades[0]), "/",
              "+" + str(self.average_positive_trades[1]) + "%")
        # Average positive trades
        print(Colors.RED, "Average negative trades profit: " + str(self.average_negative_trades[0]), "/",
              str(self.average_negative_trades[1]) + "%")
        # Best trade data
        print(Colors.GREEN, "Best trade: +" + str(round(self.best_trade[0], 2)) + " / +" +
              str(round(self.best_trade[1], 2)) + "%" + "  from: " +
              str(parse_timestamp(self.best_trade[2])) + " to " + str(parse_timestamp(self.best_trade[3])))
        # Worst trade data
        print(Colors.RED, "Worst trade: " + str(round(self.worst_trade[0], 2)) + " / " +
              str(round(self.worst_trade[1], 2)) + "%" + "  from: " +
              str(parse_timestamp(self.worst_trade[2])) + " to " + str(parse_timestamp(self.worst_trade[3])))
        # total exposure time
        print(Colors.BLUE, "Total exposure time in days: " + str(round(self.exposure_time, 2)) + " / " +
              str(round(self.percent_exposure_time, 2)) + "%")
        # average exposure time per day
        print(Colors.BLUE,
              "Average exposure time per trade in days: " + str(round(self.average_exposure_time, 2)) + " / " +
              str(round(self.average_percent_exposure_time, 2)) + "%")

    # Make Balance and Token price graphs
    def plot_wallet(self, size=10, tradeline=True):
        manager1 = GraphManager()
        manager1.set_title(self.wallet.token_name + "/" + self.wallet.coin_name)
        manager1.set_sub_title("Time (ms)", target="x", sub=1)
        manager1.set_sub_title("Price (" + self.wallet.coin_name + ")", target="y", sub=1)

        manager2 = GraphManager(3, 1, titles=["Price", "Wallet", "Trades profit"])
        manager2.set_title(self.wallet.token_name + "/" + self.wallet.coin_name)
        manager2.set_sub_title("Time (ms)", target="x", sub=2)
        manager2.set_sub_title("Time (ms)", target="x", sub=1)
        manager2.set_sub_title("Time (ms)", target="x", sub=3)
        manager2.set_sub_title("Price (" + self.wallet.coin_name + ")", target="y", sub=1)
        manager2.set_sub_title("Balance (" + self.wallet.coin_name + ")", target="y", sub=2)
        manager2.set_sub_title("Trade profit (%)", target="y", sub=3)

        # Total number of trades
        self.total_trades = round(divide(len(self.wallet.wallet_frame["timestamp"]) - 1, 2))
        # Cancel plotting if there are no trades
        if self.total_trades == 0:
            print(Colors.YELLOW, "No trades found, plotting canceled")
            return

        # Sell orders timestamps
        sell_timestamps = []
        # Buy orders timestamps
        buy_timestamps = []
        # Price at sell orders
        sell_prices = []
        # Price at buy orders
        buy_prices = []

        # --- Splitting ---
        buy_orders = \
            self.wallet.wallet_frame.loc[self.wallet.wallet_frame["order_type"] == "BUY"].reset_index(drop=True)
        sell_orders = \
            self.wallet.wallet_frame.loc[self.wallet.wallet_frame["order_type"] == "SELL"].reset_index(drop=True)

        # Build sell and buy orders timestamps and prices
        for index, row in buy_orders.iterrows():
            buy_timestamps.append(row["timestamp"])
            buy_prices.append(row["price"])

        for index, row in sell_orders.iterrows():
            sell_timestamps.append(row["timestamp"])
            sell_prices.append(row["price"])

        # Graph 1 Sub 1 - Price
        if self.wallet.dataframe is not None:
            if not tradeline:
                manager1 = GraphManager()

                manager1.plot_price(dataframe=self.wallet.dataframe)
                manager1.draw_marker(buy_timestamps, buy_prices, marker_color="black", marker_symbol="triangle-up",
                                     marker_size=size + 3)
                manager1.draw_marker(sell_timestamps, sell_prices, marker_color="black", marker_symbol="triangle-down",
                                     marker_size=size + 3)
                manager1.draw_marker(buy_timestamps, buy_prices, marker_color="green", marker_symbol="triangle-up",
                                     marker_size=size)
                manager1.draw_marker(sell_timestamps, sell_prices, marker_color="red", marker_symbol="triangle-down",
                                     marker_size=size)
            else:
                manager1.plot_price(dataframe=self.wallet.dataframe)

                manager1.draw_line([self.wallet.dataframe.iloc[0]["timestamp"],
                                    self.wallet.dataframe.iloc[-1]["timestamp"]],
                                   [0, 0], line_width=13,
                                   line_color="black", hoverinfo="none")
                manager1.draw_line([self.wallet.dataframe.iloc[0]["timestamp"],
                                    self.wallet.dataframe.iloc[-1]["timestamp"]],
                                   [0, 0], line_width=10,
                                   line_color="white", hoverinfo="none")
                for i in range(len(buy_timestamps)):
                    manager1.draw_trade_line(buy_timestamps[i], buy_prices[i], sell_timestamps[i], sell_prices[i],
                                             marker_size=13, line_width=4, marker_color="black", line_color="black")
                    manager1.draw_trade_line(buy_timestamps[i], buy_prices[i], sell_timestamps[i], sell_prices[i])

                    if buy_prices[i] >= sell_prices[i]:
                        manager1.draw_line([buy_timestamps[i], sell_timestamps[i]], [0, 0], line_width=10,
                                           line_color="red", hoverinfo="none")
                    else:
                        manager1.draw_line([buy_timestamps[i], sell_timestamps[i]], [0, 0], line_width=10,
                                           line_color="green", hoverinfo="none")
        # Graph 2 Sub 1 - Price
        if self.wallet.dataframe is not None:
            if not tradeline:
                manager2 = GraphManager()

                manager2.plot_price(dataframe=self.wallet.dataframe)
                manager2.draw_marker(buy_timestamps, buy_prices, marker_color="black", marker_symbol="triangle-up",
                                     marker_size=size + 3)
                manager2.draw_marker(sell_timestamps, sell_prices, marker_color="black", marker_symbol="triangle-down",
                                     marker_size=size + 3)
                manager2.draw_marker(buy_timestamps, buy_prices, marker_color="green", marker_symbol="triangle-up",
                                     marker_size=size)
                manager2.draw_marker(sell_timestamps, sell_prices, marker_color="red", marker_symbol="triangle-down",
                                     marker_size=size)
            else:
                manager2.plot_price(dataframe=self.wallet.dataframe)

                manager2.draw_line([self.wallet.dataframe.iloc[0]["timestamp"],
                                    self.wallet.dataframe.iloc[-1]["timestamp"]],
                                   [0, 0], line_width=13,
                                   line_color="black", hoverinfo="none")
                manager2.draw_line([self.wallet.dataframe.iloc[0]["timestamp"],
                                    self.wallet.dataframe.iloc[-1]["timestamp"]],
                                   [0, 0], line_width=10,
                                   line_color="white", hoverinfo="none")
                for i in range(len(buy_timestamps)):
                    manager2.draw_trade_line(buy_timestamps[i], buy_prices[i], sell_timestamps[i], sell_prices[i],
                                             marker_size=13, line_width=4, marker_color="black", line_color="black")
                    manager2.draw_trade_line(buy_timestamps[i], buy_prices[i], sell_timestamps[i], sell_prices[i])

                    if buy_prices[i] >= sell_prices[i]:
                        manager2.draw_line([buy_timestamps[i], sell_timestamps[i]], [0, 0], line_width=10,
                                           line_color="red", hoverinfo="none")
                    else:
                        manager2.draw_line([buy_timestamps[i], sell_timestamps[i]], [0, 0], line_width=10,
                                           line_color="green", hoverinfo="none")
        # Graph 2 Sub 2 - Wallet
        df = self.wallet.wallet_frame.loc(["timestamp"] != "blank")
        manager2.draw_line(list(df["timestamp"]), list(df["equivalence"]),
                           line_color="darkblue", line_width=3, row=2)
        manager2.draw_line([self.last_ath_timestamp, self.drawdown_timestamp],
                           [self.last_ath, self.balance_at_drawdown],
                           line_color="red", line_width=3, row=2)

        # Graph 2 Sub 3 - Trades profit
        manager2.draw_line(list(sell_timestamps), list(self.trades_percent_profit),
                           line_color="darkblue", line_width=3, row=3)
        manager2.draw_line([sell_timestamps[0], sell_timestamps[len(sell_timestamps) - 1]],
                           [0, 0], line_color="gray", line_width=3, row=3)

        manager1.show()
        manager2.show()


# -------------------------------------------------------------------------------
# This class is used to summarize backtest result of a symmetric strategy
# -------------------------------------------------------------------------------
class AsymmetricDataHandler:
    def __init__(self, wallet):
        self.wallet = wallet

        # Informative values, these values are initialized but will be calculated by make_data() function
        # coin profit
        self.profit = 0
        # coin profit in %
        self.percent_profit = 0
        # number of total trades
        self.total_orders = 0
        # number of total positive trades
        self.total_buy_orders = 0
        # number of total negative trades
        self.total_sell_orders = 0
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
        # drawback / drawdown
        self.drawdown = 0
        # drawback / drawdown timestamp
        self.drawdown_timestamp = 0
        # drawback / drawdown balance
        self.balance_at_drawdown = 0
        # last ATH
        self.last_ath = 0
        # last ATH timestamp
        self.last_ath_timestamp = 0

    # Make the required data to display wallet
    def make_data(self):
        # Total number of trades
        self.total_orders = round(len(self.wallet.wallet_frame["timestamp"]) - 1)
        # return if there were no trades
        if self.total_orders == 0:
            return

        # --- Total Profit ---
        self.profit = self.wallet.wallet_frame.iloc[-1]["coin_balance"] - self.wallet.coin_balance

        # Profit in percent depending of initial coin balance
        self.percent_profit = divide(100 * self.profit, self.wallet.coin_balance)

        # --- Splitting ---
        orders = \
            self.wallet.wallet_frame.loc[self.wallet.wallet_frame["order_type"] != "blank"].reset_index(drop=True)

        # --- Orders ---
        for index, row in orders.iterrows():
            # Get the sell order
            if row["order_type"] == "BUY":
                self.total_buy_orders += 1
            elif row["order_type"] == "SELL":
                self.total_sell_orders += 1

        ath = self.wallet.wallet_frame["equivalence"][1]
        ath_timestamp = self.wallet.dataframe["timestamp"][1]

        # Iteration in dataframe
        for index, row in self.wallet.wallet_frame.iterrows():
            if row["timestamp"] != "blank":
                balance = row["equivalence"]
                if balance >= ath:
                    ath = balance
                    ath_timestamp = row["timestamp"]
                else:
                    drawdown = -(divide(100 * (ath - balance), ath))
                    if drawdown < self.drawdown:
                        self.drawdown = drawdown
                        self.balance_at_drawdown = balance
                        self.drawdown_timestamp = row["timestamp"]
                        self.last_ath = ath
                        self.last_ath_timestamp = ath_timestamp

        # Last timestamp of the period
        self.end = self.wallet.wallet_frame.iloc[-1]["timestamp"]
        # First timestamp of the period
        self.start = self.wallet.dataframe.iloc[0]["timestamp"]
        # Total days from first timestamp to the last one
        self.total_inday_trading_time = divide(int(self.end - self.start), 86400000)
        # First close price of the dataframe
        self.first_price = self.wallet.dataframe.iloc[0]["close"]
        # Last close price of the dataframe
        self.last_price = self.wallet.dataframe.iloc[-1]["close"]
        # Profit with buy & hold
        self.buy_and_hold_profit = divide(self.wallet.wallet_frame.iloc[0]["coin_balance"] * self.last_price,
                                          self.first_price)
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

    # Summarize all trades & wallet evolution, strategy stats
    def display_wallet(self):
        # Build all required data
        self.make_data()
        # If there were no trades
        if self.total_orders == 0:
            print(Colors.YELLOW, "This strategy didn't traded")
            return

        # --- Intro ---

        print(Colors.PURPLE + "----------------------------------------------------")
        print("Data from", parse_timestamp(int(self.start)), "to", parse_timestamp(int(self.end)))
        print("Total trading time:", str(round(self.total_inday_trading_time, 2)), "day(s)")
        print("----------------------------------------------------")

        # --- Wallet data ---
        # title
        print(Colors.YELLOW + "[-Wallet-]")
        # Initial coin balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.coin_name, round(float(self.wallet.coin_balance), 3))
        # Final coin balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.coin_name,
              round(float(self.wallet.wallet_frame.iloc[-1]["coin_balance"]), 3))
        # Initial token balance
        print(Colors.LIGHT_BLUE, "Initial", self.wallet.token_name, round(float(self.wallet.token_balance), 3))
        # Final token balance
        print(Colors.LIGHT_BLUE, "Final", self.wallet.token_name,
              round(float(self.wallet.wallet_frame.iloc[-1]["token_balance"]), 3))

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

        # Average profit per day
        print(" Average profit per day: ", round(self.average_profit_per_day, 2), "/",
              str(round(self.average_percent_profit_per_day, 2)) + "%")

        # Fees
        print(Colors.LIGHT_RED, "Fees: ", round(float(self.wallet.wallet_frame.iloc[-1]["total_fees"]), 3),
              self.wallet.coin_name, "/", str(round(divide(100 * float(self.wallet.wallet_frame.iloc[-1]["total_fees"]),
                                                           self.wallet.wallet_frame.iloc[-1]["coin_balance"]),
                                                    2)) + "%")

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

        # --- Orders data ---
        print(Colors.YELLOW + "[-Orders-]")
        # Total number of trades
        print(Colors.BLUE, "Total orders:", self.total_orders)
        # Total number of positive trades
        print(Colors.GREEN, "Total buy orders:", self.total_buy_orders)
        # Total number of negative trades
        print(Colors.RED, "Total sell orders:", self.total_sell_orders)

    # Make Balance and Token price graphs
    def plot_wallet(self, size=10):
        manager1 = GraphManager()
        manager1.set_title(self.wallet.token_name + "/" + self.wallet.coin_name)
        manager1.set_sub_title("Time (ms)", target="x", sub=1)
        manager1.set_sub_title("Price (" + self.wallet.coin_name + ")", target="y", sub=1)

        manager2 = GraphManager(2, 1, height=[0.5, 1], titles=["Price", "Wallet"])
        manager2.set_title(self.wallet.token_name + "/" + self.wallet.coin_name)
        manager2.set_sub_title("Time (ms)", target="x", sub=2)
        manager2.set_sub_title("Time (ms)", target="x", sub=1)
        manager2.set_sub_title("Price (" + self.wallet.coin_name + ")", target="y", sub=1)
        manager2.set_sub_title("Balance (" + self.wallet.coin_name + ")", target="y", sub=2)

        # Total number of trades
        total_orders = len(self.wallet.wallet_frame["timestamp"])-1
        # Cancel plotting if there are no trades
        if total_orders == 0:
            print(Colors.YELLOW, "No trades found, plotting canceled")
            return

        # Sell orders timestamps
        sell_timestamps = []
        # Buy orders timestamps
        buy_timestamps = []
        # Price at sell orders
        sell_prices = []
        # Price at buy orders
        buy_prices = []
        # timestamps
        timestamps = []
        # equivalence
        equivalence = []

        # Build sell and buy orders timestamps and prices
        orders = self.wallet.wallet_frame.loc[self.wallet.wallet_frame["timestamp"] != "blank"]
        # --- Orders ---
        for index, row in orders.iterrows():
            # Get the sell order
            if row["order_type"] == "BUY":
                buy_timestamps.append(row["timestamp"])
                timestamps.append(row["timestamp"])
                buy_prices.append(row["price"])
                equivalence.append(row["equivalence"])
            elif row["order_type"] == "SELL":
                sell_timestamps.append(row["timestamp"])
                timestamps.append(row["timestamp"])
                sell_prices.append(row["price"])
                equivalence.append(row["equivalence"])

        # Graph 1 Sub 1 - Price
        manager1.plot_price(dataframe=self.wallet.dataframe)
        manager1.draw_marker(buy_timestamps, buy_prices, marker_color="black", marker_symbol="triangle-up",
                             marker_size=size + 3)
        manager1.draw_marker(sell_timestamps, sell_prices, marker_color="black",
                             marker_symbol="triangle-down",
                             marker_size=size + 3)
        manager1.draw_marker(buy_timestamps, buy_prices, marker_color="green", marker_symbol="triangle-up",
                             marker_size=size)
        manager1.draw_marker(sell_timestamps, sell_prices, marker_color="red",
                             marker_symbol="triangle-down",
                             marker_size=size)

        # Graph 2 Sub 1 - Price
        manager2.plot_price(dataframe=self.wallet.dataframe)
        manager2.draw_marker(buy_timestamps, buy_prices, marker_color="black", marker_symbol="triangle-up",
                             marker_size=size + 3)
        manager2.draw_marker(sell_timestamps, sell_prices, marker_color="black",
                             marker_symbol="triangle-down",
                             marker_size=size + 3)
        manager2.draw_marker(buy_timestamps, buy_prices, marker_color="green", marker_symbol="triangle-up",
                             marker_size=size)
        manager2.draw_marker(sell_timestamps, sell_prices, marker_color="red",
                             marker_symbol="triangle-down",
                             marker_size=size)

        # Graph 2 Sub 2 - Wallet
        manager2.draw_line(timestamps, equivalence,
                           line_color="darkblue", line_width=3, row=2)

        manager1.show()
        manager2.show()
