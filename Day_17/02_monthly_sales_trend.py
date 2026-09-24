"""
Task 17 - Monthly Sales Trend (Superstore)
Summarise sales by month and visualise the trend with a line chart.
Input : SampleSuperstore_with_OrderDate.csv  (created by 01_add_order_dates.py)
Output: monthly_sales_table.csv, monthly_sales_trend.png
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

# ---- 1. Load and convert dates correctly (explicit format, fail loudly) ----
df = pd.read_csv("SampleSuperstore_with_OrderDate.csv")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%Y-%m-%d", errors="raise")
assert df["Order Date"].notna().all()

# ---- 2. Group by month (year + month together) ----
monthly = (df.groupby(df["Order Date"].dt.to_period("M"))["Sales"]
             .sum()
             .sort_index()                       # chronological order
             .rename("Sales")
             .to_frame())

# a month with no orders would silently vanish, so make sure none are missing
full_range = pd.period_range(monthly.index.min(), monthly.index.max(), freq="M")
assert len(full_range) == len(monthly), "Some months are missing"

monthly["MoM Change %"] = monthly["Sales"].pct_change() * 100
monthly["3-Month Moving Avg"] = monthly["Sales"].rolling(3).mean()
monthly.index.name = "Month"

table = monthly.reset_index()
table["Month"] = table["Month"].dt.to_timestamp()      # first day of month
num_cols = ["Sales", "MoM Change %", "3-Month Moving Avg"]
out = table.copy()                       # rounded copy for saving/printing only
out[num_cols] = out[num_cols].round(2)
out.to_csv("monthly_sales_table.csv", index=False, date_format="%Y-%m")

print(out.to_string(index=False))
print("\nTotal sales check:", round(table["Sales"].sum(), 2), "vs", round(df["Sales"].sum(), 2))

# ---- 3. Line chart ----
fig, ax = plt.subplots(figsize=(13, 6))
ax.plot(table["Month"], table["Sales"], marker="o", markersize=4.5, linewidth=2,
        color="#1f5fa8", label="Monthly sales")
ax.plot(table["Month"], table["3-Month Moving Avg"], linewidth=2, linestyle="--",
        color="#e07b00", label="3-month moving average")

peak = table.loc[table["Sales"].idxmax()]
low = table.loc[table["Sales"].idxmin()]
ax.annotate(f"Peak: {peak['Month']:%b %Y}\n${peak['Sales']:,.0f}",
            (peak["Month"], peak["Sales"]), xytext=(-95, -10), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9)
ax.annotate(f"Low: {low['Month']:%b %Y}\n${low['Sales']:,.0f}",
            (low["Month"], low["Sales"]), xytext=(20, 25), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="gray"), fontsize=9)

ax.set_title("Superstore - Monthly Sales Trend (Jan 2014 - Dec 2017)", fontsize=14, weight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Sales (USD)")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.3)
ax.legend(loc="upper left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.tight_layout()
plt.savefig("monthly_sales_trend.png", dpi=150)
print("Saved monthly_sales_trend.png")
