"""Step 1 - Clean the Superstore data and add analysis columns.
Input : data/SampleSuperstore_raw.csv
Output: data/superstore_clean.csv, data/cleaning_log.csv
"""
import pandas as pd, numpy as np

raw = pd.read_csv("data/SampleSuperstore_raw.csv", dtype={"Postal Code": str})
log = []
def note(step, detail, rows_affected):
    log.append({"Step": step, "Detail": detail, "Rows affected": rows_affected})

df = raw.copy()
note("Load", "Raw rows loaded", len(df))

# 1. Missing values
na = int(df.isna().sum().sum())
note("Missing values", "Null cells found across all columns", na)

# 2. Trim / standardise text
txt = df.select_dtypes(include="object").columns
for c in txt:
    df[c] = df[c].astype(str).str.strip()
df["Region"] = df["Region"].str.title()
note("Text standardisation", "Trimmed whitespace, title-cased Region", len(df))

# 3. Postal code: restore leading zeros lost in the CSV (e.g. 1040 -> 01040)
df["Postal Code"] = df["Postal Code"].str.zfill(5)
note("Postal code", "Stored as 5-digit text (leading zeros restored)", int((raw["Postal Code"].astype(str).str.len() < 5).sum()))

# 4. Exact duplicates
d = int(df.duplicated().sum())
df = df.drop_duplicates().reset_index(drop=True)
note("Duplicates", "Fully identical rows removed (no Order ID exists to prove they are distinct orders)", d)

# 5. Constant column
df = df.drop(columns=["Country"])
note("Constant column", "Dropped Country (always 'United States')", len(df))

# 6. Validity checks
bad = int(((df.Sales <= 0) | (df.Quantity <= 0) | (~df.Discount.between(0, 1))).sum())
note("Validity", "Rows with Sales<=0, Quantity<=0 or Discount outside 0-1", bad)

# 7. Derived columns
df["Profit Margin"] = (df["Profit"] / df["Sales"]).round(4)
df["Loss Flag"] = (df["Profit"] < 0).astype(int)
df["Discount Band"] = pd.cut(df["Discount"], [-0.001, 0, 0.10, 0.20, 0.30, 1.0],
                             labels=["No discount", "1-10%", "11-20%", "21-30%", ">30%"]).astype(str)
df["Salesperson (Region Team)"] = df["Region"] + " Region Team"
df["Salesperson (State Rep)"] = "State Rep - " + df["State"]
note("Derived columns", "Profit Margin, Loss Flag, Discount Band, Salesperson (Region Team), Salesperson (State Rep)", len(df))

# 8. Outliers: flag only (never delete real big deals / losses)
q1, q3 = df.Profit.quantile([.25, .75]); iqr = q3 - q1
df["Profit Outlier"] = ((df.Profit < q1 - 3*iqr) | (df.Profit > q3 + 3*iqr)).astype(int)
note("Outliers", "Flagged (not removed) profit beyond 3xIQR", int(df["Profit Outlier"].sum()))

note("Final", "Clean rows saved", len(df))
df.to_csv("data/superstore_clean.csv", index=False)
pd.DataFrame(log).to_csv("data/cleaning_log.csv", index=False)
print(pd.DataFrame(log).to_string())
