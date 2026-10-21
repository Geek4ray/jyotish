"""Argala and Virodhargala on the reference chart (Taurus lagna, AL Capricorn)."""

import pytest

from jyotish.argala import argala, argala_on, sign_strength
from jyotish.chart import analyse
from jyotish.models import Meta
from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS


@pytest.fixture(scope="module")
def ref():
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC).features.argala


def places(a):
    return {x.house: x for x in a.places}


def test_h10(ref):
    # From Aquarius: Venus in Pisces (2nd), Jupiter and Saturn in Taurus (4th), Ketu in
    # Sagittarius (11th); Mars in Scorpio (10th) obstructs the 4th but is outnumbered.
    p = places(ref["H10"])
    primary = {h: x.by for h, x in p.items() if x.kind == "primary"}
    assert primary == {2: ["Venus"], 4: ["Jupiter", "Saturn"], 11: ["Ketu"]}
    assert p[4].blocked_by == ["Mars"] and p[4].outcome == "prevails"
    assert p[2].outcome == p[11].outcome == "unobstructed"
    # Secondary: Rahu in Gemini (5th) against the Moon in Libra (9th): one planet each,
    # no dignity, Gemini dual beats Libra movable.
    assert p[5].by == ["Rahu"] and p[5].blocked_by == ["Moon"] and p[5].outcome == "prevails"
    assert not ref["H10"].reversed


def test_ketu_sign_counts_backwards(ref):
    # H8 is Sagittarius, Ketu's sign: counted backwards its 2nd is Scorpio (Mars) and its
    # 11th is Aquarius (Sun, Mercury), as Rath's rule gives.
    a = ref["H8"]
    assert a.reversed
    assert places(a)[2].by == ["Mars"] and places(a)[11].by == ["Sun", "Mercury"]
    assert sum(x.reversed for x in ref.values()) == 1


def test_bandhana_on_equal_strength(ref):
    # H5 is Virgo: Ketu (4th) against Rahu (10th); one planet each, no dignity, both dual,
    # neither aspected by Jupiter from Taurus.
    x = places(ref["H5"])[4]
    assert x.by == ["Ketu"] and x.blocked_by == ["Rahu"] and x.outcome == "bandhana"


def test_arudha_lagna(ref):
    # AL in Capricorn: the 2nd (Aquarius) holds the Atmakaraka Sun with Mercury against Ketu.
    x = places(ref["AL"])[2]
    assert x.by == ["Sun", "Mercury"] and x.blocked_by == ["Ketu"] and x.outcome == "prevails"


def test_node_settings():
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, meta=Meta(argala_nodes="reverse_position"))
    p = places(c.features.argala["H10"])
    assert 11 not in p                        # Ketu counted backwards is 3rd from Aquarius
    assert c.features.argala["H10"].third_malefics == ["Ketu"]
    d = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, meta=Meta(argala_nodes="direct"))
    assert not any(a.reversed for a in d.features.argala.values())
    with pytest.raises(ValueError):
        argala(REFERENCE_POSITIONS, 1, 9, nodes="sideways")


def test_strength_order():
    # The Atmakaraka's sign outranks more planets; then count; then dignity; then dual >
    # fixed > movable; then Jupiter's sign aspect.
    assert sign_strength(0, ["Sun"], "Sun", 1) > sign_strength(1, ["Moon", "Mars"], "Sun", 1)
    assert sign_strength(0, ["Moon", "Mars"], None, 1) > sign_strength(1, ["Venus"], None, 1)
    assert sign_strength(0, ["Sun"], None, 3) > sign_strength(2, ["Moon"], None, 3)   # Sun exalted in Aries
    assert sign_strength(2, ["Rahu"], None, 0) > sign_strength(0, ["Ketu"], None, 3)


def test_vipareeta_with_three_malefics_in_the_third():
    signs = {"Sun": 2, "Mars": 2, "Saturn": 2, "Moon": 5, "Mercury": 7, "Jupiter": 9,
             "Venus": 11, "Rahu": 4, "Ketu": 10}
    a = argala_on(0, signs, nodes="rath", ak=None, malefics={"Sun", "Mars", "Saturn", "Rahu", "Ketu"})
    assert a["vipareeta"] and sorted(a["third_malefics"]) == ["Mars", "Saturn", "Sun"]
