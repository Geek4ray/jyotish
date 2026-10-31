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


def test_the_windows_are_months_and_each_is_said_as_the_engine_scores_it(reading):
    # Review Q1: the client's text named the period to avoid and then said "These are periods the engine
    # scores as favourable". Each period is now said as the engine scores it, and the closing line speaks of
    # both as scores, neither as a prediction.
    s, career = reading.summary, next(a for a in reading.areas if a.name == "career")
    month = lambda x: date.fromisoformat(x).strftime("%B %Y")
    best, avoid = max(career.windows, key=lambda w: w.score), career.avoid_window
    assert (f"The period the engine scores most favourable for career runs from {month(best.start)} to {month(best.end)}; "
            f"the period it scores least favourable runs from {month(avoid.start)} to {month(avoid.end)}.") in s.client_text
    assert s.client_text.endswith("These are the engine's scores, and neither period is a prediction of when you will act.")
    assert re.search(rf"runs from {MONTH} to {MONTH}", s.client_text)


def test_no_sentence_calls_the_low_scored_period_favourable_or_advises_avoiding_it(reading):
    # What the sentences say, not only their words (review Q1, Q11, DoD 5): a sentence that names the
    # low-scored period's months says "least favourable"; nothing after it calls the periods favourable; and
    # nothing tells the client to avoid anything.
    from jyotish.narrate import sentences
    career = next(a for a in reading.areas if a.name == "career")
    low = date.fromisoformat(career.avoid_window.start).strftime("%B %Y")
    said = sentences(reading.summary.client_text)
    at = next(i for i, x in enumerate(said) if low in x)
    assert "least favourable" in said[at].split(low)[0]
    assert not any(re.search(r"(?<!least )favourable", x) for x in said[at + 1:])
    assert not re.search(r"\bavoid", reading.summary.client_text, re.I)


def test_the_timing_note_says_the_window_to_avoid_apart():
    from jyotish.narrate import timing_note
    assert timing_note(["career"], avoid=True) == (
        "A best window is a period the engine scores as favourable for career, and a window to avoid is the period "
        "it scores lowest; neither predicts when you will act.")
    assert timing_note(["career"]) == ("These are periods the engine scores as favourable for career; "
                                       "it does not predict when you will act.")


def test_a_tier_that_is_not_a_degree_and_an_unstable_area_are_said_plainly(reading):
    areas = [a.model_copy(update={"tier": "cannot be assessed", "windows": [], "avoid_window": None,
                                  "stability": a.stability.model_copy(update={"label": "unstable"})})
             for a in reading.areas[:1]]
    text = client_summary(areas, ["career"], ["career"])
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


# --- review Q4: everything outside "For the astrologer" is in the client's words ------------------------------

def _face(md: str) -> list[str]:
    """The page's lines outside every toggle, footnote markers left out; the question is the client's own."""
    face = re.sub(r"<details[^>]*>.*?</details>", "", md, flags=re.S)
    return [re.sub(r"\[\^\d+\]", "", x) for x in face.splitlines() if x.strip() and not x.startswith("# Reading:")]


@pytest.mark.parametrize("depth,fixture,question", [
    ("curious", "narration_curious.json", None),
    ("full", "narration_full_handmade.json", "How will my career go?"),
])
def test_the_page_outside_the_toggles_is_in_the_clients_words(chart, depth, fixture, question, monkeypatch):
    # Review Q4: the stability figures, the windows table, the school conflict, "depends on exact birth time",
    # the learner, the citations and the settings were on the client's face at every depth.
    from pathlib import Path
    from jyotish.page import render
    from jyotish.service import BirthInput, make_reading
    monkeypatch.setenv("JYOTISH_ALLOW_LOCAL_FULL", "1")
    path = Path(__file__).parent / "fixtures" / fixture
    birth = BirthInput(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=REFERENCE_LAT, lon=REFERENCE_LON,
                       node="mean", place="Rewari, Haryana")
    import json as _json
    q = question or _json.loads(path.read_text())["question"]
    reading, page = make_reading(birth, q, chart=chart, as_of="2026-10-21", model_fixture=str(path), depth=depth)
    lines = _face(page)
    assert lines and not [(x, client_errors(x)) for x in lines if client_errors(x)]
    tier = [x for x in lines if x.startswith("- Tier: **")]                    # the tier line stays on the face
    assert len(tier) == 3 and not [x for x in lines if x not in tier and ENGINE_WORDS.search(x.replace("**", ""))]
    assert not [x for x in lines if re.search(r"\b(?:ayanamsa|Vimshottari|score|samples?|family|families)\b", x, re.I)]


def test_a_reviewer_edits_an_engine_summary_in_the_clients_words(chart, reading):
    # Review Q5: the review offered the engine's figures to edit, and an edit made the summary "edited", so the
    # client's face showed "Career: tier moderate (time-stability 1.00, stable) …". An engine summary's targets
    # are now its client_text sentences, held to the client's words; the figures stay as the engine wrote them.
    from jyotish.narrate import CheckResult, Proposition, sentences
    from jyotish.page import render
    from jyotish.review import apply_edit, check_edit, units
    said = sentences(reading.summary.client_text)
    assert [u["text"] for u in units(reading) if u["kind"] == "summary"] == said
    ok = lambda s, d: CheckResult(propositions=[Proposition(text=s, supported=True, evidence="stub")])
    refused = check_edit(reading, chart, "summary:0", "For career, the votes lean in favour.", ok)
    assert not refused["accepted"] and any("engine vocabulary ('votes')" in e for e in refused["errors"])
    # An edit is held as the writer's text is: tagged where it states something, glossed, no tier word.
    new = ("Your work is backed by the Sun and Mercury sitting together in the 10th house, forming Budhaditya yoga, "
           "the combination of Mercury and the Sun in the same sign [rule:yoga.budhaditya].")
    assert check_edit(reading, chart, "summary:1", new, ok)["accepted"]
    edited = apply_edit(reading, "summary:1", new, "ray")
    s = edited.summary
    assert s.source == "edited" and s.client_text == " ".join(said[:1] + [new] + said[2:]) and s.text == reading.summary.text
    face = "\n".join(_face(render(edited, chart)))
    assert "Your work is backed by the Sun and Mercury" in face and "tier moderate" not in face
    assert "time-stability" not in face and "[rule:" not in face                   # its tag is a footnote


def test_a_paragraph_held_in_part_stands_with_its_line_and_the_toggle_closed(chart):
    # Review Q7: a paragraph kept with its held sentences and a gap was shown, then said "did not pass the
    # checks", and the astrologer's reading opened. It now stands with a line of its own, the toggle closed.
    import json as _json
    from pathlib import Path
    from jyotish.narrate import FixtureChecker, FixtureDrafter, narrate
    from jyotish.page import PARTIAL_PARAGRAPH, render
    fx = _json.loads((Path(__file__).parent / "fixtures" / "narration_curious.json").read_text())
    r = narrate(chart, fx["question"], drafter=FixtureDrafter(fx), checker=FixtureChecker(fx), as_of=date(2026, 10, 21),
                areas=AREAS, depth="curious")
    gap = {"finding_id": "paragraph", "kind": "paragraph", "last_error": "refused", "attempt": 3}
    r = r.model_copy(update={"areas": [a.model_copy(update={"narration_gaps": a.narration_gaps + [gap]})
                                       if a.name == "marriage" else a for a in r.areas]})
    marriage = render(r, chart).split("## Marriage", 1)[1].split("\n## ", 1)[0]
    assert r.areas[1].paragraph and f"*{PARTIAL_PARAGRAPH}*" in marriage
    assert "did not pass the checks" not in marriage and "<details open>" not in marriage
