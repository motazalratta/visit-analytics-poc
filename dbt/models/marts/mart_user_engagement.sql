{{ config(materialized='table') }}

SELECT
    user_id,
    countDistinct(search_id) AS total_searches,
    countDistinct(click_id) AS total_clicks,
    min(datetime) AS first_activity,
    max(datetime) AS last_activity
FROM {{ ref('mart_search_activity') }}
GROUP BY user_id