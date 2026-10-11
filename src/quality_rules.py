
def valid_trip_duration(pickup, dropoff):
    """Return True when drop-off occurs after pickup."""
    return pickup is not None and dropoff is not None and dropoff > pickup


def valid_trip_distance(distance):
    """Return True when distance is present and non-negative."""
    return distance is not None and distance >= 0


def valid_passenger_count(passengers):
    """Return True when passenger count is positive."""
    return passengers is not None and passengers > 0
