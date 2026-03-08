
WITH tam AS (
    SELECT
        subregion,
        SUM(estimated_arr)                          AS tam_arr,
        COUNT(account_id)                           AS total_accounts
    FROM accounts
    GROUP BY subregion
),
actual AS (
    SELECT
        a.subregion,
        SUM(c.arr)                                  AS actual_arr,
        COUNT(DISTINCT c.customer_id)               AS n_customers
    FROM accounts a
    JOIN customers c ON a.account_id = c.account_id
    GROUP BY a.subregion
),
ws AS (
    SELECT
        a.subregion,
        SUM(a.estimated_arr)                        AS whitespace_arr,
        COUNT(a.account_id)                         AS whitespace_accounts
    FROM accounts a
    JOIN assignments asgn ON a.account_id = asgn.account_id
    WHERE a.is_customer = 0
      AND (asgn.coverage_status = 'Unassigned'
           OR asgn.engagement_status IN ('Stale', 'No Coverage'))
    GROUP BY a.subregion
)
SELECT
    t.subregion,
    t.tam_arr,
    COALESCE(a.actual_arr, 0)                       AS actual_arr,
    COALESCE(a.actual_arr, 0) / t.tam_arr * 100     AS penetration_pct,
    COALESCE(w.whitespace_arr, 0)                   AS whitespace_arr,
    COALESCE(w.whitespace_accounts, 0)              AS whitespace_accounts
FROM tam t
LEFT JOIN actual a ON t.subregion = a.subregion
LEFT JOIN ws w ON t.subregion = w.subregion
ORDER BY penetration_pct DESC
