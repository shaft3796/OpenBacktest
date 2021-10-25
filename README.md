# Open Backtest

<img src="https://cdn.discordapp.com/attachments/901790872033714216/901790945127841862/IMG_2895.JPG" alt="drawing" width="300"/>

### Open source & beginner friendly crypto trading backtest library
- [French page](https://github.com/Shaft-3796/OpenBacktest/blob/master/README-FRA.md)

<br>

<img src="https://static.pepy.tech/personalized-badge/open-backtest?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads" width=150></img>
```
pip install open-backtest
```
### Wanna contact me ? 👋

https://discord.gg/wfpGXvjj9t

### Wanna support my work ? 💰

- paypal: *sh4ft.me@gmail.com*
- usdt (ERC20): *0x17B516E9cA55C330B6b2bd2830042cAf5C7ecD7a*
- btc: *34vo6zxSFYS5QJM6dpr4JLHVEo5vZ5owZH*
- eth: *0xF7f87bc828707354AAfae235dE584F27bDCc9569*

*thanks if you do it 💖*

## What is it ? 📈

**Passionate about the world of crypto and about development I decided to create a python library because I found very
 annoying for beginners to just run a simple backtest. Open Backtest got created to give apprentice but also confirmed 
 programmers a powerful and easy to use backtesting tool**

## How does it work ? 🔧

**Open Backtest is currently made with a core engine that use different classes, it can run a backtest with binance data
 and it can handle different timeframes. The library can also download and save data as a csv file to be able to load 
 it to save a considerable amount of time. The wallet class will handle orders and the data handler will summarize and 
 calculate all required data to analyze the backtest but also to plot graphs.**
 
 ##### Requirements :
 
 - Pandas
 - Numpy
 - Matplotlib
 - Python-binance
 
 *All requirements will be downloaded and installed with Open Backtest installation*
 
 ## Doc 📝
 
**The documentation will be divided in two parts, at the moment two engines are made but 
I want to add a lot of engines. The first part of the doc will show how to run a backtest. The second part of the doc 
will describe more technically the classes and functions that can be 
used**

### How to run a backtest ?
We will see here an example that use the first engine

```python
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
engine.wallet.data_handler.plot_wallet(25)

# -----------------------------------------------------------------------------------------------------------------
# And that's finish ! Hope you like and that it wasn't hard ! If you have any question dm me on discord: Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/901922918961930241/result.png" alt="drawing" width="600"/>

<br>
<br>

We will now see an example that use the asymmetric engine

```python
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
engine.wallet.data_handler.plot_wallet(25)

# -----------------------------------------------------------------------------------------------------------------
# And that's finish ! Hope you like and that it wasn't hard ! If you have any question dm me on discord: Shaft#3796
# -----------------------------------------------------------------------------------------------------------------

```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/902310248268849222/unknown.png" alt="drawing" width="600"/>

*Next part is coming soon*
