
from pathlib import Path
import pyarrow.parquet as pq

DATA_DIR = Path("data/raw")

parquet_files = sorted(DATA_DIR.glob("*.parquet"))

if not parquet_files:
    raise FileNotFoundError(
        f"No Parquet files found in {DATA_DIR.resolve()}"
    )

for file_path in parquet_files:
    parquet_file = pq.ParquetFile(file_path)
    metadata = parquet_file.metadata
    schema = parquet_file.schema_arrow

    print("\n" + "=" * 60)
    print(f"File: {file_path.name}")
    print(f"Size: {file_path.stat().st_size / (1024**2):.2f} MB")
    print(f"Rows: {metadata.num_rows:,}")
    print(f"Columns: {len(schema)}")

    print("\nSchema:")
    for field in schema:
        print(f"  {field.name}: {field.type}")
