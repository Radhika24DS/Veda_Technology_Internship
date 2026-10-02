# Interview Questions – Model Answers

**Q1. How can joins cause double counting?**
A join returns one row per *matching pair*. If you join a one-side table (orders, with a freight column) to a many-side table (order_details), each order's freight is repeated once per line item, so `SUM(freight)` after the join is inflated. The same happens when joining two many-side tables (e.g., orders→lines and orders→payments) – rows multiply (fan-out) – and when `COUNT(*)` is used instead of `COUNT(DISTINCT order_id)`.
*Prevention:* know the grain of every table; aggregate measures at the grain where they live (or pre-aggregate in a CTE before joining); use `COUNT(DISTINCT)`; keep a single-grain fact table; use one-to-many relationships in Power BI.

**Q2. How do you validate totals?**
1) Compare row counts before/after each join (fact rows = line rows). 2) Reconcile `SUM(measure)` from the final view against the raw source table. 3) Check sum-of-parts = whole across different groupings (category, country). 4) Check for orphans with LEFT JOIN … IS NULL. 5) Check distinct keys preserved. 6) Match the Power BI card to the SQL total, and spot-check 2–3 orders by hand.
