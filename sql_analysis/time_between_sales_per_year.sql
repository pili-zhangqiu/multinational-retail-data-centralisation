-- Get average time between sales per year
WITH TIME_BETWEEN_SALES AS (
    SELECT dates.year,
        LEAD(
            TO_TIMESTAMP(
                dates.year || '-' || dates.month || '-' || dates.day || ' ' || dates.timestamp,
                'YYYY-MM-DD HH24:MI:SS.FF'
            )
        ) OVER (
            PARTITION BY dates.year
            ORDER BY TO_TIMESTAMP(
                    dates.year || '-' || dates.month || '-' || dates.day || ' ' || dates.timestamp,
                    'YYYY-MM-DD HH24:MI:SS.FF'
                )
        ) - TO_TIMESTAMP(
            dates.year || '-' || dates.month || '-' || dates.day || ' ' || dates.timestamp,
            'YYYY-MM-DD HH24:MI:SS.FF'
        ) AS time_between_sales
    FROM orders_table orders
    JOIN dim_date_times dates ON orders.date_uuid = dates.date_uuid
),
AVG_TIME_BETWEEN_SALES AS (
    SELECT CAST(year AS int),
        AVG(time_between_sales) AS avg_time_between_sales
    FROM TIME_BETWEEN_SALES
    GROUP BY year
)

SELECT year,
    avg_time_between_sales
FROM AVG_TIME_BETWEEN_SALES
ORDER BY EXTRACT(
        hours
        FROM avg_time_between_sales
    ),
    EXTRACT(
        minutes
        FROM avg_time_between_sales
    ),
    EXTRACT(
        seconds
        FROM avg_time_between_sales
    ),
    EXTRACT(
        milliseconds
        FROM avg_time_between_sales
    ) % 1000