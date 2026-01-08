import pandas as pd
import numpy as np
import pytest
from analysis.ab_tests import calculate_ab_stats

def test_binary_stats():
    # Construct obvious win
    # Control: 10% conv (100/1000)
    # Treatment: 20% conv (200/1000)
    df = pd.DataFrame({
        'treatment': [0]*1000 + [1]*1000,
        'conv': [0]*900 + [1]*100 + [0]*800 + [1]*200
    })
    
    res = calculate_ab_stats(df, 'conv', metric_type='binary')
    
    assert res['relative_lift'] == 1.0 # 0.2 / 0.1 - 1 = 1.0
    assert res['p_value'] < 0.001
    assert res['ci_low'] > 0

def test_continuous_stats():
    # Control: mean 10, std 1
    # Treatment: mean 12, std 1
    df = pd.DataFrame({
        'treatment': [0]*100 + [1]*100,
        'spend': list(np.random.normal(10, 1, 100)) + list(np.random.normal(12, 1, 100))
    })
    
    res = calculate_ab_stats(df, 'spend', metric_type='continuous')
    
    assert res['effect_estimate'] > 1.0 # approx 2
    assert res['p_value'] < 0.001
