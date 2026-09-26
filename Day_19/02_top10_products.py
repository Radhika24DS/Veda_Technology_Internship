"""
Task 19 - Top 10 Products by Sales
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---- 1. Load & clean ----
df = pd.read_csv("SampleSuperstore_with_ProductName.csv", encoding="utf-8")
before = len(df)
df = df.drop_duplicates()
df["Product Name"] = df["Product Name"].str.strip()
print(f"Rows: {before} -> {len(df)} after removing duplicates")
print("Unique products:", df["Product Name"].nunique())

# ---- 2. Aggregate to product level (a product can appear on many order lines) ----
prod = (df.groupby(["Product Name", "Category", "Sub-Category"])
          .agg(Sales=("Sales", "sum"),
               Profit=("Profit", "sum"),
               Quantity=("Quantity", "sum"),
               Orders=("Sales", "size"))
          .reset_index())

# ---- 3. Rank with explicit tie handling ----
# 'min' method: equal sales get the SAME rank, and the next rank skips
# (e.g. two products tied at rank 5 -> both get 5, next product gets 7)
prod["Sales Rank"] = prod["Sales"].rank(ascending=False, method="min").astype(int)
prod = prod.sort_values(["Sales Rank", "Product Name"], ascending=[True, True])

n_ties = prod["Sales"].duplicated(keep=False).sum()
print(f"\nProducts sharing an exact sales value with another product: {n_ties}")

top10 = prod[prod["Sales Rank"] <= 10].copy()
print(f"\nTop 10 by rank <= 10 -> {len(top10)} rows (10 unless a tie sits on the boundary)")

out = top10[["Sales Rank", "Product Name", "Category", "Sub-Category",
             "Sales", "Profit", "Quantity", "Orders"]].copy()
out["Sales"] = out["Sales"].round(2)
out["Profit"] = out["Profit"].round(2)
out.to_csv("top10_products.csv", index=False)
print("\n", out.to_string(index=False))

total_sales = df["Sales"].sum()
print(f"\nTop 10 share of total sales: {top10['Sales'].sum()/total_sales*100:.1f}% "
      f"(${top10['Sales'].sum():,.2f} of ${total_sales:,.2f})")

# ---- 4. Chart ----
plot_df = out.sort_values("Sales", ascending=True)
labels = [n if len(n) <= 40 else n[:37] + "..." for n in plot_df["Product Name"]]

fig, ax = plt.subplots(figsize=(11, 7))
bars = ax.barh(labels, plot_df["Sales"], color="#1f5fa8")
for bar, v in zip(bars, plot_df["Sales"]):
    ax.annotate(f"${v:,.0f}", (v, bar.get_y() + bar.get_height()/2),
                xytext=(5, 0), textcoords="offset points", va="center", fontsize=9)

ax.set_title("Top 10 Products by Sales", fontsize=14, weight="bold")
ax.set_xlabel("Sales (USD)")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.grid(axis="x", alpha=0.3)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("top10_products_chart.png", dpi=150)
print("Saved top10_products_chart.png")
