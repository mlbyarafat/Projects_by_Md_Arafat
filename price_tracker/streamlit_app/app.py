
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os

# try to import project modules if present (use friendly fallbacks)
try:
    from src import visualize as visualize_mod  # type: ignore
except Exception:
    try:
        import sys
        sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
        import visualize as visualize_mod  # type: ignore
    except Exception:
        visualize_mod = None

st.set_page_config(page_title='Price Tracker — Client Ready', page_icon='💸', layout='wide')

# --- helper functions
def load_sample_data():
    sample = Path(__file__).resolve().parents[1] / 'data' / 'sample_prices.csv'
    if sample.exists():
        return pd.read_csv(sample)
    return pd.DataFrame()

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.strip()
    for col in ['date', 'Date', 'timestamp']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    for col in df.columns:
        if 'price' in col.lower() or 'amount' in col.lower():
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

with st.sidebar:
    st.title('Price Tracker')
    st.markdown('A polished client-ready demo of the Price Tracker project.')
    st.info('Upload a CSV with columns: product, price, date (optional).')
    st.divider()
    show_sample = st.checkbox('Load sample dataset', value=True)
    upload = st.file_uploader('Upload CSV', type=['csv'])
    st.divider()
    st.markdown('**Export**')
    st.download_button('Download sample CSV', data=load_sample_data().to_csv(index=False), file_name='sample_prices.csv', mime='text/csv')
    st.caption('Contact: you@yourcompany.com')

st.title('Price Tracker — Client-Ready Demo')
st.subheader('Clean UI • Better UX • Ready for handoff')

if upload is not None:
    try:
        df = pd.read_csv(upload)
        st.success('CSV loaded successfully')
    except Exception as e:
        st.error(f'Unable to read uploaded file: {e}')
        df = pd.DataFrame()
elif show_sample:
    df = load_sample_data()
else:
    df = pd.DataFrame()

if df.empty:
    st.warning('No data available. Please upload a CSV or enable the sample dataset in the sidebar.')
    st.stop()

df = clean_df(df)

with st.expander('Dataset preview & summary', expanded=True):
    st.write('**Preview (first 10 rows)**')
    st.dataframe(df.head(10), use_container_width=True)
    st.write('**Columns**: ' + ', '.join(df.columns.tolist()))
    st.write('**Basic stats**')
    st.write(df.describe(include='all'))

product_col = None
for col in df.columns:
    if col.lower() in ('product', 'item', 'name'):
        product_col = col
        break

price_col = None
for col in df.columns:
    if 'price' in col.lower() or 'amount' in col.lower():
        price_col = col
        break

date_col = None
for col in df.columns:
    if col.lower() in ('date', 'timestamp', 'time'):
        date_col = col
        break

if not price_col:
    st.error('Could not detect a price column. Please ensure your CSV contains a price or amount column.')
    st.stop()

if product_col:
    products = df[product_col].dropna().unique().tolist()
    selected = st.multiselect('Select product(s) to visualize', options=products, default=products[:3])
    plot_df = df[df[product_col].isin(selected)]
else:
    plot_df = df.copy()

if date_col and pd.api.types.is_datetime64_any_dtype(plot_df[date_col]):
    ts_df = plot_df.sort_values(by=date_col)
elif date_col:
    ts_df = plot_df.copy()
    ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors='coerce')
else:
    ts_df = plot_df.copy()
    ts_df['__pseudo_date__'] = pd.date_range(end=pd.Timestamp.now(), periods=len(ts_df))
    date_col = '__pseudo_date__'

agg_df = ts_df.groupby([date_col]).agg({price_col: ['mean', 'min', 'max']})
agg_df.columns = ['mean_price', 'min_price', 'max_price']
agg_df = agg_df.reset_index()

st.subheader('Price Trends')
fig = px.line(agg_df, x=date_col, y='mean_price', labels={'mean_price':'Average price', date_col:'Date'}, title='Average Price Over Time')
st.plotly_chart(fig, use_container_width=True)

st.subheader('Price Distribution')
fig2 = px.box(plot_df, y=price_col, points='suspectedoutliers', title='Price Distribution (boxplot)')
st.plotly_chart(fig2, use_container_width=True)

if visualize_mod is not None and hasattr(visualize_mod, 'advanced_plot'):
    try:
        st.subheader('Advanced analytics (project module)')
        advanced_fig = visualize_mod.advanced_plot(plot_df, price_col=price_col, date_col=date_col)
        st.plotly_chart(advanced_fig, use_container_width=True)
    except Exception as e:
        st.warning('Advanced plotting failed: ' + str(e))

st.markdown('---')
st.markdown('**Ready to present** — This package has been redesigned for clients: cleaned UI, exports, and clear documentation.')
