# Feedback - Task 23: SQL Window Functions Intro

## Task summary
Applied ROW_NUMBER, RANK, DENSE_RANK and LAG on the Northwind orders and order-details data through 12 business-focused queries, after cleaning and preparing the dataset.

## What went well
* The task moves from theory to practice: window functions only click once you use them on questions like "top N per group" and "growth vs last month".
* Northwind is well suited - it has customers, employees, dates and revenue, so every function has a natural business use.
* Q5 (ROW_NUMBER vs RANK vs DENSE_RANK side by side) made the difference obvious in one table.
* Building the queries in CTEs kept the logic readable and let me filter on window results.

## Challenges faced
* **Partial periods:** the first (Jul-1996) and last (May-1998) months are incomplete, which created misleading growth numbers (e.g. -85% in May-1998). Solved by flagging them and excluding them from the growth ranking in Q12.
* **Missing revenue column:** revenue had to be engineered from price, quantity and discount before any analysis was possible.
* **LIMIT hiding groups:** in an early version of Q9 the `LIMIT` cut off two of the three sample customers. Filtering on a `ROW_NUMBER` sequence fixed it.
* **Only IDs available:** no product, customer or employee name tables were provided, so results are read by ID.

## Key learnings
* PARTITION BY restarts the calculation per group; ORDER BY inside OVER defines the sequence.
* Window functions keep every row, unlike GROUP BY, and cannot be used directly in WHERE - wrap them in a CTE.
* Always add a tiebreaker to ROW_NUMBER for repeatable results.
* LAG returns NULL on the first row of each partition, so growth % needs NULL handling.
* Combining functions (LAG feeding RANK in Q12) is where the real analytical power is.

## Suggestions to improve the task
* Provide product, customer and employee tables (or a ready-made database) so results can show names.
* Add LEAD, NTILE and moving averages as an optional stretch goal.
* Give sample expected output for one query so learners can self-check.
* Suggest year-over-year comparison as a follow-up once data covers more than two years.

## Self-assessment
| Area | Rating (1-5) |
|---|---|
| Understanding of ranking functions | 4 |
| Understanding of LAG / trend analysis | 4 |
| Data cleaning | 4 |
| Documentation | 5 |
| Difficulty of task | 3 / 5 (moderate) |

## Next steps
Practice LEAD, NTILE, FIRST_VALUE and moving averages (`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`), then repeat on AdventureWorks.
