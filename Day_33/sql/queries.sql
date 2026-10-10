-- =====================================================================
-- Netflix Content Trend Analysis - core SQL aggregations
-- Dialect: SQLite (also runs on PostgreSQL/MySQL with minor tweaks noted)
-- Tables (created by scripts/clean_data.py -> data/netflix.db):
--   titles           one row per title (cleaned)
--   title_genres     one row per title x genre      (show_id, type, release_year, year_added, genre)
--   title_countries  one row per title x country    (show_id, type, release_year, year_added, country)
-- Each query block starts with "-- name: <id>" so the notebook can run it.
-- =====================================================================


-- name: q01_catalog_size_by_type
-- Catalog split: how big is the library and how much is Movies vs TV?
SELECT type,
       COUNT(*)                                             AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)   AS pct_of_catalog
FROM titles
GROUP BY type;


-- name: q02_additions_per_year_by_type
-- Release cadence: titles added to the platform each year, by type.
-- (2021 is a partial year - data ends 25-Sep-2021.)
SELECT year_added,
       SUM(type = 'Movie')   AS movies_added,
       SUM(type = 'TV Show') AS tv_added,
       COUNT(*)              AS total_added
FROM titles
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;


-- name: q03_tv_share_of_additions
-- Is the mix shifting toward series? TV share of each year's new additions.
SELECT year_added,
       COUNT(*)                                                AS total_added,
       ROUND(100.0 * SUM(type = 'TV Show') / COUNT(*), 1)      AS tv_share_pct
FROM titles
WHERE year_added BETWEEN 2016 AND 2021
GROUP BY year_added
ORDER BY year_added;


-- name: q04_top_genres_by_type
-- Top 8 genres within Movies and within TV (window function + CTE).
WITH genre_counts AS (
    SELECT type, genre, COUNT(*) AS titles
    FROM title_genres
    GROUP BY type, genre
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY type ORDER BY titles DESC) AS rnk
    FROM genre_counts
)
SELECT type, rnk, genre, titles
FROM ranked
WHERE rnk <= 8
ORDER BY type, rnk;


-- name: q05_genre_momentum
-- Which genres are gaining share of new additions?
-- Compares 2016-18 (build-out era) vs 2020-21 (recent era); 2019 skipped as the transition peak.
-- Share = % of that period's additions tagged with the genre (a title can carry several genres).
WITH base AS (
    SELECT show_id,
           CASE WHEN year_added BETWEEN 2016 AND 2018 THEN 'early'
                WHEN year_added BETWEEN 2020 AND 2021 THEN 'late' END AS period
    FROM titles
    WHERE year_added IN (2016, 2017, 2018, 2020, 2021)
),
totals AS (
    SELECT period, COUNT(*) AS t FROM base GROUP BY period
)
SELECT g.genre,
       SUM(b.period = 'early') + SUM(b.period = 'late')                                      AS titles_in_window,
       ROUND(100.0 * SUM(b.period = 'early') / (SELECT t FROM totals WHERE period = 'early'), 2) AS early_share_pct,
       ROUND(100.0 * SUM(b.period = 'late')  / (SELECT t FROM totals WHERE period = 'late'),  2) AS late_share_pct,
       ROUND(100.0 * SUM(b.period = 'late')  / (SELECT t FROM totals WHERE period = 'late'), 2)
     - ROUND(100.0 * SUM(b.period = 'early') / (SELECT t FROM totals WHERE period = 'early'), 2) AS share_change_pp
FROM title_genres g
JOIN base b ON b.show_id = g.show_id
GROUP BY g.genre
HAVING titles_in_window >= 150
ORDER BY share_change_pp DESC;


-- name: q06_audience_mix_by_year
-- Content ratings grouped into audience segments (Kids / Teens / Adults), % of each year's additions.
SELECT year_added,
       ROUND(100.0 * SUM(audience = 'Kids')   / COUNT(*), 1) AS kids_pct,
       ROUND(100.0 * SUM(audience = 'Teens')  / COUNT(*), 1) AS teens_pct,
       ROUND(100.0 * SUM(audience = 'Adults') / COUNT(*), 1) AS adults_pct,
       COUNT(*)                                              AS titles
FROM titles
WHERE year_added BETWEEN 2016 AND 2021
GROUP BY year_added
ORDER BY year_added;


-- name: q07_rating_detail
-- Detailed rating distribution by type.
SELECT rating,
       SUM(type = 'Movie')   AS movies,
       SUM(type = 'TV Show') AS tv_shows,
       COUNT(*)              AS total
FROM titles
GROUP BY rating
ORDER BY total DESC;


-- name: q08_top_countries
-- Regional mix: top producing countries (multi-country titles count once per country).
SELECT country,
       COUNT(*)                                                       AS titles,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(DISTINCT show_id) FROM title_countries WHERE country <> 'Unknown'), 1) AS pct_of_titles_with_country
FROM title_countries
WHERE country <> 'Unknown'
GROUP BY country
ORDER BY titles DESC
LIMIT 10;


-- name: q09_non_us_share_by_year
-- How international is the new-addition pipeline? % of each year's titles NOT tagged United States.
WITH us AS (
    SELECT DISTINCT show_id FROM title_countries WHERE country = 'United States'
)
SELECT t.year_added,
       COUNT(*)                                                        AS titles_with_country,
       ROUND(100.0 * SUM(us.show_id IS NULL) / COUNT(*), 1)            AS non_us_share_pct
FROM titles t
LEFT JOIN us ON us.show_id = t.show_id
WHERE t.country <> 'Unknown' AND t.year_added BETWEEN 2016 AND 2021
GROUP BY t.year_added
ORDER BY t.year_added;


-- name: q10_country_growth
-- Country momentum: titles added by year for focus markets (join + conditional aggregation).
SELECT country,
       SUM(year_added = 2016) AS y2016,
       SUM(year_added = 2017) AS y2017,
       SUM(year_added = 2018) AS y2018,
       SUM(year_added = 2019) AS y2019,
       SUM(year_added = 2020) AS y2020,
       SUM(year_added = 2021) AS y2021
FROM title_countries
WHERE country IN ('United States', 'India', 'United Kingdom', 'Japan', 'South Korea', 'Spain', 'France', 'Canada')
GROUP BY country
ORDER BY y2020 + y2021 DESC;


-- name: q11_top_genres_by_country
-- JOIN practice: what does each focus market actually produce? Top 3 genres per country.
WITH cg AS (
    SELECT c.country, g.genre, COUNT(*) AS titles
    FROM title_countries c
    JOIN title_genres g ON g.show_id = c.show_id
    WHERE c.country IN ('India', 'South Korea', 'Japan', 'United Kingdom', 'Spain')
    GROUP BY c.country, g.genre
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY country ORDER BY titles DESC) AS rnk FROM cg
)
SELECT country, rnk, genre, titles
FROM ranked
WHERE rnk <= 3
ORDER BY country, rnk;


-- name: q12_movie_runtime_trend
-- Movie length trend by release year (SQLite has no MEDIAN; use AVG and the quartile spread in Python).
SELECT release_year,
       COUNT(*)                         AS movies,
       ROUND(AVG(duration_min), 1)      AS avg_runtime_min
FROM titles
WHERE type = 'Movie' AND release_year >= 2000 AND duration_min IS NOT NULL
GROUP BY release_year
ORDER BY release_year;


-- name: q13_tv_season_distribution
-- How many TV titles stop at one season vs continue?
SELECT seasons,
       COUNT(*)                                                   AS shows,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)         AS pct_of_shows
FROM titles
WHERE type = 'TV Show'
GROUP BY seasons
ORDER BY seasons;


-- name: q14_content_freshness
-- Freshness: average gap (years) between a title's release and its arrival on the platform.
SELECT year_added,
       ROUND(AVG(lag_years), 1)                                           AS avg_lag_years,
       ROUND(100.0 * SUM(lag_years <= 1) / COUNT(*), 1)                   AS pct_added_within_1yr_of_release
FROM titles
WHERE year_added BETWEEN 2016 AND 2021 AND lag_years IS NOT NULL
GROUP BY year_added
ORDER BY year_added;
