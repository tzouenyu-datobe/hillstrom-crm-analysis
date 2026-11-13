/*=== KQ2 ====*/


-- KQ2 | Step 1.1
-- Historical spending segments: treatment-arm sample sizes
-- output is saved as 'sample_sizes_historical_spending'
SELECT
    history_segment,
    segment AS treatment,
    COUNT(*) AS n_customers
FROM public.hillstrom
GROUP BY
    history_segment,
    segment
ORDER BY
    history_segment,
    segment;
/* 
findings: 
While 400+ samples per arm seem sufficient, 
low conversion rates and highly zero-inflated spend mean high-value segments remain susceptible to noise. 
Therefore, interpretation must rely on confidence intervals rather than point estimates alone.
decisions:
Retain the seven categories and subsequently determine which findings are worth interpreting based on the uncertainty of the effect estimates.**
*/


-- KQ2 | Step 1.2
-- New vs existing customers: treatment-arm sample sizes
-- output is saved as 'sample_sizes_newbie'
SELECT
    newbie,
    segment AS treatment,
    COUNT(*) AS n_customers
FROM public.hillstrom
GROUP BY
    newbie,
    segment
ORDER BY
    newbie,
    segment;


-- KQ2 | Step 1.3
-- Historical merchandise purchase preference
-- output is saved as 'sample_size_purchase_preference'
WITH customer_preference AS (
    SELECT
        segment,
        CASE
            WHEN mens = 0 AND womens = 0 THEN 'Neither'
            WHEN mens = 1 AND womens = 0 THEN 'Mens Only'
            WHEN mens = 0 AND womens = 1 THEN 'Womens Only'
            WHEN mens = 1 AND womens = 1 THEN 'Both'
        END AS purchase_preference
    FROM public.hillstrom
)

SELECT
    purchase_preference,
    segment AS treatment,
    COUNT(*) AS n_customers
FROM customer_preference
GROUP BY
    purchase_preference,
    segment
ORDER BY
    purchase_preference,
    segment;
/*findingsL
In this dataset, all customers possess at least one historical merchandise purchase flag. 
The "Neither" category is not observed; therefore, subsequent analyses retain the three mutually exclusive segments: 
Both, Men's Only, and Women's Only.
*/



-- KQ2 | Step 2.1
-- Average spend by history segment and treatment
-- output is saved as: 'avg_spend_of_historical_segment'
SELECT
    history_segment,
    segment AS treatment,
    COUNT(*) AS n_customers,
    ROUND(AVG(spend)::numeric, 4) AS avg_spend,
    COUNT(*) FILTER (WHERE spend > 0) AS n_buyers
FROM public.hillstrom
GROUP BY
    history_segment,
    segment
ORDER BY
    history_segment,
    segment;



-- KQ2 | Step 2.2
-- History Segment: Incremental Spend Matrix
-- output is saved as 'segment_uplift_matrix'
WITH segment_summary AS (
    SELECT
        history_segment,
        segment AS treatment,
        COUNT(*) AS n_customers,
        AVG(spend) AS avg_spend
    FROM public.hillstrom
    GROUP BY
        history_segment,
        segment
),

segment_matrix AS (
    SELECT
        history_segment,

        MAX(avg_spend) FILTER (
            WHERE treatment = 'Mens E-Mail'
        ) AS mens_avg_spend,

        MAX(avg_spend) FILTER (
            WHERE treatment = 'Womens E-Mail'
        ) AS womens_avg_spend,

        MAX(avg_spend) FILTER (
            WHERE treatment = 'No E-Mail'
        ) AS control_avg_spend

    FROM segment_summary
    GROUP BY history_segment
)

SELECT
    history_segment,

    ROUND(
        (mens_avg_spend - control_avg_spend)::numeric, 4
    ) AS mens_uplift,

    ROUND(
        (womens_avg_spend - control_avg_spend)::numeric, 4
    ) AS womens_uplift,

    ROUND(
        (womens_avg_spend - mens_avg_spend)::numeric, 4
    ) AS womens_vs_mens

FROM segment_matrix
ORDER BY history_segment;



-- KQ2 | Step 2.3
-- History Segment: Spend uplift with 95% CI
-- Normal approximation, exploratory / unadjusted
-- output is saved as 'segment_uplift_with_ci'
WITH arm_stats AS (
    SELECT
        history_segment,
        segment,
        COUNT(*)::float8 AS n,
        AVG(spend) AS mean_spend,
        VAR_SAMP(spend) AS var_spend
    FROM public.hillstrom
    GROUP BY history_segment, segment
),

comparisons AS (
    SELECT
        a.history_segment,
        a.segment AS treatment,
        b.segment AS comparator,
        a.n AS n_treatment,
        b.n AS n_comparator,
        a.mean_spend - b.mean_spend AS uplift,
        SQRT(
            a.var_spend / a.n
            + b.var_spend / b.n
        ) AS se
    FROM arm_stats a
    JOIN arm_stats b
      ON a.history_segment = b.history_segment
    WHERE
        (a.segment = 'Mens E-Mail'
         AND b.segment = 'No E-Mail')
        OR
        (a.segment = 'Womens E-Mail'
         AND b.segment = 'No E-Mail')
        OR
        (a.segment = 'Womens E-Mail'
         AND b.segment = 'Mens E-Mail')
)

SELECT
    history_segment,
    treatment,
    comparator,
    n_treatment::integer,
    n_comparator::integer,
    ROUND(uplift::numeric, 4) AS uplift,
    ROUND(se::numeric, 4) AS se,
    ROUND((uplift - 1.96 * se)::numeric, 4) AS ci_lower,
    ROUND((uplift + 1.96 * se)::numeric, 4) AS ci_upper
FROM comparisons
ORDER BY
    history_segment,
    treatment,
    comparator;



-- KQ2 | Step 2.4
-- Newbie: Spend uplift point estimates
-- output is saved as 'newbie_uplift'
WITH arm_means AS (
    SELECT
        newbie,
        segment,
        COUNT(*) AS n_customers,
        AVG(spend) AS avg_spend
    FROM public.hillstrom
    GROUP BY newbie, segment
),

pivoted AS (
    SELECT
        newbie,
        MAX(avg_spend) FILTER (
            WHERE segment = 'Mens E-Mail'
        ) AS mens_spend,
        MAX(avg_spend) FILTER (
            WHERE segment = 'Womens E-Mail'
        ) AS womens_spend,
        MAX(avg_spend) FILTER (
            WHERE segment = 'No E-Mail'
        ) AS control_spend
    FROM arm_means
    GROUP BY newbie
)

SELECT
    newbie,
    ROUND((mens_spend - control_spend)::numeric, 4)
        AS mens_uplift,
    ROUND((womens_spend - control_spend)::numeric, 4)
        AS womens_uplift,
    ROUND((womens_spend - mens_spend)::numeric, 4)
        AS womens_vs_mens
FROM pivoted
ORDER BY newbie;



-- KQ2 | Step 2.5
-- Newbie: Spend uplift with 95% CI
-- Exploratory, unadjusted normal approximation
-- output is saved as 'newbie_uplift_with_CI'
WITH arm_stats AS (
    SELECT
        newbie,
        segment,
        COUNT(*)::float8 AS n,
        AVG(spend) AS mean_spend,
        VAR_SAMP(spend) AS var_spend
    FROM public.hillstrom
    GROUP BY newbie, segment
),

comparisons AS (
    SELECT
        a.newbie,
        a.segment AS treatment,
        b.segment AS comparator,
        a.n AS n_treatment,
        b.n AS n_comparator,
        a.mean_spend - b.mean_spend AS uplift,
        SQRT(
            a.var_spend / a.n
            + b.var_spend / b.n
        ) AS se
    FROM arm_stats a
    JOIN arm_stats b
      ON a.newbie = b.newbie
    WHERE
        (a.segment = 'Mens E-Mail'
         AND b.segment = 'No E-Mail')
        OR
        (a.segment = 'Womens E-Mail'
         AND b.segment = 'No E-Mail')
        OR
        (a.segment = 'Womens E-Mail'
         AND b.segment = 'Mens E-Mail')
)

SELECT
    newbie,
    treatment,
    comparator,
    ROUND(uplift::numeric, 4) AS uplift,
    ROUND(se::numeric, 4) AS se,
    ROUND((uplift - 1.96 * se)::numeric, 4) AS ci_lower,
    ROUND((uplift + 1.96 * se)::numeric, 4) AS ci_upper
FROM comparisons
ORDER BY newbie, treatment, comparator;

/*
Exploratory interaction analysis suggests that the incremental spend effect of Women's Email versus No Email is higher among new customers than existing customers (interaction = +0.6183, unadjusted 95% CI: [0.1072, 1.1294]). However, this finding has not been adjusted for multiple comparisons and requires further validation.
*/
