
# NYC Yellow Taxi Data Profiling

## 1. Dataset Overview

- **Source:** NYC Taxi & Limousine Commission (TLC)
- **Dataset:** Yellow Taxi Trip Records
- **Period:** January–March 2016
- **Format:** Parquet
- **Files:** 3 monthly files
- **Total records:** 34,484,303
- **Total size:** Approximately 457.17 MB
- **Columns:** 19

## 2. Schema Findings

The three files share the same schema.

- Pickup and drop-off timestamps use microsecond precision.
- Location fields contain zone IDs rather than geographic coordinates.
- `congestion_surcharge` and `airport_fee` have null-only types in these files.

These fields will be evaluated during transformation because they contain no usable values in this historical dataset.

## 3. Data Quality Findings

Across the three monthly files:

- Negative fares: 13,056
- Non-positive trip durations: 35,981
- Passenger counts less than or equal to zero: 1,638
- Negative trip distances: 0
- Zero-distance trips: 191,777
- Zero-fare trips: 8,528
- Trips longer than three hours: 52,951
- Negative total amounts: 13,057
- Financial component mismatches exceeding one cent: 248

## 4. Anomaly Investigation

Inspection of extreme records revealed:

- Implausibly large trip distances, including values exceeding 19 million miles.
- Pickup and drop-off timestamps separated by several months.
- Extreme fare values, including a fare above $429,000.
- Trips with zero distance but substantial recorded fares.

These records require explicit validation and investigation.

## 5. Initial Data Quality Strategy

### Bronze
Preserve source data without silently removing anomalous records.

### Silver
Standardize types, normalize missing values, apply documented validation rules, and flag suspicious records.

### Quarantine
Retain records that fail critical validation rules for investigation rather than silently discarding them.

### Gold
Build analytical tables and business metrics from appropriately validated data.

## 6. Important Decisions

- Negative fares and negative totals will not automatically be deleted.
- Zero-distance and zero-fare trips require contextual validation.
- The three-hour duration threshold is a review rule, not definitive proof of invalidity.
- Extreme values will be flagged using documented rules.
- All cleaning decisions must be reproducible and testable.

## 7. Limitations

This profiling identifies suspicious patterns but does not establish the root cause of each anomaly. Further validation and comparison with the historical TLC data dictionary are needed before finalizing transformation rules.

## DATA QUALITY RULES

Define our first data-quality rules
We'll implement these rules in the Silver layer later, after documenting the profiling results.
Rule	Proposed treatment
Pickup or drop-off timestamp is null	:Reject or quarantine
Drop-off is not after pickup :	Flag; quarantine invalid durations
Trip duration exceeds 3 hours :	Flag for review, not automatically delete
Trip distance is negative :	Flag
Trip distance is extremely large :	Flag using a documented threshold
Fare is negative :	Preserve and investigate; may be an adjustment
Fare is extremely large :	Flag using a documented threshold
Passenger count is zero or negative :	Flag
congestion_surcharge and airport_fee are entirely null :	Document as unavailable in this historical dataset

![alt text](firs_data_quality_rules.png)