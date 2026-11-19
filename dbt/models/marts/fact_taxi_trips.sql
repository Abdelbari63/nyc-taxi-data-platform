
{{ config(materialized='table') }}

SELECT

    -- Date foreign keys
    TO_NUMBER(TO_CHAR(TO_DATE(PICKUP_DATETIME), 'YYYYMMDD'))
        AS PICKUP_DATE_KEY,

    TO_NUMBER(TO_CHAR(TO_DATE(DROPOFF_DATETIME), 'YYYYMMDD'))
        AS DROPOFF_DATE_KEY,

    -- Dimension foreign keys
    VENDOR_ID,
    PAYMENT_TYPE,
    RATECODE_ID,
    PU_LOCATION_ID,
    DO_LOCATION_ID,

    -- Trip attributes
    EVENT_ID,
    STORE_AND_FWD_FLAG,

    -- Trip timestamps
    PICKUP_DATETIME,
    DROPOFF_DATETIME,

    -- Trip measures
    PASSENGER_COUNT,
    TRIP_DISTANCE,
    TRIP_DURATION_MINUTES,

    -- Financial measures
    FARE_AMOUNT,
    EXTRA,
    MTA_TAX,
    TIP_AMOUNT,
    TOLLS_AMOUNT,
    IMPROVEMENT_SURCHARGE,
    CONGESTION_SURCHARGE,
    AIRPORT_FEE,
    TOTAL_AMOUNT,

    -- Additional analytical attributes
    PICKUP_HOUR,
    PICKUP_DAY_OF_WEEK,

    -- Data lineage
    SOURCE_FILE,
    INGESTION_RUN_ID,
    INGESTED_AT,
    SCHEMA_VERSION

FROM {{ ref('stg_taxi_trips') }}

QUALIFY ROW_NUMBER() OVER (
    PARTITION BY EVENT_ID
    ORDER BY INGESTED_AT DESC, SOURCE_FILE DESC
) = 1