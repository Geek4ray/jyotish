"""Time a live reading of the reference chart as it fills in (2026-10-26; docs/models.md, "Timing").

The reading goes through the service's pipeline (service.make_reading with the instant page and the
live view, as POST /readings runs it) on the backends named, and the run records the seconds from the
start to the instant page, to the first sentence shown, to the first sentence verified, to the first
area finished and to the reading done; the cost (costs.reading_cost, each role at its host's price);
the gaps; the checker's retries (the backends' `backend.retry` log events) and its unchecked
sentences. Each run appends one row to docs/live_timings.jsonl and writes the reading to
docs/live_<date>/<label>.json. Keys come from the environment or the gitignored .env, never printed.

    .venv/bin/python scripts/live_timing.py --label deepinfra-glm47-c8 --concurrency 8
    .venv/bin/python scripts/live_timing.py --label cerebras-flash-t0 \\
        --writer openai:https://api.cerebras.ai/v1:gpt-oss-120b \\
        --checker openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-5.3-Flash --checker-temperature 0
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
QUESTION = "How will my career go, and when is the best time for a job change?"
ROWS = ROOT / "docs" / "live_timings.jsonl"


class Retries(logging.Handler):
    """Counts the backends' retries by host and model (the log carries no key and no birth data)."""

    def __init__(self):
        super().__init__()
        self.by: dict[str, int] = {}

    def emit(self, record: logging.LogRecord) -> None:
        if record.getMessage() == "backend.retry":
            f = getattr(record, "fields", {}) or {}
            k = f"{f.get('host')} {f.get('model')}"
            self.by[k] = self.by.get(k, 0) + 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--label", required=True, help="the run's name (the reading's file, the row's label)")
    ap.add_argument("--writer", help="the writer's backend spec (default: JYOTISH_WRITER_BACKEND)")
    ap.add_argument("--checker", help="the checker's backend spec (default: JYOTISH_CHECKER_BACKEND)")
    ap.add_argument("--client", help="the client's layer's backend spec (default: JYOTISH_CLIENT_BACKEND)")
    ap.add_argument("--concurrency", type=int, help="checker calls in flight (JYOTISH_CHECKER_CONCURRENCY)")
    ap.add_argument("--checker-effort", help="the checker's effort (JYOTISH_CHECKER_EFFORT)")
    ap.add_argument("--checker-temperature", type=float, help="the checker's temperature (JYOTISH_CHECKER_TEMPERATURE)")
    ap.add_argument("--writer-effort", help="the writer's effort")
    ap.add_argument("--depth", default="astrologer", choices=("astrologer", "curious", "full"))
    ap.add_argument("--as-of", default="2026-10-26")
    ap.add_argument("--no-write", action="store_true", help="print the row only")
    args = ap.parse_args(argv)

    from jyotish.envfile import load as load_env
    print("read from .env:", load_env(ROOT / ".env"))            # names only
    for name, value in (("JYOTISH_WRITER_BACKEND", args.writer), ("JYOTISH_CHECKER_BACKEND", args.checker),
                        ("JYOTISH_CLIENT_BACKEND", args.client),
                        ("JYOTISH_CHECKER_CONCURRENCY", args.concurrency), ("JYOTISH_CHECKER_EFFORT", args.checker_effort),
                        ("JYOTISH_CHECKER_TEMPERATURE", args.checker_temperature)):
        if value is not None:
            os.environ[name] = str(value)
    from jyotish import logs
    from jyotish.costs import reading_cost
    from jyotish.narrate import CONFIG, ModelChecker, make_backend
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    from jyotish.service import BirthInput, assess_birth, make_reading
    retries = Retries()
    logging.getLogger(logs.LOGGER).addHandler(retries)
    birth = BirthInput(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=REFERENCE_LAT, lon=REFERENCE_LON,
                       node="mean", place="Rewari, Haryana")
    chart, _, _ = assess_birth(birth)
    concurrency = ModelChecker(make_backend(None, "checker", CONFIG), CONFIG).concurrency
    events: list[dict] = []
    started = time.perf_counter()
    reading, page = make_reading(birth, QUESTION, chart=chart, as_of=args.as_of, depth=args.depth,
                                 writer_effort=args.writer_effort, on_instant=lambda r, p: None, events=events.append)
    wall = round(time.perf_counter() - started, 1)
    doc = reading.model_dump(mode="json")
    cost = reading_cost(doc)
    t = (reading.usage or {}).get("timeline") or {}
    gaps = sum(len(a.narration_gaps) for a in reading.areas)
    row = {"label": args.label, "date": date.today().isoformat(), "depth": args.depth,
           "writer": f"{reading.writer.get('model')} on {(reading.writer.get('backend') or {}).get('host')}",
           "checker": f"{reading.checker.get('model')} on {(reading.checker.get('backend') or {}).get('host')}",
           "checker_effort": reading.checker.get("effort"), "checker_temperature": args.checker_temperature,
           "checker_concurrency": concurrency,
           "instant_s": t.get("instant_s"), "first_sentence_s": t.get("first_sentence_s"),
           "first_verified_s": t.get("first_verified_s"), "first_area_s": t.get("first_area_s"),
           "done_s": t.get("done_s"), "wall_s": wall,
           "cost_usd": cost["cost_usd"], "writer_calls": cost["writer_calls"], "checker_calls": cost["checker_calls"],
           "claims": sum(len(a.claims) for a in reading.areas), "gaps": gaps,
           "summary": reading.summary.source, "unchecked": reading.unchecked_sentences,
           "retries": retries.by, "events": len(events)}
    print(json.dumps(row, indent=2))
    if not args.no_write:
        out = ROOT / "docs" / f"live_{date.today().isoformat()}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.label}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        (out / f"{args.label}.md").write_text(page)
        with ROWS.open("a") as f:
            f.write(json.dumps(row) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
