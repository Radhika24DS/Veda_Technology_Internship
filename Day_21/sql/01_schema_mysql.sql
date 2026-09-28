-- MySQL 8 setup for Task 21 (Northwind orders + order_details)
-- Needs: SET GLOBAL local_infile = 1;  and start client with  mysql --local-infile=1 -u root -p
CREATE DATABASE IF NOT EXISTS northwind_task21;
USE northwind_task21;
DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id         INT PRIMARY KEY,
    customer_id      VARCHAR(5)   NOT NULL,
    employee_id      INT          NOT NULL,
    order_date       DATE         NOT NULL,
    required_date    DATE         NOT NULL,
    shipped_date     DATE NULL,               -- NULL = not shipped yet
    ship_via         INT          NOT NULL,
    freight          DECIMAL(8,2) NOT NULL,
    ship_name        VARCHAR(100) NOT NULL,
    ship_address     VARCHAR(150) NOT NULL,
    ship_city        VARCHAR(60)  NOT NULL,
    ship_region      VARCHAR(40)  NULL,       -- NULL = not applicable
    ship_postal_code VARCHAR(15)  NULL,
    ship_country     VARCHAR(30)  NOT NULL,
    days_to_ship     INT NULL,
    shipped_late     TINYINT      NOT NULL
);

CREATE TABLE order_details (
    order_id   INT           NOT NULL,
    product_id INT           NOT NULL,
    unit_price DECIMAL(8,2)  NOT NULL,
    quantity   INT           NOT NULL,
    discount   DECIMAL(3,2)  NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Empty CSV fields must become NULL in MySQL, so load into variables and use NULLIF
LOAD DATA LOCAL INFILE 'data/orders_clean.csv' INTO TABLE orders
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES
(order_id, customer_id, employee_id, order_date, required_date, @shipped, ship_via, freight,
 ship_name, ship_address, ship_city, @region, @postal, ship_country, @days, shipped_late)
SET shipped_date     = NULLIF(@shipped, ''),
    ship_region      = NULLIF(@region, ''),
    ship_postal_code = NULLIF(@postal, ''),
    days_to_ship     = NULLIF(@days, '');

LOAD DATA LOCAL INFILE 'data/order_details_clean.csv' INTO TABLE order_details
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES;

SELECT COUNT(*) AS orders_loaded FROM orders;          -- expect 830
SELECT COUNT(*) AS order_details_loaded FROM order_details;  -- expect 2155
