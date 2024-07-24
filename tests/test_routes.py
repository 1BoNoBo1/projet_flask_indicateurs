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
    assert response.location == '/'  # Vérifie que la redirection est vers l'index

    
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


def test_appliquer_strategie_route(client, tmp_path):
    # Créer et sauvegarder des données fictives comme dans test_rapport_performance_route
    # ...
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

    # Test GET request
    response = client.get('/appliquer_strategie/BTC/1d')
    assert response.status_code == 200
    assert "Appliquer la stratégie" in response.get_data(as_text=True)

    # Test POST request
    data = {
        'longueurALMA': 10,
        'sigma': 6,
        'offset': 0.85,
        'decalage': 3
    }
    response = client.post('/appliquer_strategie/BTC/1d', data=data)
    assert response.status_code == 200
    assert "Résultats de la Stratégie" in response.get_data(as_text=True)
    
    
    
def test_visualiser_route(client, tmp_path):

    # Créer et sauvegarder des données fictives
    # ...
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

    response = client.get('/visualiser/BTC/1d')
    assert response.status_code == 200
    assert "Cours de BTC/USDT (1d)" in response.get_data(as_text=True)
    
def test_comparer_strategies_route(client, tmp_path):
    # Créer et sauvegarder des données fictives
    # ...
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

    # Test GET request
    response = client.get('/comparer_strategies/BTC/1d')
    assert response.status_code == 200
    assert "Comparer les stratégies" in response.get_data(as_text=True)

    # Test POST request
    data = {
        'nom_1': 'Stratégie 1',
        'longueurALMA_1': 10,
        'sigma_1': 6,
        'offset_1': 0.85,
        'decalage_1': 3,
        'nom_2': 'Stratégie 2',
        'longueurALMA_2': 20,
        'sigma_2': 5,
        'offset_2': 0.75,
        'decalage_2': 5
    }
    response = client.post('/comparer_strategies/BTC/1d', data=data)
    assert response.status_code == 200
    assert "Comparaison des stratégies" in response.get_data(as_text=True)
    
    
def test_visualiser_route_invalid_crypto(client):
    response = client.get('/visualiser/INVALID/1d')
    assert response.status_code == 302  # Redirection
    # Vérifiez que le message flash est correct dans la session

def test_appliquer_strategie_route_invalid_params(client, tmp_path):
    # Créer et sauvegarder des données fictives
    # ...
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

    data = {
        'longueurALMA': 'invalid',
        'sigma': 'invalid',
        'offset': 'invalid',
        'decalage': 'invalid'
    }
    response = client.post('/appliquer_strategie/BTC/1d', data=data)
    assert response.status_code == 302  # Redirection
    assert response.location == '/'  # Vérifie que la redirection est vers l'index


    # Vérifiez que le message flash d'erreur est correct dans la session
    
    
def test_telecharger_cours_route(client, mocker):
    # Mocker la fonction telecharger_cours pour éviter les appels réseau réels
    mock_telecharger = mocker.patch('app.routes.telecharger_cours')
    mock_telecharger.return_value = pd.DataFrame({
        'open': [100, 101],
        'high': [102, 103],
        'low': [98, 99],
        'close': [101, 102],
        'volume': [1000, 1100]
    }, index=pd.date_range('2023-01-01', periods=2))

    data = {
        'crypto': 'BTC',
        'interval': '1d',
        'start_date': '2023-01-01',
        'end_date': '2023-01-02'
    }
    response = client.post('/telecharger', data=data)
    assert response.status_code == 302  # Redirection
    # Vérifiez que le message flash de succès est correct dans la session
    
    
def test_appliquer_strategie_route(client, tmp_path):
    # ... code pour créer des données fictives ...
    # ...
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
    # ...

    response = client.get('/appliquer_strategie/BTC/1d')
    assert response.status_code == 200
    assert "Appliquer la stratégie pour BTC/USDT (1d)" in response.get_data(as_text=True)
    