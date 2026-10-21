"""The rule evaluator (SPEC Layer 3) and the first ten rules. Every rule has one chart on
which it fires and one on which it does not; the reference chart is the first of these
wherever it can be."""

import json
import shutil

import pytest

from jyotish.chart import analyse
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_POSITIONS, REFERENCE_SPEEDS, reference_time_inputs,
)
from jyotish.rules import FEATURES, RULES_DIR, RuleError, _feature_name, load_rules

REF = REFERENCE_POSITIONS
FIRST_TEN = {"yoga.ruchaka", "yoga.bhadra", "yoga.hamsa", "yoga.malavya", "yoga.sasa",
             "yoga.budhaditya", "yoga.gaja_kesari", "yoga.neecha_bhanga",
             "yoga.kendra_trikona_raja", "yoga.parivartana", "yoga.gaja_kesari_bphs"}

# An Aries-lagna chart with no sign exchange and no kendra-lord/trikona-lord sambandha:
# Mars Ar H1, Sun Ta H2, Jupiter Ge H3, Venus Cn H4, Moon Vi H6, Mercury Li H7, Saturn Pi H12.
QUIET = {"Sun": 40.0, "Moon": 160.0, "Mars": 10.0, "Mercury": 200.0, "Jupiter": 70.0,
         "Venus": 100.0, "Saturn": 340.0, "Rahu": 250.0, "Ketu": 70.0}


def fires(positions, asc, rule_id, **kw):
    chart = analyse(positions, asc, speeds=REFERENCE_SPEEDS, **kw)
    return [f for f in chart.fired_rules if f.id == rule_id]


@pytest.fixture(scope="module")
def ref():
    return analyse(REF, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())


def by_id(chart, rule_id):
    return [f for f in chart.fired_rules if f.id == rule_id]


# --- the library ---------------------------------------------------------------------

def test_library_loads_and_validates():
    assert {r.id for r in load_rules()} == FIRST_TEN
    for r in load_rules():
        for s in r.data["source"]:
            assert s["text"] and s["edition"] and s["chapter"] is not None and s["verse"] is not None
        assert r.data["status"] == "classical_unconfirmed"


def test_schema_features_are_all_evaluable():
    schema = json.loads((RULES_DIR / "rule.schema.json").read_text())
    keys = set(schema["$defs"]["subject"]["properties"]) - {"planet", "planet_in", "all", "any", "not"}
    assert {_feature_name(k) for k in keys} <= set(FEATURES)


# --- the reference chart -------------------------------------------------------------

def test_reference_fires_exactly(ref):
    assert {(f.id, f.basis) for f in ref.fired_rules} == {
        ("yoga.ruchaka", "lagna"), ("yoga.ruchaka", "sun"), ("yoga.budhaditya", "lagna"),
        ("yoga.kendra_trikona_raja", "lagna"), ("yoga.parivartana", "lagna")}


def test_ruchaka_on_reference(ref):
    f = next(f for f in by_id(ref, "yoga.ruchaka") if f.basis == "lagna")
    assert f.nodes == ["Mars", "H7"]
    # Saturn's aspect 0.8 x Pratyak tara 0.85 x Marana Karaka Sthana 0.6. Mars's Shadbala
    # ratio is 1.30, so the weak-Mars 0.5 is evaluated and does not apply.
    assert f.scale == pytest.approx(0.8 * 0.85 * 0.6)
    assert f.unknown == [] and not any("shadbala" in a for a in f.applied)
    assert f.themes["courage"] == pytest.approx(3 * 0.408)
    sun = next(f for f in by_id(ref, "yoga.ruchaka") if f.basis == "sun")
    assert sun.nodes == ["Mars", "H10"] and sun.scale == pytest.approx(0.408)


def test_unknown_feature_is_reported_not_dropped():
    f = fires(REF, REFERENCE_ASC, "yoga.ruchaka")[0]   # no birth moment: no Shadbala
    assert f.unknown == ["shadbala_ratio < 1.0"]
    assert f.scale == pytest.approx(0.408)


def test_budhaditya_on_reference(ref):
    [f] = by_id(ref, "yoga.budhaditya")
    assert f.nodes == ["Sun", "Mercury", "H10"]
    assert f.scale == pytest.approx(0.9)            # Mercury in Bala avastha; not combust


def test_parivartana_on_reference(ref):
    [f] = by_id(ref, "yoga.parivartana")
    assert set(f.nodes) == {"Venus", "Jupiter", "H1", "H11"}
    assert f.details["class_by_houses"] == "maha"
    assert f.details["class_by_lordship"] == "dainya"
    assert f.details["taint"] == [6, 8]
    assert f.scale == pytest.approx(0.8)


def test_kendra_trikona_raja_on_reference(ref):
    got = {frozenset(f.nodes[:2]): f for f in by_id(ref, "yoga.kendra_trikona_raja")}
    assert set(got) == {frozenset({"Sun", "Mercury"}), frozenset({"Mars", "Saturn"})}
    assert got[frozenset({"Sun", "Mercury"})].details["relations"] == ["conjunction"]
    assert got[frozenset({"Sun", "Mercury"})].scale == 1.0
    ms = got[frozenset({"Mars", "Saturn"})]
    assert ms.details["relations"] == ["mutual_aspect"]
    assert ms.scale == pytest.approx(0.75)           # Mars also owns the 12th


@pytest.mark.parametrize("rule_id", ["yoga.gaja_kesari", "yoga.gaja_kesari_bphs", "yoga.bhadra", "yoga.hamsa",
                                     "yoga.malavya", "yoga.sasa", "yoga.neecha_bhanga"])
def test_does_not_fire_on_reference(ref, rule_id):
    assert by_id(ref, rule_id) == []


# --- each rule: fires on one known chart, not on another ------------------------------

@pytest.mark.parametrize("rule_id,positions,asc,node", [
    ("yoga.bhadra", dict(REF, Mercury=70.0), 65.0, "H1"),     # Mercury own in Gemini lagna
    ("yoga.hamsa", dict(REF, Jupiter=100.0), 95.0, "H1"),     # Jupiter exalted, Cancer lagna
    ("yoga.malavya", dict(REF, Venus=200.0), 185.0, "H1"),    # Venus own in Libra lagna
    ("yoga.sasa", dict(REF, Saturn=285.0), 275.0, "H1"),      # Saturn own, Capricorn lagna
])
def test_mahapurusha_fires(rule_id, positions, asc, node):
    f = next(f for f in fires(positions, asc, rule_id) if f.basis == "lagna")
    assert node in f.nodes


def test_sasa_carries_the_mks_modifier():
    f = next(f for f in fires(dict(REF, Saturn=285.0), 275.0, "yoga.sasa") if f.basis == "lagna")
    assert "marana_karaka_sthana -> x0.6" in f.applied   # Saturn in the 1st is MKS


def test_ruchaka_does_not_fire_with_mars_in_gemini():
    assert fires(dict(REF, Mars=75.0), REFERENCE_ASC, "yoga.ruchaka") == []


def test_budhaditya_needs_sun_and_mercury_together():
    assert fires(dict(REF, Mercury=340.0), REFERENCE_ASC, "yoga.budhaditya") == []


def test_gaja_kesari_fires_with_jupiter_tenth_from_moon():
    [f] = fires(dict(REF, Jupiter=100.0), REFERENCE_ASC, "yoga.gaja_kesari")
    assert f.basis == "moon" and f.nodes == ["Jupiter", "H10"]   # Cancer is 10th from Libra
    assert f.scale == 1.0                                          # exalted, not combust


def test_gaja_kesari_bphs_fires_with_a_benefic_joining_jupiter():
    # Jupiter exalted in Cancer with Venus: 10th from the Libra Moon (3rd from the lagna).
    [f] = fires(dict(REF, Jupiter=100.0, Venus=95.0), REFERENCE_ASC, "yoga.gaja_kesari_bphs")
    assert f.basis == "moon" and f.nodes == ["Jupiter", "H10"]


def test_gaja_kesari_bphs_not_in_an_enemy_sign():
    # Reference: Jupiter in Taurus, a kendra from the lagna, but Venus's sign is an enemy's.
    pos = dict(REF, Venus=40.0)                     # give Jupiter a benefic companion too
    chart = analyse(pos, REFERENCE_ASC)
    assert chart.bodies["Jupiter"].dignity == "enemy"
    assert [f for f in chart.fired_rules if f.id == "yoga.gaja_kesari_bphs"] == []


def test_gaja_kesari_bphs_uses_the_shadbala_mercury_rule():
    # Jupiter in Cancer with Mercury and the Sun: Mercury is malefic by association, so no
    # benefic joins Jupiter; with mercury_nature = benefic it does. Drik bala reads the same
    # rule, so the two cannot disagree about Mercury on one chart.
    from jyotish.models import Meta
    from jyotish.shadbala import natural_benefics
    pos = dict(REF, Jupiter=100.0, Mercury=105.0, Sun=118.0)
    assert fires(pos, REFERENCE_ASC, "yoga.gaja_kesari_bphs") == []
    assert "Mercury" not in natural_benefics(pos, "association")
    got = fires(pos, REFERENCE_ASC, "yoga.gaja_kesari_bphs", meta=Meta(mercury_nature="benefic"))
    assert [f.basis for f in got] == ["moon"]


def test_neecha_bhanga_fires_when_the_dispositor_is_in_a_kendra():
    pos = dict(REF, Sun=190.0, Venus=95.0)   # Sun debilitated in Libra; Venus in Cancer, H4
    got = fires(pos, 5.0, "yoga.neecha_bhanga")
    assert {f.basis for f in got} == {"lagna", "moon"}   # Cancer is 4th from Aries, 10th from Libra
    lagna = next(f for f in got if f.basis == "lagna")
    assert lagna.nodes[0] == "Sun"
    assert lagna.details["cancelled_by"] == ["dispositor_in_kendra"]


def test_neecha_bhanga_does_not_fire_without_a_cancellation():
    # Sun debilitated in Libra; Venus (dispositor) in Taurus, H2 from Aries and 8th from the
    # Libra Moon; Mars (exaltation lord) in Scorpio; Saturn (exalted in Libra) in Taurus.
    pos = dict(REF, Sun=190.0, Venus=40.0)
    chart = analyse(pos, 5.0)
    assert chart.bodies["Sun"].dignity == "debilitated"
    assert [f for f in chart.fired_rules if f.id == "yoga.neecha_bhanga"] == []


def test_kendra_trikona_raja_does_not_fire_on_quiet_chart():
    assert fires(QUIET, 5.0, "yoga.kendra_trikona_raja") == []


def test_kendra_trikona_raja_by_exchange():
    # Aries lagna: Sun (5th lord) in Cancer, Moon (4th lord) in Leo.
    [f] = fires(dict(QUIET, Sun=100.0, Moon=130.0, Venus=160.0), 5.0, "yoga.kendra_trikona_raja")
    assert f.details["relations"] == ["exchange"]


def test_parivartana_does_not_fire_on_quiet_chart():
    assert fires(QUIET, 5.0, "yoga.parivartana") == []


def test_parivartana_dainya_by_houses():
    # Aries lagna: Mercury (3rd, 6th lord) in Aries, Mars in Virgo: houses 1 and 6.
    [f] = fires(dict(QUIET, Mercury=15.0, Mars=160.0, Moon=230.0), 5.0, "yoga.parivartana")
    assert f.details["class_by_houses"] == "dainya"
    assert f.scale == pytest.approx(0.5 * 0.8)        # dainya by houses and by lordship


# --- the loader rejects malformed rules -----------------------------------------------

GOOD = """id: yoga.test_rule
family: test
school: parashari
source:
  - {text: BPHS, edition: Santhanam 1984, chapter: 1, verse: 1}
status: experimental
when:
  planet: Mars
  house_in: [1]
  basis: [lagna]
themes: {courage: 1}
outcomes: [career_status]
"""


@pytest.fixture
def libdir(tmp_path):
    shutil.copy(RULES_DIR / "rule.schema.json", tmp_path)
    return tmp_path


def _load_one(libdir, text, name="yoga.test_rule.yaml"):
    (libdir / name).write_text(text)
    return load_rules(libdir)


def test_loader_accepts_good_rule(libdir):
    assert [r.id for r in _load_one(libdir, GOOD)] == ["yoga.test_rule"]


@pytest.mark.parametrize("change,message", [
    (("  house_in: [1]\n", "  - if: aspected_by: [Saturn]\n"), "not valid YAML"),
    (("house_in", "hosue_in"), "Additional properties"),
    (("source:\n  - {text: BPHS, edition: Santhanam 1984, chapter: 1, verse: 1}\n", ""), "'source' is a required"),
    (("status: experimental", "status: maybe"), "status"),
    (("  house_in: [1]\n  basis: [lagna]", "  dignity: own\n  basis: [lagna, moon]"), "must name one basis"),
    (("outcomes: [career_status]\n", "outcomes: [career_status]\nmodifiers:\n  - {if: shadbala_ratoi < 1, scale: 0.5}\n"),
     "unknown feature"),
])
def test_loader_rejects(libdir, change, message):
    with pytest.raises(RuleError, match=message):
        _load_one(libdir, GOOD.replace(*change))


def test_loader_rejects_wrong_file_name(libdir):
    with pytest.raises(RuleError, match="file name must be the rule id"):
        _load_one(libdir, GOOD, name="something_else.yaml")


def test_pair_modifier_needs_a_subject(libdir):
    pair = GOOD.replace("  planet: Mars\n  house_in: [1]\n",
                        "  pair: {a: {planet: Sun}, b: {planet: Moon}, related_by: [conjunction]}\n")
    pair += "modifiers:\n  - {if: combust, scale: 0.5}\n"
    with pytest.raises(RuleError, match="needs `of`"):
        _load_one(libdir, pair)


def test_checked_sources_name_a_verse():
    for r in load_rules():
        for s in r.data["source"]:
            if s.get("checked"):
                assert str(s["verse"]) != "unverified", (r.id, s)
