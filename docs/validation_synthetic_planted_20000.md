# Synthetic — Validation — planted, N = 20,000, odds ratio 1.2 per SD

Run 2026-10-23 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 14894 development, 5106 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold. The split assigns by household: 0 households straddle it. The registry is not used for a synthetic cohort.

## Synthetic — Pre-registration hashes (test 10)

- rule set `8f86556c59c29d96491790ac386e9b168b795fbcf31ee835bb93bbe98ab62af0`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- (the analysis code is validate.py with jyotish.cohort, jyotish.outcomes and the outcome map; the lift interval resamples households)
- split definition `422d0b377aa693bfdcba66ed85d42c6bf64855aa93a9ed435c295d77f75a5f80` ({"salt_sha256": "b41f02ef8121a7213a6d734d2a8d039c0b2f4c63f7fdf3e6191158ac8a2bb206", "fraction": 0.25, "k": 5, "unit": "household", "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "9452785ccf381f8e5327a3e141d01ae257c25087fa2a5468d265d0a09421c1d1"})
- analysis code `6518b038ea6548fc1b8d38d49210bd49953b24ea2b0966177acf6fb260748dee`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain). Abstention is by accuracy class (approximate, unknown), the gate's stand-in: the sampler did not run.

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 14894 | 1.000 | 0.298 | 1.062 | 1.029–1.092 | 0.0010 | 0.0011 | yes | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 14894 | 1.000 | 0.508 | 1.089 | 1.066–1.114 | 0.0010 | 0.0011 | yes | 0.999 |
| children | 14894 | 1.000 | 0.302 | 1.089 | 1.047–1.129 | 0.0010 | 0.0011 | yes | 0.999 |
| intellect | 14894 | 1.000 | 0.303 | 1.139 | 1.104–1.175 | 0.0010 | 0.0011 | yes | 1.000 |
| health | 14894 | 1.000 | 0.510 | 1.067 | 1.050–1.086 | 0.0010 | 0.0011 | yes | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 14894 | 1.000 | 0.299 | 1.071 | 1.030–1.112 | 0.0010 | 0.0011 | yes | 1.000 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 14894 | 1.000 | 0.299 | 1.051 | 1.017–1.085 | 0.0010 | 0.0011 | yes | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 14894 | 1.000 | 0.517 | 1.059 | 1.035–1.082 | 0.0010 | 0.0011 | yes | 0.999 |
| gains | 14894 | 1.000 | 0.298 | 1.075 | 1.043–1.109 | 0.0010 | 0.0011 | yes | 1.000 |
| foreign | 14894 | 1.000 | 0.300 | 1.085 | 1.053–1.117 | 0.0010 | 0.0011 | yes | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 14894 | 1.000 | 0.303 | 1.043 | 1.008–1.079 | 0.0110 | 0.0110 | yes | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p (two-sided; a fall is marked) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14894 | 1.000 | 8 | 104.62 | 8 | 0.0000 | 0.506 | 0.536 | 0.0000 |
| mother_home | 14894 | 1.000 | 8 | 177.53 | 8 | 0.0000 | 0.510 | 0.555 | 0.0000 |
| children | 14894 | 1.000 | 7 | 89.15 | 7 | 0.0000 | 0.498 | 0.536 | 0.0000 |
| intellect | 14894 | 1.000 | 8 | 118.26 | 8 | 0.0000 | 0.509 | 0.544 | 0.0000 |
| health | 14894 | 1.000 | 8 | 153.34 | 8 | 0.0000 | 0.511 | 0.547 | 0.0000 |
| marriage | 14894 | 1.000 | 8 | 99.74 | 8 | 0.0000 | 0.504 | 0.537 | 0.0000 |
| father | 14894 | 1.000 | 7 | 52.35 | 7 | 0.0000 | 0.516 | 0.536 | 0.0001 |
| career | 14894 | 1.000 | 8 | 140.58 | 8 | 0.0000 | 0.508 | 0.545 | 0.0000 |
| gains | 14894 | 1.000 | 8 | 102.23 | 8 | 0.0000 | 0.506 | 0.536 | 0.0000 |
| foreign | 14894 | 1.000 | 7 | 103.22 | 7 | 0.0000 | 0.498 | 0.546 | 0.0000 |
| reputation | 14894 | 1.000 | 8 | 90.27 | 8 | 0.0000 | 0.509 | 0.541 | 0.0000 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside one of the engine's own windows, the timing join's pieces over the life to 2026-10-23, the best third of the life by joint (so a third of the person-years are active for everyone). Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14894 | 1.000 | 724484 | 4432 | 0.285 | 1.841 | 0.0050 | 0.614 (0.555, 0.674) |
| mother_home | 14894 | 1.000 | 625089 | 7565 | 0.287 | 1.554 | 0.0050 | 0.447 (0.400, 0.494) |
| children | 14894 | 1.000 | 720922 | 4496 | 0.282 | 1.874 | 0.0050 | 0.633 (0.574, 0.692) |
| intellect | 14894 | 1.000 | 720820 | 4517 | 0.287 | 1.833 | 0.0050 | 0.610 (0.551, 0.669) |
| health | 14894 | 1.000 | 623626 | 7595 | 0.290 | 1.801 | 0.0050 | 0.597 (0.551, 0.643) |
| marriage | 14894 | 1.000 | 723478 | 4446 | 0.286 | 1.891 | 0.0050 | 0.641 (0.582, 0.701) |
| father | 14894 | 1.000 | 722814 | 4453 | 0.287 | 1.290 | 0.0050 | 0.256 (0.194, 0.318) |
| career | 14894 | 1.000 | 619495 | 7705 | 0.289 | 1.637 | 0.0050 | 0.500 (0.454, 0.546) |
| gains | 14894 | 1.000 | 724484 | 4432 | 0.284 | 1.389 | 0.0050 | 0.331 (0.269, 0.392) |
| foreign | 14894 | 1.000 | 723116 | 4470 | 0.288 | 1.847 | 0.0050 | 0.619 (0.559, 0.678) |
| reputation | 14894 | 1.000 | 720820 | 4517 | 0.287 | 1.336 | 0.0050 | 0.292 (0.230, 0.353) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14894 | 1.000 | 0.008 | 0.018 | 5 | 0 | not allowed |
| mother_home | 14894 | 1.000 | 0.009 | 0.014 | 5 | 3 | not allowed |
| children | 14894 | 1.000 | 0.017 | 0.008 | 6 | 0 | not allowed |
| intellect | 14894 | 1.000 | 0.013 | 0.003 | 6 | 0 | not allowed |
| health | 14894 | 1.000 | 0.016 | 0.008 | 7 | 1 | not allowed |
| marriage | 14894 | 1.000 | 0.014 | 0.011 | 5 | 1 | not allowed |
| father | 14894 | 1.000 | 0.008 | 0.014 | 3 | 24 | not allowed |
| career | 14894 | 1.000 | 0.006 | 0.011 | 6 | 1 | not allowed |
| gains | 14894 | 1.000 | 0.010 | 0.018 | 5 | 0 | not allowed |
| foreign | 14894 | 1.000 | 0.015 | 0.003 | 5 | 0 | not allowed |
| reputation | 14894 | 1.000 | 0.010 | 0.006 | 2 | 605 | allowed |

## Synthetic — School-split (test 8)

Each school's score is the sum of its families' votes (Parashari: house, lord, karaka, varga, panchanga; Jaimini: arudha; KP: kp; Nadi has no Layer 5 family in v1). The school with the highest AUC on the development set is chosen there; its AUC on the sequestered cohort is estimated only when that cohort is scored, so the winner's curse is paid on development data.

| area | n | Parashari AUC (95% CI) | Jaimini | KP | chosen | AUC on sequestered (95% CI) |
| --- | --- | --- | --- | --- | --- | --- |
| wealth | 14894 | 0.524 (0.514–0.533), n 14894 | 0.495 (0.485–0.504), n 14894 | no vote in this area | parashari | 0.553 (0.537–0.570) |
| mother_home | 14894 | 0.541 (0.532–0.550), n 14894 | 0.503 (0.494–0.511), n 14894 | 0.494 (0.486–0.503), n 14894 | parashari | 0.536 (0.520–0.551) |
| children | 14894 | 0.535 (0.525–0.545), n 14894 | 0.496 (0.487–0.505), n 14894 | 0.500 (0.490–0.509), n 14894 | parashari | 0.536 (0.520–0.553) |
| intellect | 14894 | 0.539 (0.529–0.548), n 14894 | 0.498 (0.489–0.508), n 14894 | no vote in this area | parashari | 0.530 (0.513–0.547) |
| health | 14894 | 0.538 (0.529–0.547), n 14894 | no vote in this area | 0.505 (0.496–0.514), n 14894 | parashari | 0.532 (0.516–0.547) |
| marriage | 14894 | 0.527 (0.518–0.537), n 14894 | 0.504 (0.495–0.513), n 14894 | 0.507 (0.498–0.517), n 14894 | parashari | 0.528 (0.511–0.544) |
| father | 14894 | 0.517 (0.507–0.527), n 14894 | 0.496 (0.487–0.505), n 14894 | no vote in this area | parashari | 0.514 (0.497–0.530) |
| career | 14894 | 0.535 (0.526–0.544), n 14894 | 0.499 (0.491–0.508), n 14894 | 0.497 (0.489–0.506), n 14894 | parashari | 0.528 (0.513–0.543) |
| gains | 14894 | 0.524 (0.514–0.534), n 14894 | 0.506 (0.497–0.515), n 14894 | no vote in this area | parashari | 0.534 (0.518–0.551) |
| foreign | 14894 | 0.528 (0.518–0.538), n 14894 | 0.505 (0.495–0.514), n 14894 | no vote in this area | parashari | 0.538 (0.522–0.555) |
| reputation | 14894 | 0.521 (0.511–0.531), n 14894 | 0.499 (0.489–0.508), n 14894 | no vote in this area | parashari | 0.508 (0.491–0.525) |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 14894 | 1.000 | 5391 | 1.000 | 1.000 |
| mother_home | 14894 | 1.000 | 4377 | 0.999 | 1.000 |
| children | 14894 | 1.000 | 4083 | 0.999 | 1.000 |
| intellect | 14894 | 1.000 | 4737 | 1.000 | 1.000 |
| health | 14894 | 1.000 | 6207 | 1.000 | 1.000 |
| marriage | 14894 | 1.000 | 4111 | 1.000 | 1.000 |
| father | 14894 | 1.000 | 5138 | 1.000 | 1.000 |
| career | 14894 | 1.000 | 4387 | 0.999 | 1.000 |
| gains | 14894 | 1.000 | 5163 | 1.000 | 1.000 |
| foreign | 14894 | 1.000 | 5602 | 1.000 | 1.000 |
| reputation | 14894 | 1.000 | 4631 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 235 rules
- effect on development data: 10 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 115 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 14894 | 1206 | 0.025 | -0.004–0.055 | 0.0917 | 0.776 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 14894 | 1248 | -0.001 | -0.030–0.028 | 0.9237 | 0.792 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 14894 | 1271 | -0.022 | -0.051–0.007 | 0.1344 | 0.801 | classical_rejected (recommended: powered null) |
| `place.jupiter_h12` | 14894 | 1270 | -0.000 | -0.026–0.026 | 0.9922 | 0.862 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 14894 | 1210 | 0.006 | -0.023–0.036 | 0.6725 | 0.778 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 14894 | 1284 | 0.025 | -0.004–0.053 | 0.0922 | 0.805 | classical_rejected (recommended: powered null) |
| `place.jupiter_h4` | 14894 | 1211 | 0.022 | -0.005–0.049 | 0.1120 | 0.848 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 14894 | 1218 | 0.019 | -0.008–0.046 | 0.1708 | 0.847 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 14894 | 1210 | 0.020 | -0.010–0.049 | 0.1868 | 0.778 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 14894 | 1257 | -0.014 | -0.040–0.012 | 0.2902 | 0.859 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 14894 | 1236 | 0.027 | -0.002–0.056 | 0.0674 | 0.787 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 14894 | 1273 | 0.003 | -0.024–0.029 | 0.8509 | 0.863 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 14894 | 1161 | 0.006 | -0.022–0.034 | 0.6701 | 0.822 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 14894 | 1346 | -0.029 | -0.056–-0.002 | 0.0338 | 0.881 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 14894 | 1341 | 0.069 | 0.044–0.095 | 0.0000 | 0.875 | effect on development data |
| `place.jupiter_in_capricorn` | 14894 | 1269 | -0.073 | -0.101–-0.045 | 0.0000 | 0.863 | effect on development data |
| `place.jupiter_in_gemini` | 14894 | 1104 | -0.001 | -0.030–0.028 | 0.9606 | 0.800 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 14894 | 1314 | 0.019 | -0.008–0.045 | 0.1658 | 0.870 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 14894 | 1333 | -0.012 | -0.039–0.014 | 0.3626 | 0.877 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 14894 | 1116 | 0.006 | -0.023–0.035 | 0.6766 | 0.804 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_sagittarius` | 14894 | 1218 | 0.025 | -0.002–0.052 | 0.0733 | 0.841 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 14894 | 1241 | 0.042 | 0.015–0.069 | 0.0021 | 0.847 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 14894 | 1152 | -0.007 | -0.036–0.022 | 0.6295 | 0.819 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 14894 | 1299 | -0.044 | -0.071–-0.016 | 0.0019 | 0.870 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 14894 | 1275 | -0.005 | -0.034–0.023 | 0.7178 | 0.801 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 14894 | 1180 | 0.011 | -0.019–0.040 | 0.4825 | 0.767 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 14894 | 1244 | -0.029 | -0.058–-0.000 | 0.0468 | 0.791 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 14894 | 1257 | 0.002 | -0.025–0.028 | 0.9106 | 0.859 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 14894 | 1254 | 0.018 | -0.011–0.047 | 0.2304 | 0.794 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 14894 | 1265 | 0.029 | 0.000–0.058 | 0.0475 | 0.798 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 14894 | 1221 | -0.000 | -0.027–0.026 | 0.9827 | 0.850 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 14894 | 1233 | 0.022 | -0.005–0.049 | 0.1139 | 0.852 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 14894 | 1264 | -0.005 | -0.034–0.024 | 0.7437 | 0.797 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 14894 | 1248 | -0.015 | -0.042–0.011 | 0.2509 | 0.856 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 14894 | 1252 | 0.003 | -0.026–0.032 | 0.8335 | 0.793 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 14894 | 1201 | -0.012 | -0.039–0.015 | 0.3725 | 0.841 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 14894 | 1594 | -0.002 | -0.026–0.021 | 0.8442 | 0.930 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 14894 | 1133 | 0.017 | -0.011–0.045 | 0.2318 | 0.820 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 14894 | 1059 | -0.005 | -0.033–0.024 | 0.7359 | 0.790 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 14894 | 1500 | 0.017 | -0.008–0.042 | 0.1805 | 0.915 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 14894 | 1172 | -0.003 | -0.030–0.025 | 0.8553 | 0.832 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 14894 | 1167 | 0.005 | -0.022–0.033 | 0.7028 | 0.831 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 14894 | 1166 | 0.017 | -0.011–0.045 | 0.2354 | 0.831 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 14894 | 1421 | 0.008 | -0.017–0.033 | 0.5243 | 0.900 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 14894 | 1273 | -0.007 | -0.033–0.019 | 0.6045 | 0.863 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 14894 | 1146 | -0.024 | -0.051–0.003 | 0.0877 | 0.822 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 14894 | 1122 | -0.029 | -0.056–-0.001 | 0.0388 | 0.813 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 14894 | 1141 | -0.001 | -0.029–0.026 | 0.9229 | 0.821 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 14894 | 1293 | -0.002 | -0.026–0.023 | 0.8994 | 0.944 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 14894 | 1235 | 0.047 | 0.018–0.076 | 0.0015 | 0.787 | not_testable_yet (under-powered) |
| `place.l10_h11` | 14894 | 1266 | -0.039 | -0.068–-0.010 | 0.0082 | 0.799 | not_testable_yet (under-powered) |
| `place.l10_h12` | 14894 | 1218 | -0.018 | -0.046–0.010 | 0.2032 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 14894 | 1232 | 0.001 | -0.028–0.031 | 0.9213 | 0.787 | not_testable_yet (under-powered) |
| `place.l10_h3` | 14894 | 1241 | 0.003 | -0.026–0.032 | 0.8586 | 0.790 | not_testable_yet (under-powered) |
| `place.l10_h4` | 14894 | 1255 | 0.006 | -0.021–0.033 | 0.6590 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 14894 | 1210 | 0.022 | -0.006–0.049 | 0.1202 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 14894 | 1196 | 0.003 | -0.022–0.028 | 0.8342 | 0.924 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 14894 | 1243 | -0.020 | -0.048–0.008 | 0.1574 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 14894 | 1283 | 0.009 | -0.015–0.033 | 0.4566 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 14894 | 1222 | -0.006 | -0.034–0.022 | 0.6603 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 14894 | 1222 | 0.005 | -0.019–0.030 | 0.6638 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 14894 | 1197 | -0.014 | -0.043–0.016 | 0.3584 | 0.774 | not_testable_yet (under-powered) |
| `place.l11_h11` | 14894 | 1223 | 0.047 | 0.018–0.077 | 0.0014 | 0.783 | not_testable_yet (under-powered) |
| `place.l11_h12` | 14894 | 1223 | -0.021 | -0.049–0.007 | 0.1404 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 14894 | 1272 | -0.010 | -0.039–0.018 | 0.4803 | 0.801 | classical_rejected (recommended: powered null) |
| `place.l11_h3` | 14894 | 1254 | -0.003 | -0.032–0.026 | 0.8260 | 0.795 | not_testable_yet (under-powered) |
| `place.l11_h4` | 14894 | 1264 | -0.031 | -0.059–-0.003 | 0.0289 | 0.856 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 14894 | 1231 | 0.001 | -0.026–0.029 | 0.9346 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 14894 | 1235 | 0.003 | -0.022–0.028 | 0.8189 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 14894 | 1268 | 0.029 | 0.002–0.056 | 0.0337 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 14894 | 1216 | -0.005 | -0.030–0.020 | 0.7133 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 14894 | 1289 | -0.002 | -0.029–0.025 | 0.8878 | 0.864 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 14894 | 1229 | -0.001 | -0.028–0.027 | 0.9660 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 14894 | 1252 | -0.011 | -0.039–0.016 | 0.4264 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 14894 | 1189 | -0.002 | -0.030–0.026 | 0.8897 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 14894 | 1189 | 0.031 | 0.003–0.059 | 0.0276 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 14894 | 1223 | 0.014 | -0.014–0.041 | 0.3290 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 14894 | 1335 | -0.020 | -0.047–0.007 | 0.1386 | 0.878 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 14894 | 1262 | 0.017 | -0.012–0.046 | 0.2410 | 0.796 | not_testable_yet (under-powered) |
| `place.l12_h5` | 14894 | 1233 | 0.010 | -0.019–0.039 | 0.5167 | 0.786 | not_testable_yet (under-powered) |
| `place.l12_h6` | 14894 | 1225 | -0.015 | -0.043–0.013 | 0.2882 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 14894 | 1234 | 0.019 | -0.010–0.048 | 0.2009 | 0.786 | not_testable_yet (under-powered) |
| `place.l12_h8` | 14894 | 1305 | -0.003 | -0.030–0.024 | 0.8281 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 14894 | 1218 | 0.011 | -0.016–0.038 | 0.4205 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 14894 | 1181 | 0.041 | 0.012–0.071 | 0.0064 | 0.766 | not_testable_yet (under-powered) |
| `place.l1_h10` | 14894 | 1251 | -0.017 | -0.043–0.008 | 0.1766 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 14894 | 1255 | 0.019 | -0.005–0.043 | 0.1181 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 14894 | 1216 | -0.002 | -0.030–0.026 | 0.8925 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 14894 | 1242 | -0.011 | -0.037–0.014 | 0.3708 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 14894 | 1251 | 0.004 | -0.020–0.029 | 0.7224 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 14894 | 1264 | -0.031 | -0.058–-0.003 | 0.0311 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 14894 | 1214 | -0.026 | -0.055–0.002 | 0.0681 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 14894 | 1273 | 0.013 | -0.016–0.041 | 0.3836 | 0.800 | classical_rejected (recommended: powered null) |
| `place.l1_h7` | 14894 | 1228 | -0.020 | -0.048–0.008 | 0.1561 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 14894 | 1240 | 0.017 | -0.012–0.046 | 0.2425 | 0.789 | not_testable_yet (under-powered) |
| `place.l1_h9` | 14894 | 1279 | 0.012 | -0.015–0.039 | 0.4025 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 14894 | 1211 | 0.014 | -0.011–0.039 | 0.2664 | 0.927 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 14894 | 1299 | -0.014 | -0.043–0.014 | 0.3234 | 0.810 | classical_rejected (recommended: powered null) |
| `place.l2_h11` | 14894 | 1193 | 0.017 | -0.012–0.047 | 0.2545 | 0.772 | not_testable_yet (under-powered) |
| `place.l2_h12` | 14894 | 1257 | -0.005 | -0.033–0.022 | 0.7033 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 14894 | 1190 | 0.043 | 0.014–0.073 | 0.0040 | 0.770 | not_testable_yet (under-powered) |
| `place.l2_h3` | 14894 | 1296 | -0.013 | -0.042–0.015 | 0.3690 | 0.809 | classical_rejected (recommended: powered null) |
| `place.l2_h4` | 14894 | 1218 | 0.022 | -0.006–0.049 | 0.1192 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 14894 | 1276 | 0.008 | -0.019–0.035 | 0.5524 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 14894 | 1236 | -0.010 | -0.035–0.015 | 0.4292 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 14894 | 1251 | -0.004 | -0.032–0.023 | 0.7492 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 14894 | 1239 | -0.021 | -0.046–0.004 | 0.1063 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 14894 | 1228 | 0.000 | -0.028–0.028 | 0.9980 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 14894 | 1240 | -0.000 | -0.025–0.024 | 0.9707 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 14894 | 1199 | -0.003 | -0.032–0.027 | 0.8438 | 0.774 | not_testable_yet (under-powered) |
| `place.l3_h11` | 14894 | 1288 | -0.001 | -0.030–0.027 | 0.9390 | 0.806 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 14894 | 1213 | 0.003 | -0.025–0.030 | 0.8513 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 14894 | 1242 | 0.022 | -0.007–0.051 | 0.1298 | 0.790 | not_testable_yet (under-powered) |
| `place.l3_h3` | 14894 | 1266 | 0.018 | -0.011–0.047 | 0.2147 | 0.799 | not_testable_yet (under-powered) |
| `place.l3_h4` | 14894 | 1286 | -0.001 | -0.028–0.026 | 0.9362 | 0.861 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 14894 | 1276 | 0.009 | -0.018–0.036 | 0.5114 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 14894 | 1216 | -0.013 | -0.038–0.013 | 0.3240 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 14894 | 1218 | -0.000 | -0.028–0.027 | 0.9796 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 14894 | 1215 | -0.006 | -0.031–0.019 | 0.6502 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 14894 | 1235 | -0.020 | -0.048–0.008 | 0.1608 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 14894 | 1189 | -0.020 | -0.048–0.009 | 0.1785 | 0.828 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 14894 | 1219 | -0.024 | -0.053–0.004 | 0.0901 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 14894 | 1244 | 0.011 | -0.017–0.038 | 0.4396 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 14894 | 1270 | -0.007 | -0.036–0.022 | 0.6316 | 0.799 | not_testable_yet (under-powered) |
| `place.l4_h2` | 14894 | 1280 | 0.021 | -0.006–0.048 | 0.1241 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 14894 | 1203 | 0.004 | -0.024–0.032 | 0.7870 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 14894 | 1171 | 0.031 | 0.003–0.059 | 0.0290 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 14894 | 1290 | -0.007 | -0.036–0.021 | 0.6141 | 0.806 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 14894 | 1226 | -0.006 | -0.034–0.022 | 0.6809 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 14894 | 1273 | 0.018 | -0.011–0.046 | 0.2260 | 0.800 | not_testable_yet (under-powered) |
| `place.l4_h8` | 14894 | 1241 | -0.001 | -0.029–0.026 | 0.9310 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 14894 | 1288 | -0.005 | -0.033–0.024 | 0.7560 | 0.805 | classical_rejected (recommended: powered null) |
| `place.l5_h1` | 14894 | 1253 | -0.014 | -0.042–0.014 | 0.3259 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 14894 | 1294 | 0.004 | -0.023–0.031 | 0.7740 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 14894 | 1225 | -0.030 | -0.058–-0.002 | 0.0365 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 14894 | 1177 | 0.003 | -0.027–0.033 | 0.8395 | 0.765 | not_testable_yet (under-powered) |
| `place.l5_h2` | 14894 | 1284 | 0.032 | 0.005–0.058 | 0.0189 | 0.861 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 14894 | 1253 | 0.002 | -0.026–0.029 | 0.9125 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 14894 | 1229 | 0.005 | -0.024–0.034 | 0.7499 | 0.785 | not_testable_yet (under-powered) |
| `place.l5_h5` | 14894 | 1236 | 0.016 | -0.011–0.043 | 0.2526 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 14894 | 1173 | -0.023 | -0.051–0.006 | 0.1219 | 0.824 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 14894 | 1240 | -0.008 | -0.037–0.021 | 0.6006 | 0.789 | not_testable_yet (under-powered) |
| `place.l5_h8` | 14894 | 1310 | 0.003 | -0.024–0.030 | 0.8223 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 14894 | 1220 | 0.011 | -0.018–0.040 | 0.4549 | 0.781 | not_testable_yet (under-powered) |
| `place.l6_h1` | 14894 | 1204 | 0.025 | -0.004–0.055 | 0.0912 | 0.775 | not_testable_yet (under-powered) |
| `place.l6_h10` | 14894 | 1259 | 0.017 | -0.007–0.041 | 0.1578 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 14894 | 1277 | -0.010 | -0.035–0.015 | 0.4281 | 0.942 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 14894 | 1263 | -0.022 | -0.050–0.005 | 0.1116 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 14894 | 1272 | -0.012 | -0.037–0.013 | 0.3467 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 14894 | 1176 | 0.017 | -0.008–0.042 | 0.1861 | 0.918 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 14894 | 1246 | -0.048 | -0.076–-0.020 | 0.0009 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l6_h5` | 14894 | 1242 | -0.013 | -0.041–0.015 | 0.3621 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 14894 | 1188 | 0.004 | -0.026–0.033 | 0.7996 | 0.769 | not_testable_yet (under-powered) |
| `place.l6_h7` | 14894 | 1296 | 0.014 | -0.013–0.041 | 0.3090 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 14894 | 1196 | -0.011 | -0.040–0.019 | 0.4736 | 0.772 | not_testable_yet (under-powered) |
| `place.l6_h9` | 14894 | 1275 | -0.012 | -0.039–0.016 | 0.3953 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 14894 | 1225 | 0.006 | -0.021–0.034 | 0.6533 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 14894 | 1239 | -0.009 | -0.037–0.019 | 0.5238 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 14894 | 1262 | 0.007 | -0.021–0.034 | 0.6355 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 14894 | 1255 | -0.018 | -0.047–0.010 | 0.2107 | 0.794 | not_testable_yet (under-powered) |
| `place.l7_h2` | 14894 | 1191 | 0.051 | 0.023–0.078 | 0.0003 | 0.828 | effect on development data |
| `place.l7_h3` | 14894 | 1322 | -0.005 | -0.032–0.022 | 0.7198 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 14894 | 1245 | 0.013 | -0.016–0.042 | 0.3803 | 0.790 | not_testable_yet (under-powered) |
| `place.l7_h5` | 14894 | 1261 | -0.043 | -0.072–-0.014 | 0.0035 | 0.796 | not_testable_yet (under-powered) |
| `place.l7_h6` | 14894 | 1172 | 0.006 | -0.023–0.034 | 0.7022 | 0.823 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 14894 | 1235 | 0.026 | -0.001–0.053 | 0.0616 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 14894 | 1239 | -0.003 | -0.030–0.025 | 0.8478 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 14894 | 1248 | -0.008 | -0.037–0.021 | 0.6090 | 0.792 | not_testable_yet (under-powered) |
| `place.l8_h1` | 14894 | 1243 | 0.019 | -0.010–0.048 | 0.2095 | 0.790 | not_testable_yet (under-powered) |
| `place.l8_h10` | 14894 | 1218 | -0.010 | -0.035–0.016 | 0.4545 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 14894 | 1303 | 0.005 | -0.019–0.029 | 0.7052 | 0.945 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 14894 | 1172 | -0.001 | -0.030–0.027 | 0.9353 | 0.823 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 14894 | 1199 | 0.004 | -0.021–0.029 | 0.7404 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 14894 | 1262 | 0.021 | -0.003–0.045 | 0.0796 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 14894 | 1289 | 0.004 | -0.024–0.031 | 0.7953 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 14894 | 1284 | 0.021 | -0.006–0.048 | 0.1236 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 14894 | 1261 | -0.017 | -0.046–0.011 | 0.2383 | 0.796 | not_testable_yet (under-powered) |
| `place.l8_h7` | 14894 | 1193 | -0.008 | -0.036–0.020 | 0.5752 | 0.831 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 14894 | 1258 | 0.020 | -0.008–0.049 | 0.1655 | 0.795 | not_testable_yet (under-powered) |
| `place.l8_h9` | 14894 | 1212 | -0.026 | -0.054–0.003 | 0.0758 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 14894 | 1200 | 0.005 | -0.023–0.033 | 0.7336 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 14894 | 1333 | -0.010 | -0.037–0.017 | 0.4551 | 0.877 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 14894 | 1223 | -0.009 | -0.036–0.019 | 0.5447 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 14894 | 1258 | 0.002 | -0.024–0.029 | 0.8751 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 14894 | 1233 | -0.017 | -0.045–0.011 | 0.2306 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 14894 | 1215 | -0.021 | -0.049–0.007 | 0.1441 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 14894 | 1182 | -0.001 | -0.031–0.028 | 0.9325 | 0.767 | not_testable_yet (under-powered) |
| `place.l9_h5` | 14894 | 1299 | 0.013 | -0.015–0.041 | 0.3713 | 0.809 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 14894 | 1260 | -0.010 | -0.038–0.017 | 0.4584 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 14894 | 1265 | 0.006 | -0.023–0.035 | 0.6938 | 0.797 | not_testable_yet (under-powered) |
| `place.l9_h8` | 14894 | 1245 | -0.000 | -0.028–0.027 | 0.9909 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 14894 | 1181 | 0.012 | -0.016–0.039 | 0.4102 | 0.836 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 14894 | 1247 | 0.004 | -0.025–0.033 | 0.7624 | 0.791 | not_testable_yet (under-powered) |
| `place.mars_h10` | 14894 | 1275 | -0.020 | -0.049–0.008 | 0.1671 | 0.802 | classical_rejected (recommended: powered null) |
| `place.mars_h11` | 14894 | 1158 | 0.013 | -0.017–0.043 | 0.3928 | 0.758 | not_testable_yet (under-powered) |
| `place.mars_h12` | 14894 | 1207 | -0.026 | -0.053–-0.000 | 0.0500 | 0.842 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 14894 | 1221 | 0.028 | -0.001–0.057 | 0.0602 | 0.782 | not_testable_yet (under-powered) |
| `place.mars_h3` | 14894 | 1227 | -0.005 | -0.034–0.024 | 0.7315 | 0.785 | not_testable_yet (under-powered) |
| `place.mars_h4` | 14894 | 1271 | 0.007 | -0.020–0.033 | 0.6192 | 0.865 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 14894 | 1287 | -0.016 | -0.042–0.010 | 0.2338 | 0.865 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 14894 | 1202 | -0.018 | -0.048–0.011 | 0.2301 | 0.775 | not_testable_yet (under-powered) |
| `place.mars_h7` | 14894 | 1266 | 0.010 | -0.017–0.036 | 0.4798 | 0.863 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 14894 | 1280 | -0.008 | -0.037–0.020 | 0.5698 | 0.803 | classical_rejected (recommended: powered null) |
| `place.mars_h9` | 14894 | 1253 | -0.029 | -0.055–-0.003 | 0.0291 | 0.856 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 14894 | 892 | 0.025 | -0.009–0.058 | 0.1546 | 0.627 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 14894 | 1061 | 0.020 | -0.011–0.052 | 0.1987 | 0.716 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 14894 | 1463 | -0.029 | -0.056–-0.002 | 0.0371 | 0.858 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 14894 | 949 | 0.025 | -0.008–0.058 | 0.1376 | 0.659 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 14894 | 1407 | 0.021 | -0.006–0.049 | 0.1276 | 0.842 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 14894 | 1593 | 0.009 | -0.017–0.035 | 0.4933 | 0.886 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 14894 | 1400 | -0.021 | -0.048–0.007 | 0.1404 | 0.841 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 14894 | 1075 | -0.011 | -0.042–0.020 | 0.4812 | 0.722 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 14894 | 1102 | 0.003 | -0.028–0.034 | 0.8553 | 0.734 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 14894 | 1090 | 0.011 | -0.020–0.042 | 0.4835 | 0.729 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 14894 | 1369 | -0.019 | -0.046–0.009 | 0.1879 | 0.832 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 14894 | 1493 | -0.014 | -0.040–0.013 | 0.3163 | 0.865 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 14894 | 1191 | 0.019 | -0.011–0.048 | 0.2112 | 0.770 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 14894 | 1239 | -0.018 | -0.048–0.011 | 0.2135 | 0.789 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 14894 | 1267 | 0.029 | 0.000–0.058 | 0.0479 | 0.799 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 14894 | 1233 | -0.016 | -0.042–0.010 | 0.2353 | 0.851 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 14894 | 1217 | 0.013 | -0.016–0.042 | 0.3876 | 0.781 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 14894 | 1283 | -0.003 | -0.032–0.025 | 0.8277 | 0.805 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 14894 | 1238 | 0.003 | -0.023–0.030 | 0.8152 | 0.855 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 14894 | 1255 | 0.001 | -0.026–0.028 | 0.9408 | 0.857 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 14894 | 1261 | -0.003 | -0.031–0.026 | 0.8584 | 0.796 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 14894 | 1211 | 0.004 | -0.023–0.031 | 0.7686 | 0.846 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 14894 | 1267 | 0.001 | -0.028–0.030 | 0.9574 | 0.798 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 14894 | 1232 | 0.010 | -0.017–0.037 | 0.4686 | 0.852 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 14894 | 1272 | -0.014 | -0.043–0.015 | 0.3471 | 0.801 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 14894 | 1098 | 0.048 | 0.018–0.079 | 0.0020 | 0.732 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 14894 | 1172 | -0.017 | -0.047–0.013 | 0.2653 | 0.764 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 14894 | 1286 | -0.001 | -0.030–0.027 | 0.9406 | 0.806 | classical_rejected (recommended: powered null) |
| `place.mercury_in_gemini` | 14894 | 1114 | 0.033 | 0.002–0.063 | 0.0350 | 0.739 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 14894 | 1302 | -0.023 | -0.052–0.005 | 0.1099 | 0.811 | classical_rejected (recommended: powered null) |
| `place.mercury_in_libra` | 14894 | 1393 | -0.031 | -0.058–-0.003 | 0.0296 | 0.839 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 14894 | 1224 | -0.014 | -0.044–0.015 | 0.3336 | 0.784 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 14894 | 1307 | 0.001 | -0.028–0.029 | 0.9603 | 0.812 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 14894 | 1387 | -0.019 | -0.047–0.008 | 0.1666 | 0.837 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 14894 | 1095 | 0.006 | -0.024–0.037 | 0.6814 | 0.731 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 14894 | 1244 | 0.046 | 0.017–0.075 | 0.0018 | 0.791 | not_testable_yet (under-powered) |
| `place.moon_h1` | 14894 | 1246 | 0.007 | -0.022–0.036 | 0.6519 | 0.791 | not_testable_yet (under-powered) |
| `place.moon_h10` | 14894 | 1312 | 0.015 | -0.013–0.044 | 0.2898 | 0.814 | classical_rejected (recommended: powered null) |
| `place.moon_h11` | 14894 | 1256 | -0.005 | -0.034–0.024 | 0.7341 | 0.795 | not_testable_yet (under-powered) |
| `place.moon_h12` | 14894 | 1191 | -0.008 | -0.035–0.019 | 0.5754 | 0.838 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 14894 | 1277 | 0.018 | -0.010–0.047 | 0.2098 | 0.802 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 14894 | 1208 | -0.023 | -0.053–0.006 | 0.1196 | 0.778 | not_testable_yet (under-powered) |
| `place.moon_h4` | 14894 | 1256 | -0.008 | -0.034–0.019 | 0.5702 | 0.860 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 14894 | 1270 | 0.014 | -0.012–0.041 | 0.2930 | 0.862 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 14894 | 1222 | -0.009 | -0.038–0.020 | 0.5447 | 0.782 | not_testable_yet (under-powered) |
| `place.moon_h7` | 14894 | 1195 | -0.019 | -0.045–0.008 | 0.1652 | 0.840 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 14894 | 1188 | 0.017 | -0.013–0.046 | 0.2705 | 0.769 | not_testable_yet (under-powered) |
| `place.moon_h9` | 14894 | 1273 | -0.017 | -0.043–0.009 | 0.1933 | 0.862 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 14894 | 1248 | 0.014 | -0.015–0.043 | 0.3558 | 0.792 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 14894 | 1221 | 0.006 | -0.024–0.035 | 0.7042 | 0.783 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 14894 | 1233 | -0.032 | -0.061–-0.003 | 0.0329 | 0.787 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 14894 | 1264 | 0.014 | -0.012–0.041 | 0.2908 | 0.862 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 14894 | 1252 | 0.012 | -0.017–0.041 | 0.4311 | 0.794 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 14894 | 1201 | -0.007 | -0.036–0.023 | 0.6601 | 0.775 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 14894 | 1180 | -0.007 | -0.034–0.020 | 0.6342 | 0.836 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 14894 | 1244 | -0.005 | -0.031–0.022 | 0.7206 | 0.854 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 14894 | 1257 | 0.003 | -0.025–0.032 | 0.8131 | 0.795 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 14894 | 1275 | 0.042 | 0.015–0.069 | 0.0021 | 0.867 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 14894 | 1254 | -0.000 | -0.029–0.029 | 0.9783 | 0.794 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 14894 | 1265 | 0.003 | -0.024–0.029 | 0.8304 | 0.861 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 14894 | 1167 | 0.007 | -0.021–0.035 | 0.6334 | 0.824 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 14894 | 1166 | -0.013 | -0.042–0.016 | 0.3717 | 0.825 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 14894 | 1500 | 0.012 | -0.013–0.037 | 0.3482 | 0.913 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 14894 | 1059 | 0.006 | -0.024–0.035 | 0.6958 | 0.780 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 14894 | 1273 | 0.000 | -0.027–0.027 | 0.9859 | 0.860 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 14894 | 1594 | -0.011 | -0.035–0.014 | 0.4048 | 0.931 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 14894 | 1133 | 0.018 | -0.010–0.046 | 0.2129 | 0.811 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 14894 | 1141 | -0.034 | -0.063–-0.005 | 0.0235 | 0.817 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 14894 | 1172 | 0.017 | -0.011–0.045 | 0.2403 | 0.825 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 14894 | 1122 | 0.006 | -0.023–0.035 | 0.6867 | 0.807 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 14894 | 1146 | -0.006 | -0.035–0.022 | 0.6626 | 0.817 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 14894 | 1421 | -0.001 | -0.027–0.025 | 0.9262 | 0.898 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 14894 | 1243 | -0.037 | -0.066–-0.008 | 0.0130 | 0.790 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 14894 | 1234 | 0.011 | -0.018–0.040 | 0.4523 | 0.787 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 14894 | 1264 | 0.012 | -0.017–0.041 | 0.4062 | 0.798 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 14894 | 1211 | 0.006 | -0.021–0.033 | 0.6696 | 0.845 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 14894 | 1252 | -0.003 | -0.032–0.026 | 0.8275 | 0.794 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 14894 | 1284 | -0.011 | -0.040–0.017 | 0.4394 | 0.805 | classical_rejected (recommended: powered null) |
| `place.saturn_h4` | 14894 | 1229 | 0.000 | -0.026–0.027 | 0.9851 | 0.852 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 14894 | 1280 | -0.025 | -0.051–0.001 | 0.0559 | 0.863 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 14894 | 1213 | -0.018 | -0.047–0.012 | 0.2413 | 0.779 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 14894 | 1244 | 0.016 | -0.011–0.043 | 0.2331 | 0.857 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 14894 | 1230 | 0.019 | -0.010–0.048 | 0.1941 | 0.785 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 14894 | 1210 | 0.002 | -0.025–0.029 | 0.9036 | 0.845 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 14894 | 1203 | 0.023 | -0.001–0.048 | 0.0627 | 0.924 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 14894 | 1554 | -0.048 | -0.072–-0.025 | 0.0001 | 0.977 | effect on development data |
| `place.saturn_in_cancer` | 14894 | 1096 | -0.013 | -0.039–0.014 | 0.3476 | 0.899 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 14894 | 1347 | 0.022 | -0.001–0.045 | 0.0625 | 0.951 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 14894 | 1058 | 0.001 | -0.026–0.028 | 0.9429 | 0.886 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 14894 | 1132 | -0.028 | -0.055–-0.001 | 0.0392 | 0.911 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 14894 | 1256 | 0.057 | 0.034–0.080 | 0.0000 | 0.933 | effect on development data |
| `place.saturn_in_pisces` | 14894 | 1181 | 0.002 | -0.023–0.027 | 0.8661 | 0.921 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 14894 | 1253 | 0.001 | -0.023–0.026 | 0.9128 | 0.936 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 14894 | 1355 | -0.026 | -0.051–-0.002 | 0.0375 | 0.955 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 14894 | 1217 | 0.018 | -0.007–0.042 | 0.1519 | 0.928 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 14894 | 1242 | -0.001 | -0.026–0.024 | 0.9419 | 0.934 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 14894 | 1190 | 0.011 | -0.018–0.041 | 0.4615 | 0.770 | not_testable_yet (under-powered) |
| `place.sun_h10` | 14894 | 1251 | -0.003 | -0.032–0.026 | 0.8514 | 0.794 | not_testable_yet (under-powered) |
| `place.sun_h11` | 14894 | 1296 | -0.013 | -0.042–0.015 | 0.3690 | 0.809 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 14894 | 1206 | -0.007 | -0.034–0.020 | 0.6004 | 0.843 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 14894 | 1269 | 0.019 | -0.009–0.048 | 0.1852 | 0.800 | not_testable_yet (under-powered) |
| `place.sun_h3` | 14894 | 1250 | 0.001 | -0.028–0.030 | 0.9365 | 0.793 | not_testable_yet (under-powered) |
| `place.sun_h4` | 14894 | 1249 | -0.004 | -0.030–0.022 | 0.7622 | 0.858 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 14894 | 1266 | 0.018 | -0.009–0.045 | 0.1882 | 0.861 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 14894 | 1199 | -0.016 | -0.045–0.014 | 0.2942 | 0.774 | not_testable_yet (under-powered) |
| `place.sun_h7` | 14894 | 1235 | 0.000 | -0.026–0.027 | 0.9823 | 0.853 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 14894 | 1265 | -0.000 | -0.029–0.029 | 0.9967 | 0.798 | not_testable_yet (under-powered) |
| `place.sun_h9` | 14894 | 1218 | 0.013 | -0.014–0.040 | 0.3505 | 0.848 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 14894 | 1239 | -0.023 | -0.052–0.006 | 0.1234 | 0.789 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 14894 | 1214 | 0.033 | 0.004–0.062 | 0.0262 | 0.780 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 14894 | 1293 | -0.015 | -0.044–0.013 | 0.2975 | 0.808 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 14894 | 1247 | -0.003 | -0.032–0.026 | 0.8544 | 0.792 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 14894 | 1218 | 0.022 | -0.007–0.051 | 0.1354 | 0.781 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 14894 | 1296 | 0.006 | -0.022–0.035 | 0.6603 | 0.809 | classical_rejected (recommended: powered null) |
| `place.sun_in_libra` | 14894 | 1194 | -0.029 | -0.058–0.001 | 0.0558 | 0.773 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 14894 | 1224 | 0.004 | -0.025–0.033 | 0.7745 | 0.784 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 14894 | 1179 | -0.019 | -0.049–0.010 | 0.2041 | 0.767 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 14894 | 1219 | 0.002 | -0.027–0.031 | 0.8866 | 0.782 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 14894 | 1309 | 0.002 | -0.026–0.031 | 0.8700 | 0.813 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 14894 | 1262 | 0.017 | -0.011–0.046 | 0.2350 | 0.797 | not_testable_yet (under-powered) |
| `place.venus_h1` | 14894 | 1240 | 0.017 | -0.012–0.046 | 0.2425 | 0.789 | not_testable_yet (under-powered) |
| `place.venus_h10` | 14894 | 1220 | -0.014 | -0.044–0.015 | 0.3349 | 0.782 | not_testable_yet (under-powered) |
| `place.venus_h11` | 14894 | 1238 | -0.004 | -0.033–0.025 | 0.7918 | 0.789 | not_testable_yet (under-powered) |
| `place.venus_h12` | 14894 | 1236 | -0.008 | -0.034–0.019 | 0.5594 | 0.852 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 14894 | 1257 | -0.014 | -0.043–0.015 | 0.3373 | 0.796 | not_testable_yet (under-powered) |
| `place.venus_h3` | 14894 | 1230 | -0.001 | -0.030–0.028 | 0.9380 | 0.786 | not_testable_yet (under-powered) |
| `place.venus_h4` | 14894 | 1254 | 0.013 | -0.014–0.040 | 0.3427 | 0.860 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 14894 | 1218 | 0.001 | -0.026–0.028 | 0.9312 | 0.846 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 14894 | 1234 | 0.001 | -0.028–0.030 | 0.9650 | 0.787 | not_testable_yet (under-powered) |
| `place.venus_h7` | 14894 | 1279 | -0.002 | -0.029–0.024 | 0.8580 | 0.866 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 14894 | 1254 | -0.017 | -0.046–0.012 | 0.2507 | 0.794 | not_testable_yet (under-powered) |
| `place.venus_h9` | 14894 | 1234 | 0.005 | -0.022–0.032 | 0.7151 | 0.852 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 14894 | 1059 | -0.009 | -0.038–0.019 | 0.5218 | 0.791 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 14894 | 1148 | -0.005 | -0.033–0.022 | 0.7013 | 0.825 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 14894 | 1157 | 0.006 | -0.021–0.034 | 0.6592 | 0.829 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 14894 | 1494 | -0.002 | -0.027–0.022 | 0.8591 | 0.914 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 14894 | 1408 | 0.003 | -0.022–0.028 | 0.8213 | 0.897 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 14894 | 1472 | 0.005 | -0.020–0.030 | 0.6935 | 0.910 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 14894 | 1403 | 0.029 | 0.004–0.055 | 0.0256 | 0.898 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 14894 | 1341 | 0.046 | 0.020–0.073 | 0.0006 | 0.885 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 14894 | 1046 | -0.024 | -0.052–0.004 | 0.0962 | 0.785 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 14894 | 1131 | -0.036 | -0.063–-0.009 | 0.0086 | 0.817 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 14894 | 1194 | 0.011 | -0.017–0.038 | 0.4489 | 0.841 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 14894 | 1041 | -0.045 | -0.073–-0.018 | 0.0013 | 0.781 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 14894 | 1821 | 0.050 | 0.026–0.074 | 0.0001 | 0.924 | effect on development data |
| `yoga.budhaditya` | 14894 | 7632 | 0.013 | -0.003–0.029 | 0.1247 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 14894 | 4987 | 0.012 | -0.004–0.028 | 0.1526 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 14894 | 1437 | 0.042 | 0.017–0.067 | 0.0011 | 0.897 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 14894 | 2563 | 0.050 | 0.028–0.071 | 0.0000 | 0.980 | effect on development data |
| `yoga.kendra_trikona_raja` | 14894 | 7946 | 0.011 | -0.005–0.027 | 0.1958 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 14894 | 9640 | -0.016 | -0.033–0.000 | 0.0546 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 14894 | 2589 | 0.042 | 0.021–0.063 | 0.0001 | 0.980 | effect on development data |
| `yoga.neecha_bhanga` | 14894 | 6658 | -0.038 | -0.054–-0.021 | 0.0000 | 1.000 | effect on development data |
| `yoga.parivartana` | 14894 | 5554 | -0.008 | -0.024–0.008 | 0.3061 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 14894 | 2128 | 0.018 | -0.005–0.041 | 0.1200 | 0.956 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 14894 | 2653 | 0.053 | 0.032–0.074 | 0.0000 | 0.982 | effect on development data |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
