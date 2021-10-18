from OpenBacktest.ObtUtility import divide, Colors


# -------------------------------------------------------------------------------
# This is a class representing a long position that is one buy point and one sell point
# -------------------------------------------------------------------------------

class LongPosition:
    def __init__(self):
        # Buy order
        self.buy_timestamp = None
        self.buy_price = None
        self.balance_at_buying = None
        self.buy_coin_amount = None

        # Sell order
        self.sell_timestamp = None
        self.sell_price = None
        self.balance_at_selling = None
        self.sell_coin_amount = None

        # Filled data
        self.trade_profit = None
        self.percent_trade_profit = None

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

    def fill(self):
        self.trade_profit = (self.balance_at_buying - self.balance_at_selling) * -1
        self.percent_trade_profit = divide(100 * self.trade_profit, self.balance_at_buying)


# -------------------------------------------------------------------------------
# This is a class representing a position book that contain a list of positions
# -------------------------------------------------------------------------------
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
