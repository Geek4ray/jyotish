"""Shadbala on the reference chart, plus each component's rules on constructed inputs.

Values marked "by hand" were worked from the rules independently of the code. The
regression lock on the ratios is engine output and has not been diffed against
Jagannatha Hora or Raman's worked examples."""

import random
import re

import pytest

from jyotish.chart import analyse
from jyotish.cli import print_shadbala
from jyotish.constants import GRAHAS, SEVEN
from jyotish.models import Meta
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)
from jyotish.shadbala import (
    ShadbalaSettings, dig_bala, dig_points, drekkana_index, drishti, shadbala,
)


@pytest.fixture(scope="module")
def inputs():
    return reference_time_inputs()


def _chart(inputs, positions=REFERENCE_POSITIONS, **meta):
    kw = dict(inputs)
    kw["meta"] = kw["meta"].model_copy(update=meta)
    return analyse(positions, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **kw)


@pytest.fixture(scope="module")
def sb(inputs):
    return _chart(inputs).features.shadbala


# Classical maxima per component (virupas). Moon's Paksha and the Sun's Ayana are doubled
# by default, and the luminaries' Chesta is that same doubled value.
MAX = {"uchcha": 60, "saptavargaja": 7 * 45, "ojhayugma": 30, "kendra": 60, "drekkana": 15,
       "dig": 60, "nathonnata": 60, "paksha": 60, "tribhaga": 60, "abda": 15, "masa": 30,
       "vara": 45, "hora": 60, "ayana": 60, "chesta": 60, "naisargika": 60}
DOUBLED = {("Moon", "paksha"): 120, ("Sun", "ayana"): 120, ("Moon", "chesta"): 120,
           ("Sun", "chesta"): 120}


def _components(x):
    out = {k: v for k, v in x.sthana.model_dump().items() if k != "total"}
    out |= {k: v for k, v in x.kala.model_dump().items() if k not in ("total", "yuddha")}
    out |= {"dig": x.dig, "chesta": x.chesta, "naisargika": x.naisargika}
    return out


def _assert_within_maxima(planets):
    for p, x in planets.items():
        for name, v in _components(x).items():
            hi = DOUBLED.get((p, name), MAX[name])
            assert -1e-9 <= v <= hi + 1e-9, (p, name, v)
        assert abs(x.drik) <= 90.0, (p, x.drik)   # six aspects of at most 60, over 4


# --- reference chart ------------------------------------------------------------------

def test_absent_without_the_birth_moment():
    chart = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS)
    assert chart.features.shadbala is None


def test_every_component_within_its_classical_maximum(sb):
    assert set(sb.planets) == set(SEVEN)
    _assert_within_maxima(sb.planets)
    assert sb.wars == [] and all(x.kala.yuddha == 0 for x in sb.planets.values())


def test_naisargika_exact(sb):
    truncated = {"Sun": 60, "Moon": 51.43, "Venus": 42.85, "Jupiter": 34.28, "Mercury": 25.71,
                 "Mars": 17.14, "Saturn": 8.57}
    for p, k in {"Sun": 7, "Moon": 6, "Venus": 5, "Jupiter": 4, "Mercury": 3, "Mars": 2,
                 "Saturn": 1}.items():
        assert sb.planets[p].naisargika == 60 * k / 7
        assert sb.planets[p].naisargika == pytest.approx(truncated[p], abs=0.01)


def test_totals_required_and_ratio(sb):
    required = {"Sun": 390, "Moon": 360, "Mars": 300, "Mercury": 420, "Jupiter": 390,
                "Venus": 330, "Saturn": 300}
    for p, x in sb.planets.items():
        assert x.required == required[p]
        parts = x.sthana.total + x.dig + x.kala.total + x.chesta + x.naisargika + x.drik
        assert x.total == pytest.approx(parts)
        assert x.ratio == pytest.approx(x.total / x.required)


def test_reference_values_by_hand(sb):
    P = sb.planets
    # Kala lords: 2001-03-12 was a Monday; 10:10 IST is in the 4th hora from sunrise
    # (Moon, Saturn, Jupiter, Mars) and the first third of the day (Mercury).
    assert sb.lords["vara"] == "Moon" and sb.lords["hora"] == "Mars"
    assert sb.tribhaga_lord == "Mercury"
    assert P["Moon"].kala.vara == 45 and P["Mars"].kala.hora == 60
    assert P["Mercury"].kala.tribhaga == 60 and P["Jupiter"].kala.tribhaga == 60
    # Paksha: Moon 213.62° from the Sun, folded 146.38°, /3 = 48.79 to the benefics;
    # Mercury shares Aquarius with the Sun, so it takes the malefic 60 - 48.79.
    assert P["Jupiter"].kala.paksha == pytest.approx(48.79, abs=0.01)
    assert P["Mercury"].kala.paksha == pytest.approx(11.21, abs=0.01)
    assert P["Moon"].kala.paksha == pytest.approx(97.59, abs=0.02)
    # Ayana: Sun sayana 351.67°, kranti -3.38°, (24 - 3.38) / 48 * 60 = 25.78, doubled.
    assert P["Sun"].kala.ayana == pytest.approx(51.56, abs=0.05)
    assert P["Sun"].chesta == P["Sun"].kala.ayana and P["Moon"].chesta == P["Moon"].kala.paksha
    # Uchcha: Venus 176.66° from its debilitation point (27° Virgo).
    assert P["Venus"].sthana.uchcha == pytest.approx(58.89, abs=0.01)
    # Saptavargaja, Saturn at 2°06' Taurus: D1 Taurus great friend 20, D2 Cancer great
    # enemy 2, D3 Taurus 20, D7 Scorpio great enemy 2, D9 Capricorn own 30, D12 Taurus 20,
    # D30 Venus's Taurus 20.
    assert P["Saturn"].sthana.saptavargaja == 114
    assert {p: x.sthana.kendra for p, x in P.items()} == {
        "Sun": 60, "Moon": 15, "Mars": 60, "Mercury": 60, "Jupiter": 60, "Venus": 30, "Saturn": 60}
    assert {p: x.sthana.ojhayugma for p, x in P.items()} == {
        "Sun": 30, "Moon": 0, "Mars": 15, "Mercury": 30, "Jupiter": 15, "Venus": 15, "Saturn": 0}
    assert all(x.sthana.drekkana == 0 for x in P.values())   # nobody in its BPHS decanate
    # Saturn is 4° from the ascendant, its weakest point.
    assert P["Saturn"].dig == pytest.approx((REFERENCE_ASC - REFERENCE_POSITIONS["Saturn"]) / 3, abs=1e-9)


def test_reference_ratios_regression(sb):
    assert {p: round(x.ratio, 2) for p, x in sb.planets.items()} == {
        "Sun": 1.23, "Moon": 1.27, "Mars": 1.30, "Mercury": 1.19, "Jupiter": 1.22,
        "Venus": 1.33, "Saturn": 0.69}


def test_ratio_printed_for_all_seven(inputs, capsys):
    print_shadbala(_chart(inputs))
    out = capsys.readouterr().out
    for p in SEVEN:
        assert re.search(rf"^  {p}\s.*\s\d+\.\d\d$", out, re.M), p


# --- settings reach the chart ---------------------------------------------------------

def test_settings(inputs, sb):
    def get(**m):
        return _chart(inputs, **m).features.shadbala.planets
    assert get(drekkana_bala="phaladeepika")["Venus"].sthana.drekkana == 15   # 3rd decanate
    assert get(saptavargaja_scale="raman")["Saturn"].sthana.saptavargaja == pytest.approx(
        22.5 + 1.875 + 22.5 + 1.875 + 30 + 22.5 + 22.5)
    assert get(ayana_sun_double=False)["Sun"].kala.ayana == pytest.approx(sb.planets["Sun"].kala.ayana / 2)
    assert get(paksha_moon_double=False)["Moon"].kala.paksha == pytest.approx(sb.planets["Moon"].kala.paksha / 2)
    zero = get(chesta_luminaries="zero")
    assert zero["Sun"].chesta == 0 and zero["Moon"].chesta == 0
    assert get(mercury_nature="benefic")["Mercury"].kala.paksha == pytest.approx(48.79, abs=0.01)
    assert get(ayana_obliquity="true")["Sun"].kala.ayana != sb.planets["Sun"].kala.ayana
    mean = get(nathonnata_noon="mean")["Sun"].kala.nathonnata
    assert mean != sb.planets["Sun"].kala.nathonnata and 0 <= mean <= 60
    assert get(dig_bala_points="equal")["Sun"].dig != sb.planets["Sun"].dig


def test_equal_houses_need_no_mc(inputs):
    kw = dict(inputs, mc=None)
    assert analyse(REFERENCE_POSITIONS, REFERENCE_ASC, **kw).features.shadbala is None
    kw["meta"] = kw["meta"].model_copy(update={"dig_bala_points": "equal"})
    assert analyse(REFERENCE_POSITIONS, REFERENCE_ASC, **kw).features.shadbala is not None


# --- Dig bala -------------------------------------------------------------------------

def test_dig_bala_zero_at_weakest_and_full_at_strongest():
    pts = dig_points(asc=10.0, mc=280.0, convention="cusps")
    weakest = {"Sun": pts["ic"], "Mars": pts["ic"], "Jupiter": pts["desc"], "Mercury": pts["desc"],
               "Saturn": pts["asc"], "Moon": pts["mc"], "Venus": pts["mc"]}
    for p, lon in weakest.items():
        assert dig_bala(p, lon, pts) == 0.0, p
        assert dig_bala(p, lon + 180.0, pts) == 60.0, p


def test_dig_bala_zero_on_the_chart(inputs):
    pos = dict(REFERENCE_POSITIONS, Saturn=REFERENCE_ASC)   # Saturn on the ascendant
    assert _chart(inputs, positions=pos).features.shadbala.planets["Saturn"].dig == 0.0


# --- boundaries and drishti -----------------------------------------------------------

@pytest.mark.parametrize("lon,idx", [(0.0, 0), (9.999999, 0), (10.0, 1), (20.0, 2),
                                     (29.999999, 2), (30.0, 0), (40.0, 1), (350.0, 2)])
def test_drekkana_boundaries(lon, idx):
    assert drekkana_index(lon) == idx


def test_drishti_curve():
    for p in SEVEN:
        assert drishti(p, 180.0) == 60.0          # 7th: full for all
        assert drishti(p, 15.0) == 0.0 and drishti(p, 310.0) == 0.0
    assert drishti("Sun", 90.0) == 45.0 and drishti("Sun", 120.0) == 30.0
    assert drishti("Mars", 90.0) == 60.0 and drishti("Mars", 210.0) == 60.0
    assert drishti("Jupiter", 120.0) == 60.0 and drishti("Jupiter", 240.0) == 60.0
    assert drishti("Saturn", 60.0) == 60.0 and drishti("Saturn", 270.0) == 60.0


# --- Yuddha and invariants on random charts -------------------------------------------

def _random_inputs(rng):
    jd = 2451545.0 + rng.uniform(-30000, 30000)
    rise = jd - rng.uniform(0.0, 0.99)
    sset = rise + rng.uniform(0.35, 0.65)
    return dict(mc=rng.uniform(0, 360), jd=jd, sunrise=rise, sunset=sset,
                next_sunrise=rise + 1.0, ayanamsa=23.9, geo_lon=rng.uniform(-180, 180))


def test_yuddha_winner_gains_what_loser_loses():
    rng = random.Random(3)
    pos = {g: rng.uniform(0, 360) for g in GRAHAS}
    pos["Venus"] = (pos["Mars"] + 0.4) % 360.0
    r = shadbala(pos, rng.uniform(0, 360), **_random_inputs(rng))
    assert len(r.wars) >= 1
    war = next(w for w in r.wars if set(w.planets) == {"Mars", "Venus"})
    loser = ({"Mars", "Venus"} - {war.winner}).pop()
    assert war.bala > 0
    assert r.planets[war.winner].kala["yuddha"] == pytest.approx(war.bala)
    assert r.planets[loser].kala["yuddha"] == pytest.approx(-war.bala)


def test_maxima_hold_on_random_charts():
    rng = random.Random(11)
    for _ in range(300):
        pos = {g: rng.uniform(0, 360) for g in GRAHAS}
        settings = ShadbalaSettings(ayana_obliquity=rng.choice(["bphs", "true"]),
                                    nathonnata_noon=rng.choice(["apparent", "mean"]))
        r = shadbala(pos, rng.uniform(0, 360), settings=settings, **_random_inputs(rng))
        if r.wars:
            continue
        for p, x in r.planets.items():
            comps = {k: v for k, v in x.sthana.items() if k != "total"}
            comps |= {k: v for k, v in x.kala.items() if k not in ("total", "yuddha")}
            comps |= {"dig": x.dig, "chesta": x.chesta, "naisargika": x.naisargika}
            for name, v in comps.items():
                assert -1e-9 <= v <= DOUBLED.get((p, name), MAX[name]) + 1e-9, (p, name, v)
            assert abs(x.drik) <= 90.0
