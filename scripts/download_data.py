import argparse
import logging
import os
import pandas as pd
import numpy as np
import requests
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OFFICIAL_URL = "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"

def generate_synthetic_hillstrom(output_path, N=100000):
    """Generates synthetic data matching Hillstrom schema."""
    logger.warning("Generating SYNTHETIC Hillstrom data (Dev Mode).")
    
    np.random.seed(42)
    
    df = pd.DataFrame()
    df['recency'] = np.random.randint(1, 13, N)
    df['history_segment'] = np.random.choice(['1) $0 - $100', '2) $100 - $200', '3) $200 - $350', '4) $350 - $500', '5) $500 - $750', '6) $750 - $1,000', '7) $1,000 +'], N)
    df['history'] = np.random.gamma(50, 5, N)
    df['mens'] = np.random.choice([0, 1], N)
    df['womens'] = np.random.choice([0, 1], N)
    df['zip_code'] = np.random.choice(['Urban', 'Suburban', 'Rural'], N)
    df['newbie'] = np.random.choice([0, 1], N)
    df['channel'] = np.random.choice(['Web', 'Phone', 'Multichannel'], N)
    
    # Treatment
    df['segment'] = np.random.choice(['Mens E-Mail', 'Womens E-Mail', 'No E-Mail'], N)
    
    # Outcome Logic (Signal)
    # Mens E-Mail increases visit/conversion for men (mens=1)
    base_visit_prob = 0.1
    visit_lift = 0.05
    
    def get_visit_prob(row):
        prob = base_visit_prob
        if row['segment'] == 'Mens E-Mail' and row['mens'] == 1:
            prob += visit_lift
        if row['segment'] == 'Womens E-Mail' and row['womens'] == 1:
            prob += visit_lift
        return prob

    visit_probs = df.apply(get_visit_prob, axis=1)
    df['visit'] = np.random.binomial(1, visit_probs)
    
    df['conversion'] = df['visit'] * np.random.binomial(1, 0.3, N) # 30% conversion given visit
    df['spend'] = df['conversion'] * np.random.exponential(100, N)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Saved synthetic data to {output_path}")

def download_data(output_path: str):
    logger.info("Attempting to download Hillstrom dataset...")
    
    try:
        # Try Official URL
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(OFFICIAL_URL, headers=headers, timeout=10)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        
        logger.info(f"Downloaded {len(df)} rows from official source.")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
    except Exception as e:
        logger.error(f"Download failed: {e}. Falling back to synthetic.")
        generate_synthetic_hillstrom(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--sample-size", type=int, default=100000)
    args = parser.parse_args()
    
    download_data(args.output_path)
