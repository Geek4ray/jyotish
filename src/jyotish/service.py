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


DEPTH_DEFAULT = "curious"          # SPEC Layer 7: the request's depth, curious unless asked otherwise


def read_command(birth: BirthInput, question: str, as_of: str | None, model_fixture: str | None,
                 depth: str = DEPTH_DEFAULT) -> str:
    """The `jyotish read` invocation that reproduces a reading (output path left out)."""
    parts = ["jyotish", "read", "--date", birth.date, "--time", birth.time, "--tz", birth.tz,
             "--lat", repr(birth.lat), "--lon", repr(birth.lon), "--accuracy", birth.accuracy, "--node", birth.node,
             "--seed", str(birth.seed), "--depth", depth, "--question", question]
    if birth.place:
        parts += ["--place", birth.place]
    if as_of:
        parts += ["--as-of", as_of]
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
                   model_fixture: str | None = None, depth: str = DEPTH_DEFAULT) -> dict:
    """The reading's Chart header (narrate.chart_header plus the local inputs and the command
    that reproduces it); known as soon as the chart is, so a failed job can still show it."""
    from .narrate import chart_header
    return dict(chart_header(chart), local_date=birth.date, local_time=birth.time, tz_input=birth.tz,
                place=birth.place, seed=birth.seed, depth=depth,
                command=read_command(birth, question, as_of, model_fixture, depth))


def make_reading(birth: BirthInput, question: str, *, chart: Chart, as_of: str | None = None,
                 model_fixture: str | None = None, progress: Callable[[str, dict], None] | None = None,
                 depth: str = DEPTH_DEFAULT):
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
    reading = narrate(chart, question, drafter=drafter, checker=checker, as_of=day, areas=areas, progress=progress,
                      depth=depth)
    update: dict = {"chart": reading_header(birth, question, chart, as_of, model_fixture, depth)}
    if model_fixture:
        said = [x for x in sentences(reading.summary.text) if TAG.search(x)] + \
               [c.text for a in reading.areas for c in a.claims]
        update |= {"narration_source": f"fixture:{model_fixture}",
                   "unchecked_sentences": sum(1 for x in said if x not in checker.verdicts)}
    reading = reading.model_copy(update=update)
    return reading, render(reading, chart)
