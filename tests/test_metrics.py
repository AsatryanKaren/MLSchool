import pytest
from city_metrics.metrics import trip_weighted_delay, route_means, equal_route_delay, fixed_mix_delay


def test_average_single_route():
    trips = [{'route': 'A', 'delay_min': 2}, {'route': 'A', 'delay_min': 4}]
    assert trip_weighted_delay(trips) == 3


def test_route_means():
    trips = [{'route': 'A', 'delay_min': 1}, {'route': 'B', 'delay_min': 9}]
    assert route_means(trips)['B'] == {'mean': 9, 'count': 1}


def test_empty_data_is_rejected():
    with pytest.raises(ValueError):
        trip_weighted_delay([])


def test_equal_route_vs_trip_weighted_are_not_equivalent():
    trips = [{'route': 'A', 'delay_min': 1}] * 9 + [{'route': 'B', 'delay_min': 9}]
    assert trip_weighted_delay(trips) == 1.8
    assert equal_route_delay(trips) == 5


def test_fixed_mix_requires_all_reference_routes():
    with pytest.raises(ValueError, match='Missing routes'):
        fixed_mix_delay([{'route': 'A', 'delay_min': 1}], {'A': 9, 'B': 1})


def test_fixed_mix_rejects_invalid_weights():
    with pytest.raises(ValueError):
        fixed_mix_delay([{'route': 'A', 'delay_min': 1}], {'A': -1})
