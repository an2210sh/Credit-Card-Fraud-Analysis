# Credit Card Transaction & Fraud Pattern Analysis

An end-to-end data analytics project built to detect anomalous credit card activity, analyze transaction velocity, and evaluate rule-based fraud flags against actual labelled fraud cases.

## Problem Statement
Financial institutions lose significant revenue to fraudulent transactions, yet fraudulent activity typically accounts for less than 1% of total transaction volume. Because fraud data is heavily imbalanced, simple averages fail to catch suspicious behavior. 

The goal of this project is to build a clean data pipeline using **Python, Oracle SQL, and Power BI** to:
- Clean raw transaction logs and handle severe class imbalance.
- Flag high-risk transactions using behavioral rules (amount outliers, odd-hour activity, and rapid card swipes).
- Validate rule accuracy using **Precision** and **Recall** metrics rather than raw accuracy.

## Tech Stack
- **Data Cleaning & Rule Engine:** Python (Pandas, NumPy)
- **Database & Velocity Analytics:** Oracle SQL (Window Functions, Views, Star Schema)
- **Visualization & Reporting:** Power BI

## Project Architecture & Workflow
1. **Data Preparation (Python):** Handled duplicate records, verified missing values, engineered time-based features (hour of day, midnight flags), and implemented 3 rule-based fraud detection checks.
2. **Relational Modeling & SQL Queries (Oracle SQL):** Designed a star schema (`DIM_CARDHOLDER`, `DIM_MERCHANT`, `FACT_TRANSACTIONS`) and used `LAG()` window functions to calculate time gaps between consecutive swipes on the same card.
3. **Interactive Dashboard (Power BI):** Built a multi-page report comparing flagged transactions against actual fraud labels, broken down by merchant category, transaction amount, and time of day.

## Fraud Detection Rules Implemented
- **Rule 1 – Amount Outlier:** Flags transactions exceeding the 99th percentile threshold or deviating sharply from normal spending patterns.
- **Rule 2 – Midnight Activity:** Flags high-value transactions occurring between 12:00 AM and 4:00 AM.
- **Rule 3 – High Velocity Swipes:** Flags multiple transactions made on the same card within a 10-minute window.

## Key Metrics & Results *(To be updated after model run)*
- **Total Transactions Analyzed:** `TBD`
- **Actual Fraud Rate:** `TBD %`
- **Rule Engine Precision:** `TBD %`
- **Rule Engine Recall:** `TBD %`

## Repository Structure
```text
├── data/               # Dataset source details & sample cleaned records
├── python/             # Jupyter notebooks & Python scripts for EDA and rule flagging
├── sql/                # Oracle DDL, data load scripts, velocity queries & views
├── powerbi/            # Power BI (.pbix) file and dashboard screenshots
├── docs/               # ER diagram, test-case verification & insights summary
└── README.md