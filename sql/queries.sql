-- Q1 — Top 5 funds by expense ratio
SELECT scheme_name, fund_house, expense_ratio_pct
        FROM dim_fund
        ORDER BY expense_ratio_pct DESC
        LIMIT 5


-- Q2 — Funds with expense_ratio < 1%
SELECT scheme_name, fund_house, expense_ratio_pct
        FROM dim_fund
        WHERE expense_ratio_pct < 1.0
        ORDER BY expense_ratio_pct


-- Q3 — Average NAV per month
SELECT 
            amfi_code,
            strftime('%Y-%m', date) AS month,
            ROUND(AVG(nav), 4) AS avg_nav
        FROM fact_nav
        GROUP BY amfi_code, month
        ORDER BY month DESC
        LIMIT 20


-- Q4 — Top 5 funds by Sharpe ratio
SELECT f.scheme_name, f.fund_house, p.sharpe_ratio
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.sharpe_ratio DESC
        LIMIT 5


-- Q5 — Transactions by state
SELECT state,
               COUNT(*) AS total_txns,
               ROUND(SUM(amount_inr), 2) AS total_amount
        FROM fact_transactions
        GROUP BY state
        ORDER BY total_amount DESC


-- Q6 — SIP vs Lumpsum vs Redemption split
SELECT transaction_type,
               COUNT(*) AS count,
               ROUND(SUM(amount_inr), 2) AS total_amount
        FROM fact_transactions
        GROUP BY transaction_type


-- Q7 — Funds with highest 3yr returns
SELECT f.scheme_name, f.fund_house, p.return_3yr_pct
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC
        LIMIT 5


-- Q8 — Average transaction by age group
SELECT age_group,
               COUNT(*) AS txn_count,
               ROUND(AVG(amount_inr), 2) AS avg_amount
        FROM fact_transactions
        GROUP BY age_group
        ORDER BY avg_amount DESC


-- Q9 — Funds by risk category
SELECT risk_category,
               COUNT(*) AS fund_count
        FROM dim_fund
        GROUP BY risk_category
        ORDER BY fund_count DESC


-- Q10 — Funds with negative max drawdown < -20%
SELECT f.scheme_name, p.max_drawdown_pct, p.sharpe_ratio
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        WHERE p.max_drawdown_pct < -20
        ORDER BY p.max_drawdown_pct
