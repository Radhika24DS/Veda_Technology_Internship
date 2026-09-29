# Task 22 – Cohort Retention Basics (Online Retail II)

**Track:** Data Analytics | **Tools:** Python (pandas, seaborn), SQL (SQLite) | **Dataset:** Online Retail II (UCI)

## Objective
Build a monthly cohort retention table by customer "signup" month and understand how retention changes over time.

## Key definitions
| Term | Definition used |
|---|---|
| **Cohort** | Group of customers whose **first-ever purchase** happened in the same calendar month (the dataset has no signup date, so first purchase is the acquisition proxy). |
| **Retention window** | Calendar-month offsets: M0 = cohort month, M1 = next month, M2 … up to M23. |
| **Retained in Mn** | Customer placed ≥1 valid order in month (cohort month + n). |
| **Retention %** | Retained customers in Mn ÷ cohort size (M0) × 100. |

## Data cleaning (`data/cleaning_log.csv`)
| Step | Rows left |
|---|---|
| Raw rows | 1,067,371 |
| Drop missing Customer ID (can't be tracked) | 824,364 |
| Remove cancellations (`C…`) and adjustments (`A…`) | 805,620 |
| Remove Quantity ≤ 0 or Price ≤ 0 | 805,549 |
| Remove exact duplicate rows | 779,425 |
| Drop incomplete month (Dec-2011, data ends 9 Dec) | 762,398 |

Also: `Customer ID` cast to int, descriptions trimmed/uppercased, `revenue` and `order_month` created. Final: **5,850 customers, Dec 2009 – Nov 2011 (24 full months)**.
Cells not yet observable (e.g. M12 for a 2011 cohort) are left blank (NaN), **not** treated as 0%.

## Project structure
```
├── cohort_retention_analysis.py   # end-to-end Python pipeline (clean → cohort → heatmap → SQL check)
├── sql/cohort_retention.sql       # SQL version of the cohort table (CTEs)
├── data/
│   ├── online_retail_clean.csv.gz # cleaned transaction data
│   ├── cleaning_log.csv
│   ├── cohort_counts.csv          # cohort table – customer counts
│   ├── cohort_retention_pct.csv   # cohort table – retention %
│   └── sql_cohort_output.csv      # SQL query output (long format)
├── images/
│   ├── cohort_retention_heatmap.png
│   ├── avg_retention_curve.png
│   └── cohort_sizes.png
├── INSIGHTS.md
├── LINKEDIN_POST.md
└── FEEDBACK.md
```
The SQL output was loaded and compared to the pandas table – **they match exactly**.

## How to run
```bash
pip install pandas numpy matplotlib seaborn
# edit RAW / OUT paths at the top of the script, then:
python cohort_retention_analysis.py
```
SQL: load the cleaned data into a table `orders(invoice, customer_id, invoice_date)` and run `sql/cohort_retention.sql` (SQLite syntax; swap `strftime` for `DATE_TRUNC` on Postgres).

## Heatmap
![Cohort retention heatmap](images/cohort_retention_heatmap.png)

## Headline insights (full detail in `INSIGHTS.md`)
1. About **21% of customers return in the month after first purchase** (avg M1 = 21.5%), and retention then plateaus around 16–22%. This is a **flat tail rather than a steady decline**, so most churn happens in month 1.
2. The **Dec-2009 cohort (35% M1, ~38% at M12) is a special case**: the dataset starts that month, so it includes existing customers, not just new ones. Excluding it, average M1 falls to 20.8% and M12 to 17.9%.
3. **Seasonality:** every cohort dips in Dec-2010 and peaks in Sep–Nov (Q4 gifting), so the calendar month matters as much as cohort age.
4. **Weakest cohort:** Dec-2010 (n=76, M1 = 9.2%). **Strongest recent cohorts:** Aug–Oct 2011 (M1 27–32%).
5. Cohort size and quality are not the same: big early cohorts (Dec-09 → Mar-10) retained better than most 2010 H2 cohorts.

## Limitations
- First purchase in the dataset ≠ true signup; Dec-2009 is left-censored.
- Retention is measured by *any* order in a month (active-customer definition), not by order value.
- Later cohorts have fewer observable months and small sizes (n≈70–120), so their percentages are noisy.

## Interview questions
- **What is a cohort?** A group of users who share a defining event in the same time period (e.g. first purchase in Jan 2010), tracked together over time.
- **Why is cohort retention useful?** It separates behaviour by age from behaviour by acquisition period, so you can see whether newer customers are better or worse than older ones, spot when customers churn, measure the effect of campaigns/product changes, and forecast lifetime value.
