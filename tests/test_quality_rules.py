
from datetime import datetime, timedelta

from src.quality_rules import (
    valid_trip_duration,
    valid_trip_distance,
    valid_passenger_count,
)


def test_valid_trip_duration():
    pickup = datetime(2016, 1, 1, 10, 0)
    dropoff = pickup + timedelta(minutes=15)

    assert valid_trip_duration(pickup, dropoff) is True


def test_invalid_trip_duration():
    pickup = datetime(2016, 1, 1, 10, 0)

    assert valid_trip_duration(pickup, pickup) is False
    assert valid_trip_duration(pickup, pickup - timedelta(minutes=1)) is False


def test_trip_distance():
    assert valid_trip_distance(2.5) is True
    assert valid_trip_distance(0) is True
    assert valid_trip_distance(-1) is False
    assert valid_trip_distance(None) is False


def test_passenger_count():
    assert valid_passenger_count(1) is True
    assert valid_passenger_count(0) is False
    assert valid_passenger_count(-1) is False
    assert valid_passenger_count(None) is False
