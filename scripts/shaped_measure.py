"""The shaped answer, measured (SPEC Layer 8 rev 136, "The shaped answer"; docs/spec_notes_2026-11-16.md): the sentences
per answer on the seven-turn conversation of tests/test_conversation.py (as of 2026-10-21, as its fixture) and on the
three frozen questions of tests/fixtures/shaped_three_parts.json (as of 2026-11-16), each composed with draft meanings
off and on, and the composer's share of the twenty varied first questions of scripts/evaluate.py. No model call; the
same code runs on an older checkout (PYTHONPATH=<its src>) for the numbers before. Prints JSON.

    .venv/bin/python scripts/shaped_measure.py > docs/shaped_2026-11-16.json
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date

SEVEN = ["what are the challanges in my life", "and marriage?", "when?", "why do you say that?", "will I die early?",
         "how much money will i earn in my life, will i be rich", "whan and how"]
THREE = ["How will my career go, which field will i work in, when will i leave my current job",
         "which field will i work in", "when will i leave my current job"]
VARIED = ("how is my career", "will I get married", "what about money", "when will I buy a house", "and my health?",
          "tell me about my life", "what should I know", "hi", "is this a good year for me", "what are my strengths",
          "what are the challenges in my life", "why?", "will I travel abroad", "how are my children", "kab shaadi hogi",
          "what does my chart say", "will my business do well", "how is my relationship with my father", "am I lucky",
          "what will happen next year")


def main() -> int:
    os.environ["JYOTISH_LAYERED"] = "1"
    from jyotish.conversation import answer_turn, composes, route_turn
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    out: dict = {"seven": {}, "three": {}}
    for mode, flag in (("draft_off", "0"), ("draft_on", "1")):
        os.environ["JYOTISH_SHOW_DRAFT_MEANINGS"] = flag
        last, history, counts = None, [], []
        for m in SEVEN:
            route = route_turn(m, chart, last)
            doc = answer_turn(chart, m, route, as_of=date(2026, 10, 21), history=list(history), session_key="seven")
            counts.append({"question": m, "source": doc["source"], "sentences": len(doc["shown"])})
            history.append({"question": m, "answer": " ".join(doc["shown"]),
                            "said_keys": [s["key"] for s in (doc.get("composed") or {}).get("sentences", [])
                                          if s.get("key")]})
            if not route.off_limits:
                last = route
        out["seven"][mode] = counts
        rows = []
        for m in THREE:
            route = route_turn(m, chart)
            if not composes(route):
                rows.append({"question": m, "source": "not composed (the writer loop)", "sentences": None,
                             "areas": route.areas})
                continue
            doc = answer_turn(chart, m, route, as_of=date(2026, 11, 16), session_key="three")
            rows.append({"question": m, "source": doc["source"], "sentences": len(doc["shown"]), "areas": route.areas})
        out["three"][mode] = rows
    asked = placed = 0
    for m in VARIED:
        r = route_turn(m, chart)
        if r.off_limits:
            continue
        asked += 1
        placed += composes(r)
    out["composer_share"] = {"asked": asked, "composed": placed}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
