# Experiment Decision Report: Criteo Uplift Test
    
## Executive Summary
**Decision**: SHIP
**Experiment ID**: 1
**Status**: analyzed
**Start Date**: 2023-01-01

## Rationale
- Primary Metric (outcome_conversion): 0.0238 absolute effect (p=0.0000).
- Statistically significant positive effect observed.

## Health Checks
| Check | Status | Details |
|-------|--------|---------|
| SRM | PASS | {'status': 'PASS', 'details': {'total_n': 100000, 'expected': {'0': 50000.0, '1': 50000.0}, 'observed': {'0': 49952, '1': 50048}, 'chi2_stat': 0.09216}, 'p_value': 0.7614489151115178, 'check_name': 'SRM'} |

## Key Metrics Results
| Metric | Method | Effect | P-Value | CI |
|---|---|---|---|---|
| outcome_conversion | z_test | 0.0238 | 0.0000 | [0.0208, 0.0268] |
| conversion_cuped | cuped | 0.0237 | 0.0000 | [0.0207, 0.0267] |
| outcome_visit | welch_t_test | -0.0006 | 0.7993 | [-0.0056, 0.0043] |
| outcome_conversion | z_test | 0.0238 | 0.0000 | [0.0208, 0.0268] |
| outcome_visit | welch_t_test | -0.0006 | 0.7993 | [-0.0056, 0.0043] |
| conversion_cuped | cuped | 0.0237 | 0.0000 | [0.0207, 0.0267] |
| outcome_conversion | z_test | 0.0238 | 0.0000 | [0.0208, 0.0268] |
| outcome_visit | welch_t_test | -0.0006 | 0.7993 | [-0.0056, 0.0043] |
| conversion_cuped | cuped | 0.0237 | 0.0000 | [0.0207, 0.0267] |
| outcome_conversion | z_test | 0.0238 | 0.0000 | [0.0208, 0.0268] |
| conversion_cuped | cuped | 0.0237 | 0.0000 | [0.0207, 0.0267] |
| outcome_visit | welch_t_test | -0.0006 | 0.7993 | [-0.0056, 0.0043] |

## Uplift Modeling (Opportunity)
- **class_transform**: Qini AUC = 0.100. Targeting top 30% yields 0.049 expected lift.
- **solo_model**: Qini AUC = 0.116. Targeting top 30% yields 0.055 expected lift.
- **class_transform**: Qini AUC = 0.100. Targeting top 30% yields 0.049 expected lift.
- **solo_model**: Qini AUC = 0.116. Targeting top 30% yields 0.055 expected lift.
