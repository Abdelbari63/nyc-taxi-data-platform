
{{ config(materialized='view') }}

select
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    passenger_count,
    trip_distance,
    ratecode_id,
    store_and_fwd_flag,
    pu_location_id,
    do_location_id,
    payment_type,
    fare_amount,
    extra,
    mta_tax,
    tip_amount,
    tolls_amount,
    improvement_surcharge,
    total_amount,
    congestion_surcharge,
    airport_fee,
    source_file,
    ingestion_run_id,
    ingested_at,
    schema_version,
    event_id,
    trip_duration_minutes,
    pickup_date,
    pickup_hour,
    pickup_day_of_week
from {{ source('silver', 'taxi_trips') }}
