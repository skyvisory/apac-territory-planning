
SELECT
    a.country,
    a.subregion,
    COUNT(DISTINCT c.customer_id)   AS n_customers,
    COALESCE(SUM(c.arr), 0)         AS total_arr,
    COALESCE(AVG(c.arr), 0)         AS avg_arr
FROM accounts a
LEFT JOIN customers c ON a.account_id = c.account_id
GROUP BY a.country, a.subregion
ORDER BY total_arr DESC
