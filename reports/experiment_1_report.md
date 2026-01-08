# Experiment Decision Report: Hillstrom Mens Email
    
## Executive Summary
**Decision**: SHIP
**Experiment ID**: 1
**Status**: analyzed
**Start Date**: 2023-01-01

## Rationale
- Primary Metric (outcome_conversion): 0.0068 absolute effect (p=0.0000).
- Statistically significant positive effect observed.

## Health Checks
| Check | Status | Details |
|-------|--------|---------|
| SRM | PASS | {'status': 'PASS', 'details': {'total_n': 42613, 'expected': {'0': 21306.5, '1': 21306.5}, 'observed': {'0': 21306, '1': 21307}, 'chi2_stat': 2.346701710745547e-05}, 'p_value': 0.9961348415003554, 'check_name': 'SRM'} |

## Key Metrics Results
| Metric | Method | Effect | P-Value | CI |
|---|---|---|---|---|
| outcome_conversion | z_test | 0.0068 | 0.0000 | [0.0050, 0.0086] |
| outcome_visit | welch_t_test | 0.0766 | 0.0000 | [0.0700, 0.0832] |
