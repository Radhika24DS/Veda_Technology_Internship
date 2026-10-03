"""
Task 26 - Executive KPI Dashboard (Superstore)
Data preprocessing script for SampleSuperstore.csv (13 columns, no date/ID fields).

Usage:
    python preprocess_superstore.py SampleSuperstore.csv
Outputs:
    Superstore_Clean.csv   -> load this into Power BI
    data_quality_log.txt   -> data-quality checks and results
"""
import sys
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "SampleSuperstore.csv"
log = []

# 1. Load
try:
    df = pd.read_csv(src, encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv(src, encoding="latin-1")
log.append(f"Raw shape: {df.shape[0]} rows x {df.shape[1]} columns")

# 2. Standardise column names (Sub-Category -> Sub_Category, Postal Code -> Postal_Code)
df.columns = df.columns.str.strip().str.replace(r"[\s\-]+", "_", regex=True)

# 3. Trim whitespace in text columns
text_cols = df.select_dtypes(include=["object", "string"]).columns
for c in text_cols:
    df[c] = df[c].astype(str).str.strip()

# 4. Missing values
missing = int(df.isna().sum().sum())
log.append(f"Missing values: {missing}")
df = df.dropna()

# 5. Exact duplicates (all 13 columns identical).
#    NOTE: dataset has no Order ID, so a duplicate could in theory be a genuine
#    repeat line item. Removed as standard practice; documented here.
dups = int(df.duplicated().sum())
df = df.drop_duplicates()
log.append(f"Exact duplicate rows removed: {dups}")

# 6. Data types
df["Postal_Code"] = df["Postal_Code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(5)
for c in ["Sales", "Quantity", "Discount", "Profit"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["Quantity"] = df["Quantity"].astype(int)
log.append("Postal_Code stored as 5-digit text (4-digit New England codes zero-padded)")

# 7. Logical validation
bad_sales = int((df["Sales"] <= 0).sum())
bad_qty = int((df["Quantity"] <= 0).sum())
bad_disc = int((~df["Discount"].between(0, 1)).sum())
log.append(f"Sales <= 0: {bad_sales} | Quantity <= 0: {bad_qty} | Discount outside 0-1: {bad_disc}")
df = df[(df["Sales"] > 0) & (df["Quantity"] > 0) & df["Discount"].between(0, 1)]

# 8. Drop constant column
if df["Country"].nunique() == 1:
    log.append(f"Dropped constant column Country ('{df['Country'].iloc[0]}')")
    df = df.drop(columns="Country")

# 9. Feature engineering
df["Profit_Margin"] = (df["Profit"] / df["Sales"]).round(4)
df["Sales_Per_Unit"] = (df["Sales"] / df["Quantity"]).round(2)
df["Discount_Band"] = pd.cut(
    df["Discount"], [-0.01, 0, 0.2, 0.4, 1.0],
    labels=["No Discount", "Low (1-20%)", "Medium (21-40%)", "High (>40%)"]).astype(str)
df["Discount_Band_Order"] = df["Discount_Band"].map(
    {"No Discount": 1, "Low (1-20%)": 2, "Medium (21-40%)": 3, "High (>40%)": 4})  # for Sort by column
df["Loss_Making"] = (df["Profit"] < 0).map({True: "Yes", False: "No"})
df["Loss_Flag"] = (df["Profit"] < 0).astype(int)  # for loss-rate measure
df.insert(0, "Row_ID", range(1, len(df) + 1))      # surrogate key (no Order ID in source)

# 10. Outliers: kept (real business losses / large deals)
log.append(f"Loss-making rows kept for analysis: {int(df['Loss_Flag'].sum())} "
           f"({df['Loss_Flag'].mean():.1%})")
log.append(f"Extreme values kept: min profit {df['Profit'].min():,.2f}, max profit {df['Profit'].max():,.2f}")

# 11. Save + control totals (use these to verify Power BI cards)
df.to_csv("Superstore_Clean.csv", index=False)
log.append(f"Clean shape: {df.shape[0]} rows x {df.shape[1]} columns")
log.append(f"Total Sales: {df['Sales'].sum():,.2f}")
log.append(f"Total Profit: {df['Profit'].sum():,.2f}")
log.append(f"Profit Margin: {df['Profit'].sum() / df['Sales'].sum():.2%}")
log.append(f"Total Quantity: {df['Quantity'].sum():,}")
log.append(f"Avg Discount: {df['Discount'].mean():.2%}")

with open("data_quality_log.txt", "w") as f:
    f.write("\n".join(log))
print("\n".join(log))
