
# Silver Layer — Data Processing and Quality

## 1. Objective

The Silver layer transforms raw Bronze data into standardized, validated, and analytics-ready taxi trip records.

The pipeline is implemented in PySpark on Databricks and stores its outputs as Delta tables in Unity Catalog.

## 2. Input

Source table:

`main`.`nyc-taxi`.bronze_taxi_trips

Total input records: 34,484,303

## 3. Transformations

- Standardized business column names using snake_case.
- Preserved ingestion metadata for traceability.
- Calculated `trip_duration_minutes`.
- Derived `pickup_date`, `pickup_hour`, and `pickup_day_of_week`.
- Preserved nullable `congestion_surcharge` and `airport_fee` fields because all source values are null.
- Kept Bronze unchanged.

## 4. Data Quality Rules

Records are quarantined when they have:

- Missing pickup or drop-off timestamps.
- A non-positive trip duration.
- A missing, zero, or negative passenger count.
- A missing or negative trip distance.

Positive but unusually long trips are retained for now. No arbitrary maximum-duration threshold is applied.

## 5. Output Tables

| Table | Records | Purpose |
|---|---:|---|
| `main`.`nyc-taxi`.silver_taxi_trips | 34,446,756 | Validated trip records |
| `main`.`nyc-taxi`.quarantine_taxi_trips | 37,547 | Records failing quality rules |

Bronze contains 34,484,303 records. Silver plus Quarantine equals the Bronze record count.

## 6. Validation

The following checks passed:

- Silver and Quarantine counts reconcile with Bronze.
- No non-positive durations remain in Silver.
- No null or non-positive passenger counts remain in Silver.
- Every quarantined record has a reason.

## 7. Known Limitations

- Three groups of exact duplicates were identified across 19 business columns, representing three excess rows. They have not been removed automatically.
- Financial consistency rules require further investigation before they can be safely enforced.
- `congestion_surcharge` and `airport_fee` are entirely null in the 2016 source data.
- The current quarantine rules focus on clearly invalid records and do not reject positive durations solely because they are unusually long.

## 8. Technology Stack

- Databricks
- PySpark
- Delta Lake
- Unity Catalog
