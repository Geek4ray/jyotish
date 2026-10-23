"""The service's logs: one JSON object per line on stderr, an event name and its fields, never birth
data. What is logged is chosen field by field (a reading's id, depth, writer, attempts, gaps, tokens,
cost and seconds; a request's method, path, status and milliseconds), so a birth date, time, place,
coordinates or question cannot reach a log by being part of something else: a request's query string
(/places?q= carries a birthplace) is never logged, a chart id in a path (a hash of birth data) is
written as <chart>, and a failure is logged by its exception's class, not its message."""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any

LOGGER = "jyotish"
_CHART_PATH = re.compile(r"^/charts/[^/]+")


class JsonLines(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        body = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"), "level": record.levelname.lower(),
                "event": record.getMessage()}
        body.update(getattr(record, "fields", {}) or {})
        return json.dumps(body, ensure_ascii=False, default=str)


def setup() -> logging.Logger:
    """The service's logger, its handler added once."""
    log = logging.getLogger(LOGGER)
    if not any(getattr(h, "_jyotish", False) for h in log.handlers):
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(JsonLines())
        h._jyotish = True
        log.addHandler(h)
        log.setLevel(logging.INFO)
        log.propagate = False
    return log


def event(name: str, level: int = logging.INFO, **fields: Any) -> None:
    logging.getLogger(LOGGER).log(level, name, extra={"fields": fields})


def safe_path(path: str) -> str:
    """A request path as logged: a chart id (a hash of birth data) replaced; no query string ever."""
    return _CHART_PATH.sub("/charts/<chart>", path)
