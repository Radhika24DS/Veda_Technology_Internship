# Salesperson Performance Analysis (Superstore)

**Veda Technology Internship – Data Analytics Track – Task 27**
**Tools:** SQL · Excel · Power BI · Python (pandas, for cleaning)

Comparing salespeople fairly using **sales, profit, margin, average order value, discount discipline and a territory-adjusted margin** – not revenue alone.

---

## 1. Objective
Evaluate sales performance fairly by combining multiple KPIs and accounting for territory differences, then deliver a **ranking**, a **dashboard** and **recommendations**.

## 2. Important data note (please read)
The Superstore file provided has **no Salesperson, Order Date or Order ID column**. I handled this explicitly instead of inventing data:

| Requirement | What the data allows | What I did |
|---|---|---|
| Salesperson | Region and State only | Two proxies: **Region Team (4)** and **State Rep (49)** |
| Growth | No date field | **Not calculated** (weight 0%, marked N/A). DAX for YoY is included in `powerbi/measures.dax` for when dates exist |
| Average Order Value | No Order ID | **AOV (proxy) = sales per line item** |
| Territory size | No population/quota data | **Product-mix benchmark** + **size tiers** (see Method) |

## 3. Dataset
- Source: Sample Superstore (9,994 rows × 13 columns, United States).
- After cleaning: **9,977 rows**, 18 analysis columns.

## 4. Data cleaning (see `data/cleaning_log.csv`)
| Step | Result |
|---|---|
| Missing values | 0 found |
| Exact duplicate rows | 17 removed (no Order ID exists to prove they are separate orders) |
| Postal Code | Converted to 5-digit text (449 leading zeros restored) |
| Constant column | `Country` dropped (always United States) |
| Validity checks | No sales ≤ 0, quantity ≤ 0 or discount outside 0–1 |
| Outliers | 1,168 extreme-profit rows **flagged, not removed** (they are real big wins/losses) |
| New columns | Profit Margin, Loss Flag, Discount Band, Salesperson (Region Team), Salesperson (State Rep), Profit Outlier |

## 5. Method
1. **KPIs per salesperson:** Sales, Profit, Profit Margin, Line items, AOV (proxy), Avg Discount, % loss-making lines.
2. **Territory fairness – Margin Gap:** expected margin = margin a unit would earn if it sold its own product mix at the *national* margin of each sub-category. `Margin Gap = actual margin − expected margin`. A rep in a Furniture-heavy territory is no longer punished for the mix.
3. **Size tiers (State Reps):** Small / Mid / Large by sales percentile, with *rank within tier* and a low-volume warning (< 50 line items).
4. **Composite score (0–100):** min-max normalise each KPI, then weight:

| KPI | Weight |
|---|---|
| Sales | 20% |
| Profit | 25% |
| Profit Margin | 20% |
| AOV (proxy) | 10% |
| Discount discipline (lower avg discount = better) | 10% |
| Margin Gap vs mix benchmark | 15% |
| Growth | 0% (N/A) |

Weights are editable in the `Weights` sheet of the workbook and everything recalculates.

## 6. Key results – Region Team ranking
| Rank | Region Team | Sales | Profit | Margin | Avg Discount | Margin Gap | Score | Rank on sales only |
|---|---|---|---|---|---|---|---|---|
| 1 | West | $725,256 | $108,330 | 14.9% | 11.0% | +2.6 pp | **94.3** | 1 |
| 2 | East | $678,435 | $91,506 | 13.5% | 14.5% | +0.6 pp | **79.3** | 2 |
| 3 | South | $391,722 | $46,749 | 11.9% | 14.7% | +0.9 pp | **43.1** | 4 |
| 4 | Central | $500,783 | $39,656 | 7.9% | 24.0% | −5.3 pp | **6.5** | 3 |

**State Reps:** top – California (76.0), New York (73.9), Michigan (57.4), Washington (55.9). Bottom – Ohio, Colorado, Illinois, Tennessee, Texas (Texas lost $25.8K on $170K sales).

### Insights
- **Revenue alone misleads.** Central is 3rd on sales but last on composite score; South is 4th on sales but 3rd overall.
- **Discounts are the biggest driver.** Lines discounted over 30% lose **$125K** on $260K of sales; undiscounted lines earn **+$321K**. Central discounts over 30% on 21% of its lines vs 3.7% in West.
- **Furniture is a weak spot everywhere.** It is loss-making in Central (−1.8% margin); Tables lose about $17.7K overall (East, Central and South).
- **Territory/mix does not excuse Central.** Its product mix would predict a 13.3% margin (the highest of the four regions), yet it earned 7.9% – a −5.3 pp gap. The shortfall comes from discounting behaviour, not from an unfavourable mix.

## 7. Recommendations
1. Cap discounts and require manager approval above 20% (above 30% company-wide), starting in **Central**.
2. Use the **composite scorecard, not revenue**, for incentives and reviews.
3. Replicate **West's** discounting and deal-approval practices.
4. Run deal reviews in the bottom-10 states (Ohio, Colorado, Illinois, Tennessee, Texas…).
5. Review Table pricing and Furniture discounting.
6. Collect **Salesperson, Order Date, Order ID and territory data** so growth, true AOV and quota attainment can be added.

## 8. Dashboard (Power BI)
Four pages: **Executive Overview · Salesperson Scorecard · Territory Fairness · Discount & Risk Drivers**.
Features: KPI cards, ranking matrix with conditional formatting, synced slicers, drill-through, tooltips, bookmarks, dynamic title, adjustable weights.
Build steps: [`docs/PowerBI_Dashboard_Guide.md`](docs/PowerBI_Dashboard_Guide.md) · DAX: [`powerbi/measures.dax`](powerbi/measures.dax)

![Dashboard screenshot](powerbi/screenshots/page1_overview.png)
*(Replace with your Power BI screenshot.)*

Live link: `ADD_POWER_BI_PUBLISH_LINK_HERE`

## 9. Interview questions
**Why is revenue alone insufficient?**
Revenue ignores cost and quality. A rep can sell a lot by discounting heavily and still lose money – in this data, Central is 3rd in sales but last overall, with a 7.9% margin and 32% of lines losing money. Profit, margin, discount discipline and deal size show whether the sales are worth having.

**How can territory affect comparison?**
Territories differ in product mix, customer segments and size – California simply has far more customers than Vermont, and a territory heavy in low-margin sub-categories would look worse for reasons outside the rep's control. I handled this with a product-mix-adjusted margin (Margin Gap), size tiers with rank within tier, and low-volume warnings. In this data the adjustment actually showed that Central's weak result is *not* a mix effect (its mix predicts 13.3% margin, it earned 7.9%).

## 10. Repository structure
```
├── README.md
├── SUBMISSION_CHECKLIST.md
├── LINKEDIN_POST.md
├── FEEDBACK.md
├── data/
│   ├── SampleSuperstore_raw.csv      raw input
│   ├── superstore_clean.csv          cleaned data (Power BI / SQL source)
│   ├── cleaning_log.csv              every preprocessing step
│   ├── region_ranking.csv            scorecard, 4 Region Teams
│   └── state_ranking.csv             scorecard, 49 State Reps
├── sql/salesperson_analysis.sql      KPIs, mix benchmark, composite score, ranking
├── excel/Salesperson_Performance_Analysis.xlsx   formula-driven analysis workbook
├── powerbi/
│   ├── measures.dax
│   ├── Salesperson_Performance_Dashboard.pbix    (add after building)
│   └── screenshots/                              (add after building)
├── docs/PowerBI_Dashboard_Guide.md
└── scripts/
    ├── 01_clean_data.py
    └── 02_build_workbook.py
```

## 11. How to reproduce
```bash
python scripts/01_clean_data.py       # raw -> data/superstore_clean.csv + cleaning_log.csv
python scripts/02_build_workbook.py   # builds the Excel workbook
# SQL: load data/superstore_clean.csv into table superstore_clean, then run sql/salesperson_analysis.sql
```
The SQL results were checked against the Excel workbook (same scores and ranks).

## 12. Limitations
- Region/State are proxies for salespeople; individual rep results may differ.
- No growth/time analysis (no dates).
- AOV is per line item, not per order.
- Small states (e.g., District of Columbia, 10 lines) have unstable scores – flagged in the workbook.
- Min-max scoring with only 4 Region Teams exaggerates gaps; read scores together with the raw KPIs.
