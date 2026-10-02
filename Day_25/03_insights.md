# 5 Business Insights  (source: northwind_orders.csv, 830 orders, Jul-1996 to May-1998)

**1. Order volume nearly doubled by 1998.**
1997 averaged 34 orders/month; Jan-Apr 1998 averaged 64/month (256 orders in 4 months), up ~88%. Volume stepped up in Dec-1997 (+41% MoM) and Mar-1998 (+35% MoM). May-1998 (14 orders) is a partial month and should not be read as a drop.
*Action:* scale fulfilment capacity and stock planning for the higher run-rate.

**2. Sales are geographically concentrated.**
Germany and the USA are 14.7% of orders each (29.4% together); the top 5 countries (Germany, USA, Brazil, France, UK) account for 55.4% of orders, and the top 10 for 80.6%.
*Action:* protect these core markets; test growth campaigns in the smaller ones (Poland, Norway, Portugal, Argentina: under 2% each).

**3. Freight cost is driven by a few markets, and Austria is an outlier.**
The USA (21.2%) and Germany (17.4%) carry the most freight cost. Austria has only 4.8% of orders but 11.4% of total freight, with an average of $184.79 per order, 2.4x the overall average of $78.24. Ireland is also high ($145.01 per order).
*Action:* review shipping rates, order consolidation and free-shipping thresholds for Austria and Ireland.

**4. A small group of customers drives order volume.**
89 customers placed orders (avg 9.3 each). The top 3 (SAVEA 31, ERNSH 30, QUICK 28 orders) place 10.7% of all orders and generate 28.5% of all freight cost; the top 10 account for 25.7% of orders.
*Action:* set up key-account management and retention offers; watch dependency risk.

**5. Delivery performance is mostly good but uneven.**
Of 809 shipped orders, 37 (4.6%) arrived after the required date; average time to ship is 8.5 days; 21 orders are still open (all placed Apr 8 - May 6, 1998). United Package handles the most orders (326) but is the slowest (9.2 days), costliest (avg freight $86.64) and has the most late orders (16); Federal Shipping is fastest (7.5 days). Employee 9 has the highest late rate (9.5%, 10.9 days to ship) and Ireland the highest country late rate (15.8%).
*Action:* shift volume toward Federal Shipping where feasible; coach/rebalance workload for the slowest employee.

> Scope note: revenue, product and customer-name insights need order_details, products and customers tables, which were not in the supplied file. See `07_full_multitable_template.sql`.
