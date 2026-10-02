# Task 25: Multi-Table Sales Analysis (SQL + Power BI)

## Objective
Apply relational analysis end to end: clean and validate the data, avoid join double counting, and turn it into KPIs, a dashboard and business insights.

## Dataset
`northwind_orders.csv`: 830 orders, 89 customers, 21 countries, 9 employees, 3 shippers (Jul 1996 - May 1998).
**Scope note:** the supplied file holds the *orders* table only. Revenue, product and customer-name analysis requires `order_details`, `products` and `customers`; a ready, join-safe script for those is in `07_full_multitable_template.sql`.

## Tools
Python (pandas) for preprocessing · SQL (SQLite-tested; PostgreSQL/MySQL notes inline) · Power BI

## Preprocessing
- Trimmed text; customer_id upper-cased; dates parsed.
- 0 duplicate order_ids; 0 negative freight; 0 orders shipped before ordered.
- 21 null shipped_date: kept and flagged as open orders (not imputed); ship_region (507) and postal code (19) nulls set to "Not Specified".
- Derived: order_year, order_month, days_to_ship, is_late, is_shipped, shipper name.

## Validation
Raw vs clean rows (830 = 830), freight total (64,942.69 both), and sum-of-parts by country and year all reconcile. Orders are counted with `COUNT(DISTINCT order_id)` to stay safe when joined to order lines.

## KPIs
830 orders · 89 customers · $64,942.69 freight · $78.24 avg freight/order · 8.5 avg days to ship · 4.6% late · 21 open orders

## Key Insights
1. Order volume rose ~88% (34/month in 1997 to 64/month in Jan-Apr 1998).
2. Top 5 countries = 55.4% of orders.
3. Austria: 4.8% of orders but 11.4% of freight ($184.79 per order).
4. Top 3 customers = 10.7% of orders and 28.5% of freight.
5. United Package is the busiest and slowest carrier; 4.6% of shipments late.

## How to run
1. `python 00_clean_orders.py` 2. Import `northwind_orders.csv` as `orders_raw` and run `01_sales_analysis.sql` 

## Author
Radhika, MCA (AI & Data Analytics)
