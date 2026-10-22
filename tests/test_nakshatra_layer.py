"""The nakshatra layer to the finest grain the engine computes (SPEC Layer 2): the 27 nakshatras'
attributes, the nakshatra and dispositor tables of the chart display, the special nakshatra
points, and the tara rows of the transit timeline, on the reference chart."""

from collections import Counter

import pytest
import swisseph as swe

from jyotish.constants import NAK_ATTRIBUTE_KEYS, NAK_ATTRIBUTE_SOURCES, NAK_ATTRIBUTES, NAKSHATRAS
from jyotish.display import tables
from jyotish.nakpoints import ABHIJIT, counted_pada, in_abhijit
from jyotish.nakshatra import navatara
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.transits import Sky, transit_timeline
from jyotish.uncertainty import assess


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def t(chart):
    from datetime import date
    return tables(chart, date(2026, 10, 21))


def test_the_attribute_table_is_whole_and_sourced():
    assert len(NAK_ATTRIBUTES) == 27 and all(set(a) == set(NAK_ATTRIBUTE_KEYS) for a in NAK_ATTRIBUTES)
    for key in ("gana", "nadi", "tri_nadi"):
        assert sorted(Counter(a[key] for a in NAK_ATTRIBUTES).values()) == [9, 9, 9], key
    assert {a["nadi"]: a["tri_nadi"] for a in NAK_ATTRIBUTES} == {"vata": "adi", "pitta": "madhya", "kapha": "antya"}
    assert Counter(a["activity"] for a in NAK_ATTRIBUTES) == {
        "dhruva": 4, "chara": 5, "ugra": 5, "mishra": 2, "kshipra": 3, "mridu": 4, "tikshna": 4}
    assert Counter(a["direction"] for a in NAK_ATTRIBUTES) == {"east": 7, "south": 7, "west": 6, "north": 7}
    assert set(NAK_ATTRIBUTE_SOURCES) == set(NAK_ATTRIBUTE_KEYS)
    assert all("text" in s and s["checked"] is False for s in NAK_ATTRIBUTE_SOURCES.values())   # none read yet


def test_each_body_carries_its_nakshatras_attributes(chart):
    moon = chart.bodies["Moon"].nak_attributes
    assert chart.bodies["Moon"].nak_name == "Chitra"
    assert moon.model_dump() == {"deity": "Tvashtar", "gana": "rakshasa", "yoni": "tiger", "nadi": "pitta",
                                 "tri_nadi": "madhya", "gender": "female", "direction": "south", "activity": "mridu"}
    jup = chart.bodies["Jupiter"]
    assert jup.nak_name == "Rohini" and (jup.nak_attributes.deity, jup.nak_attributes.activity) == ("Brahma", "dhruva")
    assert all(b.nak_attributes.model_dump() == NAK_ATTRIBUTES[b.nak] for b in chart.bodies.values())


def test_the_nakshatra_table(chart, t):
    rows = {r["planet"]: r for r in t["nakshatras"]["rows"]}
    assert list(rows)[0] == "Ascendant" and len(rows) == 10
    asc = rows["Ascendant"]
    assert (asc["nakshatra"], asc["lord"], asc["tara"], asc["cycle"], asc["deity"]) == ("Krittika", "Sun", "Mitra", 2, "Agni")
    moon = rows["Moon"]
    assert (moon["nakshatra"], moon["pada"], moon["pada_navamsa"], moon["lord"]) == ("Chitra", 3, "Libra", "Mars")
    assert (moon["tara"], moon["cycle"]) == ("Janma", 1)
    b = chart.bodies["Saturn"]
    sat = rows["Saturn"]
    assert (sat["sub_lord"], sat["sub_sub_lord"]) == (b.sub_lord, b.sub_sub_lord) and sat["tara"] == "Mitra"
    assert set(NAK_ATTRIBUTE_KEYS) <= set(sat) and t["nakshatras"]["sources"] == NAK_ATTRIBUTE_SOURCES


def test_the_dispositor_panel(t):
    nak = {r["planet"]: r for r in t["dispositors"]["nakshatra"]["rows"]}
    assert nak["Saturn"]["chain"] == ["Saturn", "Sun", "Jupiter", "Moon", "Mars", "Mercury"]
    assert nak["Saturn"]["loop"] == ["Mars", "Mercury"] and nak["Rahu"]["loop"] == ["Rahu"]
    assert t["dispositors"]["nakshatra"]["loops"] == [["Mars", "Mercury"], ["Rahu"]]
    assert t["dispositors"]["sign"]["loops"] == [["Jupiter", "Venus"], ["Mars"]]
    assert t["dispositors"]["navamsa"]["loops"] == [["Saturn"], ["Mars", "Jupiter"]]


def test_the_special_nakshatra_points(chart, t):
    np = chart.features.nakshatra_points
    m64, l64 = np.navamsa_64["moon"], np.navamsa_64["lagna"]
    # The Moon in Chitra's 3rd pada (181°26'): the 64th pada is Krittika's 2nd, Taurus 0° to 3°20'.
    assert (m64.start, m64.sign, m64.nakshatra, m64.pada, m64.navamsa_sign, m64.navamsa_lord) == \
        (30.0, "Taurus", "Krittika", 2, "Capricorn", "Saturn")
    assert (l64.sign, l64.nakshatra, l64.pada, l64.navamsa_sign, l64.navamsa_lord) == ("Sagittarius", "Mula", 2, "Taurus", "Venus")
    m88, l88 = np.pada_88["moon"], np.pada_88["lagna"]
    assert (m88.nakshatra, m88.pada, m88.navamsa_sign) == ("Ashlesha", 2, "Capricorn")
    assert (l88.nakshatra, l88.pada) == ("PurvaBhadra", 2)
    assert np.abhijit.occupants == [] and (np.abhijit.start, round(np.abhijit.end, 6)) == (276 + 40 / 60, 280.888889)
    lag = np.nakshatra_lagnesha
    assert (lag.planet, lag.lagna_nakshatra, lag.sign, lag.house, lag.nakshatra, lag.dignity) == \
        ("Sun", "Krittika", "Aquarius", 10, "PurvaBhadra", "enemy")
    assert set(np.sources) == {"navamsa_64", "pada_88", "abhijit", "nakshatra_lagnesha"}
    assert all(s["checked"] is False for s in np.sources.values())
    assert t["nakshatra_points"]["nakshatra_lagnesha"]["planet"] == "Sun"


def test_pada_and_abhijit_boundaries():
    # Rule 3: 108 * lon / 360, never a division by 3°20'; 30° is the first pada of Krittika's 2nd quarter.
    assert (counted_pada(30.0, 1, "x").nakshatra, counted_pada(30.0, 1, "x").pada) == ("Krittika", 2)
    assert counted_pada(10 / 3, 1, "x").pada == 2 and counted_pada(10 / 3 - 1e-9, 1, "x").pada == 1
    assert counted_pada(359.999, 2, "x").nakshatra == "Ashwini"                    # counts wrap at Revati
    assert counted_pada(0.0, 64, "x").start == pytest.approx(210.0)              # 63 padas on
    assert in_abhijit(ABHIJIT[0]) and not in_abhijit(ABHIJIT[0] - 1e-9) and not in_abhijit(ABHIJIT[1])


@pytest.fixture(scope="module")
def tl(chart):
    return transit_timeline(chart, swe.julday(2026, 1, 1, 0.0), swe.julday(2030, 1, 1, 0.0))


def test_slow_planets_entering_adverse_taras(chart, tl):
    slow = [r for r in tl.tara_rows if r.body != "Moon"]
    assert slow and {r.body for r in slow} <= {"Saturn", "Jupiter", "Rahu", "Ketu"}
    moon = chart.bodies["Moon"].nak
    for r in slow:
        assert r.adverse and r.tara in ("Vipat", "Pratyak", "Vadha") and r.entered in ("direct", "retrograde")
        assert navatara(NAKSHATRAS.index(r.nakshatra), moon).name == r.tara and "adverse" in r.tags
    first = slow[0]
    assert (first.body, first.nakshatra, first.tara, first.cycle) == ("Saturn", "Revati", "Pratyak", 2)
    assert swe.revjul(first.start_jd)[:3] == (2026, 5, 17)


def test_the_daily_moon_tara(chart, tl):
    sky = Sky(chart.meta.ayanamsa, chart.meta.node == "true")
    moon = [r for r in tl.tara_rows if r.body == "Moon"]
    assert moon[0].start_jd == tl.start_jd and moon[-1].end_jd == tl.end_jd
    assert all(a.end_jd == b.start_jd for a, b in zip(moon, moon[1:]))          # they tile the range
    assert all(0.8 < r.end_jd - r.start_jd < 1.3 for r in moon[1:-1])
    for r in moon[::97]:
        mid = (r.start_jd + r.end_jd) / 2
        assert NAKSHATRAS[int(sky.lon("Moon", mid) * 27 / 360) % 27] == r.nakshatra
        assert "daily" in r.tags and r.adverse == (r.tara in ("Vipat", "Pratyak", "Vadha"))


def test_tara_rows_are_tagged_and_not_scored(chart):
    from jyotish.timing import tagged_timeline
    a, b = swe.julday(2026, 10, 1, 0.0), swe.julday(2026, 11, 1, 0.0)
    kinds = Counter(r.kind for r in tagged_timeline(chart, a, b).rows)
    assert kinds["tara"] > 25 and kinds["dasha"] and kinds["transit"]
    assert transit_timeline(chart, a, b, taras=False).tara_rows == []           # what the timing join reads
