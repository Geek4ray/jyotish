"""Time the reference chart's reading (SPEC Phase 4, item 3: target under two minutes).

Live (needs ANTHROPIC_API_KEY or an `ant auth login` profile; spends real tokens):
    .venv/bin/python scripts/time_reading.py                 # checker calls concurrent (now)
    .venv/bin/python scripts/time_reading.py --sequential    # one after another (before)
Each run prints and appends to scripts/timings.jsonl: the assess time (cold, then from the
cache), the narration wall time, attempts, writer and checker call counts, the sum of the
checker calls' own seconds, and each attempt's checker wall time.

Offline estimate from a recording made one call after another (no API call):
    .venv/bin/python scripts/time_reading.py --from-recording tests/fixtures/narration_career.json
Call durations are the gaps between consecutive recorded timestamps (the first call's is not
recorded); the concurrent estimate takes each attempt's checks as long as its slowest one."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

QUESTION = "How will my career go, and when is the best time for a job change?"
OUT = Path(__file__).with_name("timings.jsonl")


def estimate(path: str) -> dict:
    rec = json.loads(Path(path).read_text())
    calls = rec["calls"]
    ts = [datetime.fromisoformat(c["timestamp"]) for c in calls]
    gaps = [None] + [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
    writers = [g for c, g in zip(calls, gaps) if c["kind"] == "writer" and g is not None]
    by_attempt: dict[int, list[float]] = {}
    for c, g in zip(calls, gaps):
        if c["kind"] == "checker" and g is not None:
            by_attempt.setdefault(c["attempt"], []).append(g)
    first_writer = sum(writers) / len(writers) if writers else 0.0     # not recorded: the mean of the others
    sequential = first_writer + sum(g for g in gaps if g is not None)
    concurrent = first_writer + sum(writers) + sum(max(v) for v in by_attempt.values())
    return {"recording": path, "calls": len(calls), "attempts": len(by_attempt),
            "writer_seconds": [round(x, 1) for x in writers], "first_writer_assumed": round(first_writer, 1),
            "checker_calls_per_attempt": {a: len(v) for a, v in by_attempt.items()},
            "slowest_check_per_attempt": {a: round(max(v), 1) for a, v in by_attempt.items()},
            "sequential_seconds": round(sequential, 1), "concurrent_estimate_seconds": round(concurrent, 1)}


def live(sequential: bool) -> dict:
    from jyotish import cache
    from jyotish.narrate import CONFIG, AnthropicChecker, AnthropicDrafter, narrate, route
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    cfg = replace(CONFIG, checker_concurrency=1) if sequential else CONFIG
    kw = dict(time_accuracy="exact", tz="Asia/Kolkata", true_node=False, seed=0)
    cache.clear_memory()
    t = time.perf_counter()
    chart, src = cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **kw)
    assess_s = time.perf_counter() - t
    t = time.perf_counter()
    cache.cached_assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, **kw)
    cached_s = time.perf_counter() - t
    asked, _ = route(QUESTION, chart)
    areas = list(dict.fromkeys(asked + list(chart.scored.top)))
    recording: list = []
    t = time.perf_counter()
    reading = narrate(chart, QUESTION, drafter=AnthropicDrafter(cfg), checker=AnthropicChecker(cfg),
                      as_of=date(2026, 10, 21), config=cfg, recording=recording, areas=areas)
    narrate_s = time.perf_counter() - t
    checks = [c for c in recording if c["kind"] == "checker"]
    writers = [c for c in recording if c["kind"] == "writer"]
    walls = {}
    for a in sorted({c["attempt"] for c in checks}):
        stamps = [datetime.fromisoformat(c["timestamp"]) for c in checks if c["attempt"] == a]
        own = max(c.get("seconds", 0) for c in checks if c["attempt"] == a)
        walls[a] = round(max((max(stamps) - min(stamps)).total_seconds(), own), 1)
    return {"mode": "sequential" if sequential else f"concurrent ({cfg.checker_concurrency})",
            "when": datetime.now().isoformat(timespec="seconds"), "model": cfg.model,
            "writer_effort": cfg.effort, "checker_effort": cfg.checker_effort,
            "assess_seconds": round(assess_s, 2), "assess_source": src, "assess_cached_seconds": round(cached_s, 4),
            "narrate_seconds": round(narrate_s, 1), "total_seconds": round(assess_s + narrate_s, 1),
            "attempts": reading.attempts, "writer_calls": len(writers), "checker_calls": len(checks),
            "writer_seconds": [c.get("seconds") for c in writers],
            "checker_seconds_sum": round(sum(c.get("seconds", 0) for c in checks), 1),
            "checker_wall_per_attempt": walls}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sequential", action="store_true", help="checker calls one after another (the old way)")
    ap.add_argument("--from-recording", help="estimate from a recording instead of calling the model")
    args = ap.parse_args()
    out = estimate(args.from_recording) if args.from_recording else live(args.sequential)
    print(json.dumps(out, indent=1))
    if not args.from_recording:
        with OUT.open("a") as f:
            f.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
