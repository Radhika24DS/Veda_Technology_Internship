-- Core SQL aggregations for the Netflix catalog analysis
-- Table: titles (loaded from netflix_titles_cleaned.csv)

-- 0. Lookup table: map each rating to an audience group (used for the JOIN in query 5)
CREATE TABLE rating_lookup (rating TEXT PRIMARY KEY, audience TEXT);
INSERT INTO rating_lookup VALUES
 ('TV-Y','Kids'),('TV-Y7','Kids'),('TV-Y7-FV','Kids'),('TV-G','Kids'),('G','Kids'),
 ('TV-PG','Family'),('PG','Family'),('PG-13','Family'),
 ('TV-14','Teen'),
 ('TV-MA','Mature'),('R','Mature'),('NC-17','Mature'),
 ('NR','Unrated'),('UR','Unrated'),('Unrated','Unrated');

-- 1. Titles added per year (catalog growth)
SELECT year_added, COUNT(*) AS titles_added
FROM titles
WHERE year_added >= 2013
GROUP BY year_added
ORDER BY year_added;

-- 2. Movies vs TV shows by release year, with TV share
SELECT release_year,
       SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END)   AS movies,
       SUM(CASE WHEN type = 'TV Show' THEN 1 ELSE 0 END) AS tv_shows,
       ROUND(100.0 * SUM(CASE WHEN type = 'TV Show' THEN 1 ELSE 0 END) / COUNT(*), 1) AS tv_share_pct
FROM titles
WHERE release_year >= 2005
GROUP BY release_year
ORDER BY release_year;

-- 3. Top 10 primary genres
SELECT primary_genre, COUNT(*) AS titles
FROM titles
GROUP BY primary_genre
ORDER BY titles DESC
LIMIT 10;

-- 4. Share of new additions by production country (US / India / Other), 2015-2021
SELECT year_added,
       ROUND(100.0 * SUM(CASE WHEN primary_country = 'United States' THEN 1 ELSE 0 END) / COUNT(*), 1) AS us_pct,
       ROUND(100.0 * SUM(CASE WHEN primary_country = 'India' THEN 1 ELSE 0 END) / COUNT(*), 1)          AS india_pct,
       ROUND(100.0 * SUM(CASE WHEN primary_country NOT IN ('United States','India') THEN 1 ELSE 0 END) / COUNT(*), 1) AS other_pct
FROM titles
WHERE year_added >= 2015
GROUP BY year_added
ORDER BY year_added;

-- 5. JOIN: titles added per year by audience group (kids / family / teen / mature)
SELECT t.year_added,
       r.audience,
       COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY t.year_added), 1) AS pct_of_year
FROM titles t
JOIN rating_lookup r ON t.rating = r.rating
WHERE t.year_added >= 2015
GROUP BY t.year_added, r.audience
ORDER BY t.year_added, r.audience;

-- 6. Average movie runtime by release decade
SELECT (release_year / 10) * 10 AS decade,
       ROUND(AVG(minutes), 1)   AS avg_minutes,
       COUNT(*)                 AS movies
FROM titles
WHERE type = 'Movie' AND release_year >= 1970 AND minutes IS NOT NULL
GROUP BY decade
ORDER BY decade;

-- 7. TV shows by number of seasons (how many are single-season)
SELECT seasons, COUNT(*) AS shows,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM titles
WHERE type = 'TV Show' AND seasons IS NOT NULL
GROUP BY seasons
ORDER BY seasons
LIMIT 6;
