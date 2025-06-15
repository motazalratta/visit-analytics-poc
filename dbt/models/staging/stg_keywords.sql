{{ config(materialized='view') }}

SELECT
    searchId,
    keyword,
    datetime
FROM {{ source('raw', 'keywords') }}
