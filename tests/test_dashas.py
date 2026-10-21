"""Yogini and Chara dashas on the reference chart (Moon in Chitra, Taurus lagna)."""

import pytest

from jyotish.chart import analyse
from jyotish.dasha import yogini
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)

MOON = REFERENCE_POSITIONS["Moon"]
# Chitra runs Virgo 23°20' to Libra 6°40'; the Moon has covered 8°05'19" of 13°20'.
ELAPSED = (6 * 30 + 1 + 25 / 60 + 19 / 3600 - (5 * 30 + 23 + 1 / 3)) / (40 / 3)


@pytest.fixture(scope="module")
def inputs():
    return reference_time_inputs()


@pytest.fixture(scope="module")
def chart(inputs):
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **inputs)


def mahas(periods):
    return [p for p in periods if len(p.lords) == 1]


# --- Yogini ---------------------------------------------------------------------------

def test_yogini_starts_with_mangala(chart):
    # Chitra is nakshatra 14: (14 + 3) mod 8 = 1, Mangala (Moon, 1 year).
    first = mahas(chart.dashas["yogini"])[0]
    assert first.names == ["Mangala"] and first.lords == ["Moon"]
    birth = chart.meta.jd
    assert (first.end_jd - birth) / 365.25 == pytest.approx(1 - ELAPSED, abs=1e-6)   # 0.393 y


def test_yogini_order_and_years(chart):
    m = mahas(chart.dashas["yogini"])
    assert [p.names[0] for p in m[:8]] == ["Mangala", "Pingala", "Dhanya", "Bhramari",
                                           "Bhadrika", "Ulka", "Siddha", "Sankata"]
    assert [round((p.end_jd - p.start_jd) / 365.25, 6) for p in m[:8]] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert len(m) == 24                                     # three 36-year rounds
    assert all(a.end_jd == pytest.approx(b.start_jd) for a, b in zip(m, m[1:]))


def test_yogini_antardashas(chart):
    periods = chart.dashas["yogini"]
    birth = chart.meta.jd
    # Mangala's antars run Mangala 1/36, Pingala 2/36 ... Siddha 7/36 spans 21/36-28/36
    # of the year, and the Moon's elapsed share 0.607 falls in it.
    at_birth = [p for p in periods if len(p.lords) == 2 and p.start_jd <= birth < p.end_jd]
    assert [p.names for p in at_birth] == [["Mangala", "Siddha"]]
    pingala = mahas(periods)[1]
    subs = [p for p in periods if len(p.lords) == 2
            and pingala.start_jd <= p.start_jd < pingala.end_jd]
    assert subs[0].names[1] == "Pingala" and len(subs) == 8
    assert sum(p.end_jd - p.start_jd for p in subs) == pytest.approx(pingala.end_jd - pingala.start_jd)


def test_yogini_follows_the_year_length(inputs):
    kw = dict(inputs)
    kw["meta"] = kw["meta"].model_copy(update={"dasha_year": 360.0})
    chart = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, **kw)
    first = mahas(chart.dashas["yogini"])[0]
    assert first.end_jd - chart.meta.jd == pytest.approx((1 - ELAPSED) * 360.0, abs=1e-6)
    assert mahas(chart.dashas["yogini"])[1].end_jd - mahas(chart.dashas["yogini"])[1].start_jd == pytest.approx(720.0)


@pytest.mark.parametrize("nak,first", [(0, "Bhramari"), (4, "Sankata"), (5, "Mangala"),
                                       (13, "Mangala"), (26, "Ulka")])
def test_yogini_start_by_nakshatra(nak, first):
    # Ashwini (1) + 3 = 4 Bhramari; Mrigashira (5) + 3 = 8 Sankata; Ardra (6) + 3 = 9 -> 1
    # Mangala; Chitra (14) + 3 = 17 -> 1 Mangala; Revati (27) + 3 = 30 -> 6 Ulka.
    lon = nak * 360 / 27 + 1.0
    assert yogini(lon, 2451545.0, levels=1)[0].names[0] == first


# --- Chara ----------------------------------------------------------------------------

from jyotish.constants import SIGNS  # noqa: E402
from jyotish.dasha import (  # noqa: E402
    CHARA_VARIANTS, _sequence, chara, chara_sequence, rashi_aspects,
)

S = {name: i for i, name in enumerate(SIGNS)}


def seq(variant, positions=REFERENCE_POSITIONS, lagna=1):
    return [(SIGNS[s], y) for s, y in chara_sequence(positions, lagna, variant)]


def test_chara_kn_rao_reference():
    # Taurus lagna, 9th Capricorn even-footed: reverse. Years count from the sign to its
    # lord, forward from odd-footed signs, backward from even-footed ones, minus one.
    assert seq("kn_rao") == [
        ("Taurus", 10), ("Aries", 7), ("Pisces", 10), ("Aquarius", 9), ("Capricorn", 8),
        ("Sagittarius", 5), ("Scorpio", 1), ("Libra", 5), ("Virgo", 7), ("Leo", 6),
        ("Cancer", 9), ("Gemini", 8)]
    # Taurus: Venus in Pisces, 11 signs forward -> 10. Scorpio: Mars is in it, so count to
    # Ketu in Sagittarius -> 1. Aquarius: Saturn (with Jupiter) beats Rahu (alone) -> 9.


def test_chara_raman_adds_for_exaltation():
    got = dict(seq("raman"))
    assert got["Taurus"] == 11 and got["Libra"] == 6      # Venus exalted in Pisces
    assert sum(got.values()) == 87


def test_chara_rath_reference():
    # Taurus (Jupiter, Saturn) beats Scorpio (Mars) on planets, so the dasa starts in
    # Taurus; Saturn there makes it regular and zodiacal (J.S. 2.4.33). Ketu exalted in
    # Sagittarius (Rath's table) gives Scorpio 1 + 1.
    assert seq("rath") == [
        ("Taurus", 11), ("Gemini", 8), ("Cancer", 9), ("Leo", 6), ("Virgo", 7), ("Libra", 6),
        ("Scorpio", 2), ("Sagittarius", 5), ("Capricorn", 8), ("Aquarius", 9), ("Pisces", 10),
        ("Aries", 7)]


# Narayana Dasa (Rath, Sagar), Table 10, p. 52: the general order from each starting sign
# (1 = Aries), direction by the 9th from that sign.
TABLE_10 = {
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 2: [2, 9, 4, 11, 6, 1, 8, 3, 10, 5, 12, 7],
    3: [3, 11, 7, 6, 2, 10, 9, 5, 1, 12, 8, 4], 4: [4, 3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5],
    5: [5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7, 12], 6: [6, 10, 2, 3, 7, 11, 12, 4, 8, 9, 1, 5],
    7: [7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6], 8: [8, 3, 10, 5, 12, 7, 2, 9, 4, 11, 6, 1],
    9: [9, 5, 1, 12, 8, 4, 3, 11, 7, 6, 2, 10], 10: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 12, 11],
    11: [11, 4, 9, 2, 7, 12, 5, 10, 3, 8, 1, 6], 12: [12, 4, 8, 9, 1, 5, 6, 10, 2, 3, 7, 11],
}


@pytest.mark.parametrize("start", range(1, 13))
def test_narayana_order_matches_rath_table_10(start):
    from jyotish.constants import SAVYA
    s = start - 1
    direct = (s + 8) % 12 in SAVYA
    assert [x + 1 for x in _sequence(s, direct, "narayana")] == TABLE_10[start]


def test_chara_antardashas(chart, inputs):
    periods = chart.dashas["chara"]
    first = [p for p in periods if len(p.lords) == 1][0]
    assert first.lords == ["Taurus"] and first.start_jd == chart.meta.jd   # no balance
    subs = [p for p in periods if len(p.lords) == 2 and p.lords[0] == "Taurus"][:12]
    # K.N. Rao / Raman: the 9th from Taurus is even-footed, so reverse, from the next sign,
    # the maha sign last; twelve equal parts.
    assert [p.lords[1] for p in subs] == ["Aries", "Pisces", "Aquarius", "Capricorn",
                                          "Sagittarius", "Scorpio", "Libra", "Virgo", "Leo",
                                          "Cancer", "Gemini", "Taurus"]
    assert all(p.end_jd - p.start_jd == pytest.approx(10 * 365.25 / 12) for p in subs)
    # Rath: the stronger of Taurus and Scorpio is Taurus; its lord Venus is in Pisces, so
    # the antardashas start there, zodiacal because Saturn is in Taurus.
    rath = chara(REFERENCE_POSITIONS, 1, chart.meta.jd, variant="rath")
    r_subs = [p.lords[1] for p in rath if len(p.lords) == 2][:12]
    assert r_subs[:3] == ["Pisces", "Aries", "Taurus"] and len(set(r_subs)) == 12


def test_chara_cycles(chart):
    def total(variant):
        ps = chara(REFERENCE_POSITIONS, 1, chart.meta.jd, levels=1, variant=variant)
        return len(ps), round(sum(p.end_jd - p.start_jd for p in ps) / 365.25, 6)
    assert total("kn_rao") == (24, 170)    # second cycle repeats (his worked example)
    assert total("raman") == (12, 87)      # Raman gives no second cycle
    assert total("rath") == (24, 144)      # second cycle is 12 minus the first: 88 + 56


def test_chara_variant_and_year_length_reach_the_chart(inputs):
    kw = dict(inputs)
    kw["meta"] = kw["meta"].model_copy(update={"chara_variant": "rath", "dasha_year": 360.0})
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, **kw)
    first = [p for p in c.dashas["chara"] if len(p.lords) == 1][:2]
    assert [p.lords[0] for p in first] == ["Taurus", "Gemini"]
    assert first[0].end_jd - first[0].start_jd == pytest.approx(11 * 360.0)


def test_chara_own_sign_is_twelve_and_capped():
    pos = dict(REFERENCE_POSITIONS, Venus=40.0, Mercury=160.0)   # Venus in Taurus; Mercury exalted in Virgo
    for v in CHARA_VARIANTS:
        got = dict(seq(v, pos))
        assert got["Taurus"] == 12, v
        assert got["Virgo"] == 12, v       # own and exalted: Rath caps at 12 (p. 42)


def test_chara_dual_lords():
    # Both of Scorpio's lords in Scorpio: 12. One in, one out: count to the one outside.
    both = dict(REFERENCE_POSITIONS, Ketu=220.0, Rahu=40.0)
    assert dict(seq("kn_rao", both))["Scorpio"] == 12
    # Reference: Mars in Scorpio, Ketu in Sagittarius -> 1 year by Ketu.
    assert dict(seq("kn_rao"))["Scorpio"] == 1


def test_rashi_aspects():
    assert rashi_aspects(S["Aries"]) == {S["Leo"], S["Scorpio"], S["Aquarius"]}
    assert rashi_aspects(S["Taurus"]) == {S["Cancer"], S["Libra"], S["Capricorn"]}
    assert rashi_aspects(S["Gemini"]) == {S["Virgo"], S["Sagittarius"], S["Pisces"]}
