"""A cache for `uncertainty.assess` (SPEC Phase 4, item 3): a second question on the same chart
skips the 200-sample run.

The key is a SHA-256 of everything the chart depends on: the birth moment and place, the
accuracy class, the node, the timezone, the sample count and seed, every Meta convention, and
a hash of the engine itself (its source, its data tables and the rule library), so a changed
engine never serves a stale chart. Charts are kept in memory (per process) and on disk as JSON
under JYOTISH_CACHE_DIR (default ~/.cache/jyotish/charts); JYOTISH_CACHE=off turns the disk
cache off. A chart read back from JSON is the same pydantic object (tests/test_cache.py)."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from .models import Chart, Meta

_MEMORY: dict[str, Chart] = {}
_MEMORY_MAX = 64


@lru_cache(maxsize=1)
def engine_hash() -> str:
    """SHA-256 over the engine's source, data tables and rule files."""
    from .rules import RULES_DIR
    pkg = Path(__file__).resolve().parent
    files = sorted(pkg.rglob("*.py")) + sorted((pkg / "data").glob("*.json")) + sorted(Path(RULES_DIR).glob("*"))
    h = hashlib.sha256()
    for f in files:
        if f.is_file() and "__pycache__" not in f.parts:
            h.update(str(f.relative_to(f.parents[1])).encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def chart_key(utc: datetime, lat: float, lon: float, **kw) -> str:
    utc = utc.astimezone(timezone.utc) if utc.tzinfo else utc.replace(tzinfo=timezone.utc)
    body = {"utc": utc.isoformat(), "lat": lat, "lon": lon, "assess": dict(sorted(kw.items())),
            "meta": Meta().model_dump(), "engine": engine_hash()}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()


def cache_dir() -> Path | None:
    if os.environ.get("JYOTISH_CACHE", "").lower() in ("off", "0", "no", "false"):
        return None
    return Path(os.environ.get("JYOTISH_CACHE_DIR", Path.home() / ".cache" / "jyotish" / "charts"))


def cached_assess(utc: datetime, lat: float, lon: float, **kw) -> tuple[Chart, str]:
    """(chart, where it came from: "memory", "disk" or "computed"). The caller gets its own
    copy, so changing it never changes the cache."""
    from .uncertainty import assess
    key = chart_key(utc, lat, lon, **kw)
    if key in _MEMORY:
        return _MEMORY[key].model_copy(deep=True), "memory"
    d = cache_dir()
    path = d / f"{key}.json" if d else None
    if path is not None and path.exists():
        chart = Chart.model_validate_json(path.read_text())
        source = "disk"
    else:
        chart = assess(utc, lat, lon, **kw)
        source = "computed"
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(chart.model_dump_json())
            tmp.replace(path)
    if len(_MEMORY) >= _MEMORY_MAX:
        _MEMORY.pop(next(iter(_MEMORY)))
    _MEMORY[key] = chart
    return chart.model_copy(deep=True), source


def clear_memory() -> None:
    _MEMORY.clear()
