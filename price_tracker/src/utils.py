"""Utility helpers for reading/saving CSV and basic cleaning."""
import pandas as pd

def load_csv(path):
    return pd.read_csv(path)

def basic_clean(df, price_col="price"):
    df = df.copy()
    # drop rows without price
    if price_col in df.columns:
        df = df.dropna(subset=[price_col])
    # convert datetime if present
    if 'scrape_ts' in df.columns:
        df['scrape_ts'] = pd.to_datetime(df['scrape_ts'], errors='coerce')
    return df