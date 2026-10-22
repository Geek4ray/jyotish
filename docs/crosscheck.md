# Phase 0 cross-check: the engine against PyJHora

Run 2026-10-22 at commit `232e8f0` by `scripts/crosscheck.py --n 1000 --seed 0` in 8 s. PyJHora 4.8.7; ephemeris: Moshier (no ephemeris files), for both programs (they call the same Swiss Ephemeris, so this checks how each uses it, not two ephemerides).

**Gate (SPEC Layer 1: within 1″, varga signs boundary-aware, mahadasha starts within a day): passes.**

1000 births drawn with seed 0: uniform in time over 1900-2050, longitude over the globe, latitude 60° S to 60° N. The engine at Lahiri, the mean node, apparent positions (Moshier unless JYOTISH_EPHE_PATH names ephemeris files) and a 365.25-day dasha year.

PyJHora set to the same conventions before anything was computed. Its own defaults, any of which would show here as a disagreement: ayanamsa TRUE_PUSHYA, true nodes True, true (geometric) positions True, nutation True, light deflection True, dasha year 365.256364 days. Varga methods: PyJHora's chart_method 1 (Parashari), 2 for the hora.

## Errors per quantity

Longitudes in arc-seconds; mahadasha starts in days.

| quantity | max | mean |
| --- | --- | --- |
| longitude Sun | 0.000000 | 0.000000 |
| longitude Moon | 0.000000 | 0.000000 |
| longitude Mars | 0.000000 | 0.000000 |
| longitude Mercury | 0.000000 | 0.000000 |
| longitude Jupiter | 0.000000 | 0.000000 |
| longitude Venus | 0.000000 | 0.000000 |
| longitude Saturn | 0.000000 | 0.000000 |
| longitude Rahu | 0.000134 | 0.000018 |
| longitude Ketu | 0.000134 | 0.000018 |
| longitude Asc | 0.000000 | 0.000000 |
| mahadasha start (days) | 0.000000 | 0.000000 |

## Causes of the residuals

- Rahu and Ketu (up to 0.000134″): the engine asks Swiss Ephemeris for the mean node with the Moshier flag, PyJHora with the file flag, which falls back to Moshier without files; the two paths differ by up to 0.00013″ (seen directly at JD 2415021.0, 1900).
- Every other residual is zero to six decimals: the same library, flags and ayanamsa on both sides.

## Disagreements beyond the gate (0)

None.

## Listed, not failed: within 1″ of an edge (0)

A body this close to a varga or pada edge may legitimately fall either side (SPEC Layer 1).

None.

