from dagster import asset, Config
from sqlalchemy import create_engine
import pandas as pd
import os
from analysis.decision_report import generate_decision_report

class ReportingConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def decision_report_asset(config: ReportingConfig, experiment_results_asset, experiment_health_checks_asset):
    """
    Generates unified decision reports.
    """
    engine = create_engine(config.db_url)
    experiments = pd.read_sql("SELECT experiment_id FROM experimentation.experiment_registry", engine)
    
    os.makedirs("reports", exist_ok=True)
    
    results = []
    
    for _, row in experiments.iterrows():
        exp_id = row['experiment_id']
        
        try:
            decision, md_content = generate_decision_report(exp_id, engine)
            
            # Save to DB
            results.append({
                'experiment_id': exp_id,
                'decision': decision,
                'rationale_markdown': md_content,
                'risks_and_guardrails': "Check secondary metrics.",
                'next_steps': "Review with stakeholders."
            })
            
            # Save to file
            with open(f"reports/experiment_{exp_id}_report.md", "w") as f:
                f.write(md_content)
                
        except Exception as e:
            print(f"Reporting failed for {exp_id}: {e}")
            
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_sql('decision_reports', engine, schema='experimentation', if_exists='append', index=False)
        
    return f"Generated {len(results)} reports."
