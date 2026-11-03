# Route C launch investigation

## Conclusion

The 36% improvement is mathematically correct for yesterday's A/B trip mix, but it is not a reliable summary of current city service. C is excluded from the headline and, more seriously, from the chart and trip table that should explain it. Observed delay includes C. The dashboard therefore presents aggregates and route evidence with different, undisclosed coverage.

No production code or original CSV was changed. The tests create a temporary CSV with all original rows plus 50 today/C/30 rows and redirect the server's input root only inside pytest. Specifying every C trip as 30 is a synthetic realization of the supplied mean; it makes no claim about real delay variability. All existing metrics depend only on counts and means.

## Reproduce

From the repository root:

```sh
.venv/bin/python -m pytest -q tests investigations/route_churn
PYTHONPATH=. .venv/bin/python investigations/route_churn/test_route_churn.py
```

If setting up a fresh environment, create a virtual environment and install `requirements.txt` first. Node.js is required for the actual JavaScript rendering test; pytest explicitly skips that check if unavailable. In this investigation Node was available: **15 passed, no skips**. System `python3` lacked pytest; the repository virtual environment was used.

These are characterization tests that intentionally assert existing defects, not acceptance criteria for a future fix. Change them when an approved contract changes. The renderer test executes the unmodified inline script against a minimal DOM stub, not a browser layout or HTTP integration test. The missing-route test proves the API function raises; the handler has no exception recovery, so it cannot return a successful metrics payload in that case.

## Inputs and calculations

| Route | Yesterday trips | Yesterday mean | Today trips | Today mean |
|---|---:|---:|---:|---:|
| A | 90 | 2 | 10 | 1 |
| B | 10 | 10 | 90 | 9 |
| C | 0 (not launched) | N/A | 50 | 30 |
| Total | 100 | | 150 | |

An absent route has no observed mean; it does not have a zero-minute mean.

| Metric | Yesterday | Today | Relative change | Meaning |
|---|---:|---:|---:|---|
| Observed per-trip delay | 2.8 | 15.466667 | +452.380952% | Average of actual recorded trips each day |
| Equal-active-route delay | 6 | 13.333333 | +122.222222% | Average route mean among each day's observed routes |
| Yesterday-mix delay | 2.8 | 1.8 | −35.714286% | A/B delay weighted 90%/10% on both days |
| Recorded trips | 100 | 150 | +50% | Volume, not punctuality |

All delay values are minutes. Percentage change is `(today / yesterday - 1) * 100`, using unrounded values.

- Yesterday delay total: `90*2 + 10*10 = 280`; observed mean `280/100 = 2.8`.
- Today delay total: `10*1 + 90*9 + 50*30 = 2320`; observed mean `2320/150`.
- Equal-route means: `(2+10)/2 = 6`; `(1+9+30)/3 = 40/3`.
- Fixed mix: `(90*2+10*10)/100 = 2.8`; `(90*1+10*9)/100 = 1.8`. C has no reference weight.
- C is 1/3 of today's trips, 1/3 of active routes, and `1500/2320 = 64.655%` of today's total recorded trip-delay minutes.
- The headline covers 100% of reference weight but only `100/150 = 66.667%` of current trips and 2/3 of active routes. Reference completeness is not network coverage.
- Without C, today's observed mean is 8.2. Including it raises today's mean by `15.466667-8.2 = 7.266667` minutes. A descriptive decomposition is `15.466667-2.8 = (1.8-2.8) + (8.2-1.8) + (15.466667-8.2)` = performance −1, A/B mix +6.4, launch/composition +7.266667. This decomposition depends on ordering and is not causal attribution.

## Current behavior and assumptions that break

`city_metrics/metrics.py`:

- `route_means` includes C with count 50 and mean 30; a removed/unobserved route disappears. Empty input yields an empty dictionary. It does not distinguish launch, closure, cancellation, and missing telemetry.
- `trip_weighted_delay` includes every observed trip. Launches and removals change its population and weights. It correctly answers an experience-per-recorded-trip question; it cannot separate within-route change from composition. It rejects empty input. Recorded trips need not represent scheduled service or passengers.
- `equal_route_delay` includes C immediately, equally with A and B. Changing membership changes the denominator, so its trend is not a stable-cohort comparison. Removing a bad route can mechanically improve it. It rejects empty input.
- `fixed_mix_delay` iterates reference keys, silently ignoring all extra routes regardless of their delays or volume. Tests vary C's delay from 0 to 3000 with no headline effect. Missing A or B raises `ValueError`. Even an absent zero-weight reference key raises. Empty/nonpositive reference totals are invalid. Assigning C a positive weight in a union reference makes yesterday uncomputable without a baseline assumption.

`dashboard_server.py`:

- Reference weights are recomputed from the previous day's observed counts, not a separately versioned benchmark. A new route enters the next comparison's reference once it has prior-day observations; daily comparisons then describe changing baskets. They cannot automatically be read as one stable long-term index.
- The API includes C under today's routes and includes all 150 trips in `trip_count`, observed delay, and equal-route delay. Values are rounded to three decimals before reaching the UI; percentages should ideally use full precision with display rounding only.
- If any reference route is absent today, `dashboard_data()` fails as a whole. The handler has no structured missing-data response, so even valid observed/equal-route measures are lost. Empty days also fail. Closure and telemetry outage get identical treatment.

`dashboard/index.html`:

- Headline renders 2.8 → 1.8 and −36% in green; performance status renders −1.0 min. Both A/B statuses say Improved. These statements hold for their restricted population.
- Observed context renders 2.8 → 15.5 min. The selector shows 15.5 observed, 13.3 equal-route, or 1.8 fixed-mix today. Changing the selector does not change the fixed headline.
- Chart and trip table use `Object.keys(a.routes)` (yesterday only). C is absent from both. The visible table sums to 100 today, although the API count is 150. Total counts and excluded share are not shown explicitly. Status cards are hardcoded to A and B.
- A removed route would also break chart/table dereferences if a future API partially returned missing-route data without updating the renderer. Current API failure masks that latent issue.
- Chart height assumes an 11-minute scale; displaying C at 30 with a simple union-only fix would overflow that scale. A renderer change needs missing-value handling and dynamic scaling.
- Percentage handling reports N/A at a zero baseline, but missing metrics are not a supported per-metric state. An API failure is labeled “API unavailable,” hiding whether data or transport failed.

Within-route improvement is descriptive, not proof of an operational intervention: time, direction, trip selection, and passenger mix could change. These synthetic means provide no uncertainty estimate, passenger counts, scheduled/cancelled trips, or target for evaluating C. A new service could improve access while increasing average trip delay; these figures alone do not settle overall welfare.

## Defensible product and engineering options

| Option | Newly launched C | Removed routes | Interpretation / engineering requirements |
|---|---|---|---|
| Observed city experience as headline, fixed mix secondary | Included immediately at actual trip share: 15.47 today | Excluded from observed mean when no trips; closure/cancellation reported separately | Headline answers actual recorded-trip experience. Label composition effects; retain count and coverage. Does not isolate operational performance. |
| Keep restricted fixed-mix headline with explicit scope and coverage | Excluded from comparison; shown as New with mean 30 and count 50; headline says A/B reference performance and 66.7% of today's trips covered | Fixed KPI N/A when a required route is missing; other metrics remain available | Smallest conceptual change. Requires prominent all-trip outcome and launch panel, union route rendering, per-metric status, and explicit exclusion disclosure. Still unsuitable as the sole city headline. |
| Matched-route comparison | C shown separately; excluded until it has observations in both periods | Compare intersection with renormalized reference weights; explicitly list exclusions and reduced coverage | In this case same 1.8 vs 2.8 result. If B disappears, A-only comparison is 2→1 (−50%), not a comparable continuation of −36%. Empty intersection is N/A. Survivor bias can be severe; never silently renormalize. |
| Versioned basket with planned rebasing or chain linking | C stays in launch reporting until an agreed admission/rebase date and valid baseline/overlap | Explicit retirement/rebase policy; missing observations trigger N/A or a separately approved estimation policy | Stable basket aids longer trends. A union basket cannot calculate C yesterday. Rebase when both periods exist, start a new series, or link overlapping comparisons with disclosed methodology. Chain links do not describe one fixed basket and can drift. No backfilled observed mean for C. |
| Target/SLA score for current network, alongside observed delay | Included immediately against an approved launch target; C=30 alone cannot establish pass/fail | Closed routes removed only by service policy; missed scheduled service may need a separate penalty | Supports accountability for all routes without inventing yesterday's C. Requires targets, weighting, launch grace policy, and target-version history. A change in this score is not the existing fixed-mix improvement. |

An equal-route city headline is also possible if the city explicitly values each route equally: C enters at 1/3 weight and gives 13.33 today. It changes the question and remains membership-sensitive; it does not repair fixed-cohort comparability. Passenger weighting is another legitimate experience metric but cannot be computed from this dataset.

Recommended direction for approval: show observed trip experience and service volume prominently, retain a clearly scoped fixed-reference diagnostic, and show every route in the union with New/Closed/No data states and coverage. Preserve missing fixed-mix results as N/A rather than fabricating comparability. This is a proposal only.

## Business decisions required before implementation

1. Choose the outcome and accountable population: experience per trip, per passenger, equally valued routes, stable-route operational performance, access/service provision, or SLA attainment. Decide which is the headline and how to communicate conflicting movements.
2. Decide whether launches belong in city accountability immediately, whether any grace period is justified, and which target can judge them without a prior-period mean. Do not equate absence yesterday with zero delay.
3. Approve benchmark timing, route admission/retirement, identity changes (splits/merges), historical revisions, and whether cross-day comparisons must form a stable time series.
4. Distinguish genuine closures from outages, zero demand, and cancellations using a service registry and expected trip/telemetry data. Define missing-data and minimum coverage/sample policies. This CSV cannot supply those distinctions.
5. Approve any imputation, matched-route renormalization, or target weighting explicitly, including disclosure and audit requirements. Decide whether an incomplete KPI is withheld; valid other measures should remain available.

After those decisions, engineering can implement a versioned metric contract; per-metric value/status/reason metadata; baseline IDs/weights and included/excluded route sets; reference-weight, route, and trip coverage; union-based route rendering with dynamic scale; independent error handling; and monitoring for route churn and coverage loss. Acceptance tests should then cover launches, closures, telemetry gaps, all-new/no-overlap days, empty days, baseline zero, changing references, and approved missing-data policy. No silent zero filling or definition substitution should be introduced.
