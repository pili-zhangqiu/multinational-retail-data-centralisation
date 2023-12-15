-- Get the total sales for online and offline purchases
SELECT COUNT(*) AS numbers_of_sales,
    SUM(orders.product_quantity) AS product_quantity_count,
    CASE 
        WHEN stores.store_type = 'Web Portal' THEN 'Web'
        ELSE 'Offline'
    END AS location
FROM orders_table AS orders
    JOIN dim_store_details AS stores ON orders.store_code = stores.store_code
    JOIN dim_products AS products ON orders.product_code = products.product_code
GROUP BY location;