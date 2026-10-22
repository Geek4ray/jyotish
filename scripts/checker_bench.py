"""The checker benchmark (SPEC Layer 7 items 10-11): labelled sentences, the code validator alone and
then validator + semantic checker, scored.

    .venv/bin/python scripts/checker_bench.py --build      # (re)writes tests/fixtures/checker_bench.jsonl
    .venv/bin/python scripts/checker_bench.py              # validator alone; + live checker with credentials
    .venv/bin/python scripts/checker_bench.py --offline    # validator alone, never the API

Rows: {id, sentence, tags, facts (the data the checker is given, as JSON), label (accept | reject),
category, origin, where (claim | summary | paragraph), area, finding_id, validator (the validator's
inputs: allowed tags, offered votes, chains, family_rule), audit (accepted rows)}.

Accepted rows are the 45 sentences of examples/reference_reading_curious.json, each read against its
facts (the `audit` note says what was checked). Rejected rows are made from them by one change each:
planet_swapped, house_changed, sign_changed, dignity_changed, dasha_lord_changed, negated,
unsupported_clause, tier_word. The reading names no dasha lord, so a dasha row adds a clause naming
the period lord that activates a planet, cites the chain finding whose facts name the true lord, and
names a wrong one. A tier word is a validator matter only in a summary or paragraph sentence, so those
rows are made from those. Then the known-bad sentences: the first recording's originals that
tests/fixtures/narration_career_edited.json corrected (its note lists them), and the hand-made bad
draft of tests/test_narrate.py.

The positive class is "reject": precision is the share of rejections that were right, recall the
share of bad sentences caught."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jyotish.narrate import (TAG, TIER_WORDS, _check_payload, _summary_checks, findings, offered_chains,  # noqa: E402
                             offered_votes, sentences, validate, validate_summary)

BENCH = ROOT / "tests" / "fixtures" / "checker_bench.jsonl"
READING = ROOT / "examples" / "reference_reading_curious.json"
SCORECARD = ROOT / "docs" / "checker_scorecard.md"
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
         "Aquarius", "Pisces"]
ORD = {1: "1st", 2: "2nd", 3: "3rd"} | {n: f"{n}th" for n in range(4, 13)}
CONSTRUCTED = ["planet_swapped", "house_changed", "sign_changed", "dignity_changed", "dasha_lord_changed",
               "negated", "unsupported_clause", "tier_word"]
# Categories that are tag or wording errors: the validator alone must reject every one of them.
WORDING = {"tier_word", "untagged", "tag_not_offered", "forbidden_word", "family_not_cited"}
SEMANTIC = set(CONSTRUCTED) - WORDING | {"refers_to_another_claim", "misattached_detail", "wrong_dignity"}


# --- the chart behind the reading ---------------------------------------------------------------

def reading_chart():
    from jyotish.uncertainty import assess
    r = json.loads(READING.read_text())
    ch = r["chart"]
    utc = datetime.fromisoformat(ch["birth_utc"])
    return r, assess(utc, ch["lat"], ch["lon"], true_node=ch["conventions"]["node"] == "true",
                     seed=ch.get("seed", 0)), date.fromisoformat(r["as_of"])


# --- building the rows --------------------------------------------------------------------------

def _bare(s: str) -> str:
    return TAG.sub("", s)


def _tags(s: str) -> list[str]:
    return [f"{k}:{v}" for k, v in TAG.findall(s)]


def _swap_once(s: str, old: str, new: str) -> str | None:
    """Replace the first whole-word `old` in the sentence's words (never inside a tag)."""
    m = TAG.search(s)
    head, tail = (s[:m.start()], s[m.start():]) if m else (s, "")
    out = re.sub(rf"\b{re.escape(old)}\b", new, head, count=1)
    return None if out == head else out + tail


def _before_tags(s: str, clause: str) -> str:
    m = re.search(r"\s*(\[[^\]]+\]\s*)+[.!?]?\s*$", s)
    head, tail = (s[:m.start()], s[m.start():]) if m else (s.rstrip("."), ".")
    return f"{head}{clause}{tail}"


def planet_swapped(s, row):
    if row["where"] == "claim" and row["finding_id"].startswith(("place.", "yoga.")):
        return None                                   # a planet may be the rule's name; keep this semantic
    named = [p for p in PLANETS if re.search(rf"\b{p}\b", _bare(s))]
    if not named:
        return None
    other = next((p for p in ["Jupiter", "Saturn", "Venus", "Mars", "Mercury"] if p not in named), None)
    if other is None:
        return None
    p = named[0]
    if p in ("Sun", "Moon"):                           # "the Sun" becomes "Jupiter", not "the Jupiter"
        for art in ("The", "the"):
            out = _swap_once(s, f"{art} {p}", other)
            if out:
                return out
    return _swap_once(s, p, other)


def house_changed(s, row):
    for n in (10, 11, 7, 2, 6, 8, 1):
        if re.search(rf"\bthe {ORD[n]}\b", _bare(s)):
            return _swap_once(s, f"the {ORD[n]}", f"the {ORD[(n + 2) % 12 + 1]}")
    return None


def sign_changed(s, row):
    for i, name in enumerate(SIGNS):
        if re.search(rf"\b{name}\b", _bare(s)):
            return _swap_once(s, name, SIGNS[(i + 4) % 12])
    return None


def dignity_changed(s, row):
    for old, new in (("exalted", "debilitated"), ("its own sign", "its debilitation sign"),
                     ("a friend's sign", "an enemy's sign"), ("an enemy's sign", "its exaltation sign"),
                     ("is neutral", "is exalted")):
        if old in _bare(s):
            return _swap_once(s, old, new)
    return None


def negated(s, row):
    for old, new in (("favours", "does not favour"), ("is favourable", "is not favourable"),
                     ("goes against", "does not go against"), ("sits in", "does not sit in"),
                     ("forms", "does not form"), ("sit together", "do not sit together"), ("holds", "does not hold")):
        if re.search(rf"\b{old}\b", _bare(s)):
            return _swap_once(s, old, new)
    return None


def unsupported_clause(s, row):
    clause = (", and Jupiter's aspect on the 10th strengthens it" if row["area"] == "career" else
              ", and Jupiter aspects the 7th from the 1st to protect it" if row["area"] == "marriage" else
              ", and the 12th house adds its support")
    return _before_tags(s, clause)


def tier_word(s, row):
    if row["where"] == "claim":
        return None                                   # the validator reads tier words in summaries and paragraphs
    if s.startswith(("Five", "Six", "Of ")):
        return None
    first, rest = s.split(" ", 1)
    return f"In a strong chart, {first.lower() if first in ('The', 'Most') else first} {rest}"


# dasha_lord_changed: (area, chain tag, planet, the true lord, the wrong lords) on the reading's chart.
DASHA = [("career", "chain:career.karaka", "Sun", "Jupiter", ["Saturn", "Venus"]),
         ("marriage", "chain:marriage.lord", "Mars", "Mercury", ["Ketu", "Jupiter"]),
         ("longevity", "chain:longevity.lord", "Venus", "Mercury", ["Saturn", "Rahu"])]


def build() -> list[dict]:
    r, chart, as_of = reading_chart()
    names = [a["name"] for a in r["areas"]]
    offered = {n: findings(chart, n, as_of)[0] for n in names}
    by_id = {f["finding_id"]: f for fs in offered.values() for f in fs}
    votes = offered_votes(chart, names)
    chains = offered_chains(chart, names)
    area_tags = {n: sorted(set().union(*(set(f["allowed_tags"]) for f in offered[n]))) for n in names}
    all_tags = sorted(set().union(*map(set, area_tags.values())))
    curious = r["depth"] == "curious"

    def inputs(where, area, fid):
        if where == "claim":
            f = by_id.get(fid)
            return {"allowed": sorted(f["allowed_tags"]) if f else [], "offered_votes": votes[area],
                    "chains": chains[area], "family_rule": not curious}
        if where == "paragraph":
            return {"allowed": area_tags[area], "offered_votes": votes[area], "chains": chains[area],
                    "family_rule": False}
        return {"allowed": all_tags, "offered_votes": {k: sorted({votes[n][k] for n in names if k in votes[n]})
                                                       for n in names for k in votes[n]},
                "chains": {k: v for n in names for k, v in chains[n].items()}, "family_rule": not curious}

    def facts(where, sentence, fid):
        if where == "claim" and fid in by_id and set(_tags(sentence)) <= set(by_id[fid]["allowed_tags"]):
            return _check_payload(by_id[fid])
        checks = _summary_checks(sentence, by_id)
        return checks[0][2] if checks else json.dumps({"findings": []})

    rows = []
    for i, s in enumerate(sentences(r["summary"]["text"])):
        rows.append({"where": "summary", "area": None, "finding_id": None, "sentence": s,
                     "origin": f"reading summary sentence {i + 1}"})
    for a in r["areas"]:
        for c in a["claims"]:
            rows.append({"where": "claim", "area": a["name"], "finding_id": c["finding_id"], "sentence": c["text"],
                         "origin": f"reading claim {a['name']}/{c['finding_id']}"})
        for i, s in enumerate(sentences(a["paragraph"] or "")):
            rows.append({"where": "paragraph", "area": a["name"], "finding_id": None, "sentence": s,
                         "origin": f"reading paragraph {a['name']} sentence {i + 1}"})
    accepted = []
    for k, row in enumerate(rows):
        row |= {"id": f"accept-{k + 1:02d}", "label": "accept", "category": "accepted",
                "audit": audit(row["sentence"], chart)}
        accepted.append(row)

    out = list(accepted)
    per_cat = {c: 0 for c in CONSTRUCTED}
    cap = 9
    for name in CONSTRUCTED:
        if name == "dasha_lord_changed":
            continue
        fn = globals()[name]
        for row in accepted:
            if per_cat[name] >= cap:
                break
            new = fn(row["sentence"], row)
            if new and new != row["sentence"]:
                per_cat[name] += 1
                out.append({"id": f"{name}-{per_cat[name]}", "where": row["where"], "area": row["area"],
                            "finding_id": row["finding_id"], "sentence": new, "label": "reject", "category": name,
                            "origin": f"constructed from {row['id']} ({row['origin']})"})
    para = {a: [x for x in accepted if x["where"] == "paragraph" and x["area"] == a and x["sentence"].startswith(
        ("The Sun", "Mercury", "Mars", "Ketu"))] for a in names}
    for area, tag, planet, true_lord, wrong in DASHA:
        base = para[area][0]
        for w in wrong:
            per_cat["dasha_lord_changed"] += 1
            the = f"the {planet}" if planet in ("Sun", "Moon") else planet
            s = _before_tags(base["sentence"], f", and the current major period of {w} activates {the} through its "
                                               f"nakshatra")
            s = s[:-1] + f" [{tag}]." if s.endswith(".") else s
            out.append({"id": f"dasha_lord_changed-{per_cat['dasha_lord_changed']}", "where": "paragraph", "area": area,
                        "finding_id": None, "sentence": s, "label": "reject", "category": "dasha_lord_changed",
                        "origin": f"constructed from {base['id']}: {planet} is activated by {true_lord}'s period, "
                                  f"not {w}'s"})
    out += known_bad(r)
    for row in out:
        row["tags"] = _tags(row["sentence"])
        row["validator"] = inputs(row["where"], row["area"] or "career", row["finding_id"])
        row["facts"] = facts(row["where"], row["sentence"], row["finding_id"])
    return out


def audit(sentence: str, chart) -> str:
    """What was checked against the chart for an accepted row: each "above / below its required
    strength" against the Shadbala ratio, each dignity word against the D1 dignity; the rest of the
    sentence was read against its facts by hand (2026-10-22)."""
    notes = []
    sb = chart.features.shadbala.planets
    bare = _bare(sentence)
    planet_rx = re.compile(r"\b(" + "|".join(PLANETS[:7]) + r")\b")
    for m in re.finditer(r"\b(above|below|short of)\b[^.;,]*?required strength", bare):
        before = planet_rx.findall(bare[:m.start()])
        if not before:
            continue
        p, want = before[-1], m.group(1) == "above"       # the planet the phrase is about: the nearest before it
        group = [p] + ([before[-2]] if len(before) > 1 and re.search(rf"\b{before[-2]} and {p}\b", bare) else [])
        for q in group:
            ok = (sb[q].ratio >= 1) == want
            notes.append(f"{q} {'above' if want else 'below'} required strength: ratio {sb[q].ratio:.2f} "
                         f"{'ok' if ok else 'CONTRADICTED'}")
    for p in PLANETS[:7]:
        if re.search(rf"\b{p}\b[^.;]*?\bexalted\b", bare) and chart.bodies[p].dignity == "exalted":
            notes.append(f"{p} exalted: D1 dignity {chart.bodies[p].dignity} ok")
    return "; ".join(notes) or "read against its facts by hand; no strength or dignity word to compute"


def known_bad(reading) -> list[dict]:
    r1 = json.loads((ROOT / "tests" / "fixtures" / "narration_career_opus55_r1.json").read_text())["drafts"][0]
    claims = {c["finding_id"]: c["text"] for a in r1["areas"] for c in a["claims"]}
    summ = sentences(r1["summary"])
    src = "narration_career_opus55_r1.json, corrected in narration_career_edited.json"
    rows = [
        ("claim", "career", "yoga.kendra_trikona_raja@lagna", claims["yoga.kendra_trikona_raja@lagna"],
         "refers_to_another_claim", "opens 'The same conjunction', which the checker cannot see"),
        ("claim", "career", "yoga.ruchaka@lagna+sun", claims["yoga.ruchaka@sun"], "refers_to_another_claim",
         "'again forms Ruchaka', 'the same weakening'"),
        ("claim", "career", "vote:career.kp", claims["vote:career.kp"], "tag_not_offered",
         "the KP vote abstains under v2 and is not offered; the sentence also gives Ketu the cusp's star"),
        ("claim", "career", "vote:career.varga", claims["vote:career.varga"], "wrong_dignity",
         "under varga v2 Jupiter and the Sun are in friends' signs in D10, not poorly placed"),
        ("summary", None, None, summ[1], "family_not_cited",
         "names five votes and cites two, at astrologer depth"),
        ("summary", None, None, summ[2], "forbidden_word", "timing and the engine, tagged with the house vote"),
        ("summary", None, None, "Career is likely to peak soon [vote:career.house].", "forbidden_word",
         "tests/test_narrate.py INVALID: a probability word"),
        ("claim", "career", "yoga.budhaditya@lagna", "The Sun and Mercury share Aquarius, which forms Budhaditya yoga.",
         "untagged", "tests/test_narrate.py INVALID: a claim with no tag"),
        ("claim", "career", "vote:career.house", "The house vote is for career [rule:yoga.ruchaka].", "tag_not_offered",
         "tests/test_review.py: a tag the finding does not offer"),
    ]
    out = []
    for k, (where, area, fid, s, cat, why) in enumerate(rows, 1):
        origin = (f"{src}: {why}" if "INVALID" not in why and "test_review" not in why else why)
        out.append({"id": f"known_bad-{k}", "where": where, "area": area, "finding_id": fid, "sentence": s,
                    "label": "reject", "category": cat, "origin": origin, "astrologer_depth": where == "summary"})
    return out


# --- running --------------------------------------------------------------------------------------

def validator_errors(row: dict) -> list[str]:
    v = row["validator"]
    if row.get("astrologer_depth"):
        v = dict(v, family_rule=True)
    allowed = set(v["allowed"])
    ov = {k: (set(x) if isinstance(x, list) else x) for k, x in v["offered_votes"].items()}
    if row["where"] == "claim":
        errs = validate(row["sentence"], allowed, offered_votes=ov, family_rule=v["family_rule"], chains=v["chains"])
        if not TAG.search(row["sentence"]):
            errs.append(f"claim without a tag: {row['sentence']!r}")
        return errs
    where = f"{row['area']} paragraph" if row["where"] == "paragraph" else "summary"
    return validate_summary(row["sentence"], allowed, offered_votes=ov, where=where, family_rule=v["family_rule"],
                            chains=v["chains"])


def load() -> list[dict]:
    return [json.loads(x) for x in BENCH.read_text().splitlines() if x.strip()]


def run_validator(rows) -> dict[str, tuple[bool, str]]:
    """row id -> (rejected, reason)."""
    out = {}
    for row in rows:
        errs = validator_errors(row)
        out[row["id"]] = (bool(errs), "; ".join(errs[:2]))
    return out


def run_live(rows, config=None) -> tuple[dict[str, tuple[bool, str]], dict]:
    """Validator, then the semantic checker on every row the validator passes."""
    from jyotish.narrate import CONFIG, AnthropicChecker
    config = config or CONFIG
    checker = AnthropicChecker(config)
    v = run_validator(rows)
    out, usage, todo = {}, {"input_tokens": 0, "output_tokens": 0, "calls": 0}, []
    for row in rows:
        if v[row["id"]][0]:
            out[row["id"]] = v[row["id"]]
        else:
            todo.append(row)
    results = checker.check_many([(row["sentence"], row["facts"]) for row in todo])
    for row, (result, meta) in zip(todo, results):
        bad = [p for p in result.propositions if not p.supported]
        out[row["id"]] = (bool(bad), "; ".join(f"{p.text!r}: {p.evidence}" for p in bad[:2]) or "supported")
        u = (meta or {}).get("usage") or {}
        usage["input_tokens"] += u.get("input_tokens", 0)
        usage["output_tokens"] += u.get("output_tokens", 0)
        usage["calls"] += 1
    return out, usage


def scores(rows, preds) -> dict:
    def prf(rs):
        tp = sum(1 for r in rs if r["label"] == "reject" and preds[r["id"]][0])
        fp = sum(1 for r in rs if r["label"] == "accept" and preds[r["id"]][0])
        fn = sum(1 for r in rs if r["label"] == "reject" and not preds[r["id"]][0])
        p = tp / (tp + fp) if tp + fp else 1.0
        rec = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * p * rec / (p + rec) if p + rec else 0.0
        return {"n": len(rs), "tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": rec, "f1": f1}
    out = {"overall": prf(rows)}
    for cat in sorted({r["category"] for r in rows}):
        out[cat] = prf([r for r in rows if r["category"] == cat])
    return out


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "unknown"


def _table(s: dict, accept_note: bool = True) -> list[str]:
    out = ["| category | n | caught / false rejects | precision | recall | F1 |", "| --- | --- | --- | --- | --- | --- |"]
    for cat, x in s.items():
        caught = f"{x['fp']} false rejects" if cat == "accepted" else f"{x['tp']} of {x['tp'] + x['fn']}"
        out.append(f"| {cat} | {x['n']} | {caught} | {x['precision']:.3f} | {x['recall']:.3f} | {x['f1']:.3f} |")
    return out


def _misses(rows, preds) -> list[str]:
    out = []
    for r in rows:
        rejected, why = preds[r["id"]]
        if (r["label"] == "reject") != rejected:
            kind = "missed" if r["label"] == "reject" else "false reject"
            out.append(f"- `{r['id']}` ({r['category']}, {kind}): {r['sentence']}  \n  reason: {why or '(none given)'}")
    return out or ["None."]


def report(rows, vpred, live) -> str:
    from jyotish.narrate import CONFIG
    vs = scores(rows, vpred)
    L = ["# Checker benchmark", "",
         f"Run {date.today().isoformat()} at commit `{_commit()}` by `scripts/checker_bench.py` on "
         f"`tests/fixtures/checker_bench.jsonl` ({len(rows)} rows: {sum(r['label'] == 'accept' for r in rows)} accept, "
         f"{sum(r['label'] == 'reject' for r in rows)} reject). The positive class is reject.", "",
         "## The code validator alone", "", *_table(vs), "",
         "The validator reads tags and words, not meaning: it is meant to catch the tag and wording categories "
         f"({', '.join(sorted(WORDING))}) and to leave the semantic ones to the checker.", "",
         "Misses and false rejects (validator alone):", "", *_misses(rows, vpred), ""]
    if live is None:
        L += ["## Validator + semantic checker (live)", "",
              "Not run: no Anthropic credentials in this environment (ANTHROPIC_API_KEY unset). Run "
              "`scripts/checker_bench.py` where they are; it fills this section with the checker's precision, recall "
              f"and F1, every miss with the checker's reason, the model ({CONFIG.model}), the checker effort "
              f"({CONFIG.checker_effort}) and the cost.", ""]
    else:
        lp, usage, seconds = live
        ls = scores(rows, lp)
        L += ["## Validator + semantic checker (live)", "",
              f"Model {CONFIG.model}, checker effort {CONFIG.checker_effort}; {usage['calls']} checker calls, "
              f"{usage['input_tokens']} input and {usage['output_tokens']} output tokens, {seconds:.0f} s. Cost: "
              "the token counts at the account's current price (not computed here).", "", *_table(ls), "",
              "Misses and false rejects, with the checker's reason:", "", *_misses(rows, lp), ""]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args(argv)
    if a.build:
        rows = build()
        BENCH.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        print(f"{len(rows)} rows -> {BENCH}")
        return 0
    rows = load()
    vpred = run_validator(rows)
    live = None
    if not a.offline and os.environ.get("ANTHROPIC_API_KEY"):
        t = time.time()
        lp, usage = run_live(rows)
        live = (lp, usage, time.time() - t)
    SCORECARD.write_text(report(rows, vpred, live))
    s = scores(rows, vpred)["overall"]
    print(f"validator alone: precision {s['precision']:.3f} recall {s['recall']:.3f} F1 {s['f1']:.3f} -> {SCORECARD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
