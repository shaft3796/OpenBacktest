from ta import trend, momentum

from OpenBacktest.ObtEngine import Engine, Container, Pair
from binance.client import Client

# Initialising container & pair
container = Container()
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path="test_data/"))
container.add_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1DAY, name="ETHUSDT1d",
         path="test_data/"))

# Initialising Engine
engine = Engine(container)
container.save_all(default_path="test_data/")

# enriching the dataframe with technical indicators
engine.main_dataframe()["EMA200"] = trend.ema_indicator(engine.container.main.dataframe['close'], 3)
engine.main_dataframe()["EMA600"] = trend.ema_indicator(engine.container.main.dataframe['close'], 100)


def buy_condition(dataframe, index):
    if dataframe["EMA200"][index] is None or dataframe["EMA600"][index] is None:
        return

    if dataframe["EMA200"][index] >= dataframe["EMA600"][index]:
        return True


def sell_condition(dataframe, index):
    if dataframe["EMA200"][index] is None or dataframe["EMA600"][index] is None:
        return

    if dataframe["EMA200"][index] <= dataframe["EMA600"][index]:
        return True


engine.register_sell_and_buy_condition(buy_condition, sell_condition)
engine.run_sell_and_buy_condition("USDT", "Ethereum", 20, 0, 0.065, 0.019)
engine.wallet.data_handler.display_wallet()
engine.wallet.data_handler.plot_wallet(25)
