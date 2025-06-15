{{ config(materialized='table') }}

WITH all_events AS (
    -- Searches
    SELECT 
        visitId,
        datetime,
        'search' AS event_type,
        id AS event_id,
        queryExpression AS event_details
    FROM {{ ref('stg_searches') }}
    WHERE visitId IS NOT NULL

    UNION ALL

    -- Clicks
    SELECT 
        visitId,
        datetime,
        'click' AS event_type,
        clickId AS event_id,
        concat('Clicked: ', coalesce(documentTitle, documentUrl)) AS event_details
    FROM {{ ref('stg_clicks') }}
    WHERE visitId IS NOT NULL

    UNION ALL

    -- Custom Events
    SELECT 
        visitId,
        datetime,
        'custom_event' AS event_type,
        customEventId AS event_id,
        concat(eventType, ': ', coalesce(eventValue, '')) AS event_details
    FROM {{ ref('stg_custom_events') }}
    WHERE visitId IS NOT NULL
),
events_sorted AS (
    SELECT 
        visitId,
        arraySort(groupArray(tuple(datetime, event_type, event_id, event_details))) AS sorted_events
    FROM all_events
    GROUP BY visitId
),
flattened AS (
    SELECT
        visitId,
        arrayJoin(arrayEnumerate(sorted_events)) AS idx,
        sorted_events[idx].1 AS datetime,
        sorted_events[idx].2 AS event_type,
        sorted_events[idx].3 AS event_id,
        sorted_events[idx].4 AS event_details,
        idx AS sequence_number,
        IF(idx > 1, sorted_events[idx - 1].1, NULL) AS previous_datetime
    FROM events_sorted
)
SELECT
    visitId AS visit_id,
    sequence_number,
    datetime,
    event_type,
    event_id,
    event_details,
    IF(previous_datetime IS NULL, 0, dateDiff('millisecond', previous_datetime, datetime)) AS time_diff_ms
FROM flattened
ORDER BY visitId, sequence_number