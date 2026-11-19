{{ config(materialized='table') }}

SELECT DISTINCT
    vendor_id
FROM {{ ref('stg_taxi_trips') }}
WHERE vendor_id IS NOT NULL