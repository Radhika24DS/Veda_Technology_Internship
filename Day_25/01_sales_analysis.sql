-- =====================================================================
-- TASK 25: Multi-Table Sales Analysis  |  Dataset: northwind_orders.csv
-- Dialect: SQLite (tested). PostgreSQL / MySQL / SQL Server equivalents are noted inline.
-- Input table : orders_raw   (import northwind_orders.csv as-is)
-- Output table: orders       (cleaned, analysis-ready, one row per order)
-- NOTE: the supplied file contains ONLY the orders table. Revenue / product /
--       customer-name analysis needs order_details, products, customers:
--       see 07_full_multitable_template.sql (join + double-counting safeguards).
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. PROFILING
-- ---------------------------------------------------------------------
SELECT COUNT(*) AS rows_raw, COUNT(DISTINCT order_id) AS distinct_orders,
       MIN(order_date) AS first_order, MAX(order_date) AS last_order
FROM orders_raw;

SELECT SUM(shipped_date IS NULL OR shipped_date = '')    AS null_shipped_date,
       SUM(ship_region IS NULL OR ship_region = '')      AS null_region,
       SUM(ship_postal_code IS NULL OR ship_postal_code='') AS null_postal,
       SUM(shipped_date < order_date)                    AS ship_before_order,
       SUM(freight < 0)                                  AS negative_freight
FROM orders_raw;

-- duplicates on primary key (must return 0 rows)
SELECT order_id, COUNT(*) FROM orders_raw GROUP BY order_id HAVING COUNT(*) > 1;

-- ---------------------------------------------------------------------
-- 1. CLEANING  ->  orders
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS orders;
CREATE TABLE orders AS
SELECT
  order_id,
  UPPER(TRIM(customer_id))                         AS customer_id,
  employee_id,
  DATE(order_date)                                 AS order_date,
  DATE(required_date)                              AS required_date,
  DATE(NULLIF(shipped_date,''))                    AS shipped_date,      -- NULL = not shipped yet
  ship_via,
  CASE ship_via WHEN 1 THEN 'Speedy Express'
                WHEN 2 THEN 'United Package'
                WHEN 3 THEN 'Federal Shipping' END AS shipper,
  ROUND(freight, 2)                                AS freight,
  TRIM(ship_name)                                  AS ship_name,
  TRIM(ship_city)                                  AS ship_city,
  COALESCE(NULLIF(TRIM(ship_region),''),'Not Specified')      AS ship_region,
  COALESCE(NULLIF(TRIM(ship_postal_code),''),'Not Specified') AS ship_postal_code,
  TRIM(ship_country)                               AS ship_country,
  -- derived fields
  STRFTIME('%Y', order_date)                       AS order_year,        -- PG: EXTRACT(YEAR FROM order_date)
  STRFTIME('%Y-%m', order_date)                    AS order_month,       -- PG: TO_CHAR(order_date,'YYYY-MM')
  CASE WHEN shipped_date IS NULL OR shipped_date='' THEN 0 ELSE 1 END AS is_shipped,
  CAST(JULIANDAY(shipped_date) - JULIANDAY(order_date) AS INT)    AS days_to_ship, -- PG: shipped_date - order_date
  CASE WHEN shipped_date > required_date THEN 1 ELSE 0 END        AS is_late
FROM orders_raw
GROUP BY order_id;            -- guarantees one row per order_id

-- ---------------------------------------------------------------------
-- 2. VALIDATION (every check must pass)
-- ---------------------------------------------------------------------
SELECT (SELECT COUNT(*) FROM orders_raw) AS raw_rows,
       (SELECT COUNT(*) FROM orders)     AS clean_rows,
       (SELECT COUNT(*) FROM orders_raw) = (SELECT COUNT(*) FROM orders) AS rowcount_match;

SELECT ROUND((SELECT SUM(freight) FROM orders_raw),2) AS raw_freight,
       ROUND((SELECT SUM(freight) FROM orders),2)     AS clean_freight;

-- sum of parts = whole (by country and by year)
SELECT ROUND(SUM(f),2) AS freight_by_country_total FROM (SELECT ship_country, SUM(freight) f FROM orders GROUP BY 1);
SELECT ROUND(SUM(f),2) AS freight_by_year_total    FROM (SELECT order_year,  SUM(freight) f FROM orders GROUP BY 1);
SELECT SUM(n) AS orders_by_country_total FROM (SELECT COUNT(*) n FROM orders GROUP BY ship_country);

-- ---------------------------------------------------------------------
-- 3. KPIs
-- ---------------------------------------------------------------------
SELECT COUNT(DISTINCT order_id)                         AS total_orders,        -- DISTINCT guards against fan-out later
       COUNT(DISTINCT customer_id)                      AS active_customers,
       COUNT(DISTINCT ship_country)                     AS countries,
       ROUND(SUM(freight),2)                            AS total_freight,
       ROUND(AVG(freight),2)                            AS avg_freight_per_order,
       ROUND(AVG(days_to_ship),1)                       AS avg_days_to_ship,
       ROUND(100.0*SUM(is_late)/SUM(is_shipped),1)      AS late_delivery_pct,
       SUM(1-is_shipped)                                AS open_orders
FROM orders;

-- ---------------------------------------------------------------------
-- 4. INSIGHT QUERIES
-- ---------------------------------------------------------------------
-- INSIGHT 1: Order volume trend (monthly + MoM %)  [May-1998 is a partial month]
WITH m AS (SELECT order_month, COUNT(*) AS orders FROM orders GROUP BY 1)
SELECT order_month, orders,
       ROUND(100.0*(orders - LAG(orders) OVER (ORDER BY order_month))
             / LAG(orders) OVER (ORDER BY order_month),1) AS mom_pct
FROM m ORDER BY order_month;

SELECT order_year, COUNT(*) AS orders, COUNT(DISTINCT order_month) AS months,
       ROUND(1.0*COUNT(*)/COUNT(DISTINCT order_month),1) AS orders_per_month
FROM orders GROUP BY order_year;

-- INSIGHT 2: Geographic concentration (share + cumulative share)
SELECT ship_country, COUNT(*) AS orders,
       ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (),1) AS pct_orders,
       ROUND(100.0*SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC, ship_country)
             / SUM(COUNT(*)) OVER (),1)               AS cumulative_pct
FROM orders GROUP BY ship_country ORDER BY orders DESC;

-- INSIGHT 3: Freight cost by country (total vs per-order)
SELECT ship_country, COUNT(*) AS orders, ROUND(SUM(freight),2) AS total_freight,
       ROUND(AVG(freight),2) AS avg_freight,
       ROUND(100.0*SUM(freight)/SUM(SUM(freight)) OVER (),1) AS pct_of_freight
FROM orders GROUP BY ship_country ORDER BY total_freight DESC;

-- INSIGHT 4: Customer concentration
WITH c AS (SELECT customer_id, COUNT(*) AS orders, SUM(freight) AS freight FROM orders GROUP BY 1)
SELECT customer_id, orders, ROUND(freight,2) AS freight,
       ROUND(100.0*orders/SUM(orders) OVER (),1) AS pct_orders,
       RANK() OVER (ORDER BY orders DESC) AS rnk
FROM c ORDER BY orders DESC LIMIT 10;

-- INSIGHT 5: Delivery performance by shipper and by employee
SELECT shipper, COUNT(*) AS orders, ROUND(AVG(days_to_ship),1) AS avg_days,
       SUM(is_late) AS late_orders, ROUND(AVG(freight),2) AS avg_freight
FROM orders GROUP BY shipper ORDER BY orders DESC;

SELECT employee_id, COUNT(*) AS orders, SUM(is_late) AS late,
       ROUND(100.0*SUM(is_late)/SUM(is_shipped),1) AS late_pct,
       ROUND(AVG(days_to_ship),1) AS avg_days
FROM orders GROUP BY employee_id ORDER BY late_pct DESC;

SELECT ship_country, COUNT(*) AS shipped, SUM(is_late) AS late,
       ROUND(100.0*SUM(is_late)/COUNT(*),1) AS late_pct
FROM orders WHERE is_shipped=1 GROUP BY 1 HAVING COUNT(*)>=10 ORDER BY late_pct DESC LIMIT 5;

-- Open (unshipped) orders
SELECT MIN(order_date) AS oldest_open, MAX(order_date) AS newest_open, COUNT(*) AS open_orders
FROM orders WHERE is_shipped=0;
