"""The reading pipeline shared by `jyotish read` and the web service (`api.py`): birth data and
a question -> the assessed chart (cached), the routed areas, the narration, the header that
reproduces it, and the Markdown page."""

from __future__ import annotations

import json
import shlex
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import Chart


class BirthInput(BaseModel):
    """Birth data as a person gives it: local date and time, a timezone, the place, and the
    accuracy class. Conventions not named here are the engine's defaults (Meta)."""
    model_config = ConfigDict(extra="forbid")
    date: str                                   # YYYY-MM-DD, local
    time: str                                   # HH:MM[:SS], local
    tz: str                                     # IANA name (Asia/Kolkata) or offset (+05:30)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    accuracy: Literal["exact", "within_15", "approximate", "unknown"] = "exact"
    node: Literal["true", "mean"] = "true"
    place: str | None = None
    seed: int = 0

    @model_validator(mode="after")
    def _not_null_island(self):
        # 0, 0 is the Gulf of Guinea, and the value an empty or placeholder-filled form sends:
        # a reading there is for nobody's birthplace, so it is refused rather than computed.
        if self.lat == 0 and self.lon == 0:
            raise ValueError("latitude and longitude are both 0 (a point in the Gulf of Guinea): "
                             "enter the birthplace's coordinates")
        return self


def birth_utc(day: str, clock: str, tz: str) -> tuple[datetime, str | None]:
    """Local date and time in `tz` (an IANA name such as Asia/Kolkata, or an offset such as
    +05:30) -> UTC, and the IANA name if one was given."""
    from zoneinfo import ZoneInfo
    local = datetime.fromisoformat(f"{day}T{clock}")
    if tz[:1] in "+-" and ":" in tz:
        sign = 1 if tz[0] == "+" else -1
        h, m = tz[1:].split(":")
        return local.replace(tzinfo=timezone(sign * timedelta(hours=int(h), minutes=int(m)))).astimezone(timezone.utc), None
    return local.replace(tzinfo=ZoneInfo(tz)).astimezone(timezone.utc), tz


def assess_kwargs(birth: BirthInput) -> tuple[datetime, dict]:
    utc, tz = birth_utc(birth.date, birth.time, birth.tz)
    return utc, dict(time_accuracy=birth.accuracy, tz=tz, true_node=birth.node == "true", seed=birth.seed)


def assess_birth(birth: BirthInput) -> tuple[Chart, str, str]:
    """(chart, cache source, chart id). The chart id is the cache key: birth data, every
    convention, seed and engine hash."""
    from .cache import cached_assess, chart_key
    utc, kw = assess_kwargs(birth)
    chart, source = cached_assess(utc, birth.lat, birth.lon, **kw)
    return chart, source, chart_key(utc, birth.lat, birth.lon, **kw)


def birth_key_of(birth: BirthInput) -> str:
    """The birth's key as a person (cache.birth_key): no engine hash, no accuracy class, no seed."""
    from .cache import birth_key
    utc, _ = birth_utc(birth.date, birth.time, birth.tz)
    return birth_key(utc, birth.lat, birth.lon)


CANDIDATES = Path("data") / "candidate_rules.jsonl"     # JYOTISH_CANDIDATE_RULES overrides


def record_candidates(reading, chart: Chart, chart_id: str | None = None, path: str | Path | None = None) -> int:
    """Append the reading's [tradition:] sentences to data/candidate_rules.jsonl (or
    JYOTISH_CANDIDATE_RULES) for the astrologer to triage into draft rules (docs/triage.md): the
    chart hash (the chart id when known, else fullchart.chart_hash), the area, the sentence, the
    citation and its text and chapter, the reading's date and writer. No birth data. Returns the
    number of rows written."""
    import os
    from .fullchart import chart_hash
    rows = [{"status": "candidate", "chart_hash": chart_id or chart_hash(chart), "area": a.name, "section": x["section"],
             "sentence": x["sentence"], "citation": x["citation"], "text": x["text"], "chapter": x["chapter"],
             "verse": x["verse"], "as_of": reading.as_of, "engine": reading.engine, "writer": reading.writer,
             "recorded_at": datetime.now(timezone.utc).isoformat()}
            for a in reading.areas for x in a.traditions]
    if not rows:
        return 0
    out = Path(path or os.environ.get("JYOTISH_CANDIDATE_RULES") or CANDIDATES)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a") as f:
        f.writelines(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in rows)
    return len(rows)


DEPTH_DEFAULT = "curious"          # SPEC Layer 7: the request's depth, curious unless asked otherwise


def read_command(birth: BirthInput, question: str, as_of: str | None, model_fixture: str | None,
                 depth: str = DEPTH_DEFAULT, writer_model: str | None = None, writer_effort: str | None = None) -> str:
    """The `jyotish read` invocation that reproduces a reading (output path left out)."""
    parts = ["jyotish", "read", "--date", birth.date, "--time", birth.time, "--tz", birth.tz,
             "--lat", repr(birth.lat), "--lon", repr(birth.lon), "--accuracy", birth.accuracy, "--node", birth.node,
             "--seed", str(birth.seed), "--depth", depth, "--question", question]
    if birth.place:
        parts += ["--place", birth.place]
    if as_of:
        parts += ["--as-of", as_of]
    if writer_model:
        parts += ["--writer-model", writer_model]
    if writer_effort:
        parts += ["--writer-effort", writer_effort]
    if model_fixture:
        parts += ["--model-fixture", model_fixture]
    return shlex.join(parts)


def _coord(x: float, pos: str, neg: str) -> str:
    return f"{abs(x):.4f}° {pos if x >= 0 else neg}"


def chart_line(chart: Chart, birth: BirthInput | None = None) -> dict:
    """What a person can check against any app they already use, in the first second: the
    place and the coordinates the chart was computed for, the local and UTC birth moment, the
    lagna, and the Moon's sign and nakshatra. A wrong place, timezone or date shows here."""
    moon = chart.bodies["Moon"]
    out = {"lagna": chart.lagnas.asc_sign_name, "moon_sign": moon.sign_name, "moon_nakshatra": moon.nak_name,
           "birth_utc": chart.birth.utc}
    if birth is not None:
        utc = datetime.fromisoformat(chart.birth.utc)
        out |= {"place": birth.place, "lat": birth.lat, "lon": birth.lon, "tz": birth.tz, "node": birth.node,
                "words": (f"{birth.place or 'Place not named'}, at {_coord(birth.lat, 'N', 'S')}, "
                          f"{_coord(birth.lon, 'E', 'W')} (timezone {birth.tz}). Born {birth.date} at {birth.time} "
                          f"local time, {utc:%H:%M:%S} UTC. Ascendant (lagna) {chart.lagnas.asc_sign_name}; "
                          f"Moon in {moon.sign_name}, {moon.nak_name} nakshatra.")}
    return out


def reading_header(birth: BirthInput, question: str, chart: Chart, as_of: str | None = None,
                   model_fixture: str | None = None, depth: str = DEPTH_DEFAULT, writer_model: str | None = None,
                   writer_effort: str | None = None) -> dict:
    """The reading's Chart header (narrate.chart_header plus the local inputs and the command
    that reproduces it); known as soon as the chart is, so a failed job can still show it."""
    from .narrate import chart_header
    return dict(chart_header(chart), local_date=birth.date, local_time=birth.time, tz_input=birth.tz,
                place=birth.place, seed=birth.seed, depth=depth,
                command=read_command(birth, question, as_of, model_fixture, depth, writer_model, writer_effort))


def make_reading(birth: BirthInput, question: str, *, chart: Chart, as_of: str | None = None,
                 model_fixture: str | None = None, progress: Callable[[str, dict], None] | None = None,
                 depth: str = DEPTH_DEFAULT, writer_model: str | None = None, writer_effort: str | None = None,
                 recording: list | None = None, chart_id: str | None = None, writer_backend: str | None = None,
                 checker_backend: str | None = None, client_backend: str | None = None, live_checker: bool = False):
    """(reading, page). The areas are the question's, then the chart's top three. With
    `model_fixture` the model is replayed from that recording (offline) and sentences with no
    recorded checker verdict are counted as unchecked. `writer_model` and `writer_effort` override
    the writer's settings (narrate.writer_config); `recording` collects every call. A live reading's
    [tradition:] sentences are recorded as candidate rules under `chart_id` (record_candidates); a
    replay records none, since its sentences were recorded when it was made. The three backends
    (narrate.make_backend; None: JYOTISH_<ROLE>_BACKEND) go to narrate; with `live_checker` a replay
    keeps the recording's drafts and checks them live on `checker_backend`, so two checkers can be
    compared on the same reading (scripts/compare_readings.py --live-checker). NarrationError
    propagates."""
    from .narrate import FixtureChecker, FixtureDrafter, TAG, narrate, route, sentences
    from .page import render
    if chart.scored is None:
        raise ValueError("this chart cannot be scored (no birth moment)")
    asked, _ = route(question, chart)
    areas = list(dict.fromkeys(asked + list(chart.scored.top)))
    day = date.fromisoformat(as_of) if as_of else date.today()
    drafter = checker = client_drafter = None
    if model_fixture:
        replayed = json.loads(Path(model_fixture).read_text())
        drafter, checker = FixtureDrafter(replayed), FixtureChecker(replayed)
        client_drafter = FixtureDrafter(replayed, key="client_drafts")     # depth full's client's layer
        if live_checker:
            from .narrate import CONFIG, ModelChecker, make_backend
            checker = ModelChecker(make_backend(checker_backend, "checker", CONFIG), CONFIG)
    reading = narrate(chart, question, drafter=drafter, checker=checker, as_of=day, areas=areas, progress=progress,
                      depth=depth, writer_model=writer_model, writer_effort=writer_effort, recording=recording,
                      client_drafter=client_drafter, writer_backend=writer_backend, checker_backend=checker_backend,
                      client_backend=client_backend)
    update: dict = {"chart": reading_header(birth, question, chart, as_of, model_fixture, depth, writer_model,
                                            writer_effort)}
    if model_fixture:
        said = (sentences(reading.summary.text) if reading.summary.source == "model" else []) + \
               [c.text for a in reading.areas for c in a.claims] + \
               [x for a in reading.areas for t in (a.paragraph, a.when, *(a.analysis or {}).values()) if t
                for x in sentences(t)]
        verdicts = getattr(checker, "verdicts", None)            # none with a live checker: every sentence checked
        update |= {"narration_source": f"fixture:{model_fixture}" + (" with a live checker" if live_checker else ""),
                   "unchecked_sentences": sum(1 for x in said if x not in verdicts) if verdicts is not None else 0}
    from .narrate import with_sheets
    update["areas"] = with_sheets(reading.areas, chart, day)       # the technical sheet, at every depth
    reading = reading.model_copy(update=update)
    if not model_fixture:
        record_candidates(reading, chart, chart_id)
    return reading, render(reading, chart)
