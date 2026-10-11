
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

columns = [
    "VendorID",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "fare_amount",
    "total_amount",
]

for path in sorted(DATA_DIR.glob("*.parquet")):
    df = pd.read_parquet(path, columns=columns)

    duration = (
        df["tpep_dropoff_datetime"]
        - df["tpep_pickup_datetime"]
    ).dt.total_seconds()

    print(f"\n{'=' * 65}")
    print(path.name)

    print("\nLargest distances:")
    print(
        df.nlargest(5, "trip_distance")[columns]
        .to_string(index=False)
    )

    print("\nLargest fares:")
    print(
        df.nlargest(5, "fare_amount")[columns]
        .to_string(index=False)
    )

    print("\nLongest durations:")
    print(
        df.loc[duration.nlargest(5).index, columns]
        .assign(duration_seconds=duration.loc[duration.nlargest(5).index])
        .to_string(index=False)
    )
