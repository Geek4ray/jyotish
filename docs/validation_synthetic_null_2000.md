# Synthetic — Validation — null, N = 2,000, odds ratio 1.0 per SD

Run 2026-10-23 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1520 development, 480 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold. The split assigns by household: 0 households straddle it. The registry is not used for a synthetic cohort.

## Synthetic — Pre-registration hashes (test 10)

- rule set `8f86556c59c29d96491790ac386e9b168b795fbcf31ee835bb93bbe98ab62af0`
- weight set `4b551c99e2a9de896fcbcdf761dc91ea8a976d648b3f9e2226dbc3c0de3301b6`
- (the analysis code is validate.py with jyotish.cohort, jyotish.outcomes and the outcome map; the lift interval resamples households)
- split definition `3430fe1bd38c0112fb39a1e95936e93bff28cc60ffdaf69363ea8788dcd4114f` ({"salt_sha256": "19287501b03b53760b7a0eac16e4af0438c9bde072eec135d455423dcaaa3cb9", "fraction": 0.25, "k": 5, "unit": "household", "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "2250976227f0c6ab3af9cc4de34cc4fa26f23c9780f027075e18a9ca940723d3"})
- analysis code `6518b038ea6548fc1b8d38d49210bd49953b24ea2b0966177acf6fb260748dee`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain). Abstention is by accuracy class (approximate, unknown), the gate's stand-in: the sampler did not run.

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1520 | 1.000 | 0.307 | 0.941 | 0.848–1.030 | 0.8382 | 0.8901 | no | 0.283 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1520 | 1.000 | 0.506 | 1.005 | 0.932–1.077 | 0.4905 | 0.7708 | no | 0.217 |
| children | 1520 | 1.000 | 0.312 | 1.044 | 0.927–1.163 | 0.2398 | 0.6593 | no | 0.246 |
| intellect | 1520 | 1.000 | 0.306 | 1.004 | 0.895–1.123 | 0.4875 | 0.7708 | no | 0.267 |
| health | 1520 | 1.000 | 0.505 | 0.997 | 0.941–1.056 | 0.6194 | 0.8516 | no | 0.258 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1520 | 1.000 | 0.308 | 1.047 | 0.931–1.157 | 0.1409 | 0.5165 | no | 0.261 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1520 | 1.000 | 0.286 | 0.934 | 0.832–1.050 | 0.8901 | 0.8901 | no | 0.284 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1520 | 1.000 | 0.514 | 1.051 | 0.979–1.125 | 0.0769 | 0.5165 | no | 0.214 |
| gains | 1520 | 1.000 | 0.307 | 0.996 | 0.890–1.102 | 0.4885 | 0.7708 | no | 0.274 |
| foreign | 1520 | 1.000 | 0.320 | 0.968 | 0.876–1.061 | 0.8302 | 0.8901 | no | 0.277 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1520 | 1.000 | 0.306 | 1.059 | 0.946–1.170 | 0.1369 | 0.5165 | no | 0.264 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p (two-sided; a fall is marked) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1520 | 1.000 | 8 | 12.08 | 8 | 0.1475 | 0.495 | 0.494 | 0.8722 (AUC fell) |
| mother_home | 1520 | 1.000 | 8 | 13.53 | 8 | 0.0949 | 0.492 | 0.507 | 0.1246 |
| children | 1520 | 1.000 | 7 | 16.91 | 7 | 0.0180 | 0.489 | 0.513 | 0.0914 |
| intellect | 1520 | 1.000 | 8 | 8.95 | 8 | 0.3462 | 0.508 | 0.524 | 0.2524 |
| health | 1520 | 1.000 | 8 | 5.45 | 8 | 0.7083 | 0.518 | 0.502 | 0.1110 (AUC fell) |
| marriage | 1520 | 1.000 | 8 | 7.12 | 8 | 0.5232 | 0.504 | 0.504 | 0.9855 (AUC fell) |
| father | 1520 | 1.000 | 7 | 15.15 | 7 | 0.0342 | 0.495 | 0.503 | 0.6629 |
| career | 1520 | 1.000 | 8 | 4.37 | 8 | 0.8227 | 0.483 | 0.500 | 0.2205 |
| gains | 1520 | 1.000 | 8 | 14.64 | 8 | 0.0665 | 0.495 | 0.494 | 0.9453 (AUC fell) |
| foreign | 1520 | 1.000 | 7 | 5.02 | 7 | 0.6573 | 0.502 | 0.481 | 0.1991 (AUC fell) |
| reputation | 1520 | 1.000 | 8 | 12.41 | 8 | 0.1340 | 0.508 | 0.528 | 0.2052 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside one of the engine's own windows, the timing join's pieces over the life to 2026-10-23, the best third of the life by joint (so a third of the person-years are active for everyone). Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1520 | 1.000 | 73727 | 467 | 0.285 | 1.218 | 0.0697 | 0.199 (0.005, 0.393) |
| mother_home | 1520 | 1.000 | 63828 | 769 | 0.288 | 1.066 | 0.2786 | 0.065 (-0.090, 0.220) |
| children | 1520 | 1.000 | 73550 | 475 | 0.284 | 1.066 | 0.3930 | 0.064 (-0.134, 0.262) |
| intellect | 1520 | 1.000 | 73912 | 465 | 0.288 | 0.906 | 0.9453 | -0.099 (-0.305, 0.107) |
| health | 1520 | 1.000 | 64194 | 768 | 0.291 | 0.984 | 0.7562 | -0.016 (-0.173, 0.141) |
| marriage | 1520 | 1.000 | 73747 | 468 | 0.287 | 0.934 | 0.8507 | -0.069 (-0.273, 0.135) |
| father | 1520 | 1.000 | 74619 | 435 | 0.286 | 0.982 | 0.6269 | -0.019 (-0.228, 0.191) |
| career | 1520 | 1.000 | 64070 | 782 | 0.288 | 1.098 | 0.3333 | 0.095 (-0.058, 0.248) |
| gains | 1520 | 1.000 | 73727 | 467 | 0.284 | 1.189 | 0.0796 | 0.176 (-0.020, 0.371) |
| foreign | 1520 | 1.000 | 72973 | 486 | 0.287 | 0.914 | 0.8706 | -0.091 (-0.292, 0.110) |
| reputation | 1520 | 1.000 | 73912 | 465 | 0.286 | 0.887 | 0.9353 | -0.121 (-0.328, 0.087) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1520 | 1.000 | 0.065 | 0.013 | 3 | 0 | not allowed |
| mother_home | 1520 | 1.000 | 0.052 | 0.021 | 6 | 0 | not allowed |
| children | 1520 | 1.000 | 0.026 | 0.049 | 6 | 1 | not allowed |
| intellect | 1520 | 1.000 | 0.056 | 0.021 | 4 | 0 | not allowed |
| health | 1520 | 1.000 | 0.050 | 0.025 | 5 | 0 | not allowed |
| marriage | 1520 | 1.000 | 0.038 | 0.021 | 5 | 0 | not allowed |
| father | 1520 | 1.000 | 0.025 | 0.006 | 2 | 6 | not allowed |
| career | 1520 | 1.000 | 0.078 | 0.072 | 3 | 0 | not allowed |
| gains | 1520 | 1.000 | 0.054 | 0.011 | 4 | 0 | not allowed |
| foreign | 1520 | 1.000 | 0.036 | 0.043 | 2 | 0 | not allowed |
| reputation | 1520 | 1.000 | 0.081 | 0.021 | 4 | 0 | not allowed |

## Synthetic — School-split (test 8)

Each school's score is the sum of its families' votes (Parashari: house, lord, karaka, varga, panchanga; Jaimini: arudha; KP: kp; Nadi has no Layer 5 family in v1). The school with the highest AUC on the development set is chosen there; its AUC on the sequestered cohort is estimated only when that cohort is scored, so the winner's curse is paid on development data.

| area | n | Parashari AUC (95% CI) | Jaimini | KP | chosen | AUC on sequestered (95% CI) |
| --- | --- | --- | --- | --- | --- | --- |
| wealth | 1520 | 0.492 (0.462–0.522), n 1520 | 0.479 (0.450–0.508), n 1520 | no vote in this area | parashari | 0.505 (0.450–0.561) |
| mother_home | 1520 | 0.531 (0.503–0.559), n 1520 | 0.495 (0.469–0.521), n 1520 | 0.484 (0.457–0.511), n 1520 | parashari | 0.495 (0.445–0.545) |
| children | 1520 | 0.524 (0.493–0.554), n 1520 | 0.530 (0.502–0.557), n 1520 | 0.492 (0.463–0.521), n 1520 | jaimini | 0.488 (0.435–0.540) |
| intellect | 1520 | 0.511 (0.481–0.542), n 1520 | 0.509 (0.480–0.538), n 1520 | no vote in this area | parashari | 0.525 (0.471–0.579) |
| health | 1520 | 0.502 (0.474–0.530), n 1520 | no vote in this area | 0.508 (0.481–0.535), n 1520 | kp | 0.511 (0.462–0.560) |
| marriage | 1520 | 0.501 (0.470–0.531), n 1520 | 0.494 (0.466–0.523), n 1520 | 0.501 (0.472–0.530), n 1520 | parashari | 0.483 (0.430–0.537) |
| father | 1520 | 0.477 (0.446–0.508), n 1520 | 0.504 (0.475–0.533), n 1520 | no vote in this area | jaimini | 0.516 (0.466–0.566) |
| career | 1520 | 0.521 (0.493–0.549), n 1520 | 0.511 (0.485–0.537), n 1520 | 0.496 (0.468–0.523), n 1520 | parashari | 0.491 (0.440–0.541) |
| gains | 1520 | 0.491 (0.460–0.521), n 1520 | 0.490 (0.461–0.519), n 1520 | no vote in this area | parashari | 0.524 (0.469–0.579) |
| foreign | 1520 | 0.490 (0.460–0.521), n 1520 | 0.509 (0.481–0.537), n 1520 | no vote in this area | jaimini | 0.519 (0.465–0.572) |
| reputation | 1520 | 0.508 (0.478–0.538), n 1520 | 0.505 (0.476–0.534), n 1520 | no vote in this area | parashari | 0.528 (0.472–0.583) |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1520 | 1.000 | 571 | 0.283 | 0.515 |
| mother_home | 1520 | 1.000 | 464 | 0.217 | 0.435 |
| children | 1520 | 1.000 | 429 | 0.246 | 0.468 |
| intellect | 1520 | 1.000 | 485 | 0.267 | 0.494 |
| health | 1520 | 1.000 | 639 | 0.258 | 0.487 |
| marriage | 1520 | 1.000 | 462 | 0.261 | 0.487 |
| father | 1520 | 1.000 | 524 | 0.284 | 0.515 |
| career | 1520 | 1.000 | 453 | 0.214 | 0.430 |
| gains | 1520 | 1.000 | 513 | 0.274 | 0.503 |
| foreign | 1520 | 1.000 | 562 | 0.277 | 0.508 |
| reputation | 1520 | 1.000 | 463 | 0.264 | 0.490 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 360 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1520 | 127 | -0.053 | -0.144–0.038 | 0.2512 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1520 | 126 | 0.027 | -0.063–0.118 | 0.5534 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1520 | 123 | -0.038 | -0.130–0.054 | 0.4204 | 0.064 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1520 | 131 | 0.034 | -0.051–0.120 | 0.4298 | 0.086 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1520 | 126 | 0.036 | -0.055–0.127 | 0.4352 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1520 | 116 | 0.096 | 0.004–0.189 | 0.0419 | 0.061 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1520 | 129 | 0.003 | -0.080–0.087 | 0.9419 | 0.087 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1520 | 145 | -0.025 | -0.103–0.053 | 0.5247 | 0.095 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1520 | 118 | -0.033 | -0.127–0.061 | 0.4870 | 0.062 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1520 | 122 | 0.013 | -0.073–0.099 | 0.7710 | 0.083 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1520 | 136 | 0.027 | -0.061–0.114 | 0.5544 | 0.071 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1520 | 121 | -0.015 | -0.101–0.071 | 0.7287 | 0.079 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1520 | 118 | 0.054 | -0.032–0.139 | 0.2194 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1520 | 121 | -0.019 | -0.108–0.069 | 0.6682 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1520 | 126 | 0.005 | -0.081–0.091 | 0.9175 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1520 | 141 | -0.019 | -0.102–0.064 | 0.6553 | 0.077 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1520 | 143 | 0.002 | -0.079–0.083 | 0.9611 | 0.078 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1520 | 140 | 0.002 | -0.080–0.084 | 0.9626 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1520 | 126 | -0.056 | -0.145–0.033 | 0.2154 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1520 | 115 | -0.011 | -0.102–0.079 | 0.8088 | 0.062 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1520 | 131 | -0.015 | -0.100–0.071 | 0.7319 | 0.071 | not_testable_yet (under-powered) |
| `place.jupiter_in_scorpio` | 1520 | 135 | 0.102 | 0.025–0.179 | 0.0091 | 0.073 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1520 | 112 | -0.050 | -0.144–0.043 | 0.2928 | 0.060 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1520 | 112 | -0.002 | -0.093–0.089 | 0.9669 | 0.060 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1520 | 134 | 0.027 | -0.062–0.115 | 0.5504 | 0.070 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1520 | 133 | -0.086 | -0.174–0.002 | 0.0565 | 0.069 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1520 | 124 | 0.054 | -0.037–0.146 | 0.2412 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1520 | 131 | -0.032 | -0.114–0.049 | 0.4351 | 0.085 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1520 | 126 | 0.027 | -0.063–0.118 | 0.5534 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1520 | 102 | 0.037 | -0.063–0.137 | 0.4680 | 0.054 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1520 | 137 | 0.047 | -0.036–0.131 | 0.2658 | 0.093 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1520 | 130 | 0.062 | -0.024–0.148 | 0.1595 | 0.088 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1520 | 135 | 0.023 | -0.066–0.111 | 0.6145 | 0.070 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1520 | 126 | 0.054 | -0.033–0.141 | 0.2268 | 0.086 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1520 | 119 | -0.029 | -0.122–0.065 | 0.5502 | 0.062 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1520 | 123 | 0.112 | 0.021–0.203 | 0.0153 | 0.083 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1520 | 182 | -0.001 | -0.073–0.071 | 0.9740 | 0.116 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1520 | 96 | 0.059 | -0.041–0.159 | 0.2467 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1520 | 125 | -0.096 | -0.174–-0.018 | 0.0163 | 0.081 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1520 | 145 | -0.033 | -0.111–0.045 | 0.4025 | 0.093 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1520 | 116 | -0.029 | -0.115–0.058 | 0.5129 | 0.076 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1520 | 103 | 0.084 | -0.014–0.182 | 0.0915 | 0.070 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1520 | 134 | 0.001 | -0.081–0.084 | 0.9760 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1520 | 162 | -0.012 | -0.088–0.063 | 0.7467 | 0.104 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1520 | 137 | -0.039 | -0.118–0.041 | 0.3419 | 0.089 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1520 | 102 | 0.025 | -0.070–0.120 | 0.6058 | 0.069 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1520 | 110 | 0.018 | -0.074–0.110 | 0.7013 | 0.073 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1520 | 108 | 0.074 | -0.021–0.170 | 0.1249 | 0.073 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1520 | 113 | -0.061 | -0.149–0.026 | 0.1690 | 0.070 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1520 | 133 | 0.054 | -0.034–0.142 | 0.2291 | 0.069 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1520 | 110 | -0.025 | -0.122–0.072 | 0.6077 | 0.057 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1520 | 127 | -0.009 | -0.095–0.077 | 0.8372 | 0.069 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1520 | 119 | 0.025 | -0.068–0.119 | 0.5948 | 0.062 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1520 | 112 | 0.004 | -0.093–0.100 | 0.9406 | 0.058 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1520 | 135 | 0.031 | -0.051–0.113 | 0.4568 | 0.073 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1520 | 128 | -0.084 | -0.172–0.005 | 0.0651 | 0.070 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1520 | 121 | 0.032 | -0.045–0.108 | 0.4168 | 0.075 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1520 | 142 | -0.001 | -0.083–0.081 | 0.9792 | 0.077 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1520 | 139 | -0.001 | -0.076–0.074 | 0.9879 | 0.089 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1520 | 141 | -0.034 | -0.117–0.050 | 0.4277 | 0.077 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1520 | 121 | -0.031 | -0.114–0.051 | 0.4594 | 0.076 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1520 | 115 | 0.027 | -0.068–0.121 | 0.5812 | 0.060 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1520 | 118 | -0.043 | -0.137–0.051 | 0.3662 | 0.061 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1520 | 128 | 0.028 | -0.056–0.112 | 0.5136 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1520 | 150 | 0.006 | -0.078–0.090 | 0.8865 | 0.078 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1520 | 114 | 0.032 | -0.063–0.127 | 0.5126 | 0.060 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1520 | 110 | -0.075 | -0.170–0.020 | 0.1220 | 0.059 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1520 | 128 | 0.002 | -0.084–0.087 | 0.9688 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1520 | 127 | -0.077 | -0.161–0.006 | 0.0705 | 0.081 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1520 | 152 | 0.039 | -0.039–0.116 | 0.3284 | 0.082 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1520 | 119 | 0.046 | -0.030–0.122 | 0.2328 | 0.073 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1520 | 138 | 0.013 | -0.069–0.095 | 0.7513 | 0.075 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1520 | 122 | -0.039 | -0.128–0.051 | 0.3966 | 0.066 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1520 | 121 | 0.026 | -0.060–0.113 | 0.5521 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1520 | 113 | -0.036 | -0.129–0.056 | 0.4426 | 0.061 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1520 | 114 | -0.014 | -0.102–0.074 | 0.7597 | 0.075 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1520 | 136 | 0.040 | -0.041–0.121 | 0.3300 | 0.074 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1520 | 141 | 0.052 | -0.027–0.131 | 0.1953 | 0.076 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1520 | 110 | -0.028 | -0.125–0.069 | 0.5763 | 0.057 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1520 | 128 | -0.029 | -0.119–0.062 | 0.5337 | 0.066 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1520 | 121 | 0.057 | -0.028–0.141 | 0.1887 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1520 | 126 | 0.049 | -0.042–0.139 | 0.2912 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1520 | 156 | -0.048 | -0.128–0.032 | 0.2407 | 0.086 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1520 | 132 | -0.060 | -0.139–0.019 | 0.1392 | 0.085 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1520 | 132 | 0.094 | 0.006–0.182 | 0.0365 | 0.069 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1520 | 125 | 0.004 | -0.074–0.083 | 0.9113 | 0.078 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1520 | 126 | -0.002 | -0.081–0.076 | 0.9576 | 0.079 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1520 | 132 | -0.024 | -0.110–0.061 | 0.5787 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1520 | 107 | -0.049 | -0.138–0.040 | 0.2785 | 0.066 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1520 | 104 | -0.017 | -0.104–0.070 | 0.7077 | 0.063 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1520 | 143 | -0.029 | -0.112–0.054 | 0.4941 | 0.078 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1520 | 146 | 0.025 | -0.055–0.104 | 0.5402 | 0.080 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1520 | 118 | -0.052 | -0.145–0.042 | 0.2796 | 0.062 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1520 | 137 | -0.051 | -0.137–0.034 | 0.2388 | 0.074 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1520 | 144 | 0.017 | -0.069–0.103 | 0.6943 | 0.075 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1520 | 106 | 0.002 | -0.092–0.095 | 0.9672 | 0.057 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1520 | 121 | 0.032 | -0.045–0.108 | 0.4168 | 0.075 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1520 | 112 | -0.006 | -0.102–0.090 | 0.9029 | 0.058 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1520 | 127 | -0.037 | -0.128–0.053 | 0.4209 | 0.066 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1520 | 132 | 0.005 | -0.079–0.089 | 0.9021 | 0.072 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1520 | 133 | 0.054 | -0.034–0.142 | 0.2291 | 0.069 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1520 | 136 | 0.016 | -0.072–0.104 | 0.7146 | 0.070 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1520 | 112 | -0.067 | -0.161–0.027 | 0.1611 | 0.060 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1520 | 143 | 0.048 | -0.030–0.127 | 0.2289 | 0.078 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1520 | 112 | 0.023 | -0.058–0.103 | 0.5826 | 0.068 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1520 | 127 | -0.011 | -0.098–0.076 | 0.8007 | 0.068 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1520 | 145 | -0.020 | -0.095–0.055 | 0.6036 | 0.094 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1520 | 120 | 0.069 | -0.015–0.152 | 0.1082 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1520 | 128 | -0.024 | -0.103–0.056 | 0.5631 | 0.081 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1520 | 117 | -0.076 | -0.170–0.018 | 0.1127 | 0.061 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1520 | 120 | -0.052 | -0.145–0.041 | 0.2741 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1520 | 130 | 0.050 | -0.032–0.132 | 0.2311 | 0.070 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1520 | 129 | 0.048 | -0.042–0.137 | 0.2968 | 0.067 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1520 | 117 | 0.035 | -0.059–0.129 | 0.4620 | 0.061 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1520 | 124 | -0.008 | -0.095–0.079 | 0.8585 | 0.067 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1520 | 122 | -0.016 | -0.105–0.072 | 0.7181 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1520 | 130 | 0.040 | -0.034–0.113 | 0.2876 | 0.081 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1520 | 123 | 0.038 | -0.047–0.124 | 0.3802 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1520 | 134 | -0.060 | -0.140–0.021 | 0.1470 | 0.086 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1520 | 146 | -0.012 | -0.094–0.069 | 0.7660 | 0.080 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1520 | 105 | 0.107 | 0.022–0.192 | 0.0140 | 0.056 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1520 | 149 | 0.012 | -0.068–0.091 | 0.7717 | 0.081 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1520 | 125 | -0.014 | -0.101–0.074 | 0.7594 | 0.068 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1520 | 145 | 0.052 | -0.033–0.136 | 0.2319 | 0.075 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1520 | 155 | -0.010 | -0.089–0.069 | 0.8057 | 0.085 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1520 | 113 | -0.044 | -0.137–0.049 | 0.3492 | 0.061 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1520 | 102 | 0.049 | -0.047–0.145 | 0.3161 | 0.071 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1520 | 143 | -0.017 | -0.104–0.069 | 0.6908 | 0.074 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1520 | 112 | -0.050 | -0.144–0.043 | 0.2928 | 0.060 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1520 | 130 | 0.017 | -0.073–0.107 | 0.7087 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1520 | 116 | -0.008 | -0.098–0.082 | 0.8628 | 0.062 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1520 | 125 | -0.015 | -0.106–0.077 | 0.7498 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1520 | 126 | 0.022 | -0.063–0.107 | 0.6143 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1520 | 146 | 0.017 | -0.063–0.097 | 0.6721 | 0.080 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1520 | 120 | -0.032 | -0.121–0.058 | 0.4890 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1520 | 121 | -0.015 | -0.108–0.078 | 0.7495 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1520 | 144 | -0.018 | -0.100–0.064 | 0.6599 | 0.079 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1520 | 127 | -0.001 | -0.087–0.085 | 0.9785 | 0.069 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1520 | 124 | -0.002 | -0.094–0.089 | 0.9606 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1520 | 124 | -0.050 | -0.132–0.031 | 0.2248 | 0.082 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1520 | 111 | 0.082 | -0.003–0.168 | 0.0591 | 0.059 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1520 | 128 | 0.003 | -0.087–0.094 | 0.9441 | 0.066 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1520 | 132 | -0.037 | -0.123–0.049 | 0.4005 | 0.072 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1520 | 117 | 0.106 | 0.014–0.197 | 0.0236 | 0.061 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1520 | 116 | 0.032 | -0.063–0.126 | 0.5116 | 0.061 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1520 | 123 | -0.079 | -0.165–0.006 | 0.0677 | 0.078 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1520 | 116 | -0.025 | -0.109–0.059 | 0.5565 | 0.072 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1520 | 133 | 0.061 | -0.020–0.142 | 0.1383 | 0.072 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1520 | 124 | 0.073 | 0.002–0.144 | 0.0450 | 0.076 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1520 | 121 | -0.040 | -0.123–0.043 | 0.3446 | 0.076 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1520 | 126 | 0.005 | -0.081–0.091 | 0.9175 | 0.068 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1520 | 120 | 0.005 | -0.083–0.092 | 0.9197 | 0.065 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1520 | 121 | -0.010 | -0.103–0.083 | 0.8294 | 0.063 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1520 | 152 | 0.020 | -0.058–0.099 | 0.6109 | 0.082 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1520 | 123 | -0.028 | -0.120–0.064 | 0.5535 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1520 | 145 | 0.012 | -0.069–0.092 | 0.7795 | 0.079 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1520 | 106 | 0.069 | -0.020–0.158 | 0.1289 | 0.056 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1520 | 131 | -0.033 | -0.119–0.054 | 0.4576 | 0.071 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1520 | 130 | -0.036 | -0.123–0.051 | 0.4182 | 0.070 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1520 | 130 | 0.012 | -0.077–0.102 | 0.7870 | 0.067 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1520 | 107 | 0.058 | -0.031–0.148 | 0.2002 | 0.057 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1520 | 129 | 0.020 | -0.064–0.105 | 0.6397 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1520 | 122 | -0.008 | -0.100–0.085 | 0.8731 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1520 | 137 | -0.011 | -0.099–0.077 | 0.8052 | 0.071 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1520 | 117 | 0.015 | -0.074–0.104 | 0.7377 | 0.062 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1520 | 129 | 0.019 | -0.065–0.104 | 0.6536 | 0.087 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1520 | 152 | -0.009 | -0.089–0.071 | 0.8302 | 0.083 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1520 | 130 | 0.063 | -0.026–0.151 | 0.1640 | 0.067 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1520 | 138 | -0.006 | -0.093–0.082 | 0.8968 | 0.072 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1520 | 130 | 0.023 | -0.052–0.098 | 0.5487 | 0.082 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1520 | 126 | -0.080 | -0.164–0.004 | 0.0628 | 0.080 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1520 | 119 | 0.024 | -0.063–0.111 | 0.5904 | 0.064 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1520 | 108 | -0.006 | -0.091–0.078 | 0.8827 | 0.066 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1520 | 122 | 0.051 | -0.023–0.126 | 0.1731 | 0.075 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1520 | 131 | -0.032 | -0.118–0.055 | 0.4717 | 0.071 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1520 | 150 | -0.010 | -0.090–0.070 | 0.8036 | 0.082 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1520 | 111 | -0.001 | -0.097–0.096 | 0.9868 | 0.058 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1520 | 135 | 0.007 | -0.077–0.091 | 0.8649 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1520 | 138 | 0.026 | -0.061–0.113 | 0.5583 | 0.072 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1520 | 112 | -0.017 | -0.109–0.075 | 0.7185 | 0.060 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1520 | 116 | -0.078 | -0.171–0.015 | 0.0987 | 0.063 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1520 | 128 | 0.071 | -0.010–0.152 | 0.0878 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1520 | 111 | -0.111 | -0.207–-0.016 | 0.0223 | 0.060 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1520 | 128 | 0.060 | -0.027–0.148 | 0.1757 | 0.085 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1520 | 130 | -0.068 | -0.155–0.020 | 0.1310 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1520 | 128 | 0.019 | -0.065–0.104 | 0.6516 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1520 | 111 | 0.026 | -0.070–0.122 | 0.5994 | 0.058 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1520 | 137 | -0.009 | -0.097–0.079 | 0.8429 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1520 | 118 | 0.003 | -0.086–0.092 | 0.9531 | 0.063 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1520 | 139 | -0.050 | -0.137–0.037 | 0.2584 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1520 | 130 | -0.005 | -0.091–0.080 | 0.9061 | 0.070 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1520 | 144 | -0.039 | -0.116–0.039 | 0.3295 | 0.093 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1520 | 119 | -0.001 | -0.095–0.092 | 0.9808 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1520 | 134 | -0.016 | -0.105–0.073 | 0.7256 | 0.069 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1520 | 123 | -0.064 | -0.156–0.027 | 0.1693 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1520 | 124 | -0.032 | -0.116–0.052 | 0.4526 | 0.081 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1520 | 118 | -0.025 | -0.119–0.069 | 0.6036 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1520 | 132 | -0.041 | -0.130–0.048 | 0.3706 | 0.068 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1520 | 129 | -0.141 | -0.211–-0.070 | 0.0001 | 0.085 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1520 | 129 | -0.003 | -0.086–0.081 | 0.9504 | 0.086 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1520 | 119 | -0.010 | -0.104–0.083 | 0.8297 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1520 | 120 | 0.127 | 0.036–0.219 | 0.0065 | 0.083 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1520 | 136 | 0.010 | -0.078–0.098 | 0.8174 | 0.071 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1520 | 137 | -0.022 | -0.103–0.058 | 0.5841 | 0.089 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1520 | 93 | -0.021 | -0.126–0.084 | 0.6927 | 0.049 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1520 | 111 | -0.030 | -0.127–0.066 | 0.5400 | 0.058 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1520 | 140 | 0.094 | 0.009–0.180 | 0.0305 | 0.073 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1520 | 114 | 0.003 | -0.092–0.099 | 0.9456 | 0.059 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1520 | 123 | 0.006 | -0.086–0.098 | 0.8922 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1520 | 154 | -0.081 | -0.164–0.002 | 0.0547 | 0.079 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1520 | 157 | -0.013 | -0.095–0.070 | 0.7651 | 0.081 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1520 | 116 | -0.081 | -0.175–0.013 | 0.0913 | 0.060 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1520 | 101 | 0.032 | -0.068–0.133 | 0.5299 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1520 | 112 | 0.023 | -0.073–0.119 | 0.6396 | 0.059 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1520 | 150 | 0.043 | -0.041–0.127 | 0.3135 | 0.078 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1520 | 149 | 0.017 | -0.067–0.102 | 0.6855 | 0.077 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1520 | 113 | 0.056 | -0.039–0.152 | 0.2453 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1520 | 135 | -0.028 | -0.116–0.060 | 0.5333 | 0.070 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1520 | 114 | -0.006 | -0.102–0.089 | 0.8992 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1520 | 128 | -0.025 | -0.108–0.058 | 0.5549 | 0.083 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1520 | 129 | 0.065 | -0.025–0.154 | 0.1558 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1520 | 130 | 0.026 | -0.063–0.116 | 0.5662 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1520 | 107 | -0.009 | -0.099–0.081 | 0.8482 | 0.073 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1520 | 130 | -0.081 | -0.158–-0.004 | 0.0399 | 0.085 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1520 | 117 | -0.066 | -0.160–0.028 | 0.1684 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1520 | 151 | -0.048 | -0.122–0.027 | 0.2094 | 0.099 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1520 | 143 | -0.041 | -0.126–0.045 | 0.3551 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1520 | 123 | -0.012 | -0.097–0.074 | 0.7871 | 0.081 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1520 | 127 | -0.037 | -0.128–0.053 | 0.4209 | 0.066 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1520 | 104 | -0.047 | -0.146–0.053 | 0.3592 | 0.054 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1520 | 123 | -0.056 | -0.147–0.036 | 0.2363 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1520 | 123 | 0.077 | -0.014–0.168 | 0.0964 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1520 | 122 | 0.073 | -0.018–0.165 | 0.1154 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1520 | 118 | 0.058 | -0.035–0.151 | 0.2238 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1520 | 143 | -0.035 | -0.121–0.051 | 0.4217 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1520 | 146 | -0.046 | -0.132–0.039 | 0.2865 | 0.075 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1520 | 140 | 0.023 | -0.063–0.110 | 0.5970 | 0.073 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1520 | 138 | 0.016 | -0.071–0.103 | 0.7202 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1520 | 109 | -0.040 | -0.138–0.057 | 0.4170 | 0.057 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1520 | 127 | 0.014 | -0.076–0.105 | 0.7577 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1520 | 133 | -0.018 | -0.107–0.071 | 0.6895 | 0.069 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1520 | 136 | 0.024 | -0.063–0.112 | 0.5849 | 0.071 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1520 | 118 | -0.043 | -0.137–0.051 | 0.3662 | 0.061 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1520 | 120 | 0.051 | -0.039–0.141 | 0.2650 | 0.080 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1520 | 140 | 0.016 | -0.071–0.102 | 0.7258 | 0.073 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1520 | 116 | -0.006 | -0.101–0.088 | 0.8956 | 0.060 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1520 | 124 | 0.017 | -0.069–0.102 | 0.7026 | 0.084 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1520 | 141 | 0.015 | -0.066–0.096 | 0.7145 | 0.093 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1520 | 107 | 0.019 | -0.079–0.118 | 0.6974 | 0.056 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1520 | 129 | 0.011 | -0.073–0.095 | 0.7999 | 0.087 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1520 | 136 | -0.030 | -0.118–0.058 | 0.5039 | 0.071 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1520 | 120 | -0.003 | -0.090–0.083 | 0.9400 | 0.079 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1520 | 126 | 0.098 | 0.008–0.188 | 0.0319 | 0.066 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1520 | 137 | 0.012 | -0.075–0.100 | 0.7855 | 0.071 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1520 | 130 | 0.009 | -0.080–0.099 | 0.8373 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1520 | 135 | 0.007 | -0.076–0.090 | 0.8723 | 0.088 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1520 | 119 | -0.048 | -0.141–0.046 | 0.3178 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1520 | 123 | -0.029 | -0.121–0.063 | 0.5371 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1520 | 133 | -0.122 | -0.194–-0.051 | 0.0008 | 0.087 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1520 | 124 | 0.029 | -0.058–0.115 | 0.5191 | 0.083 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1520 | 131 | -0.060 | -0.149–0.029 | 0.1868 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1520 | 134 | 0.014 | -0.068–0.097 | 0.7354 | 0.090 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1520 | 126 | 0.012 | -0.080–0.103 | 0.8035 | 0.066 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1520 | 102 | -0.038 | -0.129–0.053 | 0.4127 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1520 | 103 | 0.009 | -0.085–0.103 | 0.8571 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1520 | 134 | -0.055 | -0.141–0.031 | 0.2132 | 0.073 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1520 | 145 | -0.068 | -0.152–0.015 | 0.1087 | 0.080 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1520 | 125 | -0.024 | -0.112–0.064 | 0.5949 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1520 | 137 | -0.029 | -0.114–0.055 | 0.4937 | 0.075 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1520 | 182 | 0.003 | -0.070–0.077 | 0.9274 | 0.101 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1520 | 96 | 0.061 | -0.033–0.154 | 0.2017 | 0.051 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1520 | 108 | 0.125 | 0.043–0.207 | 0.0029 | 0.058 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1520 | 116 | -0.017 | -0.107–0.074 | 0.7198 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1520 | 110 | 0.041 | -0.048–0.130 | 0.3658 | 0.059 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1520 | 102 | 0.047 | -0.045–0.139 | 0.3135 | 0.054 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1520 | 162 | -0.029 | -0.107–0.049 | 0.4653 | 0.090 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1520 | 136 | 0.035 | -0.053–0.122 | 0.4402 | 0.071 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1520 | 112 | 0.071 | -0.024–0.166 | 0.1425 | 0.059 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1520 | 122 | -0.042 | -0.135–0.050 | 0.3677 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1520 | 132 | 0.073 | -0.014–0.160 | 0.0986 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1520 | 116 | -0.109 | -0.202–-0.016 | 0.0221 | 0.060 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1520 | 119 | -0.029 | -0.123–0.064 | 0.5382 | 0.062 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1520 | 130 | 0.059 | -0.027–0.145 | 0.1762 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1520 | 159 | 0.030 | -0.047–0.108 | 0.4442 | 0.105 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1520 | 112 | 0.033 | -0.063–0.129 | 0.5021 | 0.059 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1520 | 128 | -0.004 | -0.087–0.080 | 0.9344 | 0.086 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1520 | 118 | -0.033 | -0.127–0.061 | 0.4870 | 0.062 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1520 | 136 | 0.020 | -0.063–0.104 | 0.6323 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1520 | 124 | 0.055 | -0.018–0.128 | 0.1404 | 0.077 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1520 | 139 | 0.007 | -0.067–0.082 | 0.8464 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1520 | 100 | -0.071 | -0.164–0.023 | 0.1384 | 0.061 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1520 | 126 | 0.041 | -0.033–0.115 | 0.2772 | 0.078 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1520 | 104 | 0.035 | -0.047–0.117 | 0.4017 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1520 | 131 | 0.008 | -0.068–0.084 | 0.8342 | 0.083 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1520 | 140 | 0.056 | -0.013–0.126 | 0.1102 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1520 | 114 | 0.027 | -0.052–0.106 | 0.5075 | 0.070 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1520 | 141 | -0.005 | -0.079–0.070 | 0.9047 | 0.090 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1520 | 150 | 0.012 | -0.059–0.083 | 0.7435 | 0.097 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1520 | 131 | -0.100 | -0.184–-0.017 | 0.0189 | 0.085 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1520 | 120 | -0.079 | -0.165–0.007 | 0.0730 | 0.076 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1520 | 101 | 0.074 | -0.026–0.174 | 0.1470 | 0.053 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1520 | 136 | -0.032 | -0.120–0.056 | 0.4755 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1520 | 112 | -0.064 | -0.160–0.032 | 0.1919 | 0.058 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1520 | 139 | -0.019 | -0.100–0.061 | 0.6364 | 0.090 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1520 | 136 | 0.073 | -0.014–0.160 | 0.1004 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1520 | 118 | 0.003 | -0.091–0.097 | 0.9553 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1520 | 124 | -0.036 | -0.118–0.046 | 0.3909 | 0.083 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1520 | 119 | -0.066 | -0.147–0.016 | 0.1161 | 0.079 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1520 | 116 | 0.069 | -0.025–0.163 | 0.1497 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1520 | 143 | -0.023 | -0.101–0.055 | 0.5571 | 0.095 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1520 | 140 | -0.084 | -0.171–0.002 | 0.0545 | 0.073 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1520 | 136 | 0.004 | -0.078–0.087 | 0.9211 | 0.089 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1520 | 121 | -0.029 | -0.122–0.064 | 0.5376 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1520 | 128 | 0.052 | -0.037–0.142 | 0.2527 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1520 | 126 | 0.019 | -0.072–0.110 | 0.6850 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1520 | 138 | 0.040 | -0.047–0.127 | 0.3695 | 0.072 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1520 | 121 | -0.002 | -0.095–0.091 | 0.9620 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1520 | 128 | 0.061 | -0.029–0.151 | 0.1827 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1520 | 120 | 0.002 | -0.091–0.096 | 0.9601 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1520 | 133 | -0.127 | -0.214–-0.040 | 0.0043 | 0.069 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1520 | 100 | 0.092 | -0.008–0.191 | 0.0713 | 0.053 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1520 | 131 | 0.013 | -0.076–0.103 | 0.7691 | 0.068 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1520 | 136 | -0.016 | -0.104–0.072 | 0.7235 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1520 | 138 | -0.080 | -0.167–0.007 | 0.0725 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1520 | 110 | 0.014 | -0.083–0.111 | 0.7783 | 0.058 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1520 | 122 | 0.020 | -0.072–0.112 | 0.6725 | 0.063 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1520 | 124 | -0.112 | -0.203–-0.022 | 0.0150 | 0.064 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1520 | 125 | 0.026 | -0.060–0.113 | 0.5505 | 0.082 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1520 | 144 | 0.038 | -0.048–0.123 | 0.3871 | 0.075 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1520 | 118 | -0.052 | -0.146–0.041 | 0.2728 | 0.061 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1520 | 106 | -0.006 | -0.096–0.085 | 0.9010 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1520 | 110 | -0.043 | -0.130–0.044 | 0.3324 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1520 | 132 | 0.036 | -0.053–0.125 | 0.4317 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1520 | 153 | -0.008 | -0.085–0.069 | 0.8369 | 0.101 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1520 | 143 | -0.010 | -0.096–0.076 | 0.8258 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1520 | 133 | -0.004 | -0.087–0.078 | 0.9184 | 0.087 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1520 | 95 | -0.003 | -0.098–0.093 | 0.9541 | 0.066 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1520 | 123 | 0.045 | -0.042–0.133 | 0.3104 | 0.084 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1520 | 114 | 0.028 | -0.062–0.117 | 0.5485 | 0.078 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1520 | 176 | -0.078 | -0.146–-0.011 | 0.0234 | 0.113 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1520 | 139 | 0.025 | -0.057–0.107 | 0.5440 | 0.093 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1520 | 161 | -0.004 | -0.079–0.071 | 0.9176 | 0.106 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1520 | 136 | -0.064 | -0.140–0.013 | 0.1045 | 0.090 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1520 | 141 | 0.028 | -0.053–0.110 | 0.5002 | 0.095 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1520 | 107 | 0.051 | -0.043–0.145 | 0.2882 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1520 | 102 | -0.099 | -0.182–-0.015 | 0.0202 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1520 | 135 | 0.085 | -0.001–0.170 | 0.0520 | 0.092 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1520 | 91 | -0.000 | -0.098–0.098 | 0.9966 | 0.064 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1520 | 186 | 0.033 | -0.044–0.109 | 0.4045 | 0.096 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1520 | 764 | -0.013 | -0.064–0.037 | 0.6036 | 0.268 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1520 | 516 | -0.035 | -0.085–0.016 | 0.1790 | 0.277 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1520 | 138 | -0.009 | -0.092–0.074 | 0.8289 | 0.075 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1520 | 240 | -0.027 | -0.096–0.042 | 0.4412 | 0.123 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1520 | 794 | 0.017 | -0.033–0.067 | 0.5037 | 0.266 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1520 | 989 | 0.012 | -0.041–0.065 | 0.6524 | 0.239 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1520 | 262 | 0.032 | -0.034–0.099 | 0.3379 | 0.134 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1520 | 687 | 0.028 | -0.022–0.078 | 0.2761 | 0.263 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1520 | 535 | -0.007 | -0.057–0.043 | 0.7874 | 0.278 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1520 | 235 | 0.031 | -0.039–0.100 | 0.3855 | 0.121 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1520 | 280 | -0.005 | -0.069–0.060 | 0.8892 | 0.143 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
