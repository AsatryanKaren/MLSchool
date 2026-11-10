from pathlib import Path
from city_metrics.io import load_trips, by_day
from city_metrics.metrics import trip_weighted_delay, route_means

trips = load_trips(Path(__file__).parent / 'data' / 'trips.csv')
yesterday = by_day(trips, 'yesterday')
today = by_day(trips, 'today')

for label, records in [('Yesterday', yesterday), ('Today', today)]:
    print(f'\n{label}:')
    print('  Per-route:', route_means(records))
    print(f'  Average delay per trip: {trip_weighted_delay(records):.1f} min')
