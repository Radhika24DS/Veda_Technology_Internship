"""Task 21 - preprocessing for the Northwind orders + order_details CSVs.
Run:  python scripts/01_preprocess.py [raw_dir]  -> writes data/*_clean.csv + data/cleaning_log.txt
"""
import sys, pandas as pd
RAW = sys.argv[1] if len(sys.argv) > 1 else "."
log = []
def note(msg): log.append(msg); print(msg)

o = pd.read_csv(f"{RAW}/northwind_orders.csv", dtype=str, keep_default_na=False)
d = pd.read_csv(f"{RAW}/northwind_order_details.csv", dtype=str, keep_default_na=False)
note(f"Raw shapes -> orders {o.shape}, order_details {d.shape}")

# 1. trim whitespace on every text column
for df in (o, d):
    for c in df.columns: df[c] = df[c].str.strip()
note("1. Trimmed leading/trailing whitespace in all columns")

# 2. blank strings -> real NULLs
blank = {c: int((o[c] == "").sum()) for c in o.columns if (o[c] == "").any()}
o = o.replace("", pd.NA)
note(f"2. Blank -> NULL: {blank}")

# 3. type conversion
for c in ["order_date", "required_date", "shipped_date"]:
    o[c] = pd.to_datetime(o[c], format="%Y-%m-%d", errors="raise")
for c in ["order_id", "employee_id", "ship_via"]: o[c] = o[c].astype(int)
o["freight"] = o["freight"].astype(float)
d = d.astype({"order_id": int, "product_id": int, "unit_price": float, "quantity": int, "discount": float})
note("3. Converted dates to DATE and numeric columns to int/float (errors would raise)")

# 4. duplicates / keys / referential integrity
note(f"4. Duplicate rows: orders={o.duplicated().sum()}, details={d.duplicated().sum()}; "
     f"duplicate order_id={o.order_id.duplicated().sum()}; duplicate (order_id,product_id)={d.duplicated(['order_id','product_id']).sum()}")
orphans = set(d.order_id) - set(o.order_id)
note(f"   Orphan order_details rows (no parent order): {len(orphans)}")

# 5. business-rule validation
shipped = o.shipped_date.notna()
assert (o.shipped_date[shipped] >= o.order_date[shipped]).all()
assert (o.required_date >= o.order_date).all()
assert (o.freight > 0).all() and (d.quantity > 0).all() and (d.unit_price > 0).all() and d.discount.between(0, 1).all()
note("5. Validated: shipped>=order date, required>=order date, freight/qty/price > 0, 0<=discount<=1 (all passed)")

# 6. missing values policy
note(f"6. ship_region NULL for {o.ship_region.isna().sum()} orders (region not applicable) - kept as NULL, not imputed; "
     f"ship_postal_code NULL for {o.ship_postal_code.isna().sum()} (all Ireland) - kept as NULL")
note(f"   shipped_date NULL for {o.shipped_date.isna().sum()} orders = not yet shipped - kept as NULL (meaningful)")

# 7. derived columns
o["days_to_ship"] = (o.shipped_date - o.order_date).dt.days.astype("Int64")
o["shipped_late"] = (o.shipped_date > o.required_date).astype(int)
d["line_total"] = (d.unit_price * d.quantity * (1 - d.discount)).round(2)
note(f"7. Added derived columns: orders.days_to_ship, orders.shipped_late ({int(o.shipped_late.sum())} late orders); order_details.line_total")

# 8. export
o = o.sort_values("order_id"); d = d.sort_values(["order_id", "product_id"])
for c in ["order_date", "required_date", "shipped_date"]: o[c] = o[c].dt.strftime("%Y-%m-%d")
o.to_csv("data/orders_clean.csv", index=False, na_rep="")
d.to_csv("data/order_details_clean.csv", index=False, na_rep="")
note(f"8. Exported clean files -> orders {o.shape}, order_details {d.shape}")
open("data/cleaning_log.txt", "w").write("\n".join(log) + "\n")
