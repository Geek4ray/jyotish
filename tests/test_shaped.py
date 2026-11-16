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
