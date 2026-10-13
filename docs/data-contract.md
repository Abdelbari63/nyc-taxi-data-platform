# Data Contract — NYC Yellow Taxi Data Platform

## 1. Purpose

This document defines the schema, business meaning, and ingestion metadata for the NYC Yellow Taxi trip records used in the project.

**Source:** Yellow Taxi Parquet files for January, February, and March 2016.

**Source format:** Apache Parquet.

**Observed schema:** 19 columns, consistent across the three files.

The contract describes the source data. Additional metadata fields will be introduced during ingestion.

## 2. Source Schema

| Column | Source type | Description |
|---|---|---|
| `VendorID` | INT64 | Code identifying the TPEP technology provider. |
| `tpep_pickup_datetime` | TIMESTAMP (µs) | Time when the taxi meter was engaged. |
| `tpep_dropoff_datetime` | TIMESTAMP (µs) | Time when the taxi meter was disengaged. |
| `passenger_count` | INT64 | Recorded number of passengers. |
| `trip_distance` | DOUBLE | Trip distance in miles reported by the taximeter. |
| `RatecodeID` | INT64 | Final rate code recorded for the trip. |
| `store_and_fwd_flag` | STRING | Indicates whether the record was held in vehicle memory before transmission. |
| `PULocationID` | INT64 | TLC Taxi Zone where the meter was engaged. |
| `DOLocationID` | INT64 | TLC Taxi Zone where the meter was disengaged. |
| `payment_type` | INT64 | Numeric code representing the payment method or payment status. |
| `fare_amount` | DOUBLE | Meter-calculated time-and-distance fare. |
| `extra` | DOUBLE | Miscellaneous extras and surcharges. |
| `mta_tax` | DOUBLE | MTA tax recorded for the trip. |
| `tip_amount` | DOUBLE | Recorded tip amount; cash tips are not included. |
| `tolls_amount` | DOUBLE | Total recorded toll charges. |
| `improvement_surcharge` | DOUBLE | Recorded improvement surcharge. |
| `total_amount` | DOUBLE | Total amount charged, excluding cash tips. |
| `congestion_surcharge` | NULL | Field present in the source schema but containing only null values in the observed 2016 files. |

**Additional observed field:** `airport_fee` is also present in the source schema and contains only null values in all three files.

## 3. Important Schema Notes

- The observed Parquet schema contains 19 columns, including `congestion_surcharge` and `airport_fee`.
- Both surcharge columns are entirely null in the three inspected files.
- Preserve these fields during ingestion rather than inventing values.
- The newer data dictionary includes `cbd_congestion_fee`, which is absent from the 2016 source files.
- Do not add `cbd_congestion_fee` to the initial source schema.
- The newer dictionary's code descriptions may not match every code used in the 2016 data. Verify historical business rules before applying them.
- `DOUBLE` fields can contain nulls or unusual values. Validation rules must be defined separately from the schema.

## 4. Ingestion Metadata

The pipeline will add the following fields to ingested records.

| Field | Proposed type | Purpose |
|---|---|---|
| `event_id` | STRING | Stable identifier for a source record, reused across batch and streaming processing. |
| `source_file` | STRING | Original source file name. |
| `ingestion_run_id` | STRING | Identifier for a batch or ingestion execution. |
| `ingested_at` | TIMESTAMP | Time the record was ingested. |
| `schema_version` | STRING | Version of the data contract applied during ingestion. |

The streaming path will additionally preserve Kafka topic, partition, and offset metadata.

## 5. Event Identity Strategy

The source data does not provide a guaranteed unique trip identifier.

The initial design will generate a deterministic identifier from the source record and its stable source position, then persist it before the batch and streaming paths diverge.

The identifier must:

- Remain stable across retries and reprocessing.
- Be identical for the same source record in batch and streaming.
- Distinguish separate source records even if their business fields are identical.
- Be reproducible without depending on ingestion timestamps or run IDs.

A practical approach is to derive `event_id` from the source file identity and the record's row position within that file. The implementation must ensure that the row position is assigned deterministically and persisted.

Exact duplicate business records will not automatically be removed: two distinct source records may legitimately contain identical values.

## 6. Data Quality Responsibilities

The schema contract defines the expected fields and types. Separate quality rules will validate the records.

Validation categories include:

- Required-field checks.
- Timestamp validity and trip-duration checks.
- Distance and passenger-count checks.
- Numeric and financial consistency checks.
- Duplicate and identifier checks.
- Schema compatibility checks.

Invalid records will be retained in quarantine with a documented reason.

## 7. Contract Evolution

If a future dataset introduces additional fields:

1. Inspect the new source schema.
2. Decide whether the new field is required or optional.
3. Document its meaning and type.
4. Update the schema version.
5. Test compatibility with existing Bronze and Silver tables.
6. Preserve historical records without fabricating missing values.

## 8. Initial Acceptance Criteria

The contract is accepted when:

- All 19 source columns are documented.
- The three 2016 files conform to the expected source schema.
- The two all-null surcharge fields are preserved.
- Ingestion metadata is defined.
- A stable, reproducible `event_id` strategy is implemented.
- Business validation rules are documented separately from schema requirements.
