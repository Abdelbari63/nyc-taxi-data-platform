
{{ config(materialized='table') }}

SELECT DISTINCT
    payment_type
FROM {{ ref('stg_taxi_trips') }}
WHERE payment_type IS NOT NULL
