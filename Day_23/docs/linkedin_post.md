📊 Task 23 done: SQL Window Functions on the Northwind dataset!

As part of my Data Analytics track, I wrote 12 queries using ROW_NUMBER, RANK, DENSE_RANK and LAG to answer real business questions:

🔹 Who was each customer's first (and most recent) order?
🔹 Who are the top customers, and how much revenue do they drive? (3 customers = ~25% of revenue!)
🔹 Which employee and which product led each year?
🔹 How fast is revenue growing month over month?
🔹 How many days pass between a customer's orders?

💡 My biggest takeaways:
1️⃣ RANK vs DENSE_RANK - both give ties the same rank, but RANK skips numbers (1,2,2,4) while DENSE_RANK doesn't (1,2,2,3).
2️⃣ ROW_NUMBER + a CTE is the cleanest way to do "Top-N per group" and "latest record per customer".
3️⃣ LAG replaces messy self-joins for growth % and time-between-events analysis.
4️⃣ Partial months at the edge of a dataset can fake a huge drop - always check before trusting a growth number!

🧹 I also cleaned the data first: fixed date types, handled nulls, validated duplicates and orphan records, and engineered revenue and date features before querying.

Full SQL, outputs, notes and README on GitHub 👉 [add your GitHub link here]

Would love feedback from the data community - what's your favourite window function trick? 👇

#SQL #DataAnalytics #WindowFunctions #Northwind #LearningInPublic #DataAnalyst #MCA #Analytics
