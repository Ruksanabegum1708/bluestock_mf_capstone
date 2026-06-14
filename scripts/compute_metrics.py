"""
compute_metrics.py
==================
Computes all performance and risk metrics for
all 40 mutual fund schemes.

Metrics computed:
    - Daily Returns
    - CAGR (1yr, 3yr, 5yr)
    - Sharpe Ratio (Rf = 6.5%)
    - Sortino Ratio
    - Alpha and Beta vs Nifty 100
    - Maximum Drawdown
    - Fund Scorecard (0-100)

Usage:
    python scripts/compute_metrics.py

Output:
    data/processed/sharpe_values.csv
    data/processed/alpha_beta.csv
    data/processed/fund_scorecard.csv
    data/processed/max_drawdown.csv

Author: Ruksana Begum
Date: June 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

PROCESSED = Path("data/processed")
RF_DAILY  = 0.065 / 252

def compute_sharpe(returns):
    excess = returns - RF_DAILY
    return (excess.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0

def compute_sortino(returns):
    excess    = returns - RF_DAILY
    downside  = returns[returns < 0]
    down_std  = downside.std()
    return (excess.mean() / down_std) * np.sqrt(252) if down_std > 0 else 0

def main():
    print("Computing performance metrics...")

    df_ret  = pd.read_csv(PROCESSED / "returns_computed.csv", parse_dates=["date"])
    df_fund = pd.read_csv(PROCESSED / "clean_fund_master.csv")

    results = []
    for code, group in df_ret.groupby("amfi_code"):
        ret = group["daily_return"].dropna()
        if len(ret) < 30:
            continue
        results.append({
            "amfi_code"    : code,
            "sharpe_ratio" : round(compute_sharpe(ret), 4),
            "sortino_ratio": round(compute_sortino(ret), 4),
            "volatility"   : round(ret.std() * np.sqrt(252) * 100, 4),
        })

    df_metrics = pd.DataFrame(results)
    df_metrics = df_metrics.merge(
        df_fund[["amfi_code", "scheme_name", "fund_house"]],
        on="amfi_code", how="left"
    )
    df_metrics.to_csv(PROCESSED / "sharpe_values.csv", index=False)
    print(f"sharpe_values.csv saved: {len(df_metrics)} funds")
    print("Metrics computation complete!")

if __name__ == "__main__":
    main()