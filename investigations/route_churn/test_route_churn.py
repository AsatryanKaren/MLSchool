"""Characterization tests: record current behavior, not a proposed product contract."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest
import dashboard_server
from city_metrics.io import load_trips, by_day
from city_metrics.metrics import route_means, trip_weighted_delay, equal_route_delay, fixed_mix_delay

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/trips.csv'


@pytest.fixture
def launch(tmp_path, monkeypatch):
    original = SOURCE.read_bytes()
    records = load_trips(SOURCE)
    # A temporary CSV is the only input changed; production reads it via patched ROOT.
    (tmp_path / 'data').mkdir()
    target = tmp_path / 'data/trips.csv'
    import csv
    with target.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['day', 'route', 'delay_min'])
        writer.writeheader()
        writer.writerows(records + [{'day': 'today', 'route': 'C', 'delay_min': 30}] * 50)
    monkeypatch.setattr(dashboard_server, 'ROOT', tmp_path)
    yield load_trips(target), dashboard_server.dashboard_data()
    assert hashlib.sha256(SOURCE.read_bytes()).digest() == hashlib.sha256(original).digest()


def test_all_metrics_and_coverage(launch):
    records, payload = launch
    y, t = payload['days']['yesterday'], payload['days']['today']
    assert (y['trip_count'], t['trip_count']) == (100, 150)
    assert t['routes'] == {'A': {'mean': 1, 'count': 10}, 'B': {'mean': 9, 'count': 90}, 'C': {'mean': 30, 'count': 50}}
    assert (y['overall'], t['overall']) == (2.8, 15.467)
    assert (y['equal_route'], t['equal_route']) == (6, 13.333)
    assert (y['fixed_mix'], t['fixed_mix']) == (2.8, 1.8)
    today = by_day(records, 'today')
    assert trip_weighted_delay(today) == pytest.approx(2320 / 150)
    assert equal_route_delay(today) == pytest.approx(40 / 3)
    assert (trip_weighted_delay(today) / 2.8 - 1) * 100 == pytest.approx(452.38095238)
    assert (equal_route_delay(today) / 6 - 1) * 100 == pytest.approx(122.22222222)
    assert sum(t['routes'][r]['count'] for r in y['routes']) / t['trip_count'] == pytest.approx(2 / 3)


def test_new_route_is_invisible_to_fixed_mix_even_if_extreme(launch):
    records, _ = launch
    today = by_day(records, 'today')
    for delay in (0, 30, 3000):
        changed = [dict(r, delay_min=delay) if r['route'] == 'C' else r for r in today]
        assert fixed_mix_delay(changed, {'A': 90, 'B': 10}) == 1.8
    with pytest.raises(ValueError, match='Missing routes'):
        fixed_mix_delay(by_day(records, 'yesterday'), {'A': 10, 'B': 90, 'C': 50})


@pytest.mark.parametrize('removed', ['A', 'B'])
def test_removed_reference_route_breaks_entire_api(launch, monkeypatch, removed):
    records, _ = launch
    remaining = [r for r in records if not (r['day'] == 'today' and r['route'] == removed)]
    today = by_day(remaining, 'today')
    assert removed not in route_means(today)
    assert trip_weighted_delay(today) > 0
    assert equal_route_delay(today) > 0
    monkeypatch.setattr(dashboard_server, 'load_trips', lambda _: remaining)
    with pytest.raises(ValueError, match='Missing routes'):
        dashboard_server.dashboard_data()


def test_empty_and_zero_weight_boundaries():
    assert route_means([]) == {}
    for metric in (trip_weighted_delay, equal_route_delay):
        with pytest.raises(ValueError, match='No trips'):
            metric([])
    # Even an absent zero-weight route is required by current implementation.
    with pytest.raises(ValueError, match='Missing routes'):
        fixed_mix_delay([{'route': 'A', 'delay_min': 1}], {'A': 1, 'C': 0})
    with pytest.raises(ValueError):
        fixed_mix_delay([], {})


def test_actual_javascript_hides_c_but_includes_it_in_aggregate(launch):
    _, payload = launch
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js required for actual dashboard renderer')
    script = (ROOT / 'dashboard/index.html').read_text().split('<script>')[1].split('</script>')[0]
    harness = '''
const assert = require('node:assert/strict');
const elements = new Map();
global.document = {getElementById(id) {
 if (!elements.has(id)) elements.set(id, {textContent:'', innerHTML:'', value:'fixed_mix', addEventListener(){}});
 return elements.get(id);
}};
global.fetch = async () => ({json:async () => (PAYLOAD)});
'''.replace('PAYLOAD', json.dumps(payload))
    checks = '''
setImmediate(() => {
 assert.equal(el('change').textContent, '-36%');
 assert.equal(el('status').textContent, '-1.0 min');
 assert.equal(el('observed').textContent, '2.8 min → 15.5 min');
 for (const id of ['chart', 'rows']) {
  assert.ok(el(id).innerHTML.includes('Route A'));
  assert.ok(el(id).innerHTML.includes('Route B'));
  assert.ok(!el(id).innerHTML.includes('Route C'));
 }
 assert.equal(el('route-a').textContent, 'Improved');
 assert.equal(el('route-b').textContent, 'Improved');
 el('metric').value='overall'; update();
 assert.equal(el('alt-t').textContent, '15.5 min');
 el('metric').value='equal_route'; update();
 assert.equal(el('alt-t').textContent, '13.3 min');
 el('metric').value='fixed_mix'; update();
 assert.equal(el('alt-t').textContent, '1.8 min');
});
'''
    result = subprocess.run([node, '-e', harness + script + checks], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


if __name__ == '__main__':
    trips = load_trips(SOURCE) + [{'day': 'today', 'route': 'C', 'delay_min': 30}] * 50
    weights = {r: v['count'] for r, v in route_means(by_day(trips, 'yesterday')).items()}
    for day in ('yesterday', 'today'):
        rows = by_day(trips, day)
        print(day, 'trips=', len(rows), 'routes=', route_means(rows))
        print('observed=', trip_weighted_delay(rows), 'equal_route=', equal_route_delay(rows), 'fixed_mix=', fixed_mix_delay(rows, weights))
