import pytest
from city_metrics.metrics import trip_weighted_delay, route_means


def test_average_single_route():
    trips = [{'route': 'A', 'delay_min': 2}, {'route': 'A', 'delay_min': 4}]
    assert trip_weighted_delay(trips) == 3


def test_route_means():
    trips = [{'route': 'A', 'delay_min': 1}, {'route': 'B', 'delay_min': 9}]
    assert route_means(trips)['B'] == {'mean': 9, 'count': 1}


def test_empty_data_is_rejected():
    with pytest.raises(ValueError):
        trip_weighted_delay([])
