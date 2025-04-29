import pandas as pd

def generate_signals(df, ticker1, ticker2, window=30, entry_z=1.0, exit_z=0.5):
    spread = df[ticker1] - df[ticker2]
    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()
    zscore = (spread - rolling_mean) / rolling_std

    df["spread"] = spread
    df["zscore"] = zscore
    df["long"] = zscore < -entry_z
    df["short"] = zscore > entry_z
    df["exit"] = zscore.abs() < exit_z

    return df
