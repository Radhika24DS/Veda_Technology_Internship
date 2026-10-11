-- =====================================================================
-- CORE AGGREGATION QUERIES — OTT Content Trend Analysis
-- Dialect: SQLite (works on PostgreSQL with minor changes: use TRUE/FALSE, ROUND(x::numeric,1))
-- =====================================================================

-- Q1. Catalog composition: Movies vs TV Shows ---------------------------
SELECT type,
       COUNT(*)                                             AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)   AS pct_of_catalog
FROM titles
GROUP BY type;

-- Q2. Content velocity: titles added per year, by type --------------------
SELECT year_added,
       SUM(type = 'Movie')   AS movies,
       SUM(type = 'TV Show') AS tv_shows,
       COUNT(*)              AS total
FROM titles
WHERE year_added IS NOT NULL AND year_added <> ''
GROUP BY year_added
ORDER BY year_added;

-- Q3. TV share of new additions per year (window function) ------------------
SELECT year_added,
       COUNT(*) AS total_added,
       ROUND(100.0 * SUM(type = 'TV Show') / COUNT(*), 1) AS tv_share_pct
FROM titles
WHERE year_added >= 2015
GROUP BY year_added
ORDER BY year_added;

-- Q4. Top 10 genres overall (JOIN on bridge table) ---------------------------
SELECT g.genre, COUNT(*) AS titles
FROM title_genres g
GROUP BY g.genre
ORDER BY titles DESC
LIMIT 10;

-- Q5. Top 5 genres within each type (JOIN + RANK window) ---------------------
WITH genre_counts AS (
    SELECT t.type, g.genre, COUNT(*) AS titles
    FROM titles t
    JOIN title_genres g ON g.show_id = t.show_id
    GROUP BY t.type, g.genre
), ranked AS (
    SELECT *, RANK() OVER (PARTITION BY type ORDER BY titles DESC) AS rnk
    FROM genre_counts
)
SELECT type, rnk, genre, titles FROM ranked WHERE rnk <= 5 ORDER BY type, rnk;

-- Q6. Genre share by release era (which genres are growing?) -----------------
WITH tagged AS (
    SELECT CASE WHEN t.release_year <= 2009 THEN '1: <=2009'
                WHEN t.release_year <= 2014 THEN '2: 2010-14'
                WHEN t.release_year <= 2017 THEN '3: 2015-17'
                ELSE '4: 2018-21' END AS era,
           g.genre
    FROM titles t JOIN title_genres g ON g.show_id = t.show_id
), era_totals AS (SELECT era, COUNT(*) AS n FROM tagged GROUP BY era),
   genre_era  AS (SELECT era, genre, COUNT(*) AS c FROM tagged GROUP BY era, genre)
SELECT ge.genre,
       ROUND(100.0 * MAX(CASE WHEN ge.era = '1: <=2009' THEN ge.c END) / MAX(CASE WHEN et.era='1: <=2009' THEN et.n END), 1) AS pct_le_2009,
       ROUND(100.0 * MAX(CASE WHEN ge.era = '4: 2018-21' THEN ge.c END) / MAX(CASE WHEN et.era='4: 2018-21' THEN et.n END), 1) AS pct_2018_21
FROM genre_era ge JOIN era_totals et ON et.era = ge.era
GROUP BY ge.genre
HAVING pct_le_2009 IS NOT NULL AND pct_2018_21 IS NOT NULL
ORDER BY (pct_2018_21 - pct_le_2009) DESC
LIMIT 10;

-- Q7. Content rating mix by type ---------------------------------------------
SELECT rating,
       SUM(type = 'Movie')   AS movies,
       SUM(type = 'TV Show') AS tv_shows,
       COUNT(*)              AS total,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM titles
WHERE rating <> 'Unknown'
GROUP BY rating
ORDER BY total DESC;

-- Q8. Audience (Kids / Teens / Adults) share by type -------------------------
SELECT type, audience,
       COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY type), 1) AS pct_within_type
FROM titles
GROUP BY type, audience
ORDER BY type, titles DESC;

-- Q9. Top 10 production countries (JOIN bridge) -------------------------------
SELECT c.country, COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM title_countries), 1) AS pct_of_country_tags
FROM title_countries c
GROUP BY c.country
ORDER BY titles DESC
LIMIT 10;

-- Q10. Country mix by year added: US vs India vs rest (JOIN + conditional agg) -
SELECT t.year_added,
       COUNT(*) AS country_tags,
       ROUND(100.0 * SUM(c.country = 'United States') / COUNT(*), 1) AS us_pct,
       ROUND(100.0 * SUM(c.country = 'India')         / COUNT(*), 1) AS india_pct,
       ROUND(100.0 * SUM(c.country = 'United Kingdom')/ COUNT(*), 1) AS uk_pct,
       ROUND(100.0 * SUM(c.country = 'South Korea')   / COUNT(*), 1) AS korea_pct
FROM titles t JOIN title_countries c ON c.show_id = t.show_id
WHERE t.year_added BETWEEN 2016 AND 2021
GROUP BY t.year_added
ORDER BY t.year_added;

-- Q11. Movie vs TV mix per country (finds the "series gap") --------------------
SELECT c.country,
       SUM(t.type = 'Movie')   AS movies,
       SUM(t.type = 'TV Show') AS tv_shows,
       ROUND(100.0 * SUM(t.type = 'TV Show') / COUNT(*), 1) AS tv_share_pct
FROM titles t JOIN title_countries c ON c.show_id = t.show_id
GROUP BY c.country
HAVING COUNT(*) >= 200
ORDER BY tv_share_pct;

-- Q12. Movie runtime trend by release era -------------------------------------
SELECT release_era,
       COUNT(*)                     AS movies,
       ROUND(AVG(duration_min), 1)  AS avg_minutes
FROM titles
WHERE type = 'Movie' AND duration_min BETWEEN 40 AND 240
GROUP BY release_era
ORDER BY MIN(release_year);

-- Q13. Season-count distribution for TV shows ---------------------------------
SELECT CASE WHEN n_seasons >= 4 THEN '4+' ELSE CAST(CAST(n_seasons AS INT) AS TEXT) END AS seasons,
       COUNT(*) AS shows,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM titles
WHERE type = 'TV Show'
GROUP BY 1
ORDER BY 1;

-- Q14. International co-production share by era (excluding unknown country) ----
SELECT release_era,
       COUNT(*) AS titles,
       ROUND(100.0 * SUM(n_countries > 1) / COUNT(*), 1) AS coprod_pct
FROM titles
WHERE country <> 'Unknown'
GROUP BY release_era
ORDER BY MIN(release_year);

-- Q15. Most prolific directors with 2+ titles, excluding unknown (JOIN) ---------
SELECT d.director, COUNT(*) AS titles
FROM title_directors d
GROUP BY d.director
HAVING COUNT(*) >= 2
ORDER BY titles DESC
LIMIT 10;

-- Q16. Top genres in India (3-table JOIN) --------------------------------------
SELECT g.genre, COUNT(*) AS titles
FROM title_countries c
JOIN title_genres   g ON g.show_id = c.show_id
WHERE c.country = 'India'
GROUP BY g.genre
ORDER BY titles DESC
LIMIT 8;

-- Q17. Which genres are most "global"? Countries per genre (distinct count) -----
SELECT g.genre,
       COUNT(DISTINCT c.country) AS countries_producing,
       COUNT(DISTINCT g.show_id) AS titles
FROM title_genres g JOIN title_countries c ON c.show_id = g.show_id
GROUP BY g.genre
HAVING titles >= 100
ORDER BY countries_producing DESC
LIMIT 10;
