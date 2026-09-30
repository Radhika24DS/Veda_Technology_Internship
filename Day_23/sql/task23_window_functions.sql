/* =====================================================================
   TASK 23 - SQL WINDOW FUNCTIONS INTRO  |  Dataset: Northwind
   Author : Radhika  |  Track: Data Analytics
   Engine : SQLite 3.25+ (window functions)  - also works in PostgreSQL / MySQL 8
   Tables (cleaned):
     orders(order_id, customer_id, employee_id, order_date, ship_country, freight, ...)
     order_details(order_id, product_id, unit_price, quantity, discount, line_total, ...)
     order_summary(one row per order + order_revenue, total_units, year_month, order_year, order_quarter,
                   is_partial_month ...)
   Revenue = unit_price * quantity * (1 - discount)   (freight excluded)
   ===================================================================== */


/* ---------------------------------------------------------------------
   SECTION A - ROW_NUMBER()   (unique sequence, ties broken arbitrarily)
   --------------------------------------------------------------------- */

-- Q1: ROW_NUMBER | What was each customer's FIRST order? (top 10 by date)
-- Business use: customer acquisition - when and how big was the first purchase?
WITH numbered AS (
    SELECT customer_id, order_id, order_date, ship_country, order_revenue,
           ROW_NUMBER() OVER (PARTITION BY customer_id
                              ORDER BY order_date, order_id) AS order_seq
    FROM order_summary
)
SELECT customer_id, order_id, order_date, ship_country, order_revenue
FROM numbered
WHERE order_seq = 1
ORDER BY order_date, customer_id
LIMIT 10;

-- Q2: ROW_NUMBER | Top 3 highest-value orders in EACH country (Top-N per group)
-- Business use: identify biggest deals per market. (Shown for 5 largest markets.)
WITH ranked AS (
    SELECT ship_country, order_id, customer_id, order_date, order_revenue,
           ROW_NUMBER() OVER (PARTITION BY ship_country
                              ORDER BY order_revenue DESC, order_id) AS rn
    FROM order_summary
    WHERE ship_country IN ('USA','Germany','Brazil','France','UK')
)
SELECT ship_country, rn AS position, order_id, customer_id, order_date, order_revenue
FROM ranked
WHERE rn <= 3
ORDER BY ship_country, rn;

-- Q3: ROW_NUMBER | Most recent order per customer + days since (recency / churn check)
-- Reference date = last order date in the data set (1998-05-06), NOT today's date.
WITH latest AS (
    SELECT customer_id, order_id, order_date, order_revenue,
           ROW_NUMBER() OVER (PARTITION BY customer_id
                              ORDER BY order_date DESC, order_id DESC) AS rn
    FROM order_summary
)
SELECT customer_id, order_id, order_date AS last_order_date, order_revenue,
       CAST(julianday((SELECT MAX(order_date) FROM order_summary)) - julianday(order_date) AS INT) AS days_since_last_order
FROM latest
WHERE rn = 1
ORDER BY days_since_last_order DESC
LIMIT 10;


/* ---------------------------------------------------------------------
   SECTION B - RANK() / DENSE_RANK()   (ties get the same rank)
   --------------------------------------------------------------------- */

-- Q4: RANK | Top 10 customers by total revenue (with share of company revenue)
SELECT customer_id,
       COUNT(*)                                   AS orders,
       ROUND(SUM(order_revenue), 2)               AS total_revenue,
       RANK() OVER (ORDER BY SUM(order_revenue) DESC) AS revenue_rank,
       ROUND(100.0 * SUM(order_revenue) / SUM(SUM(order_revenue)) OVER (), 2) AS pct_of_total
FROM order_summary
GROUP BY customer_id
ORDER BY revenue_rank
LIMIT 10;

-- Q5: ROW_NUMBER vs RANK vs DENSE_RANK | Customers ranked by NUMBER OF ORDERS
-- Many customers tie on order count, so this is the perfect place to compare the three.
--   ROW_NUMBER : 1,2,3,4,5,6 ... never repeats
--   RANK       : 1,2,2,4,5,5 ... ties share a rank, then a GAP is left
--   DENSE_RANK : 1,2,2,3,4,4 ... ties share a rank, NO gap
SELECT customer_id,
       COUNT(*) AS order_count,
       ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC, customer_id) AS row_num,
       RANK()       OVER (ORDER BY COUNT(*) DESC)               AS rnk,
       DENSE_RANK() OVER (ORDER BY COUNT(*) DESC)               AS dense_rnk
FROM order_summary
GROUP BY customer_id
ORDER BY order_count DESC, customer_id
LIMIT 15;

-- Q6: RANK (partitioned) | Employee sales ranking within each YEAR
-- Business use: who was the top performer each year? (1996 & 1998 are partial years)
WITH emp_year AS (
    SELECT order_year, employee_id,
           COUNT(*)                     AS orders,
           ROUND(SUM(order_revenue), 2) AS revenue
    FROM order_summary
    GROUP BY order_year, employee_id
)
SELECT order_year, employee_id, orders, revenue,
       RANK() OVER (PARTITION BY order_year ORDER BY revenue DESC) AS rank_in_year
FROM emp_year
ORDER BY order_year, rank_in_year;

-- Q7: DENSE_RANK | Top 3 products by revenue in each year
-- DENSE_RANK is used so a tie never hides the "3rd best" product.
WITH prod_year AS (
    SELECT o.order_year, d.product_id,
           SUM(d.quantity)              AS units_sold,
           ROUND(SUM(d.line_total), 2)  AS revenue
    FROM order_details d
    JOIN orders o ON o.order_id = d.order_id
    GROUP BY o.order_year, d.product_id
),
ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY order_year ORDER BY revenue DESC) AS dr
    FROM prod_year
)
SELECT order_year, dr AS revenue_rank, product_id, units_sold, revenue
FROM ranked
WHERE dr <= 3
ORDER BY order_year, dr;


/* ---------------------------------------------------------------------
   SECTION C - LAG()   (look at the previous row -> trends & changes)
   --------------------------------------------------------------------- */

-- Q8: LAG | Month-over-Month (MoM) revenue growth
-- LAG(revenue) returns the previous month's revenue; first month has no previous -> NULL.
-- NOTE: 1996-07 and 1998-05 are partial months (flagged), so their MoM % is not comparable.
WITH monthly AS (
    SELECT year_month,
           MAX(is_partial_month)        AS is_partial,
           ROUND(SUM(order_revenue), 2) AS revenue
    FROM order_summary
    GROUP BY year_month
)
SELECT year_month, revenue,
       LAG(revenue) OVER (ORDER BY year_month) AS prev_month_revenue,
       ROUND(revenue - LAG(revenue) OVER (ORDER BY year_month), 2) AS change_abs,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
             / LAG(revenue) OVER (ORDER BY year_month), 1) AS mom_growth_pct,
       CASE WHEN is_partial = 1 THEN 'partial month' ELSE '' END AS note
FROM monthly
ORDER BY year_month;

-- Q9: LAG | Days between a customer's consecutive orders (purchase frequency)
-- Shown for the first 8 orders of 3 sample customers; customer_avg_gap_days covers ALL their orders.
WITH gaps AS (
    SELECT customer_id, order_id, order_date,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS order_seq,
           LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_order_date
    FROM order_summary
    WHERE customer_id IN ('SAVEA','ERNSH','QUICK')
),
with_gap AS (
    SELECT *, CAST(julianday(order_date) - julianday(prev_order_date) AS INT) AS days_since_prev_order
    FROM gaps
)
SELECT customer_id, order_seq, order_id, order_date, prev_order_date, days_since_prev_order,
       ROUND(AVG(days_since_prev_order) OVER (PARTITION BY customer_id), 1) AS customer_avg_gap_days
FROM with_gap
WHERE order_seq <= 8
ORDER BY customer_id, order_seq;

-- Q10: LAG | Is each order bigger or smaller than the customer's previous order?
-- Summary of the trend over all repeat orders (customer-level behaviour).
WITH trend AS (
    SELECT customer_id, order_id, order_revenue,
           LAG(order_revenue) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS prev_revenue
    FROM order_summary
)
SELECT CASE WHEN prev_revenue IS NULL        THEN '1) First order (no previous)'
            WHEN order_revenue > prev_revenue THEN '2) Larger than previous'
            WHEN order_revenue < prev_revenue THEN '3) Smaller than previous'
            ELSE                                   '4) Same as previous' END AS vs_previous_order,
       COUNT(*)                                       AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders
FROM trend
GROUP BY 1
ORDER BY 1;

-- Q11: LAG | Quarter-over-Quarter (QoQ) revenue per employee (top 3 employees by revenue)
WITH emp_q AS (
    SELECT employee_id, order_year, order_quarter,
           order_year || '-Q' || order_quarter AS yq,
           ROUND(SUM(order_revenue), 2)        AS revenue
    FROM order_summary
    WHERE employee_id IN (SELECT employee_id FROM order_summary
                          GROUP BY employee_id ORDER BY SUM(order_revenue) DESC LIMIT 3)
    GROUP BY employee_id, order_year, order_quarter
)
SELECT employee_id, yq, revenue,
       LAG(revenue) OVER (PARTITION BY employee_id ORDER BY order_year, order_quarter) AS prev_quarter_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (PARTITION BY employee_id ORDER BY order_year, order_quarter))
             / LAG(revenue) OVER (PARTITION BY employee_id ORDER BY order_year, order_quarter), 1) AS qoq_growth_pct
FROM emp_q
ORDER BY employee_id, order_year, order_quarter;


/* ---------------------------------------------------------------------
   SECTION D - COMBINING FUNCTIONS (LAG + RANK)  - the capstone query
   --------------------------------------------------------------------- */

-- Q12: LAG + RANK + running total | Rank full months by MoM growth and show cumulative revenue
-- Partial months are excluded so growth rates are fair (complete months only).
WITH monthly AS (
    SELECT year_month, ROUND(SUM(order_revenue), 2) AS revenue
    FROM order_summary
    WHERE is_partial_month = 0
    GROUP BY year_month
),
growth AS (
    SELECT year_month, revenue,
           ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY year_month))
                 / LAG(revenue) OVER (ORDER BY year_month), 1) AS mom_growth_pct,
           ROUND(SUM(revenue) OVER (ORDER BY year_month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue
    FROM monthly
)
SELECT RANK() OVER (ORDER BY mom_growth_pct DESC) AS growth_rank,
       year_month, revenue, mom_growth_pct, cumulative_revenue
FROM growth
WHERE mom_growth_pct IS NOT NULL
ORDER BY growth_rank
LIMIT 8;
