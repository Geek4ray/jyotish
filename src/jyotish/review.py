"""The review step (SPEC Layer 6b, order of work item 3): before a reading reaches a client a
practising astrologer reads it, may edit any sentence and may add a note per area.

An edited sentence is held to the same checks as the writer's: the validator (tags offered for
its finding, rule names, forbidden words, tier words in summaries and paragraphs, and the
family-name rule except at curious depth), then the semantic checker against the derivations
it cites. Only a sentence that passes both replaces the old one. A note is the astrologer's
own words: never checked, stored apart, and shown as "the astrologer's note", visibly distinct
from checked text. The API (api.py) logs every open, edit, note and approval in the reviews
table and puts the chart into the exclusions table, which the Layer 6b learning set respects:
a chart whose reading the judge has seen is never blind again.

Targets name what is edited: "summary:<i>" (the i-th sentence of the summary),
"claim:<area>:<finding id>", "paragraph:<area>:<i>" (the i-th sentence of a curious paragraph).

The guided review (web/review.html) asks its questions one step at a time and logs every answer
(`check_answer` says which answers each step takes), each with an optional comment in the
reviewer's own words; a last step asks about the reading as a whole. Answers and comments are
judgement data: never shown to the client, never checked. Its words are an astrologer's: the chart
facts beside a sentence (`facts`) and the reasons an edit is refused (`plain_reasons`) are
written without the engine's own vocabulary; a rewrite that leans on another sentence ("again", an
opening "The same") is refused with the code `reference`. In blind mode (the judge page) an area's
paragraph and windows are withheld (`redact`) until the reviewer has answered from the chart alone."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any, Callable

from .models import Chart
from .narrate import (_ORD, TAG, CheckResult, Reading, _check_payload, _summary_checks, findings, offered_chains,
                      offered_votes, rule_names, sentences, validate, validate_summary)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def units(reading: Reading) -> list[dict[str, Any]]:
    """Every sentence a reviewer can edit, with its target."""
    out = [{"target": f"summary:{i}", "area": None, "kind": "summary", "text": s}
           for i, s in enumerate(sentences(reading.summary.text))]
    for a in reading.areas:
        out += [{"target": f"claim:{a.name}:{c.finding_id}", "area": a.name, "kind": "claim", "text": c.text}
                for c in a.claims]
        if a.paragraph:
            out += [{"target": f"paragraph:{a.name}:{i}", "area": a.name, "kind": "paragraph", "text": s}
                    for i, s in enumerate(sentences(a.paragraph))]
    return out


def _parse(target: str) -> tuple[str, str | None, str]:
    kind, _, rest = target.partition(":")
    if kind == "summary":
        return kind, None, rest
    area, _, key = rest.partition(":")
    if kind not in ("claim", "paragraph") or not area or not key:
        raise ValueError(f"unknown target {target!r}")
    return kind, area, key


def check_edit(reading: Reading, chart: Chart, target: str, text: str,
               checker: Callable[[str, str], CheckResult]) -> dict[str, Any]:
    """Validator, then checker, on an edited sentence. Returns {accepted, errors, checks}."""
    kind, area, key = _parse(target)
    text = text.strip()
    names = [a.name for a in reading.areas]
    family_rule = reading.depth != "curious"
    if area is not None and area not in names:
        raise ValueError(f"no area {area!r} in this reading")
    as_of = date.fromisoformat(reading.as_of)
    offered = {name: findings(chart, name, as_of)[0] for name in names}
    data_by_id = {f["finding_id"]: f for fs in offered.values() for f in fs}
    votes = offered_votes(chart, names)
    chains = offered_chains(chart, names)
    if kind == "claim":
        f = next((x for x in offered[area] if x["finding_id"] == key), None)
        if f is None:
            raise ValueError(f"no finding {key!r} in {area}")
        errors = validate(text, set(f["allowed_tags"]), offered_votes=votes[area], family_rule=family_rule,
                          chains=chains[area])
        if not TAG.search(text):
            errors.append(f"claim without a tag: {text!r}")
        to_check = [(text, [key], _check_payload(f))]
    else:
        scope = [area] if kind == "paragraph" else names
        tags = set().union(*(set(f["allowed_tags"]) for n in scope for f in offered[n]))
        fam = votes[area] if kind == "paragraph" else {k: {v} for n in names for k, v in votes[n].items()}
        # Depth full: the paragraph and the summary are the client's layer: a sentence may cite the
        # whole chart's facts and keeps to the client's words (jyotish.client), as the writer's did.
        full = reading.depth == "full"
        facts = None
        if full:
            from .fullchart import payload
            from .narrate import full_range
            facts = payload(chart, as_of, *full_range(as_of), names)
        errors = validate_summary(text, tags, offered_votes=fam, where=f"{area} paragraph" if area else "summary",
                                  family_rule=family_rule and kind == "summary" and not full,
                                  chains=chains[area] if area else {k: v for n in names for k, v in chains[n].items()},
                                  facts=facts, judgements=full)
        if full:
            from .client import client_errors
            errors += client_errors(text, dates=kind != "paragraph")      # a paragraph's dates go under When
        scope_data = {fid: f for fid, f in data_by_id.items() if any(fid == x["finding_id"] for n in scope for x in offered[n])}
        to_check = _summary_checks(text, scope_data, facts)
    checks = []
    reasons = plain_reasons(errors)
    if not errors:
        for sentence, ids, data in to_check:
            result = checker(sentence, data)
            checks.append({"sentence": sentence, "findings": ids, "result": result.model_dump()})
            errors += [f"unsupported: {p.text!r} ({p.evidence})" for p in result.propositions if not p.supported]
            reasons += [{"code": "unsupported", "detail": p.text} for p in result.propositions if not p.supported]
    return {"accepted": not errors, "errors": errors, "reasons": reasons, "checks": checks}


def with_tags(before: str, text: str) -> str:
    """A rewrite in plain words carrying the tags of the sentence it replaces, so it is checked
    against the same findings (a rewrite that writes its own tags keeps them)."""
    text = text.strip()
    tags = [m.group(0) for m in TAG.finditer(before)]
    if not tags or TAG.search(text):
        return text
    end = text[-1] if text and text[-1] in ".!?" else "."
    return f"{text.rstrip('.!? ')} {' '.join(tags)}{end}"


# --- refusals in plain words ------------------------------------------------------------------

def plain_reasons(errors: list[str]) -> list[dict[str, str]]:
    """The validator's errors as codes the review page words for an astrologer (web/js/strings.js):
    timing, probability, confidence, death, medical, trade, third_party (a forbidden word, with the
    word), tier (a strength word), name (the combination the sentence must name), reference (a word
    that leans on another sentence), other."""
    out = []
    for e in errors:
        m = re.match(r"(\w+) language \((['\"])(.*?)\2\)", e)
        if m and m.group(1) == "tier":
            out.append({"code": "tier", "detail": m.group(3)})
        elif m:
            out.append({"code": m.group(1), "detail": m.group(3)})
        elif (m := re.match(r"\[rule:([^\]]+)\] on a sentence that names none of", e)):
            out.append({"code": "name", "detail": rule_names(m.group(1))[0]})
        elif (m := re.match(r"refers to another claim \('(.+?)'\)", e)):
            out.append({"code": "reference", "detail": m.group(1)})
        else:
            out.append({"code": "other", "detail": ""})
    seen, uniq = set(), []
    for r in out:
        if (r["code"], r["detail"]) not in seen:
            seen.add((r["code"], r["detail"]))
            uniq.append(r)
    return uniq


# --- the chart facts a sentence rests on ------------------------------------------------------

def _o(n: int) -> str:
    return _ORD.get(n, str(n))


def _joined(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def _rule_facts(f: dict) -> list[str]:
    pl = f.get("placement")
    if pl and "lagna_sign" in pl:
        return [f"{pl['lagna_sign']} rising, its lord {pl['lagna_lord']}"]
    if pl and "nakshatra" in pl:
        return [f"{pl['planet']} in {pl['nakshatra']}"]
    if pl and "sign" in pl:
        return [f"{pl['planet']} in {pl['sign']}"]
    if pl:
        lord = f", lord of the {_joined([_o(h) for h in pl['lord_of']])}," if pl.get("lord_of") else ""
        return [f"{pl['planet']}{lord} in the {_o(pl['house'])}"]
    from .narrate import glossary
    name = next((e["term"] for e in glossary() if f["rule_id"] in e["aliases"]), None) or rule_names(f["rule_id"])[0]
    name = name if "yoga" in name.lower() else f"{name} yoga"
    planets = list(dict.fromkeys(n for fire in f["fires"] for n in fire["nodes"] if not n.startswith("H")))
    line = f"{name[0].upper()}{name[1:]}, formed by {_joined(planets)}" if planets else name
    houses = [x["words"] for x in f.get("area_houses", [])]
    return [line + (f": {'; '.join(houses)}" if houses else "")]


def _vote_facts(f: dict) -> list[str]:
    fam, d = f["family"], f.get("derivation")
    rows = d if isinstance(d, list) else []
    lagna = [r for r in rows if r.get("basis", "lagna") == "lagna"]
    out: list[str] = []
    if fam == "house":
        out = [f"The {_o(r['house'])} house ({r['sign']}): house strength {r['bhava_bala_rupas']:g} rupas"
               for r in lagna if "bhava_bala_rupas" in r]
    elif fam == "lord":
        out = [f"{r['lord']}, lord of the {_o(r['house'])} ({r['sign']}), in {r['lord_sign']} in the "
               f"{_o(r['lord_house_from_lagna'])}, {r['dignity']}" for r in lagna if "lord" in r]
    elif fam == "karaka":
        out = [f"{r['planet']}, a significator, in the {_o(r['house'])} ({r['sign']}), {r['dignity']}"
               for r in lagna if "planet" in r]
    elif fam == "varga":
        out = [f"{r['planet']} in {r['varga']} {r['varga_sign']}" + (f", {r['varga_dignity_label']}" if r.get("varga_dignity_label") else "")
               + (" (vargottama)" if r.get("vargottama_d9") else "") for r in rows if "varga_sign" in r]
    elif fam == "arudha":
        pads = (d or {}).get("padas", []) if isinstance(d, dict) else rows
        out = [f"{x['pada']} in the {_o(x['house'])} ({x['sign']})" +
               (f", with {_joined(x['occupants'])}" if x.get("occupants") else "") for x in pads if "pada" in x]
        mks = (d or {}).get("marana_karaka_sthana", []) if isinstance(d, dict) else []
        out += [f"{x['planet']} in the {_o(x['house'])}, a marana karaka sthana" for x in mks if x.get("basis") == "lagna"]
    elif fam == "kp":
        cusps = dict.fromkeys(f"The {_o(r['cusp'])} cusp: star lord {r['cusp_star']}, sub-lord {r['sub']}"
                              for r in rows if "cusp" in r)
        out = list(cusps) + [f"{r['planet']} ({r['level']}) signifies the {_joined([_o(h) for h in r['significations']])}"
                             for r in rows if r.get("decides")]
    elif fam == "panchanga":
        out = [f"{r['planet']} rules the {_joined(r['role'])}" + (
               f" and the {_joined([_o(x['house']) for x in r['rules'] if x['basis'] == 'lagna'])}"
               if any(x["basis"] == "lagna" for x in r.get("rules", [])) else "") for r in rows if "planet" in r]
    lean = {"for": "Leans in favour", "against": "Leans against"}.get(f.get("direction"))
    return out + ([lean] if lean else [])


def finding_facts(f: dict) -> list[str]:
    """A finding's chart facts in an astrologer's words (planets, houses, signs, dignities)."""
    if f["kind"] == "chain":
        return list(f["facts"])
    return _rule_facts(f) if f["kind"] == "rule" else _vote_facts(f)


def facts(chart: Chart, areas: list[str], as_of: date | None = None) -> dict[str, list[tuple[set[str], list[str]]]]:
    """area -> [(the finding's citation tags, its facts)] for every finding offered."""
    return {a: [({t for t in f["allowed_tags"] if not t.startswith("text:")}, finding_facts(f))
                for f in findings(chart, a, as_of)[0]] for a in areas}


def sentence_facts(text: str, area_facts: list[tuple[set[str], list[str]]]) -> list[str]:
    """The chart facts a sentence rests on: those of every finding whose tags it cites."""
    tags = {f"{k}:{v}" for k, v in TAG.findall(text)}
    out: list[str] = []
    for ftags, lines in area_facts:
        if ftags & tags:
            out += [x for x in lines if x not in out]
    return out


def plain(text: str) -> str:
    """A sentence as the reviewer reads it: without its citation tags."""
    return re.sub(r"\s+([.!?])", r"\1", TAG.sub("", text)).strip()


# --- the guided review's answers --------------------------------------------------------------

MODES = ("review", "blind")
TEXT_MAX = 4000       # a note, the reading as a whole, a comment: the reviewer's own words
LINE_MAX = 400        # the one line of what is off
OFF = ("missing_combination", "weight", "timing", "wording", "other")
PERIOD = ("yes", "earlier", "later", "different")
OWN_READING = ("promising", "mixed", "difficult")
AREA_STEPS = ("blind_reading", "blind_period", "match", "off", "sentences", "note", "period")
STEPS = ("intro",) + AREA_STEPS + ("whole",)      # whole: "Anything about the reading as a whole?"


def _month(x: Any) -> str:
    if not isinstance(x, str) or not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", x):
        raise ValueError("a date is YYYY-MM or YYYY-MM-DD")
    date.fromisoformat(x if len(x) == 10 else x + "-01")
    return x


def _range(answer: dict) -> None:
    a, b = _month(answer.get("from")), _month(answer.get("to"))
    if b < a:
        raise ValueError("the range ends before it starts")


def check_answer(step: str, answer: Any) -> None:
    """Raises ValueError unless `answer` is one the step takes."""
    if step not in STEPS:
        raise ValueError(f"unknown step {step!r}")
    if step == "intro":
        ok = answer == "done"
    elif step == "blind_reading":
        ok = answer in OWN_READING
    elif step == "match":
        ok = answer in ("agree", "partly", "disagree")
    elif step == "blind_period":
        if not isinstance(answer, dict):
            raise ValueError("a period is {from, to}")
        _range(answer)
        ok = True
    elif step == "off":
        ok = (isinstance(answer, dict) and isinstance(answer.get("reasons"), list) and answer["reasons"]
              and set(answer["reasons"]) <= set(OFF) and isinstance(answer.get("line", ""), str)
              and len(answer.get("line", "")) <= LINE_MAX)
    elif step == "sentences":
        ok = isinstance(answer, dict) and all(v in ("keep", "rewritten") for v in answer.get("decisions", {}).values())
    elif step in ("note", "whole"):
        ok = isinstance(answer, dict) and isinstance(answer.get("text"), str) and len(answer["text"]) <= TEXT_MAX
    else:                                                                   # period
        ok = isinstance(answer, dict) and answer.get("choice") in PERIOD
        if ok and answer["choice"] != "yes":
            _range(answer)
    if not ok:
        raise ValueError(f"not an answer the {step} step takes")


def revealed(areas: list[dict], answers: list[dict]) -> set[str]:
    """In blind mode, the areas whose reading may be shown: the reviewer has answered from the
    chart alone (their own reading, and their own best period where the area has windows)."""
    have = {(a["area"], a["step"]) for a in answers if a["mode"] == "blind"}
    return {a["name"] for a in areas if (a["name"], "blind_reading") in have and
            (not a.get("windows") or (a["name"], "blind_period") in have)}


def redact(reading: dict, shown: set[str]) -> dict:
    """The reading as the blind page may see it: an area not yet shown keeps only its name and
    whether it has windows; the summary, which speaks across areas, waits for all of them."""
    areas = [a if a["name"] in shown else {"name": a["name"], "has_windows": bool(a.get("windows")), "hidden": True}
             for a in reading["areas"]]
    keep = {"question", "as_of", "depth", "chart", "review"}
    out = {k: v for k, v in reading.items() if k in keep}
    if len(shown) == len(reading["areas"]):
        out["summary"] = reading["summary"]
    return dict(out, areas=areas)


def apply_edit(reading: Reading, target: str, text: str, reviewer: str) -> Reading:
    """The reading with an accepted edit in place (cites recomputed, the edit recorded)."""
    kind, area, key = _parse(target)
    text = text.strip()
    stamp = {"by": reviewer, "at": now()}
    cites = lambda t: [f"{k}:{v}" for k, v in TAG.findall(t)]
    edits = list(reading.review.get("edits", [])) + [dict(stamp, target=target)]
    review = dict(reading.review, edits=edits)
    if kind == "summary":
        parts = sentences(reading.summary.text)
        parts[int(key)] = text
        joined = " ".join(parts)
        summary = reading.summary.model_copy(update={"text": joined, "cites": cites(joined),
                                                     "source": "model" if reading.summary.source == "model" else "edited"})
        return reading.model_copy(update={"summary": summary, "review": review})
    areas = []
    for a in reading.areas:
        if a.name == area and kind == "claim":
            a = a.model_copy(update={"claims": [c.model_copy(update={"text": text, "cites": cites(text), "edited": stamp})
                                                if c.finding_id == key else c for c in a.claims]})
        elif a.name == area and kind == "paragraph":
            parts = sentences(a.paragraph or "")
            parts[int(key)] = text
            joined = " ".join(parts)
            a = a.model_copy(update={"paragraph": joined, "paragraph_cites": cites(joined)})
        areas.append(a)
    return reading.model_copy(update={"areas": areas, "review": review})


def add_note(reading: Reading, area: str, text: str, reviewer: str) -> Reading:
    """The astrologer's note on an area (replacing an earlier one); empty text removes it."""
    if area not in [a.name for a in reading.areas]:
        raise ValueError(f"no area {area!r} in this reading")
    note = {"text": text.strip(), "by": reviewer, "at": now()} if text.strip() else None
    return reading.model_copy(update={"areas": [a.model_copy(update={"astrologer_note": note}) if a.name == area else a
                                                for a in reading.areas]})


def approve(reading: Reading, reviewer: str) -> Reading:
    return reading.model_copy(update={"review": dict(reading.review, status="reviewed", reviewed_by=reviewer,
                                                     reviewed_at=now())})
