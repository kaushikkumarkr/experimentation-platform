import argparse
import logging
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_to_postgres(file_path, table_name, db_url):
    """
    Loads CSV data into Postgres using pandas chunking.
    """
    engine = create_engine(db_url)
    
    logger.info(f"Loading {file_path} into {table_name}...")
    
    chunksize = 10000
    with pd.read_csv(file_path, chunksize=chunksize) as reader:
        for i, chunk in enumerate(reader):
            if_exists = 'replace' if i == 0 else 'append'
            chunk.to_sql(table_name, engine, schema='raw', if_exists=if_exists, index=False)
            if i % 10 == 0:
                logger.info(f"Processed chunk {i}...")
                
    logger.info("Load complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--table-name", required=True)
    parser.add_argument("--db-url", required=True)
    args = parser.parse_args()
    
    load_to_postgres(args.input_file, args.table_name, args.db_url)
