# Scorecard

Run 2026-10-22 at commit `c71f59c` by `scripts/evaluate.py`. CI fails when any number with a direction is worse than in the committed `docs/scorecard.json`.

## Reference acceptance tests

`tests/test_reference_chart.py` and `tests/test_ephemeris_reference.py`: 25 passed, 0 failed, 0 skipped.

## Phase 0 cross-check

1,000 births (seed 0) against PyJHora 4.8.7, ephemeris Moshier (no ephemeris files), in 7 s: 0 beyond the 1″ / one-day gate, 0 listed at an edge. Per-quantity maxima and means are in the table; docs/crosscheck.md has the full report.

## Metamorphic tests

`tests/test_metamorphic.py`: 17 passed, 0 failed, 2 skipped (the narration-side invariants are live only).

## Checker benchmark (offline)

119 rows; the validator alone: precision 1.000, recall 0.216, F1 0.356; 15 of 15 tag and wording errors caught; 0 accepted sentences rejected. The semantic categories are the checker's, and the checker needs the API.

## Placement generator check

`scripts/make_placements.py --check`: 0 file(s) differ from scripts/placements.csv.

## Every number

| number | value | unit | better |
| --- | --- | --- | --- |
| `reference.passed` | 25 |  | higher |
| `reference.failed` | 0 |  | lower |
| `crosscheck.max.longitude Sun` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Sun` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Moon` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Moon` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Mars` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Mars` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Mercury` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Mercury` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Jupiter` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Jupiter` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Venus` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Venus` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Saturn` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Saturn` | 0.0 | arc-seconds | lower |
| `crosscheck.max.longitude Rahu` | 0.000133611 | arc-seconds | lower |
| `crosscheck.mean.longitude Rahu` | 1.8051e-05 | arc-seconds | lower |
| `crosscheck.max.longitude Ketu` | 0.000133611 | arc-seconds | lower |
| `crosscheck.mean.longitude Ketu` | 1.8051e-05 | arc-seconds | lower |
| `crosscheck.max.longitude Asc` | 0.0 | arc-seconds | lower |
| `crosscheck.mean.longitude Asc` | 0.0 | arc-seconds | lower |
| `crosscheck.max.mahadasha start (days)` | 0.0 | days | lower |
| `crosscheck.mean.mahadasha start (days)` | 0.0 | days | lower |
| `crosscheck.beyond_gate` | 0 |  | lower |
| `crosscheck.listed_at_edges` | 0 |  | informational |
| `crosscheck.births` | 1000 |  | informational |
| `metamorphic.passed` | 17 |  | higher |
| `metamorphic.failed` | 0 |  | lower |
| `metamorphic.seed_agreement.reference` | 0.9912 |  | higher |
| `metamorphic.changed_at_one_minute.reference` | 2 |  | informational |
| `metamorphic.seed_agreement.synthetic-1` | 0.9956 |  | higher |
| `metamorphic.changed_at_one_minute.synthetic-1` | 5 |  | informational |
| `metamorphic.seed_agreement.synthetic-2` | 1.0 |  | higher |
| `metamorphic.changed_at_one_minute.synthetic-2` | 4 |  | informational |
| `metamorphic.seed_agreement.synthetic-3` | 1.0 |  | higher |
| `metamorphic.changed_at_one_minute.synthetic-3` | 2 |  | informational |
| `checker.validator.precision` | 1.0 |  | higher |
| `checker.validator.recall` | 0.2162 |  | higher |
| `checker.validator.f1` | 0.3556 |  | higher |
| `checker.validator.wording_caught_share` | 1.0 |  | higher |
| `checker.validator.false_rejects` | 0 |  | lower |
| `checker.bench_rows` | 119 |  | informational |
| `checker.tests_failed` | 0 |  | lower |
| `placements.files_differing_from_table` | 0 |  | lower |

## Skips and what is blocked

- metamorphic: tests/test_metamorphic.py:165: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- metamorphic: tests/test_metamorphic.py:182: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- checker benchmark: tests/test_checker_bench.py:93: set JYOTISH_LIVE_NARRATION=1 to call the API
- checker benchmark, validator + live checker: no Anthropic credentials here; the live run (JYOTISH_LIVE_NARRATION=1, marked live) writes its numbers to docs/checker_scorecard.md

