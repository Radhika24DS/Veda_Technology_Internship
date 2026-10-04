# Power BI Dashboard – Step-by-Step Guide
**Task 27 – Salesperson Performance Analysis (Superstore)**

> Read this first: your dataset has **no salesperson, order date or order ID column**.
> The dashboard therefore ranks **Region Teams (4)** and **State Reps (49)** as the "salespeople",
> uses **Sales per line item** as the AOV proxy, and **cannot show growth** (say so on the dashboard footer).
> This is a data limitation, not a mistake in the analysis, and pointing it out is a strength in a review.

Files you need (all in this repo):

| File | Use in Power BI |
|---|---|
| `data/superstore_clean.csv` | Main fact table (9,977 rows, already cleaned) |
| `data/region_ranking.csv` | Pre-computed scorecard for the 4 Region Teams |
| `data/state_ranking.csv` | Pre-computed scorecard for the 49 State Reps |
| `powerbi/measures.dax` | Optional dynamic measures (advanced) |

---

## PART 1 – Load and model the data (15 min)

1. Open **Power BI Desktop → Home → Get data → Text/CSV**. Load `superstore_clean.csv`, click **Transform Data**.
2. In Power Query set data types:
   - Text: Ship Mode, Segment, City, State, **Postal Code (Text, keeps leading zeros)**, Region, Category, Sub-Category, Discount Band, both Salesperson columns.
   - Decimal number: Sales, Discount, Profit, Profit Margin.
   - Whole number: Quantity, Loss Flag, Profit Outlier.
3. Rename the query to **Superstore**. Check **Column quality / distribution** (View tab): 0 errors, 0 empty.
4. Load `region_ranking.csv` and `state_ranking.csv` the same way (name them **Region_Ranking** and **State_Ranking**). Set all numeric columns to Decimal/Whole.
5. **Close & Apply**.
6. Model view: create relationships (Many-to-one, single direction, from Superstore to the ranking tables):
   - `Superstore[Region]` → `Region_Ranking[Region]`
   - `Superstore[Salesperson (State Rep)]` → `State_Ranking[Salesperson]`
   (If Power BI complains about uniqueness, leave the ranking tables unrelated and use them only in their own visuals.)
7. Create a table called **_Measures** (Home → Enter data → empty → name it) and keep all measures in it.
8. Paste the measures from `powerbi/measures.dax` (Section 0 is a calculated column, the rest are measures). Format: Sales/Profit → Currency 0 dp, Margin/Discount/Loss % → Percentage 1 dp.

> **Two ways to build the ranking visuals**
> **Option A (simple, recommended for submission):** use the `Region_Ranking` / `State_Ranking` tables (scores already calculated and verified against SQL and Excel).
> **Option B (advanced, dynamic):** use the DAX measures `Composite Score`, `Rank (Composite)` etc. so scores react to slicers and weight parameters.

---

## PART 2 – KPIs (cards) you must show

| # | KPI | Measure | Why it matters |
|---|---|---|---|
| 1 | Total Sales | `Total Sales` | Scale |
| 2 | Total Profit | `Total Profit` | Value actually created |
| 3 | Profit Margin | `Profit Margin` | Efficiency – answers "why is revenue alone insufficient?" |
| 4 | AOV (proxy) | `AOV (proxy)` | Deal size (sales per line item) |
| 5 | Avg Discount | `Avg Discount` | Discount discipline |
| 6 | Loss-making lines % | `Loss Line %` | Quality of selling |
| 7 | Margin Gap (pp) | `Margin Gap (pp)` | Fair comparison – result vs mix-expected margin |
| 8 | Composite Score & Rank | `Composite Score`, `Rank (Composite)` | Overall ranking |
| – | Growth | *not available* | State "N/A – dataset has no date field" in a text box |

Card tips: use the **New card visual** or Multi-row card; turn on *Reference labels* to show "vs company average"; add conditional font colour (green ≥ company margin, red below).

---

## PART 3 – Page layout (build 4 pages)

Canvas: 16:9 (1280×720). Theme: **View → Themes → Executive** (or any dark-blue/neutral theme). Use ONE accent colour for "good" (green) and ONE for "bad" (red) everywhere. Add a page title text box and footer note: *"Salesperson = Region Team / State Rep (proxy). Growth not shown: no date field. AOV = sales per line item."*

### Page 1 – Executive Overview
| Visual | Fields | Purpose |
|---|---|---|
| 6–7 KPI cards (top row) | Part 2 measures | Headline numbers |
| **Clustered bar** – Sales vs Profit by Region Team | Axis: `Region`; Values: `Total Sales`, `Total Profit` | Shows big sales ≠ big profit |
| **Ranking table** | `Salesperson`, `Composite Score` (data bars), `Rank (Composite)`, `Rank (Sales only)`, `Rank change` | The deliverable "Ranking" |
| **Filled map / bar** by State – Profit | `State`, `Total Profit` (red/green diverging) | Geography of profit |
| Slicers (left or top) | Region, Category, Segment, Ship Mode, Discount Band | Interactivity |

### Page 2 – Salesperson Scorecard (the ranking page)
| Visual | Fields |
|---|---|
| **Matrix** | Rows: `Salesperson`; Values: Sales, Profit, Margin, AOV, Avg Discount, Loss %, Margin Gap, Composite Score, Rank. Apply **conditional formatting**: data bars (Sales, Profit), colour scale (Margin, Margin Gap), icons (Rank) |
| **Radar-style comparison** (use a clustered bar of normalised KPIs `n Sales … n Margin Gap`) for a selected salesperson | Shows each person's profile |
| **Bar chart – Composite Score** sorted desc, colour by tier (`Performance Tier`) | Visual ranking |
| **Top N slicer / filter** | Visual filter on `Rank` ≤ 10 for State Reps |
| (Bonus) **Weights panel** – 6 what-if parameter slicers | Let the viewer change the weights; ranking updates live (Option B) |

### Page 3 – Territory Fairness (answers "How can territory affect comparison?")
| Visual | Fields |
|---|---|
| **Matrix heatmap** Region × Category, value `Profit Margin` (red–white–green, midpoint 0) | Furniture in Central is negative – a territory/mix effect |
| **Clustered column** – `Profit Margin` vs `Expected Margin` by Region Team | Shows who beats the mix-adjusted benchmark |
| **Bar** – `Margin Gap (pp)` by Region/State | Fair ranking metric |
| **Scatter** – X: `Total Sales`, Y: `Profit Margin`, Size: `Total Profit`, Details: State, Legend: Region | Find big-but-unprofitable states (e.g. Texas) |
| **Size tier slicer** – from `State_Ranking[Size Tier]` | Compare like with like (Small / Mid / Large) |
| Card/text | `Data Quality` warning for states with < 50 line items |

### Page 4 – Discount & Risk Drivers
| Visual | Fields |
|---|---|
| **Column chart** – Profit by `Discount Band` | Shows >30% discount destroys profit |
| **100% stacked bar** – discount band mix by Region | Central has most deep discounts |
| **Decomposition tree** | Analyse: `Total Profit`; Explain by: Region → Category → Sub-Category → State |
| **Table** – Bottom 10 State Reps by composite score with red data bars | Actionable coaching list |
| **Waterfall** – Profit by Sub-Category (Tables / Bookcases negative) | Product drivers |
| Text box – 3 key recommendations (copy from README) | Insight |

---

## PART 4 – Essential features checklist (what reviewers look for)

- [ ] **Slicers synced across pages** (View → Sync slicers)
- [ ] **Drill-through page**: right-click a State/Region → drill to a "Salesperson Detail" page (add field `Salesperson` to *Drill through* well)
- [ ] **Tooltips**: report-page tooltip showing margin, discount and rank on hover
- [ ] **Conditional formatting**: data bars, colour scales, red/green icons
- [ ] **Bookmarks + page navigator buttons** (Insert → Buttons → Navigator → Page navigator)
- [ ] **Dynamic title** using the `Dashboard Title` measure (Title → fx)
- [ ] **Consistent colours**, readable fonts (≥ 10 pt), aligned grid, alt text on visuals
- [ ] **Reset-filters bookmark** button
- [ ] **Mobile layout** (View → Mobile layout) – optional
- [ ] **Footer notes** listing the data limitations (no growth, AOV proxy, Region/State as salesperson)
- [ ] **Performance**: remove unused columns, turn off auto date/time (File → Options → Data load)

---

## PART 5 – Check your numbers (they must match)

| Check | Expected |
|---|---|
| Total Sales | $2,296,195.59 |
| Total Profit | $286,241.42 |
| Profit Margin | 12.5% |
| Line items | 9,977 |
| Composite scores | West 94.3, East 79.3, South 43.1, Central 6.5 |
| Ranking | 1 West, 2 East, 3 South, 4 Central (sales-only: West, East, Central, South) |

If a number differs, check filters/slicers on the page and that Postal Code is Text.

---

## PART 6 – Export and submit

1. Save as `powerbi/Salesperson_Performance_Dashboard.pbix`.
2. Take a full-page screenshot of each page → `powerbi/screenshots/page1_overview.png`, etc. (File → Export → PDF also works; save as `powerbi/Dashboard.pdf`).
3. Optional live link: **Publish → My workspace → Share/Publish to web**. Use *Publish to web* only because this is a public sample dataset (anyone with the link can view it).
4. Push everything to GitHub (see `SUBMISSION_CHECKLIST.md`).
