import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.graph_objects as go
import plotly.express as px
import streamlit_authenticator as stauth
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- User Authentication Setup ---
import yaml
from yaml.loader import SafeLoader

# Demo user credentials (hashed passwords for 'demo' and 'test')
usernames = ['demo', 'test']
passwords = stauth.Hasher(['demo', 'test']).generate()

config = {
    'credentials': {
        'usernames': {
            usernames[0]: {
                'name': 'Demo User',
                'password': passwords[0],
                'email': 'demo@example.com'
            },
            usernames[1]: {
                'name': 'Test User',
                'password': passwords[1],
                'email': 'test@example.com'
            }
        }
    },
    'cookie': {
        'expiry_days': 1,
        'key': 'some_signature_key',
        'name': 'auth_cookie'
    },
    'preauthorized': {
        'emails': ["demo@example.com", "test@example.com"]
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
else:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Logged in as: {name} ({username})')

    st.set_page_config(page_title="Pairs Trading Dashboard", layout="wide")
    st.title("📈 Pairs Trading Backtest Dashboard")

    # --- Sidebar for file upload and downloads ---
    st.sidebar.header("Upload & Download")
    uploaded_files = st.sidebar.file_uploader("Upload one or more backtest results (CSV)", type=["csv"], accept_multiple_files=True)

    # Load sample data (from backtest/test_engine.py output)
    def load_sample_results():
        n_days = 100
        np.random.seed(42)
        t = np.linspace(0, 10, n_days)
        base = 100 + 0.1 * t + np.random.normal(0, 1, n_days)
        spread = np.random.normal(0, 0.5, n_days)
        asset1 = base + spread
        asset2 = base - spread
        prices = pd.DataFrame({'asset1': asset1, 'asset2': asset2}, index=pd.date_range(start='2024-01-01', periods=n_days))
        spread_series = prices['asset1'] - prices['asset2']
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
        st.sidebar.success(f"Loaded backtest results: {file.name}")
    else:
        prices, spread_series, trades, pnl = load_sample_results()

    # --- Download Buttons ---
    st.sidebar.download_button(
        label="Download Trade Log as CSV",
        data=trades.to_csv(index=False),
        file_name="trade_log.csv",
        mime="text/csv"
    )
    if isinstance(pnl, pd.Series) and not pnl.empty:
        st.sidebar.download_button(
            label="Download PnL as CSV",
            data=pnl.to_csv(index=False, header=True),
            file_name="pnl.csv",
            mime="text/csv"
        )

    # --- Summary Metric Cards ---
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        evaluate_performance(trades, pnl)
        perf_output = buf.getvalue()

    # Parse metrics for cards
    metrics = {}
    for line in perf_output.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            metrics[k.strip()] = v.strip()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Return", metrics.get("Total Return", "-"))
    col2.metric("Sharpe Ratio", metrics.get("Sharpe Ratio", "-"))
    col3.metric("Max Drawdown", metrics.get("Maximum Drawdown", "-"))
    col4.metric("Win Rate", metrics.get("Win Rate", "-"))

    # --- Date Range Selector ---
    min_date = prices.index.min()
    max_date = prices.index.max()
    def_date = (min_date, max_date)
    date_range = st.sidebar.date_input(
        "Select date range",
        value=def_date,
        min_value=min_date,
        max_value=max_date
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        mask = (prices.index >= pd.to_datetime(start_date)) & (prices.index <= pd.to_datetime(end_date))
        prices = prices.loc[mask]
        spread_series = spread_series.loc[mask]
        # Filter trades and pnl if possible
        if 'i' in trades.columns:
            valid_idx = prices.index
            trades = trades[trades['i'].apply(lambda x: x in range(len(valid_idx)))]
        if not pnl.empty and len(pnl) == len(valid_idx):
            pnl = pnl.iloc[:len(valid_idx)]

    # --- Tabbed Layout ---
    tabs = st.tabs(["Overview", "Visualizations", "Trades", "Comparison"])

    with tabs[0]:
        st.subheader("Overview")
        st.code(perf_output, language="text")

    with tabs[1]:
        st.subheader("Advanced Visualizations")
        # Entry/Exit markers on price chart
        st.markdown("**Price Series with Entry/Exit Markers**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices.index, y=prices['asset1'], mode='lines', name='Asset 1'))
        fig.add_trace(go.Scatter(x=prices.index, y=prices['asset2'], mode='lines', name='Asset 2'))
        if 'i' in trades.columns and 'type' in trades.columns:
            entry_idx = trades[trades['type'] == 'entry']['i'].values
            exit_idx = trades[trades['type'] == 'exit']['i'].values
            fig.add_trace(go.Scatter(
                x=prices.index[entry_idx],
                y=prices['asset1'].iloc[entry_idx],
                mode='markers',
                marker=dict(symbol='triangle-up', color='green', size=12),
                name='Entry'))
            fig.add_trace(go.Scatter(
                x=prices.index[exit_idx],
                y=prices['asset1'].iloc[exit_idx],
                mode='markers',
                marker=dict(symbol='x', color='red', size=12),
                name='Exit'))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("**Cumulative PnL**")
        if not pnl.empty:
            cum_pnl = pnl.cumsum()
            st.line_chart(cum_pnl)
        else:
            st.info("No PnL data available for cumulative PnL plot.")
        st.markdown("**Drawdown Curve**")
        if not pnl.empty:
            cum_pnl = pnl.cumsum()
            running_max = cum_pnl.cummax()
            drawdown = cum_pnl - running_max
            st.line_chart(drawdown)
        else:
            st.info("No PnL data available for drawdown plot.")
        st.markdown("**Spread (Asset1 - Asset2)**")
        st.line_chart(spread_series)

    with tabs[2]:
        st.subheader("Trade Log")
        st.dataframe(trades)
        st.markdown("**Trade PnL**")
        st.bar_chart(pnl)

    with tabs[3]:
        st.subheader("Strategy Comparison Info")
        st.write("Upload multiple files in the sidebar to compare strategies.") 