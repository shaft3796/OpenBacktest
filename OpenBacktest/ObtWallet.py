from statistics import mean
from OpenBacktest.ObtGraph import GraphManager
from OpenBacktest.ObtUtility import divide, Colors, remove_fees, parse_timestamp
from OpenBacktest.ObtPositions import PositionBook, LongPosition, OrderBook, Order


# ------------------------------------------------------------------------------------------------
# This class represent a symmetric wallet used to pass buy and sell orders of a symmetric strategy
# ------------------------------------------------------------------------------------------------
class SymmetricWallet:
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
        self.data_handler = SymmetricDataHandler(self)

    def buy(self, index):
        amount = self.coin_balance
        if amount == 0:
            return

        # Updating Position Book
        # opening a new Position
        position = LongPosition()
        position.open(self.dataframe["timestamp"][index], self.dataframe["close"][index], self.coin_balance, amount)
        self.position_book.add_position(position)

        # Buying
        self.token_balance += remove_fees(divide(amount, self.dataframe["close"][index]), self.taker, self)
        self.coin_balance = self.coin_balance - amount

    def sell(self, index):
        amount = self.token_balance
        if amount == 0:
            return

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

    def get_current_wallet_value(self, index):
        price = self.dataframe["close"][index]
        return self.coin_balance + self.token_balance * price


# ------------------------------------------------------------------------------------------------------
# This class represent an asymmetric wallet used to pass buy and sell orders of a an asymetric strategy
# ------------------------------------------------------------------------------------------------------
class AsymmetricWallet:
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

        # Represent all orders
        self.order_book = OrderBook()
        # Dataframe
        self.dataframe = dataframe

        # total fees
        self.total_fees = 0

        # data handler
        self.data_handler = AsymmetricDataHandler(self)

    def buy(self, index, amount=None, percent_amount=None):
        if amount is None:
            if percent_amount is None:
                amount = self.coin_balance
            else:
                amount = self.coin_balance * divide(percent_amount, 100)
        else:
            if amount > self.coin_balance:
                amount = self.coin_balance

        if amount == 0:
            return

        # Updating Order Book
        self.order_book.push_order(
            Order("buy", self.dataframe["timestamp"][index], self.dataframe["close"][index], self.coin_balance,
                  self.token_balance, amount, None))

        # Buying
        self.token_balance += remove_fees(divide(amount, self.dataframe["close"][index]), self.taker, self)
        self.coin_balance -= amount

    def sell(self, index, amount=None, percent_amount=None):
        if amount is None:
            if percent_amount is None:
                amount = self.token_balance
            else:
                amount = self.token_balance * divide(percent_amount, 100)
        else:
            if amount > self.token_balance:
                amount = self.token_balance

        if amount == 0:
            return

        # Selling
        old_coin_balance = self.coin_balance
        self.coin_balance += remove_fees(amount * self.dataframe["close"][index], self.taker, self)
        self.token_balance -= amount

        # Updating Order Book
        self.order_book.push_order(
            Order("sell", self.dataframe["timestamp"][index], self.dataframe["close"][index], self.coin_balance,
                  self.token_balance, None, amount))

    def get_current_wallet_value(self, index):
        price = self.dataframe["close"][index]
        return self.coin_balance + self.token_balance * price


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

        # Iteration in position book
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

        ath = self.wallet.ini_coin_balance
        ath_timestamp = self.wallet.dataframe["timestamp"][0]
        # Iteration in dataframe
        for i in range(len(self.wallet.dataframe["timestamp"])):
            balance = self.wallet.dataframe["balance"][i]
            if balance >= ath:
                ath = balance
                ath_timestamp = self.wallet.dataframe["timestamp"][i]
            else:
                drawdown = -(divide(100 * (ath - balance), ath))
                if drawdown < self.drawdown:
                    self.drawdown = drawdown
                    self.balance_at_drawdown = balance
                    self.drawdown_timestamp = self.wallet.dataframe["timestamp"][i]
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
    def plot_wallet(self, size=10, tradeline=True):
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
        self.total_trades = self.wallet.position_book.last_position_index + 1
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

        # Build sell and buy orders timestamps and prices
        for trade in self.wallet.position_book.book:
            sell_timestamps.append(trade.sell_timestamp)
            buy_timestamps.append(trade.buy_timestamp)
            sell_prices.append(trade.sell_price)
            buy_prices.append(trade.buy_price)

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

                manager1.draw_line([self.wallet.dataframe["timestamp"][0],
                                    self.wallet.dataframe["timestamp"][len(self.wallet.dataframe["timestamp"]) - 1]],
                                   [0, 0], line_width=13,
                                   line_color="black", hoverinfo="none")
                manager1.draw_line([self.wallet.dataframe["timestamp"][0],
                                    self.wallet.dataframe["timestamp"][len(self.wallet.dataframe["timestamp"]) - 1]],
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

                manager2.draw_line([self.wallet.dataframe["timestamp"][0],
                                    self.wallet.dataframe["timestamp"][len(self.wallet.dataframe["timestamp"]) - 1]],
                                   [0, 0], line_width=13,
                                   line_color="black", hoverinfo="none")
                manager2.draw_line([self.wallet.dataframe["timestamp"][0],
                                    self.wallet.dataframe["timestamp"][len(self.wallet.dataframe["timestamp"]) - 1]],
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
        manager2.draw_line(list(self.wallet.dataframe["timestamp"]), list(self.wallet.dataframe["balance"]),
                           line_color="darkblue", line_width=3, row=2)
        manager2.draw_line([self.last_ath_timestamp, self.drawdown_timestamp], [self.last_ath, self.balance_at_drawdown],
                           line_color="red", line_width=3, row=2, showlegend=True,
                           name="Worst drawDown ( on Wallet Graph )")

        manager1.show()
        manager2.show()


# -------------------------------------------------------------------------------
# This class is used to summarize backtest result of a, asymmetric strategy
# -------------------------------------------------------------------------------
class AsymmetricDataHandler:
    def __init__(self, wallet):
        self.wallet = wallet

        # Informative values, these values are initialized but will be calculated by make_data() function
        # coin profit
        self.profit = 0
        # coin profit in %
        self.percent_profit = 0
        # total number orders
        self.total_orders = 0
        # number of buy orders
        self.total_buy_orders = 0
        # number of sell orders
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

    # Make the required data to display wallet
    def make_data(self):
        # Total number of trades
        self.total_orders = len(self.wallet.order_book.book)
        # return if there were no trades
        if self.total_orders == 0:
            return

        # --- Total Profit ---
        self.profit = self.wallet.coin_balance - self.wallet.ini_coin_balance
        # Profit in percent depending of initial coin balance
        self.percent_profit = divide(100 * self.profit, self.wallet.ini_coin_balance)

        # --- Orders ---
        for order in self.wallet.order_book.book:

            # Count positive & negative trades and collect data to make average positive & negative trades profit
            if order.type == "buy":
                self.total_buy_orders += 1
            elif order.type == "sell":
                self.total_sell_orders += 1

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
        total_trades = self.wallet.order_book.last_position_index + 1
        # Cancel plotting if there are no trades
        if total_trades == 0:
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

        # Build sell and buy orders timestamps and prices
        for order in self.wallet.order_book.book:
            if order.type == "buy":
                buy_timestamps.append(order.timestamp)
                buy_prices.append(order.price)
            elif order.type == "sell":
                sell_timestamps.append(order.timestamp)
                sell_prices.append(order.price)

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
        manager2.draw_line(list(self.wallet.dataframe["timestamp"]), list(self.wallet.dataframe["balance"]),
                           line_color="darkblue", line_width=3, row=2)

        manager1.show()
        manager2.show()
