
SELECT
    a.country,
    a.subregion,
    COUNT(DISTINCT o.opportunity_id)    AS n_opps,
    COALESCE(SUM(o.arr_potential), 0)   AS open_pipeline
FROM accounts a
LEFT JOIN opportunities o ON a.account_id = o.account_id
    AND o.stage NOT IN ('Closed Won', 'Closed Lost')
GROUP BY a.country, a.subregion
ORDER BY open_pipeline DESC
