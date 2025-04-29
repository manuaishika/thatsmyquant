import yfinance as yf
import pandas as pd

def get_stock_data(ticker1, ticker2, start="2020-01-01", end="2023-12-31"):
    df1 = yf.download(ticker1, start=start, end=end)["Adj Close"]
    df2 = yf.download(ticker2, start=start, end=end)["Adj Close"]
    df = pd.DataFrame({ticker1: df1, ticker2: df2}).dropna()
    return df
