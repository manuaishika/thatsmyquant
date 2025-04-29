import matplotlib.pyplot as plt

def plot_zscore(df):
    plt.figure(figsize=(12,6))
    df["zscore"].plot()
    plt.axhline(1, color='red', linestyle='--')
    plt.axhline(-1, color='green', linestyle='--')
    plt.axhline(0, color='black', linestyle='-')
    plt.title("Z-Score Spread")
    plt.grid()
    plt.show()

def plot_pnl(df):
    df["Cum_PnL"].plot(figsize=(12,6), title="Cumulative PnL")
    plt.grid()
    plt.show()
