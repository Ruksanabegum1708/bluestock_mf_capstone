
-- dim_fund
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code       TEXT PRIMARY KEY,
    fund_house      TEXT,
    scheme_name     TEXT,
    category        TEXT,
    sub_category    TEXT,
    plan            TEXT,
    benchmark       TEXT,
    expense_ratio_pct REAL,
    risk_category   TEXT,
    fund_manager    TEXT
);

-- dim_date
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,
    year        INTEGER,
    month       INTEGER,
    quarter     INTEGER,
    month_name  TEXT,
    is_weekday  INTEGER
);

-- fact_nav
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       TEXT REFERENCES dim_fund(amfi_code),
    date            TEXT,
    nav             REAL,
    daily_return_pct REAL
);

-- fact_transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id     TEXT,
    amfi_code       TEXT REFERENCES dim_fund(amfi_code),
    transaction_date TEXT,
    transaction_type TEXT,
    amount_inr      REAL,
    state           TEXT,
    city_tier       TEXT,
    age_group       TEXT,
    gender          TEXT,
    kyc_status      TEXT
);

-- fact_performance
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code       TEXT REFERENCES dim_fund(amfi_code),
    return_1yr_pct  REAL,
    return_3yr_pct  REAL,
    return_5yr_pct  REAL,
    sharpe_ratio    REAL,
    sortino_ratio   REAL,
    alpha           REAL,
    beta            REAL,
    max_drawdown_pct REAL
);

-- fact_aum
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house  TEXT,
    quarter     TEXT,
    aum_crore   REAL
);
