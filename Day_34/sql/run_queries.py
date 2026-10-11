"""Loads cleaned CSVs into SQLite, runs every query in 02_core_queries.sql, writes results to sql/query_results.md.
Usage (from repo root):  python sql/run_queries.py"""
import sqlite3, pandas as pd, re
con = sqlite3.connect(':memory:')
pd.read_csv('data/netflix_titles_clean.csv').to_sql('titles', con, index=False)
for t in ['title_genres', 'title_countries', 'title_cast', 'title_directors']:
    pd.read_csv(f'data/{t}.csv').to_sql(t, con, index=False)
sql = open('sql/02_core_queries.sql').read()
blocks = re.split(r'\n(?=-- Q\d+\.)', sql)[1:]
out = ['# SQL query results (SQLite)\n']
for b in blocks:
    title = b.split('\n')[0].strip('- ').strip('-').strip()
    df = pd.read_sql_query(b, con)
    out.append(f'## {title}\n\n```sql\n{b.strip()}\n```\n\n{df.to_markdown(index=False)}\n')
open('sql/query_results.md', 'w').write('\n'.join(out))
print(f'Ran {len(blocks)} queries OK')
