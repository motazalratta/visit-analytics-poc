{{ config(materialized='view') }}

SELECT
    customEventId,
    lastSearchId,
    datetime,
    userAgent,
    isInternal,
    operatingSystemWithVersion,
    country,
    city,
    language,
    browserWithVersion,
    userName,
    splitTestRunVersion,
    anonymous,
    browser,
    userId,
    originContext,
    originLevel3,
    deviceCategory,
    originLevel2,
    originLevel1,
    region,
    splitTestRunName,
    eventValue,
    customDatas,
    customEventCustomData,
    eventType,
    visitorId,
    customEventOriginLevel1,
    customEventOriginLevel2,
    mobile,
    visitId,
    c_loading_time,
    c_pagelanguage,
    c_card_type,
    c_browser_time,
    c_pageaudience,
    c_workgroup,
    c_jsuiversion,
    JSONExtractString(customDatas, 'c_impressions') as c_impressions,
    JSONExtractString(customEventCustomData, 'c_query') as c_query
FROM {{ source('raw', 'custom_events') }}
WHERE customEventId IS NOT NULL
  AND datetime IS NOT NULL