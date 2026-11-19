
{{ config(materialized='table') }}

SELECT DISTINCT
    ratecode_id
FROM {{ ref('stg_taxi_trips') }}
WHERE ratecode_id IS NOT NULL
