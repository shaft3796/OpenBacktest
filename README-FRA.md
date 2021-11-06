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

**La documentation va être divisée en deux parties, pour le moment juste deux "Engine" sont faites mais je vais en 
ajouter plein d'autres dans le futur. La première partie de la doc va montrer comment lancer 
un backtest. La seconde partie va décrire plus techniquement les classes et fonctions utilisables**

### Comment lancer un backtest ?
Voyons ici in exemple utilisant la première engine

```python
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

# Nous allons maintenant ajouter nos paires à l'aide de deux fonctions, container.add_main_pair() et container.add_pair() 
# Ces 2 fonctions vont avoir les mêmes paramètres ! La "main pair" va être la paire principale tradée par notre 
# stratégie et elle est obligatoire ! Il y a aussi une autre fonction container.add_pair() pour ajouter d'autres paires,
# ce n'est pas obligatoire ! C'est cependant inutile avec cette engine d'ajouter une paire d'un autre symbole même si
# c'est techniquement possible, le réel intérêt est d'ajouter la même paire mais avec un autre timeframe ! 
# Suivez la structure ci-dessous pour ajouter vos paires. Les deux fonctions ont comme paramètre une classe avec 
# elle-même 5 paramètres, même s'ils sont assez explicites, pour clarifier, l'attribut name va servir à reconnaitre et 
# récupérer les données de la paire qui nous intéresse par la suite. Le path est la localisation des potentiels fichiers 
# de paires ou la localisation des futures fichiers, ce paramètre est optionel

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
# Et c'est terminé ! En espérant que ça n'a pas été trop difficile ! Pour toutes questions me contactaient sur discord: 
# Shaft#3796
# -----------------------------------------------------------------------------------------------------------------
```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561299503259729/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561215600394241/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561877520310342/unknown.png" alt="drawing" width="1000"/>

<br>
<br>

Voyons maintenant un exemple avec l'engine asymétrique

```python
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
from OpenBacktest.ObtEngine import AsymmetricEngine, Container, Pair

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
         path=""))

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
engine.wallet.data_handler.plot_wallet(25)

# -----------------------------------------------------------------------------------------------------------------
# Et c'est terminé ! En espérant que ça n'a pas été trop difficile ! Pour toutes questions me contacter sur discord:
# Shaft#3796
# -----------------------------------------------------------------------------------------------------------------

```

<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561364221395044/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561406592237628/unknown.png" alt="drawing" width="800"/>
<img src="https://cdn.discordapp.com/attachments/901790872033714216/906561578080563270/unknown.png" alt="drawing" width="1000"/>

*Next part is coming soon*
