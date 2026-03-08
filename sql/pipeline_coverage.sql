
WITH rep_quotas AS (
    SELECT
        subregion,
        SUM(quota_usd) AS total_quota
    FROM reps
    WHERE subregion != 'Regional'
    GROUP BY subregion
),
opp_pipeline AS (
    SELECT
        a.subregion,
        COALESCE(SUM(o.arr_potential)
            FILTER (WHERE o.stage NOT IN ('Closed Won','Closed Lost')), 0) AS open_pipeline,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage NOT IN ('Closed Won','Closed Lost'))      AS open_opps,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage = 'Closed Won')                           AS closed_won,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage = 'Closed Lost')                          AS closed_lost
    FROM opportunities o
    JOIN accounts a ON o.account_id = a.account_id
    GROUP BY a.subregion
)
SELECT
    r.subregion,
    r.total_quota,
    p.open_pipeline,
    p.open_pipeline / r.total_quota * 100                  AS coverage_ratio,
    p.open_opps,
    p.closed_won,
    p.closed_lost,
    ROUND(p.closed_won * 100.0 / NULLIF(p.closed_won + p.closed_lost, 0), 1) AS win_rate_pct
FROM rep_quotas r
JOIN opp_pipeline p ON r.subregion = p.subregion
ORDER BY coverage_ratio DESC
