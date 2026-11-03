# The City That Got Slower When Every Route Got Faster

A small Python investigation for a 90-minute AI-agent workshop.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 main.py
python3 -m pytest -q
```

## Incident ticket (student-facing)

> Each bus route has a lower average delay today than yesterday, but the dashboard's citywide average delay increased. Investigate whether this is a software defect, a data issue, or a metric-definition problem. Explain your conclusion with evidence. Do not change the metric definition without explicit approval.

Acceptance criteria:
1. Reproduce the reported numbers.
2. Explain the apparent contradiction mathematically.
3. Propose which metric(s) answer which question.
4. Demonstrate a test that catches an inappropriate metric change.
5. Explain remaining assumptions and limitations.

## Files
- `main.py`: run the investigation.
- `city_metrics/metrics.py`: candidate aggregation methods.
- `city_metrics/io.py`: CSV input.
- `data/trips.csv`: reproducible synthetic trip observations.
- `tests/test_metrics.py`: basic tests.
- `materials/`: speaker notes and investigation script.

The repository includes several metric definitions for teaching. In the live demo, reveal these progressively; don't expose the answer file at the start.

## Interactive dashboard (no Node.js or extra Python packages required)

From the project root, run:

```bash
python3 dashboard_server.py
```

Open **http://localhost:8000** in your browser. The dashboard fetches live calculations from `GET /api/metrics`, which reads `data/trips.csv` and uses the same `city_metrics` Python functions as the CLI and tests. Click **Reveal trip counts** only after students have proposed hypotheses; then compare metric definitions. Stop the server with Ctrl+C.

If you edit the CSV or Python metrics code, refresh the browser to see the recalculated results. The HTML/CSS/JS lives in `dashboard/index.html`; no React build step is needed for this teaching demo.

## Dashboard KPI correction

The headline now measures **route performance at yesterday's trip mix** using
`fixed_mix`; the API's `overall` remains the observed per-trip mean.
For the fixture, route A improves from 2 to 1 minute and B from 10 to 9,
but A's trip share falls from 90% to 10%. The observed mean therefore rises
from `0.9*2 + 0.1*10 = 2.8` to `0.1*1 + 0.9*9 = 8.2` (+193%).
Holding yesterday's weights constant gives `0.9*1 + 0.1*9 = 1.8` today,
a 35.7% reduction. The dashboard labels this reference explicitly and keeps
observed delay and trip counts visible. Equal weighting would answer a different
question and discard the baseline trip distribution.

This product request authorizes the explicitly labeled route-performance KPI;
the original workshop ticket above describes the investigation exercise.
Yesterday is the reference for this two-day comparison, not a permanent benchmark
for longer time series. Every baseline route needs current observations (the
existing function rejects missing routes); new routes do not enter the fixed
reference. Observed trips are not passenger-weighted, and these figures alone
do not establish why traffic shifted or prove a causal service improvement.

Run `python3 -m pytest -q` for metric and dashboard regression checks. The
JavaScript rendering test uses Node.js when installed (otherwise it is skipped).
