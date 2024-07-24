# app/utils/visualisation.py
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.utils

import json

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
    fig.update_xaxes(rangeslider_visible=False)

    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)





def generer_graphique_strategie(df):
    fig = make_subplots(rows=4, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        subplot_titles=('Prix et Signaux', 'Volume', 'Rendements Cumulatifs', 'Drawdown'),
                        row_heights=[0.4, 0.2, 0.2, 0.2])

    # Graphique des prix avec signaux
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='Prix'),
                  row=1, col=1)
    
    if 'ALMA_Base' in df.columns and 'ALMA_Decalee' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['ALMA_Base'], name='ALMA Base', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['ALMA_Decalee'], name='ALMA Décalée', line=dict(color='red')), row=1, col=1)

    if 'Signal' in df.columns:
        buy_signals = df[df['Signal'] == 1]
        sell_signals = df[df['Signal'] == -1]
        
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['close'],
                                 mode='markers', name='Achat',
                                 marker=dict(symbol='triangle-up', size=10, color='green')),
                      row=1, col=1)
        
        fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['close'],
                                 mode='markers', name='Vente',
                                 marker=dict(symbol='triangle-down', size=10, color='red')),
                      row=1, col=1)

    # Graphique du volume
    fig.add_trace(go.Bar(x=df.index, y=df['volume'], name='Volume'),
                  row=2, col=1)

    # Graphique des rendements cumulatifs
    fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Returns'], name='Buy & Hold'), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Strategy_Returns'], name='Stratégie'), row=3, col=1)

    # Graphique du drawdown
    drawdown = (df['Cumulative_Strategy_Returns'] / df['Cumulative_Strategy_Returns'].cummax() - 1)
    fig.add_trace(go.Scatter(x=df.index, y=drawdown, name='Drawdown', fill='tozeroy', fillcolor='rgba(255,0,0,0.2)'), row=4, col=1)

    fig.update_layout(height=1200, title_text="Analyse de la Stratégie de Trading")
    fig.update_xaxes(rangeslider_visible=False)

   # return fig.to_json()
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



# Dans app/utils/visualisation.py

def generer_graphique_comparaison(results):
    fig = make_subplots(rows=2, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.03, 
                        subplot_titles=('Prix', 'Rendements Cumulatifs'),
                        row_heights=[0.7, 0.3])

    # Graphique des prix
    df = results[0]['df']  # Utiliser le premier DataFrame pour les prix
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'],
                                 name='Prix'),
                  row=1, col=1)

    # Graphique des rendements cumulatifs
    for result in results:
        fig.add_trace(go.Scatter(x=result['df'].index, 
                                 y=result['df']['Cumulative_Strategy_Returns'], 
                                 name=f"Stratégie: {result['nom']}"),
                      row=2, col=1)

    fig.update_layout(height=800, title_text="Comparaison des Stratégies de Trading")
    fig.update_xaxes(rangeslider_visible=False)

    return fig.to_json()