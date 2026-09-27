-- Task 20 - Customer Order Count
-- Table expected: superstore(Order_ID, Customer_ID, Customer_Name, Sales, Profit, ...)
-- One row = one order LINE (a product within an order), so COUNT(*) would count
-- lines, not orders. We must count DISTINCT Order_ID per customer.

-- 0) Preprocessing: remove exact duplicate rows before aggregating
-- (in SQL there's no native DISTINCT-row DELETE; typical approach is to load into
--  a staging table, then keep one row per unique combination, e.g. with ROW_NUMBER)
WITH deduped AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY Order_ID, Customer_ID, Product_ID, Sales, Quantity, Discount, Profit
               ORDER BY Order_ID
           ) AS rn
    FROM superstore
)
SELECT * INTO superstore_clean FROM deduped WHERE rn = 1;

-- 1) Customer order table: orders per customer (avoiding duplicate order lines)
SELECT
    Customer_ID,
    Customer_Name,
    COUNT(DISTINCT Order_ID)              AS Order_Count,   -- distinct orders, not lines
    COUNT(*)                              AS Order_Lines,   -- for comparison / QA only
    SUM(Sales)                            AS Total_Sales,
    SUM(Profit)                           AS Total_Profit,
    ROUND(SUM(Sales) * 1.0 / COUNT(DISTINCT Order_ID), 2) AS Avg_Order_Value
FROM superstore_clean
GROUP BY Customer_ID, Customer_Name
ORDER BY Order_Count DESC, Total_Sales DESC;

-- 2) Top customers (frequent buyers) - proper tie handling with RANK()
--    RANK() gives tied customers the SAME rank and skips the next number,
--    so a strict "rank <= 10" filter can return MORE than 10 rows if there's
--    a tie at the cutoff (this dataset has one: 18 customers tied at 12 orders).
WITH ranked AS (
    SELECT
        Customer_ID,
        Customer_Name,
        COUNT(DISTINCT Order_ID) AS Order_Count,
        SUM(Sales)                AS Total_Sales,
        RANK() OVER (ORDER BY COUNT(DISTINCT Order_ID) DESC) AS Order_Count_Rank
    FROM superstore_clean
    GROUP BY Customer_ID, Customer_Name
)
SELECT *
FROM ranked
WHERE Order_Count_Rank <= 10
ORDER BY Order_Count_Rank, Total_Sales DESC;

-- 3) Sanity check: total orders and customers should match the raw data
SELECT COUNT(DISTINCT Order_ID) AS Total_Orders,
       COUNT(DISTINCT Customer_ID) AS Total_Customers,
       SUM(Sales) AS Grand_Total_Sales
FROM superstore_clean;
