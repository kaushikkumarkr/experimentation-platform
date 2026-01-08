from dagster import asset, Config
from sqlalchemy import create_engine, text
import pandas as pd
import json

class MartsConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def experiment_registry_seed(config: MartsConfig) -> str:
    """
    Seeds the registry with our Criteo Test Experiment.
    """
    engine = create_engine(config.db_url)
    
    # Check if exists
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM experimentation.experiment_registry WHERE name = 'Criteo Uplift Test'"))
        count = res.scalar()
        
        if count == 0:
            conn.execute(text("""
                INSERT INTO experimentation.experiment_registry 
                (name, owner, hypothesis, start_date, status, primary_metric)
                VALUES 
                ('Criteo Uplift Test', 'Data Science Team', 'Targeting high-uplift users will increase conversion.', '2023-01-01', 'analyzed', 'conversion')
            """))
            conn.commit()
            return "Seeded Registry"
        
    return "Registry Already Seeded"

@asset(deps=[experiment_registry_seed]) # Depend on registry existing
def experiment_observations_mart(context, config: MartsConfig, raw_criteo_uplift: str) -> str:
    """
    Transforms raw Criteo data into the Experiment Observations format.
    Assumes all raw data belongs to Experiment ID 1 (The Seeded Experiment).
    """
    engine = create_engine(config.db_url)
    
    # get experiment id
    with engine.connect() as conn:
        res = conn.execute(text("SELECT experiment_id FROM experimentation.experiment_registry WHERE name = 'Criteo Uplift Test'"))
        exp_id = res.scalar()
        
    if not exp_id:
        raise Exception("Experiment ID not found!")
    
    # Read Raw Data
    # In prod this would be incremental. Here we replace.
    df = pd.read_sql(f"SELECT * FROM raw.{raw_criteo_uplift}", engine)
    
    context.log.info(f"Transforming {len(df)} rows...")
    
    # Map to schema
    # raw: f0..f11, treatment, conversion, visit, exposure
    # target: experiment_id, unit_id (synthesized), treatment, features (json), outcome_visit, outcome_conversion
    
    # Synth Unit ID
    df['unit_id'] = df.index.astype(str) + "_user"
    df['experiment_id'] = exp_id
    df['outcome_conversion'] = df['conversion']
    df['outcome_visit'] = df['visit']
    df['batch_date'] = '2023-01-01'
    
    # Features to JSON
    feature_cols = [c for c in df.columns if c.startswith('f')]
    # This is slow for large dataframes, acceptable for 1M rows dev mode
    # For speed, we stick to columns or pre-optimized JSON gen.
    # df['features'] = df[feature_cols].apply(lambda x: x.to_json(), axis=1) 
    # Use to_dict -> json dumps for speed vectorization usually better but let's trust pandas for now or just avoid complex JSON if not needed.
    # Actually, Postgres JSONB from pandas dict is easy.
    
    # Let's just create a features dict column
    df['features'] = df[feature_cols].to_dict(orient='records')
    
    # Select final columns
    final_df = df[['experiment_id', 'unit_id', 'treatment', 'features', 'outcome_visit', 'outcome_conversion', 'batch_date']]
    
    # Write to Mart
    # We use 'replace' to be idempotent for this demo, in real life 'append' with limits.
    # Note: 'features' column (dict) needs to be handled by sqlalchemy dialect correctly as JSON. 
    # Pandas `to_sql` usually handles dicts as text or requires specific dtype=JSON.
    from sqlalchemy.types import JSON
    
    final_df.to_sql(
        'experiment_observations', 
        engine, 
        schema='experimentation', 
        if_exists='replace', 
        index=False,
        dtype={'features': JSON}
    )
    
    context.log.info("Mart Populated.")
    return "experimentation.experiment_observations"
