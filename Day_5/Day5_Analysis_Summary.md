# Excel Data Analysis — Sample Superstore Dataset
**Level 1, Day 5 — Data Analytics Track**

## Objective
Analyze a structured retail dataset end-to-end using core Excel tools — formulas, PivotTables, and KPIs — to answer real business questions.

## Dataset
Sample Superstore dataset — 9,994 order line items across Category, Sub-Category, Region, State, Segment, and Ship Mode, with Sales, Quantity, Discount, and Profit for each line.

While reviewing the data before building anything, I noted two things worth flagging:
- There's no Order Date or Order ID column in this file, so a month-by-month sales trend isn't something this dataset can support. I built two other pivots in its place (Sub-Category, and Top 10 States) that the available fields actually answer well.
- There are 17 exact duplicate rows. I left the raw data untouched rather than removing them, since I can't confirm from the fields available whether they're genuine repeat line items or true duplicates.

## Workbook structure
The workbook (`Day5_Excel_Data_Analysis.xlsx`) has four tabs:

**1. Raw_Data** — all 9,994 rows, left exactly as provided. Header row frozen, formatted as an Excel Table, and covered by a named range (`RawData`) so anything built on top of it — formulas or PivotTables — keeps working automatically if more rows get added later.

**2. Working_Formulas** — every KPI here is a live formula, nothing typed in by hand:
- **Core KPIs:** Total Sales, Total Profit, Total Line Items, Total Units Sold, Avg Sale/Line, Profit Margin %, Avg Discount, Loss-Making Lines — built with `SUM`, `AVERAGE`, `COUNTA`, `COUNTIF`.
- **Category / Region / Segment breakdowns:** Sales, Profit, Count, Avg Sale, and Margin per group, using `SUMIFS`, `COUNTIFS`, and `AVERAGEIFS` throughout — no array formulas anywhere, per the brief's hint.

**3. PivotTables** — five tables, each answering a different business question:
1. Sales & Profit by Category (with % of total sales and a grand total row)
2. Sales & Profit by Region
3. Sales & Profit by Sub-Category, sorted highest to lowest
4. Top 10 States by Sales
5. A Segment × Category cross-tab (two-way pivot showing sales for every segment/category combination, with row and column totals)

**4. Summary** — a one-screen KPI dashboard, a Best & Worst Performers table (using `INDEX`/`MATCH` to pull out the top category, top region, and weakest category by profit), and the written findings below.

## Key findings

Across 9,994 order line items, the dataset generated **$2,297,201** in total sales and **$286,397** in profit — a blended margin of **12.5%**. **Technology** led all categories with **$836,154** in sales, driven mainly by Phones, but **Furniture** posted the weakest profit of any category at just **$18,451** despite similar sales volume — a clear sign of discount-driven margin erosion rather than a demand problem. **West** was the strongest region overall, and **California** was the single best-performing state at **$457,688** in sales. **1,871 line items (18.7%)** were sold at a loss, which stood out as the single biggest profitability risk in the data — worth a closer look at discount thresholds by category.

## Interview questions

**When would you use SUMIFS vs. a PivotTable for the same question?**
SUMIFS is better when I need one specific number to plug into another formula or a dashboard cell — it's precise and easy to audit. A PivotTable is better for open-ended exploration, where I don't know the exact cut I need yet and want to drag fields around, add a second dimension, or filter interactively on the fly.

**How do you keep a PivotTable's source data "live" as new rows are added?**
Convert the source range into an Excel Table (Ctrl+T) before building the PivotTable, or base it on a named range. Either way, new rows appended inside that range are picked up automatically — no manual "change data source" step required.

**What's a KPI you'd track for a retail dataset, and why?**
Profit Margin % alongside raw sales. This dataset is a good example of why: Technology looks like the top performer by revenue, but the real story only shows up when you check profit — Furniture is quietly the weakest category despite comparable sales, and revenue numbers alone would completely hide that.
