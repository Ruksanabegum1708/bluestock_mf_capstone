
Data Dictionary — Bluestock MF Capstone

01_fund_master.csv / dim_fund
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT | Unique AMFI scheme code |
| fund_house | TEXT | AMC name |
| scheme_name | TEXT | Full scheme name |
| category | TEXT | Equity / Debt / Hybrid |
| sub_category | TEXT | Large Cap / Mid Cap etc. |
| expense_ratio_pct | REAL | Annual expense ratio % |
| risk_category | TEXT | Low / Moderate / High |
| fund_manager | TEXT | Primary fund manager |

02_nav_history.csv / fact_nav
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT | Foreign key to dim_fund |
| date | DATE | NAV date (business days) |
| nav | REAL | NAV value in Rs. |
| daily_return_pct | REAL | Daily return % |

08_investor_transactions.csv / fact_transactions
| Column | Type | Description |
|---|---|---|
| investor_id | TEXT | Unique investor ID |
| transaction_date | DATE | Date of transaction |
| amfi_code | TEXT | Fund invested in |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | REAL | Amount in Rs. |
| state | TEXT | Investor state |
| city_tier | TEXT | T30 or B30 |
| age_group | TEXT | 18-25 / 26-35 etc. |
| kyc_status | TEXT | Verified / Pending |

07_scheme_performance.csv / fact_performance
| Column | Type | Description |
|---|---|---|
| amfi_code | TEXT | Foreign key to dim_fund |
| return_1yr_pct | REAL | 1 year return % |
| return_3yr_pct | REAL | 3 year CAGR % |
| return_5yr_pct | REAL | 5 year CAGR % |
| sharpe_ratio | REAL | Risk adjusted return |
| alpha | REAL | Excess return vs benchmark |
| beta | REAL | Market sensitivity |
| max_drawdown_pct | REAL | Worst peak to trough % |
