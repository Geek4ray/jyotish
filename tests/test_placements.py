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
        assert d["status"] == "classical_unconfirmed" and d["confidence_base"] == 0.3 and d["school"] == "parashari"
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
