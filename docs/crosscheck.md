# Phase 0 cross-check: the engine against PyJHora

Run 2026-10-23 at commit `0650dd2` by `scripts/crosscheck.py --n 1000 --seed 0` in 7 s. PyJHora 4.8.7; ephemeris: Moshier (no ephemeris files), for both programs (they call the same Swiss Ephemeris, so this checks how each uses it, not two ephemerides).

**Gate (SPEC Layer 1: within 1″, varga signs boundary-aware, mahadasha starts within a day): passes.**

1000 births drawn with seed 0: uniform in time over 1900-2050, longitude over the globe, latitude 60° S to 60° N. The engine at Lahiri, the mean node, apparent positions (Moshier unless JYOTISH_EPHE_PATH names ephemeris files) and a 365.25-day dasha year.

PyJHora set to the same conventions before anything was computed. Its own defaults, any of which would show here as a disagreement: ayanamsa TRUE_PUSHYA, true nodes True, true (geometric) positions True, nutation True, light deflection True, dasha year 365.256364 days.

Varga methods, chosen by PyJHora's own labels (the lowest-numbered method its docstring calls "Traditional Parasara"), never by agreement with the engine: D2 method 2 (Traditional Parasara (Only Le & Cn)); D3 method 1 (Traditional Parasara with parivritti and even sign reversal (Uma Shambu)); D4 method 1 (Traditional Parasara); D7 method 1 (Traditional Parasara (even start from 7th and go forward)); D9 method 1 (Traditional Parasara); D10 method 1 (Traditional Parasara (start from 9th and go forward)); D12 method 1 (Traditional Parasara); D16 method 1 (Traditional Parasara); D20 method 1 (Traditional Parasara); D24 method 1 (Traditional Parasara Siddhamsa (Odd Le->Cn, Even Cn->Ge) -  Default); D27 method 1 (Traditional Parasara); D30 method 1 (Traditional Parasara); D40 method 1 (Traditional Parasara); D45 method 1 (Traditional Parasara); D60 method 1 (Traditional Parasara shashtyamsa (from sign)).

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

