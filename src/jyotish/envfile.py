"""A local `.env` for the measurement scripts (scripts/checker_bench.py, scripts/compare_readings.py): the
keys a live run needs, read from the repository's gitignored `.env` (the file docker-compose reads), so
they can be given without being typed into a shell or shown to anyone. Only variables a run uses are read
(ANTHROPIC_API_KEY and JYOTISH_*), only when the environment does not already set them, and no value is
ever printed or logged. The service itself takes its configuration from the environment only
(docs/deploy.md); it never reads this file."""

from __future__ import annotations

import os
from pathlib import Path

NAMES = ("ANTHROPIC_API_KEY", "JYOTISH_")


def load(path: Path) -> list[str]:
    """Set each ANTHROPIC_API_KEY / JYOTISH_* line of `path` that the environment lacks; returns the
    names set (never the values)."""
    if not path.exists():
        return []
    set_now = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.removeprefix("export ").partition("=")
        name, value = name.strip(), value.strip().strip('"').strip("'")
        if name.startswith(NAMES) and value and not os.environ.get(name):
            os.environ[name] = value
            set_now.append(name)
    return set_now
