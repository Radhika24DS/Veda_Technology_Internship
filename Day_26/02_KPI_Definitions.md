# KPI Definitions – Executive Dashboard (Superstore)

Source: `SampleSuperstore.csv` → cleaned to 9,977 transaction lines. One row = one order line (the file has no Order ID, so "orders" cannot be counted).

## Headline KPIs (5)
| KPI | Definition | Formula | Why it matters | Value (all data) |
|---|---|---|---|---|
| Total Sales | Revenue from all transaction lines in the current filter | Sum of Sales | Business size | 2,296,196 |
| Total Profit | Sales minus all costs | Sum of Profit | Real earnings | 286,241 |
| Profit Margin % | Profit per currency unit of sales | Total Profit ÷ Total Sales | Efficiency | 12.47% |
| Avg Discount % | Average discount given per line | Average of Discount | Pricing discipline | 15.63% |
| Loss-Making Rate % | Share of lines sold at a loss | Lines with Profit < 0 ÷ all lines | Risk indicator | 18.7% |

## Supporting measures (tooltips / optional)
| Measure | Definition |
|---|---|
| Total Quantity | Sum of units sold (37,820) |
| Transactions | Count of order lines (9,977) |
| Avg Sales per Transaction | Total Sales ÷ Transactions |

## DAX
```DAX
Total Sales      = SUM(Orders[Sales])
Total Profit     = SUM(Orders[Profit])
Profit Margin %  = DIVIDE([Total Profit], [Total Sales])
Avg Discount %   = AVERAGE(Orders[Discount])
Loss-Making Rate % = DIVIDE(SUM(Orders[Loss_Flag]), COUNTROWS(Orders))

Total Quantity   = SUM(Orders[Quantity])
Transactions     = COUNTROWS(Orders)
Avg Sales per Transaction = DIVIDE([Total Sales], [Transactions])

Profit Color = IF([Total Profit] >= 0, "#2A9D8F", "#E63946")
Margin Color = IF([Profit Margin %] >= 0.1, "#2A9D8F", IF([Profit Margin %] >= 0, "#F4A261", "#E63946"))
```
Use `Profit Color` / `Margin Color` in Conditional formatting → Format by → Field value.

## Slicers
Region, Segment, Category, Ship Mode.

## Notes and assumptions
- No date field exists, so trend and year-over-year KPIs are excluded by design.
- Avg Discount % is a simple average of lines, not weighted by sales.
- Margin colour thresholds (10% / 0%) are illustrative; adjust to company targets.
- 17 exact duplicate rows were removed; losses and large deals were kept.
