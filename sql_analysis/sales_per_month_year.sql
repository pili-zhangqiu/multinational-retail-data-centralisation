-- Get the month and year combinations with the highest sales
-- Ordered from highest to lowest sales
SELECT ROUND(CAST(SUM(orders.product_quantity * products.product_price_in_gbp) AS numeric),2) AS total_sales,
    dates.year AS "year",
    dates.month AS "month"
FROM orders_table AS orders
    JOIN dim_date_times AS dates ON orders.date_uuid = dates.date_uuid
    JOIN dim_products AS products ON orders.product_code = products.product_code
GROUP BY dates.year,
    dates.month
ORDER BY total_sales DESC
LIMIT 10;