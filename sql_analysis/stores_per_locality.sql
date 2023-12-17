-- Get the total number of stores in each locality, from highest to lowest
-- Only return the highest 7
SELECT locality AS locality,
    COUNT (*) AS total_no_stores
FROM dim_store_details
GROUP BY locality
ORDER BY total_no_stores DESC
LIMIT 7;