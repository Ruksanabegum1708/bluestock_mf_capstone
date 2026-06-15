"""
efficient_frontier.py - Portfolio Optimisation
Bluestock Fintech Capstone — Bonus B4
Author: Ruksana Begum
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from pathlib import Path

PROCESSED = Path("data/processed")
REPORTS   = Path("reports")
REPORTS.mkdir(exist_ok=True)
RF = 0.065

def portfolio_stats(weights, mean_ret, cov):
    ret = np.sum(mean_ret * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov * 252, weights)))
    return ret, std

def neg_sharpe(weights, mean_ret, cov):
    r, s = portfolio_stats(weights, mean_ret, cov)
    return -(r - RF) / s

def main():
    df_ret  = pd.read_csv(PROCESSED / "returns_computed.csv", parse_dates=["date"])
    df_fund = pd.read_csv(PROCESSED / "clean_fund_master.csv")

    equity = df_fund[df_fund["category"]=="Large Cap"]["amfi_code"].head(5).tolist()
    if not equity:
        equity = df_fund["amfi_code"].head(5).tolist()

    pivot = (df_ret[df_ret["amfi_code"].isin(equity)]
             .pivot_table(index="date", columns="amfi_code",
                          values="daily_return").dropna())

    if pivot.shape[1] < 2:
        print("Not enough funds! Using all available funds.")
        equity = df_ret["amfi_code"].unique()[:5].tolist()
        pivot  = (df_ret[df_ret["amfi_code"].isin(equity)]
                  .pivot_table(index="date", columns="amfi_code",
                               values="daily_return").dropna())

    mean_ret = pivot.mean()
    cov      = pivot.cov()
    n        = len(mean_ret)

    results  = np.zeros((3, 5000))
    for i in range(5000):
        w = np.random.random(n)
        w = w / w.sum()
        r, s = portfolio_stats(w, mean_ret, cov)
        results[0,i] = s
        results[1,i] = r
        results[2,i] = (r - RF) / s

    bounds  = tuple((0,1) for _ in range(n))
    cons    = ({"type":"eq","fun":lambda x: x.sum()-1},)
    opt     = minimize(neg_sharpe, [1/n]*n,
                       args=(mean_ret, cov),
                       method="SLSQP",
                       bounds=bounds, constraints=cons)
    opt_r, opt_s = portfolio_stats(opt.x, mean_ret, cov)
    opt_sharpe   = (opt_r - RF) / opt_s

    fig, ax = plt.subplots(figsize=(12, 8))
    sc = ax.scatter(results[0]*100, results[1]*100,
                    c=results[2], cmap="viridis", alpha=0.5, s=10)
    plt.colorbar(sc, label="Sharpe Ratio")
    ax.scatter(opt_s*100, opt_r*100,
               marker="*", color="red", s=400, zorder=5,
               label=f"Max Sharpe\nReturn:{opt_r*100:.1f}% Risk:{opt_s*100:.1f}% Sharpe:{opt_sharpe:.2f}")
    ax.set_xlabel("Risk / Std Dev (%)", fontsize=12)
    ax.set_ylabel("Expected Return (%)", fontsize=12)
    ax.set_title("Markowitz Efficient Frontier — 5 Large Cap Funds",
                 fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = REPORTS / "chart_efficient_frontier.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.show()

    print("\nOptimal Portfolio (Max Sharpe):")
    names = [df_fund[df_fund["amfi_code"]==c]["scheme_name"].values[0][:25]
             if len(df_fund[df_fund["amfi_code"]==c]) > 0 else str(c)
             for c in pivot.columns]
    for name, w in zip(names, opt.x):
        print(f"  {name:<30} {w*100:.1f}%")
    print(f"Expected Return : {opt_r*100:.2f}%")
    print(f"Expected Risk   : {opt_s*100:.2f}%")
    print(f"Sharpe Ratio    : {opt_sharpe:.4f}")
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()