"""The ephemeris path against the reference app: birth data -> positions.
Tolerances: planets 2 arc-seconds (Moshier vs the app's ephemeris), ascendant 1 arc-minute
(the app's stored coordinates for Rewari are not known to the minute)."""

import pytest

from jyotish.chart import compute
from jyotish.ephemeris import recover_instant
from jyotish.reference import (
    REFERENCE_APP_UTC, REFERENCE_ASC, REFERENCE_BIRTH_UTC, REFERENCE_D9, REFERENCE_LAT,
    REFERENCE_LON, REFERENCE_POSITIONS,
)
from jyotish.uncertainty import stability


def arcsec(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0


@pytest.fixture(scope="module")
def app_chart():
    """Computed at the second the app used (10:10:00 IST), mean node as the app does."""
    return compute(REFERENCE_APP_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def true_chart():
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_planets_match_the_app(app_chart):
    for name, lon in REFERENCE_POSITIONS.items():
        assert arcsec(app_chart.bodies[name].lon, lon) < 2.0, name


def test_ascendant_matches_the_app(app_chart):
    assert arcsec(app_chart.lagnas.asc, REFERENCE_ASC) < 60.0
    assert app_chart.lagnas.asc_sign == 1


def test_navamsa_from_ephemeris(app_chart):
    for name, sign in REFERENCE_D9.items():
        assert app_chart.vargas["D9"][name] == sign, name


def test_ayanamsa_and_node(app_chart):
    assert app_chart.meta.ayanamsa_value == pytest.approx(23.87, abs=0.01)
    assert app_chart.meta.node == "mean"


def test_the_true_seconds_move_the_lagna_not_the_sign(true_chart, app_chart):
    # 25 seconds of clock: ~7' of ascendant, 15" of Moon, same lagna sign and navamsa.
    assert 300 < arcsec(true_chart.lagnas.asc, app_chart.lagnas.asc) < 600
    assert 10 < arcsec(true_chart.bodies["Moon"].lon, app_chart.bodies["Moon"].lon) < 20
    assert true_chart.lagnas.asc_sign == app_chart.lagnas.asc_sign
    assert true_chart.vargas["D9"]["Asc"] == app_chart.vargas["D9"]["Asc"]


def test_panchanga(true_chart):
    p = true_chart.panchanga
    assert p.vara_lord == "Moon"          # 12 March 2001 was a Monday
    assert p.nakshatra == "Chitra"
    assert p.paksha == "krishna" and p.tithi == 18
    assert p.day_birth is True


def test_dasha_balance_from_ephemeris(true_chart):
    maha = [p for p in true_chart.dashas["vimshottari"] if len(p.lords) == 1]
    assert maha[0].lords == ["Mars"]
    remaining_years = (maha[0].end_jd - true_chart.meta.jd) / 365.25
    assert remaining_years == pytest.approx(2.75, abs=0.02)
    assert [p.lords[0] for p in maha] == ["Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
                                         "Ketu", "Venus", "Sun", "Moon"]


def test_recover_instant_finds_the_birth():
    targets = {k: REFERENCE_POSITIONS[k] for k in ("Sun", "Moon", "Jupiter", "Saturn")}
    found = recover_instant(targets, 1995, 2005)
    assert len(found) == 1
    jd_app = 2451980.694444  # 2001-03-12 04:40:00 UTC, the second the app used
    assert abs(found[0] - jd_app) * 86400 < 30


def test_stability_reflects_the_lagna_degree(true_chart):
    s = stability(true_chart.meta.jd, REFERENCE_LAT, REFERENCE_LON, "exact", n=200)
    assert s.varga_lagna["D1"] == 1.0
    assert 0.6 < s.varga_lagna["D9"] < 0.95     # 23' from the D9 boundary
    assert s.varga_lagna["D60"] < 0.7           # D60 cells are 30' wide
    assert s.ayanamsa_lagna == {"lahiri": 1, "raman": 1, "kp": 1}
