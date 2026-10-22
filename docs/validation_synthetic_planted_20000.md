# Synthetic — Validation — planted, N = 20,000, odds ratio 1.2 per SD

Run 2026-10-22 by `scripts/validate.py` on a synthetic cohort: these numbers prove the pipeline, not the engine. 20000 subjects: 15065 development, 4935 sequestered (scored in this run); 5 grouped folds, 0 groups straddling a fold.

## Synthetic — Pre-registration hashes (test 10)

- rule set `fe4a45353690525365741ebe19d5e291a49bb4fdbb09b07ea839f67ad4e15c60`
- weight set `48c7ae0f0a24d542333ad7c0726d089e89f0ba0ab5d5f0950a0fd4c8d228eeab`
- split definition `dca349ba402277e639b641790c0f54ee7be17f23af17928d948b78adefcb0eed` ({"salt_sha256": "910983680cb4ba6532374749347e94cfb93408487f5405cb42e111b7accbfa31", "fraction": 0.25, "k": 5, "groups": "household and birthplace cluster, connected components", "strata": "birth decade x sex x region", "sequestered_file_sha256": "86a5c48a152096806b2a0d84c07e5c3766366d8eb5057b5d381c7cbd2b9d98ba"})
- analysis code `d9e60e44a12abe1e9454e4a09c15c26e2d22e7ba894336c9e8e817bc9809ad94`

## Synthetic — Lift of the tier, per area (tests 2 and 5)

Positive prediction: tier strong or moderate. n is the predicted charts with the outcome recorded; coverage is their share of all charts with it (the rest abstain).

| area | n | coverage | base rate | lift | 95% CI | p (permutation) | BH p | survives | power (5 pt, α 0.01) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| personality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| wealth | 15065 | 1.000 | 0.302 | 1.088 | 1.057–1.119 | 0.0010 | 0.0011 | yes | 1.000 |
| siblings | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mother_home | 15065 | 1.000 | 0.511 | 1.082 | 1.059–1.104 | 0.0010 | 0.0011 | yes | 0.999 |
| children | 15065 | 1.000 | 0.300 | 1.078 | 1.036–1.119 | 0.0010 | 0.0011 | yes | 0.999 |
| intellect | 15065 | 1.000 | 0.302 | 1.128 | 1.091–1.160 | 0.0010 | 0.0011 | yes | 1.000 |
| health | 15065 | 1.000 | 0.514 | 1.068 | 1.049–1.085 | 0.0010 | 0.0011 | yes | 1.000 |
| debts_enemies | 0 | – | – | – | – | – | – | not_testable_yet | – |
| marriage | 15065 | 1.000 | 0.297 | 1.085 | 1.045–1.128 | 0.0010 | 0.0011 | yes | 1.000 |
| longevity | 0 | – | – | – | – | – | – | not_testable_yet | – |
| father | 15065 | 1.000 | 0.299 | 1.061 | 1.029–1.095 | 0.0010 | 0.0011 | yes | 1.000 |
| fortune | 0 | – | – | – | – | – | – | not_testable_yet | – |
| career | 15065 | 1.000 | 0.513 | 1.064 | 1.040–1.088 | 0.0010 | 0.0011 | yes | 0.999 |
| gains | 15065 | 1.000 | 0.302 | 1.081 | 1.047–1.115 | 0.0010 | 0.0011 | yes | 1.000 |
| foreign | 15065 | 1.000 | 0.302 | 1.093 | 1.059–1.123 | 0.0010 | 0.0011 | yes | 1.000 |
| spirituality | 0 | – | – | – | – | – | – | not_testable_yet | – |
| mind | 0 | – | – | – | – | – | – | not_testable_yet | – |
| reputation | 15065 | 1.000 | 0.302 | 1.025 | 0.989–1.060 | 0.0959 | 0.0959 | no | 1.000 |

## Synthetic — Incremental validity: nested models (test 3)

| area | n | coverage | engine terms | LR | df | p (LR) | AUC covariates | AUC + engine | DeLong p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15065 | 1.000 | 8 | 101.29 | 8 | 0.0000 | 0.490 | 0.536 | 0.0000 |
| mother_home | 15065 | 1.000 | 8 | 164.56 | 8 | 0.0000 | 0.508 | 0.553 | 0.0000 |
| children | 15065 | 1.000 | 7 | 95.93 | 7 | 0.0000 | 0.506 | 0.545 | 0.0000 |
| intellect | 15065 | 1.000 | 8 | 109.45 | 8 | 0.0000 | 0.514 | 0.545 | 0.0000 |
| health | 15065 | 1.000 | 8 | 152.17 | 8 | 0.0000 | 0.502 | 0.549 | 0.0000 |
| marriage | 15065 | 1.000 | 8 | 99.10 | 8 | 0.0000 | 0.500 | 0.539 | 0.0000 |
| father | 15065 | 1.000 | 7 | 49.99 | 7 | 0.0000 | 0.509 | 0.522 | 0.0089 |
| career | 15065 | 1.000 | 8 | 117.84 | 8 | 0.0000 | 0.506 | 0.545 | 0.0000 |
| gains | 15065 | 1.000 | 8 | 96.63 | 8 | 0.0000 | 0.490 | 0.533 | 0.0000 |
| foreign | 15065 | 1.000 | 7 | 103.92 | 7 | 0.0000 | 0.506 | 0.546 | 0.0000 |
| reputation | 15065 | 1.000 | 8 | 78.84 | 8 | 0.0000 | 0.514 | 0.542 | 0.0000 |

## Synthetic — Timing as a discrete-time hazard (test 4)

Activation: the year mostly inside an antardasha the engine's window gate counts as relevant to the area. Rate ratio: Mantel-Haenszel over 5-year age bins; p against coverage-matched random windows.

| area | n | coverage | person-years | events | active share | rate ratio | p (random windows) | log-odds (95% CI) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15065 | 1.000 | 732314 | 4544 | 0.933 | 1.428 | 0.0050 | 0.358 (0.221, 0.495) |
| mother_home | 15065 | 1.000 | 631620 | 7704 | 0.943 | 1.199 | 0.0050 | 0.183 (0.078, 0.289) |
| children | 15065 | 1.000 | 730909 | 4527 | 0.904 | 1.372 | 0.0050 | 0.318 (0.205, 0.431) |
| intellect | 15065 | 1.000 | 731395 | 4547 | 0.946 | 1.554 | 0.0050 | 0.443 (0.285, 0.601) |
| health | 15065 | 1.000 | 629865 | 7744 | 0.938 | 1.363 | 0.0050 | 0.313 (0.206, 0.420) |
| marriage | 15065 | 1.000 | 731898 | 4479 | 0.940 | 1.399 | 0.0050 | 0.338 (0.193, 0.482) |
| father | 15065 | 1.000 | 732191 | 4508 | 0.880 | 0.944 | 0.4527 | -0.058 (-0.147, 0.030) |
| career | 15065 | 1.000 | 630158 | 7731 | 0.954 | 1.260 | 0.0050 | 0.234 (0.115, 0.352) |
| gains | 15065 | 1.000 | 732314 | 4544 | 0.870 | 1.234 | 0.0050 | 0.212 (0.118, 0.306) |
| foreign | 15065 | 1.000 | 732681 | 4556 | 0.952 | 1.182 | 0.0050 | 0.168 (0.020, 0.315) |
| reputation | 15065 | 1.000 | 731395 | 4547 | 0.891 | 1.129 | 0.0100 | 0.122 (0.024, 0.221) |

## Synthetic — Calibration (test 7)

Isotonic map from the area score to the event rate. Probability language needs ≥ 200 positives in every bin, on the sequestered cohort.

| area | n | coverage | ECE (development folds) | ECE (sequestered) | bins | smallest bin positives | probability language |
| --- | --- | --- | --- | --- | --- | --- | --- |
| wealth | 15065 | 1.000 | 0.003 | 0.013 | 4 | 2 | not allowed |
| mother_home | 15065 | 1.000 | 0.008 | 0.003 | 3 | 200 | allowed |
| children | 15065 | 1.000 | 0.009 | 0.002 | 5 | 2 | not allowed |
| intellect | 15065 | 1.000 | 0.006 | 0.004 | 4 | 3 | not allowed |
| health | 15065 | 1.000 | 0.010 | 0.010 | 8 | 1 | not allowed |
| marriage | 15065 | 1.000 | 0.003 | 0.017 | 6 | 1 | not allowed |
| father | 15065 | 1.000 | 0.003 | 0.007 | 3 | 20 | not allowed |
| career | 15065 | 1.000 | 0.003 | 0.014 | 5 | 0 | not allowed |
| gains | 15065 | 1.000 | 0.004 | 0.008 | 6 | 0 | not allowed |
| foreign | 15065 | 1.000 | 0.012 | 0.009 | 6 | 0 | not allowed |
| reputation | 15065 | 1.000 | 0.006 | 0.005 | 2 | 663 | allowed |

## Synthetic — Power at the current n (pre-registration table)

| area | n | coverage | predicted | power, 5-point lift, α 0.01 | power, 5-point lift, α 0.05 |
| --- | --- | --- | --- | --- | --- |
| wealth | 15065 | 1.000 | 5452 | 1.000 | 1.000 |
| mother_home | 15065 | 1.000 | 4452 | 0.999 | 1.000 |
| children | 15065 | 1.000 | 4058 | 0.999 | 1.000 |
| intellect | 15065 | 1.000 | 4776 | 1.000 | 1.000 |
| health | 15065 | 1.000 | 6248 | 1.000 | 1.000 |
| marriage | 15065 | 1.000 | 4129 | 1.000 | 1.000 |
| father | 15065 | 1.000 | 5249 | 1.000 | 1.000 |
| career | 15065 | 1.000 | 4425 | 0.999 | 1.000 |
| gains | 15065 | 1.000 | 5152 | 1.000 | 1.000 |
| foreign | 15065 | 1.000 | 5642 | 1.000 | 1.000 |
| reputation | 15065 | 1.000 | 4617 | 1.000 | 1.000 |

## Synthetic — Per-rule effects (test 6)

Effect: event rate where the rule fires minus where it does not, on the development set; an effect counts after Benjamini-Hochberg across the rules tested (q 0.01). classical_rejected is a recommendation for a powered null (power ≥ 0.8 for a 5-point lift), never applied by this script.

- classical_rejected (recommended: powered null): 255 rules
- effect on development data: 12 rules
- not_testable_yet: 51 rules
- not_testable_yet (under-powered): 93 rules

| rule | n | fired | effect | 95% CI | p | power (5 pt, α 0.01) | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `place.jupiter_h1` | 15065 | 1245 | 0.019 | -0.010–0.048 | 0.1917 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h10` | 15065 | 1293 | 0.002 | -0.026–0.031 | 0.8860 | 0.808 | classical_rejected (recommended: powered null) |
| `place.jupiter_h11` | 15065 | 1243 | -0.001 | -0.030–0.028 | 0.9585 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h12` | 15065 | 1266 | -0.002 | -0.028–0.025 | 0.9048 | 0.860 | classical_rejected (recommended: powered null) |
| `place.jupiter_h2` | 15065 | 1243 | 0.008 | -0.021–0.037 | 0.5887 | 0.791 | not_testable_yet (under-powered) |
| `place.jupiter_h3` | 15065 | 1279 | 0.003 | -0.026–0.032 | 0.8311 | 0.803 | classical_rejected (recommended: powered null) |
| `place.jupiter_h4` | 15065 | 1221 | 0.036 | 0.009–0.064 | 0.0098 | 0.850 | classical_rejected (recommended: powered null) |
| `place.jupiter_h5` | 15065 | 1263 | 0.001 | -0.025–0.028 | 0.9249 | 0.861 | classical_rejected (recommended: powered null) |
| `place.jupiter_h6` | 15065 | 1261 | 0.023 | -0.006–0.052 | 0.1140 | 0.797 | not_testable_yet (under-powered) |
| `place.jupiter_h7` | 15065 | 1271 | -0.012 | -0.038–0.014 | 0.3685 | 0.864 | classical_rejected (recommended: powered null) |
| `place.jupiter_h8` | 15065 | 1228 | 0.023 | -0.006–0.052 | 0.1242 | 0.785 | not_testable_yet (under-powered) |
| `place.jupiter_h9` | 15065 | 1252 | -0.006 | -0.032–0.021 | 0.6685 | 0.856 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aquarius` | 15065 | 1175 | -0.008 | -0.036–0.020 | 0.5809 | 0.824 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_aries` | 15065 | 1346 | -0.026 | -0.053–0.001 | 0.0590 | 0.878 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_cancer` | 15065 | 1327 | 0.058 | 0.032–0.083 | 0.0000 | 0.869 | effect on development data |
| `place.jupiter_in_capricorn` | 15065 | 1255 | -0.064 | -0.093–-0.036 | 0.0000 | 0.855 | effect on development data |
| `place.jupiter_in_gemini` | 15065 | 1179 | 0.001 | -0.028–0.029 | 0.9641 | 0.825 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_leo` | 15065 | 1358 | 0.023 | -0.003–0.049 | 0.0857 | 0.879 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_libra` | 15065 | 1327 | -0.018 | -0.045–0.009 | 0.2003 | 0.873 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_pisces` | 15065 | 1101 | 0.010 | -0.019–0.039 | 0.5133 | 0.795 | not_testable_yet (under-powered) |
| `place.jupiter_in_sagittarius` | 15065 | 1240 | 0.030 | 0.003–0.057 | 0.0321 | 0.845 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_scorpio` | 15065 | 1230 | 0.022 | -0.005–0.050 | 0.1087 | 0.842 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_taurus` | 15065 | 1175 | 0.009 | -0.020–0.037 | 0.5488 | 0.823 | classical_rejected (recommended: powered null) |
| `place.jupiter_in_virgo` | 15065 | 1352 | -0.033 | -0.060–-0.006 | 0.0161 | 0.880 | classical_rejected (recommended: powered null) |
| `place.ketu_h1` | 15065 | 1284 | -0.029 | -0.058–-0.000 | 0.0470 | 0.805 | classical_rejected (recommended: powered null) |
| `place.ketu_h10` | 15065 | 1200 | 0.004 | -0.026–0.033 | 0.8009 | 0.775 | not_testable_yet (under-powered) |
| `place.ketu_h11` | 15065 | 1263 | -0.011 | -0.040–0.017 | 0.4397 | 0.798 | not_testable_yet (under-powered) |
| `place.ketu_h12` | 15065 | 1283 | -0.020 | -0.045–0.006 | 0.1373 | 0.864 | classical_rejected (recommended: powered null) |
| `place.ketu_h2` | 15065 | 1251 | 0.018 | -0.011–0.047 | 0.2138 | 0.793 | not_testable_yet (under-powered) |
| `place.ketu_h3` | 15065 | 1264 | 0.025 | -0.003–0.054 | 0.0838 | 0.798 | not_testable_yet (under-powered) |
| `place.ketu_h4` | 15065 | 1268 | 0.000 | -0.026–0.027 | 0.9726 | 0.861 | classical_rejected (recommended: powered null) |
| `place.ketu_h5` | 15065 | 1267 | 0.020 | -0.007–0.047 | 0.1421 | 0.863 | classical_rejected (recommended: powered null) |
| `place.ketu_h6` | 15065 | 1279 | 0.004 | -0.025–0.033 | 0.7904 | 0.803 | classical_rejected (recommended: powered null) |
| `place.ketu_h7` | 15065 | 1276 | -0.013 | -0.039–0.013 | 0.3198 | 0.866 | classical_rejected (recommended: powered null) |
| `place.ketu_h8` | 15065 | 1267 | 0.017 | -0.012–0.046 | 0.2464 | 0.799 | not_testable_yet (under-powered) |
| `place.ketu_h9` | 15065 | 1163 | -0.003 | -0.030–0.025 | 0.8564 | 0.828 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aquarius` | 15065 | 1561 | -0.005 | -0.029–0.019 | 0.6790 | 0.924 | classical_rejected (recommended: powered null) |
| `place.ketu_in_aries` | 15065 | 1111 | 0.019 | -0.009–0.048 | 0.1808 | 0.810 | classical_rejected (recommended: powered null) |
| `place.ketu_in_cancer` | 15065 | 1073 | -0.009 | -0.037–0.020 | 0.5550 | 0.794 | not_testable_yet (under-powered) |
| `place.ketu_in_capricorn` | 15065 | 1511 | 0.013 | -0.012–0.037 | 0.3187 | 0.916 | classical_rejected (recommended: powered null) |
| `place.ketu_in_gemini` | 15065 | 1232 | 0.001 | -0.026–0.028 | 0.9271 | 0.850 | classical_rejected (recommended: powered null) |
| `place.ketu_in_leo` | 15065 | 1175 | 0.004 | -0.023–0.032 | 0.7590 | 0.832 | classical_rejected (recommended: powered null) |
| `place.ketu_in_libra` | 15065 | 1189 | -0.004 | -0.031–0.023 | 0.7624 | 0.836 | classical_rejected (recommended: powered null) |
| `place.ketu_in_pisces` | 15065 | 1492 | 0.012 | -0.012–0.037 | 0.3233 | 0.913 | classical_rejected (recommended: powered null) |
| `place.ketu_in_sagittarius` | 15065 | 1239 | 0.003 | -0.024–0.030 | 0.8317 | 0.853 | classical_rejected (recommended: powered null) |
| `place.ketu_in_scorpio` | 15065 | 1172 | -0.021 | -0.048–0.006 | 0.1305 | 0.830 | classical_rejected (recommended: powered null) |
| `place.ketu_in_taurus` | 15065 | 1137 | -0.013 | -0.041–0.014 | 0.3469 | 0.818 | classical_rejected (recommended: powered null) |
| `place.ketu_in_virgo` | 15065 | 1173 | -0.006 | -0.033–0.021 | 0.6537 | 0.831 | classical_rejected (recommended: powered null) |
| `place.l10_h1` | 15065 | 1306 | -0.010 | -0.034–0.015 | 0.4307 | 0.947 | classical_rejected (recommended: powered null) |
| `place.l10_h10` | 15065 | 1297 | 0.052 | 0.024–0.080 | 0.0003 | 0.809 | effect on development data |
| `place.l10_h11` | 15065 | 1255 | -0.032 | -0.061–-0.003 | 0.0289 | 0.795 | not_testable_yet (under-powered) |
| `place.l10_h12` | 15065 | 1225 | -0.007 | -0.034–0.021 | 0.6452 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l10_h2` | 15065 | 1250 | -0.006 | -0.035–0.023 | 0.7023 | 0.793 | not_testable_yet (under-powered) |
| `place.l10_h3` | 15065 | 1252 | -0.002 | -0.031–0.027 | 0.8828 | 0.794 | not_testable_yet (under-powered) |
| `place.l10_h4` | 15065 | 1282 | 0.023 | -0.003–0.050 | 0.0876 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l10_h5` | 15065 | 1232 | 0.029 | 0.002–0.056 | 0.0357 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l10_h6` | 15065 | 1234 | 0.000 | -0.025–0.025 | 0.9974 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l10_h7` | 15065 | 1247 | -0.010 | -0.037–0.018 | 0.4933 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l10_h8` | 15065 | 1284 | 0.019 | -0.005–0.043 | 0.1233 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l10_h9` | 15065 | 1201 | -0.011 | -0.039–0.017 | 0.4301 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l11_h1` | 15065 | 1271 | 0.006 | -0.018–0.030 | 0.6333 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l11_h10` | 15065 | 1205 | -0.002 | -0.032–0.027 | 0.8864 | 0.777 | not_testable_yet (under-powered) |
| `place.l11_h11` | 15065 | 1234 | 0.069 | 0.040–0.097 | 0.0000 | 0.787 | effect on development data |
| `place.l11_h12` | 15065 | 1219 | -0.030 | -0.058–-0.002 | 0.0383 | 0.844 | classical_rejected (recommended: powered null) |
| `place.l11_h2` | 15065 | 1277 | -0.016 | -0.044–0.013 | 0.2837 | 0.803 | classical_rejected (recommended: powered null) |
| `place.l11_h3` | 15065 | 1231 | -0.022 | -0.051–0.007 | 0.1414 | 0.787 | not_testable_yet (under-powered) |
| `place.l11_h4` | 15065 | 1286 | -0.035 | -0.063–-0.007 | 0.0128 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l11_h5` | 15065 | 1265 | 0.000 | -0.027–0.028 | 0.9853 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l11_h6` | 15065 | 1268 | -0.002 | -0.027–0.022 | 0.8464 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l11_h7` | 15065 | 1316 | 0.029 | 0.003–0.055 | 0.0314 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l11_h8` | 15065 | 1194 | -0.006 | -0.031–0.019 | 0.6472 | 0.925 | classical_rejected (recommended: powered null) |
| `place.l11_h9` | 15065 | 1299 | 0.002 | -0.025–0.029 | 0.8625 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l12_h1` | 15065 | 1253 | -0.012 | -0.040–0.016 | 0.3926 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l12_h10` | 15065 | 1255 | -0.007 | -0.035–0.020 | 0.6138 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l12_h11` | 15065 | 1211 | -0.018 | -0.046–0.010 | 0.2080 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l12_h12` | 15065 | 1188 | 0.038 | 0.010–0.066 | 0.0075 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l12_h2` | 15065 | 1256 | 0.007 | -0.020–0.034 | 0.6085 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l12_h3` | 15065 | 1350 | -0.032 | -0.059–-0.005 | 0.0215 | 0.882 | classical_rejected (recommended: powered null) |
| `place.l12_h4` | 15065 | 1293 | 0.016 | -0.012–0.045 | 0.2604 | 0.808 | classical_rejected (recommended: powered null) |
| `place.l12_h5` | 15065 | 1229 | 0.012 | -0.017–0.041 | 0.4072 | 0.785 | not_testable_yet (under-powered) |
| `place.l12_h6` | 15065 | 1212 | -0.023 | -0.051–0.005 | 0.1077 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l12_h7` | 15065 | 1241 | 0.033 | 0.004–0.062 | 0.0248 | 0.789 | not_testable_yet (under-powered) |
| `place.l12_h8` | 15065 | 1314 | 0.003 | -0.023–0.030 | 0.8105 | 0.871 | classical_rejected (recommended: powered null) |
| `place.l12_h9` | 15065 | 1263 | 0.010 | -0.017–0.036 | 0.4830 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l1_h1` | 15065 | 1207 | 0.029 | 0.000–0.059 | 0.0500 | 0.777 | not_testable_yet (under-powered) |
| `place.l1_h10` | 15065 | 1265 | -0.004 | -0.029–0.021 | 0.7555 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l1_h11` | 15065 | 1285 | 0.004 | -0.021–0.028 | 0.7709 | 0.942 | classical_rejected (recommended: powered null) |
| `place.l1_h12` | 15065 | 1288 | 0.016 | -0.011–0.043 | 0.2358 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l1_h2` | 15065 | 1262 | -0.015 | -0.040–0.010 | 0.2421 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l1_h3` | 15065 | 1236 | 0.001 | -0.023–0.026 | 0.9154 | 0.933 | classical_rejected (recommended: powered null) |
| `place.l1_h4` | 15065 | 1296 | -0.024 | -0.051–0.004 | 0.0913 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l1_h5` | 15065 | 1201 | -0.031 | -0.059–-0.002 | 0.0344 | 0.837 | classical_rejected (recommended: powered null) |
| `place.l1_h6` | 15065 | 1271 | 0.017 | -0.012–0.046 | 0.2484 | 0.800 | classical_rejected (recommended: powered null) |
| `place.l1_h7` | 15065 | 1207 | -0.024 | -0.052–0.005 | 0.0997 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l1_h8` | 15065 | 1252 | 0.013 | -0.015–0.042 | 0.3620 | 0.794 | not_testable_yet (under-powered) |
| `place.l1_h9` | 15065 | 1295 | 0.008 | -0.019–0.035 | 0.5596 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l2_h1` | 15065 | 1222 | 0.010 | -0.015–0.035 | 0.4285 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l2_h10` | 15065 | 1310 | -0.017 | -0.045–0.011 | 0.2413 | 0.814 | classical_rejected (recommended: powered null) |
| `place.l2_h11` | 15065 | 1214 | 0.051 | 0.022–0.080 | 0.0006 | 0.780 | not_testable_yet (under-powered) |
| `place.l2_h12` | 15065 | 1286 | -0.004 | -0.031–0.023 | 0.7777 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l2_h2` | 15065 | 1183 | 0.018 | -0.011–0.048 | 0.2270 | 0.768 | not_testable_yet (under-powered) |
| `place.l2_h3` | 15065 | 1316 | -0.020 | -0.049–0.008 | 0.1601 | 0.816 | classical_rejected (recommended: powered null) |
| `place.l2_h4` | 15065 | 1226 | 0.024 | -0.003–0.051 | 0.0833 | 0.841 | classical_rejected (recommended: powered null) |
| `place.l2_h5` | 15065 | 1297 | 0.001 | -0.026–0.028 | 0.9362 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l2_h6` | 15065 | 1253 | -0.005 | -0.030–0.020 | 0.7097 | 0.937 | classical_rejected (recommended: powered null) |
| `place.l2_h7` | 15065 | 1255 | 0.001 | -0.027–0.028 | 0.9660 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l2_h8` | 15065 | 1261 | -0.014 | -0.039–0.011 | 0.2629 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l2_h9` | 15065 | 1242 | -0.011 | -0.039–0.017 | 0.4350 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l3_h1` | 15065 | 1266 | 0.004 | -0.020–0.028 | 0.7452 | 0.939 | classical_rejected (recommended: powered null) |
| `place.l3_h10` | 15065 | 1235 | 0.007 | -0.022–0.036 | 0.6248 | 0.788 | not_testable_yet (under-powered) |
| `place.l3_h11` | 15065 | 1312 | -0.005 | -0.034–0.023 | 0.7163 | 0.814 | classical_rejected (recommended: powered null) |
| `place.l3_h12` | 15065 | 1215 | 0.006 | -0.021–0.034 | 0.6456 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l3_h2` | 15065 | 1263 | 0.019 | -0.010–0.048 | 0.1980 | 0.798 | not_testable_yet (under-powered) |
| `place.l3_h3` | 15065 | 1287 | 0.006 | -0.023–0.034 | 0.7027 | 0.806 | classical_rejected (recommended: powered null) |
| `place.l3_h4` | 15065 | 1274 | -0.004 | -0.031–0.024 | 0.7874 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l3_h5` | 15065 | 1285 | 0.016 | -0.011–0.043 | 0.2343 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l3_h6` | 15065 | 1227 | -0.013 | -0.038–0.012 | 0.3143 | 0.932 | classical_rejected (recommended: powered null) |
| `place.l3_h7` | 15065 | 1195 | 0.009 | -0.019–0.037 | 0.5302 | 0.828 | classical_rejected (recommended: powered null) |
| `place.l3_h8` | 15065 | 1218 | -0.012 | -0.038–0.013 | 0.3412 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l3_h9` | 15065 | 1288 | -0.012 | -0.039–0.015 | 0.3952 | 0.864 | classical_rejected (recommended: powered null) |
| `place.l4_h1` | 15065 | 1203 | -0.019 | -0.047–0.009 | 0.1924 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h10` | 15065 | 1244 | -0.019 | -0.047–0.009 | 0.1812 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l4_h11` | 15065 | 1224 | 0.004 | -0.024–0.032 | 0.7777 | 0.842 | classical_rejected (recommended: powered null) |
| `place.l4_h12` | 15065 | 1298 | -0.013 | -0.041–0.016 | 0.3761 | 0.810 | classical_rejected (recommended: powered null) |
| `place.l4_h2` | 15065 | 1298 | 0.023 | -0.003–0.050 | 0.0839 | 0.863 | classical_rejected (recommended: powered null) |
| `place.l4_h3` | 15065 | 1206 | -0.004 | -0.032–0.024 | 0.7675 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l4_h4` | 15065 | 1191 | 0.021 | -0.007–0.048 | 0.1403 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l4_h5` | 15065 | 1329 | -0.003 | -0.031–0.025 | 0.8388 | 0.819 | classical_rejected (recommended: powered null) |
| `place.l4_h6` | 15065 | 1246 | -0.011 | -0.039–0.016 | 0.4186 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l4_h7` | 15065 | 1279 | 0.007 | -0.021–0.036 | 0.6154 | 0.803 | classical_rejected (recommended: powered null) |
| `place.l4_h8` | 15065 | 1256 | -0.014 | -0.041–0.014 | 0.3353 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l4_h9` | 15065 | 1291 | -0.006 | -0.034–0.023 | 0.6985 | 0.807 | classical_rejected (recommended: powered null) |
| `place.l5_h1` | 15065 | 1258 | -0.019 | -0.046–0.009 | 0.1870 | 0.855 | classical_rejected (recommended: powered null) |
| `place.l5_h10` | 15065 | 1306 | 0.010 | -0.017–0.036 | 0.4845 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l5_h11` | 15065 | 1243 | -0.003 | -0.030–0.025 | 0.8386 | 0.847 | classical_rejected (recommended: powered null) |
| `place.l5_h12` | 15065 | 1170 | 0.005 | -0.024–0.035 | 0.7205 | 0.762 | not_testable_yet (under-powered) |
| `place.l5_h2` | 15065 | 1283 | 0.023 | -0.004–0.049 | 0.0988 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l5_h3` | 15065 | 1279 | 0.000 | -0.027–0.027 | 0.9943 | 0.858 | classical_rejected (recommended: powered null) |
| `place.l5_h4` | 15065 | 1256 | 0.008 | -0.021–0.036 | 0.6044 | 0.795 | not_testable_yet (under-powered) |
| `place.l5_h5` | 15065 | 1258 | 0.009 | -0.018–0.035 | 0.5245 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l5_h6` | 15065 | 1210 | -0.021 | -0.050–0.007 | 0.1367 | 0.840 | classical_rejected (recommended: powered null) |
| `place.l5_h7` | 15065 | 1221 | 0.006 | -0.023–0.035 | 0.6936 | 0.782 | not_testable_yet (under-powered) |
| `place.l5_h8` | 15065 | 1335 | 0.013 | -0.013–0.039 | 0.3361 | 0.876 | classical_rejected (recommended: powered null) |
| `place.l5_h9` | 15065 | 1246 | 0.011 | -0.018–0.040 | 0.4672 | 0.791 | not_testable_yet (under-powered) |
| `place.l6_h1` | 15065 | 1235 | 0.029 | 0.000–0.058 | 0.0482 | 0.788 | not_testable_yet (under-powered) |
| `place.l6_h10` | 15065 | 1252 | 0.028 | 0.004–0.052 | 0.0202 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l6_h11` | 15065 | 1276 | 0.002 | -0.023–0.026 | 0.8859 | 0.941 | classical_rejected (recommended: powered null) |
| `place.l6_h12` | 15065 | 1303 | -0.020 | -0.047–0.007 | 0.1495 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l6_h2` | 15065 | 1268 | -0.008 | -0.033–0.016 | 0.5033 | 0.940 | classical_rejected (recommended: powered null) |
| `place.l6_h3` | 15065 | 1223 | 0.006 | -0.019–0.030 | 0.6514 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l6_h4` | 15065 | 1252 | -0.052 | -0.080–-0.024 | 0.0003 | 0.854 | effect on development data |
| `place.l6_h5` | 15065 | 1228 | -0.010 | -0.038–0.017 | 0.4660 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l6_h6` | 15065 | 1219 | -0.005 | -0.034–0.024 | 0.7373 | 0.782 | not_testable_yet (under-powered) |
| `place.l6_h7` | 15065 | 1276 | -0.002 | -0.030–0.025 | 0.8623 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l6_h8` | 15065 | 1227 | -0.009 | -0.038–0.021 | 0.5623 | 0.785 | not_testable_yet (under-powered) |
| `place.l6_h9` | 15065 | 1306 | 0.000 | -0.027–0.027 | 0.9900 | 0.869 | classical_rejected (recommended: powered null) |
| `place.l7_h1` | 15065 | 1258 | 0.005 | -0.022–0.033 | 0.7063 | 0.854 | classical_rejected (recommended: powered null) |
| `place.l7_h10` | 15065 | 1256 | -0.006 | -0.034–0.022 | 0.6674 | 0.850 | classical_rejected (recommended: powered null) |
| `place.l7_h11` | 15065 | 1255 | -0.005 | -0.033–0.022 | 0.6968 | 0.849 | classical_rejected (recommended: powered null) |
| `place.l7_h12` | 15065 | 1262 | -0.021 | -0.050–0.008 | 0.1591 | 0.797 | not_testable_yet (under-powered) |
| `place.l7_h2` | 15065 | 1192 | 0.038 | 0.011–0.066 | 0.0066 | 0.826 | classical_rejected (recommended: powered null) |
| `place.l7_h3` | 15065 | 1364 | -0.010 | -0.037–0.017 | 0.4594 | 0.880 | classical_rejected (recommended: powered null) |
| `place.l7_h4` | 15065 | 1243 | 0.010 | -0.019–0.039 | 0.4808 | 0.790 | not_testable_yet (under-powered) |
| `place.l7_h5` | 15065 | 1297 | -0.023 | -0.051–0.006 | 0.1181 | 0.809 | classical_rejected (recommended: powered null) |
| `place.l7_h6` | 15065 | 1198 | -0.004 | -0.032–0.024 | 0.7796 | 0.835 | classical_rejected (recommended: powered null) |
| `place.l7_h7` | 15065 | 1247 | 0.016 | -0.011–0.043 | 0.2435 | 0.859 | classical_rejected (recommended: powered null) |
| `place.l7_h8` | 15065 | 1277 | -0.000 | -0.028–0.027 | 0.9768 | 0.860 | classical_rejected (recommended: powered null) |
| `place.l7_h9` | 15065 | 1216 | -0.003 | -0.032–0.026 | 0.8340 | 0.780 | not_testable_yet (under-powered) |
| `place.l8_h1` | 15065 | 1289 | 0.017 | -0.011–0.046 | 0.2338 | 0.807 | classical_rejected (recommended: powered null) |
| `place.l8_h10` | 15065 | 1156 | 0.008 | -0.017–0.033 | 0.5429 | 0.914 | classical_rejected (recommended: powered null) |
| `place.l8_h11` | 15065 | 1319 | -0.003 | -0.027–0.021 | 0.8068 | 0.948 | classical_rejected (recommended: powered null) |
| `place.l8_h12` | 15065 | 1209 | -0.009 | -0.037–0.019 | 0.5376 | 0.839 | classical_rejected (recommended: powered null) |
| `place.l8_h2` | 15065 | 1242 | 0.007 | -0.018–0.032 | 0.5772 | 0.934 | classical_rejected (recommended: powered null) |
| `place.l8_h3` | 15065 | 1228 | 0.017 | -0.007–0.042 | 0.1617 | 0.930 | classical_rejected (recommended: powered null) |
| `place.l8_h4` | 15065 | 1309 | 0.013 | -0.014–0.040 | 0.3402 | 0.867 | classical_rejected (recommended: powered null) |
| `place.l8_h5` | 15065 | 1367 | 0.012 | -0.014–0.038 | 0.3763 | 0.884 | classical_rejected (recommended: powered null) |
| `place.l8_h6` | 15065 | 1248 | -0.027 | -0.056–0.002 | 0.0711 | 0.793 | not_testable_yet (under-powered) |
| `place.l8_h7` | 15065 | 1203 | 0.001 | -0.027–0.029 | 0.9348 | 0.836 | classical_rejected (recommended: powered null) |
| `place.l8_h8` | 15065 | 1244 | 0.024 | -0.005–0.053 | 0.1022 | 0.791 | not_testable_yet (under-powered) |
| `place.l8_h9` | 15065 | 1251 | -0.010 | -0.038–0.018 | 0.4760 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l9_h1` | 15065 | 1227 | -0.002 | -0.030–0.025 | 0.8671 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l9_h10` | 15065 | 1333 | 0.014 | -0.012–0.041 | 0.2881 | 0.875 | classical_rejected (recommended: powered null) |
| `place.l9_h11` | 15065 | 1227 | -0.006 | -0.034–0.022 | 0.6762 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l9_h12` | 15065 | 1283 | 0.009 | -0.017–0.036 | 0.4879 | 0.866 | classical_rejected (recommended: powered null) |
| `place.l9_h2` | 15065 | 1290 | -0.016 | -0.044–0.011 | 0.2413 | 0.865 | classical_rejected (recommended: powered null) |
| `place.l9_h3` | 15065 | 1222 | -0.031 | -0.060–-0.003 | 0.0285 | 0.845 | classical_rejected (recommended: powered null) |
| `place.l9_h4` | 15065 | 1180 | 0.002 | -0.028–0.032 | 0.8921 | 0.767 | not_testable_yet (under-powered) |
| `place.l9_h5` | 15065 | 1340 | 0.014 | -0.014–0.042 | 0.3147 | 0.822 | classical_rejected (recommended: powered null) |
| `place.l9_h6` | 15065 | 1251 | -0.006 | -0.033–0.022 | 0.6863 | 0.853 | classical_rejected (recommended: powered null) |
| `place.l9_h7` | 15065 | 1283 | 0.016 | -0.013–0.044 | 0.2832 | 0.804 | classical_rejected (recommended: powered null) |
| `place.l9_h8` | 15065 | 1253 | 0.010 | -0.018–0.037 | 0.4837 | 0.852 | classical_rejected (recommended: powered null) |
| `place.l9_h9` | 15065 | 1176 | 0.007 | -0.021–0.034 | 0.6287 | 0.833 | classical_rejected (recommended: powered null) |
| `place.mars_h1` | 15065 | 1261 | -0.000 | -0.029–0.029 | 0.9904 | 0.797 | not_testable_yet (under-powered) |
| `place.mars_h10` | 15065 | 1288 | -0.005 | -0.034–0.023 | 0.7278 | 0.806 | classical_rejected (recommended: powered null) |
| `place.mars_h11` | 15065 | 1191 | 0.002 | -0.028–0.031 | 0.9131 | 0.771 | not_testable_yet (under-powered) |
| `place.mars_h12` | 15065 | 1206 | -0.018 | -0.044–0.009 | 0.1908 | 0.841 | classical_rejected (recommended: powered null) |
| `place.mars_h2` | 15065 | 1215 | 0.031 | 0.002–0.060 | 0.0384 | 0.780 | not_testable_yet (under-powered) |
| `place.mars_h3` | 15065 | 1242 | -0.027 | -0.056–0.002 | 0.0719 | 0.791 | not_testable_yet (under-powered) |
| `place.mars_h4` | 15065 | 1298 | -0.005 | -0.031–0.021 | 0.6791 | 0.869 | classical_rejected (recommended: powered null) |
| `place.mars_h5` | 15065 | 1310 | -0.020 | -0.045–0.006 | 0.1294 | 0.872 | classical_rejected (recommended: powered null) |
| `place.mars_h6` | 15065 | 1214 | -0.022 | -0.051–0.008 | 0.1500 | 0.780 | not_testable_yet (under-powered) |
| `place.mars_h7` | 15065 | 1268 | 0.004 | -0.022–0.031 | 0.7486 | 0.864 | classical_rejected (recommended: powered null) |
| `place.mars_h8` | 15065 | 1311 | 0.002 | -0.027–0.030 | 0.9036 | 0.814 | classical_rejected (recommended: powered null) |
| `place.mars_h9` | 15065 | 1261 | -0.015 | -0.041–0.011 | 0.2604 | 0.858 | classical_rejected (recommended: powered null) |
| `place.mars_in_aquarius` | 15065 | 918 | 0.028 | -0.006–0.061 | 0.1025 | 0.642 | not_testable_yet (under-powered) |
| `place.mars_in_aries` | 15065 | 1071 | 0.001 | -0.030–0.032 | 0.9298 | 0.720 | not_testable_yet (under-powered) |
| `place.mars_in_cancer` | 15065 | 1514 | -0.032 | -0.059–-0.006 | 0.0172 | 0.870 | classical_rejected (recommended: powered null) |
| `place.mars_in_capricorn` | 15065 | 985 | 0.020 | -0.012–0.052 | 0.2212 | 0.678 | not_testable_yet (under-powered) |
| `place.mars_in_gemini` | 15065 | 1391 | 0.019 | -0.008–0.047 | 0.1729 | 0.838 | classical_rejected (recommended: powered null) |
| `place.mars_in_leo` | 15065 | 1625 | 0.015 | -0.011–0.040 | 0.2674 | 0.893 | classical_rejected (recommended: powered null) |
| `place.mars_in_libra` | 15065 | 1410 | -0.012 | -0.040–0.015 | 0.3834 | 0.843 | classical_rejected (recommended: powered null) |
| `place.mars_in_pisces` | 15065 | 1085 | -0.003 | -0.034–0.028 | 0.8601 | 0.727 | not_testable_yet (under-powered) |
| `place.mars_in_sagittarius` | 15065 | 1152 | -0.003 | -0.033–0.027 | 0.8454 | 0.756 | not_testable_yet (under-powered) |
| `place.mars_in_scorpio` | 15065 | 1088 | 0.008 | -0.023–0.038 | 0.6292 | 0.728 | not_testable_yet (under-powered) |
| `place.mars_in_taurus` | 15065 | 1345 | -0.011 | -0.039–0.017 | 0.4499 | 0.825 | classical_rejected (recommended: powered null) |
| `place.mars_in_virgo` | 15065 | 1481 | -0.013 | -0.040–0.013 | 0.3242 | 0.862 | classical_rejected (recommended: powered null) |
| `place.mercury_h1` | 15065 | 1219 | 0.005 | -0.024–0.034 | 0.7474 | 0.782 | not_testable_yet (under-powered) |
| `place.mercury_h10` | 15065 | 1234 | 0.004 | -0.025–0.033 | 0.7781 | 0.787 | not_testable_yet (under-powered) |
| `place.mercury_h11` | 15065 | 1242 | 0.031 | 0.002–0.060 | 0.0342 | 0.790 | not_testable_yet (under-powered) |
| `place.mercury_h12` | 15065 | 1279 | -0.018 | -0.044–0.008 | 0.1792 | 0.863 | classical_rejected (recommended: powered null) |
| `place.mercury_h2` | 15065 | 1204 | 0.005 | -0.025–0.034 | 0.7575 | 0.776 | not_testable_yet (under-powered) |
| `place.mercury_h3` | 15065 | 1334 | -0.011 | -0.039–0.017 | 0.4361 | 0.821 | classical_rejected (recommended: powered null) |
| `place.mercury_h4` | 15065 | 1265 | 0.004 | -0.023–0.030 | 0.7768 | 0.861 | classical_rejected (recommended: powered null) |
| `place.mercury_h5` | 15065 | 1261 | -0.007 | -0.033–0.019 | 0.6090 | 0.860 | classical_rejected (recommended: powered null) |
| `place.mercury_h6` | 15065 | 1262 | -0.005 | -0.034–0.024 | 0.7366 | 0.798 | not_testable_yet (under-powered) |
| `place.mercury_h7` | 15065 | 1213 | 0.024 | -0.004–0.051 | 0.0898 | 0.849 | classical_rejected (recommended: powered null) |
| `place.mercury_h8` | 15065 | 1305 | 0.000 | -0.028–0.029 | 0.9917 | 0.812 | classical_rejected (recommended: powered null) |
| `place.mercury_h9` | 15065 | 1247 | 0.012 | -0.015–0.039 | 0.3760 | 0.855 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aquarius` | 15065 | 1299 | -0.015 | -0.043–0.014 | 0.3065 | 0.810 | classical_rejected (recommended: powered null) |
| `place.mercury_in_aries` | 15065 | 1095 | 0.027 | -0.004–0.057 | 0.0884 | 0.731 | not_testable_yet (under-powered) |
| `place.mercury_in_cancer` | 15065 | 1183 | -0.021 | -0.051–0.008 | 0.1619 | 0.768 | not_testable_yet (under-powered) |
| `place.mercury_in_capricorn` | 15065 | 1283 | -0.011 | -0.040–0.017 | 0.4339 | 0.805 | classical_rejected (recommended: powered null) |
| `place.mercury_in_gemini` | 15065 | 1157 | 0.025 | -0.005–0.054 | 0.1073 | 0.758 | not_testable_yet (under-powered) |
| `place.mercury_in_leo` | 15065 | 1271 | -0.025 | -0.054–0.004 | 0.0863 | 0.801 | classical_rejected (recommended: powered null) |
| `place.mercury_in_libra` | 15065 | 1411 | -0.021 | -0.049–0.006 | 0.1297 | 0.844 | classical_rejected (recommended: powered null) |
| `place.mercury_in_pisces` | 15065 | 1256 | -0.001 | -0.030–0.028 | 0.9272 | 0.795 | not_testable_yet (under-powered) |
| `place.mercury_in_sagittarius` | 15065 | 1351 | -0.001 | -0.029–0.027 | 0.9408 | 0.826 | classical_rejected (recommended: powered null) |
| `place.mercury_in_scorpio` | 15065 | 1365 | -0.009 | -0.037–0.019 | 0.5144 | 0.831 | classical_rejected (recommended: powered null) |
| `place.mercury_in_taurus` | 15065 | 1106 | -0.003 | -0.034–0.027 | 0.8233 | 0.736 | not_testable_yet (under-powered) |
| `place.mercury_in_virgo` | 15065 | 1288 | 0.064 | 0.035–0.092 | 0.0000 | 0.806 | effect on development data |
| `place.moon_h1` | 15065 | 1263 | 0.001 | -0.028–0.029 | 0.9639 | 0.798 | not_testable_yet (under-powered) |
| `place.moon_h10` | 15065 | 1308 | 0.021 | -0.008–0.049 | 0.1510 | 0.813 | classical_rejected (recommended: powered null) |
| `place.moon_h11` | 15065 | 1214 | 0.001 | -0.028–0.030 | 0.9521 | 0.780 | not_testable_yet (under-powered) |
| `place.moon_h12` | 15065 | 1212 | -0.020 | -0.047–0.006 | 0.1350 | 0.843 | classical_rejected (recommended: powered null) |
| `place.moon_h2` | 15065 | 1326 | 0.005 | -0.023–0.034 | 0.7071 | 0.819 | classical_rejected (recommended: powered null) |
| `place.moon_h3` | 15065 | 1239 | -0.013 | -0.042–0.016 | 0.3792 | 0.789 | not_testable_yet (under-powered) |
| `place.moon_h4` | 15065 | 1275 | 0.000 | -0.026–0.027 | 0.9783 | 0.863 | classical_rejected (recommended: powered null) |
| `place.moon_h5` | 15065 | 1283 | 0.013 | -0.013–0.040 | 0.3298 | 0.867 | classical_rejected (recommended: powered null) |
| `place.moon_h6` | 15065 | 1225 | -0.012 | -0.041–0.017 | 0.4141 | 0.784 | not_testable_yet (under-powered) |
| `place.moon_h7` | 15065 | 1209 | -0.020 | -0.047–0.006 | 0.1339 | 0.846 | classical_rejected (recommended: powered null) |
| `place.moon_h8` | 15065 | 1223 | 0.015 | -0.014–0.045 | 0.3004 | 0.783 | not_testable_yet (under-powered) |
| `place.moon_h9` | 15065 | 1288 | -0.016 | -0.042–0.010 | 0.2340 | 0.865 | classical_rejected (recommended: powered null) |
| `place.rahu_h1` | 15065 | 1276 | -0.004 | -0.033–0.024 | 0.7736 | 0.802 | classical_rejected (recommended: powered null) |
| `place.rahu_h10` | 15065 | 1268 | 0.005 | -0.024–0.033 | 0.7560 | 0.799 | not_testable_yet (under-powered) |
| `place.rahu_h11` | 15065 | 1267 | -0.027 | -0.056–0.002 | 0.0670 | 0.799 | not_testable_yet (under-powered) |
| `place.rahu_h12` | 15065 | 1279 | 0.033 | 0.006–0.060 | 0.0175 | 0.866 | classical_rejected (recommended: powered null) |
| `place.rahu_h2` | 15065 | 1267 | -0.002 | -0.031–0.027 | 0.8975 | 0.799 | not_testable_yet (under-powered) |
| `place.rahu_h3` | 15065 | 1163 | -0.015 | -0.045–0.015 | 0.3340 | 0.760 | not_testable_yet (under-powered) |
| `place.rahu_h4` | 15065 | 1200 | -0.007 | -0.034–0.020 | 0.6000 | 0.840 | classical_rejected (recommended: powered null) |
| `place.rahu_h5` | 15065 | 1263 | -0.017 | -0.043–0.009 | 0.2041 | 0.860 | classical_rejected (recommended: powered null) |
| `place.rahu_h6` | 15065 | 1283 | -0.002 | -0.031–0.026 | 0.8834 | 0.805 | classical_rejected (recommended: powered null) |
| `place.rahu_h7` | 15065 | 1284 | 0.048 | 0.021–0.075 | 0.0005 | 0.871 | classical_rejected (recommended: powered null) |
| `place.rahu_h8` | 15065 | 1251 | 0.003 | -0.025–0.032 | 0.8161 | 0.794 | not_testable_yet (under-powered) |
| `place.rahu_h9` | 15065 | 1264 | -0.005 | -0.032–0.021 | 0.6874 | 0.859 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aquarius` | 15065 | 1175 | 0.007 | -0.021–0.035 | 0.6223 | 0.826 | classical_rejected (recommended: powered null) |
| `place.rahu_in_aries` | 15065 | 1189 | -0.015 | -0.043–0.013 | 0.2941 | 0.833 | classical_rejected (recommended: powered null) |
| `place.rahu_in_cancer` | 15065 | 1511 | 0.016 | -0.009–0.041 | 0.2049 | 0.915 | classical_rejected (recommended: powered null) |
| `place.rahu_in_capricorn` | 15065 | 1073 | 0.008 | -0.021–0.037 | 0.5929 | 0.786 | not_testable_yet (under-powered) |
| `place.rahu_in_gemini` | 15065 | 1239 | -0.007 | -0.034–0.021 | 0.6363 | 0.849 | classical_rejected (recommended: powered null) |
| `place.rahu_in_leo` | 15065 | 1561 | -0.011 | -0.036–0.013 | 0.3677 | 0.925 | classical_rejected (recommended: powered null) |
| `place.rahu_in_libra` | 15065 | 1111 | 0.018 | -0.010–0.047 | 0.2087 | 0.801 | classical_rejected (recommended: powered null) |
| `place.rahu_in_pisces` | 15065 | 1173 | -0.025 | -0.054–0.004 | 0.0870 | 0.828 | classical_rejected (recommended: powered null) |
| `place.rahu_in_sagittarius` | 15065 | 1232 | 0.016 | -0.011–0.043 | 0.2529 | 0.845 | classical_rejected (recommended: powered null) |
| `place.rahu_in_scorpio` | 15065 | 1137 | 0.004 | -0.024–0.033 | 0.7578 | 0.812 | classical_rejected (recommended: powered null) |
| `place.rahu_in_taurus` | 15065 | 1172 | 0.012 | -0.016–0.040 | 0.4141 | 0.825 | classical_rejected (recommended: powered null) |
| `place.rahu_in_virgo` | 15065 | 1492 | -0.018 | -0.044–0.007 | 0.1619 | 0.913 | classical_rejected (recommended: powered null) |
| `place.saturn_h1` | 15065 | 1269 | -0.007 | -0.036–0.022 | 0.6256 | 0.800 | not_testable_yet (under-powered) |
| `place.saturn_h10` | 15065 | 1275 | 0.007 | -0.022–0.035 | 0.6519 | 0.802 | classical_rejected (recommended: powered null) |
| `place.saturn_h11` | 15065 | 1302 | 0.012 | -0.016–0.041 | 0.3888 | 0.811 | classical_rejected (recommended: powered null) |
| `place.saturn_h12` | 15065 | 1232 | 0.008 | -0.019–0.035 | 0.5448 | 0.851 | classical_rejected (recommended: powered null) |
| `place.saturn_h2` | 15065 | 1317 | -0.002 | -0.030–0.027 | 0.9148 | 0.816 | classical_rejected (recommended: powered null) |
| `place.saturn_h3` | 15065 | 1224 | -0.007 | -0.036–0.022 | 0.6278 | 0.784 | not_testable_yet (under-powered) |
| `place.saturn_h4` | 15065 | 1227 | -0.001 | -0.028–0.026 | 0.9433 | 0.849 | classical_rejected (recommended: powered null) |
| `place.saturn_h5` | 15065 | 1296 | -0.017 | -0.043–0.008 | 0.1887 | 0.869 | classical_rejected (recommended: powered null) |
| `place.saturn_h6` | 15065 | 1195 | -0.025 | -0.054–0.005 | 0.1000 | 0.773 | not_testable_yet (under-powered) |
| `place.saturn_h7` | 15065 | 1243 | -0.001 | -0.028–0.025 | 0.9195 | 0.857 | classical_rejected (recommended: powered null) |
| `place.saturn_h8` | 15065 | 1235 | 0.021 | -0.008–0.050 | 0.1504 | 0.788 | not_testable_yet (under-powered) |
| `place.saturn_h9` | 15065 | 1250 | 0.003 | -0.024–0.029 | 0.8488 | 0.856 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aquarius` | 15065 | 1215 | 0.019 | -0.005–0.044 | 0.1221 | 0.927 | classical_rejected (recommended: powered null) |
| `place.saturn_in_aries` | 15065 | 1535 | -0.047 | -0.071–-0.024 | 0.0001 | 0.976 | effect on development data |
| `place.saturn_in_cancer` | 15065 | 1118 | -0.019 | -0.046–0.008 | 0.1604 | 0.906 | classical_rejected (recommended: powered null) |
| `place.saturn_in_capricorn` | 15065 | 1383 | 0.029 | 0.006–0.052 | 0.0118 | 0.956 | classical_rejected (recommended: powered null) |
| `place.saturn_in_gemini` | 15065 | 1074 | -0.004 | -0.031–0.022 | 0.7559 | 0.892 | classical_rejected (recommended: powered null) |
| `place.saturn_in_leo` | 15065 | 1152 | -0.024 | -0.050–0.002 | 0.0738 | 0.916 | classical_rejected (recommended: powered null) |
| `place.saturn_in_libra` | 15065 | 1277 | 0.057 | 0.034–0.079 | 0.0000 | 0.937 | effect on development data |
| `place.saturn_in_pisces` | 15065 | 1202 | -0.006 | -0.031–0.019 | 0.6438 | 0.926 | classical_rejected (recommended: powered null) |
| `place.saturn_in_sagittarius` | 15065 | 1305 | -0.007 | -0.031–0.018 | 0.5909 | 0.946 | classical_rejected (recommended: powered null) |
| `place.saturn_in_scorpio` | 15065 | 1343 | -0.021 | -0.046–0.003 | 0.0900 | 0.953 | classical_rejected (recommended: powered null) |
| `place.saturn_in_taurus` | 15065 | 1211 | 0.024 | -0.000–0.048 | 0.0544 | 0.926 | classical_rejected (recommended: powered null) |
| `place.saturn_in_virgo` | 15065 | 1250 | 0.003 | -0.021–0.028 | 0.7878 | 0.936 | classical_rejected (recommended: powered null) |
| `place.sun_h1` | 15065 | 1222 | -0.008 | -0.037–0.021 | 0.5847 | 0.783 | not_testable_yet (under-powered) |
| `place.sun_h10` | 15065 | 1246 | 0.015 | -0.014–0.044 | 0.2976 | 0.792 | not_testable_yet (under-powered) |
| `place.sun_h11` | 15065 | 1311 | -0.013 | -0.042–0.015 | 0.3618 | 0.814 | classical_rejected (recommended: powered null) |
| `place.sun_h12` | 15065 | 1224 | -0.011 | -0.037–0.016 | 0.4256 | 0.847 | classical_rejected (recommended: powered null) |
| `place.sun_h2` | 15065 | 1264 | -0.002 | -0.031–0.026 | 0.8760 | 0.798 | not_testable_yet (under-powered) |
| `place.sun_h3` | 15065 | 1279 | -0.009 | -0.037–0.020 | 0.5450 | 0.803 | classical_rejected (recommended: powered null) |
| `place.sun_h4` | 15065 | 1289 | -0.013 | -0.039–0.013 | 0.3108 | 0.866 | classical_rejected (recommended: powered null) |
| `place.sun_h5` | 15065 | 1281 | 0.003 | -0.024–0.029 | 0.8456 | 0.866 | classical_rejected (recommended: powered null) |
| `place.sun_h6` | 15065 | 1202 | -0.019 | -0.048–0.011 | 0.2093 | 0.776 | not_testable_yet (under-powered) |
| `place.sun_h7` | 15065 | 1255 | 0.013 | -0.014–0.040 | 0.3422 | 0.861 | classical_rejected (recommended: powered null) |
| `place.sun_h8` | 15065 | 1246 | -0.002 | -0.031–0.027 | 0.8827 | 0.792 | not_testable_yet (under-powered) |
| `place.sun_h9` | 15065 | 1246 | 0.019 | -0.008–0.046 | 0.1785 | 0.855 | classical_rejected (recommended: powered null) |
| `place.sun_in_aquarius` | 15065 | 1242 | -0.006 | -0.035–0.023 | 0.6626 | 0.790 | not_testable_yet (under-powered) |
| `place.sun_in_aries` | 15065 | 1244 | 0.022 | -0.007–0.051 | 0.1443 | 0.791 | not_testable_yet (under-powered) |
| `place.sun_in_cancer` | 15065 | 1302 | -0.013 | -0.041–0.016 | 0.3795 | 0.811 | classical_rejected (recommended: powered null) |
| `place.sun_in_capricorn` | 15065 | 1275 | -0.018 | -0.047–0.010 | 0.2124 | 0.802 | classical_rejected (recommended: powered null) |
| `place.sun_in_gemini` | 15065 | 1259 | 0.016 | -0.013–0.044 | 0.2909 | 0.796 | not_testable_yet (under-powered) |
| `place.sun_in_leo` | 15065 | 1300 | 0.012 | -0.017–0.040 | 0.4204 | 0.810 | classical_rejected (recommended: powered null) |
| `place.sun_in_libra` | 15065 | 1222 | -0.014 | -0.044–0.015 | 0.3365 | 0.783 | not_testable_yet (under-powered) |
| `place.sun_in_pisces` | 15065 | 1266 | -0.001 | -0.029–0.028 | 0.9681 | 0.799 | not_testable_yet (under-powered) |
| `place.sun_in_sagittarius` | 15065 | 1175 | -0.016 | -0.045–0.014 | 0.3021 | 0.765 | not_testable_yet (under-powered) |
| `place.sun_in_scorpio` | 15065 | 1214 | -0.002 | -0.031–0.028 | 0.9049 | 0.780 | not_testable_yet (under-powered) |
| `place.sun_in_taurus` | 15065 | 1278 | -0.005 | -0.034–0.024 | 0.7327 | 0.803 | classical_rejected (recommended: powered null) |
| `place.sun_in_virgo` | 15065 | 1288 | 0.025 | -0.004–0.053 | 0.0900 | 0.806 | classical_rejected (recommended: powered null) |
| `place.venus_h1` | 15065 | 1261 | 0.011 | -0.018–0.040 | 0.4510 | 0.797 | not_testable_yet (under-powered) |
| `place.venus_h10` | 15065 | 1190 | -0.004 | -0.034–0.025 | 0.7774 | 0.771 | not_testable_yet (under-powered) |
| `place.venus_h11` | 15065 | 1287 | 0.005 | -0.024–0.033 | 0.7465 | 0.806 | classical_rejected (recommended: powered null) |
| `place.venus_h12` | 15065 | 1272 | -0.006 | -0.032–0.021 | 0.6685 | 0.862 | classical_rejected (recommended: powered null) |
| `place.venus_h2` | 15065 | 1258 | -0.033 | -0.062–-0.005 | 0.0230 | 0.796 | not_testable_yet (under-powered) |
| `place.venus_h3` | 15065 | 1259 | -0.008 | -0.037–0.021 | 0.5925 | 0.796 | not_testable_yet (under-powered) |
| `place.venus_h4` | 15065 | 1251 | 0.009 | -0.017–0.036 | 0.4957 | 0.857 | classical_rejected (recommended: powered null) |
| `place.venus_h5` | 15065 | 1252 | -0.011 | -0.037–0.016 | 0.4273 | 0.857 | classical_rejected (recommended: powered null) |
| `place.venus_h6` | 15065 | 1273 | -0.001 | -0.030–0.028 | 0.9359 | 0.801 | classical_rejected (recommended: powered null) |
| `place.venus_h7` | 15065 | 1258 | 0.014 | -0.013–0.041 | 0.3083 | 0.862 | classical_rejected (recommended: powered null) |
| `place.venus_h8` | 15065 | 1244 | -0.014 | -0.043–0.015 | 0.3599 | 0.791 | not_testable_yet (under-powered) |
| `place.venus_h9` | 15065 | 1260 | 0.013 | -0.014–0.040 | 0.3429 | 0.859 | classical_rejected (recommended: powered null) |
| `place.venus_in_aquarius` | 15065 | 1093 | 0.002 | -0.026–0.030 | 0.8888 | 0.806 | classical_rejected (recommended: powered null) |
| `place.venus_in_aries` | 15065 | 1171 | -0.026 | -0.053–0.001 | 0.0551 | 0.833 | classical_rejected (recommended: powered null) |
| `place.venus_in_cancer` | 15065 | 1152 | -0.001 | -0.029–0.026 | 0.9196 | 0.828 | classical_rejected (recommended: powered null) |
| `place.venus_in_capricorn` | 15065 | 1484 | -0.001 | -0.025–0.024 | 0.9422 | 0.913 | classical_rejected (recommended: powered null) |
| `place.venus_in_gemini` | 15065 | 1439 | -0.002 | -0.027–0.023 | 0.8634 | 0.905 | classical_rejected (recommended: powered null) |
| `place.venus_in_leo` | 15065 | 1510 | -0.002 | -0.026–0.022 | 0.8612 | 0.918 | classical_rejected (recommended: powered null) |
| `place.venus_in_libra` | 15065 | 1412 | 0.027 | 0.001–0.052 | 0.0402 | 0.901 | classical_rejected (recommended: powered null) |
| `place.venus_in_pisces` | 15065 | 1352 | 0.043 | 0.017–0.069 | 0.0013 | 0.888 | classical_rejected (recommended: powered null) |
| `place.venus_in_sagittarius` | 15065 | 1068 | -0.022 | -0.050–0.006 | 0.1274 | 0.795 | not_testable_yet (under-powered) |
| `place.venus_in_scorpio` | 15065 | 1130 | -0.021 | -0.048–0.006 | 0.1300 | 0.819 | classical_rejected (recommended: powered null) |
| `place.venus_in_taurus` | 15065 | 1228 | 0.019 | -0.009–0.046 | 0.1795 | 0.854 | classical_rejected (recommended: powered null) |
| `place.venus_in_virgo` | 15065 | 1026 | -0.031 | -0.060–-0.003 | 0.0286 | 0.777 | not_testable_yet (under-powered) |
| `yoga.bhadra` | 15065 | 1915 | 0.051 | 0.027–0.075 | 0.0000 | 0.936 | effect on development data |
| `yoga.budhaditya` | 15065 | 7841 | 0.011 | -0.005–0.027 | 0.1898 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari` | 15065 | 5052 | 0.019 | 0.003–0.035 | 0.0206 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.gaja_kesari_bphs` | 15065 | 1478 | 0.039 | 0.014–0.064 | 0.0023 | 0.906 | classical_rejected (recommended: powered null) |
| `yoga.hamsa` | 15065 | 2629 | 0.042 | 0.021–0.063 | 0.0001 | 0.982 | effect on development data |
| `yoga.kendra_trikona_raja` | 15065 | 8113 | 0.008 | -0.008–0.024 | 0.3497 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.kendra_trikona_raja_weak` | 15065 | 9711 | -0.013 | -0.030–0.004 | 0.1299 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.malavya` | 15065 | 2618 | 0.031 | 0.010–0.052 | 0.0035 | 0.981 | classical_rejected (recommended: powered null) |
| `yoga.neecha_bhanga` | 15065 | 6712 | -0.030 | -0.047–-0.014 | 0.0002 | 1.000 | effect on development data |
| `yoga.parivartana` | 15065 | 5590 | -0.019 | -0.035–-0.003 | 0.0173 | 1.000 | classical_rejected (recommended: powered null) |
| `yoga.ruchaka` | 15065 | 2193 | 0.009 | -0.013–0.032 | 0.4156 | 0.961 | classical_rejected (recommended: powered null) |
| `yoga.sasa` | 15065 | 2706 | 0.054 | 0.034–0.075 | 0.0000 | 0.984 | effect on development data |

## Synthetic — Not tested

Areas with no mapped outcome, or too little data:

- personality: not_testable_yet (no measured outcome is mapped to this area)
- siblings: not_testable_yet (no measured outcome is mapped to this area)
- debts_enemies: not_testable_yet (no measured outcome is mapped to this area)
- longevity: not_testable_yet (no measured outcome is mapped to this area)
- fortune: not_testable_yet (no measured outcome is mapped to this area)
- spirituality: not_testable_yet (no measured outcome is mapped to this area)
- mind: not_testable_yet (no measured outcome is mapped to this area)
