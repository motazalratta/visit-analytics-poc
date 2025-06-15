{{ config(materialized='table') }}

SELECT
    s.id AS search_id,
    s.datetime AS datetime,
    s.userId AS user_id,
    s.visitorId AS visitor_id,
    s.city AS city,
    s.country AS country,
    s.language AS language,
    s.browser AS browser,
    s.operatingSystemWithVersion AS operating_system_with_version,
    s.deviceCategory AS device_category,
    s.originLevel1 AS origin_level1,
    s.originLevel2 AS origin_level2,
    s.queryPipeline AS query_pipeline,
    s.numberOfResults AS number_of_results,
    s.responseTimeMs AS response_time_ms,
    k.keyword AS keyword,
    g.groupName AS group_name
FROM {{ ref('stg_searches') }} s
LEFT JOIN {{ ref('stg_keywords') }} k ON s.id = k.searchId
LEFT JOIN {{ ref('stg_groups') }} g ON s.id = g.searchId