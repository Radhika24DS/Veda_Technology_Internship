import sqlite3, re, pandas as pd, math
df = pd.read_csv("data/superstore_clean.csv")
con = sqlite3.connect(":memory:")
con.create_function("POWER", 2, lambda a, b: a ** b)
df.to_sql("superstore", con, index=False)
sql = open("sql/growth_queries.sql").read()
parts = [p.strip() for p in sql.split(";") if "SELECT" in p]
names = ["q1_annual","q2_yoy","q3_qoq","q4_smallbase","q5_cagr","q6_crosssection"]
for n, p in zip(names, parts):
    r = pd.read_sql(p, con); r.to_csv(f"outputs/{n}.csv", index=False)
    print("==", n, r.shape); print(r.head(20).to_string(index=False))
