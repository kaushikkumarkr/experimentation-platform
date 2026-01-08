import pandas as pd
from sqlalchemy import text

def generate_decision_report(experiment_id: int, engine):
    """
    Generates a Markdown decision report for an experiment.
    """
    
    # 1. Fetch Metadata
    meta = pd.read_sql(f"SELECT * FROM experimentation.experiment_registry WHERE experiment_id = {experiment_id}", engine).iloc[0]
    
    # 2. Fetch Health
    health = pd.read_sql(f"SELECT * FROM experimentation.experiment_health_checks WHERE experiment_id = {experiment_id} ORDER BY computed_at DESC LIMIT 1", engine)
    
    # 3. Fetch Results
    results = pd.read_sql(f"SELECT * FROM experimentation.experiment_results WHERE experiment_id = {experiment_id} ORDER BY computed_at DESC", engine)
    
    # 4. Fetch Uplift
    uplift = pd.read_sql(f"SELECT * FROM experimentation.uplift_policy_results WHERE experiment_id = {experiment_id} ORDER BY computed_at DESC", engine)
    
    # --- Decision Logic ---
    decision = "HOLD"
    rationale = []
    
    # Check Health
    health_status = 'UNKNOWN'
    if not health.empty:
        health_status = health.iloc[0]['status']
        if health_status == 'FAIL':
            decision = "HOLD (Health Failure)"
            rationale.append("Experiment failed health checks (SRM or Data Quality). Results are invalid.")
    
    # Check Primary Metric (Conversion)
    primary_metric = meta['primary_metric'] or 'conversion'
    
    # Find result for primary metric (prefer CUPED if available)
    primary_res = results[results['metric_name'].str.contains(primary_metric)].sort_values('method')
    
    if not primary_res.empty:
        # Pick best method row
        row = primary_res.iloc[-1] # simplistic
        # Use effect_estimate (absolute difference)
        lift = row['effect_estimate'] 
        pval = row['p_value']
        
        rationale.append(f"Primary Metric ({row['metric_name']}): {lift:.4f} absolute effect (p={pval:.4f}).")
        
        if health_status != 'FAIL':
            if pval < 0.05:
                if lift > 0:
                    decision = "SHIP"
                    rationale.append("Statistically significant positive effect observed.")
                else:
                    decision = "HOLD"
                    rationale.append("Statistically significant negative effect (or neutral).")
            else:
                decision = "ITERATE"
                rationale.append("Results not significant. Consider running longer or checking power.")
                
    # --- Markdown Generation ---
    md = f"""# Experiment Decision Report: {meta['name']}
    
## Executive Summary
**Decision**: {decision}
**Experiment ID**: {experiment_id}
**Status**: {meta['status']}
**Start Date**: {meta['start_date']}

## Rationale
{chr(10).join(['- ' + r for r in rationale])}

## Health Checks
| Check | Status | Details |
|-------|--------|---------|
"""
    if not health.empty:
        row = health.iloc[0]
        md += f"| {row['check_name']} | {row['status']} | {row['details']} |\n"
    else:
        md += "| SRM | PENDING | No check run |\n"

    md += "\n## Key Metrics Results\n| Metric | Method | Effect | P-Value | CI |\n|---|---|---|---|---|\n"
    for _, row in results.iterrows():
        md += f"| {row['metric_name']} | {row['method']} | {row['effect_estimate']:.4f} | {row['p_value']:.4f} | [{row['ci_low']:.4f}, {row['ci_high']:.4f}] |\n"
        
    if not uplift.empty:
        md += "\n## Uplift Modeling (Opportunity)\n"
        for _, row in uplift.iterrows():
            md += f"- **{row['model_name']}**: Qini AUC = {row['qini_auc']:.3f}. Targeting top 30% yields {row['expected_value_lift']:.3f} expected lift.\n"
            
    return decision, md
