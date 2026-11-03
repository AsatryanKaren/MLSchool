"""Regression checks for both metric meaning and the displayed KPI."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from dashboard_server import dashboard_data
from city_metrics.metrics import fixed_mix_delay


def test_incident_preserves_observed_delay_and_standardizes_route_performance():
    days = dashboard_data()['days']
    yesterday, today = days['yesterday'], days['today']
    assert (yesterday['overall'], today['overall']) == (2.8, 8.2)
    assert (yesterday['fixed_mix'], today['fixed_mix']) == (2.8, 1.8)
    assert (today['fixed_mix'] / yesterday['fixed_mix'] - 1) * 100 == pytest.approx(-35.7142857)
    assert yesterday['routes']['A']['count'] == today['routes']['B']['count'] == 90


def test_fixed_mix_is_invariant_to_current_trip_shares():
    weights = {'A': 90, 'B': 10}
    trips = [{'route': 'A', 'delay_min': 1}, {'route': 'B', 'delay_min': 9}]
    assert fixed_mix_delay(trips, weights) == fixed_mix_delay(trips[:1] * 90 + trips[1:] * 10, weights)


def test_dashboard_renders_fixed_mix_and_handles_change_directions():
    node = shutil.which('node')
    if not node:
        pytest.skip('Node.js is needed to execute the dashboard JavaScript')
    html = (Path(__file__).resolve().parents[1] / 'dashboard/index.html').read_text()
    script = html.split('<script>')[1].split('</script>')[0]
    harness = r'''
const assert = require('node:assert/strict');
const elements = new Map();
global.document = {getElementById(id) {
  if (!elements.has(id)) elements.set(id, {textContent:'',value:'fixed_mix',addEventListener(){}});
  return elements.get(id);
}};
global.fetch = async () => ({json:async () => (PAYLOAD)});
'''.replace('PAYLOAD', json.dumps(dashboard_data()))
    checks = r'''
setImmediate(() => {
  assert.equal(el('y').textContent, '2.8 min');
  assert.equal(el('t').textContent, '1.8 min');
  assert.equal(el('change').textContent, '-36%');
  assert.equal(el('change').className, 'value green');
  assert.equal(el('observed').textContent, '2.8 min → 8.2 min');
  assert.equal(el('route-a').textContent, 'Improved');
  el('metric').value='overall'; update();
  assert.equal(el('alt-t').textContent, '8.2 min');
  showChange('change', 2, 3, true);
  assert.equal(el('change').textContent, '+50%');
  assert.equal(el('change').className, 'value red');
  showChange('change', 2, 2, true);
  assert.equal(el('change').textContent, '0%');
  showChange('change', 0, 1, true);
  assert.equal(el('change').textContent, 'N/A (zero baseline)');
});
'''
    result = subprocess.run([node, '-e', harness + script + checks], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

