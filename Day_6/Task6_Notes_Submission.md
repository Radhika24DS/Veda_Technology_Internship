# Task 6 — Excel Formulas & Functions Fundamentals
**Radhika · Data Analytics Track**

Dataset used: Sample Superstore (cleaned) — `SampleSuperstore_clean.csv`
Workbook: `Excel_Formulas_Fundamentals_Task6.xlsx`

---

## Short Notes — When to Use Each Formula

**VLOOKUP**
Use when you need to pull a matching value from a column to the **right** of your lookup column, in a table with a fixed layout.
`=VLOOKUP(lookup_value, table_array, col_index_num, FALSE)`

**INDEX/MATCH**
Use instead of VLOOKUP when the answer is to the **left** of your lookup column, or when the table's columns might get rearranged — it doesn't break when a column is inserted.
`=INDEX(return_range, MATCH(lookup_value, lookup_range, 0))`

**XLOOKUP**
Use in Excel 365 / Google Sheets as the modern replacement for both of the above — searches either direction, defaults to exact match, and can return a custom message if nothing is found.
`=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found])`

**IF**
Use for a single either/or decision based on one condition.
`=IF(logical_test, value_if_true, value_if_false)`

**Nested IF**
Use when a value needs to be sorted into 3–4 ranked outcomes (e.g. Loss / Low / Medium / High profit). Beyond 4–5 levels, switch to a lookup table for readability.
`=IF(test1, result1, IF(test2, result2, result3))`

**SUMIFS**
Use to total a number across **two or more** conditions at once. Note the sum range comes **first**, unlike SUMIF.
`=SUMIFS(sum_range, range1, criteria1, range2, criteria2)`

**COUNTIFS**
Use to count rows matching **two or more** conditions at once.
`=COUNTIFS(range1, criteria1, range2, criteria2)`

**SUMIF / COUNTIF**
Use only when filtering on exactly **one** condition — the single-condition version of the above two.

**Text functions (LEFT / RIGHT / MID / TRIM / UPPER / PROPER / CONCATENATE / TEXTJOIN / FIND / SUBSTITUTE)**
Use to extract, clean, standardize, or combine text — most commonly TRIM to fix hidden extra spaces that silently break lookups and exact-match comparisons.

---

## Interview Questions

**Q1: What's the difference between SUMIF and SUMIFS?**
SUMIF tests exactly one condition — `=SUMIF(range, criteria, sum_range)`. SUMIFS tests one or more conditions and moves the sum range to the front of the argument list — `=SUMIFS(sum_range, range1, criteria1, range2, criteria2, ...)`. Since SUMIFS works fine with just one condition too, it's often used as the default.

**Q2: How does XLOOKUP improve on VLOOKUP?**
It can search left of the return column (VLOOKUP only goes right), it defaults to an exact match, it keeps working if a column is inserted into the table, and it has a built-in "not found" argument so a custom message can be returned without wrapping it in IFERROR.

**Q3: When would you use INDEX/MATCH instead of VLOOKUP?**
When the value needed sits to the left of the lookup column, when the table's column order might change over time, or on large datasets where INDEX/MATCH is generally faster.

---

## Edge Cases Tested

Ran formulas against a blank cell, a number stored as text, and text with stray leading spaces (see `Edge_Cases` sheet in the workbook) — confirmed that plain `SUM` silently skips bad values, and that `ISBLANK`, `ISNUMBER`, `TRIM`, `VALUE`, and `IFERROR` catch and fix each case.

---

## Named Ranges Used

`Sales_Range`, `Quantity_Range`, `Discount_Range`, `Profit_Range`, `Region_Range`, `Category_Range`, `Segment_Range`, `ShipMode_Range`, `Region_Manager_Table`, `ShipMode_Col`, `SLA_Days_Col` — defined in Name Manager and used in place of raw cell references throughout the workbook.
