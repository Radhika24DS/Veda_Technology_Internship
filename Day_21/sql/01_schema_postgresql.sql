-- PostgreSQL setup for Task 21 (Northwind orders + order_details)
-- Run from the project root in psql:  \i sql/01_schema_postgresql.sql
DROP TABLE IF EXISTS order_details;
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id         INT PRIMARY KEY,
    customer_id      VARCHAR(5)   NOT NULL,
    employee_id      INT          NOT NULL,
    order_date       DATE         NOT NULL,
    required_date    DATE         NOT NULL,
    shipped_date     DATE,                    -- NULL = not shipped yet
    ship_via         INT          NOT NULL,
    freight          NUMERIC(8,2) NOT NULL,
    ship_name        VARCHAR(100) NOT NULL,
    ship_address     VARCHAR(150) NOT NULL,
    ship_city        VARCHAR(60)  NOT NULL,
    ship_region      VARCHAR(40),             -- NULL = not applicable
    ship_postal_code VARCHAR(15),
    ship_country     VARCHAR(30)  NOT NULL,
    days_to_ship     INT,
    shipped_late     SMALLINT     NOT NULL
);

CREATE TABLE order_details (
    order_id   INT           NOT NULL REFERENCES orders(order_id),
    product_id INT           NOT NULL,
    unit_price NUMERIC(8,2)  NOT NULL,
    quantity   INT           NOT NULL,
    discount   NUMERIC(3,2)  NOT NULL,
    line_total NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

-- psql client-side copy (empty unquoted field is read as NULL in CSV mode)
\copy orders FROM 'data/orders_clean.csv' WITH (FORMAT csv, HEADER true)
\copy order_details FROM 'data/order_details_clean.csv' WITH (FORMAT csv, HEADER true)

SELECT COUNT(*) AS orders_loaded FROM orders;          -- expect 830
SELECT COUNT(*) AS order_details_loaded FROM order_details;  -- expect 2155
