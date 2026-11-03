from pathlib import Path
from city_metrics.io import load_trips, by_day
from city_metrics.metrics import trip_weighted_delay, route_means, equal_route_delay, fixed_mix_delay

trips = load_trips(Path(__file__).parent / 'data' / 'trips.csv')
yesterday = by_day(trips, 'yesterday')
today = by_day(trips, 'today')
reference_mix = {route: info['count'] for route, info in route_means(yesterday).items()}

for label, records in [('Yesterday', yesterday), ('Today', today)]:
    print(f'\n{label}:')
    print('  Per-route:', route_means(records))
    print(f'  Trip-weighted average: {trip_weighted_delay(records):.1f} min')
    print(f'  Equal-route average:   {equal_route_delay(records):.1f} min')
    print(f'  Fixed-mix average:     {fixed_mix_delay(records, reference_mix):.1f} min')
