# Synthetic — Validation — null, N = 20,000, odds ratio 1.0 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 14934 development, 5066 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `baa520e885d6df218ef3701f5e25063c0b43cf3cba4e3fe3fc258c042825dcc0` ({"salt_sha256": "b40112f146d454146b91259ad7adc209cdce21e41cabb6406ccc8d9a7c66e9c2", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "4c87c96d886a1424b200197495b363a1035e738eca099a9b0ac24a69b16ad344"})
- analysis code `494dae55f6a48ddf1c97767f4f82d77adf00c78f1bdbab2488c65c423b7b012c`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 14934 | 1.000 | 0.300 | 0.994 | 0.962–1.025 | 0.6763 | 0.8657 | no | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 14934 | 1.000 | 0.509 | 1.011 | 0.988–1.035 | 0.1908 | 0.8657 | no | 0.999 |
| children | 14934 | 1.000 | 0.305 | 0.995 | 0.958–1.034 | 0.6044 | 0.8657 | no | 0.999 |
| intellect | 14934 | 1.000 | 0.303 | 0.991 | 0.956–1.027 | 0.7083 | 0.8657 | no | 1.000 |
| health | 14934 | 1.000 | 0.509 | 1.000 | 0.981–1.018 | 0.4805 | 0.8657 | no | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 14934 | 1.000 | 0.297 | 1.006 | 0.966–1.045 | 0.3766 | 0.8657 | no | 0.999 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 14934 | 1.000 | 0.303 | 0.978 | 0.945–1.012 | 0.8901 | 0.8901 | no | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 14934 | 1.000 | 0.512 | 1.005 | 0.980–1.027 | 0.3976 | 0.8657 | no | 0.999 |
| gains | 14934 | 1.000 | 0.300 | 0.995 | 0.965–1.028 | 0.5864 | 0.8657 | no | 1.000 |
| foreign | 14934 | 1.000 | 0.304 | 0.983 | 0.952–1.018 | 0.8621 | 0.8901 | no | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 14934 | 1.000 | 0.303 | 1.015 | 0.979–1.051 | 0.1858 | 0.8657 | no | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14934 | 1.000 | 8 | 4.18 | 8 | 0.8406 | 0.498 | 0.496 | 0.4796 |
| mother_home | 14934 | 1.000 | 8 | 13.04 | 8 | 0.1105 | 0.494 | 0.498 | 0.2390 |
| children | 14934 | 1.000 | 7 | 2.08 | 7 | 0.9555 | 0.500 | 0.496 | 0.3616 |
| intellect | 14934 | 1.000 | 8 | 22.00 | 8 | 0.0049 | 0.498 | 0.512 | 0.0037 |
| health | 14934 | 1.000 | 8 | 2.33 | 8 | 0.9691 | 0.496 | 0.492 | 0.2157 |
| marriage | 14934 | 1.000 | 8 | 5.89 | 8 | 0.6597 | 0.494 | 0.487 | 0.0120 |
| father | 14934 | 1.000 | 7 | 8.65 | 7 | 0.2792 | 0.496 | 0.495 | 0.7920 |
| career | 14934 | 1.000 | 8 | 7.35 | 8 | 0.4997 | 0.499 | 0.501 | 0.6009 |
| gains | 14934 | 1.000 | 8 | 6.25 | 8 | 0.6196 | 0.498 | 0.497 | 0.6734 |
| foreign | 14934 | 1.000 | 7 | 5.05 | 7 | 0.6537 | 0.494 | 0.493 | 0.9380 |
| reputation | 14934 | 1.000 | 8 | 21.41 | 8 | 0.0061 | 0.498 | 0.513 | 0.0022 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14934 | 1.000 | 724118 | 4475 | 0.932 | 1.054 | 0.0199 | 0.053 (-0.067, 0.173) |
| mother_home | 14934 | 1.000 | 622402 | 7598 | 0.943 | 0.989 | 0.0348 | -0.011 (-0.109, 0.086) |
| children | 14934 | 1.000 | 722490 | 4562 | 0.903 | 1.003 | 0.4030 | 0.003 (-0.095, 0.102) |
| intellect | 14934 | 1.000 | 723349 | 4530 | 0.946 | 0.978 | 0.1244 | -0.023 (-0.151, 0.105) |
| health | 14934 | 1.000 | 626186 | 7604 | 0.939 | 1.012 | 0.0995 | 0.012 (-0.083, 0.107) |
| marriage | 14934 | 1.000 | 726280 | 4442 | 0.940 | 0.937 | 0.7015 | -0.066 (-0.187, 0.055) |
| father | 14934 | 1.000 | 722096 | 4522 | 0.879 | 0.979 | 0.2139 | -0.022 (-0.110, 0.067) |
| career | 14934 | 1.000 | 623593 | 7649 | 0.953 | 1.110 | 0.0050 | 0.105 (-0.007, 0.218) |
| gains | 14934 | 1.000 | 724118 | 4475 | 0.869 | 1.022 | 0.1045 | 0.021 (-0.066, 0.109) |
| foreign | 14934 | 1.000 | 723340 | 4536 | 0.951 | 1.053 | 0.0249 | 0.052 (-0.087, 0.192) |
| reputation | 14934 | 1.000 | 723349 | 4530 | 0.892 | 1.044 | 0.1095 | 0.043 (-0.052, 0.139) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14934 | 1.000 | 0.009 | 0.006 | 5 | 0 | not allowed |
| mother_home | 14934 | 1.000 | 0.001 | 0.015 | 4 | 0 | not allowed |
| children | 14934 | 1.000 | 0.009 | 0.005 | 4 | 1 | not allowed |
| intellect | 14934 | 1.000 | 0.010 | 0.016 | 4 | 0 | not allowed |
| health | 14934 | 1.000 | 0.011 | 0.005 | 6 | 0 | not allowed |
| marriage | 14934 | 1.000 | 0.013 | 0.012 | 3 | 0 | not allowed |
| father | 14934 | 1.000 | 0.003 | 0.011 | 2 | 1 | not allowed |
| career | 14934 | 1.000 | 0.006 | 0.012 | 3 | 2 | not allowed |
| gains | 14934 | 1.000 | 0.007 | 0.011 | 5 | 0 | not allowed |
| foreign | 14934 | 1.000 | 0.007 | 0.008 | 3 | 0 | not allowed |
| reputation | 14934 | 1.000 | 0.018 | 0.016 | 5 | 0 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 14934 | 1.000 | 5381 | 1.000 | 1.000 |
| mother_home | 14934 | 1.000 | 4372 | 0.999 | 1.000 |
| children | 14934 | 1.000 | 4006 | 0.999 | 1.000 |
| intellect | 14934 | 1.000 | 4688 | 1.000 | 1.000 |
| health | 14934 | 1.000 | 6235 | 1.000 | 1.000 |
| marriage | 14934 | 1.000 | 4085 | 0.999 | 1.000 |
| father | 14934 | 1.000 | 5254 | 1.000 | 1.000 |
| career | 14934 | 1.000 | 4458 | 0.999 | 1.000 |
| gains | 14934 | 1.000 | 5150 | 1.000 | 1.000 |
| foreign | 14934 | 1.000 | 5648 | 1.000 | 1.000 |
| reputation | 14934 | 1.000 | 4559 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 251 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 109 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 14934 | 1205 | 0.002 | -0.027–0.032 | 0.8831 | 0.776 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 14934 | 1269 | 0.008 | -0.021–0.037 | 0.5957 | 0.799 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 14934 | 1295 | -0.015 | -0.044–0.013 | 0.2877 | 0.808 | classical_rejected (recommended: powered null) |
| `place.jupiter_h12` | 14934 | 1254 | 0.028 | 0.001–0.055 | 0.0434 | 0.857 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 14934 | 1217 | 0.004 | -0.025–0.033 | 0.7799 | 0.781 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 14934 | 1263 | 0.002 | -0.027–0.031 | 0.9013 | 0.797 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 14934 | 1271 | 0.016 | -0.010–0.043 | 0.2262 | 0.864 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 14934 | 1223 | -0.032 | -0.058–-0.005 | 0.0178 | 0.843 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 14934 | 1246 | -0.000 | -0.029–0.029 | 0.9797 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 14934 | 1228 | -0.013 | -0.039–0.014 | 0.3477 | 0.851 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 14934 | 1221 | 0.001 | -0.028–0.030 | 0.9381 | 0.782 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 14934 | 1242 | -0.002 | -0.029–0.025 | 0.8850 | 0.852 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 14934 | 1168 | 0.004 | -0.025–0.032 | 0.8043 | 0.824 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 14934 | 1310 | -0.013 | -0.040–0.014 | 0.3347 | 0.870 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 14934 | 1325 | 0.010 | -0.016–0.037 | 0.4563 | 0.873 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_capricorn` | 14934 | 1275 | -0.009 | -0.037–0.018 | 0.5064 | 0.860 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_gemini` | 14934 | 1177 | 0.016 | -0.012–0.044 | 0.2738 | 0.827 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_leo` | 14934 | 1325 | -0.005 | -0.032–0.022 | 0.7245 | 0.874 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 14934 | 1362 | 0.010 | -0.016–0.037 | 0.4411 | 0.883 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 14934 | 1053 | -0.024 | -0.054–0.006 | 0.1219 | 0.779 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 14934 | 1210 | 0.016 | -0.011–0.044 | 0.2466 | 0.838 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 14934 | 1243 | -0.017 | -0.045–0.011 | 0.2229 | 0.851 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 14934 | 1202 | 0.004 | -0.024–0.032 | 0.7797 | 0.836 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 14934 | 1284 | 0.006 | -0.021–0.033 | 0.6536 | 0.862 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 14934 | 1295 | -0.007 | -0.036–0.021 | 0.6260 | 0.808 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 14934 | 1208 | -0.015 | -0.044–0.014 | 0.3155 | 0.777 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 14934 | 1243 | 0.003 | -0.026–0.032 | 0.8425 | 0.790 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 14934 | 1278 | -0.000 | -0.027–0.026 | 0.9911 | 0.862 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 14934 | 1225 | -0.012 | -0.041–0.017 | 0.4232 | 0.784 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 14934 | 1222 | -0.026 | -0.055–0.003 | 0.0844 | 0.783 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 14934 | 1225 | 0.002 | -0.025–0.029 | 0.9003 | 0.850 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 14934 | 1236 | -0.003 | -0.030–0.024 | 0.8175 | 0.849 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 14934 | 1262 | 0.012 | -0.017–0.040 | 0.4293 | 0.796 | not_testable_yet (under-powered) |
| `place.ketu_h7` | 14934 | 1271 | 0.013 | -0.014–0.039 | 0.3423 | 0.865 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 14934 | 1263 | -0.022 | -0.051–0.007 | 0.1400 | 0.797 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 14934 | 1206 | -0.014 | -0.041–0.013 | 0.3121 | 0.840 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 14934 | 1571 | -0.006 | -0.030–0.018 | 0.6341 | 0.924 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 14934 | 1116 | 0.002 | -0.026–0.030 | 0.8909 | 0.810 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 14934 | 1079 | -0.025 | -0.053–0.003 | 0.0825 | 0.794 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 14934 | 1499 | -0.014 | -0.039–0.010 | 0.2478 | 0.912 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 14934 | 1208 | 0.028 | 0.000–0.056 | 0.0467 | 0.843 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 14934 | 1152 | 0.007 | -0.021–0.034 | 0.6378 | 0.823 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 14934 | 1160 | -0.012 | -0.039–0.016 | 0.4078 | 0.825 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 14934 | 1433 | -0.017 | -0.042–0.008 | 0.1729 | 0.899 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 14934 | 1280 | -0.002 | -0.029–0.024 | 0.8593 | 0.863 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 14934 | 1156 | 0.011 | -0.017–0.039 | 0.4328 | 0.825 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 14934 | 1124 | -0.001 | -0.029–0.027 | 0.9247 | 0.813 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 14934 | 1156 | 0.036 | 0.008–0.065 | 0.0116 | 0.826 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 14934 | 1305 | -0.029 | -0.054–-0.004 | 0.0215 | 0.950 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 14934 | 1266 | 0.020 | -0.008–0.049 | 0.1653 | 0.798 | not_testable_yet (under-powered) |
| `place.l10_h11` | 14934 | 1264 | 0.001 | -0.027–0.030 | 0.9252 | 0.798 | not_testable_yet (under-powered) |
| `place.l10_h12` | 14934 | 1221 | -0.001 | -0.029–0.027 | 0.9403 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 14934 | 1222 | -0.011 | -0.040–0.019 | 0.4776 | 0.783 | not_testable_yet (under-powered) |
| `place.l10_h3` | 14934 | 1227 | -0.009 | -0.038–0.020 | 0.5333 | 0.784 | not_testable_yet (under-powered) |
| `place.l10_h4` | 14934 | 1288 | -0.002 | -0.029–0.025 | 0.8765 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 14934 | 1204 | 0.001 | -0.027–0.029 | 0.9457 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 14934 | 1209 | 0.006 | -0.019–0.031 | 0.6481 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 14934 | 1235 | -0.011 | -0.039–0.017 | 0.4487 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 14934 | 1262 | 0.015 | -0.009–0.039 | 0.2314 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 14934 | 1231 | -0.015 | -0.043–0.013 | 0.2965 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 14934 | 1252 | 0.008 | -0.016–0.033 | 0.5001 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 14934 | 1211 | 0.010 | -0.020–0.039 | 0.5192 | 0.778 | not_testable_yet (under-powered) |
| `place.l11_h11` | 14934 | 1227 | 0.008 | -0.022–0.037 | 0.6103 | 0.784 | not_testable_yet (under-powered) |
| `place.l11_h12` | 14934 | 1247 | -0.021 | -0.049–0.007 | 0.1338 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 14934 | 1242 | -0.003 | -0.032–0.026 | 0.8525 | 0.790 | not_testable_yet (under-powered) |
| `place.l11_h3` | 14934 | 1225 | -0.014 | -0.043–0.016 | 0.3575 | 0.784 | not_testable_yet (under-powered) |
| `place.l11_h4` | 14934 | 1270 | -0.015 | -0.043–0.012 | 0.2772 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 14934 | 1232 | 0.024 | -0.004–0.051 | 0.0900 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 14934 | 1283 | -0.003 | -0.027–0.022 | 0.8348 | 0.944 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 14934 | 1257 | 0.019 | -0.008–0.047 | 0.1600 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 14934 | 1213 | -0.001 | -0.026–0.024 | 0.9088 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 14934 | 1275 | 0.011 | -0.017–0.038 | 0.4466 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 14934 | 1249 | 0.018 | -0.010–0.045 | 0.2066 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 14934 | 1271 | 0.005 | -0.022–0.032 | 0.7153 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 14934 | 1230 | 0.006 | -0.021–0.034 | 0.6645 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 14934 | 1172 | -0.010 | -0.037–0.017 | 0.4639 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 14934 | 1222 | 0.005 | -0.023–0.032 | 0.7450 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 14934 | 1334 | 0.017 | -0.010–0.043 | 0.2127 | 0.874 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 14934 | 1279 | -0.006 | -0.035–0.022 | 0.6579 | 0.803 | classical_rejected (recommended: powered null) |
| `place.l12_h5` | 14934 | 1202 | -0.016 | -0.046–0.013 | 0.2842 | 0.776 | not_testable_yet (under-powered) |
| `place.l12_h6` | 14934 | 1206 | 0.009 | -0.018–0.037 | 0.5089 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 14934 | 1248 | 0.012 | -0.017–0.041 | 0.4200 | 0.792 | not_testable_yet (under-powered) |
| `place.l12_h8` | 14934 | 1292 | -0.017 | -0.045–0.010 | 0.2170 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 14934 | 1229 | -0.012 | -0.038–0.015 | 0.3849 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 14934 | 1170 | 0.009 | -0.021–0.038 | 0.5723 | 0.762 | not_testable_yet (under-powered) |
| `place.l1_h10` | 14934 | 1197 | -0.023 | -0.049–0.003 | 0.0793 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 14934 | 1268 | -0.003 | -0.028–0.021 | 0.8045 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 14934 | 1252 | 0.003 | -0.025–0.030 | 0.8487 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 14934 | 1267 | -0.005 | -0.030–0.020 | 0.6886 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 14934 | 1212 | 0.007 | -0.017–0.032 | 0.5629 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 14934 | 1320 | 0.007 | -0.020–0.033 | 0.6313 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 14934 | 1215 | -0.005 | -0.033–0.023 | 0.7147 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 14934 | 1272 | 0.016 | -0.013–0.044 | 0.2820 | 0.800 | not_testable_yet (under-powered) |
| `place.l1_h7` | 14934 | 1187 | -0.013 | -0.042–0.015 | 0.3635 | 0.827 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 14934 | 1266 | 0.006 | -0.023–0.034 | 0.7074 | 0.798 | not_testable_yet (under-powered) |
| `place.l1_h9` | 14934 | 1308 | 0.007 | -0.020–0.034 | 0.6169 | 0.868 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 14934 | 1223 | 0.015 | -0.009–0.039 | 0.2311 | 0.931 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 14934 | 1304 | 0.007 | -0.022–0.035 | 0.6381 | 0.811 | classical_rejected (recommended: powered null) |
| `place.l2_h11` | 14934 | 1211 | -0.029 | -0.058–0.000 | 0.0530 | 0.779 | not_testable_yet (under-powered) |
| `place.l2_h12` | 14934 | 1337 | -0.008 | -0.035–0.019 | 0.5639 | 0.876 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 14934 | 1158 | 0.011 | -0.019–0.041 | 0.4665 | 0.758 | not_testable_yet (under-powered) |
| `place.l2_h3` | 14934 | 1274 | -0.001 | -0.030–0.027 | 0.9287 | 0.801 | classical_rejected (recommended: powered null) |
| `place.l2_h4` | 14934 | 1201 | 0.017 | -0.011–0.044 | 0.2404 | 0.831 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 14934 | 1274 | -0.012 | -0.040–0.015 | 0.3850 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 14934 | 1251 | 0.006 | -0.018–0.031 | 0.6056 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 14934 | 1254 | 0.009 | -0.018–0.036 | 0.5180 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 14934 | 1239 | -0.004 | -0.029–0.021 | 0.7563 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 14934 | 1208 | 0.000 | -0.028–0.028 | 0.9811 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 14934 | 1300 | -0.003 | -0.028–0.021 | 0.7847 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 14934 | 1230 | 0.031 | 0.002–0.060 | 0.0366 | 0.785 | not_testable_yet (under-powered) |
| `place.l3_h11` | 14934 | 1324 | -0.014 | -0.042–0.014 | 0.3238 | 0.818 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 14934 | 1219 | 0.014 | -0.013–0.042 | 0.3050 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 14934 | 1220 | -0.014 | -0.043–0.015 | 0.3430 | 0.782 | not_testable_yet (under-powered) |
| `place.l3_h3` | 14934 | 1271 | -0.004 | -0.033–0.024 | 0.7698 | 0.800 | classical_rejected (recommended: powered null) |
| `place.l3_h4` | 14934 | 1260 | 0.018 | -0.009–0.045 | 0.1936 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 14934 | 1255 | -0.020 | -0.047–0.008 | 0.1639 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 14934 | 1233 | -0.005 | -0.030–0.020 | 0.6822 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 14934 | 1216 | 0.006 | -0.022–0.033 | 0.6927 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 14934 | 1202 | -0.009 | -0.035–0.016 | 0.4739 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 14934 | 1204 | -0.003 | -0.031–0.025 | 0.8498 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 14934 | 1232 | 0.032 | 0.004–0.059 | 0.0228 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 14934 | 1217 | -0.010 | -0.038–0.018 | 0.4878 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 14934 | 1220 | -0.010 | -0.038–0.018 | 0.4897 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 14934 | 1316 | 0.024 | -0.005–0.052 | 0.1002 | 0.815 | classical_rejected (recommended: powered null) |
| `place.l4_h2` | 14934 | 1274 | -0.000 | -0.028–0.027 | 0.9813 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 14934 | 1210 | 0.010 | -0.017–0.038 | 0.4663 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 14934 | 1225 | -0.005 | -0.032–0.021 | 0.6913 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 14934 | 1305 | -0.005 | -0.034–0.023 | 0.7151 | 0.812 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 14934 | 1255 | -0.026 | -0.053–0.002 | 0.0710 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 14934 | 1219 | 0.009 | -0.020–0.038 | 0.5543 | 0.781 | not_testable_yet (under-powered) |
| `place.l4_h8` | 14934 | 1201 | -0.000 | -0.028–0.028 | 0.9979 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 14934 | 1260 | 0.018 | -0.010–0.047 | 0.2112 | 0.796 | not_testable_yet (under-powered) |
| `place.l5_h1` | 14934 | 1268 | 0.002 | -0.025–0.029 | 0.8885 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 14934 | 1315 | -0.010 | -0.037–0.017 | 0.4591 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 14934 | 1228 | 0.011 | -0.017–0.038 | 0.4388 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 14934 | 1174 | 0.021 | -0.009–0.051 | 0.1672 | 0.764 | not_testable_yet (under-powered) |
| `place.l5_h2` | 14934 | 1273 | -0.011 | -0.038–0.017 | 0.4427 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 14934 | 1296 | 0.000 | -0.027–0.027 | 0.9838 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 14934 | 1220 | 0.007 | -0.023–0.036 | 0.6513 | 0.782 | not_testable_yet (under-powered) |
| `place.l5_h5` | 14934 | 1210 | -0.028 | -0.054–-0.001 | 0.0413 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 14934 | 1183 | 0.002 | -0.026–0.030 | 0.8837 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 14934 | 1240 | -0.004 | -0.033–0.025 | 0.8073 | 0.789 | not_testable_yet (under-powered) |
| `place.l5_h8` | 14934 | 1310 | -0.013 | -0.040–0.014 | 0.3501 | 0.870 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 14934 | 1217 | -0.003 | -0.032–0.026 | 0.8319 | 0.781 | not_testable_yet (under-powered) |
| `place.l6_h1` | 14934 | 1250 | 0.014 | -0.014–0.043 | 0.3281 | 0.792 | not_testable_yet (under-powered) |
| `place.l6_h10` | 14934 | 1240 | 0.011 | -0.013–0.036 | 0.3665 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 14934 | 1290 | -0.005 | -0.029–0.020 | 0.7136 | 0.945 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 14934 | 1292 | 0.012 | -0.014–0.039 | 0.3630 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 14934 | 1274 | -0.017 | -0.042–0.008 | 0.1729 | 0.943 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 14934 | 1192 | -0.002 | -0.028–0.023 | 0.8537 | 0.926 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 14934 | 1210 | 0.009 | -0.019–0.037 | 0.5233 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l6_h5` | 14934 | 1225 | -0.000 | -0.028–0.027 | 0.9801 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 14934 | 1212 | -0.022 | -0.051–0.008 | 0.1482 | 0.779 | not_testable_yet (under-powered) |
| `place.l6_h7` | 14934 | 1238 | -0.014 | -0.042–0.014 | 0.3294 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 14934 | 1219 | -0.010 | -0.039–0.020 | 0.5231 | 0.781 | not_testable_yet (under-powered) |
| `place.l6_h9` | 14934 | 1292 | 0.021 | -0.006–0.048 | 0.1243 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 14934 | 1246 | 0.012 | -0.015–0.040 | 0.3797 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 14934 | 1266 | 0.022 | -0.005–0.049 | 0.1102 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 14934 | 1238 | 0.005 | -0.022–0.033 | 0.7144 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 14934 | 1293 | -0.002 | -0.031–0.026 | 0.8875 | 0.807 | classical_rejected (recommended: powered null) |
| `place.l7_h2` | 14934 | 1154 | 0.005 | -0.024–0.033 | 0.7524 | 0.815 | classical_rejected (recommended: powered null) |
| `place.l7_h3` | 14934 | 1330 | -0.000 | -0.027–0.026 | 0.9789 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 14934 | 1226 | 0.002 | -0.027–0.031 | 0.8885 | 0.783 | not_testable_yet (under-powered) |
| `place.l7_h5` | 14934 | 1264 | 0.001 | -0.027–0.030 | 0.9252 | 0.798 | not_testable_yet (under-powered) |
| `place.l7_h6` | 14934 | 1204 | -0.014 | -0.042–0.014 | 0.3307 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 14934 | 1223 | -0.006 | -0.033–0.021 | 0.6568 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 14934 | 1253 | -0.011 | -0.039–0.017 | 0.4385 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 14934 | 1237 | 0.018 | -0.011–0.047 | 0.2283 | 0.788 | not_testable_yet (under-powered) |
| `place.l8_h1` | 14934 | 1281 | 0.011 | -0.018–0.040 | 0.4559 | 0.803 | classical_rejected (recommended: powered null) |
| `place.l8_h10` | 14934 | 1181 | 0.013 | -0.012–0.038 | 0.3176 | 0.922 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 14934 | 1325 | -0.003 | -0.027–0.021 | 0.7825 | 0.951 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 14934 | 1191 | -0.018 | -0.046–0.010 | 0.2129 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 14934 | 1207 | 0.018 | -0.006–0.042 | 0.1494 | 0.928 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 14934 | 1237 | -0.011 | -0.036–0.015 | 0.4101 | 0.936 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 14934 | 1286 | -0.001 | -0.028–0.026 | 0.9602 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 14934 | 1302 | 0.002 | -0.025–0.028 | 0.9097 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 14934 | 1248 | -0.018 | -0.047–0.011 | 0.2265 | 0.792 | not_testable_yet (under-powered) |
| `place.l8_h7` | 14934 | 1200 | -0.023 | -0.051–0.006 | 0.1195 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 14934 | 1267 | 0.009 | -0.020–0.037 | 0.5616 | 0.798 | not_testable_yet (under-powered) |
| `place.l8_h9` | 14934 | 1209 | 0.008 | -0.020–0.035 | 0.5937 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 14934 | 1254 | 0.002 | -0.025–0.030 | 0.8644 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 14934 | 1288 | 0.009 | -0.018–0.036 | 0.5090 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 14934 | 1202 | 0.000 | -0.028–0.028 | 0.9835 | 0.835 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 14934 | 1303 | 0.005 | -0.021–0.031 | 0.6955 | 0.870 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 14934 | 1265 | 0.016 | -0.011–0.043 | 0.2384 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 14934 | 1208 | 0.000 | -0.028–0.028 | 0.9811 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 14934 | 1185 | -0.018 | -0.047–0.012 | 0.2439 | 0.769 | not_testable_yet (under-powered) |
| `place.l9_h5` | 14934 | 1336 | -0.015 | -0.043–0.013 | 0.3018 | 0.822 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 14934 | 1222 | -0.006 | -0.033–0.022 | 0.6983 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 14934 | 1246 | -0.024 | -0.053–0.005 | 0.1054 | 0.791 | not_testable_yet (under-powered) |
| `place.l9_h8` | 14934 | 1217 | 0.004 | -0.024–0.031 | 0.7945 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 14934 | 1208 | -0.018 | -0.045–0.009 | 0.1872 | 0.841 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 14934 | 1297 | 0.009 | -0.020–0.037 | 0.5376 | 0.808 | classical_rejected (recommended: powered null) |
| `place.mars_h10` | 14934 | 1287 | 0.014 | -0.014–0.043 | 0.3262 | 0.805 | classical_rejected (recommended: powered null) |
| `place.mars_h11` | 14934 | 1186 | 0.010 | -0.020–0.039 | 0.5229 | 0.769 | not_testable_yet (under-powered) |
| `place.mars_h12` | 14934 | 1245 | -0.008 | -0.035–0.018 | 0.5533 | 0.852 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 14934 | 1207 | 0.011 | -0.019–0.040 | 0.4786 | 0.777 | not_testable_yet (under-powered) |
| `place.mars_h3` | 14934 | 1236 | 0.010 | -0.019–0.039 | 0.5156 | 0.788 | not_testable_yet (under-powered) |
| `place.mars_h4` | 14934 | 1223 | -0.024 | -0.050–0.003 | 0.0784 | 0.848 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 14934 | 1287 | 0.001 | -0.026–0.027 | 0.9571 | 0.864 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 14934 | 1195 | 0.015 | -0.014–0.045 | 0.3180 | 0.772 | not_testable_yet (under-powered) |
| `place.mars_h7` | 14934 | 1238 | 0.031 | 0.003–0.058 | 0.0273 | 0.857 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 14934 | 1260 | -0.005 | -0.034–0.024 | 0.7434 | 0.796 | not_testable_yet (under-powered) |
| `place.mars_h9` | 14934 | 1273 | -0.012 | -0.038–0.014 | 0.3797 | 0.860 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 14934 | 900 | 0.011 | -0.023–0.044 | 0.5341 | 0.632 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 14934 | 1081 | 0.008 | -0.023–0.039 | 0.5987 | 0.724 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 14934 | 1484 | 0.023 | -0.004–0.050 | 0.0902 | 0.862 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 14934 | 983 | -0.041 | -0.073–-0.009 | 0.0133 | 0.677 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 14934 | 1361 | 0.013 | -0.015–0.041 | 0.3650 | 0.829 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 14934 | 1603 | -0.020 | -0.045–0.006 | 0.1382 | 0.888 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 14934 | 1413 | 0.017 | -0.011–0.044 | 0.2334 | 0.843 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 14934 | 1078 | -0.016 | -0.047–0.015 | 0.3075 | 0.723 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 14934 | 1133 | -0.024 | -0.054–0.006 | 0.1177 | 0.748 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 14934 | 1083 | 0.029 | -0.002–0.060 | 0.0637 | 0.725 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 14934 | 1328 | -0.006 | -0.034–0.022 | 0.6795 | 0.819 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 14934 | 1487 | -0.000 | -0.027–0.026 | 0.9729 | 0.863 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 14934 | 1225 | 0.026 | -0.003–0.055 | 0.0803 | 0.783 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 14934 | 1230 | 0.014 | -0.015–0.043 | 0.3400 | 0.785 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 14934 | 1243 | -0.001 | -0.030–0.028 | 0.9693 | 0.790 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 14934 | 1284 | -0.009 | -0.035–0.017 | 0.4819 | 0.864 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 14934 | 1170 | 0.013 | -0.017–0.043 | 0.4021 | 0.762 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 14934 | 1320 | 0.011 | -0.017–0.039 | 0.4562 | 0.816 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 14934 | 1244 | 0.005 | -0.021–0.032 | 0.6883 | 0.856 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 14934 | 1256 | -0.002 | -0.029–0.024 | 0.8636 | 0.855 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 14934 | 1230 | -0.040 | -0.069–-0.011 | 0.0069 | 0.785 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 14934 | 1189 | -0.021 | -0.047–0.006 | 0.1271 | 0.839 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 14934 | 1294 | -0.004 | -0.033–0.024 | 0.7769 | 0.807 | classical_rejected (recommended: powered null) |
| `place.mercury_h9` | 14934 | 1249 | 0.007 | -0.020–0.033 | 0.6254 | 0.854 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 14934 | 1288 | -0.012 | -0.040–0.017 | 0.4246 | 0.806 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 14934 | 1102 | -0.003 | -0.034–0.027 | 0.8300 | 0.734 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 14934 | 1191 | 0.020 | -0.009–0.050 | 0.1834 | 0.771 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 14934 | 1269 | 0.002 | -0.027–0.031 | 0.9049 | 0.799 | not_testable_yet (under-powered) |
| `place.mercury_in_gemini` | 14934 | 1153 | 0.018 | -0.012–0.048 | 0.2323 | 0.755 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 14934 | 1253 | -0.002 | -0.031–0.027 | 0.8701 | 0.794 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 14934 | 1358 | -0.010 | -0.038–0.018 | 0.4750 | 0.828 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 14934 | 1218 | -0.011 | -0.040–0.019 | 0.4788 | 0.781 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 14934 | 1320 | -0.009 | -0.037–0.019 | 0.5227 | 0.816 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 14934 | 1374 | 0.003 | -0.025–0.030 | 0.8537 | 0.833 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 14934 | 1108 | -0.004 | -0.035–0.026 | 0.7785 | 0.737 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 14934 | 1300 | 0.011 | -0.017–0.040 | 0.4446 | 0.810 | classical_rejected (recommended: powered null) |
| `place.moon_h1` | 14934 | 1236 | -0.017 | -0.046–0.012 | 0.2506 | 0.787 | not_testable_yet (under-powered) |
| `place.moon_h10` | 14934 | 1287 | -0.004 | -0.033–0.024 | 0.7623 | 0.805 | classical_rejected (recommended: powered null) |
| `place.moon_h11` | 14934 | 1233 | 0.007 | -0.022–0.037 | 0.6141 | 0.786 | not_testable_yet (under-powered) |
| `place.moon_h12` | 14934 | 1213 | 0.005 | -0.022–0.032 | 0.7179 | 0.843 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 14934 | 1304 | 0.004 | -0.024–0.033 | 0.7670 | 0.811 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 14934 | 1216 | 0.000 | -0.029–0.029 | 0.9914 | 0.780 | not_testable_yet (under-powered) |
| `place.moon_h4` | 14934 | 1263 | 0.019 | -0.008–0.045 | 0.1727 | 0.862 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 14934 | 1271 | 0.003 | -0.023–0.030 | 0.8123 | 0.859 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 14934 | 1264 | 0.005 | -0.024–0.033 | 0.7506 | 0.797 | not_testable_yet (under-powered) |
| `place.moon_h7` | 14934 | 1189 | 0.005 | -0.022–0.032 | 0.7250 | 0.840 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 14934 | 1201 | -0.013 | -0.043–0.016 | 0.3823 | 0.774 | not_testable_yet (under-powered) |
| `place.moon_h9` | 14934 | 1257 | -0.007 | -0.033–0.020 | 0.6154 | 0.856 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 14934 | 1271 | 0.025 | -0.004–0.053 | 0.0901 | 0.800 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 14934 | 1225 | 0.010 | -0.019–0.039 | 0.4897 | 0.784 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 14934 | 1236 | -0.004 | -0.033–0.026 | 0.8093 | 0.788 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 14934 | 1262 | 0.006 | -0.021–0.032 | 0.6703 | 0.858 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 14934 | 1263 | 0.026 | -0.003–0.055 | 0.0759 | 0.797 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 14934 | 1206 | 0.016 | -0.014–0.045 | 0.2980 | 0.776 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 14934 | 1208 | -0.008 | -0.035–0.019 | 0.5537 | 0.844 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 14934 | 1243 | -0.005 | -0.032–0.022 | 0.7125 | 0.851 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 14934 | 1278 | 0.006 | -0.022–0.035 | 0.6702 | 0.802 | classical_rejected (recommended: powered null) |
| `place.rahu_h7` | 14934 | 1295 | -0.008 | -0.034–0.018 | 0.5564 | 0.871 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 14934 | 1225 | -0.011 | -0.041–0.018 | 0.4474 | 0.783 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 14934 | 1222 | -0.030 | -0.056–-0.003 | 0.0272 | 0.844 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 14934 | 1152 | 0.002 | -0.026–0.031 | 0.8838 | 0.817 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 14934 | 1160 | -0.036 | -0.064–-0.007 | 0.0161 | 0.822 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 14934 | 1499 | -0.000 | -0.026–0.025 | 0.9868 | 0.913 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 14934 | 1079 | -0.019 | -0.048–0.011 | 0.2183 | 0.789 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 14934 | 1280 | 0.013 | -0.014–0.040 | 0.3529 | 0.859 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 14934 | 1571 | -0.013 | -0.038–0.012 | 0.3224 | 0.926 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 14934 | 1116 | 0.002 | -0.027–0.031 | 0.8971 | 0.803 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 14934 | 1156 | 0.015 | -0.014–0.043 | 0.3086 | 0.818 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 14934 | 1208 | 0.019 | -0.008–0.047 | 0.1709 | 0.836 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 14934 | 1124 | -0.019 | -0.048–0.011 | 0.2115 | 0.807 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 14934 | 1156 | 0.036 | 0.008–0.064 | 0.0106 | 0.816 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 14934 | 1433 | -0.001 | -0.026–0.025 | 0.9618 | 0.899 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 14934 | 1278 | 0.012 | -0.016–0.041 | 0.4032 | 0.802 | classical_rejected (recommended: powered null) |
| `place.saturn_h10` | 14934 | 1273 | 0.027 | -0.002–0.055 | 0.0687 | 0.800 | classical_rejected (recommended: powered null) |
| `place.saturn_h11` | 14934 | 1237 | -0.008 | -0.037–0.022 | 0.6106 | 0.788 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 14934 | 1220 | 0.001 | -0.026–0.028 | 0.9255 | 0.845 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 14934 | 1288 | -0.040 | -0.068–-0.011 | 0.0064 | 0.806 | classical_rejected (recommended: powered null) |
| `place.saturn_h3` | 14934 | 1220 | -0.019 | -0.048–0.011 | 0.2124 | 0.782 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 14934 | 1237 | 0.006 | -0.020–0.033 | 0.6364 | 0.854 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 14934 | 1276 | -0.009 | -0.035–0.017 | 0.4898 | 0.860 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 14934 | 1236 | 0.004 | -0.025–0.033 | 0.7818 | 0.787 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 14934 | 1265 | -0.011 | -0.037–0.016 | 0.4264 | 0.862 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 14934 | 1201 | -0.009 | -0.038–0.021 | 0.5668 | 0.774 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 14934 | 1203 | 0.001 | -0.026–0.029 | 0.9165 | 0.840 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 14934 | 1222 | 0.003 | -0.022–0.028 | 0.8050 | 0.932 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 14934 | 1508 | -0.001 | -0.024–0.021 | 0.9116 | 0.972 | classical_rejected (recommended: powered null) |
| `place.saturn_in_cancer` | 14934 | 1081 | -0.008 | -0.034–0.019 | 0.5611 | 0.897 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 14934 | 1360 | -0.005 | -0.029–0.019 | 0.6994 | 0.956 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 14934 | 1087 | 0.025 | -0.000–0.051 | 0.0505 | 0.896 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 14934 | 1150 | 0.013 | -0.013–0.038 | 0.3239 | 0.914 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 14934 | 1281 | -0.009 | -0.034–0.016 | 0.4744 | 0.944 | classical_rejected (recommended: powered null) |
| `place.saturn_in_pisces` | 14934 | 1182 | -0.003 | -0.028–0.023 | 0.8327 | 0.924 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 14934 | 1281 | 0.016 | -0.008–0.040 | 0.1951 | 0.942 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 14934 | 1326 | -0.002 | -0.026–0.022 | 0.8471 | 0.951 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 14934 | 1227 | -0.014 | -0.039–0.012 | 0.2909 | 0.934 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 14934 | 1229 | -0.012 | -0.037–0.013 | 0.3394 | 0.935 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 14934 | 1244 | 0.024 | -0.005–0.053 | 0.1017 | 0.790 | not_testable_yet (under-powered) |
| `place.sun_h10` | 14934 | 1219 | -0.002 | -0.031–0.027 | 0.8880 | 0.781 | not_testable_yet (under-powered) |
| `place.sun_h11` | 14934 | 1336 | 0.015 | -0.013–0.043 | 0.2825 | 0.821 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 14934 | 1218 | -0.017 | -0.044–0.010 | 0.2115 | 0.844 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 14934 | 1228 | 0.005 | -0.024–0.035 | 0.7191 | 0.785 | not_testable_yet (under-powered) |
| `place.sun_h3` | 14934 | 1268 | 0.006 | -0.023–0.034 | 0.7005 | 0.799 | not_testable_yet (under-powered) |
| `place.sun_h4` | 14934 | 1277 | -0.010 | -0.036–0.016 | 0.4529 | 0.864 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 14934 | 1241 | 0.015 | -0.012–0.042 | 0.2819 | 0.851 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 14934 | 1170 | -0.013 | -0.043–0.017 | 0.4029 | 0.762 | not_testable_yet (under-powered) |
| `place.sun_h7` | 14934 | 1234 | -0.002 | -0.028–0.025 | 0.8941 | 0.854 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 14934 | 1266 | -0.008 | -0.037–0.020 | 0.5722 | 0.798 | not_testable_yet (under-powered) |
| `place.sun_h9` | 14934 | 1233 | 0.004 | -0.023–0.031 | 0.7721 | 0.850 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 14934 | 1223 | -0.011 | -0.040–0.018 | 0.4591 | 0.783 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 14934 | 1232 | -0.004 | -0.034–0.025 | 0.7655 | 0.786 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 14934 | 1308 | 0.033 | 0.004–0.061 | 0.0233 | 0.812 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 14934 | 1250 | -0.003 | -0.032–0.026 | 0.8484 | 0.793 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 14934 | 1233 | 0.026 | -0.003–0.055 | 0.0789 | 0.786 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 14934 | 1311 | 0.004 | -0.025–0.032 | 0.7936 | 0.813 | classical_rejected (recommended: powered null) |
| `place.sun_in_libra` | 14934 | 1177 | 0.014 | -0.016–0.044 | 0.3567 | 0.765 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 14934 | 1239 | -0.021 | -0.050–0.008 | 0.1614 | 0.789 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 14934 | 1154 | -0.009 | -0.039–0.022 | 0.5785 | 0.756 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 14934 | 1222 | -0.003 | -0.033–0.026 | 0.8162 | 0.783 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 14934 | 1309 | -0.015 | -0.044–0.013 | 0.2855 | 0.813 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 14934 | 1276 | -0.011 | -0.039–0.018 | 0.4625 | 0.802 | classical_rejected (recommended: powered null) |
| `place.venus_h1` | 14934 | 1270 | 0.011 | -0.017–0.040 | 0.4332 | 0.799 | not_testable_yet (under-powered) |
| `place.venus_h10` | 14934 | 1181 | 0.012 | -0.018–0.042 | 0.4262 | 0.767 | not_testable_yet (under-powered) |
| `place.venus_h11` | 14934 | 1268 | -0.021 | -0.050–0.008 | 0.1510 | 0.799 | not_testable_yet (under-powered) |
| `place.venus_h12` | 14934 | 1290 | -0.017 | -0.043–0.009 | 0.2032 | 0.865 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 14934 | 1241 | 0.009 | -0.020–0.038 | 0.5381 | 0.789 | not_testable_yet (under-powered) |
| `place.venus_h3` | 14934 | 1227 | -0.011 | -0.040–0.018 | 0.4580 | 0.784 | not_testable_yet (under-powered) |
| `place.venus_h4` | 14934 | 1240 | 0.000 | -0.026–0.027 | 0.9777 | 0.854 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 14934 | 1214 | 0.007 | -0.020–0.034 | 0.5982 | 0.843 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 14934 | 1265 | 0.007 | -0.022–0.036 | 0.6425 | 0.798 | not_testable_yet (under-powered) |
| `place.venus_h7` | 14934 | 1250 | -0.009 | -0.036–0.017 | 0.4816 | 0.858 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 14934 | 1261 | 0.003 | -0.026–0.031 | 0.8629 | 0.796 | not_testable_yet (under-powered) |
| `place.venus_h9` | 14934 | 1227 | 0.029 | 0.001–0.056 | 0.0402 | 0.849 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 14934 | 1047 | -0.001 | -0.030–0.027 | 0.9205 | 0.787 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 14934 | 1179 | 0.000 | -0.027–0.027 | 0.9833 | 0.837 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 14934 | 1118 | -0.024 | -0.051–0.004 | 0.0882 | 0.814 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 14934 | 1498 | 0.015 | -0.010–0.040 | 0.2286 | 0.916 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 14934 | 1428 | -0.010 | -0.035–0.015 | 0.4341 | 0.902 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 14934 | 1500 | 0.008 | -0.017–0.033 | 0.5212 | 0.916 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 14934 | 1370 | 0.006 | -0.019–0.032 | 0.6432 | 0.890 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 14934 | 1339 | 0.001 | -0.025–0.026 | 0.9638 | 0.882 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 14934 | 1088 | -0.015 | -0.043–0.012 | 0.2756 | 0.803 | classical_rejected (recommended: powered null) |
| `place.venus_in_scorpio` | 14934 | 1080 | 0.003 | -0.026–0.031 | 0.8489 | 0.801 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 14934 | 1219 | 0.008 | -0.019–0.035 | 0.5408 | 0.850 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 14934 | 1068 | 0.002 | -0.026–0.031 | 0.8716 | 0.796 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 14934 | 1911 | 0.015 | -0.009–0.039 | 0.2162 | 0.935 | classical_rejected (recommended: powered null) |
| `yoga.budhaditya` | 14934 | 7720 | -0.004 | -0.020–0.012 | 0.6445 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 14934 | 5024 | 0.006 | -0.010–0.022 | 0.4531 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 14934 | 1446 | 0.009 | -0.017–0.034 | 0.5162 | 0.899 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 14934 | 2532 | 0.016 | -0.005–0.038 | 0.1360 | 0.978 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja` | 14934 | 7960 | 0.002 | -0.014–0.018 | 0.8441 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 14934 | 9645 | 0.002 | -0.015–0.019 | 0.8118 | 0.999 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 14934 | 2550 | -0.004 | -0.025–0.018 | 0.7334 | 0.979 | classical_rejected (recommended: powered null) |
| `yoga.neecha_bhanga` | 14934 | 6654 | 0.003 | -0.013–0.020 | 0.6707 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.parivartana` | 14934 | 5528 | 0.002 | -0.014–0.018 | 0.8061 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 14934 | 2179 | 0.009 | -0.014–0.031 | 0.4595 | 0.960 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 14934 | 2713 | 0.011 | -0.009–0.032 | 0.2799 | 0.984 | classical_rejected (recommended: powered null) |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
