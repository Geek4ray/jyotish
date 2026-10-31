# Scorecard

Run 2026-10-31 at commit `8be2e65` by `scripts/evaluate.py`. CI fails when any gated number is worse than in the committed `docs/scorecard.json`; a sampled statistic is reported with its direction and not gated.

## Reference acceptance tests

`tests/test_reference_chart.py` and `tests/test_ephemeris_reference.py`: 25 passed, 0 failed, 0 skipped.

## Phase 0 cross-check

1,000 births (seed 0) against PyJHora 4.8.7, ephemeris Moshier (no ephemeris files), in 8 s: 0 beyond the 1″ / one-day gate, 0 listed at an edge. Per-quantity maxima and means are in the table; docs/crosscheck.md has the full report.

## Metamorphic tests

`tests/test_metamorphic.py`: 17 passed, 0 failed, 2 skipped (the narration-side invariants are live only).

## Checker benchmark

149 rows; the validator alone: precision 1.000, recall 0.256, F1 0.407; 20 of 20 tag and wording errors caught; 0 accepted sentences rejected. The semantic categories are the checker's. The live run on record (docs/checker_scorecard.md, 2026-10-22 at `b0eb697`, model claude-opus-5-5, checker effort high): 72 of 74 bad sentences caught, precision 1.000, recall 0.973, F1 0.986. The harness does not re-run it (API calls), so it is reported, not gated.

## Placement generator check

`scripts/make_placements.py --check`: 0 file(s) differ from scripts/placements.csv.

## Live narration timings (reported, not gated)

One live reading per stack on the reference chart (docs/live_timings.jsonl; docs/models.md, "Timing"). Each is a single run on a shared provider, so it is reported and never gated.

- deepinfra-gptoss-glm47-c8 (2026-10-26; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-4.7 on api.deepinfra.com, concurrency 8): instant page 2.986 s, first sentence 36.075 s, first verified 67.151 s, first area 1062.886 s, done 2548.879 s; USD 0.401902; 31 claims, 6 gaps.
- deepinfra-gptoss-glm47-c16 (2026-10-26; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-4.7 on api.deepinfra.com, concurrency 16): instant page 2.886 s, first sentence 39.448 s, first verified 70.518 s, first area 606.599 s, done 1214.856 s; USD 0.365069; 33 claims, 4 gaps.
- deepinfra-gptoss-glm53flash-t0 (2026-10-27; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, concurrency 8): instant page 2.939 s, first sentence 31.675 s, first verified 35.242 s, first area 74.306 s, done 308.705 s; USD 0.035917; 35 claims, 2 gaps.
- deepinfra-gptoss-glm47-c8-r2 (2026-10-27; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-4.7 on api.deepinfra.com, concurrency 8): instant page 0.864 s, first sentence 29.696 s, first verified 81.342 s, first area 733.111 s, done 1255.654 s; USD 0.328551; 32 claims, 5 gaps.
- deepinfra-gptoss-glm53flash-t0-single (2026-10-27; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, concurrency 8): instant page 2.944 s, first sentence 85.303 s, first verified None s, first area 510.216 s, done 510.315 s; USD 0.029742; 33 claims, 4 gaps.
- deepinfra-gptoss-glm53flash-t0-live (2026-10-27; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, concurrency 8): instant page 0.857 s, first sentence 18.537 s, first verified 22.873 s, first area 70.493 s, done 310.531 s; USD 0.03379; 35 claims, 2 gaps.

## Synthetic validation (the pipeline, not the engine)

Planted, N = 2,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 0.41, recovered 0.38 (p < 0.05), 0.38 surviving BH; the timing effect recovered in 1.00; 0 of the 3 unplanted areas (father, gains, reputation: they own none of their events) also survive BH, lift inherited through the shared outcome map; 27 s.
Null, N = 2,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 9 s.
Planted, N = 20,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 1.00, recovered 1.00 (p < 0.05), 1.00 surviving BH; the timing effect recovered in 1.00; 3 of the 3 unplanted areas (father, gains, reputation: they own none of their events) also survive BH, lift inherited through the shared outcome map (father, gains, reputation); 236 s. Gated check: at least three quarters of the planted areas recovered, surviving BH and timing-recovered: passes.
Null, N = 20,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 108 s. Gated check: at most one area and three rules survive: passes.
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
| `checker.validator.recall` | 0.2558 |  | higher | no |
| `checker.validator.f1` | 0.4074 |  | higher | no |
| `checker.validator.wording_caught_share` | 1.0 |  | higher | yes |
| `checker.validator.false_rejects` | 0 |  | lower | yes |
| `checker.bench_rows` | 149 |  | informational | no |
| `checker.tests_failed` | 0 |  | lower | yes |
| `checker.live.precision` | 1.0 |  | informational | no |
| `checker.live.recall` | 0.973 |  | informational | no |
| `checker.live.f1` | 0.986 |  | informational | no |
| `placements.files_differing_from_table` | 0 |  | lower | yes |
| `live.deepinfra-gptoss-glm47-c8.instant_s` | 2.986 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.first_sentence_s` | 36.075 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.first_verified_s` | 67.151 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.first_area_s` | 1062.886 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.done_s` | 2548.879 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.cost_usd` | 0.401902 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8.gaps` | 6 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.instant_s` | 2.886 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.first_sentence_s` | 39.448 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.first_verified_s` | 70.518 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.first_area_s` | 606.599 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.done_s` | 1214.856 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.cost_usd` | 0.365069 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c16.gaps` | 4 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.instant_s` | 2.939 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.first_sentence_s` | 31.675 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.first_verified_s` | 35.242 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.first_area_s` | 74.306 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.done_s` | 308.705 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.cost_usd` | 0.035917 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0.gaps` | 2 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.instant_s` | 0.864 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.first_sentence_s` | 29.696 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.first_verified_s` | 81.342 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.first_area_s` | 733.111 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.done_s` | 1255.654 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.cost_usd` | 0.328551 |  | lower | no |
| `live.deepinfra-gptoss-glm47-c8-r2.gaps` | 5 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.instant_s` | 2.944 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.first_sentence_s` | 85.303 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.first_area_s` | 510.216 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.done_s` | 510.315 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.cost_usd` | 0.029742 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-single.gaps` | 4 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.instant_s` | 0.857 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.first_sentence_s` | 18.537 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.first_verified_s` | 22.873 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.first_area_s` | 70.493 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.done_s` | 310.531 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.cost_usd` | 0.03379 |  | lower | no |
| `live.deepinfra-gptoss-glm53flash-t0-live.gaps` | 2 |  | lower | no |
| `synthetic.planted.2000.predicted_power` | 0.4101 |  | informational | no |
| `synthetic.planted.2000.recovered_share` | 0.375 |  | higher | no |
| `synthetic.planted.2000.survived_bh_share` | 0.375 |  | higher | no |
| `synthetic.planted.2000.recovery_gap` | 0.0351 |  | informational | no |
| `synthetic.planted.2000.timing_recovered_share` | 1.0 |  | higher | no |
| `synthetic.planted.2000.unplanted_areas_surviving_bh` | 0 |  | lower | no |
| `synthetic.null.2000.areas_surviving_bh` | 0 |  | lower | no |
| `synthetic.null.2000.rules_with_effect` | 0 |  | lower | no |
| `synthetic.planted.20000.predicted_power` | 0.9987 |  | informational | no |
| `synthetic.planted.20000.recovered_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.survived_bh_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.recovery_gap` | 0.0013 |  | informational | no |
| `synthetic.planted.20000.timing_recovered_share` | 1.0 |  | higher | no |
| `synthetic.planted.20000.unplanted_areas_surviving_bh` | 3 |  | lower | no |
| `synthetic.planted.20000.pipeline_recovers` | 1 |  | higher | yes |
| `synthetic.null.20000.areas_surviving_bh` | 0 |  | lower | no |
| `synthetic.null.20000.rules_with_effect` | 0 |  | lower | no |
| `synthetic.null.20000.pipeline_quiet` | 1 |  | higher | yes |

## Skips and what is blocked

- metamorphic: tests/test_metamorphic.py:189: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- metamorphic: tests/test_metamorphic.py:206: set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API
- checker benchmark: tests/test_checker_bench.py:110: set JYOTISH_LIVE_NARRATION=1 to call the API

