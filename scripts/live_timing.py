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

With --url (2026-10-31) the reading is asked of a deployed service instead (POST /readings, then its live
view polled at GET /readings/{id}/live and the finished reading read from GET /readings/{id}): the service
uses its own backends and keys, none is read here. The row carries the service's own timeline (the same
fields as a local run's), the seconds this script saw each first event arrive (`client_timeline`, network
included), and `where` (the --where label, "fly" by default for a fly.dev host).

    .venv/bin/python scripts/live_timing.py --label fly-1 --url https://jyotish-ray.fly.dev

With --turn (2026-11-01, SPEC Layer 8) a conversation is timed instead of a reading: by default the five-turn
conversation of the spec's tests (FIVE_TURNS; review M6), or the messages given after --turn, in order. The
session's whole-chart payload is made first (`session_s`), then each turn routed with the conversation and answered
(conversation.route_turn, answer_turn on the backends named, the earlier turns' shown text as history), and each
turn writes a row (`kind` "turn", `turn` its number, `conversation` the label) with the seconds to the engine's own
answer (`engine_s`), to the first sentence verified and to done, the removed share (sentences refused of those the
writer wrote), the source of the answer the client read and the cost, and its record to
docs/live_<date>/<label>-<n>.turn.json. With --url the turns are asked of a deployed service (POST /sessions, POST
/sessions/{id}/turns, their live events polled) and the rows have the times this script saw.

    .venv/bin/python scripts/live_timing.py --label conversation-1 --turn --as-of 2026-11-01
    .venv/bin/python scripts/live_timing.py --label turn-1 --turn "what are the challanges in my life"
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


def timing_row(label: str, doc: dict, cost: dict, retries: dict | None, concurrency: int | None,
               events: int | None) -> dict:
    """One row of docs/live_timings.jsonl from a finished reading's document."""
    t = (doc.get("usage") or {}).get("timeline") or {}
    w, c = doc.get("writer") or {}, doc.get("checker") or {}
    return {"label": label, "date": date.today().isoformat(), "depth": doc.get("depth"),
            "writer": f"{w.get('model')} on {(w.get('backend') or {}).get('host')}",
            "checker": f"{c.get('model')} on {(c.get('backend') or {}).get('host')}",
            "checker_effort": c.get("effort"), "checker_temperature": (c.get("backend") or {}).get("temperature"),
            "checker_concurrency": concurrency,
            "narration": "live" if (doc.get("usage") or {}).get("parallel_areas") else "one call",
            **{k: t.get(k) for k in ("instant_s", "first_sentence_s", "first_verified_s", "first_area_s", "done_s")},
            "cost_usd": cost["cost_usd"], "writer_calls": cost["writer_calls"], "checker_calls": cost["checker_calls"],
            "claims": sum(len(a["claims"]) for a in doc["areas"]),
            "gaps": sum(len(a["narration_gaps"]) for a in doc["areas"]),
            "summary": (doc.get("summary") or {}).get("source"), "unchecked": doc.get("unchecked_sentences"),
            "retries": retries, "events": events}


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
    ap.add_argument("--url", help="a deployed service's base URL: time a reading asked of it (no key read here)")
    ap.add_argument("--where", help="the row's `where` (default: fly for a fly.dev host, else the host)")
    ap.add_argument("--turn", metavar="MESSAGE", nargs="*", default=None,
                    help="time a conversation, not a reading: the five-turn conversation (FIVE_TURNS) with no message, "
                         "else these messages in order")
    ap.add_argument("--from-reading", type=Path, help="append the row of a reading already written (a comparison's "
                    "docs/comparison_<date>/<side>.reading.json), with no model call")
    args = ap.parse_args(argv)
    if args.from_reading:
        from jyotish.costs import reading_cost
        doc = json.loads(args.from_reading.read_text())
        row = timing_row(args.label, doc, reading_cost(doc), (doc.get("usage") or {}).get("retries"), None, None)
        print(json.dumps(row, indent=2))
        if not args.no_write:
            with ROWS.open("a") as f:
                f.write(json.dumps(row) + "\n")
        return 0

    if args.url:
        return remote_turn(args) if args.turn is not None else remote(args)

    from jyotish.envfile import load as load_env
    print("read from .env:", load_env(ROOT / ".env"))            # names only
    for name, value in (("JYOTISH_WRITER_BACKEND", args.writer), ("JYOTISH_CHECKER_BACKEND", args.checker),
                        ("JYOTISH_CLIENT_BACKEND", args.client),
                        ("JYOTISH_CHECKER_CONCURRENCY", args.concurrency), ("JYOTISH_CHECKER_EFFORT", args.checker_effort),
                        ("JYOTISH_CHECKER_TEMPERATURE", args.checker_temperature)):
        if value is not None:
            os.environ[name] = str(value)
    if args.turn is not None:
        return local_turn(args)
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
    recording: list[dict] = []
    started = time.perf_counter()
    reading, page = make_reading(birth, QUESTION, chart=chart, as_of=args.as_of, depth=args.depth,
                                 writer_effort=args.writer_effort, on_instant=lambda r, p: None, events=events.append,
                                 recording=recording)
    wall = round(time.perf_counter() - started, 1)
    doc = reading.model_dump(mode="json")
    row = timing_row(args.label, doc, reading_cost(doc), retries.by, concurrency, len(events))
    row["wall_s"] = wall
    print(json.dumps(row, indent=2))
    if not args.no_write:
        out = ROOT / "docs" / f"live_{date.today().isoformat()}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.label}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        (out / f"{args.label}.md").write_text(page)
        # The recording, replayable offline unit by unit (service.make_reading's model_fixture); the models'
        # reasoning is left out to keep it small.
        from jyotish.narrate import recording_fixture
        calls = [{k: v for k, v in c.items() if k != "thinking"} for c in recording]
        (out / f"{args.label}.recording.json").write_text(json.dumps(
            {"note": "Recorded by scripts/live_timing.py.", "question": QUESTION, **recording_fixture(calls), "calls": calls},
            indent=1, ensure_ascii=False, default=str) + "\n")
        with ROWS.open("a") as f:
            f.write(json.dumps(row) + "\n")
    return 0


BIRTH = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "node": "mean", "place": "Rewari, Haryana"}
# The five-turn conversation of SPEC Layer 8's tests (tests/test_conversation.py), timed live by default (review M6).
FIVE_TURNS = ("what are the challanges in my life", "and marriage?", "when?", "why do you say that?", "will I die early?")


def turn_row(label: str, doc: dict, cost: dict, session_s: float | None, n: int | None = None,
             conversation: str | None = None) -> dict:
    """One row of docs/live_timings.jsonl from a turn's document (conversation.answer_turn); `n` the turn's number
    in a conversation timed whole, `conversation` its label."""
    t = doc.get("timeline") or {}
    w, c = doc.get("writer") or {}, doc.get("checker") or {}
    written = len(doc.get("accepted") or []) + sum(1 for x in doc.get("removed") or [] if x.get("sentence"))
    removed = sum(1 for x in doc.get("removed") or [] if x.get("sentence"))
    return {"label": label, "kind": "turn", **({"turn": n, "conversation": conversation} if n else {}),
            "date": date.today().isoformat(), "question": doc.get("question"),
            "route": doc.get("route"), "writer": f"{w.get('model')} on {(w.get('backend') or {}).get('host')}",
            "checker": f"{c.get('model')} on {(c.get('backend') or {}).get('host')}", "writer_effort": w.get("effort"),
            "session_s": session_s,
            "engine_s": t.get("engine"), "first_verified_s": t.get("first_verified"), "done_s": t.get("done"),
            "removed": removed, "written": written, "removed_share": round(removed / written, 3) if written else None,
            "source": doc.get("source"), "attempts": doc.get("attempts"), "warnings": len(doc.get("warnings") or []),
            "cost_usd": cost["cost_usd"], "writer_calls": cost["writer_calls"], "checker_calls": cost["checker_calls"]}


def local_turn(args) -> int:
    """A conversation on the reference chart, on the environment's backends, each turn timed (the module docstring)."""
    from datetime import date as _date
    from jyotish.conversation import answer_turn, route_turn
    from jyotish.costs import reading_cost
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    from jyotish.scoring import AREAS
    from jyotish.service import BirthInput, assess_birth
    birth = BirthInput(**BIRTH, lat=REFERENCE_LAT, lon=REFERENCE_LON)
    chart, _, _ = assess_birth(birth)
    as_of = _date.fromisoformat(args.as_of)
    t = time.perf_counter()
    data = cached_payload(chart, as_of, *full_range(as_of), list(AREAS))
    session_s = round(time.perf_counter() - t, 1)
    from dataclasses import replace
    from jyotish.narrate import CONFIG
    config = replace(CONFIG, effort=args.writer_effort) if args.writer_effort else CONFIG
    messages = args.turn or FIVE_TURNS
    whole = len(messages) > 1
    last, history = None, []
    for n, message in enumerate(messages, 1):
        route = route_turn(message, chart, last)
        doc = answer_turn(chart, message, route, as_of=as_of, data=data, config=config, history=list(history))
        label = f"{args.label}-{n}" if whole else args.label
        row = turn_row(label, doc, reading_cost(doc), session_s if n == 1 else None, n if whole else None,
                       args.label if whole else None)
        print(json.dumps(row, indent=2))
        if not args.no_write:
            out = ROOT / "docs" / f"live_{date.today().isoformat()}"
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{label}.turn.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
            with ROWS.open("a") as f:
                f.write(json.dumps(row) + "\n")
        history.append({"question": message, "answer": " ".join(doc["shown"])})     # what the client read
        if not route.off_limits:
            last = route
    return 0


def remote_turn(args) -> int:
    """One conversation turn asked of a deployed service, timed as its events arrive (no key read here)."""
    from urllib.parse import urlparse

    import httpx
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    base = args.url.rstrip("/")
    host = urlparse(base).hostname or base
    where = args.where or ("fly" if host.endswith(".fly.dev") else host)
    messages = args.turn or FIVE_TURNS
    whole = len(messages) > 1
    ok = True
    with httpx.Client(timeout=120) as http:              # the client keeps the conversation's cookie (review H7)
        t = time.perf_counter()
        # A deployed conversation is read for the server's date: a client may not set it (review M2).
        r = http.post(f"{base}/sessions", json=dict(BIRTH, lat=REFERENCE_LAT, lon=REFERENCE_LON))
        r.raise_for_status()
        sid = r.json()["id"]
        session_s = round(time.perf_counter() - t, 1)
        for k, message in enumerate(messages, 1):
            seen: dict[str, float] = {"session_s": session_s} if k == 1 else {}
            started = time.perf_counter()
            n = http.post(f"{base}/sessions/{sid}/turns", json={"message": message}).json()["n"]
            since = 0
            while True:
                live = http.get(f"{base}/sessions/{sid}/turns/{n}/live", params={"since": since}).json()
                now = round(time.perf_counter() - started, 1)
                since = live["version"]
                for e in live["events"]:
                    if e.get("type") == "text":
                        seen.setdefault("first_text_s", now)
                if live["done"]:
                    break
                time.sleep(0.5)
            seen["done_s"] = round(time.perf_counter() - started, 1)
            turn = http.get(f"{base}/sessions/{sid}/turns/{n}").json()
            ok = ok and turn.get("status") == "done"
            row = {"label": f"{args.label}-{k}" if whole else args.label, "kind": "turn",
                   **({"turn": k, "conversation": args.label} if whole else {}), "date": date.today().isoformat(),
                   "question": message, "where": where, "url": base, "status": turn.get("status"),
                   "sentences_shown": len(turn.get("answer") or []), "client_timeline": seen}
            print(json.dumps(row, indent=2))
            if not args.no_write:
                with ROWS.open("a") as f:
                    f.write(json.dumps(row) + "\n")
    return 0 if ok else 1


def remote(args) -> int:
    """One reading asked of a deployed service, timed as it fills in; the row appended as a local run's is."""
    from urllib.parse import urlparse

    import httpx
    from jyotish.costs import reading_cost
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    base = args.url.rstrip("/")
    host = urlparse(base).hostname or base
    where = args.where or ("fly" if host.endswith(".fly.dev") else host)
    body = dict(BIRTH, lat=REFERENCE_LAT, lon=REFERENCE_LON, question=QUESTION, depth=args.depth, as_of=args.as_of)
    if args.writer_effort:
        body["writer_effort"] = args.writer_effort
    seen: dict[str, float] = {}
    firsts = {"sentence": "first_sentence_s", "verified": "first_verified_s", "area": "first_area_s"}
    with httpx.Client(timeout=60) as http:
        started = time.perf_counter()
        r = http.post(f"{base}/readings", json=body)
        r.raise_for_status()
        rid = r.json()["id"]
        since, events, status = 0, 0, "queued"
        while True:
            # Each first event is stamped when its answer arrived (review Q10: the time was taken before the two
            # GETs, so client_timeline ran early by a request's time).
            if "instant_s" not in seen:
                got = http.get(f"{base}/readings/{rid}").json()
                if got.get("reading"):
                    seen["instant_s"] = round(time.perf_counter() - started, 1)
            live = http.get(f"{base}/readings/{rid}/live", params={"since": since}).json()
            now = round(time.perf_counter() - started, 1)
            since, status = live["version"], live["status"]
            for e in live["events"]:
                events += 1
                if e.get("type") in firsts:
                    seen.setdefault(firsts[e["type"]], now)
            if live["done"]:
                break
            time.sleep(1)
        seen["done_s"] = round(time.perf_counter() - started, 1)
        final = http.get(f"{base}/readings/{rid}").json()
    if final.get("status") != "done" or not final.get("reading"):
        print(json.dumps({"id": rid, "status": final.get("status"), "error": final.get("error")}, indent=2))
        return 1
    doc = final["reading"]
    row = timing_row(args.label, doc, reading_cost(doc), (doc.get("usage") or {}).get("retries"), None, events)
    row.update({"where": where, "url": base, "reading_id": rid, "client_timeline": seen, "wall_s": seen["done_s"]})
    print(json.dumps(row, indent=2))
    if not args.no_write:
        out = ROOT / "docs" / f"live_{date.today().isoformat()}"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{args.label}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        if final.get("page"):
            (out / f"{args.label}.md").write_text(final["page"])
        with ROWS.open("a") as f:
            f.write(json.dumps(row) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
