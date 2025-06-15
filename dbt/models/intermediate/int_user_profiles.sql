{{ config(materialized='table') }}

SELECT
    userId AS user_id,
    any(username) AS username,
    any(country) AS country,
    countDistinct(visitorId) AS unique_visitors,
    count() AS total_searches,
    sum(numberOfResults) AS total_results_shown
FROM {{ ref('stg_searches') }}
WHERE userId IS NOT NULL
GROUP BY userId