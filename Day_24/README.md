# Task 24 - Data Quality Audit (Superstore)

**Data Analytics Track | Tools: Python, Pandas | Dataset: Sample Superstore (9,994 rows x 13 columns)**

A repeatable, rule-based data quality audit. Every check is written once as a *rule* (ID, dimension, severity,
action) in a registry, so the same checklist can be re-run on any refresh of the data and on the cleaned
output to prove the fixes worked.

## Objective
Audit the dataset for **missing, duplicate, range and consistency** issues, quantify each issue, and produce a
reusable quality checklist plus a cleaned dataset.

## Project structure
```
Task24_Data_Quality_Audit/
├── data_quality_audit.py            # whole pipeline: rules -> audit -> clean -> re-audit -> report
├── requirements.txt
├── README.md
├── LinkedIn_Post.md
├── Feedback.md                      # reflection + interview answers
├── data/
│   └── SampleSuperstore.csv         # raw input
└── outputs/
    ├── audit_report.md              # DELIVERABLE 1 - audit report
    ├── issue_log.csv                # DELIVERABLE 2 - issue log (one row per rule, with priority)
    ├── issue_log_row_level.csv      # every violating row (CSV line number + rule)
    ├── cleaned_sample.csv           # DELIVERABLE 3 - 500-row cleaned sample
    ├── superstore_cleaned_full.csv  # full cleaned dataset (9,977 rows)
    ├── validation_rules_checklist.csv  # the repeatable checklist (25 rules)
    └── issues_by_rule.png           # chart used in the report
```

## How to run
```bash
pip install -r requirements.txt
python data_quality_audit.py
# optional
python data_quality_audit.py --input data/SampleSuperstore.csv --output outputs
```
Open `outputs/audit_report.md` for the results.

## Method
| Step | What happens |
|---|---|
| 1. Define | 25 validation rules across Completeness, Uniqueness, Validity, Consistency, Plausibility |
| 2. Quantify | Each rule returns the violating rows -> count, % of data, severity, PASS/FAIL |
| 3. Prioritise | `score = severity weight x (1 + log10(1 + rows))` |
| 4. Clean | Fix / remove / flag depending on the rule's `action` |
| 5. Re-audit | Same rules run on cleaned data -> before vs after table |

## Key findings
| Issue | Rows | Handling |
|---|---|---|
| Postal Code lost leading zero (4-digit ZIPs, New England + NJ) | 449 (4.49%) | **Fixed** - stored as 5-char text |
| Exact duplicate rows | 17 (0.17%) | **Removed** (keep first) |
| Postal 92024 mapped to both San Diego and Encinitas | 5 (0.05%) | **Flagged** - needs USPS reference |
| Loss-making lines | 1,871 (18.72%) | Flagged (`flag_loss`) - business finding |
| Deep discount >= 50% | 922 (9.23%) | Flagged - every one of them loses money |
| Loss greater than sale value | 349 (3.49%) | Flagged (`flag_extreme_loss`) |
| Sales / Profit outliers (IQR per sub-category) | 1,004 / 1,353 | Flagged, kept |
| Nulls, blanks, invalid labels, bad ranges, hierarchy conflicts | 0 | 17 rules passed |

**Quality scorecard:** overall 98.82% -> 99.99% after cleaning (Completeness 100, Uniqueness 99.83 -> 100,
Validity 95.51 -> 100, Consistency 99.95 -> 99.95).

**Business insight:** average margin is +34% at 0% discount but negative from a 30% discount onwards
(-11.5%), reaching -182% at 80%.

## Design decisions
* **Outliers and losses are flagged, not deleted** - they are real business events, not data errors.
* **Duplicates are removed** but documented as an assumption, because the file has no Order ID.
* **Majority-vote fixes are avoided for ZIP -> City** - the majority (San Diego) is wrong for ZIP 92024.
* Cleaning adds `Profit Margin`, `Unit List Price` and five `flag_*` columns for downstream analysis.

## Limitations
No Order ID / date / customer / product columns, so duplicate proof and time-based checks are limited.
Reference checks are internal (majority mapping + hard-coded state list). Thresholds (1.5 x IQR, 50% discount)
are conventions to tune with the business.

## Reusing on another dataset
Edit `CONFIG` (allowed values, column lists, thresholds) and the `RULES` list in `build_rules()`. The runner,
prioritisation, cleaning log, scorecard and report generator need no changes.
