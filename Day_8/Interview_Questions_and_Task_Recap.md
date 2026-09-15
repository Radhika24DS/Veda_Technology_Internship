# Interview Questions & Task Recap — Task 8 (Sales Tracker)

## Interview Question 1
**How would you design a spreadsheet so non-technical staff can enter data safely?**

Three things do most of the work here:

1. **Give them exactly one place to type.** A single "Raw Entries" tab, clearly labeled, with every other tab locked to formulas only. If there's only one place data can go in, there's only one place it can go wrong.
2. **Make invalid entries impossible, not just discouraged.** Dropdown lists (data validation) for fields with a fixed set of options — like Gender or Product Category — mean a staff member literally cannot type "Beuaty" or "male" by mistake; they pick from a list. Numeric fields like Quantity and Price get a "must be greater than 0" rule, so a blank or negative entry is rejected immediately with a plain-English warning, rather than silently breaking a total three tabs away.
3. **Pre-build the next batch of rows before anyone needs them.** New rows below the existing data are already formatted, already carry the same dropdowns and validation, and already have the Total Amount formula in place. That way a staff member never has to "extend a formula" or "set up a new row correctly" — the row is already correct before they type into it.

On top of that, a short, plain-language instructions tab (no jargon like "SUMIFS" or "array formula") tells people what's editable and what isn't, in one place they can check anytime.

## Interview Question 2
**What's the risk of mixing raw data and formulas on the same tab?**

Two failure modes, both quiet ones — they don't throw an error, they just produce a wrong number that looks fine:

1. **Inserting or deleting a row shifts formula ranges without warning.** If a `SUMIFS` formula sits a few rows below the raw data on the same tab, and someone inserts a new sale in the middle of the list, every formula referencing a fixed range below that point can silently start reading the wrong rows — or miss the new row entirely — with no error shown anywhere.
2. **A correction to raw data can overwrite a formula, or vice versa.** If a total and its underlying transaction sit in adjacent cells on the same tab, it's very easy for someone fixing a typo to overwrite a formula cell by hand, turning it into a static number that will now never update again — and there's no visual difference between "this cell recalculates" and "this cell is now just frozen text" once it's happened.

Keeping raw data and formulas on physically separate tabs removes both risks structurally: the summary tabs reference a fixed range on another tab, so growing the raw data doesn't move anything the formulas depend on, and nobody editing raw entries is ever one keystroke away from breaking a rollup they don't even know is there.

---

## Recap of Today's Task (Task 8)

**Objective:** Build a lightweight sales tracker in Google Sheets that auto-calculates daily/weekly/monthly totals from raw entries, using the Retail Sales Dataset as sample data.

**What was actually done, in order:**

1. Loaded and profiled the 1,000-row Retail Sales Dataset — checked date range, unique categories, and confirmed `Total Amount = Quantity × Price per Unit` holds for every row.
2. Designed a 6-tab structure: Read Me, Raw Entries, Daily Summary, Weekly Summary, Monthly Summary, and a Verification (QA) tab.
3. Built the Raw Entries tab with all 1,000 sample transactions, formula-driven Total Amount, and 500 pre-validated blank rows for future entries.
4. Applied data validation: dropdown lists for Gender and Product Category, numeric range rules for Age/Quantity/Price.
5. Built Daily Summary (345 unique dates) using `SUMIFS`/`COUNTIFS` keyed to an exact date match.
6. Built Weekly Summary (54 Monday–Sunday weeks) using `SUMIFS` with a two-sided date-range condition.
7. Built Monthly Summary (13 calendar months) the same way, plus an average-transaction-value metric.
8. Ran an independent manual verification in Python for one sample day, week, and month, and confirmed each matched the sheet's own formula output exactly.
9. Cross-checked the grand total (₹456,000) across all four tabs (Raw Entries, Daily, Weekly, Monthly) to confirm they agree.
10. Recalculated the full workbook to confirm zero formula errors across all 3,095 formulas.
11. Wrote the Read Me tab and this documentation set last, once the design was finalized.

**Outcome:** A verified, ready-to-import Google Sheets tracker (`Sales_Tracker.xlsx`) that meets both stated deliverables — a formula-driven template, and sample data with totals checked against an independent manual calculation.
