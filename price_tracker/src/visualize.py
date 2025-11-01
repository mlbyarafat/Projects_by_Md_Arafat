"""Create simple trend visualizations from CSV data using Matplotlib & Plotly.
Usage:
    python src/visualize.py --csv data/sample_prices.csv --out figures/price_trends.png
"""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

def plot_matplotlib(df, out_path):
    df = df.sort_values('scrape_ts')
    plt.figure(figsize=(10,5))
    plt.plot(df['scrape_ts'], df['price'], marker='o')
    plt.title('Price over time')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    print(f"Saved matplotlib plot to {out_path}")

def plot_plotly(df, out_path):
    fig = px.line(df.sort_values('scrape_ts'), x='scrape_ts', y='price', title='Price over time')
    fig.write_html(out_path)
    print(f"Saved interactive plot to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    df = pd.read_csv(args.csv, parse_dates=['scrape_ts'])
    # basic aggregation: latest price per title
    df = df.dropna(subset=['price'])
    # Save a matplotlib PNG and a Plotly HTML
    plot_matplotlib(df, args.out)
    plot_plotly(df, args.out.replace('.png', '.html'))

if __name__ == "__main__":
    main()