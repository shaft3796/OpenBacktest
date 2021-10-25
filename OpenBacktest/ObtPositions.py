from OpenBacktest.ObtUtility import divide, Colors


# ---------------------------------------------------------------------------------------------------------------
# This is a class representing a long position that is one buy point and one sell point used for symetric engine
# ---------------------------------------------------------------------------------------------------------------
class LongPosition:
    def __init__(self):
        # Buy order
        self.buy_timestamp = 0
        self.buy_price = 0
        self.balance_at_buying = 0
        self.buy_coin_amount = 0

        # Sell order
        self.sell_timestamp = 0
        self.sell_price = 0
        self.balance_at_selling = 0
        self.sell_coin_amount = 0

        # Filled data
        self.trade_profit = 0
        self.percent_trade_profit = 0
        self.position_time = 0

        self.closed = False

    def open(self, timestamp, price, balance, amount):
        self.buy_timestamp = timestamp
        self.buy_price = price
        self.balance_at_buying = balance
        self.buy_coin_amount = amount

    def close(self, timestamp, price, balance, amount):
        self.sell_timestamp = timestamp
        self.sell_price = price
        self.balance_at_selling = balance
        self.sell_coin_amount = amount

        self.fill()
        self.closed = True

    def fill(self):
        self.trade_profit = (self.balance_at_buying - self.balance_at_selling) * -1
        self.percent_trade_profit = divide(100 * self.trade_profit, self.balance_at_buying)
        self.position_time = divide(float(self.sell_timestamp) - float(self.buy_timestamp), 86400000)


# -------------------------------------------------------------------------------------------------------
# This is a class representing a position book that contain a list of positions used for symetric engine
# -------------------------------------------------------------------------------------------------------
class PositionBook:
    # Ini
    def __init__(self):
        self.book = []
        self.first_position_index = 0
        self.first_position = None
        self.last_position_index = 0
        self.last_position = None

        self.closed = False

    # Add a position to the book
    def add_position(self, position):
        if self.closed:
            print(Colors.LIGHT_RED + "Error, you tried to add a position to a closed book !")
            return

        self.book.append(position)

        if self.first_position is None:
            self.first_position = position

        if self.last_position is None:
            self.last_position = position
        else:
            self.last_position = position
            self.last_position_index += 1

    # Close the book
    def close(self):
        self.closed = True


# ---------------------------------------------------------------------------------------------------------------
# This is a class representing an order that is one buy point or one sell point, it's used for asymetric engine
# ---------------------------------------------------------------------------------------------------------------
class Order:
    def __init__(self, order_type, timestamp, price, coin_balance, token_balance, amount_of_coin, amount_of_token):

        # Order
        self.type = order_type
        self.timestamp = timestamp
        self.price = price
        self.coin_balance_at_order = coin_balance
        self.token_balance_at_order = token_balance
        self.amount_of_coin = amount_of_coin
        self.amount_of_token = amount_of_token


# -------------------------------------------------------------------------------------------------------
# This is a class representing an order book that contain a list of orders, it's used for asymetric engine
# -------------------------------------------------------------------------------------------------------
class OrderBook:
    # Ini
    def __init__(self):
        self.book = []
        self.first_position_index = 0
        self.first_position = None
        self.last_position_index = 0
        self.last_position = None

        self.closed = False

    # Add a position to the book
    def push_order(self, order):
        if self.closed:
            print(Colors.LIGHT_RED + "Error, you tried to add a position to a closed book !")
            return

        self.book.append(order)

    # Close the book
    def close(self):
        self.closed = True


# -------------------------------------------------------------------------------
# This class is used by the engine to set stop loss & tp
# -------------------------------------------------------------------------------
class Stop:
    def __init__(self, wallet, stop_type, target_price, amount=None, percent_amount=None):
        # amount
        if amount is None:
            if percent_amount is None:
                amount = wallet.coin_balance
            else:
                amount = wallet.coin_balance * divide(percent_amount, 100)
        else:
            if amount > wallet.coin_balance:
                amount = wallet.coin_balance
        self.amount = amount

        self.wallet = wallet

        if not stop_type == "up" or not stop_type == "down":
            print(Colors.RED, "Error, wrong usage of the class Stop, direction (dir) have only to be 'up' or 'down'")
            exit()
        self.stop_type = stop_type

        self.target_price = target_price

    def update(self, index):
        if self.stop_type == "up" and self.wallet.dataframe["close"][index] > self.target_price:
            self.wallet.sell(index, amount=self.amount)
        elif self.stop_type == "down" and self.wallet.dataframe["close"][index] < self.target_price:
            self.wallet.sell(index, amount=self.amount)
