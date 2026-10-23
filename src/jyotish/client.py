"""The client's layer at depth full (SPEC Layer 7, depth full; docs/spec_notes_2026-10-23.md, the heading
of 2026-10-24).

Depth full reasons for the astrologer: claims, then an analysis per area. Once those are accepted, a
second writer call turns them into what the client reads: per area one plain paragraph (the answer
first, in two or three sentences, then what argues for it, then what argues against, then the timing
in dates) and the reading's summary. The call sees only accepted text and the value of every fact
that text cites, never the chart, so it can add nothing the checks have not passed. Every sentence
carries the tags of what it draws on, copied from the accepted text, and is validated and checked
like the summary, in the client's words: no engine vocabulary (CLIENT_WORDS), no "I", and a weighing
carried over from the analysis keeps its marking in plain words ("in the reading's view"), checked
as a judgement: its premises are checked, its weighing is the reading's.

The writer's "what the chart does not decide" list for the client (`not_said_client`) is written in
the first call, beside the analysis; its words are held to CLIENT_WORDS as well (`client_errors`
with no accepted text)."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from pydantic import BaseModel, Field

# The engine's own words, which the client's text never uses (the request of 2026-10-24: no vote,
# family, term, percentile, learned score, house system, sample), with the two the astrologer's list
# carries besides (ayanamsa, derivation).
CLIENT_WORDS = re.compile(r"\bvot(?:e|es|ing)\b|\bfamil(?:y|ies)\b|\bterms?\b|\bpercentiles?\b|\blearned scores?\b|"
                          r"\bhouse systems?\b|\bsampl(?:e|es|ed|er|ing)\b|\bayanamsas?\b|\bderivations?\b", re.I)
FIRST_PERSON = re.compile(r"\bI\b|\bI'(?:m|d|ve|ll)\b")
# A sentence that ranks or weighs evidence: in the client's text it is the reading's view, said so.
WEIGHING = re.compile(r"\b(?:more|most|greater|less) weight\b|\boutweigh\w*|\bweigh(?:s|ed|ing)?\b|"
                      r"\bcounts? for (?:more|most)\b|\bmatters? (?:more|most)\b|\btips? the balance\b", re.I)
VIEW = re.compile(r"\bthe reading's view\b", re.I)


class ClientArea(BaseModel):
    name: str
    paragraph: str | None = Field(default=None, description=(
        "The area for the client, in plain words: the answer first in two or three sentences, then what "
        "argues for it, then what argues against it, then the timing in dates. Every sentence ends with the "
        "tags of the accepted sentences it draws on. Null on a retry when the paragraph is held."))


class ClientDraft(BaseModel):
    summary: str = Field(description="Two or three tagged sentences answering the question across the areas, "
                                     "from the accepted text only; empty on a retry when the summary is held.")
    areas: list[ClientArea]


CLIENT_PROMPT = """You write the part of a Vedic-astrology reading that the client reads. The client \
knows no astrology. The input holds the question, the reading date and, for each area, the \
sentences of the astrologer's reading that passed every check: the claims, the assessment, the \
timing and what the chart does not decide, each ending with its tags in brackets; the sentences \
among them that weigh the evidence (`judgements`); and the value of every fact those sentences \
cite. Write from these only. Add no fact, planet, sign, house, date or period they do not state, \
and leave out what they do not settle.

For each area write `paragraph`, five to nine sentences in this order: the answer to the question \
for this area first, in two or three sentences; then what argues for it; then what argues against \
it or limits it; then the timing, in the dates the accepted text gives. Then write `summary`: two \
or three sentences answering the question across the areas, the answer first.

Every sentence ends with the tags of the accepted sentences it draws on, copied exactly \
([fact:…], [rule:…], [vote:…], [chain:…]); a sentence drawing on two cites the tags of both, and \
cites no tag the accepted text does not carry. A sentence citing a rule names the yoga or placement \
as the accepted sentence does; a sentence citing a chain names the planet and the chain (sign, \
nakshatra or navamsa) as the accepted sentence does. Each sentence is checked against what it \
cites, so say only what those sentences and facts state.

Plain words. When you name a placement or a period, say in a few words what it means. Use none of \
the engine's words: vote, family, term, percentile, learned score, house system, sample, ayanamsa, \
derivation. Use none of the words strong, moderate, weak or mixed and no probability or confidence \
words: the engine states the tier beside your paragraph. A window is a stretch of time the \
reading's timing favours, not a prediction of when the client will act. Nothing about death, \
illness, trades or investments, or another person's own life.

A weighing. Where the astrologer's reading weighs the evidence (the sentences in `judgements`: "I \
give more weight to …", "I read … as …"), the client's sentence that carries it says so in plain \
words, "in the reading's view", and cites the same tags: its facts are checked, the weighing is the \
reading's. Any sentence that ranks or weighs evidence says "in the reading's view". Never write \
"I"."""


def client_errors(text: str | None, accepted: set[str] | None = None) -> list[str]:
    """The client's words: no engine vocabulary, no "I", a weighing marked as the reading's view, and
    (the paragraph and summary, `accepted` the tags of the accepted text they draw on) every sentence
    tagged with tags from that text only."""
    from .narrate import TAG, TRADITION, sentences
    errors = []
    for s in sentences(text or ""):
        bare = TRADITION.sub("", TAG.sub("", s))
        tags = {f"{k}:{v}" for k, v in TAG.findall(s)}
        if (m := CLIENT_WORDS.search(bare)):
            errors.append(f"engine vocabulary ({m.group(0)!r}) in the client's text: say it in plain words: {s!r}")
        if FIRST_PERSON.search(bare):
            errors.append(f"the client's text never says 'I'; a weighing is 'in the reading's view': {s!r}")
        elif (m := WEIGHING.search(bare)) and not VIEW.search(bare):
            errors.append(f"a weighing ({m.group(0)!r}) in the client's text says 'in the reading's view': {s!r}")
        if accepted is not None:
            if not tags:
                errors.append(f"every sentence of the client's text carries the tags of the accepted sentences it "
                              f"draws on: {s!r}")
            for t in sorted(tags - accepted):
                errors.append(f"[{t}] is not in the accepted text this draws on: {s!r}")
    return errors


def client_input(question: str, as_of: str, accepted: dict[str, dict[str, Any]], facts: dict[str, Any]) -> str:
    """The client writer's whole input: the question, the date, per area the accepted sentences and the
    judgements among them, and the value of every fact they cite. Nothing else of the chart."""
    return json.dumps({"question": question, "as_of": as_of, "areas": accepted, "facts": facts},
                      indent=1, ensure_ascii=False, default=str)


def accepted_text(name: str, claims: list[str], sections: dict[str, str]) -> dict[str, Any]:
    """What passed every check in one area, as the client writer sees it: the claims, the analysis
    sections (the [tradition:] sentences, never checked, are already out of them) and the judgements."""
    from .narrate import is_judgement, sentences
    out: dict[str, Any] = {"name": name, "claims": claims}
    for key, sec in (("assessment", "assessment"), ("timing", "timing"), ("not_decided", "not_said_client"),
                     ("not_computed", "not_said_astrologer"), ("not_said", "not_said")):
        if sections.get(sec):
            out[key] = sections[sec]
    out["judgements"] = [x for t in sections.values() for x in sentences(t) if is_judgement(x)]
    return out


def tags_of(texts: list[str]) -> set[str]:
    from .narrate import TAG
    return {f"{k}:{v}" for t in texts for k, v in TAG.findall(t)}


def write(drafter: Callable, checker, *, question: str, as_of: str, accepted: dict[str, dict[str, Any]],
          finding_data: dict[str, dict], facts: dict, votes: dict, chains: dict, max_attempts: int,
          recording: list | None, progress: Callable[[str, dict], None]) -> dict[str, Any]:
    """The client's layer: up to `max_attempts` calls; each paragraph and the summary that passes the
    validator is checked in its attempt and held once it passes, and a retry asks only for the failed
    ones with their reasons. Returns {summary, summary_error, paragraphs, para_errors, writer_metas,
    checker_metas, attempts}; a unit that never passed is None with its last error."""
    from .narrate import (RETRY_HEAD, NarrationError, _cited_facts, _summary_checks, retry_instruction,
                          validate_summary)
    from .fullchart import resolve
    names = [n for n in accepted]
    area_tags = {n: tags_of(accepted[n]["claims"] + [v for k, v in accepted[n].items()
                                                       if k not in ("name", "claims", "judgements")])
                 for n in names}
    all_tags = set().union(*area_tags.values()) if area_tags else set()
    cited = {}
    for n in names:
        for t in area_tags[n]:
            if t.startswith("fact:"):
                try:
                    cited[t[5:]] = resolve(facts, t[5:])
                except KeyError:
                    pass
    user = client_input(question, as_of, {n: {k: v for k, v in accepted[n].items() if k != "name"} for n in names},
                        cited)
    all_votes: dict[str, set[str]] = {}
    for n in names:
        for fam, tag in votes[n].items():
            all_votes.setdefault(fam, set()).add(tag)
    all_chains = {k: v for n in names for k, v in chains[n].items()}
    summary = summary_error = None
    paragraphs: dict[str, str] = {}
    para_errors: dict[str, tuple[str, int]] = {}
    writer_metas: list = []
    checker_metas: list = []
    errors: list[str] = []
    attempts = 0
    for attempts in range(1, max_attempts + 1):
        progress("client", {"attempt": attempts})
        try:
            draft = drafter(CLIENT_PROMPT, user, errors)
        except NarrationError as e:
            writer_metas.append(getattr(drafter, "last_meta", None))
            errors = [str(e)] + list(e.errors)
            if recording is not None:
                recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "client"}, attempt=attempts,
                                      client_draft=None, validator_errors=[], writer_error=errors))
            summary_error = summary_error or (errors[0], attempts)
            for n in names:
                if n not in paragraphs:
                    para_errors[n] = (errors[0], attempts)
            if "recording has no client draft" in str(e):
                break                                   # a replay made before the client layer: nothing to retry
            continue
        writer_metas.append(getattr(drafter, "last_meta", None))
        units: dict[str, tuple[str, list[str]]] = {}     # label -> (text, validator errors)
        if summary is None:
            text = draft.summary or ""
            errs = (validate_summary(text, all_tags, offered_votes=all_votes, family_rule=False, chains=all_chains,
                                     facts=facts, judgements=True) + client_errors(text, all_tags)
                    if text.strip() else ["no summary: it is not held, so the draft needs one"])
            units["client:summary"] = (text, errs)
        for n in names:
            if n in paragraphs:
                continue
            text = next((a.paragraph for a in draft.areas if a.name == n), None) or ""
            errs = (validate_summary(text, area_tags[n], offered_votes=votes[n], where=f"{n} paragraph",
                                     family_rule=False, chains=chains[n], facts=facts, judgements=True)
                    + client_errors(text, area_tags[n])
                    if text.strip() else [f"no paragraph for {n}: every area has one"])
            units[f"client:paragraph:{n}"] = (text, errs)
        if recording is not None:
            recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "client"}, attempt=attempts,
                                  client_draft=draft.model_dump(),
                                  validator_errors=[e for _, es in units.values() for e in es]))
        checks = [(s, ids, data, label) for label, (text, errs) in units.items() if not errs
                  for s, ids, data in _summary_checks(text, finding_data, facts)]
        progress("client check", {"attempt": attempts, "calls": len(checks)})
        if hasattr(checker, "check_many"):
            outcomes = checker.check_many([(s, data) for s, _, data, _ in checks])
        else:
            outcomes = [(checker(s, data), getattr(checker, "last_meta", None)) for s, _, data, _ in checks]
        checker_metas += [meta for _, meta in outcomes]
        refused: dict[str, list[str]] = {}
        for (s, ids, data, label), (result, meta) in zip(checks, outcomes):
            if recording is not None:
                recording.append(dict(meta or {"kind": "checker"}, attempt=attempts, layer="client", finding_id=label,
                                      findings=ids, sentence=s, result=result.model_dump()))
            for p in result.propositions:
                if not p.supported:
                    refused.setdefault(label, []).append(
                        f"unsupported by the accepted text and the facts it cites ({label}): {p.text!r} ({p.evidence}) "
                        f"in {s!r}")
        failed: dict[str, list[str]] = {}
        for label, (text, errs) in units.items():
            why = errs or refused.get(label, [])
            name = label.split(":")[-1] if label.startswith("client:paragraph:") else None
            unit = "the summary" if name is None else f"the {name} paragraph"
            if why:
                failed[unit] = why
                if name is None:
                    summary_error = (why[0], attempts)
                else:
                    para_errors[name] = (why[0], attempts)
            elif name is None:
                summary, summary_error = text, None
            else:
                paragraphs[name] = text
                para_errors.pop(name, None)
        if not failed:
            break
        held = (["the summary"] if summary is not None else []) + [f"the {n} paragraph" for n in paragraphs]
        errors = [retry_instruction(held, failed)]
        assert errors[0].startswith(RETRY_HEAD)
    return {"summary": summary, "summary_error": summary_error, "paragraphs": paragraphs,
            "para_errors": {n: e for n, e in para_errors.items() if n not in paragraphs},
            "writer_metas": writer_metas, "checker_metas": checker_metas, "attempts": attempts,
            "facts": _cited_facts(" ".join([summary or ""] + list(paragraphs.values())), facts)}
