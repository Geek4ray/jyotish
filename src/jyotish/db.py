"""The service's database (SPEC Data schema; Layer 6 and 6b's tables): the SQLAlchemy models and
`migrate`, which brings a database to the models' schema with Alembic (src/jyotish/migrations).

One function opens a database for every caller (the service, `jyotish outcomes`, `jyotish
export-reviews`, the reviewer and clerk commands, scripts/compare_readings.py): `migrate(url)`.
A database Alembic has never seen but that holds the service's tables (made by `create_all`
before 2026-10-23) is adopted: its missing tables and columns are added as they were before, its
comparison pairs are copied from the readings' `request.compared_with` into `comparisons`, and it
is stamped at the head revision; every other database is upgraded to the head. SQLite for a local
run (JYOTISH_DATABASE_URL, default sqlite:///jyotish.db), Postgres deployed (the document columns
are JSONB there)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

MIGRATIONS = Path(__file__).with_name("migrations")


def _service_environment(name: str, path: str = "/proc/1/environ") -> str | None:
    """A variable of the container's main process (the service), for a command run beside it in a
    shell that was not given the app's secrets (`fly ssh console -C "jyotish reviewer add …"`)."""
    try:
        for item in Path(path).read_bytes().split(b"\0"):
            if item.startswith(name.encode() + b"="):
                return item.split(b"=", 1)[1].decode()
    except OSError:
        pass
    return None


def database_url(url: str | None = None) -> str:
    """The database to open: the one named, else JYOTISH_DATABASE_URL, else the service process's
    own (inside its container), else sqlite:///jyotish.db (a local run). A postgres:// or
    postgresql:// URL (what hosts hand out) is given the psycopg driver."""
    url = url or os.environ.get("JYOTISH_DATABASE_URL") or _service_environment("JYOTISH_DATABASE_URL") \
        or "sqlite:///jyotish.db"
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


def describe(url: str | None = None) -> str:
    """The database in words, without its password: "postgresql at db:5432/jyotish", "sqlite at jyotish.db"."""
    from sqlalchemy.engine import make_url
    u = make_url(database_url(url))
    where = f"{u.host}:{u.port or ''}/{u.database}" if u.host else (u.database or "memory")
    return f"{u.get_backend_name()} at {where}"


def engine_for(url: str | None = None):
    url = database_url(url)
    return create_engine(url, connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
                         pool_pre_ping=not url.startswith("sqlite"))


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
    action: Mapped[str] = mapped_column(String(16))                # open | edit | note | approve | verdict | answer | compare
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



class ComparisonRow(Base):
    """A blind comparison's pair (scripts/compare_readings.py stores it; opening /compare/{a}/{b}
    records it too): the two readings, in id order, and who made the pair. A reading in a pair a
    reviewer has not answered is shown that reviewer without its settings (api.comparison_pending)."""
    __tablename__ = "comparisons"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)               # "<reading a>:<reading b>"
    reading_a: Mapped[str] = mapped_column(ForeignKey("readings.id"))
    reading_b: Mapped[str] = mapped_column(ForeignKey("readings.id"))
    created_by: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CredentialRow(Base):
    """A reviewer's, clerk's or owner's token: its SHA-256 only (the token is shown once, by `jyotish
    reviewer add`, and never stored), the name it acts under, and when it was revoked."""
    __tablename__ = "credentials"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(16))                        # reviewer | clerk | owner
    name: Mapped[str] = mapped_column(String(64))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LedgerRow(Base):
    """A finished reading's tokens and cost (jyotish.costs, from the usage the reading records): the
    owner's per-reading ledger and, summed by `day` (UTC), the daily totals."""
    __tablename__ = "ledger"
    reading_id: Mapped[str] = mapped_column(ForeignKey("readings.id"), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), index=True)            # YYYY-MM-DD, UTC
    writer_model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    checker_model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    depth: Mapped[str | None] = mapped_column(String(16), nullable=True)
    writer_tokens: Mapped[dict] = mapped_column(DOCUMENT)
    checker_tokens: Mapped[dict] = mapped_column(DOCUMENT)
    writer_calls: Mapped[int] = mapped_column(Integer, default=0)
    checker_calls: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float | None] = mapped_column(Float, nullable=True)  # null: a model without a price
    seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    replayed: Mapped[bool] = mapped_column(Boolean, default=False)       # a fixture replay costs nothing
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


KINDS = ("reviewer", "clerk", "owner")


def token_hash(token: str) -> str:
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


def issue_token(session, kind: str, name: str) -> str:
    """A new token for `name` as `kind`; only its hash is stored. Refused while `name` holds an
    active token of that kind (revoke it first)."""
    import secrets
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if not name.strip() or len(name) > 64:
        raise ValueError("a name of 1 to 64 characters")
    if session.query(CredentialRow).filter_by(kind=kind, name=name, revoked_at=None).first() is not None:
        raise ValueError(f"{name} already has an active {kind} token: revoke it first")
    token = secrets.token_urlsafe(32)
    session.add(CredentialRow(kind=kind, name=name, token_hash=token_hash(token)))
    return token


def revoke_token(session, kind: str, name: str) -> int:
    """Revoke every active token of `name` as `kind`; returns how many."""
    rows = session.query(CredentialRow).filter_by(kind=kind, name=name, revoked_at=None).all()
    for r in rows:
        r.revoked_at = _now()
    return len(rows)


def credential_name(session, kind: str, token: str) -> str | None:
    """The name an active token of `kind` acts under, or None."""
    row = session.query(CredentialRow).filter_by(kind=kind, token_hash=token_hash(token), revoked_at=None).first()
    return row.name if row else None


def record_cost(session, reading_row) -> LedgerRow | None:
    """The ledger row of a finished reading, made from its document if it is not there yet."""
    from .costs import reading_cost
    if reading_row.document is None or session.get(LedgerRow, reading_row.id) is not None:
        return None
    v = reading_cost(reading_row.document)
    when = reading_row.updated_at or _now()
    row = LedgerRow(reading_id=reading_row.id, day=when.astimezone(timezone.utc).strftime("%Y-%m-%d") if when.tzinfo
                    else when.strftime("%Y-%m-%d"), **v)
    session.add(row)
    return row


def comparison_id(a: str, b: str) -> str:
    first, second = sorted((a, b))
    return f"{first}:{second}"


def add_comparison(session, a: str, b: str, created_by: str) -> ComparisonRow:
    """The pair's row, made if it is not there yet."""
    cid = comparison_id(a, b)
    row = session.get(ComparisonRow, cid)
    if row is None:
        first, second = sorted((a, b))
        row = ComparisonRow(id=cid, reading_a=first, reading_b=second, created_by=created_by)
        session.add(row)
    return row


def compared_with(session, reading_id: str) -> list[str]:
    """The readings a reading is paired with in a blind comparison."""
    rows = session.query(ComparisonRow).filter((ComparisonRow.reading_a == reading_id) |
                                               (ComparisonRow.reading_b == reading_id)).all()
    return [r.reading_b if r.reading_a == reading_id else r.reading_a for r in rows]


# --- migrations --------------------------------------------------------------------------------

def alembic_config(connection=None):
    from alembic.config import Config
    cfg = Config()
    cfg.set_main_option("script_location", str(MIGRATIONS))
    cfg.attributes["connection"] = connection
    return cfg


def head_revision() -> str:
    from alembic.script import ScriptDirectory
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def current_revision(engine) -> str | None:
    from alembic.runtime.migration import MigrationContext
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def migrate(url_or_engine=None):
    """The database brought to the head revision (the module docstring); returns its engine."""
    from alembic import command
    engine = url_or_engine if hasattr(url_or_engine, "connect") else engine_for(url_or_engine)
    insp = inspect(engine)
    legacy = insp.has_table("readings") and not insp.has_table("alembic_version")
    with engine.begin() as conn:
        cfg = alembic_config(conn)
        if legacy:
            Base.metadata.create_all(conn)
        else:
            command.upgrade(cfg, "head")
    if legacy:
        _add_missing_columns(engine)                 # its columns, then its birth keys (below)
        _adopt_comparisons(engine)
        with engine.begin() as conn:
            command.stamp(alembic_config(conn), "head")
    else:
        _backfill_birth_keys(engine)                 # rows stored without a birth key get theirs on every open
    _backfill_ledger(engine)
    return engine


def _backfill_ledger(engine) -> None:
    """Every finished reading has its ledger row (readings finished before the ledger get theirs)."""
    with sessionmaker(engine).begin() as s:
        done = s.query(ReadingRow).outerjoin(LedgerRow, LedgerRow.reading_id == ReadingRow.id) \
            .filter(ReadingRow.status == "done", LedgerRow.reading_id.is_(None)).all()
        for r in done:
            record_cost(s, r)


def _adopt_comparisons(engine) -> None:
    """Pairs a database made before the comparisons table kept in readings.request.compared_with."""
    with sessionmaker(engine).begin() as s:
        for r in s.query(ReadingRow).all():
            for other in (r.request or {}).get("compared_with") or []:
                if s.get(ReadingRow, other) is not None:
                    add_comparison(s, r.id, other, "adopted from readings.request")
                    s.flush()
