# Task 15 — Product Count Analysis
**Track:** Data Analytics | **Tool:** Excel

## Objective
Count products by category, identify the largest category, and practice
`COUNTIF` / `COUNTIFS`.

## Dataset
- **File:** `SampleSuperstore.csv`
- **Raw rows:** 9,994
- **Columns:** Ship Mode, Segment, Country, City, State, Postal Code, Region,
  Category, Sub-Category, Sales, Quantity, Discount, Profit

### ⚠️ Important assumption — no Product Name/ID column
This version of the Superstore dataset does **not** include a Product Name
or Product ID field (only `Category` and `Sub-Category`). So "product" in
this task is treated as **one order-line row** (a category/sub-category
purchase record), not an individual SKU. This is documented here so the
counts are interpreted correctly — they measure *order-line volume per
category*, not *how many distinct SKUs* exist.

## Preprocessing done
- Checked for missing values → **none found**.
- Checked for exact duplicate rows → **17 found and removed**
  (9,994 → **9,977** rows). Deduplication matters here because a duplicate
  row would double-count a "product" that was only actually recorded once.
- Cleaned file saved as `SampleSuperstore_clean.csv` and loaded into the
  `Data` tab of the workbook.

## Deliverable
**`Product_Count_Analysis.xlsx`** — two tabs:

### 1. `Data`
The cleaned dataset (9,977 rows), used as the source for every formula.

### 2. `Product_Counts`
- **Section 1 — Product Count by Category** (`COUNTIF`): count and % of
  total for each of the 3 categories.
- **Top Category callout**: `Office Supplies` — **6,012 records (60.3% of
  total)** — found dynamically with `INDEX`/`MATCH` on the max count, so it
  updates automatically if the data changes.
- **Section 2 — Product Count by Category & Sub-Category** (`COUNTIFS`):
  all 17 sub-categories, with a % share within their parent category.
- **Section 3 — Unique Product Records Check**: a reconciliation formula
  confirming the category counts sum back to the total row count
  (`MATCH`), i.e. the "check unique products" step from the task hint.

Results:
| Category | Product Count | % of Total |
|---|---|---|
| Furniture | 2,118 | 21.2% |
| Office Supplies | 6,012 | 60.3% |
| Technology | 1,847 | 18.5% |
| **Total** | **9,977** | **100%** |

**Top category: Office Supplies**, driven mainly by Binders (1,522) and
Paper (1,359) sub-categories.

All formulas were recalculated with LibreOffice (0 errors across 47
formulas) and cross-checked against an independent pandas `groupby` on the
same cleaned CSV — figures match exactly.

## Interview questions

**COUNTIF vs COUNTIFS?**
- `COUNTIF(range, criterion)` counts cells in **one range matching one
  condition** — e.g. `=COUNTIF(Category, "Furniture")` counts every row
  where Category is Furniture.
- `COUNTIFS(range1, criterion1, range2, criterion2, ...)` counts rows that
  satisfy **multiple conditions across multiple ranges simultaneously**
  (AND logic) — e.g. `=COUNTIFS(Category, "Furniture", Sub-Category,
  "Chairs")` counts only rows that are both Furniture *and* Chairs.
  `COUNTIF` can't do that; you'd need to nest or combine conditions
  manually. `COUNTIFS` is the generalized version — `COUNTIF` is really
  `COUNTIFS` with just one condition.

**Why count unique products?**
Counting unique products (rather than total rows/transactions) tells you
the **breadth of the catalog** — how many distinct items you actually sell
— as opposed to sales *volume*. This matters because:
- A category can have high transaction volume from just a few popular
  products (concentration risk) or from a wide, diverse product range.
- Unique counts feed inventory and catalog decisions (what to stock, what
  to discontinue) differently than transaction counts feed sales/revenue
  decisions.
- Duplicate or repeated rows inflate a simple row count without adding any
  real product variety — so deduplicating before counting "unique
  products" avoids overstating catalog size. (In this dataset, since there's
  no Product ID, we approximate this by ensuring no duplicate order-lines
  are double-counted — see the Preprocessing section above.)

## How to re-verify
1. Open `Product_Count_Analysis.xlsx`.
2. Edit any `Category` or `Sub-Category` value on the `Data` tab — every
   count, percentage, and the Top Category callout on `Product_Counts`
   recalculates automatically.
3. Confirm the "Check: totals match?" cell in Section 3 still reads `MATCH`.
