{{ config(materialized='table') }}

SELECT
    keyword,
    COUNT(*) AS total_occurrences,
    MIN(datetime) AS first_seen,
    MAX(datetime) AS last_seen
FROM {{ ref('stg_keywords') }}
GROUP BY keyword