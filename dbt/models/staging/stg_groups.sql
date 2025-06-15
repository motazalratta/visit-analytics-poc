{{ config(materialized='view') }}

SELECT
    searchId,
    groupName,
    datetime
FROM {{ source('raw', 'groups') }}