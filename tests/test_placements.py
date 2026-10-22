"""The placement rule library (SPEC Layer 6b item 4): generated from scripts/placements.csv by
scripts/make_placements.py; lord-in-house from BPHS 24, planet-in-house from Phaladeepika 8."""

import csv
import importlib.util
import shutil
from pathlib import Path

import pytest

from jyotish.chart import analyse
from jyotish.constants import SIGN_LORD
from jyotish.reference import REFERENCE_ASC, REFERENCE_POSITIONS as REF, REFERENCE_SPEEDS, reference_time_inputs
from jyotish.rules import RULES_DIR, load_rules

ROOT = Path(__file__).resolve().parents[1]
TABLE = list(csv.DictReader((ROOT / "scripts" / "placements.csv").open(newline="")))
PLACE = {r.id: r for r in load_rules() if r.id.startswith("place.")}
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _generator(tmp_rules=None):
    spec = importlib.util.spec_from_file_location("make_placements", ROOT / "scripts" / "make_placements.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if tmp_rules is not None:
        mod.RULES = tmp_rules
    return mod


def test_committed_files_are_the_table():
    assert _generator().main(check=True) == 0                       # nothing differs from the table


def test_generator_is_idempotent(tmp_path, capsys):
    shutil.copy(RULES_DIR / "rule.schema.json", tmp_path)
    gen = _generator(tmp_path)
    gen.main()
    first = {p.name: p.read_text() for p in tmp_path.glob("place.*.yaml")}
    capsys.readouterr()
    gen.main()
    assert "0 written or removed" in capsys.readouterr().out
    assert {p.name: p.read_text() for p in tmp_path.glob("place.*.yaml")} == first
    assert len(first) == len(TABLE)
    (tmp_path / "place.stale_h1.yaml").write_text("id: place.stale_h1\\n")    # a row removed from the table
    gen.main()
    assert not (tmp_path / "place.stale_h1.yaml").exists()


def test_every_row_is_a_valid_rule():
    assert set(PLACE) == {r["id"] for r in TABLE}
    for rid, r in PLACE.items():
        d = r.data
        assert d["status"] == "draft" and d["confidence_base"] == 0.3 and d["school"] == "parashari"   # no verse read yet
        assert d["when"]["basis"] == ["lagna"]                         # Sudarshana stays with the yogas
        assert all(isinstance(v, int) and 1 <= abs(v) <= 2 for v in d["themes"].values()), rid
        [src] = d["source"]
        assert src["checked"] is False and src["verse"] == "not yet located"
        assert (src["text"], src["chapter"]) in (("BPHS", 24), ("Phaladeepika", 8))
        assert d["narration_key"] and "\\n" not in d["narration_key"] and '"' not in d["narration_key"]
        assert d["outcomes"]


def _chart_with(planet: str, house: int):
    """Aries lagna (so house n is sign n-1); `planet` in the middle of house `house`; the
    others parked where they do not matter, the nodes opposite."""
    pos = {"Sun": 40.0, "Moon": 160.0, "Mars": 10.0, "Mercury": 200.0, "Jupiter": 70.0, "Venus": 100.0,
           "Saturn": 340.0, "Rahu": 250.0, "Ketu": 70.0}
    pos[planet] = (house - 1) * 30 + 15.0
    if planet in ("Rahu", "Ketu"):
        other = "Ketu" if planet == "Rahu" else "Rahu"
        pos[other] = (pos[planet] + 180.0) % 360
    return analyse(pos, 15.0)


@pytest.fixture(scope="module")
def charts():
    return {(p, h): {f.id for f in _chart_with(p, h).fired_rules} for p in PLANETS for h in range(1, 13)}


def _subject(rid):
    when = PLACE[rid].data["when"]
    if "lord_of" in when:
        return SIGN_LORD[when["lord_of"][0] - 1], when["house"]       # Aries lagna: the lord of house n
    return when["planet"], when["house"]


@pytest.mark.parametrize("rid", sorted(r["id"] for r in TABLE))
def test_each_rule_fires_where_it_should_and_not_a_house_on(rid, charts):
    planet, house = _subject(rid)
    assert rid in charts[(planet, house)]
    assert rid not in charts[(planet, house % 12 + 1)]


REFERENCE_LORD_FIRES = {
    "place.l10_h1": "Saturn", "place.l9_h1": "Saturn",        # Saturn in the 1st as 9th and 10th lord
    "place.l1_h11": "Venus", "place.l6_h11": "Venus",         # Venus in the 11th as 1st and 6th lord
    "place.l7_h7": "Mars", "place.l12_h7": "Mars",            # Mars in the 7th as 7th and 12th lord
    "place.l2_h10": "Mercury", "place.l5_h10": "Mercury",     # Mercury in the 10th as 2nd and 5th lord
    "place.l4_h10": "Sun",                                    # the Sun in the 10th as 4th lord
    "place.l8_h1": "Jupiter", "place.l11_h1": "Jupiter",      # Jupiter in the 1st as 8th and 11th lord
    "place.l3_h6": "Moon",                                    # the Moon in the 6th as 3rd lord
}


@pytest.fixture(scope="module")
def ref():
    return analyse(REF, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())


def test_reference_lord_in_house_fires(ref):
    fires = {f.id: f for f in ref.fired_rules if f.family == "lord_in_house"}
    assert {k: f.nodes[0] for k, f in fires.items()} == REFERENCE_LORD_FIRES
    # The standard modifiers: Saturn in the 1st and Mars in the 7th are marana karaka sthana,
    # Jupiter (Taurus) and the Sun (Aquarius) are in enemies' signs.
    assert fires["place.l10_h1"].scale == pytest.approx(0.6) and fires["place.l7_h7"].scale == pytest.approx(0.6)
    assert fires["place.l8_h1"].scale == pytest.approx(0.8) and fires["place.l4_h10"].scale == pytest.approx(0.8)
    assert fires["place.l1_h11"].scale == 1.0                  # Venus exalted: no reduction


REFERENCE_PLANET_FIRES = {"place.saturn_h1", "place.jupiter_h1", "place.rahu_h2", "place.moon_h6", "place.mars_h7",
                          "place.ketu_h8", "place.sun_h10", "place.mercury_h10", "place.venus_h11"}


def test_reference_planet_in_house_fires(ref):
    fires = {f.id: f for f in ref.fired_rules if f.family == "planet_in_house"}
    assert set(fires) == REFERENCE_PLANET_FIRES                  # every graha exactly once
    assert fires["place.mars_h7"].scale == pytest.approx(0.6)     # marana karaka sthana
    assert fires["place.saturn_h1"].scale == pytest.approx(0.6)
    assert fires["place.venus_h11"].scale == 1.0 and fires["place.ketu_h8"].scale == 1.0
    assert fires["place.sun_h10"].themes["career"] > 0             # a malefic in an upachaya
    assert fires["place.rahu_h2"].themes["wealth"] < 0             # a malefic in the 2nd


def test_about_twenty_placements_fire_on_a_chart(ref):
    n = sum(1 for f in ref.fired_rules if f.id.startswith("place."))
    assert n == len(REFERENCE_LORD_FIRES) + len(REFERENCE_PLANET_FIRES) == 21


# --- part 3: the consequences -----------------------------------------------------------------

@pytest.fixture(scope="module")
def timed():
    from jyotish.chart import compute
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_rule_term_weighs_each_fire_by_its_confidence_base(timed):
    from jyotish.scoring import FIRE_BASIS, THEME_AREAS, WEIGHTS
    lib = {r.id: r.data.get("confidence_base", 0.5) for r in load_rules()}
    for area in ("career", "marriage", "siblings", "longevity"):
        expected = sum(WEIGHTS["rule"] * lib[f.id] * FIRE_BASIS[f.basis] *
                       sum(v for th, v in f.themes.items() if area in THEME_AREAS.get(th, []))
                       for f in timed.fired_rules if f.status not in ("experimental", "draft"))
        assert timed.scored.areas[area].terms["rules"] == pytest.approx(expected), area
    assert "rule term c_r = the rule's confidence_base" in " ".join(timed.scored.readings)


def test_a_single_placement_never_outweighs_a_yoga_theme_for_theme():
    # At full scale, a placement's largest theme (|2| x 0.3) is below every yoga's largest
    # theme times its own confidence_base.
    rules = load_rules()
    place = max(0.3 * max(abs(v) for v in r.data["themes"].values()) for r in rules if r.id.startswith("place."))
    yogas = min(r.data.get("confidence_base", 0.5) * max(abs(v) for v in r.data["themes"].values())
                for r in rules if r.id.startswith("yoga.") and r.data["status"] != "experimental")
    assert place == pytest.approx(0.6) and place < yogas


def test_driver_and_tiers_on_the_reference_chart(timed):
    # The placements fire for every planet by construction, so the driver's rule share leaves
    # them out; and no tier changes: a tier follows the votes' agreement with the sign of S,
    # and no area's S changed sign or crossed its population p40 with the placements weighed.
    sc = timed.scored
    assert sc.driver.driver == "Venus" and sc.top == ["career", "marriage", "longevity"]
    tiers = {n: a.tier for n, a in sc.areas.items()}
    assert tiers == {"personality": "weak / mixed", "wealth": "moderate", "siblings": "weak / mixed",
                     "mother_home": "weak / mixed", "children": "not emphasised", "intellect": "weak / mixed",
                     "health": "weak / mixed", "debts_enemies": "moderate", "marriage": "moderate",
                     "longevity": "moderate", "father": "not emphasised", "fortune": "weak / mixed",
                     "career": "moderate", "gains": "not emphasised", "foreign": "weak / mixed",
                     "spirituality": "weak / mixed", "mind": "weak / mixed", "reputation": "weak / mixed",
                     "synastry": "needs two charts"}


def test_an_area_offers_at_most_three_placements_the_strongest(timed):
    from jyotish.narrate import PLACEMENTS_PER_AREA, _check_data, findings, other_placements
    from jyotish.scoring import AREAS
    for area in AREAS:
        offered = [f for f in findings(timed, area)[0] if f.get("family") in ("lord_in_house", "planet_in_house")]
        rest = other_placements(timed, area)
        assert len(offered) <= PLACEMENTS_PER_AREA == 3, area
        if rest:
            assert len(offered) == 3, area
        # Drafts reach the writer and the checker as placement facts only: no effect, no themes.
        for f in offered:
            data = _check_data(f)
            assert data["status"] == "draft" and "classical_effect" not in data and "themes" not in data
            assert "contribution" not in f and set(data["placement"]) >= {"planet", "house"}
    career = {f["finding_id"] for f in findings(timed, "career")[0] if f.get("family")}
    assert {x for x in career if x.startswith("place.")} == {"place.l2_h10@lagna", "place.l5_h10@lagna",
                                                              "place.sun_h10@lagna"}
    assert [r["finding_id"] for r in other_placements(timed, "career")][:2] == ["place.mercury_h10@lagna",
                                                                                "place.l4_h10@lagna"]


def test_curious_prompt_folds_placements_into_the_chart_facts():
    from jyotish.narrate import system_prompt
    p = " ".join(system_prompt("curious").split())
    assert "a placement finding (a lord or a planet in a house, with its classical_effect when it has one) is one chart fact" in p
    assert "A finding with status draft is a placement fact only" in " ".join(system_prompt("astrologer").split())
    assert "never a sentence of its own" in p


def test_other_placements_reach_the_page(tmp_path):
    import json as _json
    from jyotish.cli import main
    out = tmp_path / "r"
    args = ["read", "--date", "2001-03-12", "--time", "10:10:25", "--tz", "Asia/Kolkata", "--lat", "28.1989",
            "--lon", "76.617", "--node", "mean", "--depth", "astrologer", "--question", "How will my career go?",
            "--as-of", "2026-10-21", "--out", str(out),
            "--model-fixture", str(ROOT / "tests" / "fixtures" / "narration_career_edited.json")]
    with pytest.raises(SystemExit):
        main(args)
    reading = _json.loads(out.with_suffix(".json").read_text())
    career = next(a for a in reading["areas"] if a["name"] == "career")
    assert [o["rule_id"] for o in career["other_placements"]][:1] == ["place.mercury_h10"]
    md = out.with_suffix(".md").read_text()
    assert "Other placements the engine weighed (not narrated; the three strongest are above):" in md
    assert "- `place.mercury_h10` (Mercury, scale 1; draft effect, verse not yet read):" in md


def test_learner_panel_shows_the_draft_effect_marked(timed):
    from jyotish.narrate import findings, learner_data
    from jyotish.page import _rule_learner
    f = next(x for x in findings(timed, "career")[0] if x["finding_id"] == "place.l2_h10@lagna")
    d = learner_data(f)
    assert d["effect_status"] == "draft effect, verse not yet read" and d["effect"].startswith("The 2nd lord in the 10th")
    assert "Effect line (draft effect, verse not yet read): The 2nd lord in the 10th" in "\n".join(_rule_learner(d))



# --- draft status (SPEC Layer 3): no weight until a named reader promotes the row -------------

def test_a_draft_fire_never_changes_a_score(timed):
    from jyotish.chart import compute
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    yogas = [r for r in load_rules() if not r.id.startswith("place.")]
    bare = compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False, rules=yogas)
    assert sum(1 for f in timed.fired_rules if f.status == "draft") == 21          # they fire and are recorded
    for n, a in timed.scored.areas.items():
        b = bare.scored.areas[n]
        assert (a.score_classical, a.tier, a.terms) == (b.score_classical, b.tier, b.terms), n
    assert timed.scored.driver.ranking == bare.scored.driver.ranking


def _promote(tmp_path, rid, **cols):
    """Copy the table with one row filled, regenerate into a scratch library, load it."""
    import csv as _csv
    lib = tmp_path / "rules"
    lib.mkdir()
    shutil.copy(RULES_DIR / "rule.schema.json", lib)
    for f in RULES_DIR.glob("yoga.*.yaml"):
        shutil.copy(f, lib)
    rows = list(_csv.DictReader((ROOT / "scripts" / "placements.csv").open(newline="")))
    for r in rows:
        if r["id"] == rid:
            r.update(cols)
    table = tmp_path / "placements.csv"
    with table.open("w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    gen = _generator(lib)
    gen.TABLE = table
    gen.main()
    return load_rules(lib)


READ = {"verse": "24.79", "verse_read_by": "Test Reader", "verse_read_on": "2026-10-22", "effect_confirmed": "yes"}


def test_a_promoted_row_becomes_a_scored_rule(tmp_path, timed):
    from jyotish.chart import compute
    from jyotish.narrate import _check_data, findings
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    rules = _promote(tmp_path, "place.l7_h7", **READ)
    rule = next(r for r in rules if r.id == "place.l7_h7")
    assert rule.data["status"] == "classical_unconfirmed"
    assert rule.data["source"][0] | {} == {"text": "BPHS", "edition": "Santhanam 1984", "chapter": 24, "verse": "24.79",
                                         "checked": True, "read_by": "Test Reader", "read_on": "2026-10-22"}
    assert sum(r.data["status"] == "draft" for r in rules if r.id.startswith("place.")) == 251
    c = compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False, rules=rules)
    fire = next(f for f in c.fired_rules if f.id == "place.l7_h7")
    # It now weighs in the rule term: marriage gains exactly 0.3 x its relationships/commerce themes.
    delta = c.scored.areas["marriage"].terms["rules"] - timed.scored.areas["marriage"].terms["rules"]
    assert delta == pytest.approx(0.3 * sum(v for th, v in fire.themes.items() if th in ("relationships",)))
    assert delta > 0
    # And a reading may state its effect: the finding carries the classical effect, read.
    f = next(x for x in findings(c, "marriage")[0] if x["finding_id"] == "place.l7_h7@lagna")
    assert _check_data(f)["classical_effect"].startswith("The 7th lord in its own house") and "status" not in f


@pytest.mark.parametrize("cols,expect", [
    ({**READ, "effect_confirmed": "no"}, "draft"),                         # the verse does not support it
    ({**READ, "verse_read_by": ""}, "draft"),                              # no named reader
    ({**READ, "verse_read_on": ""}, "draft"),
    ({**READ, "effect_confirmed": ""}, "draft"),
    ({**READ, "effect_confirmed": "changed", "narration_key": "Rewritten after reading."}, "classical_unconfirmed"),
])
def test_promotion_needs_reader_date_and_verdict(tmp_path, cols, expect):
    rules = _promote(tmp_path, "place.l7_h7", **cols)
    rule = next(r for r in rules if r.id == "place.l7_h7")
    assert rule.data["status"] == expect
    assert rule.data["source"][0]["checked"] is (expect == "classical_unconfirmed")


@pytest.mark.parametrize("cols,message", [
    ({**READ, "verse": "not yet located"}, "the verse is not named"),
    ({**READ, "effect_confirmed": "maybe"}, "yes, no or changed"),
    ({**READ, "verse_read_on": "22 Oct"}, "YYYY-MM-DD"),
])
def test_promotion_refuses_an_incomplete_reading(tmp_path, cols, message):
    with pytest.raises(ValueError, match=message):
        _promote(tmp_path, "place.l7_h7", **cols)


def test_triage_sheet_is_the_table_and_merges_back(tmp_path):
    import csv as _csv
    sheet = list(_csv.DictReader((ROOT / "scripts" / "placements_triage.csv").open(newline="")))
    assert [r["id"] for r in sheet] == [r["id"] for r in TABLE]
    assert list(sheet[0]) == ["id", "placement", "draft_effect", "verse_reference", "verse_read_by", "verse_read_on",
                              "effect_confirmed", "practitioner_note"]
    row = {r["id"]: r for r in sheet}
    assert row["place.l10_h1"]["placement"] == "the lord of the 10th in the 1st"
    assert row["place.saturn_h1"]["placement"] == "Saturn in the 1st" and row["place.sun_h1"]["placement"] == "the Sun in the 1st"
    assert row["place.l10_h1"]["verse_reference"] == ("BPHS (Santhanam 1984), chapter 24, the lord of the 10th in the 1st "
                                                       "(verse not yet located)")
    assert all(not r[c] for r in sheet for c in ("verse_read_by", "verse_read_on", "effect_confirmed", "practitioner_note"))
    # Merge: a filled sheet row (with a rewritten effect) lands in the table.
    gen = _generator()
    gen.TABLE, gen.TRIAGE = tmp_path / "t.csv", tmp_path / "s.csv"
    shutil.copy(ROOT / "scripts" / "placements.csv", gen.TABLE)
    shutil.copy(ROOT / "scripts" / "placements_triage.csv", gen.TRIAGE)
    sheet[0].update(verse_read_by="A. Reader", verse_read_on="2026-10-23", effect_confirmed="changed",
                    draft_effect="My reading of the verse.", practitioner_note="BPHS 24.3")
    with gen.TRIAGE.open("w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=list(sheet[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sheet)
    gen.merge_triage()
    merged = next(r for r in _csv.DictReader(gen.TABLE.open(newline="")) if r["id"] == sheet[0]["id"])
    assert (merged["verse_read_by"], merged["effect_confirmed"], merged["narration_key"]) == \
        ("A. Reader", "changed", "My reading of the verse.")
    # Re-writing the sheet keeps what was filled.
    gen.write_triage()
    again = next(r for r in _csv.DictReader(gen.TRIAGE.open(newline="")) if r["id"] == sheet[0]["id"])
    assert again["verse_read_by"] == "A. Reader" and again["practitioner_note"] == "BPHS 24.3"


def test_triage_guide_exists():
    text = (ROOT / "docs" / "triage.md").read_text()
    for needle in ("Santhanam (1984), chapter 24", "Sastri (1937), chapter 8", "verse_read_by", "effect_confirmed",
                   "--merge-triage", "never copy the"):
        assert needle in text, needle
