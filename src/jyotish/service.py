"""The reading pipeline shared by `jyotish read` and the web service (`api.py`): birth data and
a question -> the assessed chart (cached), the routed areas, the narration, the header that
reproduces it, and the Markdown page."""

from __future__ import annotations

import json
import shlex
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Literal

from pydantic import BaseModel, ConfigDict

from .models import Chart


class BirthInput(BaseModel):
    """Birth data as a person gives it: local date and time, a timezone, the place, and the
    accuracy class. Conventions not named here are the engine's defaults (Meta)."""
    model_config = ConfigDict(extra="forbid")
    date: str                                   # YYYY-MM-DD, local
    time: str                                   # HH:MM[:SS], local
    tz: str                                     # IANA name (Asia/Kolkata) or offset (+05:30)
    lat: float
    lon: float
    accuracy: Literal["exact", "within_15", "approximate", "unknown"] = "exact"
    node: Literal["true", "mean"] = "true"
    place: str | None = None
    seed: int = 0


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


def read_command(birth: BirthInput, question: str, as_of: str | None, model_fixture: str | None) -> str:
    """The `jyotish read` invocation that reproduces a reading (output path left out)."""
    parts = ["jyotish", "read", "--date", birth.date, "--time", birth.time, "--tz", birth.tz,
             "--lat", repr(birth.lat), "--lon", repr(birth.lon), "--accuracy", birth.accuracy, "--node", birth.node,
             "--seed", str(birth.seed), "--question", question]
    if birth.place:
        parts += ["--place", birth.place]
    if as_of:
        parts += ["--as-of", as_of]
    if model_fixture:
        parts += ["--model-fixture", model_fixture]
    return shlex.join(parts)


def chart_line(chart: Chart) -> dict:
    """The lagna sign, the Moon's sign and nakshatra and the birth moment in UTC: what a person
    recognises in the first second, so a wrong timezone shows before the reading runs."""
    moon = chart.bodies["Moon"]
    return {"lagna": chart.lagnas.asc_sign_name, "moon_sign": moon.sign_name, "moon_nakshatra": moon.nak_name,
            "birth_utc": chart.birth.utc}


def reading_header(birth: BirthInput, question: str, chart: Chart, as_of: str | None = None,
                   model_fixture: str | None = None) -> dict:
    """The reading's Chart header (narrate.chart_header plus the local inputs and the command
    that reproduces it); known as soon as the chart is, so a failed job can still show it."""
    from .narrate import chart_header
    return dict(chart_header(chart), local_date=birth.date, local_time=birth.time, tz_input=birth.tz,
                place=birth.place, seed=birth.seed, command=read_command(birth, question, as_of, model_fixture))


def make_reading(birth: BirthInput, question: str, *, chart: Chart, as_of: str | None = None,
                 model_fixture: str | None = None, progress: Callable[[str, dict], None] | None = None):
    """(reading, page). The areas are the question's, then the chart's top three. With
    `model_fixture` the model is replayed from that recording (offline) and sentences with no
    recorded checker verdict are counted as unchecked. NarrationError propagates."""
    from .narrate import FixtureChecker, FixtureDrafter, TAG, narrate, route, sentences
    from .page import render
    if chart.scored is None:
        raise ValueError("this chart cannot be scored (no birth moment)")
    asked, _ = route(question, chart)
    areas = list(dict.fromkeys(asked + list(chart.scored.top)))
    day = date.fromisoformat(as_of) if as_of else date.today()
    drafter = checker = None
    if model_fixture:
        recording = json.loads(Path(model_fixture).read_text())
        drafter, checker = FixtureDrafter(recording), FixtureChecker(recording)
    reading = narrate(chart, question, drafter=drafter, checker=checker, as_of=day, areas=areas, progress=progress)
    update: dict = {"chart": reading_header(birth, question, chart, as_of, model_fixture)}
    if model_fixture:
        said = [x for x in sentences(reading.summary.text) if TAG.search(x)] + \
               [c.text for a in reading.areas for c in a.claims]
        update |= {"narration_source": f"fixture:{model_fixture}",
                   "unchecked_sentences": sum(1 for x in said if x not in checker.verdicts)}
    reading = reading.model_copy(update=update)
    return reading, render(reading, chart)
