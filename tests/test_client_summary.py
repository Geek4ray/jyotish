"""The engine's summary in the client's words (2026-10-31; docs/spec_notes_2026-10-31.md): when no drafted
summary passes, the client's page shows the engine's summary with no engine vocabulary, the windows as
months, and the timing note; the figures stay in the JSON and under "For the astrologer". The area's
figures (classical score, probability, families agreeing, polarity) are the astrologer's at every depth;
the tier line stays on the client's face."""

import re
from datetime import date

import pytest

from jyotish.client import CLIENT_WORDS, client_errors
from jyotish.narrate import Reading, client_summary, instant_reading, upgrade_reading
from jyotish.page import ENGINE_FIGURES, FOR_ASTROLOGER, render
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

QUESTION = "How will my career go, and when is the best time for a job change?"
AREAS = ["career", "marriage", "longevity"]
ENGINE_WORDS = re.compile(r"\btier\b|time-stability|\bscore \d|\bVimshottari\b|\bdriver\b|\bq\b|\bsandhi\b", re.I)
MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}"


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def reading(chart):
    return instant_reading(chart, QUESTION, as_of=date(2026, 10, 21), areas=AREAS)


def test_the_engine_summary_has_its_client_words_with_no_engine_vocabulary(reading):
    s = reading.summary
    assert s.source == "engine" and s.client_text
    assert not CLIENT_WORDS.search(s.client_text) and not client_errors(s.client_text)
    assert not ENGINE_WORDS.search(s.client_text), ENGINE_WORDS.search(s.client_text)
    # The figures stay in the JSON: the engine's own text keeps the tier, the stability and the scores.
    assert "tier" in s.text and "Vimshottari" in s.text and re.search(r"score \d", s.text)


def test_the_windows_are_months_and_the_timing_note_stands(reading):
    s, career = reading.summary, next(a for a in reading.areas if a.name == "career")
    best = max(career.windows, key=lambda w: w.score)
    start, end = (date.fromisoformat(x).strftime("%B %Y") for x in (best.start, best.end))
    assert f"The strongest period for career runs from {start} to {end}" in s.client_text
    avoid = career.avoid_window
    assert f"the period to avoid runs from {date.fromisoformat(avoid.start).strftime('%B %Y')}" in s.client_text
    assert re.search(rf"runs from {MONTH} to {MONTH}", s.client_text)
    assert s.client_text.endswith(s.timing_note)


def test_a_tier_that_is_not_a_degree_and_an_unstable_area_are_said_plainly(reading):
    areas = [a.model_copy(update={"tier": "cannot be assessed", "windows": [], "avoid_window": None,
                                  "stability": a.stability.model_copy(update={"label": "unstable"})})
             for a in reading.areas[:1]]
    text = client_summary(areas, ["career"], ["career"], None)
    assert text.startswith("For career, the chart says that it cannot be judged from this chart. "
                           "This depends on the exact birth time.") and not client_errors(text)


def test_a_reading_made_before_gets_its_client_words_on_upgrade(chart, reading):
    old = Reading(**reading.model_dump(mode="json") | {"summary": reading.summary.model_dump() | {"client_text": None}})
    assert upgrade_reading(old, chart).summary.client_text == reading.summary.client_text


def test_a_model_summary_has_no_client_words_of_the_engines(chart, reading):
    r = reading.model_copy(update={"summary": reading.summary.model_copy(update={"source": "model", "client_text": None,
                                                                                 "text": "Career is read here."})})
    assert upgrade_reading(r, chart).summary.client_text is None


def test_the_page_shows_the_client_words_and_keeps_the_figures_for_the_astrologer(chart, reading):
    page = render(reading, chart)
    summary = page.split("## Summary", 1)[1].split("\n## ", 1)[0]
    face, astrologer = summary.split(f"<details><summary>{FOR_ASTROLOGER}</summary>", 1)
    assert reading.summary.client_text in face and not ENGINE_WORDS.search(face.replace("**", ""))
    assert ENGINE_FIGURES in astrologer and "Current period (Vimshottari)" in astrologer
    # Each area: the tier line on the face, its figures under the toggle.
    career = page.split("## Career", 1)[1].split("\n## ", 1)[0]
    face, astrologer = career.split(f"<summary>{FOR_ASTROLOGER}</summary>", 1)
    assert "- Tier: **" in face and "Classical score" not in face and "Families agreeing" not in face
    assert "Polarity" not in face and "Probability" not in face
    assert "- Classical score:" in astrologer and "- Families agreeing:" in astrologer and "- Probability:" in astrologer
