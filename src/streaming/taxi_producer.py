
import json
import time
from datetime import date, datetime
from pathlib import Path

import pyarrow.parquet as pq
from kafka import KafkaProducer


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = PROJECT_ROOT / "data" / "raw" / "yellow_tripdata_2016-01.parquet"

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "127.0.0.1:9092"
KAFKA_TOPIC = "taxi-trips"

# Controlled test settings
MAX_MESSAGES = 100
MESSAGES_PER_SECOND = 10
BATCH_SIZE = 50


def json_serializer(value):
    """Convert a Python dictionary into UTF-8 JSON bytes."""
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def normalize_value(value):
    """Convert PyArrow values into JSON-compatible Python values."""
    if value is None:
        return None
    if hasattr(value, "as_py"):
        value = value.as_py()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Parquet file not found: {DATA_FILE}")

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        acks="all",
        retries=5,
    )

    sent_count = 0
    delay = 1 / MESSAGES_PER_SECOND

    try:
        parquet_file = pq.ParquetFile(DATA_FILE)

        for batch in parquet_file.iter_batches(batch_size=BATCH_SIZE):
            for row in batch.to_pylist():
                event = {
                    key: normalize_value(value)
                    for key, value in row.items()
                }

                producer.send(KAFKA_TOPIC, value=event)
                sent_count += 1

                if sent_count % 10 == 0:
                    producer.flush()
                    print(f"Sent {sent_count} messages")

                time.sleep(delay)

                if sent_count >= MAX_MESSAGES:
                    break

            if sent_count >= MAX_MESSAGES:
                break

        producer.flush()
        print(f"Finished. Total messages sent: {sent_count}")

    finally:
        producer.close()


if __name__ == "__main__":
    main()
