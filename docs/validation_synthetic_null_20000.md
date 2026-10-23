# Synthetic — Validation — null, N = 20,000, odds ratio 1.0 per SD

Run 2026-10-23 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 15108 development, 4892 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold. The split assigns by household: 0 households straddle it. The registry is not used for a synthetic cohort.

## Synthetic — Pre-registration hashes (test 10)

- rule set `8f86556c59c29d96491790ac386e9b168b795fbcf31ee835bb93bbe98ab62af0`
- weight set `4b551c99e2a9de896fcbcdf761dc91ea8a976d648b3f9e2226dbc3c0de3301b6`
- (the analysis code is validate.py with jyotish.cohort, jyotish.outcomes and the outcome map; the lift interval resamples households)
- split definition `29c9182471b5d70c4129d587b87466f9d06f1a8f3c2c4cae1f3cdd627be3dd5c` ({"salt_sha256": "b40112f146d454146b91259ad7adc209cdce21e41cabb6406ccc8d9a7c66e9c2", "fraction": 0.25, "k": 5, "unit": "household", "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "46729ae50bb89c048c0a84fb61d10e03d48d8e856a083fbd508eef9306983a42"})
- analysis code `6518b038ea6548fc1b8d38d49210bd49953b24ea2b0966177acf6fb260748dee`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain). Abstention is by accuracy class (approximate, unknown), the gate's stand-in: the sampler did not run.

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 15108 | 1.000 | 0.299 | 1.003 | 0.972–1.033 | 0.4456 | 0.8535 | no | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 15108 | 1.000 | 0.506 | 1.008 | 0.984–1.033 | 0.2418 | 0.8535 | no | 0.999 |
| children | 15108 | 1.000 | 0.307 | 0.976 | 0.937–1.016 | 0.8661 | 0.8721 | no | 0.999 |
| intellect | 15108 | 1.000 | 0.299 | 0.984 | 0.949–1.019 | 0.7702 | 0.8721 | no | 1.000 |
| health | 15108 | 1.000 | 0.508 | 1.008 | 0.991–1.027 | 0.1798 | 0.8535 | no | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 15108 | 1.000 | 0.299 | 0.994 | 0.955–1.034 | 0.6264 | 0.8613 | no | 0.999 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 15108 | 1.000 | 0.299 | 0.981 | 0.951–1.013 | 0.8721 | 0.8721 | no | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 15108 | 1.000 | 0.507 | 1.004 | 0.980–1.027 | 0.3706 | 0.8535 | no | 0.999 |
| gains | 15108 | 1.000 | 0.299 | 0.997 | 0.965–1.029 | 0.5514 | 0.8613 | no | 1.000 |
| foreign | 15108 | 1.000 | 0.302 | 1.002 | 0.972–1.033 | 0.4655 | 0.8535 | no | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 15108 | 1.000 | 0.299 | 1.011 | 0.976–1.048 | 0.2438 | 0.8535 | no | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p (two-sided; a fall is marked) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15108 | 1.000 | 8 | 8.81 | 8 | 0.3589 | 0.502 | 0.501 | 0.7977 (AUC fell) |
| mother_home | 15108 | 1.000 | 8 | 14.72 | 8 | 0.0648 | 0.492 | 0.506 | 0.0033 |
| children | 15108 | 1.000 | 7 | 1.63 | 7 | 0.9774 | 0.493 | 0.492 | 0.8127 (AUC fell) |
| intellect | 15108 | 1.000 | 8 | 18.39 | 8 | 0.0185 | 0.499 | 0.512 | 0.0140 |
| health | 15108 | 1.000 | 8 | 5.69 | 8 | 0.6817 | 0.493 | 0.493 | 0.8653 (AUC fell) |
| marriage | 15108 | 1.000 | 8 | 11.49 | 8 | 0.1757 | 0.493 | 0.500 | 0.0967 |
| father | 15108 | 1.000 | 7 | 7.92 | 7 | 0.3395 | 0.500 | 0.507 | 0.0624 |
| career | 15108 | 1.000 | 8 | 5.61 | 8 | 0.6905 | 0.490 | 0.498 | 0.0915 |
| gains | 15108 | 1.000 | 8 | 8.60 | 8 | 0.3775 | 0.502 | 0.503 | 0.7981 |
| foreign | 15108 | 1.000 | 7 | 2.86 | 7 | 0.8973 | 0.494 | 0.495 | 0.8232 |
| reputation | 15108 | 1.000 | 8 | 17.44 | 8 | 0.0259 | 0.499 | 0.503 | 0.4229 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside one of the engine's own windows, the timing join's pieces over the life to 2026-10-23, the best third of the life by joint (so a third of the person-years are active for everyone). Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15108 | 1.000 | 735477 | 4522 | 0.285 | 1.030 | 0.6269 | 0.030 (-0.035, 0.094) |
| mother_home | 15108 | 1.000 | 634107 | 7652 | 0.287 | 0.980 | 0.9801 | -0.020 (-0.070, 0.030) |
| children | 15108 | 1.000 | 731937 | 4642 | 0.282 | 1.035 | 0.5771 | 0.035 (-0.029, 0.099) |
| intellect | 15108 | 1.000 | 734563 | 4516 | 0.287 | 1.039 | 0.6667 | 0.038 (-0.026, 0.102) |
| health | 15108 | 1.000 | 636303 | 7676 | 0.290 | 1.037 | 0.4328 | 0.037 (-0.012, 0.086) |
| marriage | 15108 | 1.000 | 735052 | 4512 | 0.286 | 0.974 | 0.9900 | -0.027 (-0.092, 0.038) |
| father | 15108 | 1.000 | 734180 | 4522 | 0.286 | 0.988 | 0.9701 | -0.012 (-0.077, 0.053) |
| career | 15108 | 1.000 | 633685 | 7666 | 0.289 | 1.026 | 0.7114 | 0.026 (-0.024, 0.075) |
| gains | 15108 | 1.000 | 735477 | 4522 | 0.284 | 1.079 | 0.0945 | 0.076 (0.013, 0.140) |
| foreign | 15108 | 1.000 | 734176 | 4570 | 0.287 | 0.978 | 0.9950 | -0.023 (-0.087, 0.042) |
| reputation | 15108 | 1.000 | 734563 | 4516 | 0.287 | 1.075 | 0.2736 | 0.072 (0.009, 0.136) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15108 | 1.000 | 0.002 | 0.012 | 4 | 0 | not allowed |
| mother_home | 15108 | 1.000 | 0.004 | 0.001 | 3 | 0 | not allowed |
| children | 15108 | 1.000 | 0.016 | 0.012 | 3 | 6 | not allowed |
| intellect | 15108 | 1.000 | 0.009 | 0.003 | 3 | 0 | not allowed |
| health | 15108 | 1.000 | 0.015 | 0.006 | 4 | 1 | not allowed |
| marriage | 15108 | 1.000 | 0.009 | 0.010 | 5 | 0 | not allowed |
| father | 15108 | 1.000 | 0.011 | 0.003 | 4 | 1 | not allowed |
| career | 15108 | 1.000 | 0.011 | 0.010 | 4 | 1 | not allowed |
| gains | 15108 | 1.000 | 0.003 | 0.010 | 4 | 1 | not allowed |
| foreign | 15108 | 1.000 | 0.013 | 0.004 | 4 | 1 | not allowed |
| reputation | 15108 | 1.000 | 0.005 | 0.007 | 4 | 1 | not allowed |

## Synthetic — School-split (test 8)

Each school's score is the sum of its families' votes (Parashari: house, lord, karaka, varga, panchanga; Jaimini: arudha; KP: kp; Nadi has no Layer 5 family in v1). The school with the highest AUC on the development set is chosen there; its AUC on the sequestered cohort is estimated only when that cohort is scored, so the winner's curse is paid on development data.

| area | n | Parashari AUC (95% CI) | Jaimini | KP | chosen | AUC on sequestered (95% CI) |
| --- | --- | --- | --- | --- | --- | --- |
| wealth | 15108 | 0.500 (0.490–0.510), n 15108 | 0.496 (0.487–0.505), n 15108 | no vote in this area | parashari | 0.495 (0.478–0.512) |
| mother_home | 15108 | 0.502 (0.493–0.511), n 15108 | 0.501 (0.493–0.509), n 15108 | 0.502 (0.494–0.511), n 15108 | kp | 0.503 (0.487–0.518) |
| children | 15108 | 0.496 (0.487–0.506), n 15108 | 0.505 (0.496–0.514), n 15108 | 0.491 (0.482–0.501), n 15108 | jaimini | 0.499 (0.483–0.515) |
| intellect | 15108 | 0.500 (0.491–0.510), n 15108 | 0.503 (0.493–0.512), n 15108 | no vote in this area | jaimini | 0.500 (0.484–0.516) |
| health | 15108 | 0.508 (0.499–0.517), n 15108 | no vote in this area | 0.499 (0.491–0.508), n 15108 | parashari | 0.496 (0.481–0.512) |
| marriage | 15108 | 0.502 (0.492–0.511), n 15108 | 0.496 (0.487–0.505), n 15108 | 0.499 (0.490–0.509), n 15108 | parashari | 0.510 (0.493–0.527) |
| father | 15108 | 0.497 (0.487–0.506), n 15108 | 0.499 (0.490–0.508), n 15108 | no vote in this area | jaimini | 0.510 (0.494–0.525) |
| career | 15108 | 0.501 (0.492–0.510), n 15108 | 0.502 (0.494–0.511), n 15108 | 0.496 (0.488–0.505), n 15108 | jaimini | 0.504 (0.489–0.518) |
| gains | 15108 | 0.499 (0.489–0.509), n 15108 | 0.498 (0.489–0.507), n 15108 | no vote in this area | parashari | 0.504 (0.487–0.521) |
| foreign | 15108 | 0.502 (0.492–0.511), n 15108 | 0.503 (0.494–0.512), n 15108 | no vote in this area | jaimini | 0.490 (0.474–0.506) |
| reputation | 15108 | 0.500 (0.490–0.510), n 15108 | 0.500 (0.491–0.509), n 15108 | no vote in this area | parashari | 0.498 (0.481–0.515) |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 15108 | 1.000 | 5468 | 1.000 | 1.000 |
| mother_home | 15108 | 1.000 | 4465 | 0.999 | 1.000 |
| children | 15108 | 1.000 | 4084 | 0.999 | 1.000 |
| intellect | 15108 | 1.000 | 4792 | 1.000 | 1.000 |
| health | 15108 | 1.000 | 6225 | 1.000 | 1.000 |
| marriage | 15108 | 1.000 | 4123 | 0.999 | 1.000 |
| father | 15108 | 1.000 | 5243 | 1.000 | 1.000 |
| career | 15108 | 1.000 | 4443 | 0.999 | 1.000 |
| gains | 15108 | 1.000 | 5229 | 1.000 | 1.000 |
| foreign | 15108 | 1.000 | 5661 | 1.000 | 1.000 |
| reputation | 15108 | 1.000 | 4619 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 271 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 89 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 15108 | 1245 | 0.004 | -0.025–0.033 | 0.7924 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 15108 | 1287 | 0.022 | -0.006–0.051 | 0.1297 | 0.805 | classical_rejected (recommended: powered null) |
| `place.jupiter_h11` | 15108 | 1302 | -0.007 | -0.036–0.021 | 0.6159 | 0.810 | classical_rejected (recommended: powered null) |
| `place.jupiter_h12` | 15108 | 1264 | 0.024 | -0.003–0.051 | 0.0821 | 0.861 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 15108 | 1269 | -0.009 | -0.037–0.020 | 0.5611 | 0.799 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 15108 | 1279 | 0.009 | -0.019–0.038 | 0.5193 | 0.803 | classical_rejected (recommended: powered null) |
| `place.jupiter_h4` | 15108 | 1242 | 0.028 | 0.001–0.055 | 0.0410 | 0.857 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 15108 | 1227 | -0.026 | -0.052–0.001 | 0.0558 | 0.844 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 15108 | 1263 | -0.010 | -0.039–0.019 | 0.4916 | 0.797 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 15108 | 1262 | -0.010 | -0.036–0.016 | 0.4408 | 0.861 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 15108 | 1214 | 0.006 | -0.024–0.035 | 0.7106 | 0.780 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 15108 | 1254 | -0.016 | -0.042–0.010 | 0.2334 | 0.856 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 15108 | 1170 | 0.010 | -0.018–0.039 | 0.4656 | 0.822 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 15108 | 1329 | -0.004 | -0.031–0.023 | 0.7623 | 0.873 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 15108 | 1347 | -0.017 | -0.044–0.010 | 0.2149 | 0.878 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_capricorn` | 15108 | 1265 | -0.008 | -0.035–0.020 | 0.5786 | 0.855 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_gemini` | 15108 | 1178 | 0.020 | -0.008–0.048 | 0.1534 | 0.824 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_leo` | 15108 | 1323 | 0.008 | -0.018–0.035 | 0.5457 | 0.871 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 15108 | 1381 | 0.005 | -0.022–0.031 | 0.7266 | 0.886 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 15108 | 1107 | -0.026 | -0.055–0.004 | 0.0876 | 0.799 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 15108 | 1235 | 0.021 | -0.006–0.048 | 0.1339 | 0.844 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 15108 | 1254 | -0.023 | -0.051–0.004 | 0.1003 | 0.852 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 15108 | 1179 | 0.003 | -0.025–0.031 | 0.8274 | 0.825 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 15108 | 1340 | 0.010 | -0.017–0.036 | 0.4758 | 0.875 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 15108 | 1312 | -0.011 | -0.040–0.017 | 0.4321 | 0.814 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 15108 | 1186 | -0.022 | -0.051–0.008 | 0.1499 | 0.769 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 15108 | 1243 | 0.016 | -0.013–0.045 | 0.2785 | 0.790 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 15108 | 1263 | -0.012 | -0.038–0.014 | 0.3641 | 0.859 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 15108 | 1256 | -0.006 | -0.035–0.023 | 0.6665 | 0.795 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 15108 | 1241 | -0.010 | -0.039–0.019 | 0.4881 | 0.790 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 15108 | 1288 | -0.004 | -0.030–0.022 | 0.7733 | 0.868 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 15108 | 1274 | 0.006 | -0.021–0.032 | 0.6785 | 0.860 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 15108 | 1287 | 0.011 | -0.017–0.040 | 0.4446 | 0.805 | classical_rejected (recommended: powered null) |
| `place.ketu_h7` | 15108 | 1267 | 0.008 | -0.018–0.035 | 0.5403 | 0.864 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 15108 | 1272 | -0.004 | -0.032–0.025 | 0.8023 | 0.800 | classical_rejected (recommended: powered null) |
| `place.ketu_h9` | 15108 | 1219 | -0.019 | -0.045–0.008 | 0.1709 | 0.845 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 15108 | 1604 | 0.003 | -0.021–0.026 | 0.8270 | 0.931 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 15108 | 1162 | 0.002 | -0.025–0.030 | 0.8678 | 0.828 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 15108 | 1096 | -0.030 | -0.058–-0.003 | 0.0323 | 0.802 | classical_rejected (recommended: powered null) |
| `place.ketu_in_capricorn` | 15108 | 1522 | -0.011 | -0.035–0.013 | 0.3610 | 0.917 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 15108 | 1189 | 0.023 | -0.005–0.051 | 0.1012 | 0.838 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 15108 | 1191 | 0.007 | -0.020–0.034 | 0.6131 | 0.838 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 15108 | 1184 | -0.001 | -0.028–0.026 | 0.9397 | 0.835 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 15108 | 1454 | -0.013 | -0.037–0.012 | 0.3076 | 0.904 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 15108 | 1293 | -0.016 | -0.042–0.010 | 0.2200 | 0.867 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 15108 | 1133 | 0.003 | -0.025–0.031 | 0.8258 | 0.818 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 15108 | 1127 | 0.009 | -0.019–0.037 | 0.5425 | 0.816 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 15108 | 1153 | 0.029 | 0.001–0.058 | 0.0414 | 0.826 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 15108 | 1340 | -0.011 | -0.035–0.013 | 0.3790 | 0.952 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 15108 | 1276 | 0.014 | -0.014–0.043 | 0.3327 | 0.802 | classical_rejected (recommended: powered null) |
| `place.l10_h11` | 15108 | 1247 | -0.012 | -0.041–0.017 | 0.4164 | 0.792 | not_testable_yet (under-powered) |
| `place.l10_h12` | 15108 | 1231 | -0.006 | -0.033–0.022 | 0.6920 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 15108 | 1272 | -0.011 | -0.039–0.018 | 0.4664 | 0.800 | classical_rejected (recommended: powered null) |
| `place.l10_h3` | 15108 | 1222 | -0.013 | -0.043–0.016 | 0.3688 | 0.783 | not_testable_yet (under-powered) |
| `place.l10_h4` | 15108 | 1318 | -0.006 | -0.033–0.021 | 0.6473 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 15108 | 1245 | -0.001 | -0.028–0.027 | 0.9554 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 15108 | 1216 | -0.004 | -0.029–0.022 | 0.7823 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 15108 | 1268 | -0.007 | -0.035–0.020 | 0.6068 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 15108 | 1271 | 0.009 | -0.015–0.033 | 0.4786 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 15108 | 1202 | 0.008 | -0.020–0.036 | 0.5786 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 15108 | 1256 | 0.015 | -0.009–0.039 | 0.2150 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 15108 | 1221 | 0.032 | 0.002–0.061 | 0.0339 | 0.782 | not_testable_yet (under-powered) |
| `place.l11_h11` | 15108 | 1250 | 0.007 | -0.022–0.036 | 0.6477 | 0.793 | not_testable_yet (under-powered) |
| `place.l11_h12` | 15108 | 1273 | -0.013 | -0.040–0.015 | 0.3595 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 15108 | 1265 | -0.007 | -0.036–0.022 | 0.6435 | 0.798 | not_testable_yet (under-powered) |
| `place.l11_h3` | 15108 | 1255 | -0.008 | -0.037–0.021 | 0.6037 | 0.795 | not_testable_yet (under-powered) |
| `place.l11_h4` | 15108 | 1294 | -0.028 | -0.055–-0.000 | 0.0473 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 15108 | 1272 | 0.018 | -0.009–0.044 | 0.2037 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 15108 | 1281 | -0.014 | -0.039–0.011 | 0.2692 | 0.943 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 15108 | 1285 | 0.024 | -0.003–0.051 | 0.0762 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 15108 | 1191 | -0.006 | -0.032–0.019 | 0.6259 | 0.924 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 15108 | 1265 | 0.010 | -0.017–0.037 | 0.4815 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 15108 | 1245 | 0.001 | -0.027–0.028 | 0.9692 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 15108 | 1289 | -0.002 | -0.029–0.025 | 0.8795 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 15108 | 1217 | 0.003 | -0.025–0.030 | 0.8566 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 15108 | 1223 | -0.010 | -0.036–0.017 | 0.4738 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 15108 | 1238 | 0.002 | -0.026–0.029 | 0.8976 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 15108 | 1360 | 0.010 | -0.017–0.036 | 0.4755 | 0.881 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 15108 | 1306 | -0.010 | -0.038–0.019 | 0.5033 | 0.812 | classical_rejected (recommended: powered null) |
| `place.l12_h5` | 15108 | 1236 | -0.001 | -0.030–0.028 | 0.9390 | 0.789 | not_testable_yet (under-powered) |
| `place.l12_h6` | 15108 | 1252 | 0.004 | -0.023–0.032 | 0.7544 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 15108 | 1230 | 0.006 | -0.023–0.035 | 0.6831 | 0.786 | not_testable_yet (under-powered) |
| `place.l12_h8` | 15108 | 1289 | -0.022 | -0.050–0.005 | 0.1107 | 0.864 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 15108 | 1223 | -0.008 | -0.035–0.019 | 0.5589 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 15108 | 1170 | 0.017 | -0.013–0.047 | 0.2582 | 0.763 | not_testable_yet (under-powered) |
| `place.l1_h10` | 15108 | 1249 | -0.016 | -0.041–0.009 | 0.2194 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 15108 | 1278 | 0.012 | -0.012–0.036 | 0.3345 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 15108 | 1290 | -0.015 | -0.043–0.012 | 0.2746 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 15108 | 1307 | -0.007 | -0.031–0.018 | 0.5821 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 15108 | 1217 | 0.007 | -0.018–0.031 | 0.6071 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 15108 | 1310 | 0.007 | -0.019–0.034 | 0.5855 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 15108 | 1229 | -0.004 | -0.032–0.024 | 0.7679 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 15108 | 1268 | 0.007 | -0.022–0.035 | 0.6487 | 0.799 | not_testable_yet (under-powered) |
| `place.l1_h7` | 15108 | 1236 | -0.006 | -0.034–0.022 | 0.6754 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 15108 | 1245 | -0.014 | -0.043–0.015 | 0.3574 | 0.791 | not_testable_yet (under-powered) |
| `place.l1_h9` | 15108 | 1309 | 0.015 | -0.012–0.041 | 0.2806 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 15108 | 1254 | 0.010 | -0.015–0.034 | 0.4360 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 15108 | 1295 | 0.014 | -0.014–0.043 | 0.3256 | 0.808 | classical_rejected (recommended: powered null) |
| `place.l2_h11` | 15108 | 1218 | -0.034 | -0.063–-0.005 | 0.0229 | 0.781 | not_testable_yet (under-powered) |
| `place.l2_h12` | 15108 | 1320 | -0.002 | -0.029–0.024 | 0.8626 | 0.871 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 15108 | 1234 | 0.011 | -0.018–0.040 | 0.4449 | 0.787 | not_testable_yet (under-powered) |
| `place.l2_h3` | 15108 | 1274 | 0.010 | -0.019–0.039 | 0.4984 | 0.801 | classical_rejected (recommended: powered null) |
| `place.l2_h4` | 15108 | 1232 | 0.005 | -0.023–0.032 | 0.7406 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 15108 | 1281 | 0.007 | -0.020–0.034 | 0.6005 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 15108 | 1225 | 0.000 | -0.025–0.025 | 0.9891 | 0.931 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 15108 | 1274 | 0.005 | -0.022–0.032 | 0.7251 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 15108 | 1257 | -0.006 | -0.031–0.019 | 0.6243 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 15108 | 1244 | -0.005 | -0.033–0.022 | 0.7143 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 15108 | 1289 | -0.001 | -0.026–0.023 | 0.9193 | 0.943 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 15108 | 1261 | 0.031 | 0.003–0.060 | 0.0330 | 0.796 | not_testable_yet (under-powered) |
| `place.l3_h11` | 15108 | 1298 | -0.012 | -0.041–0.016 | 0.3958 | 0.809 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 15108 | 1228 | 0.015 | -0.013–0.042 | 0.2924 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 15108 | 1281 | -0.015 | -0.044–0.013 | 0.2931 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l3_h3` | 15108 | 1247 | 0.004 | -0.025–0.033 | 0.8013 | 0.792 | not_testable_yet (under-powered) |
| `place.l3_h4` | 15108 | 1296 | 0.016 | -0.011–0.043 | 0.2503 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 15108 | 1282 | -0.005 | -0.033–0.022 | 0.7051 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 15108 | 1266 | -0.017 | -0.042–0.008 | 0.1773 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 15108 | 1241 | 0.008 | -0.019–0.036 | 0.5625 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 15108 | 1191 | -0.016 | -0.042–0.009 | 0.2128 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 15108 | 1228 | -0.003 | -0.031–0.025 | 0.8329 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 15108 | 1199 | 0.025 | -0.003–0.053 | 0.0755 | 0.831 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 15108 | 1211 | 0.001 | -0.027–0.029 | 0.9526 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 15108 | 1254 | -0.003 | -0.030–0.025 | 0.8530 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 15108 | 1331 | 0.020 | -0.008–0.048 | 0.1565 | 0.820 | classical_rejected (recommended: powered null) |
| `place.l4_h2` | 15108 | 1288 | 0.001 | -0.026–0.028 | 0.9560 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 15108 | 1230 | 0.015 | -0.013–0.042 | 0.2964 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 15108 | 1212 | 0.007 | -0.020–0.034 | 0.5924 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 15108 | 1315 | -0.005 | -0.033–0.024 | 0.7499 | 0.816 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 15108 | 1251 | -0.036 | -0.064–-0.008 | 0.0115 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 15108 | 1289 | 0.001 | -0.027–0.030 | 0.9352 | 0.806 | classical_rejected (recommended: powered null) |
| `place.l4_h8` | 15108 | 1247 | -0.003 | -0.031–0.024 | 0.8132 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 15108 | 1281 | 0.008 | -0.021–0.036 | 0.5892 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l5_h1` | 15108 | 1301 | -0.003 | -0.030–0.024 | 0.8447 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 15108 | 1314 | -0.002 | -0.029–0.025 | 0.8951 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 15108 | 1233 | 0.006 | -0.021–0.034 | 0.6613 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 15108 | 1205 | 0.011 | -0.019–0.040 | 0.4809 | 0.777 | not_testable_yet (under-powered) |
| `place.l5_h2` | 15108 | 1292 | 0.004 | -0.023–0.031 | 0.7465 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 15108 | 1264 | -0.000 | -0.028–0.027 | 0.9820 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 15108 | 1247 | 0.015 | -0.014–0.043 | 0.3250 | 0.792 | not_testable_yet (under-powered) |
| `place.l5_h5` | 15108 | 1212 | -0.012 | -0.039–0.015 | 0.3801 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 15108 | 1228 | 0.005 | -0.022–0.033 | 0.7077 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 15108 | 1249 | -0.006 | -0.035–0.023 | 0.6816 | 0.793 | not_testable_yet (under-powered) |
| `place.l5_h8` | 15108 | 1320 | -0.004 | -0.031–0.023 | 0.7737 | 0.873 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 15108 | 1243 | -0.001 | -0.030–0.028 | 0.9573 | 0.791 | not_testable_yet (under-powered) |
| `place.l6_h1` | 15108 | 1241 | 0.029 | -0.000–0.057 | 0.0538 | 0.789 | not_testable_yet (under-powered) |
| `place.l6_h10` | 15108 | 1274 | 0.005 | -0.019–0.029 | 0.6826 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 15108 | 1308 | -0.010 | -0.034–0.014 | 0.4236 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 15108 | 1290 | 0.007 | -0.020–0.034 | 0.6205 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 15108 | 1270 | -0.016 | -0.040–0.009 | 0.2234 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 15108 | 1177 | 0.004 | -0.021–0.030 | 0.7364 | 0.920 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 15108 | 1230 | 0.018 | -0.009–0.045 | 0.1983 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l6_h5` | 15108 | 1251 | 0.015 | -0.012–0.043 | 0.2634 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 15108 | 1256 | -0.011 | -0.040–0.017 | 0.4386 | 0.795 | not_testable_yet (under-powered) |
| `place.l6_h7` | 15108 | 1293 | -0.011 | -0.038–0.016 | 0.4319 | 0.861 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 15108 | 1204 | -0.016 | -0.045–0.013 | 0.2869 | 0.776 | not_testable_yet (under-powered) |
| `place.l6_h9` | 15108 | 1314 | 0.014 | -0.013–0.040 | 0.3185 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 15108 | 1270 | 0.020 | -0.007–0.047 | 0.1505 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 15108 | 1281 | 0.020 | -0.007–0.047 | 0.1509 | 0.856 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 15108 | 1301 | -0.013 | -0.041–0.014 | 0.3349 | 0.864 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 15108 | 1284 | -0.002 | -0.031–0.026 | 0.8698 | 0.805 | classical_rejected (recommended: powered null) |
| `place.l7_h2` | 15108 | 1195 | 0.007 | -0.021–0.035 | 0.6420 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l7_h3` | 15108 | 1329 | -0.005 | -0.032–0.022 | 0.7077 | 0.871 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 15108 | 1253 | -0.001 | -0.030–0.028 | 0.9352 | 0.794 | not_testable_yet (under-powered) |
| `place.l7_h5` | 15108 | 1259 | 0.011 | -0.018–0.040 | 0.4465 | 0.796 | not_testable_yet (under-powered) |
| `place.l7_h6` | 15108 | 1209 | -0.012 | -0.040–0.016 | 0.4118 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 15108 | 1219 | 0.004 | -0.022–0.031 | 0.7477 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 15108 | 1256 | 0.000 | -0.027–0.028 | 0.9897 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 15108 | 1252 | 0.007 | -0.021–0.036 | 0.6121 | 0.794 | not_testable_yet (under-powered) |
| `place.l8_h1` | 15108 | 1326 | 0.009 | -0.020–0.037 | 0.5538 | 0.818 | classical_rejected (recommended: powered null) |
| `place.l8_h10` | 15108 | 1205 | 0.007 | -0.018–0.032 | 0.5991 | 0.926 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 15108 | 1366 | -0.004 | -0.028–0.020 | 0.7379 | 0.955 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 15108 | 1199 | -0.016 | -0.044–0.013 | 0.2811 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 15108 | 1230 | 0.024 | 0.000–0.048 | 0.0488 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 15108 | 1241 | -0.024 | -0.049–0.002 | 0.0681 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 15108 | 1308 | 0.016 | -0.011–0.043 | 0.2371 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 15108 | 1345 | 0.016 | -0.010–0.042 | 0.2286 | 0.878 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 15108 | 1248 | -0.017 | -0.046–0.012 | 0.2594 | 0.792 | not_testable_yet (under-powered) |
| `place.l8_h7` | 15108 | 1194 | -0.016 | -0.044–0.013 | 0.2766 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 15108 | 1234 | 0.004 | -0.025–0.034 | 0.7648 | 0.787 | not_testable_yet (under-powered) |
| `place.l8_h9` | 15108 | 1212 | 0.000 | -0.028–0.028 | 0.9843 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 15108 | 1244 | -0.002 | -0.029–0.026 | 0.9145 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 15108 | 1293 | 0.006 | -0.021–0.033 | 0.6715 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 15108 | 1234 | -0.013 | -0.040–0.015 | 0.3736 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 15108 | 1310 | 0.006 | -0.020–0.033 | 0.6278 | 0.873 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 15108 | 1245 | 0.007 | -0.021–0.034 | 0.6408 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 15108 | 1230 | 0.003 | -0.025–0.031 | 0.8350 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 15108 | 1204 | -0.015 | -0.044–0.015 | 0.3261 | 0.776 | not_testable_yet (under-powered) |
| `place.l9_h5` | 15108 | 1357 | 0.001 | -0.027–0.029 | 0.9444 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 15108 | 1254 | -0.003 | -0.030–0.025 | 0.8380 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 15108 | 1273 | -0.029 | -0.058–-0.001 | 0.0452 | 0.801 | classical_rejected (recommended: powered null) |
| `place.l9_h8` | 15108 | 1267 | -0.008 | -0.035–0.020 | 0.5861 | 0.856 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 15108 | 1197 | -0.025 | -0.052–0.001 | 0.0599 | 0.838 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 15108 | 1299 | 0.007 | -0.022–0.035 | 0.6418 | 0.809 | classical_rejected (recommended: powered null) |
| `place.mars_h10` | 15108 | 1296 | 0.026 | -0.002–0.055 | 0.0676 | 0.808 | classical_rejected (recommended: powered null) |
| `place.mars_h11` | 15108 | 1211 | 0.019 | -0.010–0.049 | 0.1966 | 0.778 | not_testable_yet (under-powered) |
| `place.mars_h12` | 15108 | 1221 | -0.009 | -0.036–0.017 | 0.4985 | 0.846 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 15108 | 1195 | 0.010 | -0.020–0.039 | 0.5210 | 0.772 | not_testable_yet (under-powered) |
| `place.mars_h3` | 15108 | 1231 | 0.023 | -0.006–0.052 | 0.1162 | 0.786 | not_testable_yet (under-powered) |
| `place.mars_h4` | 15108 | 1315 | -0.019 | -0.044–0.007 | 0.1480 | 0.875 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 15108 | 1282 | 0.001 | -0.025–0.027 | 0.9446 | 0.862 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 15108 | 1189 | -0.009 | -0.039–0.020 | 0.5416 | 0.770 | not_testable_yet (under-powered) |
| `place.mars_h7` | 15108 | 1307 | 0.014 | -0.012–0.040 | 0.2971 | 0.875 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 15108 | 1295 | -0.012 | -0.040–0.017 | 0.4172 | 0.808 | classical_rejected (recommended: powered null) |
| `place.mars_h9` | 15108 | 1267 | -0.013 | -0.039–0.013 | 0.3246 | 0.860 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 15108 | 913 | 0.014 | -0.020–0.047 | 0.4227 | 0.639 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 15108 | 1056 | -0.002 | -0.033–0.029 | 0.9071 | 0.713 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 15108 | 1492 | 0.017 | -0.010–0.044 | 0.2105 | 0.864 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 15108 | 984 | -0.014 | -0.047–0.018 | 0.3806 | 0.678 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 15108 | 1413 | 0.002 | -0.025–0.030 | 0.8657 | 0.844 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 15108 | 1593 | -0.019 | -0.045–0.007 | 0.1479 | 0.886 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 15108 | 1431 | 0.008 | -0.019–0.036 | 0.5449 | 0.849 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 15108 | 1099 | -0.009 | -0.040–0.021 | 0.5456 | 0.733 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 15108 | 1142 | -0.030 | -0.060–0.000 | 0.0526 | 0.751 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 15108 | 1100 | 0.044 | 0.013–0.075 | 0.0048 | 0.733 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 15108 | 1378 | -0.017 | -0.045–0.011 | 0.2305 | 0.834 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 15108 | 1507 | 0.008 | -0.018–0.035 | 0.5383 | 0.867 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 15108 | 1236 | 0.024 | -0.005–0.053 | 0.1081 | 0.788 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 15108 | 1253 | 0.016 | -0.013–0.045 | 0.2822 | 0.794 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 15108 | 1251 | -0.034 | -0.063–-0.005 | 0.0219 | 0.793 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 15108 | 1287 | 0.001 | -0.026–0.027 | 0.9647 | 0.866 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 15108 | 1218 | 0.005 | -0.024–0.035 | 0.7211 | 0.781 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 15108 | 1302 | 0.005 | -0.023–0.034 | 0.7127 | 0.810 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 15108 | 1287 | 0.009 | -0.017–0.036 | 0.4955 | 0.869 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 15108 | 1288 | 0.027 | 0.001–0.054 | 0.0456 | 0.865 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 15108 | 1262 | -0.050 | -0.079–-0.022 | 0.0006 | 0.797 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 15108 | 1229 | -0.006 | -0.033–0.020 | 0.6454 | 0.852 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 15108 | 1274 | -0.006 | -0.035–0.022 | 0.6696 | 0.801 | classical_rejected (recommended: powered null) |
| `place.mercury_h9` | 15108 | 1221 | -0.002 | -0.029–0.025 | 0.8790 | 0.847 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 15108 | 1299 | -0.004 | -0.033–0.024 | 0.7659 | 0.809 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 15108 | 1096 | -0.018 | -0.049–0.013 | 0.2555 | 0.731 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 15108 | 1166 | 0.015 | -0.015–0.045 | 0.3182 | 0.761 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 15108 | 1314 | 0.000 | -0.028–0.029 | 0.9881 | 0.814 | classical_rejected (recommended: powered null) |
| `place.mercury_in_gemini` | 15108 | 1142 | -0.007 | -0.037–0.023 | 0.6458 | 0.751 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 15108 | 1281 | 0.009 | -0.019–0.038 | 0.5202 | 0.803 | classical_rejected (recommended: powered null) |
| `place.mercury_in_libra` | 15108 | 1397 | -0.005 | -0.032–0.023 | 0.7422 | 0.839 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 15108 | 1249 | -0.011 | -0.040–0.018 | 0.4509 | 0.792 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 15108 | 1363 | -0.005 | -0.032–0.023 | 0.7503 | 0.829 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 15108 | 1363 | 0.008 | -0.020–0.035 | 0.5935 | 0.829 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 15108 | 1140 | 0.008 | -0.022–0.038 | 0.5983 | 0.750 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 15108 | 1298 | 0.008 | -0.021–0.036 | 0.5860 | 0.809 | classical_rejected (recommended: powered null) |
| `place.moon_h1` | 15108 | 1263 | 0.005 | -0.024–0.033 | 0.7553 | 0.797 | not_testable_yet (under-powered) |
| `place.moon_h10` | 15108 | 1258 | -0.012 | -0.041–0.016 | 0.3988 | 0.796 | not_testable_yet (under-powered) |
| `place.moon_h11` | 15108 | 1274 | 0.016 | -0.013–0.045 | 0.2768 | 0.801 | classical_rejected (recommended: powered null) |
| `place.moon_h12` | 15108 | 1233 | 0.007 | -0.020–0.034 | 0.6053 | 0.851 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 15108 | 1334 | -0.012 | -0.040–0.016 | 0.3931 | 0.821 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 15108 | 1243 | -0.011 | -0.040–0.018 | 0.4515 | 0.790 | not_testable_yet (under-powered) |
| `place.moon_h4` | 15108 | 1246 | 0.020 | -0.007–0.047 | 0.1424 | 0.858 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 15108 | 1265 | -0.001 | -0.027–0.026 | 0.9656 | 0.857 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 15108 | 1246 | -0.002 | -0.031–0.027 | 0.9029 | 0.791 | not_testable_yet (under-powered) |
| `place.moon_h7` | 15108 | 1211 | 0.007 | -0.020–0.035 | 0.5875 | 0.847 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 15108 | 1231 | -0.023 | -0.053–0.006 | 0.1157 | 0.786 | not_testable_yet (under-powered) |
| `place.moon_h9` | 15108 | 1304 | 0.001 | -0.025–0.027 | 0.9220 | 0.871 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 15108 | 1267 | 0.040 | 0.011–0.069 | 0.0064 | 0.798 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 15108 | 1288 | 0.005 | -0.023–0.034 | 0.7069 | 0.806 | classical_rejected (recommended: powered null) |
| `place.rahu_h11` | 15108 | 1274 | -0.017 | -0.045–0.012 | 0.2548 | 0.801 | classical_rejected (recommended: powered null) |
| `place.rahu_h12` | 15108 | 1287 | 0.001 | -0.026–0.027 | 0.9647 | 0.866 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 15108 | 1272 | 0.031 | 0.002–0.059 | 0.0367 | 0.800 | classical_rejected (recommended: powered null) |
| `place.rahu_h3` | 15108 | 1219 | 0.008 | -0.022–0.037 | 0.6130 | 0.781 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 15108 | 1186 | -0.014 | -0.041–0.013 | 0.3167 | 0.837 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 15108 | 1243 | -0.006 | -0.033–0.021 | 0.6556 | 0.850 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 15108 | 1263 | 0.015 | -0.014–0.044 | 0.3087 | 0.797 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 15108 | 1312 | -0.015 | -0.040–0.011 | 0.2545 | 0.874 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 15108 | 1256 | -0.020 | -0.049–0.009 | 0.1725 | 0.795 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 15108 | 1241 | -0.014 | -0.041–0.012 | 0.2848 | 0.852 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 15108 | 1191 | -0.012 | -0.040–0.016 | 0.4098 | 0.832 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 15108 | 1184 | -0.030 | -0.058–-0.001 | 0.0416 | 0.830 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 15108 | 1522 | -0.000 | -0.026–0.025 | 0.9699 | 0.917 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 15108 | 1096 | -0.008 | -0.038–0.021 | 0.5724 | 0.795 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 15108 | 1293 | -0.005 | -0.032–0.022 | 0.7092 | 0.864 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 15108 | 1604 | -0.007 | -0.032–0.017 | 0.5577 | 0.931 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 15108 | 1162 | 0.004 | -0.025–0.032 | 0.7952 | 0.820 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 15108 | 1153 | 0.027 | -0.001–0.055 | 0.0572 | 0.815 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 15108 | 1189 | 0.008 | -0.019–0.036 | 0.5529 | 0.830 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 15108 | 1127 | 0.002 | -0.027–0.031 | 0.8942 | 0.807 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 15108 | 1133 | 0.019 | -0.009–0.048 | 0.1856 | 0.808 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 15108 | 1454 | 0.005 | -0.020–0.031 | 0.6813 | 0.903 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 15108 | 1290 | 0.014 | -0.014–0.043 | 0.3339 | 0.806 | classical_rejected (recommended: powered null) |
| `place.saturn_h10` | 15108 | 1269 | 0.030 | 0.002–0.059 | 0.0391 | 0.799 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 15108 | 1264 | -0.010 | -0.039–0.019 | 0.5040 | 0.798 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 15108 | 1278 | 0.001 | -0.025–0.028 | 0.9281 | 0.864 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 15108 | 1302 | -0.010 | -0.038–0.019 | 0.4993 | 0.811 | classical_rejected (recommended: powered null) |
| `place.saturn_h3` | 15108 | 1214 | -0.019 | -0.048–0.011 | 0.2087 | 0.780 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 15108 | 1219 | 0.001 | -0.026–0.028 | 0.9408 | 0.849 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 15108 | 1309 | 0.002 | -0.025–0.028 | 0.9101 | 0.869 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 15108 | 1241 | 0.015 | -0.014–0.044 | 0.2999 | 0.789 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 15108 | 1250 | -0.009 | -0.035–0.017 | 0.5026 | 0.858 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 15108 | 1246 | -0.008 | -0.037–0.021 | 0.5919 | 0.791 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 15108 | 1226 | 0.008 | -0.019–0.035 | 0.5554 | 0.849 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 15108 | 1239 | 0.003 | -0.022–0.028 | 0.8046 | 0.933 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 15108 | 1569 | 0.003 | -0.020–0.025 | 0.8249 | 0.976 | classical_rejected (recommended: powered null) |
| `place.saturn_in_cancer` | 15108 | 1091 | -0.017 | -0.043–0.010 | 0.2227 | 0.898 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 15108 | 1360 | -0.006 | -0.030–0.018 | 0.6201 | 0.955 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 15108 | 1103 | 0.022 | -0.003–0.048 | 0.0826 | 0.898 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 15108 | 1147 | -0.002 | -0.028–0.023 | 0.8591 | 0.913 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 15108 | 1228 | -0.000 | -0.025–0.025 | 0.9952 | 0.931 | classical_rejected (recommended: powered null) |
| `place.saturn_in_pisces` | 15108 | 1191 | -0.003 | -0.028–0.023 | 0.8356 | 0.923 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 15108 | 1300 | 0.022 | -0.002–0.046 | 0.0676 | 0.944 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 15108 | 1338 | -0.009 | -0.033–0.015 | 0.4748 | 0.952 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 15108 | 1266 | -0.013 | -0.038–0.012 | 0.3094 | 0.940 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 15108 | 1276 | -0.001 | -0.025–0.024 | 0.9673 | 0.941 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 15108 | 1230 | 0.024 | -0.005–0.053 | 0.1067 | 0.785 | not_testable_yet (under-powered) |
| `place.sun_h10` | 15108 | 1245 | -0.002 | -0.031–0.027 | 0.8717 | 0.791 | not_testable_yet (under-powered) |
| `place.sun_h11` | 15108 | 1338 | -0.007 | -0.035–0.021 | 0.6095 | 0.822 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 15108 | 1241 | -0.013 | -0.039–0.014 | 0.3484 | 0.852 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 15108 | 1263 | 0.000 | -0.029–0.029 | 0.9936 | 0.797 | not_testable_yet (under-powered) |
| `place.sun_h3` | 15108 | 1293 | 0.010 | -0.018–0.039 | 0.4881 | 0.807 | classical_rejected (recommended: powered null) |
| `place.sun_h4` | 15108 | 1300 | -0.021 | -0.047–0.004 | 0.1054 | 0.871 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 15108 | 1263 | 0.028 | 0.001–0.056 | 0.0396 | 0.858 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 15108 | 1230 | -0.008 | -0.037–0.021 | 0.5951 | 0.786 | not_testable_yet (under-powered) |
| `place.sun_h7` | 15108 | 1242 | 0.004 | -0.023–0.030 | 0.7925 | 0.856 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 15108 | 1249 | -0.011 | -0.040–0.018 | 0.4571 | 0.793 | not_testable_yet (under-powered) |
| `place.sun_h9` | 15108 | 1214 | 0.007 | -0.020–0.034 | 0.6142 | 0.845 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 15108 | 1237 | -0.006 | -0.035–0.023 | 0.6922 | 0.788 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 15108 | 1247 | 0.001 | -0.028–0.030 | 0.9408 | 0.792 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 15108 | 1303 | 0.018 | -0.010–0.047 | 0.2051 | 0.811 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 15108 | 1286 | -0.006 | -0.035–0.022 | 0.6605 | 0.805 | classical_rejected (recommended: powered null) |
| `place.sun_in_gemini` | 15108 | 1189 | 0.020 | -0.010–0.049 | 0.1895 | 0.770 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 15108 | 1307 | 0.002 | -0.026–0.031 | 0.8707 | 0.812 | classical_rejected (recommended: powered null) |
| `place.sun_in_libra` | 15108 | 1204 | 0.007 | -0.022–0.037 | 0.6275 | 0.776 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 15108 | 1264 | -0.031 | -0.059–-0.002 | 0.0375 | 0.798 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 15108 | 1187 | 0.012 | -0.018–0.041 | 0.4422 | 0.769 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 15108 | 1228 | -0.012 | -0.041–0.018 | 0.4352 | 0.785 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 15108 | 1343 | -0.014 | -0.042–0.014 | 0.3182 | 0.824 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 15108 | 1313 | 0.010 | -0.018–0.038 | 0.4965 | 0.814 | classical_rejected (recommended: powered null) |
| `place.venus_h1` | 15108 | 1251 | 0.007 | -0.022–0.036 | 0.6199 | 0.793 | not_testable_yet (under-powered) |
| `place.venus_h10` | 15108 | 1228 | 0.004 | -0.025–0.034 | 0.7706 | 0.785 | not_testable_yet (under-powered) |
| `place.venus_h11` | 15108 | 1268 | -0.038 | -0.067–-0.010 | 0.0091 | 0.799 | not_testable_yet (under-powered) |
| `place.venus_h12` | 15108 | 1305 | -0.017 | -0.042–0.009 | 0.2069 | 0.870 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 15108 | 1276 | 0.002 | -0.026–0.031 | 0.8818 | 0.802 | classical_rejected (recommended: powered null) |
| `place.venus_h3` | 15108 | 1229 | -0.017 | -0.047–0.012 | 0.2430 | 0.785 | not_testable_yet (under-powered) |
| `place.venus_h4` | 15108 | 1269 | -0.005 | -0.031–0.021 | 0.7079 | 0.863 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 15108 | 1272 | 0.009 | -0.018–0.035 | 0.5209 | 0.859 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 15108 | 1284 | -0.004 | -0.032–0.025 | 0.7988 | 0.805 | classical_rejected (recommended: powered null) |
| `place.venus_h7` | 15108 | 1251 | -0.005 | -0.031–0.021 | 0.7163 | 0.858 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 15108 | 1217 | 0.001 | -0.029–0.030 | 0.9679 | 0.781 | not_testable_yet (under-powered) |
| `place.venus_h9` | 15108 | 1258 | 0.009 | -0.018–0.036 | 0.5051 | 0.859 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 15108 | 1086 | -0.014 | -0.042–0.014 | 0.3180 | 0.802 | classical_rejected (recommended: powered null) |
| `place.venus_in_aries` | 15108 | 1202 | -0.010 | -0.037–0.017 | 0.4672 | 0.843 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 15108 | 1115 | -0.010 | -0.037–0.018 | 0.4933 | 0.813 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 15108 | 1531 | -0.004 | -0.028–0.020 | 0.7572 | 0.921 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 15108 | 1434 | 0.001 | -0.024–0.025 | 0.9644 | 0.903 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 15108 | 1505 | 0.006 | -0.019–0.030 | 0.6562 | 0.917 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 15108 | 1398 | 0.010 | -0.016–0.035 | 0.4470 | 0.896 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 15108 | 1363 | 0.025 | -0.001–0.051 | 0.0594 | 0.889 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 15108 | 1083 | -0.001 | -0.030–0.027 | 0.9210 | 0.801 | classical_rejected (recommended: powered null) |
| `place.venus_in_scorpio` | 15108 | 1113 | 0.004 | -0.024–0.033 | 0.7550 | 0.813 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 15108 | 1198 | -0.010 | -0.037–0.017 | 0.4745 | 0.842 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 15108 | 1080 | -0.004 | -0.032–0.025 | 0.8064 | 0.800 | classical_rejected (recommended: powered null) |
| `yoga.bhadra` | 15108 | 1883 | 0.004 | -0.020–0.028 | 0.7472 | 0.932 | classical_rejected (recommended: powered null) |
| `yoga.budhaditya` | 15108 | 7775 | 0.006 | -0.010–0.021 | 0.4970 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 15108 | 5086 | 0.002 | -0.014–0.018 | 0.8143 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 15108 | 1436 | 0.012 | -0.014–0.038 | 0.3575 | 0.895 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 15108 | 2584 | -0.009 | -0.031–0.012 | 0.3837 | 0.981 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja` | 15108 | 8024 | 0.003 | -0.013–0.019 | 0.6832 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 15108 | 9846 | 0.005 | -0.011–0.022 | 0.5385 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 15108 | 2622 | -0.001 | -0.022–0.020 | 0.9149 | 0.982 | classical_rejected (recommended: powered null) |
| `yoga.neecha_bhanga` | 15108 | 6746 | 0.009 | -0.007–0.025 | 0.2658 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.parivartana` | 15108 | 5642 | -0.000 | -0.016–0.015 | 0.9760 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 15108 | 2203 | 0.017 | -0.005–0.040 | 0.1377 | 0.962 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 15108 | 2698 | 0.017 | -0.004–0.037 | 0.1157 | 0.984 | classical_rejected (recommended: powered null) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
