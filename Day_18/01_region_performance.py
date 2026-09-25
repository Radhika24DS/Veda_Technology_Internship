"""
Task 18 - Region Performance
Compare sales and profit across regions, rank them, and chart the comparison.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ---- 1. Load & basic cleaning ----
df = pd.read_csv("SampleSuperstore.csv", encoding="latin1")
before = len(df)
df = df.drop_duplicates()
df["Region"] = df["Region"].str.strip()
assert df[["Region", "Sales", "Profit", "Quantity"]].isna().sum().sum() == 0
print(f"Rows: {before} -> {len(df)} after removing duplicates")
print("Regions:", sorted(df["Region"].unique()))

# ---- 2. Region summary ----
summary = (df.groupby("Region")
             .agg(Orders=("Region", "size"),
                  Sales=("Sales", "sum"),
                  Profit=("Profit", "sum"),
                  Quantity=("Quantity", "sum"))
             .reset_index())

summary["Profit Margin %"] = summary["Profit"] / summary["Sales"] * 100
summary["Avg Sale Value"] = summary["Sales"] / summary["Orders"]
summary["Sales Rank"] = summary["Sales"].rank(ascending=False).astype(int)
summary["Profit Rank"] = summary["Profit"].rank(ascending=False).astype(int)
summary = summary.sort_values("Sales", ascending=False).reset_index(drop=True)

# Reconciliation
assert np.isclose(summary["Sales"].sum(), df["Sales"].sum())
assert np.isclose(summary["Profit"].sum(), df["Profit"].sum())
print(f"\nTotal sales check: {summary['Sales'].sum():,.2f} vs {df['Sales'].sum():,.2f}")

out = summary.copy()
for c in ["Sales", "Profit", "Avg Sale Value"]:
    out[c] = out[c].round(2)
out["Profit Margin %"] = out["Profit Margin %"].round(2)
out.to_csv("region_summary.csv", index=False)
print("\n", out.to_string(index=False))

# ---- 3. Also produce a Power-BI-ready cleaned row-level export ----
pbi_cols = ["Ship Mode", "Segment", "Country", "City", "State", "Postal Code",
            "Region", "Category", "Sub-Category", "Sales", "Quantity", "Discount", "Profit"]
df[pbi_cols].to_csv("SampleSuperstore_cleaned_for_PowerBI.csv", index=False)
print("\nSaved SampleSuperstore_cleaned_for_PowerBI.csv:", df.shape)

# ---- 4. Bar chart: Sales vs Profit by region ----
regions = summary["Region"]
x = np.arange(len(regions))
w = 0.38

fig, ax = plt.subplots(figsize=(10, 6))
b1 = ax.bar(x - w/2, summary["Sales"], width=w, label="Sales", color="#1f5fa8")
b2 = ax.bar(x + w/2, summary["Profit"], width=w, label="Profit", color="#2ca02c")

for bars in (b1, b2):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"${h:,.0f}", (bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=8.5)

ax.set_xticks(x)
ax.set_xticklabels(regions)
ax.set_ylabel("USD")
ax.set_title("Region Performance: Sales vs Profit", fontsize=14, weight="bold")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.legend()
ax.grid(axis="y", alpha=0.3)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("region_sales_vs_profit.png", dpi=150)
print("Saved region_sales_vs_profit.png")

# ---- 5. Profit margin chart (bonus, supports ranking discussion) ----
fig2, ax2 = plt.subplots(figsize=(8, 5))
order = summary.sort_values("Profit Margin %", ascending=False)
colors = ["#2ca02c" if v == order["Profit Margin %"].max() else "#1f5fa8" for v in order["Profit Margin %"]]
bars = ax2.bar(order["Region"], order["Profit Margin %"], color=colors)
for bar, v in zip(bars, order["Profit Margin %"]):
    ax2.annotate(f"{v:.1f}%", (bar.get_x()+bar.get_width()/2, v), xytext=(0,3),
                 textcoords="offset points", ha="center", fontsize=9)
ax2.set_title("Profit Margin % by Region", fontsize=13, weight="bold")
ax2.set_ylabel("Profit Margin (%)")
ax2.grid(axis="y", alpha=0.3)
for s in ("top","right"):
    ax2.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("region_profit_margin.png", dpi=150)
print("Saved region_profit_margin.png")
