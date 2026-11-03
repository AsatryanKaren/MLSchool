"""Aggregation methods for transit delay metrics."""
from collections import defaultdict


def trip_weighted_delay(trips):
    """Average delay of a randomly selected trip (minutes)."""
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


def equal_route_delay(trips):
    """Average of route means; each active route has equal weight."""
    means = route_means(trips)
    if not means:
        raise ValueError('No trips available')
    return sum(item['mean'] for item in means.values()) / len(means)


def fixed_mix_delay(trips, baseline_weights):
    """Route-standardized delay using a fixed reference mix.

    Requires observations for every route in the reference mix.
    """
    if not baseline_weights or any(weight < 0 for weight in baseline_weights.values()):
        raise ValueError('Invalid reference weights')
    total = sum(baseline_weights.values())
    if total <= 0:
        raise ValueError('Reference weights must sum to a positive number')
    means = route_means(trips)
    missing = set(baseline_weights) - set(means)
    if missing:
        raise ValueError(f'Missing routes: {sorted(missing)}')
    return sum(means[route]['mean'] * weight for route, weight in baseline_weights.items()) / total
