# -----------------------------------------------------------------------------------------------------------------
# First of all, let's see all our imports but before, important message !!
#
# Read and understand first how does the Symmetric engine work before to try with this engine,
# it's important because I will not show here some part of the library already explained with the symmetric engine
#
# -----------------------------------------------------------------------------------------------------------------

# The library Technical Analyse is already included when installing open backtest
# it allow to add a lot of indicators very useful for trading strategy
from ta import trend, momentum

# Let's import here 4 classes of Open Backtest we will later see how to use it
from OpenBacktest.ObtEngine import AsymmetricEngine, Container, Pair, Report

# Python Binance is also included with Open Backtest it allow us to get the market data
from binance.client import Client

# ------------------------------------------------------------------
# The let's initialise our classes
# ------------------------------------------------------------------

# First of all we are here creating our container, it will contain all of our market pairs
container = Container()

# Like for a symmetric engine let's register our main pair but this time I will not show you how to register
# others pairs with others timeframe but it's possible as explained for the symmetric engine
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path="data/"))

# Let's now initialise our engine with our container but this time, an assymetric engine
engine = AsymmetricEngine(container)

# We are here enriching our dataframes with technical indicators using TA lib more information here
# https://technical-analysis-library-in-python.readthedocs.io/en/latest/

# Let's add to our main dataframe 2 EMA
engine.main_dataframe()["EMA3"] = trend.ema_indicator(engine.main_dataframe()['close'], 3)
engine.main_dataframe()["EMA100"] = trend.ema_indicator(engine.main_dataframe()['close'], 100)


# This time our Asymmetric engine will just work with a strategy function that will return a report !
def strategy(dataframe, index):
    # we will with this function return a report, return None to do nothing or return a Report class to pass an order,
    # the first parameter of our report is required and will be the order type, "sell" or "buy". The second parameter
    # is not required and is the amount of token or coin you want to spend. The third parameter is also not required
    # and is the amount in percent of your wallet you want to spend
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        return Report("buy", percent_amount=50)
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        return Report("sell", percent_amount=50)

    # you can also here use take profit and stop loss as showed with the symmetric engine !
    # note that with this simple strategy I'm not fully using the asymmetric engine. This engine can be used for
    # more advanced strategies for example grid trading


# ------------------------------------------------------------------
# The let's run our backtest !
# ------------------------------------------------------------------

# This function is used to register our strategy
engine.register_strategy(strategy)

# This function is used to run the backtest, first parameter is the coin name, second is the token name, third
# is your initial coin balance 4th is your initial token balance 5th is your taker fees and 6th is your maker fees
engine.run_strategy("USDT", "Ethereum", 20, 0, 0.065, 0.019)

# We use this function to summarize and display the result of our backtest
engine.wallet.data_handler.display_wallet()

# And we finally use it to plot graphs of price and balance evolution, the parameter is not required and is the size
# of the sell and buy point on price graph
engine.wallet.data_handler.plot_wallet()

# -----------------------------------------------------------------------------------------------------------------
# And that's finish ! Hope you like and that it wasn't hard ! If you have any question dm me on discord: Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
