# Executive KPI Dashboard – Superstore (Power BI)

**Task 26 | Data Analytics Track | Veda Technology Internship**

A one-page, interactive management dashboard showing sales, profitability, discounting and loss hotspots, with slicers for Region, Segment, Category and Ship Mode.

## Objective
Design a concise business report that answers: *How big are we? Are we profitable? Where are we losing money?*

## Dashboard preview
![Dashboard](dashboard.png)

## Tools
Power BI Desktop (Power Query, DAX), Python (pandas) for preprocessing.

## Dataset
`SampleSuperstore.csv` – 9,994 transaction lines with Ship Mode, Segment, location (City, State, Postal Code, Region), Category, Sub-Category, Sales, Quantity, Discount and Profit.

**Limitation:** this version has no date, Order ID or customer fields, so there is no time trend, year-over-year growth or order count. The dashboard is designed around profitability and mix instead.

## Data preprocessing (`preprocess_superstore.py`)
| Check | Result |
|---|---|
| Rows × columns | 9,994 × 13 → 9,977 × 19 |
| Missing values | 0 |
| Exact duplicates | 17 removed |
| Invalid values (sales ≤ 0, quantity ≤ 0, discount outside 0–1) | 0 |
| Postal code | stored as 5-digit text (449 zero-padded) |
| Constant column | Country dropped |
| Outliers | kept (genuine losses and large deals) |

Features created: `Profit_Margin`, `Sales_Per_Unit`, `Discount_Band` (+ sort order), `Loss_Making`, `Loss_Flag`, `Row_ID`. Full log: `data_quality_log.txt`.

## KPIs
Total Sales · Total Profit · Profit Margin % · Avg Discount % · Loss-Making Rate %. Definitions and DAX: `KPI_Definitions.md`.

## Visuals
1. KPI cards
2. Sales and margin by Category (drill to Sub-Category)
3. Profit margin by Discount Band
4. Profit by State (map)
5. Profit by Sub-Category (losses in red)

## Slicers
Region, Segment, Category, Ship Mode (cross-filter all visuals, with a Reset button).

## Key insights
- **Overall:** Sales 2.30M, Profit 286K, margin 12.5%; 18.7% of lines are loss-making.
- **Discounts drive losses:** lines with no discount have a 29.5% margin; discounts above 20% lose money (−15% margin at 21–40%, −77% above 40%).
- **Furniture is the weak category:** 741K in sales but only a 2.5% margin, versus about 17% for Technology and Office Supplies.
- **Problem sub-categories:** Tables (−17.7K), Bookcases (−3.5K) and Supplies (−1.2K) are unprofitable; Copiers, Phones and Accessories are top earners.
- **Regional gap:** West has a 14.9% margin and a 10% loss rate; Central has 7.9% and 31.9%.
- **Loss-making states:** Texas (−25.8K), Ohio (−17.0K), Pennsylvania (−15.6K) and Illinois (−12.6K).
- **Recommendation:** cap discounts at about 20%, review Table and Bookcase pricing, and investigate Central-region discounting.

## Design principles
5 KPIs, 3-colour palette, consistent grid, no gridline clutter, drill-down instead of extra charts.

## Repository structure
```
├── Executive_KPI_Dashboard.pbix
├── dashboard.png / Dashboard.pdf
├── SampleSuperstore.csv
├── Superstore_Clean.csv
├── preprocess_superstore.py
├── data_quality_log.txt
├── KPI_Definitions.md
└── README.md
```

## How to use
1. Open the `.pbix` in Power BI Desktop.
2. Use the slicers; click any bar or state to cross-filter.
3. Drill down Category → Sub-Category with the drill arrows.
4. Click Reset to clear filters.

## Author
Radhika Dinesh Shet – Data Analytics Track
