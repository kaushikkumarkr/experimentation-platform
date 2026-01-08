import pandas as pd

import statsmodels.api as sm
from analysis.ab_tests import calculate_ab_stats

def calculate_cuped_stats(df: pd.DataFrame, metric_col: str, covariate_cols: list, treatment_col='treatment'):
    """
    Calculates CUPED adjusted metric and runs A/B test on it.
    Y_cuped = Y - theta * (X - E[X])
    """
    
    # Check for missing data
    df_clean = df.dropna(subset=[metric_col] + covariate_cols).copy()
    
    if df_clean.empty:
        raise ValueError("No data for CUPED")
        
    y = df_clean[metric_col]
    X = df_clean[covariate_cols]
    
    # 1. Estimate Theta (using total population or pre-experiment, here total for simplicity as is common in simple CUPED)
    # Ideally should correct for treatment effect in Theta estimation if effect is large, but OLS on pooled usually fine for small effects.
    # Better: Estimate on Control only or demeaned.
    # Let's use pooled covariance.
    
    # Using statsmodels OLS to get theta
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit()
    theta = model.params[covariate_cols] # Series
    
    # 2. Calculate CUPED metric
    # Y_cuped = Y - (X - X_mean) * theta
    X_mean = X.mean()
    
    # Dot product for multiple covariates
    correction = (X - X_mean).dot(theta)
    df_clean[f'{metric_col}_cuped'] = y - correction
    
    # 3. Run Standard AB test on CUPED metric
    # Treat as continuous even if original was binary (CUPED makes it continuous)
    result = calculate_ab_stats(df_clean, f'{metric_col}_cuped', treatment_col, metric_type='continuous')
    
    result['method'] = 'cuped'
    result['original_variance'] = y.var()
    result['cuped_variance'] = df_clean[f'{metric_col}_cuped'].var()
    result['variance_reduction'] = 1 - (result['cuped_variance'] / result['original_variance'])
    
    return result
