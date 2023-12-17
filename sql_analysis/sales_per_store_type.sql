-- Get the percentage of sales per store type, ordered from highest to lowest
WITH SALES AS (
    SELECT stores.store_type,
        ROUND(CAST(SUM(orders.product_quantity * products.product_price_in_gbp) AS numeric),2) AS total_sales
    FROM orders_table AS orders
    JOIN dim_store_details AS stores 
        ON orders.store_code = stores.store_code
    JOIN dim_products AS products 
        ON orders.product_code = products.product_code
    GROUP BY stores.store_type
),
GRAND_TOTAL_SALES AS (
    SELECT SUM(total_sales) AS grand_total_sales
    FROM SALES
)

SELECT sales.store_type,
    sales.total_sales AS total_sales,
    ROUND(((total_sales / total.grand_total_sales) * 100), 2) AS "percentage_total(%)"
FROM SALES AS sales,
    GRAND_TOTAL_SALES AS total
ORDER BY total_sales DESC;