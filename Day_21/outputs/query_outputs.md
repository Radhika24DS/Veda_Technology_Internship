# Task 21 - Query Outputs

Each output below was produced by running the query in `sql/02_task21_queries.sql` on the cleaned Northwind data.

## Q1: View the first 10 orders (SELECT * and LIMIT)

Business question: What does the orders table look like?

```sql
SELECT *
FROM orders
ORDER BY order_id
LIMIT 10;
```

**Rows returned: 10**

|   order_id | customer_id   |   employee_id | order_date   | required_date   | shipped_date   |   ship_via |   freight | ship_name                 | ship_address                               | ship_city      | ship_region   | ship_postal_code   | ship_country   |   days_to_ship |   shipped_late |
|-----------:|:--------------|--------------:|:-------------|:----------------|:---------------|-----------:|----------:|:--------------------------|:-------------------------------------------|:---------------|:--------------|:-------------------|:---------------|---------------:|---------------:|
|      10248 | VINET         |             5 | 1996-07-04   | 1996-08-01      | 1996-07-16     |          3 |     32.38 | Vins et alcools Chevalier | 59 rue de l'Abbaye                         | Reims          | NULL          | 51100              | France         |             12 |              0 |
|      10249 | TOMSP         |             6 | 1996-07-05   | 1996-08-16      | 1996-07-10     |          1 |     11.61 | Toms Spezialitäten        | Luisenstr. 48                              | Münster        | NULL          | 44087              | Germany        |              5 |              0 |
|      10250 | HANAR         |             4 | 1996-07-08   | 1996-08-05      | 1996-07-12     |          2 |     65.83 | Hanari Carnes             | Rua do Paço, 67                            | Rio de Janeiro | RJ            | 05454-876          | Brazil         |              4 |              0 |
|      10251 | VICTE         |             3 | 1996-07-08   | 1996-08-05      | 1996-07-15     |          1 |     41.34 | Victuailles en stock      | 2, rue du Commerce                         | Lyon           | NULL          | 69004              | France         |              7 |              0 |
|      10252 | SUPRD         |             4 | 1996-07-09   | 1996-08-06      | 1996-07-11     |          2 |     51.3  | Suprêmes délices          | Boulevard Tirou, 255                       | Charleroi      | NULL          | B-6000             | Belgium        |              2 |              0 |
|      10253 | HANAR         |             3 | 1996-07-10   | 1996-07-24      | 1996-07-16     |          2 |     58.17 | Hanari Carnes             | Rua do Paço, 67                            | Rio de Janeiro | RJ            | 05454-876          | Brazil         |              6 |              0 |
|      10254 | CHOPS         |             5 | 1996-07-11   | 1996-08-08      | 1996-07-23     |          2 |     22.98 | Chop-suey Chinese         | Hauptstr. 31                               | Bern           | NULL          | 3012               | Switzerland    |             12 |              0 |
|      10255 | RICSU         |             9 | 1996-07-12   | 1996-08-09      | 1996-07-15     |          3 |    148.33 | Richter Supermarkt        | Starenweg 5                                | Genève         | NULL          | 1204               | Switzerland    |              3 |              0 |
|      10256 | WELLI         |             3 | 1996-07-15   | 1996-08-12      | 1996-07-17     |          2 |     13.97 | Wellington Importadora    | Rua do Mercado, 12                         | Resende        | SP            | 08737-363          | Brazil         |              2 |              0 |
|      10257 | HILAA         |             4 | 1996-07-16   | 1996-08-13      | 1996-07-22     |          3 |     81.91 | HILARION-Abastos          | Carrera 22 con Ave. Carlos Soublette #8-35 | San Cristóbal  | Táchira       | 5022               | Venezuela      |              6 |              0 |


## Q2: Select specific columns, oldest orders first (column list + ORDER BY ASC)

Business question: Which were the earliest orders and what did shipping cost?

```sql
SELECT order_id,
       customer_id,
       order_date,
       freight,
       ship_country
FROM orders
ORDER BY order_date ASC, order_id ASC
LIMIT 10;
```

**Rows returned: 10**

|   order_id | customer_id   | order_date   |   freight | ship_country   |
|-----------:|:--------------|:-------------|----------:|:---------------|
|      10248 | VINET         | 1996-07-04   |     32.38 | France         |
|      10249 | TOMSP         | 1996-07-05   |     11.61 | Germany        |
|      10250 | HANAR         | 1996-07-08   |     65.83 | Brazil         |
|      10251 | VICTE         | 1996-07-08   |     41.34 | France         |
|      10252 | SUPRD         | 1996-07-09   |     51.3  | Belgium        |
|      10253 | HANAR         | 1996-07-10   |     58.17 | Brazil         |
|      10254 | CHOPS         | 1996-07-11   |     22.98 | Switzerland    |
|      10255 | RICSU         | 1996-07-12   |    148.33 | Switzerland    |
|      10256 | WELLI         | 1996-07-15   |     13.97 | Brazil         |
|      10257 | HILAA         | 1996-07-16   |     81.91 | Venezuela      |


## Q3: Orders shipped to Germany, highest freight first (WHERE with = and ORDER BY DESC)

Business question: Which German shipments were the most expensive?

```sql
SELECT order_id,
       customer_id,
       ship_city,
       freight
FROM orders
WHERE ship_country = 'Germany'
ORDER BY freight DESC
LIMIT 10;
```

**Rows returned: 10**

|   order_id | customer_id   | ship_city   |   freight |
|-----------:|:--------------|:------------|----------:|
|      10540 | QUICK         | Cunewalde   |   1007.64 |
|      10691 | QUICK         | Cunewalde   |    810.05 |
|      10694 | QUICK         | Cunewalde   |    398.36 |
|      10658 | QUICK         | Cunewalde   |    364.15 |
|      10865 | QUICK         | Cunewalde   |    348.14 |
|      10817 | KOENE         | Brandenburg |    306.07 |
|      11021 | QUICK         | Cunewalde   |    297.18 |
|      10962 | QUICK         | Cunewalde   |    275.79 |
|      10345 | QUICK         | Cunewalde   |    249.06 |
|      11012 | FRANK         | München     |    242.95 |


## Q4: List of countries Northwind ships to (DISTINCT)

Business question: In which countries do customers receive orders?

```sql
SELECT DISTINCT ship_country
FROM orders
ORDER BY ship_country;
```

**Rows returned: 21**

| ship_country   |
|:---------------|
| Argentina      |
| Austria        |
| Belgium        |
| Brazil         |
| Canada         |
| Denmark        |
| Finland        |
| France         |
| Germany        |
| Ireland        |
| Italy          |
| Mexico         |
| Norway         |
| Poland         |
| Portugal       |
| Spain          |
| Sweden         |
| Switzerland    |
| UK             |
| USA            |
| Venezuela      |


## Q5: Expensive 1997 orders (WHERE + AND + BETWEEN)

Business question: Which 1997 orders had freight above 100?

```sql
SELECT order_id,
       customer_id,
       order_date,
       freight,
       ship_country
FROM orders
WHERE order_date BETWEEN '1997-01-01' AND '1997-12-31'
  AND freight > 100
ORDER BY freight DESC
LIMIT 15;
```

**Rows returned: 15**

|   order_id | customer_id   | order_date   |   freight | ship_country   |
|-----------:|:--------------|:-------------|----------:|:---------------|
|      10540 | QUICK         | 1997-05-19   |   1007.64 | Germany        |
|      10691 | QUICK         | 1997-10-03   |    810.05 | Germany        |
|      10514 | ERNSH         | 1997-04-22   |    789.95 | Austria        |
|      10479 | RATTC         | 1997-03-19   |    708.95 | USA            |
|      10612 | SAVEA         | 1997-07-28   |    544.08 | USA            |
|      10634 | FOLIG         | 1997-08-15   |    487.38 | France         |
|      10633 | ERNSH         | 1997-08-15   |    477.9  | Austria        |
|      10430 | ERNSH         | 1997-01-30   |    458.78 | Austria        |
|      10694 | QUICK         | 1997-10-06   |    398.36 | Germany        |
|      10678 | SAVEA         | 1997-09-23   |    388.98 | USA            |
|      10605 | MEREP         | 1997-07-21   |    379.13 | Canada         |
|      10424 | MEREP         | 1997-01-23   |    370.61 | Canada         |
|      10510 | SAVEA         | 1997-04-18   |    367.63 | USA            |
|      10658 | QUICK         | 1997-09-05   |    364.15 | Germany        |
|      10657 | SAVEA         | 1997-09-04   |    352.69 | USA            |


## Q6: Orders not shipped yet in selected countries (IN + IS NULL)

Business question: Which pending orders to France, Spain or Italy need attention?

```sql
SELECT order_id,
       customer_id,
       order_date,
       required_date,
       ship_country
FROM orders
WHERE ship_country IN ('France', 'Spain', 'Italy')
  AND shipped_date IS NULL
ORDER BY required_date ASC;
```

**Rows returned: 3**

|   order_id | customer_id   | order_date   | required_date   | ship_country   |
|-----------:|:--------------|:-------------|:----------------|:---------------|
|      11051 | LAMAI         | 1998-04-27   | 1998-05-25      | France         |
|      11062 | REGGC         | 1998-04-30   | 1998-05-28      | Italy          |
|      11076 | BONAP         | 1998-05-06   | 1998-06-03      | France         |


## Q7: Cities that start with 'S' (LIKE pattern + multi-column ORDER BY)

Business question: Which orders go to cities beginning with S?

```sql
SELECT order_id,
       ship_city,
       ship_country,
       freight
FROM orders
WHERE ship_city LIKE 'S%'
ORDER BY ship_city ASC, freight DESC
LIMIT 15;
```

**Rows returned: 15**

|   order_id | ship_city     | ship_country   |   freight |
|-----------:|:--------------|:---------------|----------:|
|      10353 | Salzburg      | Austria        |    360.63 |
|      10530 | Salzburg      | Austria        |    339.22 |
|      10392 | Salzburg      | Austria        |    122.46 |
|      10747 | Salzburg      | Austria        |    117.33 |
|      10686 | Salzburg      | Austria        |     96.5  |
|      11053 | Salzburg      | Austria        |     53.05 |
|      10597 | Salzburg      | Austria        |     35.12 |
|      10427 | Salzburg      | Austria        |     31.29 |
|      10844 | Salzburg      | Austria        |     25.22 |
|      10489 | Salzburg      | Austria        |      5.29 |
|      10490 | San Cristóbal | Venezuela      |    210.19 |
|      10395 | San Cristóbal | Venezuela      |    184.41 |
|      10641 | San Cristóbal | Venezuela      |    179.61 |
|      11055 | San Cristóbal | Venezuela      |    120.92 |
|      10957 | San Cristóbal | Venezuela      |    105.36 |


## Q8: Bulk discounted order lines (WHERE with two numeric conditions)

Business question: Which lines combined a big quantity with a discount?

```sql
SELECT order_id,
       product_id,
       unit_price,
       quantity,
       discount
FROM order_details
WHERE quantity >= 50
  AND discount > 0
ORDER BY quantity DESC, discount DESC
LIMIT 15;
```

**Rows returned: 15**

|   order_id |   product_id |   unit_price |   quantity |   discount |
|-----------:|-------------:|-------------:|-----------:|-----------:|
|      10764 |           39 |        18    |        130 |       0.1  |
|      10595 |           61 |        28.5  |        120 |       0.25 |
|      10398 |           55 |        19.2  |        120 |       0.1  |
|      10451 |           55 |        19.2  |        120 |       0.1  |
|      10776 |           51 |        53    |        120 |       0.05 |
|      10894 |           75 |         7.75 |        120 |       0.05 |
|      11030 |            2 |        19    |        100 |       0.25 |
|      11030 |           59 |        55    |        100 |       0.25 |
|      10588 |           42 |        14    |        100 |       0.2  |
|      10549 |           45 |         9.5  |        100 |       0.15 |
|      10854 |           10 |        31    |        100 |       0.15 |
|      10452 |           44 |        15.5  |        100 |       0.05 |
|      10991 |           76 |        18    |         90 |       0.2  |
|      10440 |           61 |        22.8  |         90 |       0.15 |
|      11008 |           34 |        14    |         90 |       0.05 |


## Q9: Top 10 order lines by revenue (calculated column + alias + ORDER BY alias)

Business question: Which single order lines earned the most after discount?

```sql
SELECT order_id,
       product_id,
       unit_price,
       quantity,
       discount,
       ROUND(unit_price * quantity * (1 - discount), 2) AS line_total
FROM order_details
ORDER BY line_total DESC
LIMIT 10;
```

**Rows returned: 10**

|   order_id |   product_id |   unit_price |   quantity |   discount |   line_total |
|-----------:|-------------:|-------------:|-----------:|-----------:|-------------:|
|      10981 |           38 |       263.5  |         60 |       0    |     15810    |
|      10865 |           38 |       263.5  |         60 |       0.05 |     15019.5  |
|      10417 |           38 |       210.8  |         50 |       0    |     10540    |
|      10889 |           38 |       263.5  |         40 |       0    |     10540    |
|      10897 |           29 |       123.79 |         80 |       0    |      9903.2  |
|      10353 |           38 |       210.8  |         50 |       0.2  |      8432    |
|      10424 |           38 |       210.8  |         49 |       0.2  |      8263.36 |
|      10540 |           38 |       263.5  |         30 |       0    |      7905    |
|      10817 |           38 |       263.5  |         30 |       0    |      7905    |
|      10816 |           38 |       263.5  |         30 |       0.05 |      7509.75 |


## Q10: Orders shipped after the required date (comparing two columns)

Business question: Which orders were delivered late, most recent first?

```sql
SELECT order_id,
       customer_id,
       required_date,
       shipped_date,
       ship_country
FROM orders
WHERE shipped_date > required_date
ORDER BY shipped_date DESC
LIMIT 15;
```

**Rows returned: 15**

|   order_id | customer_id   | required_date   | shipped_date   | ship_country   |
|-----------:|:--------------|:----------------|:---------------|:---------------|
|      10970 | BOLID         | 1998-04-07      | 1998-04-24     | Spain          |
|      10924 | BERGS         | 1998-04-01      | 1998-04-08     | Sweden         |
|      10927 | LACOR         | 1998-04-02      | 1998-04-08     | France         |
|      10960 | HILAA         | 1998-04-02      | 1998-04-08     | Venezuela      |
|      10847 | SAVEA         | 1998-02-05      | 1998-02-10     | USA            |
|      10827 | BONAP         | 1998-01-26      | 1998-02-06     | France         |
|      10816 | GREAL         | 1998-02-03      | 1998-02-04     | USA            |
|      10828 | RANCH         | 1998-01-27      | 1998-02-04     | Argentina      |
|      10807 | FRANS         | 1998-01-28      | 1998-01-30     | Italy          |
|      10777 | GOURL         | 1997-12-29      | 1998-01-21     | Brazil         |
|      10779 | MORGK         | 1998-01-13      | 1998-01-14     | Germany        |
|      10749 | ISLAT         | 1997-12-18      | 1997-12-19     | UK             |
|      10726 | EASTC         | 1997-11-17      | 1997-12-05     | UK             |
|      10727 | REGGC         | 1997-12-01      | 1997-12-05     | Italy          |
|      10709 | GOURL         | 1997-11-14      | 1997-11-20     | Brazil         |

