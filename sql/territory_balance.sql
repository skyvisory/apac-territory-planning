
SELECT
    r.rep_id,
    r.rep_name,
    r.subregion,
    r.segment_focus,
    r.quota_usd,
    COUNT(DISTINCT a.account_id)        AS assigned_accounts,
    COALESCE(SUM(a.estimated_arr), 0)   AS territory_arr
FROM reps r
LEFT JOIN assignments asgn ON r.rep_id = asgn.rep_id
    AND asgn.coverage_status = 'Assigned'
LEFT JOIN accounts a ON asgn.account_id = a.account_id
WHERE r.subregion != 'Regional'
GROUP BY r.rep_id, r.rep_name, r.subregion, r.segment_focus, r.quota_usd
ORDER BY territory_arr DESC
