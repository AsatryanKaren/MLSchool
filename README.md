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
