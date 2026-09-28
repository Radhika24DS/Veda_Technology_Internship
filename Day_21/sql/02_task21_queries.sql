-- =====================================================================
-- TASK 21 : Basic SQL SELECT  |  Data Analytics Track
-- Dataset : Northwind (orders, order_details)  -- cleaned CSVs
-- Author  : Radhika
-- Runs on : PostgreSQL and MySQL (standard SQL only)
-- Topics  : SELECT, WHERE, ORDER BY, DISTINCT, LIMIT, LIKE, IN, BETWEEN, IS NULL
-- =====================================================================

-- Q1: View the first 10 orders (SELECT * and LIMIT)
-- Business question: What does the orders table look like?
SELECT *
FROM orders
ORDER BY order_id
LIMIT 10;

-- Q2: Select specific columns, oldest orders first (column list + ORDER BY ASC)
-- Business question: Which were the earliest orders and what did shipping cost?
SELECT order_id,
       customer_id,
       order_date,
       freight,
       ship_country
FROM orders
ORDER BY order_date ASC, order_id ASC
LIMIT 10;

-- Q3: Orders shipped to Germany, highest freight first (WHERE with = and ORDER BY DESC)
-- Business question: Which German shipments were the most expensive?
SELECT order_id,
       customer_id,
       ship_city,
       freight
FROM orders
WHERE ship_country = 'Germany'
ORDER BY freight DESC
LIMIT 10;

-- Q4: List of countries Northwind ships to (DISTINCT)
-- Business question: In which countries do customers receive orders?
SELECT DISTINCT ship_country
FROM orders
ORDER BY ship_country;

-- Q5: Expensive 1997 orders (WHERE + AND + BETWEEN)
-- Business question: Which 1997 orders had freight above 100?
SELECT order_id,
       customer_id,
       order_date,
       freight,
       ship_country
FROM orders
WHERE order_date BETWEEN '1997-01-01' AND '1997-12-31'
  AND freight > 100
ORDER BY freight DESC
LIMIT 15;

-- Q6: Orders not shipped yet in selected countries (IN + IS NULL)
-- Business question: Which pending orders to France, Spain or Italy need attention?
SELECT order_id,
       customer_id,
       order_date,
       required_date,
       ship_country
FROM orders
WHERE ship_country IN ('France', 'Spain', 'Italy')
  AND shipped_date IS NULL
ORDER BY required_date ASC;

-- Q7: Cities that start with 'S' (LIKE pattern + multi-column ORDER BY)
-- Business question: Which orders go to cities beginning with S?
SELECT order_id,
       ship_city,
       ship_country,
       freight
FROM orders
WHERE ship_city LIKE 'S%'
ORDER BY ship_city ASC, freight DESC
LIMIT 15;

-- Q8: Bulk discounted order lines (WHERE with two numeric conditions)
-- Business question: Which lines combined a big quantity with a discount?
SELECT order_id,
       product_id,
       unit_price,
       quantity,
       discount
FROM order_details
WHERE quantity >= 50
  AND discount > 0
ORDER BY quantity DESC, discount DESC
LIMIT 15;

-- Q9: Top 10 order lines by revenue (calculated column + alias + ORDER BY alias)
-- Business question: Which single order lines earned the most after discount?
SELECT order_id,
       product_id,
       unit_price,
       quantity,
       discount,
       ROUND(unit_price * quantity * (1 - discount), 2) AS line_total
FROM order_details
ORDER BY line_total DESC
LIMIT 10;

-- Q10: Orders shipped after the required date (comparing two columns)
-- Business question: Which orders were delivered late, most recent first?
SELECT order_id,
       customer_id,
       required_date,
       shipped_date,
       ship_country
FROM orders
WHERE shipped_date > required_date
ORDER BY shipped_date DESC
LIMIT 15;
