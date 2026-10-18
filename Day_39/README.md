# COVID-19 Global Impact Dashboard

**Focused question:** *How much of the difference in countries' COVID-19 numbers is real, and how much reflects how hard each country tested?*

An end-to-end data analytics project: cleaning a messy real-world country dataset, deriving population-normalised metrics, finding patterns in Python, and communicating them in plain language through two notebooks, a one-page executive summary and an interactive **Power BI dashboard**.

![Dashboard preview](dashboard/dashboard_screenshot.png)

## Deliverables
| Deliverable | Where |
|---|---|
| Cleaned dataset with documented assumptions | `data/covid_cleaned.csv`, `data/covid_cleaned.xlsx` (with `cleaning_log` sheet), `docs/DATA_DICTIONARY.md` |
| Key insights in plain language (10) | This README, notebooks, executive summary |
| Jupyter notebooks with charts | `notebook/COVID19_Global_Impact_Analysis.ipynb`, `notebook/COVID19_Extended_Visuals.ipynb` |
| Interactive Power BI dashboard | `dashboard/COVID19_Dashboard.pbix` (+ screenshot / PDF export) |
| 1-page executive summary | `COVID19_Executive_Summary.pdf` |

## Data
- **Source:** Worldometer COVID-19 country summary (`worldometer_coronavirus_summary_data.csv`), 226 countries and territories, 12 columns.
- **What it is:** a single **snapshot** (one row per country). It has **no dates and no vaccination columns**. The US total of about 1.03 million deaths suggests it dates from roughly mid-May 2022 (inferred, not stated in the file).
- **What that means:** rolling averages, doubling time, wave analysis and vaccination-rollout analysis are **not possible** with this file. They would need a time-series dataset such as Our World in Data. This project therefore focuses on cross-country comparison, population normalisation and testing intensity.

## Key insights
1. **Uneven burden.** Africa: ~18% of the people, ~2% of reported cases. Europe: ~9% of the people, ~37% of cases.
2. **Cases track testing.** Tests per million vs cases per million: Spearman rho = 0.92 (154 countries with 1M+ people). The least-testing quarter reports ~3,000 cases per million; the most-testing quarter ~260,000.
3. **Fatality rates look worst where testing is thinnest.** Median case fatality rate: 1.8% (lowest-testing quarter) vs 0.7% (highest-testing quarter).
4. **Deaths per million is the fairer yardstick.** Highest: Peru (~6,300), Bulgaria, Bosnia and Herzegovina, Hungary, North Macedonia.
5. **High positivity with thin testing is a warning sign.** Brazil, Mexico, Ecuador, Bolivia, Honduras, Syria and Eritrea have >30% of tests positive with <300k tests per million; the true toll is probably higher than reported.

### Extended insights (second notebook, charts 7-12)
6. **Concentration:** 7 countries account for over half of reported deaths; 22 for 80%.
7. **Deaths vs infections:** relative to their case counts, Peru, Mexico, Bosnia and Herzegovina, Bulgaria and Ecuador have roughly 3.5-6x the typical deaths, while New Zealand, Taiwan, Singapore, Australia and South Korea have roughly one-fifth to one-ninth.
8. **Testing does not close the continent gap:** at similar testing levels, Europe's median deaths per million is about 2-5x Asia's.
9. **Spread inside continents is large** (Asia's fatality rate ranges 0.1% to 18%), so continent averages mislead.
10. **Positivity is highest in the Americas** (South America about 21%, North America about 18%) and lowest in Africa (about 7%).

*These are associations in reported data from one snapshot, not causes.*

## Power BI dashboard
**Page: "Executive Overview"** (1920 x 1080, dark theme in `dashboard/covid_dark_theme.json`)

| Panel | Visual | What it shows |
|---|---|---|
| KPI cards | Card x3 | 521,077,152 reported cases; 6,288,083 reported deaths; 226 countries and territories |
| Global distribution | Bubble map | Total cases by country, coloured by continent |
| Testing intelligence | Scatter (log axes) | Tests per million vs cases per million (rho = 0.92) |
| Mortality analysis | Bar chart, Top 15 | Deaths per million (Peru, Bulgaria, Bosnia and Herzegovina lead) |
| Fatality by testing quartile | Column chart | Median fatality rate: 1.83%, 2.04%, 1.21%, 0.70% |
| Positivity vs fatality | Scatter | Seven flagged countries with >30% positivity and <300k tests per million |
| Data quality | Bar chart | Missing values in the raw file |
| Slicers | Dropdowns | Continent and country |

**Main DAX measures:** `Total Cases`, `Total Deaths`, `Population`, `Countries`, `Cases per 1M`, `Deaths per 1M`, `CFR %`, `Median CFR (sample)`, `Countries in Sample`, `Share of World Cases %`.
**Calculated columns:** `Warning flag` (positivity > 30% and tests per million < 300,000).
**Rule used on rankings and correlations:** visual filter `analysis_sample = True` (population of at least 1 million and at least 1,000 cases; 157 countries).

**Honest notes about the dashboard**
- The data is one snapshot, so there is no trend or vaccination view. I did not add fake "change vs last update" arrows.
- The visual layout was inspired by a dashboard mockup. All data, measures, filters and numbers come from my own cleaned dataset (for example, the mockup's totals did not match the data and were not used).
- The "Spearman rho = 0.92" label is a text box; the value is calculated in the Python notebook.
- Step-by-step build instructions: `docs/POWERBI_DASHBOARD_BUILD_STEPS.md` and `docs/POWERBI_GUIDE.md`.

**To open it:** install Power BI Desktop (free, Windows) and open `dashboard/COVID19_Dashboard.pbix`. If it asks for the data source, point it to `data/covid_cleaned.csv`.

## Cleaning and assumptions (full log in `docs/data_quality_log.csv` and the Excel `cleaning_log` sheet)
| Issue | Treatment |
|---|---|
| 8 blank `total_deaths` | Set to 0 (blank = none reported); flagged `deaths_assumed_zero` |
| 22 blank recovered/active | Left missing, flagged `recovery_data_missing` |
| 16 countries with implausibly low recoveries (<50% of cases) | Flagged `recovery_data_stale`; recovered/active **not used** in conclusions |
| 81 blank `serious_or_critical` | Left missing; not used |
| 14 blank `total_tests` | Left missing; testing metrics skipped |
| 3 countries with tests < cases | Positivity set to missing (cannot exceed 100%) |
| Inconsistent names (e.g. "USA", "UK", "Viet Nam", "Swaziland") | 29 standardised for mapping |
| Per-million columns | Recomputed from counts and checked against the originals (matched) |
| Tiny populations (<1M, 69 rows) and <1,000 cases (10 rows) | Kept, but excluded from rankings/correlations via `analysis_sample` (157 rows remain) |

**Derived metrics (42 columns in total):** `cfr_pct`, `infection_rate_pct`, `cases_per_1m`, `deaths_per_1m`, `tests_per_1m`, `cumulative_positivity_pct`, `tests_per_case`, `recovery_rate_pct`, `active_share_pct`, plus slicer-ready tiers (`testing_tier`, `testing_tier_sample`, `cfr_band`, `burden_tier`, `population_size`), ranks, and the extended-analysis columns (`expected_deaths_per_1m`, `deaths_vs_expected`, `outcome_group`, `death_share_pct`, `cum_death_share_pct`).

## Repository structure
```
covid-19-global-impact/
├── README.md
├── clean_data.py                  # cleaning + feature engineering
├── build_notebook.py              # (optional) regenerates notebook 1
├── build_notebook2.py             # (optional) regenerates notebook 2
├── build_pdf.py                   # (optional) regenerates the PDF
├── requirements.txt
├── data/
│   ├── raw_worldometer_coronavirus_summary_data.csv
│   ├── covid_cleaned.csv          # Power BI source (42 columns)
│   ├── covid_cleaned.xlsx         # with cleaning_log sheet
│   ├── powerbi_continent_summary.csv
│   └── powerbi_missing_values.csv # for the data-quality panel
├── notebook/
│   ├── COVID19_Global_Impact_Analysis.ipynb   # charts 1-6, core insights 1-5
│   └── COVID19_Extended_Visuals.ipynb         # charts 7-12, extended insights 6-10
├── charts/                        # 12 PNG figures
├── dashboard/
│   ├── COVID19_Dashboard.pbix     # Power BI file
│   ├── covid_dark_theme.json      # theme used in the dashboard
│   └── dashboard_screenshot.png   # screenshot used at the top of this README
├── docs/
│   ├── POWERBI_GUIDE.md
│   ├── POWERBI_DASHBOARD_BUILD_STEPS.md
│   ├── DATA_DICTIONARY.md
│   └── data_quality_log.csv
└── COVID19_Executive_Summary.pdf  # 1-page summary
```

## How to run
```bash
pip install -r requirements.txt
python clean_data.py                         # creates data/covid_cleaned.csv/.xlsx
jupyter notebook notebook/COVID19_Global_Impact_Analysis.ipynb
jupyter notebook notebook/COVID19_Extended_Visuals.ipynb
```
Then open `dashboard/COVID19_Dashboard.pbix` in Power BI Desktop, or rebuild it from `data/covid_cleaned.csv` using `docs/POWERBI_DASHBOARD_BUILD_STEPS.md`.

## Limitations
- One snapshot: no trends, waves or vaccination effects.
- Countries define cases, tests and COVID deaths differently, so findings describe *reported* numbers.
- Correlations show association, not cause. Health-system capacity and age structure also matter.
- The `deaths_vs_expected` ratio and its 2x / 0.5x cut-offs are my own analytical choice for spotting outliers, not an official measure.

## Next steps
Join Our World in Data's daily file on `country` to add 7-day rolling averages, doubling time, wave detection and a vaccination-rollout vs death-rate analysis, and add a time slicer to the dashboard.

## Tools
Python (pandas, NumPy, SciPy, Matplotlib), Excel, Power BI (DAX).

*Author: Radhika Dinesh Shet | Veda Technology Internship, Data Analytics track*