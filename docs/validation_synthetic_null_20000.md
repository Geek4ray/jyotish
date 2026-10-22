# Synthetic — Validation — null, N = 20,000, odds ratio 1.0 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 14920 development, 5080 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `336c84d8fe73b6c0319bf9bba24b7c13a1069ac913b95eb6f586c7e271c9908e` ({"salt_sha256": "9e7200ace7a762a22a32d7f2e6b2fc054afa9ba8fa6b9a022d95f95f8d91123e", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "749873be890a17f9a1c30911ace010fcf716d06404f42d71915a522d7dda143f"})
- analysis code `d9e60e44a12abe1e9454e4a09c15c26e2d22e7ba894336c9e8e817bc9809ad94`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 14920 | 1.000 | 0.298 | 0.988 | 0.953–1.022 | 0.7732 | 0.8661 | no | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 14920 | 1.000 | 0.506 | 1.002 | 0.979–1.026 | 0.4456 | 0.8661 | no | 0.999 |
| children | 14920 | 1.000 | 0.302 | 0.983 | 0.945–1.022 | 0.7882 | 0.8661 | no | 0.999 |
| intellect | 14920 | 1.000 | 0.298 | 0.990 | 0.953–1.024 | 0.6673 | 0.8661 | no | 1.000 |
| health | 14920 | 1.000 | 0.513 | 1.008 | 0.990–1.028 | 0.1399 | 0.7692 | no | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 14920 | 1.000 | 0.300 | 1.001 | 0.960–1.041 | 0.4665 | 0.8661 | no | 0.999 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 14920 | 1.000 | 0.301 | 0.981 | 0.949–1.014 | 0.8661 | 0.8661 | no | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 14920 | 1.000 | 0.511 | 1.018 | 0.994–1.042 | 0.0779 | 0.7692 | no | 0.999 |
| gains | 14920 | 1.000 | 0.298 | 0.992 | 0.961–1.025 | 0.6753 | 0.8661 | no | 1.000 |
| foreign | 14920 | 1.000 | 0.302 | 0.992 | 0.959–1.024 | 0.6943 | 0.8661 | no | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 14920 | 1.000 | 0.298 | 1.005 | 0.968–1.042 | 0.4306 | 0.8661 | no | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14920 | 1.000 | 8 | 5.81 | 8 | 0.6689 | 0.491 | 0.495 | 0.4515 |
| mother_home | 14920 | 1.000 | 8 | 15.97 | 8 | 0.0428 | 0.495 | 0.506 | 0.0198 |
| children | 14920 | 1.000 | 7 | 3.33 | 7 | 0.8531 | 0.498 | 0.496 | 0.6983 |
| intellect | 14920 | 1.000 | 8 | 20.42 | 8 | 0.0089 | 0.495 | 0.509 | 0.0020 |
| health | 14920 | 1.000 | 8 | 7.05 | 8 | 0.5318 | 0.501 | 0.498 | 0.3025 |
| marriage | 14920 | 1.000 | 8 | 7.94 | 8 | 0.4389 | 0.494 | 0.495 | 0.6748 |
| father | 14920 | 1.000 | 7 | 8.16 | 7 | 0.3184 | 0.498 | 0.493 | 0.1925 |
| career | 14920 | 1.000 | 8 | 8.12 | 8 | 0.4216 | 0.498 | 0.494 | 0.1883 |
| gains | 14920 | 1.000 | 8 | 5.18 | 8 | 0.7382 | 0.491 | 0.495 | 0.4552 |
| foreign | 14920 | 1.000 | 7 | 3.28 | 7 | 0.8578 | 0.493 | 0.484 | 0.0677 |
| reputation | 14920 | 1.000 | 8 | 19.06 | 8 | 0.0146 | 0.495 | 0.506 | 0.0056 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14920 | 1.000 | 724232 | 4442 | 0.933 | 1.013 | 0.0796 | 0.013 (-0.106, 0.131) |
| mother_home | 14920 | 1.000 | 624180 | 7545 | 0.943 | 0.937 | 0.2438 | -0.066 (-0.161, 0.029) |
| children | 14920 | 1.000 | 722481 | 4511 | 0.902 | 0.960 | 0.6567 | -0.041 (-0.138, 0.057) |
| intellect | 14920 | 1.000 | 724445 | 4447 | 0.946 | 0.959 | 0.1791 | -0.042 (-0.170, 0.086) |
| health | 14920 | 1.000 | 625050 | 7656 | 0.939 | 1.053 | 0.0100 | 0.052 (-0.045, 0.148) |
| marriage | 14920 | 1.000 | 723413 | 4480 | 0.940 | 0.953 | 0.4428 | -0.049 (-0.171, 0.073) |
| father | 14920 | 1.000 | 722872 | 4496 | 0.880 | 0.991 | 0.1642 | -0.009 (-0.099, 0.081) |
| career | 14920 | 1.000 | 623838 | 7620 | 0.954 | 1.105 | 0.0199 | 0.101 (-0.012, 0.214) |
| gains | 14920 | 1.000 | 724232 | 4442 | 0.870 | 0.995 | 0.0995 | -0.005 (-0.093, 0.083) |
| foreign | 14920 | 1.000 | 724006 | 4502 | 0.952 | 0.971 | 0.2239 | -0.029 (-0.164, 0.106) |
| reputation | 14920 | 1.000 | 724445 | 4447 | 0.891 | 1.044 | 0.0796 | 0.043 (-0.053, 0.140) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14920 | 1.000 | 0.006 | 0.005 | 4 | 0 | not allowed |
| mother_home | 14920 | 1.000 | 0.006 | 0.003 | 3 | 3 | not allowed |
| children | 14920 | 1.000 | 0.010 | 0.008 | 3 | 9 | not allowed |
| intellect | 14920 | 1.000 | 0.008 | 0.008 | 3 | 0 | not allowed |
| health | 14920 | 1.000 | 0.004 | 0.016 | 3 | 14 | not allowed |
| marriage | 14920 | 1.000 | 0.004 | 0.009 | 4 | 0 | not allowed |
| father | 14920 | 1.000 | 0.006 | 0.005 | 4 | 0 | not allowed |
| career | 14920 | 1.000 | 0.007 | 0.010 | 3 | 1 | not allowed |
| gains | 14920 | 1.000 | 0.005 | 0.005 | 3 | 4 | not allowed |
| foreign | 14920 | 1.000 | 0.008 | 0.007 | 5 | 0 | not allowed |
| reputation | 14920 | 1.000 | 0.010 | 0.005 | 5 | 0 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 14920 | 1.000 | 5422 | 1.000 | 1.000 |
| mother_home | 14920 | 1.000 | 4409 | 0.999 | 1.000 |
| children | 14920 | 1.000 | 4061 | 0.999 | 1.000 |
| intellect | 14920 | 1.000 | 4751 | 1.000 | 1.000 |
| health | 14920 | 1.000 | 6134 | 1.000 | 1.000 |
| marriage | 14920 | 1.000 | 4095 | 0.999 | 1.000 |
| father | 14920 | 1.000 | 5207 | 1.000 | 1.000 |
| career | 14920 | 1.000 | 4371 | 0.999 | 1.000 |
| gains | 14920 | 1.000 | 5197 | 1.000 | 1.000 |
| foreign | 14920 | 1.000 | 5621 | 1.000 | 1.000 |
| reputation | 14920 | 1.000 | 4592 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 253 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 107 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 14920 | 1242 | 0.006 | -0.023–0.035 | 0.6918 | 0.790 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 14920 | 1215 | 0.005 | -0.024–0.034 | 0.7432 | 0.780 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 14920 | 1258 | -0.013 | -0.042–0.015 | 0.3613 | 0.795 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 14920 | 1265 | 0.015 | -0.012–0.042 | 0.2735 | 0.861 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 14920 | 1240 | 0.001 | -0.028–0.030 | 0.9668 | 0.789 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 14920 | 1270 | -0.005 | -0.034–0.024 | 0.7416 | 0.799 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 14920 | 1225 | 0.031 | 0.004–0.059 | 0.0245 | 0.853 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 14920 | 1241 | -0.019 | -0.045–0.008 | 0.1644 | 0.852 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 14920 | 1252 | -0.008 | -0.037–0.021 | 0.5769 | 0.794 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 14920 | 1246 | -0.014 | -0.040–0.012 | 0.2920 | 0.855 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 14920 | 1228 | 0.008 | -0.021–0.037 | 0.5970 | 0.785 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 14920 | 1238 | -0.034 | -0.060–-0.008 | 0.0102 | 0.850 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 14920 | 1167 | 0.008 | -0.020–0.036 | 0.5876 | 0.820 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 14920 | 1319 | -0.003 | -0.030–0.024 | 0.8412 | 0.870 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 14920 | 1326 | 0.000 | -0.027–0.027 | 0.9951 | 0.871 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_capricorn` | 14920 | 1263 | -0.004 | -0.031–0.023 | 0.7778 | 0.853 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_gemini` | 14920 | 1140 | 0.011 | -0.018–0.039 | 0.4677 | 0.810 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_leo` | 14920 | 1336 | -0.005 | -0.032–0.021 | 0.6975 | 0.874 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 14920 | 1323 | -0.012 | -0.039–0.015 | 0.4013 | 0.871 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 14920 | 1086 | -0.016 | -0.046–0.013 | 0.2795 | 0.789 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 14920 | 1240 | 0.014 | -0.014–0.041 | 0.3286 | 0.845 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 14920 | 1216 | -0.011 | -0.039–0.017 | 0.4254 | 0.839 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 14920 | 1192 | 0.014 | -0.014–0.042 | 0.3360 | 0.829 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 14920 | 1312 | 0.006 | -0.021–0.033 | 0.6564 | 0.867 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 14920 | 1275 | -0.007 | -0.036–0.022 | 0.6289 | 0.801 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 14920 | 1196 | -0.021 | -0.050–0.009 | 0.1686 | 0.773 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 14920 | 1255 | 0.000 | -0.029–0.029 | 0.9980 | 0.794 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 14920 | 1260 | -0.003 | -0.029–0.024 | 0.8372 | 0.858 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 14920 | 1247 | -0.001 | -0.030–0.028 | 0.9588 | 0.791 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 14920 | 1215 | -0.008 | -0.037–0.022 | 0.6096 | 0.780 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 14920 | 1242 | 0.015 | -0.012–0.042 | 0.2697 | 0.857 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 14920 | 1234 | 0.030 | 0.003–0.057 | 0.0317 | 0.852 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 14920 | 1275 | 0.014 | -0.015–0.042 | 0.3557 | 0.801 | classical_rejected (recommended: powered null) |
| `place.ketu_h7` | 14920 | 1259 | 0.011 | -0.015–0.038 | 0.4089 | 0.860 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 14920 | 1289 | -0.014 | -0.043–0.015 | 0.3382 | 0.806 | classical_rejected (recommended: powered null) |
| `place.ketu_h9` | 14920 | 1173 | -0.018 | -0.044–0.009 | 0.2027 | 0.830 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 14920 | 1562 | -0.001 | -0.025–0.023 | 0.9386 | 0.924 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 14920 | 1132 | -0.002 | -0.029–0.026 | 0.9155 | 0.817 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 14920 | 1062 | -0.032 | -0.060–-0.004 | 0.0248 | 0.788 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 14920 | 1472 | -0.001 | -0.026–0.024 | 0.9444 | 0.908 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 14920 | 1185 | 0.019 | -0.009–0.046 | 0.1838 | 0.837 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 14920 | 1163 | 0.013 | -0.015–0.041 | 0.3539 | 0.829 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 14920 | 1194 | 0.002 | -0.025–0.030 | 0.8584 | 0.839 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 14920 | 1459 | -0.014 | -0.038–0.011 | 0.2681 | 0.905 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 14920 | 1259 | -0.026 | -0.052–-0.000 | 0.0499 | 0.857 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 14920 | 1153 | 0.012 | -0.016–0.040 | 0.3864 | 0.825 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 14920 | 1129 | 0.012 | -0.016–0.040 | 0.4098 | 0.817 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 14920 | 1150 | 0.020 | -0.008–0.048 | 0.1665 | 0.825 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 14920 | 1281 | -0.001 | -0.026–0.023 | 0.9261 | 0.944 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 14920 | 1237 | 0.004 | -0.025–0.033 | 0.8014 | 0.788 | not_testable_yet (under-powered) |
| `place.l10_h11` | 14920 | 1273 | 0.002 | -0.026–0.031 | 0.8674 | 0.800 | classical_rejected (recommended: powered null) |
| `place.l10_h12` | 14920 | 1198 | -0.003 | -0.031–0.025 | 0.8467 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 14920 | 1231 | 0.003 | -0.026–0.032 | 0.8443 | 0.786 | not_testable_yet (under-powered) |
| `place.l10_h3` | 14920 | 1241 | -0.016 | -0.045–0.013 | 0.2910 | 0.789 | not_testable_yet (under-powered) |
| `place.l10_h4` | 14920 | 1329 | -0.019 | -0.046–0.008 | 0.1753 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 14920 | 1212 | 0.008 | -0.020–0.036 | 0.5731 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 14920 | 1210 | 0.004 | -0.020–0.029 | 0.7293 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 14920 | 1235 | -0.007 | -0.034–0.021 | 0.6387 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 14920 | 1309 | 0.000 | -0.024–0.024 | 0.9856 | 0.949 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 14920 | 1164 | -0.005 | -0.034–0.023 | 0.7142 | 0.821 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 14920 | 1237 | 0.002 | -0.023–0.027 | 0.8745 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 14920 | 1197 | 0.020 | -0.010–0.049 | 0.1909 | 0.773 | not_testable_yet (under-powered) |
| `place.l11_h11` | 14920 | 1208 | 0.014 | -0.016–0.043 | 0.3660 | 0.777 | not_testable_yet (under-powered) |
| `place.l11_h12` | 14920 | 1255 | -0.017 | -0.045–0.011 | 0.2300 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 14920 | 1305 | -0.002 | -0.030–0.026 | 0.8850 | 0.811 | classical_rejected (recommended: powered null) |
| `place.l11_h3` | 14920 | 1235 | -0.009 | -0.038–0.021 | 0.5626 | 0.787 | not_testable_yet (under-powered) |
| `place.l11_h4` | 14920 | 1242 | -0.024 | -0.052–0.004 | 0.0874 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 14920 | 1266 | 0.019 | -0.008–0.046 | 0.1597 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 14920 | 1227 | -0.000 | -0.025–0.025 | 0.9939 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 14920 | 1276 | 0.020 | -0.007–0.047 | 0.1412 | 0.856 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 14920 | 1209 | 0.012 | -0.012–0.037 | 0.3279 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 14920 | 1263 | -0.002 | -0.029–0.026 | 0.9136 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 14920 | 1248 | 0.017 | -0.011–0.044 | 0.2306 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 14920 | 1258 | -0.017 | -0.045–0.011 | 0.2312 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 14920 | 1235 | -0.005 | -0.032–0.023 | 0.7380 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 14920 | 1186 | 0.011 | -0.016–0.039 | 0.4276 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 14920 | 1222 | -0.005 | -0.033–0.023 | 0.7153 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 14920 | 1333 | 0.011 | -0.016–0.037 | 0.4198 | 0.873 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 14920 | 1262 | -0.008 | -0.037–0.021 | 0.5726 | 0.797 | not_testable_yet (under-powered) |
| `place.l12_h5` | 14920 | 1242 | -0.012 | -0.041–0.017 | 0.4242 | 0.790 | not_testable_yet (under-powered) |
| `place.l12_h6` | 14920 | 1231 | 0.007 | -0.020–0.035 | 0.6037 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 14920 | 1228 | 0.008 | -0.022–0.037 | 0.6117 | 0.785 | not_testable_yet (under-powered) |
| `place.l12_h8` | 14920 | 1287 | -0.016 | -0.043–0.011 | 0.2526 | 0.864 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 14920 | 1188 | -0.010 | -0.037–0.016 | 0.4459 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 14920 | 1182 | 0.005 | -0.025–0.035 | 0.7399 | 0.767 | not_testable_yet (under-powered) |
| `place.l1_h10` | 14920 | 1187 | -0.018 | -0.044–0.008 | 0.1725 | 0.927 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 14920 | 1293 | -0.005 | -0.029–0.020 | 0.7071 | 0.946 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 14920 | 1264 | -0.010 | -0.037–0.017 | 0.4755 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 14920 | 1273 | 0.002 | -0.023–0.026 | 0.9032 | 0.942 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 14920 | 1212 | 0.000 | -0.025–0.025 | 0.9805 | 0.931 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 14920 | 1286 | 0.023 | -0.004–0.050 | 0.0915 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 14920 | 1224 | -0.010 | -0.038–0.018 | 0.4693 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 14920 | 1264 | 0.016 | -0.013–0.045 | 0.2787 | 0.797 | not_testable_yet (under-powered) |
| `place.l1_h7` | 14920 | 1183 | -0.016 | -0.045–0.012 | 0.2624 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 14920 | 1255 | 0.007 | -0.022–0.036 | 0.6362 | 0.794 | not_testable_yet (under-powered) |
| `place.l1_h9` | 14920 | 1297 | 0.004 | -0.023–0.031 | 0.7749 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 14920 | 1269 | 0.014 | -0.010–0.038 | 0.2367 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 14920 | 1259 | 0.003 | -0.026–0.031 | 0.8597 | 0.796 | not_testable_yet (under-powered) |
| `place.l2_h11` | 14920 | 1204 | -0.036 | -0.065–-0.007 | 0.0163 | 0.776 | not_testable_yet (under-powered) |
| `place.l2_h12` | 14920 | 1296 | 0.005 | -0.022–0.032 | 0.7325 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 14920 | 1203 | 0.006 | -0.023–0.035 | 0.6913 | 0.775 | not_testable_yet (under-powered) |
| `place.l2_h3` | 14920 | 1271 | 0.009 | -0.019–0.038 | 0.5235 | 0.800 | not_testable_yet (under-powered) |
| `place.l2_h4` | 14920 | 1187 | 0.020 | -0.008–0.048 | 0.1538 | 0.825 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 14920 | 1254 | -0.013 | -0.040–0.015 | 0.3657 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 14920 | 1250 | 0.009 | -0.015–0.033 | 0.4676 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 14920 | 1248 | 0.020 | -0.007–0.047 | 0.1484 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 14920 | 1262 | -0.003 | -0.028–0.021 | 0.7911 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 14920 | 1217 | -0.009 | -0.036–0.019 | 0.5500 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 14920 | 1321 | 0.003 | -0.020–0.027 | 0.7800 | 0.950 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 14920 | 1206 | 0.022 | -0.008–0.051 | 0.1476 | 0.776 | not_testable_yet (under-powered) |
| `place.l3_h11` | 14920 | 1278 | -0.019 | -0.047–0.010 | 0.2041 | 0.802 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 14920 | 1226 | 0.021 | -0.006–0.048 | 0.1340 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 14920 | 1243 | -0.010 | -0.039–0.019 | 0.4834 | 0.790 | not_testable_yet (under-powered) |
| `place.l3_h3` | 14920 | 1258 | 0.010 | -0.019–0.039 | 0.4973 | 0.795 | not_testable_yet (under-powered) |
| `place.l3_h4` | 14920 | 1273 | 0.001 | -0.027–0.028 | 0.9537 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 14920 | 1262 | -0.013 | -0.040–0.015 | 0.3591 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 14920 | 1239 | -0.008 | -0.033–0.017 | 0.5212 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 14920 | 1180 | 0.005 | -0.023–0.033 | 0.7240 | 0.825 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 14920 | 1214 | -0.005 | -0.030–0.020 | 0.7165 | 0.931 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 14920 | 1220 | -0.007 | -0.035–0.021 | 0.6380 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 14920 | 1203 | 0.026 | -0.002–0.053 | 0.0661 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 14920 | 1209 | -0.016 | -0.044–0.013 | 0.2814 | 0.835 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 14920 | 1214 | 0.000 | -0.027–0.028 | 0.9746 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 14920 | 1289 | 0.028 | -0.001–0.056 | 0.0564 | 0.806 | classical_rejected (recommended: powered null) |
| `place.l4_h2` | 14920 | 1312 | 0.010 | -0.017–0.036 | 0.4842 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 14920 | 1203 | 0.012 | -0.015–0.040 | 0.3833 | 0.831 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 14920 | 1200 | -0.012 | -0.039–0.015 | 0.3777 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 14920 | 1315 | -0.001 | -0.030–0.027 | 0.9303 | 0.814 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 14920 | 1221 | -0.027 | -0.055–0.001 | 0.0606 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 14920 | 1267 | -0.000 | -0.029–0.029 | 0.9986 | 0.798 | not_testable_yet (under-powered) |
| `place.l4_h8` | 14920 | 1241 | -0.014 | -0.041–0.014 | 0.3405 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 14920 | 1246 | 0.016 | -0.013–0.045 | 0.2715 | 0.791 | not_testable_yet (under-powered) |
| `place.l5_h1` | 14920 | 1274 | 0.010 | -0.017–0.037 | 0.4783 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 14920 | 1301 | -0.029 | -0.056–-0.002 | 0.0379 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 14920 | 1188 | 0.016 | -0.012–0.044 | 0.2569 | 0.827 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 14920 | 1188 | 0.017 | -0.013–0.046 | 0.2693 | 0.770 | not_testable_yet (under-powered) |
| `place.l5_h2` | 14920 | 1281 | -0.008 | -0.035–0.019 | 0.5658 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 14920 | 1289 | 0.009 | -0.018–0.036 | 0.5223 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 14920 | 1236 | 0.015 | -0.014–0.044 | 0.3170 | 0.787 | not_testable_yet (under-powered) |
| `place.l5_h5` | 14920 | 1226 | -0.006 | -0.033–0.021 | 0.6633 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 14920 | 1206 | 0.005 | -0.023–0.033 | 0.7330 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 14920 | 1218 | -0.000 | -0.030–0.029 | 0.9776 | 0.781 | not_testable_yet (under-powered) |
| `place.l5_h8` | 14920 | 1334 | -0.020 | -0.047–0.007 | 0.1451 | 0.878 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 14920 | 1179 | -0.005 | -0.034–0.025 | 0.7547 | 0.766 | not_testable_yet (under-powered) |
| `place.l6_h1` | 14920 | 1239 | 0.014 | -0.015–0.043 | 0.3351 | 0.789 | not_testable_yet (under-powered) |
| `place.l6_h10` | 14920 | 1237 | 0.013 | -0.012–0.037 | 0.3114 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 14920 | 1297 | -0.010 | -0.034–0.015 | 0.4339 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 14920 | 1273 | 0.013 | -0.014–0.040 | 0.3337 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 14920 | 1285 | 0.001 | -0.024–0.025 | 0.9674 | 0.945 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 14920 | 1220 | -0.004 | -0.029–0.021 | 0.7389 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 14920 | 1221 | 0.029 | 0.002–0.056 | 0.0359 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l6_h5` | 14920 | 1224 | 0.000 | -0.027–0.028 | 0.9772 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 14920 | 1204 | -0.015 | -0.045–0.014 | 0.3120 | 0.776 | not_testable_yet (under-powered) |
| `place.l6_h7` | 14920 | 1256 | -0.022 | -0.049–0.006 | 0.1283 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 14920 | 1177 | -0.017 | -0.047–0.012 | 0.2494 | 0.766 | not_testable_yet (under-powered) |
| `place.l6_h9` | 14920 | 1287 | 0.011 | -0.016–0.038 | 0.4113 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 14920 | 1248 | 0.019 | -0.008–0.046 | 0.1748 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 14920 | 1221 | 0.016 | -0.012–0.043 | 0.2630 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 14920 | 1268 | -0.006 | -0.034–0.021 | 0.6589 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 14920 | 1236 | -0.018 | -0.047–0.011 | 0.2215 | 0.788 | not_testable_yet (under-powered) |
| `place.l7_h2` | 14920 | 1182 | 0.011 | -0.017–0.039 | 0.4332 | 0.825 | classical_rejected (recommended: powered null) |
| `place.l7_h3` | 14920 | 1365 | -0.004 | -0.030–0.023 | 0.7769 | 0.881 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 14920 | 1281 | -0.009 | -0.037–0.020 | 0.5532 | 0.803 | classical_rejected (recommended: powered null) |
| `place.l7_h5` | 14920 | 1263 | -0.005 | -0.034–0.024 | 0.7477 | 0.797 | not_testable_yet (under-powered) |
| `place.l7_h6` | 14920 | 1182 | -0.007 | -0.036–0.021 | 0.6087 | 0.828 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 14920 | 1226 | -0.002 | -0.029–0.025 | 0.8897 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 14920 | 1224 | -0.022 | -0.050–0.006 | 0.1249 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 14920 | 1224 | 0.016 | -0.014–0.045 | 0.2941 | 0.783 | not_testable_yet (under-powered) |
| `place.l8_h1` | 14920 | 1291 | 0.002 | -0.026–0.031 | 0.8823 | 0.807 | classical_rejected (recommended: powered null) |
| `place.l8_h10` | 14920 | 1195 | 0.000 | -0.025–0.025 | 0.9813 | 0.927 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 14920 | 1308 | 0.002 | -0.022–0.026 | 0.8898 | 0.948 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 14920 | 1164 | -0.018 | -0.047–0.010 | 0.2127 | 0.824 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 14920 | 1228 | 0.007 | -0.017–0.032 | 0.5652 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 14920 | 1269 | -0.010 | -0.035–0.014 | 0.4056 | 0.943 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 14920 | 1288 | 0.016 | -0.011–0.043 | 0.2447 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 14920 | 1320 | 0.009 | -0.017–0.036 | 0.5020 | 0.873 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 14920 | 1239 | -0.024 | -0.054–0.005 | 0.0993 | 0.789 | not_testable_yet (under-powered) |
| `place.l8_h7` | 14920 | 1173 | -0.038 | -0.067–-0.009 | 0.0097 | 0.827 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 14920 | 1240 | 0.011 | -0.018–0.040 | 0.4504 | 0.789 | not_testable_yet (under-powered) |
| `place.l8_h9` | 14920 | 1205 | 0.003 | -0.025–0.031 | 0.8293 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 14920 | 1269 | 0.001 | -0.026–0.028 | 0.9438 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 14920 | 1303 | 0.008 | -0.018–0.035 | 0.5406 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 14920 | 1240 | -0.008 | -0.036–0.019 | 0.5488 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 14920 | 1237 | 0.009 | -0.018–0.035 | 0.5312 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 14920 | 1266 | 0.008 | -0.019–0.035 | 0.5641 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 14920 | 1197 | 0.004 | -0.024–0.032 | 0.7694 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 14920 | 1191 | -0.023 | -0.053–0.006 | 0.1243 | 0.771 | not_testable_yet (under-powered) |
| `place.l9_h5` | 14920 | 1301 | 0.002 | -0.027–0.030 | 0.8968 | 0.810 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 14920 | 1243 | -0.010 | -0.038–0.017 | 0.4670 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 14920 | 1282 | -0.030 | -0.059–-0.001 | 0.0401 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l9_h8` | 14920 | 1240 | -0.009 | -0.037–0.018 | 0.5045 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 14920 | 1151 | -0.025 | -0.052–0.002 | 0.0725 | 0.822 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 14920 | 1276 | 0.010 | -0.019–0.038 | 0.5102 | 0.802 | classical_rejected (recommended: powered null) |
| `place.mars_h10` | 14920 | 1273 | 0.009 | -0.019–0.038 | 0.5246 | 0.800 | classical_rejected (recommended: powered null) |
| `place.mars_h11` | 14920 | 1170 | 0.011 | -0.019–0.040 | 0.4851 | 0.762 | not_testable_yet (under-powered) |
| `place.mars_h12` | 14920 | 1212 | 0.000 | -0.027–0.027 | 0.9850 | 0.844 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 14920 | 1219 | -0.014 | -0.043–0.015 | 0.3519 | 0.781 | not_testable_yet (under-powered) |
| `place.mars_h3` | 14920 | 1224 | 0.021 | -0.008–0.050 | 0.1536 | 0.783 | not_testable_yet (under-powered) |
| `place.mars_h4` | 14920 | 1296 | -0.022 | -0.047–0.004 | 0.0941 | 0.870 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 14920 | 1305 | 0.000 | -0.026–0.026 | 0.9779 | 0.871 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 14920 | 1176 | 0.002 | -0.027–0.032 | 0.8767 | 0.765 | not_testable_yet (under-powered) |
| `place.mars_h7` | 14920 | 1258 | 0.003 | -0.024–0.029 | 0.8342 | 0.859 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 14920 | 1300 | -0.011 | -0.039–0.017 | 0.4477 | 0.810 | classical_rejected (recommended: powered null) |
| `place.mars_h9` | 14920 | 1211 | -0.026 | -0.053–-0.000 | 0.0494 | 0.842 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 14920 | 932 | 0.023 | -0.010–0.056 | 0.1750 | 0.649 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 14920 | 1056 | -0.002 | -0.034–0.029 | 0.8820 | 0.713 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 14920 | 1490 | 0.016 | -0.010–0.043 | 0.2286 | 0.863 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 14920 | 963 | -0.029 | -0.061–0.004 | 0.0851 | 0.666 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 14920 | 1377 | -0.000 | -0.028–0.027 | 0.9880 | 0.833 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 14920 | 1584 | -0.011 | -0.037–0.015 | 0.4257 | 0.884 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 14920 | 1406 | 0.006 | -0.021–0.034 | 0.6569 | 0.841 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 14920 | 1053 | -0.012 | -0.043–0.019 | 0.4509 | 0.711 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 14920 | 1113 | -0.020 | -0.050–0.011 | 0.2028 | 0.739 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 14920 | 1083 | 0.045 | 0.014–0.075 | 0.0044 | 0.725 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 14920 | 1376 | -0.011 | -0.039–0.017 | 0.4363 | 0.833 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 14920 | 1487 | -0.004 | -0.031–0.023 | 0.7659 | 0.863 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 14920 | 1214 | 0.028 | -0.001–0.057 | 0.0622 | 0.779 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 14920 | 1224 | 0.004 | -0.025–0.034 | 0.7711 | 0.783 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 14920 | 1251 | -0.006 | -0.035–0.023 | 0.6828 | 0.793 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 14920 | 1246 | -0.006 | -0.033–0.020 | 0.6515 | 0.854 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 14920 | 1220 | 0.015 | -0.014–0.044 | 0.3115 | 0.781 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 14920 | 1327 | 0.011 | -0.017–0.039 | 0.4449 | 0.818 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 14920 | 1237 | 0.007 | -0.020–0.034 | 0.6181 | 0.855 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 14920 | 1264 | -0.002 | -0.028–0.025 | 0.8896 | 0.859 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 14920 | 1232 | -0.034 | -0.063–-0.005 | 0.0230 | 0.787 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 14920 | 1195 | -0.013 | -0.040–0.013 | 0.3240 | 0.839 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 14920 | 1303 | -0.016 | -0.045–0.012 | 0.2552 | 0.811 | classical_rejected (recommended: powered null) |
| `place.mercury_h9` | 14920 | 1207 | -0.000 | -0.027–0.027 | 0.9894 | 0.843 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 14920 | 1293 | 0.001 | -0.027–0.030 | 0.9242 | 0.807 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 14920 | 1086 | -0.021 | -0.052–0.009 | 0.1724 | 0.727 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 14920 | 1207 | 0.020 | -0.009–0.050 | 0.1749 | 0.777 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 14920 | 1304 | -0.003 | -0.031–0.026 | 0.8626 | 0.811 | classical_rejected (recommended: powered null) |
| `place.mercury_in_gemini` | 14920 | 1121 | 0.018 | -0.013–0.048 | 0.2504 | 0.742 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 14920 | 1270 | 0.001 | -0.028–0.030 | 0.9354 | 0.799 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 14920 | 1387 | 0.012 | -0.015–0.040 | 0.3778 | 0.836 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 14920 | 1229 | -0.017 | -0.047–0.012 | 0.2412 | 0.785 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 14920 | 1317 | -0.006 | -0.035–0.022 | 0.6599 | 0.815 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 14920 | 1371 | -0.004 | -0.032–0.024 | 0.7681 | 0.832 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 14920 | 1090 | -0.001 | -0.032–0.030 | 0.9654 | 0.728 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 14920 | 1245 | -0.002 | -0.031–0.027 | 0.9127 | 0.791 | not_testable_yet (under-powered) |
| `place.moon_h1` | 14920 | 1270 | -0.013 | -0.041–0.016 | 0.3889 | 0.800 | not_testable_yet (under-powered) |
| `place.moon_h10` | 14920 | 1290 | -0.013 | -0.041–0.016 | 0.3875 | 0.806 | classical_rejected (recommended: powered null) |
| `place.moon_h11` | 14920 | 1267 | 0.009 | -0.020–0.037 | 0.5601 | 0.798 | not_testable_yet (under-powered) |
| `place.moon_h12` | 14920 | 1217 | -0.011 | -0.038–0.016 | 0.4217 | 0.845 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 14920 | 1273 | -0.016 | -0.044–0.013 | 0.2874 | 0.801 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 14920 | 1204 | -0.006 | -0.036–0.023 | 0.6778 | 0.776 | not_testable_yet (under-powered) |
| `place.moon_h4` | 14920 | 1232 | 0.014 | -0.013–0.041 | 0.2971 | 0.854 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 14920 | 1275 | 0.001 | -0.025–0.028 | 0.9234 | 0.863 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 14920 | 1257 | 0.008 | -0.021–0.037 | 0.5960 | 0.795 | not_testable_yet (under-powered) |
| `place.moon_h7` | 14920 | 1156 | -0.005 | -0.032–0.023 | 0.7318 | 0.827 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 14920 | 1217 | -0.017 | -0.047–0.012 | 0.2437 | 0.781 | not_testable_yet (under-powered) |
| `place.moon_h9` | 14920 | 1262 | -0.011 | -0.037–0.015 | 0.4078 | 0.859 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 14920 | 1259 | 0.024 | -0.005–0.053 | 0.0988 | 0.796 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 14920 | 1242 | 0.003 | -0.026–0.032 | 0.8272 | 0.790 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 14920 | 1234 | -0.011 | -0.040–0.018 | 0.4671 | 0.787 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 14920 | 1275 | -0.007 | -0.033–0.020 | 0.6204 | 0.862 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 14920 | 1289 | 0.023 | -0.006–0.051 | 0.1193 | 0.806 | classical_rejected (recommended: powered null) |
| `place.rahu_h3` | 14920 | 1173 | 0.007 | -0.022–0.037 | 0.6297 | 0.763 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 14920 | 1196 | -0.010 | -0.037–0.017 | 0.4615 | 0.841 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 14920 | 1255 | -0.007 | -0.034–0.019 | 0.5854 | 0.856 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 14920 | 1260 | 0.004 | -0.025–0.033 | 0.7933 | 0.796 | not_testable_yet (under-powered) |
| `place.rahu_h7` | 14920 | 1275 | -0.003 | -0.030–0.023 | 0.8056 | 0.864 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 14920 | 1247 | -0.004 | -0.033–0.025 | 0.7727 | 0.792 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 14920 | 1215 | -0.015 | -0.041–0.012 | 0.2726 | 0.844 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 14920 | 1163 | -0.013 | -0.042–0.016 | 0.3694 | 0.821 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 14920 | 1194 | -0.019 | -0.047–0.010 | 0.1988 | 0.832 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 14920 | 1472 | -0.000 | -0.026–0.025 | 0.9972 | 0.906 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 14920 | 1062 | -0.011 | -0.041–0.019 | 0.4756 | 0.779 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 14920 | 1259 | -0.016 | -0.043–0.012 | 0.2649 | 0.853 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 14920 | 1562 | -0.004 | -0.029–0.021 | 0.7706 | 0.923 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 14920 | 1132 | -0.008 | -0.037–0.021 | 0.5732 | 0.809 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 14920 | 1150 | 0.028 | -0.000–0.056 | 0.0522 | 0.813 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 14920 | 1185 | 0.016 | -0.012–0.044 | 0.2599 | 0.827 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 14920 | 1129 | -0.006 | -0.035–0.022 | 0.6624 | 0.807 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 14920 | 1153 | 0.043 | 0.015–0.070 | 0.0025 | 0.814 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 14920 | 1459 | -0.006 | -0.032–0.019 | 0.6221 | 0.904 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 14920 | 1281 | 0.026 | -0.002–0.055 | 0.0723 | 0.803 | classical_rejected (recommended: powered null) |
| `place.saturn_h10` | 14920 | 1261 | 0.023 | -0.005–0.052 | 0.1116 | 0.796 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 14920 | 1278 | -0.013 | -0.042–0.015 | 0.3582 | 0.802 | classical_rejected (recommended: powered null) |
| `place.saturn_h12` | 14920 | 1236 | 0.022 | -0.005–0.049 | 0.1108 | 0.853 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 14920 | 1285 | -0.022 | -0.051–0.006 | 0.1250 | 0.805 | classical_rejected (recommended: powered null) |
| `place.saturn_h3` | 14920 | 1228 | -0.013 | -0.042–0.017 | 0.3986 | 0.785 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 14920 | 1243 | 0.020 | -0.007–0.047 | 0.1434 | 0.858 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 14920 | 1250 | 0.001 | -0.026–0.028 | 0.9453 | 0.855 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 14920 | 1216 | 0.028 | -0.001–0.057 | 0.0626 | 0.780 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 14920 | 1240 | -0.011 | -0.037–0.016 | 0.4208 | 0.853 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 14920 | 1214 | -0.009 | -0.038–0.020 | 0.5513 | 0.780 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 14920 | 1188 | 0.014 | -0.013–0.042 | 0.3114 | 0.837 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 14920 | 1219 | 0.020 | -0.005–0.044 | 0.1123 | 0.931 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 14920 | 1498 | 0.001 | -0.022–0.023 | 0.9530 | 0.972 | classical_rejected (recommended: powered null) |
| `place.saturn_in_cancer` | 14920 | 1080 | -0.019 | -0.046–0.008 | 0.1706 | 0.898 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 14920 | 1334 | -0.006 | -0.031–0.018 | 0.5997 | 0.953 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 14920 | 1056 | 0.023 | -0.003–0.049 | 0.0813 | 0.887 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 14920 | 1142 | 0.005 | -0.021–0.030 | 0.7259 | 0.914 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 14920 | 1257 | -0.002 | -0.026–0.023 | 0.8887 | 0.940 | classical_rejected (recommended: powered null) |
| `place.saturn_in_pisces` | 14920 | 1182 | 0.002 | -0.023–0.027 | 0.8716 | 0.924 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 14920 | 1303 | 0.013 | -0.010–0.037 | 0.2713 | 0.947 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 14920 | 1377 | -0.012 | -0.036–0.012 | 0.3352 | 0.959 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 14920 | 1215 | -0.014 | -0.040–0.011 | 0.2692 | 0.932 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 14920 | 1257 | -0.008 | -0.033–0.017 | 0.5352 | 0.940 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 14920 | 1206 | 0.035 | 0.006–0.065 | 0.0182 | 0.776 | not_testable_yet (under-powered) |
| `place.sun_h10` | 14920 | 1218 | -0.008 | -0.037–0.021 | 0.5879 | 0.781 | not_testable_yet (under-powered) |
| `place.sun_h11` | 14920 | 1303 | 0.002 | -0.026–0.031 | 0.8835 | 0.810 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 14920 | 1213 | -0.021 | -0.047–0.006 | 0.1265 | 0.843 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 14920 | 1278 | -0.001 | -0.030–0.027 | 0.9205 | 0.802 | classical_rejected (recommended: powered null) |
| `place.sun_h3` | 14920 | 1295 | 0.009 | -0.020–0.037 | 0.5368 | 0.808 | classical_rejected (recommended: powered null) |
| `place.sun_h4` | 14920 | 1272 | -0.026 | -0.052–-0.001 | 0.0440 | 0.863 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 14920 | 1256 | 0.013 | -0.014–0.040 | 0.3322 | 0.858 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 14920 | 1199 | -0.018 | -0.048–0.011 | 0.2225 | 0.774 | not_testable_yet (under-powered) |
| `place.sun_h7` | 14920 | 1210 | -0.006 | -0.033–0.021 | 0.6776 | 0.844 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 14920 | 1255 | -0.010 | -0.039–0.018 | 0.4795 | 0.795 | not_testable_yet (under-powered) |
| `place.sun_h9` | 14920 | 1215 | 0.000 | -0.027–0.027 | 0.9801 | 0.845 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 14920 | 1247 | -0.010 | -0.039–0.019 | 0.4824 | 0.791 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 14920 | 1215 | -0.009 | -0.039–0.020 | 0.5284 | 0.780 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 14920 | 1329 | 0.023 | -0.005–0.051 | 0.1038 | 0.819 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 14920 | 1253 | 0.001 | -0.028–0.030 | 0.9499 | 0.794 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 14920 | 1227 | 0.031 | 0.002–0.061 | 0.0346 | 0.784 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 14920 | 1264 | 0.008 | -0.021–0.037 | 0.5784 | 0.797 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 14920 | 1167 | 0.019 | -0.011–0.048 | 0.2223 | 0.761 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 14920 | 1240 | -0.018 | -0.047–0.011 | 0.2286 | 0.789 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 14920 | 1185 | -0.002 | -0.032–0.028 | 0.8936 | 0.768 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 14920 | 1225 | -0.017 | -0.047–0.012 | 0.2415 | 0.784 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 14920 | 1301 | -0.018 | -0.046–0.010 | 0.2131 | 0.810 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 14920 | 1267 | -0.007 | -0.036–0.022 | 0.6348 | 0.798 | not_testable_yet (under-powered) |
| `place.venus_h1` | 14920 | 1280 | -0.002 | -0.030–0.027 | 0.9155 | 0.803 | classical_rejected (recommended: powered null) |
| `place.venus_h10` | 14920 | 1178 | -0.013 | -0.043–0.016 | 0.3743 | 0.766 | not_testable_yet (under-powered) |
| `place.venus_h11` | 14920 | 1261 | -0.030 | -0.059–-0.002 | 0.0391 | 0.797 | not_testable_yet (under-powered) |
| `place.venus_h12` | 14920 | 1232 | -0.010 | -0.037–0.016 | 0.4427 | 0.850 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 14920 | 1276 | 0.009 | -0.020–0.038 | 0.5456 | 0.801 | classical_rejected (recommended: powered null) |
| `place.venus_h3` | 14920 | 1248 | -0.018 | -0.047–0.011 | 0.2280 | 0.792 | not_testable_yet (under-powered) |
| `place.venus_h4` | 14920 | 1245 | -0.008 | -0.035–0.018 | 0.5287 | 0.857 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 14920 | 1229 | -0.007 | -0.033–0.020 | 0.6211 | 0.849 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 14920 | 1254 | -0.008 | -0.037–0.021 | 0.5761 | 0.794 | not_testable_yet (under-powered) |
| `place.venus_h7` | 14920 | 1264 | -0.008 | -0.034–0.018 | 0.5379 | 0.860 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 14920 | 1215 | 0.005 | -0.024–0.034 | 0.7400 | 0.780 | not_testable_yet (under-powered) |
| `place.venus_h9` | 14920 | 1238 | 0.024 | -0.003–0.051 | 0.0813 | 0.854 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 14920 | 1083 | -0.005 | -0.033–0.023 | 0.7197 | 0.799 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 14920 | 1177 | -0.014 | -0.041–0.013 | 0.3013 | 0.833 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 14920 | 1099 | -0.018 | -0.045–0.010 | 0.2116 | 0.805 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 14920 | 1496 | 0.005 | -0.020–0.030 | 0.6871 | 0.914 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 14920 | 1400 | -0.007 | -0.032–0.018 | 0.5635 | 0.894 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 14920 | 1509 | 0.004 | -0.021–0.028 | 0.7724 | 0.916 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 14920 | 1379 | 0.006 | -0.019–0.032 | 0.6265 | 0.890 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 14920 | 1328 | 0.024 | -0.002–0.050 | 0.0715 | 0.879 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 14920 | 1060 | -0.003 | -0.032–0.025 | 0.8189 | 0.790 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 14920 | 1103 | -0.004 | -0.032–0.024 | 0.7738 | 0.807 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 14920 | 1228 | 0.007 | -0.020–0.034 | 0.5930 | 0.851 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 14920 | 1058 | -0.002 | -0.030–0.027 | 0.9066 | 0.789 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 14920 | 1853 | 0.012 | -0.012–0.036 | 0.3294 | 0.928 | classical_rejected (recommended: powered null) |
| `yoga.budhaditya` | 14920 | 7687 | 0.004 | -0.012–0.020 | 0.5986 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 14920 | 5030 | 0.000 | -0.016–0.016 | 0.9914 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 14920 | 1423 | 0.016 | -0.010–0.042 | 0.2165 | 0.893 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 14920 | 2572 | -0.004 | -0.025–0.017 | 0.7098 | 0.980 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja` | 14920 | 7982 | 0.005 | -0.011–0.021 | 0.5457 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 14920 | 9645 | 0.002 | -0.015–0.019 | 0.8087 | 0.999 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 14920 | 2588 | 0.004 | -0.017–0.026 | 0.6814 | 0.980 | classical_rejected (recommended: powered null) |
| `yoga.neecha_bhanga` | 14920 | 6592 | 0.013 | -0.003–0.029 | 0.1111 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.parivartana` | 14920 | 5579 | 0.000 | -0.016–0.016 | 0.9870 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 14920 | 2164 | 0.020 | -0.003–0.043 | 0.0867 | 0.959 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 14920 | 2698 | 0.017 | -0.004–0.038 | 0.1145 | 0.984 | classical_rejected (recommended: powered null) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
