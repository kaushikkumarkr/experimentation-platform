import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.weightstats import ttest_ind, CompareMeans, DescrStatsW

def calculate_ab_stats(df: pd.DataFrame, metric_col: str, treatment_col='treatment', metric_type='continuous', alpha=0.05):
    """
    Calculates A/B test statistics.
    Types: 'continuous' (means), 'binary' (proportions).
    """
    treatment = df[df[treatment_col] == 1][metric_col]
    control = df[df[treatment_col] == 0][metric_col]
    
    mean_t = treatment.mean()
    mean_c = control.mean()
    
    delta = mean_t - mean_c
    rel_lift = (mean_t / mean_c) - 1 if mean_c != 0 else 0
    
    result = {
        'metric_name': metric_col,
        'mean_control': mean_c,
        'mean_treatment': mean_t,
        'effect_estimate': delta,
        'relative_lift': rel_lift,
    }
    
    if metric_type == 'binary':
        # Z-test
        count = np.array([treatment.sum(), control.sum()])
        nobs = np.array([len(treatment), len(control)])
        
        stat, pval = proportions_ztest(count, nobs)
        
        # CI for difference in proportions (using statsmodels or manual SE)
        # For simplicity in this demo, manual Wald CI for difference
        se = np.sqrt(mean_t*(1-mean_t)/len(treatment) + mean_c*(1-mean_c)/len(control))
        z_score = 1.96 # approx for 95%
        ci_low = delta - z_score * se
        ci_high = delta + z_score * se
        
    else:
        # Welch's t-test
        # use statsmodels CompareMeans
        cm = CompareMeans(DescrStatsW(treatment), DescrStatsW(control))
        stat, pval, df_dof = cm.ttest_ind(usevar='unequal') # unequal variance (Welch)
        
        ci_low, ci_high = cm.tconfint_diff(alpha=alpha, usevar='unequal')
        
    result['p_value'] = float(pval)
    result['ci_low'] = float(ci_low)
    result['ci_high'] = float(ci_high)
    result['method'] = 'z_test' if metric_type == 'binary' else 'welch_t_test'
    
    return result
