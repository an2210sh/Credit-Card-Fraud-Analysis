-- ==========================================================
-- 04_views.sql : Analytical Views for Power BI Dashboard
-- ==========================================================

-- View 1: Hourly Fraud & Flagged Trend
CREATE OR REPLACE VIEW vw_hourly_fraud_trend AS
SELECT
    trans_hour,
    COUNT(*) AS total_transactions,
    SUM(is_fraud) AS actual_frauds,
    SUM(final_flagged) AS flagged_transactions,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_rate_pct
FROM fact_transactions
GROUP BY trans_hour
ORDER BY trans_hour;

-- View 2: Rule-by-Rule Effectiveness Summary
CREATE OR REPLACE VIEW vw_rule_performance AS
SELECT 'Rule 1: High Amount Outlier' AS rule_name,
       SUM(rule1_high_amt) AS total_hits,
       SUM(CASE WHEN rule1_high_amt = 1 AND is_fraud = 1 THEN 1 ELSE 0 END) AS true_frauds_caught
FROM fact_transactions
UNION ALL
SELECT 'Rule 2: Midnight High Spend',
       SUM(rule2_midnight_spend),
       SUM(CASE WHEN rule2_midnight_spend = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
FROM fact_transactions
UNION ALL
SELECT 'Rule 3: High Velocity Swipes',
       SUM(rule3_high_velocity),
       SUM(CASE WHEN rule3_high_velocity = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
FROM fact_transactions
UNION ALL
SELECT 'Rule 4: Unknown Far Location',
       SUM(rule4_unknown_location),
       SUM(CASE WHEN rule4_unknown_location = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
FROM fact_transactions
UNION ALL
SELECT 'Rule 5: Merchant Multi-User Burst',
       SUM(rule5_merchant_burst),
       SUM(CASE WHEN rule5_merchant_burst = 1 AND is_fraud = 1 THEN 1 ELSE 0 END)
FROM fact_transactions;

-- View 3: State-Level Fraud & Loss Summary
CREATE OR REPLACE VIEW vw_state_fraud_summary AS
SELECT
    c.state,
    COUNT(f.trans_num) AS total_txns,
    SUM(f.is_fraud) AS actual_frauds,
    ROUND(SUM(CASE WHEN f.is_fraud = 1 THEN f.amt ELSE 0 END), 2) AS fraud_loss_amount
FROM fact_transactions f
JOIN dim_cardholder c ON f.cc_num = c.cc_num
GROUP BY c.state;z