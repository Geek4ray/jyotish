# Synthetic — Validation — null, N = 2,000, odds ratio 1.0 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1511 development, 489 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `c12f6504c83a923e5ada579daa0b463d54aa0b48281aefdb0a562090abcff134` ({"salt_sha256": "96b89b76ad9432d76aaef7ce525854bddf799170c387acf6f5b3848c8376787a", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "d7d19a77748071864de11a3c4e070d34277224e28e3476c518384f444b1e7875"})
- analysis code `d9e60e44a12abe1e9454e4a09c15c26e2d22e7ba894336c9e8e817bc9809ad94`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1511 | 1.000 | 0.312 | 0.968 | 0.876–1.057 | 0.7512 | 0.7512 | no | 0.280 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1511 | 1.000 | 0.507 | 1.023 | 0.950–1.094 | 0.4116 | 0.7512 | no | 0.214 |
| children | 1511 | 1.000 | 0.302 | 1.014 | 0.896–1.141 | 0.4486 | 0.7512 | no | 0.249 |
| intellect | 1511 | 1.000 | 0.296 | 1.045 | 0.937–1.156 | 0.2897 | 0.7512 | no | 0.279 |
| health | 1511 | 1.000 | 0.498 | 0.996 | 0.938–1.049 | 0.6344 | 0.7512 | no | 0.258 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1511 | 1.000 | 0.302 | 1.105 | 0.988–1.219 | 0.0639 | 0.3516 | no | 0.264 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1511 | 1.000 | 0.274 | 0.970 | 0.857–1.082 | 0.7143 | 0.7512 | no | 0.299 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1511 | 1.000 | 0.506 | 1.038 | 0.961–1.113 | 0.1838 | 0.6740 | no | 0.210 |
| gains | 1511 | 1.000 | 0.312 | 0.988 | 0.891–1.101 | 0.6474 | 0.7512 | no | 0.269 |
| foreign | 1511 | 1.000 | 0.308 | 0.985 | 0.890–1.082 | 0.6553 | 0.7512 | no | 0.286 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1511 | 1.000 | 0.296 | 1.097 | 0.981–1.215 | 0.0519 | 0.3516 | no | 0.271 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1511 | 1.000 | 8 | 15.37 | 8 | 0.0524 | 0.473 | 0.484 | 0.3897 |
| mother_home | 1511 | 1.000 | 8 | 8.51 | 8 | 0.3853 | 0.477 | 0.479 | 0.8940 |
| children | 1511 | 1.000 | 7 | 12.97 | 7 | 0.0729 | 0.545 | 0.533 | 0.4538 |
| intellect | 1511 | 1.000 | 8 | 14.05 | 8 | 0.0804 | 0.505 | 0.531 | 0.0980 |
| health | 1511 | 1.000 | 8 | 4.74 | 8 | 0.7845 | 0.481 | 0.460 | 0.1281 |
| marriage | 1511 | 1.000 | 8 | 6.46 | 8 | 0.5954 | 0.490 | 0.501 | 0.2819 |
| father | 1511 | 1.000 | 7 | 7.60 | 7 | 0.3689 | 0.505 | 0.502 | 0.8697 |
| career | 1511 | 1.000 | 8 | 8.23 | 8 | 0.4116 | 0.506 | 0.508 | 0.8891 |
| gains | 1511 | 1.000 | 8 | 13.04 | 8 | 0.1104 | 0.473 | 0.491 | 0.1068 |
| foreign | 1511 | 1.000 | 7 | 10.79 | 7 | 0.1479 | 0.471 | 0.488 | 0.3321 |
| reputation | 1511 | 1.000 | 8 | 19.97 | 8 | 0.0105 | 0.505 | 0.530 | 0.1522 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1511 | 1.000 | 72537 | 471 | 0.934 | 0.928 | 0.4527 | -0.075 (-0.430, 0.280) |
| mother_home | 1511 | 1.000 | 63024 | 766 | 0.944 | 0.886 | 0.4677 | -0.123 (-0.417, 0.172) |
| children | 1511 | 1.000 | 73739 | 456 | 0.902 | 0.965 | 0.3184 | -0.036 (-0.341, 0.270) |
| intellect | 1511 | 1.000 | 73783 | 448 | 0.943 | 1.116 | 0.1940 | 0.110 (-0.311, 0.531) |
| health | 1511 | 1.000 | 63985 | 753 | 0.940 | 0.912 | 0.5970 | -0.093 (-0.385, 0.198) |
| marriage | 1511 | 1.000 | 73229 | 456 | 0.939 | 1.058 | 0.1990 | 0.056 (-0.341, 0.454) |
| father | 1511 | 1.000 | 74318 | 414 | 0.877 | 0.843 | 0.8557 | -0.171 (-0.448, 0.105) |
| career | 1511 | 1.000 | 63679 | 764 | 0.954 | 1.684 | 0.0100 | 0.527 (0.091, 0.962) |
| gains | 1511 | 1.000 | 72537 | 471 | 0.870 | 1.123 | 0.1493 | 0.117 (-0.165, 0.399) |
| foreign | 1511 | 1.000 | 72682 | 466 | 0.951 | 0.981 | 0.4826 | -0.019 (-0.440, 0.402) |
| reputation | 1511 | 1.000 | 73783 | 448 | 0.889 | 1.122 | 0.2786 | 0.116 (-0.193, 0.425) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1511 | 1.000 | 0.038 | 0.042 | 4 | 1 | not allowed |
| mother_home | 1511 | 1.000 | 0.025 | 0.028 | 5 | 0 | not allowed |
| children | 1511 | 1.000 | 0.038 | 0.027 | 5 | 1 | not allowed |
| intellect | 1511 | 1.000 | 0.026 | 0.024 | 3 | 1 | not allowed |
| health | 1511 | 1.000 | 0.024 | 0.048 | 2 | 32 | not allowed |
| marriage | 1511 | 1.000 | 0.029 | 0.045 | 3 | 1 | not allowed |
| father | 1511 | 1.000 | 0.020 | 0.050 | 2 | 4 | not allowed |
| career | 1511 | 1.000 | 0.043 | 0.017 | 3 | 1 | not allowed |
| gains | 1511 | 1.000 | 0.038 | 0.027 | 4 | 0 | not allowed |
| foreign | 1511 | 1.000 | 0.048 | 0.005 | 2 | 9 | not allowed |
| reputation | 1511 | 1.000 | 0.048 | 0.022 | 3 | 0 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1511 | 1.000 | 560 | 0.280 | 0.511 |
| mother_home | 1511 | 1.000 | 457 | 0.214 | 0.431 |
| children | 1511 | 1.000 | 428 | 0.249 | 0.471 |
| intellect | 1511 | 1.000 | 497 | 0.279 | 0.508 |
| health | 1511 | 1.000 | 651 | 0.258 | 0.487 |
| marriage | 1511 | 1.000 | 450 | 0.264 | 0.490 |
| father | 1511 | 1.000 | 542 | 0.299 | 0.532 |
| career | 1511 | 1.000 | 444 | 0.210 | 0.425 |
| gains | 1511 | 1.000 | 510 | 0.269 | 0.498 |
| foreign | 1511 | 1.000 | 573 | 0.286 | 0.518 |
| reputation | 1511 | 1.000 | 461 | 0.271 | 0.498 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 360 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1511 | 132 | -0.048 | -0.137–0.041 | 0.2903 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1511 | 124 | 0.038 | -0.054–0.129 | 0.4185 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1511 | 113 | -0.059 | -0.154–0.037 | 0.2280 | 0.059 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1511 | 123 | 0.071 | -0.017–0.160 | 0.1153 | 0.084 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1511 | 118 | 0.058 | -0.035–0.152 | 0.2213 | 0.062 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1511 | 127 | 0.050 | -0.041–0.140 | 0.2810 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1511 | 130 | -0.021 | -0.103–0.061 | 0.6115 | 0.086 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1511 | 140 | 0.006 | -0.074–0.086 | 0.8853 | 0.095 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1511 | 125 | -0.003 | -0.094–0.089 | 0.9563 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1511 | 132 | -0.007 | -0.088–0.075 | 0.8675 | 0.090 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1511 | 126 | 0.002 | -0.089–0.093 | 0.9691 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1511 | 121 | 0.024 | -0.063–0.111 | 0.5882 | 0.082 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1511 | 118 | 0.045 | -0.042–0.131 | 0.3146 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1511 | 116 | 0.001 | -0.089–0.091 | 0.9755 | 0.062 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1511 | 139 | -0.023 | -0.107–0.061 | 0.5933 | 0.075 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1511 | 143 | 0.027 | -0.054–0.108 | 0.5115 | 0.077 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1511 | 129 | 0.006 | -0.080–0.091 | 0.8995 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1511 | 135 | 0.022 | -0.061–0.105 | 0.6003 | 0.073 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1511 | 120 | -0.077 | -0.168–0.015 | 0.1013 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1511 | 117 | -0.051 | -0.143–0.041 | 0.2771 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1511 | 118 | -0.020 | -0.110–0.071 | 0.6671 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_scorpio` | 1511 | 136 | 0.073 | -0.006–0.153 | 0.0708 | 0.073 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1511 | 118 | -0.001 | -0.091–0.088 | 0.9748 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1511 | 122 | -0.016 | -0.105–0.073 | 0.7272 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1511 | 139 | -0.034 | -0.121–0.053 | 0.4463 | 0.072 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1511 | 130 | -0.057 | -0.146–0.033 | 0.2150 | 0.067 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1511 | 126 | 0.028 | -0.063–0.120 | 0.5395 | 0.066 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1511 | 123 | -0.044 | -0.126–0.038 | 0.2967 | 0.082 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1511 | 120 | 0.003 | -0.090–0.096 | 0.9507 | 0.063 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1511 | 103 | -0.011 | -0.111–0.089 | 0.8256 | 0.054 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1511 | 134 | 0.035 | -0.049–0.119 | 0.4190 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1511 | 122 | 0.037 | -0.050–0.124 | 0.4020 | 0.084 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1511 | 139 | 0.053 | -0.034–0.140 | 0.2290 | 0.073 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1511 | 131 | 0.012 | -0.071–0.095 | 0.7724 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1511 | 115 | -0.012 | -0.107–0.083 | 0.7993 | 0.060 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1511 | 129 | 0.070 | -0.017–0.156 | 0.1161 | 0.088 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1511 | 188 | -0.012 | -0.082–0.058 | 0.7361 | 0.122 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1511 | 92 | 0.042 | -0.058–0.142 | 0.4117 | 0.064 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1511 | 123 | -0.070 | -0.150–0.010 | 0.0843 | 0.082 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1511 | 151 | -0.004 | -0.082–0.073 | 0.9156 | 0.100 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1511 | 117 | 0.055 | -0.035–0.145 | 0.2337 | 0.080 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1511 | 108 | 0.067 | -0.027–0.161 | 0.1650 | 0.075 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1511 | 130 | 0.024 | -0.060–0.109 | 0.5701 | 0.088 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1511 | 145 | -0.028 | -0.106–0.049 | 0.4720 | 0.096 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1511 | 136 | -0.048 | -0.126–0.030 | 0.2281 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1511 | 102 | 0.037 | -0.058–0.132 | 0.4433 | 0.071 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1511 | 108 | -0.003 | -0.093–0.087 | 0.9468 | 0.074 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1511 | 111 | -0.022 | -0.109–0.066 | 0.6274 | 0.075 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1511 | 118 | -0.060 | -0.146–0.027 | 0.1751 | 0.073 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1511 | 125 | 0.085 | -0.005–0.176 | 0.0637 | 0.065 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1511 | 105 | -0.032 | -0.131–0.067 | 0.5313 | 0.055 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1511 | 127 | 0.053 | -0.030–0.137 | 0.2103 | 0.068 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1511 | 119 | 0.062 | -0.031–0.155 | 0.1887 | 0.062 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1511 | 99 | -0.022 | -0.124–0.080 | 0.6687 | 0.052 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1511 | 130 | 0.043 | -0.040–0.125 | 0.3135 | 0.070 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1511 | 146 | -0.057 | -0.140–0.027 | 0.1827 | 0.079 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1511 | 132 | 0.017 | -0.059–0.093 | 0.6645 | 0.082 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1511 | 149 | -0.045 | -0.127–0.037 | 0.2845 | 0.081 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1511 | 132 | 0.025 | -0.050–0.100 | 0.5126 | 0.082 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1511 | 129 | -0.018 | -0.104–0.069 | 0.6885 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1511 | 130 | 0.004 | -0.073–0.082 | 0.9116 | 0.081 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1511 | 113 | -0.011 | -0.107–0.085 | 0.8242 | 0.059 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1511 | 106 | -0.036 | -0.135–0.062 | 0.4681 | 0.056 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1511 | 115 | 0.066 | -0.020–0.153 | 0.1332 | 0.061 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1511 | 126 | -0.015 | -0.106–0.076 | 0.7504 | 0.066 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1511 | 126 | 0.080 | -0.010–0.171 | 0.0802 | 0.066 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1511 | 130 | -0.117 | -0.206–-0.028 | 0.0097 | 0.071 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1511 | 129 | 0.039 | -0.044–0.123 | 0.3559 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1511 | 139 | -0.041 | -0.120–0.037 | 0.3020 | 0.088 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1511 | 149 | 0.044 | -0.034–0.123 | 0.2667 | 0.080 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1511 | 119 | 0.053 | -0.023–0.128 | 0.1726 | 0.072 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1511 | 129 | 0.025 | -0.060–0.109 | 0.5686 | 0.069 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1511 | 131 | 0.002 | -0.084–0.087 | 0.9680 | 0.070 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1511 | 116 | 0.060 | -0.027–0.146 | 0.1772 | 0.062 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1511 | 118 | 0.001 | -0.089–0.090 | 0.9876 | 0.063 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1511 | 109 | 0.043 | -0.049–0.136 | 0.3592 | 0.075 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1511 | 137 | 0.006 | -0.078–0.089 | 0.8962 | 0.074 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1511 | 136 | 0.051 | -0.030–0.132 | 0.2158 | 0.073 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1511 | 113 | -0.029 | -0.125–0.066 | 0.5468 | 0.059 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1511 | 129 | -0.012 | -0.102–0.078 | 0.7936 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1511 | 121 | 0.078 | -0.006–0.162 | 0.0686 | 0.064 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1511 | 129 | 0.052 | -0.037–0.142 | 0.2535 | 0.067 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1511 | 146 | -0.042 | -0.125–0.041 | 0.3253 | 0.079 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1511 | 126 | -0.051 | -0.131–0.030 | 0.2171 | 0.084 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1511 | 129 | 0.040 | -0.050–0.130 | 0.3844 | 0.067 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1511 | 127 | 0.007 | -0.071–0.085 | 0.8679 | 0.079 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1511 | 112 | 0.019 | -0.062–0.101 | 0.6394 | 0.068 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1511 | 124 | -0.046 | -0.136–0.043 | 0.3123 | 0.066 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1511 | 111 | 0.007 | -0.076–0.090 | 0.8599 | 0.067 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1511 | 111 | -0.041 | -0.128–0.046 | 0.3553 | 0.068 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1511 | 142 | 0.017 | -0.064–0.098 | 0.6775 | 0.077 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1511 | 140 | 0.049 | -0.032–0.129 | 0.2348 | 0.075 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1511 | 123 | -0.047 | -0.139–0.045 | 0.3172 | 0.064 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1511 | 145 | -0.060 | -0.144–0.024 | 0.1615 | 0.078 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1511 | 136 | -0.031 | -0.118–0.057 | 0.4967 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1511 | 111 | 0.040 | -0.050–0.130 | 0.3790 | 0.059 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1511 | 130 | 0.030 | -0.046–0.105 | 0.4395 | 0.080 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1511 | 118 | 0.003 | -0.091–0.097 | 0.9486 | 0.062 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1511 | 118 | -0.034 | -0.128–0.060 | 0.4818 | 0.062 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1511 | 126 | -0.019 | -0.106–0.069 | 0.6792 | 0.068 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1511 | 139 | 0.014 | -0.074–0.101 | 0.7596 | 0.072 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1511 | 136 | 0.018 | -0.070–0.106 | 0.6876 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1511 | 113 | -0.083 | -0.177–0.011 | 0.0829 | 0.061 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1511 | 133 | 0.017 | -0.067–0.101 | 0.6948 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1511 | 117 | 0.012 | -0.069–0.092 | 0.7749 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1511 | 127 | -0.006 | -0.093–0.081 | 0.8912 | 0.068 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1511 | 129 | 0.036 | -0.039–0.111 | 0.3425 | 0.080 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1511 | 125 | 0.022 | -0.064–0.108 | 0.6175 | 0.067 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1511 | 134 | -0.020 | -0.099–0.058 | 0.6122 | 0.084 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1511 | 119 | -0.056 | -0.150–0.037 | 0.2368 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1511 | 125 | -0.019 | -0.111–0.072 | 0.6806 | 0.065 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1511 | 113 | 0.070 | -0.017–0.157 | 0.1129 | 0.060 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1511 | 136 | 0.050 | -0.037–0.138 | 0.2600 | 0.071 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1511 | 114 | 0.013 | -0.083–0.108 | 0.7911 | 0.060 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1511 | 117 | 0.015 | -0.073–0.104 | 0.7355 | 0.063 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1511 | 128 | -0.023 | -0.110–0.064 | 0.6050 | 0.069 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1511 | 122 | 0.058 | -0.016–0.132 | 0.1244 | 0.074 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1511 | 130 | 0.053 | -0.029–0.136 | 0.2060 | 0.069 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1511 | 132 | -0.033 | -0.113–0.047 | 0.4181 | 0.083 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1511 | 141 | 0.016 | -0.066–0.098 | 0.6961 | 0.076 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1511 | 105 | 0.078 | -0.010–0.166 | 0.0818 | 0.056 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1511 | 154 | 0.009 | -0.070–0.087 | 0.8309 | 0.084 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1511 | 123 | -0.003 | -0.090–0.085 | 0.9491 | 0.066 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1511 | 134 | 0.114 | 0.028–0.200 | 0.0093 | 0.069 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1511 | 145 | -0.014 | -0.096–0.067 | 0.7325 | 0.079 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1511 | 129 | -0.019 | -0.106–0.067 | 0.6597 | 0.070 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1511 | 99 | 0.066 | -0.032–0.165 | 0.1857 | 0.068 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1511 | 136 | 0.002 | -0.086–0.090 | 0.9634 | 0.070 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1511 | 113 | -0.063 | -0.157–0.030 | 0.1838 | 0.061 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1511 | 130 | -0.011 | -0.101–0.079 | 0.8143 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1511 | 121 | -0.044 | -0.134–0.046 | 0.3358 | 0.065 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1511 | 122 | -0.034 | -0.126–0.059 | 0.4746 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1511 | 122 | 0.052 | -0.033–0.138 | 0.2292 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1511 | 144 | 0.014 | -0.067–0.095 | 0.7323 | 0.078 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1511 | 120 | -0.040 | -0.131–0.050 | 0.3814 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1511 | 122 | -0.016 | -0.109–0.076 | 0.7315 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1511 | 146 | -0.019 | -0.101–0.063 | 0.6549 | 0.079 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1511 | 121 | -0.010 | -0.099–0.079 | 0.8246 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1511 | 121 | 0.001 | -0.092–0.093 | 0.9913 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1511 | 119 | -0.045 | -0.127–0.038 | 0.2870 | 0.081 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1511 | 111 | 0.020 | -0.072–0.111 | 0.6748 | 0.059 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1511 | 131 | -0.051 | -0.140–0.039 | 0.2674 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1511 | 143 | -0.006 | -0.088–0.077 | 0.8910 | 0.077 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1511 | 111 | 0.057 | -0.039–0.153 | 0.2448 | 0.058 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1511 | 126 | 0.036 | -0.055–0.127 | 0.4327 | 0.066 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1511 | 115 | -0.068 | -0.156–0.020 | 0.1283 | 0.071 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1511 | 114 | -0.033 | -0.119–0.053 | 0.4492 | 0.070 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1511 | 119 | 0.055 | -0.032–0.141 | 0.2156 | 0.063 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1511 | 119 | 0.071 | -0.003–0.144 | 0.0585 | 0.072 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1511 | 126 | -0.021 | -0.102–0.059 | 0.6025 | 0.078 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1511 | 130 | 0.026 | -0.057–0.110 | 0.5365 | 0.070 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1511 | 114 | 0.001 | -0.091–0.092 | 0.9899 | 0.061 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1511 | 118 | 0.029 | -0.064–0.123 | 0.5396 | 0.062 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1511 | 152 | 0.026 | -0.052–0.105 | 0.5110 | 0.082 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1511 | 129 | -0.053 | -0.143–0.037 | 0.2449 | 0.067 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1511 | 149 | 0.064 | -0.014–0.141 | 0.1073 | 0.080 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1511 | 108 | -0.019 | -0.113–0.075 | 0.6936 | 0.057 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1511 | 118 | 0.011 | -0.078–0.100 | 0.8151 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1511 | 117 | -0.057 | -0.150–0.035 | 0.2229 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1511 | 140 | 0.051 | -0.036–0.137 | 0.2486 | 0.072 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1511 | 115 | 0.029 | -0.060–0.118 | 0.5192 | 0.061 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1511 | 128 | 0.023 | -0.063–0.108 | 0.6035 | 0.068 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1511 | 110 | -0.039 | -0.135–0.058 | 0.4362 | 0.057 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1511 | 128 | 0.013 | -0.078–0.103 | 0.7811 | 0.066 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1511 | 129 | 0.021 | -0.064–0.106 | 0.6252 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1511 | 139 | 0.032 | -0.050–0.114 | 0.4423 | 0.095 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1511 | 141 | -0.002 | -0.085–0.081 | 0.9613 | 0.076 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1511 | 138 | 0.036 | -0.051–0.123 | 0.4206 | 0.071 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1511 | 133 | 0.014 | -0.075–0.103 | 0.7547 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1511 | 124 | 0.070 | -0.002–0.143 | 0.0556 | 0.075 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1511 | 125 | -0.120 | -0.207–-0.033 | 0.0071 | 0.079 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1511 | 119 | 0.027 | -0.061–0.115 | 0.5453 | 0.063 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1511 | 106 | 0.005 | -0.080–0.090 | 0.9036 | 0.064 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1511 | 115 | 0.045 | -0.033–0.123 | 0.2575 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1511 | 142 | -0.014 | -0.096–0.069 | 0.7409 | 0.077 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1511 | 136 | -0.026 | -0.111–0.059 | 0.5511 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1511 | 125 | -0.011 | -0.103–0.080 | 0.8091 | 0.065 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1511 | 137 | -0.005 | -0.090–0.079 | 0.8998 | 0.073 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1511 | 134 | 0.010 | -0.079–0.099 | 0.8250 | 0.070 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1511 | 115 | 0.005 | -0.085–0.096 | 0.9083 | 0.061 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1511 | 118 | -0.077 | -0.170–0.016 | 0.1032 | 0.063 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1511 | 116 | 0.060 | -0.027–0.146 | 0.1772 | 0.062 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1511 | 106 | -0.042 | -0.138–0.054 | 0.3957 | 0.056 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1511 | 127 | 0.016 | -0.069–0.101 | 0.7160 | 0.086 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1511 | 121 | -0.062 | -0.153–0.029 | 0.1830 | 0.065 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1511 | 134 | 0.054 | -0.027–0.136 | 0.1904 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1511 | 104 | -0.004 | -0.103–0.096 | 0.9393 | 0.054 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1511 | 139 | -0.036 | -0.123–0.051 | 0.4156 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1511 | 133 | 0.016 | -0.068–0.100 | 0.7135 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1511 | 144 | -0.066 | -0.152–0.019 | 0.1296 | 0.074 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1511 | 129 | 0.004 | -0.082–0.090 | 0.9224 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1511 | 140 | -0.001 | -0.082–0.079 | 0.9729 | 0.093 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1511 | 122 | 0.029 | -0.064–0.121 | 0.5449 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1511 | 135 | -0.002 | -0.090–0.086 | 0.9627 | 0.070 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1511 | 122 | -0.024 | -0.116–0.069 | 0.6117 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1511 | 114 | -0.030 | -0.116–0.056 | 0.4946 | 0.077 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1511 | 115 | -0.030 | -0.125–0.065 | 0.5411 | 0.060 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1511 | 129 | 0.040 | -0.049–0.130 | 0.3778 | 0.067 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1511 | 119 | -0.056 | -0.138–0.027 | 0.1869 | 0.079 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1511 | 138 | 0.011 | -0.070–0.092 | 0.7939 | 0.094 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1511 | 118 | 0.002 | -0.092–0.096 | 0.9701 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1511 | 130 | 0.107 | 0.020–0.195 | 0.0162 | 0.091 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1511 | 130 | 0.002 | -0.088–0.092 | 0.9685 | 0.068 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1511 | 139 | -0.023 | -0.102–0.056 | 0.5736 | 0.092 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1511 | 84 | -0.019 | -0.129–0.091 | 0.7408 | 0.045 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1511 | 103 | -0.043 | -0.142–0.057 | 0.4039 | 0.054 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1511 | 135 | 0.079 | -0.008–0.167 | 0.0756 | 0.070 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1511 | 105 | -0.011 | -0.110–0.088 | 0.8253 | 0.055 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1511 | 129 | -0.061 | -0.151–0.029 | 0.1813 | 0.067 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1511 | 165 | -0.044 | -0.124–0.037 | 0.2880 | 0.085 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1511 | 161 | -0.010 | -0.091–0.072 | 0.8147 | 0.083 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1511 | 123 | -0.019 | -0.112–0.073 | 0.6799 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1511 | 97 | 0.011 | -0.092–0.113 | 0.8411 | 0.051 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1511 | 114 | 0.051 | -0.044–0.146 | 0.2940 | 0.060 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1511 | 144 | 0.040 | -0.046–0.125 | 0.3616 | 0.075 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1511 | 151 | 0.020 | -0.064–0.103 | 0.6490 | 0.078 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1511 | 115 | 0.082 | -0.012–0.176 | 0.0885 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1511 | 122 | -0.006 | -0.099–0.086 | 0.8969 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1511 | 112 | 0.004 | -0.093–0.100 | 0.9421 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1511 | 123 | -0.017 | -0.101–0.067 | 0.6897 | 0.083 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1511 | 125 | -0.010 | -0.102–0.081 | 0.8222 | 0.065 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1511 | 133 | 0.014 | -0.074–0.103 | 0.7502 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1511 | 113 | -0.002 | -0.091–0.087 | 0.9623 | 0.076 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1511 | 133 | -0.026 | -0.106–0.054 | 0.5259 | 0.090 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1511 | 121 | -0.093 | -0.184–-0.001 | 0.0477 | 0.063 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1511 | 138 | -0.077 | -0.151–-0.002 | 0.0431 | 0.092 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1511 | 150 | -0.043 | -0.127–0.041 | 0.3209 | 0.078 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1511 | 126 | 0.010 | -0.075–0.095 | 0.8195 | 0.085 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1511 | 129 | -0.019 | -0.109–0.071 | 0.6819 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1511 | 116 | -0.034 | -0.129–0.060 | 0.4797 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1511 | 112 | -0.035 | -0.131–0.061 | 0.4753 | 0.059 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1511 | 122 | 0.021 | -0.072–0.113 | 0.6618 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1511 | 119 | 0.035 | -0.058–0.128 | 0.4632 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1511 | 133 | 0.031 | -0.058–0.120 | 0.4948 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1511 | 133 | -0.002 | -0.091–0.087 | 0.9641 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1511 | 138 | -0.046 | -0.133–0.041 | 0.3011 | 0.072 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1511 | 136 | 0.067 | -0.021–0.154 | 0.1356 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1511 | 145 | 0.005 | -0.080–0.091 | 0.9048 | 0.075 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1511 | 100 | -0.006 | -0.107–0.095 | 0.9073 | 0.053 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1511 | 128 | -0.023 | -0.114–0.067 | 0.6151 | 0.067 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1511 | 123 | -0.011 | -0.104–0.081 | 0.8072 | 0.064 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1511 | 138 | -0.022 | -0.110–0.065 | 0.6199 | 0.072 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1511 | 106 | -0.036 | -0.135–0.062 | 0.4681 | 0.056 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1511 | 127 | 0.059 | -0.028–0.146 | 0.1859 | 0.086 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1511 | 138 | 0.018 | -0.070–0.105 | 0.6910 | 0.072 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1511 | 120 | -0.006 | -0.099–0.087 | 0.8978 | 0.063 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1511 | 116 | 0.017 | -0.072–0.106 | 0.7043 | 0.078 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1511 | 131 | 0.021 | -0.063–0.104 | 0.6285 | 0.090 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1511 | 127 | 0.023 | -0.068–0.114 | 0.6150 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1511 | 133 | 0.081 | -0.004–0.167 | 0.0631 | 0.092 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1511 | 126 | -0.024 | -0.115–0.067 | 0.6030 | 0.066 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1511 | 126 | 0.010 | -0.075–0.095 | 0.8195 | 0.085 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1511 | 131 | 0.098 | 0.010–0.186 | 0.0298 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1511 | 134 | 0.027 | -0.062–0.115 | 0.5562 | 0.070 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1511 | 122 | 0.030 | -0.063–0.122 | 0.5306 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1511 | 139 | -0.007 | -0.087–0.073 | 0.8664 | 0.093 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1511 | 115 | -0.039 | -0.134–0.056 | 0.4202 | 0.060 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1511 | 129 | -0.053 | -0.143–0.037 | 0.2501 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1511 | 130 | -0.131 | -0.203–-0.059 | 0.0004 | 0.084 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1511 | 126 | 0.017 | -0.068–0.102 | 0.6926 | 0.086 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1511 | 123 | -0.020 | -0.112–0.072 | 0.6654 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1511 | 139 | 0.000 | -0.080–0.081 | 0.9920 | 0.094 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1511 | 120 | 0.029 | -0.064–0.122 | 0.5423 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1511 | 103 | -0.039 | -0.128–0.050 | 0.3889 | 0.070 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1511 | 108 | 0.016 | -0.076–0.108 | 0.7355 | 0.057 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1511 | 130 | 0.011 | -0.075–0.096 | 0.8079 | 0.070 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1511 | 151 | -0.025 | -0.106–0.056 | 0.5413 | 0.082 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1511 | 123 | -0.019 | -0.108–0.069 | 0.6697 | 0.066 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1511 | 136 | -0.054 | -0.140–0.032 | 0.2201 | 0.073 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1511 | 188 | 0.021 | -0.051–0.093 | 0.5686 | 0.103 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1511 | 92 | 0.058 | -0.038–0.154 | 0.2364 | 0.049 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1511 | 111 | 0.074 | -0.013–0.161 | 0.0947 | 0.059 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1511 | 117 | -0.012 | -0.102–0.079 | 0.7986 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1511 | 108 | -0.034 | -0.129–0.061 | 0.4831 | 0.058 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1511 | 102 | 0.068 | -0.023–0.159 | 0.1407 | 0.054 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1511 | 145 | -0.065 | -0.149–0.019 | 0.1284 | 0.079 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1511 | 136 | 0.026 | -0.062–0.114 | 0.5617 | 0.071 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1511 | 111 | 0.077 | -0.019–0.172 | 0.1163 | 0.058 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1511 | 121 | -0.056 | -0.148–0.037 | 0.2395 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1511 | 138 | 0.027 | -0.055–0.110 | 0.5137 | 0.093 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1511 | 131 | -0.052 | -0.141–0.037 | 0.2526 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1511 | 121 | -0.065 | -0.157–0.028 | 0.1711 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1511 | 121 | 0.056 | -0.033–0.146 | 0.2143 | 0.082 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1511 | 142 | 0.001 | -0.078–0.081 | 0.9776 | 0.096 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1511 | 119 | 0.015 | -0.078–0.109 | 0.7458 | 0.062 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1511 | 130 | -0.010 | -0.092–0.071 | 0.8039 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1511 | 117 | -0.040 | -0.134–0.054 | 0.4058 | 0.061 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1511 | 124 | 0.007 | -0.079–0.092 | 0.8784 | 0.084 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1511 | 112 | 0.029 | -0.051–0.110 | 0.4780 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1511 | 143 | 0.029 | -0.043–0.101 | 0.4281 | 0.090 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1511 | 94 | -0.051 | -0.146–0.044 | 0.2946 | 0.056 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1511 | 126 | -0.030 | -0.112–0.051 | 0.4685 | 0.078 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1511 | 108 | 0.030 | -0.052–0.112 | 0.4700 | 0.065 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1511 | 133 | 0.043 | -0.030–0.116 | 0.2432 | 0.082 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1511 | 145 | 0.025 | -0.047–0.097 | 0.4967 | 0.091 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1511 | 124 | -0.009 | -0.089–0.072 | 0.8337 | 0.077 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1511 | 134 | 0.045 | -0.027–0.118 | 0.2220 | 0.083 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1511 | 140 | 0.000 | -0.075–0.075 | 0.9962 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1511 | 122 | -0.067 | -0.152–0.019 | 0.1251 | 0.076 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1511 | 130 | -0.063 | -0.145–0.020 | 0.1349 | 0.082 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1511 | 111 | 0.152 | 0.059–0.246 | 0.0013 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1511 | 123 | -0.019 | -0.112–0.073 | 0.6799 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1511 | 109 | -0.041 | -0.138–0.057 | 0.4125 | 0.057 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1511 | 126 | 0.010 | -0.075–0.095 | 0.8195 | 0.085 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1511 | 136 | 0.026 | -0.062–0.114 | 0.5602 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1511 | 113 | 0.018 | -0.078–0.114 | 0.7151 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1511 | 121 | 0.003 | -0.084–0.089 | 0.9540 | 0.081 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1511 | 130 | -0.002 | -0.084–0.080 | 0.9629 | 0.089 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1511 | 118 | 0.075 | -0.018–0.168 | 0.1130 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1511 | 143 | 0.014 | -0.066–0.094 | 0.7267 | 0.097 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1511 | 139 | -0.042 | -0.129–0.045 | 0.3468 | 0.072 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1511 | 142 | 0.048 | -0.034–0.130 | 0.2503 | 0.096 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1511 | 117 | -0.039 | -0.133–0.056 | 0.4227 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1511 | 137 | 0.062 | -0.025–0.149 | 0.1631 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1511 | 122 | -0.006 | -0.099–0.086 | 0.8969 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1511 | 128 | 0.028 | -0.062–0.118 | 0.5438 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1511 | 121 | 0.007 | -0.086–0.100 | 0.8765 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1511 | 130 | 0.036 | -0.054–0.126 | 0.4322 | 0.068 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1511 | 118 | 0.021 | -0.072–0.115 | 0.6538 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1511 | 135 | -0.132 | -0.218–-0.046 | 0.0026 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1511 | 106 | 0.116 | 0.019–0.212 | 0.0186 | 0.056 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1511 | 133 | 0.014 | -0.074–0.103 | 0.7502 | 0.069 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1511 | 124 | -0.032 | -0.124–0.059 | 0.4877 | 0.065 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1511 | 140 | -0.053 | -0.140–0.033 | 0.2268 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1511 | 120 | 0.020 | -0.073–0.113 | 0.6755 | 0.063 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1511 | 122 | 0.047 | -0.045–0.140 | 0.3134 | 0.064 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1511 | 119 | -0.093 | -0.185–-0.000 | 0.0493 | 0.062 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1511 | 113 | 0.001 | -0.087–0.090 | 0.9746 | 0.077 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1511 | 134 | 0.068 | -0.020–0.155 | 0.1324 | 0.070 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1511 | 111 | -0.060 | -0.156–0.037 | 0.2250 | 0.058 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1511 | 124 | -0.006 | -0.090–0.079 | 0.8945 | 0.083 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1511 | 105 | -0.028 | -0.116–0.061 | 0.5439 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1511 | 136 | 0.050 | -0.037–0.138 | 0.2614 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1511 | 163 | -0.036 | -0.108–0.037 | 0.3342 | 0.108 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1511 | 140 | -0.006 | -0.093–0.081 | 0.8915 | 0.073 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1511 | 124 | 0.015 | -0.070–0.101 | 0.7242 | 0.084 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1511 | 101 | -0.016 | -0.107–0.076 | 0.7363 | 0.070 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1511 | 121 | -0.014 | -0.098–0.071 | 0.7515 | 0.083 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1511 | 109 | 0.041 | -0.051–0.133 | 0.3875 | 0.076 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1511 | 167 | -0.070 | -0.139–-0.001 | 0.0477 | 0.110 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1511 | 138 | 0.059 | -0.025–0.142 | 0.1682 | 0.095 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1511 | 159 | -0.021 | -0.095–0.053 | 0.5795 | 0.106 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1511 | 138 | -0.061 | -0.137–0.015 | 0.1154 | 0.092 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1511 | 137 | 0.037 | -0.045–0.120 | 0.3758 | 0.094 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1511 | 110 | 0.096 | 0.002–0.190 | 0.0456 | 0.078 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1511 | 106 | -0.111 | -0.191–-0.032 | 0.0061 | 0.072 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1511 | 133 | 0.007 | -0.075–0.089 | 0.8653 | 0.091 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1511 | 92 | 0.095 | -0.007–0.198 | 0.0684 | 0.066 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1511 | 188 | 0.006 | -0.071–0.082 | 0.8832 | 0.097 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1511 | 766 | -0.014 | -0.064–0.036 | 0.5847 | 0.265 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1511 | 524 | -0.007 | -0.057–0.043 | 0.7805 | 0.274 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1511 | 144 | -0.078 | -0.162–0.006 | 0.0679 | 0.079 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1511 | 251 | -0.038 | -0.105–0.030 | 0.2735 | 0.128 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1511 | 800 | -0.004 | -0.054–0.047 | 0.8771 | 0.264 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1511 | 966 | 0.039 | -0.014–0.091 | 0.1458 | 0.239 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1511 | 273 | 0.008 | -0.058–0.073 | 0.8187 | 0.139 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1511 | 679 | 0.047 | -0.003–0.098 | 0.0671 | 0.260 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1511 | 538 | -0.028 | -0.078–0.022 | 0.2734 | 0.283 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1511 | 225 | 0.043 | -0.028–0.114 | 0.2326 | 0.116 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1511 | 261 | -0.004 | -0.071–0.062 | 0.8952 | 0.133 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
