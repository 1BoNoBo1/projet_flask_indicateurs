# tests/test_strategie_trading.py
import pytest
import pandas as pd
from app.utils.strategie_trading import appliquer_strategie, calculer_alma

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [98, 99, 100, 101, 102],
        'close': [103, 104, 105, 106, 107],
        'volume': [1000, 1100, 1200, 1300, 1400]
    }, index=pd.date_range('2023-01-01', periods=5))

def test_calculer_alma(sample_df):
    assert 'close' in sample_df.columns, "La colonne 'close' est manquante dans le DataFrame de test"
    alma = calculer_alma(sample_df['close'], 3, 0.85, 6)
    assert isinstance(alma, pd.Series)
    assert len(alma) == len(sample_df)

def test_appliquer_strategie(sample_df):
    df_strategie = appliquer_strategie(sample_df)
    assert 'Signal' in df_strategie.columns
    assert 'Position' in df_strategie.columns
    assert 'Strategy_Returns' in df_strategie.columns
    assert 'Cumulative_Strategy_Returns' in df_strategie.columns