"""
recommender.py
==============
Simple Fund Recommender System for Bluestock MF Capstone.

Takes investor risk appetite as input and recommends
top 3 mutual funds based on Sharpe ratio within the
matching risk category.

Risk Appetite Options:
    - Low      → Liquid and Gilt funds
    - Moderate → Large Cap and Flexi Cap funds
    - High     → Small Cap and Mid Cap funds

Usage:
    python scripts/recommender.py

Author: Ruksana Begum
Date: June 2026
Company: Bluestock Fintech Pvt. Ltd.
"""

import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")

df_sharpe = pd.read_csv(PROCESSED / "sharpe_values.csv")
df_fund   = pd.read_csv(PROCESSED / "clean_fund_master.csv")

df_rec = df_sharpe.merge(
    df_fund[["amfi_code", "scheme_name", "fund_house",
             "risk_category", "expense_ratio_pct", "category"]],
    on="amfi_code", how="left"
)

def recommend_funds(risk_appetite, top_n=3):
    risk_map = {
        "Low"      : ["Low", "Moderately Low"],
        "Moderate" : ["Moderate", "Moderately High"],
        "High"     : ["High", "Very High"]
    }
    valid_grades = risk_map.get(risk_appetite, ["Moderate"])
    filtered = df_rec[df_rec["risk_category"].isin(valid_grades)]
    top = filtered.nlargest(top_n, "sharpe_ratio")
    return top[["scheme_name", "fund_house", "sharpe_ratio",
                "risk_category", "expense_ratio_pct"]]

if __name__ == "__main__":
    print("FUND RECOMMENDER SYSTEM")
    print("=" * 50)
    appetite = input("Enter risk appetite (Low/Moderate/High): ")
    result = recommend_funds(appetite)
    print(result.to_string(index=False))
