# ------------------------------------------------------------------
# First of all, let's see all our imports
# ------------------------------------------------------------------

# The library Technical Analyse is already included when installing open backtest
# it allow to add a lot of indicators very useful for trading strategy
from ta import trend, momentum

# Let's import here 3 classes of Open Backtest we will later see how to use it
from OpenBacktest.ObtEngine import Engine, Container, Pair

# Python Binance is also included with Open Backtest it allow us to get the market data
from binance.client import Client

# ------------------------------------------------------------------
# The let's initialise our classes
# ------------------------------------------------------------------

# First of all we are here creating our container, it will contain all of our market pairs
container = Container()

# This is the tricky part ! We will here add to the container pairs we want to use by 2 functions,
# container.add_main_pair() and container.add_pair(). These 2 functions will have the same parameter ! The main pair
# will be the pair with the timeframe used to run your backtest /!\ it's required. There is also an other function
# named container.add_pair(), it will be used to add some other pairs that are not required. Note that it's useless
# for this engine to add pairs of others symbols, I mean if your main pair is for example Ethereum Usdt it's useless
# to add Bitcoin Usdt but it's technically possible. The real interest is to add the same pair but with a different
# timeframe ! Follow the structure below to add your pairs. The parameter of both functions is a Pair class with 5
# parameters, the parameters are quite self-explanatory but just to clarify, name is just a recognizable name for you
# that will be used later to get the data of a specific pair, the path is the location of files that already exist or
# the location of futures files that will be saved, this parameter is optional.

# We register here our main pair ! The data will be get for the pair Ethereum - Usdt from the 01 january 2021 to now
# with candles of 1 hour
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path="data/"))
# We register here a second pair with a largest timeframe ! The data will be get for the pair Ethereum - Usdt from
# the 01 january 2021 to now with candles of 1 day, note that the name is not the same than our first pair !
container.add_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1DAY, name="ETHUSDT1d",
         path="data/"))

# Let's now initialise our engine with our container
engine = Engine(container)

# This line is not required ! it's used to save our data as csv files to be able to just load it for the next backtest
container.save_all(default_path="data/")

# We are here enriching our dataframes with technical indicators using TA lib more information here
# https://technical-analysis-library-in-python.readthedocs.io/en/latest/

# Let's add to our main dataframe 2 EMA
engine.main_dataframe()["EMA3"] = trend.ema_indicator(engine.main_dataframe()['close'], 3)
engine.main_dataframe()["EMA100"] = trend.ema_indicator(engine.main_dataframe()['close'], 100)

# Let's add to our second dataframe 2 EMA, to get our second dataframe we will now use our names that we
# configured before !
engine.get_sub_dataframe("ETHUSDT1d")["EMA3"] = trend.ema_indicator(engine.get_sub_dataframe("ETHUSDT1d")["close"], 3)
engine.get_sub_dataframe("ETHUSDT1d")["EMA100"] = trend.ema_indicator(engine.get_sub_dataframe("ETHUSDT1d")["close"],
                                                                      100)


# We will now set a buy condition that will return True when it want to buy and same for a sell condition. The engine
# will call this function with the main dataframe and the current index
def buy_condition(dataframe, index):
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        return True

    # For these simple buy & sell conditions we will don't use our second dataframe but if you want to get data of it
    # it's simple !
    # The Pair class
    second_pair = engine.container.get_pair("ETHUSDT1d")
    # The dataframe
    second_dataframe = second_pair.dataframe
    # And the index you have to use to get your data corresponding to the current index of the main dataframe
    second_index = second_pair.get_index(dataframe["timestamp"][index])
    # So we can now access the ema for your timeframe of 1d like this :
    current_value_of_ema = second_dataframe["EMA3"][second_index]

    # You can also place take profit and stop loss !
    engine.set_take_profit(index, percent_target=50)
    engine.set_stop_loss(index, percent_target=-50)
    # Our bot will now sell all of it tokens when the price will increase or decrease by 50%


# Same here as sell condition
def sell_condition(dataframe, index):
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        return True


# ------------------------------------------------------------------
# The let's run our backtest !
# ------------------------------------------------------------------

# This function is used to register our conditions
engine.register_sell_and_buy_condition(buy_condition, sell_condition)

# This function is used to run the backtest, first parameter is the coin name, second is the token name, third
# is your initial coin balance 4th is your initial token balance 5th is your taker fees and 6th is your maker fees
engine.run_sell_and_buy_condition("USDT", "Ethereum", 20, 0, 0.065, 0.019)

# We use this function to summarize and display the result of our backtest
engine.wallet.data_handler.display_wallet()

# And we finally use it to plot graphs of price and balance evolution, the parameter is not required and is the size
# of the sell and buy point on price graph
engine.wallet.data_handler.plot_wallet()

# -----------------------------------------------------------------------------------------------------------------
# And that's finish ! Hope you like and that it wasn't hard ! If you have any question dm me on discord: Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
