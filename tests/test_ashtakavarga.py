"""Ashtakavarga on the reference chart, plus the reduction rules case by case.

The reference values pinned below are engine output. The cells marked "by hand" were
worked from the BPHS tables independently of the code; the rest is a regression lock and
has not yet been diffed against Jagannatha Hora."""

import random

import pytest

from jyotish.ashtakavarga import (
    ashtakavarga, bhinnashtakavarga, ekadhipatya_shodhana, kakshya_index, kakshya_lord,
    sodhya_pinda, trikona_shodhana,
)
from jyotish.chart import analyse
from jyotish.cli import print_ashtakavarga
from jyotish.constants import GRAHAS, SIGNS
from jyotish.models import Meta
from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS

S = {name: i for i, name in enumerate(SIGNS)}
CLASSICAL = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52,
             "Saturn": 39}


@pytest.fixture(scope="module")
def chart():
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS)


@pytest.fixture(scope="module")
def av(chart):
    return chart.features.ashtakavarga


# --- reference chart ----------------------------------------------------------------

def test_sav_totals_337(av):
    assert sum(av.SAV) == 337


def test_bav_rows_total_their_classical_counts(av):
    for planet, total in CLASSICAL.items():
        assert sum(av.BAV[planet]) == total, planet
    assert sum(av.BAV["Asc"]) == 49


def test_bav_cells_by_hand(av):
    # Sun's table in Aries: Mercury (Aries is 3rd from Aquarius) and the lagna (12th from
    # Taurus) give bindus; no one else does.
    assert av.BAV["Sun"][S["Aries"]] == 2
    # Moon's table in Cancer: Sun 6th, Moon 10th, Mars 9th, Venus 5th, Saturn 3rd, lagna 3rd.
    assert av.BAV["Moon"][S["Cancer"]] == 6
    # Saturn's table in Gemini is empty: no contributor has Gemini in a benefic place.
    assert av.BAV["Saturn"][S["Gemini"]] == 0


def test_reference_sav(av):
    assert av.SAV == [22, 24, 23, 30, 33, 26, 28, 27, 37, 24, 29, 34]


def test_sun_reductions_and_pinda_by_hand(av):
    # Trikona: (Ar, Le, Sg) 2,6,5 -> 0,4,3; (Ta, Vi, Cp) 3,4,3 -> 0,1,0;
    # (Ge, Li, Aq) 3,4,5 -> 0,1,2; (Cn, Sc, Pi) 4,4,5 -> 0,0,1.
    assert av.trikona["Sun"] == [0, 0, 0, 0, 4, 1, 1, 0, 3, 0, 2, 1]
    # Ekadhipatya, occupied = Ta Li Sc Aq Pi. Ge/Vi both vacant, 0 < 1: both to 0.
    # Sg vacant 3, Pi occupied 1: Sg down to 1. Ta/Li both occupied: kept.
    assert av.ekadhipatya["Sun"] == [0, 0, 0, 0, 4, 0, 1, 0, 1, 0, 2, 1]
    # Rasi: Le 4x10 + Li 7 + Sg 9 + Aq 2x11 + Pi 12 = 90.
    # Graha: Sun and Mercury in Aq 2x5 each, Moon in Li 1x5, Venus in Pi 1x7 = 32.
    p = av.pinda["Sun"]
    assert (p.rasi, p.graha, p.sodhya) == (90, 32, 122)


def test_reference_pindas(av):
    assert {p: x.sodhya for p, x in av.pinda.items()} == {
        "Sun": 122, "Moon": 85, "Mars": 130, "Mercury": 122, "Jupiter": 198, "Venus": 121,
        "Saturn": 233}


def test_kakshya_lords(av):
    assert av.kakshya == {"Sun": "Asc", "Moon": "Saturn", "Mars": "Venus", "Mercury": "Saturn",
                          "Jupiter": "Mars", "Venus": "Moon", "Saturn": "Saturn", "Asc": "Jupiter"}
    assert av.kakshya_bindu["Sun"]          # Aquarius is 10th from the Taurus lagna
    assert not av.kakshya_bindu["Saturn"]   # Saturn gives no bindu in its own 1st


def test_ekadhipatya_settings_reach_the_chart():
    zero = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, meta=Meta(ekadhipatya_zero_exempt=True))
    nodes = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, meta=Meta(ekadhipatya_nodes=True))
    # Mercury's own table after Trikona has Gemini 2, Virgo 0, both vacant. BPHS reduces
    # both to 0; the zero exemption keeps Gemini 2; Rahu in Gemini makes it occupied.
    assert zero.features.ashtakavarga.ekadhipatya["Mercury"][S["Gemini"]] == 2
    assert nodes.features.ashtakavarga.ekadhipatya["Mercury"][S["Gemini"]] == 2


def test_cli_prints_ashtakavarga(chart, capsys):
    print_ashtakavarga(chart)
    out = capsys.readouterr().out
    assert "  SAV        22  24  23  30  33  26  28  27  37  24  29  34   337" in out
    assert "Saturn': '150+83=233'" in out


# --- invariants on any chart --------------------------------------------------------

def test_totals_hold_for_any_chart():
    rng = random.Random(7)
    for _ in range(200):
        pos = {g: rng.uniform(0, 360) for g in GRAHAS}
        r = ashtakavarga(pos, rng.uniform(0, 360))
        assert sum(r.sav) == 337
        assert {p: sum(r.bav[p]) for p in CLASSICAL} == CLASSICAL
        assert all(0 <= v <= 8 for p in CLASSICAL for v in r.bav[p])
        assert all(0 <= r.ekadhipatya[p][s] <= r.trikona[p][s] <= r.bav[p][s]
                   for p in CLASSICAL for s in range(12))


def test_bhinnashtakavarga_all_in_one_sign():
    # Everyone in Aries: each bindu lands on the house number itself.
    signs = {c: 0 for c in CLASSICAL} | {"Asc": 0}
    sun = bhinnashtakavarga("Sun", signs)
    assert sun[0] == 3   # 1st: Sun, Mars, Saturn
    assert sun[10] == 7  # 11th: every contributor but Venus (6, 7, 12 only)


# --- Trikona -------------------------------------------------------------------------

def test_trikona_subtracts_the_least():
    bav = [5, 0, 0, 0, 3, 0, 0, 0, 4, 0, 0, 0]
    assert trikona_shodhana(bav)[0:9:4] == [2, 0, 1]


def test_trikona_zero_in_trine_leaves_it():
    bav = [5, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0]
    assert trikona_shodhana(bav) == bav


def test_trikona_all_equal_clears():
    bav = [3, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0]
    assert trikona_shodhana(bav) == [0] * 12


# --- Ekadhipatya (Aries/Scorpio pair; Cancer and Leo never touched) -------------------

def _pair(ar, sc, occupied, **kw):
    bav = [0] * 12
    bav[0], bav[7], bav[3], bav[4] = ar, sc, 5, 6
    out = ekadhipatya_shodhana(bav, occupied, **kw)
    assert (out[3], out[4]) == (5, 6)
    return out[0], out[7]


def test_ekadhipatya_both_occupied_untouched():
    assert _pair(3, 5, {0, 7}) == (3, 5)


def test_ekadhipatya_occupied_more_clears_vacant():
    assert _pair(5, 3, {0}) == (5, 0)


def test_ekadhipatya_occupied_fewer_lowers_vacant():
    assert _pair(2, 5, {0}) == (2, 2)


def test_ekadhipatya_occupied_equal_clears_vacant():
    assert _pair(4, 4, {7}) == (0, 4)


def test_ekadhipatya_both_vacant_equal_clears_both():
    assert _pair(3, 3, set()) == (0, 0)


def test_ekadhipatya_both_vacant_unequal_to_smaller():
    assert _pair(2, 5, set()) == (2, 2)


def test_ekadhipatya_zero_setting():
    # Occupied Aries with 0 against vacant Scorpio with 4: BPHS clears Scorpio;
    # the zero exemption leaves the pair alone.
    assert _pair(0, 4, {0}) == (0, 0)
    assert _pair(0, 4, {0}, zero_exempt=True) == (0, 4)
    assert _pair(0, 4, set()) == (0, 0)
    assert _pair(0, 4, set(), zero_exempt=True) == (0, 4)


# --- Pinda and Kakshya ---------------------------------------------------------------

def test_sodhya_pinda_multipliers():
    reduced = [1] * 12
    signs = {"Sun": 0, "Moon": 0, "Mars": 0, "Mercury": 0, "Jupiter": 0, "Venus": 0, "Saturn": 0}
    p = sodhya_pinda(reduced, signs)
    assert p.rasi == 7 + 10 + 8 + 4 + 10 + 5 + 7 + 8 + 9 + 5 + 11 + 12
    assert p.graha == 5 + 5 + 8 + 5 + 10 + 7 + 5
    assert p.sodhya == p.rasi + p.graha


@pytest.mark.parametrize("lon,idx", [
    (0.0, 0), (3.75, 1), (3.75 - 1e-9, 0), (7.5, 2), (26.25, 7), (29.999999, 7),
    (30.0, 0), (33.75, 1), (93.75, 1), (183.75, 1), (356.25, 7), (360.0, 0),
])
def test_kakshya_boundaries(lon, idx):
    assert kakshya_index(lon) == idx


def test_kakshya_order():
    assert [kakshya_lord(30 * 5 + 3.75 * k + 0.1) for k in range(8)] == [
        "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Asc"]
