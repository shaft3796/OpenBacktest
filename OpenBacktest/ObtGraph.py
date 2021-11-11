import plotly.graph_objects as go
from plotly.subplots import make_subplots

from OpenBacktest.ObtUtility import Colors


class GraphManager:
    def __init__(self, rows=1, cols=1, height=None, titles=None):
        self.fig = make_subplots(rows=rows, cols=cols, row_width=height, subplot_titles=titles)
        self.fig.update_layout(
            title_text="",
            xaxis_title_text="",
            yaxis_title_text="",
            xaxis_rangeslider_visible=False,
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            )
        )

    def show(self):
        self.fig.show()

    def set_title(self, title):
        self.fig.update_layout(title_text=title)

    def set_sub_title(self, title, target="main", sub=1):
        if sub == 1:
            sub = ""
        if target == "main":
            print(self.fig["layout"])
        elif target == "x":
            target = "xaxis" + str(sub)
            self.fig["layout"][target]["title"] = title
        elif target == "y":
            target = "yaxis" + str(sub)
            self.fig["layout"][target]["title"] = title

    def add_trace(self, trace, row=1, col=1):
        self.fig.add_trace(trace, row=row, col=col)

    def draw_marker(self, x, y, marker_symbol="circle", marker_color="black", marker_size=10, text=None,
                    showlegend=False, hoverinfo=None, row=1, col=1):
        if type(x) is not list:
            x = [x]
        if type(y) is not list:
            y = [y]
        self.add_trace(
            go.Scatter(x=x, y=y, mode="markers", name='', text=text,
                       marker=dict(size=marker_size, color=marker_color, symbol=marker_symbol), showlegend=showlegend,
                       hoverinfo=hoverinfo), row=row, col=col)

    def draw_line(self, x, y, line_color="black", line_width=2, showlegend=False, name="", text=None, hoverinfo=None,
                  row=1, col=1):
        if type(x) is not list and type(y) is not list:
            print(Colors.RED + "Error: x and y must be a list, needing at least 2 points to draw a line")
            return
        self.fig.add_trace(
            go.Scatter(x=x, y=y, mode="lines", name=name, text=text, line=dict(width=line_width, color=line_color),
                       showlegend=showlegend, hoverinfo=hoverinfo), row=row, col=col)

    def draw_marked_line(self, x, y, name="", text=None, marker_symbol="circle", marker_color=None, marker_size=10,
                         line_color="black", line_width=2, showlegend=False, hoverinfo=None, row=1, col=1):
        if marker_color is None:
            marker_color = "black"
        if type(x) is not list and type(y) is not list:
            print(Colors.RED + "Error: x and y must be a list, needing at least 2 points to draw a line")
            return
        self.fig.add_trace(
            go.Scatter(x=x, y=y, text=text, name=name,
                       marker=dict(size=marker_size, color=marker_color, symbol=marker_symbol),
                       line=dict(width=line_width, color=line_color), showlegend=showlegend, hoverinfo=hoverinfo),
            row=row, col=col)

    def plot_price(self, dataframe, row=1, col=1):
        self.fig.add_trace(go.Candlestick(x=dataframe['timestamp'],
                                                         open=dataframe['open'],
                                                         high=dataframe['high'],
                                                         low=dataframe['low'],
                                                         close=dataframe['close'],
                                                         showlegend=False), row=row, col=col)

    # PRESETS
    def draw_trade_line(self, buy_time, buy_price, sell_time, sell_price, marker_symbol=None, marker_size=10,
                        line_width=2, line_color=None, marker_color=None, showlegend=False, hoverinfo="none", row=1,
                        col=1):
        if marker_symbol is None:
            marker_symbol = ["triangle-up-dot", "triangle-down-dot"]

        x = [buy_time, sell_time]
        y = [buy_price, sell_price]
        if marker_color is None:
            marker_color = ["green", "red"]
        if line_color is None:
            if buy_price >= sell_price:
                line_color = "#ed4747"
            else:
                line_color = "#54a832"

        self.draw_marked_line(x, y, text=["buy", "sell"], line_color=line_color, marker_symbol=marker_symbol,
                              marker_color=marker_color,marker_size=marker_size, line_width=line_width,
                              showlegend=showlegend, hoverinfo=hoverinfo, row=row, col=col)