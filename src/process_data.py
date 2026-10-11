
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

RAW_DIR = Path("data/raw")
VALID_DIR = Path("data/processed/valid")
QUARANTINE_DIR = Path("data/processed/quarantine")

BATCH_SIZE = 250_000


def process_file(path, valid_dir=VALID_DIR, quarantine_dir=QUARANTINE_DIR): 
    parquet = pq.ParquetFile(path)
    original_schema = parquet.schema_arrow
    quarantine_schema = original_schema.append(
        pa.field("quarantine_reason", pa.string())
    )

    valid_dir.mkdir(parents=True, exist_ok=True)
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    valid_path = valid_dir / path.name
    quarantine_path = quarantine_dir / path.name

    total_rows = 0
    total_valid = 0
    total_quarantined = 0

    # One writer per output file; write each batch incrementally.
    with (
        pq.ParquetWriter(valid_path, original_schema) as valid_writer,
        pq.ParquetWriter(quarantine_path, quarantine_schema) as quarantine_writer,
    ):
        for batch in parquet.iter_batches(batch_size=BATCH_SIZE):
            df = batch.to_pandas()
            total_rows += len(df)

            pickup = df["tpep_pickup_datetime"]
            dropoff = df["tpep_dropoff_datetime"]
            distance = df["trip_distance"]
            passengers = df["passenger_count"]

            invalid_duration = (
                pickup.isna()
                | dropoff.isna()
                | (dropoff <= pickup)
            )

            invalid_distance = (
                distance.isna()
                | (distance < 0)
            )

            invalid_passengers = (
                passengers.isna()
                | (passengers <= 0)
            )

            invalid_any = (
                invalid_duration
                | invalid_distance
                | invalid_passengers
            )

            # Save records passing every rule.
            valid_df = df.loc[~invalid_any]
            valid_table = pa.Table.from_pandas(
                valid_df,
                schema=original_schema,
                preserve_index=False,
            )
            valid_writer.write_table(valid_table)
            total_valid += len(valid_df)

            # Save rejected records with explicit reasons.
            quarantine_df = df.loc[invalid_any].copy()

            if not quarantine_df.empty:
                reasons = pd.DataFrame(
                    {
                        "invalid_duration": invalid_duration.loc[invalid_any],
                        "invalid_distance": invalid_distance.loc[invalid_any],
                        "invalid_passenger_count": (
                            invalid_passengers.loc[invalid_any]
                        ),
                    },
                    index=quarantine_df.index,
                )

                quarantine_df["quarantine_reason"] = reasons.apply(
                    lambda row: ", ".join(
                        row.index[row.to_numpy()]
                    ),
                    axis=1,
                )

                quarantine_table = pa.Table.from_pandas(
                    quarantine_df,
                    schema=quarantine_schema,
                    preserve_index=False,
                )
                quarantine_writer.write_table(quarantine_table)
                total_quarantined += len(quarantine_df)

    print(f"\nFile: {path.name}")
    print(f"Input rows: {total_rows:,}")
    print(f"Valid rows: {total_valid:,}")
    print(f"Quarantined rows: {total_quarantined:,}")

    assert total_rows == total_valid + total_quarantined


def main():
    VALID_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.parquet"))

    if not files:
        raise FileNotFoundError(
            f"No Parquet files found in {RAW_DIR.resolve()}"
        )

    for path in files:
        process_file(path)

    print("\nProcessing completed.")


if __name__ == "__main__":
    main()
