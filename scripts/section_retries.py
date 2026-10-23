"""Section-level retries, measured on a replay of a recorded depth-full reading (SPEC Layer 7, depth full).

    .venv/bin/python scripts/section_retries.py                       # reading B of docs/comparison_2026-10-23
    .venv/bin/python scripts/section_retries.py --recording <path> --json

The recording is replayed through `narrate` twice, with the engine as it is now: once with whole-
draft retries (CONFIG.section_retries False: every retry asks for the whole draft, and nothing is
checked until a draft passes the validator or the last attempt comes) and once with section retries
(a unit that passes is held, every unit that passes the validator is checked in its attempt, a retry
asks only for the failed units). The writer is replayed as it ran: an attempt the recording shows
failing (B's first: no structured output at max_tokens) fails again, and the recorded drafts follow
in order. The checker gives the recorded verdict for a sentence it has one for; a sentence with none
passes and is counted as unchecked, so the replay measures what each policy asks of the writer and
the checker, not what a live checker would decide.

Measured per attempt: the units the writer is asked to write (summary, claims, sections) and their
characters in the draft it returned, and the checker calls; at the end, the units held and the gaps."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

B = REPO / "docs" / "comparison_2026-10-23" / "b.recording.json"
B_READING = REPO / "docs" / "comparison_2026-10-23" / "b.reading.json"
UNIT = re.compile(r"^- (the .+):$")


class Replayed:
    """The recorded writer: each recorded attempt in order, a failed one failing again."""

    def __init__(self, recording: dict):
        from jyotish.narrate import ReadingDraft
        self.attempts = [(ReadingDraft(**c["draft"]) if c.get("draft") else None, c.get("writer_error"))
                         for c in recording["calls"] if c["kind"] == "writer"]
        self.asked: list[list[str]] = []
        self.last_meta = None

    def __call__(self, system, user, errors):
        from jyotish.narrate import RETRY_HEAD, NarrationError
        n = len(self.asked)
        if n == 0 or not errors:
            self.asked.append(["the whole draft"])
        elif len(errors) == 1 and errors[0].startswith(RETRY_HEAD):
            self.asked.append([m.group(1) for line in errors[0].splitlines() if (m := UNIT.match(line))])
        else:
            self.asked.append(["the whole draft"])
        draft, error = self.attempts[min(n, len(self.attempts) - 1)]
        self.last_meta = {"kind": "writer", "replayed": True}
        if draft is None:
            raise NarrationError("no structured output in the response", list(error or [])[1:] or ["max_tokens"])
        return draft


def _units(draft) -> dict[str, str]:
    """Every unit of a draft and its text, under the names retry_instruction uses."""
    out = {"the summary": draft.summary}
    for a in draft.areas:
        out |= {f"the claim for {c.finding_id} ({a.name})": c.text for c in a.claims}
        for sec in ("assessment", "timing", "not_said"):
            text = getattr(a.analysis, sec, None) if a.analysis else None
            if text:
                out[f"the {a.name} {sec}"] = text
    return out


def run(recording: dict, section_retries: bool, chart, areas: list[str], as_of: date) -> dict:
    from jyotish.narrate import CONFIG, FixtureChecker, narrate
    writer, checker, rec = Replayed(recording), FixtureChecker(recording), []
    reading = narrate(chart, recording["question"], drafter=writer, checker=checker, as_of=as_of, areas=areas,
                      depth="full", recording=rec, config=replace(CONFIG, section_retries=section_retries))
    per = []
    for i, asked in enumerate(writer.asked, 1):
        draft, _ = writer.attempts[min(i - 1, len(writer.attempts) - 1)]
        units = _units(draft) if draft is not None else {}
        wanted = units if asked == ["the whole draft"] else {u: units.get(u, "") for u in asked}
        per.append({"attempt": i, "asked": "the whole draft" if asked == ["the whole draft"] else len(asked),
                    "units_written": len(wanted), "characters_written": sum(len(t) for t in wanted.values()),
                    "writer_failed": draft is None,
                    "checker_calls": sum(1 for c in rec if c["kind"] == "checker" and c["attempt"] == i)})
    held = sum(len(a.claims) for a in reading.areas) + sum(len(a.analysis or {}) for a in reading.areas) \
        + (1 if reading.summary.source == "model" else 0)
    return {"section_retries": section_retries, "attempts": per, "units_held": held,
            "gaps": sum(len(a.narration_gaps) for a in reading.areas),
            "analysis_gaps": sum(1 for a in reading.areas for g in a.narration_gaps if g["kind"] == "analysis"),
            "checker_calls": sum(p["checker_calls"] for p in per), "unchecked_replays": len(checker.unchecked)}


def measure(path: Path = B, reading_path: Path | None = B_READING) -> dict:
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    recording = json.loads(Path(path).read_text())
    done = json.loads(Path(reading_path).read_text()) if reading_path and Path(reading_path).exists() else {}
    areas = [a["name"] for a in done.get("areas", [])] or ["career", "marriage", "longevity"]
    as_of = date.fromisoformat(done.get("as_of", "2026-10-21"))
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    whole, sections = (run(recording, x, chart, areas, as_of) for x in (False, True))
    last_whole, last_sec = whole["attempts"][-1], sections["attempts"][-1]
    return {"recording": str(path), "whole_draft": whole, "section_retries": sections,
            "last_attempt_characters_saved": last_whole["characters_written"] - last_sec["characters_written"],
            "last_attempt_units_saved": last_whole["units_written"] - last_sec["units_written"]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--recording", default=str(B))
    ap.add_argument("--reading", default=str(B_READING), help="the reading the recording made (areas, date)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    m = measure(Path(args.recording), Path(args.reading))
    if args.json:
        print(json.dumps(m, indent=1))
        return 0
    for key in ("whole_draft", "section_retries"):
        r = m[key]
        print(f"{key}: held {r['units_held']} units, {r['gaps']} gaps ({r['analysis_gaps']} analysis), "
              f"{r['checker_calls']} checker calls, {r['unchecked_replays']} sentences with no recorded verdict")
        for p in r["attempts"]:
            print(f"  attempt {p['attempt']}: asked {p['asked']}, wrote {p['units_written']} units, "
                  f"{p['characters_written']} characters{' (writer failed)' if p['writer_failed'] else ''}, "
                  f"{p['checker_calls']} checks")
    print(f"last attempt: {m['last_attempt_units_saved']} fewer units, {m['last_attempt_characters_saved']} fewer characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
