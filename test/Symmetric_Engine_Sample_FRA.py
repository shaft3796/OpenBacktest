# ------------------------------------------------------------------
# Premièrement importons le Nécessaire
# ------------------------------------------------------------------

# La library Technical Analyse va nous permettre d'ajouter pleins
# d'indicateurs techniques pour nos stratégies
from ta import trend, momentum

# Importons ici 3 classes que nous utiliserons plus tard
from OpenBacktest.ObtEngine import Engine, Container, Pair

# Maintenant importons la library python-binance pour télécharger nos données
from binance.client import Client

# ------------------------------------------------------------------
# Initialisons nos classes
# ------------------------------------------------------------------

# Premièrement créons un container qui va stocker nos paires de marchés sur diférentes timeframes si nous le souhaitons
container = Container()

# Nous allons maintenant ajouter nos paires à l'aide de deux fonctions, container.add_main_pair() et
# container.add_pair() Ces 2 fonctions vont avoir les mêmes paramètres ! La "main pair" va être la paire principale
# tradée par notre stratégie et elle est obligatoire ! Il y a aussi une autre fonction container.add_pair() pour
# ajouter d'autres paires, ce n'est pas obligatoire ! C'est cependant inutile avec cette engine d'ajouter une paire
# d'un autre symbole même si c'est techniquement possible, le réel intérêt est d'ajouter la même paire mais avec un
# autre timeframe ! Suivez la structure ci-dessous pour ajouter vos paires. Les deux fonctions ont comme paramètre
# une classe avec elle-même 5 paramètres, même s'ils sont assez explicites, pour clarifier, l'attribut name va servir
# à reconnaitre et récupérer les données de la paire qui nous intéresse par la suite. Le path est la localisation des
# potentiels fichiers de paires ou la localisation des futures fichiers, ce paramètre est optionel

# On enregistre ici notre paire principale ! Les données seront pour la paire ethereum usdt à partir du 1er janvier 2021
# avec des bougies d'1 heure
container.add_main_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1HOUR, name="ETHUSDT",
         path=""))
# On enregistre ici une seconde paire avec un timeframe plus large ! Les données seront pour la paire ethereum usdt à
# partir du 1er janvier 2021 avec des bougies d'1 heure, notez que le nom ne doit pas être identique que la paire
# principale
container.add_pair(
    Pair(market_pair="ETHUSDT", start="01 january 2021", timeframe=Client.KLINE_INTERVAL_1DAY, name="ETHUSDT1d",
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

# Idem mais cette fois si à notre seconde dataframe
engine.get_sub_dataframe("ETHUSDT1d")["EMA3"] = trend.ema_indicator(engine.get_sub_dataframe("ETHUSDT1d")["close"], 3)
engine.get_sub_dataframe("ETHUSDT1d")["EMA100"] = trend.ema_indicator(engine.get_sub_dataframe("ETHUSDT1d")["close"],
                                                                                                                    100)


# Créons maintenant deux conditions de vente et d'achat. L'Engine va les appeler avec la dataframe principal et
# l'index actuel
def buy_condition(dataframe, index):
    if dataframe["EMA3"][index] >= dataframe["EMA100"][index]:
        return True

    # Nous n'utiliserons pas ici notre deuxième dataframe mais si vous voulez utiliser ses données voici comment faire
    # On récupère la classe de la paire
    second_pair = engine.container.get_pair("ETHUSDT1d")
    # Puis le dataframe
    second_dataframe = second_pair.dataframe
    # Ensuite l'index équivalent à celui de la dataframe principal
    second_index = second_pair.get_index(dataframe["timestamp"][index])
    # On peut maintenant accéder à notre dataframe d'1 jour comme ceci
    current_value_of_ema = second_dataframe["EMA3"][second_index]

    # Vous pouvez aussi placer des take profit et des stop loss !
    engine.set_take_profit(index, percent_target=50)
    engine.set_stop_loss(index, percent_target=-50)
    # Notre bot va maintenant vendre ses tokens quand le prix va monter ou baisser de 50%

# Idem ici avec notre condition de vente
def sell_condition(dataframe, index):
    if dataframe["EMA3"][index] <= dataframe["EMA100"][index]:
        return True


# ------------------------------------------------------------------
# Lançons maintenant le backtest !
# ------------------------------------------------------------------

# Cette fonction va enregistrer nos conditions
engine.register_sell_and_buy_condition(buy_condition, sell_condition)

# Cette fonction va lancer le backtest, le premier paramètre est le nom du coin, le second le nom du token, le 3ème la
# somme initiale de coin, la 4ème la somme initiale de token, la 5ème les fraie de taker et la 6ème les fraie de taker
engine.run_sell_and_buy_condition("USDT", "Ethereum", 20, 0, 0.065, 0.019)

# On résume ici le résultat du backtest
engine.wallet.data_handler.display_wallet()

# Et on va afficher ici les différents graphiques, le paramètre de la fonction est la taille des points d'achat et de
# vente sur le graphique
engine.wallet.data_handler.plot_wallet(25)

# -----------------------------------------------------------------------------------------------------------------
# Et c'est terminé ! En espérant que ça n'a pas été trop difficile ! Pour toutes questions me contacter sur discord:
# Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
