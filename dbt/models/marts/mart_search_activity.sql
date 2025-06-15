{{ config(materialized='table') }}

SELECT
    ss.search_id AS search_id,
    ss.datetime AS datetime,
    ss.user_id AS user_id,
    up.username AS username,
    ss.city AS city,
    ss.country AS country,
    ss.language AS language,
    ss.browser AS browser,
    ss.device_category AS device_category,
    ss.query_pipeline AS query_pipeline,
    ss.number_of_results AS number_of_results,
    ss.response_time_ms AS response_time_ms,
    ss.keyword AS keyword,
    ss.group_name AS group_name,
    c.clickId AS click_id,
    c.documentTitle AS document_title,
    c.clickRank AS click_rank,
    c.clickCause AS click_cause,
    c.visitorId AS visitor_id
FROM {{ ref('int_search_sessions') }} ss
LEFT JOIN {{ ref('stg_clicks') }} c ON ss.search_id = c.searchId
LEFT JOIN {{ ref('int_user_profiles') }} up ON ss.user_id = up.user_id