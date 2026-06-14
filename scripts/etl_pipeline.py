"""
etl_pipeline.py
===============
Master ETL Pipeline for Bluestock MF Capstone Project.

Runs complete data pipeline:
1. Load all 10 CSV datasets
2. Clean and validate data
3. Load into SQLite database

Usage:
    python scripts/etl_pipeline.py

Author: Ruksana Begum
Date: June 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

RAW       = Path("data/raw")
PROCESSED = Path("data/processed")
DB_PATH   = Path("data/db/bluestock_mf.db")

PROCESSED.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_raw_data():
    log.info("Loading raw CSV files...")
    files = {
        "fund_master":   "01_fund_master.csv",
        "nav_history":   "02_nav_history.csv",
        "transactions":  "08_investor_transactions.csv",
        "performance":   "07_scheme_performance.csv",
        "aum":           "03_aum_by_fund_house.csv",
    }
    dfs = {}
    for name, fname in files.items():
        path = RAW / fname
        if path.exists():
            dfs[name] = pd.read_csv(path, low_memory=False)
            log.info(f"  Loaded {fname}: {dfs[name].shape}")
        else:
            log.warning(f"  NOT FOUND: {fname}")
    return dfs

def clean_nav(df):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(["amfi_code", "date"])
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["nav"] = df.groupby("amfi_code")["nav"].ffill()
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    df = df[df["nav"] > 0]
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    return df

def clean_transactions(df):
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    df = df[df["amount_inr"] > 0]
    df = df.drop_duplicates()
    return df

def load_to_sqlite(dfs):
    engine = create_engine(f"sqlite:///{DB_PATH}")
    table_map = {
        "fund_master":  "dim_fund",
        "nav_history":  "fact_nav",
        "transactions": "fact_transactions",
        "performance":  "fact_performance",
        "aum":          "fact_aum",
    }
    for key, table in table_map.items():
        if key in dfs:
            dfs[key].to_sql(table, engine, if_exists="replace", index=False)
            log.info(f"  Loaded {table}: {len(dfs[key]):,} rows")

def main():
    log.info("=" * 50)
    log.info("Bluestock MF ETL Pipeline Starting...")
    log.info("=" * 50)

    dfs = load_raw_data()

    if "nav_history" in dfs:
        dfs["nav_history"] = clean_nav(dfs["nav_history"])
        dfs["nav_history"].to_csv(PROCESSED / "clean_nav_history.csv", index=False)
        log.info("NAV history cleaned and saved!")

    if "transactions" in dfs:
        dfs["transactions"] = clean_transactions(dfs["transactions"])
        dfs["transactions"].to_csv(PROCESSED / "clean_investor_transactions.csv", index=False)
        log.info("Transactions cleaned and saved!")

    load_to_sqlite(dfs)

    log.info("=" * 50)
    log.info("ETL Pipeline Complete!")
    log.info(f"Database: {DB_PATH}")
    log.info("=" * 50)

if __name__ == "__main__":
    main()