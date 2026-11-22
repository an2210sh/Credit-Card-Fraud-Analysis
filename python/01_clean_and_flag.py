import os
import pandas as pd
import numpy as np

# 1. DATASET LOAD KARNA
dataset_path = os.path.join("data", "fraudTest.csv")
df = pd.read_csv(dataset_path)

if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# 2. DATA CLEANING (Warning-free syntax)
duplicates_count = df.duplicated(subset=["trans_num"]).sum()
df = df.drop_duplicates(subset=["trans_num"])

missing_count = df.isnull().sum().sum()
df = df.dropna()

invalid_amt_count = (df["amt"] <= 0).sum()
df = df[df["amt"] > 0].copy()

print("--- DATA CLEANING SUMMARY ---")
print(f"Duplicates Removed:          {duplicates_count}")
print(f"Missing Values Found:        {missing_count}")
print(f"Invalid Amounts (<=0):       {invalid_amt_count}")
print(f"Clean Rows Remaining:        {len(df)}")

fraud_counts = df["is_fraud"].value_counts()
fraud_pct = (fraud_counts[1] / len(df)) * 100
print("\n--- CLASS IMBALANCE ---")
print(f"Normal Transactions (0):     {fraud_counts[0]}")
print(f"Fraud Transactions  (1):     {fraud_counts[1]} ({fraud_pct:.3f}%)")

# 3. FEATURE ENGINEERING
df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"])
df = df.sort_values(by=["cc_num", "trans_date_trans_time"])

df["trans_hour"] = df["trans_date_trans_time"].dt.hour
df["trans_day"] = df["trans_date_trans_time"].dt.day_name()
df["is_midnight"] = np.where((df["trans_hour"] >= 0) & (df["trans_hour"] <= 3), 1, 0)

df["mins_since_last_txn"] = (
    df.groupby("cc_num")["trans_date_trans_time"].diff().dt.total_seconds() / 60.0
)

def get_distance_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    return 2 * r * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

df["distance_km"] = get_distance_km(df["lat"], df["long"], df["merch_lat"], df["merch_long"])

# 4. ALL 5 FRAUD DETECTION RULES
amt_threshold = df["amt"].quantile(0.99)
df["rule1_high_amt"] = np.where(df["amt"] > amt_threshold, 1, 0)
df["rule2_midnight_spend"] = np.where((df["is_midnight"] == 1) & (df["amt"] > 200), 1, 0)
df["rule3_high_velocity"] = np.where(
    (df["mins_since_last_txn"].notnull()) & (df["mins_since_last_txn"] <= 10), 1, 0
)
# Refined Rule 4: Ghar se >100 km door + high amount (>$150)
df["rule4_unknown_location"] = np.where((df["distance_km"] > 100) & (df["amt"] > 150), 1, 0)

# Rule 5: Merchant Burst (15-min mein >= 3 alag-alag users)
df["time_bucket_15m"] = df["trans_date_trans_time"].dt.floor("15min")
df["distinct_users_15m"] = df.groupby(["merchant", "time_bucket_15m"])["cc_num"].transform("nunique")
df["rule5_merchant_burst"] = np.where(df["distinct_users_15m"] >= 3, 1, 0)

rule_cols = [
    "rule1_high_amt", "rule2_midnight_spend", "rule3_high_velocity",
    "rule4_unknown_location", "rule5_merchant_burst"
]
df["final_flagged"] = (df[rule_cols].sum(axis=1) > 0).astype(int)

# 5. PRECISION & RECALL EVALUATION
tp = len(df[(df["final_flagged"] == 1) & (df["is_fraud"] == 1)])
fp = len(df[(df["final_flagged"] == 1) & (df["is_fraud"] == 0)])
fn = len(df[(df["final_flagged"] == 0) & (df["is_fraud"] == 1)])

precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0

print("\n--- 5-RULE ENGINE RESULTS ---")
print(f"99th Percentile Threshold:   ${amt_threshold:.2f}")
print(f"Rule 1 (High Amount) Hits:   {df['rule1_high_amt'].sum()}")
print(f"Rule 2 (Midnight Spend):     {df['rule2_midnight_spend'].sum()}")
print(f"Rule 3 (High Velocity):      {df['rule3_high_velocity'].sum()}")
print(f"Rule 4 (Unknown Location):   {df['rule4_unknown_location'].sum()}")
print(f"Rule 5 (Merchant Burst):     {df['rule5_merchant_burst'].sum()}")
print(f"Total Flagged Transactions:  {df['final_flagged'].sum()}")
print(f"Actual Frauds Caught (TP):   {tp}")
print(f"Precision:                   {precision:.2f}%")
print(f"Recall:                      {recall:.2f}%")

# 6. EXPORT CLEAN CSVs
selected_cols = [
    "trans_num", "trans_date_trans_time", "cc_num", "merchant", "category",
    "amt", "first", "last", "gender", "city", "state", "city_pop", "job",
    "trans_hour", "trans_day", "is_midnight", "mins_since_last_txn",
    "distance_km", "distinct_users_15m",
    "rule1_high_amt", "rule2_midnight_spend", "rule3_high_velocity",
    "rule4_unknown_location", "rule5_merchant_burst",
    "final_flagged", "is_fraud"
]
clean_df = df[selected_cols]
clean_df.to_csv(os.path.join("data", "cleaned_transactions.csv"), index=False)
clean_df.head(1000).to_csv(os.path.join("data", "sample_transactions.csv"), index=False)
print("\nSuccess! Files saved cleanly.")