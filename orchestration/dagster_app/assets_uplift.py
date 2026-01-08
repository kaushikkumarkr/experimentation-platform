from dagster import asset, Config
from sqlalchemy import create_engine
import pandas as pd
from analysis.uplift_models import train_uplift_model

class UpliftConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def uplift_results_asset(config: UpliftConfig, experiment_observations_mart):
    """
    Trains uplift models for eligible experiments.
    """
    engine = create_engine(config.db_url)
    experiments = pd.read_sql("SELECT experiment_id FROM experimentation.experiment_registry", engine)
    
    results = []
    
    for _, row in experiments.iterrows():
        exp_id = row['experiment_id']
        
        # Read Data
        df = pd.read_sql(f"SELECT * FROM experimentation.experiment_observations WHERE experiment_id = {exp_id}", engine)
        if df.empty:
            continue

        # Parse Features
        features_df = pd.json_normalize(df['features'])
        df_full = pd.concat([df, features_df], axis=1)
        
        feature_cols = [c for c in features_df.columns if c.startswith('f')]
        
        if not feature_cols:
            continue
            
        # Train Class Transform
        try:
            res_ct = train_uplift_model(df_full, feature_cols, method='class_transform')
            res_ct['experiment_id'] = exp_id
            res_ct['uplift_auc'] = 0.0 # Placeholder for now
            results.append(res_ct)
            
            # Train Solo Model (S-Learner)
            res_solo = train_uplift_model(df_full, feature_cols, method='solo_model')
            res_solo['experiment_id'] = exp_id
            res_solo['uplift_auc'] = 0.0
            results.append(res_solo)
        except Exception as e:
            print(f"Uplift training failed: {e}")
            
    if results:
        results_df = pd.DataFrame(results)
        # Match schema: experiment_id, model_name, qini_auc, uplift_auc, expected_value_lift, targeting_fraction
        cols = ['experiment_id', 'model_name', 'qini_auc', 'uplift_auc', 'expected_value_lift', 'targeting_fraction']
        results_df = results_df[cols]
        results_df.to_sql('uplift_policy_results', engine, schema='experimentation', if_exists='append', index=False)
        
    return f"Trained {len(results)} uplift models."
