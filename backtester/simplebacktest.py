def run_backtest(df):
    position = 0
    pnl = []

    for i in range(len(df)):
        if df["long"].iloc[i]:
            position = 1
        elif df["short"].iloc[i]:
            position = -1
        elif df["exit"].iloc[i]:
            position = 0
        pnl.append(position * df["spread"].diff().fillna(0).iloc[i])

    df["PnL"] = pnl
    df["Cum_PnL"] = df["PnL"].cumsum()
    return df
