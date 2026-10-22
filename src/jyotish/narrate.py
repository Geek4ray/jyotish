"""Layer 7: narration. `narrate(chart, question)` returns a Reading in the SPEC Layer 7
output schema.

The engine decides every fact; the language model only writes sentences about findings
the engine hands it. What the engine owns, in code:
  - which findings are narrated: non-experimental fired rules that map to the area, with
    time-stability >= 0.5; those below 0.5, and areas below 0.5, go to
    `depends_on_birth_time` instead; fires of one rule on the same planets from several
    bases are one finding;
  - tier, confidence and stability words, copied verbatim from the scored chart (the model
    writes no confidence words at all);
  - ordering of claims by stability x confidence;
  - school conflicts (a Jaimini or KP family voting against the Parashari families),
    timing windows (via the TimingQuery engine for "when" questions), polarity (top three
    areas only), disclaimers.
What the validator enforces on every sentence the model writes (rejected sentences make
the model regenerate, up to `CONFIG.max_attempts`):
  - a sentence with a claim verb ends with at least one [rule:...] or [text:...] tag, and
    every tag is one the engine offered for that finding;
  - no probability language (the areas are not calibrated: probability is null);
  - no confidence words (certain, definitely, guaranteed, ...);
  - no death timing, medical diagnosis or trade advice;
  - no claim about a third party's own life (mother, father, partner, children, siblings).
After the validator, the semantic checker (`AnthropicChecker`, at `CONFIG.checker_effort`)
reads every claim against its finding's derivation and every tagged summary sentence against
the union of the derivations it cites; one unsupported proposition sends the draft back.

The model call (`AnthropicDrafter`) uses the Anthropic SDK's structured output
(`beta.messages.parse` with a pydantic schema), server-side refusal fallback, and the
settings in CONFIG. Tests inject a drafter that replays a fixture, so the suite is offline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from .models import Chart, Stability, TimingQuery
from .rules import PLACEMENT_FAMILIES, default_rules, in_default
from .scoring import AREAS, THEME_AREAS


# --- the one config ------------------------------------------------------------------

@dataclass(frozen=True)
class NarrationConfig:
    model: str = "claude-opus-5-5"
    max_tokens: int = 16000
    effort: str = "medium"                    # the writer; Opus 5.5's default, set explicitly
    checker_effort: str = "high"              # the checker is the gate (SPEC Layer 7 item 10)
    fallbacks: str = "default"                # server-side refusal fallback, routed by category
    betas: tuple[str, ...] = ("server-side-fallback-2026-07-01",)
    max_attempts: int = 3                     # draft + regenerations on validator failure
    checker_concurrency: int = 16             # checker calls of one attempt in flight at once; 1 = one after another
    timing_years: int = 10                    # window for a "when" question with no dates


CONFIG = NarrationConfig()


# --- what the model returns ------------------------------------------------------------

class DraftClaim(BaseModel):
    finding_id: str = Field(description="The id of the finding this sentence narrates, from the input.")
    text: str = Field(description="One or two sentences; every claim sentence ends with its tags, "
                                  "e.g. 'Mars in its own sign in the 7th forms Ruchaka yoga [rule:yoga.ruchaka].'")


class DraftArea(BaseModel):
    name: str
    claims: list[DraftClaim]
    paragraph: str | None = Field(default=None, description=(
        "Curious depth only: one short plain-language paragraph about the area, every sentence ending "
        "with the tags of the findings it draws on. Null at the other depths."))


class ReadingDraft(BaseModel):
    summary: str = Field(description="Two or three tagged sentences answering the question.")
    areas: list[DraftArea]


# --- the reading (SPEC Layer 7 output schema) ------------------------------------------

class ReadingClaim(BaseModel):
    finding_id: str
    text: str
    cites: list[str]
    kind: str                           # rule | vote | chain
    school: str
    basis: str
    stability: float | None
    stability_label: str | None = None  # the sampler's word for `stability` (uncertainty.label)
    confidence: float | None            # rule: scale x confidence_base; vote: min(1, 1 - rho) x |vote|; chain: none
    learner: dict[str, Any] | None = None   # the finding's derivation, by the engine (learner_data)
    edited: dict[str, Any] | None = None    # review step: {by, at} when a reviewer's edit replaced the text (checked)


class ReadingWindow(BaseModel):
    kind: str = "dasha+transit"
    start: str
    end: str
    score: float
    q: float
    q_terms: dict[str, float]
    t: float
    relevant_systems: list[str]
    strongest_piece: dict[str, Any] | None
    confidence: str | None
    stability: float | None             # edge movement over the time samples, in days
    sandhi: bool
    truncated: bool
    tags: list[str]
    why: list[dict[str, Any]]


class ReadingArea(BaseModel):
    name: str
    score_classical: float | None
    score_learned: float | None = None
    model_disagreement: float | None = None
    tier: str
    stability: Stability | None
    probability: float | None = None     # null until Layer 6 calibrates
    calibrated: bool = False
    bin_n: int = 0
    families_agree_w: float
    families_total_w: float
    polarity: list[str]
    polarity_touches: dict[str, list[str]] = Field(default_factory=dict)
    claims: list[ReadingClaim]
    school_conflicts: list[dict[str, Any]]
    windows: list[ReadingWindow] = Field(default_factory=list)
    avoid_window: ReadingWindow | None = None
    disclaimer: str | None = None
    # Offered findings with no claim that passed the validator and the checker within
    # CONFIG.max_attempts: {finding_id, kind, last_error, attempt}. Shown as "not narrated
    # within the checks"; the reading never fails on narration alone.
    narration_gaps: list[dict[str, Any]] = Field(default_factory=list)
    paragraph: str | None = None        # curious depth: the plain-language paragraph (checked like the summary)
    paragraph_cites: list[str] = Field(default_factory=list)
    other_placements: list[dict[str, Any]] = Field(default_factory=list)   # placements beyond the three offered
    astrologer_note: dict[str, Any] | None = None   # review step: {text, by, at}, the reviewer's words, never checked


class ReadingSummary(BaseModel):
    text: str
    cites: list[str]
    driver_planet: str
    driver_alternates: list[str]
    current_period: str | None
    top_areas: list[str]
    time_window_min: float | None
    stable_findings: int                # scored rules' fires (drafts counted apart, below)
    unstable_findings: int
    abstained_areas: list[str]
    timing_line: str | None = None      # engine-written, for a "when" question (the model writes no timing)
    source: str = "model"               # "model", or "engine" when no drafted summary passed the checks
    timing_note: str | None = None      # engine-written, under the timing line: what a window is and is not
    # Fires of scored rules and of draft placements (which fire and are recorded but carry no
    # weight), counted apart; None on readings made before they were.
    rules_fired: int | None = None
    drafts_fired: int | None = None
    drafts_unstable: int | None = None


class Reading(BaseModel):
    as_of: str
    weights: str
    engine: str
    question: str
    model: str
    attempts: int
    chart: dict[str, Any] = Field(default_factory=dict)   # birth data and every convention used
    narration_source: str = "live"      # "live", or "fixture:<path>" for an offline replay
    unchecked_sentences: int = 0        # offline replay: sentences with no recorded checker verdict
    narration_complete: bool = True     # false when some finding or the summary was not narrated within the checks
    depth: str = "astrologer"           # curious | learner | astrologer (SPEC Layer 7 prompt contract, item 1)
    review: dict[str, Any] = Field(default_factory=lambda: {"status": "draft"})   # draft | reviewed (SPEC Layer 6b)
    summary: ReadingSummary
    areas: list[ReadingArea]
    fired_rules: list[dict[str, Any]]
    unstable: list[dict[str, Any]]
    depends_on_birth_time: list[dict[str, Any]]
    disclaimers: list[str]


class NarrationError(RuntimeError):
    """The model's draft failed validation on every attempt (`errors` holds the last list)."""

    def __init__(self, message: str, errors: list[str]):
        super().__init__(message)
        self.errors = errors


# --- the validator ---------------------------------------------------------------------

TAG = re.compile(r"\[(rule|text|vote|chain):([^\]\s]+)\]")
CLAIM_VERBS = re.compile(
    r"\b(is|are|was|were|has|have|gives|give|shows|show|indicates|indicate|suggests|suggest|"
    r"brings|bring|forms|form|makes|make|supports|support|favours|favors|promises|denotes|"
    r"signifies|strengthens|weakens|rules|occupies|aspects|activates|marks|points|will|"
    r"can|may|tends|tend|means|leads|lead|sits|sit|lies|holds|hold|places|place)\b", re.I)
FORBIDDEN = {
    "probability": re.compile(r"\b(probability|probable|probably|likely|likelihood|unlikely|chances?|"
                              r"odds|percent)\b|\d+\s*%", re.I),
    "confidence": re.compile(r"\b(certain|certainly|definitely|definite|guarantee[sd]?|undoubtedly|"
                             r"surely|assuredly|inevitabl[ey]|without doubt|no doubt)\b", re.I),
    "death": re.compile(r"\b(die|dies|died|dying|death|demise|lifespan|life span|fatal|mortality|"
                        r"passing away|pass away)\b", re.I),
    # "cancer" the disease only in lowercase: capitalised Cancer is the sign ("UL2 in Cancer").
    "medical": re.compile(r"(?i:\b(diagnos\w*|diabetes|tumou?r|disorder|syndrome|prescri\w*|"
                          r"medication|surgery)\b)|\b(cancers?)\b"),
    "trade": re.compile(r"(?=.*\b(buy|buying|bought|sell|selling|sold|invest|investing|invested|purchase|"
                        r"purchasing|short|shorting)\b)(?=.*\b(stocks?|shares|equit(?:y|ies)|crypto\w*|bitcoin|"
                        r"securities|bonds?|options|futures|commodit(?:y|ies)|mutual funds?|forex|etfs?)\b)", re.I),
    # SPEC Layer 7 item 11: the engine states timing and windows itself.
    "timing": re.compile(r"\b(timing|timed|time frame|window|windows|date|dates|dated|engine|dasha|"
                         r"mahadasha|antardasha|bhukti|transits?|years?|months?|weeks?|"
                         r"january|february|march|april|june|july|august|september|october|november|"
                         r"december)\b|\b(?:19|20)\d{2}\b", re.I),
    "third_party": re.compile(r"\b(mother|father|parents?|partner|spouse|wife|husband|child|children|son|"
                              r"daughter|sibling|brother|sister)s?(?:'s)?\s+(?:\w+\s+){0,2}"
                              r"(will|is going to|shall|would|must|has to|gets?|suffers?)\b", re.I),
}


def sentences(text: str) -> list[str]:
    """Split prose into sentences, keeping trailing tags with the sentence they end."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?<=\])\s+(?=[A-Z])", text.strip())
    return [p.strip() for p in parts if p.strip()]


# A sentence "names" a family (SPEC Layer 7 item 11). House, lord and karaka are ordinary
# words, so they name their family only in the exact phrase "<family> vote(s)" or "<family>
# family"; a coordinated list counts as that phrase ("the house, lord and karaka votes").
# "karaka-sthana", "a denial house, which decides the vote" and "the star-lord level" do not.
# KP, varga, arudha and panchanga keep their distinctive words.
_FAMILY_NAMES = r"(?:house|lord|karaka|varga|arudha|kp|panchanga)"
_LIST_SEP = r"(?:\s*,\s*and\s+|\s*,\s*|\s+and\s+)"


def _phrase(word: str) -> re.Pattern:
    return re.compile(rf"\b{word}(?:{_LIST_SEP}{_FAMILY_NAMES})*\s+(?:votes?|famil(?:y|ies))\b", re.I)


FAMILY_WORDS = {
    "house": _phrase("house"),
    "lord": _phrase("lord"),
    "karaka": _phrase("karaka"),
    "varga": re.compile(r"\bvargas?\b|\bD\d{1,2}\b|\bdasamsa\b|\bnavamsa\b", re.I),
    "arudha": re.compile(r"\barudhas?\b|\bpadas?\b|\bupapada\b|\bA\d{1,2}\b|\bUL\b", re.I),
    "kp": re.compile(r"\bKP\b|\bcusps?\b|\bsub-?lords?\b", re.I),
    "panchanga": re.compile(r"\bpanchanga\b|\btithi\b|\bweekday\b|\bvara\b|\bnakshatra lord\b|"
                            r"\bnitya[- ]yoga\b", re.I),
}


def families_named(sentence: str) -> set[str]:
    bare = TAG.sub("", sentence)
    return {f for f, rx in FAMILY_WORDS.items() if rx.search(bare)}


def rule_names(rule_id: str) -> list[str]:
    lib = {r.id: r for r in default_rules()}
    rule = lib.get(rule_id)
    names = rule.data.get("names") if rule else None
    return names or [rule_id.split(".")[-1].replace("_", " ")]


# The engine states the tier (SPEC Layer 7 item 3): the model's summary may not use the tier words.
TIER_WORDS = re.compile(r"\b(strong|moderate|weak|mixed)\b", re.I)


def validate_summary(text: str, allowed: set[str], *, offered_votes=None, where: str = "summary",
                     family_rule: bool = True, chains: dict[str, list[str]] | None = None) -> list[str]:
    """`validate`, plus: no tier word (strong, moderate, weak, mixed) in the summary, or in a
    curious-depth paragraph (`where` names which, in the error)."""
    errors = validate(text, allowed, offered_votes=offered_votes, family_rule=family_rule, chains=chains)
    for sentence in sentences(text):
        m = TIER_WORDS.search(TAG.sub("", sentence))
        if m:
            errors.append(f"tier language ({m.group(0)!r}) in the {where}; the engine states the tier: {sentence!r}")
    return errors


CHAIN_KINDS = re.compile(r"\b(signs?|nakshatras?|navamsas?)\b", re.I)


def validate(text: str, allowed: set[str], *, offered_votes: dict[str, str | set[str]] | None = None,
             family_rule: bool = True, chains: dict[str, list[str]] | None = None) -> list[str]:
    """Every violation in a block of model text, as human-readable errors. `allowed` is the
    set of tags this text may carry; `offered_votes` maps family -> vote tag (or, for a
    summary over several areas, the set of that family's vote tags) for every vote offered:
    a sentence naming such a family must cite it (one of them). `family_rule` False (the
    curious depth, SPEC Layer 7 "Depth") drops both halves of that rule: a vote tag need not
    be on a sentence naming its family, and naming a family need not cite it; the checker,
    which reads every sentence against the derivations it cites, carries the guarantee.
    `chains` maps a chain tag's value (career.lord) to the planets its finding is about: a
    [chain:] sentence names one of them and the chain it follows (sign, nakshatra or navamsa),
    the way a vote's sentence names its family. "Nakshatra lord" in a chain sentence is the
    chain's word, not the panchanga family's."""
    offered_votes = offered_votes or {}
    errors = []
    for s in sentences(text):
        bare = TAG.sub("", s)
        found = TAG.findall(s)
        tags = {f"{k}:{v}" for k, v in found}
        if CLAIM_VERBS.search(bare) and not tags:
            errors.append(f"untagged claim: {s!r}")
        for t in tags - allowed:
            errors.append(f"tag not offered for this finding: [{t}] in {s!r}")
        if tags and not re.search(r"\]\s*[.!?]?\s*$", s):
            errors.append(f"tags must end the sentence: {s!r}")
        named = families_named(s)
        if any(k == "chain" for k, _ in found) and "panchanga" in named and \
                not FAMILY_WORDS["panchanga"].search(re.sub(r"\bnakshatra lords?\b", "", bare, flags=re.I)):
            named.discard("panchanga")
        for kind, value in found:
            if kind == "vote":
                family = value.split(".", 1)[-1]
                if family_rule and family not in named:
                    errors.append(f"[vote:{value}] on a sentence that does not name the {family} family: {s!r}")
            elif kind == "rule":
                if not any(n.lower() in bare.lower() for n in rule_names(value)):
                    errors.append(f"[rule:{value}] on a sentence that names none of {rule_names(value)}: {s!r}")
            elif kind == "chain":
                planets = (chains or {}).get(value, [])
                if planets and not any(re.search(rf"\b{p}\b", bare, re.I) for p in planets):
                    errors.append(f"[chain:{value}] on a sentence that names none of {planets}: {s!r}")
                if not CHAIN_KINDS.search(bare):
                    errors.append(f"[chain:{value}] on a sentence that names no chain (sign, nakshatra or navamsa): {s!r}")
        for family in sorted(named) if family_rule else ():
            want = offered_votes.get(family)
            want = {want} if isinstance(want, str) else set(want or ())
            if want and not want & tags:
                shown = " or ".join(f"[{t}]" for t in sorted(want))
                errors.append(f"names the {family} family but does not cite {shown}: {s!r}")
        for kind, rx in FORBIDDEN.items():
            m = rx.search(bare)
            if m:
                word = m.group(0) or " + ".join(g for g in m.groups() if g)
                errors.append(f"{kind} language ({word!r}) in {s!r}")
    return errors


# --- what the engine hands the model ---------------------------------------------------

THIRD_PARTY_AREAS = {"mother_home", "children", "marriage", "father", "synastry"}
DISCLAIMER_KEYS = {"health": "health", "longevity": "longevity", "wealth": "finance", "gains": "finance",
                   "debts_enemies": "finance"}
DISCLAIMERS = {
    "health": "This is a classical indication, not a medical assessment; it diagnoses nothing.",
    "longevity": "Classical longevity indications are shown as indications only; the engine does not time death.",
    "finance": "This is a classical indication, not financial advice; it recommends no trade or investment.",
    "third_party": "This describes the relationship as seen from this chart, not the other person's own life.",
}
AREA_WORDS = {
    "career": ("career", "job", "work", "profession", "promotion", "business", "status"),
    "marriage": ("marriage", "marry", "spouse", "partner", "wedding", "relationship"),
    "wealth": ("wealth", "money", "income", "finance", "financial", "earn"),
    "health": ("health", "illness", "vitality", "disease"),
    "children": ("child", "children", "kids", "progeny"),
    "mother_home": ("mother", "home", "house", "property", "vehicle"),
    "intellect": ("education", "study", "studies", "exam", "learning"),
    "foreign": ("abroad", "foreign", "travel", "relocat"),
    "spirituality": ("spiritual", "moksha", "meditation"),
    "father": ("father",),
    "siblings": ("sibling", "brother", "sister", "courage"),
    "reputation": ("reputation", "fame", "public"),
    "fortune": ("fortune", "luck", "dharma"),
    "mind": ("mind", "emotion", "mental"),
    "gains": ("gains", "network", "friends"),
    "debts_enemies": ("debt", "enemies", "litigation", "court"),
    "personality": ("personality", "self", "temperament"),
    "longevity": ("longevity",),
}


def route(question: str, chart: Chart) -> tuple[list[str], bool]:
    """(areas, is a "when" question). With no area named, the chart's top areas."""
    q = question.lower()
    areas = [a for a, words in AREA_WORDS.items() if any(w in q for w in words)]
    when = bool(re.search(r"\bwhen\b|\bwhich year\b|\bwhat year\b|\btiming\b", q))
    return (areas or list(chart.scored.top)), when


def _text_tag(src: dict) -> str:
    return "text:" + "/".join(str(x).replace(" ", "-") for x in (src["text"], src["edition"], src["chapter"], src["verse"]))


BASIS_ORDER = {"lagna": 0, "moon": 1, "sun": 2}

FAMILY_SCHOOL = {"house": "parashari", "lord": "parashari", "karaka": "parashari", "varga": "parashari",
                 "arudha": "jaimini", "kp": "kp", "panchanga": "parashari"}


PLACEMENTS_PER_AREA = 3
_ORD = {1: "1st", 2: "2nd", 3: "3rd"} | {n: f"{n}th" for n in range(4, 13)}
# "the 10th, a career house": the area as an adjective, where its name is not one.
AREA_LABEL = {"personality": "self", "siblings": "sibling", "mother_home": "home and mother", "children": "children's",
              "intellect": "learning", "debts_enemies": "debts and adversaries", "father": "father's",
              "spirituality": "spiritual"}


def houses_involved(item: dict, area: str) -> list[dict]:
    """Which of the area's houses a finding involves, each with its basis and in words ("the
    10th, a career house"; "the 10th from the Sun, a career house"; "the 7th, the 10th's Bhavat
    Bhavam"), so a sentence calling it "the house of career" can be checked against the data."""
    from .scoring import AREAS, _houses
    spec = AREAS.get(area)
    if spec is None:
        return []
    houses = _houses(spec)
    primary = spec["houses"][0]
    found: list[tuple[str, int]] = []
    if item["kind"] == "rule":
        for fire in item.get("fires", []):
            found += [(fire["basis"], int(n[1:])) for n in fire["nodes"] if n.startswith("H")]
            for side in (fire.get("details") or {}).get("lordships", {}).values():
                found += [(fire["basis"], h) for h in side]
        for h in (item.get("placement") or {}).get("lord_of", []):
            found.append(("lagna", h))
    else:
        d = item.get("derivation")
        rows = d if isinstance(d, list) else [r for v in (d or {}).values() if isinstance(v, list) for r in v]
        for r in rows:
            if "house" in r and "basis" in r and "planet" not in r:
                found.append((r["basis"], r["house"]))
            for x in r.get("area_house_from", []) + r.get("rules", []):
                found.append((x["basis"], x["house"]))
            if "cusp" in r:
                found.append(("lagna", r["cusp"]))
    out, seen = [], set()
    label = AREA_LABEL.get(area, area.replace("_", " "))
    for basis, h in found:
        if h not in houses or (basis, h) in seen:
            continue
        seen.add((basis, h))
        where = "" if basis == "lagna" else f" from the {basis.capitalize()}"
        what = f"a {label} house" if h in spec["houses"] else f"the {_ORD[primary]}'s Bhavat Bhavam"
        out.append({"basis": basis, "house": h, "words": f"the {_ORD[h]}{where}, {what}"})
    return out


def other_placements(chart: Chart, area: str) -> list[dict]:
    """The area's placement fires beyond its three strongest: weighed by the engine and shown in
    the learner material, not offered to the writer."""
    from .rules import default_rules
    lib = {r.id: r for r in default_rules()}
    offered = {f["finding_id"] for f in findings(chart, area)[0]}
    rows = []
    for f in chart.fired_rules:
        if f.family not in PLACEMENT_FAMILIES or f"{f.id}@{f.basis}" in offered:
            continue
        if f.stability is not None and f.stability.time < 0.5:
            continue
        contribution = sum(abs(v) for th, v in f.themes.items() if area in THEME_AREAS.get(th, []))
        if contribution:
            rows.append({"finding_id": f"{f.id}@{f.basis}", "rule_id": f.id, "planet": f.nodes[0],
                         "scale": round(f.scale, 3), "contribution": round(contribution, 3),
                         "classical_effect": lib[f.id].data.get("narration_key") if f.id in lib else None,
                         "effect_status": effect_status(lib.get(f.id))})
    return sorted(rows, key=lambda r: (-r["contribution"], r["finding_id"]))


def findings(chart: Chart, area: str, as_of: date | None = None) -> tuple[list[dict], list[dict]]:
    """(narratable, depends-on-birth-time) findings for an area, split at time-stability
    0.5. Two kinds (SPEC Layer 7 item 8): the non-experimental fired rules whose themes map
    to the area, tagged by rule id and each checked source; and the area's family votes
    that voted (+1 or -1), tagged [vote:<area>.<family>] with the vote's derivation.
    Fires of one rule on the same planets from different bases are one finding listing its
    bases (id `yoga.ruchaka@lagna+sun`), with each basis's fire under `fires`; its
    stability and confidence are the minimum across those fires. Fires are split at 0.5
    before grouping, so a time-unstable basis does not take a stable one out of narration.
    A text's verse defines a yoga from the ascendant; the Moon and Sun bases are the
    engine's Sudarshana reading (Layer 2), so each non-lagna fire is marked `sudarshana`
    and cited to the rule, and the text tags are offered only when a lagna fire is present.
    Each finding carries its claim confidence: a fire's scale x the rule's confidence_base,
    a vote's family weight min(1, 1 - rho) x |vote|. A third kind, the dispositor chains
    (chains.py): the area's primary lord and main karaka, and in the personality area the
    chart's final dispositors, tagged [chain:<area>.<lord|karaka|chart>]; with `as_of` (the
    reading's date) each carries the Nadi activation of the periods running then."""
    from .scoring import family_rho
    lib = {r.id: r for r in default_rules()}
    ok, shaky = [], []
    groups: dict[tuple, list] = {}
    for f in chart.fired_rules:
        if not in_default(f.status, f.family) or not any(area in THEME_AREAS.get(t, []) for t in f.themes):
            continue
        unstable = f.stability is not None and f.stability.time < 0.5
        planets = tuple(n for n in f.nodes if not n.startswith("H"))
        groups.setdefault((unstable, f.id, planets), []).append(f)
    for (unstable, rule_id, planets), fires in groups.items():
        fires.sort(key=lambda f: BASIS_ORDER.get(f.basis, len(BASIS_ORDER)))
        rule = lib.get(rule_id)
        bases = [f.basis for f in fires]
        texts = [_text_tag(s) for s in (rule.data.get("source", []) if rule else []) if s.get("checked")]
        tags = [f"rule:{rule_id}"] + (texts if "lagna" in bases else [])
        base = rule.data.get("confidence_base", 0.5) if rule else 0.5
        times = [f.stability.time for f in fires if f.stability is not None]
        item = {"finding_id": f"{rule_id}@{'+'.join(bases)}", "kind": "rule", "rule_id": rule_id,
                "basis": ", ".join(bases), "bases": bases, "sudarshana_bases": [b for b in bases if b != "lagna"],
                "school": fires[0].school, "planets": list(planets),
                "themes": {k: round(v, 2) for k, v in fires[0].themes.items()},
                "fires": [{"basis": f.basis, "sudarshana": f.basis != "lagna",
                           "cited_to": "rule and text" if f.basis == "lagna" and texts else "rule",
                           "nodes": f.nodes, "scale": round(f.scale, 3),
                           "modifiers_applied": f.applied, "modifiers_unknown": f.unknown, "details": f.details,
                           "stability": f.stability.time if f.stability else None} for f in fires],
                "allowed_tags": tags, "stability": min(times) if times else None,
                "confidence": min(f.scale for f in fires) * base, "family": fires[0].family}
        if fires[0].family in PLACEMENT_FAMILIES and rule:
            when = rule.data["when"]
            item["placement"] = {"planet": fires[0].nodes[0], "house": when["house"],
                                 **({"lord_of": when["lord_of"]} if "lord_of" in when else {})}
            item["contribution"] = round(sum(abs(v) for th, v in fires[0].themes.items()
                                             if area in THEME_AREAS.get(th, [])), 3)
            if fires[0].status == "draft":
                # SPEC Layer 3: an effect written before its verse was read is not the text's.
                # The writer and the checker get the placement fact only; the effect line is in
                # the learner material, marked as a draft.
                item["status"] = "draft"
                item.pop("themes", None)
            else:
                # A promoted placement's classical effect, read in the named edition.
                item["classical_effect"] = rule.data.get("narration_key")
        item["area_houses"] = houses_involved(item, area)
        item["glossary"] = glossary_for(_check_data(item))
        (shaky if unstable else ok).append(item)
    # SPEC Layer 6b item 4: an area offers at most its three strongest placements (by theme
    # contribution to the area x scale); the rest stay in the learner material.
    placed = sorted((i for i in ok if i.get("family") in PLACEMENT_FAMILIES),
                    key=lambda i: (-i["contribution"], i["finding_id"]))
    ok = [i for i in ok if i.get("family") not in PLACEMENT_FAMILIES or i in placed[:PLACEMENTS_PER_AREA]]
    for i in ok:
        i.pop("contribution", None)            # used to choose the three; not the writer's to state
    a = chart.scored.areas.get(area)
    tally = area_votes(a) if a is not None and a.score_classical is not None else None
    if a is not None and a.score_classical is not None:
        from .scoring import family_weights
        rho = family_rho(chart.meta.varga_term, chart.meta.kp_vote)
        weights = family_weights(a, rho)
        for family, vote in a.votes.items():
            if not vote:
                continue
            tag = f"vote:{area}.{family}"
            item = {"finding_id": tag, "kind": "vote", "family": family, "vote": vote, "area_votes": tally,
                    "direction": "for" if vote > 0 else "against", "basis": "lagna, moon, sun 3:2:1"
                    if family in ("house", "lord") else "lagna", "school": FAMILY_SCHOOL[family],
                    "derivation": a.vote_details.get(family), "term": a.terms.get(family),
                    "allowed_tags": [tag], "stability": a.vote_stability.get(family),
                    "confidence": min(1.0, weights[family]) * abs(vote)}
            item["area_houses"] = houses_involved(item, area)
            item["glossary"] = glossary_for(_check_data(item))
            st = item["stability"]
            (shaky if st is not None and st < 0.5 else ok).append(item)
    from .chains import area_chain_findings
    for item in area_chain_findings(chart, area, as_of):
        item["area_houses"] = []
        item["glossary"] = glossary_for(_check_data(item))
        st = item["stability"]
        (shaky if st is not None and st < 0.5 else ok).append(item)
    return ok, shaky


def offered_chains(chart: Chart, areas: list[str]) -> dict[str, dict[str, list[str]]]:
    """area -> chain tag value -> the planets its finding is about (for the validator)."""
    from .chains import area_chain_findings
    return {a: {f["finding_id"].split(":", 1)[1]: f["planets"] for f in area_chain_findings(chart, a)} for a in areas}


def area_votes(a) -> dict:
    """The engine's seven tests on an area, as the curious paragraph's closing clause counts
    them: each family's verdict (for, against, abstains, not applicable) and the counts."""
    from .scoring import FAMILIES
    word = {1: "for", -1: "against", 0: "abstains", None: "not applicable"}
    verdict = {f: word[a.votes.get(f)] for f in FAMILIES}
    counts = {w: sum(1 for v in verdict.values() if v == w) for w in ("for", "against", "abstains", "not applicable")}
    return {"tests": len(FAMILIES), "verdict": verdict, **counts}


GLOSSARY_FILE = Path(__file__).with_name("data") / "glossary.yaml"


@lru_cache(maxsize=1)
def glossary() -> list[dict]:
    """data/glossary.yaml: one plain definition per Sanskrit or technical term, with its source.
    Each entry gets one pattern over its aliases: whole words, case-insensitive, except two- and
    three-letter codes (UL, AK, A7), which must match in capitals."""
    import yaml
    out = []
    for e in yaml.safe_load(GLOSSARY_FILE.read_text()):
        long = [a for a in e["aliases"] if len(a) > 3]
        short = [a for a in e["aliases"] if len(a) <= 3]
        parts = ([rf"(?i:\b(?:{'|'.join(re.escape(a) for a in long)})\b)"] if long else []) + \
                ([rf"\b(?:{'|'.join(re.escape(a) for a in short)})\b"] if short else [])
        out.append(dict(e, pattern=re.compile("|".join(parts))))
    return out


def _present(data: Any) -> Any:
    """The data with empty and false values (and their keys) removed: `sudarshana_bases: []` or
    `vargottama_d9: false` is no reason to gloss Sudarshana or vargottama."""
    if isinstance(data, dict):
        kept = {k: _present(v) for k, v in data.items()}
        return {k: v for k, v in kept.items() if v not in (None, False, [], {}, "")}
    if isinstance(data, list):
        return [x for x in (_present(v) for v in data) if x not in (None, False, [], {}, "")]
    return data


def glossary_for(data: Any) -> dict[str, str]:
    """The glossary entries for every term that appears in a finding's data (empty and false
    fields left out), term -> definition."""
    text = json.dumps(_present(data), default=str)
    return {e["term"]: e["definition"] for e in glossary() if e.get("writer", True) and e["pattern"].search(text)}


def school_conflicts(area) -> list[dict]:
    """A Jaimini (arudha) or KP family voting against the Parashari families' majority."""
    parashari = [area.votes.get(f) for f in ("house", "lord", "karaka", "varga")]
    s = sum(v for v in parashari if v)
    if s == 0:
        return []
    side = 1 if s > 0 else -1
    out = []
    for family, school in (("arudha", "jaimini"), ("kp", "kp")):
        v = area.votes.get(family)
        if v and v == -side:
            out.append({"schools": ["parashari", school], "families": ["house/lord/karaka/varga", family],
                        "parashari": "for" if side > 0 else "against", school: "against" if side > 0 else "for"})
    return out


SYSTEM_PROMPT = """You write one part of a Vedic-astrology reading: plain sentences about findings an \
engine has already computed. You add no facts. A finding is either a rule that fired (with the \
planets, houses and modifiers it involved) or a family vote (house, lord, karaka, varga, arudha, \
KP, panchanga) with its derivation: the planets, houses, dignities, cusp sub-lords or varga \
placements the vote used, and whether it is for or against the area. Each finding has an id and \
the citation tags you may use. A rule that fires from more than one basis (lagna, Moon, Sun) is \
one finding listing its bases, with each basis's fire; narrate it as one claim ("forms from the \
lagna and from the Sun"). A third kind is a dispositor chain: for one planet (the area's lord or its \
main karaka) the sign, nakshatra and navamsa chains to their final dispositors, the loops and mutual \
exchanges it is part of, and whether a running period activates it, each stated in its `facts`; the \
chart chain (chain:personality.chart) is the final dispositors of the whole chart. A sentence citing \
a chain names the planet and the chain it follows (sign, nakshatra or navamsa) and says only what \
the facts state; a running period is "the current major period" or "sub-period" of its lord, never \
a date.

Write, for each area, one claim per finding, in the order given. Each claim narrates that finding \
only and stands alone: it is checked against that finding's data and nothing else, so it may not \
refer to another finding or claim (no "again", "the same", "also", "as above", "likewise"). Each claim ends with one or more of that finding's allowed tags, written exactly, for example \
[rule:yoga.ruchaka], [text:BPHS/Santhanam-1984/75/1-2] or [vote:career.kp]. For a vote, say \
in words what the derivation shows. Put the tags at the very end of the sentence. Also write a two- or three-sentence summary answering the question; each summary \
sentence that states something ends with the tags of the findings it draws on, and is checked \
against those findings' data only.

The engine states the confidence tier, the stability and any timing windows itself, so do not \
write confidence words (certain, definitely, guaranteed), probabilities or percentages, do not \
restate the tier, and do not mention timing, windows, dates, years, dashas, transits or the engine. \
A sentence citing a vote names that family ("the KP vote", "the house vote"); a sentence naming a \
family's vote cites it; a sentence citing a rule names the yoga. Say exactly what the derivation \
states and attach each detail to the thing it belongs to: a cusp's star is the cusp's, not its \
sub-lord's. Never write about death or its timing, medical conditions, or buying and selling \
investments. For relationships (mother, father, partner, children, siblings), describe only what \
this chart shows about the relationship, never what will happen to the other person. A finding with \
status draft is a placement fact only: say where the planet is and which house it rules, and nothing \
it is said to mean, since its effect has not been read in the text. A house is called by its area \
("the house of career", "a career house") only where the finding's area_houses words it so ("the \
10th, a career house"); say "the 10th" otherwise."""


DEPTHS = ("curious", "learner", "astrologer")

# The family-name sentence of SYSTEM_PROMPT, dropped at curious depth (SPEC Layer 7 "Depth").
FAMILY_RULE_TEXT = ('A sentence citing a vote names that family ("the KP vote", "the house vote"); a sentence naming a '
                    "family's vote cites it; ")

CURIOUS_PROMPT = """

Depth: curious. The reader knows no astrology. For each area, besides the claims, write \
`paragraph`: one short paragraph, plain language, in this shape. First, what the chart shows, in \
chart terms with a gloss: where the planets are and what combination they form ("the Sun and \
Mercury sit together in the house of career, forming Budhaditya yoga, a Sun and Mercury \
combination"). Then what the tradition associates it with, from the finding's themes. Then the \
weakest point or the disagreement, named from the derivations: for example the area's own house \
weakest by strength while its lord and the planets in it are strong; a school whose test goes the \
other way; a test that abstains. Last, in one clause, how many of the engine's seven tests agree, \
from the area's `tests` (say how many apply when some do not) - never a list of the tests or votes, \
and a placement finding (a lord or a planet in a house, with its classical_effect when it has one) is one chart fact \
among the others, folded into the sentence about where the planets are, never a sentence of its own, \
and do not name the votes one by one anywhere in the paragraph. No degrees, rupas, strength ratios \
or other figures beyond that count; every Sanskrit or technical term glossed once, the first time \
it appears, from the finding's glossary entry for it: the same meaning, in plain words ("Ruchaka \
yoga, the great-person combination of Mars"); a term \
with no glossary entry is left out rather than glossed from elsewhere. Each sentence that states \
something ends with the tags of the findings it draws on, written exactly as in the claims, and \
is checked against those findings' data only; the closing clause cites the votes it counts. Do \
not state the tier, the stability or any timing: the engine states them.

The summary, at this depth, answers the question in two or three sentences about the asked area \
only, tagged the same way, and does not repeat the paragraph's sentences. At this depth a \
sentence citing a vote need not name its family. The claims are still written as above: they \
are the astrologer's reading, shown under the paragraph."""


def system_prompt(depth: str) -> str:
    if depth not in DEPTHS:
        raise ValueError(f"depth must be one of {DEPTHS}, not {depth!r}")
    if depth == "curious":
        assert FAMILY_RULE_TEXT + "a sentence citing a rule" in SYSTEM_PROMPT
        return SYSTEM_PROMPT.replace(FAMILY_RULE_TEXT + "a sentence citing a rule", "A sentence citing a rule") \
            + CURIOUS_PROMPT
    return SYSTEM_PROMPT


def timing_note(areas: list[str]) -> str:
    """The engine's sentence under the timing line: what the windows are, and what they are not."""
    names = [a.replace("_", " ") for a in areas]
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return f"These are periods the engine scores as favourable for {joined}; it does not predict when you will act."


def payload(chart: Chart, question: str, areas: list[str], depth: str = "astrologer",
            as_of: date | None = None) -> tuple[str, dict[str, set[str]]]:
    """The user message for the model, and the tags allowed per finding id."""
    allowed: dict[str, set[str]] = {}
    body = {"question": question, "depth": depth, "areas": []}
    for name in areas:
        ok, _ = findings(chart, name, as_of)
        for f in ok:
            allowed[f["finding_id"]] = set(f["allowed_tags"])
        a = chart.scored.areas.get(name)
        body["areas"].append({"name": name, "findings": ok,
                              **({"tests": area_votes(a)} if a is not None and a.score_classical is not None else {})})
    return json.dumps(body, indent=1, default=str), allowed


def offered_votes(chart: Chart, areas: list[str]) -> dict[str, dict[str, str]]:
    """area -> family -> vote tag, for the votes offered as findings."""
    out = {}
    for name in areas:
        ok, _ = findings(chart, name)
        out[name] = {f["family"]: f["finding_id"] for f in ok if f["kind"] == "vote"}
    return out


# --- the model call ----------------------------------------------------------------------

Drafter = Callable[[str, str, list[str]], ReadingDraft]


class Proposition(BaseModel):
    text: str = Field(description="One proposition the sentence asserts, as a reader would take it.")
    supported: bool = Field(description="True only if the derivation states it.")
    evidence: str = Field(description="The derivation field that states it, or why it is not stated.")


class CheckResult(BaseModel):
    propositions: list[Proposition]


Checker = Callable[[str, str], CheckResult]

CHECKER_PROMPT = """You check one sentence of an astrology reading against the data it was written \
from. List every proposition the sentence asserts, including what each appositive or relative \
clause attaches to, read the way an ordinary reader would read it. For each, say whether the data \
states it. Mark it unsupported if the data does not state it, if the sentence attaches a detail to \
the wrong thing, or if the sentence is ambiguous between a supported and an unsupported reading. \
Generic framing ("for career", "the vote is against") is supported when the data's direction or \
area says so. A gloss, a short definition given beside a term ("marana karaka sthana, a placement \
in which a planet cannot give its good results"), is supported when it matches the meaning of \
that term's entry in the data's glossary, and unsupported when it does not match or the term has \
no entry there. A chain finding's `facts` state its rows in sentences; a proposition about a \
chain is supported when its facts or rows state it. A house called by its area ("the house of career", "a career house") is supported \
when the data's area_houses lists that house in those words, and unsupported otherwise. Ignore the \
bracketed citation tags."""


def _meta(response, kind: str, effort: str, started: float | None = None) -> dict:
    import time
    from datetime import datetime, timezone
    usage = getattr(response, "usage", None)
    out = {"kind": kind, "request_id": getattr(response, "_request_id", None),
           "model": getattr(response, "model", None), "effort": effort,
           "usage": usage.model_dump() if hasattr(usage, "model_dump") else usage,
           "stop_reason": getattr(response, "stop_reason", None),
           "timestamp": datetime.now(timezone.utc).isoformat()}
    if started is not None:
        out["seconds"] = round(time.perf_counter() - started, 3)
    return out


class AnthropicDrafter:
    """Calls the Messages API with structured output. Keeps the conversation append-only
    across regenerations (each failed draft and its errors stay in the history)."""

    def __init__(self, config: NarrationConfig = CONFIG, client=None):
        import anthropic
        self.config = config
        self.client = client or anthropic.Anthropic()
        self.messages: list[dict] = []
        self.last_meta: dict | None = None

    def __call__(self, system: str, user: str, errors: list[str]) -> ReadingDraft:
        if not self.messages:
            self.messages.append({"role": "user", "content": user})
        else:
            self.messages.append({"role": "user", "content":
                                  "The draft was rejected. Fix every one of these and return the whole draft again:\n- "
                                  + "\n- ".join(errors)})
        import time
        cfg = self.config
        started = time.perf_counter()
        response = self.client.beta.messages.parse(
            model=cfg.model, max_tokens=cfg.max_tokens, betas=list(cfg.betas), fallbacks=cfg.fallbacks,
            output_config={"effort": cfg.effort}, system=system, messages=self.messages,
            output_format=ReadingDraft)
        self.last_meta = _meta(response, "writer", cfg.effort, started)
        if response.stop_reason == "refusal":
            raise NarrationError("the model declined the request", [str(getattr(response, "stop_details", ""))])
        self.messages.append({"role": "assistant", "content": response.content})
        if response.parsed_output is None:
            raise NarrationError("no structured output in the response", [response.stop_reason or ""])
        return response.parsed_output


class AnthropicChecker:
    """The semantic checker (SPEC Layer 7 item 10): one structured call per sentence with only
    the sentence and the derivation it may draw on (a claim's finding; for a summary sentence,
    the findings it cites). Same model and config block as the writer, at `checker_effort`.

    The calls of one attempt are independent, so `check_many` sends them concurrently through
    the async client (`CONFIG.checker_concurrency` in flight at once; 1 sends them one after
    another), and returns the results in the order asked."""

    def __init__(self, config: NarrationConfig = CONFIG, client=None, async_client=None):
        import anthropic
        self.config = config
        self.client = client or anthropic.Anthropic()
        self._async_client = async_client
        self.last_meta: dict | None = None

    def _kwargs(self, sentence: str, derivation: str) -> dict:
        cfg = self.config
        return dict(model=cfg.model, max_tokens=cfg.max_tokens, betas=list(cfg.betas), fallbacks=cfg.fallbacks,
                    output_config={"effort": cfg.checker_effort}, system=CHECKER_PROMPT,
                    messages=[{"role": "user", "content": f"Sentence:\n{sentence}\n\nData:\n{derivation}"}],
                    output_format=CheckResult)

    def _result(self, response, started: float) -> tuple[CheckResult, dict]:
        meta = _meta(response, "checker", self.config.checker_effort, started)
        if response.stop_reason == "refusal" or response.parsed_output is None:
            # No verdict is not a pass: the sentence is rejected like an unsupported one, and the
            # rest of the attempt's checks stand.
            return CheckResult(propositions=[Proposition(
                text="(no verdict)", supported=False,
                evidence=f"the checker returned no result ({response.stop_reason or 'no structured output'})")]), meta
        return response.parsed_output, meta

    def __call__(self, sentence: str, derivation: str) -> CheckResult:
        import time
        started = time.perf_counter()
        result, self.last_meta = self._result(self.client.beta.messages.parse(**self._kwargs(sentence, derivation)),
                                              started)
        return result

    def check_many(self, items: list[tuple[str, str]]) -> list[tuple[CheckResult, dict]]:
        if self.config.checker_concurrency <= 1:
            return [(self(s, d), self.last_meta) for s, d in items]
        return _run_async(self._gather(items))

    async def _gather(self, items):
        import asyncio
        import time
        import anthropic
        client = self._async_client or anthropic.AsyncAnthropic()
        gate = asyncio.Semaphore(self.config.checker_concurrency)

        async def one(sentence, derivation):
            async with gate:
                started = time.perf_counter()
                response = await client.beta.messages.parse(**self._kwargs(sentence, derivation))
                return self._result(response, started)
        return await asyncio.gather(*(one(s, d) for s, d in items))


def _run_async(coro):
    """Run a coroutine to completion from sync code, also when the caller is itself inside a
    running event loop (a web server's worker): then it runs on a thread of its own."""
    import asyncio
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


def chart_header(chart: Chart) -> dict[str, Any]:
    """What the reading was computed from: the birth data, the sampler, and every Meta
    convention (ayanamsa, node, house system, dasha year, karaka scheme and the rest), so a
    reading can be reproduced from its header."""
    m, b, u = chart.meta, chart.birth, chart.uncertainty
    conventions = m.model_dump(exclude={"engine", "ayanamsa_value", "jd", "time_accuracy"})
    return {"birth_utc": b.utc, "lat": b.lat, "lon": b.lon, "tz": b.tz, "accuracy": m.time_accuracy,
            "ayanamsa_value": m.ayanamsa_value, "conventions": conventions,
            "sampler": ({"samples": u.samples, "shape": u.shape, "half_width_min": u.half_width_min,
                         "ayanamsas": u.ayanamsas, "house_systems": u.house_systems} if u else None)}


# --- offline replay of a recording -------------------------------------------------------

class FixtureDrafter:
    """Replays a recording's writer drafts in order (the last one repeats)."""

    def __init__(self, recording: dict):
        self.drafts = [ReadingDraft(**d) for d in recording["drafts"]]
        self.calls = 0
        self.last_meta: dict | None = None

    def __call__(self, system: str, user: str, errors: list[str]) -> ReadingDraft:
        self.calls += 1
        self.last_meta = {"kind": "writer", "replayed": True}
        return self.drafts[min(self.calls, len(self.drafts)) - 1]


class FixtureChecker:
    """Replays a recording's checker verdicts by sentence (the latest one recorded for that
    exact sentence). A sentence with no recorded verdict was never checked: it is passed with
    no propositions and counted in `unchecked`, which the reading reports. Offline replay is
    a rendering of a recording, not a check."""

    def __init__(self, recording: dict):
        self.verdicts = {c["sentence"]: CheckResult(**c["result"])
                         for c in recording.get("calls", []) if c.get("kind") == "checker"}
        self.unchecked: set[str] = set()
        self.last_meta: dict | None = None

    def __call__(self, sentence: str, derivation: str) -> CheckResult:
        self.last_meta = {"kind": "checker", "replayed": True}
        if sentence in self.verdicts:
            return self.verdicts[sentence]
        self.unchecked.add(sentence)
        return CheckResult(propositions=[])


# --- assembly ----------------------------------------------------------------------------

def _date_str(jd: float) -> str:
    import swisseph as swe
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def _window(w) -> ReadingWindow:
    d = w.derivation
    sp = d.get("strongest_piece")
    return ReadingWindow(
        start=_date_str(w.start_jd), end=_date_str(w.end_jd), score=round(w.joint, 3),
        q=round(w.dasha_quality, 3), q_terms={k: round(v, 3) for k, v in d.get("q_terms", {}).items()},
        t=round(w.transit_activation, 3), relevant_systems=d.get("relevant_systems", []),
        strongest_piece=({"start": _date_str(sp["start_jd"]), "end": _date_str(sp["end_jd"]),
                          "score": round(sp["joint"], 3), "t": round(sp["t"], 3)} if sp else None),
        confidence=w.confidence, stability=(w.stability or {}).get("time_range_days"),
        sandhi="dasha_sandhi" in w.tags, truncated="truncated" in w.tags, tags=w.tags,
        why=[{"kind": "dasha", "system": s, "lords": l} for s, l in w.periods.items()]
        + [{"kind": "transit", "activation": round(w.transit_activation, 3),
            "targets": d.get("targets")}])


SUDARSHANA_NOTE = ("is the engine's Sudarshana reading (counting from that body as lagna). The texts define "
                   "the yoga from the ascendant, so the text citations belong to the lagna fire and this one is "
                   "cited to the rule only.")


DRAFT_EFFECT = "draft effect, verse not yet read"


def effect_status(rule) -> str | None:
    """How a placement's effect line stands: a draft, or read in the named edition (by whom)."""
    if rule is None or rule.data.get("family") not in PLACEMENT_FAMILIES:
        return None
    if rule.data["status"] == "draft":
        return DRAFT_EFFECT
    src = next((s for s in rule.data.get("source", []) if s.get("checked")), {})
    who = f" by {src['read_by']} on {src['read_on']}" if src.get("read_by") else ""
    return f"verse read{who}"


def learner_data(f: dict) -> dict[str, Any]:
    """What a claim rests on, as data the page and the website render (never the model): for a
    rule, the rule block, each modifier with where it applied, and each basis's fire with the
    Sudarshana mark; for a vote, its direction, family, stability and derivation rows."""
    if f["kind"] == "chain":
        from .chains import DISPOSITOR
        return {"kind": "chain", "chain": f["chain"], "planet": f["planet"], "role": f["role"], "what": DISPOSITOR,
                "stability": f["stability"], "facts": f["facts"], "derivation": f["derivation"]}
    if f["kind"] == "vote":
        return {"kind": "vote", "family": f["family"], "school": f["school"], "vote": f["vote"],
                "direction": f["direction"], "stability": f["stability"], "term": f["term"],
                "derivation": f["derivation"]}
    from .rules import bound_planets, modifier_text
    rule = next(r for r in default_rules() if r.id == f["rule_id"])
    bound = bound_planets(rule, f["fires"][0]["nodes"])            # the same planets in every fire
    mods = []
    for m in rule.data.get("modifiers", []):
        text = modifier_text(m, bound)
        mods.append({"modifier": text, "scale": m["scale"], "applied": {
            x["basis"]: ("applied" if f"{text} -> x{m['scale']}" in x["modifiers_applied"]
                         else "unknown" if text in x["modifiers_unknown"] else "not applied") for x in f["fires"]}})
    effect = ({"effect": rule.data.get("narration_key"), "effect_status": effect_status(rule)}
              if rule.data.get("family") in PLACEMENT_FAMILIES else {})
    return {"kind": "rule", **effect,
            "rule": {"id": rule.id, "school": rule.data["school"], "status": rule.data["status"],
                                     "confidence_base": rule.data.get("confidence_base", 0.5),
                                     "when": rule.data["when"]},
            "modifiers": mods,
            "fires": [{"basis": x["basis"], "nodes": x["nodes"], "scale": x["scale"], "stability": x["stability"],
                       "cited_to": x["cited_to"], "sudarshana": x["sudarshana"]} for x in f["fires"]],
            "sudarshana_bases": f.get("sudarshana_bases", [])}


def _label(stability: float | None) -> str | None:
    from .uncertainty import label
    return None if stability is None else label(stability)


def upgrade_reading(reading: "Reading", chart: Chart) -> "Reading":
    """A reading JSON brought up to the current schema from its own chart: the engine-derived
    fields a reading written before them lacks (each claim's learner block, the timing line).
    The model's text is not touched."""
    as_of = date.fromisoformat(reading.as_of)
    by_id = {f["finding_id"]: f for a in reading.areas for f in findings(chart, a.name, as_of)[0]}
    def up(c):
        fill = {}
        if not c.learner:
            fill["learner"] = learner_data(by_id[c.finding_id])
        if c.stability_label is None and c.stability is not None:
            fill["stability_label"] = _label(c.stability)
        return c.model_copy(update=fill) if fill else c
    areas = [a.model_copy(update={"claims": [up(c) for c in a.claims]}) for a in reading.areas]
    summary = reading.summary
    if summary.timing_note is None and (summary.timing_line or any(a.windows for a in reading.areas)):
        summary = summary.model_copy(update={"timing_note": timing_note([a.name for a in reading.areas if a.windows])})
    if summary.timing_line is None:
        lines = [timing_line(a.name, a.windows, a.avoid_window) for a in reading.areas if a.windows]
        summary = summary.model_copy(update={"timing_line": " ".join(x for x in lines if x) or None})
    return reading.model_copy(update={"areas": areas, "summary": summary})


def engine_summary(areas: list["ReadingArea"], routed: list[str], sc, period: str | None,
                   when_line: str | None) -> str:
    """The summary the engine writes from its own fields when no drafted summary passed the
    checks: the asked areas' tiers with their stability, the top areas, the driver, the current
    period and the timing line. Every word is a field."""
    by = {a.name: a for a in areas}
    parts = []
    for name in [n for n in routed if n in by] or [a.name for a in areas[:1]]:
        a = by[name]
        st = f" (time-stability {a.stability.time:.2f}, {a.stability.label})" if a.stability else ""
        parts.append(f"{name.replace('_', ' ').capitalize()}: tier {a.tier}{st}.")
    parts.append(f"Top areas: {', '.join(n.replace('_', ' ') for n in sc.top)}.")
    parts.append(f"Driver planet: {sc.driver.driver}.")
    if period:
        parts.append(f"Current Vimshottari period: {period.replace('-', '–')}.")
    if when_line:
        parts.append(when_line)
    return " ".join(parts)


def _vim_lords(w: ReadingWindow) -> str:
    lords = next((x["lords"] for x in w.why if x.get("kind") == "dasha" and x.get("system") == "vimshottari"), [])
    return "–".join(lords) or "no Vimshottari lords"


def timing_line(area: str, windows: list[ReadingWindow], avoid: ReadingWindow | None) -> str | None:
    """The engine's answer to a "when" question, in words: the highest-scoring window with its
    Vimshottari lords and strongest piece, and the window to avoid. Written by the engine
    because the model may not write about timing (SPEC Phase 4, item 2)."""
    if not windows:
        return None
    best = max(windows, key=lambda w: w.score)
    name = area.replace("_", " ")
    marks = [m for m, on in (("dasha sandhi: confidence capped at moderate", best.sandhi),
                             ("cut by the start or end of the range asked about", best.truncated)) if on]
    line = (f"Best window for {name} by the engine's timing score: {best.start} to {best.end} "
            f"(Vimshottari {_vim_lords(best)}, score {best.score:.2f}"
            + "".join(f"; {m}" for m in marks) + ")")
    sp = best.strongest_piece
    if sp and (sp["start"], sp["end"]) != (best.start, best.end):
        line += f", strongest from {sp['start']} to {sp['end']} (score {sp['score']:.2f})"
    line += "."
    if avoid is not None:
        line += (f" Window to avoid: {avoid.start} to {avoid.end} (Vimshottari {_vim_lords(avoid)}, "
                 f"score {avoid.score:.2f}).")
    return line


def _check_payload(f: dict) -> str:
    """What the checker sees for one finding: its derivation and nothing else."""
    return json.dumps(_check_data(f), indent=1, default=str)


def _check_data(f: dict) -> dict:
    keep = ("finding_id", "kind", "rule_id", "family", "direction", "basis", "bases", "sudarshana_bases",
            "school", "planets",
            "themes", "fires", "derivation", "area_votes", "glossary", "classical_effect", "status", "placement",
            "area_houses", "chain", "planet", "role", "facts")
    return {k: f[k] for k in keep if k in f}


def _summary_checks(summary: str, finding_data: dict[str, dict]) -> list[tuple[str, list[str], str]]:
    """(sentence, finding ids, data) for each summary sentence that cites a tag: the data is
    the union of the derivations of every finding offering one of its tags."""
    out = []
    for s in sentences(summary):
        tags = {f"{k}:{v}" for k, v in TAG.findall(s)}
        if not tags:
            continue
        ids = [fid for fid, f in finding_data.items() if tags & set(f["allowed_tags"])]
        data = {"findings": [_check_data(finding_data[i]) for i in ids]}
        out.append((s, ids, json.dumps(data, indent=1, default=str)))
    return out


def narrate(chart: Chart, question: str, *, drafter: Drafter | None = None, checker: Checker | None = None,
            as_of: date | None = None, config: NarrationConfig = CONFIG,
            recording: list | None = None, areas: list[str] | None = None,
            progress: Callable[[str, dict], None] | None = None, depth: str = "astrologer") -> Reading:
    """`areas` overrides the routed areas (the question's "when" is still read from it).
    `progress(stage, info)` is told "draft" before each writer call and "check" before each
    attempt's checker calls, with the attempt number (the service's job status). `depth`
    "curious" adds a plain-language paragraph per area, validated and checked like the
    summary; the claims and every engine field are the same at every depth."""
    progress = progress or (lambda stage, info: None)
    if chart.scored is None:
        raise ValueError("narration needs a scored chart (birth moment, Shadbala, Bhava Bala)")
    as_of = as_of or date.today()
    sc = chart.scored
    routed, when = route(question, chart)
    areas = list(areas) if areas is not None else routed
    system = system_prompt(depth)
    curious = depth == "curious"
    user, allowed = payload(chart, question, areas, depth, as_of)
    area_tags = {name: set().union(*(set(f["allowed_tags"]) for f in findings(chart, name, as_of)[0])) for name in areas}
    all_tags = set().union(*allowed.values()) if allowed else set()
    drafter = drafter or AnthropicDrafter(config)
    checker = checker or AnthropicChecker(config)
    votes_offered = offered_votes(chart, areas)
    chains_offered = offered_chains(chart, areas)
    all_chains = {k: v for name in areas for k, v in chains_offered[name].items()}
    finding_data = {f["finding_id"]: f for name in areas for f in findings(chart, name, as_of)[0]}
    all_votes: dict[str, set[str]] = {}
    for name in areas:
        for fam, tag in votes_offered[name].items():
            all_votes.setdefault(fam, set()).add(tag)

    # Every attempt: the writer drafts, the validator reads every sentence, and (once the draft
    # passes, or on the last attempt for the sentences that pass) the checker reads them. A
    # claim or summary the checker accepts is kept, the latest accepted version of each; after
    # the last attempt, a finding with none is a narration gap and a summary with none is
    # replaced by the engine's own. The reading never fails on narration alone.
    kept: dict[tuple[str, str], DraftClaim] = {}        # (area, finding id) -> latest accepted claim
    last_error: dict[tuple[str, str], tuple[str, int]] = {}
    kept_summary, summary_error = None, None
    kept_para: dict[str, str] = {}
    para_error: dict[str, tuple[str, int]] = {}
    draft, errors, attempts, clean = None, [], 0, False
    for attempts in range(1, config.max_attempts + 1):
        progress("draft", {"attempt": attempts})
        try:
            draft = drafter(system, user, errors)
        except NarrationError as e:                        # a refusal or no structured output
            errors = [str(e)] + list(e.errors)
            if recording is not None:
                recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "writer"}, attempt=attempts,
                                      draft=None, validator_errors=[], writer_error=errors))
            summary_error = (errors[0], attempts)
            for name in areas:
                para_error[name] = (errors[0], attempts)
                for f in findings(chart, name, as_of)[0]:
                    last_error[(name, f["finding_id"])] = (errors[0], attempts)
            continue
        entry = dict(getattr(drafter, "last_meta", None) or {"kind": "writer"}, attempt=attempts,
                     draft=draft.model_dump())
        summary_errs = validate_summary(draft.summary, all_tags, offered_votes=all_votes, family_rule=not curious,
                                        chains=all_chains)
        errors = list(summary_errs)
        claim_errs: dict[tuple[str, str], list[str]] = {}
        drafted: list[tuple[str, DraftClaim]] = []
        for da in draft.areas:
            if da.name not in areas:
                errors.append(f"area not asked for: {da.name}")
                continue
            for c in da.claims:
                if c.finding_id not in allowed:
                    errors.append(f"unknown finding id {c.finding_id!r}")
                    continue
                if (da.name, c.finding_id) in claim_errs:
                    errors.append(f"two claims for {c.finding_id} in {da.name}")
                    continue
                errs = validate(c.text, allowed[c.finding_id], offered_votes=votes_offered[da.name],
                                family_rule=not curious, chains=chains_offered[da.name])
                if not TAG.search(c.text):
                    errs.append(f"claim without a tag: {c.text!r}")
                claim_errs[(da.name, c.finding_id)] = errs
                drafted.append((da.name, c))
                errors += errs
        para_errs: dict[str, list[str]] = {}
        if curious:
            # Each area's paragraph is read like the summary: tags offered for the area's findings,
            # families named and cited, and no tier word (the engine states the tier).
            for name in areas:
                text = next((d.paragraph for d in draft.areas if d.name == name), None)
                para_errs[name] = (validate_summary(text, area_tags[name], offered_votes=votes_offered[name],
                                                    where=f"{name} paragraph", family_rule=False,
                                                    chains=chains_offered[name])
                                   if text else [f"no paragraph for {name}: at curious depth every area has one"])
                errors += para_errs[name]
        entry["validator_errors"] = list(errors)
        if recording is not None:
            recording.append(entry)
        for name, errs in para_errs.items():
            if errs:
                para_error[name] = (errs[0], attempts)
        for key, errs in claim_errs.items():
            if errs:
                last_error[key] = (errs[0], attempts)
        if summary_errs:
            summary_error = (summary_errs[0], attempts)
        final = attempts == config.max_attempts
        if errors and not final:
            continue
        # The semantic check (SPEC Layer 7 item 10): on every claim of every attempt that
        # reaches it (the checker is a sample, so a claim that passed before is checked again),
        # each with its finding's derivation alone; and on every tagged summary sentence,
        # against the union of the derivations of the findings it cites. On the last attempt
        # the sentences that passed the validator are checked even if others did not.
        checks = ([(s, ids, data, "summary", None) for s, ids, data in _summary_checks(draft.summary, finding_data)]
                  if not summary_errs else [])
        checks += [(c.text, [c.finding_id], _check_payload(finding_data[c.finding_id]), c.finding_id, name)
                   for name, c in drafted if not claim_errs[(name, c.finding_id)]]
        paragraphs = {d.name: d.paragraph for d in draft.areas if d.paragraph}
        for name, errs in para_errs.items():
            if not errs:
                checks += [(s_, ids, data, f"paragraph:{name}", name)
                           for s_, ids, data in _summary_checks(paragraphs[name], finding_data)]
        progress("check", {"attempt": attempts, "calls": len(checks)})
        # The checks of one attempt are independent: a checker with `check_many` runs them
        # concurrently (AnthropicChecker); any other checker is called one by one.
        if hasattr(checker, "check_many"):
            outcomes = checker.check_many([(sentence, data) for sentence, _, data, _, _ in checks])
        else:
            outcomes = [(checker(sentence, data), getattr(checker, "last_meta", None))
                        for sentence, _, data, _, _ in checks]
        rejected: dict[tuple[str, str] | str, str] = {}
        for (sentence, ids, data, label, name), (result, meta) in zip(checks, outcomes):
            if recording is not None:
                recording.append(dict(meta or {"kind": "checker"},
                                      attempt=attempts, finding_id=label, findings=ids, sentence=sentence,
                                      result=result.model_dump()))
            where = (f"the derivations of {', '.join(ids)} (summary)" if label == "summary"
                     else f"the derivations of {', '.join(ids)} ({label})" if label.startswith("paragraph:")
                     else f"the derivation of {label}")
            for prop in result.propositions:
                if not prop.supported:
                    msg = f"unsupported by {where}: {prop.text!r} ({prop.evidence}) in {sentence!r}"
                    errors.append(msg)
                    rejected.setdefault(label if label == "summary" or label.startswith("paragraph:")
                                        else (name, label), msg)
        for name, c in drafted:
            key = (name, c.finding_id)
            if claim_errs[key]:
                continue
            if key in rejected:
                last_error[key] = (rejected[key], attempts)
            else:
                kept[key] = c
        for name, errs in para_errs.items():
            if not errs:
                if f"paragraph:{name}" in rejected:
                    para_error[name] = (rejected[f"paragraph:{name}"], attempts)
                else:
                    kept_para[name] = paragraphs[name]
        if not summary_errs:
            if "summary" in rejected:
                summary_error = (rejected["summary"], attempts)
            else:
                kept_summary = draft.summary
        if not errors:
            clean = True
            break

    if clean:                                              # the last draft passed every check: it is the reading
        kept = {(name, c.finding_id): c for name, c in drafted}
        kept_summary = draft.summary
        kept_para = {d.name: d.paragraph for d in draft.areas if d.paragraph} if curious else {}

    by_finding = {f["finding_id"]: f for name in areas for f in findings(chart, name, as_of)[0]}
    reading_areas, depends = [], []
    for name in areas:
        a = sc.areas[name]
        conf = a.confidence or 0.0
        offered = findings(chart, name, as_of)[0]
        claims, gaps = [], []
        for f in offered:
            c = kept.get((name, f["finding_id"]))
            if c is None:
                err, at = last_error.get((name, f["finding_id"]), ("no claim was drafted for this finding", attempts))
                gaps.append({"finding_id": f["finding_id"], "kind": f["kind"], "last_error": err, "attempt": at})
                continue
            claims.append(ReadingClaim(finding_id=c.finding_id, text=c.text, cites=[f"{k}:{v}" for k, v in TAG.findall(c.text)],
                                       kind=f["kind"], school=f["school"], basis=f["basis"],
                                       stability=f["stability"], stability_label=_label(f["stability"]),
                                       confidence=f["confidence"], learner=learner_data(f)))
        # SPEC Layer 7 item 4: two groups, rule fires first, then votes, each by stability x the
        # claim's own confidence. The two confidences are on different scales (a rule's is
        # capped at 0.7, a vote's is near 1), so they are never ranked against each other.
        claims.sort(key=lambda c: ({"rule": 0, "vote": 1}.get(c.kind, 2),
                                   -((c.stability if c.stability is not None else 1.0) * (c.confidence or 0.0))))
        _, shaky = findings(chart, name, as_of)
        depends += [({"area": name, "rule": f["rule_id"], "basis": f["basis"], "stability": f["stability"]}
                     if f["kind"] == "rule" else
                     {"area": name, "chain": f["finding_id"], "stability": f["stability"]} if f["kind"] == "chain" else
                     {"area": name, "vote": f["finding_id"], "direction": f["direction"], "stability": f["stability"]})
                    for f in shaky]
        if a.stability is not None and a.stability.time < 0.5:
            depends.append({"area": name, "tier": a.tier, "stability": a.stability.time})
        windows, avoid = [], None
        # Windows only for the areas the question routes to: a job-change question gets career
        # windows, never health or marriage ones; the page's other areas carry none.
        if when and name in AREAS and name in routed:
            q = TimingQuery(area=name, start=as_of, end=as_of + timedelta(days=round(365.25 * config.timing_years)),
                            question=question)
            from .timing import answer
            ans = answer(chart, q)
            windows = [_window(w) for w in ans.windows]
            avoid = _window(ans.avoid) if ans.avoid is not None else None
        top3 = name in sc.top
        paragraph = kept_para.get(name) if curious else None
        if curious and paragraph is None:
            err, at = para_error.get(name, ("no paragraph was drafted for this area", attempts))
            gaps.append({"finding_id": "paragraph", "kind": "paragraph", "last_error": err, "attempt": at})
        disclaimer = DISCLAIMERS["third_party"] if name in THIRD_PARTY_AREAS else (
            DISCLAIMERS[DISCLAIMER_KEYS[name]] if name in DISCLAIMER_KEYS else None)
        reading_areas.append(ReadingArea(
            name=name, score_classical=a.score_classical, tier=a.tier, stability=a.stability,
            families_agree_w=a.families_agree_w, families_total_w=a.families_total_w,
            polarity=a.polarity if top3 else [], polarity_touches=a.polarity_touches if top3 else {},
            claims=claims, school_conflicts=school_conflicts(a), windows=windows, avoid_window=avoid,
            disclaimer=disclaimer, narration_gaps=gaps, paragraph=paragraph,
            other_placements=other_placements(chart, name),
            paragraph_cites=[f"{k}:{v}" for k, v in TAG.findall(paragraph or "")]))

    fired = [{"id": f.id, "basis": f.basis, "scale": round(f.scale, 3), "status": f.status,
              "stability": f.stability.time if f.stability else None}
             for f in chart.fired_rules if in_default(f.status, f.family)]
    unstable = [x for x in fired if x["stability"] is not None and x["stability"] < 0.5]
    disclaimers = sorted({("third_party" if n in THIRD_PARTY_AREAS else DISCLAIMER_KEYS.get(n)) for n in areas} - {None})
    period = None
    vim = [p for p in chart.dashas.get("vimshottari", []) if len(p.lords) == 2]
    from .timing import _jd
    jd_now = _jd(as_of)
    cur = next((p for p in vim if p.start_jd <= jd_now < p.end_jd), None)
    if cur:
        period = "-".join(cur.lords)
    u = chart.uncertainty
    scored = [x for x in fired if x["status"] != "draft"]
    drafts = [x for x in fired if x["status"] == "draft"]
    stable_n = sum(1 for x in scored if x["stability"] is not None and x["stability"] >= 0.5)
    unstable_of = lambda xs: sum(1 for x in xs if x["stability"] is not None and x["stability"] < 0.5)
    lines = [timing_line(a.name, a.windows, a.avoid_window) for a in reading_areas if a.windows]
    when_line = " ".join(x for x in lines if x) or None
    source, text = "model", kept_summary
    if kept_summary is None:
        source = "engine"
        text = engine_summary(reading_areas, routed, sc, period, when_line)
    summary = ReadingSummary(
        timing_line=when_line, source=source,
        timing_note=timing_note([a.name for a in reading_areas if a.windows]) if when_line else None,
        text=text, cites=[f"{k}:{v}" for k, v in TAG.findall(text)],
        driver_planet=sc.driver.driver, driver_alternates=sc.driver.alternates, current_period=period,
        top_areas=list(sc.top), time_window_min=u.half_width_min if u else None,
        stable_findings=stable_n, unstable_findings=unstable_of(scored),
        rules_fired=len(scored), drafts_fired=len(drafts), drafts_unstable=unstable_of(drafts),
        abstained_areas=[n for n, x in sc.areas.items() if x.tier in ("not emphasised", "cannot be assessed",
                                                                   "needs two charts")])
    return Reading(as_of=as_of.isoformat(), weights=sc.weights, engine=chart.meta.engine, question=question,
                   chart=chart_header(chart),
                   model=config.model, attempts=attempts, summary=summary, areas=reading_areas,
                   narration_complete=source == "model" and not any(a.narration_gaps for a in reading_areas),
                   depth=depth,
                   fired_rules=fired, unstable=unstable, depends_on_birth_time=depends, disclaimers=disclaimers)
