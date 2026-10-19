
import json
import time
from datetime import date, datetime
from pathlib import Path

import pyarrow.parquet as pq
from confluent_kafka import Producer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "yellow_tripdata_2016-01.parquet"
)
CONFIG_FILE = (
    PROJECT_ROOT
    / "src"
    / "streaming"
    / "ccloud-python-client"
    / "client.properties"
)

# Kafka configuration
KAFKA_TOPIC = "taxi-trips"

# Controlled test settings
MAX_MESSAGES = 100
MESSAGES_PER_SECOND = 10
BATCH_SIZE = 50


def read_config():
    """Load Kafka credentials from the local properties file."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Kafka configuration not found: {CONFIG_FILE}"
        )

    config = {}
    with CONFIG_FILE.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    return config


def normalize_value(value):
    """Convert values to JSON-compatible Python types."""
    if value is None:
        return None

    if hasattr(value, "as_py"):
        value = value.as_py()

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    return value


def delivery_report(error, message):
    """Report failed deliveries."""
    if error is not None:
        print(f"Delivery failed: {error}")


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {DATA_FILE}"
        )

    config = read_config()
    producer = Producer(config)

    sent_count = 0
    delay = 1 / MESSAGES_PER_SECOND

    try:
        parquet_file = pq.ParquetFile(DATA_FILE)

        for batch in parquet_file.iter_batches(
            batch_size=BATCH_SIZE
        ):
            for row in batch.to_pylist():
                event = {
                    key: normalize_value(value)
                    for key, value in row.items()
                }

                producer.produce(
                    KAFKA_TOPIC,
                    key=str(sent_count + 1),
                    value=json.dumps(event).encode("utf-8"),
                    callback=delivery_report,
                )

                sent_count += 1
                producer.poll(0)

                if sent_count % 10 == 0:
                    print(f"Submitted {sent_count} messages")

                time.sleep(delay)

                if sent_count >= MAX_MESSAGES:
                    break

            if sent_count >= MAX_MESSAGES:
                break

        remaining = producer.flush(30)

        if remaining:
            print(f"Warning: {remaining} messages remain undelivered.")
        else:
            print(
                f"Finished. {sent_count} messages submitted "
                "and delivery queue drained."
            )

    finally:
        producer.flush(10)


if __name__ == "__main__":
    main()
