# Example commands to run locally after installing requirements
python src/scrapers/bs_scraper.py
python src/visualize.py --csv data/sample_prices.csv --out figures/price_trends.png
streamlit run streamlit_app/app.py --server.port 8501
