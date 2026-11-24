import glob
import re
import sqlite3
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# 1. Load cleaned CSV and build Star Schema tables in SQLite
csv_files = glob.glob("data/*.csv")
if not csv_files:
    raise FileNotFoundError("data/ folder mein koi CSV file nahi mili!")

df = pd.read_csv(csv_files[0])
if "merchant" in df.columns and "merchant_name" not in df.columns:
    df["merchant_name"] = df["merchant"]

conn = sqlite3.connect(":memory:")
df.to_sql("cleaned_transactions", conn, if_exists="replace", index=False)
df.to_sql("fact_transactions", conn, if_exists="replace", index=False)

if "merchant_name" in df.columns and "category" in df.columns:
    df[["merchant_name", "category"]].drop_duplicates().to_sql(
        "dim_merchant", conn, if_exists="replace", index=False
    )

card_cols = [c for c in ["cc_num", "first", "last", "gender", "city", "state", "city_pop", "job"] if c in df.columns]
if "cc_num" in card_cols:
    df[card_cols].drop_duplicates(subset=["cc_num"]).to_sql(
        "dim_cardholder", conn, if_exists="replace", index=False
    )

print(f"Loaded {len(df):,} rows into 'fact_transactions' & dimension tables.\n")


def replace_cast_as_date(sql_text):
    pattern = re.compile(r"\bCAST\s*\(", re.IGNORECASE)
    while True:
        match = pattern.search(sql_text)
        if not match:
            break
        start = match.start()
        i = match.end()
        depth = 1
        while i < len(sql_text) and depth > 0:
            if sql_text[i] == "(":
                depth += 1
            elif sql_text[i] == ")":
                depth -= 1
            i += 1
        inner = sql_text[match.end():i - 1]
        m_as = re.search(r"\s+AS\s+DATE\s*$", inner, re.IGNORECASE)
        if m_as:
            expr = inner[:m_as.start()].strip()
            sql_text = sql_text[:start] + f"julianday({expr})" + sql_text[i:]
        else:
            sql_text = sql_text[:start] + "CAST_KEEP(" + sql_text[match.end():]
    return sql_text.replace("CAST_KEEP(", "CAST(")


def adapt_oracle_to_sqlite(sql_text):
    sql_text = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.DOTALL)
    sql_text = re.sub(r"--.*", "", sql_text)
    sql_text = replace_cast_as_date(sql_text)
    sql_text = re.sub(
        r"ORDER\s+BY\s+([a-zA-Z0-9_.]+)\s+RANGE\s+BETWEEN\s+INTERVAL\s+'(\d+)'\s+MINUTE\s+PRECEDING\s+AND\s+CURRENT\s+ROW",
        lambda m: f"ORDER BY (julianday({m.group(1)}) * 86400) RANGE BETWEEN {int(m.group(2)) * 60} PRECEDING AND CURRENT ROW",
        sql_text,
        flags=re.IGNORECASE,
    )
    sql_text = re.sub(r"FETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY", r"LIMIT \1", sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(r"\bNVL\s*\(", "IFNULL(", sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(r"\bWITH\s+READ\s+ONLY\b", "", sql_text, flags=re.IGNORECASE)
    sql_text = re.sub(
        r"CREATE\s+OR\s+REPLACE\s+VIEW\s+([a-zA-Z0-9_]+)",
        r"DROP VIEW IF EXISTS \1;\nCREATE VIEW \1",
        sql_text,
        flags=re.IGNORECASE,
    )
    return sql_text


# 2. Run Window Function & Analytics Queries
print("=" * 75)
print("PART 1: ANALYTICS & WINDOW FUNCTION QUERIES (03_analytics_queries.sql)")
print("=" * 75)
with open("sql/03_analytics_queries.sql", "r", encoding="utf-8") as f:
    queries_sql = adapt_oracle_to_sqlite(f.read())

for idx, stmt in enumerate([s.strip() for s in queries_sql.split(";") if len(s.strip()) > 3], 1):
    print(f"\n--- Query {idx} ---")
    try:
        res = pd.read_sql_query(stmt, conn)
        print(res.head(12).to_string(index=False))
    except Exception as e:
        print(f"Error in Query {idx}: {e}")

# 3. Create & Query Analytical Views
print("\n" + "=" * 75)
print("PART 2: ANALYTICAL VIEWS OUTPUT (04_views.sql)")
print("=" * 75)
with open("sql/04_views.sql", "r", encoding="utf-8") as f:
    views_sql = adapt_oracle_to_sqlite(f.read())

for stmt in [s.strip() for s in views_sql.split(";") if len(s.strip()) > 3]:
    try:
        conn.execute(stmt)
    except Exception as e:
        print(f"View warning: {e}")

views = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='view'", conn)["name"].tolist()
for v in views:
    print(f"\n--- View: {v} ---")
    res = pd.read_sql_query(f"SELECT * FROM {v} LIMIT 12", conn)
    print(res.to_string(index=False))

conn.close()