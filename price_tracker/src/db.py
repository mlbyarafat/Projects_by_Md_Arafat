"""Simple CSV-based storage helpers (could be swapped for SQLite/Postgres)."""
import pandas as pd
import os

def append_to_csv(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df_new = pd.DataFrame(rows)
    if os.path.exists(path):
        df_old = pd.read_csv(path)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(path, index=False)
    return df
