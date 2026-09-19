# Task 12 — Missing Value Identification

**Program:** HI Radhika — Data Analytics Track (Veda Technology)
**Level:** 1 | **Day:** 12
**Dataset:** [Titanic-Dataset.csv](Titanic-Dataset.csv) (891 rows × 12 columns)

## Objective
Learn basic missing-data inspection by identifying missing values in the Titanic dataset and summarizing where they occur.

## Tools Used
- Python
- Pandas

## Approach
1. Loaded `Titanic-Dataset.csv` into a pandas DataFrame.
2. Ran `df.isnull().sum()` to count nulls per column.
3. Calculated missing percentage per column: `(nulls / total_rows) * 100`.
4. Broke down `Age` missingness by `Pclass` to check for a pattern.
5. Inspected the 2 missing `Embarked` rows individually.
6. Documented findings and imputation/deletion recommendations — no rows or columns were deleted at this stage.

## Missing-Value Summary

| Column | Missing Count | Missing % |
|---|---|---|
| Cabin | 687 | 77.10% |
| Age | 177 | 19.87% |
| Embarked | 2 | 0.22% |
| All other columns | 0 | 0% |

**Total missing cells:** 866

## Key Findings
- **Cabin** is missing in 77% of rows — too much to drop; better handled with a "Cabin Known/Unknown" flag.
- **Age** is missing in ~20% of rows, concentrated in 3rd class (136 of 177 missing) — suggests Missing At Random (MAR), not pure randomness.
- **Embarked** is missing in only 2 rows (both 1st class, same Fare/Cabin) — negligible impact.
- All other columns are fully complete.

## Why Not Delete Rows Blindly?
- Deleting rows with missing `Cabin` would remove 77% of the dataset.
- `Age` missingness correlates with `Pclass`, so deletion would bias the sample.
- Missing data should be understood and handled deliberately (imputation, flagging, or informed deletion) — not stripped out by default.

## Deliverables
- [`Task12_Missing_Value_Report.docx`](Task12_Missing_Value_Report.docx) — full write-up with tables, findings, recommendations, and interview Q&A
- This README — summary of the day's work

## Interview Questions Covered
1. What is a missing value?
2. Why can blindly deleting rows be risky?

(Full answers in the report.)
