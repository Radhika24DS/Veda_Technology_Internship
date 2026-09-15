# Task 8 — Sales Tracker in Google Sheets
### Submission Summary

**Submitted by:** Radhika | **Track:** Data Analytics | **Date:** 15 Sep 2026
**Deliverable file:** `Sales_Tracker.xlsx` (import into Google Sheets — File → Import → Replace/Insert)

---

## 1. What was asked

Build a lightweight sales tracker that:
- Separates raw data entry from the summary/reporting layer
- Auto-calculates daily, weekly, and monthly totals using date-range formulas
- Prevents bad data entry with validation
- Is loaded with sample data and the totals verified against a manual check

## 2. What was delivered

One workbook, six tabs:

| # | Tab | Contents |
|---|-----|----------|
| 1 | **Read Me** | Plain-English instructions for whoever enters data day to day: which tab to type in, what not to touch, and why the workbook is structured the way it is |
| 2 | **Raw Entries** | 1,000 sample transactions (Jan 1 2023 – Jan 1 2024) plus 500 pre-formatted blank rows, ready for future entries, with dropdowns and input rules already applied |
| 3 | **Daily Summary** | 345 unique calendar dates with Total Sales, Total Transactions, Total Quantity Sold, and Avg Sale Value, each computed live from Raw Entries |
| 4 | **Weekly Summary** | 54 Monday–Sunday weeks spanning the data, with the same rollup metrics |
| 5 | **Monthly Summary** | 13 calendar months, with totals and Avg Transaction Value |
| 6 | **Verification (QA)** | Three independently-recomputed totals (one day, one week, one month) checked against the sheet's own formulas |

## 3. Data validation rules built into Raw Entries

| Field | Rule | Why |
|---|---|---|
| Gender | Dropdown: Male / Female | Prevents free-typed variants ("male", "M", etc.) that would break future filtering |
| Product Category | Dropdown: Beauty / Clothing / Electronics | Same reason — keeps category names consistent for rollups |
| Age | Whole number, 0–120 | Blocks obvious typos |
| Quantity | Whole number, greater than 0 | Blocks blank, zero, or negative quantities |
| Price per Unit | Number, greater than 0 | Blocks blank, zero, or negative prices |
| Total Amount | Formula only (`Quantity × Price per Unit`) | Removes the possibility of a hand-typed total ever disagreeing with its inputs |

## 4. Manual verification (proof the formulas are correct)

Three totals were recalculated independently in Python, straight off the raw CSV, with no spreadsheet formulas involved, then compared to what the sheet's own `SUMIFS`/`COUNTIFS` formulas produced:

| Check | Period | Manual total | Sheet formula total | Result |
|---|---|---|---|---|
| Daily | 30 Jun 2023 | ₹1,030 | ₹1,030 | ✅ Match |
| Weekly | 03–09 Jul 2023 | ₹4,315 | ₹4,315 | ✅ Match |
| Monthly | July 2023 | ₹35,465 | ₹35,465 | ✅ Match |
| **Grand total** | Full year | **₹456,000** | **₹456,000** (Daily, Weekly, Monthly, and Raw Entries tabs all agree independently) | ✅ Match |

The workbook was also run through a formula recalculation engine: **0 errors across 3,095 formulas.**

## 5. Files being submitted

| File | Purpose |
|---|---|
| `Sales_Tracker.xlsx` | The tracker itself — the actual deliverable |
| `Submission_Summary.md` | This document |
| `Interview_Questions_and_Task_Recap.md` | Written answers to the two interview questions, plus a recap of today's work |


