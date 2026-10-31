"""Evaluation harness v1: one scorecard from the engine's checks.

    .venv/bin/python scripts/evaluate.py                                  # writes docs/scorecard.{md,json}
    .venv/bin/python scripts/evaluate.py --out /tmp/sc --compare docs/scorecard.json   # the CI gate

It runs, in order:
  1. the reference acceptance tests (tests/test_reference_chart.py, tests/test_ephemeris_reference.py);
  2. the Phase 0 cross-check against PyJHora (scripts/crosscheck.py, 1,000 births), when PyJHora is
     installed; otherwise a skip with its reason;
  3. the metamorphic tests (tests/test_metamorphic.py) and their measured numbers (what a minute
     changes, the seed agreement per birth);
  4. the offline part of the checker benchmark (scripts/checker_bench.py: the validator alone) and
     its tests;
  5. the placement generator check (scripts/make_placements.py --check);
  6. the synthetic validation runs (scripts/synthetic_cohort.py, scripts/validate.py): a planted and a
     null cohort at N = 2,000 and 20,000 (--quick: 2,000 only), each written to
     docs/validation_synthetic_<mode>_<n>.md, with what was recovered against what was planted.
Every number carries its direction (higher or lower is better, or informational) and whether it
gates CI. Gated are the verdicts: tests passed and failed, the cross-check's maxima, the validator's
wording catch and false rejects, the placement check, and two pass/fail checks on the 20,000-subject
synthetic runs. Sampled statistics (the synthetic shares and counts, the sampler's seed agreement,
the validator's precision and recall on the benchmark, whose rows define them) are reported with
their direction and not gated: they move with every change to scoring or to the benchmark, so a
gate on them would fail on noise and could be passed by regenerating (review 2026-10-23, F5). The
live checker run is not re-run here (it costs API calls); its last numbers are read from
docs/checker_scorecard.md. --compare reads a committed scorecard JSON and exits 1 when any gated
number is worse than there; a number skipped now (PyJHora absent, say) is reported and not counted
as worse."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PY = sys.executable
DOCS = ROOT / "docs"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _commit() -> str:
    out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def pytest(*paths: str) -> dict:
    """Run pytest on `paths`: counts, and every skip with its reason."""
    out = subprocess.run([PY, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", *paths], cwd=ROOT,
                         capture_output=True, text=True)
    text = out.stdout + out.stderr
    counts = {k: 0 for k in ("passed", "failed", "skipped", "errors")}
    tail = [line for line in text.splitlines() if re.search(r"\d+ (passed|failed|skipped|error)", line)]
    for n, kind in re.findall(r"(\d+) (passed|failed|skipped|errors?)", tail[-1] if tail else ""):
        counts["errors" if kind.startswith("error") else kind] += int(n)
    skips = [re.sub(r"^SKIPPED \[\d+\] ", "", line) for line in text.splitlines() if line.startswith("SKIPPED")]
    return counts | {"skips": skips, "returncode": out.returncode}


class Card:
    def __init__(self):
        self.numbers: dict[str, dict] = {}
        self.skips: list[str] = []
        self.sections: list[tuple[str, list[str]]] = []

    def num(self, key: str, value, better: str | None, unit: str = "", gate: bool | None = None):
        """`gate` defaults to whether the number has a direction; a sampled statistic passes False."""
        self.numbers[key] = {"value": value, "better": better, "unit": unit,
                             "gate": bool(gate if gate is not None else better is not None)}

    def skip(self, what: str, why: str):
        self.skips.append(f"{what}: {why}")


def reference(card: Card):
    r = pytest("tests/test_reference_chart.py", "tests/test_ephemeris_reference.py")
    card.num("reference.passed", r["passed"], "higher")
    card.num("reference.failed", r["failed"] + r["errors"], "lower")
    card.skips += [f"reference: {s}" for s in r["skips"]]
    card.sections.append(("Reference acceptance tests", [
        f"`tests/test_reference_chart.py` and `tests/test_ephemeris_reference.py`: {r['passed']} passed, "
        f"{r['failed'] + r['errors']} failed, {r['skipped']} skipped."]))


def crosscheck(card: Card):
    try:
        xc = _load("crosscheck")
        t = time.time()
        r, j, _ = xc.run(1000, 0)
    except ImportError as e:
        card.skip("cross-check (1,000 births against PyJHora)", f"PyJHora is not installed ({e}); "
                  "pip install -e '.[crosscheck]' (see docs/crosscheck.md for the last run)")
        card.sections.append(("Phase 0 cross-check", ["Skipped: PyJHora is not installed in this environment."]))
        return
    s = xc.summary(r)
    for q, (mx, mean) in s.items():
        unit = "days" if "days" in q else "arc-seconds"
        card.num(f"crosscheck.max.{q}", round(mx, 9), "lower", unit)
        card.num(f"crosscheck.mean.{q}", round(mean, 9), "lower", unit)
    card.num("crosscheck.beyond_gate", len(r.failed), "lower")
    card.num("crosscheck.listed_at_edges", len(r.listed), None)
    card.num("crosscheck.births", r.n, None)
    card.sections.append(("Phase 0 cross-check", [
        f"1,000 births (seed 0) against PyJHora {j.version}, ephemeris {xc.ephemeris_mode()}, in "
        f"{time.time() - t:.0f} s: {len(r.failed)} beyond the 1″ / one-day gate, {len(r.listed)} listed at an edge. "
        "Per-quantity maxima and means are in the table; docs/crosscheck.md has the full report."]))


def metamorphic(card: Card):
    r = pytest("tests/test_metamorphic.py")
    card.num("metamorphic.passed", r["passed"], "higher")
    card.num("metamorphic.failed", r["failed"] + r["errors"], "lower")
    card.skips += [f"metamorphic: {s}" for s in r["skips"]]
    # The measured numbers behind the tests.
    from datetime import datetime, timedelta
    from jyotish.chart import compute
    from jyotish.uncertainty import assess, placements, rule_keys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_metamorphic import BIRTHS, _classes
    lines = [f"`tests/test_metamorphic.py`: {r['passed']} passed, {r['failed'] + r['errors']} failed, "
             f"{r['skipped']} skipped (the narration-side invariants are live only)."]
    for b in BIRTHS:
        utc = datetime.fromisoformat(b["utc"])
        c = assess(utc, b["lat"], b["lon"], true_node=False, seed=0)
        moved = 0
        for m in (-1, 1):
            o = compute(utc + timedelta(minutes=m), b["lat"], b["lon"], true_node=False)
            moved += sum(placements(o)[k] != v for k, v in placements(c).items()) + len(rule_keys(c) ^ rule_keys(o))
        x, y = _classes(c), _classes(assess(utc, b["lat"], b["lon"], true_node=False, seed=1))
        common = set(x) & set(y)
        agree = sum(x[k] == y[k] for k in common) / len(common)
        card.num(f"metamorphic.seed_agreement.{b['name']}", round(agree, 4), "higher", gate=False)
        card.num(f"metamorphic.changed_at_one_minute.{b['name']}", moved, None)
    card.sections.append(("Metamorphic tests", lines))


def checker(card: Card):
    cb = _load("checker_bench")
    rows = cb.load()
    pred = cb.run_validator(rows)
    s = cb.scores(rows, pred)
    for k in ("precision", "recall", "f1"):
        card.num(f"checker.validator.{k}", round(s["overall"][k], 4), "higher", gate=False)   # the rows define them
    wording = [r for r in rows if r["category"] in cb.WORDING]
    caught = sum(pred[r["id"]][0] for r in wording)
    card.num("checker.validator.wording_caught_share", round(caught / len(wording), 4), "higher")
    card.num("checker.validator.false_rejects", s["accepted"]["fp"], "lower")
    card.num("checker.bench_rows", len(rows), None)
    t = pytest("tests/test_checker_bench.py")
    card.num("checker.tests_failed", t["failed"] + t["errors"], "lower")
    card.skips += [f"checker benchmark: {x}" for x in t["skips"]]
    live = live_checker(card)
    card.sections.append(("Checker benchmark", [
        f"{len(rows)} rows; the validator alone: precision {s['overall']['precision']:.3f}, recall "
        f"{s['overall']['recall']:.3f}, F1 {s['overall']['f1']:.3f}; {caught} of {len(wording)} tag and wording "
        f"errors caught; {s['accepted']['fp']} accepted sentences rejected. The semantic categories are the "
        "checker's. " + live]))


def live_checker(card: Card) -> str:
    """The live checker run is not part of the harness (it costs API calls): its last numbers on
    record in docs/checker_scorecard.md are reported, not gated, with the commit they were measured
    at; without a run on record the skip says so."""
    doc = DOCS / "checker_scorecard.md"
    text = doc.read_text() if doc.exists() else ""
    head = re.search(r"Run (\d{4}-\d{2}-\d{2}) at commit `([0-9a-f]+)`", text)
    parts = text.split("## Validator + semantic checker (live)", 1)
    if len(parts) == 2 and (kept := re.search(r"Carried over from the run of (\d{4}-\d{2}-\d{2}) at commit `([0-9a-f]+)`", parts[1])):
        head = kept                                   # the live section is an earlier run's
    row = re.search(r"\| overall \| \d+ \| (\d+) of (\d+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|", parts[1]) \
        if len(parts) == 2 else None
    model = re.search(r"Model ([\w.-]+), checker effort (\w+)", parts[1]) if len(parts) == 2 else None
    if row is None or head is None:
        card.skip("checker benchmark, validator + live checker", "no live run on record in docs/checker_scorecard.md; "
                  "run scripts/checker_bench.py with ANTHROPIC_API_KEY set to add one")
        return "No live checker run is on record."
    for k, v in zip(("precision", "recall", "f1"), row.groups()[2:]):
        card.num(f"checker.live.{k}", float(v), None)
    return (f"The live run on record (docs/checker_scorecard.md, {head.group(1)} at `{head.group(2)}`"
            + (f", model {model.group(1)}, checker effort {model.group(2)}" if model else "") + f"): {row.group(1)} of "
            f"{row.group(2)} bad sentences caught, precision {row.group(3)}, recall {row.group(4)}, F1 {row.group(5)}. "
            "The harness does not re-run it (API calls), so it is reported, not gated.")


def live_timings(card: Card):
    """The live narration's timeline (2026-10-26; review R14): the last row per stack in
    docs/live_timings.jsonl (scripts/live_timing.py, live readings of the reference chart), reported and
    never gated, since each is one live run on a shared provider."""
    path = DOCS / "live_timings.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []
    if not rows:
        card.skip("live timings", "no row in docs/live_timings.jsonl; run scripts/live_timing.py")
        return
    last = {r["label"]: r for r in rows}
    lines = []
    for label, r in last.items():
        for k in ("instant_s", "first_sentence_s", "first_verified_s", "first_area_s", "done_s", "cost_usd", "gaps"):
            if r.get(k) is not None:
                card.num(f"live.{label}.{k}", r[k], "lower", gate=False)
        where = f"on the deployed service ({r['where']})" if r.get("where") else f"concurrency {r['checker_concurrency']}"
        lines.append(f"- {label} ({r['date']}; {r['writer']}, {r['checker']}, {where}): "
                     f"instant page {r['instant_s']} s, first sentence {r['first_sentence_s']} s, first verified "
                     f"{r['first_verified_s']} s, first area {r['first_area_s']} s, done {r['done_s']} s; USD "
                     f"{r['cost_usd']}; {r['claims']} claims, {r['gaps']} gaps.")
    # The deployed service's readings (scripts/live_timing.py --url, 2026-10-31): their medians, per `where`.
    import statistics
    for where in sorted({r["where"] for r in rows if r.get("where")}):
        mine = [r for r in rows if r.get("where") == where]
        meds = {k: statistics.median(r[k] for r in mine) for k in ("instant_s", "first_sentence_s", "first_verified_s",
                                                                    "first_area_s", "done_s", "cost_usd", "gaps")
                if all(r.get(k) is not None for r in mine)}
        for k, v in meds.items():
            card.num(f"live.{where}_median.{k}", v, "lower", gate=False)
        lines.append(f"- Median of the {len(mine)} readings on {where}: " + ", ".join(f"{k} {v:g}" for k, v in meds.items())
                     + ".")
    card.sections.append(("Live narration timings (reported, not gated)", [
        "One live reading per stack on the reference chart (docs/live_timings.jsonl; docs/models.md, \"Timing\"). "
        "Each is a single run on a shared provider, so it is reported and never gated.", ""] + lines))


def placements_check(card: Card):
    out = subprocess.run([PY, str(ROOT / "scripts" / "make_placements.py"), "--check"], cwd=ROOT, capture_output=True,
                         text=True)
    m = re.search(r"(\d+) file\(s\) differ", out.stdout)
    differ = int(m.group(1)) if m else -1
    card.num("placements.files_differing_from_table", differ, "lower")
    card.sections.append(("Placement generator check", [f"`scripts/make_placements.py --check`: {differ} file(s) "
                                                        "differ from scripts/placements.csv."]))


SYNTHETIC_SIZES = (2000, 20000)
GATE_SIZE = 20000          # the size at which the pipeline's pass/fail checks are near-certain, so they gate


def synthetic(card: Card, sizes=SYNTHETIC_SIZES, out_dir: Path = DOCS):
    import tempfile
    try:
        V, SC = _load("validate"), _load("synthetic_cohort")
        import sklearn, statsmodels  # noqa: F401
    except ImportError as e:
        card.skip("synthetic validation runs", f"the validate extra is not installed ({e}): pip install -e '.[validate]'")
        return
    lines = []
    for n in sizes:
        feats = None                                       # one feature computation a size: the births are the same
        for mode in ("planted", "null"):
            t = time.time()
            with tempfile.TemporaryDirectory() as d:
                url = f"sqlite:///{Path(d) / 'cohort.db'}"
                feats, truth = SC.make(n, mode, url, seed=0, features=feats)
                res = V.run(V.load_cohort(url, features=feats, synthetic=True), Path(d) / "sequestered.txt",
                            score_sequestered=True, salt=f"synthetic-{n}-{mode}")
            c = SC.compare(truth, res)
            (out_dir / f"validation_synthetic_{mode}_{n}.md").write_text(
                V.report(res, label=f"{mode}, N = {n:,}, odds ratio {truth['odds_ratio_per_sd']} per SD"))
            k = f"synthetic.{mode}.{n}"
            gated = n >= GATE_SIZE
            if mode == "planted":
                card.num(f"{k}.predicted_power", round(c["predicted_power_mean"], 4), None)
                card.num(f"{k}.recovered_share", round(c["recovered_share"], 4), "higher", gate=False)
                card.num(f"{k}.survived_bh_share", round(c["survived_bh_share"], 4), "higher", gate=False)
                card.num(f"{k}.recovery_gap", round(abs(c["recovered_share"] - c["predicted_power_mean"]), 4), None)
                card.num(f"{k}.timing_recovered_share", round(c["timing_recovered_share"], 4), "higher", gate=False)
                card.num(f"{k}.unplanted_areas_surviving_bh", len(c["unplanted_surviving_bh"]), "lower", gate=False)
                ok = min(c["recovered_share"], c["survived_bh_share"], c["timing_recovered_share"]) >= 0.75
                if gated:
                    card.num(f"{k}.pipeline_recovers", int(ok), "higher")
                lines.append(f"Planted, N = {n:,} (odds ratio {truth['odds_ratio_per_sd']} per SD of the area score, "
                             f"timing weight {truth['timing_weight']}): {len(c['planted_areas'])} planted areas; predicted "
                             f"power {c['predicted_power_mean']:.2f}, recovered {c['recovered_share']:.2f} (p < 0.05), "
                             f"{c['survived_bh_share']:.2f} surviving BH; the timing effect recovered in "
                             f"{c['timing_recovered_share']:.2f}; {len(c['unplanted_surviving_bh'])} of the "
                             f"{len(c['unplanted_areas'])} unplanted areas ({', '.join(c['unplanted_areas'])}: they own none "
                             f"of their events) also survive BH, lift inherited through the shared outcome map"
                             + (f" ({', '.join(c['unplanted_surviving_bh'])})" if c["unplanted_surviving_bh"] else "")
                             + f"; {time.time() - t:.0f} s."
                             + (f" Gated check: at least three quarters of the planted areas recovered, surviving BH and "
                                f"timing-recovered: {'passes' if ok else 'FAILS'}." if gated else ""))
            else:
                card.num(f"{k}.areas_surviving_bh", c["areas_surviving_bh"], "lower", gate=False)
                card.num(f"{k}.rules_with_effect", c["rules_with_effect"], "lower", gate=False)
                ok = c["areas_surviving_bh"] <= 1 and c["rules_with_effect"] <= 3
                if gated:
                    card.num(f"{k}.pipeline_quiet", int(ok), "higher")
                lines.append(f"Null, N = {n:,}: {c['areas_surviving_bh']} of {c['areas_tested']} areas survive BH; "
                             f"{c['rules_with_effect']} of {c['rules_tested']} rules show an effect after BH; "
                             f"{time.time() - t:.0f} s."
                             + (f" Gated check: at most one area and three rules survive: {'passes' if ok else 'FAILS'}."
                                if gated else ""))
            print(f"synthetic {mode} {n:,}: {time.time() - t:.0f} s", flush=True)      # progress, for a CI log
    card.sections.append(("Synthetic validation (the pipeline, not the engine)", lines + [
        "The shares and counts are sampled statistics and are reported, not gated: the planted events are drawn from "
        "the engine's own scores, so any change to scoring redraws them. The two pass/fail checks at N = 20,000, "
        "where the planted effect is near-certain, gate.",
        f"Each run's full report: {out_dir.name}/validation_synthetic_<mode>_<n>.md (every heading says synthetic)."]))


def markdown(card: Card) -> str:
    L = ["# Scorecard", "", f"Run {date.today().isoformat()} at commit `{_commit()}` by `scripts/evaluate.py`. "
         "CI fails when any gated number is worse than in the committed `docs/scorecard.json`; a sampled statistic "
         "is reported with its direction and not gated.", ""]
    for title, lines in card.sections:
        L += [f"## {title}", "", *lines, ""]
    L += ["## Every number", "", "| number | value | unit | better | gates CI |", "| --- | --- | --- | --- | --- |"]
    L += [f"| `{k}` | {v['value']} | {v['unit']} | {v['better'] or 'informational'} | {'yes' if v['gate'] else 'no'} |"
          for k, v in card.numbers.items()]
    L += ["", "## Skips and what is blocked", ""] + ([f"- {s}" for s in card.skips] or ["None."]) + [""]
    return "\n".join(L) + "\n"


TOLERANCE = 1e-6


def compare(new: dict, old: dict) -> list[str]:
    """Every gated number that is worse than in `old`; one not measured now is not worse, and one
    the committed scorecard marks `gate: false` is never worse."""
    worse = []
    for k, o in old["numbers"].items():
        n = new["numbers"].get(k)
        if n is None or o.get("better") is None or n["value"] is None or o["value"] is None or o.get("gate") is False:
            continue
        tol = TOLERANCE + TOLERANCE * abs(o["value"])        # float noise across platforms, not a change
        if (o["better"] == "higher" and n["value"] < o["value"] - tol) or \
                (o["better"] == "lower" and n["value"] > o["value"] + tol):
            worse.append(f"{k}: {o['value']} -> {n['value']} ({o['better']} is better)")
    return worse


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DOCS / "scorecard"), help="path without extension: writes .md and .json")
    ap.add_argument("--compare", help="a committed scorecard JSON: exit 1 if any number is worse")
    ap.add_argument("--quick", action="store_true", help="synthetic runs at N = 2,000 only")
    a = ap.parse_args(argv)
    card = Card()
    for step in (reference, crosscheck, metamorphic, checker, placements_check, live_timings):
        t = time.time()
        step(card)
        print(f"{step.__name__}: {time.time() - t:.0f} s", flush=True)                 # progress, for a CI log
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    synthetic(card, SYNTHETIC_SIZES[:1] if a.quick else SYNTHETIC_SIZES, out_dir=out.parent)
    data = {"date": date.today().isoformat(), "commit": _commit(), "numbers": card.numbers, "skips": card.skips}
    out.with_suffix(".md").write_text(markdown(card))
    out.with_suffix(".json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"{len(card.numbers)} numbers, {len(card.skips)} skips -> {out.with_suffix('.md')}")
    if a.compare:
        old = json.loads(Path(a.compare).read_text())
        missing = [k for k in old["numbers"] if k not in card.numbers]
        if missing:
            print(f"not measured this run (skipped): {', '.join(missing)}")
        worse = compare(data, old)
        for w in worse:
            print("WORSE", w)
        return 1 if worse else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
