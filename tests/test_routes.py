import pytest
from app import app
import os
import json
import pandas as pd
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "Projet Flask Indicateurs" in response.get_data(as_text=True)

def test_telecharger_route(client):
    response = client.get('/telecharger')
    assert response.status_code == 200
    assert "Télécharger les cours" in response.get_data(as_text=True)

def test_visualiser_route_no_data(client):
    response = client.get('/visualiser/BTC/1d')
    assert response.status_code == 302  # Redirection
    # Vérifiez que le message flash est correct dans la session
    
def test_rapport_performance_route(client):
    response = client.get('/rapport/BTC/1d')
    assert response.status_code == 200
    assert "Rapport de Performance - BTC/USDT (1d)" in response.get_data(as_text=True)
    
def test_rapport_performance_route(client, tmp_path):
    # Créer des données fictives
    df = pd.DataFrame({
        'open': [100, 101, 102],
        'high': [102, 103, 104],
        'low': [98, 99, 100],
        'close': [101, 102, 103],
        'volume': [1000, 1100, 1200]
    }, index=pd.date_range(start=datetime.now(), periods=3))

    # Sauvegarder les données fictives
    data_dir = tmp_path / 'data'
    os.makedirs(data_dir, exist_ok=True)
    filename = f"BTCUSDT_1d_{datetime.now().strftime('%Y-%m-%d')}_{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}.json"
    filepath = data_dir / filename
    
    json_data = {
        'columns': df.columns.tolist(),
        'index': (df.index.astype(int) // 10**6).tolist(),  # Convertir en millisecondes
        'data': df.values.tolist()
    }
    with open(filepath, 'w') as f:
        json.dump(json_data, f)

    # Configurer l'application pour utiliser le répertoire de données temporaire
    client.application.config['DATA_DIR'] = str(data_dir)

    # Faire la requête
    response = client.get('/rapport/BTC/1d')
    assert response.status_code == 200
    assert "Rapport de Performance - BTC/USDT (1d)" in response.get_data(as_text=True)


