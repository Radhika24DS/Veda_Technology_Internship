"""Task 30 - preprocessing. Run: python3 preprocess.py <raw_csv> <out_csv>"""
import sys
import numpy as np, pandas as pd

raw, out = sys.argv[1], sys.argv[2]
df = pd.read_csv(raw)
log = {"raw_rows": len(df)}

# 1. text cleanup
for c in df.select_dtypes("object").columns.union(df.select_dtypes("string").columns):
    df[c] = df[c].astype(str).str.strip()
df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]

# 2. exact duplicates
log["duplicates_removed"] = int(df.duplicated().sum())
df = df.drop_duplicates().reset_index(drop=True)

# 3. validity checks
log["null_cells"] = int(df.isna().sum().sum())
log["non_positive_sales"] = int((df.Sales <= 0).sum())
log["discount_out_of_range"] = int((~df.Discount.between(0, 1)).sum())
df["Postal_Code"] = df["Postal_Code"].astype(str).str.zfill(5)

# 4. derived measures
df["Profit_Margin"] = (df.Profit / df.Sales).round(4)
df["Loss_Making"] = (df.Profit < 0).astype(int)

# 5. SIMULATED order date (file has no date column). Seeded -> reproducible.
rng = np.random.default_rng(42)
days = pd.date_range("2014-01-01", "2017-12-31", freq="D")
df["Order_Date_SIMULATED"] = rng.choice(days, size=len(df))
d = pd.to_datetime(df.Order_Date_SIMULATED)
df["Year"] = d.dt.year
df["Quarter"] = d.dt.quarter
df["Year_Quarter"] = d.dt.year.astype(str) + "-Q" + d.dt.quarter.astype(str)
df["Order_Date_SIMULATED"] = d.dt.strftime("%Y-%m-%d")

df.to_csv(out, index=False)
log["clean_rows"] = len(df)
print(log)
