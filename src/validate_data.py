
from pathlib import Path
import pyarrow.parquet as pq

DATA_DIR = Path("data/raw")
BATCH_SIZE = 250_000

total_rows = 0
total_invalid_duration = 0
total_invalid_distance = 0
total_invalid_passengers = 0
total_invalid_any = 0

parquet_files = sorted(DATA_DIR.glob("*.parquet"))

if not parquet_files:
    raise FileNotFoundError(f"No Parquet files found in {DATA_DIR.resolve()}")

for path in parquet_files:
    parquet = pq.ParquetFile(path)

    rows = 0
    invalid_duration = 0
    invalid_distance = 0
    invalid_passengers = 0
    invalid_any = 0

    for batch in parquet.iter_batches(batch_size=BATCH_SIZE):
        df = batch.to_pandas()
        rows += len(df)

        # Rule 1: Drop-off must occur after pick-up.
        valid_duration = (
            df["tpep_pickup_datetime"].notna()
            & df["tpep_dropoff_datetime"].notna()
            & (
                df["tpep_dropoff_datetime"]
                > df["tpep_pickup_datetime"]
            )
        )

        # Rule 2: Distance must be present and non-negative.
        valid_distance = (
            df["trip_distance"].notna()
            & (df["trip_distance"] >= 0)
        )

        # Rule 3: Passenger count must be positive.
        valid_passengers = (
            df["passenger_count"].notna()
            & (df["passenger_count"] > 0)
        )

        invalid_duration += int((~valid_duration).sum())
        invalid_distance += int((~valid_distance).sum())
        invalid_passengers += int((~valid_passengers).sum())

        valid_record = (
            valid_duration & valid_distance & valid_passengers
        )
        invalid_any += int((~valid_record).sum())

    total_rows += rows
    total_invalid_duration += invalid_duration
    total_invalid_distance += invalid_distance
    total_invalid_passengers += invalid_passengers
    total_invalid_any += invalid_any

    print(f"\n{'=' * 50}")
    print(f"File: {path.name}")
    print(f"Total rows: {rows:,}")
    print(f"Invalid duration: {invalid_duration:,}")
    print(f"Invalid distance: {invalid_distance:,}")
    print(f"Invalid passenger count: {invalid_passengers:,}")
    print(f"Records failing at least one rule: {invalid_any:,}")
    print(f"Records passing all rules: {rows - invalid_any:,}")

print(f"\n{'=' * 50}")
print("OVERALL RESULTS")
print(f"Total rows: {total_rows:,}")
print(f"Invalid duration: {total_invalid_duration:,}")
print(f"Invalid distance: {total_invalid_distance:,}")
print(f"Invalid passenger count: {total_invalid_passengers:,}")
print(f"Records failing at least one rule: {total_invalid_any:,}")
print(f"Records passing all rules: {total_rows - total_invalid_any:,}")
