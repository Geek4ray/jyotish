"""The SPEC.md worked example as executable acceptance tests. Every assertion here is a
value stated in the spec's 'Worked example' section for the Taurus-lagna reference chart.
If a test fails, either the code or the spec is wrong, and the spec is fixed too."""

import pytest

from jyotish.chart import analyse
from jyotish.constants import SIGNS
from jyotish.nakshatra import vimshottari_balance
from jyotish.reference import REFERENCE_ASC, REFERENCE_D9, REFERENCE_POSITIONS, REFERENCE_SPEEDS

S = {name: i for i, name in enumerate(SIGNS)}


@pytest.fixture(scope="module")
def chart():
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS)


def test_nakshatra_and_pada(chart):
    expect = {
        "Sun": ("PurvaBhadra", 3), "Moon": ("Chitra", 3), "Mars": ("Jyestha", 1),
        "Mercury": ("Dhanishtha", 3), "Jupiter": ("Rohini", 1), "Venus": ("Revati", 3),
        "Saturn": ("Krittika", 2), "Rahu": ("Ardra", 4), "Ketu": ("PurvaAshadha", 2),
    }
    for name, (nak, pada) in expect.items():
        assert (chart.bodies[name].nak_name, chart.bodies[name].pada) == (nak, pada), name
    assert chart.lagnas.asc_nak == "Krittika"


def test_navamsa_matches_the_app(chart):
    for name, sign in REFERENCE_D9.items():
        assert chart.vargas["D9"][name] == sign, f"{name} D9 should be {SIGNS[sign]}"


def test_lordship_and_roles(chart):
    f = chart.features
    assert f.lordship == {"Sun": [4], "Moon": [3], "Mars": [7, 12], "Mercury": [2, 5],
                          "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
    assert f.roles["Saturn"] == ["yogakaraka"]
    assert f.roles["Venus"] == ["lagna_lord"]
    assert "maraka" in f.roles["Mars"] and "maraka" in f.roles["Mercury"]


def test_dignities_natural(chart):
    b = chart.bodies
    assert b["Venus"].dignity == "exalted"
    assert b["Venus"].deep_exalt_dist == pytest.approx(27 - (23 + 39 / 60 + 19 / 3600), abs=1e-6)
    assert b["Mars"].dignity == "own"
    assert b["Saturn"].dignity == "friend"
    assert b["Mercury"].dignity == "neutral"
    assert b["Sun"].dignity == "enemy"
    assert b["Jupiter"].dignity == "enemy"
    assert b["Moon"].dignity == "neutral"
    assert b["Moon"].dignity_compound == "enemy"   # Venus is 6th from the Moon


def test_avasthas_odd_even(chart):
    b = chart.bodies
    assert b["Moon"].avastha_baladi == "Bala"      # Libra is odd: forward
    assert b["Mercury"].avastha_baladi == "Bala"
    assert b["Saturn"].avastha_baladi == "Mrita"   # Taurus is even: reversed
    assert b["Jupiter"].avastha_baladi == "Vriddha"


def test_sensitive_flags(chart):
    b = chart.bodies
    assert b["Mars"].marana_karaka_sthana and b["Saturn"].marana_karaka_sthana
    assert not b["Rahu"].marana_karaka_sthana
    assert b["Rahu"].pushkara_navamsa and b["Rahu"].pushkara_bhaga
    assert not b["Moon"].pushkara_navamsa and not b["Moon"].pushkara_bhaga
    assert {n for n, x in b.items() if x.boundary} == {"Moon", "Mercury", "Saturn", "Sun"}
    assert b["Moon"].vargottama
    assert not b["Mercury"].combust  # 27° from the Sun


def test_aspects(chart):
    asp = set(chart.features.aspects)
    assert {("Saturn", 3), ("Saturn", 7), ("Saturn", 10)} <= asp
    assert {("Jupiter", 5), ("Jupiter", 7), ("Jupiter", 9)} <= asp
    assert {("Mars", 1), ("Mars", 10), ("Mars", 2)} <= asp


def test_sign_dispositor_chains(chart):
    d = chart.features.dispositors
    assert d.sign["Sun"] == ["Sun", "Saturn", "Venus", "Jupiter"]
    assert d.sign["Rahu"] == ["Rahu", "Mercury", "Saturn", "Venus", "Jupiter"]
    assert d.sign["Mars"] == ["Mars"]
    assert sorted(d.final_sign) == ["Jupiter", "Mars", "Venus"]
    loop = next(l for l in d.loops if sorted(l.planets) == ["Jupiter", "Venus"])
    assert loop.houses == [1, 11]
    assert loop.class_by_houses == "maha" and loop.class_by_lordship == "dainya"
    assert loop.taint == [6, 8]


def test_nakshatra_dispositor_chains(chart):
    d = chart.features.dispositors
    assert d.nakshatra["Saturn"] == ["Saturn", "Sun", "Jupiter", "Moon", "Mars", "Mercury"]
    assert d.nakshatra["Mars"] == ["Mars", "Mercury"] and d.nakshatra["Mercury"] == ["Mercury", "Mars"]
    assert d.nakshatra["Rahu"] == ["Rahu"]
    assert sorted(d.final_nakshatra) == ["Mars", "Mercury", "Rahu"]


def test_navamsa_dispositor_chains(chart):
    d = chart.features.dispositors
    assert sorted(d.final_navamsa) == ["Jupiter", "Mars", "Saturn"]  # Saturn own; Jupiter-Mars exchange


def test_navatara(chart):
    expect = {
        "Sun": ("Vipat", 2), "Moon": ("Janma", 1), "Mars": ("Pratyak", 1), "Mercury": ("Janma", 2),
        "Jupiter": ("Atimitra", 2), "Venus": ("Pratyak", 2), "Saturn": ("Mitra", 2),
        "Rahu": ("Sampat", 3), "Ketu": ("Vadha", 1),
    }
    for name, (tara, cycle) in expect.items():
        t = chart.bodies[name].tara
        assert (t.name, t.cycle) == (tara, cycle), name
    assert chart.lagnas.asc_tara == "Mitra"
    assert chart.bodies["Mercury"].tara.special == "karma"      # 10th from Janma
    assert chart.bodies["Jupiter"].tara.special == "samudaya"   # 18th


def test_chara_karakas_both_schemes(chart):
    j = chart.features.jaimini
    assert j.karakas == {"AK": "Sun", "AmK": "Venus", "BK": "Mars", "MK": "Rahu", "PiK": "Jupiter",
                         "PK": "Saturn", "GK": "Moon", "DK": "Mercury"}
    assert j.karakas_7 == {"AK": "Sun", "AmK": "Venus", "BK": "Mars", "MK": "Jupiter",
                           "PK": "Saturn", "GK": "Moon", "DK": "Mercury"}
    assert j.karakamsa == S["Gemini"]


def test_arudha_padas(chart):
    a = chart.features.jaimini.arudhas
    assert a["AL"] == S["Capricorn"]
    assert a["UL"] == S["Gemini"]
    assert a["A7"] == S["Leo"]       # Mars in the 7th itself: exception
    assert a["A10"] == S["Taurus"]   # pada fell 7th from the 10th: exception
    assert a["A2"] == S["Libra"]


def test_sudarshana_tenth(chart):
    s = chart.features.sudarshana_h10
    assert s == {"from_lagna": ["Sun", "Mercury"], "from_moon": [], "from_sun": ["Mars"]}


def test_kp_seventh_cusp(chart):
    assert chart.lagnas.cusp_lords_kp[7] == {"star": "Saturn", "sub": "Mercury", "sub_sub": "Sun"}


def test_vimshottari_balance():
    lord, years = vimshottari_balance(REFERENCE_POSITIONS["Moon"])
    assert lord == "Mars"
    assert years == pytest.approx(2.75, abs=0.02)
