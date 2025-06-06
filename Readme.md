A sophisticated quantitative trading system for pairs trading, featuring dynamic pair detection, backtesting, and execution simulation.

## Project Structure

```
quant-system/
│
├── data/
│   ├── fetch.py             → Bulk data fetching (S&P 500 tickers)
│   ├── preprocessing.py     → Handle missing values, align dates, etc.
│
├── research/
│   ├── pairs_scanner.py     → Auto-find cointegrated pairs
│   ├── spread_model.py      → Dynamic hedge ratio, Kalman Filter
│   └── strategy.py          → Z-score + regime switching + volatility filter
│
├── backtest/
│   ├── engine.py            → Realistic backtest (slippage, fees)
│   ├── evaluator.py         → Sharpe, drawdown, win/loss ratio, etc.
│
├── execution/
│   └── mock_broker.py       → Simulated broker (or Alpaca integration)
│
├── dashboard/
│   └── streamlit_app.py     → Visual dashboard to explore results
│
├── models/
│   └── kalman_filter.py     → Estimate dynamic hedge ratio
│
├── notebooks/
│   └── exploration.ipynb    → For experiments + sanity checks
│
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd quant-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Streamlit:
```bash
pip install streamlit
```

## Current Stage: Stage 1 - Pair Scanner

The current implementation includes:
- S&P 500 data fetching using yfinance
- Cointegration testing for pair detection
- Parallel processing for efficient pair scanning

### Usage

1. Fetch S&P 500 data:
```python
from data.fetch import get_sp500_symbols, fetch_stock_data

# Get S&P 500 symbols
symbols = get_sp500_symbols()

# Fetch historical data
data = fetch_stock_data(symbols)
```

2. Find cointegrated pairs:
```python
from research.pairs_scanner import find_cointegrated_pairs

# Convert to price DataFrame
prices = pd.DataFrame({symbol: df['Close'] for symbol, df in data.items()})

# Find cointegrated pairs
pairs = find_cointegrated_pairs(prices)
```

## Next Steps

1. Implement Kalman Filter for dynamic hedge ratio estimation
2. Build realistic backtesting engine
3. Create Streamlit dashboard
4. Add ML-based spread prediction
5. Implement auto hyperparameter tuning

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


