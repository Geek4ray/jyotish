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

Run:  .venv/bin/uvicorn jyotish.api:app      then open http://127.0.0.1:8000/"""

from __future__ import annotations

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
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from .service import BirthInput

DOCUMENT = JSON().with_variant(JSONB(), "postgresql")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ChartRow(Base):
    """One chart object per chart id (SPEC data schema), with the birth data it came from."""
    __tablename__ = "charts"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    birth_key: Mapped[str | None] = mapped_column(String(64), nullable=True)   # cache.birth_key: the birth, no engine
    birth: Mapped[dict] = mapped_column(DOCUMENT)
    engine: Mapped[str] = mapped_column(String(32))
    document: Mapped[dict] = mapped_column(DOCUMENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ReadingRow(Base):
    """One reading job: its request, status and progress, then the reading and its page."""
    __tablename__ = "readings"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    chart_id: Mapped[str | None] = mapped_column(ForeignKey("charts.id"), nullable=True)
    birth_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    request: Mapped[dict] = mapped_column(DOCUMENT)
    status: Mapped[str] = mapped_column(String(16))                 # queued | running | done | failed
    progress: Mapped[dict] = mapped_column(DOCUMENT)
    document: Mapped[dict | None] = mapped_column(DOCUMENT, nullable=True)
    page: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[dict | None] = mapped_column(DOCUMENT, nullable=True)
    review_status: Mapped[str] = mapped_column(String(16), default="draft", server_default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ReviewRow(Base):
    """One reviewer action on a reading: open, edit (accepted or not, with the checks' errors),
    note, approve. The judgement data of the review step."""
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reading_id: Mapped[str] = mapped_column(ForeignKey("readings.id"))
    chart_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reviewer_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(16))                # open | edit | note | approve | verdict | answer
    target: Mapped[str | None] = mapped_column(String(200), nullable=True)
    before: Mapped[str | None] = mapped_column(Text, nullable=True)
    after: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    errors: Mapped[list | None] = mapped_column(DOCUMENT, nullable=True)
    area: Mapped[str | None] = mapped_column(String(32), nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(16), nullable=True)      # agree | partly | disagree
    reason: Mapped[str | None] = mapped_column(String(32), nullable=True)       # why, when not agree
    step: Mapped[str | None] = mapped_column(String(32), nullable=True)         # a guided-review step
    answer: Mapped[Any | None] = mapped_column(DOCUMENT, nullable=True)         # its answer
    mode: Mapped[str | None] = mapped_column(String(16), nullable=True)         # review | blind
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)            # "in your own words", never shown
    facts: Mapped[list | None] = mapped_column(DOCUMENT, nullable=True)         # an edit: the chart facts shown beside the sentence then
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExclusionRow(Base):
    """A chart whose reading a judge has seen: excluded from the blind learning set for good."""
    __tablename__ = "exclusions"
    chart_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    birth_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str] = mapped_column(String(64))
    reviewer_id: Mapped[str] = mapped_column(String(64))
    reading_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


# --- outcome capture (SPEC Layer 6, outcome dataset; outcomes.py) ---------------------------------

class ConsentRow(Base):
    """A subject's consent: purpose-limited to validation, withdrawable (DPDP Act 2023)."""
    __tablename__ = "consents"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    subject_id: Mapped[str] = mapped_column(String(64))
    form_version: Mapped[str] = mapped_column(String(32))
    track: Mapped[str] = mapped_column(String(16))                      # backlog | new
    given_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(64))


class SubjectRow(Base):
    """A person whose dated events are recorded. `chart_id` is the engine's chart key for the birth
    data at the first import (it carries the engine hash and the accuracy class); `birth_key` is the
    birth as a person (cache.birth_key), by which the subject's rows are matched and erased.
    Rectified charts are refused at import (SPEC Layer 6: excluded from every test)."""
    __tablename__ = "subjects"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    chart_id: Mapped[str] = mapped_column(String(64))
    birth_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    birth: Mapped[dict] = mapped_column(DOCUMENT)                       # date, time, tz, lat, lon, place, node
    accuracy: Mapped[str] = mapped_column(String(16))
    sex: Mapped[str] = mapped_column(String(16))
    region: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(16))                     # file | interview | follow_up | public
    rectified: Mapped[bool] = mapped_column(Boolean, default=False)
    seen_by_astrologer: Mapped[bool] = mapped_column(Boolean, default=False)
    household_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    birthplace_cluster: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class EventRow(Base):
    """An outcome triple (event type, age at event, censor age); no age at event means the event
    had not happened by the censor age. `after` is true when it was entered once a reading had
    been shown, and such events are excluded from every test."""
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"))
    event_type: Mapped[str] = mapped_column(String(32))
    age_at_event: Mapped[float | None] = mapped_column(Float, nullable=True)
    censor_age: Mapped[float] = mapped_column(Float)
    value: Mapped[dict | None] = mapped_column(DOCUMENT, nullable=True)  # occupation: isco08, isei
    self_report: Mapped[bool] = mapped_column(Boolean, default=False)
    entered_by: Mapped[str] = mapped_column(String(64))
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    before_reading: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    after: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_id: Mapped[str] = mapped_column(String(64))


class ErasureRow(Base):
    """A right-of-erasure request carried out: who, when, and how many rows went. No birth data."""
    __tablename__ = "erasures"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subject_id: Mapped[str] = mapped_column(String(64))
    erased_by: Mapped[str] = mapped_column(String(64))
    counts: Mapped[dict] = mapped_column(DOCUMENT)
    erased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


def excluded_charts(session) -> set[str]:
    """The chart ids the Layer 6b learning set must leave out (their readings were seen)."""
    return {r.chart_id for r in session.query(ExclusionRow).all()}


def _add_missing_columns(engine) -> None:
    """create_all makes new tables but never alters old ones: add columns a newer model has, then
    fill the birth keys of rows stored before they existed."""
    insp = inspect(engine)
    for table in Base.metadata.sorted_tables:
        if not insp.has_table(table.name):
            continue
        have = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name not in have:
                default = f" DEFAULT '{col.server_default.arg}'" if col.server_default is not None else ""
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {col.name} "
                                      f"{col.type.compile(engine.dialect)}{default}"))
    _backfill_birth_keys(engine)


def _backfill_birth_keys(engine) -> None:
    """Charts and subjects stored before the birth key existed get theirs from their birth data,
    readings and exclusions from their chart; a record that cannot be keyed is left as it is."""
    from .cache import birth_key_of_record
    with sessionmaker(engine)() as s:
        for row in list(s.query(ChartRow).filter(ChartRow.birth_key.is_(None))) + \
                list(s.query(SubjectRow).filter(SubjectRow.birth_key.is_(None))):
            try:
                row.birth_key = birth_key_of_record(row.birth)
            except (KeyError, ValueError, TypeError):
                pass
        s.flush()
        keys = dict(s.query(ChartRow.id, ChartRow.birth_key))
        for r in s.query(ReadingRow).filter(ReadingRow.birth_key.is_(None), ReadingRow.chart_id.isnot(None)):
            r.birth_key = keys.get(r.chart_id)
        for x in s.query(ExclusionRow).filter(ExclusionRow.birth_key.is_(None)):
            x.birth_key = keys.get(x.chart_id)
        s.commit()


class ReadingRequest(BirthInput):
    """Birth data, the question, and optionally the date the reading is for."""
    model_config = ConfigDict(extra="forbid")
    question: str
    as_of: str | None = None
    depth: Literal["curious", "learner", "astrologer"] = "curious"


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


def create_app(database_url: str | None = None, *, model_fixture: str | None = None, workers: int = 2,
               web_dir: Path | None = REPO / "web", examples_dir: Path | None = REPO / "examples",
               reviewers: dict[str, str] | None = None, review_checker=None,
               clerks: dict[str, str] | None = None) -> FastAPI:
    """The app. `model_fixture` replays a recorded narration instead of calling the model
    (offline tests); it is never taken from a request. The website and the examples are
    mounted when their directories exist (a source checkout). `reviewers` (token -> reviewer
    id) defaults to JYOTISH_REVIEWERS; `review_checker` checks edited sentences (default the
    live AnthropicChecker; tests pass a stub)."""
    url = database_url or os.environ.get("JYOTISH_DATABASE_URL", "sqlite:///jyotish.db")
    engine = create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {})
    Base.metadata.create_all(engine)
    _add_missing_columns(engine)
    Session = sessionmaker(engine, expire_on_commit=False)
    tokens = reviewers if reviewers is not None else reviewers_from_env()
    clerk_tokens = clerks if clerks is not None else reviewers_from_env("JYOTISH_CLERKS")
    pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="reading")

    @asynccontextmanager
    async def lifespan(_):
        yield
        pool.shutdown(wait=False, cancel_futures=True)

    app = FastAPI(title="Jyotish readings", lifespan=lifespan)
    app.state.engine, app.state.pool, app.state.Session = engine, pool, Session

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
            with Session.begin() as s:
                if s.get(ChartRow, chart_id) is None:
                    s.add(ChartRow(id=chart_id, birth_key=bkey, birth=birth.model_dump(), engine=chart.meta.engine,
                                   document=chart.model_dump(mode="json")))
            update(reading_id, chart_id=chart_id, birth_key=bkey)
            keep = {"chart": chart_line(chart, birth),
                    "header": reading_header(birth, req.question, chart, req.as_of, model_fixture, req.depth)}
            stage(reading_id, log, "score", keep, chart_source=source,
                  tiers={n: a.tier for n, a in chart.scored.areas.items()} if chart.scored else None)

            def on(event: str, info: dict) -> None:
                stage(reading_id, log, f"{event} {info['attempt']}", keep, **info)
            reading, page = make_reading(birth, req.question, chart=chart, as_of=req.as_of, depth=req.depth,
                                         model_fixture=model_fixture, progress=on)
            log.append("done")
            update(reading_id, status="done", document=reading.model_dump(mode="json"), page=page,
                   progress={"stage": "done", "attempts": reading.attempts, "narration_complete": reading.narration_complete,
                             **keep, "log": list(log)})
        except NarrationError as e:
            log.append("failed")
            update(reading_id, status="failed", progress={"stage": "failed", **keep, "log": list(log)},
                   error={"message": str(e), "errors": list(e.errors)})
        except Exception as e:                      # the job reports its failure; it never raises into the pool
            log.append("failed")
            message = f"{type(e).__name__}: {e}"
            if "Could not resolve authentication method" in str(e):
                message = ("The server has no model key: set ANTHROPIC_API_KEY in the environment the server "
                           "runs in (it is never sent by the browser).")
            update(reading_id, status="failed", progress={"stage": "failed", **keep, "log": list(log)},
                   error={"message": message})

    @app.post("/readings", status_code=202, response_model=Accepted)
    def post_reading(req: ReadingRequest) -> Accepted:
        reading_id = uuid.uuid4().hex
        with Session.begin() as s:
            s.add(ReadingRow(id=reading_id, question=req.question, request=req.model_dump(), status="queued",
                             progress={"stage": "queued", "log": []}))
        pool.submit(run, reading_id, req)
        return Accepted(id=reading_id, status="queued", url=f"/readings/{reading_id}")

    def chart_of(chart_id: str):
        from .models import Chart
        with Session() as s:
            row = s.get(ChartRow, chart_id)
            if row is None:
                raise HTTPException(status_code=404, detail="no such chart")
            return Chart.model_validate(row.document)

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
        auth = request.headers.get("authorization", "")
        tok = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not tok or tok not in tokens:
            raise HTTPException(status_code=401, detail="a reviewer token is required",
                                headers={"WWW-Authenticate": "Bearer"})
        return tokens[tok]

    def done_reading(s, reading_id: str):
        from .narrate import Reading
        row = s.get(ReadingRow, reading_id)
        if row is None:
            raise HTTPException(status_code=404, detail="no such reading")
        if row.status != "done" or row.document is None:
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
        if mode == "blind":
            return {"id": row.id, "chart_id": row.chart_id, "review_status": row.review_status,
                    "reading": redact(row.document, shown), **guided}
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
                "reading": row.document, "page": row.page, "history": history, **guided}

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

    # --- outcome capture (outcomes.py): the clerk's sheet over HTTP, the same checks as the CLI ---

    @app.post("/outcomes")
    def post_outcomes(req: OutcomeRows, request: Request) -> dict:
        """Sheet rows as JSON. Refused rows come back with their reasons and are not stored; the
        rest are. A clerk's token (JYOTISH_CLERKS) is required; rows are entered under its id."""
        from .outcomes import import_rows
        auth = request.headers.get("authorization", "")
        tok = auth[7:].strip() if auth.lower().startswith("bearer ") else ""
        if not tok or tok not in clerk_tokens:
            raise HTTPException(status_code=401, detail="a clerk token is required", headers={"WWW-Authenticate": "Bearer"})
        with Session.begin() as s:
            res = import_rows(s, req.rows, entered_by=clerk_tokens[tok])
            return {"accepted": res.accepted, "subjects_created": res.subjects_created, "refused": res.refused}

    @app.get("/places")
    def get_places(q: str, limit: int = 10) -> list[dict]:
        """Places for the birth form's Place field (GeoNames cities15000, CC BY 4.0)."""
        from .places import search
        return search(q, max(1, min(limit, 20)))

    @app.get("/readings/{reading_id}", response_model=ReadingStatus, response_model_exclude_none=True)
    def get_reading(reading_id: str) -> ReadingStatus:
        with Session() as s:
            row = s.get(ReadingRow, reading_id)
            if row is None:
                raise HTTPException(status_code=404, detail="no such reading")
            return ReadingStatus(id=row.id, status=row.status, progress=row.progress, chart_id=row.chart_id,
                                 question=row.question, created_at=row.created_at, updated_at=row.updated_at,
                                 reading=row.document, page=row.page, error=row.error,
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
