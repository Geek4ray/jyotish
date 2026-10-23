"""Compare two narration settings on the same birth data and question (SPEC Layer 7, depth full).

Each setting is model,effort,depth. Both readings go through the same pipeline (service.make_reading:
the validator and the checker, the checker at CONFIG.checker_model and checker_effort whatever the
writer is), and the script writes docs/comparison_<date>.md: per setting the checked sentences and
claims shown, the checker's rejections and the validator's errors over all attempts, the narration
gaps, the synthesis and tradition sentences, the tokens of each side, the cost and the wall time;
then the two pages side by side, section by section. The two readings and their recordings are
written to docs/comparison_<date>/ (a recording replays offline: --replay-a / --replay-b). With
--database the two readings are stored, and the script prints the /compare/<id_a>/<id_b> page,
where a reviewer sees them blind.

Live, on the reference chart (spends real tokens; needs ANTHROPIC_API_KEY or an `ant auth login`
profile):
    .venv/bin/python scripts/compare_readings.py \\
        --a claude-opus-5-5,medium,astrologer --b claude-opus-5-5,max,full \\
        --database sqlite:///jyotish.db

Offline, from two recordings this script wrote (no API call):
    .venv/bin/python scripts/compare_readings.py --replay-a docs/comparison_<date>/a.recording.json \\
        --replay-b docs/comparison_<date>/b.recording.json --out /tmp/comparison.md

Costs use PRICES (USD per million tokens, the Anthropic price list as cached on 2026-10-06; check it
before quoting a cost). Thinking is billed as output and is inside output_tokens."""

from __future__ import annotations

import argparse
import html
import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

QUESTION = "How will my career go, and when is the best time for a job change?"


def reference_birth() -> dict:
    """The worked example's birth data (jyotish.reference), as the form takes it; the reference app
    uses the mean node."""
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    return {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
            "node": "mean", "place": "Rewari, Haryana"}
# USD per million tokens: input, output, cache read, cache write (5-minute, 1.25 x input).
PRICES = {"claude-opus-5-5": (4.00, 20.00, 0.20, 5.00), "claude-fable-5-1": (10.00, 50.00, 0.25, 12.50),
          "claude-opus-5": (5.00, 25.00, 0.50, 6.25), "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50)}


def setting(text: str) -> dict:
    """'model,effort,depth' -> {model, effort, depth}, checked against the engine's own lists."""
    from jyotish.narrate import DEPTHS, EFFORTS, WRITER_MODELS
    try:
        model, effort, depth = (x.strip() for x in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"a setting is model,effort,depth, not {text!r}")
    for value, allowed, what in ((model, WRITER_MODELS, "model"), (effort, EFFORTS, "effort"), (depth, DEPTHS, "depth")):
        if value not in allowed:
            raise argparse.ArgumentTypeError(f"{what} {value!r} is not one of {', '.join(allowed)}")
    return {"model": model, "effort": effort, "depth": depth}


def tokens(recording: list, kind: str) -> dict:
    out = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0,
           "cache_creation_input_tokens": 0}
    for c in recording:
        if c.get("kind") != kind:
            continue
        out["calls"] += 1
        for k in list(out)[1:]:
            out[k] += int(((c.get("usage") or {}).get(k)) or 0)
    return out


def cost(model: str, t: dict) -> float | None:
    p = PRICES.get(model)
    if p is None:
        return None
    return (t["input_tokens"] * p[0] + t["output_tokens"] * p[1] + t["cache_read_input_tokens"] * p[2]
            + t["cache_creation_input_tokens"] * p[3]) / 1e6


def metrics(reading, recording: list, wall_seconds: float | None) -> dict:
    """The comparison's numbers for one reading, from the reading and its recording."""
    from jyotish.narrate import TAG, sentences
    s = reading.summary
    # Every shown sentence of the model's is checked (the review's F2) except a judgement's weighing,
    # which is counted on its own row (F11), and a tradition sentence, apart from the sections.
    summary_n = len(sentences(s.text)) if s.source == "model" else 0
    para_n = sum(len(sentences(a.paragraph or "")) for a in reading.areas)
    judgements = sum(len(a.judgements) for a in reading.areas)
    analysis_n = sum(len(sentences(t)) for a in reading.areas for t in (a.analysis or {}).values()) - judgements
    claims = sum(len(a.claims) for a in reading.areas)
    writer, checker = tokens(recording, "writer"), tokens(recording, "checker")
    wc, cc = cost(reading.writer.get("model", reading.model), writer), cost(reading.checker.get("model", ""), checker)
    rejected = [c for c in recording if c.get("kind") == "checker"
                and any(not p["supported"] for p in c["result"]["propositions"])]
    return {"writer": reading.writer, "checker": reading.checker, "attempts": reading.attempts,
            "sentences_checked_shown": claims + summary_n + para_n + analysis_n, "claims_shown": claims,
            "checker_rejections": len(rejected),
            "claim_rejections": sum(1 for c in rejected if c.get("finding_id") != "summary"
                                    and not str(c.get("finding_id", "")).startswith(("paragraph:", "analysis:"))),
            "validator_errors": sum(len(c.get("validator_errors") or []) for c in recording if c.get("kind") == "writer"),
            "narration_gaps": sum(len(a.narration_gaps) for a in reading.areas),
            "synthesis_sentences": reading.synthesis_sentences, "judgement_sentences": judgements,
            "tradition_sentences": sum(len(a.traditions) for a in reading.areas),
            "summary_source": s.source, "narration_complete": reading.narration_complete,
            "writer_tokens": writer, "checker_tokens": checker,
            "cost_usd": None if wc is None or cc is None else round(wc + cc, 4),
            "writer_cost_usd": None if wc is None else round(wc, 4), "checker_cost_usd": None if cc is None else round(cc, 4),
            "wall_seconds": wall_seconds}


def _sections(page: str) -> dict[str, str]:
    """A page's "## " sections, by heading, in order (the title block under "")."""
    out, head, lines = {}, "", []
    for line in page.splitlines():
        if line.startswith("## "):
            out[head] = "\n".join(lines).strip()
            head, lines = line[3:].strip(), []
        else:
            lines.append(line)
    out[head] = "\n".join(lines).strip()
    return out


def side_by_side(page_a: str, page_b: str) -> str:
    """The two pages as an HTML table, a row per section heading (either page's), A left, B right."""
    a, b = _sections(page_a), _sections(page_b)
    heads = list(dict.fromkeys(list(a) + list(b)))
    cell = lambda t: html.escape(t).replace("\n", "<br>") if t else "<em>(no such section)</em>"
    rows = [f'<tr><th colspan="2">{html.escape(h) or "Title"}</th></tr>\n<tr><td valign="top">{cell(a.get(h, ""))}</td>'
            f'<td valign="top">{cell(b.get(h, ""))}</td></tr>' for h in heads]
    return '<table>\n<tr><th width="50%">A</th><th width="50%">B</th></tr>\n' + "\n".join(rows) + "\n</table>"


ROWS = [("Writer", lambda m: f"{m['writer'].get('model')}, effort {m['writer'].get('effort')}, "
                             f"thinking {m['writer'].get('thinking') or 'not sent'}"),
        ("Checker", lambda m: f"{m['checker'].get('model')}, effort {m['checker'].get('effort')}"),
        ("Attempts", lambda m: m["attempts"]),
        ("Checked sentences shown", lambda m: m["sentences_checked_shown"]),
        ("Claims shown", lambda m: m["claims_shown"]),
        ("Checker rejections (all attempts)", lambda m: m["checker_rejections"]),
        ("Rejected claims (checker, all attempts)", lambda m: m["claim_rejections"]),
        ("Validator errors (all attempts)", lambda m: m["validator_errors"]),
        ("Narration gaps", lambda m: m["narration_gaps"]),
        ("Synthesis sentences", lambda m: m["synthesis_sentences"]),
        ("Judgement sentences (premises checked, the weighing not; not among the checked)",
         lambda m: m["judgement_sentences"]),
        ("Tradition sentences (unchecked, shown apart)", lambda m: m["tradition_sentences"]),
        ("Summary written by", lambda m: m["summary_source"]),
        ("Writer tokens: input / cache read / cache write / output",
         lambda m: " / ".join(f"{m['writer_tokens'][k]:,}" for k in ("input_tokens", "cache_read_input_tokens",
                                                                     "cache_creation_input_tokens", "output_tokens"))),
        ("Checker tokens: input / output (calls)",
         lambda m: f"{m['checker_tokens']['input_tokens']:,} / {m['checker_tokens']['output_tokens']:,} "
                   f"({m['checker_tokens']['calls']})"),
        ("Cost, USD (writer + checker)", lambda m: "–" if m["cost_usd"] is None else
         f"{m['cost_usd']:.2f} ({m['writer_cost_usd']:.2f} + {m['checker_cost_usd']:.2f})"),
        ("Narration wall time, s", lambda m: "–" if m["wall_seconds"] is None else f"{m['wall_seconds']:.1f}")]


def per_attempt(recording: list) -> list[dict]:
    """Each attempt's writer call (effort, stop reason, tokens, seconds) and checker calls (count,
    tokens, the sum of their seconds), from a recording."""
    out = []
    for w in (c for c in recording if c.get("kind") == "writer"):
        u = w.get("usage") or {}
        checks = [c for c in recording if c.get("kind") == "checker" and c.get("attempt") == w.get("attempt")]
        out.append({"attempt": w.get("attempt"), "effort": w.get("effort"), "stop": w.get("stop_reason"),
                    "draft": bool(w.get("draft")), "writer_in": int(u.get("input_tokens") or 0)
                    + int(u.get("cache_read_input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0),
                    "writer_out": int(u.get("output_tokens") or 0), "writer_s": w.get("seconds"),
                    "checks": len(checks), "checker_out": sum(int((c.get("usage") or {}).get("output_tokens") or 0)
                                                              for c in checks),
                    "checker_s": round(sum(float(c.get("seconds") or 0) for c in checks), 1)})
    return out


def _attempt_table(rows: list[dict]) -> list[str]:
    L = ["| attempt | effort | stop | draft | writer tokens in / out | writer s | checks | checker tokens out | "
         "checker s (sum) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['attempt']} | {r['effort'] or '–'} | {r['stop'] or '–'} | {'yes' if r['draft'] else 'no'} | "
                 f"{r['writer_in']:,} / {r['writer_out']:,} | {r['writer_s'] if r['writer_s'] is not None else '–'} | "
                 f"{r['checks']} | {r['checker_out']:,} | {r['checker_s']} |")
    return L


def document(run_date: str, birth: dict, question: str, as_of: str, source: str, ma: dict, mb: dict,
             page_a: str, page_b: str, ids: tuple[str, str] | None, attempts: tuple[list, list] = ([], [])) -> str:
    L = [f"# Comparison of two readings, {run_date}", "",
         f"Birth data: {birth.get('place') or 'place not named'}, {birth['date']} {birth['time']} ({birth['tz']}), "
         f"{birth['lat']}, {birth['lon']}, node {birth.get('node', 'true')}. Question: \"{question}\". As of {as_of}.",
         f"Source: {source}. Both readings went through the same validator and checker; the tier, stability and "
         "windows are the engine's in both.", ""]
    if ids:
        L += [f"Blind review: `/compare/{ids[0]}/{ids[1]}` (the reviewer sees A and B without their settings).", ""]
    L += ["| | A | B |", "|---|---|---|"] + [f"| {name} | {f(ma)} | {f(mb)} |" for name, f in ROWS] + [""]
    L += ["Prices: USD per million tokens from `PRICES` in scripts/compare_readings.py (the Anthropic price list "
          "as cached on 2026-10-06); thinking is billed as output. Wall time is the narration's (writer and "
          "checker calls), not the chart's.", ""]
    for label, rows in zip("AB", attempts):
        if rows:
            L += [f"Per attempt, {label} (the checker's seconds are the sum of its calls, which run concurrently):", ""] \
                + _attempt_table(rows) + [""]
    L += ["## The two pages side by side", "", side_by_side(page_a, page_b), ""]
    return "\n".join(L)


def run(birth_data: dict, question: str, as_of: str, s: dict, replay: str | None = None):
    """(reading, page, recording, wall seconds, chart, chart id) for one setting."""
    from jyotish.service import BirthInput, assess_birth, make_reading
    birth = BirthInput(**birth_data)
    chart, _, chart_id = assess_birth(birth)
    if replay:
        rec = json.loads(Path(replay).read_text())
        s = rec["settings"]
        reading, page = make_reading(birth, question, chart=chart, as_of=as_of, model_fixture=replay, depth=s["depth"],
                                     writer_model=s["model"], writer_effort=s["effort"])
        return reading, page, rec.get("calls", []), rec.get("wall_seconds"), chart, chart_id, s
    recording: list = []
    t = time.perf_counter()
    reading, page = make_reading(birth, question, chart=chart, as_of=as_of, depth=s["depth"], writer_model=s["model"],
                                 writer_effort=s["effort"], recording=recording)
    return reading, page, recording, round(time.perf_counter() - t, 1), chart, chart_id, s


def save_recording(path: Path, question: str, s: dict, recording: list, wall: float | None) -> None:
    path.write_text(json.dumps({"note": "Recorded by scripts/compare_readings.py.", "question": question, "settings": s,
                                "wall_seconds": wall, "drafts": [c["draft"] for c in recording
                                                                 if c.get("kind") == "writer" and c.get("draft")],
                                "calls": recording}, indent=1, ensure_ascii=False, default=str) + "\n")


def store(database_url: str, birth_data: dict, question: str, chart, chart_id: str, reading, page: str) -> str:
    """Store a finished reading (and its chart) as the service would; returns its id."""
    import uuid
    from sqlalchemy.orm import sessionmaker
    from jyotish.db import ChartRow, ReadingRow, migrate
    from jyotish.service import BirthInput, birth_key_of
    engine = migrate(database_url)
    bkey = birth_key_of(BirthInput(**birth_data))
    rid = uuid.uuid4().hex
    with sessionmaker(engine).begin() as s:
        if s.get(ChartRow, chart_id) is None:
            s.add(ChartRow(id=chart_id, birth_key=bkey, birth=birth_data, engine=chart.meta.engine,
                           document=chart.model_dump(mode="json")))
        s.add(ReadingRow(id=rid, chart_id=chart_id, birth_key=bkey, question=question,
                         request=dict(birth_data, question=question, as_of=reading.as_of, depth=reading.depth,
                                      writer_model=reading.writer.get("model"), writer_effort=reading.writer.get("effort")),
                         status="done", progress={"stage": "done", "source": "scripts/compare_readings.py"},
                         document=reading.model_dump(mode="json"), page=page))
    return rid


def link(database_url: str, a: str, b: str) -> None:
    """Record the two stored readings as a comparison pair (the comparisons table), so the service
    withholds their settings from a reviewer who has not answered it (api.comparison_pending)."""
    from sqlalchemy.orm import sessionmaker
    from jyotish.db import add_comparison, migrate
    with sessionmaker(migrate(database_url)).begin() as s:
        add_comparison(s, a, b, "scripts/compare_readings.py")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--a", type=setting, default=None, help="model,effort,depth for reading A")
    ap.add_argument("--b", type=setting, default=None, help="model,effort,depth for reading B")
    ap.add_argument("--replay-a", help="a recording this script wrote, replayed offline instead of setting A")
    ap.add_argument("--replay-b", help="the same for B")
    ap.add_argument("--question", default=QUESTION)
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--birth", help="birth data as JSON (BirthInput fields); default the reference chart")
    ap.add_argument("--out", help="the Markdown file (default docs/comparison_<today>.md)")
    ap.add_argument("--database", help="store both readings here (a database URL) for /compare/<a>/<b>")
    args = ap.parse_args(argv)
    if not ((args.a or args.replay_a) and (args.b or args.replay_b)):
        ap.error("name both settings (--a and --b) or both recordings (--replay-a and --replay-b)")
    birth = json.loads(args.birth) if args.birth else reference_birth()
    today = date.today().isoformat()
    out = Path(args.out) if args.out else REPO / "docs" / f"comparison_{today}.md"
    side = out.with_suffix("")
    side.mkdir(parents=True, exist_ok=True)
    results = {}
    for key, s, replay in (("a", args.a, args.replay_a), ("b", args.b, args.replay_b)):
        reading, page, rec, wall, chart, chart_id, s = run(birth, args.question, args.as_of, s, replay)
        if not replay:
            save_recording(side / f"{key}.recording.json", args.question, s, rec, wall)
        (side / f"{key}.reading.json").write_text(json.dumps(reading.model_dump(mode="json"), indent=1,
                                                             ensure_ascii=False) + "\n")
        results[key] = (reading, page, rec, wall, chart, chart_id)
        print(f"{key.upper()}: {s['model']}, {s['effort']}, {s['depth']}: {reading.attempts} attempt(s), "
              f"{sum(len(a.narration_gaps) for a in reading.areas)} gap(s)", file=sys.stderr)
    ids = None
    if args.database:
        ids = tuple(store(args.database, birth, args.question, r[4], r[5], r[0], r[1]) for r in results.values())
        link(args.database, *ids)
    (ra, pa, reca, wa, *_), (rb, pb, recb, wb, *_) = results["a"], results["b"]
    source = "replayed from recordings (no API call)" if args.replay_a or args.replay_b else "live"
    out.write_text(document(today, birth, args.question, args.as_of, source, metrics(ra, reca, wa),
                            metrics(rb, recb, wb), pa, pb, ids, (per_attempt(reca), per_attempt(recb))))
    print(f"wrote {out}" + (f"; blind review at /compare/{ids[0]}/{ids[1]}" if ids else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
