import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

def generer_graphique(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=('Prix', 'Volume'),
                        row_heights=[0.7, 0.3])

    # Graphique des prix
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='Prix'),
                  row=1, col=1)

    # Graphique du volume
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume'),
                  row=2, col=1)

    fig.update_layout(height=800, title_text="Cours et Volume")
    fig.update_xaxes(rangeslider_visible=False,
                     rangebreaks=[dict(bounds=["sat", "mon"])])

    return fig.to_json()