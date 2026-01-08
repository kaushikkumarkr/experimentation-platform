import pandas as pd
import numpy as np
import pytest
from analysis.uplift_models import train_uplift_model

def test_uplift_persuadables():
    # Synthetic data:
    # Feature X > 0: Responds to treatment (Persuadable)
    # Feature X < 0: No effect (Sleeping Dog or Lost Cause)
    
    np.random.seed(42)
    n = 1000
    X = np.random.normal(0, 1, n)
    treatment = np.random.choice([0, 1], n)
    
    # Baseline conversion 10%
    y = np.random.choice([0, 1], n, p=[0.9, 0.1])
    
    # Add lift for X > 0 and Treatment = 1
    mask = (X > 0) & (treatment == 1)
    # Force conversion for these people
    y[mask] = 1 # Extreme lift
    
    df = pd.DataFrame({
        'feature_x': X,
        'treatment': treatment,
        'outcome': y
    })
    
    res = train_uplift_model(df, ['feature_x'], outcome_col='outcome')
    
    # Model should easily find this signal
    assert res['qini_auc'] > 0.05
    assert res['uplift_at_30'] > 0
