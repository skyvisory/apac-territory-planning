
SELECT
    r.rep_id,
    r.rep_name,
    r.subregion,
    r.segment_focus,
    r.quota_usd,
    COALESCE(SUM(c.arr), 0)                                AS actual_arr,
    COALESCE(SUM(c.arr), 0) / r.quota_usd * 100            AS quota_attainment_pct,
    COUNT(DISTINCT c.customer_id)                          AS n_customers
FROM reps r
LEFT JOIN customers c ON r.rep_id = c.rep_id
WHERE r.subregion != 'Regional'
GROUP BY r.rep_id, r.rep_name, r.subregion, r.segment_focus, r.quota_usd
ORDER BY quota_attainment_pct DESC
