
SELECT
    a.account_id,
    a.company_name,
    a.country,
    a.subregion,
    a.industry,
    a.employee_band,
    a.estimated_arr,
    a.segment,
    a.account_status,
    asgn.coverage_status,
    asgn.engagement_status,
    COALESCE(asgn.last_activity_date, 'Never') AS last_activity_date
FROM accounts a
JOIN assignments asgn ON a.account_id = asgn.account_id
WHERE a.is_customer = 0
  AND (
      asgn.coverage_status = 'Unassigned'
      OR asgn.engagement_status IN ('Stale', 'No Coverage')
  )
