"""
Step 1 - Add Product Name to SampleSuperstore.csv

Why: SampleSuperstore.csv (13 columns) has no product-level identifier, only
Sub-Category (17 groups). "Top 10 Products" needs actual product names.

A public reference file with Product Name exists but differs from the original
in some rows (Sales/Quantity/Profit/Category, ~2%), as found in Task 17.
So we take ONLY Product Name + Product ID from it, matched row by row, and
verify alignment on 9 shared columns before trusting the match. All Sales
values used in the analysis remain from the original SampleSuperstore.csv.
"""
import pandas as pd

ORIGINAL = "SampleSuperstore.csv"
REFERENCE_URL = ("https://raw.githubusercontent.com/Bimal2614/Data-Analysis/"
                  "main/Super%20Store%20Dataset.csv")     # has Product Name / Product ID
OUTPUT = "SampleSuperstore_with_ProductName.csv"

orig = pd.read_csv(ORIGINAL, encoding="latin1")
ref = pd.read_csv(REFERENCE_URL, encoding="utf-8")   # needs internet access

shared = ["Ship Mode", "Segment", "Country", "City", "State",
          "Postal Code", "Region", "Sub-Category", "Discount"]
assert len(orig) == len(ref), "Row counts differ"
for col in shared:
    assert (orig[col].astype(str).values == ref[col].astype(str).values).all(), \
        f"Column {col} does not line up - do not merge"

orig["Product ID"] = ref["Product ID"]
orig["Product Name"] = ref["Product Name"]

assert orig["Product Name"].notna().all()
print("Rows:", len(orig), "| unique products:", orig["Product Name"].nunique())

orig.to_csv(OUTPUT, index=False)
print(f"Saved {OUTPUT}")
