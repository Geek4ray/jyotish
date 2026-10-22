# Synthetic — Validation — planted, N = 20,000, odds ratio 1.2 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 14991 development, 5009 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `70e63fadfc05b2dcf877580d53ef430b2974bc1f353e5a6e6038de24ceee92ba` ({"salt_sha256": "b41f02ef8121a7213a6d734d2a8d039c0b2f4c63f7fdf3e6191158ac8a2bb206", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "6ebe17a740123e67afcda74ce81874651755b92f8a49972a2cd198a037709ed8"})
- analysis code `494dae55f6a48ddf1c97767f4f82d77adf00c78f1bdbab2488c65c423b7b012c`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 14991 | 1.000 | 0.300 | 1.093 | 1.061–1.127 | 0.0010 | 0.0012 | yes | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 14991 | 1.000 | 0.510 | 1.090 | 1.065–1.115 | 0.0010 | 0.0012 | yes | 0.999 |
| children | 14991 | 1.000 | 0.301 | 1.091 | 1.052–1.126 | 0.0010 | 0.0012 | yes | 0.999 |
| intellect | 14991 | 1.000 | 0.303 | 1.135 | 1.096–1.171 | 0.0010 | 0.0012 | yes | 1.000 |
| health | 14991 | 1.000 | 0.506 | 1.067 | 1.048–1.086 | 0.0010 | 0.0012 | yes | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 14991 | 1.000 | 0.300 | 1.069 | 1.028–1.108 | 0.0020 | 0.0022 | yes | 1.000 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 14991 | 1.000 | 0.301 | 1.059 | 1.025–1.095 | 0.0010 | 0.0012 | yes | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 14991 | 1.000 | 0.516 | 1.072 | 1.047–1.095 | 0.0010 | 0.0012 | yes | 0.999 |
| gains | 14991 | 1.000 | 0.300 | 1.090 | 1.057–1.123 | 0.0010 | 0.0012 | yes | 1.000 |
| foreign | 14991 | 1.000 | 0.301 | 1.110 | 1.077–1.142 | 0.0010 | 0.0012 | yes | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 14991 | 1.000 | 0.303 | 1.043 | 1.007–1.081 | 0.0140 | 0.0140 | yes | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14991 | 1.000 | 8 | 106.40 | 8 | 0.0000 | 0.495 | 0.540 | 0.0000 |
| mother_home | 14991 | 1.000 | 8 | 177.50 | 8 | 0.0000 | 0.506 | 0.553 | 0.0000 |
| children | 14991 | 1.000 | 7 | 102.83 | 7 | 0.0000 | 0.503 | 0.545 | 0.0000 |
| intellect | 14991 | 1.000 | 8 | 108.96 | 8 | 0.0000 | 0.502 | 0.544 | 0.0000 |
| health | 14991 | 1.000 | 8 | 138.22 | 8 | 0.0000 | 0.501 | 0.545 | 0.0000 |
| marriage | 14991 | 1.000 | 8 | 89.39 | 8 | 0.0000 | 0.509 | 0.534 | 0.0000 |
| father | 14991 | 1.000 | 7 | 44.55 | 7 | 0.0000 | 0.511 | 0.526 | 0.0006 |
| career | 14991 | 1.000 | 8 | 132.28 | 8 | 0.0000 | 0.508 | 0.544 | 0.0000 |
| gains | 14991 | 1.000 | 8 | 106.06 | 8 | 0.0000 | 0.495 | 0.539 | 0.0000 |
| foreign | 14991 | 1.000 | 7 | 111.90 | 7 | 0.0000 | 0.500 | 0.548 | 0.0000 |
| reputation | 14991 | 1.000 | 8 | 75.12 | 8 | 0.0000 | 0.502 | 0.531 | 0.0000 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14991 | 1.000 | 729283 | 4490 | 0.934 | 1.287 | 0.0050 | 0.253 (0.122, 0.385) |
| mother_home | 14991 | 1.000 | 629300 | 7646 | 0.943 | 1.135 | 0.0050 | 0.128 (0.024, 0.231) |
| children | 14991 | 1.000 | 726944 | 4510 | 0.903 | 1.429 | 0.0050 | 0.359 (0.244, 0.474) |
| intellect | 14991 | 1.000 | 726599 | 4539 | 0.946 | 1.397 | 0.0050 | 0.336 (0.186, 0.486) |
| health | 14991 | 1.000 | 630773 | 7584 | 0.939 | 1.340 | 0.0050 | 0.295 (0.188, 0.403) |
| marriage | 14991 | 1.000 | 726831 | 4502 | 0.940 | 1.258 | 0.0050 | 0.231 (0.094, 0.368) |
| father | 14991 | 1.000 | 728191 | 4509 | 0.880 | 0.943 | 0.3234 | -0.059 (-0.147, 0.029) |
| career | 14991 | 1.000 | 624346 | 7742 | 0.954 | 1.194 | 0.0050 | 0.179 (0.064, 0.295) |
| gains | 14991 | 1.000 | 729283 | 4490 | 0.870 | 1.140 | 0.0050 | 0.132 (0.040, 0.224) |
| foreign | 14991 | 1.000 | 729662 | 4514 | 0.952 | 1.250 | 0.0050 | 0.225 (0.074, 0.376) |
| reputation | 14991 | 1.000 | 726599 | 4539 | 0.892 | 1.075 | 0.0597 | 0.073 (-0.024, 0.170) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 14991 | 1.000 | 0.002 | 0.010 | 4 | 29 | not allowed |
| mother_home | 14991 | 1.000 | 0.006 | 0.008 | 6 | 1 | not allowed |
| children | 14991 | 1.000 | 0.006 | 0.004 | 6 | 1 | not allowed |
| intellect | 14991 | 1.000 | 0.013 | 0.003 | 5 | 1 | not allowed |
| health | 14991 | 1.000 | 0.011 | 0.024 | 6 | 4 | not allowed |
| marriage | 14991 | 1.000 | 0.004 | 0.010 | 5 | 1 | not allowed |
| father | 14991 | 1.000 | 0.007 | 0.005 | 4 | 2 | not allowed |
| career | 14991 | 1.000 | 0.006 | 0.009 | 6 | 1 | not allowed |
| gains | 14991 | 1.000 | 0.003 | 0.010 | 6 | 0 | not allowed |
| foreign | 14991 | 1.000 | 0.005 | 0.010 | 5 | 0 | not allowed |
| reputation | 14991 | 1.000 | 0.007 | 0.004 | 4 | 1 | not allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 14991 | 1.000 | 5411 | 1.000 | 1.000 |
| mother_home | 14991 | 1.000 | 4385 | 0.999 | 1.000 |
| children | 14991 | 1.000 | 4049 | 0.999 | 1.000 |
| intellect | 14991 | 1.000 | 4712 | 1.000 | 1.000 |
| health | 14991 | 1.000 | 6235 | 1.000 | 1.000 |
| marriage | 14991 | 1.000 | 4125 | 1.000 | 1.000 |
| father | 14991 | 1.000 | 5221 | 1.000 | 1.000 |
| career | 14991 | 1.000 | 4426 | 0.999 | 1.000 |
| gains | 14991 | 1.000 | 5200 | 1.000 | 1.000 |
| foreign | 14991 | 1.000 | 5645 | 1.000 | 1.000 |
| reputation | 14991 | 1.000 | 4609 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 248 rules
- effect on development data: 8 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 104 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 14991 | 1221 | 0.016 | -0.013–0.046 | 0.2743 | 0.782 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 14991 | 1248 | 0.001 | -0.028–0.030 | 0.9303 | 0.793 | not_testable_yet (under-powered) |
| `place.jupiter_h11` | 14991 | 1310 | -0.011 | -0.040–0.017 | 0.4334 | 0.814 | classical_rejected (recommended: powered null) |
| `place.jupiter_h12` | 14991 | 1257 | -0.007 | -0.033–0.020 | 0.6282 | 0.858 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 14991 | 1244 | 0.009 | -0.020–0.038 | 0.5319 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 14991 | 1246 | 0.002 | -0.027–0.031 | 0.8818 | 0.792 | not_testable_yet (under-powered) |
| `place.jupiter_h4` | 14991 | 1231 | 0.027 | -0.000–0.054 | 0.0537 | 0.853 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 14991 | 1254 | 0.008 | -0.019–0.034 | 0.5763 | 0.858 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 14991 | 1276 | 0.002 | -0.027–0.031 | 0.8852 | 0.801 | classical_rejected (recommended: powered null) |
| `place.jupiter_h7` | 14991 | 1215 | -0.020 | -0.047–0.006 | 0.1285 | 0.845 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 14991 | 1234 | 0.025 | -0.004–0.054 | 0.0874 | 0.786 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 14991 | 1255 | -0.009 | -0.036–0.017 | 0.4802 | 0.857 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 14991 | 1154 | 0.004 | -0.025–0.032 | 0.8081 | 0.818 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 14991 | 1335 | -0.023 | -0.050–0.004 | 0.0888 | 0.877 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 14991 | 1307 | 0.068 | 0.042–0.093 | 0.0000 | 0.864 | effect on development data |
| `place.jupiter_in_capricorn` | 14991 | 1267 | -0.071 | -0.099–-0.043 | 0.0000 | 0.861 | effect on development data |
| `place.jupiter_in_gemini` | 14991 | 1149 | -0.017 | -0.046–0.012 | 0.2494 | 0.817 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_leo` | 14991 | 1338 | 0.023 | -0.003–0.050 | 0.0802 | 0.875 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 14991 | 1334 | -0.024 | -0.051–0.003 | 0.0850 | 0.877 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 14991 | 1119 | 0.010 | -0.018–0.039 | 0.4758 | 0.804 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_sagittarius` | 14991 | 1219 | 0.025 | -0.002–0.052 | 0.0736 | 0.840 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 14991 | 1253 | 0.036 | 0.009–0.063 | 0.0081 | 0.850 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 14991 | 1186 | -0.001 | -0.029–0.027 | 0.9323 | 0.830 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 14991 | 1330 | -0.028 | -0.055–-0.001 | 0.0412 | 0.876 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 14991 | 1274 | -0.023 | -0.051–0.006 | 0.1201 | 0.801 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 14991 | 1169 | 0.013 | -0.017–0.043 | 0.3837 | 0.763 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 14991 | 1223 | -0.021 | -0.050–0.008 | 0.1588 | 0.784 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 14991 | 1305 | -0.007 | -0.033–0.019 | 0.6136 | 0.871 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 14991 | 1251 | 0.017 | -0.012–0.046 | 0.2382 | 0.793 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 14991 | 1249 | 0.030 | 0.001–0.059 | 0.0440 | 0.793 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 14991 | 1235 | 0.004 | -0.023–0.030 | 0.7908 | 0.853 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 14991 | 1240 | 0.007 | -0.020–0.034 | 0.6092 | 0.854 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 14991 | 1294 | 0.001 | -0.027–0.030 | 0.9369 | 0.807 | classical_rejected (recommended: powered null) |
| `place.ketu_h7` | 14991 | 1248 | -0.015 | -0.041–0.012 | 0.2730 | 0.855 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 14991 | 1284 | 0.010 | -0.019–0.038 | 0.5049 | 0.804 | classical_rejected (recommended: powered null) |
| `place.ketu_h9` | 14991 | 1219 | -0.010 | -0.037–0.017 | 0.4678 | 0.846 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 14991 | 1542 | -0.013 | -0.036–0.011 | 0.3054 | 0.921 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 14991 | 1162 | 0.035 | 0.006–0.063 | 0.0160 | 0.830 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 14991 | 1094 | -0.001 | -0.030–0.027 | 0.9225 | 0.803 | classical_rejected (recommended: powered null) |
| `place.ketu_in_capricorn` | 14991 | 1486 | 0.014 | -0.011–0.039 | 0.2740 | 0.912 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 14991 | 1188 | -0.002 | -0.030–0.025 | 0.8573 | 0.837 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 14991 | 1183 | -0.004 | -0.031–0.023 | 0.7799 | 0.835 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 14991 | 1169 | 0.006 | -0.021–0.034 | 0.6439 | 0.831 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 14991 | 1457 | 0.009 | -0.016–0.034 | 0.4637 | 0.907 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 14991 | 1251 | -0.003 | -0.030–0.023 | 0.8116 | 0.856 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 14991 | 1150 | -0.024 | -0.051–0.003 | 0.0843 | 0.823 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 14991 | 1134 | -0.016 | -0.043–0.012 | 0.2613 | 0.818 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 14991 | 1175 | -0.004 | -0.031–0.024 | 0.8002 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 14991 | 1313 | -0.008 | -0.032–0.017 | 0.5391 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 14991 | 1242 | 0.045 | 0.016–0.074 | 0.0021 | 0.790 | not_testable_yet (under-powered) |
| `place.l10_h11` | 14991 | 1254 | -0.025 | -0.054–0.004 | 0.0913 | 0.795 | not_testable_yet (under-powered) |
| `place.l10_h12` | 14991 | 1221 | -0.007 | -0.035–0.021 | 0.6308 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 14991 | 1261 | -0.005 | -0.034–0.023 | 0.7136 | 0.797 | not_testable_yet (under-powered) |
| `place.l10_h3` | 14991 | 1243 | -0.001 | -0.030–0.028 | 0.9556 | 0.791 | not_testable_yet (under-powered) |
| `place.l10_h4` | 14991 | 1283 | 0.025 | -0.002–0.052 | 0.0677 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 14991 | 1198 | 0.028 | 0.000–0.055 | 0.0466 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 14991 | 1228 | -0.002 | -0.027–0.023 | 0.8560 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 14991 | 1260 | -0.020 | -0.047–0.008 | 0.1660 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 14991 | 1308 | 0.012 | -0.012–0.036 | 0.3146 | 0.944 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 14991 | 1180 | -0.013 | -0.042–0.015 | 0.3555 | 0.830 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 14991 | 1268 | 0.006 | -0.018–0.030 | 0.6277 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 14991 | 1202 | -0.012 | -0.042–0.017 | 0.4077 | 0.776 | not_testable_yet (under-powered) |
| `place.l11_h11` | 14991 | 1230 | 0.061 | 0.032–0.090 | 0.0000 | 0.786 | effect on development data |
| `place.l11_h12` | 14991 | 1236 | -0.025 | -0.053–0.003 | 0.0771 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 14991 | 1247 | -0.006 | -0.035–0.023 | 0.6786 | 0.792 | not_testable_yet (under-powered) |
| `place.l11_h3` | 14991 | 1242 | -0.018 | -0.047–0.011 | 0.2262 | 0.791 | not_testable_yet (under-powered) |
| `place.l11_h4` | 14991 | 1268 | -0.020 | -0.047–0.008 | 0.1613 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 14991 | 1253 | -0.001 | -0.029–0.026 | 0.9271 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 14991 | 1229 | -0.012 | -0.037–0.013 | 0.3582 | 0.931 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 14991 | 1304 | 0.025 | -0.002–0.051 | 0.0673 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 14991 | 1207 | 0.009 | -0.016–0.034 | 0.4628 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 14991 | 1305 | -0.001 | -0.028–0.026 | 0.9410 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 14991 | 1254 | -0.017 | -0.044–0.011 | 0.2429 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 14991 | 1291 | -0.008 | -0.035–0.020 | 0.5836 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 14991 | 1231 | -0.009 | -0.037–0.019 | 0.5211 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 14991 | 1150 | 0.036 | 0.008–0.065 | 0.0116 | 0.826 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 14991 | 1236 | 0.001 | -0.026–0.029 | 0.9284 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 14991 | 1333 | -0.031 | -0.058–-0.004 | 0.0244 | 0.879 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 14991 | 1278 | 0.012 | -0.016–0.041 | 0.4047 | 0.802 | classical_rejected (recommended: powered null) |
| `place.l12_h5` | 14991 | 1243 | 0.014 | -0.015–0.043 | 0.3475 | 0.790 | not_testable_yet (under-powered) |
| `place.l12_h6` | 14991 | 1225 | -0.015 | -0.043–0.013 | 0.2883 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 14991 | 1240 | 0.031 | 0.002–0.060 | 0.0365 | 0.789 | not_testable_yet (under-powered) |
| `place.l12_h8` | 14991 | 1287 | 0.001 | -0.026–0.028 | 0.9288 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 14991 | 1223 | 0.010 | -0.017–0.037 | 0.4881 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 14991 | 1167 | 0.030 | 0.000–0.060 | 0.0463 | 0.761 | not_testable_yet (under-powered) |
| `place.l1_h10` | 14991 | 1241 | -0.007 | -0.032–0.018 | 0.5597 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 14991 | 1268 | 0.017 | -0.007–0.041 | 0.1603 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 14991 | 1227 | 0.020 | -0.007–0.048 | 0.1525 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 14991 | 1270 | -0.015 | -0.040–0.010 | 0.2375 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 14991 | 1205 | -0.000 | -0.025–0.025 | 0.9919 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 14991 | 1337 | -0.020 | -0.047–0.007 | 0.1452 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 14991 | 1206 | -0.025 | -0.054–0.003 | 0.0819 | 0.834 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 14991 | 1300 | 0.001 | -0.027–0.030 | 0.9387 | 0.809 | classical_rejected (recommended: powered null) |
| `place.l1_h7` | 14991 | 1217 | -0.030 | -0.058–-0.001 | 0.0396 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 14991 | 1233 | 0.002 | -0.027–0.031 | 0.8949 | 0.786 | not_testable_yet (under-powered) |
| `place.l1_h9` | 14991 | 1320 | 0.016 | -0.011–0.042 | 0.2475 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 14991 | 1254 | 0.006 | -0.019–0.030 | 0.6443 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 14991 | 1309 | -0.005 | -0.033–0.023 | 0.7273 | 0.813 | classical_rejected (recommended: powered null) |
| `place.l2_h11` | 14991 | 1216 | 0.016 | -0.013–0.045 | 0.2805 | 0.781 | not_testable_yet (under-powered) |
| `place.l2_h12` | 14991 | 1317 | -0.000 | -0.027–0.027 | 0.9928 | 0.873 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 14991 | 1178 | 0.033 | 0.003–0.062 | 0.0299 | 0.766 | not_testable_yet (under-powered) |
| `place.l2_h3` | 14991 | 1290 | -0.010 | -0.038–0.019 | 0.5137 | 0.807 | classical_rejected (recommended: powered null) |
| `place.l2_h4` | 14991 | 1210 | 0.010 | -0.018–0.038 | 0.4767 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 14991 | 1267 | 0.006 | -0.021–0.033 | 0.6497 | 0.856 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 14991 | 1216 | -0.013 | -0.038–0.012 | 0.3174 | 0.929 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 14991 | 1230 | -0.010 | -0.038–0.017 | 0.4603 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 14991 | 1251 | -0.002 | -0.027–0.023 | 0.8860 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 14991 | 1253 | -0.018 | -0.046–0.010 | 0.1989 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 14991 | 1269 | -0.002 | -0.026–0.023 | 0.9046 | 0.938 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 14991 | 1223 | 0.009 | -0.020–0.038 | 0.5348 | 0.783 | not_testable_yet (under-powered) |
| `place.l3_h11` | 14991 | 1339 | 0.012 | -0.016–0.040 | 0.4062 | 0.823 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 14991 | 1234 | 0.002 | -0.025–0.030 | 0.8625 | 0.848 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 14991 | 1259 | 0.022 | -0.007–0.050 | 0.1432 | 0.796 | not_testable_yet (under-powered) |
| `place.l3_h3` | 14991 | 1275 | -0.001 | -0.030–0.027 | 0.9316 | 0.802 | classical_rejected (recommended: powered null) |
| `place.l3_h4` | 14991 | 1276 | 0.002 | -0.025–0.030 | 0.8605 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 14991 | 1252 | 0.021 | -0.006–0.048 | 0.1269 | 0.851 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 14991 | 1233 | -0.006 | -0.031–0.019 | 0.6579 | 0.932 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 14991 | 1196 | -0.003 | -0.031–0.025 | 0.8252 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 14991 | 1202 | -0.011 | -0.036–0.015 | 0.4096 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 14991 | 1233 | -0.022 | -0.050–0.006 | 0.1271 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 14991 | 1202 | -0.019 | -0.047–0.010 | 0.1940 | 0.830 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 14991 | 1206 | -0.019 | -0.047–0.009 | 0.1850 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 14991 | 1259 | 0.013 | -0.014–0.040 | 0.3480 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 14991 | 1282 | -0.020 | -0.049–0.008 | 0.1642 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l4_h2` | 14991 | 1295 | 0.005 | -0.022–0.032 | 0.6958 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 14991 | 1236 | -0.010 | -0.037–0.018 | 0.4985 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 14991 | 1196 | 0.023 | -0.005–0.050 | 0.1088 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 14991 | 1326 | 0.009 | -0.019–0.037 | 0.5428 | 0.818 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 14991 | 1233 | -0.017 | -0.045–0.011 | 0.2419 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 14991 | 1237 | 0.005 | -0.024–0.034 | 0.7405 | 0.788 | not_testable_yet (under-powered) |
| `place.l4_h8` | 14991 | 1212 | 0.002 | -0.026–0.030 | 0.9150 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 14991 | 1307 | 0.001 | -0.027–0.030 | 0.9345 | 0.812 | classical_rejected (recommended: powered null) |
| `place.l5_h1` | 14991 | 1295 | -0.023 | -0.050–0.005 | 0.1030 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 14991 | 1296 | 0.005 | -0.022–0.032 | 0.7030 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 14991 | 1249 | -0.030 | -0.058–-0.003 | 0.0326 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 14991 | 1170 | 0.017 | -0.013–0.046 | 0.2733 | 0.762 | not_testable_yet (under-powered) |
| `place.l5_h2` | 14991 | 1290 | 0.015 | -0.011–0.042 | 0.2603 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 14991 | 1270 | 0.005 | -0.022–0.033 | 0.6944 | 0.857 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 14991 | 1214 | 0.010 | -0.020–0.039 | 0.5245 | 0.779 | not_testable_yet (under-powered) |
| `place.l5_h5` | 14991 | 1235 | 0.013 | -0.014–0.040 | 0.3539 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 14991 | 1202 | -0.027 | -0.056–0.001 | 0.0589 | 0.832 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 14991 | 1233 | -0.008 | -0.038–0.021 | 0.5719 | 0.786 | not_testable_yet (under-powered) |
| `place.l5_h8` | 14991 | 1313 | 0.004 | -0.023–0.031 | 0.7502 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 14991 | 1224 | 0.008 | -0.022–0.037 | 0.6116 | 0.783 | not_testable_yet (under-powered) |
| `place.l6_h1` | 14991 | 1213 | 0.023 | -0.007–0.052 | 0.1286 | 0.779 | not_testable_yet (under-powered) |
| `place.l6_h10` | 14991 | 1254 | 0.008 | -0.016–0.033 | 0.5014 | 0.935 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 14991 | 1305 | 0.010 | -0.014–0.034 | 0.4139 | 0.944 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 14991 | 1286 | -0.019 | -0.046–0.009 | 0.1843 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 14991 | 1293 | -0.003 | -0.027–0.022 | 0.8399 | 0.943 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 14991 | 1214 | 0.014 | -0.010–0.039 | 0.2533 | 0.926 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 14991 | 1224 | -0.044 | -0.072–-0.015 | 0.0026 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l6_h5` | 14991 | 1222 | -0.012 | -0.040–0.016 | 0.4045 | 0.838 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 14991 | 1206 | 0.007 | -0.022–0.037 | 0.6359 | 0.776 | not_testable_yet (under-powered) |
| `place.l6_h7` | 14991 | 1266 | 0.008 | -0.019–0.036 | 0.5469 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 14991 | 1178 | -0.013 | -0.043–0.017 | 0.3969 | 0.765 | not_testable_yet (under-powered) |
| `place.l6_h9` | 14991 | 1330 | -0.010 | -0.037–0.017 | 0.4501 | 0.871 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 14991 | 1253 | 0.009 | -0.018–0.036 | 0.5241 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 14991 | 1238 | -0.000 | -0.028–0.028 | 0.9949 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 14991 | 1278 | -0.006 | -0.034–0.021 | 0.6492 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 14991 | 1270 | -0.020 | -0.049–0.009 | 0.1734 | 0.800 | not_testable_yet (under-powered) |
| `place.l7_h2` | 14991 | 1191 | 0.034 | 0.007–0.062 | 0.0138 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l7_h3` | 14991 | 1339 | -0.000 | -0.027–0.026 | 0.9750 | 0.876 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 14991 | 1257 | 0.014 | -0.015–0.043 | 0.3338 | 0.795 | not_testable_yet (under-powered) |
| `place.l7_h5` | 14991 | 1253 | -0.049 | -0.078–-0.020 | 0.0008 | 0.794 | not_testable_yet (under-powered) |
| `place.l7_h6` | 14991 | 1193 | -0.000 | -0.029–0.028 | 0.9731 | 0.829 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 14991 | 1210 | 0.028 | 0.000–0.055 | 0.0496 | 0.846 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 14991 | 1242 | 0.011 | -0.017–0.038 | 0.4365 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 14991 | 1267 | -0.015 | -0.044–0.014 | 0.2994 | 0.799 | not_testable_yet (under-powered) |
| `place.l8_h1` | 14991 | 1284 | 0.004 | -0.025–0.032 | 0.7964 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l8_h10` | 14991 | 1168 | -0.003 | -0.028–0.023 | 0.8288 | 0.917 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 14991 | 1342 | 0.006 | -0.018–0.029 | 0.6463 | 0.950 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 14991 | 1167 | -0.012 | -0.041–0.016 | 0.3991 | 0.819 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 14991 | 1247 | -0.003 | -0.028–0.022 | 0.8338 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 14991 | 1216 | 0.024 | -0.001–0.048 | 0.0559 | 0.926 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 14991 | 1306 | 0.011 | -0.015–0.038 | 0.4048 | 0.861 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 14991 | 1336 | 0.007 | -0.020–0.033 | 0.6191 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 14991 | 1244 | -0.025 | -0.054–0.004 | 0.0931 | 0.790 | not_testable_yet (under-powered) |
| `place.l8_h7` | 14991 | 1204 | -0.004 | -0.032–0.024 | 0.7657 | 0.833 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 14991 | 1243 | 0.018 | -0.011–0.047 | 0.2319 | 0.790 | not_testable_yet (under-powered) |
| `place.l8_h9` | 14991 | 1234 | -0.003 | -0.030–0.025 | 0.8532 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 14991 | 1251 | 0.003 | -0.025–0.030 | 0.8550 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 14991 | 1320 | 0.017 | -0.009–0.044 | 0.1988 | 0.872 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 14991 | 1218 | -0.006 | -0.034–0.022 | 0.6749 | 0.843 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 14991 | 1269 | 0.002 | -0.024–0.029 | 0.8538 | 0.862 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 14991 | 1235 | -0.010 | -0.037–0.018 | 0.4959 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 14991 | 1211 | -0.034 | -0.062–-0.006 | 0.0180 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 14991 | 1215 | 0.001 | -0.028–0.031 | 0.9327 | 0.780 | not_testable_yet (under-powered) |
| `place.l9_h5` | 14991 | 1344 | 0.011 | -0.017–0.039 | 0.4406 | 0.823 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 14991 | 1233 | -0.005 | -0.033–0.023 | 0.7406 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 14991 | 1260 | 0.009 | -0.019–0.038 | 0.5202 | 0.796 | not_testable_yet (under-powered) |
| `place.l9_h8` | 14991 | 1243 | -0.002 | -0.029–0.026 | 0.9090 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 14991 | 1192 | 0.013 | -0.015–0.040 | 0.3591 | 0.839 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 14991 | 1306 | -0.011 | -0.040–0.017 | 0.4271 | 0.811 | classical_rejected (recommended: powered null) |
| `place.mars_h10` | 14991 | 1254 | -0.020 | -0.049–0.009 | 0.1820 | 0.795 | not_testable_yet (under-powered) |
| `place.mars_h11` | 14991 | 1186 | 0.021 | -0.009–0.050 | 0.1723 | 0.769 | not_testable_yet (under-powered) |
| `place.mars_h12` | 14991 | 1228 | -0.019 | -0.046–0.007 | 0.1509 | 0.849 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 14991 | 1204 | 0.032 | 0.002–0.061 | 0.0337 | 0.776 | not_testable_yet (under-powered) |
| `place.mars_h3` | 14991 | 1236 | -0.028 | -0.057–0.001 | 0.0628 | 0.789 | not_testable_yet (under-powered) |
| `place.mars_h4` | 14991 | 1286 | 0.011 | -0.015–0.037 | 0.4180 | 0.868 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 14991 | 1263 | -0.015 | -0.041–0.011 | 0.2708 | 0.859 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 14991 | 1191 | -0.030 | -0.059–-0.000 | 0.0492 | 0.771 | not_testable_yet (under-powered) |
| `place.mars_h7` | 14991 | 1281 | 0.004 | -0.023–0.030 | 0.7847 | 0.866 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 14991 | 1254 | -0.009 | -0.038–0.020 | 0.5394 | 0.794 | not_testable_yet (under-powered) |
| `place.mars_h9` | 14991 | 1302 | -0.026 | -0.052–-0.001 | 0.0448 | 0.869 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 14991 | 905 | 0.032 | -0.001–0.066 | 0.0571 | 0.635 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 14991 | 1101 | 0.014 | -0.017–0.045 | 0.3666 | 0.734 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 14991 | 1455 | -0.022 | -0.049–0.005 | 0.1167 | 0.856 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 14991 | 978 | 0.019 | -0.014–0.051 | 0.2621 | 0.675 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 14991 | 1370 | 0.020 | -0.007–0.048 | 0.1478 | 0.832 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 14991 | 1616 | 0.018 | -0.007–0.044 | 0.1631 | 0.891 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 14991 | 1428 | -0.020 | -0.047–0.008 | 0.1562 | 0.849 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 14991 | 1077 | -0.021 | -0.052–0.010 | 0.1797 | 0.724 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 14991 | 1138 | 0.007 | -0.023–0.037 | 0.6528 | 0.750 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 14991 | 1077 | 0.012 | -0.019–0.043 | 0.4551 | 0.723 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 14991 | 1371 | -0.007 | -0.035–0.021 | 0.6082 | 0.832 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 14991 | 1475 | -0.034 | -0.061–-0.008 | 0.0121 | 0.861 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 14991 | 1211 | 0.016 | -0.013–0.046 | 0.2709 | 0.778 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 14991 | 1255 | -0.012 | -0.041–0.017 | 0.4044 | 0.795 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 14991 | 1267 | 0.028 | -0.001–0.057 | 0.0543 | 0.799 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 14991 | 1267 | -0.009 | -0.035–0.017 | 0.4979 | 0.861 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 14991 | 1197 | 0.011 | -0.019–0.040 | 0.4758 | 0.774 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 14991 | 1309 | -0.003 | -0.032–0.025 | 0.8158 | 0.813 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 14991 | 1256 | 0.009 | -0.018–0.035 | 0.5305 | 0.860 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 14991 | 1279 | -0.004 | -0.030–0.022 | 0.7597 | 0.865 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 14991 | 1218 | -0.012 | -0.041–0.018 | 0.4303 | 0.781 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 14991 | 1210 | 0.007 | -0.020–0.034 | 0.6200 | 0.845 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 14991 | 1280 | -0.002 | -0.031–0.026 | 0.8812 | 0.803 | classical_rejected (recommended: powered null) |
| `place.mercury_h9` | 14991 | 1242 | 0.020 | -0.007–0.047 | 0.1431 | 0.855 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 14991 | 1309 | -0.011 | -0.039–0.017 | 0.4510 | 0.813 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 14991 | 1110 | 0.040 | 0.009–0.070 | 0.0106 | 0.738 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 14991 | 1195 | -0.017 | -0.046–0.013 | 0.2737 | 0.773 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 14991 | 1277 | -0.002 | -0.031–0.027 | 0.8837 | 0.803 | classical_rejected (recommended: powered null) |
| `place.mercury_in_gemini` | 14991 | 1129 | 0.031 | 0.000–0.061 | 0.0472 | 0.746 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 14991 | 1242 | -0.018 | -0.047–0.011 | 0.2262 | 0.791 | not_testable_yet (under-powered) |
| `place.mercury_in_libra` | 14991 | 1396 | -0.021 | -0.048–0.007 | 0.1446 | 0.840 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 14991 | 1238 | -0.014 | -0.043–0.015 | 0.3317 | 0.789 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 14991 | 1342 | -0.015 | -0.043–0.013 | 0.3012 | 0.824 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 14991 | 1358 | -0.020 | -0.048–0.008 | 0.1661 | 0.829 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 14991 | 1126 | 0.012 | -0.018–0.042 | 0.4384 | 0.745 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 14991 | 1269 | 0.046 | 0.018–0.075 | 0.0015 | 0.800 | not_testable_yet (under-powered) |
| `place.moon_h1` | 14991 | 1256 | -0.000 | -0.029–0.029 | 0.9805 | 0.794 | not_testable_yet (under-powered) |
| `place.moon_h10` | 14991 | 1308 | 0.026 | -0.002–0.055 | 0.0675 | 0.813 | classical_rejected (recommended: powered null) |
| `place.moon_h11` | 14991 | 1235 | -0.014 | -0.043–0.015 | 0.3476 | 0.788 | not_testable_yet (under-powered) |
| `place.moon_h12` | 14991 | 1209 | -0.005 | -0.032–0.021 | 0.6913 | 0.844 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 14991 | 1309 | -0.001 | -0.029–0.027 | 0.9527 | 0.813 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 14991 | 1224 | -0.009 | -0.038–0.020 | 0.5457 | 0.784 | not_testable_yet (under-powered) |
| `place.moon_h4` | 14991 | 1266 | -0.004 | -0.030–0.023 | 0.7879 | 0.862 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 14991 | 1294 | 0.015 | -0.011–0.041 | 0.2669 | 0.870 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 14991 | 1225 | -0.010 | -0.039–0.020 | 0.5222 | 0.783 | not_testable_yet (under-powered) |
| `place.moon_h7` | 14991 | 1176 | -0.024 | -0.051–0.003 | 0.0766 | 0.832 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 14991 | 1223 | 0.009 | -0.020–0.038 | 0.5394 | 0.782 | not_testable_yet (under-powered) |
| `place.moon_h9` | 14991 | 1266 | -0.010 | -0.036–0.017 | 0.4694 | 0.860 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 14991 | 1248 | 0.014 | -0.015–0.043 | 0.3550 | 0.791 | not_testable_yet (under-powered) |
| `place.rahu_h10` | 14991 | 1235 | -0.001 | -0.030–0.028 | 0.9617 | 0.788 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 14991 | 1240 | -0.021 | -0.050–0.008 | 0.1654 | 0.790 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 14991 | 1294 | 0.029 | 0.002–0.056 | 0.0329 | 0.870 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 14991 | 1284 | -0.011 | -0.040–0.017 | 0.4440 | 0.805 | classical_rejected (recommended: powered null) |
| `place.rahu_h3` | 14991 | 1219 | -0.003 | -0.032–0.026 | 0.8322 | 0.782 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 14991 | 1169 | -0.001 | -0.028–0.026 | 0.9400 | 0.832 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 14991 | 1223 | -0.005 | -0.032–0.021 | 0.6981 | 0.848 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 14991 | 1305 | -0.004 | -0.032–0.025 | 0.8075 | 0.811 | classical_rejected (recommended: powered null) |
| `place.rahu_h7` | 14991 | 1274 | 0.041 | 0.014–0.068 | 0.0032 | 0.866 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 14991 | 1251 | 0.018 | -0.011–0.046 | 0.2344 | 0.793 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 14991 | 1249 | -0.008 | -0.034–0.018 | 0.5556 | 0.856 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 14991 | 1183 | 0.000 | -0.028–0.029 | 0.9750 | 0.831 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 14991 | 1169 | 0.002 | -0.027–0.030 | 0.9103 | 0.826 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 14991 | 1486 | 0.002 | -0.024–0.027 | 0.9050 | 0.912 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 14991 | 1094 | 0.019 | -0.010–0.048 | 0.1933 | 0.795 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 14991 | 1251 | -0.000 | -0.028–0.027 | 0.9756 | 0.853 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 14991 | 1542 | -0.006 | -0.031–0.019 | 0.6515 | 0.922 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 14991 | 1162 | 0.035 | 0.007–0.063 | 0.0135 | 0.821 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 14991 | 1175 | -0.014 | -0.042–0.014 | 0.3323 | 0.829 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 14991 | 1188 | 0.017 | -0.011–0.044 | 0.2403 | 0.831 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 14991 | 1134 | 0.002 | -0.027–0.030 | 0.9012 | 0.812 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 14991 | 1150 | -0.012 | -0.041–0.017 | 0.4140 | 0.819 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 14991 | 1457 | -0.034 | -0.060–-0.008 | 0.0104 | 0.908 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 14991 | 1273 | -0.027 | -0.055–0.002 | 0.0690 | 0.800 | classical_rejected (recommended: powered null) |
| `place.saturn_h10` | 14991 | 1257 | 0.022 | -0.006–0.051 | 0.1269 | 0.796 | not_testable_yet (under-powered) |
| `place.saturn_h11` | 14991 | 1251 | 0.013 | -0.016–0.042 | 0.3772 | 0.794 | not_testable_yet (under-powered) |
| `place.saturn_h12` | 14991 | 1219 | -0.011 | -0.037–0.016 | 0.4281 | 0.846 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 14991 | 1310 | -0.011 | -0.040–0.017 | 0.4334 | 0.814 | classical_rejected (recommended: powered null) |
| `place.saturn_h3` | 14991 | 1250 | -0.014 | -0.043–0.015 | 0.3580 | 0.793 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 14991 | 1223 | -0.008 | -0.035–0.018 | 0.5417 | 0.849 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 14991 | 1278 | -0.018 | -0.043–0.008 | 0.1851 | 0.863 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 14991 | 1205 | -0.013 | -0.043–0.016 | 0.3799 | 0.776 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 14991 | 1285 | -0.010 | -0.036–0.016 | 0.4450 | 0.866 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 14991 | 1208 | 0.012 | -0.018–0.041 | 0.4397 | 0.777 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 14991 | 1232 | 0.011 | -0.016–0.038 | 0.4393 | 0.852 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 14991 | 1204 | 0.030 | 0.006–0.055 | 0.0139 | 0.923 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 14991 | 1559 | -0.044 | -0.068–-0.021 | 0.0002 | 0.977 | effect on development data |
| `place.saturn_in_cancer` | 14991 | 1091 | -0.011 | -0.038–0.015 | 0.4012 | 0.896 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 14991 | 1318 | 0.024 | 0.001–0.048 | 0.0434 | 0.945 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 14991 | 1071 | 0.004 | -0.023–0.030 | 0.7872 | 0.888 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 14991 | 1129 | -0.050 | -0.078–-0.023 | 0.0003 | 0.910 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 14991 | 1289 | 0.053 | 0.030–0.075 | 0.0000 | 0.938 | effect on development data |
| `place.saturn_in_pisces` | 14991 | 1196 | 0.004 | -0.021–0.029 | 0.7395 | 0.923 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 14991 | 1281 | -0.016 | -0.041–0.009 | 0.2054 | 0.942 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 14991 | 1368 | -0.012 | -0.036–0.012 | 0.3282 | 0.955 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 14991 | 1213 | 0.012 | -0.012–0.037 | 0.3269 | 0.926 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 14991 | 1272 | 0.011 | -0.013–0.035 | 0.3672 | 0.938 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 14991 | 1211 | -0.008 | -0.037–0.022 | 0.6041 | 0.778 | not_testable_yet (under-powered) |
| `place.sun_h10` | 14991 | 1244 | 0.004 | -0.025–0.033 | 0.7877 | 0.791 | not_testable_yet (under-powered) |
| `place.sun_h11` | 14991 | 1332 | -0.010 | -0.038–0.018 | 0.4943 | 0.821 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 14991 | 1202 | 0.000 | -0.027–0.027 | 0.9968 | 0.842 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 14991 | 1265 | -0.001 | -0.030–0.028 | 0.9390 | 0.799 | not_testable_yet (under-powered) |
| `place.sun_h3` | 14991 | 1274 | 0.018 | -0.011–0.047 | 0.2166 | 0.801 | classical_rejected (recommended: powered null) |
| `place.sun_h4` | 14991 | 1272 | -0.004 | -0.031–0.022 | 0.7491 | 0.863 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 14991 | 1273 | 0.006 | -0.020–0.032 | 0.6552 | 0.863 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 14991 | 1203 | -0.022 | -0.052–0.007 | 0.1389 | 0.775 | not_testable_yet (under-powered) |
| `place.sun_h7` | 14991 | 1219 | 0.012 | -0.015–0.040 | 0.3688 | 0.848 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 14991 | 1270 | -0.009 | -0.038–0.020 | 0.5380 | 0.799 | not_testable_yet (under-powered) |
| `place.sun_h9` | 14991 | 1226 | 0.022 | -0.005–0.049 | 0.1124 | 0.850 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 14991 | 1257 | -0.026 | -0.055–0.003 | 0.0753 | 0.796 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 14991 | 1233 | 0.021 | -0.008–0.050 | 0.1488 | 0.787 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 14991 | 1307 | -0.007 | -0.035–0.022 | 0.6435 | 0.813 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 14991 | 1259 | 0.001 | -0.028–0.030 | 0.9625 | 0.796 | not_testable_yet (under-powered) |
| `place.sun_in_gemini` | 14991 | 1242 | 0.017 | -0.012–0.046 | 0.2451 | 0.790 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 14991 | 1269 | 0.004 | -0.025–0.033 | 0.7855 | 0.800 | not_testable_yet (under-powered) |
| `place.sun_in_libra` | 14991 | 1213 | -0.018 | -0.048–0.011 | 0.2207 | 0.780 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 14991 | 1245 | 0.002 | -0.027–0.031 | 0.9044 | 0.792 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 14991 | 1165 | -0.022 | -0.052–0.008 | 0.1489 | 0.761 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 14991 | 1218 | -0.011 | -0.040–0.019 | 0.4720 | 0.782 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 14991 | 1326 | 0.016 | -0.012–0.044 | 0.2686 | 0.819 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 14991 | 1257 | 0.021 | -0.008–0.050 | 0.1592 | 0.796 | not_testable_yet (under-powered) |
| `place.venus_h1` | 14991 | 1267 | 0.010 | -0.019–0.038 | 0.5174 | 0.798 | not_testable_yet (under-powered) |
| `place.venus_h10` | 14991 | 1205 | -0.017 | -0.046–0.013 | 0.2712 | 0.777 | not_testable_yet (under-powered) |
| `place.venus_h11` | 14991 | 1297 | 0.015 | -0.013–0.044 | 0.2902 | 0.809 | classical_rejected (recommended: powered null) |
| `place.venus_h12` | 14991 | 1238 | -0.007 | -0.033–0.020 | 0.6129 | 0.852 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 14991 | 1259 | -0.014 | -0.043–0.015 | 0.3400 | 0.797 | not_testable_yet (under-powered) |
| `place.venus_h3` | 14991 | 1247 | -0.009 | -0.038–0.020 | 0.5539 | 0.792 | not_testable_yet (under-powered) |
| `place.venus_h4` | 14991 | 1267 | 0.013 | -0.013–0.040 | 0.3248 | 0.863 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 14991 | 1210 | -0.007 | -0.034–0.020 | 0.5977 | 0.844 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 14991 | 1267 | 0.004 | -0.024–0.033 | 0.7681 | 0.798 | not_testable_yet (under-powered) |
| `place.venus_h7` | 14991 | 1240 | 0.002 | -0.024–0.029 | 0.8661 | 0.854 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 14991 | 1237 | -0.004 | -0.033–0.025 | 0.7755 | 0.788 | not_testable_yet (under-powered) |
| `place.venus_h9` | 14991 | 1257 | 0.011 | -0.016–0.038 | 0.4258 | 0.859 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 14991 | 1067 | 0.008 | -0.021–0.036 | 0.6023 | 0.794 | not_testable_yet (under-powered) |
| `place.venus_in_aries` | 14991 | 1176 | -0.014 | -0.041–0.013 | 0.3091 | 0.833 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 14991 | 1116 | -0.003 | -0.031–0.025 | 0.8303 | 0.812 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 14991 | 1514 | 0.002 | -0.023–0.026 | 0.8908 | 0.917 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 14991 | 1447 | 0.003 | -0.022–0.028 | 0.8356 | 0.905 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 14991 | 1495 | 0.001 | -0.024–0.025 | 0.9511 | 0.914 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 14991 | 1371 | 0.036 | 0.010–0.062 | 0.0064 | 0.890 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 14991 | 1372 | 0.034 | 0.008–0.061 | 0.0095 | 0.890 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 14991 | 1072 | -0.033 | -0.061–-0.005 | 0.0189 | 0.794 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 14991 | 1091 | -0.035 | -0.063–-0.008 | 0.0116 | 0.801 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 14991 | 1211 | 0.007 | -0.020–0.034 | 0.6339 | 0.845 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 14991 | 1059 | -0.023 | -0.051–0.005 | 0.1021 | 0.789 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 14991 | 1869 | 0.040 | 0.016–0.064 | 0.0011 | 0.931 | classical_rejected (recommended: powered null) |
| `yoga.budhaditya` | 14991 | 7746 | 0.007 | -0.009–0.023 | 0.4019 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 14991 | 5047 | 0.011 | -0.005–0.027 | 0.1674 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 14991 | 1426 | 0.041 | 0.016–0.067 | 0.0013 | 0.894 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 14991 | 2556 | 0.055 | 0.034–0.076 | 0.0000 | 0.979 | effect on development data |
| `yoga.kendra_trikona_raja` | 14991 | 8012 | 0.001 | -0.015–0.017 | 0.8632 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 14991 | 9706 | -0.011 | -0.027–0.006 | 0.2105 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 14991 | 2614 | 0.024 | 0.003–0.045 | 0.0255 | 0.981 | classical_rejected (recommended: powered null) |
| `yoga.neecha_bhanga` | 14991 | 6691 | -0.038 | -0.054–-0.022 | 0.0000 | 1.000 | effect on development data |
| `yoga.parivartana` | 14991 | 5557 | -0.010 | -0.026–0.006 | 0.2243 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 14991 | 2218 | 0.014 | -0.008–0.037 | 0.2216 | 0.963 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 14991 | 2677 | 0.050 | 0.029–0.071 | 0.0000 | 0.983 | effect on development data |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
