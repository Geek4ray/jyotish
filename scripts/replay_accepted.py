"""Replay a comparison's recordings offline and say what is accepted now against what was accepted then.

    .venv/bin/python scripts/replay_accepted.py docs/comparison_2026-10-23_r2 --out docs/replay_2026-10-24.md

For each side (a, b) of the comparison directory: the recording is replayed through the current engine
(the writer's drafts and the checker's verdicts as recorded, no API call) and the reading compared with
the committed `<side>.reading.json`: every accepted claim, every analysis section (a recorded single
`not_said` is the astrologer's list), the judgements and the tradition sentences, per area; then the
gaps and who wrote the summary. A change to the validator, the payload or the reading's shape that
should leave accepted text alone is checked here. The checker's verdicts are the recorded ones, so a
sentence refused then is refused in the replay whatever the engine now gives it to cite: what a new
fact makes possible is measured by a live run, not by this."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

QUESTION = "How will my career go, and when is the best time for a job change?"
BIRTH = dict(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=28.1989, lon=76.617, node="mean",
             place="Rewari, Haryana")


def accepted(reading: dict) -> dict[str, object]:
    out: dict[str, object] = {}
    for a in reading["areas"]:
        out[f"{a['name']}.claims"] = sorted(c["text"] for c in a["claims"])
        an = dict(a.get("analysis") or {})
        if "not_said" in an:
            an["not_said_astrologer"] = an.pop("not_said")
        for k, v in an.items():
            out[f"{a['name']}.{k}"] = v
        out[f"{a['name']}.judgements"] = sorted(j["sentence"] for j in a.get("judgements", []))
        out[f"{a['name']}.traditions"] = sorted(t["sentence"] for t in a.get("traditions", []))
    return out


def replay(directory: Path, side: str, as_of: str) -> dict:
    from jyotish.service import BirthInput, assess_birth, make_reading
    birth = BirthInput(**BIRTH)
    chart, _, _ = assess_birth(birth)
    path = directory / f"{side}.recording.json"
    s = json.loads(path.read_text())["settings"]
    reading, _ = make_reading(birth, QUESTION, chart=chart, as_of=as_of, model_fixture=str(path), depth=s["depth"],
                              writer_model=s["model"], writer_effort=s["effort"])
    new = json.loads(reading.model_dump_json())
    old = json.loads((directory / f"{side}.reading.json").read_text())
    o, n = accepted(old), accepted(new)
    gaps = lambda r: sorted(f"{a['name']} {g['finding_id']}" for a in r["areas"] for g in a["narration_gaps"])
    return {"settings": s, "differences": [k for k in sorted(set(o) | set(n)) if o.get(k) != n.get(k)],
            "compared": len(set(o) | set(n)), "claims": (sum(len(a["claims"]) for a in old["areas"]),
                                                         sum(len(a["claims"]) for a in new["areas"])),
            "gaps": (gaps(old), gaps(new)), "summary": (old["summary"]["source"], new["summary"]["source"]),
            "paragraphs": sum(1 for a in new["areas"] if a.get("paragraph")),
            "unchecked": new.get("unchecked_sentences")}


def report(directory: Path, results: dict[str, dict]) -> str:
    L = [f"# Replay of {directory.relative_to(ROOT) if directory.is_relative_to(ROOT) else directory}", "",
         "Written by scripts/replay_accepted.py: each recording replayed through the current engine (drafts and "
         "checker verdicts as recorded, no API call) and compared with the committed reading.", ""]
    for side, r in results.items():
        s = r["settings"]
        new_gaps = [g for g in r["gaps"][1] if g not in r["gaps"][0]]
        L += [f"## {side.upper()}: {s['model']}, effort {s['effort']}, depth {s['depth']}", "",
              f"- Accepted text compared: {r['compared']} units (claims per area, each analysis section, judgements, "
              f"traditions); differences: {len(r['differences'])}" + (f" ({', '.join(r['differences'])})"
                                                                     if r["differences"] else ""),
              f"- Claims: {r['claims'][0]} then, {r['claims'][1]} now",
              f"- Gaps then: {', '.join(r['gaps'][0]) or 'none'}",
              f"- Gaps now: {', '.join(r['gaps'][1]) or 'none'}",
              f"- New gaps: {', '.join(new_gaps) or 'none'}",
              f"- Summary written by: {r['summary'][0]} then, {r['summary'][1]} now",
              f"- Paragraphs now: {r['paragraphs']}; sentences with no recorded verdict: {r['unchecked']}", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("directory", type=Path, help="a comparison directory with a/b .recording.json and .reading.json")
    ap.add_argument("--as-of", default="2026-10-21")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    d = args.directory.resolve()
    results = {side: replay(d, side, args.as_of) for side in ("a", "b") if (d / f"{side}.recording.json").exists()}
    text = report(d, results)
    if args.out:
        args.out.write_text(text + "\n")
    print(text)
    return 0 if not any(r["differences"] for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
