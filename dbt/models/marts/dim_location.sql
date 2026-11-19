
{{ config(materialized='table') }}

WITH all_locations AS (

    SELECT pu_location_id AS location_id
    FROM {{ ref('stg_taxi_trips') }}
    WHERE pu_location_id IS NOT NULL

    UNION

    SELECT do_location_id AS location_id
    FROM {{ ref('stg_taxi_trips') }}
    WHERE do_location_id IS NOT NULL

)

SELECT
    location_id
FROM all_locations
