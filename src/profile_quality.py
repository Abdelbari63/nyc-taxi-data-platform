
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd

DATA_DIR = Path("data/raw")

for path in sorted(DATA_DIR.glob("*.parquet")):
    parquet = pq.ParquetFile(path)

    null_counts = {}
    rows = 0
    negative_fares = 0
    negative_distances = 0
    invalid_passengers = 0
    invalid_durations = 0
    min_pickup = None
    max_pickup = None

    for batch in parquet.iter_batches(batch_size=250_000):
        df = batch.to_pandas()
        rows += len(df)

        for col in df.columns:
            null_counts[col] = (
                null_counts.get(col, 0) + int(df[col].isna().sum())
            )

        negative_fares += int((df["fare_amount"] < 0).sum())
        negative_distances += int((df["trip_distance"] < 0).sum())
        invalid_passengers += int((df["passenger_count"] <= 0).sum())

        duration = (
            df["tpep_dropoff_datetime"]
            - df["tpep_pickup_datetime"]
        ).dt.total_seconds()

        invalid_durations += int((duration <= 0).sum())

        batch_min = df["tpep_pickup_datetime"].min()
        batch_max = df["tpep_pickup_datetime"].max()

        min_pickup = (
            batch_min if min_pickup is None
            else min(min_pickup, batch_min)
        )
        max_pickup = (
            batch_max if max_pickup is None
            else max(max_pickup, batch_max)
        )

    print(f"\n{'=' * 55}")
    print(f"File: {path.name}")
    print(f"Rows checked: {rows:,}")
    print(f"Pickup range: {min_pickup} to {max_pickup}")

    print("\nNull counts:")
    for col, count in null_counts.items():
        if count:
            print(f"  {col}: {count:,} ({count / rows:.2%})")

    print("\nPotential quality issues:")
    print(f"  Negative fares: {negative_fares:,}")
    print(f"  Negative distances: {negative_distances:,}")
    print(f"  Passenger count <= 0: {invalid_passengers:,}")
    print(f"  Duration <= 0 seconds: {invalid_durations:,}")
