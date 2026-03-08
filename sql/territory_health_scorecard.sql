
WITH active_customers AS (
    SELECT *
    FROM customers
    WHERE contract_end > '2025-03-01'
       OR renewal_flag = 1
),
rep_quota AS (
    SELECT
        r.rep_id,
        r.rep_name,
        r.subregion,
        r.segment_focus,
        r.quota_usd,
        r.max_accounts
    FROM reps r
    WHERE r.subregion != 'Regional'
),
rep_accounts AS (
    SELECT
        r.rep_id,
        COUNT(DISTINCT asgn.account_id)     AS assigned_accounts,
        SUM(a.estimated_arr)                AS territory_arr
    FROM rep_quota r
    LEFT JOIN assignments asgn ON r.rep_id = asgn.rep_id
        AND asgn.coverage_status = 'Assigned'
    LEFT JOIN accounts a ON asgn.account_id = a.account_id
    GROUP BY r.rep_id
),
rep_revenue AS (
    SELECT
        r.rep_id,
        COALESCE(SUM(c.arr), 0)             AS actual_arr,
        COUNT(DISTINCT c.customer_id)        AS n_customers
    FROM rep_quota r
    LEFT JOIN active_customers c ON r.rep_id = c.rep_id
    GROUP BY r.rep_id
),
rep_pipeline AS (
    SELECT
        r.rep_id,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage NOT IN ('Closed Won','Closed Lost'))
                                            AS open_opps,
        COALESCE(SUM(o.arr_potential)
            FILTER (WHERE o.stage NOT IN ('Closed Won','Closed Lost')), 0)
                                            AS open_pipeline,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage = 'Closed Won')
                                            AS closed_won,
        COUNT(DISTINCT o.opportunity_id)
            FILTER (WHERE o.stage = 'Closed Lost')
                                            AS closed_lost
    FROM rep_quota r
    LEFT JOIN opportunities o ON r.rep_id = o.rep_id
    GROUP BY r.rep_id
)
SELECT
    q.rep_name,
    q.subregion,
    q.segment_focus                                                     AS segment,
    q.quota_usd                                                         AS quota,
    ra.assigned_accounts,
    q.max_accounts,
    ROUND(ra.assigned_accounts * 100.0 / q.max_accounts, 1)            AS load_pct,
    ROUND(ra.territory_arr, 0)                                          AS territory_arr,
    COALESCE(rr.actual_arr, 0)                                          AS actual_arr,
    ROUND(COALESCE(rr.actual_arr, 0) / q.quota_usd * 100, 1)           AS attainment_pct,
    rr.n_customers,
    rp.open_opps,
    ROUND(rp.open_pipeline, 0)                                          AS open_pipeline,
    ROUND(rp.open_pipeline / NULLIF(q.quota_usd, 0) * 100, 1)          AS pipeline_coverage_pct,
    ROUND(
        rp.closed_won * 100.0 / NULLIF(rp.closed_won + rp.closed_lost, 0)
    , 1)                                                                AS win_rate_pct
FROM rep_quota q
LEFT JOIN rep_accounts  ra ON q.rep_id = ra.rep_id
LEFT JOIN rep_revenue   rr ON q.rep_id = rr.rep_id
LEFT JOIN rep_pipeline  rp ON q.rep_id = rp.rep_id
ORDER BY attainment_pct DESC NULLS LAST
