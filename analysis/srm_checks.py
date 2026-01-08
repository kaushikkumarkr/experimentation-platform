import pandas as pd
from scipy.stats import chisquare
import logging

logger = logging.getLogger(__name__)

def check_srm(df: pd.DataFrame, treatment_col='treatment') -> dict:
    """
    Performs a Chi-Square test for Sample Ratio Mismatch.
    Assumes 50/50 allocation if not specified.
    """
    if df.empty:
        return {'status': 'FAIL', 'p_value': 0.0, 'details': 'No data'}

    observed_counts = df[treatment_col].value_counts().sort_index()
    
    # Ensure zero counts are handled if a group is missing entirely
    possible_treatments = [0, 1] 
    observed = [int(observed_counts.get(t, 0)) for t in possible_treatments]
    total_n = sum(observed)
    
    # Expected counts (assuming 50/50)
    expected = [float(total_n / 2), float(total_n / 2)]
    
    chi2, p_value = chisquare(f_obs=observed, f_exp=expected)
    
    status = 'PASS'
    if p_value < 0.001:
        status = 'FAIL'
    elif p_value < 0.01:
        status = 'WARN'
        
    return {
        'status': status,
        'p_value': float(p_value),
        'check_name': 'SRM',
        'details': {
            'observed': dict(zip(possible_treatments, observed)),
            'expected': dict(zip(possible_treatments, expected)),
            'total_n': int(total_n),
            'chi2_stat': float(chi2)
        }
    }
