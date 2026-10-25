"""Rebuild a comparison's reading pages from their JSON with the current renderer, beside the old.

    .venv/bin/python scripts/rebuild_pages.py docs/comparison_2026-10-23_r2

For each `<side>.reading.json` in the directory (a, b) it writes `<side>.page.md`: the reading brought up
to the current schema from its own chart (narrate.upgrade_reading: learner blocks, the timing line, the
technical sheet) and rendered by jyotish.page. Nothing the model wrote is touched and no API is called;
the old pages stay where they were (side by side in the comparison's Markdown report). The chart is
the reference chart's, assessed as compare_readings.py assesses it."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BIRTH = dict(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=28.1989, lon=76.617, node="mean",
             place="Rewari, Haryana")


def rebuild(directory: Path) -> dict[str, Path]:
    from jyotish.narrate import Reading, upgrade_reading
    from jyotish.page import render
    from jyotish.service import BirthInput, assess_birth
    chart, _, _ = assess_birth(BirthInput(**BIRTH))
    out = {}
    for side in ("a", "b"):
        src = directory / f"{side}.reading.json"
        if not src.exists():
            continue
        reading = upgrade_reading(Reading(**json.loads(src.read_text())), chart)
        dest = directory / f"{side}.page.md"
        note = (f"<!-- Rebuilt by scripts/rebuild_pages.py from {src.name} with the renderer of 2026-10-25 "
                "(both views: the client's and the astrologer's technical sheet). The model's text is the "
                "reading's own; the old page is in the comparison report beside this directory. -->\n\n")
        dest.write_text(note + render(reading, chart))
        out[side] = dest
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("directory", type=Path)
    args = ap.parse_args(argv)
    for side, path in rebuild(args.directory.resolve()).items():
        print(f"{side}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
