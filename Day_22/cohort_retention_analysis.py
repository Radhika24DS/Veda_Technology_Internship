"""
Task 22 - Cohort Retention Basics (Online Retail II)
Cohort  = month of a customer's FIRST purchase (acquisition/"signup" proxy)
Window  = calendar month offsets (M0 = cohort month, M1 = next month, ...)
Retained in Mn = customer placed >=1 valid order in month (cohort month + n)
"""
import sqlite3
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

RAW = "/mnt/user-data/uploads/online_retail_II.csv"
OUT = "/mnt/user-data/outputs"

# ---------------- 1. LOAD ----------------
df = pd.read_csv(RAW, dtype={"Invoice": str, "StockCode": str},
                 parse_dates=["InvoiceDate"])
df.columns = ["invoice", "stock_code", "description", "quantity",
              "invoice_date", "price", "customer_id", "country"]
log = [("Raw rows", len(df))]

# ---------------- 2. CLEAN ----------------
df = df.dropna(subset=["customer_id"]);            log.append(("After dropping missing Customer ID", len(df)))
df = df[~df.invoice.str.startswith(("C", "A"))];   log.append(("After removing cancellations (C) / adjustments (A)", len(df)))
df = df[(df.quantity > 0) & (df.price > 0)];       log.append(("After removing qty<=0 or price<=0", len(df)))
df = df.drop_duplicates();                         log.append(("After removing exact duplicates", len(df)))
# Dec-2011 is a partial month (data ends 9 Dec) -> drop it so every retention window is a full calendar month
df = df[df.invoice_date < "2011-12-01"];           log.append(("After dropping incomplete month (Dec-2011)", len(df)))
df["customer_id"] = df.customer_id.astype(int)
df["description"] = df.description.str.strip().str.upper()
df["revenue"] = df.quantity * df.price
df["order_month"] = df.invoice_date.dt.to_period("M").dt.to_timestamp()
pd.DataFrame(log, columns=["step", "rows"]).to_csv(f"{OUT}/data/cleaning_log.csv", index=False)
df.to_csv(f"{OUT}/data/online_retail_clean.csv.gz", index=False, compression="gzip")

# ---------------- 3. COHORTS (pandas) ----------------
df["cohort_month"] = df.groupby("customer_id").order_month.transform("min")
df["month_index"] = ((df.order_month.dt.year - df.cohort_month.dt.year) * 12
                     + df.order_month.dt.month - df.cohort_month.dt.month)

counts = (df.groupby(["cohort_month", "month_index"]).customer_id.nunique()
            .unstack(fill_value=0))
# cells beyond the dataset end are "not observable" -> NaN (not 0)
last = df.order_month.max()
for c in counts.index:
    max_obs = (last.year - c.year) * 12 + last.month - c.month
    counts.loc[c, counts.columns > max_obs] = np.nan
retention = counts.div(counts[0], axis=0) * 100
counts.index = retention.index = counts.index.strftime("%Y-%m")
counts.to_csv(f"{OUT}/data/cohort_counts.csv")
retention.round(1).to_csv(f"{OUT}/data/cohort_retention_pct.csv")

# ---------------- 4. SQL CROSS-CHECK (SQLite) ----------------
con = sqlite3.connect(":memory:")
df[["invoice", "customer_id", "invoice_date"]].assign(
    invoice_date=df.invoice_date.dt.strftime("%Y-%m-%d %H:%M:%S")
).to_sql("orders", con, index=False)
sql = open(f"{OUT}/sql/cohort_retention.sql").read()
sql_res = pd.read_sql(sql, con)
sql_res.to_csv(f"{OUT}/data/sql_cohort_output.csv", index=False)
piv = sql_res.pivot(index="cohort_month", columns="month_index", values="active_customers")
piv = piv.reindex(counts.index)
match = np.allclose(piv.fillna(0).values, counts.fillna(0).values[:, :piv.shape[1]])
print("SQL result matches pandas cohort table:", match)

# ---------------- 5. HEATMAP ----------------
fig, ax = plt.subplots(figsize=(16, 10))
hm = retention.drop(columns=0)
annot = hm.round(0).astype("Int64").astype(str).replace("<NA>", "")
ylabels = [f"{c}  (n={int(n):,})" for c, n in counts[0].items()]
sns.heatmap(hm, mask=hm.isna(), annot=annot, fmt="", cmap="YlGnBu", vmin=0, vmax=50,
            linewidths=.5, yticklabels=ylabels, cbar_kws={"label": "Retention % of cohort (M0 = 100%)"}, ax=ax)
ax.set_title("Monthly Customer Retention by First-Purchase Cohort - Online Retail II", fontsize=15, pad=14)
ax.set_xlabel("Months since first purchase"); ax.set_ylabel("Cohort (first purchase month)")
plt.yticks(rotation=0); plt.tight_layout()
plt.savefig(f"{OUT}/images/cohort_retention_heatmap.png", dpi=150); plt.close()

# ---------------- 6. EXTRA CHARTS ----------------
avg = retention.drop(columns=0).mean()
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(avg.index, avg.values, marker="o", color="#1f77b4")
ax.set_title("Average Retention Curve across Cohorts"); ax.set_xlabel("Months since first purchase")
ax.set_ylabel("Avg retention %"); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(f"{OUT}/images/avg_retention_curve.png", dpi=150); plt.close()

fig, ax = plt.subplots(figsize=(12, 4.5))
counts[0].plot.bar(ax=ax, color="#2a9d8f"); ax.set_title("New Customers per Cohort (M0 size)")
ax.set_ylabel("Customers"); plt.tight_layout()
plt.savefig(f"{OUT}/images/cohort_sizes.png", dpi=150); plt.close()

# ---------------- 7. INSIGHT NUMBERS ----------------
print(pd.DataFrame(log, columns=["step", "rows"]))
print("Customers:", df.customer_id.nunique(), "| Range:", df.invoice_date.min(), "->", df.invoice_date.max())
print("\nCohort sizes:\n", counts[0].astype(int).to_string())
print("\nAvg retention (M1..M12):\n", avg.head(12).round(1).to_string())
print("\nM1 by cohort:\n", retention[1].round(1).to_string())
print("\nM12 by cohort:\n", retention[12].dropna().round(1).to_string())
pd.set_option("display.width", 250)
print(retention.round(1).iloc[:, :14].to_string())
