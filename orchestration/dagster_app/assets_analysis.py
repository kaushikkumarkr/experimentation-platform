from dagster import asset, Config
from sqlalchemy import create_engine
import pandas as pd
from analysis.ab_tests import calculate_ab_stats
from analysis.cuped import calculate_cuped_stats

class AnalysisConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def experiment_results_asset(config: AnalysisConfig, experiment_observations_mart):
    """
    Calculates A/B results for all experiments.
    """
    engine = create_engine(config.db_url)
    
    experiments = pd.read_sql("SELECT experiment_id FROM experimentation.experiment_registry", engine)
    
    results = []
    
    for _, row in experiments.iterrows():
        exp_id = row['experiment_id']
        df = pd.read_sql(f"SELECT * FROM experimentation.experiment_observations WHERE experiment_id = {exp_id}", engine)
        
        if df.empty:
            continue
            
        # Parse features for CUPED
        # df['features'] is list of dicts or None
        # We need to normalize it into columns f0..f11
        # Assumes df['features'] came from Postgres JSONB as dicts
        
        features_df = pd.json_normalize(df['features'])
        df_full = pd.concat([df, features_df], axis=1)
        
        # 1. Conversion (Binary)
        res_conv = calculate_ab_stats(df, 'outcome_conversion', metric_type='binary')
        res_conv['experiment_id'] = exp_id
        res_conv['segment'] = 'all'
        results.append(res_conv)
        
        # 2. Visits (Continuous)
        res_visit = calculate_ab_stats(df, 'outcome_visit', metric_type='continuous')
        res_visit['experiment_id'] = exp_id
        res_visit['segment'] = 'all'
        results.append(res_visit)
        
        # 3. CUPED on Conversion (using f0..f5 as proxies)
        # Note: CUPED on binary outcome is valid and often powerful (linear probability model)
        try:
            cuped_covariates = [c for c in features_df.columns if c.startswith('f')]
            if cuped_covariates:
                # Use first few features
                covariates = cuped_covariates[:6] 
                
                # We interpret 'outcome_conversion' as continuous for CUPED
                res_cuped = calculate_cuped_stats(df_full, 'outcome_conversion', covariates)
                res_cuped['experiment_id'] = exp_id
                res_cuped['segment'] = 'all'
                # Rename metric to indicate it's the cuped version
                res_cuped['metric_name'] = 'conversion_cuped' 
                results.append(res_cuped)
        except Exception as e:
            print(f"CUPED failed: {e}")
            
    if results:
        results_df = pd.DataFrame(results)
        # Select columns to match DB
        cols = ['experiment_id', 'metric_name', 'effect_estimate', 'ci_low', 'ci_high', 
                'p_value', 'method', 'segment']
        results_df = results_df[cols]
        
        results_df.to_sql('experiment_results', engine, schema='experimentation', if_exists='append', index=False)
        
    return f"Calculated {len(results)} metrics."
