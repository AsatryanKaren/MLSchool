"""Tiny local dashboard server using only Python's standard library."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from city_metrics.io import load_trips, by_day
from city_metrics.metrics import trip_weighted_delay, route_means, equal_route_delay, fixed_mix_delay

ROOT = Path(__file__).resolve().parent


def dashboard_data():
    trips = load_trips(ROOT / 'data' / 'trips.csv')
    yesterday = by_day(trips, 'yesterday')
    today = by_day(trips, 'today')
    weights = {name: info['count'] for name, info in route_means(yesterday).items()}
    return {
        'days': {
            name: {
                'overall': round(trip_weighted_delay(records), 3),
                'equal_route': round(equal_route_delay(records), 3),
                'fixed_mix': round(fixed_mix_delay(records, weights), 3),
                'routes': route_means(records),
                'trip_count': len(records),
            }
            for name, records in [('yesterday', yesterday), ('today', today)]
        }
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/metrics':
            content = json.dumps(dashboard_data()).encode('utf-8')
            mime = 'application/json; charset=utf-8'
        elif path in ('/', '/index.html'):
            content = (ROOT / 'dashboard' / 'index.html').read_bytes()
            mime = 'text/html; charset=utf-8'
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    print('Dashboard ready: http://localhost:8000', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
