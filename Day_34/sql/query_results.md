# SQL query results (SQLite)

## Q1. Catalog composition: Movies vs TV Shows

```sql
-- Q1. Catalog composition: Movies vs TV Shows ---------------------------
SELECT type,
       COUNT(*)                                             AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)   AS pct_of_catalog
FROM titles
GROUP BY type;
```

| type    |   titles |   pct_of_catalog |
|:--------|---------:|-----------------:|
| Movie   |     6131 |             69.6 |
| TV Show |     2676 |             30.4 |

## Q2. Content velocity: titles added per year, by type

```sql
-- Q2. Content velocity: titles added per year, by type --------------------
SELECT year_added,
       SUM(type = 'Movie')   AS movies,
       SUM(type = 'TV Show') AS tv_shows,
       COUNT(*)              AS total
FROM titles
WHERE year_added IS NOT NULL AND year_added <> ''
GROUP BY year_added
ORDER BY year_added;
```

|   year_added |   movies |   tv_shows |   total |
|-------------:|---------:|-----------:|--------:|
|         2008 |        1 |          1 |       2 |
|         2009 |        2 |          0 |       2 |
|         2010 |        1 |          0 |       1 |
|         2011 |       13 |          0 |      13 |
|         2012 |        3 |          0 |       3 |
|         2013 |        6 |          5 |      11 |
|         2014 |       19 |          5 |      24 |
|         2015 |       56 |         26 |      82 |
|         2016 |      253 |        176 |     429 |
|         2017 |      839 |        349 |    1188 |
|         2018 |     1237 |        412 |    1649 |
|         2019 |     1424 |        592 |    2016 |
|         2020 |     1284 |        595 |    1879 |
|         2021 |      993 |        505 |    1498 |

## Q3. TV share of new additions per year (window function)

```sql
-- Q3. TV share of new additions per year (window function) ------------------
SELECT year_added,
       COUNT(*) AS total_added,
       ROUND(100.0 * SUM(type = 'TV Show') / COUNT(*), 1) AS tv_share_pct
FROM titles
WHERE year_added >= 2015
GROUP BY year_added
ORDER BY year_added;
```

|   year_added |   total_added |   tv_share_pct |
|-------------:|--------------:|---------------:|
|         2015 |            82 |           31.7 |
|         2016 |           429 |           41   |
|         2017 |          1188 |           29.4 |
|         2018 |          1649 |           25   |
|         2019 |          2016 |           29.4 |
|         2020 |          1879 |           31.7 |
|         2021 |          1498 |           33.7 |

## Q4. Top 10 genres overall (JOIN on bridge table)

```sql
-- Q4. Top 10 genres overall (JOIN on bridge table) ---------------------------
SELECT g.genre, COUNT(*) AS titles
FROM title_genres g
GROUP BY g.genre
ORDER BY titles DESC
LIMIT 10;
```

| genre                    |   titles |
|:-------------------------|---------:|
| International Movies     |     2752 |
| Dramas                   |     2427 |
| Comedies                 |     1674 |
| International TV Shows   |     1351 |
| Documentaries            |      869 |
| Action & Adventure       |      859 |
| TV Dramas                |      763 |
| Independent Movies       |      756 |
| Children & Family Movies |      641 |
| Romantic Movies          |      616 |

## Q5. Top 5 genres within each type (JOIN + RANK window)

```sql
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
```

| type    |   rnk | genre                  |   titles |
|:--------|------:|:-----------------------|---------:|
| Movie   |     1 | International Movies   |     2752 |
| Movie   |     2 | Dramas                 |     2427 |
| Movie   |     3 | Comedies               |     1674 |
| Movie   |     4 | Documentaries          |      869 |
| Movie   |     5 | Action & Adventure     |      859 |
| TV Show |     1 | International TV Shows |     1351 |
| TV Show |     2 | TV Dramas              |      763 |
| TV Show |     3 | TV Comedies            |      581 |
| TV Show |     4 | Crime TV Shows         |      470 |
| TV Show |     5 | Kids' TV               |      451 |

## Q6. Genre share by release era (which genres are growing?)

```sql
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
```

| genre                     |   pct_le_2009 |   pct_2018_21 |
|:--------------------------|--------------:|--------------:|
| International TV Shows    |           2.2 |           9.3 |
| TV Dramas                 |           1.1 |           5.5 |
| Crime TV Shows            |           0.4 |           3.7 |
| TV Comedies               |           1.4 |           4.1 |
| Documentaries             |           1.7 |           4.3 |
| Docuseries                |           0.7 |           2.9 |
| Reality TV                |           0.2 |           2.2 |
| Kids' TV                  |           1.5 |           2.8 |
| Romantic TV Shows         |           0.9 |           2   |
| Spanish-Language TV Shows |           0.3 |           1.4 |

## Q7. Content rating mix by type

```sql
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
```

| rating   |   movies |   tv_shows |   total |   pct |
|:---------|---------:|-----------:|--------:|------:|
| TV-MA    |     2062 |       1145 |    3207 |  36.4 |
| TV-14    |     1427 |        733 |    2160 |  24.5 |
| TV-PG    |      540 |        323 |     863 |   9.8 |
| R        |      797 |          2 |     799 |   9.1 |
| PG-13    |      490 |          0 |     490 |   5.6 |
| TV-Y7    |      139 |        195 |     334 |   3.8 |
| TV-Y     |      131 |        176 |     307 |   3.5 |
| PG       |      287 |          0 |     287 |   3.3 |
| TV-G     |      126 |         94 |     220 |   2.5 |
| NR       |       75 |          5 |      80 |   0.9 |
| G        |       41 |          0 |      41 |   0.5 |
| TV-Y7-FV |        5 |          1 |       6 |   0.1 |
| NC-17    |        3 |          0 |       3 |   0   |
| UR       |        3 |          0 |       3 |   0   |

## Q8. Audience (Kids / Teens / Adults) share by type

```sql
-- Q8. Audience (Kids / Teens / Adults) share by type -------------------------
SELECT type, audience,
       COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY type), 1) AS pct_within_type
FROM titles
GROUP BY type, audience
ORDER BY type, titles DESC;
```

| type    | audience   |   titles |   pct_within_type |
|:--------|:-----------|---------:|------------------:|
| Movie   | Adults     |     2862 |              46.7 |
| Movie   | Teens      |     2744 |              44.8 |
| Movie   | Kids       |      442 |               7.2 |
| Movie   | Unrated    |       83 |               1.4 |
| TV Show | Adults     |     1147 |              42.9 |
| TV Show | Teens      |     1056 |              39.5 |
| TV Show | Kids       |      466 |              17.4 |
| TV Show | Unrated    |        7 |               0.3 |

## Q9. Top 10 production countries (JOIN bridge)

```sql
-- Q9. Top 10 production countries (JOIN bridge) -------------------------------
SELECT c.country, COUNT(*) AS titles,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM title_countries), 1) AS pct_of_country_tags
FROM title_countries c
GROUP BY c.country
ORDER BY titles DESC
LIMIT 10;
```

| country        |   titles |   pct_of_country_tags |
|:---------------|---------:|----------------------:|
| United States  |     3690 |                  36.9 |
| India          |     1046 |                  10.4 |
| United Kingdom |      806 |                   8.1 |
| Canada         |      445 |                   4.4 |
| France         |      393 |                   3.9 |
| Japan          |      318 |                   3.2 |
| Spain          |      232 |                   2.3 |
| South Korea    |      231 |                   2.3 |
| Germany        |      226 |                   2.3 |
| Mexico         |      169 |                   1.7 |

## Q10. Country mix by year added: US vs India vs rest (JOIN + conditional agg)

```sql
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
```

|   year_added |   country_tags |   us_pct |   india_pct |   uk_pct |   korea_pct |
|-------------:|---------------:|---------:|------------:|---------:|------------:|
|         2016 |            539 |     37.7 |         2.4 |     10   |         2   |
|         2017 |           1409 |     32.8 |        11.5 |      9.5 |         3.1 |
|         2018 |           1919 |     31.3 |        18.2 |      7.7 |         1.7 |
|         2019 |           2262 |     37.8 |         9.6 |      8.4 |         2.6 |
|         2020 |           2228 |     37.2 |         8.9 |      6.6 |         2.5 |
|         2021 |           1470 |     42.7 |         7.1 |      8.2 |         2   |

## Q11. Movie vs TV mix per country (finds the "series gap")

```sql
-- Q11. Movie vs TV mix per country (finds the "series gap") --------------------
SELECT c.country,
       SUM(t.type = 'Movie')   AS movies,
       SUM(t.type = 'TV Show') AS tv_shows,
       ROUND(100.0 * SUM(t.type = 'TV Show') / COUNT(*), 1) AS tv_share_pct
FROM titles t JOIN title_countries c ON c.show_id = t.show_id
GROUP BY c.country
HAVING COUNT(*) >= 200
ORDER BY tv_share_pct;
```

| country        |   movies |   tv_shows |   tv_share_pct |
|:---------------|---------:|-----------:|---------------:|
| India          |      962 |         84 |            8   |
| Germany        |      182 |         44 |           19.5 |
| France         |      303 |         90 |           22.9 |
| United States  |     2752 |        938 |           25.4 |
| Spain          |      171 |         61 |           26.3 |
| Canada         |      319 |        126 |           28.3 |
| United Kingdom |      534 |        272 |           33.7 |
| Japan          |      119 |        199 |           62.6 |
| South Korea    |       61 |        170 |           73.6 |

## Q12. Movie runtime trend by release era

```sql
-- Q12. Movie runtime trend by release era -------------------------------------
SELECT release_era,
       COUNT(*)                     AS movies,
       ROUND(AVG(duration_min), 1)  AS avg_minutes
FROM titles
WHERE type = 'Movie' AND duration_min BETWEEN 40 AND 240
GROUP BY release_era
ORDER BY MIN(release_year);
```

| release_era   |   movies |   avg_minutes |
|:--------------|---------:|--------------:|
| Pre-2000      |      468 |         116   |
| 2000-09       |      673 |         112.6 |
| 2010-14       |      939 |         102.7 |
| 2015-17       |     1789 |          97.7 |
| 2018-19       |     1351 |          97.3 |
| 2020-21       |      738 |          98.5 |

## Q13. Season-count distribution for TV shows

```sql
-- Q13. Season-count distribution for TV shows ---------------------------------
SELECT CASE WHEN n_seasons >= 4 THEN '4+' ELSE CAST(CAST(n_seasons AS INT) AS TEXT) END AS seasons,
       COUNT(*) AS shows,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM titles
WHERE type = 'TV Show'
GROUP BY 1
ORDER BY 1;
```

| seasons   |   shows |   pct |
|:----------|--------:|------:|
| 1         |    1793 |  67   |
| 2         |     425 |  15.9 |
| 3         |     199 |   7.4 |
| 4+        |     259 |   9.7 |

## Q14. International co-production share by era (excluding unknown country)

```sql
-- Q14. International co-production share by era (excluding unknown country) ----
SELECT release_era,
       COUNT(*) AS titles,
       ROUND(100.0 * SUM(n_countries > 1) / COUNT(*), 1) AS coprod_pct
FROM titles
WHERE country <> 'Unknown'
GROUP BY release_era
ORDER BY MIN(release_year);
```

| release_era   |   titles |   coprod_pct |
|:--------------|---------:|-------------:|
| Pre-2000      |      502 |         16.5 |
| 2000-09       |      786 |         22.8 |
| 2010-14       |     1182 |         19.4 |
| 2015-17       |     2320 |         17.6 |
| 2018-19       |     1951 |         14.7 |
| 2020-21       |     1235 |         10.8 |

## Q15. Most prolific directors with 2+ titles, excluding unknown (JOIN)

```sql
-- Q15. Most prolific directors with 2+ titles, excluding unknown (JOIN) ---------
SELECT d.director, COUNT(*) AS titles
FROM title_directors d
GROUP BY d.director
HAVING COUNT(*) >= 2
ORDER BY titles DESC
LIMIT 10;
```

| director            |   titles |
|:--------------------|---------:|
| Rajiv Chilaka       |       22 |
| Jan Suter           |       21 |
| Raúl Campos         |       19 |
| Suhas Kadav         |       16 |
| Marcus Raboy        |       16 |
| Jay Karas           |       15 |
| Cathy Garcia-Molina |       13 |
| Youssef Chahine     |       12 |
| Martin Scorsese     |       12 |
| Jay Chapman         |       12 |

## Q16. Top genres in India (3-table JOIN)

```sql
-- Q16. Top genres in India (3-table JOIN) --------------------------------------
SELECT g.genre, COUNT(*) AS titles
FROM title_countries c
JOIN title_genres   g ON g.show_id = c.show_id
WHERE c.country = 'India'
GROUP BY g.genre
ORDER BY titles DESC
LIMIT 8;
```

| genre                |   titles |
|:---------------------|---------:|
| International Movies |      864 |
| Dramas               |      662 |
| Comedies             |      323 |
| Independent Movies   |      167 |
| Action & Adventure   |      137 |
| Romantic Movies      |      120 |
| Music & Musicals     |       96 |
| Thrillers            |       92 |

## Q17. Which genres are most "global"? Countries per genre (distinct count)

```sql
-- Q17. Which genres are most "global"? Countries per genre (distinct count) -----
SELECT g.genre,
       COUNT(DISTINCT c.country) AS countries_producing,
       COUNT(DISTINCT g.show_id) AS titles
FROM title_genres g JOIN title_countries c ON c.show_id = g.show_id
GROUP BY g.genre
HAVING titles >= 100
ORDER BY countries_producing DESC
LIMIT 10;
```

| genre                  |   countries_producing |   titles |
|:-----------------------|----------------------:|---------:|
| International Movies   |                   100 |     2543 |
| Dramas                 |                    92 |     2317 |
| Documentaries          |                    73 |      794 |
| Independent Movies     |                    66 |      745 |
| Comedies               |                    66 |     1580 |
| International TV Shows |                    61 |     1128 |
| TV Dramas              |                    59 |      663 |
| Action & Adventure     |                    59 |      817 |
| Thrillers              |                    55 |      549 |
| Romantic Movies        |                    53 |      588 |
