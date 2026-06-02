import pandas as pd

files = [
    "data/raw/01_fund_master.csv",
    "data/raw/02_nav_history.csv",
    "data/raw/03_aum_by_fund_house.csv",
    "data/raw/04_monthly_sip_inflows.csv",
    "data/raw/05_category_inflows.csv",
    "data/raw/06_industry_folio_count.csv",
    "data/raw/07_scheme_performance.csv",
    "data/raw/08_investor_transactions.csv",
    "data/raw/09_portfolio_holdings.csv",
    "data/raw/10_benchmark_indices.csv"
]

for file in files:
    print("\n==============================")
    print("File:", file)
    print("==============================")

    df = pd.read_csv(file)

    print("Shape:", df.shape)
    print("\nData Types:\n", df.dtypes)
    print("\nFirst 5 rows:\n", df.head())