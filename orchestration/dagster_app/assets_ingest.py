from dagster import asset, Config
import subprocess

import pandas as pd
from sqlalchemy import create_engine

class IngestConfig(Config):
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"
    input_file: str = "data/hillstrom.csv"

@asset
def hillstrom_data_file():
    """
    Downloads the Hillstrom Email Marketing dataset.
    """
    output_path = "data/hillstrom.csv"
    script_path = "scripts/download_data.py"
    
    # Run the script
    subprocess.run(["python3", script_path, "--output-path", output_path], check=True)
    
    return output_path

@asset
def raw_hillstrom(config: IngestConfig, hillstrom_data_file):
    """
    Loads Hillstrom CSV into Postgres raw.hillstrom table.
    """
    engine = create_engine(config.db_url)
    
    # Read CSV
    # Chunking is good practice even if file is small
    chunksize = 10000
    table_name = "hillstrom"
    schema = "raw"
    
    # Drop and recreate handled by pandas replace? 
    # Actually better to append chunk by chunk, so we truncate first.
    # But for simplicity in this asset, 'replace' on first chunk, 'append' on rest.
    
    first_chunk = True
    for chunk in pd.read_csv(hillstrom_data_file, chunksize=chunksize):
        if first_chunk:
            chunk.to_sql(table_name, engine, schema=schema, if_exists='replace', index=False)
            first_chunk = False
        else:
            chunk.to_sql(table_name, engine, schema=schema, if_exists='append', index=False)
            
    return f"Loaded data to {schema}.{table_name}"
