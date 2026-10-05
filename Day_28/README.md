# Customer Repeat Purchase Analysis

**Veda Technology Internship – Data Analytics Track – Task 28**
Measure repeat purchase behaviour, compare first-time vs repeat order value and segment customers by loyalty. Built with **Python, SQL and Power BI** on the *Online Retail II* dataset (UCI).

## Problem
How many customers come back, how much more do they spend, and which customers drive the revenue?

## Key results
| KPI | Value |
|---|---|
| Customers analysed | 5,853 |
| **Repeat rate** (2+ orders) | **72.34%** |
| AOV – one-time customers vs repeat customers | £343.87 vs £472.38 (+37%) |
| AOV – first orders vs repeat orders | £407.16 vs £478.03 |
| Median days to 2nd order | 56 |
| Champions (10+ orders) | 16.4% of customers → 66.7% of revenue |
| Customers lapsed 180+ days | 2,379 (41%) |

![Dashboard](dashboard_screenshot.png)

## Definition
> **Repeat customer** = a customer with **≥ 2 distinct invoices** in the data window (1-Dec-2009 → 9-Dec-2011).
> **Repeat rate** = repeat customers ÷ total identified customers.
> **AOV** = total order revenue ÷ number of orders (revenue = quantity × unit price).

## Data cleaning (raw 1,067,371 rows → 776,827 clean rows)
| Step | Rows removed |
|---|---|
| Missing Customer ID (guest checkouts) | 243,007 |
| Cancellation invoices (start with "C") | 18,744 |
| Quantity ≤ 0 or price ≤ 0 | 71 |
| Non-product lines (POST, D, M, BANK CHARGES, AMAZONFEE, etc.) | 2,662 |
| Exact duplicate rows | 26,060 |

Also: parsed dates, standardised column names/text, created `revenue`, built order-level and customer-level tables, assigned order sequence number, recency, frequency segments and cohort month.

## Segments
| Segment | Customers | % revenue |
|---|---|---|
| One-Time (1 order) | 1,619 | 3.3% |
| Occasional (2–3) | 1,604 | 9.5% |
| Regular (4–9) | 1,669 | 20.6% |
| Champions (10+) | 961 | 66.7% |

Recency status: Active (≤90 d), At Risk (91–180 d), Lapsed (>180 d).

## Project structure
```
├── README.md
├── repeat_purchase_analysis.py      # cleaning + analysis (Python)
├── repeat_purchase_analysis.sql     # same metrics in SQL
├── data/                            # raw online_retail_II.csv (not committed – too large, download from UCI)
├── output/
│   ├── online_retail_cleaned.csv    # cleaned line-level data (81 MB – use Git LFS or omit)
│   ├── segment_table.csv  aov_comparison.csv  segment_by_recency.csv  kpis.json
│   ├── powerbi_data/                # tables loaded into Power BI
│   └── charts/                      # PNG charts
├── Repeat_Purchase_Dashboard.pbix   # Power BI file
└── dashboard_screenshot.png
```

## How to run
```bash
pip install pandas matplotlib
python repeat_purchase_analysis.py
```
Then open Power BI Desktop → Get Data → load the CSVs in `output/powerbi_data/` and follow `PowerBI_Dashboard_Guide.md`.

## Insights
1. Loyalty is strong but concentrated: 16% of customers produce two-thirds of revenue.
2. Repeat customers have a 37% higher AOV; order #2+ is 17% larger than the first order.
3. Half of the customers who return do so within ~2 months, so follow-up timing matters.
4. 589 customers are "At Risk" and 2,379 lapsed – a clear win-back target.

## Recommendations
Trigger a day 30–45 follow-up, create a VIP programme for Champions, run win-back offers in the 91–180-day window, and use bundles to lift first-order value.

## Limitations
B2B-heavy dataset (repeat rate is much higher than typical B2C), 23% of rows without Customer ID excluded, 2-year window (right-censoring), Dec-2011 partial month.

## Interview Q&A
- **How do you define repeat customer?** A customer with 2+ distinct orders (invoices) in the observation window; one-timers have exactly one.
- **Why track repeat rate?** It shows loyalty and product-market fit, and repeat customers are cheaper to retain than new ones are to acquire, so it drives CLV, marketing budgets and forecasting.

## Tools
Python (pandas, matplotlib), SQL, Power BI (DAX), GitHub.

*Author: Radhika Dinesh Shet*
