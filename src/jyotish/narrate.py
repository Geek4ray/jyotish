"""Layer 7: narration. `narrate(chart, question)` returns a Reading in the SPEC Layer 7
output schema.

The engine decides every fact; the language model only writes sentences about findings
the engine hands it. What the engine owns, in code:
  - which findings are narrated: non-experimental fired rules that map to the area, with
    time-stability >= 0.5; those below 0.5, and areas below 0.5, go to
    `depends_on_birth_time` instead;
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
    effort: str = "medium"                    # Opus 5.5's default, set explicitly
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
    text: str
    cites: list[str]
    school: str
    basis: str
    stability: float | None


class ReadingWindow(BaseModel):
    kind: str = "dasha+transit"
    start: str
    end: str
    score: float
    confidence: str | None
    stability: float | None             # edge movement over the time samples, in days
    sandhi: bool
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

TAG = re.compile(r"\[(rule|text):([^\]\s]+)\]")
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
    "trade": re.compile(r"\b(buy|sell|invest(?:ing|ment)? in|stocks?|shares|crypto\w*|trading|trade|"
                        r"portfolio|securities)\b", re.I),
    "third_party": re.compile(r"\b(mother|father|parents?|partner|spouse|wife|husband|child|children|son|"
                              r"daughter|sibling|brother|sister)s?(?:'s)?\s+(?:\w+\s+){0,2}"
                              r"(will|is going to|shall|would|must|has to|gets?|suffers?)\b", re.I),
}


def sentences(text: str) -> list[str]:
    """Split prose into sentences, keeping trailing tags with the sentence they end."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])|(?<=\])\s+(?=[A-Z])", text.strip())
    return [p.strip() for p in parts if p.strip()]


def validate(text: str, allowed: set[str]) -> list[str]:
    """Every violation in a block of model text, as human-readable errors."""
    errors = []
    for s in sentences(text):
        bare = TAG.sub("", s)
        tags = {f"{k}:{v}" for k, v in TAG.findall(s)}
        if CLAIM_VERBS.search(bare) and not tags:
            errors.append(f"untagged claim: {s!r}")
        for t in tags - allowed:
            errors.append(f"tag not offered for this finding: [{t}] in {s!r}")
        if tags and not re.search(r"\]\s*[.!?]?\s*$", s):
            errors.append(f"tags must end the sentence: {s!r}")
        for kind, rx in FORBIDDEN.items():
            m = rx.search(bare)
            if m:
                errors.append(f"{kind} language ({m.group(0)!r}) in {s!r}")
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


def findings(chart: Chart, area: str) -> tuple[list[dict], list[dict]]:
    """(narratable, depends-on-birth-time) findings for an area: the non-experimental fired
    rules whose themes map to it, split at time-stability 0.5."""
    lib = {r.id: r for r in default_rules()}
    ok, shaky = [], []
    for f in chart.fired_rules:
        if f.status == "experimental" or not any(area in THEME_AREAS.get(t, []) for t in f.themes):
            continue
        rule = lib.get(f.id)
        tags = [f"rule:{f.id}"] + [_text_tag(s) for s in (rule.data.get("source", []) if rule else [])
                                   if s.get("checked")]
        item = {"finding_id": f"{f.id}@{f.basis}", "rule_id": f.id, "basis": f.basis, "school": f.school,
                "nodes": f.nodes, "scale": round(f.scale, 3), "themes": {k: round(v, 2) for k, v in f.themes.items()},
                "modifiers_applied": f.applied, "details": f.details, "allowed_tags": tags,
                "stability": f.stability.time if f.stability else None}
        (shaky if f.stability is not None and f.stability.time < 0.5 else ok).append(item)
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
engine has already computed. You add no facts. Every finding you are given has an id, the rule \
that fired, the planets and houses it involves, and the citation tags you may use.

Write, for each area, one claim per finding, in the order given. Each claim narrates that finding \
only and ends with one or more of that finding's allowed tags, written exactly, for example \
[rule:yoga.ruchaka] or [text:BPHS/Santhanam-1984/75/1-2]. Put the tags at the very end of the \
sentence. Also write a two- or three-sentence summary answering the question; each summary \
sentence that states something ends with a tag from the findings.

The engine states the confidence tier, the stability and any timing windows itself, so do not \
write confidence words (certain, definitely, guaranteed), probabilities or percentages, and do not \
restate the tier. Never write about death or its timing, medical conditions, or buying and selling \
investments. For relationships (mother, father, partner, children, siblings), describe only what \
this chart shows about the relationship, never what will happen to the other person."""


def payload(chart: Chart, question: str, areas: list[str]) -> tuple[str, dict[str, set[str]]]:
    """The user message for the model, and the tags allowed per finding id."""
    allowed: dict[str, set[str]] = {}
    body = {"question": question, "areas": []}
    for name in areas:
        a = chart.scored.areas[name]
        ok, _ = findings(chart, name)
        for f in ok:
            allowed[f["finding_id"]] = set(f["allowed_tags"])
        body["areas"].append({"name": name, "findings": ok})
    return json.dumps(body, indent=1, default=str), allowed


# --- the model call ----------------------------------------------------------------------

Drafter = Callable[[str, str, list[str]], ReadingDraft]


class AnthropicDrafter:
    """Calls the Messages API with structured output. Keeps the conversation append-only
    across regenerations (each failed draft and its errors stay in the history)."""

    def __init__(self, config: NarrationConfig = CONFIG, client=None):
        import anthropic
        self.config = config
        self.client = client or anthropic.Anthropic()
        self.messages: list[dict] = []

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
        if response.stop_reason == "refusal":
            raise NarrationError("the model declined the request", [str(getattr(response, "stop_details", ""))])
        self.messages.append({"role": "assistant", "content": response.content})
        if response.parsed_output is None:
            raise NarrationError("no structured output in the response", [response.stop_reason or ""])
        return response.parsed_output


# --- assembly ----------------------------------------------------------------------------

def _date_str(jd: float) -> str:
    import swisseph as swe
    y, m, d, _ = swe.revjul(jd, swe.GREG_CAL)
    return f"{y:04d}-{m:02d}-{d:02d}"


def narrate(chart: Chart, question: str, *, drafter: Drafter | None = None, as_of: date | None = None,
            config: NarrationConfig = CONFIG) -> Reading:
    if chart.scored is None:
        raise ValueError("narration needs a scored chart (birth moment, Shadbala, Bhava Bala)")
    as_of = as_of or date.today()
    sc = chart.scored
    areas, when = route(question, chart)
    user, allowed = payload(chart, question, areas)
    all_tags = set().union(*allowed.values()) if allowed else set()
    drafter = drafter or AnthropicDrafter(config)

    draft, errors, attempts = None, [], 0
    for attempts in range(1, config.max_attempts + 1):
        draft = drafter(SYSTEM_PROMPT, user, errors)
        errors = validate(draft.summary, all_tags)
        for da in draft.areas:
            if da.name not in areas:
                errors.append(f"area not asked for: {da.name}")
            for c in da.claims:
                if c.finding_id not in allowed:
                    errors.append(f"unknown finding id {c.finding_id!r}")
                    continue
                errors += validate(c.text, allowed[c.finding_id])
                if not TAG.search(c.text):
                    errors.append(f"claim without a tag: {c.text!r}")
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
            claims.append(ReadingClaim(text=c.text, cites=[f"{k}:{v}" for k, v in TAG.findall(c.text)],
                                       school=f["school"], basis=f["basis"], stability=f["stability"]))
        claims.sort(key=lambda c: -((c.stability if c.stability is not None else 1.0) * conf))
        _, shaky = findings(chart, name)
        depends += [{"area": name, "rule": f["rule_id"], "basis": f["basis"], "stability": f["stability"]} for f in shaky]
        if a.stability is not None and a.stability.time < 0.5:
            depends.append({"area": name, "tier": a.tier, "stability": a.stability.time})
        windows = []
        if when and name in AREAS:
            q = TimingQuery(area=name, start=as_of, end=as_of + timedelta(days=round(365.25 * config.timing_years)),
                            question=question)
            from .timing import answer
            ans = answer(chart, q)
            for w in ans.windows:
                windows.append(ReadingWindow(
                    start=_date_str(w.start_jd), end=_date_str(w.end_jd), score=round(w.joint, 3),
                    confidence=w.confidence,
                    stability=(w.stability or {}).get("time_range_days"),
                    sandhi="dasha_sandhi" in w.tags,
                    why=[{"kind": "dasha", "system": s, "lords": l} for s, l in w.periods.items()]
                    + [{"kind": "transit", "activation": round(w.transit_activation, 3)}]))
        top3 = name in sc.top
        disclaimer = DISCLAIMERS["third_party"] if name in THIRD_PARTY_AREAS else (
            DISCLAIMERS[DISCLAIMER_KEYS[name]] if name in DISCLAIMER_KEYS else None)
        reading_areas.append(ReadingArea(
            name=name, score_classical=a.score_classical, tier=a.tier, stability=a.stability,
            families_agree_w=a.families_agree_w, families_total_w=a.families_total_w,
            polarity=a.polarity if top3 else [], polarity_touches=a.polarity_touches if top3 else {},
            claims=claims, school_conflicts=school_conflicts(a), windows=windows, disclaimer=disclaimer))

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
                   model=config.model, attempts=attempts, summary=summary, areas=reading_areas,
                   fired_rules=fired, unstable=unstable, depends_on_birth_time=depends, disclaimers=disclaimers)
