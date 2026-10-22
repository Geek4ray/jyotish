"""The sign and nakshatra draft families on the placements generator (scripts/make_placements.py):
the Moon in each sign (Brihat Jataka 17) and nakshatra (16), the other eight planets in each sign
(Brihat Jataka 18, Saravali second), the rising sign (Saravali). Drafts: they fire, are recorded,
are narrated as a placement fact only and change no score."""

import csv
from datetime import date
from pathlib import Path

import pytest

from jyotish.chart import analyse
from jyotish.constants import NAKSHATRAS
from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS as REF, REFERENCE_SPEEDS, reference_time_inputs
from jyotish.rules import NAKSHATRA_PLACEMENTS, SIGN_PLACEMENTS, load_rules, weighed

ROOT = Path(__file__).resolve().parents[1]
TABLE = [r for r in csv.DictReader((ROOT / "scripts" / "placements.csv").open(newline=""))
         if r["kind"] in ("moon_sign", "moon_nakshatra", "planet_sign", "lagna_sign")]
RULES = {r.id: r for r in load_rules()}
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
         "Aquarius", "Pisces"]


def test_the_four_kinds_are_whole_drafts():
    kinds = {}
    for r in TABLE:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    assert kinds == {"moon_sign": 12, "moon_nakshatra": 27, "planet_sign": 96, "lagna_sign": 12}
    for row in TABLE:
        d = RULES[row["id"]].data
        assert d["status"] == "draft" and not weighed(d["status"], d["family"]) and d["confidence_base"] == 0.3
        assert d["family"] in SIGN_PLACEMENTS | NAKSHATRA_PLACEMENTS
        assert d["names"] and d["themes"] and d["outcomes"] and d["narration_key"].endswith(".")
        assert all(isinstance(v, int) and 1 <= abs(v) <= 2 for v in d["themes"].values())
        src = d["source"][0]
        assert src["checked"] is False and src["verse"] == "not yet located"
        assert all(not row[c] for c in ("verse_read_by", "verse_read_on", "effect_confirmed", "practitioner_note"))
        if row["kind"] == "lagna_sign":
            assert (src["text"], src["chapter"]) == ("Saravali", "not yet located")
        else:
            chapter = {"moon_nakshatra": 16, "moon_sign": 17, "planet_sign": 18}[row["kind"]]
            assert (src["text"], src["edition"], src["chapter"]) == ("Brihat Jataka", "N. Chidambaram Iyer 1885", chapter)
        if row["kind"] == "planet_sign":
            assert d["source"][1]["text"] == "Saravali"                          # the second edition
    moon = RULES["place.moon_in_libra"].data
    assert [m["if"] for m in moon["modifiers"]] == [{"paksha": "krishna"}, "paksha_bala < 30", {"dignity": "debilitated"}]
    assert [m["if"] for m in RULES["place.saturn_in_taurus"].data["modifiers"]] == ["retro", "combust"]
    assert "modifiers" not in RULES["place.sun_in_leo"].data and "modifiers" not in RULES["place.rahu_in_gemini"].data
    assert {"temperament", "emotional_life"} == set(moon["themes"])                # personality and mind


@pytest.fixture(scope="module")
def ref():
    return analyse(REF, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())


def test_they_fire_on_the_reference_chart(ref):
    # The reference chart: Taurus rising, the Moon in Libra in Chitra (not Rohini: Jupiter is in Rohini).
    fires = {f.id: f for f in ref.fired_rules if f.family in SIGN_PLACEMENTS | NAKSHATRA_PLACEMENTS}
    assert set(fires) == {"place.moon_in_libra", "place.moon_in_chitra", "place.lagna_taurus", "place.sun_in_aquarius",
                          "place.mars_in_scorpio", "place.mercury_in_aquarius", "place.jupiter_in_taurus",
                          "place.venus_in_pisces", "place.saturn_in_taurus", "place.rahu_in_gemini",
                          "place.ketu_in_sagittarius"}
    assert "place.moon_in_taurus" not in fires and "place.moon_in_rohini" not in fires and "place.lagna_aries" not in fires
    assert fires["place.moon_in_libra"].applied == ["paksha: krishna -> x0.8"]       # a waning Moon
    assert fires["place.venus_in_pisces"].applied == ["retro -> x1.2"]
    assert fires["place.lagna_taurus"].nodes[0] == "Venus"                          # the rule binds the lagna lord


def _chart(kind: str, planet: str | None, k: int):
    """Aries lagna; the planet (or the lagna) in the middle of sign k, or of nakshatra k."""
    pos = {"Sun": 40.0, "Moon": 160.0, "Mars": 10.0, "Mercury": 200.0, "Jupiter": 70.0, "Venus": 100.0,
           "Saturn": 340.0, "Rahu": 250.0, "Ketu": 70.0}
    asc = 15.0
    mid = (k * 360 / 27 + 180 / 27) if kind == "moon_nakshatra" else k * 30 + 15.0
    if kind == "lagna_sign":
        asc = mid
    else:
        pos[planet] = mid
        if planet in ("Rahu", "Ketu"):
            pos["Ketu" if planet == "Rahu" else "Rahu"] = (mid + 180.0) % 360
    return {f.id for f in analyse(pos, asc).fired_rules}


@pytest.mark.parametrize("row", TABLE, ids=[r["id"] for r in TABLE])
def test_each_fires_where_it_should_and_not_one_on(row):
    kind = row["kind"]
    k = NAKSHATRAS.index(row["nakshatra"]) if kind == "moon_nakshatra" else int(row["sign"])
    n = 27 if kind == "moon_nakshatra" else 12
    planet = row["planet"] or None
    assert row["id"] in _chart(kind, planet, k)
    assert row["id"] not in _chart(kind, planet, (k + 1) % n)


@pytest.fixture(scope="module")
def timed():
    from jyotish.chart import compute
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_narration_offers_one_sign_row_and_one_nakshatra_row(timed):
    from jyotish.narrate import _check_data, findings, learner_data, other_placements
    from jyotish.scoring import AREAS
    for area in AREAS:
        ok = findings(timed, area, date(2026, 10, 21))[0]
        fam = [f.get("family") for f in ok]
        assert sum(f in SIGN_PLACEMENTS for f in fam) <= 1 and sum(f in NAKSHATRA_PLACEMENTS for f in fam) <= 1, area
        assert sum(f in ("lord_in_house", "planet_in_house") for f in fam) <= 3, area
        offered = {f["finding_id"] for f in ok}
        assert not offered & {o["finding_id"] for o in other_placements(timed, area)}
    personality = {f["finding_id"]: f for f in findings(timed, "personality")[0]}
    assert "place.lagna_taurus@lagna" in personality and "place.moon_in_chitra@lagna" in personality
    mind = {f["finding_id"]: f for f in findings(timed, "mind")[0]}
    assert {"place.moon_in_libra@lagna", "place.moon_in_chitra@lagna"} <= set(mind)
    assert "place.lagna_taurus" in [o["rule_id"] for o in other_placements(timed, "mind")]
    lagna = personality["place.lagna_taurus@lagna"]
    data = _check_data(lagna)
    assert data["placement"] == {"lagna_sign": "Taurus", "lagna_lord": "Venus"} and "themes" not in data
    assert data["status"] == "draft" and "classical_effect" not in data         # a fact only
    assert _check_data(mind["place.moon_in_chitra@lagna"])["placement"] == {"planet": "Moon", "nakshatra": "Chitra"}
    d = learner_data(mind["place.moon_in_libra@lagna"])
    assert d["effect_status"].startswith("draft") and d["effect"].startswith("The Moon in Libra (Venus's sign)")
    assert "Lagna" in [o["planet"] for o in other_placements(timed, "mind")]


def test_a_sign_row_sentence_names_the_sign():
    from jyotish.narrate import validate
    tags = {"rule:place.moon_in_libra"}
    assert validate("The Moon sits in Libra [rule:place.moon_in_libra].", tags) == []
    assert any("names none of ['Libra']" in e for e in validate("The Moon sits in the 6th [rule:place.moon_in_libra].", tags))


def test_the_triage_sheet_carries_the_new_kinds():
    sheet = {r["id"]: r for r in csv.DictReader((ROOT / "scripts" / "placements_triage.csv").open(newline=""))}
    assert sheet["place.moon_in_libra"]["placement"] == "the Moon in Libra"
    assert sheet["place.moon_in_libra"]["verse_reference"] == \
        "Brihat Jataka (N. Chidambaram Iyer 1885), chapter 17, the Moon in Libra (verse not yet located)"
    assert sheet["place.lagna_taurus"]["placement"] == "Taurus rising"
    assert sheet["place.lagna_taurus"]["verse_reference"] == \
        "Saravali (Santhanam 1983), chapter not yet located, Taurus rising (verse not yet located)"
    assert sheet["place.moon_in_chitra"]["placement"] == "the Moon in Chitra"
    assert sheet["place.saturn_in_taurus"]["placement"] == "Saturn in Taurus"
    assert all(sheet[r["id"]]["verse_read_by"] == "" for r in TABLE)
    guide = (ROOT / "docs" / "triage.md").read_text()
    for kind in ("Moon in each sign", "Moon in each nakshatra", "planets in each sign", "rising sign"):
        assert kind in guide, kind
