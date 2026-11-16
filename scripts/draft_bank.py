"""Draft the sentence bank (SPEC Layer 8 rev 134, "The layered answer"; docs/spec_notes_2026-11-15.md, step 3).

Which rows: every plan signature (`jyotish.plan`) that the areas career, marriage and wealth produce on random
synthetic charts (`synthetic_cohort.births`, no one's data), with every question kind and a "when" turn, plus every
opening, period and stretch signature; a fact row for each, and a meaning row per area for each fired rule and hidden
weakness of those three areas. A row already in data/bank is kept (an approved row is never redrafted); `--redraft`
replaces the draft rows.

How: claude-sonnet-5-5 on the anthropic backend (the key from the gitignored .env as ANTHROPIC_API_KEY, never
printed) drafts the three variants of about ten rows a call, given for each signature its slots, the engine's own
sentence (what a fact row may say, and no more), a chart's values for the slots and the facts behind it; a meaning
row is given the rule's names, glossary definition, themes, outcomes and citation (its `source`). Every variant is
held to `bank.row_errors` (never-show, client and tier words; declared slots); a row that fails is redrafted once
with the reasons. Then every fact variant, filled with that chart's values, is checked once by the gate checker
(JYOTISH_CHECKER_BACKEND, GLM-5.3-Flash at temperature 0) against the signature's facts and the engine's sentence; a
row with an unsupported variant is redrafted once with the checker's evidence and checked again, and left out if it
still fails. The verdicts are kept on the row (`checks`).

The expected cost is printed first; above --budget (USD 2) nothing is called.

    .venv/bin/python scripts/draft_bank.py --estimate     # the signatures and the expected cost, no model call
    .venv/bin/python scripts/draft_bank.py                # draft, check, write data/bank/*.yaml as status draft
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from pydantic import BaseModel, Field  # noqa: E402

MODEL = "claude-sonnet-5-5"
AREAS = ["career", "marriage", "wealth"]
AS_OF = date(2026, 11, 15)
PER_CALL = 10
SHAPES = 4                # slot shapes a fact variant is checked on (bank.shape_of): one value, several, empty, a node
# The estimate: characters a row's prompt part takes (signature, slots, engine sentence, values, facts) at 3.5 a
# token, the fixed prompt, the tokens a row's three variants take out, every call possibly sent twice (a redraft);
# the checker's tokens a variant as the live checks of 2026-11-01 measured them per sentence (16,773 in and 7,074
# out over about 4 sentences a turn), at the gate checker's price.
CHARS_PER_TOKEN, SYSTEM_TOKENS, OUT_PER_ROW, REDRAFT = 3.5, 1800, 260, 2.0
CHECK_TOKENS = (4200, 1800)
TODAY = date.today()


class DraftRow(BaseModel):
    signature: str
    variants: list[str] = Field(min_length=3, max_length=3)


class Drafts(BaseModel):
    rows: list[DraftRow]


SYSTEM = """You draft rows of a sentence bank for Tatva, a Vedic astrology conversation. A client reads these \
sentences about their own birth chart. Each row is one sentence in three variants that say the same thing in \
different words and shapes. The engine fills the slots, written {like_this}, with the chart's values.

For a FACT row you are given the engine's own sentence and the facts behind it. Each variant says what the engine's \
sentence says, and nothing more: no new claim, no effect, no promise, no figure, no date, no advice. Use only the \
slots listed for the row, each as {slot}; you may leave out a slot the sentence can do without, never add one. Keep \
the slots' values in the places they make sense: {planet} is a planet's name with its article (the Sun, Mars), \
{house} an ordinal (10th), {area} a phrase in the client's words (your career), {dignity} a phrase that can be empty \
(in a friendly sign), so write ", {dignity}" where it closes a clause.

For a MEANING row you are given a rule (a classical combination) or a weakness, its definition, its themes, the \
outcomes it is read for and its citation, and one area of life. Each variant says what it is traditionally read to \
mean for that area, as tradition, never as a prediction: "is traditionally read as", "is said to", "texts link it \
with". One sentence, no promise, no figure, no date, no advice, nothing about health, death or another person. A \
reduced rule's meaning says the promise is read as reduced.

Every variant: one sentence, plain warm English to "you", 12 to 35 words, ending with a full stop. Never use these \
words: vote, family (except "your family"), KP, Krishnamurti, analysis, score, D1 to D60, "marked as", "indications", \
arudha, dasha, cusp, sub-lord, Shadbala, Bhava Bala, engine, percentile, term, sample, house system, ayanamsa, \
derivation, rupa, strong, strongest, weak, weakest, moderate, mixed, "I". A Sanskrit name (Ruchaka, Budhaditya) is \
said with its plain meaning in the same sentence: in a rule's row write {named} where the rule is named (its name with \
its plain meaning in brackets, filled by the engine), never {name} alone. A weakness's meaning says "a house that \
drains it", "a feeble state" or "less strength than it needs", never its Sanskrit name. Return one row for each \
signature asked, with its signature as given.

A VOCATION meaning row (vocation.works.<planet>@career) is given one planet: each variant says the kinds of work \
tradition links with that planet where it shapes the house of work, as tradition ("is traditionally linked with work \
in", "texts associate it with"), naming three to five kinds of work in plain words. Never a promise about the \
client's own job, never advice, never a figure."""

FILES = {"opening": "openings", "verdict": "verdicts", "stability": "stability", "family": "families", "rule": "rules",
         "weakness": "weaknesses", "period": "periods", "stretch": "stretches", "vocation": "vocations"}
REDRAFT_NOTE = "Your last draft of these rows could not stand. Redraft each, for the reasons given:"


def _signatures(n: int, seed: int) -> dict[tuple[str, str], dict]:
    """(signature, kind) -> a sample: slots, facts, the engine's sentence, the area; from plans over `n` random charts
    and the reference chart (its payload gives the stretches' facts)."""
    from synthetic_cohort import births
    from jyotish.chart import compute
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    from jyotish.plan import plan
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    from jyotish.bank import shape_of
    kinds = ["amount", "yes_no", "when", "why"]
    found: dict[tuple[str, str], dict] = {}

    def take(p):
        for i in p.items:
            if not i.engine:
                continue                      # a "when" item from a chart with no payload: taken from the reference
            sample = {"slots": i.slots, "facts": i.facts, "engine": i.engine, "area": i.area, "part": i.part}
            first = found.setdefault((i.signature, "fact"), sample | {"shapes": []})
            # Up to SHAPES samples of distinct slot shapes (review 2026-11-15, H1): a fact variant is checked on each.
            if len(first["shapes"]) < SHAPES and shape_of(i.slots) not in [shape_of(x["slots"]) for x in first["shapes"]]:
                first["shapes"].append(sample)
            if i.part in ("rule", "weakness") and i.area in AREAS:
                found.setdefault((f"{i.signature}@{i.area}", "meaning"), sample)
            if i.part == "vocation" and i.meaning:
                # A planet's kinds of work: its row may use the planet and the area only, the slots every vocation
                # item has (decision 3).
                found.setdefault((f"{i.meaning}@career", "meaning"),
                                 sample | {"slots": {k: i.slots[k] for k in ("planet", "area")}})
    ref = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    data = cached_payload(ref, AS_OF, *full_range(AS_OF), AREAS)
    for direction in ("both", "against"):
        take(plan(ref, "draft", AREAS, direction, kinds, as_of=AS_OF, when=True, data=data))
    # One cannot-give line for every combination of asks that needs one (SPEC rev 136, "The shaped answer", decision 1).
    from jyotish.plan import CANNOT_LINE
    for key in CANNOT_LINE:
        take(plan(ref, "draft", AREAS[:1], "both", key.split("."), as_of=AS_OF, when=True, data=data))
    take(plan(ref, "draft", AREAS, "against", kinds, as_of=AS_OF, weakest=True, data=data))
    vocation = [{"kind": "vocation", "areas": ["career"]}]          # the field of work (SPEC rev 136, decision 3)
    take(plan(ref, "draft", ["career"], "both", ["vocation"], as_of=AS_OF, data=data, parts=vocation))
    for b in births(n, seed):
        c = compute(datetime.fromisoformat(f"{b['date']}T{b['time']}"), b["lat"], b["lon"], true_node=False)
        take(plan(c, "draft", AREAS, "both", kinds, as_of=AS_OF, weakest=False))
        take(plan(c, "draft", ["career"], "both", ["vocation"], as_of=AS_OF, parts=vocation))
        # Every other area's fact signatures too (2026-11-16: the varga sentence on another divisional chart,
        # family.varga.*.other, arises in personality, mind and the areas with two vargas); meaning rows stay the
        # three areas' (`take`).
        take(plan(c, "draft", [x for x in c.scored.areas if x not in AREAS and x != "synastry"], "both", kinds,
                  as_of=AS_OF))
        take(plan(c, "draft", AREAS, "against", kinds, as_of=AS_OF, weakest=True))
    return found


def _rule_context(signature: str) -> dict:
    from jyotish.narrate import glossary_for
    from jyotish.rules import default_rules
    rule_id = ".".join(signature.split("@")[0].split(".")[1:3])
    rule = next((r for r in default_rules() if r.id == rule_id), None)
    if rule is None:
        return {}
    d = rule.data
    src = "; ".join(f"{s['text']}, {s['edition']}, {s['chapter']}.{s['verse']}" for s in d.get("source", []))
    return {"rule": rule_id, "names": d.get("names"), "definition": list(glossary_for({"rule_id": rule_id}).values()),
            "themes": d.get("themes"), "outcomes": d.get("outcomes"), "source": src}


WEAKNESS_SOURCE = {
    "mks": "Marana karaka sthana: the Jaimini tradition as taught by Sanjay Rath (constants.MARANA_KARAKA_STHANA)",
    "mrita": "Baladi avastha, the Mrita state: BPHS (Santhanam 1984) 45.3-4",
    "low_strength": "Shadbala below the planet's required strength: BPHS (Santhanam 1984) chapter 27"}
WEAKNESS_WHAT = {
    "mks": "the planet sits in its marana karaka sthana, a house counted as draining it whatever its sign",
    "mrita": "the planet is in the Mrita (dead) state of the five Baladi age states by its degree in its sign",
    "low_strength": "the planet's six-fold strength is below what it needs to give fully what it promises"}
# One planet's weaknesses in one sentence (SPEC rev 136, "The shaped answer", decision 2): any of the three above.
WEAKNESS_SOURCE["planet"] = "; ".join(WEAKNESS_SOURCE[k] for k in ("mks", "mrita", "low_strength"))
WEAKNESS_WHAT["planet"] = ("the planet, the area's main ruler or main significator, has one or more of these hidden "
                           "weaknesses, listed in its {weaknesses} slot: " + "; ".join(
                               WEAKNESS_WHAT[k] for k in ("mks", "mrita", "low_strength"))
                           + ". The meaning is of the planet so held back, for the area, whichever of them it has")


# A planet's kinds of work (decision 3): the classical lists of livelihood by planet. The verse was not read in a named
# edition, so the source says so, and every row is draft until the astrologer approves it.
VOCATION_SOURCE = ("Brihat Jataka 10 (Karmajiva), the kinds of livelihood linked with each planet; the verse not yet "
                   "read in a named edition")
VOCATION_WHAT = ("the kinds of work tradition links with this planet where it rules the 10th house, sits in it or is "
                 "strong in the D10, the divisional chart for work")


def _source(key: tuple[str, str]) -> str | None:
    sig, kind = key
    if kind != "meaning":
        return None
    base = sig.split("@")[0]
    if base.startswith("vocation.works."):
        return VOCATION_SOURCE
    if base.startswith("rule."):
        return _rule_context(base).get("source") or None
    return WEAKNESS_SOURCE.get(base.split(".")[1])


def _ask(key: tuple[str, str], sample: dict) -> dict:
    sig, kind = key
    item = {"signature": sig, "kind": kind, "slots": sorted(sample["slots"])}
    if kind == "fact":
        item |= {"engine_sentence": sample["engine"], "example_values": sample["slots"],
                 "facts": sample["facts"]}
    else:
        base, area = sig.split("@")
        item |= {"area": area, "example_values": sample["slots"]}
        if base.startswith("rule."):
            item |= {"rule": _rule_context(base), "reduced": base.split(".")[-1] == "reduced" or ".reduced." in base}
        elif base.startswith("vocation.works."):
            item |= {"vocation_planet": base.split(".")[-1].capitalize(), "what": VOCATION_WHAT, "source": VOCATION_SOURCE}
        else:
            w = base.split(".")[1]
            item |= {"weakness": WEAKNESS_WHAT[w], "source": WEAKNESS_SOURCE[w]}
    return item


def check_data(sample: dict) -> dict:
    """What a fact variant is checked against: the item's facts (with what its area is: its houses, main house, lord
    and significators), the engine's own sentence, the plain words the engine uses for a dignity, and the glossary's
    definitions of the terms the facts name."""
    from jyotish.narrate import DIGNITY_PLAIN, glossary_for
    data = {"facts": sample["facts"], "the engine's own sentence (the row says this, in other words)": sample["engine"],
            "the engine's plain words for a dignity": DIGNITY_PLAIN}
    gl = glossary_for({"facts": sample["facts"], "engine": sample["engine"]})
    if gl:
        data["glossary"] = gl
    return data


def samples_for(row, sample: dict) -> list[dict]:
    """The samples a fact row is checked on: each shape whose slots the row's variants can be filled from (as the
    composer would fill them: every slot the row declares has a value, a dignity excepted)."""
    out = []
    for x in sample.get("shapes") or [sample]:
        if set(row.slots) <= set(x["slots"]) and all(x["slots"][s] for s in row.slots if s != "dignity"):
            out.append(x)
    return out


def check_rows(rows: dict, found: dict, checker, checker_model: str, spent: dict) -> tuple[dict, dict]:
    """Every fact variant of `rows` ({(signature, kind): BankRow}), filled with each of its signature's sample shapes,
    checked once by the gate checker against that sample's facts and engine sentence; each verdict is kept on the row
    with its shape. Returns the rows and, per signature, why a variant was refused."""
    from jyotish.bank import Check, shape_of
    from jyotish.costs import cost
    asks, where = [], []
    for k, r in rows.items():
        if k[1] != "fact" or k not in found:
            continue
        fits = samples_for(r, found[k])
        if not fits:
            continue                      # no sample can fill it (the composer cannot either): its checks stand
        r.checks = []
        for x in fits:
            data = json.dumps(check_data(x), default=str, indent=1)
            for i in range(3):
                asks.append((r.fill(i, x["slots"]), data))
                where.append((k, i, shape_of(x["slots"])))
    results = checker.check_many(asks) if asks else []
    # A call that returned no verdict (max_tokens, "(no verdict)"; a failed call, "unchecked") is asked again once; a
    # second miss stands as a refusal, so an unchecked variant is never shown.
    missed = lambda res, meta: (meta or {}).get("unchecked") or any(p.text in ("(no verdict)", "(unchecked)")
                                                                   for p in res.propositions)
    again = [n for n, (res, meta) in enumerate(results) if missed(res, meta)]
    if again:
        for n, r in zip(again, checker.check_many([asks[n] for n in again])):
            results[n] = r
    bad = defaultdict(list)
    for (k, i, shape), (sentence, _), (res, meta) in zip(where, asks, results):
        ok = all(p.supported for p in res.propositions)
        ev = "; ".join(p.evidence for p in res.propositions if not p.supported)
        rows[k].checks.append(Check(variant=i, sentence=sentence, supported=ok, evidence=ev[:400],
                                    model=checker_model, on=TODAY, shape=shape))
        spent["checker"] = spent.get("checker", 0.0) + (
            cost(checker_model, (meta or {}).get("usage") or {}, "api.deepinfra.com") or 0)
        if not ok:
            bad[k[0]].append(f"variant {i + 1} ({sentence!r}) is not stated by the facts: {ev}")
    return rows, dict(bad)


def estimate(found: dict) -> tuple[float, dict]:
    from jyotish.costs import price
    sonnet = price(MODEL, "api.anthropic.com")
    checker = price("zai-org/GLM-5.3-Flash", "api.deepinfra.com")
    asks = [json.dumps(_ask(k, v), default=str) for k, v in found.items()]
    calls = math.ceil(len(asks) / PER_CALL)
    tin = calls * SYSTEM_TOKENS + sum(len(a) for a in asks) / CHARS_PER_TOKEN
    tout = len(asks) * OUT_PER_ROW
    usd_draft = REDRAFT * (tin * sonnet[0] + tout * sonnet[1]) / 1e6
    facts = sum(1 for k in found if k[1] == "fact")
    usd_check = REDRAFT * facts * 3 * (CHECK_TOKENS[0] * checker[0] + CHECK_TOKENS[1] * checker[1]) / 1e6
    return usd_draft + usd_check, {"rows": len(asks), "fact rows": facts, "meaning rows": len(asks) - facts,
                                   "calls": calls, "draft USD": round(usd_draft, 3), "check USD": round(usd_check, 3)}


def draft(backend, keys: list[tuple[str, str]], found: dict, notes: dict[str, list[str]] | None = None) -> tuple[dict, dict]:
    """signature -> three variants, for `keys` (one call), and the call's usage."""
    asks = [_ask(k, found[k]) | ({"why_redraft": notes[k[0]]} if notes and k[0] in notes else {}) for k in keys]
    head = (REDRAFT_NOTE + "\n\n") if notes else ""
    msg = head + "Draft these rows:\n" + json.dumps(asks, indent=1, default=str)
    done = backend.structured(system=SYSTEM, messages=[{"role": "user", "content": msg}], schema=Drafts, kind="draft_bank",
                              effort="medium", thinking=None, max_tokens=8000)
    out = {}
    if done.parsed is not None:
        for r in done.parsed.rows:
            out[r.signature] = r.variants
    return out, (done.meta or {}).get("usage") or {}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--estimate", action="store_true", help="print the signatures and the expected cost, no model call")
    ap.add_argument("--budget", type=float, default=2.0, help="stop before any call when the estimate is above this (USD)")
    ap.add_argument("--charts", type=int, default=300, help="random charts the signatures are gathered from")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--redraft", action="store_true", help="replace the draft rows already in the bank")
    ap.add_argument("--recheck", action="store_true",
                    help="draft nothing: check every fact row (or --signatures) on each sample shape, and write its checks")
    ap.add_argument("--signatures", nargs="*", default=None, help="with --recheck: only these signatures")
    ap.add_argument("--only", nargs="*", default=None,
                    help="draft only the signatures starting with one of these (a decision's own rows)")
    a = ap.parse_args(argv)
    from jyotish import envfile
    from jyotish.bank import BANK_DIR, BankRow, Check, dump_rows, load_bank, row_errors
    print(f"read from .env: {envfile.load(ROOT / '.env')}")                # names only, never a value
    if a.recheck:
        return recheck(a)
    if not os.environ.get("ANTHROPIC_API_KEY") and not a.estimate:
        raise SystemExit("ANTHROPIC_API_KEY is not set (the anthropic SDK reads it): nothing drafted")
    have = load_bank(strict=False)
    keep = {(r.signature, r.kind): r for r in have.rows if r.status == "approved" or not a.redraft}
    found = _signatures(a.charts, a.seed)
    todo = {k: v for k, v in sorted(found.items()) if k not in keep
            and (a.only is None or any(k[0].startswith(x) for x in a.only))}
    usd, parts = estimate(todo)
    print(f"{len(found)} signatures from {a.charts} random charts and the reference chart; {len(todo)} to draft")
    print("expected cost (worst case, every call and check sent twice): "
          + ", ".join(f"{k} {v}" for k, v in parts.items()) + f"; total USD {usd:.3f} (budget {a.budget})")
    if usd > a.budget:
        print(f"over the budget of USD {a.budget}: nothing drafted")
        return 2
    if a.estimate:
        for k in todo:
            print(f"  {k[1]:8} {k[0]}")
        return 0
    from jyotish.costs import cost
    from jyotish.narrate import CONFIG, AnthropicBackend, ModelChecker, make_backend
    writer = AnthropicBackend(MODEL, CONFIG)
    checker = ModelChecker(make_backend(os.environ.get("JYOTISH_CHECKER_BACKEND"), "checker", CONFIG), CONFIG)
    checker_model = checker.backend.describe().get("model")
    spent = {"writer": 0.0, "checker": 0.0}
    usage_all = []

    def run(keys, notes=None) -> dict:
        got = {}
        for i in range(0, len(keys), PER_CALL):
            chunk = keys[i:i + PER_CALL]
            out, usage = draft(writer, chunk, todo, notes)
            spent["writer"] += cost(MODEL, usage, "api.anthropic.com") or 0
            usage_all.append(usage)
            got.update(out)
            print(f"  drafted {len(got)} of {len(keys)} (USD {spent['writer']:.3f})", flush=True)
        return got

    def as_row(k, variants) -> BankRow:
        return BankRow(signature=k[0], kind=k[1], slots=sorted(todo[k]["slots"]), variants=variants,
                       source=_source(k), drafted_by=MODEL, drafted_on=TODAY, status="draft")

    def words(got: dict) -> tuple[dict, dict]:
        ok, bad = {}, {}
        for k in todo:
            if k[0] not in got:
                continue
            try:
                r = as_row(k, got[k[0]])
            except Exception as e:                               # three variants or not
                bad[k[0]] = [str(e)]
                continue
            # A variant may not use a slot the plan does not fill for this signature.
            errs = row_errors(r)
            (bad.__setitem__(k[0], errs) if errs else ok.__setitem__(k, r))
        return ok, bad

    def check(rows: dict) -> tuple[dict, dict]:
        """Every fact variant, filled with each sample shape's values, checked against its facts and engine sentence."""
        return check_rows(rows, todo, checker, checker_model, spent)

    keys = list(todo)
    got = run(keys)
    ok, bad = words(got)
    missing = [k for k in keys if k[0] not in got]
    if bad or missing:
        print(f"redrafting {len(bad) + len(missing)} rows for their words or a missing draft")
        again = run([k for k in keys if k[0] in bad or k in missing],
                    {s: e for s, e in bad.items()} | {k[0]: ["no draft came back for it"] for k in missing})
        ok2, bad = words(again)
        ok |= ok2
    ok, unsupported = check(ok)
    if unsupported:
        print(f"redrafting {len(unsupported)} fact rows the checker did not support")
        retry_keys = [k for k in ok if k[0] in unsupported]
        again = run(retry_keys, unsupported)
        ok3, bad3 = words(again)
        for k in retry_keys:
            ok.pop(k, None)
        ok3, still = check(ok3)
        for k, r in ok3.items():
            if k[0] not in still:
                ok[k] = r
        bad = {**bad, **bad3, **still}
    rows = list(keep.values()) + [r.model_copy(update={"checks": [c for c in r.checks if r.kind == "fact"]})
                                  for k, r in ok.items()]
    write_bank(rows)
    left = sorted(set(bad) | {k[0] for k in keys if k not in ok and k[0] not in bad})
    report = {"date": TODAY.isoformat(), "model": MODEL, "checker": checker_model, "rows_written": len(ok),
              "rows_kept": len(keep), "left_out": {s: bad.get(s, ["no draft"]) for s in left},
              "usd": {k: round(v, 4) for k, v in spent.items()}, "calls": len(usage_all)}
    log_run(report, len(rows))                                  # each run is kept
    print(f"wrote {len(ok)} rows (kept {len(keep)}); left out {len(left)}; spent USD "
          f"{spent['writer']:.3f} drafting and {spent['checker']:.3f} checking -> docs/bank_draft_2026-11-15.json")
    return 0


def write_bank(rows) -> None:
    from jyotish.bank import BANK_DIR, dump_rows, load_bank
    files = defaultdict(list)
    for r in rows:
        files["meanings" if r.kind == "meaning" else FILES[r.base.split(".")[0]]].append(r)
    BANK_DIR.mkdir(parents=True, exist_ok=True)
    for name, rs in sorted(files.items()):
        rs.sort(key=lambda r: r.signature)
        (BANK_DIR / f"{name}.yaml").write_text(
            f"# The sentence bank: {name} (SPEC Layer 8, The layered answer). Drafted by scripts/draft_bank.py;\n"
            "# a draft row is shown as fact only after its checks, a meaning only where JYOTISH_SHOW_DRAFT_MEANINGS is on.\n"
            + dump_rows(rs))
    load_bank()                                                 # the written bank must stand


def log_run(report: dict, rows_in_bank: int) -> None:
    path = ROOT / "docs" / "bank_draft_2026-11-15.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    runs = old.get("runs", [old] if old.get("date") else []) + [report]
    path.write_text(json.dumps({"runs": runs, "rows_in_bank": rows_in_bank,
                                "usd_total": round(sum(r["usd"].get("writer", 0) + r["usd"].get("checker", 0)
                                                       for r in runs), 4)}, indent=1) + "\n")


def recheck(a) -> int:
    """Every fact row (or `--signatures`) checked again on each sample shape; nothing is drafted. A variant refused on
    any shape is never shown (bank.BankRow.usable); its evidence is printed for a redraft."""
    from jyotish.narrate import CONFIG, ModelChecker, make_backend
    from jyotish.bank import load_bank
    bank = load_bank()
    found = _signatures(a.charts, a.seed)
    rows = {(r.signature, r.kind): r for r in bank.rows if r.kind == "fact"
            and (a.signatures is None or r.signature in a.signatures)}
    n = sum(3 * len(samples_for(r, found[k])) for k, r in rows.items() if k in found)
    from jyotish.costs import price
    pc = price("zai-org/GLM-5.3-Flash", "api.deepinfra.com")
    usd = n * (CHECK_TOKENS[0] * pc[0] + CHECK_TOKENS[1] * pc[1]) / 1e6
    print(f"{len(rows)} fact rows, {n} checks (up to {SHAPES} shapes a row); expected USD {usd:.3f} (budget {a.budget})")
    if usd > a.budget:
        print(f"over the budget of USD {a.budget}: nothing checked")
        return 2
    checker = ModelChecker(make_backend(os.environ.get("JYOTISH_CHECKER_BACKEND"), "checker", CONFIG), CONFIG)
    checker_model = checker.backend.describe().get("model")
    spent = {"checker": 0.0}
    _, bad = check_rows(rows, found, checker, checker_model, spent)
    no_sample = sorted(k[0] for k, r in rows.items() if k not in found or not samples_for(r, found[k]))
    write_bank(bank.rows)
    report = {"date": TODAY.isoformat(), "kind": "recheck", "checker": checker_model, "rows_checked": len(rows),
              "checks": n, "refused": bad, "no_sample": no_sample, "usd": {k: round(v, 4) for k, v in spent.items()}}
    log_run(report, len(bank.rows))
    for sig, why in sorted(bad.items()):
        print(f"  refused: {sig}: {len(why)} variant(s)")
    print(f"checked {n}; {sum(len(v) for v in bad.values())} refused over {len(bad)} rows; no sample for "
          f"{len(no_sample)}; spent USD {spent['checker']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
