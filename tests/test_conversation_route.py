"""How a turn is read (SPEC Layer 8, 2026-11-01; jyotish.conversation): keyword routing tolerant of spelling,
no model; the direction; a bare follow-up carrying the last turn; the weakest areas for a question asking what
is against with no area; and the off-limits kinds with their fixed replies, logged by kind before any model call."""

import json
import logging

import pytest

from jyotish.conversation import (MINOR_AREAS, OFF_LIMITS, REPLIES, areas_of, direction_of, fixed_reply, is_minor,
                                  off_limits, route_turn, top_areas, weakest_areas)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.mark.parametrize("message,direction", [
    ("what are the challanges in my life", "against"), ("any obstacles at work?", "against"),
    ("what problems will I face", "against"), ("is marriage dificult for me", "against"),
    ("where do I struggle", "against"), ("my weaknesses", "against"), ("what are the risks", "against"),
    ("should I worry about money", "against"), ("what are my strenghts", "for"), ("is my career good", "for"),
    ("best time to marry", "for"), ("tell me about my career", None), ("my strengths and weaknesses", "both"),
])
def test_the_direction_of_a_message(message, direction):
    assert direction_of(message) == direction


@pytest.mark.parametrize("message,areas", [
    ("and marraige?", ["marriage"]), ("what about my carrer", ["career"]), ("I would rather know", []),
    ("money and my job", ["career", "wealth"]), ("is the house of my mother calm", ["mother_home"]),
])
def test_areas_tolerate_spelling_but_not_a_common_word(message, areas):
    assert sorted(areas_of(message)) == sorted(areas)


def test_a_question_against_with_no_area_goes_to_the_weakest_areas(chart):
    # Adverse direction first, then families against, then polarity flags, then tier (review H2). No area of the
    # reference chart is adverse; father, reputation and siblings have the most families against (three each).
    weak = weakest_areas(chart)
    assert weak == ["father", "reputation", "siblings"]
    against = {n: sum(1 for v in a.votes.values() if (getattr(v, "vote", v) or 0) < 0) for n, a in chart.scored.areas.items()}
    assert all(against[n] == 3 for n in weak) and max(against.values()) == 3
    assert not set(weak) & set(chart.scored.top)                   # never the strongest
    r = route_turn("what are the challanges in my life", chart)
    assert (r.areas, r.direction, r.areas_from) == (weak, "against", "weakest")
    # The same question asking what is for goes to the chart's top areas, never long life or health (review C1).
    r = route_turn("what are the strengths in my life", chart)
    assert (r.areas, r.direction, r.areas_from) == (top_areas(chart), "for", "top")
    assert list(chart.scored.top) == ["career", "marriage", "longevity"] and top_areas(chart)[:2] == ["career", "marriage"]
    assert "longevity" not in top_areas(chart) and len(top_areas(chart)) == 3


def test_the_weakest_areas_never_include_death_or_illness(chart):
    assert not {"longevity", "health", "synastry"} & set(weakest_areas(chart, n=20))


def test_a_bare_follow_up_carries_the_last_turn(chart):
    first = route_turn("what are the challanges in my life", chart)
    second = route_turn("and marriage?", chart, first)
    assert (second.areas, second.direction, second.follow_up, second.carried) == (
        ["marriage"], "against", True, ["direction"])
    third = route_turn("when?", chart, second)
    assert (third.areas, third.direction, third.when, third.carried) == (["marriage"], "against", True,
                                                                          ["areas", "direction"])
    fourth = route_turn("why do you say that?", chart, third.model_dump())       # a stored route reads back
    assert (fourth.areas, fourth.direction, fourth.why, fourth.when) == (["marriage"], "against", True, False)
    # A full question of its own carries nothing.
    own = route_turn("How will my career go, and when is the best time for a job change?", chart, fourth)
    assert (own.areas, own.direction, own.when, own.carried, own.follow_up) == (["career"], "for", True, [], False)


def test_nothing_is_carried_from_an_off_limits_turn(chart):
    refused = route_turn("will I die early?", chart, route_turn("and marriage?", chart))
    assert refused.off_limits == "death"
    after = route_turn("when?", chart, refused)
    assert not after.follow_up and after.areas == top_areas(chart)


@pytest.mark.parametrize("message,kind", [
    ("will I die early?", "death"), ("when will I die", "death"), ("how long will I live", "death"),
    ("what is my lifespan", "death"), ("I want to die", "distress"), ("I am thinking of suicide", "distress"),
    ("I can't go on anymore", "distress"), ("do I have cancer", "illness"), ("what disease will I get", "illness"),
    ("should I buy bitcoin", "trade"), ("is the stock market good for me", "trade"), ("should I invest now", "trade"),
    ("what is my wife's future", "other_person"), ("read my husband's chart", "other_person"),
])                                # "will she marry me" is the client's own marriage (SPEC rev 130; review H1)
def test_off_limits_kinds(message, kind):
    assert off_limits(message) == kind


@pytest.mark.parametrize("message", [
    "what are the challanges in my life", "how is my reading", "how is my health", "is my career good",
    "when is the best time for a job change?", "will my marriage be happy", "what about my father",
])
def test_ordinary_questions_are_not_off_limits(message):
    assert off_limits(message) is None


def test_every_kind_has_a_fixed_reply_and_distress_gets_a_helpline():
    assert set(REPLIES) == set(OFF_LIMITS) and all(fixed_reply(k) for k in OFF_LIMITS)
    assert "14416" in fixed_reply("distress") and "112" in fixed_reply("distress")
    assert "chart" not in fixed_reply("distress").split("not a chart")[1]          # no chart reading in it


def test_a_minors_chart_answers_the_general_areas_only(chart):
    from datetime import date
    assert is_minor(date(2012, 5, 1), date(2026, 11, 1)) and not is_minor(date(2001, 3, 12), date(2026, 11, 1))
    assert route_turn("tell me about my studies", chart, minor=True).off_limits is None
    assert route_turn("when will I marry", chart, minor=True).off_limits == "minor"
    assert "intellect" in MINOR_AREAS and "marriage" not in MINOR_AREAS


def test_an_off_limits_turn_is_logged_by_kind_without_the_message(chart, caplog):
    from jyotish import logs
    logs.setup()
    logger = logging.getLogger(logs.LOGGER)
    logger.propagate = True
    try:
        with caplog.at_level(logging.INFO, logger=logs.LOGGER):
            route_turn("should I buy bitcoin", chart)
    finally:
        logger.propagate = False
    rec = [r for r in caplog.records if r.getMessage() == "turn.off_limits"]
    assert rec and rec[0].fields == {"kind": "trade"}
    assert "bitcoin" not in json.dumps(rec[0].fields)
