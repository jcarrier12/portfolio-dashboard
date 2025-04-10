import streamlit as st
st.set_page_config(page_title="Global Disruption Portfolio Dashboard", layout="wide")

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

""" Portfolio definition """
portfolio = {
    'RHM.DE': 0.07,
    '012450.KQ': 0.05,
    'HAG.DE': 0.04,
    'RTX': 0.05,
    'PLTR': 0.05,
    'XOM': 0.05,
    'VALE': 0.05,
    'MP': 0.05,
    'CCJ': 0.05,
    'NEM': 0.05,
    'TSM': 0.05,
    'TXN': 0.05,
    'INFY': 0.05,
    'CSU.TO': 0.05,
    'EWZ': 0.05,
    'EMLP': 0.05,
    'BTC-USD': 0.05,
    'TLT': 0.05
}

""" Sidebar settings """
st.sidebar.header("Settings")
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.now())
initial_capital = st.sidebar.number_input("Initial Investment ($)", min_value=1000, value=10000, step=500)
refresh_interval = st.sidebar.slider("Auto-Refresh Interval (seconds)", min_value=10, max_value=300, value=30, step=10)

""" Fetch price data """
@st.cache_data
def get_data(tickers, start, end):
    return yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)

tickers = list(portfolio.keys()) + ['^GSPC']
data = get_data(tickers, start_date, end_date)

""" Weight filtering """
valid_tickers = [ticker for ticker in portfolio if ticker in data.columns.levels[0]]
weights = {ticker: portfolio[ticker] for ticker in valid_tickers}
weights = {k: v / sum(weights.values()) for k, v in weights.items()}

""" Calculate performance """
returns = pd.DataFrame({ticker: data[ticker]['Close'].pct_change() for ticker in weights}).fillna(0)
portfolio_returns = (returns * pd.Series(weights)).sum(axis=1)
portfolio_cum = (1 + portfolio_returns).cumprod()
portfolio_value = portfolio_cum * initial_capital

sp500_returns = data['^GSPC']['Close'].pct_change().fillna(0)
sp500_cum = (1 + sp500_returns).cumprod()
sp500_value = sp500_cum * initial_capital

""" Performance chart """
st.subheader("Portfolio vs. S&P 500 Performance")
st.line_chart(pd.DataFrame({
    'Portfolio ($)': portfolio_value,
    'S&P 500 ($)': sp500_value
}))

""" Stats """
st.subheader("Performance Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Portfolio Return (%)", f"{(portfolio_cum[-1] - 1) * 100:.2f}")
col2.metric("S&P 500 Return (%)", f"{(sp500_cum[-1] - 1) * 100:.2f}")
col3.metric("Portfolio Value ($)", f"{portfolio_value[-1]:,.2f}")

""" Auto-refresh every X seconds using meta tag """
st.markdown(f"""
    <meta http-equiv="refresh" content="{int(refresh_interval)}">
""", unsafe_allow_html=True)