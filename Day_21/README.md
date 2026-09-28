# Task 21 – Basic SQL SELECT (Northwind)

**Track:** Data Analytics  |  **Author:** Radhika  |  **Tools:** PostgreSQL / MySQL, Python (pandas) for preprocessing

## 🎯 Objective
Build SQL fundamentals by writing simple `SELECT`, `WHERE` and `ORDER BY` queries on a real business dataset.

## 📦 Dataset
Northwind trading company – two tables:

| Table | Rows | Description |
|---|---|---|
| `orders` | 830 | One row per order: customer, dates, freight, shipping city/country |
| `order_details` | 2,155 | One row per product line in an order: price, quantity, discount |

Coverage: orders from **1996-07-04 to 1998-05-06**, shipped to **21 countries**. `order_id` links the two tables.

## 🧹 Data Preprocessing
Script: `scripts/01_preprocess.py` → log in `data/cleaning_log.txt`

| # | Step | Result |
|---|---|---|
| 1 | Trimmed whitespace in all text columns | No issues found |
| 2 | Blank strings converted to real `NULL` | `shipped_date` 21, `ship_region` 507, `ship_postal_code` 19 |
| 3 | Converted dates to `DATE`; numeric columns to int / float | No parse errors |
| 4 | Checked duplicates, duplicate keys and orphan foreign keys | 0 found |
| 5 | Validated business rules (shipped ≥ order date, required ≥ order date, freight/qty/price > 0, 0 ≤ discount ≤ 1) | All passed |
| 6 | Missing-value policy | Kept as `NULL` (not imputed): missing region = not applicable, missing shipped date = not shipped yet |
| 7 | Added derived columns | `orders.days_to_ship`, `orders.shipped_late`, `order_details.line_total` |

Final clean files: `data/orders_clean.csv` (830 × 16) and `data/order_details_clean.csv` (2,155 × 6).

## 📁 Project Structure
```
Task21_Basic_SQL_Select/
├── README.md
├── LinkedIn_Post.md
├── Feedback.md
├── Interview_Answers.md
├── data/
│   ├── orders_clean.csv
│   ├── order_details_clean.csv
│   └── cleaning_log.txt
├── sql/
│   ├── 01_schema_postgresql.sql
│   ├── 01_schema_mysql.sql
│   └── 02_task21_queries.sql        ← the 10 queries
├── outputs/
│   ├── query_outputs.md             ← all queries + results in one file
│   └── q01_result.csv … q10_result.csv
└── scripts/
    ├── 01_preprocess.py
    └── 02_run_queries.py
```

## ▶️ How to Run
**PostgreSQL**
```bash
createdb northwind_task21
psql -d northwind_task21 -f sql/01_schema_postgresql.sql   # run from the project root
psql -d northwind_task21 -f sql/02_task21_queries.sql
```
**MySQL 8**
```bash
mysql --local-infile=1 -u root -p < sql/01_schema_mysql.sql   # run from the project root
mysql -u root -p northwind_task21 < sql/02_task21_queries.sql
```
**Re-create preprocessing and outputs (optional)**
```bash
pip install pandas tabulate
python scripts/01_preprocess.py <folder_with_raw_csvs>
python scripts/02_run_queries.py
```

## 🧾 The 10 Queries
| # | Query | Concepts |
|---|---|---|
| Q1 | First 10 orders | `SELECT *`, `ORDER BY`, `LIMIT` |
| Q2 | Earliest orders with chosen columns | Column list, `ORDER BY ASC` (2 keys) |
| Q3 | German orders, highest freight first | `WHERE =`, `ORDER BY DESC` |
| Q4 | Countries Northwind ships to | `DISTINCT` |
| Q5 | 1997 orders with freight > 100 | `WHERE`, `AND`, `BETWEEN` |
| Q6 | Unshipped orders to France / Spain / Italy | `IN`, `IS NULL` |
| Q7 | Cities starting with "S" | `LIKE`, multi-column `ORDER BY` |
| Q8 | Bulk discounted order lines | `WHERE` with two numeric conditions |
| Q9 | Top 10 order lines by revenue | Calculated column, alias, `ROUND` |
| Q10 | Orders shipped after required date | Comparing two columns |

Full SQL is in `sql/02_task21_queries.sql`; full results are in `outputs/query_outputs.md`.

## 🔍 Findings from the Queries
- Northwind ships to **21 countries**; Germany and the USA have the most orders (122 each).
- The single most expensive shipment was order **10540** (Germany, customer QUICK) with freight of **1,007.64**. QUICK, based in Cunewalde, appears in 8 of the top 10 German freight charges.
- **37 orders** were shipped after their required date, and **21 orders** had not shipped at all. Of those, 3 were bound for France or Italy (Q6).
- The largest discounted bulk lines reach **130 units** (order 10764) and discounts of up to **25%** (Q8).
- Product **38** accounts for 9 of the top 10 revenue lines, with a highest line value of **15,810** (Q9).

## 🎓 Interview Questions
See `Interview_Answers.md`.

## ✅ Skills Demonstrated
Data cleaning and validation · SELECT / WHERE / ORDER BY · filtering with AND, IN, BETWEEN, LIKE, IS NULL · calculated columns and aliases · clear query formatting and documentation
