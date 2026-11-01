"""The independent review of chat v1 (docs/review_2026-11-01_chat.md), each finding's test, as SPEC Layer 8 (rev 130,
"Decided after the independent review") settles it."""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import OfflineTurnWriter, answer_turn, route_turn
from jyotish.narrate import CheckResult, Proposition, engine_reading
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 10, 21)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]


def _chart(b):
    return assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)


@pytest.fixture(scope="module")
def charts():
    return {b["name"]: _chart(b) for b in BIRTHS}


@pytest.fixture(scope="module")
def chart(charts):
    return charts["reference"]


def as_of(b) -> date:
    """The session's date for a birth: AS_OF, or thirty years after a synthetic birth drawn after it (synthetic-3,
    2036), since a conversation is about a life already begun."""
    born = datetime.fromisoformat(b["utc"]).date()
    return AS_OF if born < AS_OF else born.replace(year=born.year + 30)


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


def chips() -> list[str]:
    """Every chip the conversation page offers (web/js/strings.js, chat.chip.*)."""
    text = (ROOT / "web" / "js" / "strings.js").read_text()
    return re.findall(r'"chat\.chip\.[\w.]+":\s*"([^"]+)"', text)


def first_chips() -> list[str]:
    text = (ROOT / "web" / "js" / "strings.js").read_text()
    return re.findall(r'"chat\.chip\.first\.[\w.]+":\s*"([^"]+)"', text)


# --- C1: long life and health are never a default route, and no stretch about them reaches the client --------------

LONG_LIFE = re.compile(r"long life|longevity|lifespan|\bhealth\b|\blive\b", re.I)


def test_c1_a_chip_before_the_first_question_names_an_area():
    from jyotish.conversation import areas_of
    assert len(first_chips()) == 3
    for chip in first_chips():
        assert areas_of(chip), chip


@pytest.mark.parametrize("message", sorted(set(chips()) | {"when?", "why?", "what are my strengths"}))
def test_c1_no_first_turn_mentions_long_life_or_health(charts, message):
    for b in BIRTHS:
        name, chart = b["name"], charts[b["name"]]
        route = route_turn(message, chart)
        assert not {"longevity", "health"} & set(route.areas), (name, message, route.areas)
        if route.off_limits:
            continue
        doc = answer_turn(chart, message, route, as_of=as_of(b), drafter=OfflineTurnWriter(), checker=passes)
        said = doc["shown"] + [s["text"] for s in doc["engine"]["sentences"]]
        assert not [s for s in said if LONG_LIFE.search(s)], (name, message)


def test_c1_no_stretch_for_long_life_or_health_on_any_route(chart):
    ans = engine_reading(chart, "when will my health improve", "both", ["health", "longevity", "career"], as_of=AS_OF,
                         when=True)
    stretches = [s.text for s in ans.sentences if "stretch" in s.text]
    assert stretches and not [s for s in stretches if LONG_LIFE.search(s)]
    route = route_turn("when will my health improve", chart)
    assert route.areas == ["health"] and route.when
    doc = answer_turn(chart, "when will my health improve", route, as_of=AS_OF, drafter=OfflineTurnWriter(),
                      checker=passes)
    assert not [s for s in doc["shown"] if "stretch" in s]


# --- C2: distress is read first and widest, before a follow-up can carry anything ------------------------------------

DISTRESS_SET = [
    # the review's table
    "I can’t go on like this anymore", "I don’t want to live anymore", "I’d be better off dead",
    "mujhe marna hai, kuch accha nahi ho raha", "jeena nahi chahta ab", "I feel hopeless, nothing works",
    # the same with other apostrophes, case and spacing
    "I can't go on like this anymore", "I CAN‘T GO ON", "I dont want to live", "i do not want to be alive",
    "Id be better off dead", "everyone is better off without me", "I’m better off dead tbh",
    # their kin in English
    "there is no point living", "no point in living anymore", "what is the point of living, no point in life",
    "I have nothing to live for", "life is not worth living", "I’m so tired of living", "I want to end it all",
    "I'm going to end it", "I can’t take it anymore", "I wish I was never born", "I feel worthless",
    "I have been cutting myself", "I want to kill myself", "thinking about suicide",
    # Hinglish in Latin script
    "marna chahta hu", "main mar jaun to accha", "mar jana chahti hoon", "jeena nahi chahti", "jeene ka mann nahi karta",
    "zindagi khatam kar dunga", "khudkushi ke baare mein soch raha hoon", "aatmahatya", "atmahatya kar lunga",
    "apni jaan de dunga", "koi umeed nahi bachi",
    # Hindi in Devanagari
    "मुझे मरना है", "मैं मर जाऊं", "अब जीना नहीं चाहता", "जीने का मन नहीं करता", "आत्महत्या के बारे में सोच रहा हूँ",
    "खुदकुशी कर लूँ", "ज़िंदगी खत्म कर दूँ", "कोई उम्मीद नहीं है",
]


@pytest.mark.parametrize("message", DISTRESS_SET)
def test_c2_every_distress_message_reaches_the_helpline_cold_and_after_a_turn(chart, message):
    from jyotish.conversation import fixed_reply
    challenges = route_turn("what are the challanges in my life", chart)
    for last in (None, challenges):
        route = route_turn(message, chart, last)
        assert route.off_limits == "distress", (message, last is not None)
        assert not route.follow_up and not route.carried and not route.areas
        doc = answer_turn(chart, message, route, as_of=AS_OF)
        assert doc["source"] == "fixed" and doc["shown"] == [fixed_reply("distress")]
        assert "14416" in doc["shown"][0] and "112" in doc["shown"][0]


@pytest.mark.parametrize("message", ["how is my career", "when will I marry", "tell me about my life",
                                     "meri shaadi kab hogi", "I am a marine engineer", "is my marriage hopeful?"])
def test_c2_ordinary_messages_are_not_distress(chart, message):
    assert route_turn(message, chart).off_limits != "distress"
