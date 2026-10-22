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
Every open, edit, note and approval is logged in `reviews` with chart id, reviewer id and time;
the chart goes into `exclusions`, which the Layer 6b learning set respects. A reading's review
status is draft until approved; the client-facing page says "reviewed by" only after.

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
from pydantic import BaseModel, ConfigDict
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
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
    birth: Mapped[dict] = mapped_column(DOCUMENT)
    engine: Mapped[str] = mapped_column(String(32))
    document: Mapped[dict] = mapped_column(DOCUMENT)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ReadingRow(Base):
    """One reading job: its request, status and progress, then the reading and its page."""
    __tablename__ = "readings"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    chart_id: Mapped[str | None] = mapped_column(ForeignKey("charts.id"), nullable=True)
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
    action: Mapped[str] = mapped_column(String(16))                # open | edit | note | approve
    target: Mapped[str | None] = mapped_column(String(200), nullable=True)
    before: Mapped[str | None] = mapped_column(Text, nullable=True)
    after: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    errors: Mapped[list | None] = mapped_column(DOCUMENT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExclusionRow(Base):
    """A chart whose reading a judge has seen: excluded from the blind learning set for good."""
    __tablename__ = "exclusions"
    chart_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    reason: Mapped[str] = mapped_column(String(64))
    reviewer_id: Mapped[str] = mapped_column(String(64))
    reading_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


def excluded_charts(session) -> set[str]:
    """The chart ids the Layer 6b learning set must leave out (their readings were seen)."""
    return {r.chart_id for r in session.query(ExclusionRow).all()}


def _add_missing_columns(engine) -> None:
    """create_all makes new tables but never alters old ones: add columns a newer model has."""
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


class ReadingRequest(BirthInput):
    """Birth data, the question, and optionally the date the reading is for."""
    model_config = ConfigDict(extra="forbid")
    question: str
    as_of: str | None = None
    depth: Literal["curious", "learner", "astrologer"] = "curious"


class EditRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target: str
    text: str


class NoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    area: str
    text: str


def reviewers_from_env() -> dict[str, str]:
    """token -> reviewer id, from JYOTISH_REVIEWERS="judge-1:<token>,judge-2:<token>"."""
    out = {}
    for pair in os.environ.get("JYOTISH_REVIEWERS", "").split(","):
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
               reviewers: dict[str, str] | None = None, review_checker=None) -> FastAPI:
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
        from .service import assess_birth, chart_line, make_reading, reading_header
        log: list[str] = []
        keep: dict = {}
        try:
            stage(reading_id, log, "chart", keep)
            birth = BirthInput(**req.model_dump(include=set(BirthInput.model_fields)))
            chart, source, chart_id = assess_birth(birth)
            with Session.begin() as s:
                if s.get(ChartRow, chart_id) is None:
                    s.add(ChartRow(id=chart_id, birth=birth.model_dump(), engine=chart.meta.engine,
                                   document=chart.model_dump(mode="json")))
            update(reading_id, chart_id=chart_id)
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
    def chart_svg(chart_id: str) -> Response:
        """D1, D9 and D10 in the North-Indian style, drawn by the engine from the stored chart."""
        from .display import svg
        return Response(svg(chart_of(chart_id)), media_type="image/svg+xml")

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

    def log(s, row, who: str, action: str, **fields) -> None:
        s.add(ReviewRow(reading_id=row.id, chart_id=row.chart_id, reviewer_id=who, action=action, **fields))
        if row.chart_id and s.get(ExclusionRow, row.chart_id) is None:
            s.add(ExclusionRow(chart_id=row.chart_id, reason="reading seen in review", reviewer_id=who,
                               reading_id=row.id))

    def save(s, row, reading) -> None:
        from .page import render
        row.document = reading.model_dump(mode="json")
        row.page = render(reading, chart_of(row.chart_id))

    def review_view(s, row, reading) -> dict:
        from .review import units
        history = [{"action": r.action, "target": r.target, "reviewer": r.reviewer_id, "accepted": r.accepted,
                    "before": r.before, "after": r.after, "errors": r.errors, "at": r.created_at.isoformat()}
                   for r in s.query(ReviewRow).filter_by(reading_id=row.id).order_by(ReviewRow.id)]
        return {"id": row.id, "chart_id": row.chart_id, "review_status": row.review_status, "reading": row.document,
                "page": row.page, "units": units(reading), "history": history}

    @app.get("/review/{reading_id}", include_in_schema=False)
    def review_page(reading_id: str):
        from fastapi.responses import FileResponse
        if web_dir is None or not (Path(web_dir) / "review.html").exists():
            raise HTTPException(status_code=404, detail="no review page")
        return FileResponse(Path(web_dir) / "review.html")

    @app.get("/readings/{reading_id}/review")
    def get_review(reading_id: str, request: Request) -> dict:
        """The reading as the reviewer sees it, every sentence with its target; opening it logs
        the reviewer and excludes the chart from the blind learning set."""
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            log(s, row, who, "open")
            s.flush()
            return review_view(s, row, reading)

    @app.post("/readings/{reading_id}/review/edit")
    def post_edit(reading_id: str, req: EditRequest, request: Request) -> dict:
        """An edited sentence: accepted only if it passes the validator and the checker."""
        from .review import apply_edit, check_edit, units
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            before = next((u["text"] for u in units(reading) if u["target"] == req.target), None)
            if before is None:
                raise HTTPException(status_code=404, detail=f"no sentence {req.target!r} in this reading")
            checker = review_checker or app.state.__dict__.setdefault("live_checker", _live_checker())
            try:
                result = check_edit(reading, chart_of(row.chart_id), req.target, req.text, checker)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            log(s, row, who, "edit", target=req.target, before=before, after=req.text.strip(),
                accepted=result["accepted"], errors=result["errors"])
            if result["accepted"]:
                reading = apply_edit(reading, req.target, req.text, who)
                save(s, row, reading)
            s.flush()
            return dict(result, review=review_view(s, row, reading))

    @app.post("/readings/{reading_id}/review/note")
    def post_note(reading_id: str, req: NoteRequest, request: Request) -> dict:
        """The astrologer's note on an area: the reviewer's words, stored and shown apart, never checked."""
        from .review import add_note
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            try:
                reading = add_note(reading, req.area, req.text, who)
            except ValueError as e:
                raise HTTPException(status_code=422, detail=str(e))
            log(s, row, who, "note", target=f"note:{req.area}", after=req.text.strip())
            save(s, row, reading)
            s.flush()
            return review_view(s, row, reading)

    @app.post("/readings/{reading_id}/review/approve")
    def post_approve(reading_id: str, request: Request) -> dict:
        """Mark the reading reviewed: the client-facing page then says by whom."""
        from .review import approve
        who = reviewer(request)
        with Session.begin() as s:
            row, reading = done_reading(s, reading_id)
            reading = approve(reading, who)
            row.review_status = "reviewed"
            log(s, row, who, "approve")
            save(s, row, reading)
            s.flush()
            return review_view(s, row, reading)

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
