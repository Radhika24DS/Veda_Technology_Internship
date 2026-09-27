"""
Step 1 - Add Customer ID, Customer Name and Order ID to SampleSuperstore.csv

Why: SampleSuperstore.csv (13 columns) has no customer or order identifier at all,
so orders per customer cannot be counted from it directly. These columns are added
from a public reference copy of the Superstore dataset, matched row by row and
validated the same way as in Tasks 17 and 19, before being trusted.
All Sales/Profit/Quantity values used in the analysis remain from the original file.
"""
import pandas as pd

ORIGINAL = "SampleSuperstore.csv"
REFERENCE_URL = ("https://raw.githubusercontent.com/Bimal2614/Data-Analysis/"
                  "main/Super%20Store%20Dataset.csv")
OUTPUT = "SampleSuperstore_with_CustomerOrder.csv"

orig = pd.read_csv(ORIGINAL, encoding="latin1")
ref = pd.read_csv(REFERENCE_URL, encoding="utf-8")   # needs internet access

shared = ["Ship Mode", "Segment", "Country", "City", "State",
          "Postal Code", "Region", "Sub-Category", "Discount"]
assert len(orig) == len(ref), "Row counts differ"
for col in shared:
    assert (orig[col].astype(str).values == ref[col].astype(str).values).all(), \
        f"Column {col} does not line up - do not merge"

orig["Order ID"] = ref["Order ID"]
orig["Order Date"] = ref["Order Date"]
orig["Customer ID"] = ref["Customer ID"]
orig["Customer Name"] = ref["Customer Name"]

assert orig[["Order ID", "Customer ID", "Customer Name"]].notna().all().all()
print("Rows:", len(orig))
print("Unique orders (Order ID):", orig["Order ID"].nunique())
print("Unique customers (Customer ID):", orig["Customer ID"].nunique())

orig.to_csv(OUTPUT, index=False)
print(f"Saved {OUTPUT}")
