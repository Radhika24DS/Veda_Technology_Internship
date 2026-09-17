# Task 10 — Simple KPI Tracking Sheet
**Track:** Data Analytics | **Dataset:** Sample Superstore (9,994 order lines)

## What this was

Build a one-page KPI summary that pulls straight from raw order data and keeps
recalculating on its own as new rows get added — no manual totals, no
re-pasting numbers every time the data changes.

## Files in this delivery

| File | What it is |
|---|---|
| `Superstore_KPI_Tracker.xlsx` | The KPI sheet itself. Two tabs: `Raw_Data` and `KPI_Summary`. |
| `README.md` | This file. |
| Colab code (below) | Five charts that visualize the same KPIs, for when a picture works better than a number in a cell. |

## Dataset reality check (do this before building anything)

The Superstore file most people expect has an Order ID, Order Date, and
Product Name. **This one doesn't** — it's line-item level: Ship Mode,
Segment, Country, City, State, Postal Code, Region, Category, Sub-Category,
Sales, Quantity, Discount, Profit. No missing values, 9,994 rows, one header
row.

That gap changes two of the KPIs, and I flagged both directly on the
spreadsheet rather than quietly working around them:

- **"Average Order Value"** → since there's no Order ID to group lines into
  orders, this is the average revenue *per line item*. If a version of this
  data with real order IDs shows up later, swap in
  `SUMIFS(Sales, OrderID, x)` grouped by order first.
- **"Top Product"** → no Product Name column exists, so Sub-Category
  (Phones, Chairs, Binders, etc.) is the closest available stand-in.

Pretending the data had columns it doesn't would've made the sheet look more
complete and less trustworthy. Better to say what was actually available.

## What's in `Superstore_KPI_Tracker.xlsx`

### Tab 1 — Raw_Data
The CSV as-is, 9,994 rows, untouched. This is what you paste new orders
into.

### Tab 2 — KPI_Summary (the actual deliverable)

**Section 1 — Key Metrics (all orders)**
| Metric | Formula basis |
|---|---|
| Total Revenue | `SUM` |
| Total Profit | `SUM` |
| Total Units Sold | `SUM` |
| Average Order Value* | `AVERAGE` |
| Overall Profit Margin | Profit ÷ Revenue |
| Top Sub-Category (by Revenue)* | `INDEX` / `MATCH` against a `SUMIFS` helper table |

**Section 2 — Filter by Region**
Type a region into the yellow input cell (South / West / Central / East,
enforced by a dropdown) and four numbers recalculate for that region alone,
via `SUMIFS` / `AVERAGEIFS`. This is the part that most directly answers the
brief's hint to use SUMIFS/AVERAGEIFS instead of manual totals — it's a live
filter, not just a label.

**Section 3 — Category Breakdown**
Furniture / Office Supplies / Technology, each with Revenue, Profit, Units
Sold, and Profit Margin %, all `SUMIFS`-driven.

Currency is formatted `$#,##0`, percentages `0.0%`, consistent throughout —
per the formatting hint in the brief.

### How the "recalculates automatically" part actually works

Every formula reads `Raw_Data` rows 2 through 20,000, not just the 9,994
rows that currently have data. Blank rows don't distort `SUM`, `AVERAGE`,
`SUMIFS`, or `AVERAGEIFS` — they're just skipped. So you can paste new
orders straight below row 9,995 and every KPI on the summary tab updates
without touching a single formula.

**I tested this, not just assumed it.** Added a dummy $5,000 / 10-unit order
at row 9,996, recalculated the workbook, and confirmed Total Revenue moved
from $2,297,200.86 → $2,302,200.86 and Total Units from 37,873 → 37,883 —
exactly the expected deltas, with zero formula errors. The one caveat: new
rows have to go *below* the last existing row, not inserted above it, or the
range references shift.

All 39 formulas in the workbook were recalculated with LibreOffice and
checked for errors (`0 errors`), and every headline number was
cross-verified against an independent `pandas` groupby before shipping.

## Colab visuals (optional companion, not a replacement for the sheet)

Five charts covering the same ground as the KPI tabs, plus one diagnostic
chart that came out of actually looking at the numbers rather than
following the brief mechanically:

1. **Revenue & Profit by Category** — bar chart, mirrors Section 3 of the
   sheet.
2. **Revenue by Region** — bar chart, mirrors Section 2's filter.
3. **Top 10 Sub-Categories by Revenue** — horizontal bar, mirrors the "Top
   Product" KPI.
4. **Profit Margin by Category** — horizontal bar, margins under 5%
   highlighted red. This is where Furniture's problem becomes visible at a
   glance (2.5% margin vs. Office Supplies' 17%).
5. **Discount vs. Profit scatter** — *not* one of the five core KPIs, added
   because the margin chart above raises an obvious "why," and this answers
   it: heavy discounting is dragging a chunk of Furniture orders into the
   red. Left it in because a KPI sheet that only reports numbers without
   room for the next question isn't that useful in practice.

Full code for all six cells was shared earlier in this conversation — copy
each block into its own Colab cell, upload `SampleSuperstore.csv` when
prompted in Cell 1, and run top to bottom.

## Interview questions

**How would you decide which KPIs matter most for a small retail business?**
Start from the decision, not the data — if a number wouldn't change what you
do next, it doesn't earn a spot on a one-page sheet. Revenue and units tell
you whether the business is growing; margin tells you whether that growth
is actually worth anything, which is why it sits right next to revenue here
instead of being an afterthought — plenty of small retailers grow the top
line while margin quietly erodes. Past that, one segmentation cut that
matches how the business is actually managed (region, category, whatever
the owner already thinks in) beats five different headline numbers nobody
checks day to day.

**How do you keep a KPI sheet accurate as new data comes in?**
Two failure modes show up in practice more than anything else: someone
inserts new rows in the *middle* of the data instead of appending at the
bottom, which shifts every range reference out from under the formulas; and
someone hardcodes a number "just this once" during a rush, and it never
gets fixed. The generous-range trick (formulas reaching well past the
current data) solves the first one structurally. The second is more of a
discipline problem than a technical one — the real fix is making sure
there's never a faster path to the number than the formula that's already
sitting there.
