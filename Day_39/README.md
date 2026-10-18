# COVID-19 Global Impact Dashboard

**Focused question:** *How much of the difference in countries' COVID-19 numbers is real, and how much reflects how hard each country tested?*

An end-to-end data analytics project: cleaning a messy real-world country dataset, deriving population-normalised metrics, finding patterns, and communicating them in plain language through a notebook, a one-page executive summary and a Power BI dashboard.

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

**Derived metrics:** `cfr_pct`, `infection_rate_pct`, `cases_per_1m`, `deaths_per_1m`, `tests_per_1m`, `cumulative_positivity_pct`, `tests_per_case`, `recovery_rate_pct`, `active_share_pct`, plus slicer-ready tiers (`testing_tier`, `cfr_band`, `burden_tier`, `population_size`) and ranks.

## Repository structure
```
covid-19-global-impact/
├── README.md
├── clean_data.py                  # cleaning + feature engineering
├── build_notebook.py              # (optional) regenerates the notebook
├── build_pdf.py                   # (optional) regenerates the PDF
├── requirements.txt
├── data/
│   ├── raw_worldometer_coronavirus_summary_data.csv
│   ├── covid_cleaned.csv          # Power BI source
│   ├── covid_cleaned.xlsx         # with cleaning_log sheet
│   └── powerbi_continent_summary.csv
├── notebook/COVID19_Global_Impact_Analysis.ipynb
├── charts/                        # 6 PNG figures
├── docs/
│   ├── POWERBI_GUIDE.md
│   ├── DATA_DICTIONARY.md
│   └── data_quality_log.csv
├── COVID19_Executive_Summary.pdf  # 1-page summary
└── dashboard/                     # add your .pbix and screenshots here
```

## How to run
```bash
pip install -r requirements.txt
python clean_data.py                         # creates data/covid_cleaned.csv/.xlsx
jupyter notebook notebook/COVID19_Global_Impact_Analysis.ipynb
```
Then follow `docs/POWERBI_GUIDE.md` to build the dashboard from `data/covid_cleaned.csv`.

## Limitations
- One snapshot: no trends, waves or vaccination effects.
- Countries define cases, tests and COVID deaths differently, so findings describe *reported* numbers.
- Correlations show association, not cause. Health-system capacity and age structure also matter.

## Next steps
Join Our World in Data's daily file on `country` to add 7-day rolling averages, doubling time, wave detection and a vaccination-rollout vs death-rate analysis.

## Tools
Python (pandas, NumPy, SciPy, Matplotlib), Excel, Power BI.

*Author: Radhika Dinesh Shet | Veda Technology Internship, Data Analytics track*
