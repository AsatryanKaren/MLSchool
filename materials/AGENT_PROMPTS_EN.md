# Agent demonstration prompts

## Prompt 1 — investigate, do not fix prematurely
The city dashboard reports that average delay rose even though the average delay on each route fell. Investigate the repository and reproduce the discrepancy. List at least three competing hypotheses and test them. Do not change any code yet. Cite exact calculations and files.

## Prompt 2 — adversarial review
A teammate suggests changing the dashboard aggregation from trip-weighted mean to equal-route mean because that produces the expected improvement. Evaluate whether this is a bug fix or a change of metric semantics. Provide a counterexample and a regression test.

## Prompt 3 — edge-case challenge
Propose a fixed-reference-mix KPI for comparing route performance across days. What assumptions does it make? What should happen if one of the reference routes is absent on the comparison day? Write a test before changing the implementation.

## Important
Do not claim an agent spontaneously discovered the root cause or proposed the misleading fix unless it actually did so during a documented run. If using a staged branch, identify it as a prepared exercise.
