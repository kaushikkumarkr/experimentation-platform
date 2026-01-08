from dagster import asset, Config
from sqlalchemy import create_engine, text
import pandas as pd
import json

class MartsConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def experiment_registry_seed(config: MartsConfig):
    """
    Seeds the registry with the Hillstrom experiment if not exists.
    """
    engine = create_engine(config.db_url)
    
    with engine.connect() as conn:
        # Check if exists
        res = conn.execute(text("SELECT experiment_id FROM experimentation.experiment_registry WHERE name = 'Hillstrom Mens Email'"))
        if res.fetchone():
            return "Experiment already exists."
        
        # Insert
        conn.execute(text("""
            INSERT INTO experimentation.experiment_registry 
            (name, description, start_date, status, primary_metric, hypothesis)
            VALUES 
            ('Hillstrom Mens Email', 'Testing effect of Mens Merchandise Email vs No Email on spend.', '2023-01-01', 'analyzed', 'outcome_conversion', 'Mens Email increases spend for men.')
        """))
        conn.commit()
    
    return "Seeded Hillstrom experiment."

@asset
def experiment_observations_mart(config: MartsConfig, raw_hillstrom, experiment_registry_seed):
    """
    Transforms raw Hillstrom data into the experiment_observations mart.
    Maps:
      - Treatment: 'Mens E-Mail' -> 1, 'No E-Mail' -> 0. (Excludes 'Womens E-Mail')
      - Outcome: conversion (spend > 0)
      - Features: recency, history, zip_code, newbie, channel
    """
    engine = create_engine(config.db_url)
    
    # 1. Fetch Experiment ID
    exp_id = pd.read_sql("SELECT experiment_id FROM experimentation.experiment_registry WHERE name = 'Hillstrom Mens Email'", engine).iloc[0]['experiment_id']
    
    # 2. Fetch Raw Data
    # Filter only Mens and Control
    df = pd.read_sql("SELECT * FROM raw.hillstrom WHERE segment IN ('Mens E-Mail', 'No E-Mail')", engine)
    
    if df.empty:
        return "No data found."
        
    # 3. Transform
    # Treatment
    df['treatment'] = df['segment'].apply(lambda x: 1 if x == 'Mens E-Mail' else 0)
    
    # Outcomes
    df['outcome_conversion'] = df['conversion']
    df['outcome_visit'] = df['visit']
    
    # Features (Pack into JSON)
    # Be sure to handle categorical variables if needed. 
    # For simplicity, we keep them as is in JSON, but typical Uplift models (S-Learner trees) handle numbers best.
    # We will One-Hot Encode categoricals for the Feature Vector
    
    # One-Hot Encoding for 'zip_code', 'channel'
    dummy_cols = ['zip_code', 'channel']
    df_dummies = pd.get_dummies(df[dummy_cols], prefix=dummy_cols, dtype=int)
    
    # Numeric features
    numeric_cols = ['recency', 'history', 'mens', 'womens', 'newbie']
    
    # Combine
    features_df = pd.concat([df[numeric_cols], df_dummies], axis=1)
    
    # Convert to list of dicts for JSONB
    df['features'] = features_df.to_dict(orient='records')
    df['features'] = df['features'].apply(json.dumps)
    
    # Unit ID (Synthetic)
    df['unit_id'] = df.index.astype(str) + '_user'
    df['experiment_id'] = int(exp_id)
    df['batch_date'] = '2023-01-01'
    
    # Select Columns
    mart_df = df[['experiment_id', 'unit_id', 'treatment', 'features', 'outcome_visit', 'outcome_conversion', 'batch_date']]
    
    # Load to Postgres
    mart_df.to_sql('experiment_observations', engine, schema='experimentation', if_exists='replace', index=False)
    
    return f"Transformed {len(mart_df)} rows into observations mart."
