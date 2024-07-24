import pytest
from app.utils.telechargement_cours import telecharger_cours, sauvegarder_donnees
import pandas as pd
import os
import json

def test_telecharger_cours():
    df = telecharger_cours('BTC', '1d', '2023-01-01', '2023-01-07')
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])

def test_sauvegarder_donnees(tmp_path):
    df = pd.DataFrame({
        'open': [100, 101], 
        'high': [102, 103], 
        'low': [98, 99], 
        'close': [101, 102], 
        'volume': [1000, 1100]
    }, index=pd.date_range('2023-01-01', periods=2))
    
    csv_path, json_path = sauvegarder_donnees(df, 'BTC', '1d', '2023-01-01', '2023-01-02', data_dir=tmp_path)
    
    assert os.path.exists(csv_path)
    assert os.path.exists(json_path)
    
    # Vérifier que les fichiers sont lisibles et contiennent les bonnes données
    df_csv = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    assert df_csv.equals(df)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
        assert 'columns' in data
        assert 'index' in data
        assert 'data' in data