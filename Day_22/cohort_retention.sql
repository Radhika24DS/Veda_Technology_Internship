-- Cohort retention by first-purchase month (SQLite syntax; works on cleaned `orders` table)
-- orders(invoice, customer_id, invoice_date)  -- already filtered: no cancellations, no null customers
WITH monthly AS (           -- one row per customer per active month
    SELECT DISTINCT customer_id,
           strftime('%Y-%m', invoice_date) AS order_month
    FROM orders
),
first_purchase AS (         -- define the cohort
    SELECT customer_id, MIN(order_month) AS cohort_month
    FROM monthly
    GROUP BY customer_id
),
activity AS (               -- month offset since first purchase (consistent monthly window)
    SELECT f.cohort_month,
           (CAST(substr(m.order_month,1,4) AS INT) - CAST(substr(f.cohort_month,1,4) AS INT)) * 12
         + (CAST(substr(m.order_month,6,2) AS INT) - CAST(substr(f.cohort_month,6,2) AS INT)) AS month_index,
           m.customer_id
    FROM monthly m
    JOIN first_purchase f USING (customer_id)
),
cohort_counts AS (
    SELECT cohort_month, month_index, COUNT(DISTINCT customer_id) AS active_customers
    FROM activity
    GROUP BY cohort_month, month_index
)
SELECT c.cohort_month,
       c.month_index,
       c.active_customers,
       s.active_customers AS cohort_size,
       ROUND(100.0 * c.active_customers / s.active_customers, 1) AS retention_pct
FROM cohort_counts c
JOIN cohort_counts s ON s.cohort_month = c.cohort_month AND s.month_index = 0
ORDER BY c.cohort_month, c.month_index;
