# Synthetic — Validation — planted, N = 2,000, odds ratio 1.2 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1502 development, 498 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `ce126a6fcd9accfa188b2d622698d9ff73fec086de8d5cc415c1780622692274` ({"salt_sha256": "6295df2c9197b43b02a9ebf2563806128934891279163c3d1169f838b2803d4d", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "bac2bac83577fa8502afef2d5c0e959fa56fc6093c6ca16e2abce144b74f5459"})
- analysis code `494dae55f6a48ddf1c97767f4f82d77adf00c78f1bdbab2488c65c423b7b012c`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1502 | 1.000 | 0.316 | 1.011 | 0.914–1.111 | 0.3437 | 0.3437 | no | 0.276 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1502 | 1.000 | 0.513 | 1.048 | 0.980–1.124 | 0.1279 | 0.1758 | no | 0.214 |
| children | 1502 | 1.000 | 0.302 | 1.113 | 0.984–1.243 | 0.0569 | 0.0895 | no | 0.248 |
| intellect | 1502 | 1.000 | 0.328 | 1.146 | 1.038–1.250 | 0.0160 | 0.0440 | yes | 0.265 |
| health | 1502 | 1.000 | 0.510 | 1.055 | 0.997–1.116 | 0.0509 | 0.0895 | no | 0.255 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1502 | 1.000 | 0.308 | 1.130 | 1.020–1.250 | 0.0130 | 0.0440 | yes | 0.259 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1502 | 1.000 | 0.290 | 1.038 | 0.932–1.145 | 0.2787 | 0.3407 | no | 0.285 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1502 | 1.000 | 0.546 | 1.107 | 1.041–1.176 | 0.0020 | 0.0220 | yes | 0.215 |
| gains | 1502 | 1.000 | 0.316 | 1.019 | 0.920–1.120 | 0.3387 | 0.3437 | no | 0.269 |
| foreign | 1502 | 1.000 | 0.284 | 1.111 | 1.007–1.213 | 0.0300 | 0.0659 | no | 0.315 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1502 | 1.000 | 0.328 | 1.155 | 1.046–1.271 | 0.0050 | 0.0275 | yes | 0.256 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1502 | 1.000 | 8 | 7.50 | 8 | 0.4843 | 0.452 | 0.467 | 0.2493 |
| mother_home | 1502 | 1.000 | 8 | 19.43 | 8 | 0.0127 | 0.487 | 0.528 | 0.0088 |
| children | 1502 | 1.000 | 7 | 26.11 | 7 | 0.0005 | 0.473 | 0.520 | 0.0058 |
| intellect | 1502 | 1.000 | 8 | 25.08 | 8 | 0.0015 | 0.492 | 0.545 | 0.0005 |
| health | 1502 | 1.000 | 8 | 35.09 | 8 | 0.0000 | 0.498 | 0.554 | 0.0007 |
| marriage | 1502 | 1.000 | 8 | 24.03 | 8 | 0.0023 | 0.498 | 0.540 | 0.0030 |
| father | 1502 | 1.000 | 7 | 9.01 | 7 | 0.2517 | 0.467 | 0.502 | 0.0362 |
| career | 1502 | 1.000 | 8 | 18.60 | 8 | 0.0171 | 0.507 | 0.527 | 0.0889 |
| gains | 1502 | 1.000 | 8 | 13.18 | 8 | 0.1057 | 0.452 | 0.495 | 0.0019 |
| foreign | 1502 | 1.000 | 7 | 10.12 | 7 | 0.1817 | 0.505 | 0.528 | 0.0508 |
| reputation | 1502 | 1.000 | 8 | 13.53 | 8 | 0.0948 | 0.492 | 0.522 | 0.0362 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1502 | 1.000 | 72943 | 474 | 0.936 | 1.285 | 0.0995 | 0.252 (-0.160, 0.663) |
| mother_home | 1502 | 1.000 | 62956 | 771 | 0.942 | 1.123 | 0.4577 | 0.118 (-0.203, 0.438) |
| children | 1502 | 1.000 | 73594 | 454 | 0.904 | 1.200 | 0.0348 | 0.183 (-0.154, 0.520) |
| intellect | 1502 | 1.000 | 71917 | 493 | 0.943 | 1.521 | 0.0100 | 0.422 (-0.038, 0.881) |
| health | 1502 | 1.000 | 64813 | 766 | 0.940 | 1.244 | 0.0448 | 0.220 (-0.112, 0.552) |
| marriage | 1502 | 1.000 | 72933 | 463 | 0.941 | 0.969 | 0.3284 | -0.032 (-0.415, 0.352) |
| father | 1502 | 1.000 | 73595 | 436 | 0.876 | 1.074 | 0.1940 | 0.071 (-0.222, 0.364) |
| career | 1502 | 1.000 | 61613 | 820 | 0.956 | 0.949 | 0.3682 | -0.053 (-0.381, 0.276) |
| gains | 1502 | 1.000 | 72943 | 474 | 0.871 | 1.001 | 0.5771 | 0.001 (-0.269, 0.271) |
| foreign | 1502 | 1.000 | 74632 | 426 | 0.950 | 0.876 | 0.8905 | -0.133 (-0.546, 0.281) |
| reputation | 1502 | 1.000 | 71917 | 493 | 0.888 | 1.117 | 0.2836 | 0.111 (-0.182, 0.405) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1502 | 1.000 | 0.034 | 0.013 | 5 | 0 | not allowed |
| mother_home | 1502 | 1.000 | 0.054 | 0.027 | 6 | 1 | not allowed |
| children | 1502 | 1.000 | 0.020 | 0.035 | 7 | 1 | not allowed |
| intellect | 1502 | 1.000 | 0.044 | 0.034 | 6 | 0 | not allowed |
| health | 1502 | 1.000 | 0.038 | 0.045 | 7 | 4 | not allowed |
| marriage | 1502 | 1.000 | 0.023 | 0.035 | 5 | 0 | not allowed |
| father | 1502 | 1.000 | 0.038 | 0.052 | 7 | 0 | not allowed |
| career | 1502 | 1.000 | 0.035 | 0.067 | 5 | 1 | not allowed |
| gains | 1502 | 1.000 | 0.022 | 0.019 | 4 | 0 | not allowed |
| foreign | 1502 | 1.000 | 0.021 | 0.021 | 5 | 0 | not allowed |
| reputation | 1502 | 1.000 | 0.034 | 0.053 | 4 | 4 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1502 | 1.000 | 542 | 0.276 | 0.507 |
| mother_home | 1502 | 1.000 | 459 | 0.214 | 0.431 |
| children | 1502 | 1.000 | 413 | 0.248 | 0.470 |
| intellect | 1502 | 1.000 | 484 | 0.265 | 0.492 |
| health | 1502 | 1.000 | 643 | 0.255 | 0.483 |
| marriage | 1502 | 1.000 | 445 | 0.259 | 0.484 |
| father | 1502 | 1.000 | 511 | 0.285 | 0.516 |
| career | 1502 | 1.000 | 460 | 0.215 | 0.433 |
| gains | 1502 | 1.000 | 510 | 0.269 | 0.497 |
| foreign | 1502 | 1.000 | 571 | 0.315 | 0.550 |
| reputation | 1502 | 1.000 | 459 | 0.256 | 0.481 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 360 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1502 | 127 | -0.007 | -0.097–0.084 | 0.8867 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1502 | 130 | -0.008 | -0.098–0.081 | 0.8580 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1502 | 109 | -0.054 | -0.152–0.043 | 0.2731 | 0.056 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1502 | 127 | -0.000 | -0.082–0.082 | 0.9967 | 0.091 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1502 | 134 | 0.031 | -0.056–0.119 | 0.4818 | 0.069 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1502 | 128 | -0.050 | -0.141–0.040 | 0.2769 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1502 | 121 | -0.011 | -0.096–0.075 | 0.8075 | 0.080 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1502 | 143 | -0.009 | -0.088–0.069 | 0.8134 | 0.096 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1502 | 120 | 0.016 | -0.077–0.109 | 0.7314 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1502 | 117 | -0.038 | -0.122–0.047 | 0.3813 | 0.079 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1502 | 140 | -0.058 | -0.145–0.028 | 0.1876 | 0.072 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1502 | 106 | -0.011 | -0.099–0.077 | 0.8101 | 0.077 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1502 | 125 | 0.038 | -0.045–0.121 | 0.3695 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1502 | 128 | -0.048 | -0.135–0.039 | 0.2758 | 0.071 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1502 | 123 | 0.095 | 0.016–0.174 | 0.0186 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1502 | 145 | -0.124 | -0.208–-0.039 | 0.0041 | 0.082 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1502 | 138 | 0.004 | -0.077–0.086 | 0.9145 | 0.076 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1502 | 134 | 0.051 | -0.028–0.131 | 0.2064 | 0.074 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1502 | 115 | -0.102 | -0.196–-0.009 | 0.0317 | 0.063 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1502 | 110 | -0.073 | -0.168–0.021 | 0.1277 | 0.060 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1502 | 126 | 0.127 | 0.052–0.202 | 0.0009 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_in_scorpio` | 1502 | 133 | 0.082 | 0.005–0.160 | 0.0380 | 0.073 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1502 | 110 | -0.005 | -0.096–0.086 | 0.9192 | 0.060 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1502 | 115 | -0.055 | -0.147–0.037 | 0.2381 | 0.063 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1502 | 143 | -0.023 | -0.109–0.064 | 0.6066 | 0.074 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1502 | 126 | -0.015 | -0.107–0.076 | 0.7387 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1502 | 127 | 0.066 | -0.023–0.155 | 0.1463 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1502 | 121 | 0.024 | -0.061–0.110 | 0.5803 | 0.088 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1502 | 128 | 0.018 | -0.072–0.108 | 0.6930 | 0.066 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1502 | 100 | -0.017 | -0.118–0.084 | 0.7409 | 0.052 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1502 | 134 | 0.071 | -0.014–0.157 | 0.1029 | 0.089 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1502 | 130 | 0.014 | -0.069–0.098 | 0.7359 | 0.089 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1502 | 134 | -0.068 | -0.157–0.020 | 0.1292 | 0.069 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1502 | 126 | -0.033 | -0.115–0.049 | 0.4262 | 0.084 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1502 | 111 | -0.045 | -0.141–0.052 | 0.3624 | 0.058 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1502 | 122 | 0.030 | -0.055–0.116 | 0.4872 | 0.088 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1502 | 176 | -0.025 | -0.095–0.044 | 0.4760 | 0.122 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1502 | 84 | -0.036 | -0.131–0.060 | 0.4650 | 0.063 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1502 | 127 | -0.000 | -0.082–0.082 | 0.9967 | 0.091 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1502 | 151 | 0.045 | -0.033–0.124 | 0.2559 | 0.108 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1502 | 115 | 0.022 | -0.065–0.110 | 0.6146 | 0.084 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1502 | 113 | 0.028 | -0.060–0.117 | 0.5316 | 0.082 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1502 | 130 | 0.001 | -0.080–0.082 | 0.9790 | 0.093 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1502 | 159 | -0.001 | -0.075–0.073 | 0.9858 | 0.112 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1502 | 126 | -0.024 | -0.104–0.057 | 0.5633 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1502 | 102 | 0.001 | -0.090–0.091 | 0.9872 | 0.075 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1502 | 106 | -0.031 | -0.117–0.055 | 0.4798 | 0.077 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1502 | 113 | 0.009 | -0.078–0.096 | 0.8378 | 0.082 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1502 | 127 | 0.044 | -0.027–0.116 | 0.2238 | 0.082 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1502 | 118 | 0.024 | -0.069–0.117 | 0.6177 | 0.061 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1502 | 103 | -0.127 | -0.227–-0.028 | 0.0116 | 0.053 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1502 | 132 | -0.047 | -0.133–0.039 | 0.2832 | 0.073 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1502 | 116 | 0.053 | -0.040–0.146 | 0.2647 | 0.060 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1502 | 112 | -0.001 | -0.097–0.094 | 0.9772 | 0.058 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1502 | 140 | -0.073 | -0.157–0.012 | 0.0920 | 0.078 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1502 | 121 | -0.008 | -0.096–0.079 | 0.8514 | 0.066 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1502 | 113 | 0.009 | -0.071–0.089 | 0.8220 | 0.072 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1502 | 145 | 0.031 | -0.047–0.109 | 0.4368 | 0.081 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1502 | 147 | 0.028 | -0.041–0.097 | 0.4195 | 0.098 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1502 | 128 | 0.017 | -0.067–0.101 | 0.6885 | 0.070 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1502 | 128 | 0.038 | -0.035–0.110 | 0.3078 | 0.083 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1502 | 121 | -0.036 | -0.129–0.056 | 0.4412 | 0.062 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1502 | 107 | 0.096 | 0.002–0.191 | 0.0463 | 0.056 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1502 | 125 | -0.087 | -0.177–0.003 | 0.0570 | 0.069 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1502 | 145 | 0.022 | -0.063–0.107 | 0.6170 | 0.075 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1502 | 130 | 0.000 | -0.089–0.090 | 0.9959 | 0.067 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1502 | 113 | -0.010 | -0.101–0.080 | 0.8261 | 0.061 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1502 | 109 | 0.002 | -0.089–0.093 | 0.9666 | 0.059 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1502 | 129 | 0.039 | -0.033–0.111 | 0.2836 | 0.083 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1502 | 145 | 0.046 | -0.031–0.123 | 0.2391 | 0.081 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1502 | 125 | -0.003 | -0.080–0.075 | 0.9491 | 0.081 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1502 | 125 | 0.009 | -0.076–0.094 | 0.8369 | 0.068 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1502 | 130 | -0.000 | -0.086–0.086 | 0.9937 | 0.069 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1502 | 108 | -0.005 | -0.098–0.087 | 0.9070 | 0.058 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1502 | 109 | 0.047 | -0.041–0.135 | 0.2938 | 0.059 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1502 | 107 | -0.024 | -0.110–0.063 | 0.5929 | 0.078 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1502 | 147 | 0.017 | -0.062–0.096 | 0.6740 | 0.081 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1502 | 144 | -0.029 | -0.111–0.053 | 0.4929 | 0.080 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1502 | 111 | 0.003 | -0.093–0.100 | 0.9446 | 0.058 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1502 | 121 | 0.082 | -0.010–0.174 | 0.0801 | 0.064 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1502 | 120 | 0.031 | -0.057–0.119 | 0.4875 | 0.064 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1502 | 126 | 0.002 | -0.089–0.093 | 0.9646 | 0.065 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1502 | 151 | 0.018 | -0.062–0.097 | 0.6659 | 0.081 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1502 | 128 | -0.028 | -0.108–0.051 | 0.4865 | 0.091 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1502 | 126 | 0.006 | -0.085–0.098 | 0.8901 | 0.065 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1502 | 124 | -0.049 | -0.130–0.033 | 0.2438 | 0.081 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1502 | 115 | -0.006 | -0.086–0.075 | 0.8934 | 0.073 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1502 | 134 | 0.101 | 0.023–0.180 | 0.0115 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1502 | 120 | -0.031 | -0.113–0.050 | 0.4534 | 0.078 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1502 | 112 | 0.017 | -0.063–0.096 | 0.6802 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1502 | 138 | -0.007 | -0.090–0.076 | 0.8708 | 0.075 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1502 | 141 | -0.039 | -0.123–0.044 | 0.3571 | 0.077 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1502 | 113 | 0.013 | -0.083–0.109 | 0.7883 | 0.059 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1502 | 135 | -0.004 | -0.087–0.079 | 0.9223 | 0.074 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1502 | 135 | -0.015 | -0.103–0.073 | 0.7388 | 0.070 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1502 | 109 | 0.015 | -0.077–0.108 | 0.7474 | 0.058 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1502 | 130 | 0.049 | -0.021–0.120 | 0.1692 | 0.084 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1502 | 122 | -0.041 | -0.134–0.051 | 0.3842 | 0.063 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1502 | 128 | 0.001 | -0.089–0.091 | 0.9823 | 0.066 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1502 | 119 | -0.109 | -0.201–-0.017 | 0.0206 | 0.065 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1502 | 138 | 0.045 | -0.041–0.131 | 0.3050 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1502 | 138 | 0.029 | -0.057–0.116 | 0.5089 | 0.071 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1502 | 104 | -0.000 | -0.093–0.093 | 0.9995 | 0.056 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1502 | 141 | -0.051 | -0.134–0.033 | 0.2339 | 0.079 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1502 | 105 | 0.032 | -0.048–0.112 | 0.4321 | 0.065 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1502 | 115 | 0.071 | -0.012–0.154 | 0.0948 | 0.063 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1502 | 138 | -0.050 | -0.128–0.027 | 0.2049 | 0.093 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1502 | 124 | -0.011 | -0.098–0.075 | 0.7967 | 0.068 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1502 | 125 | 0.041 | -0.031–0.114 | 0.2668 | 0.080 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1502 | 115 | 0.030 | -0.064–0.124 | 0.5281 | 0.059 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1502 | 115 | -0.045 | -0.140–0.050 | 0.3531 | 0.059 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1502 | 120 | -0.060 | -0.150–0.031 | 0.1942 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1502 | 135 | 0.059 | -0.027–0.146 | 0.1796 | 0.069 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1502 | 124 | 0.047 | -0.044–0.137 | 0.3127 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1502 | 110 | -0.020 | -0.112–0.072 | 0.6704 | 0.060 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1502 | 132 | -0.053 | -0.139–0.033 | 0.2276 | 0.073 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1502 | 122 | 0.009 | -0.068–0.086 | 0.8162 | 0.079 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1502 | 130 | 0.045 | -0.036–0.125 | 0.2803 | 0.072 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1502 | 128 | -0.022 | -0.100–0.056 | 0.5781 | 0.084 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1502 | 146 | 0.030 | -0.049–0.108 | 0.4578 | 0.080 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1502 | 108 | 0.029 | -0.062–0.120 | 0.5354 | 0.058 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1502 | 148 | -0.050 | -0.131–0.032 | 0.2342 | 0.082 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1502 | 119 | 0.045 | -0.040–0.130 | 0.3016 | 0.065 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1502 | 136 | -0.001 | -0.090–0.087 | 0.9740 | 0.071 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1502 | 166 | 0.036 | -0.038–0.109 | 0.3439 | 0.092 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1502 | 116 | -0.010 | -0.100–0.079 | 0.8250 | 0.063 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1502 | 98 | 0.044 | -0.053–0.142 | 0.3734 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1502 | 127 | -0.023 | -0.114–0.068 | 0.6167 | 0.066 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1502 | 110 | -0.083 | -0.178–0.013 | 0.0895 | 0.059 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1502 | 129 | 0.025 | -0.065–0.114 | 0.5924 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1502 | 121 | 0.003 | -0.085–0.091 | 0.9478 | 0.065 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1502 | 124 | -0.045 | -0.137–0.046 | 0.3313 | 0.065 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1502 | 123 | -0.010 | -0.098–0.078 | 0.8198 | 0.066 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1502 | 130 | 0.050 | -0.030–0.131 | 0.2222 | 0.071 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1502 | 123 | -0.135 | -0.227–-0.044 | 0.0036 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1502 | 121 | 0.037 | -0.056–0.130 | 0.4312 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1502 | 148 | 0.036 | -0.041–0.113 | 0.3626 | 0.082 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1502 | 120 | -0.011 | -0.099–0.077 | 0.8004 | 0.066 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1502 | 129 | 0.070 | -0.019–0.159 | 0.1232 | 0.067 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1502 | 115 | -0.007 | -0.094–0.080 | 0.8716 | 0.079 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1502 | 113 | -0.149 | -0.244–-0.054 | 0.0022 | 0.061 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1502 | 133 | 0.010 | -0.079–0.099 | 0.8188 | 0.069 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1502 | 136 | -0.006 | -0.090–0.078 | 0.8900 | 0.074 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1502 | 111 | 0.050 | -0.047–0.146 | 0.3138 | 0.059 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1502 | 115 | -0.034 | -0.129–0.061 | 0.4785 | 0.060 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1502 | 127 | -0.024 | -0.103–0.054 | 0.5445 | 0.083 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1502 | 109 | -0.039 | -0.125–0.047 | 0.3706 | 0.069 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1502 | 133 | 0.008 | -0.076–0.093 | 0.8458 | 0.071 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1502 | 127 | 0.027 | -0.046–0.101 | 0.4679 | 0.082 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1502 | 117 | 0.017 | -0.060–0.095 | 0.6605 | 0.075 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1502 | 128 | -0.096 | -0.186–-0.007 | 0.0345 | 0.070 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1502 | 120 | 0.007 | -0.080–0.095 | 0.8677 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1502 | 123 | 0.118 | 0.028–0.207 | 0.0103 | 0.064 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1502 | 142 | -0.025 | -0.107–0.058 | 0.5537 | 0.078 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1502 | 116 | -0.095 | -0.189–-0.001 | 0.0470 | 0.060 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1502 | 145 | -0.029 | -0.111–0.054 | 0.5002 | 0.078 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1502 | 116 | -0.017 | -0.107–0.073 | 0.7185 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1502 | 121 | -0.041 | -0.130–0.048 | 0.3638 | 0.067 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1502 | 117 | -0.036 | -0.125–0.054 | 0.4371 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1502 | 134 | -0.007 | -0.096–0.082 | 0.8743 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1502 | 114 | 0.097 | 0.016–0.178 | 0.0189 | 0.062 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1502 | 124 | -0.023 | -0.110–0.064 | 0.6031 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1502 | 115 | -0.044 | -0.139–0.051 | 0.3599 | 0.060 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1502 | 122 | 0.088 | -0.003–0.179 | 0.0585 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1502 | 117 | -0.004 | -0.093–0.085 | 0.9282 | 0.063 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1502 | 137 | 0.014 | -0.068–0.096 | 0.7339 | 0.092 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1502 | 149 | -0.059 | -0.141–0.023 | 0.1593 | 0.083 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1502 | 136 | -0.040 | -0.128–0.048 | 0.3776 | 0.070 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1502 | 120 | 0.034 | -0.059–0.127 | 0.4679 | 0.063 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1502 | 132 | 0.011 | -0.063–0.085 | 0.7718 | 0.086 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1502 | 107 | -0.034 | -0.121–0.052 | 0.4332 | 0.067 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1502 | 127 | -0.009 | -0.097–0.078 | 0.8315 | 0.068 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1502 | 113 | 0.009 | -0.071–0.089 | 0.8220 | 0.072 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1502 | 123 | 0.029 | -0.046–0.103 | 0.4488 | 0.079 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1502 | 137 | -0.042 | -0.127–0.043 | 0.3350 | 0.074 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1502 | 141 | -0.000 | -0.082–0.082 | 0.9955 | 0.077 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1502 | 118 | -0.029 | -0.123–0.065 | 0.5419 | 0.061 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1502 | 142 | -0.025 | -0.107–0.058 | 0.5537 | 0.078 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1502 | 135 | 0.034 | -0.054–0.122 | 0.4524 | 0.070 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1502 | 107 | 0.028 | -0.064–0.121 | 0.5460 | 0.057 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1502 | 120 | 0.004 | -0.085–0.093 | 0.9327 | 0.064 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1502 | 122 | 0.000 | -0.087–0.087 | 0.9929 | 0.066 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1502 | 112 | -0.070 | -0.164–0.024 | 0.1442 | 0.061 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1502 | 132 | -0.137 | -0.203–-0.070 | 0.0001 | 0.091 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1502 | 137 | -0.097 | -0.183–-0.010 | 0.0279 | 0.076 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1502 | 126 | -0.058 | -0.146–0.031 | 0.2016 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1502 | 108 | -0.041 | -0.139–0.056 | 0.4066 | 0.057 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1502 | 135 | 0.059 | -0.029–0.147 | 0.1908 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1502 | 114 | -0.007 | -0.098–0.085 | 0.8873 | 0.061 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1502 | 134 | 0.058 | -0.030–0.146 | 0.1933 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1502 | 133 | -0.074 | -0.162–0.014 | 0.0975 | 0.071 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1502 | 129 | -0.022 | -0.102–0.058 | 0.5895 | 0.092 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1502 | 117 | -0.006 | -0.101–0.088 | 0.8976 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1502 | 130 | -0.025 | -0.115–0.065 | 0.5849 | 0.067 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1502 | 123 | -0.063 | -0.155–0.029 | 0.1781 | 0.063 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1502 | 127 | -0.069 | -0.145–0.007 | 0.0752 | 0.090 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1502 | 122 | 0.066 | -0.025–0.157 | 0.1534 | 0.063 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1502 | 127 | -0.054 | -0.145–0.036 | 0.2398 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1502 | 125 | -0.013 | -0.097–0.072 | 0.7690 | 0.083 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1502 | 126 | -0.035 | -0.117–0.046 | 0.3932 | 0.085 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1502 | 110 | -0.001 | -0.098–0.096 | 0.9844 | 0.058 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1502 | 126 | 0.027 | -0.058–0.113 | 0.5319 | 0.085 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1502 | 132 | -0.036 | -0.125–0.053 | 0.4308 | 0.068 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1502 | 137 | -0.015 | -0.093–0.063 | 0.7083 | 0.097 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1502 | 99 | 0.086 | -0.013–0.185 | 0.0880 | 0.052 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1502 | 102 | 0.151 | 0.057–0.244 | 0.0016 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1502 | 137 | -0.071 | -0.158–0.017 | 0.1146 | 0.070 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1502 | 103 | 0.029 | -0.070–0.128 | 0.5679 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1502 | 127 | 0.049 | -0.041–0.138 | 0.2858 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1502 | 162 | -0.031 | -0.112–0.051 | 0.4594 | 0.083 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1502 | 169 | -0.035 | -0.115–0.045 | 0.3896 | 0.087 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1502 | 126 | 0.002 | -0.089–0.093 | 0.9684 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1502 | 91 | -0.066 | -0.172–0.039 | 0.2188 | 0.048 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1502 | 115 | 0.040 | -0.054–0.134 | 0.4070 | 0.059 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1502 | 133 | -0.046 | -0.135–0.043 | 0.3080 | 0.068 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1502 | 138 | -0.043 | -0.130–0.045 | 0.3398 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1502 | 115 | 0.050 | -0.044–0.145 | 0.2961 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1502 | 125 | -0.011 | -0.102–0.080 | 0.8160 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1502 | 104 | 0.023 | -0.076–0.122 | 0.6486 | 0.054 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1502 | 125 | -0.030 | -0.110–0.050 | 0.4612 | 0.089 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1502 | 138 | 0.029 | -0.057–0.116 | 0.5089 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1502 | 137 | 0.074 | -0.012–0.160 | 0.0909 | 0.071 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1502 | 105 | -0.032 | -0.122–0.058 | 0.4834 | 0.070 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1502 | 127 | -0.012 | -0.095–0.071 | 0.7772 | 0.086 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1502 | 118 | -0.029 | -0.123–0.065 | 0.5419 | 0.061 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1502 | 148 | 0.003 | -0.076–0.081 | 0.9436 | 0.098 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1502 | 133 | -0.081 | -0.169–0.007 | 0.0720 | 0.069 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1502 | 127 | -0.026 | -0.106–0.054 | 0.5241 | 0.090 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1502 | 125 | -0.020 | -0.111–0.072 | 0.6747 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1502 | 108 | 0.030 | -0.067–0.127 | 0.5396 | 0.056 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1502 | 123 | 0.061 | -0.030–0.151 | 0.1886 | 0.063 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1502 | 120 | -0.023 | -0.116–0.070 | 0.6320 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1502 | 126 | 0.019 | -0.071–0.110 | 0.6782 | 0.065 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1502 | 122 | -0.041 | -0.134–0.051 | 0.3842 | 0.063 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1502 | 132 | -0.034 | -0.123–0.055 | 0.4585 | 0.068 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1502 | 150 | -0.044 | -0.128–0.041 | 0.3103 | 0.077 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1502 | 131 | -0.013 | -0.102–0.077 | 0.7807 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1502 | 145 | -0.047 | -0.133–0.039 | 0.2814 | 0.075 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1502 | 102 | 0.024 | -0.075–0.124 | 0.6319 | 0.053 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1502 | 118 | 0.116 | 0.026–0.206 | 0.0116 | 0.061 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1502 | 137 | 0.001 | -0.087–0.089 | 0.9811 | 0.071 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1502 | 140 | 0.044 | -0.042–0.130 | 0.3162 | 0.072 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1502 | 102 | 0.003 | -0.097–0.103 | 0.9484 | 0.053 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1502 | 133 | -0.006 | -0.086–0.074 | 0.8838 | 0.095 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1502 | 139 | -0.007 | -0.094–0.080 | 0.8743 | 0.071 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1502 | 125 | 0.024 | -0.067–0.115 | 0.6032 | 0.064 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1502 | 115 | 0.026 | -0.064–0.115 | 0.5782 | 0.077 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1502 | 135 | -0.047 | -0.125–0.031 | 0.2343 | 0.091 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1502 | 105 | 0.035 | -0.063–0.134 | 0.4834 | 0.055 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1502 | 132 | 0.003 | -0.080–0.085 | 0.9513 | 0.088 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1502 | 124 | -0.011 | -0.103–0.081 | 0.8164 | 0.064 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1502 | 115 | 0.004 | -0.082–0.090 | 0.9344 | 0.083 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1502 | 126 | 0.024 | -0.067–0.115 | 0.6091 | 0.066 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1502 | 134 | -0.001 | -0.090–0.087 | 0.9774 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1502 | 130 | -0.092 | -0.182–-0.003 | 0.0434 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1502 | 134 | -0.033 | -0.110–0.045 | 0.4064 | 0.095 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1502 | 111 | -0.045 | -0.141–0.052 | 0.3641 | 0.057 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1502 | 122 | 0.066 | -0.025–0.157 | 0.1534 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1502 | 126 | -0.093 | -0.171–-0.016 | 0.0184 | 0.082 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1502 | 127 | -0.046 | -0.126–0.034 | 0.2567 | 0.086 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1502 | 121 | 0.012 | -0.081–0.104 | 0.8064 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1502 | 143 | -0.016 | -0.095–0.063 | 0.6884 | 0.095 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1502 | 128 | 0.032 | -0.059–0.122 | 0.4903 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1502 | 100 | -0.015 | -0.105–0.076 | 0.7511 | 0.073 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1502 | 113 | -0.057 | -0.149–0.036 | 0.2325 | 0.061 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1502 | 130 | -0.011 | -0.096–0.074 | 0.7963 | 0.071 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1502 | 151 | 0.063 | -0.012–0.138 | 0.1007 | 0.083 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1502 | 127 | 0.058 | -0.024–0.139 | 0.1673 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1502 | 126 | -0.006 | -0.092–0.080 | 0.8989 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1502 | 176 | -0.059 | -0.135–0.017 | 0.1255 | 0.100 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1502 | 84 | -0.043 | -0.149–0.063 | 0.4242 | 0.045 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1502 | 113 | -0.066 | -0.159–0.027 | 0.1644 | 0.061 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1502 | 115 | 0.073 | -0.011–0.157 | 0.0888 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1502 | 106 | -0.002 | -0.095–0.091 | 0.9645 | 0.057 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1502 | 102 | -0.005 | -0.100–0.089 | 0.9098 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1502 | 159 | 0.036 | -0.039–0.112 | 0.3419 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1502 | 130 | -0.036 | -0.126–0.054 | 0.4297 | 0.067 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1502 | 111 | -0.006 | -0.102–0.091 | 0.9056 | 0.057 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1502 | 127 | -0.054 | -0.145–0.036 | 0.2398 | 0.065 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1502 | 129 | -0.056 | -0.133–0.021 | 0.1537 | 0.091 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1502 | 130 | -0.025 | -0.115–0.065 | 0.5849 | 0.067 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1502 | 124 | 0.011 | -0.080–0.103 | 0.8057 | 0.064 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1502 | 119 | 0.004 | -0.083–0.091 | 0.9272 | 0.079 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1502 | 139 | -0.056 | -0.132–0.021 | 0.1526 | 0.093 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1502 | 109 | 0.004 | -0.093–0.102 | 0.9347 | 0.057 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1502 | 132 | 0.069 | -0.017–0.155 | 0.1154 | 0.090 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1502 | 122 | -0.082 | -0.174–0.010 | 0.0792 | 0.063 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1502 | 130 | 0.010 | -0.072–0.091 | 0.8196 | 0.093 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1502 | 109 | 0.060 | -0.015–0.134 | 0.1167 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1502 | 158 | -0.090 | -0.165–-0.014 | 0.0195 | 0.111 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1502 | 92 | -0.149 | -0.250–-0.048 | 0.0038 | 0.057 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1502 | 137 | -0.012 | -0.087–0.063 | 0.7478 | 0.091 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1502 | 110 | 0.111 | 0.044–0.177 | 0.0011 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1502 | 134 | -0.010 | -0.086–0.066 | 0.7952 | 0.088 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1502 | 134 | 0.064 | -0.004–0.131 | 0.0649 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1502 | 121 | -0.002 | -0.080–0.076 | 0.9629 | 0.078 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1502 | 127 | -0.033 | -0.112–0.046 | 0.4164 | 0.083 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1502 | 128 | 0.021 | -0.054–0.095 | 0.5877 | 0.083 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1502 | 130 | 0.049 | -0.021–0.120 | 0.1692 | 0.084 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1502 | 122 | -0.009 | -0.087–0.070 | 0.8281 | 0.079 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1502 | 99 | -0.016 | -0.118–0.086 | 0.7568 | 0.052 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1502 | 116 | -0.068 | -0.163–0.026 | 0.1562 | 0.060 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1502 | 114 | 0.017 | -0.078–0.112 | 0.7293 | 0.059 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1502 | 131 | -0.043 | -0.120–0.034 | 0.2749 | 0.093 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1502 | 151 | 0.078 | -0.004–0.160 | 0.0631 | 0.078 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1502 | 125 | -0.020 | -0.111–0.072 | 0.6747 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1502 | 112 | -0.061 | -0.146–0.024 | 0.1569 | 0.074 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1502 | 120 | -0.093 | -0.171–-0.015 | 0.0188 | 0.081 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1502 | 110 | -0.011 | -0.108–0.086 | 0.8277 | 0.058 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1502 | 145 | 0.010 | -0.070–0.090 | 0.8066 | 0.097 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1502 | 144 | 0.004 | -0.082–0.090 | 0.9215 | 0.075 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1502 | 135 | -0.027 | -0.104–0.051 | 0.4996 | 0.096 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1502 | 129 | -0.021 | -0.111–0.070 | 0.6544 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1502 | 138 | -0.011 | -0.098–0.077 | 0.8103 | 0.071 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1502 | 124 | 0.011 | -0.080–0.103 | 0.8057 | 0.064 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1502 | 123 | -0.037 | -0.129–0.055 | 0.4344 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1502 | 128 | 0.052 | -0.037–0.141 | 0.2501 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1502 | 118 | 0.033 | -0.060–0.126 | 0.4876 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1502 | 122 | -0.014 | -0.107–0.078 | 0.7613 | 0.063 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1502 | 131 | -0.029 | -0.119–0.060 | 0.5195 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1502 | 107 | -0.004 | -0.102–0.094 | 0.9333 | 0.055 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1502 | 119 | 0.000 | -0.093–0.094 | 0.9949 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1502 | 131 | 0.037 | -0.051–0.126 | 0.4066 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1502 | 132 | -0.017 | -0.106–0.072 | 0.7062 | 0.068 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1502 | 127 | 0.036 | -0.054–0.127 | 0.4309 | 0.066 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1502 | 120 | -0.050 | -0.143–0.043 | 0.2939 | 0.062 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1502 | 111 | -0.074 | -0.170–0.023 | 0.1334 | 0.057 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1502 | 120 | -0.091 | -0.166–-0.015 | 0.0183 | 0.085 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1502 | 134 | 0.015 | -0.073–0.103 | 0.7367 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1502 | 102 | 0.035 | -0.064–0.134 | 0.4915 | 0.053 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1502 | 132 | 0.053 | -0.033–0.138 | 0.2279 | 0.088 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1502 | 100 | 0.062 | -0.035–0.159 | 0.2117 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1502 | 134 | 0.014 | -0.075–0.102 | 0.7633 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1502 | 145 | -0.013 | -0.091–0.065 | 0.7457 | 0.096 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1502 | 146 | 0.072 | -0.012–0.157 | 0.0930 | 0.076 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1502 | 131 | -0.010 | -0.090–0.070 | 0.8132 | 0.093 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1502 | 100 | -0.020 | -0.112–0.073 | 0.6775 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1502 | 123 | 0.027 | -0.059–0.114 | 0.5373 | 0.083 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1502 | 116 | -0.007 | -0.094–0.080 | 0.8733 | 0.079 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1502 | 174 | 0.054 | -0.021–0.130 | 0.1572 | 0.116 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1502 | 139 | -0.038 | -0.117–0.040 | 0.3346 | 0.092 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1502 | 159 | -0.063 | -0.135–0.008 | 0.0839 | 0.103 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1502 | 125 | 0.048 | -0.039–0.135 | 0.2834 | 0.085 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1502 | 139 | 0.073 | -0.011–0.157 | 0.0906 | 0.094 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1502 | 100 | -0.020 | -0.112–0.073 | 0.6775 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1502 | 104 | -0.032 | -0.121–0.058 | 0.4891 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1502 | 132 | 0.011 | -0.072–0.094 | 0.7975 | 0.089 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1502 | 91 | -0.071 | -0.162–0.020 | 0.1283 | 0.063 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1502 | 183 | 0.069 | -0.007–0.145 | 0.0740 | 0.094 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1502 | 730 | 0.031 | -0.020–0.081 | 0.2342 | 0.265 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1502 | 513 | 0.011 | -0.039–0.061 | 0.6670 | 0.273 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1502 | 136 | 0.076 | -0.001–0.154 | 0.0535 | 0.074 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1502 | 237 | 0.058 | -0.010–0.126 | 0.0949 | 0.121 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1502 | 793 | 0.011 | -0.040–0.061 | 0.6726 | 0.266 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1502 | 976 | -0.038 | -0.090–0.015 | 0.1619 | 0.247 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1502 | 263 | 0.074 | 0.009–0.140 | 0.0263 | 0.134 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1502 | 693 | -0.038 | -0.089–0.012 | 0.1361 | 0.269 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1502 | 572 | -0.014 | -0.063–0.035 | 0.5710 | 0.297 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1502 | 230 | 0.084 | 0.016–0.153 | 0.0158 | 0.118 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1502 | 269 | 0.037 | -0.028–0.102 | 0.2682 | 0.137 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
