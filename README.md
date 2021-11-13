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
 - Plotly
 - Python-binance
 
 *All requirements will be downloaded and installed with Open Backtest installation*
 
 ## Doc 📝

### How to run a backtest ?
We will see here a simple example

```python
# ------------------------------------------------------------------
# Let's show you how to run a very simple strategy !
# First of all, let's see all our imports
# ------------------------------------------------------------------

# The library Technical Analyse is already included when installing open backtest
# it allow to add a lot of indicators very useful for trading strategy
from ta import trend, momentum

# Let's import here 4 classes of Open Backtest we will later see how to use it
from OpenBacktest.ObtEngine import Engine, Container, Pair, Report

# Python Binance is also included with Open Backtest it allow us to get the market data
from binance.client import Client

# ------------------------------------------------------------------
# The let's initialise our classes
# ------------------------------------------------------------------

# First of all we are here creating our container, it will contain all of our market pairs
container = Container()

# Let's add our market pair with the container.add_main_pair() method

# The parameter of the method is a Pair class with 5
# parameters, the parameters are quite self-explanatory but just to clarify, name is just a recognizable name for you
# that will be used later to get the data of a pair if you have multiple dataframes but we will see it later !
# At the moment just don't take care about the name it's not important,
# the path is the location of files that already exist or
# the location of futures files that will be saved, this parameter is optional.

# We register here our main pair ! The data will be get for the pair Ethereum - Usdt from the 01 january 2021 to now
# with candles of 1 hour
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path=""))

# Let's now initialise our engine with our container
engine = Engine(container)

# This line is not required ! it's used to save our data as csv files to be able to just have to load it
# for the next backtest
container.save_all(default_path="")

# We are here enriching our dataframe with technical indicators using TA lib more information here
# https://technical-analysis-library-in-python.readthedocs.io/en/latest/

# Let's add to our dataframe 2 EMA
engine.main_dataframe()["EMA3"] = trend.ema_indicator(engine.main_dataframe()['close'], 3)
engine.main_dataframe()["EMA100"] = trend.ema_indicator(engine.main_dataframe()['close'], 100)


# We will now set a strategy that will return a report class. The engine
# will call this function with the main dataframe and each index
def strategy(dataframe, index):
    # first, there's our buy condition
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        # we return a report with the order_type and the amount in percent of our coin wallet we want to buy
        return Report("buy", percent_amount=100)
    # then, there's our sell condition
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        # we return a report with the order_type and the amount in percent of our token wallet we want to sell
        return Report("sell", percent_amount=100)


# ------------------------------------------------------------------
# The let's run our backtest !
# ------------------------------------------------------------------

# This function is used to register our strategy
engine.register_strategy(strategy)

# This function is used to run the backtest, first parameter is the coin name, second is the token name, third
# is your initial coin balance 4th is your initial token balance 5th is your taker fees in percent
engine.run_strategy(coin_name="USDT", token_name="ETH", coin_balance=1000, token_balance=0, taker=0.075)

# We use this function to summarize and display the result of our backtest
engine.wallet.get_data_handler().display_wallet()

# And we finally use it to plot graphs of price and balance evolution, you can use the parameter size=... to set the
# points size and the parameter tradeline=False to disable trade lines
engine.wallet.get_data_handler().plot_wallet()

# -----------------------------------------------------------------------------------------------------------------
# And that's finish ! Hope you like and that it wasn't hard ! If you have any question dm me on discord: Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336432760889404/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336484149510165/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336590319943740/unknown.png" alt="drawing" width="1000"/>

OpenBacktest C++ is coming soon
