"""The client's layer at depth full (SPEC Layer 7, depth full; docs/spec_notes_2026-10-23.md, the heading
of 2026-10-24).

Depth full reasons for the astrologer: claims, then an analysis per area. Once those are accepted, a
second writer call turns them into what the client reads (the client's view, 2026-10-25): per area
"What the chart says for you" (`paragraph`: the answer in two or three sentences, what supports it,
what works against it, no dates), "When" (`when`: the windows in dates and months, the reading's
weighing carried over and marked "the reading's view") and the reading's summary; "What this chart
does not tell" is the client's half of not-said, written in the first call. The call sees only accepted text and the value of every fact
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

# The engine's own words, which the client's text never uses (the requests of 2026-10-24 and -25: no
# vote, family, term, percentile, learned score, house system, sample, cusp, sub-lord, arudha, dasha,
# Shadbala, Bhava Bala, rupa), with the two the astrologer's list carries besides (ayanamsa, derivation).
CLIENT_WORDS = re.compile(r"\bvot(?:e|es|ing)\b|\bfamil(?:y|ies)\b|\bterms?\b|\bpercentiles?\b|\blearned scores?\b|"
                          r"\bhouse systems?\b|\bsampl(?:e|es|ed|er|ing)\b|\bayanamsas?\b|\bderivations?\b|"
                          r"\bcusps?\b|\bsub-?lords?\b|\barudhas?\b|\b(?:maha|antar)?dashas?\b|\bshadbala\b|"
                          r"\bbhava bala\b|\brupas?\b", re.I)
# Sanskrit words that have a plain phrase: the client's text uses the phrase (the word, with its
# phrase, is the astrologer's sheet's). "Kendra" and "trikona" inside the rule's own name
# (Kendra-Trikona Raja yoga) and "karaka" inside marana karaka sthana or chara karaka are not these.
CLIENT_PLAIN = {
    "lagna": (r"\blagna\b", "the rising sign"), "bhava": (r"\bbhavas?\b(?! bala)", "house"),
    "kendra": (r"\bkendras?\b(?!-trikona)", "angular house"), "trikona": (r"(?<!kendra-)\btrikonas?\b", "trine house"),
    "karaka": (r"(?<!marana )(?<!chara )\bkarakas?\b", "significator"), "varga": (r"\bvargas?\b", "divisional chart"),
    "rashi": (r"\brashis?\b", "sign"), "graha": (r"\bgrahas?\b", "planet"), "gochara": (r"\bgochara\b", "transit"),
    "uccha": (r"\buccha\b", "exalted"), "neecha": (r"\bneecha\b(?! bhanga)", "debilitated"),
    "swakshetra": (r"\bswakshetra\b", "own sign"),
}
# Sanskrit terms with no plain phrase: allowed in the client's text only glossed in the same sentence
# (", a combination formed when …", "(…)"), the gloss checked against the term's glossary entry.
SANSKRIT_TERMS = ("Pancha Mahapurusha yoga", "Ruchaka yoga", "Bhadra yoga", "Hamsa yoga", "Malavya yoga", "Sasa yoga",
                  "Budhaditya yoga", "Gaja Kesari yoga", "Kendra-Trikona Raja yoga", "Parivartana yoga",
                  "Dainya parivartana", "Neecha Bhanga", "moolatrikona", "Chandra lagna", "Sudarshana", "dusthana",
                  "Bhavat Bhavam", "navamsa", "dasamsa", "trimsamsa", "vargottama", "marana karaka sthana",
                  "avastha", "Mrita avastha", "nakshatra", "tara", "Vipat tara", "Pratyak tara", "Vadha tara",
                  "Jaimini", "karakamsa", "chara karaka", "panchanga", "tithi", "nitya yoga", "Upapada")
ENGLISH_ALIASES = {"exchange", "trine", "angular house", "star", "weekday", "bala", "D9", "D10", "D30"}
GLOSS_AFTER = re.compile(r"^\s*(?:yoga\b)?\s*(?:,|\(|—|–|:)\s*\S")
FIRST_PERSON = re.compile(r"\bI\b|\bI'(?:m|d|ve|ll)\b")
# A sentence that ranks or weighs evidence: in the client's text it is the reading's view, said so.
WEIGHING = re.compile(r"\b(?:more|most|greater|less) weight\b|\boutweigh\w*|\bweigh(?:s|ed|ing)?\b|"
                      r"\bcounts? for (?:more|most)\b|\bmatters? (?:more|most)\b|\btips? the balance\b", re.I)
VIEW = re.compile(r"\bthe reading's view\b", re.I)


class ClientArea(BaseModel):
    name: str
    paragraph: str | None = Field(default=None, description=(
        "What the chart says for you, in plain words: the answer in two or three sentences, then what "
        "supports it, then what works against it; no dates (they go in `when`). Every sentence ends with "
        "the tags of the accepted sentences it draws on. Null on a retry when it is held; on a retry where some of "
        "its sentences are held, only the sentences to rewrite, in the order asked."))
    when: str | None = Field(default=None, description=(
        "When, in plain words: the windows in dates and months as the accepted timing gives them, and the "
        "reading's weighing of them marked 'in the reading's view'. Every sentence tagged. Null when the "
        "area has no accepted timing, or on a retry when it is held."))


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

For each area write two parts. `paragraph`, "What the chart says for you", four to seven \
sentences in this order: the answer to the question for this area first, in two or three \
sentences; then what supports it; then what works against it or limits it. No dates or periods \
here. `when`, "When", two to five sentences: the windows the accepted timing gives, in dates and \
months, the one to avoid if it gives one, and which window the reading weighs most, marked "in the \
reading's view"; leave it null when the area has no accepted timing. Then write `summary`: two or \
three sentences answering the question across the areas, the answer first.

Every sentence ends with the tags of the accepted sentences it draws on, copied exactly \
([fact:…], [rule:…], [vote:…], [chain:…]); a sentence drawing on two cites the tags of both, and \
cites no tag the accepted text does not carry. A sentence citing a rule names the yoga or placement \
as the accepted sentence does; a sentence citing a chain names the planet and the chain (sign, \
nakshatra or navamsa) as the accepted sentence does. Each sentence is checked against what it \
cites, so say only what those sentences and facts state.

Plain words. When you name a placement or a period, say in a few words what it means. Use none of \
the engine's words: vote, family, term, percentile, learned score, house system, sample, cusp, \
sub-lord, arudha, dasha, Shadbala, Bhava Bala, rupa, ayanamsa, derivation. Where a plain phrase \
exists, use it: the rising sign (not lagna), house (not bhava), angular house (not kendra), \
significator (not karaka), divisional chart (not varga). A Sanskrit term with no plain phrase (a \
yoga's name, nakshatra, navamsa, marana karaka sthana) comes with its gloss in the same sentence, \
right after it ("Ruchaka yoga, a combination formed when Mars is in its own sign in an angular \
house, …"), the gloss matching the term's meaning. Use none of the words strong, moderate, weak or mixed and no probability or confidence \
words: the engine states the tier beside your paragraph. A window is a stretch of time the \
reading's timing favours, not a prediction of when the client will act. Nothing about death, \
illness, trades or investments, or another person's own life.

A weighing. Where the astrologer's reading weighs the evidence (the sentences in `judgements`: "I \
give more weight to …", "I read … as …"), the client's sentence that carries it says so in plain \
words, "in the reading's view", and cites the same tags: its facts are checked, the weighing is the \
reading's. Any sentence that ranks or weighs evidence says "in the reading's view". Never write \
"I"."""


def sanskrit_terms() -> list[tuple[str, re.Pattern, str]]:
    """(term, pattern over its Sanskrit aliases, definition) for SANSKRIT_TERMS, from the glossary."""
    from .narrate import glossary
    out = []
    for e in glossary():
        if e["term"] not in SANSKRIT_TERMS:
            continue
        names = [a for a in [e["term"], *e["aliases"]] if "." not in a and "_" not in a and a not in ENGLISH_ALIASES]
        names = sorted(set(names), key=len, reverse=True)
        out.append((e["term"], re.compile(r"\b(?:" + "|".join(re.escape(n) for n in names) + r")\b",
                                          0 if all(len(n) <= 3 for n in names) else re.I), e["definition"]))
    return out


def terms_in(sentence: str) -> dict[str, str]:
    """The Sanskrit terms a sentence names, each with its glossary definition (for the checker)."""
    from .narrate import HYPHENS, TAG
    bare = TAG.sub("", sentence).translate(HYPHENS)
    return {t: d for t, rx, d in sanskrit_terms() if rx.search(bare)}


def gloss_errors(s: str, bare: str) -> list[str]:
    """A Sanskrit term the client's text uses: refused where a plain phrase exists (CLIENT_PLAIN), and
    otherwise glossed in the same sentence, right after it (GLOSS_AFTER)."""
    errors = []
    for word, (rx, plain) in CLIENT_PLAIN.items():
        if (m := re.search(rx, bare, re.I)):
            errors.append(f"{m.group(0)!r} has a plain phrase: say {plain!r} in the client's text: {s!r}")
    for term, rx, _ in sanskrit_terms():
        for m in rx.finditer(bare):
            if not GLOSS_AFTER.match(bare[m.end():]):
                errors.append(f"{m.group(0)!r} is a Sanskrit term: gloss it in the same sentence, right after it "
                              f"(', a …' or '(…)'), or use a plain phrase: {s!r}")
                break
    return errors


DATE = re.compile(r"\b(?:19|20)\d{2}\b")


def client_errors(text: str | None, accepted: set[str] | None = None, dates: bool = True) -> list[str]:
    """The client's words: no engine vocabulary, a Sanskrit term glossed or replaced by its plain
    phrase, no "I", a weighing marked as the reading's view, and (the paragraph, the when and the
    summary, `accepted` the tags of the accepted text they draw on) every sentence tagged with tags
    from that text only. `dates` False (the paragraph): no date, which belongs under When."""
    from .narrate import HYPHENS, TAG, TRADITION, sentences
    errors = []
    for s in sentences(text or ""):
        bare = TRADITION.sub("", TAG.sub("", s)).translate(HYPHENS)
        tags = {f"{k}:{v}" for k, v in TAG.findall(s)}
        if (m := CLIENT_WORDS.search(bare)):
            errors.append(f"engine vocabulary ({m.group(0)!r}) in the client's text: say it in plain words: {s!r}")
        errors += gloss_errors(s, bare)
        if not dates and (m := DATE.search(bare)):
            errors.append(f"a date ({m.group(0)!r}) in 'What the chart says for you': dates go under When: {s!r}")
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
          recording: list | None, progress: Callable[[str, dict], None], live=None,
          want: str = "all") -> dict[str, Any]:
    """The client's layer: up to `max_attempts` calls; each paragraph and the summary that passes the
    validator is checked in its attempt and held once it passes, and a retry asks only for the failed
    ones with their reasons. Returns {summary, summary_error, paragraphs, para_errors, writer_metas,
    checker_metas, attempts}; a unit that never passed is None with its last error.

    `want` (the live narration, 2026-10-26): "all"; "areas", each area's paragraph and when, the
    summary left to a later call; "summary", the summary alone from every area's accepted text.
    `live` (jyotish.live.Live) is shown each unit as it streams, is validated and is checked."""
    from .live import HeldParagraph
    from .narrate import (PARAGRAPH_RETRY_NOTE, RETRY_HEAD, NarrationError, _cited_facts, _summary_checks,
                          name_hint, paragraph_units, retry_instruction, validate_summary)
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
    need_summary = want != "areas"
    unit_names = names if want != "summary" else []
    if want == "areas":
        user += ("\n\nThis call writes each area's paragraph and when only. Leave `summary` empty: it is written "
                 "last, from every area's accepted text.")
    elif want == "summary":
        user += ("\n\nThis call writes the summary only, across the areas above. Leave every area's `paragraph` "
                 "and `when` null: they are written and held.")
    all_votes: dict[str, set[str]] = {}
    for n in names:
        for fam, tag in votes[n].items():
            all_votes.setdefault(fam, set()).add(tag)
    all_chains = {k: v for n in names for k, v in chains[n].items()}
    summary = summary_error = None
    paragraphs: dict[str, str] = {}
    para_errors: dict[str, tuple[str, int]] = {}
    # Each paragraph held sentence by sentence (2026-10-31): a retry rewrites only its failed sentences.
    held_paras: dict[str, HeldParagraph] = {n: HeldParagraph() for n in unit_names}
    whens: dict[str, str] = {}
    when_errors: dict[str, tuple[str, int]] = {}
    timed = [n for n in unit_names if accepted[n].get("timing")]  # an area with accepted timing has a When
    writer_metas: list = []
    checker_metas: list = []
    errors: list[str] = []
    attempts = 0
    for attempts in range(1, max_attempts + 1):
        progress("client", {"attempt": attempts})
        if live is not None and hasattr(drafter, "on_text"):
            def skip(u: str) -> bool:
                if u.startswith("paragraph:"):
                    name, _, key = u[10:].partition(":")
                    return name not in unit_names or held_paras[name].complete() or key in held_paras[name].held
                return ((u == "summary" and (not need_summary or summary is not None))
                        or (u.startswith("when:") and (u[5:] in whens or u[5:] not in timed)))
            drafter.on_text = live.draft_stream(skip, paragraphs=held_paras)
        try:
            draft = drafter(CLIENT_PROMPT, user, errors)
        except NarrationError as e:
            writer_metas.append(getattr(drafter, "last_meta", None))
            errors = [str(e)] + list(e.errors)
            if recording is not None:
                recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "client"}, attempt=attempts,
                                      client_draft=None, validator_errors=[], writer_error=errors))
            summary_error = summary_error or (errors[0], attempts)
            for n in unit_names:
                if not held_paras[n].complete():
                    para_errors[n] = (errors[0], attempts)
            for n in timed:
                if n not in whens:
                    when_errors[n] = (errors[0], attempts)
            if "recording has no client draft" in str(e):
                break                                   # a replay made before the client layer: nothing to retry
            continue
        writer_metas.append(getattr(drafter, "last_meta", None))
        units: dict[str, tuple[str, list[str]]] = {}     # label -> (text, validator errors)
        if need_summary and summary is None:
            text = draft.summary or ""
            errs = (validate_summary(text, all_tags, offered_votes=all_votes, family_rule=False, chains=all_chains,
                                     facts=facts, judgements=True) + client_errors(text, all_tags)
                    if text.strip() else ["no summary: it is not held, so the draft needs one"])
            units["client:summary"] = (text, errs)
        placed: dict[str, list[str]] = {}               # area -> the keys of this draft's sentences
        for n in unit_names:
            hp = held_paras[n]
            if hp.complete():
                continue
            text = next((a.paragraph for a in draft.areas if a.name == n), None) or ""
            placed[n] = []
            for k, sentence in hp.place(text):
                errs = (validate_summary(sentence, area_tags[n], offered_votes=votes[n], where=f"{n} paragraph",
                                         family_rule=False, chains=chains[n], facts=facts, judgements=True)
                        + client_errors(sentence, area_tags[n], dates=False))
                units[f"client:paragraph:{n}:{k}"] = (sentence, errs)
                placed[n].append(k)
            if not hp.slots:
                units[f"client:paragraph:{n}"] = ("", [f"no paragraph for {n}: every area has one"])
        for n in timed:
            if n in whens:
                continue
            text = next((a.when for a in draft.areas if a.name == n), None) or ""
            errs = (validate_summary(text, area_tags[n], offered_votes=votes[n], where=f"{n} when",
                                     family_rule=False, chains=chains[n], facts=facts, judgements=True)
                    + client_errors(text, area_tags[n])
                    if text.strip() else [f"no when for {n}: an area with accepted timing has one"])
            units[f"client:when:{n}"] = (text, errs)
        if recording is not None:
            recording.append(dict(getattr(drafter, "last_meta", None) or {"kind": "client"}, attempt=attempts,
                                  client_draft=draft.model_dump(),
                                  validator_errors=[e for _, es in units.values() for e in es]))
        checks = [(s, ids, with_glosses(s, data), label) for label, (text, errs) in units.items() if not errs
                  for s, ids, data in _summary_checks(text, finding_data, facts)]
        if live is not None:
            for label, (text, errs) in units.items():
                if errs:
                    live.removed(label[7:], "the validator")
                elif text:
                    live.text(label[7:], text)
            for s, _, data, label in checks:
                live.watch(label[7:], s, data)
        progress("client check", {"attempt": attempts, "calls": len(checks)})
        from .live import SharedChecker, unit_area
        if isinstance(checker, SharedChecker):          # each check for its unit's area, as the stream keyed it
            outcomes = checker.check_many([(s, data) for s, _, data, _ in checks],
                                          owners=[unit_area(label[7:]) for _, _, _, label in checks])
        elif hasattr(checker, "check_many"):
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
            if label.count(":") == 3:                      # one sentence of a paragraph held sentence by sentence
                name, key = label.split(":")[2:]
                if live is not None:
                    (live.removed(label[7:], "the checker" if not errs else "the validator") if why
                     else live.accepted(label[7:]))
                held_paras[name].fail(key, why) if why else held_paras[name].hold(key)
                continue
            kind = label.split(":")[1]                     # summary | paragraph | when
            name = label.split(":")[2] if kind != "summary" else None
            unit = "the summary" if name is None else f"the {name} {kind}"
            store, errs_of = {"paragraph": (paragraphs, para_errors), "when": (whens, when_errors)}.get(kind, (None, None))
            if live is not None:
                (live.removed(label[7:], "the checker") if why else live.accepted(label[7:]))
            if why:
                failed[unit] = why
                if name is None:
                    summary_error = (why[0], attempts)
                else:
                    errs_of[name] = (why[0], attempts)
            elif name is None:
                summary, summary_error = text, None
            else:
                store[name] = text
                errs_of.pop(name, None)
        for n in placed:
            hp = held_paras[n]
            if hp.text() is not None:
                paragraphs[n] = hp.text()
            if hp.complete():
                para_errors.pop(n, None)
            else:
                failed.update(paragraph_units(n, hp))
                if hp.failed():
                    para_errors[n] = (hp.failed()[0][3][0], attempts)
        if live is not None:                           # a unit shown but never decided on is withdrawn (review R8)
            live.sweep(tuple(f"paragraph:{n}" for n in unit_names) + tuple(f"when:{n}" for n in timed)
                       + (("summary",) if need_summary else ()))
        if not failed:
            break
        held = (["the summary"] if summary is not None or not need_summary else []) + \
            [f"the {n} paragraph" if held_paras[n].complete() else
             f"the {n} paragraph's other sentences ({len(held_paras[n].held)} of {len(held_paras[n].keys())})"
             for n in unit_names if held_paras[n].held] + \
            [f"the {n} when" for n in whens]
        partial = any(hp.held and not hp.complete() for hp in held_paras.values())
        errors = [retry_instruction(held, {u: [name_hint(x, finding_data) for x in why] for u, why in failed.items()},
                                    [PARAGRAPH_RETRY_NOTE] if partial else None)]
        assert errors[0].startswith(RETRY_HEAD)
    return {"summary": summary, "summary_error": summary_error, "paragraphs": paragraphs,
            "para_errors": {n: e for n, e in para_errors.items() if not held_paras.get(n, HeldParagraph()).complete()},
            "para_open": sorted(n for n, hp in held_paras.items() if hp.held and not hp.complete()),
            "whens": whens, "when_errors": {n: e for n, e in when_errors.items() if n not in whens},
            "writer_metas": writer_metas, "checker_metas": checker_metas, "attempts": attempts,
            "facts": _cited_facts(" ".join([summary or ""] + list(paragraphs.values()) + list(whens.values())), facts)}


def with_glosses(sentence: str, data: str) -> str:
    """The checker's data for a client sentence, with the glossary definition of each Sanskrit term
    it names, so its gloss is checked against the definition (the checker's prompt says how)."""
    terms = terms_in(sentence)
    if not terms:
        return data
    d = json.loads(data)
    d["glossary"] = dict(d.get("glossary") or {}, **terms)
    return json.dumps(d, indent=1, default=str)
