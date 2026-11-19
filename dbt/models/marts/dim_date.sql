
{{ config(materialized='table') }}

WITH date_bounds AS (
    SELECT
        DATE '2016-01-01' AS start_date,
        GREATEST(
            COALESCE(MAX(TO_DATE(pickup_datetime)), DATE '2016-01-01'),
            COALESCE(MAX(TO_DATE(dropoff_datetime)), DATE '2016-01-01')
        ) AS end_date
    FROM {{ ref('stg_taxi_trips') }}
),

date_spine AS (
    SELECT
        DATEADD(
            DAY,
            ROW_NUMBER() OVER (ORDER BY SEQ4()) - 1,
            start_date
        )::DATE AS full_date
    FROM date_bounds,
         TABLE(GENERATOR(ROWCOUNT => 10000))
    QUALIFY full_date <= end_date
)

SELECT
    TO_NUMBER(TO_CHAR(full_date, 'YYYYMMDD')) AS date_key,
    full_date,
    YEAR(full_date) AS year,
    QUARTER(full_date) AS quarter,
    MONTH(full_date) AS month,
    MONTHNAME(full_date) AS month_name,
    DAY(full_date) AS day_of_month,
    DAYOFWEEKISO(full_date) AS day_of_week,
    DAYNAME(full_date) AS day_name,
    IFF(DAYOFWEEKISO(full_date) IN (6, 7), TRUE, FALSE) AS is_weekend
FROM date_spine
