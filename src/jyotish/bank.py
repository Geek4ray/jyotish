"""The sentence bank (SPEC Layer 8 rev 134, "The layered answer"): `data/bank/*.yaml`, data like the rule library,
validated against `data/bank/bank.schema.json` and the checks below at load time.

A row is one plain sentence for one finding signature (`jyotish.plan`: a family's lean for an area, a rule full or
reduced, a lord's or significator's hidden weakness, the period now, a stretch, an opening per question kind) in three
variants with slots (`{planet}`, `{sign}`, `{house}`, `{area}`, ...), filled with the chart's values by the composer.
Its kind:
- `fact` says only what the chart object states for the signature. Checked once against the signature's data by
  the gate checker (`checks`, scripts/draft_bank.py), never again per client.
- `meaning` is what the placement or rule is traditionally read to mean for one area (signature
  `<item signature>@<area>`), drawn from the rule's cited effect. Its `source` is that citation. Until approved it is
  shown only where JYOTISH_SHOW_DRAFT_MEANINGS is on; no public client sees an unapproved meaning.

Every row records the model and date that drafted it and its status: `draft`, then `approved` with the approver's
name and date (or the astrologer's own rewrite, `rewritten_by`). Every variant, its slots filled with sample values,
passes the never-show list, the client's-word rules for a conversation and the tier words: a row that does not is a
load error, as a rule's typo is. The bank's version is a hash of its files (`version`), so a stored answer
(step 7) is served only for the bank that wrote it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import jsonschema
import yaml
from pydantic import BaseModel, Field

BANK_DIR = Path(os.environ.get("JYOTISH_BANK_PATH", Path(__file__).resolve().parents[2] / "data" / "bank"))
SCHEMA_FILE = "bank.schema.json"
SLOT = re.compile(r"\{([A-Za-z_]+)\}")
# Sample values a variant's slots are filled with before its words are checked: the words the slots will carry are
# the plan's, already in the client's words; the check is of the row's own words around them.
SAMPLE = {"planet": "Venus", "planets": "Venus and Mars", "helpers": "Jupiter", "sign": "Taurus", "signs": "Taurus and Leo",
          "house": "2nd", "houses": "2nd and 10th", "ruled_house": "10th", "area": "your career", "Area": "Your career",
          "areas": "your career and money", "lean": "favourably", "standing": "better supported than most",
          "dignity": "in a friendly sign", "sits": "sits", "name": "Ruchaka",
          "named": "Ruchaka (Mars in its own or exalted sign in an angular house)", "reductions": "Saturn's aspect on it",
          "role": "the ruler of your 10th house", "maha": "Jupiter", "antar": "Mercury", "until": "November 2028",
          "touching": "Jupiter", "when": "from October 2029 to June 2032",
          "weaknesses": "sits in your 1st house, which drains it, and it is in a feeble state by its degree in Taurus",
          "in_sign": "Taurus", "varga": "the divisional chart of comforts and vehicles",
          "ruled": "Mars, which rules the lunar day and your birth star, and the Moon, which rules the weekday",
          "ruler": "Mars, which rules the lunar day and your birth star"}


class BankError(ValueError):
    pass


class Check(BaseModel):
    """One gate-checker verdict on a fact variant, filled with a chart's values for its signature."""
    variant: int
    sentence: str
    supported: bool
    evidence: str = ""
    model: str
    on: date
    shape: str | None = None         # the slot shape the values had (`shape_of`): one value, several, empty, a node


class BankRow(BaseModel):
    signature: str
    kind: Literal["fact", "meaning"]
    slots: list[str]
    variants: list[str] = Field(min_length=3, max_length=3)
    source: str | None = None
    drafted_by: str
    drafted_on: date
    status: Literal["draft", "approved"] = "draft"   # approved: all three variants approved
    approved_variants: list[int] = Field(default_factory=list)   # the variants the astrologer approved (H3)
    approved_by: str | None = None
    approved_on: date | None = None
    rewritten_by: str | None = None
    withdrawn_by: str | None = None              # judged wrong by the astrologer: never shown again
    withdrawn_on: date | None = None
    withdrawn_why: str | None = None
    checks: list[Check] = Field(default_factory=list)
    file: str | None = Field(default=None, exclude=True)

    @property
    def base(self) -> str:
        """The plan signature a row serves (a meaning row's `<signature>@<area>` without its area)."""
        return self.signature.split("@", 1)[0]

    @property
    def area(self) -> str | None:
        return self.signature.split("@", 1)[1] if "@" in self.signature else None

    def approved(self, i: int) -> bool:
        """Variant i approved: the astrologer approved it as he read it (review 2026-11-15, H3: one "right" approved
        all three variants of a row, two of them never shown to him). A row approved before approval was per
        variant (status approved, no list) counts as all three."""
        return i in self.approved_variants or (self.status == "approved" and not self.approved_variants)

    def approved_pick(self, i: int) -> int | None:
        """The variant a public client reads of a meaning row for the session's pick i: i if approved, else the next
        approved variant, else none."""
        return next((j for j in ((i + k) % 3 for k in range(3)) if self.approved(j)), None)

    def refused(self) -> set[int]:
        """The variants the composer never shows as fact: refused by a check on any shape, or never checked (a fact
        row says only what its signature states, checked once: a row no sample reached is the engine's sentence)."""
        checked = {c.variant for c in self.checks}
        return {c.variant for c in self.checks if not c.supported} | {i for i in range(3) if i not in checked}

    def usable(self, i: int) -> int | None:
        """The variant shown for a session's pick `i`: `i` itself, else the next variant checked and never refused,
        else none (review 2026-11-15, H1: a variant true for one sample's values may be false for another's)."""
        bad = self.refused()
        return next((j for j in ((i + k) % 3 for k in range(3)) if j not in bad), None)

    def fill(self, i: int, slots: dict[str, str]) -> str:
        return tidy(SLOT.sub(lambda m: slots.get(m.group(1), m.group(0)), agree(self.variants[i], slots)))


# A verb right after a slot agrees with the slot's value (2026-11-15: "The Sun and Mercury sits", "Jupiter have a hand"):
# a list ("the Sun and Mercury", "Saturn's aspect, an unhelpful star and a house") takes the plural, one value the
# singular. Only these verbs are changed, so a noun after a slot is never touched.
VERBS = {"sits": "sit", "has": "have", "is": "are", "was": "were", "holds": "hold", "reduces": "reduce",
         "weakens": "weaken", "lessens": "lessen", "leans": "lean", "bears": "bear", "forms": "form", "gives": "give",
         "lies": "lie", "falls": "fall", "stands": "stand", "rules": "rule", "brings": "bring", "makes": "make",
         "supports": "support", "works": "work", "dims": "dim", "tempers": "temper", "softens": "soften",
         "limits": "limit", "cuts": "cut", "takes": "take", "keeps": "keep", "draws": "draw", "shows": "show"}
PLURAL_OF = {s: p for s, p in VERBS.items()}
SINGULAR_OF = {p: s for s, p in VERBS.items()}
_AFTER_SLOT = re.compile(r"\{([A-Za-z_]+)\}(\s+)([a-z]+)\b")


def plural(value: str) -> bool:
    return bool(re.search(r"\band\b|,", value or ""))


# Slots whose value is one thing whatever its words: a role ("the ruler of your 2nd house and the main planet for
# money") is one planet (review 2026-11-15, M6: "...are the Sun"), an area or a name is one subject.
ONE_THING = ("dignity", "area", "Area", "areas", "named", "name", "when", "until", "role", "varga", "ruler")
# A verb coordinated with the slot's own verb in the same clause ("{planets} sit in your 10th house and forms", M6).
_SECOND_VERB = re.compile(r"^([^,;:.]*?\band\s+)([a-z]+)\b")


def agree(template: str, slots: dict[str, str]) -> str:
    def number(verb: str, many: bool) -> str:
        if many and verb in PLURAL_OF:
            return PLURAL_OF[verb]
        if not many and verb in SINGULAR_OF:
            return SINGULAR_OF[verb]
        return verb

    out, at = [], 0
    for m in _AFTER_SLOT.finditer(template):
        name, space, verb = m.group(1), m.group(2), m.group(3)
        out.append(template[at:m.start()])
        at = m.end()
        if name not in slots or name in ONE_THING or (verb not in PLURAL_OF and verb not in SINGULAR_OF):
            out.append(m.group(0))
            continue
        many = plural(slots[name])
        out.append("{" + name + "}" + space + number(verb, many))
        rest = _SECOND_VERB.match(template[at:])
        if rest and (rest.group(2) in PLURAL_OF or rest.group(2) in SINGULAR_OF):
            out.append(rest.group(1) + number(rest.group(2), many))
            at += rest.end()
    out.append(template[at:])
    return "".join(out)


NODES = re.compile(r"\b(?:Rahu|Ketu)\b")
LUMINARIES = re.compile(r"\bthe (?:Sun|Moon)\b")


def shape_of(slots: dict[str, str]) -> str:
    """The shape of a plan item's slot values, what a fact variant's truth can turn on (review 2026-11-15, H1): per
    slot, empty, one value or several, and whether it names a node or the Sun or Moon. A variant is checked once per
    shape the random charts give its signature, not on one chart."""
    out = []
    for k in sorted(slots):
        v = slots[k] or ""
        n = "empty" if not v.strip() else "many" if plural(v) else "one"
        out.append(f"{k}:{n}" + ("+node" if NODES.search(v) else "") + ("+lum" if LUMINARIES.search(v) else ""))
    return ",".join(out)


def tidy(text: str) -> str:
    """A filled variant's punctuation where an empty slot left it loose (", ." from an empty dignity)."""
    text = re.sub(r",(?:\s*,)+", ",", text)       # ", ," and ",," after an empty dignity (review M6)
    text = re.sub(r"\s+,", ",", re.sub(r",\s*([.;:])", r"\1", text))
    return re.sub(r"\s{2,}", " ", text).strip()


def row_errors(row: BankRow) -> list[str]:
    """Why a row cannot stand: its slots, its source and approval, and its words."""
    from .client import client_warnings, never_show
    from .narrate import TIER_WORDS
    out = []
    used = {s for v in row.variants for s in SLOT.findall(v)}
    if used - set(row.slots):
        out.append(f"{row.signature}: a variant uses a slot the row does not declare: {sorted(used - set(row.slots))}")
    if set(row.slots) - used:
        # A declared slot is one the composer requires a value for (review 2026-11-15, M5: every .nohouse row declared
        # `houses`, empty by construction, and none was ever shown).
        out.append(f"{row.signature}: the row declares a slot no variant uses: {sorted(set(row.slots) - used)}")
    for i, v in enumerate(row.variants):
        if re.search(r"\{[^}]*$|^[^{]*\}|\{\}", v):
            out.append(f"{row.signature}: variant {i + 1} has a broken slot: {v!r}")
    if row.kind == "meaning":
        if "@" not in row.signature:
            out.append(f"{row.signature}: a meaning row names its area (<signature>@<area>)")
        if not row.source:
            out.append(f"{row.signature}: a meaning row carries its source (the rule's citation)")
    elif "@" in row.signature:
        out.append(f"{row.signature}: a fact row is the same for every area; only a meaning row names one")
    if row.kind == "meaning" and row.base.startswith("rule.") and ".nohouse" not in row.base:
        # A row with a house is a fire from the rising sign: for a rule counted from the rising sign as well as the
        # Moon, "from the Moon" is wrong there (review 2026-11-15, M9: Gaja Kesari's BPHS form). A .nohouse row is a
        # fire from the Moon or the Sun only, where it can be right.
        bases = rule_bases(".".join(row.base.split(".")[1:3]))
        if "lagna" in bases and len(bases) > 1:
            for i, v in enumerate(row.variants):
                if re.search(r"\bfrom (?:the|your) Moon\b", v):
                    out.append(f"{row.signature}: variant {i + 1} counts from the Moon a rule that fired from the "
                               f"rising sign here: {v!r}")
    for i, v in enumerate(row.variants):
        # Only the weekday's lord rules the day (2026-11-16: the nakshatra's lord was among "the rulers of the day").
        if re.search(r"\brulers? of (?:the|your) (?:birth )?day\b", v):
            out.append(f"{row.signature}: variant {i + 1} calls a planet a ruler of the day; say what it rules: {v!r}")
    if (row.status == "approved" or row.approved_variants) and not (row.approved_by and row.approved_on):
        out.append(f"{row.signature}: an approved row names who approved it and when")
    if any(i not in (0, 1, 2) for i in row.approved_variants) or len(set(row.approved_variants)) != len(row.approved_variants):
        out.append(f"{row.signature}: approved_variants are distinct variant numbers 0-2")
    if row.approved_variants and (row.status == "approved") != (sorted(row.approved_variants) == [0, 1, 2]):
        out.append(f"{row.signature}: a row is approved when, and only when, all three variants are")
    for i, v in enumerate(row.variants):
        filled = tidy(SLOT.sub(lambda m: SAMPLE.get(m.group(1), "Venus"), v))
        for e in never_show(filled) + client_warnings(filled, conversation=True):
            out.append(f"{row.signature}: variant {i + 1}: {e}")
        if (m := TIER_WORDS.search(filled)):
            out.append(f"{row.signature}: variant {i + 1}: a tier word ({m.group(0)!r}): {filled!r}")
    return out


def fills(row: BankRow | None, slots: dict[str, str]) -> bool:
    """A fact row the composer can fill from an item's slots: every slot it declares has a value (a dignity may be
    empty), and a variant no check refused is left. The composer's rule, and the coverage tool's (review M5)."""
    return (row is not None and set(row.slots) <= set(slots) and len(row.refused()) < 3
            and all(slots[s] for s in row.slots if s != "dignity"))


@lru_cache(maxsize=64)
def rule_bases(rule_id: str) -> tuple[str, ...]:
    """The points a rule is counted from (its file's when.basis: lagna, moon, sun), read from rules/<id>.yaml."""
    path = Path(__file__).resolve().parents[2] / "rules" / f"{rule_id}.yaml"
    if not path.exists():
        return ()
    when = (yaml.safe_load(path.read_text()) or {}).get("when") or {}
    return tuple(when.get("basis") or ())


class Bank:
    """The rows by (signature, kind), with the bank's version."""

    def __init__(self, rows: list[BankRow], version: str):
        self.rows = rows
        self.version = version
        self._by = {(r.signature, r.kind): r for r in rows}

    def fact(self, signature: str) -> BankRow | None:
        """The fact row a composer may use (none once the astrologer withdrew it)."""
        r = self._by.get((signature, "fact"))
        return None if r is None or r.withdrawn_by else r

    def meaning(self, signature: str, area: str | None) -> BankRow | None:
        r = self._by.get((f"{signature}@{area}", "meaning")) if area else None
        return None if r is None or r.withdrawn_by else r

    def row(self, signature: str, kind: str) -> BankRow | None:
        """Any row, withdrawn or not (the worksheet and apply-reviews)."""
        return self._by.get((signature, kind))

    def __len__(self) -> int:
        return len(self.rows)


def _version(directory: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(directory.glob("*.yaml")):
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    return h.hexdigest()[:12]


def load_bank(directory: Path | str | None = None, strict: bool = True) -> Bank:
    """Every data/bank/*.yaml, validated against the schema and `row_errors`. A bad row is a BankError (strict), or
    left out (strict=False, for a tool that reports them)."""
    directory = Path(directory) if directory is not None else BANK_DIR
    if not directory.exists():
        return Bank([], "empty")
    validator = jsonschema.Draft202012Validator(json.loads((directory / SCHEMA_FILE).read_text()))
    rows, errors, seen = [], [], set()
    for path in sorted(directory.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text()) or []
        doc = json.loads(json.dumps(doc, default=str))   # YAML reads a bare date as a date; the schema reads text
        for e in validator.iter_errors(doc):
            errors.append(f"{path.name}: {'/'.join(map(str, e.path))}: {e.message}")
        if not isinstance(doc, list):
            continue
        for d in doc:
            try:
                row = BankRow(**d, file=path.name)
            except Exception as e:                       # the schema has said why; pydantic's message adds the field
                errors.append(f"{path.name}: {d.get('signature') if isinstance(d, dict) else d!r}: {e}")
                continue
            key = (row.signature, row.kind)
            errs = row_errors(row) + ([f"{row.signature}: a second {row.kind} row"] if key in seen else [])
            seen.add(key)
            errors += [f"{path.name}: {e}" for e in errs]
            if not errs:
                rows.append(row)
    if errors and strict:
        raise BankError("; ".join(errors[:20]) + (f" (and {len(errors) - 20} more)" if len(errors) > 20 else ""))
    return Bank(rows, _version(directory))


@lru_cache(maxsize=4)
def _cached(directory: str, version: str) -> Bank:
    return load_bank(Path(directory))


def default_bank() -> Bank:
    """The bank in use, reloaded when its files change."""
    return _cached(str(BANK_DIR), _version(BANK_DIR) if BANK_DIR.exists() else "empty")


def dump_rows(rows: list[BankRow]) -> str:
    """Rows as their YAML file holds them (the keys in the schema's order, no empty optional field)."""
    out = []
    for r in rows:
        d = r.model_dump(mode="json", exclude_none=True)
        for k in ("checks", "approved_variants"):
            if not d.get(k):
                d.pop(k, None)
        out.append(d)
    return yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)


# --- coverage ----------------------------------------------------------------------------------------------------

KINDS = ["amount", "yes_no", "when", "why"]


def _plan_for(birth: dict, as_of: date) -> list[tuple[str, str | None, dict, str]]:
    """(signature, area, slots, part) of every item of one random chart's plan over all its areas, every question
    kind and a "when" turn."""
    from datetime import datetime
    from .chart import compute
    from .plan import plan
    c = compute(datetime.fromisoformat(f"{birth['date']}T{birth['time']}"), birth["lat"], birth["lon"], true_node=False)
    areas = [a for a in c.scored.areas if a != "synastry"]
    # Every ask: how each area goes, which field (SPEC rev 136, decision 3: the vocation items), when, why.
    parts = [{"kind": "goes", "areas": areas}, {"kind": "vocation", "areas": ["career"]},
             {"kind": "when", "areas": areas}, {"kind": "why", "areas": areas}]
    p = plan(c, "coverage", areas, "both", KINDS, as_of=as_of, when=True, parts=parts)
    return [(i.signature, i.area, dict(i.slots), i.part, i.meaning) for i in p.items]


def coverage(n: int = 1000, seed: int = 0, bank: Bank | None = None, as_of: date = date(2026, 11, 15),
             workers: int | None = None) -> dict[str, Any]:
    """The share of plan items on `n` random charts (scripts/synthetic_cohort.births: synthetic, no one's data) that
    find a fact row the composer can fill from the item's slot values (`fills`), overall and by part, the meaning rows' share among items that can take
    one (rules and weaknesses), and the signatures most often missing."""
    import sys
    from concurrent.futures import ProcessPoolExecutor
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from synthetic_cohort import births
    bank = bank if bank is not None else default_bank()
    bs = births(n, seed)
    if workers == 1:
        plans = [_plan_for(b, as_of) for b in bs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            plans = list(ex.map(_plan_for, bs, [as_of] * len(bs), chunksize=8))
    total, found, missing = Counter(), Counter(), Counter()
    can_mean, meant = 0, 0
    for items in plans:
        for sig, area, slots, part, meaning in items:
            total[part] += 1
            # What the composer would show, slot values included; a stretch's dates come from the payload, which this
            # tool does not make (its plans carry "when" empty), so they are taken as given (the scorecard of 2026-11-16
            # read 33% for stretches once fills required the value).
            if fills(bank.fact(sig), slots | ({"when": "(the payload's dates)"} if part == "stretch" and
                                              "when" in slots and not slots["when"] else {})):
                found[part] += 1
            else:
                missing[sig] += 1
            if part in ("rule", "weakness", "vocation"):
                can_mean += 1
                meant += bank.meaning(meaning or sig, area) is not None
    n_items = sum(total.values())
    return {"charts": n, "seed": seed, "items": n_items, "found": sum(found.values()),
            "share": round(sum(found.values()) / n_items, 4) if n_items else None,
            "by_part": {p: round(found[p] / total[p], 4) for p in sorted(total)},
            "meaning_share": round(meant / can_mean, 4) if can_mean else None,
            "approved_share": round(sum(r.status == "approved" for r in bank.rows) / len(bank), 4) if len(bank) else 0.0,
            "approved_variant_share": round(sum(r.approved(i) for r in bank.rows for i in range(3)) / (3 * len(bank)), 4)
            if len(bank) else 0.0,
            "rows": len(bank), "version": bank.version, "missing": missing.most_common(25)}


# --- the astrologer's verdicts, written back (`jyotish bank apply-reviews`) --------------------------------------

def template(sentence: str, slots: dict[str, str]) -> str:
    """A sentence in the astrologer's own words with the chart's values put back as slots ({planet}, {house}, ...),
    the longest value first, so his rewrite serves every later chart."""
    out = sentence.strip()
    for name, value in sorted(((k, v) for k, v in slots.items() if isinstance(v, str) and v and not k.startswith("_")),
                              key=lambda kv: -len(kv[1])):
        # The value as the plan gives it and capitalised at a sentence's start ("the Sun" read as "The Sun": review
        # 2026-11-15, H4, where the capital kept "The Sun" literal in a rewrite served to every chart).
        forms = sorted({value, value[:1].upper() + value[1:]}, key=len, reverse=True)
        pattern = "|".join(re.escape(f) for f in forms)
        out = re.sub(rf"(?<![{{\w])(?:{pattern})(?![\w}}])", "{" + name + "}", out)
    return out


def rewrite_errors(old: str, new: str) -> list[str]:
    """Why an astrologer's rewrite cannot replace a variant: its slots are not the variant's (a value left literal,
    or one the variant did not carry), so it would tell one chart's values to every chart (review H4)."""
    a, b = set(SLOT.findall(old)), set(SLOT.findall(new))
    out = []
    if a - b:
        out.append(f"the rewrite does not carry the chart's values for {sorted(a - b)} as the sentence did: a value "
                   f"left in the words would be told to every chart")
    if b - a:
        out.append(f"the rewrite carries {sorted(b - a)}, which the sentence did not")
    return out


def approve(row: BankRow, i: int, by: str, today: date) -> None:
    """Variant i approved by `by` (only the variant he read, review H3); the row is approved once all three are."""
    row.approved_variants = sorted(set(row.approved_variants) | {i})
    row.approved_by, row.approved_on = by, today
    row.status = "approved" if row.approved_variants == [0, 1, 2] else "draft"


def apply_reviews(database_url: str | None = None, directory: Path | str | None = None,
                  today: date | None = None, checker=None) -> dict[str, Any]:
    """Every verdict not yet written back, oldest first, so the latest decides: right approves the variant he read
    (approved_by, approved_on); change puts the astrologer's words, with the chart's values as slots, in place of the
    variant he read, approved and `rewritten_by` him; wrong withdraws the row (never shown again) until a later right
    or change brings it back. A row that would no longer
    stand (`row_errors`) is left as it was and reported; a verdict on a sentence with no row (the engine's own) is
    reported for drafting. Each file is rewritten once, and every verdict written back is marked applied."""
    from datetime import datetime, timezone
    from sqlalchemy.orm import sessionmaker
    from .db import BankReviewRow, migrate
    directory = Path(directory) if directory is not None else BANK_DIR
    today = today or date.today()
    bank = load_bank(directory)
    by_file: dict[str, list[BankRow]] = {}
    for r in bank.rows:
        by_file.setdefault(r.file, []).append(r)
    report = {"approved": [], "rewritten": [], "withdrawn": [], "refused": [], "no_row": []}
    Session = sessionmaker(migrate(database_url))
    changed: set[str] = set()
    with Session.begin() as s:
        # Oldest first, each applied in turn (review 2026-11-15, M8: newest first with one per variant let an older
        # "wrong" on variant 0 withdraw a row after a newer "right" on variant 1): the latest verdict on a row decides
        # whether it is withdrawn, and the latest on a variant its words and approval.
        pending = s.query(BankReviewRow).filter(BankReviewRow.applied_at.is_(None)).order_by(BankReviewRow.id).all()
        for v in pending:
            row = bank.row(v.signature, v.kind) if v.kind else None
            if row is None:
                report["no_row"].append({"signature": v.signature, "verdict": v.verdict, "words": v.words})
                continue
            new = row.model_copy(deep=True)
            i = v.variant or 0
            if v.verdict in ("right", "change") and new.withdrawn_by:
                # Judged right or rewritten after it was withdrawn: shown again (M8).
                new.withdrawn_by = new.withdrawn_on = new.withdrawn_why = None
            if v.verdict == "right":
                approve(new, i, v.reviewer_id, today)
                what = "approved"
            elif v.verdict == "change":
                slots = v.slots or {}
                words = template(v.words or v.sentence, slots)
                why = rewrite_errors(row.variants[i], words)
                check = None
                if not why and new.kind == "fact":
                    # A fact variant is checked once against the item's facts, as the drafted variants were (H4).
                    if checker is None:
                        why = ["a rewritten fact sentence is checked against its facts, and no checker was given"]
                    elif not slots.get("_facts"):
                        why = ["the facts this sentence rests on were erased with the conversation: rewrite it on "
                               "another turn"]
                    else:
                        filled = BankRow.fill(new.model_copy(update={"variants": [words] * 3}), 0,
                                              {k: x for k, x in slots.items() if not k.startswith("_")})
                        data = json.dumps({"facts": slots["_facts"], "the engine's own sentence": slots.get("_engine")},
                                          default=str, indent=1)
                        res, meta = checker.ask_one(filled, data)
                        ok = all(p.supported for p in res.propositions)
                        model = ((meta or {}).get("backend") or {}).get("model") or "checker"
                        check = Check(variant=i, sentence=filled, supported=ok, model=model, on=today,
                                      evidence="; ".join(p.evidence for p in res.propositions if not p.supported)[:400],
                                      shape=shape_of({k: x for k, x in slots.items() if not k.startswith("_")}))
                        if not ok:
                            why = [f"the checker found the rewrite not stated by the facts: {check.evidence}"]
                if why:
                    report["refused"].append({"signature": v.signature, "verdict": v.verdict, "why": why})
                    continue
                variants = list(new.variants)
                variants[i] = words
                new.variants = variants
                new.rewritten_by = v.reviewer_id
                new.checks = [c for c in new.checks if c.variant != i] + ([check] if check else [])
                approve(new, i, v.reviewer_id, today)
                what = "rewritten"
            else:
                new.withdrawn_by, new.withdrawn_on, new.withdrawn_why = v.reviewer_id, today, v.words
                new.approved_variants, new.status = [], "draft"
                what = "withdrawn"
            errs = row_errors(new)
            if errs:
                report["refused"].append({"signature": v.signature, "verdict": v.verdict, "why": errs})
                continue
            rows = by_file[row.file]
            rows[rows.index(row)] = new
            bank._by[(new.signature, new.kind)] = new
            changed.add(row.file)
            report[what].append({"signature": v.signature, "variant": v.variant, "by": v.reviewer_id})
            v.applied_at = datetime.now(timezone.utc)
        # Written to a copy of the bank first and loaded there; only a bank that stands is moved into place, and the
        # verdicts are marked applied only then (review 2026-11-15, L3: the files were rewritten before the check, so
        # a failing check left them rewritten with the verdicts unapplied, and the next run applied them twice).
        import shutil
        import tempfile
        if changed:
            with tempfile.TemporaryDirectory(dir=directory.parent) as tmp:
                staged = Path(tmp) / directory.name
                shutil.copytree(directory, staged)
                for name in sorted(changed):
                    head = "".join(line for line in (directory / name).read_text().splitlines(keepends=True)
                                   if line.startswith("#"))
                    (staged / name).write_text(head + dump_rows(by_file[name]))
                load_bank(staged)                        # the written bank must stand, or nothing is written or marked
                for name in sorted(changed):
                    os.replace(staged / name, directory / name)
    return report
