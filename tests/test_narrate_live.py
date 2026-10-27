"""One live narration on the backends the service runs (JYOTISH_<ROLE>_BACKEND; Anthropic when
unset), through the production path: no drafter passed, so the live narration (each area its own
call, the summary last) is what is tested (review R5, 2026-10-26). Skipped unless
JYOTISH_LIVE_NARRATION=1 (keys from the environment or the gitignored .env).

JYOTISH_LIVE_DEPTH picks the depth (default astrologer; "curious" narrates the question's
area and the chart's top three, as the website does, with a paragraph per area). With
JYOTISH_RECORD_FIXTURE=1 it writes every draft the writer produced (rejected ones included)
and every call's record (request id, token usage, model, effort, timestamp, validator errors
for writer calls, propositions for checker calls) to tests/fixtures/narration_career.json,
or tests/fixtures/narration_curious.json at curious depth.

    JYOTISH_LIVE_NARRATION=1 JYOTISH_RECORD_FIXTURE=1 JYOTISH_LIVE_DEPTH=curious \
        .venv/bin/pytest tests/test_narrate_live.py"""

import json
import os
from datetime import date
from pathlib import Path

import pytest

LIVE = os.environ.get("JYOTISH_LIVE_NARRATION") == "1"
DEPTH = os.environ.get("JYOTISH_LIVE_DEPTH", "astrologer")


@pytest.mark.skipif(not LIVE, reason="set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API")
def test_live_narration_passes_validator_and_checker():
    from jyotish.envfile import load
    from jyotish.narrate import CONFIG, narrate, recording_fixture, route
    load(Path(__file__).resolve().parents[1] / ".env")          # names only; never a value printed
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess

    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    question = "How will my career go, and when is the best time for a job change?"
    areas = None
    if DEPTH == "curious":
        asked, _ = route(question, chart)
        areas = list(dict.fromkeys(asked + list(chart.scored.top)))
    recording: list = []
    reading = narrate(chart, question, as_of=date(2026, 10, 21), recording=recording, areas=areas, depth=DEPTH)

    if os.environ.get("JYOTISH_RECORD_FIXTURE") == "1":
        name = "narration_curious.json" if DEPTH == "curious" else "narration_career.json"
        (Path(__file__).parent / "fixtures" / name).write_text(json.dumps({
            "note": (f"Recorded from {CONFIG.model} (writer effort {CONFIG.effort}, checker effort "
                     f"{CONFIG.checker_effort}, depth {DEPTH}) by tests/test_narrate_live.py."),
            "question": question, "depth": DEPTH,
            **recording_fixture(recording),
            "accepted": reading.narration_complete,
            "calls": recording}, indent=2, ensure_ascii=False, default=str) + "\n")

    # A gap is reported, not failed: the reading never fails on narration alone. What must hold
    # is that the reading is there, that a curious one has its paragraphs, and that every
    # sentence the reading shows went through the checker and was accepted on its attempt.
    gaps = [(a.name, g["finding_id"], g["last_error"][:200]) for a in reading.areas for g in a.narration_gaps]
    for gap in gaps:
        print("narration gap:", *gap)
    if reading.summary.source == "engine":
        print("summary: written by the engine")
    assert reading.areas and all(c.cites for a in reading.areas for c in a.claims)
    assert all(e.get("request_id") for e in recording if e["kind"] == "writer" and e.get("draft"))
    if DEPTH == "curious":
        assert any(a.paragraph for a in reading.areas)
    accepted = {e["sentence"] for e in recording
                if e["kind"] == "checker" and all(p["supported"] for p in e["result"]["propositions"])}
    from jyotish.narrate import TAG, sentences
    shown = [c.text for a in reading.areas for c in a.claims]
    shown += [x for a in reading.areas if a.paragraph for x in sentences(a.paragraph) if TAG.search(x)]
    if reading.summary.source == "model":
        shown += [x for x in sentences(reading.summary.text) if TAG.search(x)]
    unchecked = [x for x in shown if x not in accepted]
    assert not unchecked, unchecked
