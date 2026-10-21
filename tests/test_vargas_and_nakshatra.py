"""Unit tests on the division rules themselves, independent of any chart."""

import pytest

from jyotish import vargas
from jyotish.nakshatra import kp_sub_lords, nakshatra_of, navatara
from jyotish.dignity import baladi_avastha, house_of


def test_navamsa_starts():
    # Aries (movable) starts from itself; Taurus (fixed) from Capricorn; Gemini (dual) from Libra.
    assert vargas.d9(0.1) == 0
    assert vargas.d9(30.1) == 9
    assert vargas.d9(60.1) == 6
    # Last navamsa of Pisces is Cancer (dual Pisces starts from Cancer: 5th from itself).
    assert vargas.d9(359.9) == (3 + 8) % 12


def test_hora():
    assert vargas.d2(5.0) == 4    # Aries first half: Sun's hora (Leo)
    assert vargas.d2(25.0) == 3   # Aries second half: Moon's
    assert vargas.d2(35.0) == 3   # Taurus first half: Moon's
    assert vargas.d2(55.0) == 4


def test_trimsamsa_unequal():
    assert vargas.d30(2.0) == 0      # Aries 0-5 Mars -> Aries
    assert vargas.d30(7.0) == 10     # Aries 5-10 Saturn -> Aquarius
    assert vargas.d30(15.0) == 8     # Aries 10-18 Jupiter -> Sagittarius
    assert vargas.d30(32.0) == 1     # Taurus 0-5 Venus -> Taurus
    assert vargas.d30(58.0) == 7     # Taurus 25-30 Mars -> Scorpio


def test_d60_counts_from_sign():
    assert vargas.d60(0.0) == 0
    assert vargas.d60(0.6) == 1
    assert vargas.d60(29.9) == (0 + 59) % 12


def test_every_varga_returns_a_sign():
    for lon in (0.0, 13.37, 123.456, 299.999, 359.99):
        for name, fn in vargas.VARGAS.items():
            assert 0 <= fn(lon) <= 11, name


def test_nakshatra_boundaries():
    assert nakshatra_of(0.0).name == "Ashwini"
    assert nakshatra_of(13.3333).name == "Ashwini"
    assert nakshatra_of(13.3334).name == "Bharani"
    assert nakshatra_of(359.9).name == "Revati"
    # 40° = 26°40' + 13°20' is exactly the start of Rohini, pada 1 (a float-boundary case).
    assert nakshatra_of(40.0).name == "Rohini"
    assert nakshatra_of(40.0).pada == 1
    assert nakshatra_of(39.999).name == "Krittika"


def test_kp_sub_lord_sequence_starts_with_star_lord():
    # First sub of Ashwini (Ketu) is Ketu, spanning 7/120 of 13°20' = 46'40".
    assert kp_sub_lords(0.1)[0] == "Ketu"
    assert kp_sub_lords(0.8)[0] == "Venus"


def test_navatara_cycles():
    t = navatara(13, 13)
    assert (t.name, t.cycle, t.count) == ("Janma", 1, 1)
    t = navatara((13 + 9) % 27, 13)
    assert (t.name, t.cycle) == ("Janma", 2)
    assert navatara((13 + 2) % 27, 13).name == "Vipat"
    assert navatara((13 + 26) % 27, 13).count == 27


def test_baladi_reversal():
    assert baladi_avastha(2.0) == "Bala"        # Aries, odd
    assert baladi_avastha(32.0) == "Mrita"      # Taurus, even
    assert baladi_avastha(58.0) == "Bala"


def test_house_of():
    assert house_of(1, 1) == 1
    assert house_of(0, 1) == 12
    assert house_of(7, 1) == 7
