# Scorecard

Run 2026-11-09 at commit `61ba9af` by `scripts/evaluate.py`. CI fails when any gated number is worse than in the committed `docs/scorecard.json`; a sampled statistic is reported with its direction and not gated.

## Reference acceptance tests

`tests/test_reference_chart.py` and `tests/test_ephemeris_reference.py`: 25 passed, 0 failed, 0 skipped.

## Phase 0 cross-check

1,000 births (seed 0) against PyJHora 4.8.7, ephemeris Moshier (no ephemeris files), in 8 s: 0 beyond the 1″ / one-day gate, 0 listed at an edge. Per-quantity maxima and means are in the table; docs/crosscheck.md has the full report.

## Metamorphic tests

`tests/test_metamorphic.py`: 17 passed, 0 failed, 2 skipped (the narration-side invariants are live only).

## Checker benchmark

184 rows; the validator alone: precision 1.000, recall 0.342, F1 0.510; 35 of 35 tag and wording errors caught; 0 accepted sentences rejected. The semantic categories are the checker's. A turn's sentences (`where: "answer"`, 27 rows from the live turns of 2026-11-01, Ray's of 2026-11-02 and the writer bake-off of 2026-11-09): the validator alone refuses 14 of 24 wrong ones and 0 true ones. The live run on record (docs/checker_scorecard.md, 2026-10-22 at `b0eb697`, model claude-opus-5-5, checker effort high): 72 of 74 bad sentences caught, precision 1.000, recall 0.973, F1 0.986. The harness does not re-run it (API calls), so it is reported, not gated.

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
- fly-1 (2026-10-31; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, on the deployed service (fly)): instant page 14.693 s, first sentence 55.447 s, first verified 57.677 s, first area 98.54 s, done 409.109 s; USD 0.029619; 35 claims, 2 gaps.
- fly-2 (2026-10-31; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, on the deployed service (fly)): instant page 3.242 s, first sentence 35.827 s, first verified 37.707 s, first area 64.146 s, done 322.022 s; USD 0.031136; 37 claims, 0 gaps.
- fly-3 (2026-10-31; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, on the deployed service (fly)): instant page 3.296 s, first sentence 45.03 s, first verified 48.768 s, first area 77.593 s, done 330.469 s; USD 0.024055; 37 claims, 0 gaps.
- compare-2026-10-31-a-curious (2026-10-31; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, concurrency None): instant page 3.449 s, first sentence 82.521 s, first verified 84.35 s, first area 172.858 s, done 439.49 s; USD 0.047195; 37 claims, 0 gaps.
- compare-2026-10-31-b (2026-10-31; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com, concurrency None): instant page 0.865 s, first sentence 50.603 s, first verified 52.636 s, first area 147.799 s, done 492.992 s; USD 0.03687; 36 claims, 1 gaps.
- Median of the 3 readings on fly: instant_s 3.296, first_sentence_s 45.03, first_verified_s 48.768, first_area_s 77.593, done_s 330.469, cost_usd 0.029619, gaps 0.

## Conversation turns (reported, not gated)

Live turns of the reference chart (docs/live_timings.jsonl, scripts/live_timing.py --turn): the engine's seconds to its own answer, the writer's first verified sentence, and the share of the writer's sentences removed by the checks. Each is one run on a shared provider, so it is reported and never gated.

- turn-challenges-1 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.002 s, first verified 31.202 s, done 32.471 s; 2 of 7 sentences removed; answer from the writer; USD 0.004904.
- turn-challenges-2 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.002 s, first verified 22.939 s, done 39.793 s; 3 of 7 sentences removed; answer from the writer; USD 0.005306.
- turn-challenges-3 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.002 s, first verified 36.108 s, done 38.391 s; 3 of 7 sentences removed; answer from the writer; USD 0.005673.
- turn-challenges-low-1 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.695 s, first verified 9.839 s, done 14.541 s; 0 of 3 sentences removed; answer from the writer; USD 0.002962.
- turn-challenges-low-2 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.724 s, first verified 22.017 s, done 25.493 s; 5 of 8 sentences removed; answer from the writer; USD 0.003505.
- conversation-1-1 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.003 s, first verified 37.993 s, done 195.607 s; 7 of 14 sentences removed; answer from the writer; USD 0.012647.
- conversation-1-2 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.001 s, first verified 34.844 s, done 170.192 s; 8 of 15 sentences removed; answer from the writer; USD 0.009581.
- conversation-1-3 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.001 s, first verified 102.754 s, done 102.755 s; 5 of 6 sentences removed; answer from the writer; USD 0.00334.
- conversation-1-4 (2026-11-01; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.001 s, first verified 34.141 s, done 158.833 s; 6 of 14 sentences removed; answer from the writer; USD 0.010349.
- gpt-oss-120b-1 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.003 s, first verified 85.066 s, done 271.475 s; 11 of 18 sentences removed; answer from the writer; USD 0.011311.
- gpt-oss-120b-2 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.001 s, first verified 62.181 s, done 139.355 s; 3 of 8 sentences removed; answer from the writer; USD 0.004934.
- gpt-oss-120b-3 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.001 s, first verified 33.851 s, done 80.21 s; 3 of 4 sentences removed; answer from the writer; USD 0.000597.
- gpt-oss-120b-4 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.001 s, first verified 128.837 s, done 128.837 s; 3 of 4 sentences removed; answer from the writer; USD 0.002501.
- gpt-oss-120b-6 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.001 s, first verified 34.198 s, done 94.994 s; 1 of 7 sentences removed; answer from the writer; USD 0.00696.
- gpt-oss-120b-7 (2026-11-06; openai/gpt-oss-120b on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.001 s, first verified 58.692 s, done 262.863 s; 12 of 18 sentences removed; answer from the writer; USD 0.009721.
- qwen3.6-35b-a3b-1 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.004 s, first verified 99.724 s, done 295.824 s; 13 of 21 sentences removed; answer from the writer; USD 0.035396.
- qwen3.6-35b-a3b-2 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.001 s, first verified 109.544 s, done 348.218 s; 10 of 17 sentences removed; answer from the writer; USD 0.033941.
- qwen3.6-35b-a3b-3 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.002 s, first verified 77.87 s, done 154.473 s; 1 of 4 sentences removed; answer from the writer; USD 0.012017.
- qwen3.6-35b-a3b-4 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.002 s, first verified 103.595 s, done 233.194 s; 9 of 11 sentences removed; answer from the writer; USD 0.027852.
- qwen3.6-35b-a3b-6 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.002 s, first verified 60.999 s, done 151.973 s; 4 of 14 sentences removed; answer from the writer; USD 0.019509.
- qwen3.6-35b-a3b-7 (2026-11-06; Qwen/Qwen3.6-35B-A3B on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 73.601 s, done 236.92 s; 8 of 17 sentences removed; answer from the writer; USD 0.024728.
- deepseek-v3.2-1 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.005 s, first verified 28.996 s, done 89.046 s; 17 of 25 sentences removed; answer from the writer; USD 0.015485.
- deepseek-v3.2-2 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.002 s, first verified 26.681 s, done 50.541 s; 5 of 7 sentences removed; answer from the writer; USD 0.005305.
- deepseek-v3.2-3 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.002 s, first verified 2.415 s, done 51.036 s; 15 of 19 sentences removed; answer from the writer; USD 0.005075.
- deepseek-v3.2-4 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.002 s, first verified 25.65 s, done 28.649 s; 4 of 7 sentences removed; answer from the writer; USD 0.006195.
- deepseek-v3.2-6 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.002 s, first verified 18.161 s, done 57.663 s; 5 of 11 sentences removed; answer from the writer; USD 0.010055.
- deepseek-v3.2-7 (2026-11-06; deepseek-ai/DeepSeek-V3.2 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 3.162 s, done 55.704 s; 17 of 21 sentences removed; answer from the writer; USD 0.005261.
- kimi-k2.6-1 (2026-11-07; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.002 s, first verified 1276.656 s, done 7396.484 s; 3 of 10 sentences removed; answer from the writer; USD 0.163055.
- kimi-k2.6-2 (2026-11-07; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.004 s, first verified 938.965 s, done 3968.127 s; 2 of 12 sentences removed; answer from the writer; USD 0.057995.
- kimi-k2.6-3 (2026-11-08; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.003 s, first verified 1190.698 s, done 8792.033 s; 5 of 7 sentences removed; answer from the writer; USD 0.16166.
- kimi-k2.6-4 (2026-11-08; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.006 s, first verified None s, done 1923.264 s; 0 of 0 sentences removed; answer from the engine; USD 0.170835.
- kimi-k2.6-6 (2026-11-08; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.004 s, first verified 188.869 s, done 1552.538 s; 5 of 13 sentences removed; answer from the writer; USD 0.145629.
- kimi-k2.6-7 (2026-11-08; moonshotai/Kimi-K2.6 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 682.955 s, done 1206.072 s; 2 of 5 sentences removed; answer from the writer; USD 0.099888.
- glm-5.3-1 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.003 s, first verified 62.638 s, done 2079.052 s; 21 of 32 sentences removed; answer from the writer; USD 0.060832.
- glm-5.3-2 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.003 s, first verified 34.868 s, done 172.95 s; 11 of 20 sentences removed; answer from the writer; USD 0.020145.
- glm-5.3-3 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.002 s, first verified 4.701 s, done 104.462 s; 9 of 13 sentences removed; answer from the writer; USD 0.014735.
- glm-5.3-4 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.002 s, first verified None s, done 97.363 s; 21 of 21 sentences removed; answer from the engine; USD 0.01884.
- glm-5.3-6 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.002 s, first verified 6.236 s, done 64.229 s; 4 of 13 sentences removed; answer from the writer; USD 0.014279.
- glm-5.3-7 (2026-11-09; zai-org/GLM-5.3 on api.deepinfra.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 8.265 s, done 98.702 s; 8 of 13 sentences removed; answer from the writer; USD 0.015163.
- claude-haiku-5-5-1 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.002 s, first verified 14.737 s, done 110.508 s; 16 of 25 sentences removed; answer from the writer; USD 0.018127.
- claude-haiku-5-5-2 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.002 s, first verified 50.119 s, done 83.888 s; 6 of 12 sentences removed; answer from the writer; USD 0.012658.
- claude-haiku-5-5-3 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.002 s, first verified 8.37 s, done 49.932 s; 4 of 8 sentences removed; answer from the writer; USD 0.00578.
- claude-haiku-5-5-4 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.002 s, first verified 19.194 s, done 62.813 s; 6 of 10 sentences removed; answer from the writer; USD 0.010347.
- claude-haiku-5-5-6 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.002 s, first verified 9.571 s, done 59.248 s; 3 of 12 sentences removed; answer from the writer; USD 0.013309.
- claude-haiku-5-5-7 (2026-11-09; claude-haiku-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 15.955 s, done 28.001 s; 15 of 16 sentences removed; answer from the writer; USD 0.005403.
- claude-sonnet-5-5-1 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "what are the challanges in my life", engine 0.003 s, first verified 34.433 s, done 147.858 s; 12 of 22 sentences removed; answer from the writer; USD 0.070407.
- claude-sonnet-5-5-2 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "and marriage?", engine 0.002 s, first verified 33.381 s, done 112.871 s; 9 of 19 sentences removed; answer from the writer; USD 0.060395.
- claude-sonnet-5-5-3 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "when?", engine 0.002 s, first verified 2.562 s, done 105.122 s; 19 of 27 sentences removed; answer from the writer; USD 0.064941.
- claude-sonnet-5-5-4 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "why do you say that?", engine 0.001 s, first verified 53.615 s, done 343.649 s; 21 of 29 sentences removed; answer from the writer; USD 0.070663.
- claude-sonnet-5-5-6 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "how much money will i earn in my life, will i be rich", engine 0.002 s, first verified 3.507 s, done 211.199 s; 8 of 18 sentences removed; answer from the writer; USD 0.054651.
- claude-sonnet-5-5-7 (2026-11-09; claude-sonnet-5-5 on api.anthropic.com, zai-org/GLM-5.3-Flash on api.deepinfra.com): "whan and how", engine 0.002 s, first verified 1.548 s, done 98.135 s; 13 of 22 sentences removed; answer from the writer; USD 0.066513.

## The paragraph held sentence by sentence (reported, not gated)

From docs/comparison_2026-11-01_curious_r2 (6 curious paragraphs, one live run per side): 4 complete, 2 held in part, 0 none; the writer's rounds per area, mean 3.00; sentences held at each attempt: attempt 1 9, attempt 2 6, attempt 3 7; ended early with attempts unused: 0. The latest comparison at curious depth is read; a later one replaces it.

## Synthetic validation (the pipeline, not the engine)

Planted, N = 2,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 0.41, recovered 0.38 (p < 0.05), 0.38 surviving BH; the timing effect recovered in 1.00; 0 of the 3 unplanted areas (father, gains, reputation: they own none of their events) also survive BH, lift inherited through the shared outcome map; 30 s.
Null, N = 2,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 11 s.
Planted, N = 20,000 (odds ratio 1.2 per SD of the area score, timing weight 2.0): 8 planted areas; predicted power 1.00, recovered 1.00 (p < 0.05), 1.00 surviving BH; the timing effect recovered in 1.00; 3 of the 3 unplanted areas (father, gains, reputation: they own none of their events) also survive BH, lift inherited through the shared outcome map (father, gains, reputation); 247 s. Gated check: at least three quarters of the planted areas recovered, surviving BH and timing-recovered: passes.
Null, N = 20,000: 0 of 11 areas survive BH; 0 of 360 rules show an effect after BH; 111 s. Gated check: at most one area and three rules survive: passes.
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
| `checker.validator.recall` | 0.3421 |  | higher | no |
| `checker.validator.f1` | 0.5098 |  | higher | no |
| `checker.validator.wording_caught_share` | 1.0 |  | higher | yes |
| `checker.validator.false_rejects` | 0 |  | lower | yes |
| `checker.bench_rows` | 184 |  | informational | no |
| `checker.answer.rows` | 27 |  | informational | no |
| `checker.answer.validator_recall` | 0.5833 |  | higher | no |
| `checker.answer.validator_false_rejects` | 0 |  | lower | no |
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
| `live.fly-1.instant_s` | 14.693 |  | lower | no |
| `live.fly-1.first_sentence_s` | 55.447 |  | lower | no |
| `live.fly-1.first_verified_s` | 57.677 |  | lower | no |
| `live.fly-1.first_area_s` | 98.54 |  | lower | no |
| `live.fly-1.done_s` | 409.109 |  | lower | no |
| `live.fly-1.cost_usd` | 0.029619 |  | lower | no |
| `live.fly-1.gaps` | 2 |  | lower | no |
| `live.fly-2.instant_s` | 3.242 |  | lower | no |
| `live.fly-2.first_sentence_s` | 35.827 |  | lower | no |
| `live.fly-2.first_verified_s` | 37.707 |  | lower | no |
| `live.fly-2.first_area_s` | 64.146 |  | lower | no |
| `live.fly-2.done_s` | 322.022 |  | lower | no |
| `live.fly-2.cost_usd` | 0.031136 |  | lower | no |
| `live.fly-2.gaps` | 0 |  | lower | no |
| `live.fly-3.instant_s` | 3.296 |  | lower | no |
| `live.fly-3.first_sentence_s` | 45.03 |  | lower | no |
| `live.fly-3.first_verified_s` | 48.768 |  | lower | no |
| `live.fly-3.first_area_s` | 77.593 |  | lower | no |
| `live.fly-3.done_s` | 330.469 |  | lower | no |
| `live.fly-3.cost_usd` | 0.024055 |  | lower | no |
| `live.fly-3.gaps` | 0 |  | lower | no |
| `live.compare-2026-10-31-a-curious.instant_s` | 3.449 |  | lower | no |
| `live.compare-2026-10-31-a-curious.first_sentence_s` | 82.521 |  | lower | no |
| `live.compare-2026-10-31-a-curious.first_verified_s` | 84.35 |  | lower | no |
| `live.compare-2026-10-31-a-curious.first_area_s` | 172.858 |  | lower | no |
| `live.compare-2026-10-31-a-curious.done_s` | 439.49 |  | lower | no |
| `live.compare-2026-10-31-a-curious.cost_usd` | 0.047195 |  | lower | no |
| `live.compare-2026-10-31-a-curious.gaps` | 0 |  | lower | no |
| `live.compare-2026-10-31-b.instant_s` | 0.865 |  | lower | no |
| `live.compare-2026-10-31-b.first_sentence_s` | 50.603 |  | lower | no |
| `live.compare-2026-10-31-b.first_verified_s` | 52.636 |  | lower | no |
| `live.compare-2026-10-31-b.first_area_s` | 147.799 |  | lower | no |
| `live.compare-2026-10-31-b.done_s` | 492.992 |  | lower | no |
| `live.compare-2026-10-31-b.cost_usd` | 0.03687 |  | lower | no |
| `live.compare-2026-10-31-b.gaps` | 1 |  | lower | no |
| `live.fly_median.instant_s` | 3.296 |  | lower | no |
| `live.fly_median.first_sentence_s` | 45.03 |  | lower | no |
| `live.fly_median.first_verified_s` | 48.768 |  | lower | no |
| `live.fly_median.first_area_s` | 77.593 |  | lower | no |
| `live.fly_median.done_s` | 330.469 |  | lower | no |
| `live.fly_median.cost_usd` | 0.029619 |  | lower | no |
| `live.fly_median.gaps` | 0 |  | lower | no |
| `turn.turn-challenges-1.engine_s` | 0.002 |  | lower | no |
| `turn.turn-challenges-1.first_verified_s` | 31.202 |  | lower | no |
| `turn.turn-challenges-1.removed_share` | 0.286 |  | lower | no |
| `turn.turn-challenges-1.done_s` | 32.471 |  | lower | no |
| `turn.turn-challenges-1.cost_usd` | 0.004904 |  | lower | no |
| `turn.turn-challenges-2.engine_s` | 0.002 |  | lower | no |
| `turn.turn-challenges-2.first_verified_s` | 22.939 |  | lower | no |
| `turn.turn-challenges-2.removed_share` | 0.429 |  | lower | no |
| `turn.turn-challenges-2.done_s` | 39.793 |  | lower | no |
| `turn.turn-challenges-2.cost_usd` | 0.005306 |  | lower | no |
| `turn.turn-challenges-3.engine_s` | 0.002 |  | lower | no |
| `turn.turn-challenges-3.first_verified_s` | 36.108 |  | lower | no |
| `turn.turn-challenges-3.removed_share` | 0.429 |  | lower | no |
| `turn.turn-challenges-3.done_s` | 38.391 |  | lower | no |
| `turn.turn-challenges-3.cost_usd` | 0.005673 |  | lower | no |
| `turn.turn-challenges-low-1.engine_s` | 0.695 |  | lower | no |
| `turn.turn-challenges-low-1.first_verified_s` | 9.839 |  | lower | no |
| `turn.turn-challenges-low-1.removed_share` | 0.0 |  | lower | no |
| `turn.turn-challenges-low-1.done_s` | 14.541 |  | lower | no |
| `turn.turn-challenges-low-1.cost_usd` | 0.002962 |  | lower | no |
| `turn.turn-challenges-low-2.engine_s` | 0.724 |  | lower | no |
| `turn.turn-challenges-low-2.first_verified_s` | 22.017 |  | lower | no |
| `turn.turn-challenges-low-2.removed_share` | 0.625 |  | lower | no |
| `turn.turn-challenges-low-2.done_s` | 25.493 |  | lower | no |
| `turn.turn-challenges-low-2.cost_usd` | 0.003505 |  | lower | no |
| `turn.conversation-1-1.engine_s` | 0.003 |  | lower | no |
| `turn.conversation-1-1.first_verified_s` | 37.993 |  | lower | no |
| `turn.conversation-1-1.removed_share` | 0.5 |  | lower | no |
| `turn.conversation-1-1.done_s` | 195.607 |  | lower | no |
| `turn.conversation-1-1.cost_usd` | 0.012647 |  | lower | no |
| `turn.conversation-1-2.engine_s` | 0.001 |  | lower | no |
| `turn.conversation-1-2.first_verified_s` | 34.844 |  | lower | no |
| `turn.conversation-1-2.removed_share` | 0.533 |  | lower | no |
| `turn.conversation-1-2.done_s` | 170.192 |  | lower | no |
| `turn.conversation-1-2.cost_usd` | 0.009581 |  | lower | no |
| `turn.conversation-1-3.engine_s` | 0.001 |  | lower | no |
| `turn.conversation-1-3.first_verified_s` | 102.754 |  | lower | no |
| `turn.conversation-1-3.removed_share` | 0.833 |  | lower | no |
| `turn.conversation-1-3.done_s` | 102.755 |  | lower | no |
| `turn.conversation-1-3.cost_usd` | 0.00334 |  | lower | no |
| `turn.conversation-1-4.engine_s` | 0.001 |  | lower | no |
| `turn.conversation-1-4.first_verified_s` | 34.141 |  | lower | no |
| `turn.conversation-1-4.removed_share` | 0.429 |  | lower | no |
| `turn.conversation-1-4.done_s` | 158.833 |  | lower | no |
| `turn.conversation-1-4.cost_usd` | 0.010349 |  | lower | no |
| `turn.gpt-oss-120b-1.engine_s` | 0.003 |  | lower | no |
| `turn.gpt-oss-120b-1.first_verified_s` | 85.066 |  | lower | no |
| `turn.gpt-oss-120b-1.removed_share` | 0.611 |  | lower | no |
| `turn.gpt-oss-120b-1.done_s` | 271.475 |  | lower | no |
| `turn.gpt-oss-120b-1.cost_usd` | 0.011311 |  | lower | no |
| `turn.gpt-oss-120b-2.engine_s` | 0.001 |  | lower | no |
| `turn.gpt-oss-120b-2.first_verified_s` | 62.181 |  | lower | no |
| `turn.gpt-oss-120b-2.removed_share` | 0.375 |  | lower | no |
| `turn.gpt-oss-120b-2.done_s` | 139.355 |  | lower | no |
| `turn.gpt-oss-120b-2.cost_usd` | 0.004934 |  | lower | no |
| `turn.gpt-oss-120b-3.engine_s` | 0.001 |  | lower | no |
| `turn.gpt-oss-120b-3.first_verified_s` | 33.851 |  | lower | no |
| `turn.gpt-oss-120b-3.removed_share` | 0.75 |  | lower | no |
| `turn.gpt-oss-120b-3.done_s` | 80.21 |  | lower | no |
| `turn.gpt-oss-120b-3.cost_usd` | 0.000597 |  | lower | no |
| `turn.gpt-oss-120b-4.engine_s` | 0.001 |  | lower | no |
| `turn.gpt-oss-120b-4.first_verified_s` | 128.837 |  | lower | no |
| `turn.gpt-oss-120b-4.removed_share` | 0.75 |  | lower | no |
| `turn.gpt-oss-120b-4.done_s` | 128.837 |  | lower | no |
| `turn.gpt-oss-120b-4.cost_usd` | 0.002501 |  | lower | no |
| `turn.gpt-oss-120b-6.engine_s` | 0.001 |  | lower | no |
| `turn.gpt-oss-120b-6.first_verified_s` | 34.198 |  | lower | no |
| `turn.gpt-oss-120b-6.removed_share` | 0.143 |  | lower | no |
| `turn.gpt-oss-120b-6.done_s` | 94.994 |  | lower | no |
| `turn.gpt-oss-120b-6.cost_usd` | 0.00696 |  | lower | no |
| `turn.gpt-oss-120b-7.engine_s` | 0.001 |  | lower | no |
| `turn.gpt-oss-120b-7.first_verified_s` | 58.692 |  | lower | no |
| `turn.gpt-oss-120b-7.removed_share` | 0.667 |  | lower | no |
| `turn.gpt-oss-120b-7.done_s` | 262.863 |  | lower | no |
| `turn.gpt-oss-120b-7.cost_usd` | 0.009721 |  | lower | no |
| `turn.qwen3.6-35b-a3b-1.engine_s` | 0.004 |  | lower | no |
| `turn.qwen3.6-35b-a3b-1.first_verified_s` | 99.724 |  | lower | no |
| `turn.qwen3.6-35b-a3b-1.removed_share` | 0.619 |  | lower | no |
| `turn.qwen3.6-35b-a3b-1.done_s` | 295.824 |  | lower | no |
| `turn.qwen3.6-35b-a3b-1.cost_usd` | 0.035396 |  | lower | no |
| `turn.qwen3.6-35b-a3b-2.engine_s` | 0.001 |  | lower | no |
| `turn.qwen3.6-35b-a3b-2.first_verified_s` | 109.544 |  | lower | no |
| `turn.qwen3.6-35b-a3b-2.removed_share` | 0.588 |  | lower | no |
| `turn.qwen3.6-35b-a3b-2.done_s` | 348.218 |  | lower | no |
| `turn.qwen3.6-35b-a3b-2.cost_usd` | 0.033941 |  | lower | no |
| `turn.qwen3.6-35b-a3b-3.engine_s` | 0.002 |  | lower | no |
| `turn.qwen3.6-35b-a3b-3.first_verified_s` | 77.87 |  | lower | no |
| `turn.qwen3.6-35b-a3b-3.removed_share` | 0.25 |  | lower | no |
| `turn.qwen3.6-35b-a3b-3.done_s` | 154.473 |  | lower | no |
| `turn.qwen3.6-35b-a3b-3.cost_usd` | 0.012017 |  | lower | no |
| `turn.qwen3.6-35b-a3b-4.engine_s` | 0.002 |  | lower | no |
| `turn.qwen3.6-35b-a3b-4.first_verified_s` | 103.595 |  | lower | no |
| `turn.qwen3.6-35b-a3b-4.removed_share` | 0.818 |  | lower | no |
| `turn.qwen3.6-35b-a3b-4.done_s` | 233.194 |  | lower | no |
| `turn.qwen3.6-35b-a3b-4.cost_usd` | 0.027852 |  | lower | no |
| `turn.qwen3.6-35b-a3b-6.engine_s` | 0.002 |  | lower | no |
| `turn.qwen3.6-35b-a3b-6.first_verified_s` | 60.999 |  | lower | no |
| `turn.qwen3.6-35b-a3b-6.removed_share` | 0.286 |  | lower | no |
| `turn.qwen3.6-35b-a3b-6.done_s` | 151.973 |  | lower | no |
| `turn.qwen3.6-35b-a3b-6.cost_usd` | 0.019509 |  | lower | no |
| `turn.qwen3.6-35b-a3b-7.engine_s` | 0.002 |  | lower | no |
| `turn.qwen3.6-35b-a3b-7.first_verified_s` | 73.601 |  | lower | no |
| `turn.qwen3.6-35b-a3b-7.removed_share` | 0.471 |  | lower | no |
| `turn.qwen3.6-35b-a3b-7.done_s` | 236.92 |  | lower | no |
| `turn.qwen3.6-35b-a3b-7.cost_usd` | 0.024728 |  | lower | no |
| `turn.deepseek-v3.2-1.engine_s` | 0.005 |  | lower | no |
| `turn.deepseek-v3.2-1.first_verified_s` | 28.996 |  | lower | no |
| `turn.deepseek-v3.2-1.removed_share` | 0.68 |  | lower | no |
| `turn.deepseek-v3.2-1.done_s` | 89.046 |  | lower | no |
| `turn.deepseek-v3.2-1.cost_usd` | 0.015485 |  | lower | no |
| `turn.deepseek-v3.2-2.engine_s` | 0.002 |  | lower | no |
| `turn.deepseek-v3.2-2.first_verified_s` | 26.681 |  | lower | no |
| `turn.deepseek-v3.2-2.removed_share` | 0.714 |  | lower | no |
| `turn.deepseek-v3.2-2.done_s` | 50.541 |  | lower | no |
| `turn.deepseek-v3.2-2.cost_usd` | 0.005305 |  | lower | no |
| `turn.deepseek-v3.2-3.engine_s` | 0.002 |  | lower | no |
| `turn.deepseek-v3.2-3.first_verified_s` | 2.415 |  | lower | no |
| `turn.deepseek-v3.2-3.removed_share` | 0.789 |  | lower | no |
| `turn.deepseek-v3.2-3.done_s` | 51.036 |  | lower | no |
| `turn.deepseek-v3.2-3.cost_usd` | 0.005075 |  | lower | no |
| `turn.deepseek-v3.2-4.engine_s` | 0.002 |  | lower | no |
| `turn.deepseek-v3.2-4.first_verified_s` | 25.65 |  | lower | no |
| `turn.deepseek-v3.2-4.removed_share` | 0.571 |  | lower | no |
| `turn.deepseek-v3.2-4.done_s` | 28.649 |  | lower | no |
| `turn.deepseek-v3.2-4.cost_usd` | 0.006195 |  | lower | no |
| `turn.deepseek-v3.2-6.engine_s` | 0.002 |  | lower | no |
| `turn.deepseek-v3.2-6.first_verified_s` | 18.161 |  | lower | no |
| `turn.deepseek-v3.2-6.removed_share` | 0.455 |  | lower | no |
| `turn.deepseek-v3.2-6.done_s` | 57.663 |  | lower | no |
| `turn.deepseek-v3.2-6.cost_usd` | 0.010055 |  | lower | no |
| `turn.deepseek-v3.2-7.engine_s` | 0.002 |  | lower | no |
| `turn.deepseek-v3.2-7.first_verified_s` | 3.162 |  | lower | no |
| `turn.deepseek-v3.2-7.removed_share` | 0.81 |  | lower | no |
| `turn.deepseek-v3.2-7.done_s` | 55.704 |  | lower | no |
| `turn.deepseek-v3.2-7.cost_usd` | 0.005261 |  | lower | no |
| `turn.kimi-k2.6-1.engine_s` | 0.002 |  | lower | no |
| `turn.kimi-k2.6-1.first_verified_s` | 1276.656 |  | lower | no |
| `turn.kimi-k2.6-1.removed_share` | 0.3 |  | lower | no |
| `turn.kimi-k2.6-1.done_s` | 7396.484 |  | lower | no |
| `turn.kimi-k2.6-1.cost_usd` | 0.163055 |  | lower | no |
| `turn.kimi-k2.6-2.engine_s` | 0.004 |  | lower | no |
| `turn.kimi-k2.6-2.first_verified_s` | 938.965 |  | lower | no |
| `turn.kimi-k2.6-2.removed_share` | 0.167 |  | lower | no |
| `turn.kimi-k2.6-2.done_s` | 3968.127 |  | lower | no |
| `turn.kimi-k2.6-2.cost_usd` | 0.057995 |  | lower | no |
| `turn.kimi-k2.6-3.engine_s` | 0.003 |  | lower | no |
| `turn.kimi-k2.6-3.first_verified_s` | 1190.698 |  | lower | no |
| `turn.kimi-k2.6-3.removed_share` | 0.714 |  | lower | no |
| `turn.kimi-k2.6-3.done_s` | 8792.033 |  | lower | no |
| `turn.kimi-k2.6-3.cost_usd` | 0.16166 |  | lower | no |
| `turn.kimi-k2.6-4.engine_s` | 0.006 |  | lower | no |
| `turn.kimi-k2.6-4.done_s` | 1923.264 |  | lower | no |
| `turn.kimi-k2.6-4.cost_usd` | 0.170835 |  | lower | no |
| `turn.kimi-k2.6-6.engine_s` | 0.004 |  | lower | no |
| `turn.kimi-k2.6-6.first_verified_s` | 188.869 |  | lower | no |
| `turn.kimi-k2.6-6.removed_share` | 0.385 |  | lower | no |
| `turn.kimi-k2.6-6.done_s` | 1552.538 |  | lower | no |
| `turn.kimi-k2.6-6.cost_usd` | 0.145629 |  | lower | no |
| `turn.kimi-k2.6-7.engine_s` | 0.002 |  | lower | no |
| `turn.kimi-k2.6-7.first_verified_s` | 682.955 |  | lower | no |
| `turn.kimi-k2.6-7.removed_share` | 0.4 |  | lower | no |
| `turn.kimi-k2.6-7.done_s` | 1206.072 |  | lower | no |
| `turn.kimi-k2.6-7.cost_usd` | 0.099888 |  | lower | no |
| `turn.glm-5.3-1.engine_s` | 0.003 |  | lower | no |
| `turn.glm-5.3-1.first_verified_s` | 62.638 |  | lower | no |
| `turn.glm-5.3-1.removed_share` | 0.656 |  | lower | no |
| `turn.glm-5.3-1.done_s` | 2079.052 |  | lower | no |
| `turn.glm-5.3-1.cost_usd` | 0.060832 |  | lower | no |
| `turn.glm-5.3-2.engine_s` | 0.003 |  | lower | no |
| `turn.glm-5.3-2.first_verified_s` | 34.868 |  | lower | no |
| `turn.glm-5.3-2.removed_share` | 0.55 |  | lower | no |
| `turn.glm-5.3-2.done_s` | 172.95 |  | lower | no |
| `turn.glm-5.3-2.cost_usd` | 0.020145 |  | lower | no |
| `turn.glm-5.3-3.engine_s` | 0.002 |  | lower | no |
| `turn.glm-5.3-3.first_verified_s` | 4.701 |  | lower | no |
| `turn.glm-5.3-3.removed_share` | 0.692 |  | lower | no |
| `turn.glm-5.3-3.done_s` | 104.462 |  | lower | no |
| `turn.glm-5.3-3.cost_usd` | 0.014735 |  | lower | no |
| `turn.glm-5.3-4.engine_s` | 0.002 |  | lower | no |
| `turn.glm-5.3-4.removed_share` | 1.0 |  | lower | no |
| `turn.glm-5.3-4.done_s` | 97.363 |  | lower | no |
| `turn.glm-5.3-4.cost_usd` | 0.01884 |  | lower | no |
| `turn.glm-5.3-6.engine_s` | 0.002 |  | lower | no |
| `turn.glm-5.3-6.first_verified_s` | 6.236 |  | lower | no |
| `turn.glm-5.3-6.removed_share` | 0.308 |  | lower | no |
| `turn.glm-5.3-6.done_s` | 64.229 |  | lower | no |
| `turn.glm-5.3-6.cost_usd` | 0.014279 |  | lower | no |
| `turn.glm-5.3-7.engine_s` | 0.002 |  | lower | no |
| `turn.glm-5.3-7.first_verified_s` | 8.265 |  | lower | no |
| `turn.glm-5.3-7.removed_share` | 0.615 |  | lower | no |
| `turn.glm-5.3-7.done_s` | 98.702 |  | lower | no |
| `turn.glm-5.3-7.cost_usd` | 0.015163 |  | lower | no |
| `turn.claude-haiku-5-5-1.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-1.first_verified_s` | 14.737 |  | lower | no |
| `turn.claude-haiku-5-5-1.removed_share` | 0.64 |  | lower | no |
| `turn.claude-haiku-5-5-1.done_s` | 110.508 |  | lower | no |
| `turn.claude-haiku-5-5-1.cost_usd` | 0.018127 |  | lower | no |
| `turn.claude-haiku-5-5-2.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-2.first_verified_s` | 50.119 |  | lower | no |
| `turn.claude-haiku-5-5-2.removed_share` | 0.5 |  | lower | no |
| `turn.claude-haiku-5-5-2.done_s` | 83.888 |  | lower | no |
| `turn.claude-haiku-5-5-2.cost_usd` | 0.012658 |  | lower | no |
| `turn.claude-haiku-5-5-3.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-3.first_verified_s` | 8.37 |  | lower | no |
| `turn.claude-haiku-5-5-3.removed_share` | 0.5 |  | lower | no |
| `turn.claude-haiku-5-5-3.done_s` | 49.932 |  | lower | no |
| `turn.claude-haiku-5-5-3.cost_usd` | 0.00578 |  | lower | no |
| `turn.claude-haiku-5-5-4.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-4.first_verified_s` | 19.194 |  | lower | no |
| `turn.claude-haiku-5-5-4.removed_share` | 0.6 |  | lower | no |
| `turn.claude-haiku-5-5-4.done_s` | 62.813 |  | lower | no |
| `turn.claude-haiku-5-5-4.cost_usd` | 0.010347 |  | lower | no |
| `turn.claude-haiku-5-5-6.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-6.first_verified_s` | 9.571 |  | lower | no |
| `turn.claude-haiku-5-5-6.removed_share` | 0.25 |  | lower | no |
| `turn.claude-haiku-5-5-6.done_s` | 59.248 |  | lower | no |
| `turn.claude-haiku-5-5-6.cost_usd` | 0.013309 |  | lower | no |
| `turn.claude-haiku-5-5-7.engine_s` | 0.002 |  | lower | no |
| `turn.claude-haiku-5-5-7.first_verified_s` | 15.955 |  | lower | no |
| `turn.claude-haiku-5-5-7.removed_share` | 0.938 |  | lower | no |
| `turn.claude-haiku-5-5-7.done_s` | 28.001 |  | lower | no |
| `turn.claude-haiku-5-5-7.cost_usd` | 0.005403 |  | lower | no |
| `turn.claude-sonnet-5-5-1.engine_s` | 0.003 |  | lower | no |
| `turn.claude-sonnet-5-5-1.first_verified_s` | 34.433 |  | lower | no |
| `turn.claude-sonnet-5-5-1.removed_share` | 0.545 |  | lower | no |
| `turn.claude-sonnet-5-5-1.done_s` | 147.858 |  | lower | no |
| `turn.claude-sonnet-5-5-1.cost_usd` | 0.070407 |  | lower | no |
| `turn.claude-sonnet-5-5-2.engine_s` | 0.002 |  | lower | no |
| `turn.claude-sonnet-5-5-2.first_verified_s` | 33.381 |  | lower | no |
| `turn.claude-sonnet-5-5-2.removed_share` | 0.474 |  | lower | no |
| `turn.claude-sonnet-5-5-2.done_s` | 112.871 |  | lower | no |
| `turn.claude-sonnet-5-5-2.cost_usd` | 0.060395 |  | lower | no |
| `turn.claude-sonnet-5-5-3.engine_s` | 0.002 |  | lower | no |
| `turn.claude-sonnet-5-5-3.first_verified_s` | 2.562 |  | lower | no |
| `turn.claude-sonnet-5-5-3.removed_share` | 0.704 |  | lower | no |
| `turn.claude-sonnet-5-5-3.done_s` | 105.122 |  | lower | no |
| `turn.claude-sonnet-5-5-3.cost_usd` | 0.064941 |  | lower | no |
| `turn.claude-sonnet-5-5-4.engine_s` | 0.001 |  | lower | no |
| `turn.claude-sonnet-5-5-4.first_verified_s` | 53.615 |  | lower | no |
| `turn.claude-sonnet-5-5-4.removed_share` | 0.724 |  | lower | no |
| `turn.claude-sonnet-5-5-4.done_s` | 343.649 |  | lower | no |
| `turn.claude-sonnet-5-5-4.cost_usd` | 0.070663 |  | lower | no |
| `turn.claude-sonnet-5-5-6.engine_s` | 0.002 |  | lower | no |
| `turn.claude-sonnet-5-5-6.first_verified_s` | 3.507 |  | lower | no |
| `turn.claude-sonnet-5-5-6.removed_share` | 0.444 |  | lower | no |
| `turn.claude-sonnet-5-5-6.done_s` | 211.199 |  | lower | no |
| `turn.claude-sonnet-5-5-6.cost_usd` | 0.054651 |  | lower | no |
| `turn.claude-sonnet-5-5-7.engine_s` | 0.002 |  | lower | no |
| `turn.claude-sonnet-5-5-7.first_verified_s` | 1.548 |  | lower | no |
| `turn.claude-sonnet-5-5-7.removed_share` | 0.591 |  | lower | no |
| `turn.claude-sonnet-5-5-7.done_s` | 98.135 |  | lower | no |
| `turn.claude-sonnet-5-5-7.cost_usd` | 0.066513 |  | lower | no |
| `turn.median.engine_s` | 0.002 |  | lower | no |
| `turn.median.first_verified_s` | 34.198 |  | lower | no |
| `turn.median.removed_share` | 0.5605 |  | lower | no |
| `turn.median.done_s` | 110.508 |  | lower | no |
| `turn.median.cost_usd` | 0.013309 |  | lower | no |
| `paragraph.complete` | 4 |  | higher | no |
| `paragraph.partial` | 2 |  | lower | no |
| `paragraph.none` | 0 |  | lower | no |
| `paragraph.writer_rounds_mean` | 3.0 |  | lower | no |
| `paragraph.ended_early` | 0 |  | lower | no |
| `paragraph.sentences_held_attempt_1` | 9 |  | informational | no |
| `paragraph.sentences_held_attempt_2` | 6 |  | informational | no |
| `paragraph.sentences_held_attempt_3` | 7 |  | informational | no |
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
- checker benchmark: tests/test_checker_bench.py:129: set JYOTISH_LIVE_NARRATION=1 to call the API

