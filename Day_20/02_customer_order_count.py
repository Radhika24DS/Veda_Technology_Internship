"""
Task 20 - Customer Order Count
Count orders per customer (not order lines) and identify frequent buyers.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---- 1. Load & clean ----
df = pd.read_csv("SampleSuperstore_with_CustomerOrder.csv")
before = len(df)
df = df.drop_duplicates()
print(f"Rows (order lines): {before} -> {len(df)} after removing exact duplicate rows")

# IMPORTANT: one Order ID can appear on several rows (one row per product in that
# order). Counting rows would count "5 items in 1 order" as 5 orders. We must
# count DISTINCT Order IDs per customer, not rows.
lines_per_order = df.groupby("Order ID").size()
print(f"Order lines per order: min {lines_per_order.min()}, max {lines_per_order.max()}, "
      f"avg {lines_per_order.mean():.2f}")
print(f"Total order lines: {len(df)} | Distinct orders: {df['Order ID'].nunique()} "
      f"| Distinct customers: {df['Customer ID'].nunique()}")

# ---- 2. Group by Customer ID (Customer Name kept for readability; IDs can collide on name) ----
cust = (df.groupby(["Customer ID", "Customer Name"])
          .agg(Order_Count=("Order ID", "nunique"),
               Order_Lines=("Order ID", "size"),
               Total_Sales=("Sales", "sum"),
               Total_Profit=("Profit", "sum"))
          .reset_index())
cust["Avg_Order_Value"] = cust["Total_Sales"] / cust["Order_Count"]
cust["Items_per_Order"] = cust["Order_Lines"] / cust["Order_Count"]

cust["Order_Count_Rank"] = cust["Order_Count"].rank(ascending=False, method="min").astype(int)
cust = cust.sort_values(["Order_Count_Rank", "Total_Sales"], ascending=[True, False]).reset_index(drop=True)

# reconciliation
assert cust["Order_Lines"].sum() == len(df)
assert np.isclose(cust["Total_Sales"].sum(), df["Sales"].sum())
print(f"\nReconciliation: sum of customer sales = {cust['Total_Sales'].sum():,.2f} "
      f"vs raw data total = {df['Sales'].sum():,.2f}")

out = cust.copy()
for c in ["Total_Sales", "Total_Profit", "Avg_Order_Value", "Items_per_Order"]:
    out[c] = out[c].round(2)
out.to_csv("customer_order_table.csv", index=False)

# ---- 3. Frequent buyers = highest order count ----
max_orders = cust["Order_Count"].max()
top_freq = cust[cust["Order_Count_Rank"] <= 10].copy()
n_tied_at_10 = (cust["Order_Count"] == cust.loc[cust["Order_Count_Rank"] <= 10, "Order_Count"].min()).sum()
print(f"\nMost orders by a single customer: {max_orders}")
print(f"Customers tied for the rank-10 cutoff value: {n_tied_at_10}")

top_freq[["Order_Count_Rank","Customer ID","Customer Name","Order_Count",
          "Total_Sales","Avg_Order_Value"]].round(2).to_csv("top10_frequent_customers.csv", index=False)
print("\nTop 10 by Order Count:\n", top_freq[["Order_Count_Rank","Customer Name","Order_Count","Total_Sales"]].to_string(index=False))

# distribution of order counts
dist = cust["Order_Count"].value_counts().sort_index()
print("\nDistribution of Order Count across customers:\n", dist.to_string())

# ---- 4. Chart: Top 10 customers by order count ----
# top_freq includes every customer tied at the rank-10 cutoff value (26 rows here),
# which is correct for the table but too crowded for a "Top 10" chart. For the chart
# only, break ties with Total Sales (documented) to show exactly 10 bars.
chart10 = cust.head(10).sort_values("Order_Count")
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(chart10["Customer Name"], chart10["Order_Count"], color="#1f5fa8")
for bar, v in zip(bars, chart10["Order_Count"]):
    ax.annotate(str(int(v)), (v, bar.get_y()+bar.get_height()/2), xytext=(5,0),
                textcoords="offset points", va="center", fontsize=9)
ax.set_title("Top 10 Customers by Order Count\n(ties broken by total sales)", fontsize=14, weight="bold")
ax.set_xlabel("Number of distinct orders")
ax.grid(axis="x", alpha=0.3)
for s in ("top","right"):
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("top10_customers_chart.png", dpi=150)
print("Saved top10_customers_chart.png")

# ---- 5. Distribution chart ----
fig2, ax2 = plt.subplots(figsize=(8,5))
ax2.bar(dist.index, dist.values, color="#2ca02c")
ax2.set_title("Distribution: How Many Orders Do Customers Place?", fontsize=13, weight="bold")
ax2.set_xlabel("Number of orders")
ax2.set_ylabel("Number of customers")
ax2.grid(axis="y", alpha=0.3)
for s in ("top","right"):
    ax2.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("order_count_distribution.png", dpi=150)
print("Saved order_count_distribution.png")
