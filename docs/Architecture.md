# NYC Taxi Data Platform — Architecture

## 1. Project Overview

The NYC Taxi Data Platform is an end-to-end Data Engineering and Analytics project built using historical NYC Yellow Taxi trip data from January, February, and March 2016.

The project aims to demonstrate a complete data lifecycle, from raw data ingestion to analytical dashboards and machine learning.

The platform combines batch processing, simulated streaming, cloud data warehousing, analytical transformations, workflow orchestration, automated testing, machine learning, and data visualization.

The project follows a local-first development strategy, introducing cloud services selectively to control costs while gaining practical experience with industry-relevant technologies.

## 2. Technology Stack

| Technology | Responsibility |
|---|---|
| Python | Data ingestion, event production, utilities, and ML development |
| Apache Kafka | Streaming event ingestion and transport |
| Databricks | Managed Spark execution environment |
| Apache Spark / PySpark | Batch processing and streaming computation |
| Delta Lake | Bronze and Silver data storage |
| Snowflake | Cloud data warehouse |
| dbt | SQL transformations, analytical modeling, and data testing |
| Apache Airflow | Workflow orchestration and scheduling |
| scikit-learn | Machine learning model development and evaluation |
| MLflow | Experiment tracking and model management, if appropriate |
| Power BI | Interactive dashboards and data visualization |
| Git | Version control |
| GitHub | Source code hosting and collaboration |
| GitHub Actions | Continuous integration and automated checks |
| Docker / Docker Compose | Local development services and environment management |

## 3. High-Level Architecture — Lambda-Style Design

The platform follows a Lambda-style architecture, combining historical batch processing and simulated streaming processing to support both comprehensive historical analytics and low-latency event processing.

The architecture consists of three conceptual layers:

### 3.1 Batch Layer

**Technologies:** Databricks, Apache Spark, Delta Lake.

The batch layer processes the historical NYC Yellow Taxi Parquet files for January, February, and March 2016.

Responsibilities:

1. Read the original historical Parquet files.
2. Store ingested records in Bronze Delta tables.
3. Apply data quality rules and transformations using PySpark.
4. Separate valid records from quarantined records.
5. Store validated records in Silver Delta tables.
6. Load curated historical data into Snowflake.
7. Make historical data available for analytical transformations using dbt.

The batch layer provides a reproducible historical view of the dataset and serves as the reference for validating the streaming implementation.

### 3.2 Speed Layer

**Technologies:** Apache Kafka, Spark Structured Streaming, Delta Lake.

The speed layer simulates continuously arriving taxi trip events by replaying a selected subset of the historical dataset.

Responsibilities:

1. Publish trip events from a Python producer to Kafka.
2. Consume events using Spark Structured Streaming.
3. Store incoming events in separate Bronze streaming tables.
4. Apply streaming validation and transformations.
5. Calculate selected low-latency metrics.
6. Store processed streaming outputs separately from batch outputs.
7. Optionally publish suitable curated results to Snowflake.

The speed layer demonstrates event ingestion and incremental processing. Because the source is historical, the streaming pipeline is a simulation rather than a live NYC taxi feed.

### 3.3 Serving Layer

**Technologies:** Snowflake, dbt, Power BI.

The serving layer provides analytics-ready data for reporting and downstream use cases.

Responsibilities:

1. Store curated batch data in Snowflake.
2. Ingest selected streaming results when required.
3. Use dbt to build analytical models and aggregations.
4. Apply data quality tests and document model dependencies.
5. Expose business metrics through Power BI dashboards.
6. Provide suitable curated datasets for machine learning.

Snowflake is the primary analytical warehouse. dbt builds the business-facing models, while Power BI presents the resulting insights.

### 3.4 Batch and Streaming Reconciliation

The batch and speed layers must remain logically separate until their outputs can be combined safely.

The project will define a consistent event identity and processing policy before combining results. Where reliable trip identifiers are unavailable, a documented composite key or alternative deduplication strategy will be evaluated.

The initial implementation will avoid combining batch and streaming aggregates blindly. This prevents double-counting when streamed events also exist in the historical source data.

The serving layer will distinguish historical batch results, streaming results, and any reconciled metrics where appropriate.

### 3.5 Orchestration and CI/CD

**Technologies:** Apache Airflow, Git, GitHub, GitHub Actions.

Airflow coordinates batch processing, warehouse loading, dbt execution, and later machine learning workflows. Streaming jobs require an appropriate lifecycle and checkpointing strategy.

Git and GitHub manage source code and documentation. GitHub Actions runs lightweight automated tests and code-quality checks.

### 3.6 Machine Learning and Visualization

**Technologies:** scikit-learn, optionally MLflow, and Power BI.

After the core pipelines are operational, curated data will support model training and evaluation. Suitable prediction outputs and evaluation metrics may be stored in Snowflake and presented through Power BI.

Machine learning and dashboard development are downstream extensions; they do not replace the responsibilities of the batch, speed, or serving layers.


## 4. Data Architecture

### 4.1 Bronze — Raw Ingestion

**Technology:** PySpark and Delta Lake.

Responsibilities:

- Preserve ingested source values.
- Record ingestion metadata where appropriate.
- Track source file or event provenance.
- Keep batch and streaming records logically separate.
- Support reproducible processing and troubleshooting.

The original source files remain unchanged and excluded from Git.

### 4.2 Silver — Cleaned and Validated Data

**Technology:** PySpark and Delta Lake.

Responsibilities:

- Enforce documented schemas and data types.
- Apply data quality rules.
- Normalize values where required.
- Quarantine invalid records with explicit reasons.
- Handle duplicates according to a documented policy.
- Produce consistent records for analytical loading.

The initial quality rules cover valid trip duration, non-negative trip distance, and positive passenger count.

Additional policies for extreme values, negative fares, and financial inconsistencies must be documented before those cases are incorporated into quarantine logic.

### 4.3 Snowflake — Cloud Data Warehouse

**Technology:** Snowflake.

Snowflake will serve as the primary analytical warehouse.

Responsibilities:

- Store curated trip data.
- Provide a structured environment for analytical queries.
- Separate ingestion and staging structures from business-facing models.
- Support downstream reporting and machine learning data extraction.
- Store selected prediction outputs and model evaluation results when useful.

The ingestion design will account for incremental loading, safe retries, and reconciliation of record counts.

### 4.4 Gold — Analytics-Ready Models

**Technology:** dbt running against Snowflake.

Gold will contain tested, documented, and analytics-ready models.

Initial candidate models include:

- `fct_trips`: trip-level fact table.
- `dim_datetime`: date and time attributes.
- `dim_vendor`: vendor information.
- `dim_payment_type`: payment method attributes.
- `dim_location`: pickup and drop-off location attributes, subject to source data availability.
- `agg_daily_revenue`: daily trip and revenue metrics.
- `agg_pickup_demand`: trip demand by pickup location and time.

The final model design will depend on source columns, data profiling, business definitions, and analytical requirements.

dbt will manage model dependencies, SQL transformations, documentation, and data tests.

## 5. Machine Learning Architecture

The ML component will be built after the main Data Engineering pipeline is operational.

### 5.1 Data Preparation

Curated data will be extracted from Snowflake or Delta Lake. Feature engineering, missing-value handling, categorical encoding, and dataset splitting will be implemented in Python.

### 5.2 Model Development

scikit-learn will be the initial framework for building and evaluating baseline models.

Candidate evaluation metrics include:

- MAE and RMSE for regression.
- R² as a supplementary regression metric.
- Additional metrics where appropriate to the selected task.

The project will compare a simple baseline with more advanced models rather than assuming a complex model is automatically better.

### 5.3 Experiment Tracking

MLflow may be introduced to track:

- Model parameters.
- Evaluation metrics.
- Experiment runs.
- Model artifacts and versions.

The exact tracking and artifact-storage configuration will depend on the selected execution environment and cost constraints.

### 5.4 Predictions and Integration

The selected model will generate predictions from curated features.

Predictions and relevant evaluation results may be stored in Snowflake so that Power BI can analyze them alongside business metrics.

Training and scoring workflows can later be orchestrated with Airflow.

## 6. Data Visualization Architecture

**Technology:** Power BI.

Power BI will connect to suitable Snowflake Gold tables and selected prediction outputs.

The visualization layer will focus on presenting business insights rather than repeating transformations that should be performed in Spark or dbt.

The project will demonstrate:

- KPI cards and trend analysis.
- Time-based and geographical analysis where location data permits.
- Interactive filters and drill-downs.
- Comparisons across vendors and payment methods.
- Model evaluation and prediction analysis.
- Clear metric definitions and traceability to warehouse models.

The connection mode and refresh strategy will be chosen according to available Power BI capabilities, Snowflake configuration, and licensing constraints.

## 7. Technology Responsibilities and Boundaries

### Apache Kafka

Transports streaming events between producers and consumers. It is not the primary engine for historical batch transformations.

### Databricks and Apache Spark

Perform large-scale ingestion and data processing. Databricks provides the managed execution environment for Spark workloads.

### Delta Lake

Provides reliable table storage for Bronze and Silver data.

### Snowflake

Stores curated analytical data and executes warehouse queries and dbt transformations.

### dbt

Transforms staged warehouse data into analytical models. It does not replace PySpark's role in the initial large-scale ingestion and cleaning pipeline.

### Apache Airflow

Coordinates tasks, dependencies, schedules, retries, and failure reporting. It orchestrates processing jobs rather than performing the underlying transformations itself.

### scikit-learn and MLflow

scikit-learn supports model training and evaluation. MLflow can track experiments and model artifacts.

### Power BI

Consumes analytical tables and selected prediction outputs to create interactive dashboards.

### GitHub Actions

Automates lightweight tests and code-quality checks. Full dataset processing and expensive cloud workloads will not run on every code change.

### Docker

Provides reproducible local environments for services such as Kafka and Airflow. It is not required for Snowflake, and its role in local Spark development will depend on the chosen setup.

## 8. Orchestration and Execution Flow

The intended historical batch workflow is:

1. Validate source availability and configuration.
2. Execute the Databricks ingestion job.
3. Write Bronze data.
4. Transform Bronze into Silver.
5. Validate record counts and quarantine metrics.
6. Load curated data into Snowflake staging tables.
7. Execute dbt models.
8. Run dbt data tests.
9. Refresh or expose analytics-ready data to Power BI.
10. Record execution status and report failures.

The machine learning workflow will be introduced later:

1. Prepare a versioned training dataset.
2. Train and evaluate candidate models.
3. Track experiments and select a model.
4. Generate predictions.
5. Store prediction outputs and relevant metrics.
6. Make suitable results available to Power BI.

Airflow can coordinate the batch and ML workflows. Streaming jobs will require an appropriate lifecycle, checkpointing, and monitoring strategy rather than being treated as ordinary short-lived batch tasks.

## 9. Development and Deployment Strategy

The project follows a local-first development strategy.

- Keep raw datasets and generated data files outside Git.
- Develop and test Python utilities locally.
- Use local Spark where practical for learning and initial validation.
- Use Docker Compose for local services such as Kafka and Airflow when introduced.
- Introduce Databricks and Snowflake selectively for managed processing and warehouse integration.
- Use small test datasets in CI.
- Verify cloud pricing, account limitations, connector compatibility, and required compute before deployment.
- Avoid leaving paid cloud resources running unnecessarily.

The machine learning pipeline will initially use manageable datasets and local scikit-learn execution where practical. More expensive or distributed ML workloads will only be introduced when justified.

## 10. Data Quality and Reliability

The platform will progressively implement:

- Schema validation.
- Explicit quarantine reasons.
- Reconciliation of input, valid, and invalid record counts.
- Duplicate detection and documented handling.
- dbt uniqueness, not-null, and relationship tests where appropriate.
- Repeatable ingestion and safe retry behavior.
- Pipeline execution logs and failure reporting.
- ML evaluation and validation checks.
- Checks for target leakage and invalid prediction inputs.

The existing Python/PyArrow pipeline will serve as a reference for validating the initial Spark implementation.

## 11. Repository and CI/CD

The repository will contain source code, tests, documentation, dbt models, Airflow workflows, ML code, dashboard documentation, and GitHub Actions configuration.

Git will track source code and configuration, while raw and generated datasets remain excluded.

GitHub Actions will initially run unit tests, linting, and lightweight validation. Integration tests requiring external services will be introduced deliberately.

Dashboard files and ML artifacts will be managed according to their size and reproducibility requirements rather than committing large generated artifacts indiscriminately.

## 12. Implementation Order

1. Finalize the architecture and data contracts.
2. Set up Spark and Delta Lake development.
3. Implement the historical batch pipeline.
4. Load curated data into Snowflake.
5. Build and test dbt models.
6. Orchestrate the batch pipeline with Airflow.
7. Implement the Kafka streaming simulation.
8. Integrate suitable streaming outputs.
9. Build the machine learning training and evaluation pipeline.
10. Develop Power BI dashboards for business analytics and ML results.
11. Add CI/CD, operational documentation, and final validation.

## 13. Success Criteria

The project is considered complete when it demonstrates:

- Reproducible processing of the historical dataset.
- Explicit data quality rules and quarantine handling.
- Reliable Bronze and Silver Delta tables.
- Curated data loaded into Snowflake.
- Tested and documented dbt analytical models.
- An orchestrated batch workflow.
- A working Kafka-to-Spark streaming simulation.
- A reproducible machine learning pipeline with documented evaluation.
- Interactive Power BI dashboards with clearly defined metrics.
- Automated code checks through GitHub Actions.
- Clear architecture documentation and reproducible setup instructions.
- A cost-conscious implementation with documented limitations.
