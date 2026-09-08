# Task 1: Data Cleaning & Preprocessing — World Happiness Report (2020–2024)

**Internship:** Veda Technology — Data Analytics Track
**Dataset:** World Happiness Report, 5 yearly CSV files (`2020.csv`–`2024.csv`)
**Tools used:** Python, Pandas, openpyxl

## Objective

The raw data came as five separate yearly files. Before any year-over-year
analysis could be trusted, I needed to inventory each file for quality
issues, combine them into a single dataset, and fix everything so the same
country is represented consistently across all five years.

## Process

I started by running `df.info()`, `df.isnull().sum()`, and
`df.duplicated().sum()` on each of the 5 files individually, then compared
the set of country names across years to catch problems a null/duplicate
check alone wouldn't reveal — the same country listed under two different
names is not a duplicate or a null, it just silently breaks any merge or
trend calculation.

## Issues Found & How I Fixed Them

### 1. Inconsistent column headers
The `Economy (GDP per Capita)` column had a trailing tab character baked
into the header in every raw file.
**Fix:** Stripped whitespace/tab characters from every column header before
using the data.

### 2. Footnote markers in country names
Several country names (mostly in the 2022 file) had a trailing `*`
footnote marker, e.g. `Azerbaijan*`, which prevented them from matching the
same country's rows in other years.
**Fix:** Stripped trailing `*` from every country name.

### 3. The same country spelled differently across years
Six countries were labeled inconsistently between years, which would have
caused Pandas to treat them as separate entities:

| Name used in earlier years | Standardized to |
|---|---|
| Czech Republic | Czechia |
| Macedonia | North Macedonia |
| Swaziland | Eswatini |
| Eswatini, Kingdom of | Eswatini |
| Turkey | Turkiye |
| Palestinian Territories | State of Palestine |
| Congo *(unlabeled, 2022 only)* | Congo (Brazzaville) |

The last one needed extra care — 2022 just listed `Congo` with no
qualifier, while other years split it into `Congo (Brazzaville)` and
`Congo (Kinshasa)`. I compared the 2022 happiness score (5.075) against
each entity's trend in the surrounding years: Brazzaville runs ~5.19 → 5.34
→ 5.27, while Kinshasa runs ~4.31 → 3.2 → 3.3. The 2022 value clearly
belongs to Brazzaville, so I mapped it there instead of guessing or leaving
it as a third, incorrect entity.

**Fix:** Applied a single canonical name per country across all five years.

### 4. Missing values (19 cells total)
Missing data appeared in 2023 (1 cell — State of Palestine's Healthy life
expectancy) and 2024 (18 cells — Bahrain, Tajikistan, and State of Palestine
missing 6 columns each).

Rather than applying one blanket rule to every gap, I handled it case by
case:
- If the country had its own value for that column in a **different year**,
  I filled the gap with that **country's own average** across its available
  years — this keeps the estimate grounded in that specific country's
  baseline instead of pulling it toward a generic global number.
- Only when a country had **no history at all** for a column did I fall back
  to that **year's median** as a last resort.

Every filled cell is flagged in a new `Imputed` column in the final dataset,
so it's always possible to tell a real survey value apart from an estimated
one. All 19 fixes are also listed individually in `change_log.csv`.

### 5. Duplicate rows
Checked for both fully duplicated rows and duplicate `(Year, Country)` keys
— found zero of either. The check is kept in the script so it will still
catch duplicates automatically if the dataset is ever refreshed.

### 6. Data types
Verified all 10 numeric columns (Happiness Rank, Happiness score, Economy,
Social support, etc.) were read in as proper numeric types, converting any
that weren't.

## Before vs. After

| Check | Before | After |
|---|---|---|
| Missing values | 19 cells | **0** |
| Duplicate rows | 0 | **0** |
| Duplicate (Year, Country) keys | 0 | **0** |
| Unique countries | 154 (inflated by the "Congo" naming issue) | **153** |
| Column header issues | 1 (stray tab character) | **0** |
| Combined dataset | 5 separate files | **1 file, 728 rows** |

## Deliverables

- `happiness_cleaned.csv` / `happiness_cleaned.xlsx` — the merged, cleaned
  dataset (one row per country per year), including the `Imputed` flag
  column
- `change_log.csv` — every individual fix applied, with year, country,
  column, issue, and the value used
- `inventory.py` — the full cleaning script
- This README

## What I Learned

Case-by-case imputation gave much more sensible results than a single
blanket rule would have — filling Bahrain's missing GDP figure with its own
historical average (1.612) is far more accurate than forcing it to the
global median, since Bahrain's actual GDP level is well above average.
I also learned that null and duplicate checks alone aren't enough for
multi-year datasets — the "same entity, different name" problem (Turkey vs.
Turkiye, Congo vs. Congo (Brazzaville)) only shows up if you explicitly
compare category values across files, not just run standard `.isnull()` /
`.duplicated()` checks.

## Interview Question Answers

**How do you decide whether to drop or impute a missing value?**
It depends on how much would be lost by dropping it. Here, dropping
Bahrain, Tajikistan, and State of Palestine for 2024 would have discarded
otherwise-complete country records over a handful of missing columns. Since
each of those countries had reliable data in other years, imputing from
their own history preserved the record without inventing implausible
numbers.

**What's the difference between a duplicate row and a duplicate key?**
A duplicate row is identical across every single column. A duplicate key —
here, `Year` + `Country name` — means the same real-world entity appears
twice even if other columns differ. This dataset didn't have any duplicate
rows, but it *did* have the equivalent of a duplicate-key risk: if "Turkey"
and "Turkiye" had both been left in the same year, that would have counted
as two records for one country.

**How would you handle outliers differently from missing values?**
Missing values are gaps that must be filled or excluded before any
calculation can even run. Outliers are real, valid values that are just
extreme — a country with genuinely very low GDP or high perceived
corruption isn't a data error, so I wouldn't delete it; I'd flag it for
awareness rather than alter it, since removing it would change the actual
story the data tells.

**How would you validate that a dataset is "clean" before starting
analysis?**
Re-run the same inventory checks used to find the original problems —
nulls, duplicates, and dtypes — and additionally re-check cross-file key
consistency (country names matching across years), since that's the one
issue standard null/duplicate checks won't catch on their own.