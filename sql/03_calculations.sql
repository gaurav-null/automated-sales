-- ============================================================
-- Calculations: Views & Stored Calculations for Payout & Attainment
-- Demonstrates: CTEs, Window Functions (SUM OVER PARTITION BY),
--               CASE statements, and tiered commission logic.
-- ============================================================

-- 1. Monthly Rep Summary with Quota Attainment & Commission Payout
--    Model: "Flat tiered rate" — the rep's total monthly sales fall into
--    one commission band (Base / Growth / Accelerator), and that single
--    rate is applied to the full month's sales.
DROP VIEW IF EXISTS vw_monthly_rep_summary;
CREATE VIEW vw_monthly_rep_summary AS
WITH
-- CTE 1: Aggregate closed sales per rep per month
monthly_sales AS (
    SELECT
        s.rep_id,
        DATE_TRUNC('month', s.deal_date) AS period_month,
        SUM(s.amount) AS total_sales_amount
    FROM fact_sales s
    GROUP BY s.rep_id, DATE_TRUNC('month', s.deal_date)
),
-- CTE 2: Join monthly sales with quotas to compute attainment percentage
monthly_with_quotas AS (
    SELECT
        ms.rep_id,
        ms.period_month,
        ms.total_sales_amount,
        q.quota_amount,
        CASE
            WHEN q.quota_amount IS NULL OR q.quota_amount = 0 THEN 0
            ELSE (ms.total_sales_amount / q.quota_amount) * 100.0
        END AS attainment_pct
    FROM monthly_sales ms
    LEFT JOIN dim_quotas q
        ON ms.rep_id = q.rep_id
       AND ms.period_month = q.period_month
),
-- CTE 3: Determine which commission tier the total sales fall into
tier_calc AS (
    SELECT
        mwr.*,
        t.tier_name,
        t.commission_pct
    FROM monthly_with_quotas mwr
    LEFT JOIN dim_commission_tiers t
        ON mwr.total_sales_amount >= t.min_amount
       AND (t.max_amount IS NULL OR mwr.total_sales_amount <= t.max_amount)
)
-- Final: compute the commission payout for the month
SELECT
    tc.rep_id,
    r.rep_name,
    tc.period_month,
    tc.quota_amount,
    tc.total_sales_amount,
    tc.attainment_pct,
    tc.commission_pct,
    tc.total_sales_amount * (tc.commission_pct / 100.0) AS commission_payout,
    tc.tier_name
FROM tier_calc tc
LEFT JOIN dim_reps r ON tc.rep_id = r.rep_id
ORDER BY tc.period_month, tc.rep_id;


-- 2. Running Total Sales per Rep using Window Functions
--    Demonstrates: SUM() OVER (PARTITION BY rep_id ORDER BY period_month)
DROP VIEW IF EXISTS vw_rep_running_totals;
CREATE VIEW vw_rep_running_totals AS
WITH
-- Step 1: Aggregate sales to monthly totals first (GROUP BY)
monthly_totals AS (
    SELECT
        rep_id,
        DATE_TRUNC('month', deal_date) AS period_month,
        SUM(amount) AS monthly_sales
    FROM fact_sales
    GROUP BY rep_id, DATE_TRUNC('month', deal_date)
),
-- Step 2: Apply the window function on the aggregated result
rep_running AS (
    SELECT
        rep_id,
        period_month,
        monthly_sales,
        SUM(monthly_sales) OVER (
            PARTITION BY rep_id
            ORDER BY period_month
        ) AS running_total
    FROM monthly_totals
)
SELECT * FROM rep_running ORDER BY rep_id, period_month;
