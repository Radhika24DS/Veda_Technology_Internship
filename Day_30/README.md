# Task 30 - Regional Growth Analysis (Superstore)

**Track:** Data Analytics - Veda Technology Internship
**Objective:** Practise period-over-period comparisons (YoY, QoQ, CAGR) and understand why growth rates can mislead.
**Tools:** Python (pandas) for cleaning, SQL (SQLite) for analysis, Excel for the growth table and charts.

> ## Important data note
> `SampleSuperstore.csv` has **no order-date column**, and growth over time needs one.
> To build a working period-over-period pipeline, each row was given a **simulated order date**
> (random, `numpy` seed 42, 2014-01-01 to 2017-12-31). Consequently:
> - Growth figures are **illustrative, not real business trends**. Every chart and sheet that uses them says so.
> - The **region profile** (sales share, margin, discount, loss-making lines) uses no dates and is **real**.
> - If you have the full Superstore file with `Order Date`, replace the date columns and re-run: the SQL and Excel formulas need no changes.

## Deliverables

| Required | File |
|---|---|
| Growth table | `outputs/Task30_Regional_Growth_Analysis.xlsx` (sheet `Growth_Table`, live formulas) and `outputs/growth_table.csv` |
| Chart | `outputs/chart_regional_growth.png` (plus native Excel charts in the workbook) and `outputs/chart_small_base_effect.png` |
| 5 insights | `INSIGHTS.md` (also answers both interview questions) |
| SQL | `sql/growth_queries.sql` (6 queries; results in `outputs/q*.csv`) |

## Repository structure

```
data/        SampleSuperstore.csv (raw), superstore_clean.csv (cleaned + simulated dates)
sql/         growth_queries.sql
scripts/     preprocess.py, run_sql.py, build_xlsx.py, make_charts.py
outputs/     Excel workbook, charts, growth_table.csv, SQL result CSVs
INSIGHTS.md  5 insights + interview answers
```

## Preprocessing steps
1. Loaded 9,994 rows x 13 columns; trimmed text and standardised column names (`Sub-Category` -> `Sub_Category`).
2. Checked nulls (0), non-positive sales (0), discounts outside 0-1 (0).
3. Removed **17 exact duplicate rows** -> **9,977 rows**.
4. Restored `Postal_Code` as a 5-character text field (it is an identifier, not a number).
5. Added `Profit_Margin`, `Loss_Making`.
6. Added simulated `Order_Date_SIMULATED`, `Year`, `Quarter`, `Year_Quarter` (see data note).

## Method
- **Consistent periods:** full calendar years 2014-2017 and calendar quarters; no partial periods are compared.
- **YoY growth** = (Sales this year - Sales prior year) / Sales prior year (SQL `LAG()` window function; Excel `SUMIFS`).
- **CAGR 2014-17** = (Sales 2017 / Sales 2014)^(1/3) - 1.
- **Small-base check:** growth at Region x Category (Excel, threshold is an editable input cell) and Region x Sub-Category (chart),
  flagging cases where the prior-year base is small.

## Results at a glance (simulated periods)

| Region | 2014 | 2015 | 2016 | 2017 | YoY 2015 | YoY 2016 | YoY 2017 | CAGR |
|---|---|---|---|---|---|---|---|---|
| Central | 112,302 | 117,155 | 136,683 | 134,643 | +4.3% | +16.7% | -1.5% | +6.2% |
| East | 194,339 | 190,772 | 149,596 | 143,729 | -1.8% | -21.6% | -3.9% | -9.6% |
| South | 121,936 | 85,381 | 89,697 | 94,708 | -30.0% | +5.1% | +5.6% | -8.1% |
| West | 198,516 | 168,515 | 177,419 | 180,805 | -15.1% | +5.3% | +1.9% | -3.1% |

Real (date-free) profile: West 31.6% of sales at 14.9% margin; Central 21.8% of sales at only 7.9% margin with a 24% average discount.

## How to reproduce
Run from the repository root (Python 3.10+, `pandas`, `numpy`, `openpyxl`, `matplotlib`):
```bash
python3 scripts/preprocess.py data/SampleSuperstore.csv data/superstore_clean.csv
python3 scripts/run_sql.py        # runs sql/growth_queries.sql on SQLite, writes outputs/q*.csv
python3 scripts/make_charts.py
python3 scripts/build_xlsx.py     # then recalculate the workbook in Excel/LibreOffice
```

## Key learnings
- Growth rates need the base and the absolute change next to them.
- Small bases produce extreme, unstable percentages.
- CAGR smooths over the path; one odd year can dominate a region's story.
- Quarterly numbers are noisier than annual ones; compare like-for-like periods.
- Sales growth must be read together with margin and discounting.
