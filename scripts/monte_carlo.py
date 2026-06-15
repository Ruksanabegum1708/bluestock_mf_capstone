"""
monte_carlo.py - NAV Growth Projections
Bluestock Fintech Capstone — Bonus B3
Author: Ruksana Begum
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROCESSED = Path("data/processed")
REPORTS   = Path("reports")
REPORTS.mkdir(exist_ok=True)

def run_simulation(returns, current_nav, n_sim=500, n_days=1260):
    mean = returns.mean()
    std  = returns.std()
    results = []
    for _ in range(n_sim):
        prices = [current_nav]
        for _ in range(n_days):
            prices.append(prices[-1] * (1 + np.random.normal(mean, std)))
        results.append(prices)
    return np.array(results)

def main():
    df_ret  = pd.read_csv(PROCESSED / "returns_computed.csv", parse_dates=["date"])
    df_nav  = pd.read_csv(PROCESSED / "clean_nav_history.csv", parse_dates=["date"])
    df_fund = pd.read_csv(PROCESSED / "clean_fund_master.csv")

    top5 = (df_ret.groupby("amfi_code")["daily_return"]
            .count().nlargest(5).index.tolist())

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for i, code in enumerate(top5):
        ret = df_ret[df_ret["amfi_code"]==code]["daily_return"].dropna()
        nav = df_nav[df_nav["amfi_code"]==code]["nav"]
        if len(nav) == 0:
            continue
        current = nav.iloc[-1]
        name    = df_fund[df_fund["amfi_code"]==code]["scheme_name"].values
        name    = name[0][:28] if len(name) > 0 else str(code)

        sims = run_simulation(ret, current)
        days = np.arange(sims.shape[1])
        p5   = np.percentile(sims, 5,  axis=0)
        p50  = np.percentile(sims, 50, axis=0)
        p95  = np.percentile(sims, 95, axis=0)

        ax = axes[i]
        ax.fill_between(days, p5, p95, alpha=0.2, color="blue", label="5-95% band")
        ax.plot(days, p50, color="blue", linewidth=2, label="Median")
        ax.axhline(y=current, color="red", linestyle="--",
                   label=f"Current: Rs{current:.0f}")
        cagr = (p50[-1]/current)**(1/5) - 1
        ax.set_title(f"{name}", fontsize=10, fontweight="bold")
        ax.set_xlabel("Trading Days (5 Years)")
        ax.set_ylabel("NAV (Rs)")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.92,
                f"Median 5Y: Rs{p50[-1]:.0f}\nCAGR: {cagr*100:.1f}%",
                transform=ax.transAxes, fontsize=8,
                bbox=dict(boxstyle="round", facecolor="lightyellow"))

    axes[-1].set_visible(False)
    plt.suptitle("Monte Carlo Simulation — 5-Year NAV Projections (500 simulations)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = REPORTS / "chart_monte_carlo.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()