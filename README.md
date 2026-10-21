# jyotish

A Vedic-astrology engine that computes every classical quantity exactly and reports each
finding with its stability under birth-time uncertainty. The full design is in
[SPEC.md](SPEC.md); working rules for contributors (human or Claude Code) are in
[CLAUDE.md](CLAUDE.md).

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

The venv matters: on Debian/Ubuntu the system setuptools cannot build `pyswisseph`
(`AttributeError: install_layout`). Positions come from the built-in Moshier model; set
`JYOTISH_EPHE_PATH` to a Swiss Ephemeris data directory for full precision.

## Use

```sh
# The SPEC.md reference chart from its printed longitudes (no ephemeris needed)
.venv/bin/jyotish reference

# A chart from birth data (UTC, latitude, longitude)
.venv/bin/jyotish compute --utc 2001-03-12T04:40:00 --lat 28.61 --lon 77.21 --json

# Recover the UTC instant behind a printed position table
.venv/bin/jyotish recover --sun 327.7986 --moon 181.4219 --jupiter 40.6456 --saturn 32.1058 --rahu 78.0989
```

From Python:

```python
from jyotish import analyse, compute
chart = analyse(positions, ascendant)        # sidereal longitudes in degrees
chart = compute(utc_datetime, lat, lon)      # birth data
chart.model_dump()                           # the data schema from SPEC.md
```

## What is implemented

Layer 1: Swiss Ephemeris wrapper (Lahiri/Raman/KP/true-Chitrapaksha ayanamsas, true or mean
node, Placidus cusps, sunrise), all 16 Parashari vargas plus D11, nakshatras with padas,
Vimshottari lords, KP sub and sub-sub lords, panchanga.
Layer 1b-A: the birth-time uncertainty sampler with per-varga stability.
Layer 2 (partial): lordship and functional roles, five-fold dignity (natural and compound),
Baladi avasthas, combustion, boundary flags, Gandanta, Pushkara, Marana Karaka Sthana,
whole-sign aspects, three dispositor chains with loops and Parivartana classes, chara karakas
under both schemes, arudha padas with the Jaimini exception, Navatara with special taras,
Sudarshana 10th house.
Layer 4 (partial): Vimshottari to any depth with the year-length setting.

`tests/test_reference_chart.py` encodes the SPEC worked example; all of it passes.

## Licensing

Swiss Ephemeris (via `pyswisseph`) is AGPL-3.0 or a paid Astrodienst licence. See the
Tech stack section of SPEC.md before any commercial deployment.
