# tests/test_evaluation_strategie.py
import pytest
import pandas as pd
from app.utils.evaluation_strategie import calculer_metriques

@pytest.fixture
def sample_df_strategie():
    return pd.DataFrame({
        'close': [100, 101, 102, 101, 103],
        'Strategy_Returns': [0.01, -0.01, 0.02, -0.02, 0.03],
        'Cumulative_Strategy_Returns': [1.01, 1.00, 1.02, 1.00, 1.03],
        'Cumulative_Returns': [1.00, 1.01, 1.03, 1.01, 1.04]
    }, index=pd.date_range('2023-01-01', periods=5))

def test_calculer_metriques(sample_df_strategie):
    sample_df_strategie['Signal'] = [1, -1, 1, -1, 1]  # Ajout de la colonne Signal
    metriques = calculer_metriques(sample_df_strategie)
    assert isinstance(metriques, dict)
    assert 'Rendement cumulatif' in metriques
    assert 'Ratio de Sharpe' in metriques
    assert 'Drawdown maximum' in metriques
    assert 'Nombre de trades' in metriques
    assert metriques['Nombre de trades'] == 2