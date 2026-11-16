"""The shaped answer (SPEC Layer 8 rev 136, "The shaped answer (decided 2026-11-16)"; docs/spec_notes_2026-11-16.md):
parts in the order asked, the eight-sentence shape, the vocation ask, a change of job, the client's page, the draft
meanings flag. Each decision's tests are under its number, on the reference chart first.

The failing case is frozen first (tests/fixtures/shaped_three_parts.json): the three-part question Ray asked on the
deployed service on 2026-11-16 and the two single questions inside it, composed on the reference chart as of that day,
with draft meanings off and on. Each decision's commit re-records it (JYOTISH_RECORD_FIXTURE=1), so its diff shows
what the decision changed in the answer; a change is read, not only recorded."""

import json
import os
from datetime import date
from pathlib import Path

import pytest

from jyotish.conversation import route_turn
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 16)
THREE = ["How will my career go, which field will i work in, when will i leave my current job",
         "which field will i work in", "when will i leave my current job"]
FROZEN = ROOT / "tests" / "fixtures" / "shaped_three_parts.json"


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def three_answers(chart, monkeypatch, draft: bool) -> list[dict]:
    """Each of THREE composed on the reference chart as of 2026-11-16 (variant 0 of every row, so a bank's variants
    do not move the frozen text), or its route where the composer does not answer it."""
    import jyotish.conversation as conv
    from jyotish.conversation import answer_turn, composes, kinds_of
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_SHOW_DRAFT_MEANINGS", "1" if draft else "0")
    monkeypatch.setattr(conv, "variant_of", lambda key, signature: 0)
    out = []
    for m in THREE:
        route = route_turn(m, chart)
        got = {"question": m, "areas": route.areas, "areas_from": route.areas_from, "kinds": kinds_of(m, route),
               "composes": composes(route)}
        if got["composes"]:
            doc = answer_turn(chart, m, route, as_of=AS_OF, session_key="three")
            got |= {"source": doc["source"], "sentences": len(doc["shown"]), "shown": doc["shown"],
                    "paragraphs": doc["paragraphs"]}
        out.append(got)
    return out


def test_0_the_three_part_question_and_its_two_parts_are_frozen(chart, monkeypatch):
    """The failing case (the module docstring), with draft meanings off and on, against the committed bank."""
    from jyotish.bank import default_bank
    got = {"as_of": AS_OF.isoformat(), "bank": default_bank().version,
           "draft_off": three_answers(chart, monkeypatch, draft=False),
           "draft_on": three_answers(chart, monkeypatch, draft=True)}
    if os.environ.get("JYOTISH_RECORD_FIXTURE"):
        FROZEN.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n")
    assert got == json.loads(FROZEN.read_text())


# --- 1. Parts -----------------------------------------------------------------------------------------------------

def test_1_the_three_part_question_is_three_asks_in_order(chart):
    from jyotish.conversation import parts_of
    parts = parts_of(THREE[0])
    assert [p.kind for p in parts] == ["goes", "vocation", "change"]
    assert route_turn(THREE[0], chart).parts[0] == {"kind": "goes", "areas": ["career"]}


@pytest.mark.parametrize("message,kind", [
    ("will i marry", "yes_no"), ("can i get a promotion", "yes_no"), ("should i study abroad", "yes_no"),
    ("is my marriage going to last", "yes_no"), ("do i have luck in money", "yes_no"),
    ("kya meri shaadi hogi", "yes_no"), ("meri naukri lagegi ya nahi, hogi", "yes_no"),
    ("how will my career go", "goes"), ("which job suits me", "goes"), ("how is my marriage", "goes"),
    ("when will i marry", "when"), ("why is my career slow", "why"), ("how much will i earn", "amount"),
    ("which field will i work in", "vocation"), ("when will i leave my current job", "change")])
def test_1_a_part_is_yes_or_no_only_when_it_opens_on_an_auxiliary(message, kind):
    from jyotish.conversation import kind_of
    assert kind_of(message) == kind


@pytest.mark.parametrize("message,kinds", [
    ("whan and how", ["when", "why"]), ("how is my career and marriage", ["goes"]),
    ("will I marry, and when?", ["yes_no", "when"]), ("when will I marry and how is my career", ["when", "goes"]),
    ("hi, how is my career", ["goes", "goes"])])
def test_1_a_message_splits_at_its_asks_never_inside_a_list_of_areas(message, kinds):
    from jyotish.conversation import parts_of
    assert [p.kind for p in parts_of(message)] == kinds


def compose_for(chart, message, monkeypatch, last=None, **kw):
    import jyotish.conversation as conv
    from jyotish.conversation import compose, plan_turn
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    monkeypatch.setattr(conv, "variant_of", lambda key, signature: 0)
    route = route_turn(message, chart, last)
    data = cached_payload(chart, AS_OF, *full_range(AS_OF), list(route.areas))
    return compose(plan_turn(chart, message, route, as_of=AS_OF, data=data), session_key="s", **kw)


def test_1_one_line_of_what_a_chart_cannot_give_for_every_part_that_needs_it(chart, monkeypatch):
    c = compose_for(chart, "will I marry, and when?", monkeypatch)
    openings = [s for s in c["sentences"] if s["part"] == "opening"]
    assert [s["signature"] for s in openings] == ["opening.yes_no.when"] and c["sentences"][0] is openings[0]
    # A question of how it goes needs none; a change of job's line is at its own part, after the career's lean.
    c = compose_for(chart, THREE[0], monkeypatch)
    openings = [s for s in c["sentences"] if s["part"] == "opening"]
    assert len(openings) == 1 and openings[0]["section"] == "timing" and c["sentences"][0]["part"] == "verdict"


def test_1_the_parts_are_answered_in_the_order_asked(chart, monkeypatch):
    c = compose_for(chart, "when will I marry and how is my career", monkeypatch)
    assert c["sections"] == ["timing", "general"]
    sections = [s["section"] for s in c["sentences"]]
    assert sections == sorted(sections, key=["timing", "general"].index)
    timing = [s for s in c["sentences"] if s["section"] == "timing"]
    assert {s["area"] for s in timing if s["part"] in ("verdict", "stretch")} == {"marriage"}
    assert {s["area"] for s in c["sentences"] if s["section"] == "general"} == {"career"}


# --- 2. Shape -----------------------------------------------------------------------------------------------------

ATTRIBUTION = __import__("re").compile(r"\b(?:tradition\w*|texts?)\b", __import__("re").I)


def facts_per_area(c) -> dict:
    """Facts (not meanings, not the cannot-give line, not a vocation section) per area, the period counted once."""
    n: dict = {}
    for s in c["sentences"]:
        if (s["row"] or {}).get("kind") == "meaning" or s["part"] == "opening" or s["section"] == "vocation":
            continue
        n[s["area"]] = n.get(s["area"], 0) + 1
    return n


@pytest.mark.parametrize("message", ["how is my career", "how is my marriage", "will I be rich",
                                     "what is hard in my career", "how is my career, and when will it rise",
                                     THREE[0], THREE[2]])
def test_2_one_area_is_at_most_eight_sentences_on_the_reference_chart(chart, monkeypatch, message):
    from jyotish.conversation import SHAPE
    for draft in (False, True):
        c = compose_for(chart, message, monkeypatch, draft_meanings=draft)
        assert all(v <= SHAPE for v in facts_per_area(c).values()), [s["text"] for s in c["sentences"]]
        assert c["held"] or message == THREE[2]           # the rest is held for "tell me more"


def test_2_what_is_hard_is_one_sentence_per_planet(chart, monkeypatch):
    c = compose_for(chart, "how is my career", monkeypatch)
    weak = [s for s in c["sentences"] if s["part"] == "weakness"]
    assert [s["text"].split(",")[1].strip() for s in weak] == ["Saturn", "the Sun"]
    saturn = weak[0]["text"]
    assert "drains it" in saturn and "feeble state" in saturn and "less strength" in saturn
    assert not any("whatever the sign" in s["text"] or "no matter what" in s["text"] for s in c["sentences"])


def test_2_no_bank_row_says_what_a_sign_says():
    """The row that composed "no matter what Taurus says" is gone with the per-kind weakness rows."""
    from jyotish.bank import load_bank
    assert not [v for r in load_bank().rows for v in r.variants if " says" in v and "{sign}" in v]
    assert not [r.signature for r in load_bank().rows if r.base in ("weakness.mks", "weakness.mrita",
                                                                    "weakness.low_strength")]


def test_2_a_meaning_follows_its_fact_and_a_paragraph_attributes_to_the_tradition_once(chart, monkeypatch):
    for message in ("how is my career", "how is my marriage", "will I be rich", THREE[0], "tell me about my money"):
        c = compose_for(chart, message, monkeypatch, draft_meanings=True)
        ss, paras = c["sentences"], c["paragraphs"] + [len(c["sentences"])]
        for i, s in enumerate(ss):
            if (s["row"] or {}).get("kind") == "meaning":
                assert i > 0 and ss[i - 1]["item"] == s["item"] and (ss[i - 1]["row"] or {}).get("kind") != "meaning"
        for a, b in zip(paras, paras[1:]):
            assert sum(len(ATTRIBUTION.findall(s["text"])) > 0 for s in ss[a:b]) <= 1, [s["text"] for s in ss[a:b]]


def test_2_tell_me_more_gives_what_the_shape_held_and_repeats_nothing(chart, monkeypatch):
    from jyotish.conversation import said_keys_of
    first = compose_for(chart, "how is my career", monkeypatch)
    more = compose_for(chart, "tell me more", monkeypatch, last=route_turn("how is my career", chart),
                       said_keys=said_keys_of({"composed": first}))
    keys = {s["key"] for s in first["sentences"]}
    assert more["sentences"] and not keys & {s["key"] for s in more["sentences"]}
    assert {s["key"] for s in more["sentences"]} <= {h["key"] for h in first["held"]}
    assert any(s["part"] == "rule" for s in more["sentences"])           # the yogas the first answer held


def test_2_over_random_charts_one_area_is_at_most_eight_sentences():
    """40 synthetic charts, every area asked how it goes (and when): the composer's shape holds on each."""
    import sys
    from datetime import datetime
    sys.path.insert(0, str(ROOT / "scripts"))
    from synthetic_cohort import births
    from jyotish.chart import compute
    from jyotish.conversation import SHAPE, compose
    from jyotish.plan import plan
    n = 0
    for b in births(40, 7):
        c = compute(datetime.fromisoformat(f"{b['date']}T{b['time']}"), b["lat"], b["lon"], true_node=False)
        for a in [x for x in c.scored.areas if x != "synastry"]:
            for when in (False, True):
                p = plan(c, "x", [a], "both", ["goes"], as_of=AS_OF, when=when,
                         parts=[{"kind": "goes", "areas": [a]}] + ([{"kind": "when", "areas": [a]}] if when else []))
                got = compose(p, session_key="r", draft_meanings=True)
                assert all(v <= SHAPE for v in facts_per_area(got).values())
                weak = [s["text"] for s in got["sentences"] if s["part"] == "weakness"]
                assert len(weak) == len(set(weak))
                n += 1
    assert n > 500


# --- 3. Vocation --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("message", [
    "which field will i work in", "what kind of work suits me", "which line should I go into", "business or job?",
    "which profession is good for me", "kaun sa field mere liye sahi hai", "naukri ya business", "kya kaam karunga",
    "मैं कौन सा काम करूंगा", "किस क्षेत्र में जाऊं"])
def test_3_which_field_is_career_with_the_ask_vocation(chart, message):
    from jyotish.conversation import composes, kinds_of
    route = route_turn(message, chart)
    assert route.areas == ["career"] and route.areas_from == "named" and composes(route)
    assert "vocation" in kinds_of(message, route)


def test_3_the_vocation_items_are_what_the_engine_computes_on_the_reference_chart(chart, monkeypatch):
    from jyotish.conversation import plan_turn
    p = plan_turn(chart, THREE[1], route_turn(THREE[1], chart), as_of=AS_OF)
    voc = [(i.signature, i.facts.get("planet") or i.facts.get("tenth_house_ruler")) for i in p.items if i.part == "vocation"]
    # The 10th is Aquarius ruled by Saturn (in Taurus, the 1st); the Sun and Mercury sit in it; the D10 holds Mars
    # exalted (Capricorn) and Saturn in its own sign (Capricorn).
    assert voc == [("vocation.tenth", "Saturn"), ("vocation.in_tenth", "Sun"), ("vocation.d10", "Mars"),
                   ("vocation.in_tenth", "Mercury"), ("vocation.d10", "Saturn")]
    tenth = next(i for i in p.items if i.signature == "vocation.tenth")
    assert tenth.facts | {"about": None} == {"tenth_house_sign": "Aquarius", "tenth_house_ruler": "Saturn",
                                              "ruler_sign": "Taurus", "ruler_house": 1, "about": None}
    # Nothing here weighs: no vote or rule tag, and no karmajiva item (its method was not read in a named edition).
    assert all(not i.tags for i in p.items if i.part == "vocation")
    assert not [i for i in p.items if "karmajiva" in i.signature]
    c = compose_for(chart, THREE[1], monkeypatch)
    assert [s["section"] for s in c["sentences"]] == ["vocation"] * 4         # at most four; Saturn's D10 held
    assert [h["signature"] for h in c["held"] if h["signature"].startswith("vocation.")] == ["vocation.d10"]
    on = compose_for(chart, THREE[1], monkeypatch, draft_meanings=True)
    meanings = [s["row"]["signature"] for s in on["sentences"] if s["row"]["kind"] == "meaning"]
    assert meanings == ["vocation.works.saturn@career", "vocation.works.sun@career", "vocation.works.mars@career",
                        "vocation.works.mercury@career"]                # each planet's kinds of work, once


def test_3_over_random_charts_a_vocation_item_states_only_the_chart():
    import sys
    from datetime import datetime
    sys.path.insert(0, str(ROOT / "scripts"))
    from synthetic_cohort import births
    from jyotish.chart import compute
    from jyotish.constants import SIGN_LORD, SIGNS
    from jyotish.plan import plan
    from jyotish.scoring import varga_dignity_word
    for b in births(60, 3):
        c = compute(datetime.fromisoformat(f"{b['date']}T{b['time']}"), b["lat"], b["lon"], true_node=False)
        p = plan(c, "x", ["career"], "both", ["vocation"], as_of=AS_OF, parts=[{"kind": "vocation", "areas": ["career"]}])
        tenth = (c.lagnas.asc_sign + 9) % 12
        for i in p.items:
            f = i.facts
            if i.signature == "vocation.tenth":
                assert f["tenth_house_sign"] == SIGNS[tenth] and f["tenth_house_ruler"] == SIGN_LORD[tenth]
                assert c.bodies[SIGN_LORD[tenth]].house == f["ruler_house"]
            elif i.signature == "vocation.in_tenth":
                assert c.bodies[f["planet"]].house == 10
            elif i.signature == "vocation.d10":
                assert varga_dignity_word(f["planet"], c.vargas["D10"][f["planet"]]) in ("own", "exalted")


def test_3_the_vocation_rows_are_drafts_checked_as_the_others_were():
    from jyotish.bank import load_bank
    rows = {r.signature: r for r in load_bank().rows if r.base.startswith("vocation.")}
    for sig in ("vocation.tenth", "vocation.in_tenth", "vocation.d10"):
        r = rows[sig]
        assert r.kind == "fact" and r.status == "draft" and {c.variant for c in r.checks} == {0, 1, 2}
        assert all(c.supported and c.model == "zai-org/GLM-5.3-Flash" for c in r.checks)
    planets = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    for p in planets:
        r = rows[f"vocation.works.{p}@career"]
        assert r.kind == "meaning" and r.status == "draft" and r.source.startswith("Brihat Jataka 10")
        assert "not yet read" in r.source                                 # the verse was not read: said so
