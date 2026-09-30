# Notes - Task 23: SQL Window Functions Intro (Northwind)

## 1. What is a window function?
A window function performs a calculation across a set of rows **related to the current row** - *without collapsing them* the way `GROUP BY` does. Every input row is kept, and a new column is added.

```sql
function_name(...) OVER (
    PARTITION BY <group columns>      -- optional: restart the calculation per group
    ORDER BY <sort columns>           -- defines the order inside each group
    ROWS BETWEEN ... AND ...          -- optional: the frame (used by running totals)
)
```

| Piece | Meaning |
|---|---|
| `PARTITION BY` | Splits rows into independent groups (like GROUP BY, but rows are not collapsed) |
| `ORDER BY` | Order of rows *inside* each partition - required for ranking and LAG |
| Frame (`ROWS BETWEEN`) | Which rows around the current one are included (running totals, moving averages) |

## 2. Ranking functions compared (Q5 is the live demo)
Data: customers ordered by number of orders (ties exist).

| customer | orders | ROW_NUMBER | RANK | DENSE_RANK |
|---|---|---|---|---|
| FOLKO | 19 | 4 | 4 | 4 |
| HUNGO | 19 | 5 | **4** | **4** |
| BERGS | 18 | 6 | **6** (gap) | **5** (no gap) |
| HILAA | 18 | 7 | 6 | 5 |
| RATTC | 18 | 8 | 6 | 5 |
| BONAP | 17 | 9 | 9 | 6 |

* **ROW_NUMBER** - always unique (1,2,3,4...). Ties are split arbitrarily, so add a tiebreaker column to `ORDER BY` for repeatable results.
* **RANK** - ties share a rank and the next rank **skips** (1,2,2,4). Like Olympic medals: two golds, no silver, next is bronze.
* **DENSE_RANK** - ties share a rank and the next rank **does not skip** (1,2,2,3). Use when you want "top N distinct levels".

**Which one to pick?**
* Need exactly one row per group (latest order, first order, de-duplication) -> `ROW_NUMBER`.
* Need a true leaderboard where equal values get equal positions -> `RANK`.
* Need "top 3 distinct tiers/prices/scores" -> `DENSE_RANK`.

## 3. LAG (and LEAD)
`LAG(col, n, default) OVER (PARTITION BY ... ORDER BY ...)` returns the value from **n rows before** the current row (default n = 1). `LEAD` looks forward. The first row in a partition has no previous row, so it returns `NULL` (or the `default` if given).

Typical uses: month-over-month growth, days between events, "did the value go up or down?", detecting churn gaps.

Growth formula used in Q8/Q11/Q12: `(current - LAG(current)) / LAG(current) * 100`

## 4. Query index and key findings

| # | Function | Business question | Key finding |
|---|---|---|---|
| Q1 | ROW_NUMBER | First order of each customer | 89 customers; first orders begin 1996-07-04 (order 10248, VINET) |
| Q2 | ROW_NUMBER | Top 3 orders per country | Biggest single orders: Germany 16,387.50 (QUICK, Feb-1998), Brazil 15,810.00 (HANAR), USA 12,615.05 (SAVEA) |
| Q3 | ROW_NUMBER | Latest order + days since | CENTC has not ordered since 1996-07-18 (657 days before the dataset ends) - biggest churn risk |
| Q4 | RANK | Top customers by revenue | QUICK, ERNSH, SAVEA together = ~25% of all revenue; top 10 = ~45% |
| Q5 | ROW_NUMBER vs RANK vs DENSE_RANK | Customers by order count | Ties at 19, 18, 15 orders show the gap vs no-gap behaviour |
| Q6 | RANK (partition) | Employee ranking per year | Employee 4 is #1 in 1996 and 1997; employee 3 leads 1998 (partial year) |
| Q7 | DENSE_RANK (partition) | Top 3 products per year | Product 38 is #1 every year; its revenue rose 24.9k -> 49.2k -> 67.3k |
| Q8 | LAG | Month-over-month revenue | Monthly revenue grew from ~26k (Aug-1996) to ~124k (Apr-1998); May-1998 is partial (-85% is an artefact) |
| Q9 | LAG | Days between orders | Average gap: ERNSH 24.3 days, QUICK 28.3 days, SAVEA 40.4 days |
| Q10 | LAG | Order bigger/smaller than previous? | 44.3% larger vs 44.9% smaller - order size is essentially random around each customer's mean |
| Q11 | LAG (partition) | Quarter-over-quarter per top employee | Employee 1: +116.4% in 1997-Q3; 1998-Q2 is partial so its drop is not real |
| Q12 | LAG + RANK + running SUM | Rank months by MoM growth | Best month Dec-1997 (+64.0%), right after a -34.8% dip in Nov-1997 |

## 5. Data preprocessing summary
See `docs/preprocessing_log.txt` and `scripts/01_preprocess.py`.

| Issue found | Action |
|---|---|
| Dates stored as text | Converted to real dates; stored as ISO `YYYY-MM-DD` so they sort correctly in SQL |
| 21 orders with NULL `shipped_date` | Kept as NULL (means "not shipped yet"), added `is_shipped` flag |
| 507 NULL `ship_region` | Region does not apply to many countries -> filled with `Not Specified` |
| 19 NULL `ship_postal_code` | Filled with `Not Provided`; column read as text to protect leading zeros |
| No revenue column | Created `gross_amount`, `discount_amount`, `line_total = price x qty x (1-discount)` |
| Need order-level grain | Built `order_summary` (1 row/order: revenue, units, line items) |
| No year/month/quarter fields | Added `order_year`, `order_month`, `order_quarter`, `year_month` |
| Partial first/last months (Jul-1996, May-1998) | Added `is_partial_month` flag so growth is not misread |
| Duplicates, orphans, invalid qty/price/discount, ship-before-order | Checked - **none found** (0 rows removed) |

## 6. Interview questions

**Q. RANK vs DENSE_RANK?**
Both give tied rows the same rank. RANK leaves gaps after a tie (1,2,2,4); DENSE_RANK does not (1,2,2,3). Use RANK for standard leaderboards, DENSE_RANK when you want the "Nth distinct value" (e.g. the 3rd highest salary).

**Q. When do you use LAG?**
When you need to compare a row with an earlier row: month-over-month or year-over-year change, days between consecutive purchases, price change history, or flagging when a value went up or down. It replaces a slow and messy self-join on `date - 1`.

**Bonus Q. Window function vs GROUP BY?**
GROUP BY collapses rows into one per group; a window function keeps every row and adds the calculated value beside it.

**Bonus Q. Why can't I use a window function in WHERE?**
Window functions are evaluated after WHERE / GROUP BY / HAVING. Wrap the query in a CTE or subquery and filter in the outer query (as done in Q1, Q2, Q3, Q7).

## 7. Pitfalls I noticed
* Always put a tiebreaker (e.g. `order_id`) in `ROW_NUMBER`'s ORDER BY, otherwise results can change between runs.
* `LAG` returns NULL for the first row of every partition - handle it (`COALESCE`) or filter it.
* Without `PARTITION BY` the window is the *whole table* - LAG would compare across customers.
* Partial periods at the edge of a dataset distort growth rates.
* `LIMIT` is applied after the window is computed, and can hide groups (this happened while building Q9, fixed by filtering on `ROW_NUMBER`).
* This dataset only has the orders and order-details tables, so results use IDs (customer, employee, product) rather than names.
