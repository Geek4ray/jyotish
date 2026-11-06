"""Ray's first use of the live chat (2026-11-02; "how much money will i earn in my life, will i be rich", then
"whan and how"), each fix's test (docs/spec_notes_2026-11-02.md): the writer's material in plain words only, the
never-show list as refusals, "when", "why" and "how" read with the same spelling tolerance as area words, and the
question answered as asked."""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import Route, _material, route_turn
from jyotish.narrate import engine_reading
from jyotish.scoring import AREAS
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 2)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]
MONEY = "how much money will i earn in my life, will i be rich"


def _chart(b):
    return assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)


@pytest.fixture(scope="module")
def charts():
    return {b["name"]: _chart(b) for b in BIRTHS}


@pytest.fixture(scope="module")
def chart(charts):
    return charts["reference"]


def as_of(b) -> date:
    born = datetime.fromisoformat(b["utc"]).date()
    return AS_OF if born < AS_OF else born.replace(year=born.year + 30)


def material(chart, message, route, when=AS_OF):
    engine = engine_reading(chart, message, "both" if route.why else route.direction, route.areas, as_of=when,
                            when=route.when, weakest=route.areas_from == "weakest" and not route.why)
    return _material(chart, message, route, engine, [], when)


# --- 1. the writer's material is plain words only -------------------------------------------------------------------

# A label the writer copied back to the client, or engine vocabulary: none is in what the writer is given. "for" and
# "against" are refused as labels (a value, "is for", "are against"); "works against" is the material's own lean word.
LABELS = re.compile(r"\bvotes?\b|\bfamil(?:y|ies)\b|\btiers?\b|\bmarked as\b|\bindications?\b|\bverdict\b|"
                    r"\bderivation\b|\bglossary\b|\bfinding_id\b|\bscores?\b|\bKP\b|\bKrishnamurti\b|\bD\d{1,2}\b|"
                    r"\barudha|\bdasha|\bcusp|\bsub-?lord|\bShadbala|\bBhava Bala|\bkaraka|\blagna\b|"
                    r"\"(?:for|against)\"|\b(?:is|are) (?:for|against)\b|(?<!work )(?<!works )\bagainst\b", re.I)


@pytest.mark.parametrize("name", [b["name"] for b in BIRTHS])
def test_1_the_writers_material_carries_no_label_on_any_area_or_direction(charts, name):
    chart = charts[name]
    when = as_of(next(b for b in BIRTHS if b["name"] == name))
    for area in AREAS:
        if area == "synastry":
            continue
        for direction in ("against", "for", "both"):
            user = material(chart, "q", Route(areas=[area], direction=direction), when)[0]
            m = LABELS.search(user)
            assert m is None, (name, area, direction, m.group(0), user[max(0, m.start() - 80):m.end() + 40])


def test_1_the_material_is_the_engines_answer_and_one_plain_sentence_per_finding(chart):
    user, finding_data, tags, votes, chains, handles = material(chart, MONEY, route_turn(MONEY, chart))
    body = json.loads(user)
    assert set(body) == {"message", "asked_about", "asks_when", "asks_why", "earlier_turns", "engine_answer", "areas"}
    assert body["asked_about"] == "the good and the hard"
    (area,) = body["areas"]
    assert area["area"] == "money" and all(set(f) == {"tag", "says"} for f in area["findings"])
    says = {f["tag"]: f["says"] for f in area["findings"]}
    # Each finding's tag is a handle for its own tag; the engine's sentences cite the same handles.
    assert all(re.fullmatch(r"f\d+", t) for t in says) and set(handles.real) >= set(says)
    assert {handles.real[t] for t in says} <= tags
    assert all(re.fullmatch(r"f\d+", t) for s in body["engine_answer"] for t in s["tags"])
    # Frozen: which way each finding leans, in the material's own words.
    assert "The signs that show how others see money, Libra and Cancer, work against it: the Moon sits there, with " \
           "no helpful planet beside." in says.values()
    assert "Taken together, the houses that govern money support it: the main one, the 2nd house from your rising " \
           "sign, in Gemini, is better supported than most of your twelve houses." in says.values()
    assert "Jupiter and Venus form the Parivartana yoga, which is an exchange of signs: two planets each sitting in " \
           "the sign the other rules, joining the 1st and 11th houses; it supports money." in says.values()
    assert "Mercury, the ruler of the 2nd house, sits in the 10th house; the 2nd is a house of money; it is a " \
           "placement only, with no lean of its own." in says.values()
    assert len(user) < 6000                            # 45,053 characters before (the findings' whole data)


def test_1_a_handle_is_put_back_to_its_findings_tag_before_the_checks(chart):
    *_, handles = material(chart, MONEY, route_turn(MONEY, chart))
    h = handles.of["vote:wealth.house"]
    assert handles.to_real(f"Your money houses are well placed [{h}].") == "Your money houses are well placed " \
                                                                         "[vote:wealth.house]."
    two = handles.of["rule:yoga.parivartana"]
    assert handles.to_real(f"Two planets trade places [{h}, {two}].").endswith(
        "[vote:wealth.house] [rule:yoga.parivartana].")
    assert handles.to_real("A made-up one [f999].") == "A made-up one [f999]."           # refused as not offered
    assert handles.to_handles("tag not offered for this finding: [vote:wealth.house]") == \
        f"tag not offered for this finding: [{h}]"


def test_1_a_turn_cites_handles_and_is_checked_against_the_real_findings(chart):
    from jyotish.conversation import OfflineTurnWriter, answer_turn
    from jyotish.narrate import CheckResult, Proposition
    seen = []

    def checker(sentence, data):
        seen.append(data)
        return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])
    route = route_turn(MONEY, chart)
    doc = answer_turn(chart, MONEY, route, as_of=AS_OF, drafter=OfflineTurnWriter(), checker=checker)
    assert doc["source"] == "writer" and doc["accepted"]
    assert all("[f" not in s for s in doc["accepted"]) and any("[vote:wealth.house]" in s for s in doc["accepted"])
    assert any('"family": "house"' in d for d in seen)         # the checker reads the finding's whole data
    assert not any("[" in s for s in doc["shown"])
