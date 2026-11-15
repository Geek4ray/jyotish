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
          "touching": "Jupiter", "when": "from October 2029 to June 2032"}


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


class BankRow(BaseModel):
    signature: str
    kind: Literal["fact", "meaning"]
    slots: list[str]
    variants: list[str] = Field(min_length=3, max_length=3)
    source: str | None = None
    drafted_by: str
    drafted_on: date
    status: Literal["draft", "approved"] = "draft"
    approved_by: str | None = None
    approved_on: date | None = None
    rewritten_by: str | None = None
    checks: list[Check] = Field(default_factory=list)
    file: str | None = Field(default=None, exclude=True)

    @property
    def base(self) -> str:
        """The plan signature a row serves (a meaning row's `<signature>@<area>` without its area)."""
        return self.signature.split("@", 1)[0]

    @property
    def area(self) -> str | None:
        return self.signature.split("@", 1)[1] if "@" in self.signature else None

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


def agree(template: str, slots: dict[str, str]) -> str:
    def fix(m):
        name, space, verb = m.group(1), m.group(2), m.group(3)
        if name not in slots or name in ("dignity", "area", "Area", "areas", "named", "name", "when", "until"):
            return m.group(0)
        many = plural(slots[name])
        if many and verb in PLURAL_OF:
            verb = PLURAL_OF[verb]
        elif not many and verb in SINGULAR_OF:
            verb = SINGULAR_OF[verb]
        return "{" + name + "}" + space + verb
    return _AFTER_SLOT.sub(fix, template)


def tidy(text: str) -> str:
    """A filled variant's punctuation where an empty slot left it loose (", ." from an empty dignity)."""
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
    if row.status == "approved" and not (row.approved_by and row.approved_on):
        out.append(f"{row.signature}: an approved row names who approved it and when")
    for i, v in enumerate(row.variants):
        filled = tidy(SLOT.sub(lambda m: SAMPLE.get(m.group(1), "Venus"), v))
        for e in never_show(filled) + client_warnings(filled, conversation=True):
            out.append(f"{row.signature}: variant {i + 1}: {e}")
        if (m := TIER_WORDS.search(filled)):
            out.append(f"{row.signature}: variant {i + 1}: a tier word ({m.group(0)!r}): {filled!r}")
    return out


class Bank:
    """The rows by (signature, kind), with the bank's version."""

    def __init__(self, rows: list[BankRow], version: str):
        self.rows = rows
        self.version = version
        self._by = {(r.signature, r.kind): r for r in rows}

    def fact(self, signature: str) -> BankRow | None:
        return self._by.get((signature, "fact"))

    def meaning(self, signature: str, area: str | None) -> BankRow | None:
        return self._by.get((f"{signature}@{area}", "meaning")) if area else None

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
        if not d.get("checks"):
            d.pop("checks", None)
        out.append(d)
    return yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120)


# --- coverage ----------------------------------------------------------------------------------------------------

KINDS = ["amount", "yes_no", "when", "why"]


def _plan_for(birth: dict, as_of: date) -> list[tuple[str, str | None, list[str], str]]:
    """(signature, area, slot names, part) of every item of one random chart's plan over all its areas, every question
    kind and a "when" turn."""
    from datetime import datetime
    from .chart import compute
    from .plan import plan
    c = compute(datetime.fromisoformat(f"{birth['date']}T{birth['time']}"), birth["lat"], birth["lon"], true_node=False)
    areas = [a for a in c.scored.areas if a != "synastry"]
    p = plan(c, "coverage", areas, "both", KINDS, as_of=as_of, when=True)
    return [(i.signature, i.area, sorted(i.slots), i.part) for i in p.items]


def coverage(n: int = 1000, seed: int = 0, bank: Bank | None = None, as_of: date = date(2026, 11, 15),
             workers: int | None = None) -> dict[str, Any]:
    """The share of plan items on `n` random charts (scripts/synthetic_cohort.births: synthetic, no one's data) that
    find a fact row whose slots the item fills, overall and by part, the meaning rows' share among items that can take
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
        for sig, area, slots, part in items:
            total[part] += 1
            row = bank.fact(sig)
            if row is not None and set(row.slots) <= set(slots):
                found[part] += 1
            else:
                missing[sig] += 1
            if part in ("rule", "weakness"):
                can_mean += 1
                meant += bank.meaning(sig, area) is not None
    n_items = sum(total.values())
    return {"charts": n, "seed": seed, "items": n_items, "found": sum(found.values()),
            "share": round(sum(found.values()) / n_items, 4) if n_items else None,
            "by_part": {p: round(found[p] / total[p], 4) for p in sorted(total)},
            "meaning_share": round(meant / can_mean, 4) if can_mean else None,
            "approved_share": round(sum(r.status == "approved" for r in bank.rows) / len(bank), 4) if len(bank) else 0.0,
            "rows": len(bank), "version": bank.version, "missing": missing.most_common(25)}
