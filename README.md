# CityPulse

City transport reliability metrics: average trip delay per day and per route.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 main.py
python3 -m pytest -q
```

## Dashboard

```bash
python3 dashboard_server.py
```

Open http://localhost:8000. The page reads `GET /api/metrics`, which loads
`data/trips.csv` and uses the `city_metrics` functions. Restart the server
after changing Python code. Stop it with Ctrl+C.

## Files
- `main.py`: print daily metrics.
- `city_metrics/metrics.py`: delay aggregation.
- `city_metrics/io.py`: CSV input.
- `data/trips.csv`: trip observations.
- `dashboard_server.py`, `dashboard/index.html`: local dashboard.
- `tests/test_metrics.py`: unit tests.
