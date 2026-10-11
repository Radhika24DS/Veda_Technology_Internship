-- =====================================================================
-- Setup: load the cleaned CSVs into 5 tables (SQLite / PostgreSQL friendly)
-- Fact table : titles       (one row per title)
-- Bridge tbls: title_genres, title_countries, title_cast, title_directors
--              (many-to-many, created by exploding comma-separated fields)
-- =====================================================================
CREATE TABLE titles (
    show_id TEXT PRIMARY KEY, type TEXT, title TEXT, director TEXT, "cast" TEXT, country TEXT,
    date_added TEXT, release_year INT, rating TEXT, duration TEXT, listed_in TEXT, description TEXT,
    year_added INT, month_added INT, lag_years INT, duration_num INT, duration_min REAL, n_seasons REAL,
    audience TEXT, primary_country TEXT, n_countries INT, primary_genre TEXT,
    is_international_coprod TEXT, release_era TEXT
);
CREATE TABLE title_genres    (show_id TEXT, genre TEXT);
CREATE TABLE title_countries (show_id TEXT, country TEXT);
CREATE TABLE title_cast      (show_id TEXT, actor TEXT);
CREATE TABLE title_directors (show_id TEXT, director TEXT);
-- Load with the .import commands in load_and_run.py / sqlite3 shell:
--   .mode csv   .import --skip 1 data/netflix_titles_clean.csv titles   (etc.)
