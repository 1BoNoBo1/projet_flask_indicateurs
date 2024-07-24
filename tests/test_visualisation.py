# tests/test_visualisation.py
import pytest
import pandas as pd
import json
from app.utils.visualisation import generer_graphique, generer_graphique_strategie

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'open': [100, 101, 102],
        'high': [105, 106, 107],
        'low': [98, 99, 100],
        'close': [103, 104, 105],
        'volume': [1000, 1100, 1200]
    }, index=pd.date_range('2023-01-01', periods=3))

def test_generer_graphique(sample_df):
    graphique_json = generer_graphique(sample_df)
    assert isinstance(graphique_json, str)
    graphique_data = json.loads(graphique_json)
    assert 'data' in graphique_data
    assert 'layout' in graphique_data
    assert len(graphique_data['data']) == 2  # Un pour les prix, un pour le volume

def test_generer_graphique_strategie(sample_df):
    sample_df['Signal'] = [1, -1, 1]
    sample_df['ALMA_Base'] = [101, 102, 103]
    sample_df['ALMA_Decalee'] = [100, 101, 102]
    sample_df['Cumulative_Returns'] = [1.01, 1.02, 1.03]
    sample_df['Cumulative_Strategy_Returns'] = [1.02, 1.03, 1.04]
    
    graphique_json = generer_graphique_strategie(sample_df)
    assert isinstance(graphique_json, str)
    graphique_data = json.loads(graphique_json)
    assert 'data' in graphique_data
    assert 'layout' in graphique_data
    assert len(graphique_data['data']) > 2  # Devrait avoir plus de traces que generer_graphique