# Task 16 — Simple Profit Analysis
**Track:** Data Analytics | **Tool:** Excel

## Objective
Compare total profit across product categories and understand basic
profitability — not just sales volume.

## Dataset
- **File:** `SampleSuperstore.csv`
- **Raw rows:** 9,994
- **Columns:** Ship Mode, Segment, Country, City, State, Postal Code, Region,
  Category, Sub-Category, Sales, Quantity, Discount, Profit

## Preprocessing done
- Checked for missing values → **none found**.
- Checked for exact duplicate rows → **17 found and removed**
  (9,994 → **9,977** rows), same cleaning step as Task 15, so profit totals
  aren't inflated by repeated records.
- Cleaned file saved as `SampleSuperstore_clean.csv` and loaded into the
  `Data` tab of the workbook.

## Deliverable
**`Profit_Analysis.xlsx`** — two tabs:

### 1. `Data`
The cleaned dataset (9,977 rows), used as the source for every formula.

### 2. `Profit_Summary`
- **Profit & Sales by Category table** — `SUMIF`/`COUNTIF`-driven: Total
  Sales, Total Profit, Avg Profit per Order, Profit Margin (Profit ÷
  Sales), and Order Count for each category, plus a Total row.
- **Two callouts**, computed dynamically with `INDEX`/`MATCH` (no
  hardcoding): "Most Profitable" category and "Lowest Margin" category.
- **Two embedded charts** (the required chart deliverable):
  1. *Sales vs Profit by Category* — clustered column chart, showing sales
     and profit side by side per category.
  2. *Profit Margin by Category* — column chart isolating margin %, which
     makes the Furniture problem visible at a glance.

### Results
| Category | Total Sales | Total Profit | Avg Profit/Order | Profit Margin | Orders |
|---|---|---|---|---|---|
| Furniture | $741,306 | $18,422 | $8.70 | **2.5%** | 2,118 |
| Office Supplies | $718,735 | $122,365 | $20.35 | 17.0% | 6,012 |
| Technology | $836,154 | $145,455 | $78.75 | 17.4% | 1,847 |
| **Total** | **$2,296,196** | **$286,241** | **$28.69** | **12.5%** | **9,977** |

**Most profitable: Technology** ($145,455 total profit, highest profit per
order by far). **Lowest margin: Furniture** (2.5%) — despite having the
second-highest sales volume, almost none of it converts to profit. This is
the direct real-data example for the interview question below.

All formulas were recalculated with LibreOffice (0 errors across 22
formulas) and cross-checked against an independent pandas `groupby` on the
same cleaned CSV — figures match exactly.

## Interview questions

**Revenue vs profit?**
- **Revenue (Sales)** is the total money brought in from selling
  products — top-line, before any costs are subtracted.
- **Profit** is what's left after subtracting costs (cost of goods,
  discounts, shipping, overhead, etc.) from revenue — the actual money
  the business keeps.
High revenue doesn't guarantee high profit; a category can sell a lot and
still make little or nothing once costs are accounted for.

**Why can sales be high but profit low?**
This dataset shows it directly: **Furniture** has $741K in sales (2nd
highest) but only $18.4K profit — a 2.5% margin, far below Office Supplies
(17.0%) and Technology (17.4%). Common reasons sales-high/profit-low
happens:
- **Heavy discounting** — large discounts push units out the door but eat
  directly into margin (Furniture, especially Tables, tends to carry steep
  discounts in this dataset).
- **High cost-to-sell items** — bulky/expensive-to-ship products (like
  furniture) have higher fulfillment and logistics costs relative to price.
- **Low markup by design** — some categories are priced competitively with
  thin margins to drive volume, relying on quantity rather than
  per-unit profit.
- **Returns, damage, or overhead** absorbed per order can silently erode
  profit even when the sale itself looks large.
The takeaway: sales volume measures *activity*, profit measures *value
captured* — a category can be busy without being healthy.

## How to re-verify
1. Open `Profit_Analysis.xlsx`.
2. Edit any `Sales`, `Profit`, or `Category` value on the `Data` tab — the
   summary table, both callouts, and both charts on `Profit_Summary`
   recalculate/redraw automatically.
3. Confirm the Total row's Profit Margin still reads 12.5% (or the new
   correct value if you changed data).
