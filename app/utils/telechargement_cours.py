import requests
import pandas as pd
from datetime import datetime
import os
from app import app
import json

def telecharger_cours(crypto='BTC', interval='1d', start_date=None, end_date=None):
    base_url = 'https://api.binance.com/api/v3/klines'
    symbol = f'{crypto}USDT'
    
    if start_date is None:
        start_date = '2016-01-01'
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        'symbol': symbol,
        'interval': interval,
        'startTime': int(pd.Timestamp(start_date).timestamp() * 1000),
        'endTime': int(pd.Timestamp(end_date).timestamp() * 1000)
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df.astype(float)
    
    return df

def sauvegarder_donnees(df, crypto, interval, start_date, end_date, data_dir=None):
    if data_dir is None:
        data_dir = app.config['DATA_DIR']
    
    filename = f"{crypto}USDT_{interval}_{start_date}_{end_date}"
    
    # Sauvegarder en CSV
    csv_path = os.path.join(data_dir, f'{filename}.csv')
    df.to_csv(csv_path)
    
    # Sauvegarder en JSON
    json_path = os.path.join(data_dir, f'{filename}.json')
    json_data = {
        'columns': df.columns.tolist(),
        'index': (df.index.astype(int) // 10**6).tolist(),  # Convertir en millisecondes
        'data': df.values.tolist()
    }
    with open(json_path, 'w') as f:
        json.dump(json_data, f)
    
    return csv_path, json_path
