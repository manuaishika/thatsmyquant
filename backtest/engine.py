import pandas as pd
import numpy as np

class PairsBacktest:
    def __init__(self, prices1, prices2, signals, initial_capital=100000, 
                 slippage=0.0005, commission=0.0005, max_leverage=2):
        self.prices1 = prices1
        self.prices2 = prices2
        self.signals = signals  # 1: long spread, -1: short spread, 0: flat
        self.capital = initial_capital
        self.slippage = slippage
        self.commission = commission
        self.max_leverage = max_leverage
        self.positions = []
        self.pnl = []
        self.trades = []

    def run(self):
        position = 0
        cash = self.capital
        for i in range(1, len(self.signals)):
            price1 = self.prices1[i]
            price2 = self.prices2[i]
            signal = self.signals[i]
            prev_signal = self.signals[i-1]
            trade = None

            # Enter/exit logic
            if signal != prev_signal:
                if signal != 0:
                    # Enter trade
                    size = cash * self.max_leverage / (abs(price1) + abs(price2))
                    entry1 = price1 * (1 + self.slippage)
                    entry2 = price2 * (1 + self.slippage)
                    position = signal * size
                    cash -= abs(position) * (entry1 + entry2) * self.commission
                    trade = {'type': 'entry', 'i': i, 'signal': signal, 'price1': entry1, 'price2': entry2, 'size': position}
                else:
                    # Exit trade
                    exit1 = price1 * (1 - self.slippage)
                    exit2 = price2 * (1 - self.slippage)
                    pnl = position * (exit1 - self.prices1[i-1]) - abs(position) * (exit1 + exit2) * self.commission
                    cash += abs(position) * (exit1 + exit2) + pnl
                    self.pnl.append(pnl)
                    trade = {'type': 'exit', 'i': i, 'signal': prev_signal, 'price1': exit1, 'price2': exit2, 'size': position, 'pnl': pnl}
                    position = 0
            self.positions.append(position)
            if trade:
                self.trades.append(trade)
        return pd.DataFrame(self.trades), pd.Series(self.pnl) 