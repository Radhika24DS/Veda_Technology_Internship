-- =====================================================================
-- TASK 25: Multi-Table Sales Analysis (Orders + Products + Customers)
-- Dataset : Northwind  | Dialect: PostgreSQL (notes for MySQL/SQL Server inline)
-- Tables  : orders, order_details, products, categories, customers
-- Grain   : fact view = ONE ROW PER ORDER LINE (order_id + product_id)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. PREPROCESSING / CLEANING
-- ---------------------------------------------------------------------
-- 0.1 Profile: row counts per table
SELECT 'orders' t, COUNT(*) n FROM orders
UNION ALL SELECT 'order_details', COUNT(*) FROM order_details
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'customers', COUNT(*) FROM customers;

-- 0.2 Null / invalid checks
SELECT
  SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer,
  SUM(CASE WHEN order_date  IS NULL THEN 1 ELSE 0 END) AS null_order_date,
  SUM(CASE WHEN shipped_date IS NULL THEN 1 ELSE 0 END) AS not_shipped_yet,
  SUM(CASE WHEN shipped_date < order_date THEN 1 ELSE 0 END) AS ship_before_order
FROM orders;

SELECT
  SUM(CASE WHEN quantity   <= 0 THEN 1 ELSE 0 END) AS bad_qty,
  SUM(CASE WHEN unit_price <  0 THEN 1 ELSE 0 END) AS bad_price,
  SUM(CASE WHEN discount NOT BETWEEN 0 AND 1 THEN 1 ELSE 0 END) AS bad_discount
FROM order_details;

-- 0.3 Duplicate checks (primary keys must be unique)
SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1;
SELECT order_id, product_id, COUNT(*) FROM order_details
GROUP BY order_id, product_id HAVING COUNT(*) > 1;
SELECT customer_id, COUNT(*) FROM customers GROUP BY customer_id HAVING COUNT(*) > 1;

-- 0.4 Orphan checks (broken relationships)
SELECT o.order_id FROM orders o
LEFT JOIN customers c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;                                  -- orders without customer

SELECT d.order_id, d.product_id FROM order_details d
LEFT JOIN products p ON p.product_id = d.product_id
WHERE p.product_id IS NULL;                                   -- lines without product

SELECT d.order_id FROM order_details d
LEFT JOIN orders o ON o.order_id = d.order_id
WHERE o.order_id IS NULL;                                     -- lines without order

-- 0.5 Standardise text (run only if checks show dirty values)
UPDATE customers SET company_name = TRIM(company_name),
                     country      = INITCAP(TRIM(country)),
                     city         = INITCAP(TRIM(city));
UPDATE products  SET product_name = TRIM(product_name);

-- 0.6 Cap impossible discounts / remove invalid lines (document what you did!)
-- DELETE FROM order_details WHERE quantity <= 0 OR unit_price < 0;

-- ---------------------------------------------------------------------
-- 1. WHY JOINS CAUSE DOUBLE COUNTING (demonstration)
-- ---------------------------------------------------------------------
-- Freight lives at ORDER grain. order_details is LINE grain (many per order).
-- WRONG: joining first, then summing freight repeats it once per line.
SELECT SUM(o.freight) AS freight_WRONG
FROM orders o JOIN order_details d ON d.order_id = o.order_id;

-- RIGHT: aggregate at the grain where the measure lives.
SELECT SUM(freight) AS freight_CORRECT FROM orders;

-- Customers x Orders x Lines: counting rows != counting orders
SELECT COUNT(*) AS rows_after_join,
       COUNT(DISTINCT o.order_id) AS real_orders
FROM orders o JOIN order_details d ON d.order_id = o.order_id;

-- ---------------------------------------------------------------------
-- 2. CLEAN FACT VIEW (order-line grain, all three entities combined)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS vw_sales_fact;
CREATE VIEW vw_sales_fact AS
SELECT
  o.order_id,
  d.product_id,
  o.order_date,
  o.shipped_date,
  c.customer_id,
  c.company_name,
  c.country,
  c.city,
  p.product_name,
  cat.category_name,
  d.unit_price,
  d.quantity,
  d.discount,
  d.unit_price * d.quantity                         AS gross_sales,
  d.unit_price * d.quantity * d.discount            AS discount_amount,
  d.unit_price * d.quantity * (1 - d.discount)      AS net_sales
FROM orders o
JOIN order_details d  ON d.order_id    = o.order_id
JOIN customers c      ON c.customer_id = o.customer_id
JOIN products p       ON p.product_id  = d.product_id
LEFT JOIN categories cat ON cat.category_id = p.category_id;

-- ---------------------------------------------------------------------
-- 3. VALIDATION (reconcile totals - must all return TRUE / 0 difference)
-- ---------------------------------------------------------------------
-- 3.1 Row count of fact = row count of order_details (no fan-out, no loss)
SELECT (SELECT COUNT(*) FROM vw_sales_fact)  AS fact_rows,
       (SELECT COUNT(*) FROM order_details)  AS source_rows,
       (SELECT COUNT(*) FROM vw_sales_fact) =
       (SELECT COUNT(*) FROM order_details)  AS rows_match;

-- 3.2 Revenue: fact view vs. straight from source table
SELECT ROUND((SELECT SUM(net_sales) FROM vw_sales_fact)::numeric, 2) AS fact_revenue,
       ROUND((SELECT SUM(unit_price*quantity*(1-discount)) FROM order_details)::numeric, 2) AS source_revenue;

-- 3.3 Distinct orders / customers preserved
SELECT (SELECT COUNT(DISTINCT order_id)    FROM vw_sales_fact) AS fact_orders,
       (SELECT COUNT(*)                    FROM orders)        AS source_orders,
       (SELECT COUNT(DISTINCT customer_id) FROM vw_sales_fact) AS fact_customers;

-- 3.4 Sum of parts = whole (by category, by country)
SELECT ROUND(SUM(rev)::numeric,2) AS sum_of_categories FROM
 (SELECT category_name, SUM(net_sales) rev FROM vw_sales_fact GROUP BY category_name) x;
SELECT ROUND(SUM(rev)::numeric,2) AS sum_of_countries FROM
 (SELECT country, SUM(net_sales) rev FROM vw_sales_fact GROUP BY country) x;

-- ---------------------------------------------------------------------
-- 4. KPIs
-- ---------------------------------------------------------------------
SELECT
  ROUND(SUM(net_sales)::numeric,2)                                   AS total_revenue,
  COUNT(DISTINCT order_id)                                           AS total_orders,
  COUNT(DISTINCT customer_id)                                        AS active_customers,
  ROUND((SUM(net_sales)/COUNT(DISTINCT order_id))::numeric,2)        AS avg_order_value,
  SUM(quantity)                                                      AS units_sold,
  ROUND((SUM(discount_amount)/NULLIF(SUM(gross_sales),0)*100)::numeric,2) AS discount_pct
FROM vw_sales_fact;

-- Freight (order grain - NOT from the fact view!)
SELECT ROUND(SUM(freight)::numeric,2) AS total_freight FROM orders;

-- ---------------------------------------------------------------------
-- 5. INSIGHT QUERIES
-- ---------------------------------------------------------------------
-- INSIGHT 1: Monthly revenue trend + MoM growth
WITH m AS (
  SELECT DATE_TRUNC('month', order_date)::date AS month, SUM(net_sales) AS revenue
  FROM vw_sales_fact GROUP BY 1)
SELECT month, ROUND(revenue::numeric,2) AS revenue,
       ROUND(((revenue - LAG(revenue) OVER (ORDER BY month))
              / NULLIF(LAG(revenue) OVER (ORDER BY month),0)*100)::numeric,1) AS mom_growth_pct
FROM m ORDER BY month;

-- INSIGHT 2: Category & product concentration (Pareto)
SELECT category_name, ROUND(SUM(net_sales)::numeric,2) AS revenue,
       ROUND((SUM(net_sales)/SUM(SUM(net_sales)) OVER ()*100)::numeric,1) AS pct_of_total
FROM vw_sales_fact GROUP BY category_name ORDER BY revenue DESC;

SELECT product_name, ROUND(SUM(net_sales)::numeric,2) AS revenue,
       ROUND((SUM(SUM(net_sales)) OVER (ORDER BY SUM(net_sales) DESC)
              / SUM(SUM(net_sales)) OVER ()*100)::numeric,1) AS cumulative_pct
FROM vw_sales_fact GROUP BY product_name ORDER BY revenue DESC LIMIT 15;

-- INSIGHT 3: Top customers & concentration
SELECT company_name, country, COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(net_sales)::numeric,2) AS revenue,
       RANK() OVER (ORDER BY SUM(net_sales) DESC) AS rnk
FROM vw_sales_fact GROUP BY company_name, country ORDER BY revenue DESC LIMIT 10;

-- INSIGHT 4: Geography - revenue, orders and AOV by country
SELECT country, ROUND(SUM(net_sales)::numeric,2) AS revenue,
       COUNT(DISTINCT order_id) AS orders,
       ROUND((SUM(net_sales)/COUNT(DISTINCT order_id))::numeric,2) AS aov
FROM vw_sales_fact GROUP BY country ORDER BY revenue DESC;

-- INSIGHT 5: Discount effectiveness - does discounting lift volume?
SELECT CASE WHEN discount = 0 THEN '0%'
            WHEN discount <= 0.10 THEN '1-10%'
            WHEN discount <= 0.20 THEN '11-20%'
            ELSE '>20%' END AS discount_band,
       COUNT(*) AS lines, ROUND(AVG(quantity),1) AS avg_qty,
       ROUND(SUM(net_sales)::numeric,2) AS revenue
FROM vw_sales_fact GROUP BY 1 ORDER BY 1;

-- BONUS: Repeat vs one-time customers
SELECT CASE WHEN n = 1 THEN 'One-time' ELSE 'Repeat' END AS type, COUNT(*) AS customers
FROM (SELECT customer_id, COUNT(DISTINCT order_id) n FROM vw_sales_fact GROUP BY 1) t GROUP BY 1;

-- BONUS: Delivery performance (days to ship)
SELECT ROUND(AVG(shipped_date - order_date),1) AS avg_days_to_ship FROM orders WHERE shipped_date IS NOT NULL;
-- MySQL: DATEDIFF(shipped_date, order_date) | SQL Server: DATEDIFF(day, order_date, shipped_date)
