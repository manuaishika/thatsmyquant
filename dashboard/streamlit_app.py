import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Pairs Trading Dashboard", layout="wide")

st.title("📈 Pairs Trading Backtest Dashboard")

# Load sample data (from backtest/test_engine.py output)
def load_sample_results():
    # For demo, generate synthetic data
    n_days = 100
    np.random.seed(42)
    t = np.linspace(0, 10, n_days)
    base = 100 + 0.1 * t + np.random.normal(0, 1, n_days)
    spread = np.random.normal(0, 0.5, n_days)
    asset1 = base + spread
    asset2 = base - spread
    prices = pd.DataFrame({'asset1': asset1, 'asset2': asset2}, index=pd.date_range(start='2024-01-01', periods=n_days))
    spread_series = prices['asset1'] - prices['asset2']
    # Fake trades and PnL
    trades = pd.DataFrame({
        'type': ['entry', 'exit', 'entry', 'exit'],
        'i': [10, 11, 13, 14],
        'signal': [1, 1, -1, -1],
        'price1': [98.77, 99.53, 99.54, 98.22],
        'price2': [100.69, 99.55, 97.08, 98.41],
        'size': [1003.63, 1003.63, -3057.20, -3057.20],
        'pnl': [np.nan, 657.57, np.nan, 3152.04]
    })
    pnl = pd.Series([657.57, 3152.04])
    return prices, spread_series, trades, pnl

prices, spread_series, trades, pnl = load_sample_results()

# Show metrics
st.header("Performance Metrics")
from evaluator.performance import evaluate_performance
import io
import contextlib

# Capture printed output
with io.StringIO() as buf, contextlib.redirect_stdout(buf):
    evaluate_performance(trades, pnl)
    perf_output = buf.getvalue()
st.code(perf_output, language="text")

# Show price series
st.header("Price Series")
st.line_chart(prices)

# Show spread
st.header("Spread (Asset1 - Asset2)")
st.line_chart(spread_series)

# Show trade log
st.header("Trade Log")
st.dataframe(trades)

# Show PnL
st.header("Trade PnL")
st.bar_chart(pnl) 