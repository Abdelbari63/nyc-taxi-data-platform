# NYC Taxi Data Engineering Platform

An end-to-end Data Engineering portfolio project built around the NYC Yellow Taxi trip dataset. The goal is to develop a reproducible data platform covering data ingestion, transformation, orchestration, data quality, and analytics.

## Project Objectives

- Build a reliable pipeline for historical taxi trip data.
- Learn and integrate modern Data Engineering technologies.
- Apply data-quality checks and document anomalies.
- Transform raw data into analytics-ready datasets.
- Automate pipeline execution and testing.
- Demonstrate the project through documented code and architecture.

## Dataset

**Source:** [NYC Taxi & Limousine Commission — Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

The initial dataset contains Yellow Taxi trip records for January, February, and March 2016.

| Property | Value |
|---|---|
| Format | Parquet |
| Monthly files | 3 |
| Total records | 34,484,303 |
| Approximate total size | 457 MB |

Raw data is stored locally and excluded from Git.

## Technology Stack

Planned technologies:

- **Python:** Data inspection and supporting scripts
- **Apache Kafka:** Event ingestion and simulated streaming
- **Databricks / Apache Spark:** Distributed data processing
- **dbt:** SQL transformations and data testing
- **Apache Airflow:** Workflow orchestration
- **Git and GitHub:** Version control and collaboration
- **GitHub Actions:** Automated checks and CI

The stack will be introduced incrementally as each part of the platform becomes functional.

## Current Progress

### Phase 0 — Data Exploration and Project Foundations

- [x] Download the initial Yellow Taxi dataset.
- [x] Set up a Python virtual environment.
- [x] Inspect Parquet schemas and file metadata.
- [x] Profile null values and potential data-quality issues.
- [x] Investigate extreme distances, fares, and trip durations.
- [x] Document initial profiling findings.
- [x] Initialize Git and create the first commit.
- [ ] Finalize project documentation and repository setup.
- [ ] Build the first reproducible ingestion pipeline.

See [`docs/data-profiling.md`](docs/data-profiling.md) for profiling results.

## Data Quality Findings

Initial profiling identified suspicious values, including:

- Trips with implausibly large recorded distances.
- Pickup and drop-off timestamps separated by months.
- Extreme fare values.
- Records with zero distances or fares.
- Missing values in fields that are unavailable in the selected historical dataset.

These records will be handled through documented validation rules rather than silently deleted.

## Planned Architecture

The target architecture will progressively incorporate historical data ingestion, simulated event streaming, processing and storage, SQL transformations, orchestration, testing, and analytics.

The architecture and technology choices will be documented as the implementation evolves.

## Reproducibility

Create and activate a Python virtual environment, then install the project dependencies:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the profiling scripts from the project root:

```powershell
python src/profile_data1.py
python src/profile_quality2.py
python src/profile_statistics3.py
python src/inspect_outliers4.py
```

## Project Status

**In progress.** The current milestone covers local setup, dataset exploration, and initial data-quality investigation. The complete pipeline has not yet been implemented.
