"""The layered answer (SPEC Layer 8 rev 134, "The layered answer"; docs/spec_notes_2026-11-15.md): the answer plan,
the sentence bank, the composer, the polisher, the worksheet and the stored answer, each step's tests, on the
reference chart first."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import plan_turn, route_turn
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 15)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def data(chart):
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    return cached_payload(chart, AS_OF, *full_range(AS_OF), [a for a in chart.scored.areas if a != "synastry"])


@pytest.fixture(scope="module")
def charts(chart):
    out = {"reference": chart}
    for b in BIRTHS:
        if b["name"] != "reference":
            out[b["name"]] = assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)
    return out


def career(chart, data=None, message="how is my career"):
    return plan_turn(chart, message, route_turn(message, chart), as_of=AS_OF, data=data)


# --- 1. The answer plan ------------------------------------------------------------------------------------------------

def test_1_the_career_plan_holds_the_yogas_with_their_reductions_and_saturns_hidden_weakness(chart, data):
    """The sample worksheet of 2026-11-15 (career, the reference chart): three fired yogas never reached the client,
    and the tenth lord's marana karaka sthana was told as "a friendly sign"."""
    p = career(chart, data)
    sig = p.signatures()
    assert "rule.yoga.budhaditya.reduced" in sig                   # Mercury in a feeble state (bala/mrita) reduces it
    assert "rule.yoga.kendra_trikona_raja.full" in sig
    ruchaka = next(i for i in p.items if i.signature.startswith("rule.yoga.ruchaka"))
    assert ruchaka.signature == "rule.yoga.ruchaka.reduced"
    assert ruchaka.slots["reductions"] == ("Saturn's aspect on it, an unhelpful star counted from your Moon and a "
                                           "house that drains it")
    mks = next(i for i in p.items if i.signature == "weakness.mks")
    assert mks.facts["planet"] == "Saturn" and mks.facts["house"] == 1 and mks.slots["role"] == "the ruler of your 10th house"
    assert "drains" in mks.engine and "friendly" not in mks.engine
    assert {i.signature for i in p.items if i.facts.get("planet") == "Saturn"} == {
        "weakness.mks", "weakness.mrita", "weakness.low_strength"}     # ratio 0.69, Mrita, 1st house


def test_1_the_plan_is_in_order_helps_by_the_strongest_terms_and_says_what_it_left_out(chart, data):
    p = career(chart, data)
    order = [i.part for i in p.items]
    from jyotish.plan import PARTS
    assert order == sorted(order, key=PARTS.index)
    helps = [i for i in p.items if i.part == "helps"]
    terms = chart.scored.areas["career"].terms
    assert 2 <= len(helps) <= 3 and [i.facts["strength"] for i in helps] == sorted((i.facts["strength"] for i in helps), reverse=True)
    assert min(i.facts["term"] for i in helps) >= max(terms[f] for f in ("varga", "panchanga"))
    left = {x["what"]: x["why"] for x in p.left_out}
    assert left["vote:career.varga"].startswith("a weaker term") and left["vote:career.kp"] == "abstains"
    assert left["place.sun_h10@lagna"].startswith("a draft placement")
    assert left["chain:career.lord"].startswith("a chain")
    assert p.items[-1].signature == "period.now.touches" and p.items[-1].slots["maha"] == "Jupiter"


def test_1_a_when_turn_ends_with_the_stretches_and_the_plan_is_the_same_without_the_payload(chart, data):
    m = "when will my career rise"
    p = plan_turn(chart, m, route_turn(m, chart), as_of=AS_OF, data=data)
    assert p.signatures()[-3:] == ["stretch.most.first", "stretch.least.second", "stretch.caveat.two"]
    assert p.items[-1].engine == "Neither stretch is a prediction of when you will act."
    assert "opening.when" in p.signatures()
    # The chart object alone gives the same items (the coverage tool's path), without notes or stretch texts.
    assert career(chart).signatures() == career(chart, data).signatures()
    assert [i.engine for i in career(chart).items] == [i.engine for i in career(chart, data).items]


def test_1_hard_findings_come_by_the_most_negative_term(charts, data):
    found = 0
    for name, c in charts.items():
        for area in c.scored.areas:
            if area == "synastry" or c.scored.areas[area].score_classical is None:
                continue
            p = plan_turn(c, "tell me", route_turn(f"how is my {area.replace('_', ' ')}", c).model_copy(
                update={"areas": [area]}), as_of=AS_OF)
            hard = [i for i in p.items if i.part == "hard"]
            assert len(hard) <= 2 and len([i for i in p.items if i.part == "helps"]) <= 3
            assert [i.facts["strength"] for i in hard] == sorted(i.facts["strength"] for i in hard)
            found += len(hard)
    assert found


def test_1_every_engine_sentence_of_a_plan_passes_the_never_show_list(charts):
    """An item with no bank row falls back to its engine sentence (step 4): every one is in the client's words."""
    from jyotish.client import never_show
    for name, c in charts.items():
        areas = [a for a in c.scored.areas if a != "synastry"]
        p = plan_turn(c, "how much will i earn", route_turn("how is my career", c).model_copy(update={"areas": areas}),
                      as_of=AS_OF)
        for i in p.items:
            assert never_show(i.engine) == [], (name, i.signature, i.engine)


def test_1_a_reduction_with_no_plain_words_keeps_the_rule_out_and_says_so():
    from jyotish.plan import reductions_plain
    assert reductions_plain(["marana_karaka_sthana -> x0.6", "aspected_by: [Saturn] -> x0.8"]) == (
        ["a house that drains it", "Saturn's aspect on it"], [])
    assert reductions_plain(["kp_sub_lord in [6, 8] -> x0.7"]) == ([], ["kp_sub_lord in [6, 8]"])
    assert reductions_plain(["dignity: friend -> x1.1"]) == ([], [])          # a boost is not a reduction
