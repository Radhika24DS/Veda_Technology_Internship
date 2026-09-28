# Interview Questions – Task 21

### 1. What does SELECT do?
`SELECT` retrieves data from one or more tables. It specifies which columns to return (or `*` for all), and it can also return calculated columns, aliases (`AS`) and unique values (`DISTINCT`). It only reads data; it does not change the table.

```sql
SELECT order_id, freight FROM orders;
```

### 2. What does ORDER BY do?
`ORDER BY` sorts the result set by one or more columns, ascending (`ASC`, the default) or descending (`DESC`). It is applied after `WHERE` and is the last step before `LIMIT`. Without it, SQL guarantees no particular row order.

```sql
SELECT order_id, freight FROM orders ORDER BY freight DESC;
```

### Bonus: what does WHERE do?
`WHERE` filters rows before they are returned, using conditions such as `=`, `>`, `BETWEEN`, `IN`, `LIKE` and `IS NULL`. Use `IS NULL`, never `= NULL`, to find missing values.
