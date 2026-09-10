# RetailIQ: Superstore Performance Dashboard
### *Turning Transactions into Insight*

**Task:** Data Analytics Track — Level 1, Day 3: Simple Sales Dashboard Design
**Tool used:** Power BI Desktop
**Dataset:** Sample Superstore

---

## 📌 Objective

Turn cleaned sales data and a small set of KPIs into an interactive dashboard a stakeholder could open and explore on their own — no walkthrough needed.

---

## 🧹 Data Cleaning

Source file: `SampleSuperstore.csv` (9,994 rows, 13 columns)

| Step | Action | Result |
|---|---|---|
| 1 | Removed exact duplicate rows | 9,994 → 9,977 rows |
| 2 | Fixed Postal Code data type | Changed from Number → Text (prevents accidental summing) |
| 3 | Verified numeric types | Sales, Discount, Profit = Decimal; Quantity = Whole Number |
| 4 | Kept negative Profit values | These are genuine loss-making orders (high-discount sales), not data errors |

Cleaning was done inside Power BI's **Power Query Editor**, so it's a repeatable step — refreshing the data source re-applies the same cleaning automatically.

**Note:** This dataset version has no Order Date, Order ID, or Customer Name column, so month-over-month trends and customer-level views were not possible. Region, State, Category, Sub-Category, and Segment were used as the primary analytical dimensions instead.

---

## 📊 KPIs

Four KPIs were chosen to keep the header focused and scannable:

| KPI | DAX Measure | Why it's here |
|---|---|---|
| **Total Sales** | `SUM(Sales)` | Headline revenue figure |
| **Total Profit** | `SUM(Profit)` | Absolute profitability |
| **Profit Margin %** | `DIVIDE([Total Profit],[Total Sales])` | Profitability *rate* — sales alone can be misleading |
| **Total Units** | `SUM(Quantity)` | Volume check, alongside revenue |

**Color coding:** Profit Margin % turns **green** when ≥ 10%, **red** when below — a quick visual health check.

---

## 📈 Dashboard Visuals

1. **KPI Cards** (x4) — Total Sales, Total Profit, Profit Margin %, Total Units
2. **Sales by Region** — clustered bar chart, sorted descending
3. **Sales by Category & Segment** — stacked column chart
4. **Sales by Segment** — donut chart
5. **Sales by State** — ranked bar chart
6. **Sales by Sub-Category** — treemap
7. **Sales by State** — filled/bubble map (geographic view)

## 🎛 Interactivity

- **Region Slicer** (tile style, top-right) — click any region to filter every visual and KPI card on the page simultaneously. Click again to clear the selection and return to full totals.

---

## 📁 How to Read This Dashboard

- Start with the **4 KPI cards** at the top for the headline numbers.
- Use the **Region slicer** to drill into a specific region — every chart updates together.
- **Sales by Region** and **Sales by State** show *where* the business is strongest.
- **Sales by Category/Segment** and the **Sub-Category treemap** show *what* is selling and to *whom*.
- **Profit Margin %** color (green/red) is the fastest way to judge overall health at a glance.

---

## 🗂 Files in this submission

| File | Description |
|---|---|
| `SampleSuperstore_clean.csv` | Cleaned dataset (duplicates removed) used as the data source |
| `RetailIQ_Superstore_Dashboard.pbix` | Interactive Power BI dashboard file |
| `README.md` | This file — project summary and how-to-read guide |

---

*Prepared by Radhika — Data Analytics Track, Level 1, Day 3*gi