# Synthetic — Validation — null, N = 2,000, odds ratio 1.0 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 2000 subjects: 1536 development, 464 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `a1c5d6d4bceacf1af09eed0d36c81e275dabf20ed8a691de86a12e3b99c7db2f` ({"salt_sha256": "19287501b03b53760b7a0eac16e4af0438c9bde072eec135d455423dcaaa3cb9", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "dd5e8a6df2ec8ec1fc222aa22443f7055f6f66a73d8cbfbad619ad3b18f37e14"})
- analysis code `494dae55f6a48ddf1c97767f4f82d77adf00c78f1bdbab2488c65c423b7b012c`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 1536 | 1.000 | 0.309 | 0.983 | 0.883–1.080 | 0.5974 | 0.7275 | no | 0.288 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 1536 | 1.000 | 0.517 | 1.025 | 0.956–1.098 | 0.2847 | 0.7275 | no | 0.221 |
| children | 1536 | 1.000 | 0.310 | 1.002 | 0.881–1.131 | 0.5844 | 0.7275 | no | 0.251 |
| intellect | 1536 | 1.000 | 0.294 | 1.073 | 0.959–1.189 | 0.1129 | 0.6209 | no | 0.284 |
| health | 1536 | 1.000 | 0.505 | 1.001 | 0.949–1.059 | 0.6613 | 0.7275 | no | 0.260 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 1536 | 1.000 | 0.312 | 1.038 | 0.929–1.152 | 0.2747 | 0.7275 | no | 0.256 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 1536 | 1.000 | 0.287 | 1.009 | 0.892–1.117 | 0.5275 | 0.7275 | no | 0.297 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 1536 | 1.000 | 0.510 | 1.005 | 0.928–1.077 | 0.5744 | 0.7275 | no | 0.221 |
| gains | 1536 | 1.000 | 0.309 | 1.027 | 0.922–1.130 | 0.3616 | 0.7275 | no | 0.281 |
| foreign | 1536 | 1.000 | 0.313 | 0.955 | 0.866–1.056 | 0.8851 | 0.8851 | no | 0.286 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 1536 | 1.000 | 0.294 | 1.089 | 0.960–1.211 | 0.0689 | 0.6209 | no | 0.277 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1536 | 1.000 | 8 | 9.51 | 8 | 0.3011 | 0.495 | 0.497 | 0.8587 |
| mother_home | 1536 | 1.000 | 8 | 11.66 | 8 | 0.1669 | 0.475 | 0.493 | 0.1352 |
| children | 1536 | 1.000 | 7 | 15.46 | 7 | 0.0306 | 0.495 | 0.523 | 0.0256 |
| intellect | 1536 | 1.000 | 8 | 7.63 | 8 | 0.4705 | 0.495 | 0.511 | 0.3720 |
| health | 1536 | 1.000 | 8 | 5.04 | 8 | 0.7532 | 0.499 | 0.495 | 0.7620 |
| marriage | 1536 | 1.000 | 8 | 7.06 | 8 | 0.5299 | 0.519 | 0.519 | 0.9922 |
| father | 1536 | 1.000 | 7 | 7.91 | 7 | 0.3405 | 0.511 | 0.502 | 0.5429 |
| career | 1536 | 1.000 | 8 | 3.69 | 8 | 0.8839 | 0.483 | 0.464 | 0.2175 |
| gains | 1536 | 1.000 | 8 | 8.68 | 8 | 0.3698 | 0.495 | 0.489 | 0.6437 |
| foreign | 1536 | 1.000 | 7 | 6.40 | 7 | 0.4935 | 0.501 | 0.508 | 0.6077 |
| reputation | 1536 | 1.000 | 8 | 11.83 | 8 | 0.1590 | 0.495 | 0.521 | 0.1493 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1536 | 1.000 | 75554 | 475 | 0.934 | 0.857 | 0.6219 | -0.156 (-0.497, 0.186) |
| mother_home | 1536 | 1.000 | 65244 | 794 | 0.942 | 0.818 | 0.7015 | -0.203 (-0.479, 0.073) |
| children | 1536 | 1.000 | 75272 | 476 | 0.901 | 0.913 | 0.4677 | -0.091 (-0.383, 0.200) |
| intellect | 1536 | 1.000 | 75917 | 452 | 0.942 | 1.020 | 0.3085 | 0.020 (-0.378, 0.417) |
| health | 1536 | 1.000 | 65383 | 776 | 0.940 | 1.055 | 0.1940 | 0.054 (-0.252, 0.361) |
| marriage | 1536 | 1.000 | 75250 | 479 | 0.941 | 1.137 | 0.2239 | 0.129 (-0.275, 0.533) |
| father | 1536 | 1.000 | 76054 | 441 | 0.881 | 0.863 | 0.7015 | -0.149 (-0.422, 0.125) |
| career | 1536 | 1.000 | 65326 | 784 | 0.955 | 1.380 | 0.0448 | 0.326 (-0.067, 0.719) |
| gains | 1536 | 1.000 | 75554 | 475 | 0.873 | 1.086 | 0.1891 | 0.083 (-0.196, 0.363) |
| foreign | 1536 | 1.000 | 74320 | 481 | 0.951 | 1.174 | 0.3035 | 0.162 (-0.287, 0.611) |
| reputation | 1536 | 1.000 | 75917 | 452 | 0.889 | 1.053 | 0.3731 | 0.052 (-0.248, 0.353) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 1536 | 1.000 | 0.028 | 0.039 | 2 | 33 | not allowed |
| mother_home | 1536 | 1.000 | 0.058 | 0.038 | 6 | 1 | not allowed |
| children | 1536 | 1.000 | 0.025 | 0.031 | 4 | 1 | not allowed |
| intellect | 1536 | 1.000 | 0.017 | 0.055 | 2 | 55 | not allowed |
| health | 1536 | 1.000 | 0.040 | 0.021 | 2 | 113 | not allowed |
| marriage | 1536 | 1.000 | 0.041 | 0.026 | 2 | 26 | not allowed |
| father | 1536 | 1.000 | 0.018 | 0.006 | 3 | 0 | not allowed |
| career | 1536 | 1.000 | 0.075 | 0.059 | 2 | 68 | not allowed |
| gains | 1536 | 1.000 | 0.035 | 0.021 | 2 | 64 | not allowed |
| foreign | 1536 | 1.000 | 0.015 | 0.042 | 3 | 1 | not allowed |
| reputation | 1536 | 1.000 | 0.026 | 0.040 | 6 | 0 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 1536 | 1.000 | 569 | 0.288 | 0.520 |
| mother_home | 1536 | 1.000 | 470 | 0.221 | 0.440 |
| children | 1536 | 1.000 | 441 | 0.251 | 0.474 |
| intellect | 1536 | 1.000 | 494 | 0.284 | 0.515 |
| health | 1536 | 1.000 | 639 | 0.260 | 0.490 |
| marriage | 1536 | 1.000 | 451 | 0.256 | 0.481 |
| father | 1536 | 1.000 | 542 | 0.297 | 0.530 |
| career | 1536 | 1.000 | 470 | 0.221 | 0.439 |
| gains | 1536 | 1.000 | 526 | 0.281 | 0.512 |
| foreign | 1536 | 1.000 | 582 | 0.286 | 0.518 |
| reputation | 1536 | 1.000 | 471 | 0.277 | 0.506 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 360 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 1536 | 134 | -0.014 | -0.102–0.075 | 0.7588 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 1536 | 130 | 0.014 | -0.076–0.104 | 0.7626 | 0.068 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 1536 | 113 | -0.026 | -0.121–0.070 | 0.6006 | 0.059 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 1536 | 137 | 0.057 | -0.027–0.141 | 0.1853 | 0.092 | not_testable_yet (under-powered) |
| `place.jupiter_h2` | 1536 | 125 | 0.037 | -0.055–0.128 | 0.4317 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 1536 | 128 | 0.048 | -0.042–0.138 | 0.2928 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 1536 | 126 | 0.018 | -0.068–0.103 | 0.6859 | 0.085 | not_testable_yet (under-powered) |
| `place.jupiter_h5` | 1536 | 151 | 0.016 | -0.062–0.095 | 0.6860 | 0.100 | not_testable_yet (under-powered) |
| `place.jupiter_h6` | 1536 | 125 | -0.036 | -0.127–0.055 | 0.4378 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 1536 | 122 | -0.000 | -0.086–0.085 | 0.9926 | 0.082 | not_testable_yet (under-powered) |
| `place.jupiter_h8` | 1536 | 134 | 0.027 | -0.061–0.115 | 0.5498 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 1536 | 111 | 0.041 | -0.051–0.133 | 0.3804 | 0.075 | not_testable_yet (under-powered) |
| `place.jupiter_in_aquarius` | 1536 | 121 | -0.013 | -0.102–0.075 | 0.7687 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_aries` | 1536 | 124 | 0.014 | -0.073–0.100 | 0.7587 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_in_cancer` | 1536 | 138 | 0.003 | -0.080–0.086 | 0.9478 | 0.075 | not_testable_yet (under-powered) |
| `place.jupiter_in_capricorn` | 1536 | 155 | 0.044 | -0.032–0.121 | 0.2565 | 0.084 | not_testable_yet (under-powered) |
| `place.jupiter_in_gemini` | 1536 | 130 | 0.005 | -0.080–0.090 | 0.9071 | 0.070 | not_testable_yet (under-powered) |
| `place.jupiter_in_leo` | 1536 | 133 | -0.019 | -0.105–0.066 | 0.6543 | 0.072 | not_testable_yet (under-powered) |
| `place.jupiter_in_libra` | 1536 | 121 | -0.049 | -0.139–0.041 | 0.2854 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_pisces` | 1536 | 123 | -0.007 | -0.095–0.081 | 0.8748 | 0.066 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 1536 | 124 | -0.039 | -0.128–0.050 | 0.3888 | 0.067 | not_testable_yet (under-powered) |
| `place.jupiter_in_scorpio` | 1536 | 134 | 0.065 | -0.015–0.145 | 0.1114 | 0.072 | not_testable_yet (under-powered) |
| `place.jupiter_in_taurus` | 1536 | 120 | -0.026 | -0.115–0.064 | 0.5764 | 0.065 | not_testable_yet (under-powered) |
| `place.jupiter_in_virgo` | 1536 | 113 | 0.007 | -0.083–0.098 | 0.8735 | 0.060 | not_testable_yet (under-powered) |
| `place.ketu_h1` | 1536 | 139 | -0.018 | -0.105–0.070 | 0.6923 | 0.072 | not_testable_yet (under-powered) |
| `place.ketu_h10` | 1536 | 131 | -0.099 | -0.187–-0.011 | 0.0282 | 0.068 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 1536 | 124 | -0.003 | -0.094–0.089 | 0.9564 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 1536 | 133 | -0.047 | -0.126–0.033 | 0.2507 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_h2` | 1536 | 118 | -0.002 | -0.096–0.092 | 0.9650 | 0.062 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 1536 | 100 | -0.033 | -0.134–0.069 | 0.5289 | 0.053 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 1536 | 136 | 0.121 | 0.034–0.207 | 0.0062 | 0.093 | not_testable_yet (under-powered) |
| `place.ketu_h5` | 1536 | 128 | 0.062 | -0.024–0.149 | 0.1586 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_h6` | 1536 | 141 | 0.092 | 0.007–0.177 | 0.0349 | 0.074 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 1536 | 133 | 0.062 | -0.024–0.147 | 0.1555 | 0.090 | not_testable_yet (under-powered) |
| `place.ketu_h8` | 1536 | 129 | -0.027 | -0.117–0.063 | 0.5592 | 0.067 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 1536 | 124 | 0.107 | 0.017–0.197 | 0.0199 | 0.085 | not_testable_yet (under-powered) |
| `place.ketu_in_aquarius` | 1536 | 191 | -0.005 | -0.075–0.065 | 0.8920 | 0.123 | not_testable_yet (under-powered) |
| `place.ketu_in_aries` | 1536 | 94 | 0.029 | -0.070–0.128 | 0.5641 | 0.065 | not_testable_yet (under-powered) |
| `place.ketu_in_cancer` | 1536 | 133 | -0.079 | -0.156–-0.003 | 0.0422 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 1536 | 149 | -0.042 | -0.118–0.034 | 0.2766 | 0.097 | not_testable_yet (under-powered) |
| `place.ketu_in_gemini` | 1536 | 118 | 0.037 | -0.052–0.126 | 0.4143 | 0.080 | not_testable_yet (under-powered) |
| `place.ketu_in_leo` | 1536 | 103 | 0.112 | 0.014–0.210 | 0.0256 | 0.071 | not_testable_yet (under-powered) |
| `place.ketu_in_libra` | 1536 | 146 | 0.017 | -0.063–0.097 | 0.6724 | 0.097 | not_testable_yet (under-powered) |
| `place.ketu_in_pisces` | 1536 | 146 | -0.036 | -0.113–0.041 | 0.3625 | 0.095 | not_testable_yet (under-powered) |
| `place.ketu_in_sagittarius` | 1536 | 132 | -0.053 | -0.132–0.027 | 0.1934 | 0.087 | not_testable_yet (under-powered) |
| `place.ketu_in_scorpio` | 1536 | 91 | 0.041 | -0.060–0.142 | 0.4270 | 0.063 | not_testable_yet (under-powered) |
| `place.ketu_in_taurus` | 1536 | 113 | -0.013 | -0.101–0.075 | 0.7679 | 0.076 | not_testable_yet (under-powered) |
| `place.ketu_in_virgo` | 1536 | 120 | 0.049 | -0.040–0.138 | 0.2810 | 0.081 | not_testable_yet (under-powered) |
| `place.l10_h1` | 1536 | 123 | -0.045 | -0.127–0.038 | 0.2906 | 0.078 | not_testable_yet (under-powered) |
| `place.l10_h10` | 1536 | 134 | 0.054 | -0.034–0.142 | 0.2293 | 0.070 | not_testable_yet (under-powered) |
| `place.l10_h11` | 1536 | 114 | -0.011 | -0.107–0.084 | 0.8172 | 0.060 | not_testable_yet (under-powered) |
| `place.l10_h12` | 1536 | 132 | 0.030 | -0.053–0.113 | 0.4785 | 0.071 | not_testable_yet (under-powered) |
| `place.l10_h2` | 1536 | 126 | 0.041 | -0.050–0.131 | 0.3814 | 0.066 | not_testable_yet (under-powered) |
| `place.l10_h3` | 1536 | 103 | -0.016 | -0.116–0.084 | 0.7483 | 0.054 | not_testable_yet (under-powered) |
| `place.l10_h4` | 1536 | 136 | 0.044 | -0.037–0.124 | 0.2868 | 0.074 | not_testable_yet (under-powered) |
| `place.l10_h5` | 1536 | 139 | -0.058 | -0.143–0.027 | 0.1824 | 0.076 | not_testable_yet (under-powered) |
| `place.l10_h6` | 1536 | 125 | 0.030 | -0.046–0.105 | 0.4376 | 0.078 | not_testable_yet (under-powered) |
| `place.l10_h7` | 1536 | 132 | -0.014 | -0.100–0.071 | 0.7448 | 0.071 | not_testable_yet (under-powered) |
| `place.l10_h8` | 1536 | 137 | -0.013 | -0.090–0.063 | 0.7357 | 0.088 | not_testable_yet (under-powered) |
| `place.l10_h9` | 1536 | 135 | -0.051 | -0.137–0.035 | 0.2415 | 0.073 | not_testable_yet (under-powered) |
| `place.l11_h1` | 1536 | 132 | -0.032 | -0.111–0.047 | 0.4286 | 0.084 | not_testable_yet (under-powered) |
| `place.l11_h10` | 1536 | 122 | -0.038 | -0.130–0.054 | 0.4197 | 0.064 | not_testable_yet (under-powered) |
| `place.l11_h11` | 1536 | 109 | 0.023 | -0.074–0.121 | 0.6377 | 0.057 | not_testable_yet (under-powered) |
| `place.l11_h12` | 1536 | 125 | 0.037 | -0.048–0.122 | 0.3972 | 0.067 | not_testable_yet (under-powered) |
| `place.l11_h2` | 1536 | 151 | -0.008 | -0.092–0.076 | 0.8541 | 0.078 | not_testable_yet (under-powered) |
| `place.l11_h3` | 1536 | 121 | 0.020 | -0.073–0.113 | 0.6709 | 0.063 | not_testable_yet (under-powered) |
| `place.l11_h4` | 1536 | 116 | -0.030 | -0.121–0.060 | 0.5121 | 0.063 | not_testable_yet (under-powered) |
| `place.l11_h5` | 1536 | 117 | 0.020 | -0.069–0.108 | 0.6602 | 0.063 | not_testable_yet (under-powered) |
| `place.l11_h6` | 1536 | 141 | -0.075 | -0.155–0.004 | 0.0632 | 0.092 | not_testable_yet (under-powered) |
| `place.l11_h7` | 1536 | 153 | 0.033 | -0.045–0.110 | 0.4105 | 0.083 | not_testable_yet (under-powered) |
| `place.l11_h8` | 1536 | 118 | 0.053 | -0.022–0.128 | 0.1687 | 0.073 | not_testable_yet (under-powered) |
| `place.l11_h9` | 1536 | 131 | 0.011 | -0.074–0.095 | 0.8035 | 0.070 | not_testable_yet (under-powered) |
| `place.l12_h1` | 1536 | 118 | -0.005 | -0.095–0.084 | 0.9053 | 0.063 | not_testable_yet (under-powered) |
| `place.l12_h10` | 1536 | 129 | 0.064 | -0.018–0.146 | 0.1241 | 0.069 | not_testable_yet (under-powered) |
| `place.l12_h11` | 1536 | 107 | -0.050 | -0.146–0.045 | 0.3029 | 0.057 | not_testable_yet (under-powered) |
| `place.l12_h12` | 1536 | 112 | 0.019 | -0.072–0.109 | 0.6873 | 0.076 | not_testable_yet (under-powered) |
| `place.l12_h2` | 1536 | 133 | 0.008 | -0.076–0.092 | 0.8512 | 0.072 | not_testable_yet (under-powered) |
| `place.l12_h3` | 1536 | 142 | 0.055 | -0.024–0.134 | 0.1730 | 0.077 | not_testable_yet (under-powered) |
| `place.l12_h4` | 1536 | 120 | -0.017 | -0.110–0.076 | 0.7192 | 0.062 | not_testable_yet (under-powered) |
| `place.l12_h5` | 1536 | 132 | -0.002 | -0.091–0.087 | 0.9659 | 0.068 | not_testable_yet (under-powered) |
| `place.l12_h6` | 1536 | 116 | 0.035 | -0.053–0.122 | 0.4379 | 0.062 | not_testable_yet (under-powered) |
| `place.l12_h7` | 1536 | 133 | 0.092 | 0.005–0.179 | 0.0376 | 0.069 | not_testable_yet (under-powered) |
| `place.l12_h8` | 1536 | 161 | -0.068 | -0.148–0.011 | 0.0927 | 0.089 | not_testable_yet (under-powered) |
| `place.l12_h9` | 1536 | 133 | -0.047 | -0.126–0.033 | 0.2507 | 0.087 | not_testable_yet (under-powered) |
| `place.l1_h1` | 1536 | 120 | 0.040 | -0.053–0.132 | 0.4039 | 0.063 | not_testable_yet (under-powered) |
| `place.l1_h10` | 1536 | 133 | 0.020 | -0.055–0.094 | 0.6057 | 0.084 | not_testable_yet (under-powered) |
| `place.l1_h11` | 1536 | 112 | -0.007 | -0.090–0.076 | 0.8687 | 0.069 | not_testable_yet (under-powered) |
| `place.l1_h12` | 1536 | 138 | -0.078 | -0.163–0.008 | 0.0764 | 0.075 | not_testable_yet (under-powered) |
| `place.l1_h2` | 1536 | 115 | -0.028 | -0.112–0.056 | 0.5112 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h3` | 1536 | 114 | -0.021 | -0.105–0.063 | 0.6194 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h4` | 1536 | 143 | 0.004 | -0.077–0.085 | 0.9284 | 0.079 | not_testable_yet (under-powered) |
| `place.l1_h5` | 1536 | 139 | 0.069 | -0.009–0.148 | 0.0839 | 0.075 | not_testable_yet (under-powered) |
| `place.l1_h6` | 1536 | 134 | -0.030 | -0.119–0.058 | 0.5033 | 0.070 | not_testable_yet (under-powered) |
| `place.l1_h7` | 1536 | 140 | -0.060 | -0.145–0.024 | 0.1626 | 0.076 | not_testable_yet (under-powered) |
| `place.l1_h8` | 1536 | 137 | 0.054 | -0.033–0.142 | 0.2218 | 0.071 | not_testable_yet (under-powered) |
| `place.l1_h9` | 1536 | 111 | 0.029 | -0.061–0.119 | 0.5237 | 0.059 | not_testable_yet (under-powered) |
| `place.l2_h1` | 1536 | 126 | 0.015 | -0.062–0.091 | 0.7111 | 0.079 | not_testable_yet (under-powered) |
| `place.l2_h10` | 1536 | 116 | -0.030 | -0.124–0.065 | 0.5353 | 0.061 | not_testable_yet (under-powered) |
| `place.l2_h11` | 1536 | 115 | -0.054 | -0.148–0.041 | 0.2679 | 0.060 | not_testable_yet (under-powered) |
| `place.l2_h12` | 1536 | 123 | 0.031 | -0.055–0.117 | 0.4777 | 0.066 | not_testable_yet (under-powered) |
| `place.l2_h2` | 1536 | 134 | 0.038 | -0.051–0.126 | 0.4033 | 0.070 | not_testable_yet (under-powered) |
| `place.l2_h3` | 1536 | 138 | -0.027 | -0.115–0.060 | 0.5394 | 0.072 | not_testable_yet (under-powered) |
| `place.l2_h4` | 1536 | 112 | -0.015 | -0.107–0.076 | 0.7425 | 0.060 | not_testable_yet (under-powered) |
| `place.l2_h5` | 1536 | 150 | 0.077 | 0.002–0.153 | 0.0451 | 0.081 | not_testable_yet (under-powered) |
| `place.l2_h6` | 1536 | 127 | 0.034 | -0.041–0.108 | 0.3765 | 0.079 | not_testable_yet (under-powered) |
| `place.l2_h7` | 1536 | 129 | -0.023 | -0.110–0.063 | 0.6000 | 0.070 | not_testable_yet (under-powered) |
| `place.l2_h8` | 1536 | 145 | -0.005 | -0.079–0.069 | 0.8884 | 0.094 | not_testable_yet (under-powered) |
| `place.l2_h9` | 1536 | 121 | 0.016 | -0.071–0.104 | 0.7128 | 0.065 | not_testable_yet (under-powered) |
| `place.l3_h1` | 1536 | 130 | -0.003 | -0.080–0.074 | 0.9412 | 0.082 | not_testable_yet (under-powered) |
| `place.l3_h10` | 1536 | 124 | -0.099 | -0.190–-0.008 | 0.0323 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h11` | 1536 | 124 | -0.090 | -0.181–0.001 | 0.0515 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h12` | 1536 | 117 | 0.060 | -0.026–0.146 | 0.1737 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h2` | 1536 | 130 | 0.056 | -0.033–0.145 | 0.2198 | 0.068 | not_testable_yet (under-powered) |
| `place.l3_h3` | 1536 | 118 | 0.035 | -0.059–0.128 | 0.4685 | 0.062 | not_testable_yet (under-powered) |
| `place.l3_h4` | 1536 | 118 | 0.059 | -0.026–0.143 | 0.1730 | 0.064 | not_testable_yet (under-powered) |
| `place.l3_h5` | 1536 | 137 | 0.008 | -0.075–0.091 | 0.8491 | 0.074 | not_testable_yet (under-powered) |
| `place.l3_h6` | 1536 | 131 | 0.041 | -0.032–0.114 | 0.2715 | 0.082 | not_testable_yet (under-powered) |
| `place.l3_h7` | 1536 | 123 | 0.108 | 0.028–0.188 | 0.0081 | 0.066 | not_testable_yet (under-powered) |
| `place.l3_h8` | 1536 | 142 | -0.089 | -0.169–-0.009 | 0.0301 | 0.093 | not_testable_yet (under-powered) |
| `place.l3_h9` | 1536 | 142 | -0.030 | -0.114–0.053 | 0.4756 | 0.077 | not_testable_yet (under-powered) |
| `place.l4_h1` | 1536 | 113 | 0.053 | -0.034–0.139 | 0.2329 | 0.061 | not_testable_yet (under-powered) |
| `place.l4_h10` | 1536 | 156 | -0.021 | -0.100–0.058 | 0.6078 | 0.086 | not_testable_yet (under-powered) |
| `place.l4_h11` | 1536 | 114 | -0.018 | -0.109–0.073 | 0.6942 | 0.062 | not_testable_yet (under-powered) |
| `place.l4_h12` | 1536 | 147 | 0.090 | 0.007–0.173 | 0.0342 | 0.076 | not_testable_yet (under-powered) |
| `place.l4_h2` | 1536 | 148 | -0.034 | -0.116–0.047 | 0.4107 | 0.082 | not_testable_yet (under-powered) |
| `place.l4_h3` | 1536 | 124 | -0.031 | -0.120–0.057 | 0.4841 | 0.067 | not_testable_yet (under-powered) |
| `place.l4_h4` | 1536 | 119 | 0.020 | -0.068–0.108 | 0.6542 | 0.081 | not_testable_yet (under-powered) |
| `place.l4_h5` | 1536 | 131 | 0.004 | -0.086–0.093 | 0.9373 | 0.068 | not_testable_yet (under-powered) |
| `place.l4_h6` | 1536 | 115 | -0.017 | -0.107–0.073 | 0.7113 | 0.062 | not_testable_yet (under-powered) |
| `place.l4_h7` | 1536 | 121 | -0.046 | -0.139–0.046 | 0.3262 | 0.063 | not_testable_yet (under-powered) |
| `place.l4_h8` | 1536 | 128 | -0.064 | -0.152–0.024 | 0.1545 | 0.070 | not_testable_yet (under-powered) |
| `place.l4_h9` | 1536 | 120 | 0.010 | -0.083–0.103 | 0.8326 | 0.062 | not_testable_yet (under-powered) |
| `place.l5_h1` | 1536 | 132 | 0.069 | -0.011–0.150 | 0.0913 | 0.071 | not_testable_yet (under-powered) |
| `place.l5_h10` | 1536 | 142 | -0.010 | -0.092–0.072 | 0.8133 | 0.077 | not_testable_yet (under-powered) |
| `place.l5_h11` | 1536 | 122 | -0.046 | -0.136–0.044 | 0.3177 | 0.066 | not_testable_yet (under-powered) |
| `place.l5_h12` | 1536 | 124 | -0.010 | -0.101–0.082 | 0.8369 | 0.064 | not_testable_yet (under-powered) |
| `place.l5_h2` | 1536 | 138 | -0.021 | -0.105–0.063 | 0.6220 | 0.075 | not_testable_yet (under-powered) |
| `place.l5_h3` | 1536 | 127 | 0.039 | -0.045–0.123 | 0.3596 | 0.068 | not_testable_yet (under-powered) |
| `place.l5_h4` | 1536 | 127 | 0.013 | -0.078–0.104 | 0.7772 | 0.066 | not_testable_yet (under-powered) |
| `place.l5_h5` | 1536 | 121 | -0.022 | -0.107–0.062 | 0.6025 | 0.081 | not_testable_yet (under-powered) |
| `place.l5_h6` | 1536 | 108 | 0.061 | -0.028–0.150 | 0.1783 | 0.057 | not_testable_yet (under-powered) |
| `place.l5_h7` | 1536 | 121 | -0.017 | -0.110–0.076 | 0.7206 | 0.063 | not_testable_yet (under-powered) |
| `place.l5_h8` | 1536 | 149 | -0.058 | -0.140–0.025 | 0.1688 | 0.082 | not_testable_yet (under-powered) |
| `place.l5_h9` | 1536 | 125 | 0.073 | -0.017–0.163 | 0.1128 | 0.065 | not_testable_yet (under-powered) |
| `place.l6_h1` | 1536 | 130 | 0.028 | -0.062–0.118 | 0.5417 | 0.068 | not_testable_yet (under-powered) |
| `place.l6_h10` | 1536 | 125 | -0.057 | -0.140–0.026 | 0.1774 | 0.079 | not_testable_yet (under-powered) |
| `place.l6_h11` | 1536 | 123 | -0.045 | -0.127–0.038 | 0.2906 | 0.078 | not_testable_yet (under-powered) |
| `place.l6_h12` | 1536 | 126 | 0.079 | -0.002–0.160 | 0.0568 | 0.068 | not_testable_yet (under-powered) |
| `place.l6_h2` | 1536 | 135 | 0.096 | 0.031–0.162 | 0.0038 | 0.084 | not_testable_yet (under-powered) |
| `place.l6_h3` | 1536 | 125 | -0.014 | -0.093–0.066 | 0.7377 | 0.079 | not_testable_yet (under-powered) |
| `place.l6_h4` | 1536 | 117 | 0.017 | -0.071–0.105 | 0.7026 | 0.063 | not_testable_yet (under-powered) |
| `place.l6_h5` | 1536 | 121 | -0.013 | -0.101–0.076 | 0.7807 | 0.065 | not_testable_yet (under-powered) |
| `place.l6_h6` | 1536 | 127 | -0.010 | -0.101–0.081 | 0.8296 | 0.066 | not_testable_yet (under-powered) |
| `place.l6_h7` | 1536 | 138 | -0.003 | -0.086–0.080 | 0.9428 | 0.075 | not_testable_yet (under-powered) |
| `place.l6_h8` | 1536 | 129 | -0.010 | -0.100–0.080 | 0.8293 | 0.067 | not_testable_yet (under-powered) |
| `place.l6_h9` | 1536 | 140 | 0.023 | -0.058–0.104 | 0.5771 | 0.076 | not_testable_yet (under-powered) |
| `place.l7_h1` | 1536 | 106 | 0.036 | -0.055–0.128 | 0.4379 | 0.056 | not_testable_yet (under-powered) |
| `place.l7_h10` | 1536 | 128 | -0.009 | -0.096–0.077 | 0.8340 | 0.069 | not_testable_yet (under-powered) |
| `place.l7_h11` | 1536 | 126 | -0.015 | -0.103–0.072 | 0.7311 | 0.068 | not_testable_yet (under-powered) |
| `place.l7_h12` | 1536 | 142 | 0.011 | -0.075–0.097 | 0.8076 | 0.073 | not_testable_yet (under-powered) |
| `place.l7_h2` | 1536 | 121 | 0.032 | -0.055–0.118 | 0.4741 | 0.065 | not_testable_yet (under-powered) |
| `place.l7_h3` | 1536 | 125 | 0.016 | -0.070–0.102 | 0.7078 | 0.067 | not_testable_yet (under-powered) |
| `place.l7_h4` | 1536 | 123 | 0.007 | -0.085–0.099 | 0.8836 | 0.064 | not_testable_yet (under-powered) |
| `place.l7_h5` | 1536 | 135 | -0.051 | -0.139–0.037 | 0.2574 | 0.070 | not_testable_yet (under-powered) |
| `place.l7_h6` | 1536 | 115 | 0.044 | -0.044–0.132 | 0.3253 | 0.061 | not_testable_yet (under-powered) |
| `place.l7_h7` | 1536 | 131 | -0.015 | -0.097–0.067 | 0.7117 | 0.087 | not_testable_yet (under-powered) |
| `place.l7_h8` | 1536 | 151 | -0.021 | -0.102–0.059 | 0.6054 | 0.082 | not_testable_yet (under-powered) |
| `place.l7_h9` | 1536 | 133 | 0.043 | -0.046–0.131 | 0.3435 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h1` | 1536 | 132 | 0.061 | -0.028–0.149 | 0.1801 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h10` | 1536 | 127 | 0.042 | -0.031–0.116 | 0.2611 | 0.079 | not_testable_yet (under-powered) |
| `place.l8_h11` | 1536 | 119 | -0.119 | -0.207–-0.030 | 0.0087 | 0.076 | not_testable_yet (under-powered) |
| `place.l8_h12` | 1536 | 121 | 0.013 | -0.075–0.100 | 0.7726 | 0.065 | not_testable_yet (under-powered) |
| `place.l8_h2` | 1536 | 108 | 0.043 | -0.036–0.122 | 0.2894 | 0.066 | not_testable_yet (under-powered) |
| `place.l8_h3` | 1536 | 122 | 0.086 | 0.017–0.156 | 0.0148 | 0.075 | not_testable_yet (under-powered) |
| `place.l8_h4` | 1536 | 134 | -0.045 | -0.131–0.040 | 0.3019 | 0.074 | not_testable_yet (under-powered) |
| `place.l8_h5` | 1536 | 138 | -0.028 | -0.113–0.056 | 0.5095 | 0.075 | not_testable_yet (under-powered) |
| `place.l8_h6` | 1536 | 132 | 0.011 | -0.078–0.100 | 0.8110 | 0.069 | not_testable_yet (under-powered) |
| `place.l8_h7` | 1536 | 141 | -0.003 | -0.085–0.080 | 0.9485 | 0.076 | not_testable_yet (under-powered) |
| `place.l8_h8` | 1536 | 146 | 0.032 | -0.053–0.117 | 0.4598 | 0.076 | not_testable_yet (under-powered) |
| `place.l8_h9` | 1536 | 116 | 0.007 | -0.083–0.096 | 0.8824 | 0.062 | not_testable_yet (under-powered) |
| `place.l9_h1` | 1536 | 126 | -0.120 | -0.210–-0.029 | 0.0094 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h10` | 1536 | 121 | 0.079 | -0.004–0.162 | 0.0619 | 0.065 | not_testable_yet (under-powered) |
| `place.l9_h11` | 1536 | 111 | -0.084 | -0.179–0.011 | 0.0844 | 0.060 | not_testable_yet (under-powered) |
| `place.l9_h12` | 1536 | 133 | 0.061 | -0.025–0.146 | 0.1652 | 0.089 | not_testable_yet (under-powered) |
| `place.l9_h2` | 1536 | 141 | -0.033 | -0.117–0.051 | 0.4366 | 0.077 | not_testable_yet (under-powered) |
| `place.l9_h3` | 1536 | 128 | 0.028 | -0.057–0.112 | 0.5209 | 0.069 | not_testable_yet (under-powered) |
| `place.l9_h4` | 1536 | 104 | 0.015 | -0.084–0.115 | 0.7608 | 0.054 | not_testable_yet (under-powered) |
| `place.l9_h5` | 1536 | 143 | 0.024 | -0.062–0.110 | 0.5876 | 0.074 | not_testable_yet (under-powered) |
| `place.l9_h6` | 1536 | 133 | -0.020 | -0.106–0.065 | 0.6425 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h7` | 1536 | 129 | -0.031 | -0.121–0.059 | 0.4960 | 0.067 | not_testable_yet (under-powered) |
| `place.l9_h8` | 1536 | 133 | 0.013 | -0.071–0.096 | 0.7659 | 0.072 | not_testable_yet (under-powered) |
| `place.l9_h9` | 1536 | 134 | -0.032 | -0.112–0.048 | 0.4280 | 0.088 | not_testable_yet (under-powered) |
| `place.mars_h1` | 1536 | 114 | 0.013 | -0.082–0.109 | 0.7841 | 0.060 | not_testable_yet (under-powered) |
| `place.mars_h10` | 1536 | 140 | -0.043 | -0.130–0.044 | 0.3324 | 0.073 | not_testable_yet (under-powered) |
| `place.mars_h11` | 1536 | 122 | -0.038 | -0.130–0.054 | 0.4197 | 0.064 | not_testable_yet (under-powered) |
| `place.mars_h12` | 1536 | 117 | -0.024 | -0.110–0.061 | 0.5768 | 0.078 | not_testable_yet (under-powered) |
| `place.mars_h2` | 1536 | 124 | -0.038 | -0.129–0.054 | 0.4209 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h3` | 1536 | 132 | 0.055 | -0.034–0.144 | 0.2246 | 0.069 | not_testable_yet (under-powered) |
| `place.mars_h4` | 1536 | 130 | -0.052 | -0.131–0.027 | 0.1979 | 0.086 | not_testable_yet (under-powered) |
| `place.mars_h5` | 1536 | 129 | -0.025 | -0.107–0.057 | 0.5457 | 0.086 | not_testable_yet (under-powered) |
| `place.mars_h6` | 1536 | 124 | -0.023 | -0.115–0.069 | 0.6200 | 0.065 | not_testable_yet (under-powered) |
| `place.mars_h7` | 1536 | 123 | 0.085 | -0.004–0.175 | 0.0620 | 0.084 | not_testable_yet (under-powered) |
| `place.mars_h8` | 1536 | 138 | 0.002 | -0.085–0.090 | 0.9600 | 0.072 | not_testable_yet (under-powered) |
| `place.mars_h9` | 1536 | 143 | -0.052 | -0.129–0.024 | 0.1799 | 0.093 | not_testable_yet (under-powered) |
| `place.mars_in_aquarius` | 1536 | 96 | -0.056 | -0.159–0.047 | 0.2903 | 0.051 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 1536 | 116 | -0.002 | -0.097–0.093 | 0.9679 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 1536 | 147 | 0.075 | -0.009–0.159 | 0.0803 | 0.076 | not_testable_yet (under-powered) |
| `place.mars_in_capricorn` | 1536 | 101 | 0.068 | -0.032–0.168 | 0.1798 | 0.053 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 1536 | 120 | -0.056 | -0.149–0.036 | 0.2331 | 0.062 | not_testable_yet (under-powered) |
| `place.mars_in_leo` | 1536 | 166 | -0.079 | -0.159–0.001 | 0.0523 | 0.086 | not_testable_yet (under-powered) |
| `place.mars_in_libra` | 1536 | 158 | 0.002 | -0.080–0.085 | 0.9525 | 0.082 | not_testable_yet (under-powered) |
| `place.mars_in_pisces` | 1536 | 137 | -0.064 | -0.151–0.024 | 0.1541 | 0.071 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 1536 | 99 | -0.017 | -0.118–0.085 | 0.7503 | 0.052 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 1536 | 116 | 0.063 | -0.030–0.157 | 0.1857 | 0.061 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 1536 | 136 | 0.053 | -0.034–0.141 | 0.2340 | 0.071 | not_testable_yet (under-powered) |
| `place.mars_in_virgo` | 1536 | 144 | 0.019 | -0.067–0.105 | 0.6612 | 0.075 | not_testable_yet (under-powered) |
| `place.mercury_h1` | 1536 | 114 | 0.099 | 0.005–0.192 | 0.0392 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 1536 | 130 | -0.079 | -0.168–0.011 | 0.0841 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 1536 | 114 | -0.021 | -0.116–0.075 | 0.6702 | 0.060 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 1536 | 135 | -0.035 | -0.114–0.045 | 0.3930 | 0.089 | not_testable_yet (under-powered) |
| `place.mercury_h2` | 1536 | 140 | 0.059 | -0.027–0.145 | 0.1779 | 0.073 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 1536 | 125 | -0.059 | -0.150–0.032 | 0.2026 | 0.065 | not_testable_yet (under-powered) |
| `place.mercury_h4` | 1536 | 108 | 0.006 | -0.085–0.097 | 0.8971 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_h5` | 1536 | 131 | -0.013 | -0.095–0.069 | 0.7500 | 0.087 | not_testable_yet (under-powered) |
| `place.mercury_h6` | 1536 | 129 | -0.035 | -0.125–0.055 | 0.4421 | 0.067 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 1536 | 145 | -0.055 | -0.131–0.021 | 0.1543 | 0.095 | not_testable_yet (under-powered) |
| `place.mercury_h8` | 1536 | 142 | -0.060 | -0.146–0.026 | 0.1708 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_h9` | 1536 | 123 | -0.005 | -0.090–0.081 | 0.9162 | 0.082 | not_testable_yet (under-powered) |
| `place.mercury_in_aquarius` | 1536 | 135 | -0.015 | -0.104–0.073 | 0.7312 | 0.070 | not_testable_yet (under-powered) |
| `place.mercury_in_aries` | 1536 | 111 | -0.016 | -0.113–0.080 | 0.7441 | 0.058 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 1536 | 107 | -0.056 | -0.154–0.041 | 0.2588 | 0.056 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 1536 | 123 | 0.046 | -0.046–0.138 | 0.3240 | 0.064 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 1536 | 118 | 0.025 | -0.068–0.119 | 0.5947 | 0.062 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 1536 | 130 | 0.022 | -0.067–0.112 | 0.6270 | 0.068 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 1536 | 143 | -0.062 | -0.147–0.024 | 0.1590 | 0.074 | not_testable_yet (under-powered) |
| `place.mercury_in_pisces` | 1536 | 141 | -0.031 | -0.118–0.056 | 0.4828 | 0.073 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 1536 | 141 | 0.031 | -0.055–0.118 | 0.4749 | 0.073 | not_testable_yet (under-powered) |
| `place.mercury_in_scorpio` | 1536 | 156 | 0.017 | -0.066–0.100 | 0.6879 | 0.081 | not_testable_yet (under-powered) |
| `place.mercury_in_taurus` | 1536 | 109 | 0.004 | -0.094–0.101 | 0.9422 | 0.057 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 1536 | 122 | 0.033 | -0.059–0.125 | 0.4802 | 0.064 | not_testable_yet (under-powered) |
| `place.moon_h1` | 1536 | 132 | -0.014 | -0.103–0.075 | 0.7586 | 0.069 | not_testable_yet (under-powered) |
| `place.moon_h10` | 1536 | 147 | -0.015 | -0.100–0.070 | 0.7246 | 0.076 | not_testable_yet (under-powered) |
| `place.moon_h11` | 1536 | 109 | 0.013 | -0.084–0.111 | 0.7860 | 0.057 | not_testable_yet (under-powered) |
| `place.moon_h12` | 1536 | 135 | 0.022 | -0.061–0.105 | 0.6019 | 0.090 | not_testable_yet (under-powered) |
| `place.moon_h2` | 1536 | 130 | 0.014 | -0.076–0.104 | 0.7626 | 0.068 | not_testable_yet (under-powered) |
| `place.moon_h3` | 1536 | 115 | -0.016 | -0.111–0.079 | 0.7420 | 0.060 | not_testable_yet (under-powered) |
| `place.moon_h4` | 1536 | 119 | 0.038 | -0.050–0.127 | 0.3979 | 0.081 | not_testable_yet (under-powered) |
| `place.moon_h5` | 1536 | 144 | 0.018 | -0.062–0.099 | 0.6570 | 0.096 | not_testable_yet (under-powered) |
| `place.moon_h6` | 1536 | 119 | 0.008 | -0.085–0.102 | 0.8665 | 0.062 | not_testable_yet (under-powered) |
| `place.moon_h7` | 1536 | 127 | 0.038 | -0.048–0.124 | 0.3910 | 0.086 | not_testable_yet (under-powered) |
| `place.moon_h8` | 1536 | 143 | -0.033 | -0.119–0.053 | 0.4555 | 0.074 | not_testable_yet (under-powered) |
| `place.moon_h9` | 1536 | 116 | 0.034 | -0.056–0.124 | 0.4545 | 0.078 | not_testable_yet (under-powered) |
| `place.rahu_h1` | 1536 | 133 | 0.089 | 0.001–0.177 | 0.0468 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 1536 | 136 | 0.085 | -0.001–0.172 | 0.0538 | 0.071 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 1536 | 128 | -0.020 | -0.110–0.071 | 0.6666 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 1536 | 141 | -0.001 | -0.081–0.079 | 0.9765 | 0.093 | not_testable_yet (under-powered) |
| `place.rahu_h2` | 1536 | 129 | -0.024 | -0.114–0.066 | 0.6007 | 0.067 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 1536 | 124 | 0.024 | -0.068–0.115 | 0.6112 | 0.065 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 1536 | 131 | -0.146 | -0.216–-0.077 | 0.0000 | 0.085 | not_testable_yet (under-powered) |
| `place.rahu_h5` | 1536 | 124 | 0.014 | -0.072–0.100 | 0.7524 | 0.084 | not_testable_yet (under-powered) |
| `place.rahu_h6` | 1536 | 133 | -0.043 | -0.131–0.046 | 0.3450 | 0.069 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 1536 | 139 | -0.011 | -0.091–0.069 | 0.7944 | 0.092 | not_testable_yet (under-powered) |
| `place.rahu_h8` | 1536 | 118 | 0.040 | -0.053–0.134 | 0.3991 | 0.062 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 1536 | 100 | -0.035 | -0.127–0.056 | 0.4462 | 0.068 | not_testable_yet (under-powered) |
| `place.rahu_in_aquarius` | 1536 | 103 | 0.006 | -0.088–0.101 | 0.8959 | 0.055 | not_testable_yet (under-powered) |
| `place.rahu_in_aries` | 1536 | 146 | -0.012 | -0.093–0.070 | 0.7813 | 0.079 | not_testable_yet (under-powered) |
| `place.rahu_in_cancer` | 1536 | 149 | -0.056 | -0.138–0.027 | 0.1854 | 0.081 | not_testable_yet (under-powered) |
| `place.rahu_in_capricorn` | 1536 | 133 | -0.008 | -0.093–0.077 | 0.8462 | 0.072 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 1536 | 132 | -0.061 | -0.148–0.026 | 0.1700 | 0.071 | not_testable_yet (under-powered) |
| `place.rahu_in_leo` | 1536 | 191 | 0.018 | -0.053–0.089 | 0.6189 | 0.106 | not_testable_yet (under-powered) |
| `place.rahu_in_libra` | 1536 | 94 | 0.062 | -0.032–0.157 | 0.1975 | 0.050 | not_testable_yet (under-powered) |
| `place.rahu_in_pisces` | 1536 | 120 | 0.095 | 0.013–0.177 | 0.0238 | 0.064 | not_testable_yet (under-powered) |
| `place.rahu_in_sagittarius` | 1536 | 118 | -0.029 | -0.120–0.061 | 0.5246 | 0.063 | not_testable_yet (under-powered) |
| `place.rahu_in_scorpio` | 1536 | 113 | 0.029 | -0.060–0.119 | 0.5210 | 0.060 | not_testable_yet (under-powered) |
| `place.rahu_in_taurus` | 1536 | 91 | 0.052 | -0.045–0.149 | 0.2927 | 0.048 | not_testable_yet (under-powered) |
| `place.rahu_in_virgo` | 1536 | 146 | -0.049 | -0.132–0.034 | 0.2432 | 0.080 | not_testable_yet (under-powered) |
| `place.saturn_h1` | 1536 | 129 | -0.001 | -0.092–0.089 | 0.9748 | 0.067 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 1536 | 117 | 0.058 | -0.035–0.152 | 0.2234 | 0.061 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 1536 | 126 | -0.029 | -0.120–0.062 | 0.5377 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 1536 | 132 | 0.047 | -0.038–0.132 | 0.2801 | 0.089 | not_testable_yet (under-powered) |
| `place.saturn_h2` | 1536 | 128 | -0.062 | -0.153–0.028 | 0.1740 | 0.066 | not_testable_yet (under-powered) |
| `place.saturn_h3` | 1536 | 124 | -0.064 | -0.155–0.027 | 0.1701 | 0.064 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 1536 | 128 | 0.080 | -0.007–0.168 | 0.0724 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_h5` | 1536 | 147 | 0.003 | -0.075–0.082 | 0.9336 | 0.098 | not_testable_yet (under-powered) |
| `place.saturn_h6` | 1536 | 116 | 0.041 | -0.053–0.135 | 0.3943 | 0.061 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 1536 | 128 | 0.001 | -0.083–0.085 | 0.9868 | 0.085 | not_testable_yet (under-powered) |
| `place.saturn_h8` | 1536 | 130 | -0.014 | -0.104–0.076 | 0.7585 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 1536 | 131 | -0.009 | -0.091–0.074 | 0.8393 | 0.087 | not_testable_yet (under-powered) |
| `place.saturn_in_aquarius` | 1536 | 111 | 0.049 | -0.029–0.126 | 0.2168 | 0.068 | not_testable_yet (under-powered) |
| `place.saturn_in_aries` | 1536 | 149 | 0.017 | -0.054–0.088 | 0.6403 | 0.096 | not_testable_yet (under-powered) |
| `place.saturn_in_cancer` | 1536 | 93 | -0.038 | -0.132–0.055 | 0.4225 | 0.056 | not_testable_yet (under-powered) |
| `place.saturn_in_capricorn` | 1536 | 129 | -0.013 | -0.092–0.065 | 0.7371 | 0.082 | not_testable_yet (under-powered) |
| `place.saturn_in_gemini` | 1536 | 110 | -0.012 | -0.096–0.072 | 0.7821 | 0.067 | not_testable_yet (under-powered) |
| `place.saturn_in_leo` | 1536 | 142 | 0.004 | -0.069–0.078 | 0.9055 | 0.091 | not_testable_yet (under-powered) |
| `place.saturn_in_libra` | 1536 | 142 | -0.003 | -0.078–0.071 | 0.9308 | 0.091 | not_testable_yet (under-powered) |
| `place.saturn_in_pisces` | 1536 | 119 | 0.082 | 0.011–0.153 | 0.0237 | 0.073 | not_testable_yet (under-powered) |
| `place.saturn_in_sagittarius` | 1536 | 131 | 0.033 | -0.041–0.106 | 0.3873 | 0.082 | not_testable_yet (under-powered) |
| `place.saturn_in_scorpio` | 1536 | 153 | 0.016 | -0.054–0.087 | 0.6483 | 0.100 | not_testable_yet (under-powered) |
| `place.saturn_in_taurus` | 1536 | 131 | -0.059 | -0.141–0.022 | 0.1536 | 0.084 | not_testable_yet (under-powered) |
| `place.saturn_in_virgo` | 1536 | 126 | -0.081 | -0.165–0.004 | 0.0609 | 0.080 | not_testable_yet (under-powered) |
| `place.sun_h1` | 1536 | 110 | 0.122 | 0.027–0.216 | 0.0115 | 0.058 | not_testable_yet (under-powered) |
| `place.sun_h10` | 1536 | 126 | -0.046 | -0.137–0.045 | 0.3223 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_h11` | 1536 | 119 | -0.098 | -0.190–-0.005 | 0.0380 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_h12` | 1536 | 129 | -0.012 | -0.095–0.071 | 0.7799 | 0.086 | not_testable_yet (under-powered) |
| `place.sun_h2` | 1536 | 144 | 0.019 | -0.067–0.105 | 0.6612 | 0.075 | not_testable_yet (under-powered) |
| `place.sun_h3` | 1536 | 126 | 0.015 | -0.076–0.106 | 0.7534 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_h4` | 1536 | 112 | -0.025 | -0.112–0.062 | 0.5677 | 0.076 | not_testable_yet (under-powered) |
| `place.sun_h5` | 1536 | 123 | -0.010 | -0.094–0.075 | 0.8190 | 0.083 | not_testable_yet (under-powered) |
| `place.sun_h6` | 1536 | 127 | 0.067 | -0.023–0.157 | 0.1430 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_h7` | 1536 | 134 | 0.018 | -0.065–0.101 | 0.6697 | 0.089 | not_testable_yet (under-powered) |
| `place.sun_h8` | 1536 | 149 | -0.047 | -0.131–0.038 | 0.2780 | 0.077 | not_testable_yet (under-powered) |
| `place.sun_h9` | 1536 | 137 | 0.009 | -0.073–0.091 | 0.8331 | 0.091 | not_testable_yet (under-powered) |
| `place.sun_in_aquarius` | 1536 | 126 | -0.020 | -0.111–0.071 | 0.6671 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 1536 | 144 | 0.057 | -0.028–0.143 | 0.1860 | 0.075 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 1536 | 118 | -0.039 | -0.133–0.055 | 0.4171 | 0.062 | not_testable_yet (under-powered) |
| `place.sun_in_capricorn` | 1536 | 141 | 0.000 | -0.086–0.087 | 0.9956 | 0.073 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 1536 | 117 | 0.049 | -0.045–0.143 | 0.3069 | 0.061 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 1536 | 129 | 0.044 | -0.046–0.133 | 0.3405 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 1536 | 129 | -0.024 | -0.114–0.066 | 0.6007 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 1536 | 128 | -0.097 | -0.186–-0.007 | 0.0343 | 0.066 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 1536 | 110 | 0.126 | 0.032–0.220 | 0.0087 | 0.058 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 1536 | 134 | 0.013 | -0.075–0.102 | 0.7715 | 0.070 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 1536 | 128 | -0.037 | -0.127–0.053 | 0.4232 | 0.067 | not_testable_yet (under-powered) |
| `place.sun_in_virgo` | 1536 | 132 | -0.061 | -0.150–0.028 | 0.1777 | 0.068 | not_testable_yet (under-powered) |
| `place.venus_h1` | 1536 | 132 | -0.014 | -0.103–0.075 | 0.7586 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_h10` | 1536 | 125 | 0.054 | -0.037–0.145 | 0.2442 | 0.065 | not_testable_yet (under-powered) |
| `place.venus_h11` | 1536 | 109 | -0.115 | -0.211–-0.019 | 0.0186 | 0.057 | not_testable_yet (under-powered) |
| `place.venus_h12` | 1536 | 117 | -0.015 | -0.102–0.071 | 0.7309 | 0.078 | not_testable_yet (under-powered) |
| `place.venus_h2` | 1536 | 136 | 0.077 | -0.010–0.164 | 0.0814 | 0.071 | not_testable_yet (under-powered) |
| `place.venus_h3` | 1536 | 114 | -0.068 | -0.163–0.027 | 0.1596 | 0.059 | not_testable_yet (under-powered) |
| `place.venus_h4` | 1536 | 127 | -0.002 | -0.086–0.081 | 0.9561 | 0.085 | not_testable_yet (under-powered) |
| `place.venus_h5` | 1536 | 110 | -0.020 | -0.109–0.068 | 0.6495 | 0.075 | not_testable_yet (under-powered) |
| `place.venus_h6` | 1536 | 135 | 0.063 | -0.024–0.151 | 0.1569 | 0.070 | not_testable_yet (under-powered) |
| `place.venus_h7` | 1536 | 147 | -0.021 | -0.099–0.056 | 0.5887 | 0.097 | not_testable_yet (under-powered) |
| `place.venus_h8` | 1536 | 148 | -0.013 | -0.098–0.071 | 0.7594 | 0.077 | not_testable_yet (under-powered) |
| `place.venus_h9` | 1536 | 136 | 0.036 | -0.048–0.119 | 0.4036 | 0.091 | not_testable_yet (under-powered) |
| `place.venus_in_aquarius` | 1536 | 101 | -0.005 | -0.098–0.088 | 0.9117 | 0.069 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 1536 | 122 | 0.053 | -0.036–0.142 | 0.2405 | 0.083 | not_testable_yet (under-powered) |
| `place.venus_in_cancer` | 1536 | 106 | 0.020 | -0.073–0.112 | 0.6770 | 0.072 | not_testable_yet (under-powered) |
| `place.venus_in_capricorn` | 1536 | 184 | -0.046 | -0.114–0.023 | 0.1949 | 0.118 | not_testable_yet (under-powered) |
| `place.venus_in_gemini` | 1536 | 135 | -0.001 | -0.083–0.081 | 0.9845 | 0.090 | not_testable_yet (under-powered) |
| `place.venus_in_leo` | 1536 | 154 | -0.022 | -0.098–0.054 | 0.5729 | 0.101 | not_testable_yet (under-powered) |
| `place.venus_in_libra` | 1536 | 146 | -0.095 | -0.167–-0.023 | 0.0100 | 0.095 | not_testable_yet (under-powered) |
| `place.venus_in_pisces` | 1536 | 141 | 0.055 | -0.028–0.138 | 0.1945 | 0.095 | not_testable_yet (under-powered) |
| `place.venus_in_sagittarius` | 1536 | 112 | 0.039 | -0.052–0.131 | 0.4005 | 0.076 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 1536 | 108 | -0.106 | -0.187–-0.025 | 0.0100 | 0.072 | not_testable_yet (under-powered) |
| `place.venus_in_taurus` | 1536 | 138 | 0.063 | -0.021–0.147 | 0.1393 | 0.093 | not_testable_yet (under-powered) |
| `place.venus_in_virgo` | 1536 | 89 | 0.086 | -0.018–0.191 | 0.1042 | 0.063 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 1536 | 179 | 0.048 | -0.029–0.126 | 0.2223 | 0.093 | not_testable_yet (under-powered) |
| `yoga.budhaditya` | 1536 | 777 | -0.007 | -0.057–0.043 | 0.7912 | 0.271 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari` | 1536 | 521 | -0.015 | -0.064–0.035 | 0.5695 | 0.280 | not_testable_yet (under-powered) |
| `yoga.gaja_kesari_bphs` | 1536 | 129 | -0.025 | -0.111–0.062 | 0.5749 | 0.070 | not_testable_yet (under-powered) |
| `yoga.hamsa` | 1536 | 257 | -0.015 | -0.082–0.052 | 0.6640 | 0.132 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja` | 1536 | 830 | -0.017 | -0.068–0.033 | 0.4960 | 0.270 | not_testable_yet (under-powered) |
| `yoga.kendra_trikona_raja_weak` | 1536 | 1005 | 0.012 | -0.041–0.064 | 0.6653 | 0.240 | not_testable_yet (under-powered) |
| `yoga.malavya` | 1536 | 275 | 0.042 | -0.023–0.107 | 0.2078 | 0.141 | not_testable_yet (under-powered) |
| `yoga.neecha_bhanga` | 1536 | 711 | 0.037 | -0.013–0.087 | 0.1488 | 0.267 | not_testable_yet (under-powered) |
| `yoga.parivartana` | 1536 | 554 | -0.011 | -0.060–0.038 | 0.6552 | 0.290 | not_testable_yet (under-powered) |
| `yoga.ruchaka` | 1536 | 234 | 0.063 | -0.006–0.132 | 0.0724 | 0.121 | not_testable_yet (under-powered) |
| `yoga.sasa` | 1536 | 268 | -0.008 | -0.074–0.058 | 0.8096 | 0.137 | not_testable_yet (under-powered) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
