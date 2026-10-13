# Ingestion Design — NYC Taxi Data Platform

## 1. Objective

Define how historical NYC Yellow Taxi data is ingested, validated, processed, and made available for analytics.

The platform uses a Lambda-style architecture with two ingestion paths:

- **Batch:** Historical data processed using Databricks, PySpark, and Delta Lake.
- **Streaming:** Simulated taxi events transported through Kafka and processed using Spark Structured Streaming.

Snowflake is the analytical warehouse, dbt builds analytical models, and Airflow orchestrates batch workflows.

## 2. Source Data

- Source: NYC Yellow Taxi historical Parquet files.
- Period: January–March 2016.
- Original volume: Approximately 34.5 million records.
- Source files are immutable and must never be overwritten by pipeline processing.

## 3. Batch Ingestion

### Processing flow

1. Read historical Parquet files from the designated source location.
2. Validate the expected schema and required columns.
3. Add ingestion metadata and a stable `event_id`.
4. Write the ingested records to Bronze Delta tables.
5. Apply data quality rules using PySpark.
6. Separate valid records from quarantined records.
7. Write validated records to Silver Delta tables.
8. Load the required curated data into Snowflake.
9. Execute dbt models to build analytical tables.

### Storage layers

- **Bronze:** Source records plus ingestion metadata, with minimal changes.
- **Silver:** Validated, cleaned, typed, and deduplicated records according to documented rules.
- **Gold:** Business-facing analytical models built primarily in Snowflake using dbt.

## 4. Streaming Ingestion

### Processing flow

1. Select a defined subset of historical records for replay.
2. Publish records as events using a Python Kafka producer.
3. Include the stable `event_id` in every event.
4. Consume events with Spark Structured Streaming on Databricks.
5. Validate events and preserve Kafka metadata.
6. Write raw events to a separate Bronze streaming Delta table.
7. Process valid events into a separate Silver streaming table.
8. Calculate selected streaming metrics and optionally publish curated results to Snowflake.

This pipeline simulates streaming. It does not represent a live NYC taxi feed.

## 5. Data Contract

Each ingested record must preserve the source data and conform to an agreed schema.

### Business fields

The exact names and types will be confirmed against the source schema. Expected fields include:

- Pickup and drop-off timestamps
- Trip distance
- Passenger count
- Fare amount
- Tip amount
- Taxes and surcharges
- Total amount
- Available vendor and payment identifiers

### Ingestion metadata

| Field | Purpose |
|---|---|
| `event_id` | Stable identifier for a source record |
| `source_file` | Original file name or source path |
| `ingestion_run_id` | Identifies the ingestion run |
| `ingested_at` | Timestamp when the record was ingested |
| `schema_version` | Identifies the data contract version |

### Streaming metadata

| Field | Purpose |
|---|---|
| `kafka_topic` | Source Kafka topic |
| `kafka_partition` | Kafka partition |
| `kafka_offset` | Position of the event within the partition |
| `event_time` | Event timestamp, where available and defined |

## 6. Event Identity and Deduplication

The source dataset does not guarantee a unique identifier for every trip.

The pipeline will therefore create a stable `event_id` during source preparation. That identifier must be persisted and reused by both the batch and streaming paths.

Requirements:

1. Identical source rows must not automatically be assumed to represent duplicate trips.
2. Exact duplicate records must be investigated before deciding whether to remove them.
3. The same `event_id` must remain stable across retries and reprocessing.
4. Delta writes must use a controlled merge or replacement strategy where appropriate.
5. Kafka checkpoints must be stored persistently to support streaming recovery.
6. Batch and streaming results must not be added together without a defined reconciliation policy.

## 7. Data Quality and Quarantine

The pipeline will apply the following validation categories:

- Schema and data type validation
- Missing or invalid required values
- Invalid timestamps and trip durations
- Negative trip distances
- Invalid passenger counts
- Financial inconsistencies and suspicious fare values
- Duplicate detection
- Source-to-target reconciliation

Records failing defined rules will be retained in quarantine with a `quarantine_reason`.

Suspicious values must be investigated and documented before being rejected; unusual values are not necessarily invalid.

## 8. Reliability and Reprocessing

- Keep source files immutable.
- Use stable record identifiers and explicit run identifiers.
- Make batch ingestion safe to rerun.
- Persist streaming checkpoints outside ephemeral compute storage.
- Monitor failed records, processing failures, and data volume.
- Document how to recover from failed or interrupted runs.
- Validate record counts between processing stages.

Exactly-once end-to-end processing must not be assumed merely because Delta Lake or Kafka is used. It depends on source identity, checkpointing, sink behavior, and retry design.

## 9. Batch and Streaming Reconciliation

The batch pipeline processes the full historical dataset.

The streaming pipeline replays a documented subset of that dataset. Consequently, the same trips can exist in both paths.

Initially, batch and streaming outputs will remain separate. Combined metrics will only be introduced after defining record ownership, deduplication rules, and reconciliation logic.

## 10. Target Responsibilities

| Technology | Responsibility |
|---|---|
| Databricks | Managed Spark execution and pipeline development |
| PySpark | Batch transformations and data validation |
| Delta Lake | Bronze and Silver storage |
| Kafka | Event transport |
| Spark Structured Streaming | Incremental event processing |
| Snowflake | Analytical data warehouse |
| dbt | Analytical transformations and model tests |
| Airflow | Workflow orchestration |
| GitHub Actions | Automated code checks and tests |
| Power BI | Dashboards and reporting |

## 11. Implementation Order

1. Inspect and confirm the source schema.
2. Define the data contract and stable event identity.
3. Configure Databricks and source access.
4. Implement batch ingestion into Bronze Delta.
5. Implement Silver transformations and quarantine.
6. Validate counts and rerun behavior.
7. Design the Kafka event format and streaming subset.
8. Implement streaming ingestion and persistent checkpoints.
9. Design Snowflake loading and dbt models.
10. Add orchestration, monitoring, and automated tests.

## 12. Completion Criteria

The ingestion design is complete when:

- Source fields and data types are documented.
- Event identity and duplicate handling are defined.
- Bronze, Silver, and Gold responsibilities are clear.
- Quarantine and reprocessing behavior is specified.
- Batch and streaming overlap is explicitly addressed.
- The design can be implemented and tested reproducibly.
