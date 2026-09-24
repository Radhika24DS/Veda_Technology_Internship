"""
Step 1 - Add the missing Order Date column to SampleSuperstore.csv

Why: SampleSuperstore.csv (13 columns) has NO date column, so a monthly trend
cannot be built from it. The full public Superstore file has Order Date, but the
copy used here differs from the original in 199 rows (Sales/Quantity/Profit/Category).

So we take ONLY the Order Date column from the full file and attach it to the
original SampleSuperstore.csv row by row. Every Sales value stays as in the
original file. The merge is validated before anything is saved.
"""
import pandas as pd
import numpy as np

ORIGINAL = "SampleSuperstore.csv"
FULL_URL = ("https://raw.githubusercontent.com/Bimal2614/Data-Analysis/"
            "main/Super%20Store%20Dataset.csv")
OUTPUT = "SampleSuperstore_with_OrderDate.csv"

orig = pd.read_csv(ORIGINAL, encoding="latin1")
full = pd.read_csv(FULL_URL)

# 1) Row alignment: shared text columns must match on every row
shared = ["Ship Mode", "Segment", "Country", "City", "State",
          "Postal Code", "Region", "Sub-Category", "Discount"]
assert len(orig) == len(full), "Row counts differ"
for col in shared:
    assert (orig[col].astype(str).values == full[col].astype(str).values).all(), \
        f"Column {col} does not line up - do not merge"

# 2) Convert dates with an EXPLICIT format (no guessing -> no day/month mix-ups)
orig["Order Date"] = pd.to_datetime(full["Order Date"], format="%Y-%m-%d", errors="raise")
ship = pd.to_datetime(full["Ship Date"], format="%Y-%m-%d", errors="raise")

# 3) Sanity checks
assert orig["Order Date"].notna().all(), "Missing dates"
assert (ship >= orig["Order Date"]).all(), "A ship date is before its order date"

# 4) Reconciliation with the well-known yearly totals of the original Superstore
print(orig.groupby(orig["Order Date"].dt.year)["Sales"].sum().round(2))

orig.to_csv(OUTPUT, index=False)
print(f"Saved {OUTPUT}: {orig.shape[0]} rows, "
      f"{orig['Order Date'].min().date()} to {orig['Order Date'].max().date()}")
