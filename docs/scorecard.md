# Scorecard

Run 2026-10-23 at commit `4699460` by `scripts/evaluate.py`. CI fails when any gated number is worse than in the committed `docs/scorecard.json`; a sampled statistic is reported with its direction and not gated.

## Reference acceptance tests

`tests/test_reference_chart.py` and `tests/test_ephemeris_reference.py`: 25 passed, 0 failed, 0 skipped.

## Phase 0 cross-check

1,000 births (seed 0) against PyJHora 4.8.7, ephemeris Moshier (no ephemeris files), in 8 s: 0 beyond the 1″ / one-day gate, 0 listed at an edge. Per-quantity maxima and means are in the table; docs/crosscheck.md has the full report.

## Metamorphic tests

`tests/test_metamorphic.py`: 17 passed, 0 failed, 2 skipped (the narration-side invariants are live only).

## Checker benchmark

119 rows; the validator alone: precision 1.000, recall 0.243, F1 0.391; 17 of 17 tag and wording errors caught; 0 accepted sentences rejected. The semantic categories are the checker's. The live run on record (docs/checker_scorecard.md, 2026-10-22 at `b0eb697`, model claude-opus-5-5, checker effort high): 72 of 74 bad sentences caught, precision 1.000, recall 0.973, F1 0.986. The harness does not re-run it (API calls), so it is reported, not gated.

## Placement generator check

`scripts/make_placements.py --check`: 0 file(s) differ from scripts/placements.csv.

## Synthetic validation (the pipeline, not the engine)

Planted, N = 2,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 0.41, recovered 0.38 (p < 0.05), 0.38 surviving BH; the timing effect recovered in 1.00; 23 s.
Null, N = 2,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 7 s.
Planted, N = 20,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 1.00, recovered 1.00 (p < 0.05), 1.00 surviving BH; the timing effect recovered in 1.00; 220 s. Gated check: at least three quarters of the planted areas recovered, surviving BH and timing-recovered: passes.
Null, N = 20,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 71 s. Gated check: at most one area and three rules survive: passes.
The shares and counts are sampled statistics and are reported, not gated: the planted events are drawn from the engine's own scores, so any change to scoring redraws them. The two pass/fail checks at N = 20,000, where the planted effect is near-certain, gate.
Each run's full report: docs/validation_synthetic_<mode>_<n>.md (every heading says synthetic).

## Every number

| number | value | unit | better | gates CI |
| --- | --- | --- | --- | --- |
| `reference.passed` | 25 |  | higher | yes |
| `reference.failed` | 0 |  | lower | yes |
| `crosscheck.max.longitude Sun` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Sun` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Moon` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Moon` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Mars` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Mars` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Mercury` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Mercury` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Jupiter` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Jupiter` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Venus` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Venus` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Saturn` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Saturn` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Rahu` | 0.000133611 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Rahu` | 1.8051e-05 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Ketu` | 0.000133611 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Ketu` | 1.8051e-05 | arc-seconds | lower | yes |
| `crosscheck.max.longitude Asc` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.mean.longitude Asc` | 0.0 | arc-seconds | lower | yes |
| `crosscheck.max.mahadasha start (days)` | 0.0 | days | lower | yes |
| `crosscheck.mean.mahadasha start (days)` | 0.0 | days | lower | yes |
| `crosscheck.beyond_gate` | 0 |  | lower | yes |
| `crosscheck.listed_at_edges` | 0 |  | informational | no |
| `crosscheck.births` | 1000 |  | informational | no |
| `metamorphic.passed` | 17 |  | higher | yes |
| `metamorphic.failed` | 0 |  | lower | yes |
| `metamorphic.seed_agreement.reference` | 0.9912 |  | higher | no |
| `metamorphic.changed_at_one_minute.reference` | 2 |  | informational | no |
| `metamorphic.seed_agreement.synthetic-1` | 0.9956 |  | higher | no |
| `metamorphic.changed_at_one_minute.synthetic-1` | 5 |  | informational | no |
| `metamorphic.seed_agreement.synthetic-2` | 1.0 |  | higher | no |
| `metamorphic.changed_at_one_minute.synthetic-2` | 4 |  | informational | no |
| `metamorphic.seed_agreement.synthetic-3` | 1.0 |  | higher | no |
| `metamorphic.changed_at_one_minute.synthetic-3` | 2 |  | informational | no |
| `checker.validator.precision` | 1.0 |  | higher | no |
| `checker.validator.recall` | 0.2432 |  | higher | no |
| `checker.validator.f1` | 0.3913 |  | higher | no |
| `checker.validator.wording_caught_share` | 1.0 |  | higher | yes |
| `checker.validator.false_rejects` | 0 |  | lower | yes |
| `checker.bench_rows` | 119 |  | informational | no |
| `checker.tests_failed` | 0 |  | lower | yes |
| `checker.live.precision` | 1.0 |  | informational | no |
| `checker.live.recall` | 0.973 |  | informational | no |
| `checker.live.f1` | 0.986 |  | informational | no |
| `placements.files_differing_from_table` | 0 |  | lower | yes |
| `synthetic.planted.2000.predicted_power` | 0.4101 |  | informational | no |
| `synthetic.planted.2000.recovered_share` | 0.375 |  | higher | no |
| `synthetic.planted.2000.survived_bh_share` | 0.375 |  | higher | no |
| `synthetic.planted.2000.recovery_gap` | 0.0351 |  | informational | no |
| `synthetic.planted.2000.timing_recovered_share` | 1.0 |  | higher | no |
| `synthetic.null.2000.areas_surviving_bh` | 0 |  | lower | no |
| `synthetic.null.2000.rules_with_effect` | 0 |  | lower | no |
| `synthetic.planted.20000.predicted_power` | 0.9987 |  | informational | no |
| `synthetic.planted.20000.recovered_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.survived_bh_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.recovery_gap` | 0.0013 |  | informational | no |
| `synthetic.planted.20000.timing_recovered_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.pipeline_recovers` | 1 |  | higher | yes |
| `synthetic.null.20000.areas_surviving_bh` | 0 |  | lower | no |
| `synthetic.null.20000.rules_with_effect` | 0 |  | lower | no |
| `synthetic.null.20000.pipeline_quiet` | 1 |  | higher | yes |

## Skips and what is blocked

- metamorphic: tests/test_metamorphic.py:172: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- metamorphic: tests/test_metamorphic.py:189: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- checker benchmark: tests/test_checker_bench.py:109: set JYOTISH_LIVE_NARRATION=1 to call the API

