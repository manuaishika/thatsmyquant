import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.graph_objects as go
import plotly.express as px
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="Pairs Trading Dashboard", layout="wide")

st.title("📈 Pairs Trading Backtest Dashboard")

# --- Multi-file Upload for Strategy Comparison ---
uploaded_files = st.file_uploader("Upload one or more backtest results (CSV)", type=["csv"], accept_multiple_files=True)

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

from evaluator.performance import evaluate_performance
import io
import contextlib

# --- Strategy Comparison ---
if uploaded_files and len(uploaded_files) > 1:
    st.header("Strategy Comparison Table")
    comparison_data = []
    for file in uploaded_files:
        trades = pd.read_csv(file)
        name = file.name
        pnl = trades['pnl'].dropna() if 'pnl' in trades.columns else pd.Series([])
        # Capture metrics
        with io.StringIO() as buf, contextlib.redirect_stdout(buf):
            evaluate_performance(trades, pnl)
            perf_output = buf.getvalue()
        # Parse metrics from output
        metrics = {}
        for line in perf_output.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                metrics[k.strip()] = v.strip()
        metrics['Strategy'] = name
        comparison_data.append(metrics)
    # Create DataFrame for comparison
    comp_df = pd.DataFrame(comparison_data).set_index('Strategy')
    st.dataframe(comp_df)
    st.stop()

# --- Single Strategy Mode (default or one file) ---
if uploaded_files:
    file = uploaded_files[0]
    trades = pd.read_csv(file)
    if {'price1', 'price2'}.issubset(trades.columns):
        prices = pd.DataFrame({
            'asset1': trades['price1'],
            'asset2': trades['price2']
        })
        spread_series = prices['asset1'] - prices['asset2']
    else:
        prices, spread_series, _, _ = load_sample_results()
    pnl = trades['pnl'].dropna() if 'pnl' in trades.columns else pd.Series([])
    st.success(f"Loaded backtest results: {file.name}")
else:
    prices, spread_series, trades, pnl = load_sample_results()

# --- Download Buttons ---
st.download_button(
    label="Download Trade Log as CSV",
    data=trades.to_csv(index=False),
    file_name="trade_log.csv",
    mime="text/csv"
)
if isinstance(pnl, pd.Series) and not pnl.empty:
    st.download_button(
        label="Download PnL as CSV",
        data=pnl.to_csv(index=False, header=True),
        file_name="pnl.csv",
        mime="text/csv"
    )

# Show metrics
st.header("Performance Metrics")
with io.StringIO() as buf, contextlib.redirect_stdout(buf):
    evaluate_performance(trades, pnl)
    perf_output = buf.getvalue()
st.code(perf_output, language="text")

# --- Advanced Visualizations ---
# Entry/Exit markers on price chart
st.header("Price Series with Entry/Exit Markers")
fig = go.Figure()
fig.add_trace(go.Scatter(x=prices.index, y=prices['asset1'], mode='lines', name='Asset 1'))
fig.add_trace(go.Scatter(x=prices.index, y=prices['asset2'], mode='lines', name='Asset 2'))

if 'i' in trades.columns and 'type' in trades.columns:
    entry_idx = trades[trades['type'] == 'entry']['i'].values
    exit_idx = trades[trades['type'] == 'exit']['i'].values
    # Markers for entries
    fig.add_trace(go.Scatter(
        x=prices.index[entry_idx],
        y=prices['asset1'].iloc[entry_idx],
        mode='markers',
        marker=dict(symbol='triangle-up', color='green', size=12),
        name='Entry'))
    # Markers for exits
    fig.add_trace(go.Scatter(
        x=prices.index[exit_idx],
        y=prices['asset1'].iloc[exit_idx],
        mode='markers',
        marker=dict(symbol='x', color='red', size=12),
        name='Exit'))
st.plotly_chart(fig, use_container_width=True)

# Cumulative PnL plot
st.header("Cumulative PnL")
if not pnl.empty:
    cum_pnl = pnl.cumsum()
    st.line_chart(cum_pnl)
else:
    st.info("No PnL data available for cumulative PnL plot.")

# Drawdown plot
st.header("Drawdown Curve")
if not pnl.empty:
    cum_pnl = pnl.cumsum()
    running_max = cum_pnl.cummax()
    drawdown = cum_pnl - running_max
    st.line_chart(drawdown)
else:
    st.info("No PnL data available for drawdown plot.")

# Show spread
st.header("Spread (Asset1 - Asset2)")
st.line_chart(spread_series)

# Show trade log
st.header("Trade Log")
st.dataframe(trades)

# Show PnL
st.header("Trade PnL")
st.bar_chart(pnl) 