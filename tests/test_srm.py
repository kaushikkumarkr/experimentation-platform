import pandas as pd

from analysis.srm_checks import check_srm

def test_srm_perfect_split():
    df = pd.DataFrame({'treatment': [0]*500 + [1]*500})
    result = check_srm(df)
    assert result['status'] == 'PASS'
    assert result['p_value'] > 0.9  # Should be 1.0 ideally

def test_srm_fail():
    # 800 vs 200 split -> Major SRM
    df = pd.DataFrame({'treatment': [0]*800 + [1]*200})
    result = check_srm(df)
    assert result['status'] == 'FAIL'
    assert result['p_value'] < 0.001

def test_srm_warn():
    # Slightly off
    # 540 vs 460 - might be warn or pass depending on N
    # Let's try 550 vs 450
    df = pd.DataFrame({'treatment': [0]*550 + [1]*450})
    # chi2 on 550/450: (50^2/500 + 50^2/500) = 2500/500*2 = 10. p(chi2>10, df=1) ~ 0.0015 -> WARN
    result = check_srm(df)
    assert result['status'] in ['WARN', 'FAIL'] 
