import pandas as pd
import numpy as np

def custom_alma(src, length, offset, sigma):
    m = int(np.floor(offset * (length - 1)))
    s = length / sigma
    sum_weight = 0.0
    alma_val = 0.0
    for i in range(length):
        weight = np.exp(-((i - m) ** 2) / (2 * (s ** 2)))
        sum_weight += weight
        alma_val += src.iloc[i] * weight
    return alma_val / sum_weight

def calculer_alma(df, length, offset, sigma):
    if 'close' not in df.columns:
        raise ValueError("La colonne 'close' est manquante dans le DataFrame")
    return df['close'].rolling(window=length).apply(lambda x: custom_alma(x, length, offset, sigma))

def appliquer_strategie(df, longueurALMA=10, sigma=6, offset=0.85, decalage=3):
    df['ALMA_Base'] = calculer_alma(df, longueurALMA, offset, sigma)
    df['ALMA_Decalee'] = calculer_alma(df.shift(decalage), longueurALMA, offset, sigma)
    
    df['Signal'] = 0
    df.loc[(df['ALMA_Base'] > df['ALMA_Decalee']), 'Signal'] = 1
    df.loc[(df['ALMA_Base'] < df['ALMA_Decalee']), 'Signal'] = -1
    
    df['Position'] = df['Signal'].shift()
    df['Returns'] = df['close'].pct_change()
    df['Strategy_Returns'] = df['Returns'] * df['Position']
    
    df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
    df['Cumulative_Strategy_Returns'] = (1 + df['Strategy_Returns']).cumprod()
    
    return df