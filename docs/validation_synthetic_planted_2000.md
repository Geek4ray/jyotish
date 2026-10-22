# Synthetic — Validation — planted, N = 2,000, odds ratio 1.2 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1516 development, 484 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `af07e96238baba17d566b011a79ade78b901761000ad7d86c2b4ff55f9724807` ({"salt_sha256": "d464c926034a806a50f39a5d03cd96b176e8c05deb92429cac7e8c78791070d3", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "9b97ae386b439039191efc7033e4252ff304f65f86b1cfa29086e62e354e4ba1"})
- analysis code `d9e60e44a12abe1e9454e4a09c15c26e2d22e7ba894336c9e8e817bc9809ad94`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1516 | 1.000 | 0.318 | 1.037 | 0.934–1.138 | 0.2098 | 0.2098 | no | 0.281 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1516 | 1.000 | 0.527 | 1.050 | 0.978–1.116 | 0.0659 | 0.1209 | no | 0.218 |
| children | 1516 | 1.000 | 0.314 | 1.155 | 1.038–1.277 | 0.0120 | 0.0604 | no | 0.249 |
| intellect | 1516 | 1.000 | 0.330 | 1.074 | 0.970–1.171 | 0.1099 | 0.1511 | no | 0.263 |
| health | 1516 | 1.000 | 0.502 | 1.069 | 1.013–1.129 | 0.0220 | 0.0604 | no | 0.258 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1516 | 1.000 | 0.313 | 1.114 | 0.997–1.229 | 0.0290 | 0.0637 | no | 0.258 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1516 | 1.000 | 0.307 | 1.054 | 0.954–1.161 | 0.1708 | 0.2088 | no | 0.285 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1516 | 1.000 | 0.536 | 1.111 | 1.041–1.188 | 0.0010 | 0.0110 | yes | 0.217 |
| gains | 1516 | 1.000 | 0.318 | 1.038 | 0.935–1.139 | 0.2048 | 0.2098 | no | 0.272 |
| foreign | 1516 | 1.000 | 0.285 | 1.074 | 0.968–1.179 | 0.1039 | 0.1511 | no | 0.314 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1516 | 1.000 | 0.330 | 1.122 | 1.019–1.229 | 0.0170 | 0.0604 | no | 0.262 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1516 | 1.000 | 8 | 7.05 | 8 | 0.5307 | 0.493 | 0.469 | 0.0978 |
| mother_home | 1516 | 1.000 | 8 | 24.54 | 8 | 0.0019 | 0.495 | 0.502 | 0.6761 |
| children | 1516 | 1.000 | 7 | 31.70 | 7 | 0.0000 | 0.475 | 0.540 | 0.0001 |
| intellect | 1516 | 1.000 | 8 | 16.82 | 8 | 0.0320 | 0.478 | 0.518 | 0.0253 |
| health | 1516 | 1.000 | 8 | 43.59 | 8 | 0.0000 | 0.474 | 0.526 | 0.0000 |
| marriage | 1516 | 1.000 | 8 | 19.44 | 8 | 0.0127 | 0.518 | 0.549 | 0.0563 |
| father | 1516 | 1.000 | 7 | 15.36 | 7 | 0.0316 | 0.484 | 0.525 | 0.0318 |
| career | 1516 | 1.000 | 8 | 18.76 | 8 | 0.0162 | 0.520 | 0.535 | 0.3427 |
| gains | 1516 | 1.000 | 8 | 8.09 | 8 | 0.4247 | 0.493 | 0.493 | 0.9902 |
| foreign | 1516 | 1.000 | 7 | 10.93 | 7 | 0.1417 | 0.527 | 0.531 | 0.6977 |
| reputation | 1516 | 1.000 | 8 | 12.81 | 8 | 0.1186 | 0.478 | 0.516 | 0.0165 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1516 | 1.000 | 72616 | 482 | 0.933 | 1.369 | 0.0249 | 0.316 (-0.096, 0.727) |
| mother_home | 1516 | 1.000 | 62271 | 799 | 0.942 | 1.080 | 0.3433 | 0.078 (-0.232, 0.387) |
| children | 1516 | 1.000 | 73089 | 476 | 0.901 | 1.425 | 0.0149 | 0.356 (0.006, 0.706) |
| intellect | 1516 | 1.000 | 72140 | 501 | 0.942 | 1.666 | 0.0050 | 0.514 (0.042, 0.985) |
| health | 1516 | 1.000 | 64535 | 761 | 0.940 | 1.215 | 0.1095 | 0.197 (-0.131, 0.525) |
| marriage | 1516 | 1.000 | 72636 | 475 | 0.941 | 0.879 | 0.4577 | -0.130 (-0.490, 0.230) |
| father | 1516 | 1.000 | 73016 | 466 | 0.877 | 0.948 | 0.3333 | -0.054 (-0.326, 0.218) |
| career | 1516 | 1.000 | 62512 | 812 | 0.956 | 0.991 | 0.1493 | -0.010 (-0.346, 0.327) |
| gains | 1516 | 1.000 | 72616 | 482 | 0.869 | 1.117 | 0.1343 | 0.112 (-0.166, 0.389) |
| foreign | 1516 | 1.000 | 74347 | 432 | 0.952 | 0.954 | 0.6667 | -0.047 (-0.478, 0.383) |
| reputation | 1516 | 1.000 | 72140 | 501 | 0.890 | 1.282 | 0.0299 | 0.250 (-0.060, 0.561) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1516 | 1.000 | 0.051 | 0.023 | 3 | 3 | not allowed |
| mother_home | 1516 | 1.000 | 0.035 | 0.043 | 4 | 16 | not allowed |
| children | 1516 | 1.000 | 0.047 | 0.044 | 6 | 2 | not allowed |
| intellect | 1516 | 1.000 | 0.047 | 0.046 | 5 | 0 | not allowed |
| health | 1516 | 1.000 | 0.039 | 0.038 | 7 | 1 | not allowed |
| marriage | 1516 | 1.000 | 0.021 | 0.025 | 6 | 1 | not allowed |
| father | 1516 | 1.000 | 0.029 | 0.024 | 6 | 0 | not allowed |
| career | 1516 | 1.000 | 0.034 | 0.041 | 6 | 0 | not allowed |
| gains | 1516 | 1.000 | 0.050 | 0.015 | 2 | 64 | not allowed |
| foreign | 1516 | 1.000 | 0.018 | 0.043 | 6 | 0 | not allowed |
| reputation | 1516 | 1.000 | 0.018 | 0.050 | 4 | 3 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1516 | 1.000 | 549 | 0.281 | 0.512 |
| mother_home | 1516 | 1.000 | 466 | 0.218 | 0.436 |
| children | 1516 | 1.000 | 422 | 0.249 | 0.472 |
| intellect | 1516 | 1.000 | 496 | 0.263 | 0.490 |
| health | 1516 | 1.000 | 654 | 0.258 | 0.487 |
| marriage | 1516 | 1.000 | 450 | 0.258 | 0.483 |
| father | 1516 | 1.000 | 537 | 0.285 | 0.517 |
| career | 1516 | 1.000 | 464 | 0.217 | 0.435 |
| gains | 1516 | 1.000 | 515 | 0.272 | 0.501 |
| foreign | 1516 | 1.000 | 585 | 0.314 | 0.550 |
| reputation | 1516 | 1.000 | 480 | 0.262 | 0.488 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- effect on development data: 1 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 359 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1516 | 132 | -0.052 | -0.141–0.037 | 0.2522 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1516 | 118 | -0.002 | -0.096–0.092 | 0.9689 | 0.061 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1516 | 111 | -0.092 | -0.188–0.004 | 0.0610 | 0.057 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1516 | 124 | 0.050 | -0.036–0.136 | 0.2574 | 0.090 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1516 | 117 | 0.049 | -0.044–0.143 | 0.2987 | 0.061 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1516 | 136 | -0.023 | -0.111–0.065 | 0.6089 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1516 | 116 | -0.064 | -0.148–0.019 | 0.1310 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1516 | 144 | -0.017 | -0.096–0.062 | 0.6722 | 0.094 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1516 | 137 | 0.034 | -0.054–0.122 | 0.4478 | 0.071 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1516 | 131 | 0.016 | -0.068–0.100 | 0.7033 | 0.087 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1516 | 135 | -0.014 | -0.103–0.074 | 0.7499 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1516 | 115 | -0.017 | -0.101–0.068 | 0.6991 | 0.083 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1516 | 120 | 0.013 | -0.073–0.099 | 0.7623 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1516 | 118 | -0.057 | -0.147–0.034 | 0.2198 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1516 | 128 | 0.077 | -0.002–0.156 | 0.0557 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1516 | 139 | -0.091 | -0.176–-0.005 | 0.0370 | 0.078 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1516 | 136 | 0.005 | -0.077–0.087 | 0.9079 | 0.075 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1516 | 135 | 0.051 | -0.028–0.130 | 0.2064 | 0.074 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1516 | 122 | -0.133 | -0.224–-0.041 | 0.0044 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1516 | 120 | -0.059 | -0.149–0.031 | 0.1980 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1516 | 122 | 0.206 | 0.141–0.271 | 0.0000 | 0.066 | effect on development data |
| `place.jupiter_in_scorpio` | 1516 | 138 | 0.082 | 0.006–0.158 | 0.0354 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1516 | 114 | -0.014 | -0.104–0.076 | 0.7637 | 0.062 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1516 | 124 | -0.090 | -0.180–-0.000 | 0.0493 | 0.069 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1516 | 133 | -0.023 | -0.112–0.066 | 0.6156 | 0.069 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1516 | 129 | -0.018 | -0.108–0.072 | 0.6995 | 0.067 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1516 | 124 | 0.005 | -0.086–0.097 | 0.9127 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1516 | 127 | 0.007 | -0.076–0.089 | 0.8687 | 0.091 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1516 | 122 | -0.039 | -0.131–0.054 | 0.4118 | 0.063 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1516 | 104 | 0.003 | -0.096–0.102 | 0.9520 | 0.054 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1516 | 145 | 0.075 | -0.007–0.158 | 0.0745 | 0.096 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1516 | 120 | 0.030 | -0.058–0.118 | 0.5044 | 0.081 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1516 | 134 | -0.043 | -0.132–0.045 | 0.3395 | 0.070 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1516 | 131 | -0.042 | -0.122–0.038 | 0.3033 | 0.086 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1516 | 123 | -0.033 | -0.125–0.059 | 0.4806 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1516 | 124 | 0.059 | -0.028–0.145 | 0.1851 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1516 | 186 | -0.043 | -0.110–0.024 | 0.2068 | 0.127 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1516 | 102 | -0.011 | -0.101–0.079 | 0.8067 | 0.074 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1516 | 121 | -0.031 | -0.113–0.050 | 0.4513 | 0.086 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1516 | 145 | 0.043 | -0.036–0.123 | 0.2874 | 0.104 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1516 | 117 | 0.052 | -0.036–0.141 | 0.2463 | 0.085 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1516 | 103 | 0.048 | -0.045–0.142 | 0.3116 | 0.076 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1516 | 126 | -0.008 | -0.090–0.074 | 0.8510 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1516 | 142 | -0.011 | -0.089–0.066 | 0.7727 | 0.100 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1516 | 140 | -0.046 | -0.121–0.029 | 0.2252 | 0.098 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1516 | 104 | 0.014 | -0.077–0.105 | 0.7617 | 0.076 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1516 | 114 | -0.052 | -0.134–0.030 | 0.2112 | 0.081 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1516 | 116 | 0.074 | -0.016–0.164 | 0.1067 | 0.085 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1516 | 134 | 0.051 | -0.020–0.121 | 0.1611 | 0.085 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1516 | 121 | 0.020 | -0.073–0.112 | 0.6764 | 0.063 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1516 | 103 | -0.148 | -0.246–-0.050 | 0.0032 | 0.054 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1516 | 132 | -0.049 | -0.136–0.037 | 0.2632 | 0.072 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1516 | 115 | 0.051 | -0.043–0.145 | 0.2882 | 0.060 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1516 | 113 | 0.005 | -0.091–0.100 | 0.9258 | 0.059 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1516 | 138 | -0.095 | -0.181–-0.009 | 0.0296 | 0.077 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1516 | 132 | 0.044 | -0.036–0.125 | 0.2827 | 0.073 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1516 | 119 | 0.033 | -0.044–0.109 | 0.4043 | 0.074 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1516 | 141 | 0.023 | -0.057–0.102 | 0.5727 | 0.078 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1516 | 139 | 0.050 | -0.019–0.120 | 0.1549 | 0.089 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1516 | 129 | -0.025 | -0.111–0.061 | 0.5711 | 0.070 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1516 | 141 | 0.015 | -0.058–0.087 | 0.6959 | 0.091 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1516 | 111 | -0.092 | -0.188–0.004 | 0.0610 | 0.057 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1516 | 115 | 0.088 | -0.004–0.181 | 0.0611 | 0.060 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1516 | 117 | -0.111 | -0.204–-0.018 | 0.0199 | 0.064 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1516 | 152 | 0.034 | -0.050–0.117 | 0.4292 | 0.078 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1516 | 118 | -0.002 | -0.096–0.092 | 0.9689 | 0.061 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1516 | 110 | -0.030 | -0.123–0.062 | 0.5228 | 0.060 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1516 | 127 | 0.015 | -0.069–0.099 | 0.7308 | 0.070 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1516 | 136 | 0.021 | -0.052–0.095 | 0.5662 | 0.087 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1516 | 145 | 0.078 | 0.003–0.152 | 0.0410 | 0.080 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1516 | 113 | 0.059 | -0.017–0.134 | 0.1263 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1516 | 131 | -0.002 | -0.087–0.082 | 0.9574 | 0.071 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1516 | 123 | -0.016 | -0.105–0.073 | 0.7289 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1516 | 123 | -0.017 | -0.105–0.071 | 0.7008 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1516 | 113 | -0.022 | -0.113–0.070 | 0.6401 | 0.061 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1516 | 109 | -0.001 | -0.089–0.087 | 0.9893 | 0.079 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1516 | 134 | -0.002 | -0.086–0.081 | 0.9581 | 0.073 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1516 | 132 | -0.016 | -0.101–0.069 | 0.7102 | 0.072 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1516 | 120 | -0.013 | -0.107–0.080 | 0.7790 | 0.063 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1516 | 134 | 0.080 | -0.007–0.168 | 0.0725 | 0.070 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1516 | 126 | -0.041 | -0.130–0.048 | 0.3703 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1516 | 124 | -0.042 | -0.134–0.050 | 0.3678 | 0.064 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1516 | 155 | 0.034 | -0.044–0.112 | 0.3954 | 0.083 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1516 | 123 | -0.009 | -0.092–0.073 | 0.8253 | 0.088 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1516 | 132 | 0.014 | -0.075–0.104 | 0.7513 | 0.069 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1516 | 132 | -0.019 | -0.097–0.059 | 0.6302 | 0.085 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1516 | 111 | -0.003 | -0.086–0.079 | 0.9362 | 0.069 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1516 | 128 | 0.120 | 0.040–0.199 | 0.0031 | 0.068 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1516 | 114 | -0.063 | -0.150–0.024 | 0.1561 | 0.072 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1516 | 107 | 0.027 | -0.054–0.108 | 0.5125 | 0.065 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1516 | 143 | -0.041 | -0.124–0.042 | 0.3331 | 0.078 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1516 | 148 | -0.063 | -0.146–0.020 | 0.1349 | 0.081 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1516 | 120 | -0.011 | -0.104–0.082 | 0.8138 | 0.063 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1516 | 135 | 0.017 | -0.065–0.100 | 0.6779 | 0.073 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1516 | 134 | -0.027 | -0.115–0.062 | 0.5543 | 0.070 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1516 | 112 | 0.003 | -0.090–0.095 | 0.9569 | 0.059 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1516 | 134 | 0.059 | -0.011–0.128 | 0.0989 | 0.085 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1516 | 130 | -0.081 | -0.171–0.009 | 0.0764 | 0.067 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1516 | 125 | 0.044 | -0.047–0.135 | 0.3406 | 0.065 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1516 | 120 | -0.045 | -0.135–0.045 | 0.3299 | 0.065 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1516 | 137 | 0.061 | -0.025–0.148 | 0.1656 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1516 | 135 | -0.003 | -0.091–0.086 | 0.9555 | 0.070 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1516 | 102 | 0.045 | -0.046–0.136 | 0.3293 | 0.055 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1516 | 140 | -0.056 | -0.140–0.028 | 0.1897 | 0.078 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1516 | 116 | 0.017 | -0.062–0.096 | 0.6685 | 0.072 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1516 | 125 | 0.042 | -0.040–0.125 | 0.3173 | 0.069 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1516 | 135 | -0.045 | -0.125–0.034 | 0.2604 | 0.088 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1516 | 117 | 0.000 | -0.088–0.089 | 0.9916 | 0.063 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1516 | 133 | 0.032 | -0.040–0.105 | 0.3832 | 0.084 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1516 | 120 | -0.002 | -0.096–0.091 | 0.9583 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1516 | 127 | -0.052 | -0.143–0.039 | 0.2638 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1516 | 126 | -0.017 | -0.104–0.070 | 0.7040 | 0.068 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1516 | 129 | 0.075 | -0.013–0.164 | 0.0942 | 0.067 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1516 | 110 | 0.040 | -0.056–0.136 | 0.4143 | 0.057 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1516 | 120 | -0.016 | -0.105–0.072 | 0.7151 | 0.065 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1516 | 131 | -0.017 | -0.101–0.068 | 0.6978 | 0.072 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1516 | 128 | 0.015 | -0.061–0.091 | 0.7026 | 0.081 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1516 | 126 | 0.027 | -0.056–0.110 | 0.5216 | 0.069 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1516 | 132 | -0.044 | -0.124–0.036 | 0.2796 | 0.085 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1516 | 134 | -0.002 | -0.086–0.081 | 0.9581 | 0.073 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1516 | 119 | 0.050 | -0.035–0.136 | 0.2503 | 0.064 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1516 | 142 | -0.083 | -0.167–0.002 | 0.0547 | 0.079 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1516 | 119 | 0.035 | -0.050–0.121 | 0.4202 | 0.065 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1516 | 145 | 0.015 | -0.071–0.100 | 0.7364 | 0.075 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1516 | 146 | 0.051 | -0.026–0.128 | 0.1983 | 0.080 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1516 | 109 | -0.014 | -0.106–0.078 | 0.7671 | 0.059 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1516 | 110 | -0.019 | -0.108–0.070 | 0.6702 | 0.073 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1516 | 148 | 0.008 | -0.077–0.092 | 0.8593 | 0.076 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1516 | 117 | -0.094 | -0.187–-0.001 | 0.0469 | 0.063 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1516 | 127 | 0.032 | -0.058–0.122 | 0.4861 | 0.066 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1516 | 122 | -0.031 | -0.120–0.058 | 0.4958 | 0.066 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1516 | 112 | -0.004 | -0.100–0.092 | 0.9306 | 0.059 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1516 | 124 | -0.014 | -0.102–0.073 | 0.7492 | 0.067 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1516 | 144 | 0.001 | -0.079–0.081 | 0.9755 | 0.080 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1516 | 106 | -0.102 | -0.198–-0.005 | 0.0398 | 0.058 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1516 | 117 | 0.022 | -0.073–0.116 | 0.6514 | 0.061 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1516 | 144 | 0.024 | -0.054–0.103 | 0.5457 | 0.080 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1516 | 127 | 0.006 | -0.078–0.091 | 0.8868 | 0.070 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1516 | 131 | 0.034 | -0.055–0.123 | 0.4507 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1516 | 127 | 0.001 | -0.083–0.085 | 0.9803 | 0.084 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1516 | 117 | -0.102 | -0.195–-0.009 | 0.0318 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1516 | 137 | 0.041 | -0.047–0.128 | 0.3620 | 0.071 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1516 | 129 | -0.050 | -0.138–0.038 | 0.2620 | 0.070 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1516 | 113 | 0.013 | -0.083–0.109 | 0.7916 | 0.059 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1516 | 123 | -0.015 | -0.108–0.077 | 0.7429 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1516 | 128 | -0.002 | -0.080–0.075 | 0.9542 | 0.081 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1516 | 105 | -0.059 | -0.149–0.031 | 0.1971 | 0.065 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1516 | 128 | -0.017 | -0.105–0.071 | 0.7048 | 0.068 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1516 | 134 | 0.001 | -0.074–0.077 | 0.9705 | 0.086 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1516 | 125 | -0.009 | -0.088–0.070 | 0.8309 | 0.079 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1516 | 129 | -0.086 | -0.174–0.003 | 0.0587 | 0.070 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1516 | 128 | -0.019 | -0.106–0.067 | 0.6626 | 0.069 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1516 | 122 | 0.167 | 0.079–0.256 | 0.0002 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1516 | 138 | -0.015 | -0.098–0.069 | 0.7287 | 0.075 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1516 | 117 | -0.090 | -0.183–0.003 | 0.0579 | 0.061 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1516 | 139 | -0.024 | -0.109–0.061 | 0.5783 | 0.074 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1516 | 121 | 0.013 | -0.074–0.100 | 0.7664 | 0.065 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1516 | 116 | -0.038 | -0.128–0.053 | 0.4130 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1516 | 121 | -0.040 | -0.129–0.049 | 0.3772 | 0.067 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1516 | 123 | 0.042 | -0.050–0.133 | 0.3726 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1516 | 106 | 0.140 | 0.061–0.218 | 0.0005 | 0.057 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1516 | 134 | -0.035 | -0.120–0.049 | 0.4130 | 0.075 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1516 | 121 | -0.009 | -0.102–0.083 | 0.8421 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1516 | 134 | -0.020 | -0.108–0.069 | 0.6658 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1516 | 121 | -0.005 | -0.093–0.083 | 0.9149 | 0.065 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1516 | 134 | -0.008 | -0.090–0.074 | 0.8467 | 0.089 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1516 | 153 | 0.016 | -0.062–0.094 | 0.6923 | 0.084 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1516 | 132 | -0.041 | -0.130–0.048 | 0.3700 | 0.068 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1516 | 133 | 0.018 | -0.070–0.107 | 0.6845 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1516 | 118 | 0.003 | -0.077–0.083 | 0.9403 | 0.074 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1516 | 125 | -0.052 | -0.135–0.030 | 0.2147 | 0.080 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1516 | 106 | -0.080 | -0.178–0.018 | 0.1079 | 0.056 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1516 | 122 | 0.029 | -0.047–0.105 | 0.4495 | 0.076 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1516 | 129 | 0.059 | -0.012–0.130 | 0.1022 | 0.081 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1516 | 140 | -0.042 | -0.126–0.042 | 0.3268 | 0.076 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1516 | 141 | -0.014 | -0.097–0.069 | 0.7361 | 0.077 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1516 | 114 | -0.031 | -0.126–0.065 | 0.5293 | 0.060 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1516 | 136 | -0.020 | -0.104–0.064 | 0.6355 | 0.074 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1516 | 143 | 0.094 | 0.009–0.179 | 0.0294 | 0.075 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1516 | 109 | 0.012 | -0.081–0.105 | 0.8048 | 0.058 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1516 | 126 | 0.020 | -0.067–0.106 | 0.6526 | 0.067 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1516 | 114 | -0.056 | -0.149–0.036 | 0.2327 | 0.062 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1516 | 109 | -0.065 | -0.160–0.030 | 0.1770 | 0.059 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1516 | 125 | -0.049 | -0.128–0.030 | 0.2216 | 0.088 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1516 | 133 | -0.104 | -0.192–-0.016 | 0.0201 | 0.073 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1516 | 130 | -0.064 | -0.152–0.023 | 0.1515 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1516 | 118 | -0.013 | -0.107–0.080 | 0.7785 | 0.062 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1516 | 144 | 0.060 | -0.025–0.145 | 0.1688 | 0.075 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1516 | 128 | 0.034 | -0.051–0.119 | 0.4304 | 0.068 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1516 | 125 | 0.023 | -0.068–0.115 | 0.6151 | 0.065 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1516 | 142 | -0.046 | -0.131–0.038 | 0.2835 | 0.076 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1516 | 122 | -0.042 | -0.123–0.038 | 0.2982 | 0.087 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1516 | 124 | 0.007 | -0.085–0.098 | 0.8875 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1516 | 134 | -0.031 | -0.120–0.058 | 0.4946 | 0.069 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1516 | 110 | -0.048 | -0.145–0.049 | 0.3299 | 0.057 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1516 | 131 | -0.061 | -0.137–0.015 | 0.1134 | 0.092 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1516 | 120 | 0.016 | -0.077–0.108 | 0.7415 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1516 | 125 | -0.052 | -0.143–0.040 | 0.2660 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1516 | 139 | 0.014 | -0.068–0.096 | 0.7324 | 0.091 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1516 | 135 | -0.019 | -0.100–0.061 | 0.6378 | 0.089 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1516 | 125 | 0.046 | -0.045–0.137 | 0.3249 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1516 | 112 | 0.009 | -0.081–0.099 | 0.8486 | 0.075 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1516 | 130 | -0.002 | -0.092–0.088 | 0.9624 | 0.068 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1516 | 131 | -0.053 | -0.129–0.024 | 0.1760 | 0.092 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1516 | 95 | 0.057 | -0.045–0.160 | 0.2708 | 0.050 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1516 | 107 | 0.107 | 0.013–0.202 | 0.0263 | 0.056 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1516 | 138 | -0.023 | -0.111–0.064 | 0.6024 | 0.071 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1516 | 105 | 0.049 | -0.049–0.147 | 0.3295 | 0.055 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1516 | 130 | 0.037 | -0.052–0.126 | 0.4186 | 0.067 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1516 | 171 | 0.009 | -0.070–0.089 | 0.8184 | 0.088 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1516 | 166 | -0.033 | -0.114–0.047 | 0.4188 | 0.085 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1516 | 123 | 0.036 | -0.055–0.128 | 0.4343 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1516 | 102 | -0.080 | -0.180–0.020 | 0.1164 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1516 | 117 | 0.022 | -0.072–0.115 | 0.6516 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1516 | 127 | -0.043 | -0.134–0.048 | 0.3515 | 0.066 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1516 | 135 | -0.100 | -0.188–-0.012 | 0.0255 | 0.070 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1516 | 118 | 0.044 | -0.050–0.137 | 0.3592 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1516 | 130 | 0.003 | -0.087–0.093 | 0.9458 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1516 | 115 | 0.004 | -0.091–0.099 | 0.9374 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1516 | 121 | -0.022 | -0.104–0.060 | 0.5948 | 0.086 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1516 | 133 | 0.047 | -0.040–0.135 | 0.2898 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1516 | 125 | 0.061 | -0.029–0.152 | 0.1811 | 0.065 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1516 | 119 | -0.017 | -0.103–0.069 | 0.7032 | 0.079 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1516 | 138 | -0.003 | -0.084–0.078 | 0.9493 | 0.091 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1516 | 116 | -0.011 | -0.106–0.083 | 0.8122 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1516 | 141 | 0.014 | -0.067–0.095 | 0.7309 | 0.093 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1516 | 138 | -0.098 | -0.184–-0.012 | 0.0263 | 0.072 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1516 | 122 | -0.051 | -0.131–0.028 | 0.2034 | 0.086 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1516 | 129 | -0.052 | -0.142–0.039 | 0.2616 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1516 | 110 | 0.089 | -0.005–0.183 | 0.0647 | 0.057 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1516 | 110 | 0.089 | -0.005–0.183 | 0.0647 | 0.057 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1516 | 123 | 0.028 | -0.064–0.119 | 0.5546 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1516 | 118 | 0.044 | -0.049–0.137 | 0.3524 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1516 | 129 | -0.009 | -0.099–0.081 | 0.8400 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1516 | 140 | -0.079 | -0.165–0.008 | 0.0756 | 0.072 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1516 | 154 | -0.061 | -0.145–0.022 | 0.1487 | 0.079 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1516 | 133 | -0.035 | -0.124–0.054 | 0.4415 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1516 | 135 | -0.051 | -0.140–0.037 | 0.2550 | 0.070 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1516 | 117 | 0.012 | -0.082–0.106 | 0.7967 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1516 | 118 | 0.081 | -0.011–0.173 | 0.0844 | 0.061 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1516 | 136 | -0.002 | -0.090–0.086 | 0.9614 | 0.071 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1516 | 132 | 0.061 | -0.027–0.148 | 0.1769 | 0.068 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1516 | 108 | 0.011 | -0.086–0.109 | 0.8171 | 0.056 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1516 | 123 | 0.008 | -0.075–0.092 | 0.8442 | 0.088 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1516 | 136 | -0.023 | -0.111–0.065 | 0.6089 | 0.070 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1516 | 115 | -0.034 | -0.129–0.061 | 0.4853 | 0.060 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1516 | 116 | -0.008 | -0.096–0.079 | 0.8541 | 0.077 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1516 | 142 | -0.074 | -0.150–0.001 | 0.0518 | 0.092 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1516 | 121 | 0.074 | -0.018–0.166 | 0.1141 | 0.063 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1516 | 136 | 0.003 | -0.079–0.085 | 0.9402 | 0.090 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1516 | 140 | -0.002 | -0.089–0.085 | 0.9608 | 0.073 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1516 | 111 | 0.004 | -0.084–0.091 | 0.9359 | 0.080 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1516 | 131 | 0.010 | -0.079–0.100 | 0.8205 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1516 | 145 | 0.025 | -0.060–0.110 | 0.5577 | 0.075 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1516 | 120 | -0.066 | -0.159–0.027 | 0.1658 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1516 | 134 | -0.018 | -0.097–0.061 | 0.6562 | 0.095 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1516 | 123 | -0.034 | -0.126–0.058 | 0.4652 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1516 | 124 | 0.040 | -0.051–0.131 | 0.3856 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1516 | 129 | -0.085 | -0.163–-0.007 | 0.0324 | 0.083 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1516 | 124 | -0.078 | -0.158–0.001 | 0.0523 | 0.081 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1516 | 127 | -0.041 | -0.131–0.050 | 0.3773 | 0.066 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1516 | 133 | -0.055 | -0.134–0.024 | 0.1712 | 0.087 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1516 | 122 | 0.060 | -0.032–0.152 | 0.1991 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1516 | 104 | -0.017 | -0.105–0.072 | 0.7082 | 0.076 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1516 | 103 | -0.006 | -0.101–0.088 | 0.8935 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1516 | 126 | -0.008 | -0.095–0.078 | 0.8529 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1516 | 145 | 0.034 | -0.045–0.112 | 0.4049 | 0.079 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1516 | 121 | 0.057 | -0.026–0.141 | 0.1800 | 0.065 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1516 | 140 | -0.026 | -0.109–0.057 | 0.5440 | 0.077 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1516 | 186 | -0.055 | -0.129–0.020 | 0.1490 | 0.105 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1516 | 102 | -0.052 | -0.150–0.045 | 0.2948 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1516 | 116 | -0.040 | -0.131–0.051 | 0.3907 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1516 | 117 | 0.093 | 0.011–0.175 | 0.0262 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1516 | 114 | -0.028 | -0.119–0.063 | 0.5488 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1516 | 104 | -0.044 | -0.140–0.052 | 0.3673 | 0.056 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1516 | 142 | 0.073 | -0.004–0.150 | 0.0632 | 0.077 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1516 | 145 | 0.009 | -0.076–0.095 | 0.8322 | 0.075 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1516 | 114 | -0.086 | -0.181–0.009 | 0.0765 | 0.059 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1516 | 128 | -0.030 | -0.121–0.060 | 0.5107 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1516 | 125 | -0.023 | -0.104–0.058 | 0.5797 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1516 | 127 | 0.008 | -0.082–0.099 | 0.8558 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1516 | 123 | 0.010 | -0.082–0.102 | 0.8327 | 0.064 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1516 | 122 | -0.007 | -0.093–0.079 | 0.8723 | 0.080 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1516 | 151 | -0.010 | -0.088–0.067 | 0.7927 | 0.099 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1516 | 105 | 0.003 | -0.096–0.102 | 0.9529 | 0.055 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1516 | 133 | 0.044 | -0.041–0.129 | 0.3102 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1516 | 126 | -0.080 | -0.170–0.010 | 0.0823 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1516 | 117 | 0.015 | -0.071–0.102 | 0.7269 | 0.085 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1516 | 127 | 0.064 | -0.006–0.135 | 0.0742 | 0.079 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1516 | 149 | -0.076 | -0.154–0.001 | 0.0542 | 0.100 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1516 | 96 | -0.144 | -0.243–-0.045 | 0.0045 | 0.059 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1516 | 128 | 0.023 | -0.052–0.098 | 0.5426 | 0.081 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1516 | 97 | 0.058 | -0.022–0.139 | 0.1561 | 0.058 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1516 | 131 | -0.013 | -0.091–0.065 | 0.7444 | 0.084 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1516 | 142 | 0.024 | -0.048–0.096 | 0.5105 | 0.092 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1516 | 120 | -0.011 | -0.091–0.070 | 0.7940 | 0.075 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1516 | 123 | 0.031 | -0.044–0.107 | 0.4176 | 0.077 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1516 | 142 | -0.023 | -0.098–0.053 | 0.5586 | 0.093 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1516 | 135 | 0.060 | -0.009–0.130 | 0.0884 | 0.085 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1516 | 126 | -0.006 | -0.085–0.072 | 0.8718 | 0.080 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1516 | 107 | 0.013 | -0.085–0.111 | 0.7961 | 0.056 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1516 | 123 | -0.052 | -0.144–0.040 | 0.2683 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1516 | 121 | 0.011 | -0.082–0.103 | 0.8208 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1516 | 125 | -0.066 | -0.143–0.010 | 0.0903 | 0.088 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1516 | 150 | 0.071 | -0.011–0.154 | 0.0906 | 0.077 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1516 | 120 | -0.057 | -0.150–0.036 | 0.2322 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1516 | 120 | -0.010 | -0.097–0.076 | 0.8124 | 0.079 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1516 | 134 | -0.050 | -0.129–0.029 | 0.2172 | 0.088 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1516 | 107 | 0.003 | -0.095–0.101 | 0.9539 | 0.056 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1516 | 141 | 0.006 | -0.074–0.087 | 0.8761 | 0.093 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1516 | 142 | 0.021 | -0.065–0.107 | 0.6314 | 0.074 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1516 | 126 | -0.016 | -0.098–0.065 | 0.6901 | 0.090 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1516 | 125 | -0.008 | -0.100–0.083 | 0.8586 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1516 | 144 | 0.014 | -0.071–0.100 | 0.7420 | 0.074 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1516 | 129 | 0.033 | -0.056–0.123 | 0.4686 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1516 | 135 | -0.035 | -0.123–0.053 | 0.4370 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1516 | 122 | 0.024 | -0.068–0.116 | 0.6140 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1516 | 124 | 0.075 | -0.015–0.165 | 0.1005 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1516 | 125 | -0.052 | -0.143–0.040 | 0.2660 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1516 | 139 | -0.035 | -0.122–0.052 | 0.4281 | 0.072 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1516 | 103 | 0.009 | -0.091–0.108 | 0.8648 | 0.054 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1516 | 115 | -0.043 | -0.138–0.052 | 0.3724 | 0.060 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1516 | 128 | 0.072 | -0.017–0.161 | 0.1118 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1516 | 127 | -0.052 | -0.143–0.039 | 0.2638 | 0.066 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1516 | 131 | 0.052 | -0.037–0.141 | 0.2518 | 0.068 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1516 | 126 | -0.073 | -0.164–0.018 | 0.1135 | 0.065 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1516 | 111 | -0.063 | -0.159–0.034 | 0.2026 | 0.058 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1516 | 113 | -0.059 | -0.140–0.022 | 0.1521 | 0.081 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1516 | 143 | -0.005 | -0.091–0.081 | 0.9167 | 0.074 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1516 | 108 | 0.021 | -0.076–0.119 | 0.6654 | 0.056 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1516 | 127 | 0.023 | -0.063–0.108 | 0.6071 | 0.084 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1516 | 111 | 0.031 | -0.061–0.122 | 0.5123 | 0.075 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1516 | 135 | -0.039 | -0.127–0.049 | 0.3890 | 0.070 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1516 | 141 | 0.038 | -0.045–0.120 | 0.3693 | 0.094 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1516 | 137 | 0.066 | -0.021–0.153 | 0.1376 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1516 | 133 | -0.007 | -0.087–0.072 | 0.8555 | 0.094 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1516 | 106 | -0.022 | -0.112–0.067 | 0.6248 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1516 | 121 | 0.028 | -0.060–0.115 | 0.5357 | 0.081 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1516 | 105 | -0.040 | -0.129–0.049 | 0.3790 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1516 | 179 | 0.031 | -0.043–0.105 | 0.4078 | 0.117 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1516 | 146 | -0.021 | -0.099–0.057 | 0.6007 | 0.096 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1516 | 154 | -0.038 | -0.113–0.037 | 0.3215 | 0.100 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1516 | 133 | 0.027 | -0.057–0.111 | 0.5223 | 0.089 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1516 | 149 | 0.107 | 0.024–0.189 | 0.0115 | 0.100 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1516 | 111 | -0.017 | -0.106–0.071 | 0.7015 | 0.075 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1516 | 105 | -0.009 | -0.101–0.082 | 0.8435 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1516 | 125 | -0.036 | -0.119–0.046 | 0.3878 | 0.083 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1516 | 82 | -0.060 | -0.158–0.037 | 0.2239 | 0.057 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1516 | 177 | 0.040 | -0.038–0.117 | 0.3173 | 0.091 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1516 | 764 | 0.018 | -0.032–0.068 | 0.4845 | 0.268 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1516 | 524 | 0.009 | -0.040–0.059 | 0.7209 | 0.279 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1516 | 134 | 0.031 | -0.051–0.112 | 0.4591 | 0.073 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1516 | 245 | 0.072 | 0.005–0.139 | 0.0362 | 0.125 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1516 | 803 | 0.008 | -0.043–0.058 | 0.7650 | 0.268 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1516 | 991 | -0.023 | -0.075–0.030 | 0.3979 | 0.244 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1516 | 262 | 0.028 | -0.038–0.095 | 0.4004 | 0.134 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1516 | 691 | -0.064 | -0.114–-0.014 | 0.0125 | 0.272 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1516 | 553 | 0.013 | -0.036–0.062 | 0.6025 | 0.287 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1516 | 227 | 0.070 | 0.000–0.139 | 0.0498 | 0.116 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1516 | 280 | 0.022 | -0.043–0.087 | 0.5037 | 0.143 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
