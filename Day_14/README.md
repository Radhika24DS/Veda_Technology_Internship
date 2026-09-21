# Task 14 — Basic Sales Summary
**Track:** Data Analytics | **Tool:** Excel

## Objective
Build a basic business summary from a retail transactions dataset: total sales,
average sales, and transaction count, using live formulas (not hardcoded numbers).

## Dataset
- **File:** `retail_sales_dataset.csv`
- **Rows:** 1,000 transactions, no missing values
- **Columns:** Transaction ID, Date, Customer ID, Gender, Age, Product Category,
  Quantity, Price per Unit, Total Amount

## Deliverable
**`Retail_Sales_Summary.xlsx`** — two tabs:

### 1. `Data`
The raw dataset, unmodified, formatted as a table. This is the single source
of truth every formula on the Summary tab pulls from.

### 2. `Summary`
- **3 KPI cards** (the required deliverable), each a live formula against the `Data` tab:
  | KPI | Formula | Result |
  |---|---|---|
  | Total Sales | `=SUM(Data!I2:I1001)` | ₹456,000 |
  | Average Sale Value | `=AVERAGE(Data!I2:I1001)` | ₹456.00 |
  | Transaction Count | `=COUNTA(Data!A2:A1001)` | 1,000 |
- **Sales by Product Category** breakdown table (Total Sales, Transactions,
  Avg Sale Value, % of Total Sales per category), built with `SUMIF` /
  `COUNTIF`, plus a Total row.
- **Manual verification row**: a `MATCH`/`CHECK` formula that confirms the
  category totals sum back to the grand total KPI — this is the "verify
  totals manually" step from the task hint, done as a self-checking formula
  so it stays correct if the data changes.

All formulas were recalculated with LibreOffice and checked for errors
(0 errors across 20 formulas), and cross-checked independently against a
pandas calculation on the same CSV — figures match exactly.

## KPI definitions (interview prep)

**What is a KPI?**
A Key Performance Indicator is a specific, measurable metric used to track
how well a business (or a process within it) is performing against an
objective. A good KPI is quantifiable, tied to a goal, and tracked
consistently over time — here, Total Sales, Average Sale Value, and
Transaction Count are the KPIs that summarize overall sales performance.

**How is average different from total?**
- **Total** is the sum of every value in a range — it answers "how much
  overall?" (Total Sales = ₹456,000, all 1,000 transactions added together).
- **Average** divides that total by the count of values — it answers "how
  much typically, per transaction?" (₹456,000 ÷ 1,000 = ₹456 average sale).

Total scales with volume (more transactions → bigger total even if each
sale is small); average does not — it stays representative of a "typical"
transaction regardless of how many transactions there are. Both are needed
together: total shows scale, average shows typical transaction size.

## How to re-verify
1. Open `Retail_Sales_Summary.xlsx`.
2. Change any value in the `Data` tab — the KPI cards and category table on
   `Summary` recalculate automatically.
3. Check the "Category totals sum to grand total" cell on the `Summary` tab
   still reads `MATCH`.
