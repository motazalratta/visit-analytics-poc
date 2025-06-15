{{ config(materialized='table') }}

SELECT
    toDate(datetime) AS date,
    countDistinct(user_id) AS daily_active_users,
    countDistinct(search_id) AS total_searches,
    countDistinct(click_id) AS total_clicks,
    countDistinct(visitor_id) AS unique_visitors
FROM {{ ref('mart_search_activity') }} 
GROUP BY date
ORDER BY date