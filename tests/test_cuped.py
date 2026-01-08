import pandas as pd
import numpy as np
import pytest
from analysis.cuped import calculate_cuped_stats

def test_cuped_variance_reduction():
    np.random.seed(42)
    n = 1000
    
    # Pre-experiment covariate (highly correlated with outcome)
    pre_spend = np.random.normal(100, 10, n)
    
    # Treatment assignment
    treatment = np.random.choice([0, 1], n)
    
    # Outcome: correlated with pre_spend + treatment effect + noise
    # R^2 should be high -> high variance reduction
    noise = np.random.normal(0, 2, n)
    effect = treatment * 5
    post_spend = pre_spend + effect + noise
    
    df = pd.DataFrame({
        'treatment': treatment,
        'pre_spend': pre_spend,
        'post_spend': post_spend
    })
    
    res = calculate_cuped_stats(df, 'post_spend', ['pre_spend'])
    
    assert res['variance_reduction'] > 0.5 # Expect > 50% reduction due to high correlation
    assert res['effect_estimate'] > 4.0 # Should still capture the +5 lift
    assert res['method'] == 'cuped'

def test_cuped_no_correlation():
    # If covariate is noise, variance reduction should be near 0
    df = pd.DataFrame({
        'treatment': [0, 1] * 100,
        'metric': np.random.normal(0, 1, 200),
        'noise': np.random.normal(0, 1, 200)
    })
    res = calculate_cuped_stats(df, 'metric', ['noise'])
    assert res['variance_reduction'] < 0.1
