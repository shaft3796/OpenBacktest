# -----------------------------------------------------------------------------------------------------------------
# Premièrement importons le Nécessaire mais avant, message important !!
#
# Lisez et comprenez l'engine symétrique avant de vous lancer dans celle-ci ! Je ne reviendrais pas ici
# sur certains points déjà évoqués avec l'engine précédente
#
# -----------------------------------------------------------------------------------------------------------------

# La library Technical Analyse va nous permettre d'ajouter pleins
# d'indicateurs techniques pour nos stratégies
from ta import trend, momentum

# Importons ici 3 classes que nous utiliserons plus tard
from OpenBacktest.ObtEngine import AsymmetricEngine, Container, Pair, Report

# Maintenant importons la library python-binance pour télécharger nos données
from binance.client import Client

# ------------------------------------------------------------------
# Initialisons nos classes
# ------------------------------------------------------------------

# Premièrement créons un container qui va stocker nos paires de marchés sur diférentes timeframes si nous le souhaitons
container = Container()

# Like for a symmetric engine let's register our main pair but this time I will not show you how to register
# others pairs with others timeframe but it's possible as explained for the symmetric engine

# Comme pour notre engine symétrique enregistrons notre paire principale, mais cette fois je ne vais pas vous
# montrer comment enregistrer d'autres paires avec d'autres timeframes mais c'est possible comme expliqué avec l'engine
# symétrique
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path="data/"))

# Initialisons notre Engine avec notre container
engine = AsymmetricEngine(container)

# Ajoutons des indicateurs à nos dataframes vous pouvez suivre le lien si-dessous pour plus d'informations
# https://technical-analysis-library-in-python.readthedocs.io/en/latest/

# On ajoute 2 moyennes mobiles exponentielles
engine.main_dataframe()["EMA3"] = trend.ema_indicator(engine.main_dataframe()['close'], 3)
engine.main_dataframe()["EMA100"] = trend.ema_indicator(engine.main_dataframe()['close'], 100)


# Cette fois si notre engine va juste fonctionner avec une seule fonction qui va retourner un report
def strategy(dataframe, index):
    # Nous allons avec cette fonction retourner un report, vous pouvez ne rien retourner ou retourner None pour ne rien
    # faire ou bien retourner un Report pour passer un ordre. Le premier paramètre de notre report est obligatoire et va
    # être le type de notre ordre ! soit "sell" soit "buy". Le second paramètre n'est pas obligatoire et sera le montant
    # de token ou de coins que vous souhaitez vendre. Le 3ème paramètre n'est lui non plus pas obligatoire et va être le
    # pourcentage de votre wallet à passer dans l'ordre
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        return Report("buy", percent_amount=50)
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        return Report("sell", percent_amount=50)

    # Vous pouvez aussi ici utiliser des take profit et des stop loss !
    # Nottez qu'avec cette stratégie je n'utilise pas du tout le plein potentiel de l'engine asymétrique. Cette engine
    # peut être utilisée pour des stratégies plus avancées comme du grid trading


# ------------------------------------------------------------------
# Lançons maintenant le backtest !
# ------------------------------------------------------------------

# Cette fonction va enregistrer notre stratégie
engine.register_strategy(strategy)

# Cette fonction va lancer le backtest, le premier paramètre est le nom du coin, le second le nom du token, le 3ème la
# somme initiale de coin, la 4ème la somme initiale de token, la 5ème les fraie de taker et la 6ème les fraie de taker
engine.run_strategy("USDT", "Ethereum", 20, 0, 0.065, 0.019)

# On résume ici le résultat du backtest
engine.wallet.data_handler.display_wallet()

# Et on va afficher ici les différents graphiques, le paramètre de la fonction est la taille des points d'achat et de
# vente sur le graphique
engine.wallet.data_handler.plot_wallet()

# -----------------------------------------------------------------------------------------------------------------
# Et c'est terminé ! En espérant que ça n'a pas été trop difficile ! Pour toutes questions me contacter sur discord:
# Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
