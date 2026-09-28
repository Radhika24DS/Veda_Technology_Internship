"""Loads the cleaned CSVs into a temporary SQLite DB, runs the 10 queries from
sql/02_task21_queries.sql and saves each result as outputs/qNN_result.csv plus outputs/query_outputs.md.
(SQLite is used only to execute the same standard SQL for generating verified outputs.)"""
import re, sqlite3, pandas as pd
con = sqlite3.connect(":memory:")
pd.read_csv("data/orders_clean.csv", dtype={"ship_postal_code": str}).to_sql("orders", con, index=False)
pd.read_csv("data/order_details_clean.csv").to_sql("order_details", con, index=False)
text = open("sql/02_task21_queries.sql").read()
blocks = re.split(r"(?m)^-- (Q\d+): ", text)[1:]
md = ["# Task 21 - Query Outputs\n", "Each output below was produced by running the query in `sql/02_task21_queries.sql` on the cleaned Northwind data.\n"]
for qid, body in zip(blocks[0::2], blocks[1::2]):
    lines = body.split("\n")
    title = lines[0].strip()
    biz = next((l[3:].strip() for l in lines if l.startswith("-- Business")), "")
    sql = re.sub(r"(?m)^--.*\n?", "", "\n".join(lines[1:])).strip().rstrip(";")
    df = pd.read_sql_query(sql, con)
    n = int(qid[1:])
    df.to_csv(f"outputs/q{n:02d}_result.csv", index=False, na_rep="NULL")
    md += [f"## {qid}: {title}\n", f"{biz}\n", "```sql", sql + ";", "```\n", f"**Rows returned: {len(df)}**\n", df.astype(object).where(df.notna(), "NULL").to_markdown(index=False) if len(df) else "_(no rows)_", "\n"]
    print(qid, len(df), "rows")
open("outputs/query_outputs.md", "w").write("\n".join(md))
