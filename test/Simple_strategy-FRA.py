# ------------------------------------------------------------------
# Voyons comment lancer une stratégie très simple !
# Premièrement importons le Nécessaire
# ------------------------------------------------------------------

# La library Technical Analyse va nous permettre d'ajouter pleins
# d'indicateurs techniques pour nos stratégies
from ta import trend, momentum

# Importons ici 3 classes que nous utiliserons plus tard
from OpenBacktest.ObtEngine import Engine, Container, Pair, Report

# Maintenant importons la library python-binance pour télécharger nos données
from binance.client import Client

# ------------------------------------------------------------------
# Initialisons nos classes
# ------------------------------------------------------------------

# Premièrement créons un container qui va stocker notre paire
container = Container()

# Ajouton notre paire avec la méthode container.add_main_pair()

# The parameter of the method is a Pair class with 5
# parameters, the parameters are quite self-explanatory but just to clarify, name is just a recognizable name for you
# that will be used later to get the data of a pair if you have multiple dataframes but we will see it later !
# At the moment just don't take care about the name it's not important,
# the path is the location of files that already exist or
# the location of futures files that will be saved, this parameter is optional.

# La fonction a comme paramètre une classe avec
# elle-même 5 paramètres, même s'ils sont assez explicites, pour clarifier, l'attribut name va servir à reconnaitre et
# récupérer les données de la paire qui nous intéresse si nous en avons plusieurs mais ça nous le verrons plus tard
# ça n'a pas d'importance pour cette stratégie ! Le path est la localisation des potentiels fichiers
# de paires ou la localisation des futures fichiers, ce paramètre est optionel

# On enregistre ici notre paire principale ! Les données seront pour la paire ethereum usdt à partir du 1er janvier 2021
# avec des bougies d'1 heure
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path=""))

# Initialisons notre Engine avec notre container
engine = Engine(container)

# Cette ligne n'est pas obligatoire elle permet de sauvegarder la paire sous forme de fichier csv
container.save_all(default_path="")

# Ajoutons des indicateurs à nos dataframes vous pouvez suivre le lien si-dessous pour plus d'informations
# https://technical-analysis-library-in-python.readthedocs.io/en/latest/

# On ajoute 2 moyennes mobiles exponentielles
engine.main_dataframe()["EMA3"] = trend.ema_indicator(engine.main_dataframe()['close'], 3)
engine.main_dataframe()["EMA100"] = trend.ema_indicator(engine.main_dataframe()['close'], 100)


# Créons maintenant notre stratégie ! ici quand une EMA 3 passe au dessus d'une EMA 100, on achete et inversement
def strategy(dataframe, index):
    # Voici notre condition d'achat
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        # on retourne un Report avec le type de l'ordre et le montant en pourcent de notre
        # portefeuille que nous voulons acheter
        return Report("buy", percent_amount=100)
    # Voici notre condition de vente
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        # on retourne un Report avec le type de l'ordre et le montant en pourcent de notre
        # portefeuille que nous voulons vendre
        return Report("sell", percent_amount=100)


# ------------------------------------------------------------------
# Lançons maintenant le backtest !
# ------------------------------------------------------------------

# Cette fonction va enregistrer nos conditions
engine.register_strategy(strategy)

# Cette fonction va lancer le backtest, le premier paramètre est le nom du coin, le second le nom du token, le 3ème la
# somme initiale de coin, la 4ème la somme initiale de token, la 5ème les fraie de taker
engine.run_strategy(coin_name="USDT", token_name="ETH", coin_balance=1000, token_balance=0, taker=0.075)

# On résume ici le résultat du backtest
engine.wallet.data_handler.display_wallet()

# Et on va afficher ici les différents graphiques, vous pouvez ajouter size=... pour modifier la taille des points et
# tradeline=False pour désactiver les tradelines
engine.wallet.get_data_handler().plot_wallet()

# -----------------------------------------------------------------------------------------------------------------
# Et c'est terminé ! En espérant que ça n'a pas été trop difficile ! Pour toutes questions me contactaient sur discord:
# Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
