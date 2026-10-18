# Power BI Guide: building the COVID-19 Global Impact Dashboard

Dataset: `data/covid_cleaned.csv` (226 rows, 35 columns). Optional: `data/powerbi_continent_summary.csv`.
Time: about 60-90 minutes. Power BI Desktop is free (Windows).

> Your file is a **snapshot** (one row per country), so there is no date axis. The dashboard compares **countries**, **continents** and **testing levels**, not time periods. If you later get the Our World in Data time series, add it as a second table and relate it on `country`.

---
## Step 1. Load and check the data
1. **Home > Get data > Text/CSV** > pick `covid_cleaned.csv` > **Transform Data**.
2. In Power Query, confirm types: text for `country`, `continent`, `population_size`, `testing_tier`, `cfr_band`, `burden_tier`; whole number for counts; decimal for ratios; **True/False** for every column in the flag group (`analysis_sample`, `small_population`, ...).
3. Set `country` **Data category = Country/Region** (Column tools tab) so the map geocodes.
4. **Close & Apply**.
5. Rename the table to `Covid`.

## Step 2. Sort order for the category columns
Power BI sorts text alphabetically, which breaks tiers. For each, add a numeric helper and use **Sort by column**:
- Create column: `Tier Sort = SWITCH([testing_tier],"Q1 Lowest testing",1,"Q2",2,"Q3",3,"Q4 Highest testing",4)`, then select `testing_tier` > Column tools > **Sort by column** > `Tier Sort`.
- Same idea for `population_size` (<1M, 1-10M, 10-50M, 50-200M, >200M) and `cfr_band`.

## Step 3. DAX measures
Create a table for measures: **Home > Enter data > name it `_Measures`** (empty), then add:

```DAX
Total Cases   = SUM(Covid[total_confirmed])
Total Deaths  = SUM(Covid[total_deaths])
Population    = SUM(Covid[population])
Total Tests   = SUM(Covid[total_tests])

Cases per 1M  = DIVIDE([Total Cases],  [Population]) * 1000000
Deaths per 1M = DIVIDE([Total Deaths], [Population]) * 1000000
CFR %         = DIVIDE([Total Deaths], [Total Cases])

-- Tests only where testing data exists, so averages are not distorted by blanks
Tests per 1M =
VAR pop_with_tests = CALCULATE(SUM(Covid[population]), NOT ISBLANK(Covid[total_tests]))
RETURN DIVIDE([Total Tests], pop_with_tests) * 1000000

Positivity % = DIVIDE(CALCULATE([Total Cases], NOT ISBLANK(Covid[total_tests])), [Total Tests])

Share of World Pop %    = DIVIDE([Population],  CALCULATE([Population],  ALL(Covid)))
Share of World Cases %  = DIVIDE([Total Cases], CALCULATE([Total Cases], ALL(Covid)))
Share of World Deaths % = DIVIDE([Total Deaths],CALCULATE([Total Deaths],ALL(Covid)))

Median CFR (sample) =
CALCULATE(MEDIAN(Covid[cfr_pct]), Covid[analysis_sample] = TRUE())

Median Cases per 1M (sample) =
CALCULATE(MEDIAN(Covid[cases_per_1m]), Covid[analysis_sample] = TRUE())

Countries = DISTINCTCOUNT(Covid[country])
```
Format: `CFR %`, `Positivity %` and the three share measures as **Percentage (1 decimal)**; the "per 1M" measures as **Whole number with thousands separator**.

**Important:** set a **page-level filter `analysis_sample = True`** on the ranking and correlation visuals (it removes 69 tiny territories and 10 countries with under 1,000 cases whose per-million values swing wildly). Leave it off the KPI cards if you want true world totals.

## Step 4. Page layout (canvas 16:9)
Use a clean white or very light grey background, one accent colour (blue `#2A78D6`) and one highlight colour (orange `#EB6834`). Fonts: Segoe UI.

### Page 1: "Global Overview"
| Visual | Fields | Insight shown |
|---|---|---|
| 4 **Card** visuals | `Total Cases`, `Total Deaths`, `CFR %`, `Countries` | headline numbers |
| **Slicers** (top row, dropdown style) | `continent`, `population_size`, `testing_tier` | compare at a glance |
| **Filled map** | Location `country`, Colour saturation `Deaths per 1M` (sequential blue) | Insight 4: where the heaviest reported burden is |
| **Clustered column** | Axis `continent`; Values `Share of World Pop %`, `Share of World Cases %`, `Share of World Deaths %` | **Insight 1**: Africa ~18% of people, ~2% of cases; Europe ~9% of people, ~37% of cases |
| **Table** or **Bar chart** | `country`, `Deaths per 1M`; visual filter **Top N = 10** by `Deaths per 1M` | Peru, Bulgaria, Bosnia and Herzegovina, Hungary, North Macedonia |

### Page 2: "Does testing explain the numbers?"
| Visual | Setup | Insight shown |
|---|---|---|
| **Scatter chart** | X `tests_per_1m` (average), Y `cases_per_1m` (average), Details `country`, Legend `continent`. Set **both axes to Log scale** (Format > Axis > Scale type). Page filter `analysis_sample = True` | **Insight 2**: more testing, more reported cases (Spearman 0.92) |
| **Clustered column** | Axis `testing_tier`, Values `Median CFR (sample)` with data labels | **Insight 3**: 1.8% in the lowest-testing quarter vs 0.7% in the highest |
| **Clustered column** | Axis `testing_tier`, Values `Median Cases per 1M (sample)` | the ~3,000 vs ~260,000 contrast |
| **Slicer** | `continent` (syncs across pages: View > Sync slicers) | |

> Note: Power BI's `testing_tier` column in the CSV was cut over all 212 countries with test data, while the notebook cut quartiles over the 154-country analysis sample. With the `analysis_sample = True` filter on the page, the medians in Power BI may differ slightly from the notebook (for example 1.8% vs 0.7%). Quote the notebook/PDF numbers in your write-up, or recreate the tiers inside the sample if you want exact agreement.

### Page 3: "Warning signs" (Insight 5)
| Visual | Setup |
|---|---|
| **Scatter chart** | X `Positivity %`, Y `CFR %`, Details `country`; filter `analysis_sample = True` |
| **Conditional colour** | Format > Data colours > fx > Rules: orange if `Positivity %` > 0.30 **and** `Tests per 1M` < 300000. Easiest route: add a calculated column `Warning flag = IF(Covid[cumulative_positivity_pct] > 30 && Covid[tests_per_1m] < 300000, "High positivity, thin testing", "Other")` and put it in **Legend** |
| **Table** | `country`, `cumulative_positivity_pct`, `tests_per_1m`, `cfr_pct`, `deaths_per_1m`, filtered to `Warning flag` = "High positivity, thin testing" |

### Page 4: "Data quality and notes"
- Card: count of rows where `recovery_data_missing = True` (22).
- Card: count where `recovery_data_stale = True` (16).
- Text box: assumptions (blank deaths = 0; recovered/active not used; snapshot only; per-million excluded under 1M people).

## Step 5. Interactivity checklist
- **Edit interactions** so the map and charts cross-filter each other.
- Add a **Tooltip**: hover on map/scatter shows `country`, `Cases per 1M`, `Deaths per 1M`, `CFR %`, `Tests per 1M`.
- **Bookmarks** (View > Bookmarks): save "Europe vs Africa" and "High burden" views and add **buttons** to jump between them.
- **Drill-through** page: right-click a country > Drill through > a one-country detail page.
- Add **Alt text** on every visual (Format > General) and keep colour contrast high.

## Step 6. Compare any two countries (the "compare at a glance" requirement)
1. Add a **slicer** on `country` set to **Multi-select** (Ctrl+click).
2. The measures have very different scales, so do **not** put them in one chart. Use three **Card** visuals (`Cases per 1M`, `Deaths per 1M`, `CFR %`), or one **Clustered bar** with a single measure, and let the slicer select the countries to compare.
3. For two or three countries side by side, add a **Table** with `country`, `Cases per 1M`, `Deaths per 1M`, `CFR %`, `Tests per 1M`.

## Step 7. Publish and submit
1. **File > Save as** `COVID19_Dashboard.pbix`.
2. Export a **PDF** (File > Export > PDF) and take **screenshots** of each page into `/dashboard_screenshots`.
3. (Optional) **Publish to Power BI Service** (free "Publish to web" is only allowed with a work/school account); otherwise submit the `.pbix` plus screenshots, plus the Jupyter notebook as a live-viewable alternative.
4. Commit `.pbix` and screenshots to GitHub (the .pbix is binary but under 100 MB).

## Common problems
| Problem | Fix |
|---|---|
| Map shows few countries | Make sure `country` Data category is Country/Region; names were already standardised in cleaning |
| Scatter looks like a blob | Switch both axes to **Log scale** |
| Averages differ from my notebook | Use the `analysis_sample = True` filter and **Median** measures, not Average |
| `testing_tier` sorts alphabetically | Use Sort by column (Step 2) |
| Blank values in the map | Expected for small territories (e.g. Micronesia); filter them out with `analysis_sample` |
