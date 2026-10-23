"""Outcome capture (SPEC Layer 6, outcome dataset): the event vocabulary, the area and rule outcome
map, the clerk's intake sheet, and erasure.

An outcome is a triple (event type, age at event, censor age), never a bare yes or no; no age at
event means the event had not happened by the censor age. The intake sheet (docs/intake_template.csv)
has one row per event, the subject's birth data repeated on each, with the accuracy class and the
consent id. A row is refused when:
  - the event age exceeds the censor age, or is negative (before birth);
  - the censor age is beyond the subject's age today;
  - the consent is missing, belongs to another subject, or has been withdrawn;
  - the chart is rectified (rectified charts are excluded from every test);
  - the event type is outside the vocabulary, or an occupation row has no ISCO-08 code or ISEI.
An event entered once a reading had been shown (reading_shown_at on or before entered_at) is kept
and flagged `after`, and every test leaves it out; one entered before any reading carries its
pre-reading timestamp.

These are outcomes: what happened. They never touch the review step's judgements (export.py), and
`erase` removes everything a subject left (DPDP Act 2023, right of erasure) and logs that it did."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

MAP_FILE = Path(__file__).with_name("data") / "outcome_map.yaml"
EVENT_TYPES = ("first_marriage", "divorce", "first_child", "occupation", "tenure_change", "first_relocation_abroad",
               "major_surgery", "chronic_diagnosis", "parental_loss", "property_purchase")
ACCURACY = ("exact", "within_15", "approximate", "unknown")
SOURCES = ("file", "interview", "follow_up", "public")
TRACKS = ("backlog", "new")
SHEET_COLUMNS = ["consent_id", "subject_id", "date", "time", "tz", "lat", "lon", "place", "node", "accuracy", "sex",
                 "region", "source", "rectified", "seen_by_astrologer", "household_key", "birthplace_cluster",
                 "event_type", "age_at_event", "censor_age", "isco08", "isei", "self_report", "entered_at",
                 "reading_shown_at"]


@lru_cache(maxsize=1)
def outcome_map() -> dict:
    data = yaml.safe_load(MAP_FILE.read_text())
    for name, spec in data["areas"].items():
        for e in spec.get("events", []) + spec.get("adverse", []):
            if e not in EVENT_TYPES:
                raise ValueError(f"outcome_map: {name} names {e!r}, not in the vocabulary")
    for name, events in data["rule_outcomes"].items():
        if any(e not in EVENT_TYPES for e in events):
            raise ValueError(f"outcome_map: rule outcome {name} names an event outside the vocabulary")
    return data


def area_events(area: str) -> list[str]:
    return list(outcome_map()["areas"].get(area, {}).get("events", []))


def rule_events(rule) -> list[str]:
    """The events a rule is tested against, through its `outcomes` field."""
    m = outcome_map()["rule_outcomes"]
    return sorted({e for o in rule.data.get("outcomes", []) for e in m.get(o, [])})


def rule_testability(rules=None) -> dict[str, dict[str, Any]]:
    """rule id -> {status, events}: a rule whose outcomes map to nothing measured is not_testable_yet
    (SPEC Layer 6), whatever its library status; the rest are testable, which is not confirmed."""
    from .rules import default_rules
    out = {}
    for r in rules or default_rules():
        ev = rule_events(r)
        out[r.id] = {"library_status": r.data.get("status"), "events": ev,
                     "status": "testable" if ev else "not_testable_yet",
                     "unmapped_outcomes": [o for o in r.data.get("outcomes", []) if o not in outcome_map()["rule_outcomes"]]}
    return out


# --- the intake sheet --------------------------------------------------------------------------

@dataclass
class ImportResult:
    accepted: int = 0
    subjects_created: int = 0
    refused: list[dict] = field(default_factory=list)       # {row, subject_id, reasons}


def _bool(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "y")


def _num(v) -> float | None:
    v = str(v).strip() if v is not None else ""
    return float(v) if v else None


def _when(v) -> datetime | None:
    v = str(v).strip() if v is not None else ""
    if not v:
        return None
    d = datetime.fromisoformat(v)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def check_row(row: dict, consents: dict, today: date | None = None) -> list[str]:
    """Every reason a sheet row is refused (empty: accepted)."""
    today = today or date.today()
    out = []
    try:
        age, censor = _num(row.get("age_at_event")), _num(row.get("censor_age"))
    except ValueError:
        return ["age_at_event and censor_age must be numbers"]
    if censor is None:
        out.append("no censor age")
    if age is not None and age < 0:
        out.append(f"event age {age:g} precedes birth")
    if age is not None and censor is not None and age > censor:
        out.append(f"event age {age:g} exceeds the censor age {censor:g}")
    try:
        born = date.fromisoformat(str(row.get("date", "")).strip())
        now_age = (today - born).days / 365.25
        if censor is not None and censor > now_age + 1:
            out.append(f"censor age {censor:g} is beyond the subject's age today ({now_age:.1f})")
    except ValueError:
        out.append("birth date must be YYYY-MM-DD")
    if row.get("event_type") not in EVENT_TYPES:
        out.append(f"event type {row.get('event_type')!r} is not in the vocabulary")
    if row.get("event_type") == "occupation" and age is not None:
        if not re.fullmatch(r"\d{4}", str(row.get("isco08", "")).strip()):
            out.append("an occupation row needs its ISCO-08 code (four digits)")
        isei = _num(row.get("isei"))
        if isei is None or not 10 <= isei <= 90:
            out.append("an occupation row needs its ISEI score (10 to 90)")
    c = consents.get(str(row.get("consent_id", "")).strip())
    if c is None:
        out.append("no consent with this id")
    elif c["subject_id"] != str(row.get("subject_id", "")).strip():
        out.append("the consent belongs to another subject")
    elif c["withdrawn_at"] is not None:
        out.append("the consent has been withdrawn")
    if _bool(row.get("rectified")):
        out.append("the chart is rectified: rectified charts are excluded from every test")
    if row.get("accuracy") not in ACCURACY:
        out.append(f"accuracy class must be one of {', '.join(ACCURACY)}")
    if row.get("source") not in SOURCES:
        out.append(f"source must be one of {', '.join(SOURCES)}")
    return out


def _keys(row: dict) -> tuple[str, str]:
    """(the engine's chart key, the birth key) of a sheet row's birth data. The chart key carries the
    engine hash and the accuracy class and changes with them; the birth key does not, and is what a
    subject's rows are matched and erased by."""
    from .cache import birth_key, chart_key
    from .service import BirthInput, assess_kwargs
    b = BirthInput(date=row["date"], time=row["time"], tz=row["tz"], lat=float(row["lat"]), lon=float(row["lon"]),
                   accuracy=row["accuracy"], node=row.get("node") or "mean", place=row.get("place") or None)
    utc, kw = assess_kwargs(b)
    return chart_key(utc, b.lat, b.lon, **kw), birth_key(utc, b.lat, b.lon)


def import_rows(session, rows: list[dict], entered_by: str, today: date | None = None) -> ImportResult:
    """Validate and store sheet rows (the CLI and POST /outcomes share this). A later row for a known
    subject must carry the same birth (birth key), whatever the engine version or accuracy class."""
    from .api import ConsentRow, EventRow, SubjectRow
    from .cache import birth_key_of_record
    consents = {c.id: {"subject_id": c.subject_id, "withdrawn_at": c.withdrawn_at} for c in session.query(ConsentRow).all()}
    res = ImportResult()
    now = datetime.now(timezone.utc)
    for i, row in enumerate(rows, 1):
        row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        reasons = check_row(row, consents, today)
        if not reasons:
            try:
                cid, bkey = _keys(row)
            except Exception as e:                      # bad timezone or coordinates
                reasons = [f"birth data: {e}"]
        if reasons:
            res.refused.append({"row": i, "subject_id": row.get("subject_id"), "reasons": reasons})
            continue
        sid = row["subject_id"]
        subj = session.get(SubjectRow, sid)
        if subj is None:
            subj = SubjectRow(id=sid, chart_id=cid, birth_key=bkey,
                              birth={k: row.get(k) for k in ("date", "time", "tz", "lat", "lon", "place", "node")},
                              accuracy=row["accuracy"], sex=row.get("sex") or "unknown", region=row.get("region") or "unknown",
                              source=row["source"], rectified=False, seen_by_astrologer=_bool(row.get("seen_by_astrologer")),
                              household_key=row.get("household_key") or None,
                              birthplace_cluster=row.get("birthplace_cluster") or None)
            session.add(subj)
            res.subjects_created += 1
        elif (subj.birth_key or birth_key_of_record(subj.birth)) != bkey:
            res.refused.append({"row": i, "subject_id": sid, "reasons": ["the birth data differs from this subject's earlier rows"]})
            continue
        elif subj.birth_key is None:
            subj.birth_key = bkey
        entered = _when(row.get("entered_at")) or now
        shown = _when(row.get("reading_shown_at"))
        after = shown is not None and shown <= entered
        value = ({"isco08": row["isco08"], "isei": float(row["isei"])} if row["event_type"] == "occupation"
                 and _num(row.get("age_at_event")) is not None else None)
        session.add(EventRow(subject_id=sid, event_type=row["event_type"], age_at_event=_num(row.get("age_at_event")),
                             censor_age=_num(row["censor_age"]), value=value, self_report=_bool(row.get("self_report")),
                             entered_by=entered_by, entered_at=entered, before_reading=None if after else entered,
                             after=after, consent_id=row["consent_id"]))
        res.accepted += 1
    session.flush()
    return res


def read_sheet(path_or_text: str | Path) -> list[dict]:
    text = Path(path_or_text).read_text() if isinstance(path_or_text, Path) or "\n" not in str(path_or_text) \
        else str(path_or_text)
    return list(csv.DictReader(io.StringIO(text)))


# --- consents and erasure ------------------------------------------------------------------------

def add_consent(session, consent_id: str, subject_id: str, form_version: str, track: str, recorded_by: str,
                given_at: datetime | None = None):
    from .api import ConsentRow
    if track not in TRACKS:
        raise ValueError(f"track must be one of {', '.join(TRACKS)}")
    if session.get(ConsentRow, consent_id) is not None:
        raise ValueError(f"consent {consent_id} exists")
    session.add(ConsentRow(id=consent_id, subject_id=subject_id, form_version=form_version, track=track,
                           given_at=given_at or datetime.now(timezone.utc), recorded_by=recorded_by))


def withdraw_consent(session, consent_id: str) -> None:
    from .api import ConsentRow
    c = session.get(ConsentRow, consent_id)
    if c is None:
        raise ValueError(f"no consent {consent_id}")
    c.withdrawn_at = datetime.now(timezone.utc)


def erase(session, subject_id: str, erased_by: str) -> dict[str, int]:
    """Remove a subject's chart, readings, reviews, exclusions, events, consents and the subject
    itself; log the erasure (who, when, how many rows), never the data. Charts, readings and
    exclusions are found by the birth key, so a reading of the same birth made under another engine
    version goes too. When another subject shares the birth (twins) the chart and its readings are
    theirs as well: they stay, and the log counts them as kept."""
    from sqlalchemy import or_
    from .api import ChartRow, ConsentRow, ErasureRow, EventRow, ExclusionRow, ReadingRow, ReviewRow, SubjectRow
    from .cache import birth_key_of_record
    subj = session.get(SubjectRow, subject_id)
    if subj is None:
        raise ValueError(f"no subject {subject_id}")
    bkey = subj.birth_key or birth_key_of_record(subj.birth)
    twins = session.query(SubjectRow).filter(SubjectRow.birth_key == bkey, SubjectRow.id != subject_id).count()
    chart_ids = {c.id for c in session.query(ChartRow).filter(or_(ChartRow.birth_key == bkey, ChartRow.id == subj.chart_id))}
    readings = [r.id for r in session.query(ReadingRow).filter(
        or_(ReadingRow.birth_key == bkey, *([ReadingRow.chart_id.in_(chart_ids)] if chart_ids else [])))]
    counts = {"reviews": 0, "readings": 0, "exclusions": 0, "charts": 0}
    if not twins:
        if readings:
            counts["reviews"] = session.query(ReviewRow).filter(ReviewRow.reading_id.in_(readings)).delete(synchronize_session=False)
            counts["readings"] = session.query(ReadingRow).filter(ReadingRow.id.in_(readings)).delete(synchronize_session=False)
        counts["exclusions"] = session.query(ExclusionRow).filter(
            or_(ExclusionRow.birth_key == bkey, *([ExclusionRow.chart_id.in_(chart_ids)] if chart_ids else []))).delete(synchronize_session=False)
        if chart_ids:
            counts["charts"] = session.query(ChartRow).filter(ChartRow.id.in_(chart_ids)).delete(synchronize_session=False)
    counts["events"] = session.query(EventRow).filter_by(subject_id=subject_id).delete(synchronize_session=False)
    counts["consents"] = session.query(ConsentRow).filter_by(subject_id=subject_id).delete(synchronize_session=False)
    session.delete(subj)
    counts["subjects"] = 1
    if twins:
        counts["kept_for_another_subject"] = twins          # the chart and its readings are also theirs
    session.add(ErasureRow(subject_id=subject_id, erased_by=erased_by, counts=counts))
    session.flush()
    return counts


def sessionmaker_for(database_url: str):
    from sqlalchemy.orm import sessionmaker
    from .db import migrate
    return sessionmaker(migrate(database_url), expire_on_commit=False)
