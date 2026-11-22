-- ==========================================================
-- 01_ddl.sql : Star Schema DDL for Credit Card Fraud Analysis
-- ==========================================================

-- 1. Dimension Table: Cardholder Details
CREATE TABLE dim_cardholder (
    cc_num      NUMBER(20) PRIMARY KEY,
    first_name  VARCHAR2(50),
    last_name   VARCHAR2(50),
    gender      CHAR(1),
    city        VARCHAR2(100),
    state       VARCHAR2(10),
    city_pop    NUMBER(12),
    job         VARCHAR2(100)
);

-- 2. Dimension Table: Merchant Details
CREATE TABLE dim_merchant (
    merchant_name VARCHAR2(150) PRIMARY KEY,
    category      VARCHAR2(50)
);

-- 3. Fact Table: Credit Card Transactions & Fraud Flags
CREATE TABLE fact_transactions (
    trans_num               VARCHAR2(50) PRIMARY KEY,
    trans_date_trans_time   TIMESTAMP NOT NULL,
    cc_num                  NUMBER(20) NOT NULL,
    merchant_name           VARCHAR2(150) NOT NULL,
    amt                     NUMBER(10, 2) NOT NULL,
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
    is_fraud                NUMBER(1),
    CONSTRAINT fk_cardholder FOREIGN KEY (cc_num) REFERENCES dim_cardholder(cc_num),
    CONSTRAINT fk_merchant   FOREIGN KEY (merchant_name) REFERENCES dim_merchant(merchant_name)
);

-- Performance Indexes for Velocity & Time-Based Queries
CREATE INDEX idx_fact_cc_time ON fact_transactions(cc_num, trans_date_trans_time);
CREATE INDEX idx_fact_fraud   ON fact_transactions(is_fraud, final_flagged);