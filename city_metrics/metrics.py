"""Aggregation methods for transit delay metrics."""
from collections import defaultdict


def trip_weighted_delay(trips):
    """Average delay per trip (minutes)."""
    if not trips:
        raise ValueError('No trips available')
    return sum(trip['delay_min'] for trip in trips) / len(trips)


def route_means(trips):
    """Average delay per route, along with the number of trips."""
    grouped = defaultdict(list)
    for trip in trips:
        grouped[trip['route']].append(trip['delay_min'])
    return {
        route: {'mean': sum(values) / len(values), 'count': len(values)}
        for route, values in sorted(grouped.items())
    }
