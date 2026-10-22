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
"claim:<area>:<finding id>", "paragraph:<area>:<i>" (the i-th sentence of a curious paragraph)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from .models import Chart
from .narrate import (TAG, CheckResult, Reading, _check_payload, _summary_checks, findings, offered_votes,
                      sentences, validate, validate_summary)


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
    offered = {name: findings(chart, name)[0] for name in names}
    data_by_id = {f["finding_id"]: f for fs in offered.values() for f in fs}
    votes = offered_votes(chart, names)
    if kind == "claim":
        f = next((x for x in offered[area] if x["finding_id"] == key), None)
        if f is None:
            raise ValueError(f"no finding {key!r} in {area}")
        errors = validate(text, set(f["allowed_tags"]), offered_votes=votes[area], family_rule=family_rule)
        if not TAG.search(text):
            errors.append(f"claim without a tag: {text!r}")
        to_check = [(text, [key], _check_payload(f))]
    else:
        scope = [area] if kind == "paragraph" else names
        tags = set().union(*(set(f["allowed_tags"]) for n in scope for f in offered[n]))
        fam = votes[area] if kind == "paragraph" else {k: {v} for n in names for k, v in votes[n].items()}
        errors = validate_summary(text, tags, offered_votes=fam, where=f"{area} paragraph" if area else "summary",
                                  family_rule=family_rule and kind == "summary")
        scope_data = {fid: f for fid, f in data_by_id.items() if any(fid == x["finding_id"] for n in scope for x in offered[n])}
        to_check = _summary_checks(text, scope_data)
    checks = []
    if not errors:
        for sentence, ids, data in to_check:
            result = checker(sentence, data)
            checks.append({"sentence": sentence, "findings": ids, "result": result.model_dump()})
            errors += [f"unsupported: {p.text!r} ({p.evidence})" for p in result.propositions if not p.supported]
    return {"accepted": not errors, "errors": errors, "checks": checks}


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
