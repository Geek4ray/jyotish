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
from .rules import HOUSE_PLACEMENTS, NAKSHATRA_PLACEMENTS, PLACEMENT_FAMILIES, default_rules, in_default
from .scoring import AREAS, THEME_AREAS


# --- the one config ------------------------------------------------------------------

@dataclass(frozen=True)
class NarrationConfig:
    model: str = "claude-opus-5-5"            # the writer (jyotish read --writer-model)
    max_tokens: int = 16000
    effort: str = "medium"                    # the writer; Opus 5.5's default, set explicitly
    checker_model: str = "claude-opus-5-5"    # the gate stays fixed when the writer's model is changed
    checker_effort: str = "high"              # the checker is the gate (SPEC Layer 7 item 10)
    fallbacks: str = "default"                # server-side refusal fallback, routed by category
    betas: tuple[str, ...] = ("server-side-fallback-2026-07-01",)
    max_attempts: int = 3                     # draft + regenerations on validator failure
    checker_concurrency: int = 16             # checker calls of one attempt in flight at once; 1 = one after another
    timing_years: int = 10                    # window for a "when" question with no dates; at depth full, the range always
    thinking: str | None = None               # the writer's `thinking` type; None sends none (Opus 5.5 thinks adaptively anyway)
    thinking_display: str = "summarized"      # a summary of the writer's reasoning, kept in the recording only
    # Depth full (SPEC Layer 7, depth full): extended thinking on, effort xhigh (max stays available by
    # --writer-effort: at max, reading B's first attempt thought through all 128,000 output tokens and
    # returned no draft) and room for the reasoning and the analysis. A max_tokens above STREAM_ABOVE
    # is sent as a stream (the SDK refuses a long request otherwise). When thinking reaches max_tokens
    # with no draft, the next attempt runs one effort level lower (narrate records it).
    full_thinking: str = "adaptive"
    full_effort: str = "xhigh"
    full_max_tokens: int = 128000
    # Depth full: every unit (the summary, a claim, a section) that passes the validator is checked in
    # the same attempt and held once it passes; a retry asks only for the units that failed, with
    # their reasons, and a held unit is never rewritten. False: the whole draft every time.
    section_retries: bool = True


CONFIG = NarrationConfig()
STREAM_ABOVE = 16000
EFFORTS = ("low", "medium", "high", "xhigh", "max")
# The writers a request may name (POST /readings, --writer-model): each takes adaptive thinking,
# the five efforts and the server-side fallback.
WRITER_MODELS = ("claude-opus-5-5", "claude-fable-5-1", "claude-opus-5", "claude-sonnet-5-5")


def writer_config(config: NarrationConfig, depth: str, model: str | None = None,
                  effort: str | None = None) -> NarrationConfig:
    """The writer's settings for a depth: at full, extended thinking (`full_thinking`), `full_effort`
    (xhigh) and `full_max_tokens`; `model` and `effort` override at any depth (the
    --writer-model and --writer-effort flags). The checker's model and effort are not touched."""
    from dataclasses import replace
    if model is not None and model not in WRITER_MODELS:
        raise ValueError(f"writer model must be one of {WRITER_MODELS}, not {model!r}")
    if effort is not None and effort not in EFFORTS:
        raise ValueError(f"writer effort must be one of {EFFORTS}, not {effort!r}")
    full = depth == "full"
    return replace(config, model=model or config.model,
                   effort=effort or (config.full_effort if full else config.effort),
                   thinking=config.full_thinking if full else config.thinking,
                   max_tokens=config.full_max_tokens if full else config.max_tokens)


# --- what the model returns ------------------------------------------------------------

class DraftClaim(BaseModel):
    finding_id: str = Field(description="The id of the finding this sentence narrates, from the input.")
    text: str = Field(description="One or two sentences; every claim sentence ends with its tags, "
                                  "e.g. 'Mars in its own sign in the 7th forms Ruchaka yoga [rule:yoga.ruchaka].'")


class DraftAnalysis(BaseModel):
    # Null on a retry for a section that passed and is held.
    assessment: str | None = Field(default=None, description=(
        "The evidence for and against the area weighed: the strongest and the weakest support, every "
        "contradiction between families resolved explicitly, and what matters most ranked. Every sentence "
        "ends with the tags of the findings and facts it rests on. Null when the section is held."))
    timing: str | None = Field(default=None, description=(
        "The area's periods, windows and transits, every date and period cited to its fact. Null when held."))
    not_said: str | None = Field(default=None, description=(
        "What this chart does not say about the area, each statement cited. Null when held."))


ANALYSIS_SECTIONS = ("assessment", "timing", "not_said")


class DraftArea(BaseModel):
    name: str
    claims: list[DraftClaim]
    paragraph: str | None = Field(default=None, description=(
        "Curious depth only: one short plain-language paragraph about the area, every sentence ending "
        "with the tags of the findings it draws on. Null at the other depths."))
    analysis: DraftAnalysis | None = Field(default=None, description="Full depth only; null at the other depths.")


class ReadingDraft(BaseModel):
    summary: str = Field(description="Two or three tagged sentences answering the question; empty on a retry "
                                     "when the summary is held.")
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
    # Depth full: the checked sections (assessment, timing, not_said -> text), each accepted whole,
    # the latest version in which every sentence passed; a section that never did is a narration gap.
    analysis: dict[str, str] | None = None
    analysis_cites: list[str] = Field(default_factory=list)
    # Depth full: the [tradition:] sentences, taken out of the sections they were written in:
    # {section, sentence, citation, text, chapter, verse, checked: false, note}. Never checked, shown
    # apart under "from the texts, not computed on this chart", recorded as candidate rules.
    traditions: list[dict[str, Any]] = Field(default_factory=list)
    # Depth full: the sentences of the analysis that weigh ({section, sentence}), shown as the
    # reading's weighing; their premises were checked, their weighing never is.
    judgements: list[dict[str, str]] = Field(default_factory=list)


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
    depth: str = "astrologer"           # curious | learner | astrologer | full (SPEC Layer 7 prompt contract, item 1)
    facts_cited: dict[str, Any] = Field(default_factory=dict)   # depth full: path -> the chart's value, for every [fact:] shown
    # The writer's and the checker's settings as run ({model, effort, thinking, max_tokens}; {model,
    # effort}), the token usage of each side and the narration's wall time; empty on readings made
    # before them.
    writer: dict[str, Any] = Field(default_factory=dict)
    checker: dict[str, Any] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    synthesis_sentences: int = 0        # depth full: sentences shown that rest on two or more findings or facts
    judgement_sentences: int = 0        # depth full: sentences shown that weigh (premises checked, weighing not)
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

TAG = re.compile(r"\[(rule|text|vote|chain|fact):([^\]\s]+)\]")
# Depth full: a classical text the rule library does not hold, as [tradition:<text> <chapter>]. Never
# checked, never counted as checked, shown apart and recorded as a candidate rule (SPEC Layer 7, depth full).
TRADITION = re.compile(r"\[tradition:([^\]]*)\]")
TRADITION_TEXTS = {"bphs": "BPHS", "brihat parashara hora shastra": "BPHS", "phaladeepika": "Phaladeepika",
                   "saravali": "Saravali", "brihat jataka": "Brihat Jataka", "jataka parijata": "Jataka Parijata",
                   "uttara kalamrita": "Uttara Kalamrita", "jaimini sutras": "Jaimini Sutras",
                   "tajaka neelakanthi": "Tajaka Neelakanthi"}      # the classical texts of the SPEC's corpus
CITATION = re.compile(r"^(?P<text>[A-Za-z][A-Za-z ]*?)\s+(?P<chapter>\d{1,3})(?:[.:](?P<verse>\d{1,3}(?:-\d{1,3})?))?$")
TRADITION_NOTE = ("Unverified: the engine has not checked this against the chart or against the verse, and it "
                  "weighs nothing in any score.")
# What a [tradition:] sentence may not state: anything the engine computes, which must cite a fact.
TRADITION_LIMITS = {
    "numeral": re.compile(r"\d"),
    "degree": re.compile(r"°|\bdegrees?\b", re.I),
    # "may" is left out: the month is far rarer in a classical paraphrase than the verb.
    "date": re.compile(r"\b(january|february|march|april|june|july|august|september|october|november|december|"
                       r"years?|months?|weeks?|aged?)\b", re.I),
    "dasha, period or transit": re.compile(r"\b(dashas?|mahadashas?|antardashas?|bhuktis?|pratyantar\w*|periods?|"
                                           r"sub-periods?|transits?|transiting|gochara|sade sati|windows?|timing)\b", re.I),
    "strength word": re.compile(r"\b(?:strong\w*|strength\w*|weak\w*|powerful|powerless|feeble|afflict\w*)\b", re.I),
    "figure the engine computes": re.compile(r"\b(shadbala|bhava bala|rupas?|virupas?|bindus?|ashtakavarga|sav|bav|"
                                             r"scores?|tiers?|votes?|stability|ratios?|vimsopaka|ishta|kashta|"
                                             r"sub-lords?|cusps?)\b", re.I),
    "statement about this chart": re.compile(r"\b(this|your|the) (chart|horoscope|nativity|reading)\b|"
                                             r"\byou(r|rs)?\b|\bhere\b", re.I),
}


def tradition_citation(value: str) -> dict | None:
    """'Phaladeepika 10' -> {text, chapter, verse} (the text's name as the engine writes it), or None."""
    m = CITATION.match(value.strip())
    if m is None or m["text"].strip().lower() not in TRADITION_TEXTS:
        return None
    return {"text": TRADITION_TEXTS[m["text"].strip().lower()], "chapter": m["chapter"], "verse": m["verse"]}


ORDINAL_WORDS = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh", 8: "eighth",
                 9: "ninth", 10: "tenth", 11: "eleventh", 12: "twelfth"}


def tradition_errors(sentence: str, allowed: bool, facts: dict | None = None) -> list[str]:
    """A [tradition:] sentence's limits: in the analysis at depth full only, one citation of a
    classical text by chapter, no other tag, nothing the engine computes (TRADITION_LIMITS), and
    nothing of this chart's own configuration (review F6): a planet named with the sign or the
    house (as a word: "the seventh") it has on this chart, or this chart's rising sign named as
    rising. Such a sentence describes this chart under a text's name; the placement is a fact to
    cite in a sentence of its own."""
    cites = TRADITION.findall(sentence)
    if not cites:
        return []
    if not allowed:
        return [f"a [tradition:] sentence belongs in the analysis at depth full: {sentence!r}"]
    errors = []
    if TAG.search(sentence):
        errors.append(f"a [tradition:] sentence carries no other tag: it is never checked, so a fact it rests on "
                      f"goes in a sentence of its own: {sentence!r}")
    for c in cites:
        m = CITATION.match(c.strip())
        if m is None:
            errors.append(f"a [tradition:] citation is '<text> <chapter>' (a chapter number, optionally .verse), "
                          f"not {c!r}: {sentence!r}")
        elif m["text"].strip().lower() not in TRADITION_TEXTS:
            errors.append(f"{m['text'].strip()!r} is not a classical text the engine names "
                          f"({', '.join(sorted(set(TRADITION_TEXTS.values())))}): {sentence!r}")
    bare = TRADITION.sub("", sentence)
    for what, rx in TRADITION_LIMITS.items():
        if (m := rx.search(bare)):
            errors.append(f"a [tradition:] sentence states no {what} ({m.group(0)!r}): that is the engine's, "
                          f"said in a sentence citing a fact: {sentence!r}")
    planets = (facts or {}).get("planets") or {}
    for p, row in planets.items():
        if not re.search(rf"\b{p}\b", bare):
            continue
        house = ORDINAL_WORDS.get(row.get("house"))
        for what, word in (("sign", row.get("sign")), ("house", house)):
            if word and re.search(rf"\b{word}\b", bare, re.I):
                errors.append(f"a [tradition:] sentence names {p} with the {what} it has on this chart ({word}): that "
                              f"describes this chart, whose placement is a fact to cite in a sentence of its own "
                              f"(planets.{p}): {sentence!r}")
                break
    rising = (((facts or {}).get("lagnas") or {}).get("asc") or {}).get("sign")
    if rising and re.search(rf"\b{rising}\b[^.;]*\b(rising|ascendant|lagna)\b|\b(rising|ascendant|lagna)\b[^.;]*\b{rising}\b",
                            bare, re.I):
        errors.append(f"a [tradition:] sentence names this chart's rising sign ({rising}): cite lagnas.asc in a "
                      f"sentence of its own: {sentence!r}")
    return errors
CLAIM_VERBS = re.compile(
    r"\b(is|are|was|were|has|have|gives|give|shows|show|indicates|indicate|suggests|suggest|"
    r"brings|bring|forms|form|makes|make|supports|support|favours|favors|promises|denotes|"
    r"signifies|strengthens|weakens|rules|occupies|aspects|activates|marks|points|will|"
    r"can|may|tends|tend|means|leads|lead|sits|sit|lies|holds|hold|places|place)\b", re.I)
# An age is timing as a year is (review F1: "after forty" passed the timing filter).
AGE = (r"\b(?:after|before|by|until|around|about|near|at|past|from|over|under)\s+(?:the\s+age\s+of\s+)?"
       r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\b|\bage(?:d)?\s+(?:of\s+)?\d+|"
       r"\b(?:twenties|thirties|forties|fifties|sixties|seventies|eighties)\b|"
       r"\b(?:after|before|by|until|around|at)\s+\d{2}\b")
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
                         r"december)\b|\b(?:19|20)\d{2}\b|" + AGE, re.I),
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
                     family_rule: bool = True, chains: dict[str, list[str]] | None = None,
                     facts: dict | None = None, traditions: bool = False, judgements: bool = False) -> list[str]:
    """`validate`, plus: no tier word (strong, moderate, weak, mixed) in the summary, or in a
    curious-depth paragraph (`where` names which, in the error)."""
    errors = validate(text, allowed, offered_votes=offered_votes, family_rule=family_rule, chains=chains, standalone=False,
                      facts=facts, traditions=traditions, judgements=judgements)
    for sentence in sentences(text):
        m = TIER_WORDS.search(TRADITION.sub("", TAG.sub("", sentence)))
        if m:
            errors.append(f"tier language ({m.group(0)!r}) in the {where}; the engine states the tier: {sentence!r}")
    return errors


CHAIN_KINDS = re.compile(r"\b(signs?|nakshatras?|navamsas?)\b", re.I)
# Depth full: a ranking of the area's families is the engine's (fullchart.contributions), so a
# sentence that names the strongest support or the weakest point cites it, never its own ranking.
# Depth full: a sentence that weighs ("I weigh …", "I give more weight to … than …", "I read … as
# …", "I resolve … toward …") is the reading's judgement: its premises are checked, its weighing is
# shown as the reading's and never checked (SPEC Layer 7, depth full).
JUDGEMENT = re.compile(r"\bI (?:weigh|resolve)\b|\bI give\b[^.;]*\bweight\b|\bI read\b[^.;]*\bas\b")
# "the 10th sign" reads as the 10th of the zodiac (Capricorn), not the 10th house from the lagna.
NTH_SIGN = re.compile(r"\b(?:\d{1,2}(?:st|nd|rd|th)|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|"
                      r"tenth|eleventh|twelfth) sign\b", re.I)


# What a judgement may state only as its cited facts state it (review F1): its weighing is the
# reading's, every other proposition is the chart's. A word of these kinds must appear in the value of
# a fact the sentence cites; an age never does (the engine computes none).
JUDGEMENT_LIMITS = {
    "date": re.compile(r"\b(?:19|20)\d{2}(?:-\d{2}(?:-\d{2})?)?\b"),
    "period": re.compile(r"\b(?:maha|antar)?dashas?\b|\bbhuktis?\b|\bpratyantar\w*|\bsub-?periods?\b|\bperiods?\b", re.I),
    "dignity word": re.compile(r"\bexalt\w*|\bdebilitat\w*|\bmoolatrikona\b|\bown sign\b|"
                               r"\b(?:friend|enemy|neutral)(?:'s|ly)?(?:\s+sign)?\b", re.I),
    "strength word": re.compile(r"\b(?:strong\w*|weak\w*|powerful|feeble|afflict\w*|strength)\b", re.I),
    "outcome": re.compile(r"\b(?:rises?|rising|peaks?|peaking|success\w*|succeed\w*|promotions?|wealth\w*|fame|"
                          r"famous|prosper\w*|thrives?|fails?|failure|loss(?:es)?|gains?|late|delay\w*|den(?:y|ies|ial)|"
                          r"marr(?:y|ies|iage comes)|divorce\w*|happ(?:y|iness)|suffer\w*|struggle\w*)\b", re.I),
}
JUDGEMENT_STEMS = {"dignity word": lambda w: re.sub(r"(ation|ed|s|'s|ly)$", "", w.lower().replace(" sign", "")),
                   "strength word": lambda w: w.lower()[:5]}


def judgement_errors(sentence: str, bare: str, cited: dict[str, Any]) -> list[str]:
    """A judgement states a figure, a date, an age, a period, a dignity, a strength or an outcome only
    as a fact it cites states it: the figure or the word (its stem) must be in a cited fact's value,
    and a period word needs a cited dasha or timing field; an age is refused outright, the engine
    computing none."""
    text = json.dumps(cited, default=str).lower()
    errors = []
    for n in re.findall(r"\d+(?:\.\d+)?", bare):
        if not re.search(rf"(?<![\d.]){re.escape(n)}(?![\d])", text):
            errors.append(f"a weighing states a figure ({n!r}) that no fact it cites states: cite the fact that "
                          f"states it: {sentence!r}")
            break
    if (m := re.search(AGE, bare, re.I)):
        errors.append(f"a weighing states no age ({m.group(0)!r}): the engine computes none: {sentence!r}")
    for kind, rx in JUDGEMENT_LIMITS.items():
        for m in rx.finditer(bare):
            word = m.group(0)
            if kind == "period":
                ok = any(p.split(".")[0] in ("vimshottari", "yogini", "chara", "timing", "period_quality") for p in cited)
            else:
                ok = JUDGEMENT_STEMS.get(kind, str.lower)(word) in text
            if not ok:
                errors.append(f"a weighing states a {kind} ({word!r}) that no fact it cites states: the weighing "
                              f"is the reading's, every other proposition is the chart's and must be cited: {sentence!r}")
                break
    return errors


def is_judgement(sentence: str) -> bool:
    return bool(JUDGEMENT.search(TRADITION.sub("", TAG.sub("", sentence))))


RANKING = re.compile(r"\bstrongest support\b|\bweakest (?:point|support|family)\b|\bleast support\b", re.I)
# A claim that leans on another: the checker sees one claim and its finding, so "again" or an
# opening "The same" is either unsupported or, worse, passed as true of nothing (SPEC Layer 7 item 10;
# review 2026-10-23, F9). Narrow on purpose: "also" and "the same sign" are ordinary words.
CROSS_REFERENCE = re.compile(r"\b(again|likewise|aforementioned)\b|\bas (above|noted|said|mentioned|before)\b"
                             r"|^\s*(the|this|that) same\b", re.I)


def _cites_family_fact(fact_tag: str, vote_tag: str, facts: dict | None = None) -> bool:
    """Depth full: a fact that states a family's vote stands for its vote tag in the family rule: the
    area's whole votes or contributions (every family), that family's own vote, or a part of the
    contributions whose value names the family (review F13: `contributions.strongest`, "lord", used to
    stand for every family)."""
    from .fullchart import resolve
    area, family = vote_tag[5:].split(".", 1)
    path = fact_tag[5:]
    if path in (f"areas.{area}.votes", f"areas.{area}.contributions") or path.startswith(f"areas.{area}.votes.{family}"):
        return True
    if path.startswith(f"areas.{area}.contributions.") and facts is not None:
        try:
            return re.search(rf'"{family}"', json.dumps(resolve(facts, path))) is not None
        except KeyError:
            return False
    return False


def validate(text: str, allowed: set[str], *, offered_votes: dict[str, str | set[str]] | None = None,
             family_rule: bool = True, chains: dict[str, list[str]] | None = None, standalone: bool = True,
             facts: dict | None = None, traditions: bool = False, judgements: bool = False) -> list[str]:
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
    chain's word, not the panchanga family's. `standalone` (a claim, which is checked against
    its own finding only) refuses a sentence that refers to another (CROSS_REFERENCE); a summary
    or a paragraph is read whole and may. `facts` (depth full: the whole chart, fullchart.payload)
    offers a [fact:<path>] tag for every path it has; a path it lacks is refused, and with no
    `facts` a fact tag is not offered at all. A sentence citing a fact may state timing, since
    its dates and periods are the cited field's, checked against it. `traditions` (the analysis at
    depth full) admits a [tradition:<text> <chapter>] sentence within its limits (tradition_errors);
    anywhere else such a sentence is refused. `judgements` (the same) admits a judgement sentence
    (is_judgement) within its limits: it cites what it weighs, and states no figure, date or period
    except by citing the fact; at depth full a judgement anywhere else is refused, and so is "the
    10th sign" anywhere (it is "the 10th house from the lagna")."""
    from .fullchart import resolve
    offered_votes = offered_votes or {}
    errors = []
    for s in sentences(text):
        bare = TRADITION.sub("", TAG.sub("", s))
        found = TAG.findall(s)
        tags = {f"{k}:{v}" for k, v in found}
        fact_tags = {t for t in tags if t.startswith("fact:")}
        tradition = bool(TRADITION.search(s))
        if CLAIM_VERBS.search(bare) and not tags and not tradition:
            errors.append(f"untagged claim: {s!r}")
        elif facts is not None and judgements and not tags and not tradition:
            errors.append(f"an analysis sentence carries the tags of what it rests on (every one is checked, and "
                          f"an untagged one rests on nothing): {s!r}")
        errors += tradition_errors(s, traditions, facts)
        if facts is not None and is_judgement(s):
            if not judgements:
                errors.append(f"a weighing ('I weigh', 'I give more weight') belongs in the analysis: {s!r}")
            elif not tags:
                errors.append(f"a weighing cites the findings and facts it weighs: {s!r}")
            else:
                errors += judgement_errors(s, bare, _cited_facts(s, facts))
        if facts is not None and (m := NTH_SIGN.search(bare)):
            errors.append(f"{m.group(0)!r} reads as the zodiac's: say 'the 10th house from the lagna' and cite "
                          f"[fact:houses.lagna.10]: {s!r}")
        if standalone and (m := CROSS_REFERENCE.search(bare)):
            errors.append(f"refers to another claim ({m.group(0).strip()!r}): a claim stands alone and is checked "
                          f"against its finding only: {s!r}")
        for t in sorted(tags - allowed - (fact_tags if facts is not None else set())):
            errors.append(f"tag not offered for this finding: [{t}] in {s!r}")
        for t in sorted(fact_tags) if facts is not None else ():
            try:
                resolve(facts, t[5:])
            except KeyError:
                errors.append(f"no field at path {t[5:]!r} in the chart: [{t}] in {s!r}")
        if facts is not None and (m := RANKING.search(bare)) and \
                not any(re.match(r"fact:areas\.\w+\.contributions(\.|$)", t) for t in fact_tags):
            errors.append(f"a ranking ({m.group(0)!r}) is the engine's: cite [fact:areas.<area>.contributions], "
                          f"which ranks the families, not a ranking of your own: {s!r}")
        if (tags or tradition) and not re.search(r"\]\s*[.!?]?\s*$", s):
            errors.append(f"tags must end the sentence: {s!r}")
        named = families_named(s)
        if any(k == "chain" for k, _ in found) and "panchanga" in named and \
                not FAMILY_WORDS["panchanga"].search(re.sub(r"\bnakshatra lords?\b", "", bare, flags=re.I)):
            named.discard("panchanga")
        # A navamsa chain's sentence says "navamsa" and "the D9 lagna" for the chain, not for the
        # varga family (B's attempt 2 lost six chain claims to it).
        if any(k == "chain" for k, _ in found) and "varga" in named and \
                not FAMILY_WORDS["varga"].search(re.sub(r"\bnavamsas?\b|\bD9\b", "", bare, flags=re.I)):
            named.discard("varga")
        if tradition:                     # never checked and carries no tag: the family rule cannot apply
            named = set()
        for kind, value in found:
            if kind == "vote":
                family = value.split(".", 1)[-1]
                if family_rule and family not in named:
                    errors.append(f"[vote:{value}] on a sentence that does not name the {family} family: {s!r}")
            elif kind == "rule":
                # "lord-of-the-7th-in-the-7th" names "lord of the 7th" as well as the spaced form does
                if not any(n.lower() in bare.lower().replace("-", " ") for n in rule_names(value)):
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
            if want and not want & tags and not any(_cites_family_fact(t, w, facts) for t in fact_tags for w in want):
                shown = " or ".join(f"[{t}]" for t in sorted(want))
                errors.append(f"names the {family} family but does not cite {shown}: {s!r}")
        for kind, rx in FORBIDDEN.items():
            if kind == "timing" and facts is not None and fact_tags:
                continue
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


PLACEMENTS_PER_AREA = 3          # house placements (lord or planet in a house)
SIGN_ROWS_PER_AREA = 1           # one sign row (the Moon, a planet or the rising sign by sign)
NAKSHATRA_ROWS_PER_AREA = 1      # one nakshatra row (the Moon by nakshatra)


def placement_fact(family: str, fires: list, when: dict) -> dict:
    """What a placement finding offers the writer: the fact only (SPEC Layer 3, draft status)."""
    from .constants import SIGNS
    if family == "lagna_sign":
        return {"lagna_sign": SIGNS[when["lagna_sign"]], "lagna_lord": fires[0].nodes[0]}
    if family == "moon_nakshatra":
        return {"planet": "Moon", "nakshatra": when["nakshatra"]}
    if family in ("moon_sign", "planet_sign"):
        return {"planet": when["planet"], "sign": SIGNS[when["sign"]]}
    return {"planet": fires[0].nodes[0], "house": when["house"], **({"lord_of": when["lord_of"]} if "lord_of" in when else {})}


def _quota(family: str) -> int:
    from .rules import NAKSHATRA_PLACEMENTS, SIGN_PLACEMENTS
    return (SIGN_ROWS_PER_AREA if family in SIGN_PLACEMENTS else
            NAKSHATRA_ROWS_PER_AREA if family in NAKSHATRA_PLACEMENTS else PLACEMENTS_PER_AREA)
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
        rows = d if isinstance(d, list) else [r for v in (d or {}).values() if isinstance(v, list) for r in v if isinstance(r, dict)]
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
            rows.append({"finding_id": f"{f.id}@{f.basis}", "rule_id": f.id, "family": f.family,
                         "planet": "Lagna" if f.family == "lagna_sign" else f.nodes[0],
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
            item["placement"] = placement_fact(fires[0].family, fires, rule.data["when"])
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
    # SPEC Layer 6b item 4: an area offers at most its three strongest house placements, one sign
    # row and one nakshatra row (by theme contribution to the area); the rest stay in the learner
    # material (other_placements).
    placed = sorted((i for i in ok if i.get("family") in PLACEMENT_FAMILIES),
                    key=lambda i: (-i["contribution"], i["finding_id"]))
    chosen, used = set(), {}
    for i in placed:
        group = _quota(i["family"]), i["family"] in HOUSE_PLACEMENTS, i["family"] in NAKSHATRA_PLACEMENTS
        if used.get(group, 0) < group[0]:
            used[group] = used.get(group, 0) + 1
            chosen.add(i["finding_id"])
    ok = [i for i in ok if i.get("family") not in PLACEMENT_FAMILIES or i["finding_id"] in chosen]
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
refer to another finding or claim (no "again", "the same", "also", "as above", "likewise"; a claim with \
"again", "likewise", "as above" or opening "The same" is refused before it is checked). Each claim ends with one or more of that finding's allowed tags, written exactly, for example \
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
status draft is a placement fact only: say where the planet is and which house it rules (or which \
sign or nakshatra it is in, or which sign rises), and nothing it is said to mean, since its effect \
has not been read in the text. A house is called by its area \
("the house of career", "a career house") only where the finding's area_houses words it so ("the \
10th, a career house"); say "the 10th" otherwise."""


DEPTHS = ("curious", "learner", "astrologer", "full")

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


# The timing sentence of SYSTEM_PROMPT, which depth full narrows to sentences citing no fact.
TIMING_RULE_TEXT = "and do not mention timing, windows, dates, years, dashas, transits or the engine."
FULL_TIMING_RULE = ("and mention timing, windows, dates, years, dashas, transits or the engine only in a sentence "
                    "citing the fact that states them.")

FULL_PROMPT = """

Depth: full. The reader is an astrologer who wants the best analysis these facts allow. Besides \
the findings, the input carries `chart`: everything the engine computed on this chart, under \
stable paths. A path is the keys from the root of `chart` joined by dots, a list item by its \
index: planets.Mars.dignity, shadbala.planets.Mars.ratio, vargas.D9.Mars, \
areas.career.votes.kp.derivation, vimshottari.periods.Rahu-Saturn, transits.windows.3, and a rule \
fire as rules.<rule id with its dots written as hyphens>@<basis>, e.g. rules.place-l7_h7@lagna. Cite any \
field as [fact:<path>], the path written exactly as in the input, without a leading "chart.". \
A sentence citing a fact is checked against that field's value and nothing else it does not \
cite, so cite the field that states what the sentence says, as narrowly as it is stated \
(planets.Mars.dignity, not planets.Mars); a path that does not exist is refused. A claim may \
cite facts besides its finding's tags. Dates, periods and transits come only from the cited \
fields: a sentence that names one cites the field that states it. Where the engine gives a word \
beside a number, use the word and cite the field: a planet's dignity in a varga (vargas.D10.Saturn \
gives its sign and dignity; a vote row's varga_dignity_label: "exalted", "own"), a stability's \
"holds under 2 of 3 ayanamsas". A transit window or tara row carries areas_touched: the house it \
occupies from the Moon and from the lagna and the areas whose houses those are; a sentence tying \
a transit to an area cites it. chart.constants holds the sign order, the \
sign lords and each planet's exaltation, debilitation, moolatrikona and own signs; \
chart.houses.<lagna|moon|sun>.<n> each house's sign, lord and occupants from that basis; \
chart.not_computed what the engine does not do. Cite these for what they state rather than \
stating it from memory.

Think the chart through before you write: for each area, read its findings and the chart's own \
fields, test each reading against the others, and only then write. Besides the claims, write for \
each area `analysis`, in three parts.
- `assessment`: weigh the evidence for and against the area. Name the strongest support and the \
weakest, and say from which facts. The ranking of the families is the engine's: \
chart.areas.<area>.contributions gives each family's term and its percentile against 10,000 \
random charts, and names the strongest and the weakest by percentile, what is unusual on this \
chart. The terms are on different scales and the lord term is the largest on most charts by \
construction, so the largest term is not a finding. A sentence saying "the strongest support" \
or "the weakest point" cites [fact:areas.<area>.contributions] (its percentile) and never a \
ranking of your own. Where families or schools disagree (a vote against the others, \
an area's own house low by Bhava Bala while its lord is dignified, a cusp's sub-lord against its \
house), resolve the contradiction explicitly: say which side you give more weight and on which \
fact, or that the facts leave it open. Then rank what matters most for this area, most first.
- `timing`: the area's time over chart.transits.range: the running Vimshottari, Yogini and Chara \
periods, the timing join's windows in chart.timing.<area> with their reasons, and the transit \
windows. Every date and period cites the field that states it. The engine sets and states each \
window's score and confidence; argue which reasons weigh, never a score of your own.
- `not_said`: what this chart does not say about the area: what the engine does not compute for \
it, which families abstain or do not apply, what depends on the exact birth time (a stability \
under 0.5, cited), and what no fact here decides.

A synthesis sentence combines several findings and facts into one conclusion. It ends with every \
tag it rests on and is checked as a whole: it passes when each cited fact is true and the \
conclusion follows from them together, and it is refused when its conclusion follows from none of \
them. Cite every premise; conclude only what the premises carry together. Each section is accepted \
whole, so one sentence the checker refuses sends the section back.

Two kinds of sentence in the analysis. A checked sentence states facts, and every proposition in \
it is checked against what it cites. A judgement sentence weighs: it says "I weigh …", "I give \
more weight to … than …", "I read … as …" or "I resolve … toward …", cites the findings and facts \
it weighs, and is shown as the reading's weighing; the checker verifies its premises (each cited \
fact true and stated as the fact states it), not the weighing. Make every weighing a judgement \
sentence and every fact a checked sentence of its own: a judgement carries no fact its citations \
do not state, and states no date, period, figure or tier word except by citing the fact. Say "the \
10th house from the lagna" and cite [fact:houses.lagna.10], never "the 10th sign", which reads as \
the 10th sign of the zodiac. The running periods are those at the reading date \
(chart.vimshottari.current, the current Yogini and Chara periods): say "at the reading date", \
never "over the range", and list the range's later periods from the fields that state them.

The tier stays the engine's: the analysis and the summary use none of the words strong, moderate, \
weak or mixed ("the strongest support", "below its required strength" say it without them), and \
no confidence or probability words. The engine places the tier beside your analysis.

Knowledge beyond the engine. In the analysis you may state what a classical text says that no \
finding or fact here holds, in a sentence of its own ending [tradition:<text> <chapter>], for \
example [tradition:Phaladeepika 10] or [tradition:Saravali 30.2], from these texts only: BPHS, \
Phaladeepika, Saravali, Brihat Jataka, Jataka Parijata, Uttara Kalamrita, Jaimini Sutras, Tajaka \
Neelakanthi. Such a sentence is never checked: it is shown apart, marked unverified, and recorded \
for the astrologer to read in the text. So it carries no other tag and states only the text's \
general principle: no numeral, date, degree, period, dasha or transit, no strength, score or vote, \
and nothing about this chart ("this chart", "your", "here"); a fact of this chart goes in a \
sentence of its own citing it. Write the house as a word ("the tenth"). Cite a chapter only where \
you know the text says it there; leave the sentence out otherwise."""


def system_prompt(depth: str) -> str:
    if depth not in DEPTHS:
        raise ValueError(f"depth must be one of {DEPTHS}, not {depth!r}")
    if depth == "curious":
        assert FAMILY_RULE_TEXT + "a sentence citing a rule" in SYSTEM_PROMPT
        return SYSTEM_PROMPT.replace(FAMILY_RULE_TEXT + "a sentence citing a rule", "A sentence citing a rule") \
            + CURIOUS_PROMPT
    if depth == "full":
        assert TIMING_RULE_TEXT in SYSTEM_PROMPT
        return SYSTEM_PROMPT.replace(TIMING_RULE_TEXT, FULL_TIMING_RULE) + FULL_PROMPT
    return SYSTEM_PROMPT


def timing_note(areas: list[str]) -> str:
    """The engine's sentence under the timing line: what the windows are, and what they are not."""
    names = [a.replace("_", " ") for a in areas]
    joined = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    return f"These are periods the engine scores as favourable for {joined}; it does not predict when you will act."


def full_range(as_of: date, config: NarrationConfig = CONFIG) -> tuple[date, date]:
    """The range the whole chart's transits and timing windows cover at depth full."""
    return as_of, as_of + timedelta(days=round(365.25 * config.timing_years))


def payload(chart: Chart, question: str, areas: list[str], depth: str = "astrologer",
            as_of: date | None = None, facts: dict | None = None) -> tuple[str, dict[str, set[str]]]:
    """The user message for the model, and the tags allowed per finding id. At depth full the
    message also carries `chart`, the whole chart (`facts`, fullchart.payload), and is written
    compactly."""
    allowed: dict[str, set[str]] = {}
    body = {"question": question, "depth": depth, "areas": []}
    for name in areas:
        ok, _ = findings(chart, name, as_of)
        for f in ok:
            allowed[f["finding_id"]] = set(f["allowed_tags"])
        a = chart.scored.areas.get(name)
        body["areas"].append({"name": name, "findings": ok,
                              **({"tests": area_votes(a)} if a is not None and a.score_classical is not None else {})})
    if facts is not None:
        from .fullchart import dumps
        return dumps(dict(body, chart=facts)), allowed
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
when the data's area_houses lists that house in those words, and unsupported otherwise. The data \
may carry `facts`: each a path in the chart and the engine's value there, cited by the sentence; a \
proposition a cited fact states is supported, and a date, period or figure no cited fact or \
finding states is not. When the data has `synthesis` true, the sentence combines its cited \
findings and facts into one conclusion: list each premise it takes from them as a proposition and \
its conclusion as one more. The synthesis is supported when each of its cited facts is true and the \
conclusion follows from them together; reject the conclusion when it does not follow from them \
together, and always when none of its cited findings or facts supports it. When the data has \
`judgement` true, the sentence is the reading's weighing ("I weigh …", "I give more weight to …", \
"I read … as …"). List every proposition in it, as for any sentence. Each proposition about the \
chart (a placement, a dignity, a strength, a date, an age, a period, an outcome, and how a fact is \
read: "I read Saturn in Taurus as its exaltation" states that Saturn is exalted) must be stated by \
a cited finding or fact, and is unsupported otherwise, whether or not anything is cited for it. \
Only the weighing itself may stand unverified: which side the reading gives more weight to, or \
what it makes of the cited facts taken together; list it with evidence "the weighing" and mark it \
supported. Ignore the bracketed citation tags."""


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
            # The payload is cached: a regeneration resends it unchanged, and at depth full it is
            # the whole chart (docs/spec_notes_2026-10-23.md has its size).
            self.messages.append({"role": "user", "content": [
                {"type": "text", "text": user, "cache_control": {"type": "ephemeral"}}]})
        elif len(errors) == 1 and errors[0].startswith(RETRY_HEAD):
            self.messages.append({"role": "user", "content": errors[0]})     # a section retry (retry_instruction)
        else:
            self.messages.append({"role": "user", "content":
                                  "The draft was rejected. Fix every one of these and return the whole draft again:\n- "
                                  + "\n- ".join(errors)})
        import time
        cfg = self.config
        started = time.perf_counter()
        kwargs = dict(model=cfg.model, max_tokens=cfg.max_tokens, betas=list(cfg.betas), fallbacks=cfg.fallbacks,
                      output_config={"effort": cfg.effort}, system=system, messages=self.messages,
                      output_format=ReadingDraft)
        if cfg.thinking:
            kwargs["thinking"] = {"type": cfg.thinking, "display": cfg.thinking_display}
        if cfg.max_tokens > STREAM_ABOVE:
            with self.client.beta.messages.stream(**kwargs) as stream:
                response = stream.get_final_message()
        else:
            response = self.client.beta.messages.parse(**kwargs)
        self.last_meta = _meta(response, "writer", cfg.effort, started)
        thought = "\n".join(b.thinking for b in getattr(response, "content", None) or []
                             if getattr(b, "type", None) == "thinking" and getattr(b, "thinking", ""))
        if thought:                                   # the summarised reasoning, for the recording only
            self.last_meta["thinking"] = thought
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
        return dict(model=cfg.checker_model, max_tokens=min(cfg.max_tokens, STREAM_ABOVE), betas=list(cfg.betas),
                    fallbacks=cfg.fallbacks,
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


def _check_payload(f: dict, text: str = "", facts: dict | None = None) -> str:
    """What the checker sees for one claim: its finding's derivation and, at depth full, the
    value of every field the claim cites as a fact (a claim citing one is a synthesis of its
    finding and the fact); nothing else."""
    data = _check_data(f)
    cited = _cited_facts(text, facts)
    return json.dumps({"finding": data, "facts": cited, "synthesis": True} if cited else data, indent=1, default=str)


RETRY_HEAD = "Some parts of the draft passed every check and are held."


def retry_instruction(held: list[str], failed: dict[str, list[str]]) -> str:
    """The writer's next message under section retries: what is held (never rewritten), and each
    unit to rewrite with the reasons it failed, the checker's quoted as it gave them."""
    lines = [RETRY_HEAD + " They stand as written and are not rewritten: leave each out of your answer "
             "(an empty summary, no claim for it, a null section).", ""]
    lines += ["Held: " + ("; ".join(held) if held else "nothing yet") + ".", "",
              "Rewrite only these, each for the reasons quoted, and return them in the same schema:"]
    for unit, reasons in failed.items():
        lines.append(f"- {unit}:")
        lines += [f"    - {r}" for r in reasons]
    return "\n".join(lines)


def _cited_facts(text: str, facts: dict | None) -> dict[str, Any]:
    """path -> the chart's value there, for each [fact:<path>] in `text` that resolves."""
    from .fullchart import resolve
    out = {}
    for kind, path in TAG.findall(text):
        if kind == "fact" and facts is not None:
            try:
                out[path] = resolve(facts, path)
            except KeyError:
                pass
    return out


def _check_data(f: dict) -> dict:
    keep = ("finding_id", "kind", "rule_id", "family", "direction", "basis", "bases", "sudarshana_bases",
            "school", "planets",
            "themes", "fires", "derivation", "area_votes", "glossary", "classical_effect", "status", "placement",
            "area_houses", "chain", "planet", "role", "facts")
    return {k: f[k] for k in keep if k in f}


def _summary_checks(summary: str, finding_data: dict[str, dict],
                    facts: dict | None = None) -> list[tuple[str, list[str], str]]:
    """(sentence, finding ids, data) for every sentence of a summary, paragraph or section, tagged
    or not (review F2: an untagged sentence with no listed claim verb used to reach the page
    unchecked): the data is the union of the derivations of every finding offering one of its tags,
    and at depth full the value of every fact it cites; an untagged sentence is checked against
    nothing, so it passes only if it asserts nothing about the chart. A [tradition:] sentence is
    never checked."""
    out = []
    for s in sentences(summary):
        tags = {f"{k}:{v}" for k, v in TAG.findall(s)}
        if TRADITION.search(s):
            continue
        ids = [fid for fid, f in finding_data.items() if tags & set(f["allowed_tags"])]
        data: dict[str, Any] = {"findings": [_check_data(finding_data[i]) for i in ids]}
        if cited := _cited_facts(s, facts):
            data["facts"] = cited
        if facts is not None and is_judgement(s):
            data["judgement"] = True                     # its premises are checked, never its weighing
        elif facts is not None and len(ids) + len(cited) > 1:
            data["synthesis"] = True
        out.append((s, ids, json.dumps(data, indent=1, default=str)))
    return out


def split_traditions(sections: dict[str, str]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    """The analysis's sections with their [tradition:] sentences taken out, and those sentences,
    each with its citation, unchecked and carrying TRADITION_NOTE."""
    kept, out = {}, []
    for sec, text in sections.items():
        rest = []
        for s in sentences(text):
            cite = TRADITION.search(s)
            if cite is None:
                rest.append(s)
                continue
            c = tradition_citation(cite.group(1)) or {"text": None, "chapter": None, "verse": None}
            out.append({"section": sec, "sentence": s, "citation": cite.group(1).strip(), **c, "checked": False,
                        "note": TRADITION_NOTE})
        if rest:
            kept[sec] = " ".join(rest)
    return kept, out


def is_synthesis(sentence: str, finding_data: dict[str, dict], facts: dict | None) -> bool:
    """Depth full: a sentence resting on two or more findings or facts (checked as a synthesis)."""
    tags = {f"{k}:{v}" for k, v in TAG.findall(sentence)}
    ids = [fid for fid, f in finding_data.items() if tags & set(f["allowed_tags"])]
    return facts is not None and not is_judgement(sentence) and len(ids) + len(_cited_facts(sentence, facts)) > 1


def _usage(metas: list[dict | None]) -> dict[str, Any]:
    """The calls of one side and their token usage, summed (a replayed call has none)."""
    keys = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    out: dict[str, Any] = {"calls": len(metas)} | {k: 0 for k in keys}
    for m in metas:
        for k in keys:
            out[k] += int(((m or {}).get("usage") or {}).get(k) or 0)
    out["seconds"] = round(sum(float((m or {}).get("seconds") or 0) for m in metas), 3)
    return out


def narrate(chart: Chart, question: str, *, drafter: Drafter | None = None, checker: Checker | None = None,
            as_of: date | None = None, config: NarrationConfig = CONFIG,
            recording: list | None = None, areas: list[str] | None = None,
            progress: Callable[[str, dict], None] | None = None, depth: str = "astrologer",
            writer_model: str | None = None, writer_effort: str | None = None) -> Reading:
    """`areas` overrides the routed areas (the question's "when" is still read from it).
    `progress(stage, info)` is told "draft" before each writer call and "check" before each
    attempt's checker calls, with the attempt number (the service's job status). `depth`
    "curious" adds a plain-language paragraph per area, validated and checked like the
    summary; "full" hands the writer the whole chart (fullchart.payload over `full_range`), whose
    fields a sentence cites as [fact:<path>], with the writer thinking at the highest effort
    (writer_config) and an analysis per area (assessment, timing, not_said), each section checked
    like the summary, its synthesis sentences as syntheses; the claims and every engine field are
    the same at every depth. `writer_model` and `writer_effort` override the writer's settings
    (the checker's never change); the reading records both sides' settings and usage."""
    import time
    started = time.perf_counter()
    progress = progress or (lambda stage, info: None)
    if chart.scored is None:
        raise ValueError("narration needs a scored chart (birth moment, Shadbala, Bhava Bala)")
    as_of = as_of or date.today()
    sc = chart.scored
    routed, when = route(question, chart)
    areas = list(areas) if areas is not None else routed
    system = system_prompt(depth)
    curious, full = depth == "curious", depth == "full"
    facts = None
    if full:
        from .fullchart import payload as whole_chart
        facts = whole_chart(chart, as_of, *full_range(as_of, config), areas)
    user, allowed = payload(chart, question, areas, depth, as_of, facts)
    area_tags = {name: set().union(*(set(f["allowed_tags"]) for f in findings(chart, name, as_of)[0])) for name in areas}
    all_tags = set().union(*allowed.values()) if allowed else set()
    wcfg = writer_config(config, depth, writer_model, writer_effort)
    drafter = drafter or AnthropicDrafter(wcfg)
    writer_metas: list[dict | None] = []
    checker_metas: list[dict | None] = []
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
    kept_ana: dict[tuple[str, str], str] = {}           # (area, section) -> latest accepted text (depth full)
    ana_error: dict[tuple[str, str], tuple[str, int]] = {}
    draft, errors, attempts, clean = None, [], 0, False
    # Depth full, section retries (CONFIG.section_retries): a unit that passed is held and never
    # validated, checked or rewritten again; every unit that passes the validator is checked in the
    # same attempt, and the next draft is asked for the failed units only (retry_instruction).
    held = full and config.section_retries
    # The writer's settings as it runs them: a drafter with its own config (AnthropicDrafter) is the
    # authority, so a step down starts from the effort it actually uses.
    if isinstance(getattr(drafter, "config", None), NarrationConfig):
        wcfg = drafter.config
    effort_now, efforts, stepped = wcfg.effort, [], []
    for attempts in range(1, config.max_attempts + 1):
        progress("draft", {"attempt": attempts})
        efforts.append(effort_now)
        try:
            draft = drafter(system, user, errors)
        except NarrationError as e:                        # a refusal or no structured output
            writer_metas.append(getattr(drafter, "last_meta", None))
            errors = [str(e)] + list(e.errors)
            # Thinking reached max_tokens and left no draft: the next attempt one effort level lower.
            if "max_tokens" in e.errors and effort_now in EFFORTS and EFFORTS.index(effort_now) > 0:
                lower = EFFORTS[EFFORTS.index(effort_now) - 1]
                stepped.append({"attempt": attempts, "from": effort_now, "to": lower,
                                "why": "no draft: the writer's thinking reached max_tokens"})
                effort_now = lower
                if isinstance(getattr(drafter, "config", None), NarrationConfig):
                    from dataclasses import replace as _replace
                    drafter.config = _replace(drafter.config, effort=lower)
            if recording is not None:
                recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "writer"}, attempt=attempts,
                                      draft=None, validator_errors=[], writer_error=errors))
            summary_error = (errors[0], attempts)
            for name in areas:
                para_error[name] = (errors[0], attempts)
                for sec in ANALYSIS_SECTIONS:
                    ana_error[(name, sec)] = (errors[0], attempts)
                for f in findings(chart, name, as_of)[0]:
                    last_error[(name, f["finding_id"])] = (errors[0], attempts)
            continue
        writer_metas.append(getattr(drafter, "last_meta", None))
        entry = dict(getattr(drafter, "last_meta", None) or {"kind": "writer"}, attempt=attempts,
                     draft=draft.model_dump())
        summary_held = held and kept_summary is not None
        summary_errs = [] if summary_held else validate_summary(
            draft.summary, all_tags, offered_votes=all_votes, family_rule=not curious, chains=all_chains, facts=facts)
        if held and not summary_held and not draft.summary.strip():
            summary_errs = ["no summary: it is not held, so the draft needs one"]
        errors = list(summary_errs)
        unit_errors: dict[str, list[str]] = {"the summary": list(summary_errs)} if not summary_held else {}
        claim_errs: dict[tuple[str, str], list[str]] = {}
        drafted: list[tuple[str, DraftClaim]] = []
        for da in draft.areas:
            if da.name not in areas:
                errors.append(f"area not asked for: {da.name}")
                unit_errors.setdefault("the draft", []).append(errors[-1])
                continue
            for c in da.claims:
                if held and (da.name, c.finding_id) in kept:
                    continue                                 # held: what the writer sent again is ignored
                if c.finding_id not in allowed:
                    errors.append(f"unknown finding id {c.finding_id!r}")
                    unit_errors.setdefault("the draft", []).append(errors[-1])
                    continue
                if (da.name, c.finding_id) in claim_errs:
                    errors.append(f"two claims for {c.finding_id} in {da.name}")
                    unit_errors.setdefault(f"the claim for {c.finding_id} ({da.name})", []).append(errors[-1])
                    continue
                errs = validate(c.text, allowed[c.finding_id], offered_votes=votes_offered[da.name],
                                family_rule=not curious, chains=chains_offered[da.name], facts=facts)
                if not TAG.search(c.text):
                    errs.append(f"claim without a tag: {c.text!r}")
                claim_errs[(da.name, c.finding_id)] = errs
                drafted.append((da.name, c))
                unit_errors[f"the claim for {c.finding_id} ({da.name})"] = list(errs)
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
        ana_errs: dict[tuple[str, str], list[str]] = {}
        sections: dict[tuple[str, str], str] = {}
        if full:
            # Each section of each area's analysis is read like the summary: the area's tags and any
            # fact, families named and cited, and no tier word (the engine states the tier).
            for name in areas:
                an = next((d.analysis for d in draft.areas if d.name == name), None)
                for sec in ANALYSIS_SECTIONS:
                    if held and (name, sec) in kept_ana:
                        continue
                    text = getattr(an, sec, None) if an is not None else None
                    if text:
                        sections[(name, sec)] = text
                    ana_errs[(name, sec)] = (validate_summary(text, area_tags[name], offered_votes=votes_offered[name],
                                                              where=f"{name} {sec}", chains=chains_offered[name],
                                                              facts=facts, traditions=True, judgements=True)
                                             if text else [f"no {sec} for {name}: at full depth every area has one"])
                    unit_errors[f"the {name} {sec}"] = list(ana_errs[(name, sec)])
                    errors += ana_errs[(name, sec)]
        entry["validator_errors"] = list(errors)
        if recording is not None:
            recording.append(entry)
        for name, errs in para_errs.items():
            if errs:
                para_error[name] = (errs[0], attempts)
        for key, errs in ana_errs.items():
            if errs:
                ana_error[key] = (errs[0], attempts)
        for key, errs in claim_errs.items():
            if errs:
                last_error[key] = (errs[0], attempts)
        if summary_errs:
            summary_error = (summary_errs[0], attempts)
        final = attempts == config.max_attempts
        if errors and not final and not held:
            continue
        # The semantic check (SPEC Layer 7 item 10): on every claim of every attempt that
        # reaches it (the checker is a sample, so a claim that passed before is checked again),
        # each with its finding's derivation alone; and on every tagged summary sentence,
        # against the union of the derivations of the findings it cites. On the last attempt
        # the sentences that passed the validator are checked even if others did not.
        checks = ([(s, ids, data, "summary", None)
                   for s, ids, data in _summary_checks(draft.summary, finding_data, facts)]
                  if not summary_errs and not summary_held else [])
        checks += [(c.text, [c.finding_id], _check_payload(finding_data[c.finding_id], c.text, facts), c.finding_id, name)
                   for name, c in drafted if not claim_errs[(name, c.finding_id)]]
        paragraphs = {d.name: d.paragraph for d in draft.areas if d.paragraph}
        for name, errs in para_errs.items():
            if not errs:
                checks += [(s_, ids, data, f"paragraph:{name}", name)
                           for s_, ids, data in _summary_checks(paragraphs[name], finding_data)]
        for (name, sec), errs in ana_errs.items():
            if not errs:
                checks += [(s_, ids, data, f"analysis:{name}:{sec}", name)
                           for s_, ids, data in _summary_checks(sections[(name, sec)], finding_data, facts)]
        progress("check", {"attempt": attempts, "calls": len(checks)})
        # The checks of one attempt are independent: a checker with `check_many` runs them
        # concurrently (AnthropicChecker); any other checker is called one by one.
        if hasattr(checker, "check_many"):
            outcomes = checker.check_many([(sentence, data) for sentence, _, data, _, _ in checks])
        else:
            outcomes = [(checker(sentence, data), getattr(checker, "last_meta", None))
                        for sentence, _, data, _, _ in checks]
        checker_metas += [meta for _, meta in outcomes]
        rejected: dict[tuple[str, str] | str, str] = {}
        for (sentence, ids, data, label, name), (result, meta) in zip(checks, outcomes):
            if recording is not None:
                recording.append(dict(meta or {"kind": "checker"},
                                      attempt=attempts, finding_id=label, findings=ids, sentence=sentence,
                                      result=result.model_dump()))
            whole = label == "summary" or label.startswith(("paragraph:", "analysis:"))
            where = (f"the derivations of {', '.join(ids)} (summary)" if label == "summary"
                     else f"the derivations of {', '.join(ids)} ({label})" if label.startswith("paragraph:")
                     else f"the derivations and facts it cites ({label})" if label.startswith("analysis:")
                     else f"the derivation of {label}")
            for prop in result.propositions:
                if not prop.supported:
                    msg = f"unsupported by {where}: {prop.text!r} ({prop.evidence}) in {sentence!r}"
                    errors.append(msg)
                    rejected.setdefault(label if whole else (name, label), msg)
                    unit = ("the summary" if label == "summary" else f"the {name} {label.split(':')[2]}"
                            if label.startswith("analysis:") else f"the {name} paragraph"
                            if label.startswith("paragraph:") else f"the claim for {label} ({name})")
                    unit_errors.setdefault(unit, []).append(
                        f"the checker refused {prop.text!r}: {prop.evidence!r}, in {sentence!r}")
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
        for (name, sec), errs in ana_errs.items():
            if not errs:
                if f"analysis:{name}:{sec}" in rejected:
                    ana_error[(name, sec)] = (rejected[f"analysis:{name}:{sec}"], attempts)
                else:
                    kept_ana[(name, sec)] = sections[(name, sec)]
        if not summary_errs and not summary_held:
            if "summary" in rejected:
                summary_error = (rejected["summary"], attempts)
            else:
                kept_summary = draft.summary
        if not errors:
            clean = True
            break
        if held:
            # Every error reaches the writer (review F13): one no unit names goes under "the draft".
            named = {e for v in unit_errors.values() for e in v}
            stray = [e for e in errors if e not in named and not e.startswith("unsupported by ")]
            if stray:
                unit_errors.setdefault("the draft", []).extend(stray)
            heldnow = (["the summary"] if kept_summary is not None else []) + \
                [f"the {n} {sec}" for n in areas for sec in ANALYSIS_SECTIONS if (n, sec) in kept_ana] + \
                [f"the claim for {fid} ({n})" for n, fid in kept]
            errors = [retry_instruction(heldnow, {u: e for u, e in unit_errors.items() if e})]

    if clean and not held:                                 # the last draft passed every check: it is the reading
        kept = {(name, c.finding_id): c for name, c in drafted}
        kept_summary = draft.summary
        kept_para = {d.name: d.paragraph for d in draft.areas if d.paragraph} if curious else {}
        kept_ana = dict(sections)

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
        analysis, traditions = (split_traditions({sec: kept_ana[(name, sec)] for sec in ANALYSIS_SECTIONS
                                                  if (name, sec) in kept_ana}) if full else (None, []))
        for sec in ANALYSIS_SECTIONS if full else ():
            if sec not in analysis:
                err, at = ana_error.get((name, sec), (f"no {sec} was drafted for this area", attempts))
                gaps.append({"finding_id": f"analysis.{sec}", "kind": "analysis", "last_error": err, "attempt": at})
        disclaimer = DISCLAIMERS["third_party"] if name in THIRD_PARTY_AREAS else (
            DISCLAIMERS[DISCLAIMER_KEYS[name]] if name in DISCLAIMER_KEYS else None)
        reading_areas.append(ReadingArea(
            name=name, score_classical=a.score_classical, tier=a.tier, stability=a.stability,
            families_agree_w=a.families_agree_w, families_total_w=a.families_total_w,
            polarity=a.polarity if top3 else [], polarity_touches=a.polarity_touches if top3 else {},
            claims=claims, school_conflicts=school_conflicts(a), windows=windows, avoid_window=avoid,
            disclaimer=disclaimer, narration_gaps=gaps, paragraph=paragraph,
            other_placements=other_placements(chart, name),
            paragraph_cites=[f"{k}:{v}" for k, v in TAG.findall(paragraph or "")],
            analysis=analysis, analysis_cites=list(dict.fromkeys(
                f"{k}:{v}" for t in (analysis or {}).values() for k, v in TAG.findall(t))), traditions=traditions,
            judgements=[{"section": sec, "sentence": x} for sec, t in (analysis or {}).items() for x in sentences(t)
                        if is_judgement(x)]))

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
    shown = [text] + [c.text for a in reading_areas for c in a.claims] + \
        [t for a in reading_areas for t in (a.analysis or {}).values()]
    synthesis = sum(1 for t in shown for x in sentences(t) if is_synthesis(x, finding_data, facts))
    return Reading(as_of=as_of.isoformat(), weights=sc.weights, engine=chart.meta.engine, question=question,
                   chart=chart_header(chart), facts_cited={k: v for t in shown for k, v in _cited_facts(t, facts).items()},
                   writer={"model": wcfg.model, "effort": wcfg.effort, "thinking": wcfg.thinking,
                           "max_tokens": wcfg.max_tokens,
                           **({"efforts_by_attempt": efforts, "stepped_down": stepped} if stepped else {})},
                   checker={"model": config.checker_model, "effort": config.checker_effort},
                   usage={"writer": _usage(writer_metas), "checker": _usage(checker_metas),
                          "wall_seconds": round(time.perf_counter() - started, 3)},
                   synthesis_sentences=synthesis,
                   judgement_sentences=sum(len(a.judgements) for a in reading_areas),
                   model=wcfg.model, attempts=attempts, summary=summary, areas=reading_areas,
                   narration_complete=source == "model" and not any(a.narration_gaps for a in reading_areas),
                   depth=depth,
                   fired_rules=fired, unstable=unstable, depends_on_birth_time=depends, disclaimers=disclaimers)
