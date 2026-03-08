
SELECT
    subregion,
    tier,
    priority_flag,
    COUNT(account_id)           AS n_accounts,
    ROUND(SUM(estimated_arr),0) AS total_arr,
    ROUND(AVG(estimated_arr),0) AS avg_arr
FROM ws_scored
GROUP BY subregion, tier, priority_flag
ORDER BY subregion, tier, priority_flag
