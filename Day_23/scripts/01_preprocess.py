"""
Task 23 - SQL Window Functions Intro (Northwind)
Step 1: Data cleaning & preprocessing
Reads raw CSVs -> validates -> cleans -> engineers features -> writes cleaned CSVs + SQLite DB
"""
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, CLEAN = ROOT / "data/raw", ROOT / "data/cleaned"
log = []
def note(msg):
    print(msg); log.append(msg)

# ---------- 1. Load (postal code as text so leading zeros survive) ----------
orders = pd.read_csv(RAW / "northwind_orders.csv", dtype={"ship_postal_code": "string"}, encoding="utf-8")
details = pd.read_csv(RAW / "northwind_order_details.csv")
note(f"Loaded orders={orders.shape}, order_details={details.shape}")

# ---------- 2. Standardise text ----------
text_cols = [c for c in orders.columns if c not in ("order_id","employee_id","ship_via","freight")]
for c in text_cols:
    orders[c] = orders[c].astype("string").str.strip().replace({"": pd.NA})
orders["customer_id"] = orders["customer_id"].str.upper()
note("Trimmed whitespace, upper-cased customer_id, blank strings -> NULL")

# ---------- 3. Fix data types ----------
for c in ["order_date", "required_date", "shipped_date"]:
    orders[c] = pd.to_datetime(orders[c], errors="coerce")
note("Converted order_date / required_date / shipped_date to datetime")

# ---------- 4. Duplicates & integrity ----------
dup_o = orders.duplicated("order_id").sum()
dup_d = details.duplicated(["order_id", "product_id"]).sum()
orders = orders.drop_duplicates("order_id"); details = details.drop_duplicates(["order_id", "product_id"])
note(f"Duplicate orders removed: {dup_o}; duplicate order lines removed: {dup_d}")
orphan = ~details.order_id.isin(orders.order_id)
note(f"Orphan order lines (no parent order): {orphan.sum()}")
details = details[~orphan]
note(f"Orders without any line item: {(~orders.order_id.isin(details.order_id)).sum()}")

# ---------- 5. Business-rule validation ----------
bad_qty  = (details.quantity <= 0).sum()
bad_disc = ((details.discount < 0) | (details.discount > 1)).sum()
bad_prc  = (details.unit_price <= 0).sum()
bad_ship = (orders.shipped_date < orders.order_date).sum()
note(f"Invalid quantity={bad_qty}, discount={bad_disc}, price={bad_prc}, shipped-before-ordered={bad_ship}")
details = details[(details.quantity > 0) & details.discount.between(0, 1) & (details.unit_price > 0)]

# ---------- 6. Missing values ----------
note(f"shipped_date NULL = {orders.shipped_date.isna().sum()} (orders not shipped yet -> kept as NULL, flagged)")
note(f"ship_region NULL = {orders.ship_region.isna().sum()} (region not applicable for many countries -> 'Not Specified')")
note(f"ship_postal_code NULL = {orders.ship_postal_code.isna().sum()} (-> 'Not Provided')")
orders["is_shipped"]  = orders.shipped_date.notna().astype(int)
orders["ship_region"] = orders.ship_region.fillna("Not Specified")
orders["ship_postal_code"] = orders.ship_postal_code.fillna("Not Provided")

# ---------- 7. Feature engineering ----------
details["gross_amount"]    = (details.unit_price * details.quantity).round(2)
details["discount_amount"] = (details.gross_amount * details.discount).round(2)
details["line_total"]      = (details.gross_amount - details.discount_amount).round(2)

orders["order_year"]    = orders.order_date.dt.year
orders["order_month"]   = orders.order_date.dt.month
orders["order_quarter"] = orders.order_date.dt.quarter
orders["year_month"]    = orders.order_date.dt.strftime("%Y-%m")
orders["days_to_ship"]  = (orders.shipped_date - orders.order_date).dt.days
orders["shipped_late"]  = (orders.shipped_date > orders.required_date).astype("Int64")
orders.loc[orders.shipped_date.isna(), "shipped_late"] = pd.NA

agg = details.groupby("order_id").agg(
    line_items=("product_id", "count"), total_units=("quantity", "sum"),
    order_revenue=("line_total", "sum")).reset_index()
agg["order_revenue"] = agg.order_revenue.round(2)
order_summary = orders.merge(agg, on="order_id", how="inner")
note(f"Built order_summary: {order_summary.shape}; total revenue = {order_summary.order_revenue.sum():,.2f}")

last = orders.order_date.max(); first = orders.order_date.min()
order_summary["is_partial_month"] = order_summary.year_month.isin(
    [first.strftime("%Y-%m"), last.strftime("%Y-%m")]).astype(int)
note(f"Data range {first.date()} -> {last.date()}; first & last months are partial (flag is_partial_month)")

# ---------- 8. Export ----------
def dates_to_str(df):
    df = df.copy()
    for c in ["order_date", "required_date", "shipped_date"]:
        df[c] = df[c].dt.strftime("%Y-%m-%d")
    return df
orders_out, summ_out = dates_to_str(orders), dates_to_str(order_summary)
orders_out.to_csv(CLEAN / "orders_clean.csv", index=False)
details.to_csv(CLEAN / "order_details_clean.csv", index=False)
summ_out.to_csv(CLEAN / "order_summary.csv", index=False)

db = ROOT / "northwind.db"
db.unlink(missing_ok=True)
con = sqlite3.connect(db)
orders_out.to_sql("orders", con, index=False)
details.to_sql("order_details", con, index=False)
summ_out.to_sql("order_summary", con, index=False)
con.execute("CREATE INDEX ix_od_order ON order_details(order_id)")
con.execute("CREATE INDEX ix_o_cust ON orders(customer_id)")
con.commit(); con.close()
note(f"Wrote cleaned CSVs and SQLite DB: {db.name}")
(ROOT / "docs/preprocessing_log.txt").write_text("\n".join(log), encoding="utf-8")
