# Data dictionary: `data/covid_cleaned.csv`

| Column | Meaning |
|---|---|
| country, continent | Standardised names; "Australia/Oceania" renamed "Oceania" |
| population | Population |
| population_size | Bucket: <1M, 1-10M, 10-50M, 50-200M, >200M |
| total_confirmed, total_deaths | Cumulative reported cases and deaths (blank deaths set to 0) |
| total_recovered, active_cases | As reported; blank where unavailable. Unreliable for flagged rows |
| serious_or_critical | As reported; 81 blanks |
| total_tests | As reported; 14 blanks |
| cases_per_1m, deaths_per_1m, tests_per_1m | Recomputed per million people |
| infection_rate_pct | Cases / population x 100 |
| cfr_pct | Deaths / cases x 100 (crude case fatality rate) |
| recovery_rate_pct, active_share_pct | Recovered / cases, active / cases (x100) |
| tests_per_case | Tests / cases |
| cumulative_positivity_pct | Cases / tests x 100; blank when tests < cases |
| log10_cases_per_1m, log10_tests_per_1m | For log-scale charts |
| testing_tier | Quartile of tests_per_1m (all countries with test data) |
| cfr_band | <0.5%, 0.5-1%, 1-2%, 2-5%, >5% |
| burden_tier | Quartile of deaths_per_1m |
| rank_* | Rank within analysis sample (1 = highest) |
| analysis_sample | TRUE if population >= 1M and cases >= 1,000 (157 rows) |
| small_population, low_case_count | Flags behind analysis_sample |
| deaths_assumed_zero | Blank deaths set to 0 |
| recovery_data_missing, recovery_data_stale | Recovered blank / recovered < 50% of cases |
| tests_missing, tests_lt_cases | Test count blank / tests below cases |
