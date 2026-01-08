from dagster import asset, Config
import os
import subprocess

class IngestConfig(Config):
    sample_size: int = 100000
    db_url: str = "postgresql://postgres:postgres@localhost:5432/experimentation_db"

@asset
def criteo_data_file(config: IngestConfig) -> str:
    """
    Downloads/Generates Criteo data and returns the path.
    """
    output_path = "data/criteo_sample.csv"
    cmd = [
        "python3", "scripts/download_data.py",
        "--output-path", output_path,
        "--sample-size", str(config.sample_size)
    ]
    subprocess.check_call(cmd)
    return os.path.abspath(output_path)

@asset
def raw_criteo_uplift(context, config: IngestConfig, criteo_data_file: str) -> str:
    """
    Loads Criteo data into Postgres.
    """
    table_name = "criteo_uplift"
    cmd = [
        "python3", "scripts/load_to_postgres.py",
        "--input-file", criteo_data_file,
        "--table-name", table_name,
        "--db-url", config.db_url
    ]
    subprocess.check_call(cmd)
    context.log.info(f"Loaded data to raw.{table_name}")
    return table_name
