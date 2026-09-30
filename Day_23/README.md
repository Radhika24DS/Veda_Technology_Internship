# Task 23 - SQL Window Functions Intro (Northwind)

**Track:** Data Analytics | **Author:** Radhika | **Tool:** SQL (SQLite 3.25+, portable to PostgreSQL / MySQL 8)

## Objective
Learn analytical SQL patterns by applying `ROW_NUMBER`, `RANK`, `DENSE_RANK` and `LAG` to real business questions on the Northwind sales data.

## Dataset
Northwind trading data (1996-07-04 to 1998-05-06):

| File | Rows | Description |
|---|---|---|
| `northwind_orders.csv` | 830 | One row per order: customer, employee, dates, freight, shipping country |
| `northwind_order_details.csv` | 2,155 | One row per product line: product, unit price, quantity, discount |

**Revenue** = `unit_price x quantity x (1 - discount)` (freight excluded). Total revenue = **1,265,793** across 89 customers.

## Project structure
```
task23/
├── README.md
├── northwind.db                      # SQLite database built from cleaned data
├── data/
│   ├── raw/                          # original CSVs (untouched)
│   └── cleaned/                      # orders_clean.csv, order_details_clean.csv, order_summary.csv
├── scripts/
│   ├── 01_preprocess.py              # cleaning + feature engineering -> CSVs + DB
│   └── 02_run_queries.py             # runs every query, saves outputs
├── sql/
│   └── task23_window_functions.sql   # THE 12 QUERIES (main deliverable)
├── outputs/
│   ├── all_query_outputs.md          # every query + its result table
│   └── q1_output.csv ... q12_output.csv
└── docs/
    ├── notes.md                      # concepts, findings, interview answers
    ├── preprocessing_log.txt         # what the cleaning step found / did
    ├── linkedin_post.md
    └── feedback.md
```

## Data preprocessing (summary)
* Parsed text dates into ISO dates; read postal codes as text.
* Trimmed whitespace, standardised IDs, converted blanks to NULL.
* Validated: 0 duplicates, 0 orphan rows, 0 invalid quantity / price / discount, 0 orders shipped before being placed.
* Handled missing values: `shipped_date` (21) kept NULL + `is_shipped` flag; `ship_region` (507) -> "Not Specified"; `ship_postal_code` (19) -> "Not Provided".
* Engineered: `line_total`, `order_revenue`, `order_year/quarter/month`, `year_month`, `days_to_ship`, `shipped_late`, `is_partial_month`.
* Built `order_summary` (one row per order) so window functions run at order grain.

Full log: `docs/preprocessing_log.txt`.

## The 12 queries

| # | Function | Business question |
|---|---|---|
| 1 | ROW_NUMBER | First order of every customer |
| 2 | ROW_NUMBER | Top 3 highest-value orders per country |
| 3 | ROW_NUMBER | Latest order per customer and days since (recency) |
| 4 | RANK | Top 10 customers by revenue + % of total |
| 5 | ROW_NUMBER vs RANK vs DENSE_RANK | Customers by order count (tie comparison) |
| 6 | RANK + PARTITION BY | Employee ranking within each year |
| 7 | DENSE_RANK + PARTITION BY | Top 3 products by revenue each year |
| 8 | LAG | Month-over-month revenue growth |
| 9 | LAG | Days between a customer's consecutive orders |
| 10 | LAG | Is each order larger or smaller than the previous one? |
| 11 | LAG + PARTITION BY | Quarter-over-quarter revenue for top employees |
| 12 | LAG + RANK + running SUM | Rank months by growth with cumulative revenue |

## Headline findings
* Just three customers (QUICK, ERNSH, SAVEA) generate about **25%** of revenue; the top 10 generate about **45%**.
* Monthly revenue grew from roughly **26k (Aug-1996)** to **124k (Apr-1998)**.
* **Product 38** is the #1 revenue product in every year.
* **Dec-1997** was the strongest month-over-month jump (**+64%**), straight after a -35% dip.
* Customers order about every **24-40 days** (sample: ERNSH, QUICK, SAVEA); one customer (CENTC) has been silent for 657 days.

## How to reproduce
```bash
pip install pandas tabulate
python scripts/01_preprocess.py     # cleans data, builds northwind.db
python scripts/02_run_queries.py    # runs sql/task23_window_functions.sql, writes outputs/
```
Or open `northwind.db` in DB Browser for SQLite / DBeaver and run the `.sql` file directly.

## Notes & limitations
* First and last months (Jul-1996, May-1998) are partial; growth rates for those months should not be compared (flagged in Q8, excluded in Q12).
* Only orders and order-details tables were supplied, so analysis uses customer / employee / product IDs rather than names.
* Sample queries use `LIMIT` or a country / customer filter to keep outputs readable; remove them to see the full result.

## Interview quick answers
* **RANK vs DENSE_RANK:** both give ties the same rank; RANK skips the next number(s) (1,2,2,4), DENSE_RANK does not (1,2,2,3).
* **When to use LAG:** to compare a row with a previous row - growth %, time between events, up/down trends.

See `docs/notes.md` for detailed explanations.
