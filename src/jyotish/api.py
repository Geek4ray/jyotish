"""The reading service (SPEC Phase 4, item 4).

    POST /readings        birth data and a question -> 202 {"id", "status", "url"}
    GET  /readings/{id}   status and progress (chart, score, draft n, check n) while it runs;
                          then the reading JSON (SPEC output schema) and the Markdown page

A reading runs on a worker thread: the chart (`service.assess_birth`, cached by birth data,
conventions, seed and engine), its scored block, then the narration with its writer and
checker calls. The model key is read from the server's environment by the Anthropic SDK
(ANTHROPIC_API_KEY); a request carries no key and may not (unknown fields are refused), and
no response echoes one.

Storage follows the SPEC data schema: a `charts` table keyed by chart id (the cache key) with
the chart object as a JSON document, and a `readings` table with the reading document, its
page, status and progress. SQLite for now (JYOTISH_DATABASE_URL, default
sqlite:///jyotish.db); the document columns are JSONB under PostgreSQL, so moving is a
connection-string change.

The website (web/: plain HTML, CSS and JavaScript modules, no build step) is served at /, and
examples/ (the reference reading) at /examples, after the API routes.

The review step (SPEC Layer 6b): GET /review/{id} is the reviewer's page; the reviewer API under
/readings/{id}/review needs a reviewer token (`Authorization: Bearer <token>`), mapped to a
reviewer id by JYOTISH_REVIEWERS="judge-1:<token>,judge-2:<token>" in the server's environment.
Every open, edit, note, approval and guided-review answer (POST /readings/{id}/review/answer:
step, area, answer, mode) is logged in `reviews` with chart id, reviewer id and time; the chart
goes into `exclusions`, which the Layer 6b learning set respects. A reading's review status is
draft until approved; the client-facing page says "reviewed by" only after. `?mode=blind` (the
judge page) withholds an area's reading until the reviewer has answered from the chart alone:
the server sends it only then, and only then is the chart excluded.

The blind comparison (SPEC Layer 7, depth full; scripts/compare_readings.py): GET /compare/{a}/{b}
is the page, GET /compare/{a}/{b}/view (a reviewer token) the two readings of one chart and question
as A and B with their settings withheld, and POST /compare/{a}/{b}/answer the one question, which
reading the reviewer would give the client and why, logged in `reviews` (action `compare`) and
answered once: the answer reveals the settings.

Run:  .venv/bin/uvicorn jyotish.api:app      then open http://127.0.0.1:8000/"""

from __future__ import annotations

import logging
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# The tables live in db.py; they are imported here too, where scripts and tests have always found them.
from .db import (DOCUMENT, Base, ChartRow, ComparisonRow, ConsentRow, ErasureRow, EventRow, ExclusionRow,  # noqa: F401
                 ReadingRow, ReviewRow, SubjectRow, _add_missing_columns, _now, add_comparison, compared_with,
                 excluded_charts)
from .service import BirthInput


class ReadingRequest(BirthInput):
    """Birth data, the question, and optionally the date the reading is for, the depth and the
    writer's model and effort (narrate.WRITER_MODELS, narrate.EFFORTS; the checker's never change)."""
    model_config = ConfigDict(extra="forbid")
    question: str
    as_of: str | None = None
    depth: Literal["curious", "learner", "astrologer", "full"] = "curious"
    writer_model: str | None = None
    writer_effort: str | None = None

    @model_validator(mode="after")
    def _writer(self):
        from .narrate import EFFORTS, WRITER_MODELS
        if self.writer_model is not None and self.writer_model not in WRITER_MODELS:
            raise ValueError(f"writer_model must be one of {', '.join(WRITER_MODELS)}")
        if self.writer_effort is not None and self.writer_effort not in EFFORTS:
            raise ValueError(f"writer_effort must be one of {', '.join(EFFORTS)}")
        return self


class EditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: str
    text: str = Field(max_length=2000)  # one or two sentences
    keep_tags: bool = False             # a rewrite in plain words carries the old sentence's tags


class AnswerRequest(BaseModel):
    """One answer of the guided review (review.check_answer says which answers a step takes)."""
    model_config = ConfigDict(extra="forbid")
    step: str
    area: str | None = None
    answer: Any
    mode: Literal["review", "blind"] = "review"
    comment: str | None = Field(default=None, max_length=4000)   # the reviewer's own words: judgement, never checked


VERDICTS = ("agree", "partly", "disagree")
REASONS = ("missing_rule", "wrong_weight", "wrong_timing", "other")


class VerdictRequest(BaseModel):
    """The reviewer's structured verdict on an area: judgement data, never shown to the client."""
    model_config = ConfigDict(extra="forbid")
    area: str
    verdict: Literal["agree", "partly", "disagree"]
    reason: Literal["missing_rule", "wrong_weight", "wrong_timing", "other"] | None = None

    @model_validator(mode="after")
    def _reason_when_not_agree(self):
        if self.verdict == "agree" and self.reason is not None:
            raise ValueError("an agree verdict takes no reason")
        if self.verdict != "agree" and self.reason is None:
            raise ValueError(f"a {self.verdict} verdict needs a reason: {', '.join(REASONS)}")
        return self


class CompareAnswer(BaseModel):
    """The blind comparison's one question: which reading would you give the client (A or B), and why."""
    model_config = ConfigDict(extra="forbid")
    choice: Literal["A", "B"]
    why: str = Field(min_length=1, max_length=4000)


# What the blind comparison withholds of each reading until it is answered: the settings that made
# it (writer, checker, usage, the model and attempts, the replay source) and the header's command
# and depth, which name them.
SETTINGS_FIELDS = ("model", "attempts", "writer", "checker", "usage", "narration_source", "depth")


def blind(document: dict) -> dict:
    """A reading with the settings that made it left out (review F7: the top-level depth too); the
    page renders the depth from what the reading holds."""
    out = {k: v for k, v in document.items() if k not in SETTINGS_FIELDS}
    out["chart"] = {k: v for k, v in (document.get("chart") or {}).items() if k not in ("command", "depth")}
    return out



def settings_of(document: dict) -> dict:
    w = document.get("writer") or {}
    return {"model": w.get("model") or document.get("model"), "effort": w.get("effort"), "depth": document.get("depth"),
            "thinking": w.get("thinking"), "checker": document.get("checker") or {}}


def compare_order(a: str, b: str, reviewer: str) -> tuple[str, str]:
    """(the reading shown as A, as B) for this reviewer: from a hash of the pair and the reviewer,
    so it is the same on every visit and for either order of the URL, and the URL says nothing."""
    import hashlib
    first, second = sorted((a, b))
    flip = int(hashlib.sha256(f"{first}|{second}|{reviewer}".encode()).hexdigest(), 16) % 2
    return (second, first) if flip else (first, second)


class OutcomeRows(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rows: list[dict[str, Any]] = Field(max_length=5000)


class NoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    area: str
    text: str = Field(max_length=4000)  # the same bound as a comment


def reviewers_from_env(var: str = "JYOTISH_REVIEWERS") -> dict[str, str]:
    """token -> reviewer id, from JYOTISH_REVIEWERS="judge-1:<token>,judge-2:<token>" (or the clerks'
    JYOTISH_CLERKS, the same shape)."""
    out = {}
    for pair in os.environ.get(var, "").split(","):
        if ":" in pair:
            rid, tok = pair.split(":", 1)
            if rid.strip() and tok.strip():
                out[tok.strip()] = rid.strip()
    return out


class Accepted(BaseModel):
    id: str
    status: str
    url: str


class ReadingStatus(BaseModel):
    id: str
    status: str
    progress: dict[str, Any]
    chart_id: str | None
    question: str
    created_at: datetime
    updated_at: datetime
    reading: dict[str, Any] | None = None
    page: str | None = None
    error: dict[str, Any] | None = None
    review_status: str | None = None


REPO = Path(__file__).resolve().parents[2]


class RateLimit:
    """Readings per client per hour and per day overall (POST /readings: each one costs a model's
    tokens). In this process's memory: one service process per database (docs/deploy.md)."""

    def __init__(self, per_client_hour: int, per_day: int):
        import threading
        from collections import deque
        self.per_client_hour, self.per_day = per_client_hour, per_day
        self.clients: dict[str, Any] = {}
        self.all = deque()
        self.lock = threading.Lock()
        self._deque = deque

    def check(self, client: str) -> int | None:
        """None when allowed (and counted), else the seconds until it would be."""
        import time
        now = time.time()
        with self.lock:
            mine = self.clients.setdefault(client, self._deque())
            while mine and now - mine[0] >= 3600:
                mine.popleft()
            while self.all and now - self.all[0] >= 86400:
                self.all.popleft()
            if len(mine) >= self.per_client_hour:
                return int(3600 - (now - mine[0])) + 1
            if len(self.all) >= self.per_day:
                return int(86400 - (now - self.all[0])) + 1
            mine.append(now)
            self.all.append(now)
            return None


def create_app(database_url: str | None = None, *, model_fixture: str | None = None, workers: int = 2,
               web_dir: Path | None = REPO / "web", examples_dir: Path | None = REPO / "examples",
               reviewers: dict[str, str] | None = None, review_checker=None,
               clerks: dict[str, str] | None = None, rate: tuple[int, int] | None = None) -> FastAPI:
    """The app. `model_fixture` replays a recorded narration instead of calling the model
    (offline tests); it is never taken from a request. The website and the examples are
    mounted when their directories exist (a source checkout). Reviewers, clerks and the owner
    are the `credentials` table's (`jyotish reviewer add`); `reviewers` and `clerks` (token -> id)
    add to it for a local run and default to JYOTISH_REVIEWERS and JYOTISH_CLERKS, which the log
    says. `review_checker` checks edited sentences (default the live AnthropicChecker; tests pass a
    stub). `rate` is (readings per client per hour, readings per day), default
    JYOTISH_READINGS_PER_HOUR and JYOTISH_READINGS_PER_DAY, else 30 and 300."""
    from . import logs
    from .db import migrate
    logs.setup()
    if model_fixture is None and os.environ.get("JYOTISH_MODEL_FIXTURE"):
        # The CI smoke test's replay (scripts/smoke.py): never set on a real deployment, and loud when it is.
        model_fixture = os.environ["JYOTISH_MODEL_FIXTURE"]
        logs.event("narration.fixture", logging.WARNING, note="JYOTISH_MODEL_FIXTURE is set: every reading replays "
                   "a recording and calls no model; /health says narration fixture")
    engine = migrate(database_url)                # JYOTISH_DATABASE_URL when none is named
    Session = sessionmaker(engine, expire_on_commit=False)
    tokens = reviewers if reviewers is not None else reviewers_from_env()
    clerk_tokens = clerks if clerks is not None else reviewers_from_env("JYOTISH_CLERKS")
    for var, given, explicit in (("JYOTISH_REVIEWERS", tokens, reviewers), ("JYOTISH_CLERKS", clerk_tokens, clerks)):
        if given and explicit is None:
            logs.event("credentials.environment", logging.WARNING, variable=var, names=sorted(set(given.values())),
                       note="tokens from the environment: for a local run; deployed, use `jyotish reviewer add` "
                            "and `jyotish clerk add`, which store only a hash")
    limits = RateLimit(*(rate or (int(os.environ.get("JYOTISH_READINGS_PER_HOUR", 30)),
                                  int(os.environ.get("JYOTISH_READINGS_PER_DAY", 300)))))
    pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="reading")

    @asynccontextmanager
    async def lifespan(_):
        yield
        pool.shutdown(wait=False, cancel_futures=True)

    app = FastAPI(title="Jyotish readings", lifespan=lifespan)
    app.state.engine, app.state.pool, app.state.Session = engine, pool, Session

    @app.middleware("http")
    async def request_log(request: Request, call_next):
        """One line per request: method, path (no query string; a chart id replaced), status, ms."""
        import time
        t = time.perf_counter()
        response = await call_next(request)
        logs.event("http.request", method=request.method, path=logs.safe_path(request.url.path),
                   status=response.status_code, ms=round((time.perf_counter() - t) * 1000, 1))
        return response

    def credential(request: Request, kind: str, fallback: dict[str, str] | None = None) -> str:
        """The name a bearer token acts under as `kind` (reviewer, clerk, owner): an active token in
        the credentials table, or one from the local fallback (JYOTISH_REVIEWERS, JYOTISH_CLERKS); 401
        otherwise. Only the token's hash is compared with the table."""
        from .db import credential_name
        auth = request.headers.get("authorization", "")
        tok = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        name = None
        if tok:
            if fallback and tok in fallback:
                name = fallback[tok]
            else:
                with Session() as s:
                    name = credential_name(s, kind, tok)
        if name is None:
            raise HTTPException(status_code=401, detail=f"a {kind} token is required", headers={"WWW-Authenticate": "Bearer"})
        return name

    @app.exception_handler(RequestValidationError)
    async def refused(_: Request, exc: RequestValidationError) -> JSONResponse:
        """422 with where and why, never the values sent (a key sent by mistake is not echoed)."""
        return JSONResponse(status_code=422, content={"detail": [
            {"loc": list(e.get("loc", [])), "type": e.get("type"), "msg": e.get("msg")} for e in exc.errors()]})

    def update(reading_id: str, **fields) -> None:
        with Session.begin() as s:
            row = s.get(ReadingRow, reading_id)
            for k, v in fields.items():
                setattr(row, k, v)

    def stage(reading_id: str, log: list[str], name: str, keep: dict, **info) -> None:
        """Progress: the stage, its own info, and what is known so far (`keep`: the chart line
        and the header, from the chart step on), so a failed job still shows them."""
        log.append(name)
        update(reading_id, status="running", progress={"stage": name.split()[0], **info, **keep, "log": list(log)})

    def run(reading_id: str, req: ReadingRequest) -> None:
        from .narrate import NarrationError
        from .service import assess_birth, birth_key_of, chart_line, make_reading, reading_header
        log: list[str] = []
        keep: dict = {}
        try:
            stage(reading_id, log, "chart", keep)
            birth = BirthInput(**req.model_dump(include=set(BirthInput.model_fields)))
            chart, source, chart_id = assess_birth(birth)
            bkey = birth_key_of(birth)
            try:
                with Session.begin() as s:
                    if s.get(ChartRow, chart_id) is None:
                        s.add(ChartRow(id=chart_id, birth_key=bkey, birth=birth.model_dump(), engine=chart.meta.engine,
                                       document=chart.model_dump(mode="json")))
            except IntegrityError:
                # Two jobs for one chart at once (a comparison posts two): the other stored it first,
                # and a chart id is its document's key, so the stored row is this one.
                pass
            update(reading_id, chart_id=chart_id, birth_key=bkey)
            keep = {"chart": chart_line(chart, birth),
                    "header": reading_header(birth, req.question, chart, req.as_of, model_fixture, req.depth,
                                             req.writer_model, req.writer_effort)}
            stage(reading_id, log, "score", keep, chart_source=source,
                  tiers={n: a.tier for n, a in chart.scored.areas.items()} if chart.scored else None)

            def on(event: str, info: dict) -> None:
                stage(reading_id, log, f"{event} {info['attempt']}", keep, **info)

            def instant(first, page) -> None:
                # The instant page (2026-10-26): stored at once, the job still running, its narration pending.
                log.append("instant")
                update(reading_id, document=first.model_dump(mode="json"), page=page,
                       progress={"stage": "narration", **keep, "log": list(log)})
            reading, page = make_reading(birth, req.question, chart=chart, as_of=req.as_of, depth=req.depth,
                                         model_fixture=model_fixture, progress=on, writer_model=req.writer_model,
                                         writer_effort=req.writer_effort, chart_id=chart_id, on_instant=instant)
            log.append("done")
            update(reading_id, status="done", document=reading.model_dump(mode="json"), page=page,
                   progress={"stage": "done", "attempts": reading.attempts, "narration_complete": reading.narration_complete,
                             **keep, "log": list(log)})
            from .db import record_cost
            with Session.begin() as s:
                ledger = record_cost(s, s.get(ReadingRow, reading_id))
            logs.event("reading.done", reading_id=reading_id, depth=reading.depth, writer=reading.writer.get("model"),
                       effort=reading.writer.get("effort"), attempts=reading.attempts,
                       gaps=sum(len(a.narration_gaps) for a in reading.areas),
                       cost_usd=ledger.cost_usd if ledger else None, seconds=(reading.usage or {}).get("wall_seconds"))
        except NarrationError as e:
            log.append("failed")
            update(reading_id, status="failed", progress={"stage": "failed", **keep, "log": list(log)},
                   error={"message": str(e), "errors": list(e.errors)})
            logs.event("reading.failed", logging.WARNING, reading_id=reading_id, error=type(e).__name__)
        except Exception as e:                      # the job reports its failure; it never raises into the pool
            log.append("failed")
            message = f"{type(e).__name__}: {e}"
            if "Could not resolve authentication method" in str(e):
                message = ("The server has no model key: set ANTHROPIC_API_KEY in the environment the server "
                           "runs in (it is never sent by the browser).")
            update(reading_id, status="failed", progress={"stage": "failed", **keep, "log": list(log)},
                   error={"message": message})
            logs.event("reading.failed", logging.WARNING, reading_id=reading_id, error=type(e).__name__)

    @app.post("/readings", status_code=202, response_model=Accepted)
    def post_reading(req: ReadingRequest, request: Request) -> Accepted:
        """Queue a reading. Rate-limited per client and per day (`rate`): 429 with Retry-After."""
        wait = limits.check(request.client.host if request.client else "unknown")
        if wait is not None:
            logs.event("readings.rate_limited", logging.WARNING, retry_after=wait)
            raise HTTPException(status_code=429, detail="too many readings: try again later",
                                headers={"Retry-After": str(wait)})
        reading_id = uuid.uuid4().hex
        with Session.begin() as s:
            s.add(ReadingRow(id=reading_id, question=req.question, request=req.model_dump(), status="queued",
                             progress={"stage": "queued", "log": []}))
        pool.submit(run, reading_id, req)
        logs.event("reading.queued", reading_id=reading_id, depth=req.depth, writer=req.writer_model,
                   effort=req.writer_effort)
        return Accepted(id=reading_id, status="queued", url=f"/readings/{reading_id}")

    def chart_of(chart_id: str):
        from .models import Chart
        with Session() as s:
            row = s.get(ChartRow, chart_id)
            if row is None:
                raise HTTPException(status_code=404, detail="no such chart")
            return Chart.model_validate(row.document)

    def with_sheets(document: dict | None, chart_id: str | None) -> dict | None:
        """A done reading's document with every area's technical sheet (jyotish.sheet): a reading stored
        before the sheet existed gets it from its chart as it is read (not stored; the payload is cached)."""
        areas = (document or {}).get("areas") or []
        if not areas or all(a.get("sheet") for a in areas) or not chart_id:
            return document
        from datetime import date as _date
        from .sheet import sheets
        made = sheets(chart_of(chart_id), _date.fromisoformat(document["as_of"]), [a["name"] for a in areas],
                      {a["name"]: a.get("judgements") or [] for a in areas})
        return dict(document, areas=[a if a.get("sheet") else dict(a, sheet=made.get(a["name"])) for a in areas])

    @app.get("/charts/{chart_id}/chart.svg")
    def chart_svg(chart_id: str, vargas: str = "D1,D9,D10") -> Response:
        """D1, D9 and D10 (or those named in `vargas`) in the North-Indian style, drawn by the
        engine from the stored chart."""
        from .display import svg
        try:
            drawing = svg(chart_of(chart_id), tuple(v.strip() for v in vargas.split(",") if v.strip()))
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return Response(drawing, media_type="image/svg+xml")

    @app.get("/charts/{chart_id}/tables.json")
    def chart_tables(chart_id: str, as_of: str | None = None) -> dict:
        """Planets, Vimshottari to the pratyantar (current period marked at `as_of`, default
        today), Shadbala, Ashtakavarga and Bhava Bala, from the stored chart."""
        from datetime import date as _date
        from .display import tables
        try:
            day = _date.fromisoformat(as_of) if as_of else None
        except ValueError:
            raise HTTPException(status_code=422, detail="as_of must be YYYY-MM-DD")
        return tables(chart_of(chart_id), day)

    # --- the review step ----------------------------------------------------------------

    def reviewer(request: Request) -> str:
        return credential(request, "reviewer", tokens)

    def done_reading(s, reading_id: str):
        from .narrate import Reading
        row = s.get(ReadingRow, reading_id)
        if row is None:
            raise HTTPException(status_code=404, detail="no such reading")
        # A running reading with its instant page (narration pending) can be opened too (2026-10-26).
        if row.document is None or row.status not in ("done", "running"):
            raise HTTPException(status_code=409, detail=f"the reading is {row.status}, not done")
        return row, Reading(**row.document)

    def log(s, row, who: str, action: str, seen: bool = True, **fields) -> None:
        s.add(ReviewRow(reading_id=row.id, chart_id=row.chart_id, reviewer_id=who, action=action, **fields))
        if seen and row.chart_id and s.get(ExclusionRow, row.chart_id) is None:
            s.add(ExclusionRow(chart_id=row.chart_id, birth_key=row.birth_key, reason="reading seen in review",
                               reviewer_id=who, reading_id=row.id))

    def save(s, row, reading) -> None:
        from .page import render
        row.document = reading.model_dump(mode="json")
        row.page = render(reading, chart_of(row.chart_id))

    fact_cache: dict = {}

    def answers_of(s, row, who: str) -> list[dict]:
        return [{"step": r.step, "area": r.area, "answer": r.answer, "mode": r.mode, "comment": r.comment,
                 "at": r.created_at.isoformat()}
                for r in s.query(ReviewRow).filter_by(reading_id=row.id, reviewer_id=who, action="answer")
                .order_by(ReviewRow.id)]

    def shown_areas(s, row, reading, who: str, mode: str) -> set[str]:
        from .review import revealed
        names = {a.name for a in reading.areas}
        return names if mode == "review" else revealed(row.document["areas"], answers_of(s, row, who))

    def area_facts_of(row, reading) -> dict:
        from .review import facts
        names = [a.name for a in reading.areas]
        key = (row.chart_id, tuple(names), reading.as_of)
        if key not in fact_cache:
            from datetime import date as _date
            fact_cache[key] = facts(chart_of(row.chart_id), names, _date.fromisoformat(reading.as_of))
        return fact_cache[key]

    def review_view(s, row, reading, who: str, mode: str = "review") -> dict:
        """The reviewer's view. Each sentence carries its plain words and the chart facts it rests
        on; in blind mode an area not yet answered from the chart alone is withheld, with its
        sentences, and so are the page, the summary and the log."""
        from .review import plain, redact, sentence_facts, units
        names = [a.name for a in reading.areas]
        area_facts = area_facts_of(row, reading)
        shown = shown_areas(s, row, reading, who, mode)
        us = [dict(u, plain=plain(u["text"]), facts=sentence_facts(u["text"], area_facts.get(u["area"], [])))
              for u in units(reading) if (u["area"] in shown if u["area"] else len(shown) == len(names))]
        intro_done = s.query(ReviewRow).filter_by(reviewer_id=who, action="answer", step="intro").first() is not None
        guided = {"reviewer": who, "mode": mode, "intro_done": intro_done, "answers": answers_of(s, row, who),
                  "shown": sorted(shown), "units": us}
        # A reading in a comparison this reviewer has not answered shows no settings here either (F7).
        document = blind(row.document) if comparison_pending(s, row, who) else with_sheets(row.document, row.chart_id)
        if mode == "blind":
            return {"id": row.id, "chart_id": row.chart_id, "review_status": row.review_status,
                    "reading": redact(document, shown), **guided}
        rows = list(s.query(ReviewRow).filter_by(reading_id=row.id).order_by(ReviewRow.id))
        # What changed the reading (opens, edits, notes, approvals) is everyone's history. Another
        # reviewer's answers, verdicts and words are their judgement, given blind to this one's, and
        # are not shown here (SPEC Layer 6b; review 2026-10-23, F10): the export (jyotish
        # export-reviews) is where the judgements meet.
        shown = [r for r in rows if r.reviewer_id == who or r.action in ("open", "edit", "note", "approve")]
        history = [{"action": r.action, "target": r.target, "reviewer": r.reviewer_id, "accepted": r.accepted,
                    "before": r.before, "after": r.after, "errors": r.errors, "area": r.area, "verdict": r.verdict,
                    "reason": r.reason, "step": r.step, "answer": r.answer, "mode": r.mode, "comment": r.comment,
                    "at": r.created_at.isoformat()} for r in shown]
        verdicts = {r.area: {"verdict": r.verdict, "reason": r.reason, "by": r.reviewer_id, "at": r.created_at.isoformat()}
                    for r in rows if r.reviewer_id == who
                    and (r.action == "verdict" or (r.action == "answer" and r.step == "match"))}   # the latest per area, this reviewer's
        return {"id": row.id, "chart_id": row.chart_id, "review_status": row.review_status, "verdicts": verdicts,
                "reading": document, "page": None if document is not row.document else row.page, "history": history,
                **guided}

    def blind_gate(s, row, reading, who: str, mode: str, area: str | None) -> None:
        if mode == "blind" and area is not None and area not in shown_areas(s, row, reading, who, mode):
            raise HTTPException(status_code=409, detail=f"answer {area} from the chart alone first")

    @app.get("/review/{reading_id}", include_in_schema=False)
    def review_page(reading_id: str):
        from fastapi.responses import FileResponse
        if web_dir is None or not (Path(web_dir) / "review.html").exists():
            raise HTTPException(status_code=404, detail="no review page")
        return FileResponse(Path(web_dir) / "review.html")

    @app.get("/readings/{reading_id}/review")
    def get_review(reading_id: str, request: Request, mode: Literal["review", "blind"] = "review") -> dict:
        """The reading as the reviewer sees it, every sentence with its target; opening it logs
        the reviewer and (outside blind mode) excludes the chart from the blind learning set."""
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            log(s, row, who, "open", seen=mode == "review", mode=mode)
            s.flush()
            return review_view(s, row, reading, who, mode)

    @app.post("/readings/{reading_id}/review/answer")
    def post_answer(reading_id: str, req: AnswerRequest, request: Request) -> dict:
        """One answer of the guided review, logged with its step, area, answer, mode, reviewer and
        time. In blind mode the reviewer's own reading and period come before the engine's is
        shown, and cannot be changed after."""
        from .review import AREA_STEPS, check_answer
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            names = [a.name for a in reading.areas]
            try:
                check_answer(req.step, req.answer)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            if req.step in AREA_STEPS and req.area not in names:
                raise HTTPException(status_code=422, detail=f"no area {req.area!r} in this reading")
            if req.step in ("intro", "whole") and req.area is not None:
                raise HTTPException(status_code=422, detail=f"the {req.step} step belongs to no area")
            if req.step == "whole" and len(shown_areas(s, row, reading, who, req.mode)) < len(names):
                raise HTTPException(status_code=409, detail="answer every area before the reading as a whole")
            blind_step = req.step.startswith("blind_")
            if blind_step and req.mode != "blind":
                raise HTTPException(status_code=422, detail=f"{req.step} is asked in blind mode only")
            if blind_step and req.area in shown_areas(s, row, reading, who, req.mode):
                raise HTTPException(status_code=409, detail=f"{req.area} is already shown: answered from the chart alone")
            if req.step in AREA_STEPS and not blind_step:
                blind_gate(s, row, reading, who, req.mode, req.area)
            log(s, row, who, "answer", seen=req.mode == "review", step=req.step, area=req.area, answer=req.answer,
                mode=req.mode, target=f"{req.step}:{req.area}" if req.area else req.step,
                verdict=req.answer if req.step == "match" else None,
                comment=req.comment.strip() if req.comment and req.comment.strip() else None)
            s.flush()
            if req.mode == "blind" and req.area in shown_areas(s, row, reading, who, req.mode) \
                    and s.get(ExclusionRow, row.chart_id) is None:     # the reading is now seen
                s.add(ExclusionRow(chart_id=row.chart_id, birth_key=row.birth_key, reason="reading seen in review",
                                   reviewer_id=who, reading_id=row.id))
                s.flush()
            return review_view(s, row, reading, who, req.mode)

    @app.post("/readings/{reading_id}/review/edit")
    def post_edit(reading_id: str, req: EditRequest, request: Request,
                  mode: Literal["review", "blind"] = "review") -> dict:
        """An edited sentence: accepted only if it passes the validator and the checker. The
        result carries the refusal's reasons as codes the review page words plainly."""
        from .review import _parse, apply_edit, check_edit, units, with_tags
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            before = next((u["text"] for u in units(reading) if u["target"] == req.target), None)
            if before is None:
                raise HTTPException(status_code=404, detail=f"no sentence {req.target!r} in this reading")
            blind_gate(s, row, reading, who, mode, _parse(req.target)[1])
            text_ = with_tags(before, req.text) if req.keep_tags else req.text
            checker = review_checker or app.state.__dict__.setdefault("live_checker", _live_checker())
            try:
                result = check_edit(reading, chart_of(row.chart_id), req.target, text_, checker)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            from .review import sentence_facts
            area = _parse(req.target)[1]
            # The facts the page showed beside the sentence, kept with the edit: the export reads them
            # rather than recomputing them with a later engine (review 2026-10-23).
            shown = sentence_facts(before, area_facts_of(row, reading).get(area, [])) if area else []
            log(s, row, who, "edit", target=req.target, before=before, after=text_.strip(),
                accepted=result["accepted"], errors=result["errors"], mode=mode, area=area, facts=shown)
            if result["accepted"]:
                reading = apply_edit(reading, req.target, text_, who)
                save(s, row, reading)
            s.flush()
            return dict(result, review=review_view(s, row, reading, who, mode))

    @app.post("/readings/{reading_id}/review/note")
    def post_note(reading_id: str, req: NoteRequest, request: Request,
                  mode: Literal["review", "blind"] = "review") -> dict:
        """The astrologer's note on an area: the reviewer's words, stored and shown apart, never checked."""
        from .review import add_note
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            if req.area in [a.name for a in reading.areas]:
                blind_gate(s, row, reading, who, mode, req.area)
            try:
                reading = add_note(reading, req.area, req.text, who)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            log(s, row, who, "note", target=f"note:{req.area}", after=req.text.strip(), mode=mode)
            save(s, row, reading)
            s.flush()
            return review_view(s, row, reading, who, mode)

    @app.post("/readings/{reading_id}/review/verdict")
    def post_verdict(reading_id: str, req: VerdictRequest, request: Request) -> dict:
        """The reviewer's verdict on an area (agree, partly, disagree, and why when not agree),
        logged with the area, reviewer and time. Judgement data only: the reading and its page
        are not touched, so the client sees nothing of it."""
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            if req.area not in [a.name for a in reading.areas]:
                raise HTTPException(status_code=422, detail=f"no area {req.area!r} in this reading")
            log(s, row, who, "verdict", target=f"verdict:{req.area}", area=req.area, verdict=req.verdict,
                reason=req.reason)
            s.flush()
            return review_view(s, row, reading, who)

    @app.post("/readings/{reading_id}/review/approve")
    def post_approve(reading_id: str, request: Request, mode: Literal["review", "blind"] = "review") -> dict:
        """Mark the reading reviewed: the client-facing page then says by whom."""
        from .review import approve
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            if len(shown_areas(s, row, reading, who, mode)) < len(reading.areas):
                raise HTTPException(status_code=409, detail="every area must be answered before approval")
            reading = approve(reading, who)
            row.review_status = "reviewed"
            log(s, row, who, "approve", mode=mode)
            save(s, row, reading)
            s.flush()
            return review_view(s, row, reading, who, mode)

    # --- the blind comparison (scripts/compare_readings.py) -------------------------------------

    def compare_rows(s, a: str, b: str, who: str = "a reviewer"):
        if a == b:
            raise HTTPException(status_code=422, detail="a comparison needs two different readings")
        rows = [done_reading(s, x)[0] for x in (a, b)]
        if rows[0].chart_id != rows[1].chart_id or rows[0].question != rows[1].question:
            raise HTTPException(status_code=422, detail="the two readings are not of the same chart and question")
        add_comparison(s, a, b, who)                              # each is now known to be in this comparison
        s.flush()
        return rows

    def comparison_pending(s, row, who: str | None) -> bool:
        """A reading in a comparison this reviewer (or, with none, anyone) has not answered: its
        settings are withheld wherever it is shown (review F7)."""
        others = compared_with(s, row.id)
        if not others:
            return False
        return who is None or any(compare_answer_of(s, row.id, o, who) is None for o in others)

    def compare_answer_of(s, a: str, b: str, who: str):
        target = "compare:" + ":".join(sorted((a, b)))
        return s.query(ReviewRow).filter_by(action="compare", target=target, reviewer_id=who).first()

    def compare_view(s, a: str, b: str, who: str) -> dict:
        rows = {r.id: r for r in compare_rows(s, a, b)}
        shown = dict(zip(("A", "B"), compare_order(a, b, who)))
        view = {"readings": {label: blind(rows[rid].document) for label, rid in shown.items()}, "answer": None}
        ans = compare_answer_of(s, a, b, who)
        if ans is not None:                       # revealed only once answered
            view["answer"] = {"choice": ans.answer["choice"], "why": ans.comment, "reviewer": who,
                              "at": ans.created_at.isoformat()}
            view["reveal"] = {label: dict(settings_of(rows[rid].document), reading_id=rid) for label, rid in shown.items()}
        return view

    @app.get("/compare/{a}/{b}", include_in_schema=False)
    def compare_page(a: str, b: str):
        from fastapi.responses import FileResponse
        if web_dir is None or not (Path(web_dir) / "compare.html").exists():
            raise HTTPException(status_code=404, detail="no compare page")
        return FileResponse(Path(web_dir) / "compare.html")

    @app.get("/compare/{a}/{b}/view")
    def get_compare(a: str, b: str, request: Request) -> dict:
        """The two readings as A and B with their settings withheld (which is A is fixed per
        reviewer, compare_order); after this reviewer has answered, the answer and the settings.
        Opening it logs the reviewer and excludes the chart from the blind learning set."""
        who = reviewer(request)
        with Session.begin() as s:
            rows = compare_rows(s, a, b, who)
            log(s, rows[0], who, "open", mode="compare", target="compare:" + ":".join(sorted((a, b))))
            s.flush()
            return compare_view(s, a, b, who)

    @app.post("/compare/{a}/{b}/answer")
    def post_compare(a: str, b: str, req: CompareAnswer, request: Request) -> dict:
        """"Which reading would you give the client, and why": logged to the judgements with the
        reviewer, both readings, which was shown as A and each one's settings. One answer per
        reviewer and pair: the settings are revealed by it, so a second would not be blind."""
        who = reviewer(request)
        with Session.begin() as s:
            rows = {r.id: r for r in compare_rows(s, a, b, who)}
            if compare_answer_of(s, a, b, who) is not None:
                raise HTTPException(status_code=409, detail="this comparison is answered: the settings are shown")
            shown = dict(zip(("A", "B"), compare_order(a, b, who)))
            first = rows[sorted((a, b))[0]]
            log(s, first, who, "compare", mode="blind", target="compare:" + ":".join(sorted((a, b))),
                answer={"choice": req.choice, "chosen": shown[req.choice], "shown_as": shown,
                        "settings": {rid: settings_of(r.document) for rid, r in rows.items()}},
                comment=req.why.strip())
            s.flush()
            return compare_view(s, a, b, who)

    # --- outcome capture (outcomes.py): the clerk's sheet over HTTP, the same checks as the CLI ---

    @app.post("/outcomes")
    def post_outcomes(req: OutcomeRows, request: Request) -> dict:
        """Sheet rows as JSON. Refused rows come back with their reasons and are not stored; the
        rest are. A clerk's token (JYOTISH_CLERKS) is required; rows are entered under its id."""
        from .outcomes import import_rows
        clerk = credential(request, "clerk", clerk_tokens)
        with Session.begin() as s:
            res = import_rows(s, req.rows, entered_by=clerk)
            return {"accepted": res.accepted, "subjects_created": res.subjects_created, "refused": res.refused}

    @app.get("/costs/daily")
    def costs_daily(request: Request, days: int = 30) -> list[dict]:
        """The owner's daily totals from the ledger, newest day first: readings, the writer's, the
        checker's and the client's layer's tokens, and the cost (a day with a reading on an unpriced
        model says how many)."""
        from sqlalchemy import func
        from .db import LedgerRow
        credential(request, "owner")
        with Session() as s:
            days_seen = [d for (d,) in s.query(LedgerRow.day).distinct().order_by(LedgerRow.day.desc())
                         .limit(max(1, min(days, 366)))]
            out = []
            for day in days_seen:
                rows = s.query(LedgerRow).filter_by(day=day).all()
                total = lambda side, k: sum(int((getattr(r, side) or {}).get(k) or 0) for r in rows)
                out.append({"day": day, "readings": len(rows), "replayed": sum(r.replayed for r in rows),
                            "cost_usd": round(sum(r.cost_usd or 0.0 for r in rows), 4),
                            "unpriced": sum(r.cost_usd is None for r in rows),
                            "writer_tokens": {k: total("writer_tokens", k) for k in ("input_tokens", "output_tokens",
                                              "cache_read_input_tokens", "cache_creation_input_tokens")},
                            "checker_tokens": {k: total("checker_tokens", k) for k in ("input_tokens", "output_tokens",
                                               "cache_read_input_tokens", "cache_creation_input_tokens")},
                            "client_tokens": {k: total("client_tokens", k) for k in ("input_tokens", "output_tokens",
                                              "cache_read_input_tokens", "cache_creation_input_tokens")}})
            return out

    @app.get("/costs/readings")
    def costs_readings(request: Request, day: str) -> list[dict]:
        """The owner's per-reading ledger for one day (YYYY-MM-DD, UTC)."""
        from .db import LedgerRow
        credential(request, "owner")
        with Session() as s:
            return [{"reading_id": r.reading_id, "depth": r.depth, "writer_model": r.writer_model,
                     "checker_model": r.checker_model, "writer_tokens": r.writer_tokens,
                     "checker_tokens": r.checker_tokens, "writer_calls": r.writer_calls, "checker_calls": r.checker_calls,
                     "client_model": r.client_model, "client_tokens": r.client_tokens, "client_calls": r.client_calls,
                     "backends": r.backends, "cost_usd": r.cost_usd, "seconds": r.seconds, "replayed": r.replayed}
                    for r in s.query(LedgerRow).filter_by(day=day).order_by(LedgerRow.created_at)]

    @app.get("/health")
    def health() -> JSONResponse:
        """For a load balancer and for whoever runs the service: the engine (version and hash: the
        hash changes with any source, data table or rule file), the database (reachable, its dialect,
        its Alembic revision against the head), whether narration is live, replayed or without a key
        (never the key), and where the source is (AGPL-3.0 section 13: docs/deploy.md). 503 when the
        database cannot be reached; the database URL is never shown."""
        from .cache import engine_hash
        from .db import current_revision, head_revision
        from . import __version__
        from .narrate import backends_status
        backends = backends_status()                            # each role's provider, host, model, readiness
        db: dict[str, Any] = {"dialect": engine.dialect.name}
        try:
            db |= {"ok": True, "revision": current_revision(engine), "head": head_revision()}
        except Exception as e:                                  # unreachable: say so, not where
            db |= {"ok": False, "error": type(e).__name__}
        body = {"status": "ok" if db["ok"] else "degraded",
                "engine": {"version": __version__, "hash": engine_hash()}, "database": db,
                "narration": ("fixture" if model_fixture else "live" if all(b["ready"] for b in backends.values())
                              else "no key"),
                "backends": backends,
                "source": os.environ.get("JYOTISH_SOURCE_URL") or None}
        return JSONResponse(body, status_code=200 if db["ok"] else 503)

    @app.get("/source", include_in_schema=False)
    def source():
        """The program's source (AGPL-3.0 section 13, Swiss Ephemeris's licence): JYOTISH_SOURCE_URL."""
        from fastapi.responses import RedirectResponse
        url = os.environ.get("JYOTISH_SOURCE_URL")
        if not url:
            raise HTTPException(status_code=404, detail="JYOTISH_SOURCE_URL is not set on this server")
        return RedirectResponse(url)

    @app.get("/places")
    def get_places(q: str, limit: int = 10) -> list[dict]:
        """Places for the birth form's Place field (GeoNames cities15000, CC BY 4.0)."""
        from .places import search
        return search(q, max(1, min(limit, 20)))

    @app.get("/readings/{reading_id}", response_model=ReadingStatus, response_model_exclude_none=True)
    def get_reading(reading_id: str, request: Request) -> ReadingStatus:
        """The reading and its page. A reading in a blind comparison needs a reviewer token, and until
        that reviewer has answered the comparison it comes as the blind view: no settings, no page
        (whose header carries the command) and no progress beyond its stage (review F7)."""
        with Session() as s:
            row = s.get(ReadingRow, reading_id)
            if row is None:
                raise HTTPException(status_code=404, detail="no such reading")
            if compared_with(s, row.id):
                who = reviewer(request)
                if comparison_pending(s, row, who):
                    return ReadingStatus(id=row.id, status=row.status, progress={"stage": row.progress.get("stage")},
                                         chart_id=row.chart_id, question=row.question, created_at=row.created_at,
                                         updated_at=row.updated_at, reading=blind(row.document) if row.document else None,
                                         page=None, error=row.error)
            return ReadingStatus(id=row.id, status=row.status, progress=row.progress, chart_id=row.chart_id,
                                 question=row.question, created_at=row.created_at, updated_at=row.updated_at,
                                 reading=with_sheets(row.document, row.chart_id) if row.status == "done" else row.document,
                                 page=row.page, error=row.error,
                                 review_status=row.review_status if row.status == "done" else None)

    # Static files last, so /readings is never shadowed.
    if examples_dir is not None and Path(examples_dir).is_dir():
        app.mount("/examples", StaticFiles(directory=examples_dir), name="examples")
    if web_dir is not None and Path(web_dir).is_dir():
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
    return app


def _live_checker():
    from .narrate import CONFIG, AnthropicChecker
    return AnthropicChecker(CONFIG)


def __getattr__(name: str):
    """`jyotish.api:app` for uvicorn, made on first use (so importing the module opens no database)."""
    if name == "app":
        global app
        app = create_app()
        return app
    raise AttributeError(name)
