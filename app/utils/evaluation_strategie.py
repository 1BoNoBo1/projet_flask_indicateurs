import numpy as np
import pandas as pd

def calculer_metriques(df):

    
    # Rendements cumulatifs
    cumulative_returns = df['Cumulative_Strategy_Returns'].iloc[-1] - 1
    buy_hold_returns = df['Cumulative_Returns'].iloc[-1] - 1

    # Rendements annualisés
    trading_days = len(df)
    annual_returns = (1 + cumulative_returns) ** (252 / trading_days) - 1
    buy_hold_annual_returns = (1 + buy_hold_returns) ** (252 / trading_days) - 1

    # Volatilité annualisée
    volatility = df['Strategy_Returns'].std() * np.sqrt(252)

    # Ratio de Sharpe (en supposant un taux sans risque de 0)
    sharpe_ratio = annual_returns / volatility if volatility != 0 else 0

    # Drawdown maximum
    drawdown = (df['Cumulative_Strategy_Returns'] / df['Cumulative_Strategy_Returns'].cummax() - 1).min()

    # ...
    if 'Signal' in df.columns:
        trades = df['Signal'].diff().abs().sum() // 2
    else:
        trades = 0
    # ...
    # Nombre de trades
    trades = df['Signal'].diff().abs().sum() // 2

    # Taux de réussite
    winning_trades = df[df['Strategy_Returns'] > 0]['Strategy_Returns'].count()
    win_rate = winning_trades / trades if trades > 0 else 0

    # Ratio profit/perte
    avg_win = df[df['Strategy_Returns'] > 0]['Strategy_Returns'].mean()
    avg_loss = df[df['Strategy_Returns'] < 0]['Strategy_Returns'].mean()
    profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.inf

    return {
        'Rendement cumulatif': cumulative_returns,
        'Rendement Buy & Hold': buy_hold_returns,
        'Rendement annualisé': annual_returns,
        'Rendement annualisé Buy & Hold': buy_hold_annual_returns,
        'Volatilité annualisée': volatility,
        'Ratio de Sharpe': sharpe_ratio,
        'Drawdown maximum': drawdown,
        'Nombre de trades': trades,
        'Taux de réussite': win_rate,
        'Ratio profit/perte': profit_loss_ratio
    }