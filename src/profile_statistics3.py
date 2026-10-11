
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd

DATA_DIR = Path("data/raw")

for path in sorted(DATA_DIR.glob("*.parquet")):
    parquet = pq.ParquetFile(path)

    stats = {
        "rows": 0,
        "zero_distances": 0,
        "zero_fares": 0,
        "long_trips_over_3h": 0,
        "negative_totals": 0,
        "amount_mismatches_over_1cent": 0,
    }

    max_distance = float("-inf")
    max_fare = float("-inf")
    max_duration = float("-inf")

    for batch in parquet.iter_batches(batch_size=250_000):
        df = batch.to_pandas()
        stats["rows"] += len(df)

        duration = (
            df["tpep_dropoff_datetime"]
            - df["tpep_pickup_datetime"]
        ).dt.total_seconds()

        stats["zero_distances"] += int(
            (df["trip_distance"] == 0).sum()
        )
        stats["zero_fares"] += int(
            (df["fare_amount"] == 0).sum()
        )
        stats["long_trips_over_3h"] += int(
            (duration > 3 * 3600).sum()
        )
        stats["negative_totals"] += int(
            (df["total_amount"] < 0).sum()
        )

        # Compare total with the available fare components.
        components = [
            "fare_amount", "extra", "mta_tax", "tip_amount",
            "tolls_amount", "improvement_surcharge"
        ]
        expected = df[components].sum(axis=1)

        # Round to cents to reduce floating-point noise.
        mismatch = (
            (expected - df["total_amount"]).abs().round(2) > 0.01
        )
        stats["amount_mismatches_over_1cent"] += int(
            mismatch.sum()
        )

        max_distance = max(max_distance, df["trip_distance"].max())
        max_fare = max(max_fare, df["fare_amount"].max())
        max_duration = max(max_duration, duration.max())

    print(f"\n{path.name}")
    for name, value in stats.items():
        print(f"{name}: {value:,}")
    print(f"Maximum distance: {max_distance}")
    print(f"Maximum fare: {max_fare}")
    print(f"Maximum duration (seconds): {max_duration}")
