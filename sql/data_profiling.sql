/*==== Create table =====*/
CREATE TABLE public.hillstrom (
    recency INTEGER,
    history_segment TEXT,
    history NUMERIC(12,2),
    mens INTEGER,
    womens INTEGER,
    zip_code TEXT,
    newbie INTEGER,
    channel TEXT,
    segment TEXT,
    visit INTEGER,
    conversion INTEGER,
    spend NUMERIC(12,2)
);

-- check table schema
SELECT
    column_name,
    data_type,
    ordinal_position
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'hillstrom'
ORDER BY ordinal_position;

-- import data manually

-- confirm total rows=64,000
SELECT COUNT(*) AS total_rows
FROM public.hillstrom;

-- confirm total treatment segment = total rows
SELECT
    segment,
    COUNT(*) AS customers
FROM public.hillstrom
GROUP BY segment
ORDER BY segment;

-- confirm import status 
SELECT *
FROM public.hillstrom
LIMIT 5;

/*==== Data Profiling ====*/
-- confirm 0 missing value of 3 key columns
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE segment IS NULL)
        AS missing_segment,
    COUNT(*) FILTER (WHERE spend IS NULL)
        AS missing_spend,
    COUNT(*) FILTER (WHERE history IS NULL)
        AS missing_history
FROM public.hillstrom;

-- confirm 0 missing value of all 12 columns
SELECT
    COUNT(*) AS total_rows,
    COUNT(*) FILTER (WHERE recency IS NULL) AS missing_recency,
    COUNT(*) FILTER (WHERE history_segment IS NULL) AS missing_history_segment,
    COUNT(*) FILTER (WHERE history IS NULL) AS missing_history,
    COUNT(*) FILTER (WHERE mens IS NULL) AS missing_mens,
    COUNT(*) FILTER (WHERE womens IS NULL) AS missing_womens,
    COUNT(*) FILTER (WHERE zip_code IS NULL) AS missing_zip_code,
    COUNT(*) FILTER (WHERE newbie IS NULL) AS missing_newbie,
    COUNT(*) FILTER (WHERE channel IS NULL) AS missing_channel,
    COUNT(*) FILTER (WHERE segment IS NULL) AS missing_segment,
    COUNT(*) FILTER (WHERE visit IS NULL) AS missing_visit,
    COUNT(*) FILTER (WHERE conversion IS NULL) AS missing_conversion,
    COUNT(*) FILTER (WHERE spend IS NULL) AS missing_spend
FROM public.hillstrom;

-- Validity check

-- cofirm of binary columns
SELECT
    COUNT(*) FILTER (
        WHERE mens NOT IN (0, 1)
    ) AS invalid_mens,

    COUNT(*) FILTER (
        WHERE womens NOT IN (0, 1)
    ) AS invalid_womens,

    COUNT(*) FILTER (
        WHERE newbie NOT IN (0, 1)
    ) AS invalid_newbie,

    COUNT(*) FILTER (
        WHERE visit NOT IN (0, 1)
    ) AS invalid_visit,

    COUNT(*) FILTER (
        WHERE conversion NOT IN (0, 1)
    ) AS invalid_conversion
FROM public.hillstrom;

/*-- Numerical range check
-- output as 'check-numerical range'
-- findings: 99.1% of customers had 0 spend.
-- impact: 
	1.average of spend may highly impacted by few outliers. 
	2.Estimation of  Incremental Spend can be unprecise. 
	3.Customers had 0 spend should retain in denominator.
*/
SELECT
    MIN(recency) AS min_recency,
    MAX(recency) AS max_recency,

    MIN(history) AS min_history,
    MAX(history) AS max_history,

    MIN(spend) AS min_spend,
    MAX(spend) AS max_spend,

    COUNT(*) FILTER (
        WHERE recency < 0
    ) AS negative_recency,

    COUNT(*) FILTER (
        WHERE history < 0
    ) AS negative_history,

    COUNT(*) FILTER (
        WHERE spend < 0
    ) AS negative_spend,

    COUNT(*) FILTER (
        WHERE spend = 0
    ) AS zero_spend
FROM public.hillstrom;

/* Check consistency of Conversion and Spend
*/
SELECT
    conversion,
    CASE
        WHEN spend = 0 THEN 'Zero Spend'
        WHEN spend > 0 THEN 'Positive Spend'
    END AS spend_status,
    COUNT(*) AS customers
FROM public.hillstrom
GROUP BY conversion, spend_status
ORDER BY conversion, spend_status;

/*Check Spend Distribution
-- output is saved as spend_distribution
-- findings: 
	Spend is heavily zero-inflated and right-skewed, 
	with a small fraction of positive spenders pulling up the mean.
*/
SELECT
    ROUND(AVG(spend), 2) AS avg_spend_all,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spend)
        AS median_spend_all,

    ROUND(
        AVG(spend) FILTER (WHERE spend > 0),
        2
    ) AS avg_spend_buyers,

    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY spend)
        FILTER (WHERE spend > 0)
        AS median_spend_buyers,

    ROUND(STDDEV_SAMP(spend), 2) AS stddev_spend
FROM public.hillstrom;

/* Check Treatment Group Baseline Balance
-- output is saved as 'segment_baseline_balance'
-- findings: 
	Based on the examined pre-treatment characteristics, 
	the three experimental groups appear reasonably balanced, 
	with no substantial baseline differences observed.
*/
SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(AVG(history), 2) AS avg_history,
    ROUND(AVG(recency), 2) AS avg_recency,
    ROUND(AVG(newbie::NUMERIC), 4) AS newbie_rate,
    ROUND(AVG(mens::NUMERIC), 4) AS mens_rate,
    ROUND(AVG(womens::NUMERIC), 4) AS womens_rate
FROM public.hillstrom
GROUP BY segment
ORDER BY segment;

/* Experimental Baseline Table
-- purpose: Compare the raw performance across the three experimental groups to establish the baseline for calculating KQ1 Incremental Effects.
-- Descriptive statistics by randomized treatment group
-- output is saved as'experimental_baseline'
-- findings: 

Men's Email showed the highest observed average spend per randomized customer (1.4226), 
conversion rate (1.25%), and visit rate (18.28%), 
followed by Women's Email and No Email. 
Given the randomized experimental design, 
these differences provide initial estimates of treatment effects, 
but statistical uncertainty must be assessed before drawing firm conclusions about effectiveness.

Hypothesis: Differences in promoted product mix or price points may contribute to the observed spending differences between email variants. 
Campaign content and transaction-level data would be required to investigate this mechanism.
*/
SELECT
    segment,
    COUNT(*) AS customers,

    ROUND(AVG(spend), 4)
        AS avg_spend_per_customer,

    ROUND(AVG(conversion::NUMERIC), 4)
        AS conversion_rate,

    ROUND(AVG(visit::NUMERIC), 4)
        AS visit_rate,

    ROUND(SUM(spend), 2)
        AS total_spend

FROM public.hillstrom
GROUP BY segment
ORDER BY segment;
