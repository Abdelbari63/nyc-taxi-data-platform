
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from src.process_data import process_file


def test_process_file(tmp_path):
    # Create three artificial taxi records.
    pickup = datetime(2016, 1, 1, 10, 0)

    df = pd.DataFrame({
        "tpep_pickup_datetime": [
            pickup,
            pickup,
            pickup,
        ],
        "tpep_dropoff_datetime": [
            pickup + timedelta(minutes=10),  # Valid
            pickup - timedelta(minutes=5),   # Invalid duration
            pickup + timedelta(minutes=10),  # Invalid passenger count
        ],
        "trip_distance": [2.5, 3.0, 1.0],
        "passenger_count": [2, 1, 0],
    })

    # Save the artificial records as a temporary Parquet file.
    input_file = tmp_path / "test_taxi.parquet"
    pq.write_table(pa.Table.from_pandas(df), input_file)

    valid_dir = tmp_path / "valid"
    quarantine_dir = tmp_path / "quarantine"

    # Run the actual processing function.
    process_file(input_file, valid_dir, quarantine_dir)

    # Read the generated outputs.
    valid = pq.read_table(valid_dir / input_file.name).to_pandas()
    quarantined = pq.read_table(
        quarantine_dir / input_file.name
    ).to_pandas()

    # Verify the expected results.
    assert len(valid) == 1
    assert len(quarantined) == 2

    reasons = quarantined["quarantine_reason"].tolist()
    assert "invalid_duration" in reasons
    assert "invalid_passenger_count" in reasons
