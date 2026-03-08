
WITH active_customers AS (
    SELECT * FROM customers
    WHERE contract_end > '2025-03-01' OR renewal_flag = 1
),
subregion_metrics AS (
    SELECT
        a.subregion,
        COUNT(DISTINCT a.account_id)                                        AS total_accounts,
        COUNT(DISTINCT CASE WHEN asgn.coverage_status = 'Assigned' 
            THEN a.account_id END)                                          AS assigned_accounts,
        COUNT(DISTINCT CASE WHEN asgn.coverage_status = 'Unassigned' 
            THEN a.account_id END)                                          AS unassigned_accounts,
        COUNT(DISTINCT CASE WHEN a.is_customer = 1 
            THEN a.account_id END)                                          AS n_customers,
        COALESCE(SUM(CASE WHEN a.is_customer = 1 
            THEN c.arr END), 0)                                             AS customer_arr,
        COUNT(DISTINCT r.rep_id)                                            AS n_reps,
        SUM(DISTINCT r.quota_usd)                                           AS total_quota,
        COALESCE(SUM(CASE WHEN o.stage NOT IN ('Closed Won','Closed Lost')
            THEN o.arr_potential END), 0)                                   AS open_pipeline,
        COUNT(DISTINCT CASE WHEN o.stage = 'Closed Won' 
            THEN o.opportunity_id END)                                      AS closed_won,
        COUNT(DISTINCT CASE WHEN o.stage = 'Closed Lost' 
            THEN o.opportunity_id END)                                      AS closed_lost
    FROM accounts a
    LEFT JOIN assignments asgn ON a.account_id = asgn.account_id
    LEFT JOIN active_customers c ON a.account_id = c.account_id
    LEFT JOIN reps r ON asgn.rep_id = r.rep_id AND r.subregion != 'Regional'
    LEFT JOIN opportunities o ON a.account_id = o.account_id
    GROUP BY a.subregion
)
SELECT
    subregion,
    total_accounts,
    assigned_accounts,
    unassigned_accounts,
    ROUND(unassigned_accounts * 100.0 / total_accounts, 1)              AS whitespace_pct,
    n_customers,
    ROUND(n_customers * 100.0 / total_accounts, 1)                      AS customer_rate_pct,
    ROUND(customer_arr, 0)                                               AS customer_arr,
    n_reps,
    ROUND(open_pipeline, 0)                                              AS open_pipeline,
    ROUND(closed_won * 100.0 / NULLIF(closed_won + closed_lost, 0), 1)  AS win_rate_pct
FROM subregion_metrics
ORDER BY customer_arr DESC NULLS LAST
