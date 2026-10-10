"""Clean netflix_titles.csv and write analysis-ready tables.

Usage: python scripts/clean_data.py
Outputs (in data/):
  netflix_clean.csv      one row per title (cleaned)
  netflix_genres.csv     one row per title-genre (exploded listed_in)
  netflix_countries.csv  one row per title-country (exploded country)
  netflix_netflix.db     SQLite DB with the three tables, for the SQL queries
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

df = pd.read_csv(DATA / "netflix_titles.csv")
log = {"raw_rows": len(df)}

# 1. Strip whitespace on all text columns
for c in df.select_dtypes(include=["object", "string"]).columns:
    df[c] = df[c].str.strip()

# 2. Fix shifted rows: 3 records have the duration stored in `rating`
shifted = df["rating"].astype(str).str.contains("min", na=False)
log["shifted_rating_rows_fixed"] = int(shifted.sum())
df.loc[shifted, "duration"] = df.loc[shifted, "rating"]
df.loc[shifted, "rating"] = pd.NA

# 3. Missing categorical values -> explicit 'Unknown' (keeps rows for analysis)
for c in ["director", "cast", "country"]:
    log[f"missing_{c}"] = int(df[c].isna().sum())
    df[c] = df[c].fillna("Unknown")
log["missing_rating"] = int(df["rating"].isna().sum())
df["rating"] = df["rating"].fillna("Not Rated")

# 4. Dates
df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y", errors="coerce")
log["missing_date_added"] = int(df["date_added"].isna().sum())
df["year_added"] = df["date_added"].dt.year.astype("Int64")
df["month_added"] = df["date_added"].dt.month.astype("Int64")

# 5. Duration -> numeric columns (minutes for movies, seasons for TV)
num = pd.to_numeric(df["duration"].str.extract(r"(\d+)")[0], errors="coerce")
df["duration_min"] = num.where(df["type"] == "Movie")
df["seasons"] = num.where(df["type"] == "TV Show")

# 6. Rating groups (audience segment) for strategy analysis
rating_group = {
    "TV-Y": "Kids", "TV-Y7": "Kids", "TV-Y7-FV": "Kids", "TV-G": "Kids", "G": "Kids",
    "TV-PG": "Teens", "PG": "Teens", "TV-14": "Teens", "PG-13": "Teens",
    "TV-MA": "Adults", "R": "Adults", "NC-17": "Adults",
    "NR": "Not Rated", "UR": "Not Rated", "Not Rated": "Not Rated",
}
df["audience"] = df["rating"].map(rating_group).fillna("Not Rated")

# 7. Primary country / primary genre, content age, release era
df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()
df["lag_years"] = (df["year_added"] - df["release_year"]).astype("Int64")
df["era"] = pd.cut(df["release_year"], [1924, 1999, 2009, 2014, 2021],
                   labels=["Pre-2000", "2000-09", "2010-14", "2015-21"])
df["era"] = df["era"].astype(str)

# 8. Duplicates check
log["duplicate_show_ids"] = int(df["show_id"].duplicated().sum())
dup_cols = ["title", "type", "release_year", "country", "date_added"]
log["duplicate_title_rows_dropped"] = int(df.duplicated(dup_cols).sum())
df = df.drop_duplicates(dup_cols).reset_index(drop=True)

# 9. Exploded tables
genres = (df[["show_id", "type", "release_year", "year_added", "listed_in"]]
          .assign(genre=lambda d: d["listed_in"].str.split(","))
          .explode("genre").drop(columns="listed_in"))
genres["genre"] = genres["genre"].str.strip()

countries = (df[["show_id", "type", "release_year", "year_added", "country"]]
             .assign(country=lambda d: d["country"].str.split(","))
             .explode("country"))
countries["country"] = countries["country"].str.strip()
countries = countries[(countries["country"] != "") & countries["country"].notna()]

# 10. Save
df.to_csv(DATA / "netflix_clean.csv", index=False)
genres.to_csv(DATA / "netflix_genres.csv", index=False)
countries.to_csv(DATA / "netflix_countries.csv", index=False)

db = DATA / "netflix.db"
if db.exists():
    db.unlink()
with sqlite3.connect(db) as con:
    out = df.copy()
    out["date_added"] = out["date_added"].dt.strftime("%Y-%m-%d")
    out.to_sql("titles", con, index=False)
    genres.to_sql("title_genres", con, index=False)
    countries.to_sql("title_countries", con, index=False)

log.update(clean_rows=len(df), genre_rows=len(genres), country_rows=len(countries))
for k, v in log.items():
    print(f"{k:30s} {v}")
