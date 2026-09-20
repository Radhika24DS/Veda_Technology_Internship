# Task 13 — Duplicate Record Check
**Veda Technology | Data Analytics Track | Radhika**
Dataset used: `retail_sales_dataset.csv` (1,000 rows × 9 columns)

---

## 1. Objective
Understand duplicate detection: find duplicate records in the dataset, document what was found, and produce a cleaned copy.

## 2. Dataset at a Glance
| Column | Type | Notes |
|---|---|---|
| Transaction ID | Integer | Intended primary key — should be unique |
| Date | Date | Transaction date |
| Customer ID | Text | e.g. CUST001 |
| Gender | Text | Male / Female |
| Age | Integer | |
| Product Category | Text | Beauty, Clothing, Electronics |
| Quantity | Integer | |
| Price per Unit | Numeric | |
| Total Amount | Numeric | Quantity × Price per Unit |

No missing values were found in any column.

## 3. Method — Three Layers of Duplicate Checking
A single check isn't enough, because "duplicate" can mean different things. This task ran three checks, from strictest to most business-relevant:

1. **Full-row duplicate** — every single column (including Transaction ID) is identical between two rows. This is the strictest, most obvious kind of duplicate (e.g., the same record accidentally pasted or imported twice).
2. **Key-column duplicate** (excludes Transaction ID) — Date, Customer ID, Gender, Age, Product Category, Quantity, Price per Unit, and Total Amount all match, but the Transaction ID differs. This catches the more dangerous case: the same real-world sale logged twice under two different IDs.
3. **Primary-key duplicate** — the same Transaction ID appears more than once. If this ever happens, the "unique key" has broken, which usually signals a serious upstream data problem (e.g., an ID counter reset, or a failed join).

Each check was done twice, for cross-verification:
- **In Python (pandas)** using `df.duplicated()`, for a fast programmatic result.
- **In Excel (formulas)** using `COUNTIFS` across the relevant columns, so the same audit can be reproduced or re-run directly inside Excel without touching Python — see the `Full_Data_Flagged` sheet in the workbook.

## 4. Findings
| Check | Rows flagged |
|---|---|
| Full-row duplicate | **0** |
| Key-column duplicate (excl. Transaction ID) | **0** |
| Transaction ID duplicate | **0** |

**Result: No duplicate records exist in this dataset.** All 1,000 rows are unique observations under all three definitions of "duplicate" tested above.

## 5. Audit Note
> This dataset was checked for duplicates using three methods (full-row match, business-key match, and primary-key match), cross-verified in both pandas and Excel formulas. Zero duplicates were found under any method. No rows were removed. The delivered "cleaned" file is therefore identical to the source file in content — it represents the verified, audit-passed copy, not a version with rows deleted. This is an expected and valid outcome of a duplicate check: absence of duplicates is itself a documented finding, not a skipped step.

If this dataset is later refreshed or new data appended, re-run the same three checks — the `Full_Data_Flagged` sheet's formulas will recalculate automatically and re-flag anything new.

## 6. Deliverables Submitted
1. **`Task13_Duplicate_Report.xlsx`** — Excel workbook with:
   - `Summary` — overview, checks performed, results, audit note, methodology.
   - `Full_Data_Flagged` — full dataset with live Excel formulas (`COUNTIFS`) flagging any full-row, key-column, or Transaction ID duplicates.
   - `Cleaned_Data` — the deduplicated dataset (identical to source here, since none were found).
2. **`retail_sales_dataset_cleaned.csv`** — cleaned copy of the dataset (CSV), ready for downstream use.
3. **This guide** — methodology and audit note, plus interview prep below.

## 7. Interview Questions — Answers

**Q1: What is a duplicate row?**
A duplicate row is a record that repeats information already present elsewhere in the dataset. It can be:
- An **exact duplicate** — every column is identical to another row.
- A **partial/business-key duplicate** — the meaningful business fields match (e.g., same customer, date, product, quantity, price) even though a surrogate field like an auto-generated ID differs. This second kind is usually the more important one to catch, because a unique ID column can make truly duplicated data look "unique" at a glance.

**Q2: How can duplicates affect totals?**
- **Inflated aggregates**: SUM, COUNT, and AVG calculations (e.g., total revenue, total units sold) will overstate the real figures if the same transaction is counted twice.
- **Skewed averages/ratios**: metrics like average order value or conversion rate get distorted because the denominator (row count) and numerator (value) are both artificially inflated, and not always proportionally.
- **Double-counted customers/behavior**: a customer's purchase count or lifetime value can appear higher than reality, affecting segmentation, forecasting, and business decisions built on that data.
- **Downstream errors**: any report, dashboard, or model trained on the data inherits the inflation — the error compounds the further downstream it travels.

This is why a duplicate check happens **before** any aggregation or analysis step, not after.
