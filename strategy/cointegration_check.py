from statsmodels.tsa.stattools import coint

def check_cointegration(series1, series2):
    score, pvalue, _ = coint(series1, series2)
    return pvalue < 0.05, pvalue
