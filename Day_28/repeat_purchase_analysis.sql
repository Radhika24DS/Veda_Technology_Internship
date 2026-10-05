-- Task 28: Repeat Purchase Analysis (SQL version, SQLite or PostgreSQL friendly)
-- Source table: cleaned_orders(customer_id, invoice, order_date, order_value)  -> output/powerbi_data/orders.csv

-- 1. Repeat rate
WITH cust AS (SELECT customer_id, COUNT(DISTINCT invoice) AS n_orders, SUM(order_value) AS rev
              FROM cleaned_orders GROUP BY customer_id)
SELECT COUNT(*) AS customers,
       SUM(CASE WHEN n_orders>=2 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0*SUM(CASE WHEN n_orders>=2 THEN 1 ELSE 0 END)/COUNT(*),2) AS repeat_rate_pct
FROM cust;

-- 2. Segment table
WITH cust AS (SELECT customer_id, COUNT(DISTINCT invoice) AS n_orders, SUM(order_value) AS rev
              FROM cleaned_orders GROUP BY customer_id)
SELECT CASE WHEN n_orders=1 THEN '1 order (One-Time)'
            WHEN n_orders<=3 THEN '2-3 orders (Occasional)'
            WHEN n_orders<=9 THEN '4-9 orders (Regular)'
            ELSE '10+ orders (Champions)' END AS segment,
       COUNT(*) AS customers, ROUND(SUM(rev),2) AS revenue,
       ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM cust),2) AS pct_customers,
       ROUND(100.0*SUM(rev)/(SELECT SUM(rev) FROM cust),2) AS pct_revenue
FROM cust GROUP BY 1 ORDER BY MIN(n_orders);

-- 3. AOV: one-time vs repeat customers
WITH cust AS (SELECT customer_id, COUNT(DISTINCT invoice) AS n_orders FROM cleaned_orders GROUP BY customer_id)
SELECT CASE WHEN c.n_orders=1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
       ROUND(AVG(o.order_value),2) AS aov
FROM cleaned_orders o JOIN cust c USING (customer_id) GROUP BY 1;

-- 4. AOV: first order vs later orders
WITH ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn FROM cleaned_orders)
SELECT CASE WHEN rn=1 THEN 'First order' ELSE 'Repeat order' END AS order_type,
       ROUND(AVG(order_value),2) AS aov FROM ranked GROUP BY 1;

-- 5. Median-style: average days from 1st to 2nd order
WITH ranked AS (SELECT customer_id, order_date, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS rn FROM cleaned_orders)
SELECT ROUND(AVG(julianday(o2.order_date)-julianday(o1.order_date)),1) AS avg_days_to_second_order
FROM ranked o1 JOIN ranked o2 ON o1.customer_id=o2.customer_id AND o1.rn=1 AND o2.rn=2;
