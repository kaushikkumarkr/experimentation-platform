from dagster import asset, Config
from sqlalchemy import create_engine, text
import pandas as pd
import json
from analysis.srm_checks import check_srm

class ChecksConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def experiment_health_checks_asset(config: ChecksConfig, experiment_observations_mart):
    """
    Runs SRM checks for all active experiments.
    """
    engine = create_engine(config.db_url)
    
    # 1. Get List of Experiments to Check
    experiments = pd.read_sql("SELECT experiment_id FROM experimentation.experiment_registry", engine)
    
    results = []
    
    for _, row in experiments.iterrows():
        exp_id = row['experiment_id']
        
        # 2. Get Data
        df = pd.read_sql(f"SELECT treatment FROM experimentation.experiment_observations WHERE experiment_id = {exp_id}", engine)
        
        # 3. Run Checks
        srm_result = check_srm(df)
        
        # 4. Save Record
        record = {
            'experiment_id': int(exp_id),
            'check_name': 'SRM',
            'status': srm_result['status'],
            'details': json.dumps(srm_result) # Store the whole result
        }
        
        results.append(record)
        
    # 5. Write to DB
    if results:
        results_df = pd.DataFrame(results)
        # Append to history
        results_df.to_sql('experiment_health_checks', engine, schema='experimentation', if_exists='append', index=False)
        
    return f"Ran checks for {len(results)} experiments."
