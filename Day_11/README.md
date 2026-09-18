# Task 11 - Basic Data Sorting & Filtering

**Track:** Data Analytics
**Submitted by:** Radhika
**Dataset used:** Retail Sales Dataset (retail_sales_dataset.csv) - 1000 transactions

## What I did

I started with the raw retail sales file, which had 1000 rows and 9 columns
(Transaction ID, Date, Customer ID, Gender, Age, Product Category, Quantity,
Price per Unit, Total Amount). Before touching anything, I copied the original
data into a "Raw Data" tab in the workbook and left it exactly as it came in -
no sorting, no edits, no deleted rows. That way I always have a clean copy to
go back to if a filter is wrong or I need to double check a number.

From there I applied filters (not deletions) to look at the data from a few
different angles:

1. **Electronics 500+** - Product Category = Electronics AND Total Amount > 500.
   Wanted to see how big a slice of Electronics sales is coming from higher
   value purchases.
2. **Female High Spend** - Gender = Female AND Total Amount > 800.
   Quick look at the top-spending female customers in the dataset.
3. **Bulk Orders** - Quantity >= 3 AND Total Amount > 300.
   Trying to spot the bigger basket / bulk-type transactions.

Each filter is on its own tab so the raw data doesn't get touched and I can
always compare a filtered view back to the full set.

I also added an "Answers" tab where I worked out the 5 business questions
below using formulas (SUMIF / AVERAGEIF / COUNTIFS / SUMPRODUCT) pulling
straight from the Raw Data tab, so the numbers update automatically if the
source data changes.

## Files in this submission

- `retail_sales_filtered_workbook.xlsx` - the workbook with Raw Data, Answers,
  and the three filtered views
- `README.md` - this file

## The 5 Questions I Answered

**Q1. Which product category brought in the highest total revenue?**
Electronics, with ₹1,56,905 in total sales - but it's close. Clothing is
right behind at ₹1,55,580 and Beauty at ₹1,43,515. None of the three
categories is really dominating, Electronics just edges ahead.

**Q2. On average, who spends more per transaction - male or female customers?**
Basically a tie. Female customers average ₹456.55 per transaction, male
customers average ₹455.43. About a one rupee difference, so gender doesn't
seem to affect spend per visit in this data.

**Q3. Which month recorded the highest total sales in 2023?**
May, with ₹53,150 in sales. October (₹46,580) and December (₹44,690) come
next. September was the weakest month at ₹23,620 - less than half of May.
Would be worth checking what happened in May (maybe a sale/promo period) if
this was a real business scenario.

**Q4. Which age group contributes the most revenue?**
The 46-55 age band, at ₹1,00,690, just ahead of 26-35 (₹98,480). The 56-65
group brought in the least, at ₹80,410. Again fairly even overall, no single
age group is running away with it.

**Q5. How many Electronics transactions crossed ₹500, and what share of
Electronics revenue do they represent?**
100 transactions, and together they make up about 79% of all Electronics
revenue. So a relatively small number of higher-value orders is doing most
of the work for that category.

## Interview Questions

**When would you use filtering instead of deleting rows?**
Filtering is the safer option any time you still need the full dataset
around, which is basically always. If I delete rows to "clean up" a view,
that data is gone from the sheet - if I made a wrong assumption about what
to remove, or someone later asks me a question that needs those rows, I'm
stuck. Filtering just hides rows that don't match a condition; the moment I
clear the filter, everything is back. It also means two people can look at
the same file and apply different filters for different questions without
stepping on each other's work. I'd only actually delete rows if they were
genuine junk - duplicate entries, test rows, something like that - and even
then I'd rather move them to a separate "removed" tab than delete them
outright.

**Why should raw data be preserved?**
Because every answer I give is only as good as the data it came from, and if
the original gets overwritten I have no way to check my work later or explain
how I got a number. Raw data is also the one version everyone can agree on -
the moment you start sorting, filtering in place, or deleting things directly
in the source, it becomes very easy to lose track of what was changed and
why. Keeping the raw copy untouched means I can always rebuild any analysis
from scratch, catch mistakes in my own filtering logic, and hand the file to
someone else without worrying that I've quietly changed what the "real" data
says.
