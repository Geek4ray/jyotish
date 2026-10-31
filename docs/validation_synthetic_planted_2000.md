# Synthetic — Validation — planted, N = 2,000, odds ratio 1.2 per SD

Run 2026-10-31 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1479 development, 521 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold. The split assigns by household: 0 households straddle it. The registry is not used for a synthetic cohort.

## Synthetic — Pre-registration hashes (test 10)

- rule set `8f86556c59c29d96491790ac386e9b168b795fbcf31ee835bb93bbe98ab62af0`
- weight set `4b551c99e2a9de896fcbcdf761dc91ea8a976d648b3f9e2226dbc3c0de3301b6`
- (the analysis code is validate.py with jyotish.cohort, jyotish.outcomes and the outcome map; the lift interval resamples households)
- split definition `363323c8d5c450c04ef5324fbb0c4ebe99fc792a770ae6f2439576498354edd9` ({"salt_sha256": "6295df2c9197b43b02a9ebf2563806128934891279163c3d1169f838b2803d4d", "fraction": 0.25, "k": 5, "unit": "household", "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "28ee480aec704498539ab50b840122b853473d54ca81e0798c72f44f2da61e71"})
- analysis code `4e9b3936a8ab40ebcf5679000b7f9a759cde1a881180d1058bdb21269fd7599d`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain). Abstention is by accuracy class (approximate, unknown), the gate's stand-in: the sampler did not run.

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1479 | 1.000 | 0.318 | 1.013 | 0.918–1.112 | 0.3337 | 0.3656 | no | 0.274 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1479 | 1.000 | 0.523 | 1.043 | 0.975–1.120 | 0.1588 | 0.1941 | no | 0.210 |
| children | 1479 | 1.000 | 0.312 | 1.077 | 0.972–1.191 | 0.1019 | 0.1401 | no | 0.239 |
| intellect | 1479 | 1.000 | 0.310 | 1.135 | 1.028–1.246 | 0.0100 | 0.0366 | yes | 0.275 |
| health | 1479 | 1.000 | 0.499 | 1.102 | 1.047–1.159 | 0.0010 | 0.0110 | yes | 0.252 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1479 | 1.000 | 0.315 | 1.087 | 0.968–1.198 | 0.0859 | 0.1350 | no | 0.248 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1479 | 1.000 | 0.302 | 1.101 | 0.989–1.211 | 0.0599 | 0.1319 | no | 0.287 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1479 | 1.000 | 0.515 | 1.118 | 1.041–1.189 | 0.0060 | 0.0330 | yes | 0.213 |
| gains | 1479 | 1.000 | 0.318 | 1.009 | 0.905–1.123 | 0.3656 | 0.3656 | no | 0.262 |
| foreign | 1479 | 1.000 | 0.293 | 1.083 | 0.987–1.185 | 0.0849 | 0.1350 | no | 0.302 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1479 | 1.000 | 0.310 | 1.095 | 0.982–1.214 | 0.0509 | 0.1319 | no | 0.260 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p (two-sided; a fall is marked) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1479 | 1.000 | 8 | 8.18 | 8 | 0.4158 | 0.485 | 0.509 | 0.0779 |
| mother_home | 1479 | 1.000 | 8 | 20.57 | 8 | 0.0084 | 0.486 | 0.515 | 0.0605 |
| children | 1479 | 1.000 | 7 | 22.00 | 7 | 0.0025 | 0.471 | 0.530 | 0.0014 |
| intellect | 1479 | 1.000 | 8 | 30.60 | 8 | 0.0002 | 0.502 | 0.549 | 0.0006 |
| health | 1479 | 1.000 | 8 | 36.83 | 8 | 0.0000 | 0.509 | 0.535 | 0.1150 |
| marriage | 1479 | 1.000 | 8 | 16.65 | 8 | 0.0340 | 0.491 | 0.536 | 0.0052 |
| father | 1479 | 1.000 | 7 | 8.97 | 7 | 0.2548 | 0.497 | 0.503 | 0.6819 |
| career | 1479 | 1.000 | 8 | 14.04 | 8 | 0.0808 | 0.526 | 0.529 | 0.8133 |
| gains | 1479 | 1.000 | 8 | 10.67 | 8 | 0.2211 | 0.485 | 0.509 | 0.0507 |
| foreign | 1479 | 1.000 | 7 | 10.79 | 7 | 0.1483 | 0.484 | 0.494 | 0.5207 |
| reputation | 1479 | 1.000 | 8 | 20.95 | 8 | 0.0073 | 0.502 | 0.515 | 0.4124 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside one of the engine's own windows, the timing join's pieces over the life to 2026-10-31, the best third of the life by joint (so a third of the person-years are active for everyone). Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1479 | 1.000 | 71775 | 470 | 0.286 | 1.718 | 0.0050 | 0.546 (0.361, 0.731) |
| mother_home | 1479 | 1.000 | 61881 | 774 | 0.289 | 1.671 | 0.0050 | 0.522 (0.377, 0.666) |
| children | 1479 | 1.000 | 72031 | 461 | 0.283 | 1.818 | 0.0050 | 0.600 (0.414, 0.786) |
| intellect | 1479 | 1.000 | 71197 | 459 | 0.288 | 2.087 | 0.0050 | 0.743 (0.559, 0.928) |
| health | 1479 | 1.000 | 63585 | 738 | 0.291 | 1.822 | 0.0050 | 0.608 (0.461, 0.755) |
| marriage | 1479 | 1.000 | 71070 | 466 | 0.288 | 1.851 | 0.0050 | 0.621 (0.437, 0.805) |
| father | 1479 | 1.000 | 72019 | 446 | 0.286 | 1.412 | 0.0050 | 0.348 (0.154, 0.541) |
| career | 1479 | 1.000 | 61921 | 762 | 0.289 | 1.783 | 0.0050 | 0.587 (0.442, 0.732) |
| gains | 1479 | 1.000 | 71775 | 470 | 0.285 | 1.491 | 0.0050 | 0.404 (0.216, 0.592) |
| foreign | 1479 | 1.000 | 72613 | 433 | 0.288 | 1.911 | 0.0050 | 0.651 (0.460, 0.842) |
| reputation | 1479 | 1.000 | 71197 | 459 | 0.287 | 1.645 | 0.0050 | 0.501 (0.313, 0.689) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1479 | 1.000 | 0.050 | 0.021 | 3 | 4 | not allowed |
| mother_home | 1479 | 1.000 | 0.045 | 0.024 | 5 | 1 | not allowed |
| children | 1479 | 1.000 | 0.064 | 0.036 | 8 | 0 | not allowed |
| intellect | 1479 | 1.000 | 0.027 | 0.046 | 4 | 3 | not allowed |
| health | 1479 | 1.000 | 0.048 | 0.058 | 7 | 3 | not allowed |
| marriage | 1479 | 1.000 | 0.053 | 0.039 | 6 | 0 | not allowed |
| father | 1479 | 1.000 | 0.031 | 0.026 | 4 | 1 | not allowed |
| career | 1479 | 1.000 | 0.064 | 0.074 | 5 | 1 | not allowed |
| gains | 1479 | 1.000 | 0.026 | 0.025 | 3 | 3 | not allowed |
| foreign | 1479 | 1.000 | 0.018 | 0.025 | 6 | 0 | not allowed |
| reputation | 1479 | 1.000 | 0.036 | 0.057 | 5 | 0 | not allowed |

## Synthetic — School-split (test 8)

Each school's score is the sum of its families' votes (Parashari: house, lord, karaka, varga, panchanga; Jaimini: arudha; KP: kp; Nadi has no Layer 5 family in v1). The school with the highest AUC on the development set is chosen there; its AUC on the sequestered cohort is estimated only when that cohort is scored, so the winner's curse is paid on development data.

| area | n | Parashari AUC (95% CI) | Jaimini | KP | chosen | AUC on sequestered (95% CI) |
| --- | --- | --- | --- | --- | --- | --- |
| wealth | 1479 | 0.515 (0.484–0.545), n 1479 | 0.508 (0.479–0.537), n 1479 | no vote in this area | parashari | 0.552 (0.500–0.604) |
| mother_home | 1479 | 0.543 (0.514–0.571), n 1479 | 0.493 (0.467–0.520), n 1479 | 0.493 (0.465–0.520), n 1479 | parashari | 0.572 (0.524–0.619) |
| children | 1479 | 0.549 (0.519–0.580), n 1479 | 0.495 (0.467–0.523), n 1479 | 0.494 (0.464–0.523), n 1479 | parashari | 0.540 (0.487–0.594) |
| intellect | 1479 | 0.546 (0.515–0.577), n 1479 | 0.508 (0.478–0.537), n 1479 | no vote in this area | parashari | 0.531 (0.481–0.581) |
| health | 1479 | 0.543 (0.515–0.571), n 1479 | no vote in this area | 0.498 (0.471–0.526), n 1479 | parashari | 0.547 (0.499–0.595) |
| marriage | 1479 | 0.530 (0.499–0.561), n 1479 | 0.506 (0.478–0.534), n 1479 | 0.521 (0.491–0.550), n 1479 | parashari | 0.539 (0.486–0.592) |
| father | 1479 | 0.522 (0.491–0.553), n 1479 | 0.503 (0.474–0.532), n 1479 | no vote in this area | parashari | 0.515 (0.464–0.566) |
| career | 1479 | 0.554 (0.526–0.582), n 1479 | 0.507 (0.481–0.533), n 1479 | 0.501 (0.473–0.528), n 1479 | parashari | 0.535 (0.485–0.585) |
| gains | 1479 | 0.503 (0.472–0.533), n 1479 | 0.492 (0.464–0.521), n 1479 | no vote in this area | parashari | 0.526 (0.473–0.579) |
| foreign | 1479 | 0.539 (0.508–0.569), n 1479 | 0.512 (0.482–0.541), n 1479 | no vote in this area | parashari | 0.540 (0.485–0.595) |
| reputation | 1479 | 0.538 (0.508–0.569), n 1479 | 0.509 (0.480–0.538), n 1479 | no vote in this area | parashari | 0.548 (0.497–0.598) |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1479 | 1.000 | 550 | 0.274 | 0.504 |
| mother_home | 1479 | 1.000 | 449 | 0.210 | 0.425 |
| children | 1479 | 1.000 | 414 | 0.239 | 0.459 |
| intellect | 1479 | 1.000 | 497 | 0.275 | 0.504 |
| health | 1479 | 1.000 | 640 | 0.252 | 0.479 |
| marriage | 1479 | 1.000 | 438 | 0.248 | 0.470 |
| father | 1479 | 1.000 | 530 | 0.287 | 0.519 |
| career | 1479 | 1.000 | 460 | 0.213 | 0.429 |
| gains | 1479 | 1.000 | 502 | 0.262 | 0.489 |
| foreign | 1479 | 1.000 | 574 | 0.302 | 0.536 |
| reputation | 1479 | 1.000 | 462 | 0.260 | 0.485 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 360 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1479 | 130 | -0.075 | -0.164–0.014 | 0.1003 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1479 | 118 | -0.007 | -0.101–0.087 | 0.8787 | 0.061 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1479 | 112 | -0.103 | -0.199–-0.008 | 0.0332 | 0.058 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1479 | 126 | 0.001 | -0.082–0.084 | 0.9818 | 0.088 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1479 | 108 | 0.014 | -0.084–0.111 | 0.7859 | 0.056 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1479 | 127 | -0.012 | -0.103–0.079 | 0.7904 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1479 | 123 | -0.054 | -0.136–0.028 | 0.1978 | 0.080 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1479 | 141 | 0.000 | -0.080–0.081 | 0.9923 | 0.093 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1479 | 123 | 0.041 | -0.051–0.133 | 0.3826 | 0.064 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1479 | 132 | -0.005 | -0.088–0.078 | 0.9074 | 0.087 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1479 | 131 | -0.070 | -0.159–0.019 | 0.1227 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1479 | 108 | -0.026 | -0.113–0.061 | 0.5557 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1479 | 121 | 0.031 | -0.054–0.117 | 0.4724 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1479 | 125 | -0.019 | -0.106–0.068 | 0.6715 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1479 | 129 | 0.086 | 0.007–0.166 | 0.0330 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1479 | 135 | -0.104 | -0.192–-0.017 | 0.0188 | 0.074 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1479 | 129 | -0.016 | -0.102–0.071 | 0.7238 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1479 | 122 | 0.034 | -0.051–0.120 | 0.4319 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1479 | 127 | -0.090 | -0.180–-0.001 | 0.0473 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1479 | 107 | -0.042 | -0.137–0.053 | 0.3839 | 0.058 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1479 | 113 | 0.132 | 0.053–0.212 | 0.0011 | 0.060 | not_testable_yet (under-powered) |
| `place.jupiter_in_scorpio` | 1479 | 140 | 0.054 | -0.025–0.133 | 0.1797 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1479 | 111 | 0.021 | -0.069–0.111 | 0.6483 | 0.060 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1479 | 120 | -0.080 | -0.172–0.011 | 0.0857 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1479 | 128 | -0.025 | -0.115–0.066 | 0.5951 | 0.067 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1479 | 123 | -0.021 | -0.113–0.071 | 0.6552 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1479 | 123 | 0.077 | -0.015–0.168 | 0.0995 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1479 | 117 | 0.025 | -0.062–0.113 | 0.5686 | 0.083 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1479 | 120 | -0.053 | -0.146–0.040 | 0.2662 | 0.062 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1479 | 96 | -0.039 | -0.142–0.065 | 0.4647 | 0.050 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1479 | 132 | 0.059 | -0.027–0.145 | 0.1815 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1479 | 126 | -0.028 | -0.111–0.054 | 0.5007 | 0.083 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1479 | 131 | -0.037 | -0.126–0.053 | 0.4231 | 0.068 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1479 | 129 | -0.039 | -0.121–0.042 | 0.3416 | 0.084 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1479 | 119 | -0.049 | -0.142–0.044 | 0.3018 | 0.062 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1479 | 135 | 0.045 | -0.038–0.128 | 0.2925 | 0.095 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1479 | 174 | -0.013 | -0.084–0.059 | 0.7280 | 0.118 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1479 | 89 | -0.025 | -0.120–0.071 | 0.6130 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1479 | 113 | -0.030 | -0.114–0.055 | 0.4955 | 0.079 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1479 | 148 | 0.013 | -0.065–0.091 | 0.7527 | 0.102 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1479 | 110 | 0.057 | -0.035–0.149 | 0.2255 | 0.079 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1479 | 115 | 0.022 | -0.066–0.110 | 0.6248 | 0.081 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1479 | 125 | -0.023 | -0.104–0.059 | 0.5863 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1479 | 152 | -0.055 | -0.128–0.018 | 0.1372 | 0.103 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1479 | 135 | 0.012 | -0.069–0.093 | 0.7716 | 0.094 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1479 | 102 | 0.044 | -0.051–0.138 | 0.3665 | 0.073 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1479 | 112 | 0.012 | -0.077–0.100 | 0.7957 | 0.079 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1479 | 104 | 0.006 | -0.085–0.097 | 0.9022 | 0.074 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1479 | 111 | 0.058 | -0.020–0.135 | 0.1458 | 0.066 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1479 | 127 | 0.048 | -0.042–0.138 | 0.2982 | 0.066 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1479 | 116 | -0.129 | -0.222–-0.036 | 0.0066 | 0.060 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1479 | 122 | 0.005 | -0.083–0.093 | 0.9107 | 0.065 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1479 | 105 | -0.001 | -0.100–0.098 | 0.9843 | 0.055 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1479 | 109 | -0.002 | -0.099–0.096 | 0.9749 | 0.057 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1479 | 135 | -0.060 | -0.146–0.026 | 0.1722 | 0.074 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1479 | 126 | 0.062 | -0.020–0.144 | 0.1379 | 0.068 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1479 | 128 | 0.044 | -0.030–0.119 | 0.2419 | 0.078 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1479 | 131 | -0.002 | -0.087–0.083 | 0.9622 | 0.071 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1479 | 136 | 0.010 | -0.066–0.085 | 0.8002 | 0.085 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1479 | 133 | -0.013 | -0.099–0.072 | 0.7621 | 0.071 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1479 | 125 | 0.021 | -0.056–0.099 | 0.5899 | 0.077 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1479 | 117 | -0.030 | -0.125–0.064 | 0.5273 | 0.061 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1479 | 102 | 0.015 | -0.085–0.116 | 0.7659 | 0.053 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1479 | 115 | -0.093 | -0.187–0.001 | 0.0522 | 0.062 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1479 | 134 | 0.016 | -0.073–0.105 | 0.7219 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1479 | 119 | 0.043 | -0.050–0.136 | 0.3673 | 0.062 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1479 | 118 | 0.017 | -0.071–0.105 | 0.6979 | 0.063 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1479 | 125 | -0.001 | -0.088–0.085 | 0.9741 | 0.068 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1479 | 125 | 0.039 | -0.037–0.115 | 0.3156 | 0.076 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1479 | 151 | 0.070 | -0.006–0.145 | 0.0704 | 0.082 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1479 | 122 | 0.033 | -0.044–0.110 | 0.4033 | 0.074 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1479 | 126 | -0.026 | -0.115–0.062 | 0.5576 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1479 | 120 | 0.013 | -0.076–0.102 | 0.7788 | 0.063 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1479 | 110 | -0.026 | -0.120–0.068 | 0.5905 | 0.059 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1479 | 118 | -0.035 | -0.126–0.056 | 0.4483 | 0.063 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1479 | 107 | -0.003 | -0.093–0.086 | 0.9425 | 0.076 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1479 | 134 | 0.006 | -0.078–0.090 | 0.8862 | 0.072 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1479 | 133 | -0.005 | -0.090–0.080 | 0.9094 | 0.071 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1479 | 104 | 0.020 | -0.080–0.119 | 0.6972 | 0.055 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1479 | 126 | 0.121 | 0.032–0.210 | 0.0077 | 0.066 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1479 | 123 | 0.013 | -0.075–0.101 | 0.7683 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1479 | 130 | -0.035 | -0.125–0.054 | 0.4395 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1479 | 152 | -0.007 | -0.088–0.073 | 0.8567 | 0.081 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1479 | 122 | -0.069 | -0.147–0.010 | 0.0851 | 0.084 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1479 | 129 | 0.022 | -0.068–0.113 | 0.6275 | 0.067 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1479 | 123 | -0.080 | -0.166–0.006 | 0.0667 | 0.076 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1479 | 119 | -0.019 | -0.102–0.064 | 0.6549 | 0.073 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1479 | 126 | 0.135 | 0.056–0.214 | 0.0008 | 0.066 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1479 | 108 | -0.058 | -0.148–0.032 | 0.2034 | 0.065 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1479 | 110 | 0.065 | -0.012–0.142 | 0.0956 | 0.066 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1479 | 136 | -0.004 | -0.088–0.080 | 0.9289 | 0.073 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1479 | 141 | -0.049 | -0.133–0.036 | 0.2600 | 0.076 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1479 | 123 | 0.014 | -0.078–0.107 | 0.7595 | 0.064 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1479 | 129 | -0.020 | -0.106–0.067 | 0.6574 | 0.070 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1479 | 132 | -0.040 | -0.130–0.049 | 0.3735 | 0.069 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1479 | 103 | 0.034 | -0.060–0.128 | 0.4798 | 0.054 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1479 | 126 | 0.049 | -0.025–0.124 | 0.1932 | 0.077 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1479 | 121 | -0.057 | -0.150–0.036 | 0.2277 | 0.063 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1479 | 122 | -0.052 | -0.145–0.040 | 0.2673 | 0.063 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1479 | 120 | -0.047 | -0.137–0.044 | 0.3155 | 0.064 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1479 | 138 | 0.039 | -0.048–0.126 | 0.3787 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1479 | 130 | 0.034 | -0.056–0.124 | 0.4583 | 0.067 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1479 | 93 | 0.074 | -0.020–0.167 | 0.1214 | 0.049 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1479 | 129 | -0.049 | -0.137–0.038 | 0.2674 | 0.070 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1479 | 118 | 0.025 | -0.055–0.104 | 0.5416 | 0.072 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1479 | 122 | 0.078 | -0.004–0.160 | 0.0618 | 0.066 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1479 | 139 | -0.040 | -0.119–0.039 | 0.3193 | 0.088 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1479 | 121 | -0.025 | -0.115–0.065 | 0.5841 | 0.065 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1479 | 124 | 0.037 | -0.039–0.113 | 0.3433 | 0.076 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1479 | 123 | 0.023 | -0.069–0.115 | 0.6197 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1479 | 120 | -0.053 | -0.146–0.040 | 0.2662 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1479 | 116 | -0.042 | -0.135–0.050 | 0.3677 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1479 | 127 | 0.031 | -0.060–0.121 | 0.5063 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1479 | 103 | 0.041 | -0.059–0.141 | 0.4192 | 0.054 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1479 | 109 | 0.008 | -0.083–0.100 | 0.8575 | 0.058 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1479 | 131 | -0.010 | -0.095–0.075 | 0.8236 | 0.071 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1479 | 133 | 0.029 | -0.046–0.103 | 0.4545 | 0.082 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1479 | 132 | 0.051 | -0.031–0.132 | 0.2219 | 0.071 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1479 | 126 | -0.063 | -0.147–0.021 | 0.1387 | 0.078 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1479 | 135 | -0.015 | -0.101–0.070 | 0.7210 | 0.072 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1479 | 105 | 0.020 | -0.073–0.113 | 0.6777 | 0.056 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1479 | 150 | -0.099 | -0.182–-0.016 | 0.0200 | 0.083 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1479 | 118 | 0.036 | -0.051–0.123 | 0.4184 | 0.063 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1479 | 130 | 0.014 | -0.076–0.104 | 0.7634 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1479 | 138 | 0.045 | -0.035–0.126 | 0.2705 | 0.075 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1479 | 114 | 0.024 | -0.065–0.113 | 0.5948 | 0.061 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1479 | 100 | -0.030 | -0.122–0.062 | 0.5268 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1479 | 140 | 0.042 | -0.044–0.128 | 0.3405 | 0.072 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1479 | 117 | -0.111 | -0.205–-0.018 | 0.0198 | 0.063 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1479 | 141 | 0.017 | -0.070–0.103 | 0.7067 | 0.072 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1479 | 115 | -0.053 | -0.146–0.039 | 0.2593 | 0.062 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1479 | 111 | -0.065 | -0.161–0.031 | 0.1864 | 0.058 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1479 | 116 | -0.017 | -0.108–0.074 | 0.7105 | 0.062 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1479 | 126 | -0.007 | -0.094–0.079 | 0.8705 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1479 | 117 | -0.175 | -0.269–-0.081 | 0.0003 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1479 | 120 | -0.009 | -0.103–0.084 | 0.8468 | 0.062 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1479 | 143 | 0.030 | -0.050–0.110 | 0.4629 | 0.078 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1479 | 118 | 0.005 | -0.084–0.093 | 0.9199 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1479 | 125 | 0.055 | -0.035–0.146 | 0.2314 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1479 | 116 | -0.011 | -0.098–0.076 | 0.8076 | 0.078 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1479 | 117 | -0.088 | -0.181–0.005 | 0.0635 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1479 | 131 | 0.066 | -0.023–0.155 | 0.1441 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1479 | 136 | -0.048 | -0.134–0.038 | 0.2735 | 0.073 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1479 | 114 | 0.010 | -0.086–0.105 | 0.8397 | 0.059 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1479 | 122 | -0.035 | -0.127–0.058 | 0.4628 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1479 | 123 | -0.036 | -0.119–0.047 | 0.3948 | 0.076 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1479 | 110 | -0.052 | -0.141–0.036 | 0.2468 | 0.067 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1479 | 119 | 0.028 | -0.061–0.116 | 0.5382 | 0.063 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1479 | 121 | -0.014 | -0.096–0.068 | 0.7359 | 0.074 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1479 | 117 | 0.013 | -0.067–0.094 | 0.7475 | 0.071 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1479 | 123 | -0.106 | -0.197–-0.014 | 0.0232 | 0.067 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1479 | 123 | -0.004 | -0.092–0.084 | 0.9339 | 0.066 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1479 | 121 | 0.168 | 0.079–0.257 | 0.0002 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1479 | 142 | -0.015 | -0.097–0.068 | 0.7255 | 0.077 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1479 | 119 | -0.058 | -0.151–0.035 | 0.2200 | 0.062 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1479 | 139 | -0.061 | -0.147–0.025 | 0.1619 | 0.074 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1479 | 106 | 0.019 | -0.073–0.112 | 0.6808 | 0.057 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1479 | 129 | -0.042 | -0.129–0.045 | 0.3478 | 0.070 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1479 | 122 | -0.065 | -0.155–0.025 | 0.1593 | 0.066 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1479 | 124 | 0.052 | -0.039–0.143 | 0.2603 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1479 | 105 | 0.134 | 0.052–0.216 | 0.0013 | 0.056 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1479 | 125 | -0.002 | -0.089–0.084 | 0.9607 | 0.068 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1479 | 108 | -0.041 | -0.139–0.057 | 0.4094 | 0.056 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1479 | 121 | 0.064 | -0.028–0.156 | 0.1738 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1479 | 127 | -0.008 | -0.095–0.078 | 0.8484 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1479 | 133 | 0.009 | -0.074–0.092 | 0.8314 | 0.088 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1479 | 156 | -0.015 | -0.095–0.064 | 0.7021 | 0.086 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1479 | 123 | -0.067 | -0.159–0.025 | 0.1548 | 0.063 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1479 | 122 | 0.010 | -0.083–0.103 | 0.8318 | 0.064 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1479 | 117 | -0.042 | -0.128–0.043 | 0.3302 | 0.072 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1479 | 118 | -0.040 | -0.125–0.045 | 0.3582 | 0.072 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1479 | 117 | -0.016 | -0.107–0.076 | 0.7385 | 0.062 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1479 | 104 | 0.064 | -0.015–0.143 | 0.1149 | 0.061 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1479 | 117 | 0.078 | 0.005–0.152 | 0.0365 | 0.070 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1479 | 147 | -0.028 | -0.110–0.054 | 0.5031 | 0.080 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1479 | 136 | -0.016 | -0.100–0.069 | 0.7188 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1479 | 114 | -0.084 | -0.179–0.010 | 0.0797 | 0.060 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1479 | 135 | -0.002 | -0.086–0.082 | 0.9590 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1479 | 140 | 0.017 | -0.070–0.104 | 0.7035 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1479 | 112 | 0.015 | -0.077–0.106 | 0.7550 | 0.059 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1479 | 113 | 0.028 | -0.063–0.118 | 0.5519 | 0.059 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1479 | 124 | -0.059 | -0.149–0.031 | 0.1963 | 0.066 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1479 | 111 | -0.090 | -0.186–0.005 | 0.0639 | 0.059 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1479 | 116 | -0.074 | -0.154–0.005 | 0.0670 | 0.080 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1479 | 125 | -0.082 | -0.172–0.008 | 0.0747 | 0.067 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1479 | 126 | -0.044 | -0.133–0.045 | 0.3345 | 0.068 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1479 | 103 | -0.037 | -0.137–0.063 | 0.4641 | 0.054 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1479 | 138 | 0.095 | 0.008–0.181 | 0.0315 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1479 | 128 | 0.062 | -0.021–0.146 | 0.1440 | 0.067 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1479 | 138 | 0.005 | -0.083–0.092 | 0.9152 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1479 | 128 | -0.083 | -0.173–0.007 | 0.0698 | 0.068 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1479 | 129 | -0.057 | -0.135–0.020 | 0.1470 | 0.089 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1479 | 116 | -0.018 | -0.112–0.077 | 0.7156 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1479 | 133 | 0.012 | -0.077–0.101 | 0.7881 | 0.069 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1479 | 118 | -0.099 | -0.192–-0.006 | 0.0362 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1479 | 117 | -0.002 | -0.088–0.083 | 0.9571 | 0.082 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1479 | 122 | 0.046 | -0.046–0.138 | 0.3279 | 0.063 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1479 | 124 | -0.017 | -0.109–0.075 | 0.7233 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1479 | 118 | 0.014 | -0.075–0.102 | 0.7591 | 0.078 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1479 | 132 | -0.018 | -0.100–0.064 | 0.6687 | 0.087 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1479 | 125 | 0.023 | -0.069–0.114 | 0.6231 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1479 | 111 | 0.029 | -0.062–0.121 | 0.5283 | 0.075 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1479 | 130 | -0.075 | -0.164–0.014 | 0.1003 | 0.067 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1479 | 133 | -0.057 | -0.134–0.019 | 0.1427 | 0.091 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1479 | 87 | 0.039 | -0.069–0.147 | 0.4804 | 0.046 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1479 | 101 | 0.127 | 0.030–0.225 | 0.0107 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1479 | 144 | -0.048 | -0.133–0.038 | 0.2768 | 0.074 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1479 | 98 | 0.060 | -0.041–0.162 | 0.2448 | 0.052 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1479 | 124 | 0.054 | -0.037–0.145 | 0.2477 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1479 | 167 | -0.061 | -0.141–0.019 | 0.1363 | 0.086 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1479 | 152 | -0.046 | -0.130–0.038 | 0.2790 | 0.078 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1479 | 120 | 0.047 | -0.046–0.140 | 0.3213 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1479 | 94 | -0.028 | -0.132–0.077 | 0.6044 | 0.050 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1479 | 113 | 0.017 | -0.079–0.113 | 0.7269 | 0.059 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1479 | 141 | -0.029 | -0.115–0.058 | 0.5185 | 0.073 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1479 | 138 | -0.049 | -0.136–0.039 | 0.2747 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1479 | 114 | 0.058 | -0.037–0.153 | 0.2307 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1479 | 131 | -0.013 | -0.102–0.077 | 0.7846 | 0.068 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1479 | 116 | -0.054 | -0.148–0.041 | 0.2637 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1479 | 113 | -0.010 | -0.097–0.076 | 0.8142 | 0.080 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1479 | 125 | 0.014 | -0.078–0.105 | 0.7647 | 0.065 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1479 | 122 | 0.091 | -0.000–0.182 | 0.0509 | 0.063 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1479 | 108 | 0.007 | -0.085–0.098 | 0.8846 | 0.072 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1479 | 132 | -0.010 | -0.092–0.073 | 0.8205 | 0.087 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1479 | 112 | -0.009 | -0.105–0.088 | 0.8617 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1479 | 145 | -0.013 | -0.092–0.066 | 0.7487 | 0.094 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1479 | 145 | -0.125 | -0.209–-0.041 | 0.0034 | 0.075 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1479 | 116 | -0.046 | -0.129–0.036 | 0.2699 | 0.081 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1479 | 115 | 0.017 | -0.078–0.111 | 0.7334 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1479 | 109 | 0.028 | -0.069–0.125 | 0.5704 | 0.057 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1479 | 108 | 0.073 | -0.023–0.170 | 0.1363 | 0.056 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1479 | 124 | 0.001 | -0.091–0.093 | 0.9830 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1479 | 108 | 0.034 | -0.064–0.131 | 0.5005 | 0.056 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1479 | 120 | -0.017 | -0.110–0.077 | 0.7281 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1479 | 144 | -0.040 | -0.126–0.046 | 0.3621 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1479 | 140 | -0.096 | -0.182–-0.009 | 0.0296 | 0.072 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1479 | 128 | 0.018 | -0.073–0.108 | 0.7037 | 0.066 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1479 | 148 | -0.039 | -0.124–0.045 | 0.3624 | 0.076 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1479 | 114 | 0.012 | -0.083–0.107 | 0.8048 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1479 | 121 | 0.051 | -0.041–0.143 | 0.2795 | 0.063 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1479 | 126 | 0.010 | -0.081–0.101 | 0.8336 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1479 | 130 | 0.009 | -0.081–0.099 | 0.8509 | 0.067 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1479 | 107 | 0.029 | -0.069–0.127 | 0.5629 | 0.056 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1479 | 118 | 0.023 | -0.065–0.110 | 0.6112 | 0.083 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1479 | 128 | -0.068 | -0.158–0.022 | 0.1399 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1479 | 109 | -0.011 | -0.109–0.086 | 0.8177 | 0.057 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1479 | 120 | 0.026 | -0.062–0.114 | 0.5643 | 0.080 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1479 | 141 | -0.007 | -0.087–0.073 | 0.8552 | 0.093 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1479 | 127 | 0.074 | -0.016–0.165 | 0.1063 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1479 | 129 | -0.005 | -0.089–0.078 | 0.8978 | 0.085 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1479 | 127 | 0.014 | -0.077–0.105 | 0.7623 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1479 | 117 | -0.021 | -0.105–0.063 | 0.6268 | 0.082 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1479 | 129 | 0.039 | -0.051–0.129 | 0.3923 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1479 | 132 | 0.008 | -0.081–0.098 | 0.8563 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1479 | 126 | -0.095 | -0.185–-0.004 | 0.0401 | 0.065 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1479 | 131 | -0.011 | -0.092–0.070 | 0.7836 | 0.091 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1479 | 119 | -0.021 | -0.115–0.073 | 0.6587 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1479 | 135 | 0.069 | -0.019–0.156 | 0.1230 | 0.070 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1479 | 123 | -0.089 | -0.169–-0.010 | 0.0266 | 0.080 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1479 | 123 | -0.083 | -0.162–-0.004 | 0.0399 | 0.081 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1479 | 117 | -0.013 | -0.107–0.082 | 0.7901 | 0.061 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1479 | 128 | -0.028 | -0.111–0.054 | 0.4979 | 0.084 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1479 | 120 | 0.028 | -0.065–0.122 | 0.5517 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1479 | 96 | -0.057 | -0.146–0.032 | 0.2089 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1479 | 115 | -0.008 | -0.099–0.083 | 0.8586 | 0.061 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1479 | 125 | -0.056 | -0.145–0.034 | 0.2216 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1479 | 148 | 0.050 | -0.029–0.128 | 0.2132 | 0.079 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1479 | 113 | 0.042 | -0.047–0.131 | 0.3502 | 0.060 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1479 | 135 | 0.001 | -0.083–0.085 | 0.9850 | 0.072 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1479 | 174 | -0.034 | -0.111–0.042 | 0.3774 | 0.095 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1479 | 89 | -0.011 | -0.114–0.091 | 0.8287 | 0.047 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1479 | 104 | -0.080 | -0.178–0.018 | 0.1112 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1479 | 110 | 0.122 | 0.038–0.205 | 0.0043 | 0.058 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1479 | 112 | 0.020 | -0.071–0.111 | 0.6649 | 0.059 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1479 | 102 | -0.004 | -0.100–0.092 | 0.9292 | 0.054 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1479 | 152 | -0.029 | -0.110–0.052 | 0.4818 | 0.082 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1479 | 126 | -0.016 | -0.107–0.075 | 0.7271 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1479 | 117 | -0.030 | -0.125–0.064 | 0.5273 | 0.061 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1479 | 136 | -0.106 | -0.193–-0.019 | 0.0173 | 0.070 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1479 | 125 | 0.012 | -0.072–0.096 | 0.7751 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1479 | 119 | -0.021 | -0.115–0.073 | 0.6587 | 0.062 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1479 | 116 | 0.002 | -0.093–0.097 | 0.9637 | 0.060 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1479 | 111 | 0.007 | -0.083–0.098 | 0.8783 | 0.074 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1479 | 131 | -0.015 | -0.097–0.067 | 0.7142 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1479 | 125 | -0.029 | -0.121–0.062 | 0.5277 | 0.065 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1479 | 130 | 0.043 | -0.043–0.128 | 0.3317 | 0.086 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1479 | 121 | -0.057 | -0.150–0.035 | 0.2238 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1479 | 122 | -0.033 | -0.115–0.049 | 0.4259 | 0.085 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1479 | 125 | 0.056 | -0.018–0.130 | 0.1354 | 0.076 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1479 | 150 | -0.032 | -0.107–0.044 | 0.4107 | 0.096 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1479 | 91 | -0.154 | -0.256–-0.051 | 0.0035 | 0.054 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1479 | 131 | -0.009 | -0.087–0.070 | 0.8262 | 0.081 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1479 | 100 | 0.045 | -0.039–0.128 | 0.2934 | 0.059 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1479 | 123 | -0.018 | -0.100–0.063 | 0.6605 | 0.076 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1479 | 141 | 0.066 | -0.003–0.135 | 0.0596 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1479 | 105 | -0.057 | -0.148–0.034 | 0.2168 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1479 | 139 | -0.016 | -0.093–0.061 | 0.6805 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1479 | 130 | 0.031 | -0.044–0.106 | 0.4166 | 0.080 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1479 | 117 | 0.041 | -0.037–0.119 | 0.3005 | 0.071 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1479 | 127 | 0.008 | -0.070–0.086 | 0.8387 | 0.078 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1479 | 99 | 0.017 | -0.085–0.119 | 0.7390 | 0.052 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1479 | 124 | -0.078 | -0.170–0.013 | 0.0935 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1479 | 108 | -0.036 | -0.134–0.061 | 0.4662 | 0.056 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1479 | 128 | -0.030 | -0.110–0.051 | 0.4683 | 0.089 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1479 | 138 | 0.079 | -0.007–0.166 | 0.0727 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1479 | 114 | -0.026 | -0.122–0.070 | 0.5939 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1479 | 117 | -0.020 | -0.107–0.066 | 0.6469 | 0.077 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1479 | 127 | -0.039 | -0.121–0.042 | 0.3425 | 0.084 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1479 | 109 | 0.046 | -0.052–0.143 | 0.3573 | 0.057 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1479 | 150 | 0.028 | -0.052–0.108 | 0.4957 | 0.098 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1479 | 134 | -0.015 | -0.104–0.073 | 0.7355 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1479 | 131 | -0.028 | -0.108–0.052 | 0.4893 | 0.091 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1479 | 114 | -0.007 | -0.103–0.089 | 0.8861 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1479 | 142 | -0.009 | -0.096–0.077 | 0.8377 | 0.073 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1479 | 115 | 0.035 | -0.059–0.130 | 0.4645 | 0.060 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1479 | 126 | -0.008 | -0.099–0.083 | 0.8644 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1479 | 114 | 0.041 | -0.055–0.136 | 0.4031 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1479 | 122 | 0.037 | -0.055–0.129 | 0.4313 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1479 | 109 | -0.061 | -0.158–0.036 | 0.2188 | 0.057 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1479 | 126 | -0.060 | -0.151–0.031 | 0.1962 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1479 | 103 | 0.051 | -0.048–0.151 | 0.3099 | 0.054 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1479 | 137 | -0.013 | -0.101–0.075 | 0.7763 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1479 | 128 | 0.035 | -0.056–0.125 | 0.4517 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1479 | 143 | -0.028 | -0.115–0.058 | 0.5177 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1479 | 111 | 0.074 | -0.022–0.170 | 0.1297 | 0.058 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1479 | 119 | -0.103 | -0.196–-0.011 | 0.0286 | 0.062 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1479 | 107 | -0.102 | -0.199–-0.005 | 0.0396 | 0.056 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1479 | 112 | -0.066 | -0.147–0.016 | 0.1163 | 0.078 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1479 | 134 | -0.000 | -0.089–0.088 | 0.9944 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1479 | 110 | 0.052 | -0.044–0.149 | 0.2874 | 0.057 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1479 | 122 | -0.007 | -0.093–0.079 | 0.8753 | 0.080 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1479 | 106 | 0.071 | -0.025–0.166 | 0.1464 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1479 | 134 | 0.009 | -0.079–0.098 | 0.8369 | 0.070 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1479 | 150 | -0.017 | -0.094–0.061 | 0.6712 | 0.097 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1479 | 143 | 0.051 | -0.034–0.137 | 0.2405 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1479 | 131 | -0.053 | -0.131–0.024 | 0.1786 | 0.090 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1479 | 90 | 0.043 | -0.059–0.145 | 0.4069 | 0.062 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1479 | 128 | 0.057 | -0.030–0.144 | 0.1991 | 0.085 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1479 | 110 | -0.036 | -0.124–0.052 | 0.4215 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1479 | 168 | 0.081 | 0.003–0.159 | 0.0411 | 0.111 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1479 | 132 | -0.038 | -0.119–0.042 | 0.3529 | 0.086 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1479 | 152 | -0.065 | -0.139–0.009 | 0.0835 | 0.097 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1479 | 139 | 0.041 | -0.042–0.125 | 0.3303 | 0.092 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1479 | 137 | 0.063 | -0.022–0.148 | 0.1445 | 0.091 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1479 | 101 | -0.019 | -0.112–0.073 | 0.6813 | 0.068 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1479 | 108 | -0.030 | -0.119–0.059 | 0.5044 | 0.072 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1479 | 130 | -0.042 | -0.123–0.039 | 0.3105 | 0.085 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1479 | 84 | -0.107 | -0.198–-0.016 | 0.0215 | 0.057 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1479 | 172 | 0.049 | -0.030–0.128 | 0.2282 | 0.088 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1479 | 739 | 0.020 | -0.031–0.071 | 0.4500 | 0.258 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1479 | 501 | -0.020 | -0.071–0.031 | 0.4434 | 0.266 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1479 | 140 | 0.003 | -0.080–0.085 | 0.9506 | 0.076 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1479 | 234 | 0.048 | -0.022–0.117 | 0.1763 | 0.119 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1479 | 780 | 0.000 | -0.051–0.051 | 0.9889 | 0.258 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1479 | 976 | -0.012 | -0.065–0.042 | 0.6725 | 0.229 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1479 | 264 | -0.010 | -0.076–0.057 | 0.7766 | 0.134 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1479 | 667 | -0.048 | -0.099–0.003 | 0.0648 | 0.258 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1479 | 546 | 0.008 | -0.042–0.057 | 0.7682 | 0.275 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1479 | 211 | 0.068 | -0.004–0.140 | 0.0651 | 0.108 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1479 | 281 | 0.032 | -0.033–0.097 | 0.3368 | 0.142 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
