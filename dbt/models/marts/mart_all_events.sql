{{ config(materialized='table') }}

SELECT
    visit_id,
    sequence_number,
    datetime,
    event_type,
    event_id,
    event_details,
    time_diff_ms
FROM {{ ref('int_all_events_union') }}
ORDER BY visit_id, sequence_number