# Open Backtest

<img src="https://cdn.discordapp.com/attachments/901790872033714216/901790945127841862/IMG_2895.JPG" alt="drawing" width="300"/>

### Open source & beginner friendly crypto trading backtest library
- [English](https://github.com/Shaft-3796/OpenBacktest/blob/master/README.md)

<br>

<img src="https://static.pepy.tech/personalized-badge/open-backtest?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads" width=150></img>

```
pip install open-backtest
```
### Vous voulez me contacter ? 👋

https://discord.gg/wfpGXvjj9t

### Vous voulez supporter mon travail ? ? 💰

- paypal: *sh4ft.me@gmail.com*
- usdt (ERC20): *0x17B516E9cA55C330B6b2bd2830042cAf5C7ecD7a*
- btc: *34vo6zxSFYS5QJM6dpr4JLHVEo5vZ5owZH*
- eth: *0xF7f87bc828707354AAfae235dE584F27bDCc9569*

*merci si vous le faites 💖*

## Qu'est-ce qu'Open Backtest ? 📈
 
 **Passionné par le monde des cryptos en général et du développement j'ai décidé de créer une library ayant trouvé très
  ennuyeux pour les débutants de juste faire un simple backtest. Open backtest a été crée pour donner aux apprentis
   mais aussi aux confirmés un outil puissant et simple de backtesting**

## Comment ça fonctionne ? 🔧
 
 **Open Backtest fonctionne actuellement avec une "Engine" principale qui utilise différentes classes utilitaires,
  les donnés sont récoltées sur binance et la library peut gérer plusieurs intervalles de temps à la fois !
Le téléchargement des donnéss sous format Csv est aussi pris en charge afin de limiter le temps de chargement pour les 
backtests suivants. La classe Wallet va gérer les ordres d'achat et de vente et le Data Handler va résumer et calculer 
les données nécessaires à nos analyses mais aussi créer des graphiques**
 
 ##### Libraries requises :
 
 - Pandas
 - Numpy
 - Plotly
 - Python-binance
 
 *Ces libraries seront automatiquement installées en meme temps qu'Open Backtest*
 
 ## Doc 📝

### Comment lancer un backtest ? ?
Voyons un example simple !

```python
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

```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336432760889404/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336484149510165/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/908336590319943740/unknown.png" alt="drawing" width="1000"/>

OpenBacktest c++ arrive bientot !
