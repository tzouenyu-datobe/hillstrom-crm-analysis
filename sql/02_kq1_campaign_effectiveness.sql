/*==KQ1.campaign_effectiveness*/


-- KQ1 | Step 1: Incremental Spend
-- Primary KPI: Spend per randomized customer
-- All customers are included, including zero spend.
-- output is saved as 'incremental_spend_by_segment'
WITH group_spend AS (
    SELECT
        segment,
        COUNT(*) AS customers,
        AVG(spend) AS avg_spend
    FROM public.hillstrom
    GROUP BY segment
)

SELECT
    treatment.segment AS treatment_group,
    comparison.segment AS comparison_group,

    treatment.customers AS treatment_n,
    comparison.customers AS comparison_n,

    ROUND(treatment.avg_spend, 4)
        AS treatment_avg_spend,

    ROUND(comparison.avg_spend, 4)
        AS comparison_avg_spend,

    ROUND(
        treatment.avg_spend - comparison.avg_spend,
        4
    ) AS spend_difference

FROM group_spend AS treatment
JOIN group_spend AS comparison
    ON (
        treatment.segment = 'Mens E-Mail'
        AND comparison.segment = 'No E-Mail'
    )
    OR (
        treatment.segment = 'Womens E-Mail'
        AND comparison.segment = 'No E-Mail'
    )
    OR (
        treatment.segment = 'Womens E-Mail'
        AND comparison.segment = 'Mens E-Mail'
    )

ORDER BY
    treatment.segment,
    comparison.segment;


-- KQ1 | Step 2.1: Spend Variability by Treatment Group
-- Inputs for confidence interval estimation: caculate standard deviations
-- output is saved as 'SD by treatment group'
SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(AVG(spend), 4) AS avg_spend,
    ROUND(STDDEV_SAMP(spend), 4) AS sd_spend,
    COUNT(*) FILTER (WHERE spend > 0)
        AS positive_spend_customers
FROM public.hillstrom
GROUP BY segment
ORDER BY segment;


-- KQ1 | Step 2.2: Spend Uplift and 95% CI
-- Independent-group difference in means
-- Normal-approximation confidence interval
-- output is saved as 'spend_upflift_under_95%_CI'
WITH group_stats AS (
    SELECT
        segment,
        COUNT(*) AS n,
        AVG(spend) AS mean_spend,
        STDDEV_SAMP(spend) AS sd_spend
    FROM public.hillstrom
    GROUP BY segment
),

comparisons AS (
    SELECT
        treatment.segment AS treatment_group,
        comparison.segment AS comparison_group,

        treatment.mean_spend - comparison.mean_spend
            AS spend_difference,

        SQRT(
            POWER(treatment.sd_spend, 2) / treatment.n
            + POWER(comparison.sd_spend, 2) / comparison.n
        ) AS se_difference

    FROM group_stats AS treatment
    JOIN group_stats AS comparison
        ON (
            treatment.segment = 'Mens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'Mens E-Mail'
        )
)

SELECT
    treatment_group,
    comparison_group,

    ROUND(spend_difference, 4) AS spend_difference,
    ROUND(se_difference, 4) AS standard_error,

    ROUND(
        spend_difference - 1.96 * se_difference,
        4
    ) AS ci_lower,

    ROUND(
        spend_difference + 1.96 * se_difference,
        4
    ) AS ci_upper

FROM comparisons
ORDER BY treatment_group, comparison_group;


-- KQ1 | Step 3.1: Conversion & Visit Uplift
-- Absolute differences in percentage points (pp)
-- output is saved as 'conversion&visit_uplift_by_group'
WITH group_metrics AS (
    SELECT
        segment,
        COUNT(*) AS customers,
        AVG(conversion::NUMERIC) AS conversion_rate,
        AVG(visit::NUMERIC) AS visit_rate
    FROM public.hillstrom
    GROUP BY segment
)

SELECT
    treatment.segment AS treatment_group,
    comparison.segment AS comparison_group,

    ROUND(
        100 * (treatment.conversion_rate
             - comparison.conversion_rate), 4
    ) AS conversion_uplift_pp,

    ROUND(
        100 * (treatment.visit_rate
             - comparison.visit_rate), 4
    ) AS visit_uplift_pp

FROM group_metrics AS treatment
JOIN group_metrics AS comparison
    ON (
        treatment.segment = 'Mens E-Mail'
        AND comparison.segment = 'No E-Mail'
    )
    OR (
        treatment.segment = 'Womens E-Mail'
        AND comparison.segment = 'No E-Mail'
    )
    OR (
        treatment.segment = 'Womens E-Mail'
        AND comparison.segment = 'Mens E-Mail'
    )

ORDER BY treatment.segment, comparison.segment;


-- KQ1 | Step 3.2: Conversion Uplift 95% CI
-- Normal approximation for independent proportions
-- output is saved as 'conversion_uplift_95%_CI'
/* findings: 
Under random assignment, both Men's (+0.6805 pp) and Women's (+0.3111 pp) Email campaigns achieved statistically significant conversion lifts over control. 
Men's Email significantly outperformed Women's Email by 0.3694 pp (95% CI: [0.1743, 0.5644]).
*/
WITH group_stats AS (
    SELECT
        segment,
        COUNT(*) AS n,
        AVG(conversion::NUMERIC) AS conversion_rate
    FROM public.hillstrom
    GROUP BY segment
),

comparisons AS (
    SELECT
        treatment.segment AS treatment_group,
        comparison.segment AS comparison_group,

        treatment.conversion_rate
            - comparison.conversion_rate AS rate_difference,

        SQRT(
            treatment.conversion_rate
                * (1 - treatment.conversion_rate)
                / treatment.n
            +
            comparison.conversion_rate
                * (1 - comparison.conversion_rate)
                / comparison.n
        ) AS se_difference

    FROM group_stats AS treatment
    JOIN group_stats AS comparison
        ON (
            treatment.segment = 'Mens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'Mens E-Mail'
        )
)

SELECT
    treatment_group,
    comparison_group,

    ROUND(100 * rate_difference, 4)
        AS conversion_uplift_pp,

    ROUND(100 * se_difference, 4)
        AS se_pp,

    ROUND(
        100 * (rate_difference - 1.96 * se_difference),
        4
    ) AS ci_lower_pp,

    ROUND(
        100 * (rate_difference + 1.96 * se_difference),
        4
    ) AS ci_upper_pp

FROM comparisons
ORDER BY treatment_group, comparison_group;



-- KQ1 | Step 3.3: Visit Uplift 95% CI
-- output is saved as 'visit_uplift_95%_CI'
WITH group_stats AS (
    SELECT
        segment,
        COUNT(*) AS n,
        AVG(visit::NUMERIC) AS visit_rate
    FROM public.hillstrom
    GROUP BY segment
),

comparisons AS (
    SELECT
        treatment.segment AS treatment_group,
        comparison.segment AS comparison_group,

        treatment.visit_rate - comparison.visit_rate
            AS rate_difference,

        SQRT(
            treatment.visit_rate
                * (1 - treatment.visit_rate) / treatment.n
            +
            comparison.visit_rate
                * (1 - comparison.visit_rate) / comparison.n
        ) AS se_difference

    FROM group_stats AS treatment
    JOIN group_stats AS comparison
        ON (
            treatment.segment = 'Mens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'No E-Mail'
        )
        OR (
            treatment.segment = 'Womens E-Mail'
            AND comparison.segment = 'Mens E-Mail'
        )
)

SELECT
    treatment_group,
    comparison_group,

    ROUND(100 * rate_difference, 4)
        AS visit_uplift_pp,

    ROUND(100 * se_difference, 4)
        AS se_pp,

    ROUND(
        100 * (rate_difference - 1.96 * se_difference),
        4
    ) AS ci_lower_pp,

    ROUND(
        100 * (rate_difference + 1.96 * se_difference),
        4
    ) AS ci_upper_pp

FROM comparisons
ORDER BY treatment_group, comparison_group;


-- KQ1 | Robustness Check: Export Spend Data
SELECT
    segment,
    spend
FROM public.hillstrom
ORDER BY segment;

