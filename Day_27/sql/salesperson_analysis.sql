-- =====================================================================
-- Task 27 - Salesperson Performance Analysis (Superstore)
-- Dialect: portable ANSI SQL (tested on SQLite 3.35+; runs on MySQL 8 /
--          PostgreSQL with the table-creation tweaks noted in step 0).
-- Source : data/superstore_clean.csv  ->  table superstore_clean
-- NOTE   : the dataset has no salesperson, order date or order id.
--          "Salesperson" = Region Team or State Rep (proxies).
-- =====================================================================

-- 0. TABLE ------------------------------------------------------------
-- MySQL/PostgreSQL: use VARCHAR and NUMERIC types, then import the CSV with
-- LOAD DATA INFILE (MySQL), COPY (PostgreSQL) or the Workbench import wizard.
CREATE TABLE IF NOT EXISTS superstore_clean (
    ship_mode TEXT, segment TEXT, city TEXT, state TEXT, postal_code TEXT,
    region TEXT, category TEXT, sub_category TEXT,
    sales REAL, quantity INTEGER, discount REAL, profit REAL,
    profit_margin REAL, loss_flag INTEGER, discount_band TEXT,
    salesperson_region_team TEXT, salesperson_state_rep TEXT, profit_outlier INTEGER
);

-- 1. SANITY CHECKS ------------------------------------------------------
SELECT COUNT(*) AS rows_loaded, ROUND(SUM(sales),2) AS total_sales, ROUND(SUM(profit),2) AS total_profit
FROM superstore_clean;                       -- expect 9977 rows, 2,296,195.59 sales, 286,241.42 profit

-- 2. KPIs PER REGION TEAM (multiple KPIs, not revenue alone) ----------------
SELECT region AS salesperson,
       ROUND(SUM(sales),2) AS sales, ROUND(SUM(profit),2) AS profit,
       ROUND(SUM(profit)/SUM(sales),4) AS profit_margin, COUNT(*) AS line_items,
       ROUND(SUM(sales)/COUNT(*),2) AS aov_proxy, ROUND(AVG(discount),4) AS avg_discount,
       ROUND(AVG(loss_flag),4) AS pct_loss_lines
FROM superstore_clean GROUP BY region ORDER BY profit DESC;

-- 3. REGION TEAM RANKING: product-mix adjusted, weighted composite score -----------------------------------------------------------------
WITH bench AS (                                   -- national margin per sub-category
    SELECT sub_category, SUM(profit)/SUM(sales) AS nat_margin
    FROM superstore_clean GROUP BY sub_category
),
unit AS (
    SELECT s.region AS unit_key,
           SUM(s.sales) AS sales, SUM(s.profit) AS profit, COUNT(*) AS line_items,
           AVG(s.discount) AS avg_discount, AVG(s.loss_flag) AS pct_loss_lines,
           SUM(s.sales * b.nat_margin) AS expected_profit
    FROM superstore_clean s JOIN bench b ON b.sub_category = s.sub_category
    GROUP BY s.region
),
kpi AS (
    SELECT unit_key, sales, profit, line_items, avg_discount, pct_loss_lines,
           profit/sales                           AS margin,
           sales*1.0/line_items                   AS aov_proxy,
           profit/sales - expected_profit/sales   AS margin_gap
    FROM unit
),
norm AS (                                         -- min-max normalise every KPI to 0..1
    SELECT k.*,
        (sales        - MIN(sales)        OVER()) / (MAX(sales)        OVER() - MIN(sales)        OVER()) AS n_sales,
        (profit       - MIN(profit)       OVER()) / (MAX(profit)       OVER() - MIN(profit)       OVER()) AS n_profit,
        (margin       - MIN(margin)       OVER()) / (MAX(margin)       OVER() - MIN(margin)       OVER()) AS n_margin,
        (aov_proxy    - MIN(aov_proxy)    OVER()) / (MAX(aov_proxy)    OVER() - MIN(aov_proxy)    OVER()) AS n_aov,
        1 - (avg_discount - MIN(avg_discount) OVER()) / (MAX(avg_discount) OVER() - MIN(avg_discount) OVER()) AS n_disc,
        (margin_gap   - MIN(margin_gap)   OVER()) / (MAX(margin_gap)   OVER() - MIN(margin_gap)   OVER()) AS n_gap
    FROM kpi k
),
scored AS (
    SELECT n.*,
           100*(0.20*n_sales + 0.25*n_profit + 0.20*n_margin + 0.10*n_aov + 0.10*n_disc + 0.15*n_gap) AS composite_score
    FROM norm n
)
SELECT unit_key || ' Region Team' AS salesperson,
       ROUND(sales,2) AS sales, ROUND(profit,2) AS profit, ROUND(margin,4) AS profit_margin,
       line_items, ROUND(aov_proxy,2) AS aov_proxy, ROUND(avg_discount,4) AS avg_discount,
       ROUND(margin_gap,4) AS margin_gap, ROUND(composite_score,1) AS composite_score,
       RANK() OVER (ORDER BY composite_score DESC) AS rank_composite,
       RANK() OVER (ORDER BY sales DESC)           AS rank_sales_only
FROM scored
ORDER BY rank_composite;

-- 4. STATE REP RANKING (49 reps) - same method -----------------------------------------------------------------
WITH bench AS (                                   -- national margin per sub-category
    SELECT sub_category, SUM(profit)/SUM(sales) AS nat_margin
    FROM superstore_clean GROUP BY sub_category
),
unit AS (
    SELECT s.state AS unit_key,
           SUM(s.sales) AS sales, SUM(s.profit) AS profit, COUNT(*) AS line_items,
           AVG(s.discount) AS avg_discount, AVG(s.loss_flag) AS pct_loss_lines,
           SUM(s.sales * b.nat_margin) AS expected_profit
    FROM superstore_clean s JOIN bench b ON b.sub_category = s.sub_category
    GROUP BY s.state
),
kpi AS (
    SELECT unit_key, sales, profit, line_items, avg_discount, pct_loss_lines,
           profit/sales                           AS margin,
           sales*1.0/line_items                   AS aov_proxy,
           profit/sales - expected_profit/sales   AS margin_gap
    FROM unit
),
norm AS (                                         -- min-max normalise every KPI to 0..1
    SELECT k.*,
        (sales        - MIN(sales)        OVER()) / (MAX(sales)        OVER() - MIN(sales)        OVER()) AS n_sales,
        (profit       - MIN(profit)       OVER()) / (MAX(profit)       OVER() - MIN(profit)       OVER()) AS n_profit,
        (margin       - MIN(margin)       OVER()) / (MAX(margin)       OVER() - MIN(margin)       OVER()) AS n_margin,
        (aov_proxy    - MIN(aov_proxy)    OVER()) / (MAX(aov_proxy)    OVER() - MIN(aov_proxy)    OVER()) AS n_aov,
        1 - (avg_discount - MIN(avg_discount) OVER()) / (MAX(avg_discount) OVER() - MIN(avg_discount) OVER()) AS n_disc,
        (margin_gap   - MIN(margin_gap)   OVER()) / (MAX(margin_gap)   OVER() - MIN(margin_gap)   OVER()) AS n_gap
    FROM kpi k
),
scored AS (
    SELECT n.*,
           100*(0.20*n_sales + 0.25*n_profit + 0.20*n_margin + 0.10*n_aov + 0.10*n_disc + 0.15*n_gap) AS composite_score
    FROM norm n
)
SELECT 'State Rep - ' || unit_key AS salesperson,
       ROUND(sales,2) AS sales, ROUND(profit,2) AS profit, ROUND(margin,4) AS profit_margin,
       line_items, ROUND(aov_proxy,2) AS aov_proxy, ROUND(avg_discount,4) AS avg_discount,
       ROUND(margin_gap,4) AS margin_gap, ROUND(composite_score,1) AS composite_score,
       RANK() OVER (ORDER BY composite_score DESC) AS rank_composite,
       RANK() OVER (ORDER BY sales DESC)           AS rank_sales_only
FROM scored
ORDER BY rank_composite;

-- 5. TERRITORY CONTEXT: margin by region x category -------------------------
SELECT region, category, ROUND(SUM(profit)/SUM(sales),4) AS margin, ROUND(SUM(profit),2) AS profit
FROM superstore_clean GROUP BY region, category ORDER BY region, category;

-- 6. DISCOUNT DISCIPLINE: how much money do deep discounts burn? --------------
SELECT discount_band, COUNT(*) AS lines, ROUND(SUM(sales),2) AS sales, ROUND(SUM(profit),2) AS profit
FROM superstore_clean GROUP BY discount_band
ORDER BY CASE discount_band WHEN 'No discount' THEN 1 WHEN '1-10%' THEN 2 WHEN '11-20%' THEN 3 WHEN '21-30%' THEN 4 ELSE 5 END;

SELECT region, ROUND(100.0*SUM(CASE WHEN discount > 0.30 THEN 1 ELSE 0 END)/COUNT(*),1) AS pct_lines_over_30_discount,
       ROUND(SUM(CASE WHEN discount > 0.30 THEN profit ELSE 0 END),2) AS profit_on_over_30_discount
FROM superstore_clean GROUP BY region ORDER BY pct_lines_over_30_discount DESC;

-- 7. WORST SUB-CATEGORIES PER REGION (where to coach) ---------------------------
SELECT region, sub_category, ROUND(SUM(profit),2) AS profit
FROM superstore_clean GROUP BY region, sub_category HAVING SUM(profit) < 0
ORDER BY profit ASC LIMIT 15;
