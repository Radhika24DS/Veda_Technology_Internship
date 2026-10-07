-- Task 30: Regional Growth Analysis (SQLite syntax)
-- Table: superstore  (loaded from data/superstore_clean.csv)
-- NOTE: Year / Quarter come from a SIMULATED order date (source file has no date column).

-- Q1. Annual sales, profit and orders per region
SELECT Region, Year,
       ROUND(SUM(Sales), 2)  AS Sales,
       ROUND(SUM(Profit), 2) AS Profit,
       COUNT(*)              AS Order_Lines
FROM superstore
GROUP BY Region, Year
ORDER BY Region, Year;

-- Q2. Year-over-year sales growth per region (LAG window function)
WITH yearly AS (
    SELECT Region, Year, SUM(Sales) AS Sales
    FROM superstore
    GROUP BY Region, Year
)
SELECT Region, Year,
       ROUND(Sales, 2) AS Sales,
       ROUND(LAG(Sales) OVER (PARTITION BY Region ORDER BY Year), 2) AS Prior_Year_Sales,
       ROUND(Sales - LAG(Sales) OVER (PARTITION BY Region ORDER BY Year), 2) AS Abs_Change,
       ROUND(100.0 * (Sales - LAG(Sales) OVER (PARTITION BY Region ORDER BY Year))
             / LAG(Sales) OVER (PARTITION BY Region ORDER BY Year), 2) AS YoY_Growth_Pct
FROM yearly
ORDER BY Region, Year;

-- Q3. Quarter-over-quarter growth per region (consistent calendar quarters)
WITH q AS (
    SELECT Region, Year, Quarter, Year_Quarter, SUM(Sales) AS Sales
    FROM superstore
    GROUP BY Region, Year, Quarter, Year_Quarter
)
SELECT Region, Year_Quarter,
       ROUND(Sales, 2) AS Sales,
       ROUND(100.0 * (Sales - LAG(Sales) OVER (PARTITION BY Region ORDER BY Year, Quarter))
             / LAG(Sales) OVER (PARTITION BY Region ORDER BY Year, Quarter), 2) AS QoQ_Growth_Pct
FROM q
ORDER BY Region, Year, Quarter;

-- Q4. Small-base check: YoY growth at Region x Category level with the prior-year base
WITH rc AS (
    SELECT Region, Category, Year, SUM(Sales) AS Sales
    FROM superstore
    GROUP BY Region, Category, Year
)
SELECT Region, Category, Year,
       ROUND(Sales, 0) AS Sales,
       ROUND(LAG(Sales) OVER (PARTITION BY Region, Category ORDER BY Year), 0) AS Prior_Base,
       ROUND(100.0 * (Sales - LAG(Sales) OVER (PARTITION BY Region, Category ORDER BY Year))
             / LAG(Sales) OVER (PARTITION BY Region, Category ORDER BY Year), 1) AS YoY_Growth_Pct
FROM rc
ORDER BY ABS(YoY_Growth_Pct) DESC;

-- Q5. Compound annual growth rate 2014 -> 2017 per region
WITH y AS (
    SELECT Region,
           SUM(CASE WHEN Year = 2014 THEN Sales END) AS s14,
           SUM(CASE WHEN Year = 2017 THEN Sales END) AS s17
    FROM superstore GROUP BY Region
)
SELECT Region, ROUND(s14, 0) AS Sales_2014, ROUND(s17, 0) AS Sales_2017,
       ROUND(100.0 * (POWER(s17 / s14, 1.0 / 3) - 1), 2) AS CAGR_Pct
FROM y;

-- Q6. Real (non-simulated) cross-section: margin and discount by region
SELECT Region,
       ROUND(SUM(Sales), 0) AS Sales,
       ROUND(100.0 * SUM(Sales) / (SELECT SUM(Sales) FROM superstore), 1) AS Sales_Share_Pct,
       ROUND(100.0 * SUM(Profit) / SUM(Sales), 2) AS Margin_Pct,
       ROUND(AVG(Discount), 3) AS Avg_Discount,
       ROUND(100.0 * AVG(Loss_Making), 1) AS Loss_Line_Pct
FROM superstore
GROUP BY Region
ORDER BY Sales DESC;
