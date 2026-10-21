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
from typing import Any, Callable

from pydantic import BaseModel, Field

from .models import Chart, Stability, TimingQuery
from .rules import default_rules
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


class ReadingDraft(BaseModel):
    summary: str = Field(description="Two or three tagged sentences answering the question.")
    areas: list[DraftArea]


# --- the reading (SPEC Layer 7 output schema) ------------------------------------------

class ReadingClaim(BaseModel):
    finding_id: str
    text: str
    cites: list[str]
    kind: str                           # rule | vote
    school: str
    basis: str
    stability: float | None
    confidence: float                   # rule: scale x confidence_base; vote: min(1, 1 - rho) x |vote|


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


class ReadingSummary(BaseModel):
    text: str
    cites: list[str]
    driver_planet: str
    driver_alternates: list[str]
    current_period: str | None
    top_areas: list[str]
    time_window_min: float | None
    stable_findings: int
    unstable_findings: int
    abstained_areas: list[str]


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

TAG = re.compile(r"\[(rule|text|vote):([^\]\s]+)\]")
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
    "medical": re.compile(r"\b(diagnos\w*|cancer|diabetes|tumou?r|disorder|syndrome|prescri\w*|"
                          r"medication|surgery)\b", re.I),
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


# A sentence "names" a family (SPEC Layer 7 item 11). Distinctive words count anywhere; the
# ordinary words "house" and "lord" count only when the sentence speaks of a vote or family
# with them, or (house) names Bhava Bala. "marana karaka" is a placement, not the family.
FAMILY_WORDS = {
    "house": re.compile(r"\bhouses?\b[^.\[]*\b(votes?|famil(?:y|ies))\b|\bbhava bala\b", re.I),
    "lord": re.compile(r"\blords?\b[^.\[]*\b(votes?|famil(?:y|ies))\b", re.I),
    "karaka": re.compile(r"(?<!marana )\bkarakas?\b", re.I),
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


def validate(text: str, allowed: set[str], *, offered_votes: dict[str, str | set[str]] | None = None) -> list[str]:
    """Every violation in a block of model text, as human-readable errors. `allowed` is the
    set of tags this text may carry; `offered_votes` maps family -> vote tag (or, for a
    summary over several areas, the set of that family's vote tags) for every vote offered:
    a sentence naming such a family must cite it (one of them)."""
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
        for kind, value in found:
            if kind == "vote":
                family = value.split(".", 1)[-1]
                if family not in named:
                    errors.append(f"[vote:{value}] on a sentence that does not name the {family} family: {s!r}")
            elif kind == "rule":
                if not any(n.lower() in bare.lower() for n in rule_names(value)):
                    errors.append(f"[rule:{value}] on a sentence that names none of {rule_names(value)}: {s!r}")
        for family in sorted(named):
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


def findings(chart: Chart, area: str) -> tuple[list[dict], list[dict]]:
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
    a vote's family weight min(1, 1 - rho) x |vote|."""
    from .scoring import family_rho
    lib = {r.id: r for r in default_rules()}
    ok, shaky = [], []
    groups: dict[tuple, list] = {}
    for f in chart.fired_rules:
        if f.status == "experimental" or not any(area in THEME_AREAS.get(t, []) for t in f.themes):
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
                           "cited_to": "rule" if f.basis != "lagna" else "rule and text",
                           "nodes": f.nodes, "scale": round(f.scale, 3),
                           "modifiers_applied": f.applied, "modifiers_unknown": f.unknown, "details": f.details,
                           "stability": f.stability.time if f.stability else None} for f in fires],
                "allowed_tags": tags, "stability": min(times) if times else None,
                "confidence": min(f.scale for f in fires) * base}
        (shaky if unstable else ok).append(item)
    a = chart.scored.areas.get(area)
    if a is not None and a.score_classical is not None:
        from .scoring import family_weights
        rho = family_rho(chart.meta.varga_term, chart.meta.kp_vote)
        weights = family_weights(a, rho)
        for family, vote in a.votes.items():
            if not vote:
                continue
            tag = f"vote:{area}.{family}"
            item = {"finding_id": tag, "kind": "vote", "family": family, "vote": vote,
                    "direction": "for" if vote > 0 else "against", "basis": "lagna, moon, sun 3:2:1"
                    if family in ("house", "lord") else "lagna", "school": FAMILY_SCHOOL[family],
                    "derivation": a.vote_details.get(family), "term": a.terms.get(family),
                    "allowed_tags": [tag], "stability": a.vote_stability.get(family),
                    "confidence": min(1.0, weights[family]) * abs(vote)}
            st = item["stability"]
            (shaky if st is not None and st < 0.5 else ok).append(item)
    return ok, shaky


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
lagna and from the Sun").

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
this chart shows about the relationship, never what will happen to the other person."""


def payload(chart: Chart, question: str, areas: list[str]) -> tuple[str, dict[str, set[str]]]:
    """The user message for the model, and the tags allowed per finding id."""
    allowed: dict[str, set[str]] = {}
    body = {"question": question, "areas": []}
    for name in areas:
        ok, _ = findings(chart, name)
        for f in ok:
            allowed[f["finding_id"]] = set(f["allowed_tags"])
        body["areas"].append({"name": name, "findings": ok})
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
area says so. Ignore the bracketed citation tags."""


def _meta(response, kind: str, effort: str) -> dict:
    from datetime import datetime, timezone
    usage = getattr(response, "usage", None)
    return {"kind": kind, "request_id": getattr(response, "_request_id", None),
            "model": getattr(response, "model", None), "effort": effort,
            "usage": usage.model_dump() if hasattr(usage, "model_dump") else usage,
            "stop_reason": getattr(response, "stop_reason", None),
            "timestamp": datetime.now(timezone.utc).isoformat()}


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
        cfg = self.config
        response = self.client.beta.messages.parse(
            model=cfg.model, max_tokens=cfg.max_tokens, betas=list(cfg.betas), fallbacks=cfg.fallbacks,
            output_config={"effort": cfg.effort}, system=system, messages=self.messages,
            output_format=ReadingDraft)
        self.last_meta = _meta(response, "writer", cfg.effort)
        if response.stop_reason == "refusal":
            raise NarrationError("the model declined the request", [str(getattr(response, "stop_details", ""))])
        self.messages.append({"role": "assistant", "content": response.content})
        if response.parsed_output is None:
            raise NarrationError("no structured output in the response", [response.stop_reason or ""])
        return response.parsed_output


class AnthropicChecker:
    """The semantic checker (SPEC Layer 7 item 10): one structured call per sentence with only
    the sentence and the derivation it may draw on (a claim's finding; for a summary sentence,
    the findings it cites). Same model and config block as the writer, at `checker_effort`."""

    def __init__(self, config: NarrationConfig = CONFIG, client=None):
        import anthropic
        self.config = config
        self.client = client or anthropic.Anthropic()
        self.last_meta: dict | None = None

    def __call__(self, sentence: str, derivation: str) -> CheckResult:
        cfg = self.config
        response = self.client.beta.messages.parse(
            model=cfg.model, max_tokens=cfg.max_tokens, betas=list(cfg.betas), fallbacks=cfg.fallbacks,
            output_config={"effort": cfg.checker_effort}, system=CHECKER_PROMPT,
            messages=[{"role": "user", "content": f"Sentence:\n{sentence}\n\nData:\n{derivation}"}],
            output_format=CheckResult)
        self.last_meta = _meta(response, "checker", cfg.checker_effort)
        if response.stop_reason == "refusal" or response.parsed_output is None:
            raise NarrationError("the checker returned no result", [response.stop_reason or ""])
        return response.parsed_output


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


def _check_payload(f: dict) -> str:
    """What the checker sees for one finding: its derivation and nothing else."""
    return json.dumps(_check_data(f), indent=1, default=str)


def _check_data(f: dict) -> dict:
    keep = ("finding_id", "kind", "rule_id", "family", "direction", "basis", "bases", "sudarshana_bases",
            "school", "planets",
            "themes", "fires", "derivation")
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
            recording: list | None = None, areas: list[str] | None = None) -> Reading:
    """`areas` overrides the routed areas (the question's "when" is still read from it)."""
    if chart.scored is None:
        raise ValueError("narration needs a scored chart (birth moment, Shadbala, Bhava Bala)")
    as_of = as_of or date.today()
    sc = chart.scored
    routed, when = route(question, chart)
    areas = list(areas) if areas is not None else routed
    user, allowed = payload(chart, question, areas)
    all_tags = set().union(*allowed.values()) if allowed else set()
    drafter = drafter or AnthropicDrafter(config)
    checker = checker or AnthropicChecker(config)
    votes_offered = offered_votes(chart, areas)
    finding_data = {f["finding_id"]: f for name in areas for f in findings(chart, name)[0]}
    all_votes: dict[str, set[str]] = {}
    for name in areas:
        for fam, tag in votes_offered[name].items():
            all_votes.setdefault(fam, set()).add(tag)

    draft, errors, attempts = None, [], 0
    for attempts in range(1, config.max_attempts + 1):
        draft = drafter(SYSTEM_PROMPT, user, errors)
        entry = dict(getattr(drafter, "last_meta", None) or {"kind": "writer"}, attempt=attempts,
                     draft=draft.model_dump())
        errors = validate(draft.summary, all_tags, offered_votes=all_votes)
        for da in draft.areas:
            if da.name not in areas:
                errors.append(f"area not asked for: {da.name}")
                continue
            for c in da.claims:
                if c.finding_id not in allowed:
                    errors.append(f"unknown finding id {c.finding_id!r}")
                    continue
                errors += validate(c.text, allowed[c.finding_id], offered_votes=votes_offered[da.name])
                if not TAG.search(c.text):
                    errors.append(f"claim without a tag: {c.text!r}")
        entry["validator_errors"] = list(errors)
        if recording is not None:
            recording.append(entry)
        if errors:
            continue
        # The semantic check (SPEC Layer 7 item 10): after the validator passes, on every claim
        # of every attempt (the checker is a sample, so a claim that passed before is checked
        # again), each with its finding's derivation alone; and on every tagged summary
        # sentence, against the union of the derivations of the findings it cites.
        checks = [(s, ids, data, "summary") for s, ids, data in _summary_checks(draft.summary, finding_data)]
        checks += [(c.text, [c.finding_id], _check_payload(finding_data[c.finding_id]), c.finding_id)
                   for da in draft.areas for c in da.claims]
        for sentence, ids, data, label in checks:
            result = checker(sentence, data)
            if recording is not None:
                recording.append(dict(getattr(checker, "last_meta", None) or {"kind": "checker"},
                                      attempt=attempts, finding_id=label, findings=ids, sentence=sentence,
                                      result=result.model_dump()))
            where = (f"the derivations of {', '.join(ids)} (summary)" if label == "summary"
                     else f"the derivation of {label}")
            for prop in result.propositions:
                if not prop.supported:
                    errors.append(f"unsupported by {where}: {prop.text!r} ({prop.evidence}) in {sentence!r}")
        if not errors:
            break
    else:
        raise NarrationError(f"the draft failed validation {config.max_attempts} times", errors)

    by_finding = {f["finding_id"]: f for name in areas for f in findings(chart, name)[0]}
    reading_areas, depends = [], []
    for name in areas:
        a = sc.areas[name]
        conf = a.confidence or 0.0
        drafted = next((d for d in draft.areas if d.name == name), DraftArea(name=name, claims=[]))
        claims = []
        for c in drafted.claims:
            f = by_finding[c.finding_id]
            claims.append(ReadingClaim(finding_id=c.finding_id, text=c.text, cites=[f"{k}:{v}" for k, v in TAG.findall(c.text)],
                                       kind=f["kind"], school=f["school"], basis=f["basis"],
                                       stability=f["stability"], confidence=f["confidence"]))
        # SPEC Layer 7 item 4: two groups, rule fires first, then votes, each by stability x the
        # claim's own confidence. The two confidences are on different scales (a rule's is
        # capped at 0.7, a vote's is near 1), so they are never ranked against each other.
        claims.sort(key=lambda c: (c.kind != "rule",
                                   -((c.stability if c.stability is not None else 1.0) * c.confidence)))
        _, shaky = findings(chart, name)
        depends += [({"area": name, "rule": f["rule_id"], "basis": f["basis"], "stability": f["stability"]}
                     if f["kind"] == "rule" else
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
        disclaimer = DISCLAIMERS["third_party"] if name in THIRD_PARTY_AREAS else (
            DISCLAIMERS[DISCLAIMER_KEYS[name]] if name in DISCLAIMER_KEYS else None)
        reading_areas.append(ReadingArea(
            name=name, score_classical=a.score_classical, tier=a.tier, stability=a.stability,
            families_agree_w=a.families_agree_w, families_total_w=a.families_total_w,
            polarity=a.polarity if top3 else [], polarity_touches=a.polarity_touches if top3 else {},
            claims=claims, school_conflicts=school_conflicts(a), windows=windows, avoid_window=avoid,
            disclaimer=disclaimer))

    fired = [{"id": f.id, "basis": f.basis, "scale": round(f.scale, 3),
              "stability": f.stability.time if f.stability else None}
             for f in chart.fired_rules if f.status != "experimental"]
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
    stable_n = sum(1 for x in fired if x["stability"] is not None and x["stability"] >= 0.5)
    summary = ReadingSummary(
        text=draft.summary, cites=[f"{k}:{v}" for k, v in TAG.findall(draft.summary)],
        driver_planet=sc.driver.driver, driver_alternates=sc.driver.alternates, current_period=period,
        top_areas=list(sc.top), time_window_min=u.half_width_min if u else None,
        stable_findings=stable_n, unstable_findings=len(unstable),
        abstained_areas=[n for n, x in sc.areas.items() if x.tier in ("not emphasised", "cannot be assessed",
                                                                   "needs two charts")])
    return Reading(as_of=as_of.isoformat(), weights=sc.weights, engine=chart.meta.engine, question=question,
                   chart=chart_header(chart),
                   model=config.model, attempts=attempts, summary=summary, areas=reading_areas,
                   fired_rules=fired, unstable=unstable, depends_on_birth_time=depends, disclaimers=disclaimers)
