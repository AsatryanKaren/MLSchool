"""CSV loader for trip observations."""
import csv
from pathlib import Path


def load_trips(path):
    with Path(path).open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    return [
        {'day': row['day'], 'route': row['route'], 'delay_min': float(row['delay_min'])}
        for row in rows
    ]


def by_day(trips, day):
    return [trip for trip in trips if trip['day'] == day]
