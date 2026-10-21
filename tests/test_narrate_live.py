"""One live narration against the Anthropic API: the writer and the semantic checker, both
from narrate.CONFIG. Skipped unless JYOTISH_LIVE_NARRATION=1 (credentials from
ANTHROPIC_API_KEY or an `ant auth login` profile). With JYOTISH_RECORD_FIXTURE=1 it
rewrites tests/fixtures/narration_career.json with every draft the writer produced (rejected
ones included) and every call's record: request id, token usage, model, effort, timestamp,
validator errors for writer calls, and the propositions for checker calls."""

import json
import os
from datetime import date
from pathlib import Path

import pytest

LIVE = os.environ.get("JYOTISH_LIVE_NARRATION") == "1"


@pytest.mark.skipif(not LIVE, reason="set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API")
def test_live_narration_passes_validator_and_checker():
    from jyotish.narrate import CONFIG, AnthropicChecker, AnthropicDrafter, NarrationError, narrate
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess

    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    question = "How will my career go, and when is the best time for a job change?"
    recording: list = []
    error = None
    try:
        reading = narrate(chart, question, drafter=AnthropicDrafter(CONFIG), checker=AnthropicChecker(CONFIG),
                          as_of=date(2026, 10, 21), recording=recording)
    except NarrationError as e:
        reading, error = None, e

    if os.environ.get("JYOTISH_RECORD_FIXTURE") == "1":
        path = Path(__file__).parent / "fixtures" / "narration_career.json"
        path.write_text(json.dumps({
            "note": f"Recorded from {CONFIG.model} (effort {CONFIG.effort}) by tests/test_narrate_live.py.",
            "question": question,
            "drafts": [e["draft"] for e in recording if e["kind"] == "writer"],
            "accepted": reading is not None,
            "calls": recording}, indent=2, ensure_ascii=False, default=str) + "\n")

    assert error is None, f"narration failed after {CONFIG.max_attempts} attempts: {error.errors if error else ''}"
    assert reading.areas and all(c.cites for a in reading.areas for c in a.claims)
    assert all(e.get("request_id") for e in recording)
