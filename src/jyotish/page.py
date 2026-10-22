"""The Markdown page for a reading (`jyotish read`). Everything on it is the engine's: the
model's sentences appear verbatim as claims and summary, their tags become footnotes, and
every number, table and derivation is rendered here from the chart and the Reading, never
by the model.

Order: the summary with its engine fields; each area (the question's, then the chart's top
three) with tier, the three stability numbers, polarity and its touches, the claims in engine
order, school conflicts, the windows and the avoid window; "depends on exact birth time";
a learner section per claim with its finding's derivation as a table; disclaimers."""

from __future__ import annotations

import json
from typing import Any

from .models import Chart
from .narrate import DISCLAIMERS, SUDARSHANA_NOTE, TAG, Reading, ReadingWindow, findings, learner_data, timing_line
from .rules import default_rules
from .uncertainty import label

SENSITIVE_BELOW = 0.8      # a claim under this time-stability is marked where it is read


class _Notes:
    """Tags -> numbered footnotes, one number per distinct tag across the page."""

    def __init__(self, chart: Chart):
        self.order: list[str] = []
        self.names = {r.id: (r.data.get("names") or [r.id])[0] for r in default_rules()}
        self.chart = chart

    def render(self, text: str) -> str:
        def sub(m):
            tag = f"{m.group(1)}:{m.group(2)}"
            if tag not in self.order:
                self.order.append(tag)
            return f"[^{self.order.index(tag) + 1}]"
        return TAG.sub(sub, text).replace(" [^", "[^")

    def definition(self, tag: str) -> str:
        kind, value = tag.split(":", 1)
        if kind == "rule":
            return f"Rule `{value}` ({self.names.get(value, value)}), from the engine's rule library."
        if kind == "text":
            text, edition, chapter, verse = value.split("/")
            return f"{text}, {edition.replace('-', ' ')}, chapter {chapter}, verse {verse} (checked in that edition)."
        area, family = value.split(".", 1)
        return f"The {_family(family)} family's vote on {area.replace('_', ' ')}, derived by the engine (learner table below)."

    def block(self) -> list[str]:
        return [f"[^{i}]: `{t}`: {self.definition(t)}" for i, t in enumerate(self.order, 1)]


def _family(name: str) -> str:
    return "KP" if name == "kp" else name


def _cell(v: Any) -> str:
    if v is None:
        return "–"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.3g}"
    if isinstance(v, list):
        return ", ".join(_cell(x) if not isinstance(x, dict) else _compact(x) for x in v) or "–"
    if isinstance(v, dict):
        return _compact(v)
    return str(v).replace("|", "\\|")


def _compact(d: dict) -> str:
    return " ".join(f"{k} {_cell(v)}" for k, v in d.items())


def _table(rows: list[dict], columns: list[str] | None = None) -> list[str]:
    if not rows:
        return ["(no rows)"]
    cols = columns or list(dict.fromkeys(k for r in rows for k in r))
    out = ["| " + " | ".join(c.replace("_", " ") for c in cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_cell(r.get(c)) for c in cols) + " |" for r in rows]
    return out


def _claim(notes: "_Notes", c) -> str:
    """The claim with its tags as footnotes and, under 0.8 time-stability, the number inline."""
    text = notes.render(c.text)
    if c.stability is not None and c.stability < SENSITIVE_BELOW:
        text += f" *(time-stability {c.stability:.3g}, {c.stability_label or label(c.stability)})*"
    return text


def _header(chart: dict) -> list[str]:
    if not chart:
        return []
    c = chart.get("conventions", {})
    place = chart.get("place") or "place not named"
    local = (f"{chart['local_date']} {chart['local_time']} ({chart['tz_input']})" if chart.get("local_date")
             else "local time not given")
    year = c.get("dasha_year")
    out = [f"**Chart:** born {local} = {chart['birth_utc']} UTC, {place} ({chart['lat']}, {chart['lon']}); "
           f"accuracy {chart['accuracy']}; ayanamsa {c.get('ayanamsa')} ({chart['ayanamsa_value']:.4f}°); "
           f"node {c.get('node')}; houses {c.get('house_system')} (KP {c.get('kp_house_system')}); "
           f"dasha year {year:g} days; karaka scheme {c.get('karaka_scheme')}."]
    shown = {"ayanamsa", "node", "house_system", "kp_house_system", "dasha_year", "karaka_scheme"}
    rest = ", ".join(f"{k} {_cell(v)}" for k, v in c.items() if k not in shown)
    out += ["", f"Other settings: {rest}."]
    sm = chart.get("sampler")
    if sm:
        seed = f", seed {chart['seed']}" if chart.get("seed") is not None else ""
        out += ["", f"Stability sampler: {sm['samples']} birth times, {sm['shape']} ±{sm['half_width_min']:g} min{seed}; "
                    f"ayanamsas {', '.join(sm['ayanamsas'])}; houses {', '.join(sm['house_systems'])}."]
    if chart.get("command"):
        out += ["", f"Reproduce: `{chart['command']}`"]
    return out + [""]


def _stab(st) -> str:
    return f"time {st.time:.2f} · ayanamsa {st.ayanamsa:.2f} · house {st.house:.2f} ({st.label})" if st else "–"


def _window_rows(ws: list[ReadingWindow], avoid: ReadingWindow | None) -> list[str]:
    rows = []
    for label, w in [("window", w) for w in ws] + ([("avoid", avoid)] if avoid else []):
        sp = w.strongest_piece
        rows.append({"": label, "start": w.start, "end": w.end, "score": w.score, "q": w.q, "t": w.t,
                     "systems": w.relevant_systems,
                     "strongest piece": f"{sp['start']} – {sp['end']} (score {sp['score']:.3g}, t {sp['t']:.3g})" if sp else None,
                     "edge movement (days)": w.stability, "sandhi": w.sandhi, "truncated": w.truncated})
    return _table(rows)


def _rule_learner(d: dict) -> list[str]:
    r = d["rule"]
    out = [f"Rule block (`{r['id']}`, school {r['school']}, status {r['status']}, "
           f"confidence base {r['confidence_base']}):", ""]
    out += _table([{"condition": k, "value": json.dumps(v, default=str)} for k, v in r["when"].items()])
    out += ["", "Modifiers, and where each applied:", ""]
    out += _table([{"modifier": m["modifier"], "scale": f"×{m['scale']}",
                    **{f"from {b}": v for b, v in m["applied"].items()}} for m in d["modifiers"]])
    out += ["", "Fires:", ""]
    out += _table([{"basis": x["basis"], "nodes": x["nodes"], "scale": x["scale"], "stability": x["stability"],
                    "cited to": x["cited_to"], "sudarshana": x["sudarshana"]} for x in d["fires"]])
    if d.get("sudarshana_bases"):
        out += ["", f"Sudarshana: the fire from the {' and the '.join(b.capitalize() for b in d['sudarshana_bases'])} "
                + SUDARSHANA_NOTE]
    return out


def derivation_table(d: Any) -> list[str]:
    """A vote's derivation as Markdown. Two shapes occur: a list of rows (house, lord, karaka,
    varga, KP, panchanga) and a dict of named row lists (arudha: `padas`, or
    `marana_karaka_sthana` where the arudha vote reads the 8th from the lagna)."""
    if not d:
        return ["(no derivation rows)"]
    if isinstance(d, list):
        return _table(d)
    if isinstance(d, dict):
        out: list[str] = []
        for k, v in d.items():
            if out:
                out.append("")
            if isinstance(v, list) and all(isinstance(r, dict) for r in v):
                out += [f"{k.replace('_', ' ')}:", ""] + (_table(v) if v else ["(no rows)"])
            else:
                out.append(f"{k.replace('_', ' ')}: {_cell(v)}")
        return out
    raise TypeError(f"unknown derivation shape: {type(d).__name__}")


def _vote_learner(d: dict) -> list[str]:
    out = [f"Vote {d['direction']} ({d['vote']:+d}), family {_family(d['family'])}, school {d['school']}, "
           f"stability {_cell(d['stability'])}, term {_cell(d['term'])}. Derivation:", ""]
    return out + derivation_table(d["derivation"])


def render(reading: Reading, chart: Chart) -> str:
    notes = _Notes(chart)
    s = reading.summary
    L = [f"# Reading: {reading.question}", "",
         f"As of {reading.as_of} · engine {reading.engine} · weights {reading.weights} · model {reading.model} "
         f"· {reading.attempts} attempt(s) · narration {reading.narration_source}", ""] + _header(reading.chart)
    rv = reading.review or {}
    if rv.get("status") == "reviewed":                    # only a reviewed reading says so
        L += [f"**Reviewed by {rv['reviewed_by']}** on {rv['reviewed_at'][:10]}. Edited sentences passed the same "
              "validator and checker as the writer's; the astrologer's notes are the reviewer's own words.", ""]
    if reading.unchecked_sentences:
        L += [f"> Offline replay: {reading.unchecked_sentences} sentence(s) on this page have no recorded "
                  "checker verdict and were not semantically checked; the code validator ran on all of them.", ""]
    if not reading.narration_complete:
        n = sum(len(a.narration_gaps) for a in reading.areas)
        L += [f"> Narration incomplete: {n} finding(s) were not narrated within the checks"
              + (", and the summary is the engine's own" if s.source == "engine" else "") + ".", ""]
    L += ["## Summary", ""]
    if s.source == "engine":
        L += ["*Written by the engine from its fields: no drafted summary passed the checks.*", ""]
    L += [notes.render(s.text), ""]
    # A reading written before summary.timing_line existed gets the same line from its windows;
    # an engine-written summary already carries it.
    when = s.timing_line or " ".join(x for x in (timing_line(a.name, a.windows, a.avoid_window)
                                                 for a in reading.areas if a.windows) if x)
    if when and s.source != "engine":
        L += [f"**When (engine):** {when}", ""]
    if s.timing_note:
        L += [f"*{s.timing_note}*", ""]
    L += [
          f"- Driver: {s.driver_planet}" + (f" (alternates {', '.join(s.driver_alternates)})" if s.driver_alternates else ""),
          f"- Current period (Vimshottari): {s.current_period or '–'}",
          f"- Top areas: {', '.join(s.top_areas)}",
          f"- Birth-time window: ±{s.time_window_min:g} min" if s.time_window_min is not None else "- Birth-time window: –",
          f"- Fired rules stable / unstable under that window: {s.stable_findings} / {s.unstable_findings}",
          f"- Abstained areas: {', '.join(s.abstained_areas) or 'none'}", ""]

    by_id = {f["finding_id"]: f for a in reading.areas for f in findings(chart, a.name)[0]}
    learner: list[tuple[str, Any, dict]] = []
    for a in reading.areas:
        L += [f"## {a.name.replace('_', ' ').capitalize()}", "",
              f"- Tier: **{a.tier}** (classical score {_cell(a.score_classical)}; probability not calibrated)",
              f"- Stability: {_stab(a.stability)}",
              f"- Families agreeing: {a.families_agree_w:.2f} of {a.families_total_w:.2f} (weighted)"]
        if a.polarity:
            L.append("- Polarity: " + "; ".join(f"{p} ({', '.join(a.polarity_touches.get(p, []))})" for p in a.polarity))
        L.append("")
        curious = reading.depth == "curious"
        if curious and a.paragraph:
            L += [notes.render(a.paragraph), ""]
        if curious and a.claims:
            L += ["<details><summary>Show the astrologer's reading</summary>", ""]
        if a.claims:
            L += [f"{i}. {_claim(notes, c)}" for i, c in enumerate(a.claims, 1)]
            missing = [c.finding_id for c in a.claims if c.finding_id not in by_id]
            if missing:
                raise ValueError(f"the reading cites findings this chart does not offer: {', '.join(missing)} "
                                 "(different birth data, settings or engine version)")
            learner += [(a.name, c, by_id[c.finding_id]) for c in a.claims]
        elif not a.narration_gaps:
            offered = len(findings(chart, a.name)[0])
            L.append(f"No claims were drafted for this area ({offered} finding(s) offered).")
        if a.other_placements:
            L += ["", "Other placements the engine weighed (not narrated; the three strongest are above):", ""]
            L += [f"- `{o['rule_id']}` ({o['planet']}, scale {o['scale']:.3g}): {o['classical_effect']}"
                  for o in a.other_placements]
        if curious and a.claims:
            L += ["", "</details>"]
        if a.narration_gaps:
            L += ["", "Not narrated within the checks:", ""]
            L += [f"- `{g['finding_id']}` ({g['kind']}), last error on attempt {g['attempt']}: {g['last_error']}"
                  for g in a.narration_gaps]
        if a.astrologer_note:
            n = a.astrologer_note
            L += ["", f"> **The astrologer's note** ({n['by']}, {n['at'][:10]}; not checked by the engine)", ">"]
            L += [f"> {line}" if line else ">" for line in n["text"].splitlines()]
        L.append("")
        for sc in a.school_conflicts:
            other = next(x for x in sc["schools"] if x != "parashari")
            L.append(f"School conflict: the Parashari families ({sc['families'][0]}) are {sc['parashari']}, "
                     f"the {other.upper() if other == 'kp' else other.capitalize()} family ({sc['families'][1]}) "
                     f"is {sc[other]}. The two are not averaged.")
        if a.school_conflicts:
            L.append("")
        if a.windows or a.avoid_window:
            L += ["Windows (engine; score = 0.6 q + 0.4 t):", ""] + _window_rows(a.windows, a.avoid_window) + [""]
        if a.disclaimer:
            L += [f"> {a.disclaimer}", ""]

    L += ["## Depends on exact birth time", ""]
    if reading.depends_on_birth_time:
        for d in reading.depends_on_birth_time:
            what = d.get("rule") or d.get("vote") or f"tier {d.get('tier')}"
            extra = f" from {d['basis']}" if "basis" in d else (f", {d['direction']}" if "direction" in d else "")
            L.append(f"- {d['area']}: {what}{extra} holds in {d['stability']:.0%} of birth-time samples")
    else:
        L.append("Nothing: every finding offered for these areas holds in at least half the birth-time samples.")
    L.append("")

    L += ["## Learner: what each claim rests on", ""]
    for i, (area, c, f) in enumerate(learner, 1):
        L += [f"### {area}.{i}: `{c.finding_id}`", "", _claim(notes, c), ""]
        d = c.learner or learner_data(f)                 # the JSON's block, or the engine's for an older reading
        L += (_rule_learner(d) if d["kind"] == "rule" else _vote_learner(d)) + [""]

    if reading.disclaimers:
        L += ["## Disclaimers", ""] + [f"- {DISCLAIMERS[k]}" for k in reading.disclaimers] + [""]
    L += ["---", ""] + notes.block()
    return "\n".join(L) + "\n"
