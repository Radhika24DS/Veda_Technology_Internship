# Insights & Recommendations – Repeat Purchase Analysis

**Definition:** a *repeat customer* is a customer with **2 or more distinct invoices** (orders) between 1-Dec-2009 and 9-Dec-2011. *Repeat rate = repeat customers ÷ all identified customers.*

## Headline numbers
| Metric | Value |
|---|---|
| Customers analysed | 5,853 |
| Repeat customers / one-time | 4,234 / 1,619 |
| **Repeat rate** | **72.34%** |
| Repeat rate within 90 days of first order | 47.1% (customers with ≥90 days of history) |
| Orders / customer | 6.25 (8.26 for repeat customers) |
| Median days between 1st and 2nd order | 56 |
| AOV – first-time (one-time) customers | £343.87 |
| AOV – repeat customers | £472.38 (+37%) |
| AOV – first orders vs repeat orders | £407.16 vs £478.03 (+17%) |
| Avg CLV – repeat vs one-time | £3,903 vs £344 (11×) |

## Segment table
| Segment | Customers | % cust. | Revenue (£) | % revenue | Avg CLV (£) | Avg recency (days) |
|---|---|---|---|---|---|---|
| 1 order (One-Time) | 1,619 | 27.7% | 556,725 | 3.3% | 344 | 352 |
| 2–3 orders (Occasional) | 1,604 | 27.4% | 1,629,308 | 9.5% | 1,016 | 217 |
| 4–9 orders (Regular) | 1,669 | 28.5% | 3,511,364 | 20.6% | 2,104 | 124 |
| 10+ orders (Champions) | 961 | 16.4% | 11,383,732 | 66.7% | 11,846 | 47 |

## Key insights
1. **Loyalty is strong but concentrated.** 72% of customers repeat, yet 16% of customers (10+ orders) generate 67% of revenue. Losing a handful of Champions would hurt far more than losing many one-timers.
2. **Repeat customers spend more per order.** AOV is 37% higher for repeat customers, and order #2+ is 17% above order #1 – trust builds basket size.
3. **The first 2 months decide.** Median time to the second order is 56 days; 47% of customers come back within 90 days. A follow-up at ~day 30–45 is the best window.
4. **Retention fades quickly after month 1.** Roughly 15–25% of a cohort buys again in month 1, and about 13–25% are still active 12 months later for most 2010 cohorts; the Dec-2009 cohort (existing customers when data starts) retains far better (35–40%).
5. **Lapse risk is in the middle.** 2,379 customers (41%) have not bought in 180+ days, including 761 Occasional and 413 Regular buyers – a reactivation pool.
6. **UK dominates** (91% of customers; repeat rate 72.5%). Germany (78.5%) and France (69.6%) are comparable, so growth levers are acquisition abroad rather than loyalty fixes.

## Recommendations
- Triggered email/offer 30–45 days after the first order to convert one-timers.
- VIP programme / account managers for the 961 Champions (watch the 61 who have lapsed).
- Win-back campaign for Occasional/Regular customers in the 91–180-day At Risk window (589 customers).
- Bundle / minimum-spend offers to lift first-order AOV toward repeat-order AOV.

## Limitations (be honest in interviews)
- The dataset is largely **B2B wholesalers**, so repeat rates are far higher than typical B2C (Olist is ~3%).
- 243k rows (23%) had no Customer ID and are excluded – guest buyers' behaviour is unknown.
- Observation window is 2 years; one-time customers near the end may still repeat (right-censoring). Dec-2011 is a partial month.
- Dec-2009 cohort includes pre-existing customers.
- "Repeat" counts two invoices on the same day as repeat; counting only orders on different days gives 71.4% (4,179 customers), so the result is robust.
