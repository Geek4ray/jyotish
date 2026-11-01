"""The engine's own answer to a turn (SPEC Layer 8, 2026-11-01; narrate.engine_reading): no model,
deterministic, in plain words with no figures, each sentence footnoted to the area's technical sheet. Its text
on the reference chart is frozen here for the career question and for "what are the challanges in my life":
a change to it is a change to what the astrologer reads and to the client's fallback, made on purpose."""

import re
from datetime import date

import pytest

from jyotish.client import CLIENT_WORDS
from jyotish.narrate import engine_reading, with_sheets, instant_reading
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
CAREER_Q = "How will my career go, and when is the best time for a job change?"
CHALLENGES_Q = "what are the challanges in my life"

CAREER = [
    "For your career, the chart's indications are moderately supportive.",
    "Taken together, the houses that govern your career lean favourably, though the main one, the 10th house from "
    "your rising sign, in Aquarius, is one of the weakest of your twelve houses.",
    "The planets that rule the houses of your career lean favourably; Saturn, which rules the 10th house, sits in "
    "Taurus in your 1st house, in a friendly sign.",
    "The planets that signify your career lean favourably; the main one, the Sun, sits in Aquarius in your 10th "
    "house, in an unfriendly sign.",
    "The divisional chart for your career (D10) leans favourably; there Mars falls in Capricorn, exalted, where it "
    "is at its strongest.",
    "The rulers of the day you were born, Mars and the Moon, lean favourably for your career.",
    "The stretch the chart scores most favourable for your career runs from October 2029 to June 2032.",
    "The stretch it scores least favourable runs from November 2028 to August 2029.",
    "These are the chart's scores, and neither stretch is a prediction of when you will act.",
]
CHALLENGES = [
    "This chart does not emphasise your father.",
    "Taken together, the houses that govern your father lean unfavourably: the main one, the 9th house from your "
    "rising sign, in Capricorn, is one of the weakest of your twelve houses.",
    "The planets that signify your father lean unfavourably; the main one, the Sun, sits in Aquarius in your 10th "
    "house, in an unfriendly sign.",
    "The divisional chart for your father (D12) leans unfavourably; there Mars falls in Gemini, in an unfriendly sign.",
    "This chart does not emphasise children.",
    "The planets that signify children lean unfavourably; the main one, Jupiter, sits in Taurus in your 1st house, "
    "in an unfriendly sign.",
    "The divisional chart for children (D7) leans unfavourably; there Jupiter falls in Capricorn, debilitated, where "
    "it is at its weakest.",
    "This chart does not emphasise gains and friendships.",
    "The planets that signify gains and friendships lean unfavourably; the main one, Jupiter, sits in Taurus in your "
    "1st house, in an unfriendly sign.",
    "The divisional chart for gains and friendships (D11) leans unfavourably; there Jupiter falls in Capricorn, "
    "debilitated, where it is at its weakest.",
]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def career(chart):
    return engine_reading(chart, CAREER_Q, "for", ["career"], as_of=AS_OF, when=True)


@pytest.fixture(scope="module")
def challenges(chart):
    return engine_reading(chart, CHALLENGES_Q, "against", ["father", "children", "gains"], as_of=AS_OF)


def test_the_career_answer_is_frozen(career):
    assert [s.text for s in career.sentences] == CAREER


def test_the_challenges_answer_is_frozen_and_says_only_what_is_against(challenges):
    assert [s.text for s in challenges.sentences] == CHALLENGES
    assert "favourably;" not in challenges.text.replace("unfavourably", "")


def test_it_is_deterministic(chart, career):
    again = engine_reading(chart, CAREER_Q, "for", ["career"], as_of=AS_OF, when=True)
    assert again.model_dump() == career.model_dump()


@pytest.mark.parametrize("which", ["career", "challenges"])
def test_every_sentence_is_footnoted_to_the_sheet_and_the_note_quotes_it(chart, which, request):
    ans = request.getfixturevalue(which)
    sheets = {a.name: a.sheet for a in with_sheets(
        instant_reading(chart, ans.question, as_of=AS_OF, areas=ans.areas).areas, chart, AS_OF)}
    for s in ans.sentences:
        assert s.notes, s.text
        for n in s.notes:
            point = next(p for p in sheets[n["area"]]["points"] if p["n"] == n["point"])
            if "row" in n:
                row = next(r for r in point["table"]["rows"] if r["family"] == n["row"])
                assert n["text"] == f"{row['vote']} — {row['rests on']}"
            else:
                assert n["text"] == point["items"][n["item"]]["text"]
    md = ans.footnoted()
    assert md.count("[^1]:") == 1 and "sheet, point" in md


@pytest.mark.parametrize("which", ["career", "challenges"])
def test_it_is_in_plain_words_with_no_figures(which, request):
    text = request.getfixturevalue(which).text
    assert not CLIENT_WORDS.search(text)
    # The only digits are house ordinals, a divisional chart's name and the years of a month.
    rest = re.sub(r"\b\d{1,2}(?:st|nd|rd|th)\b|\(D\d{1,2}\)|\b(?:19|20)\d{2}\b", "", text)
    assert not re.search(r"\d", rest), rest


def test_a_hard_question_puts_the_least_favourable_stretch_first(chart):
    ans = engine_reading(chart, "when will career be difficult?", "against", ["career"], as_of=AS_OF, when=True)
    texts = [s.text for s in ans.sentences]
    least = next(i for i, t in enumerate(texts) if "least favourable" in t)
    assert least < next(i for i, t in enumerate(texts) if "most favourable" in t)
    assert not any("leans favourably" in t or "lean favourably" in t for t in texts)


def test_both_directions_say_for_then_against_and_a_bad_direction_is_refused(chart):
    ans = engine_reading(chart, "tell me about marriage", "both", ["marriage"], as_of=AS_OF)
    texts = [s.text for s in ans.sentences]
    fav = [i for i, t in enumerate(texts) if re.search(r"\blean(?:s)? favourably", t)]
    unfav = [i for i, t in enumerate(texts) if "unfavourably" in t]
    assert fav and unfav and max(fav) < min(unfav)
    with pytest.raises(ValueError):
        engine_reading(chart, "x", "sideways", ["marriage"], as_of=AS_OF)


def test_an_area_with_no_sheet_says_so_plainly(chart):
    ans = engine_reading(chart, "are we a match?", "both", ["synastry"], as_of=AS_OF)
    assert [s.text for s in ans.sentences] == ["A match between two charts needs a second person's chart to be read."]
