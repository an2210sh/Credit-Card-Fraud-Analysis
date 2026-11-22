-- ==========================================================
-- 02_load.sql : Load Cleaned CSV into Star Schema Tables
-- ==========================================================

-- Staging table matching data/cleaned_transactions.csv
CREATE TABLE stg_transactions (
    trans_num               VARCHAR2(50),
    trans_date_trans_time   VARCHAR2(30),
    cc_num                  NUMBER(20),
    merchant                VARCHAR2(150),
    category                VARCHAR2(50),
    amt                     NUMBER(10, 2),
    first_name              VARCHAR2(50),
    last_name               VARCHAR2(50),
    gender                  CHAR(1),
    city                    VARCHAR2(100),
    state                   VARCHAR2(10),
    city_pop                NUMBER(12),
    job                     VARCHAR2(100),
    trans_hour              NUMBER(2),
    trans_day               VARCHAR2(15),
    is_midnight             NUMBER(1),
    mins_since_last_txn     NUMBER(10, 2),
    distance_km             NUMBER(10, 2),
    distinct_users_15m      NUMBER(5),
    rule1_high_amt          NUMBER(1),
    rule2_midnight_spend    NUMBER(1),
    rule3_high_velocity     NUMBER(1),
    rule4_unknown_location  NUMBER(1),
    rule5_merchant_burst    NUMBER(1),
    final_flagged           NUMBER(1),
    is_fraud                NUMBER(1)
);

-- Note: Bulk CSV load via SQL*Loader / SQL Developer Import Wizard into STG_TRANSACTIONS,
-- then populate Star Schema tables using the INSERT statements below:

INSERT INTO dim_cardholder (cc_num, first_name, last_name, gender, city, state, city_pop, job)
SELECT DISTINCT cc_num, first_name, last_name, gender, city, state, city_pop, job
FROM stg_transactions;

INSERT INTO dim_merchant (merchant_name, category)
SELECT DISTINCT merchant, category
FROM stg_transactions;

INSERT INTO fact_transactions (
    trans_num, trans_date_trans_time, cc_num, merchant_name, amt,
    trans_hour, trans_day, is_midnight, mins_since_last_txn,
    distance_km, distinct_users_15m,
    rule1_high_amt, rule2_midnight_spend, rule3_high_velocity,
    rule4_unknown_location, rule5_merchant_burst, final_flagged, is_fraud
)
SELECT
    trans_num,
    TO_TIMESTAMP(trans_date_trans_time, 'YYYY-MM-DD HH24:MI:SS'),
    cc_num, merchant, amt,
    trans_hour, trans_day, is_midnight, mins_since_last_txn,
    distance_km, distinct_users_15m,
    rule1_high_amt, rule2_midnight_spend, rule3_high_velocity,
    rule4_unknown_location, rule5_merchant_burst, final_flagged, is_fraud
FROM stg_transactions;

COMMIT;