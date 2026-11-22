-- ==========================================================
-- 03_analytics_queries.sql : Fraud Velocity & KPI Queries
-- ==========================================================

-- 1. SQL Window Function (LAG): Same Card par consecutive swipes ke beech time gap (minutes)
SELECT
    trans_num,
    cc_num,
    trans_date_trans_time,
    amt,
    ROUND(
        (CAST(trans_date_trans_time AS DATE) -
         CAST(LAG(trans_date_trans_time) OVER (PARTITION BY cc_num ORDER BY trans_date_trans_time) AS DATE)
        ) * 24 * 60, 2
    ) AS sql_mins_since_last_txn,
    is_fraud
FROM fact_transactions
ORDER BY cc_num, trans_date_trans_time;

-- 2. SQL Window Function (COUNT OVER): High-Velocity Cards (Cards with >= 3 rapid swipes)
SELECT *
FROM (
    SELECT
        cc_num,
        trans_num,
        trans_date_trans_time,
        amt,
        COUNT(*) OVER (
            PARTITION BY cc_num
            ORDER BY trans_date_trans_time
            RANGE BETWEEN INTERVAL '10' MINUTE PRECEDING AND CURRENT ROW
        ) AS txns_in_10_min_window,
        is_fraud
    FROM fact_transactions
)
WHERE txns_in_10_min_window >= 3;

-- 3. Precision & Recall Verification Query (Python vs SQL Reconciliation)
SELECT
    COUNT(*) AS total_transactions,
    SUM(is_fraud) AS actual_frauds,
    SUM(final_flagged) AS total_flagged,
    SUM(CASE WHEN final_flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) AS true_positives,
    ROUND(
        SUM(CASE WHEN final_flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(final_flagged), 0), 2
    ) AS precision_pct,
    ROUND(
        SUM(CASE WHEN final_flagged = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(is_fraud), 0), 2
    ) AS recall_pct
FROM fact_transactions;

-- 4. Midnight Edge Case Check (12:00 AM to 3:59 AM Fraud Rate vs Daytime)
SELECT
    CASE WHEN is_midnight = 1 THEN 'Midnight (12 AM - 4 AM)' ELSE 'Regular Hours' END AS time_window,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_rate_pct,
    ROUND(AVG(amt), 2) AS avg_txn_amount
FROM fact_transactions
GROUP BY is_midnight;

-- 5. Merchant Category-Wise Fraud Breakdown
SELECT
    m.category,
    COUNT(f.trans_num) AS total_txns,
    SUM(f.is_fraud) AS actual_frauds,
    SUM(f.final_flagged) AS flagged_txns,
    ROUND(SUM(f.is_fraud) * 100.0 / COUNT(f.trans_num), 3) AS fraud_rate_pct,
    ROUND(SUM(CASE WHEN f.is_fraud = 1 THEN f.amt ELSE 0 END), 2) AS total_fraud_loss
FROM fact_transactions f
JOIN dim_merchant m ON f.merchant_name = m.merchant_name
GROUP BY m.category
ORDER BY fraud_rate_pct DESC;