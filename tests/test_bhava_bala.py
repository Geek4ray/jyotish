"""Bhava Bala (BPHS 27.26-31, Santhanam 1984) on the reference chart."""

import pytest

from jyotish.bhava_bala import birth_time_class, dig_point, time_bonus
from jyotish.chart import analyse
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)


@pytest.fixture(scope="module")
def inputs():
    return reference_time_inputs()


def chart(inputs, **meta):
    kw = dict(inputs)
    kw["meta"] = kw["meta"].model_copy(update=meta)
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **kw)


@pytest.fixture(scope="module")
def bb(inputs):
    return chart(inputs).features.bhava_bala


def test_present_for_both_systems(bb):
    assert bb.birth_time == "day"
    assert sorted(bb.whole_sign) == sorted(bb.sripati) == list(range(1, 13))
    assert bb.whole_sign[1].madhya == pytest.approx(REFERENCE_ASC)
    assert bb.sripati[1].madhya == pytest.approx(REFERENCE_ASC)


def test_components_within_their_bounds_and_sum(bb):
    # No total range is stated in 27.26-31; the bounds follow from the components:
    # Dig 0-60; Drishti between -5 x 15 (five malefic quarters) and 60 + 60 + 15 + 15;
    # occupants whole rupas; the time bonus 0 or 15; the lord's Shadbala as computed.
    for table in (bb.whole_sign, bb.sripati):
        for h, x in table.items():
            assert 0.0 <= x.dig <= 60.0
            assert -75.0 <= x.drishti <= 150.0
            assert x.occupants % 60 == 0 and x.time in (0.0, 15.0)
            assert x.total == pytest.approx(x.bhavadhipati + x.dig + x.drishti + x.occupants + x.time)
            assert 0.0 < x.rupas < 15.0
            assert x.rupas == pytest.approx(x.total / 60)


def test_dig_by_hand(bb):
    assert bb.whole_sign[10].dig == pytest.approx(30.0)   # Aquarius: 90° from the descendant
    assert bb.whole_sign[7].dig == pytest.approx(60.0)    # Scorpio: 180° from the lagna
    assert bb.sripati[10].dig == pytest.approx(0.0)       # 2nd half of Capricorn at the MC itself
    assert dig_point(5 * 30 + 1) == "desc" and dig_point(8 * 30 + 20) == "ic"
    assert dig_point(9 * 30 + 10) == "ic" and dig_point(9 * 30 + 20) == "mc"


def test_drishti_by_hand(bb):
    # On H7 (Scorpio 6°10'): Jupiter in full 51.0; Venus +38.75/4; Saturn -57.97/4;
    # Sun -25.82/4; Mercury (with the Sun, malefic) -12.1/4; the waning Moon -2.37/4.
    assert bb.whole_sign[7].drishti == pytest.approx(36.14, abs=0.1)


def test_occupants_and_lords(bb):
    w = bb.whole_sign
    assert w[1].occupants == 0          # Jupiter +60, Saturn -60
    assert w[10].occupants == 0         # Mercury +60, Sun -60
    assert w[7].occupants == -60        # Mars
    assert w[10].lord == "Saturn" and w[10].bhavadhipati == pytest.approx(207.26, abs=0.05)
    assert bb.sripati[10].occupants == 60 and bb.sripati[11].occupants == -60   # Mercury H10, Sun H11


def test_time_bonus_and_rising_setting(inputs, bb):
    assert bb.whole_sign[2].time == 15.0     # Gemini, head-rising, day birth
    assert bb.whole_sign[1].time == 0.0      # Taurus, back-rising
    assert bb.whole_sign[8].time == 15.0     # Sagittarius head-rising in BPHS ch. 4
    pd = chart(inputs, rising_signs="phaladeepika").features.bhava_bala
    assert pd.whole_sign[8].time == 0.0      # back-rising in Phaladeepika 1.8
    assert time_bonus(11, "night", "bphs") == 15.0 and time_bonus(11, "day", "bphs") == 15.0
    assert time_bonus(2, "twilight", "bphs") == 15.0 and time_bonus(4, "twilight", "bphs") == 0.0


def test_birth_time_class():
    assert birth_time_class(10.0, 9.9, 10.4, 10.9, 24) == "day"
    assert birth_time_class(10.405, 9.9, 10.4, 10.9, 24) == "twilight"
    assert birth_time_class(10.6, 9.9, 10.4, 10.9, 24) == "night"


def test_absent_without_shadbala():
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC)
    assert c.features.bhava_bala is None
