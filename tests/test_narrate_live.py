"""One live narration against the Anthropic API. Skipped unless JYOTISH_LIVE_NARRATION=1
(credentials from ANTHROPIC_API_KEY or an `ant auth login` profile). With
JYOTISH_RECORD_FIXTURE=1 it also rewrites tests/fixtures/narration_career.json from the
model's own drafts, replacing the hand-authored fixture."""

import json
import os
from datetime import date
from pathlib import Path

import pytest

LIVE = os.environ.get("JYOTISH_LIVE_NARRATION") == "1"


@pytest.mark.skipif(not LIVE, reason="set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API")
def test_live_narration_passes_the_validator():
    from jyotish.narrate import CONFIG, AnthropicDrafter, narrate
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess

    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    question = "How will my career go, and when is the best time for a job change?"
    drafts = []

    class Recording(AnthropicDrafter):
        def __call__(self, system, user, errors):
            d = super().__call__(system, user, errors)
            drafts.append(d.model_dump())
            return d

    reading = narrate(chart, question, drafter=Recording(CONFIG), as_of=date(2026, 10, 21))
    assert reading.areas and all(c.cites for a in reading.areas for c in a.claims)
    assert reading.model == CONFIG.model

    if os.environ.get("JYOTISH_RECORD_FIXTURE") == "1":
        path = Path(__file__).parent / "fixtures" / "narration_career.json"
        path.write_text(json.dumps({
            "note": f"Recorded from {CONFIG.model} by tests/test_narrate_live.py.",
            "question": question, "drafts": drafts}, indent=2, ensure_ascii=False) + "\n")
