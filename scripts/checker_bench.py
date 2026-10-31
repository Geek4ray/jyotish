"""The checker benchmark (SPEC Layer 7 items 10-11): labelled sentences, the code validator alone and
then validator + semantic checker, scored.

    .venv/bin/python scripts/checker_bench.py --build      # (re)writes tests/fixtures/checker_bench.jsonl
    .venv/bin/python scripts/checker_bench.py              # validator alone; + live checker with credentials
    .venv/bin/python scripts/checker_bench.py --offline    # validator alone, never the API

Rows: {id, sentence, tags, facts (the data the checker is given, as JSON), label (accept | reject),
category, origin, where (claim | summary | paragraph), area, finding_id, validator (the validator's
inputs: allowed tags, offered votes, chains, family_rule), audit (accepted rows)}.

Accepted rows are the 45 sentences of examples/reference_reading_curious.json, each read against its
facts (the `audit` note says what was checked). Rejected rows are made from them by one change each:
planet_swapped, house_changed, sign_changed, dignity_changed, dasha_lord_changed, negated,
unsupported_clause, tier_word. The reading names no dasha lord, so a dasha row adds a clause naming
the period lord that activates a planet, cites the chain finding whose facts name the true lord, and
names a wrong one. A tier word is a validator matter only in a summary or paragraph sentence, so those
rows are made from those. Then the known-bad sentences: the first recording's originals that
tests/fixtures/narration_career_edited.json corrected (its note lists them), and the hand-made bad
draft of tests/test_narrate.py.

The positive class is "reject": precision is the share of rejections that were right, recall the
share of bad sentences caught."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from jyotish.client import client_errors  # noqa: E402
from jyotish.narrate import (TAG, TIER_WORDS, _check_payload, _summary_checks, findings, offered_chains,  # noqa: E402
                             offered_votes, sentences, validate, validate_summary)

BENCH = ROOT / "tests" / "fixtures" / "checker_bench.jsonl"
READING = ROOT / "examples" / "reference_reading_curious.json"
SCORECARD = ROOT / "docs" / "checker_scorecard.md"
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
         "Aquarius", "Pisces"]
ORD = {1: "1st", 2: "2nd", 3: "3rd"} | {n: f"{n}th" for n in range(4, 13)}
CONSTRUCTED = ["planet_swapped", "house_changed", "sign_changed", "dignity_changed", "dasha_lord_changed",
               "negated", "unsupported_clause", "tier_word"]
# Categories that are tag or wording errors: the validator alone must reject every one of them. A
# reference to another claim ("again", an opening "The same") joined them on 2026-10-23 (review, F9):
# the checker sees one claim and cannot resolve it, the validator can read the word.
# A curious paragraph's sentence in engine words or with a Sanskrit term unglossed joined them on 2026-10-31
# (`client_words`): the curious paragraph is held to client.client_errors as the client's layer is.
WORDING = {"tier_word", "untagged", "tag_not_offered", "forbidden_word", "family_not_cited", "refers_to_another_claim",
           "ranking_not_cited", "nth_sign", "client_words"}
# The depth-full comparison's rows (comparison_rows) add three semantic kinds: a sentence citing a field
# narrower than its claim, a judgement whose premise is false, and a clause no field states.
SEMANTIC = set(CONSTRUCTED) - WORDING | {"misattached_detail", "wrong_dignity", "cites_too_narrowly",
                                         "judgement_premise", "unstated_claim", "contradicts_its_fact",
                                         "synthesis_does_not_follow", "untagged_unsupported"}
COMPARISON = ROOT / "docs" / "comparison_2026-10-23" / "b.recording.json"
COMPARISON_R2 = ROOT / "docs" / "comparison_2026-10-23_r2" / "b.recording.json"   # the re-run after F1-F13
FULL = {"as_of": "2026-10-21", "areas": ["career", "marriage", "longevity"]}
LIVE_HEADING = "## Validator + semantic checker (live)"
# The gate in use for client readings (docs/models.md): GLM-5.3-Flash at temperature 0 on DeepInfra since
# 2026-10-31 (Ray's decision; it passed the rule against GLM-4.7, the gate from 2026-10-25, with recall 1.000 on
# every category); GLM-4.7's scorecard (PREVIOUS_GATE) and Opus's (SCORECARD) are the earlier gates'.
GATE = ROOT / "docs" / "checker_scorecard_zai-org-glm-5.3-flash_temp-0.md"
PREVIOUS_GATE = ROOT / "docs" / "checker_scorecard_zai-org-glm-4.7.md"


# --- the chart behind the reading ---------------------------------------------------------------

def reading_chart():
    from jyotish.uncertainty import assess
    r = json.loads(READING.read_text())
    ch = r["chart"]
    utc = datetime.fromisoformat(ch["birth_utc"])
    return r, assess(utc, ch["lat"], ch["lon"], true_node=ch["conventions"]["node"] == "true",
                     seed=ch.get("seed", 0)), date.fromisoformat(r["as_of"])


# --- building the rows --------------------------------------------------------------------------

def _bare(s: str) -> str:
    return TAG.sub("", s)


def _tags(s: str) -> list[str]:
    return [f"{k}:{v}" for k, v in TAG.findall(s)]


def _swap_once(s: str, old: str, new: str) -> str | None:
    """Replace the first whole-word `old` in the sentence's words (never inside a tag)."""
    m = TAG.search(s)
    head, tail = (s[:m.start()], s[m.start():]) if m else (s, "")
    out = re.sub(rf"\b{re.escape(old)}\b", new, head, count=1)
    return None if out == head else out + tail


def _before_tags(s: str, clause: str) -> str:
    m = re.search(r"\s*(\[[^\]]+\]\s*)+[.!?]?\s*$", s)
    head, tail = (s[:m.start()], s[m.start():]) if m else (s.rstrip("."), ".")
    return f"{head}{clause}{tail}"


def planet_swapped(s, row):
    if row["where"] == "claim" and row["finding_id"].startswith(("place.", "yoga.")):
        return None                                   # a planet may be the rule's name; keep this semantic
    named = [p for p in PLANETS if re.search(rf"\b{p}\b", _bare(s))]
    if not named:
        return None
    other = next((p for p in ["Jupiter", "Saturn", "Venus", "Mars", "Mercury"] if p not in named), None)
    if other is None:
        return None
    p = named[0]
    if p in ("Sun", "Moon"):                           # "the Sun" becomes "Jupiter", not "the Jupiter"
        for art in ("The", "the"):
            out = _swap_once(s, f"{art} {p}", other)
            if out:
                return out
    return _swap_once(s, p, other)


def house_changed(s, row):
    for n in (10, 11, 7, 2, 6, 8, 1):
        if re.search(rf"\bthe {ORD[n]}\b", _bare(s)):
            return _swap_once(s, f"the {ORD[n]}", f"the {ORD[(n + 2) % 12 + 1]}")
    return None


def sign_changed(s, row):
    for i, name in enumerate(SIGNS):
        if re.search(rf"\b{name}\b", _bare(s)):
            return _swap_once(s, name, SIGNS[(i + 4) % 12])
    return None


def dignity_changed(s, row):
    for old, new in (("exalted", "debilitated"), ("its own sign", "its debilitation sign"),
                     ("a friend's sign", "an enemy's sign"), ("an enemy's sign", "its exaltation sign"),
                     ("is neutral", "is exalted")):
        if old in _bare(s):
            return _swap_once(s, old, new)
    return None


def negated(s, row):
    for old, new in (("favours", "does not favour"), ("is favourable", "is not favourable"),
                     ("goes against", "does not go against"), ("sits in", "does not sit in"),
                     ("forms", "does not form"), ("sit together", "do not sit together"), ("holds", "does not hold")):
        if re.search(rf"\b{old}\b", _bare(s)):
            return _swap_once(s, old, new)
    return None


def unsupported_clause(s, row):
    clause = (", and Jupiter's aspect on the 10th strengthens it" if row["area"] == "career" else
              ", and Jupiter aspects the 7th from the 1st to protect it" if row["area"] == "marriage" else
              ", and the 12th house adds its support")
    return _before_tags(s, clause)


def tier_word(s, row):
    if row["where"] == "claim":
        return None                                   # the validator reads tier words in summaries and paragraphs
    if s.startswith(("Five", "Six", "Of ")):
        return None
    first, rest = s.split(" ", 1)
    return f"In a strong chart, {first.lower() if first in ('The', 'Most') else first} {rest}"


# dasha_lord_changed: (area, chain tag, planet, the true lord, the wrong lords) on the reading's chart.
DASHA = [("career", "chain:career.karaka", "Sun", "Jupiter", ["Saturn", "Venus"]),
         ("marriage", "chain:marriage.lord", "Mars", "Mercury", ["Ketu", "Jupiter"]),
         ("longevity", "chain:longevity.lord", "Venus", "Mercury", ["Saturn", "Rahu"])]


def build() -> list[dict]:
    r, chart, as_of = reading_chart()
    names = [a["name"] for a in r["areas"]]
    offered = {n: findings(chart, n, as_of)[0] for n in names}
    by_id = {f["finding_id"]: f for fs in offered.values() for f in fs}
    votes = offered_votes(chart, names)
    chains = offered_chains(chart, names)
    area_tags = {n: sorted(set().union(*(set(f["allowed_tags"]) for f in offered[n]))) for n in names}
    all_tags = sorted(set().union(*map(set, area_tags.values())))
    curious = r["depth"] == "curious"

    def inputs(where, area, fid):
        if where == "claim":
            f = by_id.get(fid)
            return {"allowed": sorted(f["allowed_tags"]) if f else [], "offered_votes": votes[area],
                    "chains": chains[area], "family_rule": not curious}
        if where == "paragraph":
            return {"allowed": area_tags[area], "offered_votes": votes[area], "chains": chains[area],
                    "family_rule": False}
        return {"allowed": all_tags, "offered_votes": {k: sorted({votes[n][k] for n in names if k in votes[n]})
                                                       for n in names for k in votes[n]},
                "chains": {k: v for n in names for k, v in chains[n].items()}, "family_rule": not curious}

    def facts(where, sentence, fid):
        if where == "claim" and fid in by_id and set(_tags(sentence)) <= set(by_id[fid]["allowed_tags"]):
            return _check_payload(by_id[fid])
        checks = _summary_checks(sentence, by_id)
        return checks[0][2] if checks else json.dumps({"findings": []})

    rows = []
    for i, s in enumerate(sentences(r["summary"]["text"])):
        rows.append({"where": "summary", "area": None, "finding_id": None, "sentence": s,
                     "origin": f"reading summary sentence {i + 1}"})
    for a in r["areas"]:
        for c in a["claims"]:
            rows.append({"where": "claim", "area": a["name"], "finding_id": c["finding_id"], "sentence": c["text"],
                         "origin": f"reading claim {a['name']}/{c['finding_id']}"})
        for i, s in enumerate(sentences(a["paragraph"] or "")):
            rows.append({"where": "paragraph", "area": a["name"], "finding_id": None, "sentence": s,
                         "origin": f"reading paragraph {a['name']} sentence {i + 1}"})
    accepted = []
    for k, row in enumerate(rows):
        row |= {"id": f"accept-{k + 1:02d}", "label": "accept", "category": "accepted",
                "audit": audit(row["sentence"], chart)}
        accepted.append(row)

    out = list(accepted)
    per_cat = {c: 0 for c in CONSTRUCTED}
    cap = 9
    for name in CONSTRUCTED:
        if name == "dasha_lord_changed":
            continue
        fn = globals()[name]
        for row in accepted:
            if per_cat[name] >= cap:
                break
            new = fn(row["sentence"], row)
            if new and new != row["sentence"]:
                per_cat[name] += 1
                out.append({"id": f"{name}-{per_cat[name]}", "where": row["where"], "area": row["area"],
                            "finding_id": row["finding_id"], "sentence": new, "label": "reject", "category": name,
                            "origin": f"constructed from {row['id']} ({row['origin']})"})
    para = {a: [x for x in accepted if x["where"] == "paragraph" and x["area"] == a and x["sentence"].startswith(
        ("The Sun", "Mercury", "Mars", "Ketu"))] for a in names}
    for area, tag, planet, true_lord, wrong in DASHA:
        base = para[area][0]
        for w in wrong:
            per_cat["dasha_lord_changed"] += 1
            the = f"the {planet}" if planet in ("Sun", "Moon") else planet
            s = _before_tags(base["sentence"], f", and the current major period of {w} activates {the} through its "
                                               f"nakshatra")
            s = s[:-1] + f" [{tag}]." if s.endswith(".") else s
            out.append({"id": f"dasha_lord_changed-{per_cat['dasha_lord_changed']}", "where": "paragraph", "area": area,
                        "finding_id": None, "sentence": s, "label": "reject", "category": "dasha_lord_changed",
                        "origin": f"constructed from {base['id']}: {planet} is activated by {true_lord}'s period, "
                                  f"not {w}'s"})
    out += known_bad(r)
    # 2026-10-31: the curious paragraph is the client's and is held to the client's words. A paragraph
    # sentence the reading accepted before that rule and that breaks it is now a wording reject.
    for row in out:
        why = client_errors(row["sentence"]) if row["where"] == "paragraph" and row["label"] == "accept" else []
        if why:
            row.update(label="reject", category="client_words",
                       origin=f"{row['origin']}; accepted before the curious paragraph was held to the client's "
                              f"words (2026-10-31), now refused: {why[0].split(':')[0]}")
            row.pop("audit", None)
    for row in out:
        row["tags"] = _tags(row["sentence"])
        row["validator"] = inputs(row["where"], row["area"] or "career", row["finding_id"])
        row["facts"] = facts(row["where"], row["sentence"], row["finding_id"])
    return out + comparison_rows()


# --- the depth-full comparison's refusals that were the engine's fault ----------------------------

def _b_sentence(prefix: str, recording: Path = COMPARISON) -> str:
    """The sentence of reading B (its recording: checked sentences and drafts) that starts so."""
    rec = json.loads(recording.read_text())
    found = [c["sentence"] for c in rec["calls"] if c["kind"] == "checker"]
    for c in rec["calls"]:
        for a in (c.get("draft") or {}).get("areas", []):
            found += [x for cl in a["claims"] for x in sentences(cl["text"])]
            found += [x for t in (a.get("analysis") or {}).values() if t for x in sentences(t)]
    hits = sorted({x for x in found if x.startswith(prefix)})
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


@__import__("functools").lru_cache(maxsize=1)
def full_inputs():
    """(chart, as_of, whole-chart payload, finding data) for B's reading: the reference chart, mean node."""
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    as_of = date.fromisoformat(FULL["as_of"])
    whole = payload(chart, as_of, *full_range(as_of), FULL["areas"])
    data = {f["finding_id"]: f for n in FULL["areas"] for f in findings(chart, n, as_of)[0]}
    return chart, as_of, whole, data


# The review of 2026-10-23 (F5): one row of each new sentence kind that reaches the live checker (the
# validator passes it), so the benchmark measures the checker on the kinds and not only the validator.
KIND_ROWS = [
    ("kind-judgement-accept", "analysis", "career", "assessment",
     "I give the lord family more weight than the arudha vote, since the lord family's term is the largest "
     "[fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].", "accept", "accepted",
     "constructed for the review's F5: an accepted judgement. Its one chart proposition, the lord family's term the "
     "largest, is largest_term 'lord'; the arudha vote is cited for what is weighed against; the weighing is the reading's."),
    ("kind-judgement-premise", "analysis", "career", "assessment",
     "I give the lord family more weight than the arudha vote, since the arudha vote is against career "
     "[fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].", "reject", "judgement_premise",
     "constructed for the review's F5: a judgement whose premise is false and whose form is clean: the career arudha "
     "vote is 0 (abstains), not against"),
    ("kind-synthesis-does-not-follow", "analysis", "career", "assessment",
     "Mars is in its own sign in the 7th house from the lagna, so Mars rules the 10th house from the lagna "
     "[fact:planets.Mars.dignity] [fact:houses.lagna.7].", "reject", "synthesis_does_not_follow",
     "constructed for the review's F5: a synthesis with true premises (Mars own sign; the 7th from the lagna is "
     "Scorpio, lord Mars, Mars in it) and a conclusion that does not follow and is false (the 10th from the lagna is "
     "Aquarius, lord Saturn); the validator's form is clean"),
    ("kind-untagged-summary", "summary", None, None, "Saturn exalted in Libra, Venus debilitated in Virgo.", "reject",
     "untagged_unsupported", "constructed for the review's F2: an untagged sentence with no claim verb, which the "
     "validator passes outside the analysis, now sent to the checker with nothing to rest on (and false: Saturn is in "
     "Taurus, Venus exalted in Pisces)"),
    ("kind-untagged-framing", "summary", None, None, "Three areas follow, career first.", "accept", "accepted",
     "constructed for the review's F2: an untagged sentence that asserts nothing about the chart, sent to the checker "
     "with nothing to rest on and supported for that reason"),
]


def comparison_rows() -> list[dict]:
    """B's refusals (docs/comparison_2026-10-23, depth full) that were the engine's fault, each with
    the label the engine now makes it earn, and beside a still-refused one the form that now passes.
    Every sentence is B's verbatim except a `fixed` one, built from B's by the change its origin names;
    every accepted row was read against the facts below by hand (its audit)."""
    from jyotish.narrate import TRADITION, _cited_facts
    chart, as_of, whole, data = full_inputs()
    votes, chains = offered_votes(chart, FULL["areas"]), offered_chains(chart, FULL["areas"])
    area_tags = {n: sorted(set().union(*(set(f["allowed_tags"]) for f in findings(chart, n, as_of)[0])))
                 for n in FULL["areas"]}
    fault = "the engine's fault on 2026-10-23"
    rows = [
        # (id, where, area, section or finding, sentence, label, category, origin / audit)
        ("b-varga-career", "claim", "career", "vote:career.varga", _b_sentence("The varga vote is for career"),
         "accept", "accepted", f"{fault}: the D10 rows gave varga_dignity 2.0 and 1.0 with no word; varga_dignity_label "
         "now says exalted (Mars) and own (Saturn). Every planet, sign and score read against the seven D10 rows."),
        ("b-varga-marriage", "claim", "marriage", "vote:marriage.varga", _b_sentence("The varga vote is for marriage"),
         "accept", "accepted", f"{fault}: Saturn's D9 row gave 1.0 with no word; now own. The six D9 rows read."),
        ("b-varga-longevity", "claim", "longevity", "vote:longevity.varga", _b_sentence("The varga vote is for longevity"),
         "accept", "accepted", f"{fault}: Saturn's D9 row gave 1.0 with no word; now own. The Moon vargottama at 1.0, "
         "Jupiter in Virgo at -0.25 in D30 and the other D30 scores (0 or 0.25) read against the rows."),
        ("b-stability-career", "analysis", "career", "not_said", _b_sentence("The D10 lagna holds in 0.795"),
         "accept", "accepted", f"{fault}: the stability triple was unlabelled; each now says 'holds under 2 of 3 "
         "ayanamsas'. The D10 lagna's 0.795 and the varga vote's use of the three D10 rows read."),
        ("b-stability-marriage", "analysis", "marriage", "not_said", _b_sentence("The D9 lagna holds in 0.78"),
         "accept", "accepted", f"{fault}: as above for the D9 signs of Mars and Saturn (2 of 3) and the D9 lagna (0.78)."),
        ("b-stability-longevity", "analysis", "longevity", "not_said", _b_sentence("The trimsamsa signs of Jupiter"),
         "accept", "accepted", f"{fault}: as above for the D30 signs of Jupiter, Mars and Venus (2 of 3), all three D30 "
         "rows of the varga vote."),
        ("b-ranking-career", "analysis", "career", "assessment", _b_sentence("The strongest support is in the lords, as "
         "the lord vote shows: Venus, lord of the 6th"), "reject", "ranking_not_cited",
         f"{fault}: no field ranked the families, so the ranking could only be the writer's; it now must cite the "
         "engine's (areas.career.contributions), and as written it does not"),
        ("b-ranking-career-fixed", "analysis", "career", "assessment", None, "reject", "contradicts_its_fact",
         "fixed from b-ranking-career by citing [fact:areas.career.contributions]; since the review's F4 that field "
         "ranks by percentile against 10,000 charts and names the varga family the strongest (90th), the lord family's "
         "term being the largest on most charts by construction, so the sentence now contradicts the fact it cites"),
        ("b-ranking-career-percentile", "analysis", "career", "assessment",
         "The strongest support is the varga family, at the 90th percentile of 10,000 charts "
         "[fact:areas.career.contributions].", "accept", "accepted",
         "written from b-ranking-career for what the engine's ranking now states: strongest varga, "
         "strongest_percentile 90.0, against 10,000 random charts (contributions.basis)."),
        ("b-ranking-longevity", "analysis", "longevity", "assessment", _b_sentence("The least support is Saturn"),
         "reject", "ranking_not_cited", f"{fault}: as above; the engine's weakest for longevity is the panchanga "
         "family by percentile"),
        ("b-nth-sign", "analysis", "career", "timing", _b_sentence("The timing join's full targets for career"),
         "reject", "nth_sign", f"{fault}: no field gave the houses from the lagna, so 'the 10th sign' (the zodiac's "
         "Capricorn, or the 10th house's Aquarius) could not be pinned; houses.lagna.10 now does"),
        ("b-nth-sign-fixed", "analysis", "career", "timing", None, "accept", "accepted",
         "fixed from b-nth-sign: 'the 10th house from the lagna' citing [fact:houses.lagna.10] (Aquarius) for the "
         "lagna's sign. Targets Aquarius and Taurus, A10 in Taurus: read."),
        ("b-arudha", "analysis", "career", "not_said", _b_sentence("The arudha vote is 0, so the A10"), "reject",
         "cites_too_narrowly", f"{fault}: no field named the arudha the vote rests on; the derivation now does "
         "(rests_on A10), but this sentence cites the bare vote, which does not state it"),
        ("b-arudha-fixed", "analysis", "career", "not_said",
         "The arudha vote rests on the A10 and abstains, the benefics and malefics in it balancing "
         "[fact:areas.career.votes.arudha.derivation].", "accept", "accepted",
         "fixed from b-arudha: cites the derivation, whose rests_on (A10) and why (the benefics and malefics balance) "
         "state it; A10 is Taurus with Jupiter and Saturn."),
        ("b-synastry", "analysis", "marriage", "not_said", _b_sentence("This chart says nothing about a partner"),
         "reject", "cites_too_narrowly", f"{fault}: nothing said what the engine does not do; not_computed.synastry now "
         "does, but this sentence cites only the synastry tier"),
        ("b-synastry-fixed", "analysis", "marriage", "not_said", None, "accept", "accepted",
         "fixed from b-synastry by also citing [fact:not_computed.synastry], which says the engine says nothing of "
         "another person's own chart or life; the tier 'needs two charts' read."),
        ("b-judgement-marriage", "analysis", "marriage", "assessment", _b_sentence("I give the six agreeing families"),
         "reject", "judgement_premise", f"{fault} that a weighing could never pass; as a judgement every proposition "
         "but the weighing is checked, and one is false on the facts: the arudha vote rests on UL, UL2 and A7 "
         "(rests_on), not on the Upapada alone, though Rahu in the UL is the only occupant of the three (settled as "
         "the review of 2026-10-23 argues, F8b; the lord-vote premise is left as B's summary had it, which the live "
         "checker passed)"),
        ("b-chain-navamsa", "claim", "career", "chain:career.lord", _b_sentence("In its navamsa chain Saturn is in its "
         "own sign Capricorn, the 12th from the D9 lagna, and is its own final dispositor"), "accept", "accepted", f"{fault}: the validator read 'navamsa' in a chain sentence as "
         "naming the varga family. Capricorn, 12th from the D9 lagna, own; its own final navamsa dispositor; in "
         "neither current period's activation set: read against the chain's facts."),
        ("b-tradition-family", "analysis", "marriage", "assessment", _b_sentence("BPHS reads marriage through the "
         "Upapada"), "accept", "accepted", f"{fault}: a [tradition:] sentence may carry no tag, yet the family rule "
         "asked it to cite the arudha vote. Never checked by design: the validator alone reads it."),
        ("b-hyphen", "analysis", "marriage", "assessment", _b_sentence("A second tension sits in Mars itself: its place in the 7th"), "reject",
         "unstated_claim", f"{fault}: 'lord-of-the-7th' did not match the rule's name 'lord of the 7th', and the "
         "validator now passes it. Both placements scaled to 0.6 by marana karaka sthana, Mars in it, its ratio 1.3: "
         "read; but its last clause (the facts leave the net quality open) is stated by no field it cites, the same "
         "kind as b-votes-fact's, and is labelled the same (the review of 2026-10-23, F8a)"),
        ("b-votes-fact", "analysis", "longevity", "not_said", _b_sentence("The votes for this area weigh houses"),
         "reject", "unstated_claim", f"{fault}: the family rule refused it although it cites the area's votes; the "
         "validator now passes it, and its last clause (the reading draws no medical statement) is stated by no field"),
    ]
    # The re-run's two narration gaps (docs/comparison_2026-10-23_r2, reading B), both refused for want of
    # a fact the engine did not give: each verbatim, now citing fields that state what it says.
    r2 = "the engine's fault in the re-run of 2026-10-23"
    rows += [
        ("r2-varga-dignity", "analysis", "career", "assessment",
         _b_sentence("I give more weight to Saturn's divisional dignity", COMPARISON_R2), "accept", "accepted",
         f"{r2}: vargas.D10.Saturn gave the sign alone, so 'Saturn's divisional dignity' stated nothing; it now gives "
         "{sign Capricorn, dignity own}. Saturn the 10th lord (houses.lagna.10.lord), yogakaraka (roles.Saturn), "
         "Shadbala ratio 0.69, below its required strength, and in marana karaka sthana: read. A judgement: the "
         "weighing and the reading of the deficit as a brake are the reading's."),
        ("r2-areas-touched", "analysis", "marriage", "timing",
         _b_sentence("I give more weight to the Jupiter–Venus window than to the two windows in the Jupiter–Mercury period, "
                     "because it joins", COMPARISON_R2),
         "accept", "accepted",
         f"{r2}: the Kantaka Shani spans were tagged house_moon:7 with nothing tying them to marriage; each transit "
         "window now carries areas_touched, and both spans (transits.windows.1 and .3, Saturn in Aries, graded "
         "adverse) are the 7th from the Moon, a marriage house. Marriage windows 0 (Jupiter-Venus, its strongest "
         "piece crediting Jupiter in Scorpio), 1 and 2 (Jupiter-Mercury); Venus the main karaka, exalted: read. "
         "A judgement: which window it gives more weight is the reading's."),
    ]
    # The live readings of 2026-10-27 (docs/comparison_2026-10-27_*): a placement claim refused on every
    # attempt for stating the lordship as "rules the 2nd"; verbatim. The validator now takes that wording.
    rows += [
        ("live-rules-the-2nd", "claim", "career", "place.l2_h10@lagna",
         "Mercury is placed in the 10th house and rules the 2nd house. [rule:place.l2_h10]", "accept", "accepted",
         "the validator's false reject in the live readings of 2026-10-27: 'rules the 2nd' names the 2nd lord as "
         "'lord of the 2nd' does. Mercury in the 10th, lord of the 2nd (the placement's fact): read."),
        # 2026-10-31, the first reading on Fly (curious depth): the career paragraph was refused three times for
        # naming the 5th lord in a list. The quoted clause is the reading's; the sentence around it is rebuilt.
        ("live-lord-of-the-2nd-and-5th", "paragraph", "career", None,
         "Mercury sits in the 10th house, and it is the lord of the 2nd and 5th houses [rule:place.l5_h10].",
         "accept", "accepted",
         "the validator's false reject in the first reading on Fly, 2026-10-31: 'the lord of the 2nd and 5th houses' "
         "names the 5th lord in a list. Mercury in the 10th, lord of the 2nd and the 5th (the placements' facts): read."),
        # 2026-10-31, the curious comparison (docs/comparison_2026-10-31_curious.md): the career paragraph was refused
        # in both runs as "'Kendra' has a plain phrase" because the writer joined the yoga's name with a non-breaking
        # hyphen (U+2011). The term and its hyphen are the reading's; the sentence around it is rebuilt.
        ("live-kendra-nonbreaking-hyphen", "paragraph", "career", None,
         "The Sun and Mercury together form Kendra\u2011Trikona Raja yoga, a combination joining the lord of an angular "
         "house with the lord of a trine house [rule:yoga.kendra_trikona_raja].",
         "accept", "accepted",
         "the validator's false reject in the curious comparison of 2026-10-31: 'Kendra\u2011Trikona' with a non-breaking "
         "hyphen is the yoga's name, not 'kendra' for 'angular house'. The Sun and Mercury in the 10th form the yoga "
         "(its fire); the gloss is the glossary's: read."),
        # 2026-11-01, the curious comparison (docs/comparison_2026-10-31_curious_r2.md): "Venus is exalted" was refused
        # twice for want of a field: the sign placement stated the sign only. It now carries the dignity.
        ("live-venus-exalted-in-pisces", "paragraph", "marriage", None,
         "Venus is exalted in Pisces, the sign where the texts hold it at its strongest [rule:place.venus_in_pisces].",
         "accept", "accepted",
         "the engine's fault in the curious comparison of 2026-10-31 (r2): place.venus_in_pisces stated Venus's sign "
         "and not its dignity, so 'exalted' rested on nothing; its placement now carries dignity exalted and the "
         "glossary's 'exalted'. Venus in Pisces, exalted (planets.Venus.dignity): read."),
    ]
    rows += KIND_ROWS
    by_id = {r[0]: r for r in rows}
    fixes = {"b-ranking-career-fixed": lambda: by_id["b-ranking-career"][4][:-1] + " [fact:areas.career.contributions].",
             "b-nth-sign-fixed": lambda: by_id["b-nth-sign"][4].replace("the 10th sign", "the 10th house from the lagna")
             .replace("[fact:lagnas.asc.sign]", "[fact:houses.lagna.10]"),
             "b-synastry-fixed": lambda: by_id["b-synastry"][4][:-1] + " [fact:not_computed.synastry]."}
    out = []
    for rid, where, area, unit, sentence, label, cat, note in rows:
        sentence = sentence or fixes[rid]()
        kind = rid.startswith("kind-")
        row = {"id": rid, "where": where, "area": area, "finding_id": unit if where == "claim" else None,
               "section": unit if where == "analysis" else None, "sentence": sentence, "label": label, "category": cat,
               "origin": note if kind or rid.startswith("live-") else
                         f"comparison 2026-10-23{' r2' if rid.startswith('r2-') else ''}, reading B: {note}",
               "tags": _tags(sentence),
               "validator": {"allowed": sorted(data[unit]["allowed_tags"]) if where == "claim" else
                             area_tags[area or "career"], "offered_votes": votes[area or "career"],
                             "chains": chains[area or "career"], "family_rule": where != "paragraph",
                             **({} if where in ("summary", "paragraph") else {"full": FULL})}}
        if label == "accept":
            row["audit"] = note
        if TRADITION.search(sentence):
            row["facts"] = json.dumps({"never_checked": "a [tradition:] sentence"})
        elif where == "claim":
            row["facts"] = _check_payload(data[unit], sentence, whole)
        else:
            row["facts"] = _summary_checks(sentence, data, whole)[0][2]
        assert row["tags"] or TRADITION.search(sentence) or where == "summary", rid
        out.append(row)
    return out


def audit(sentence: str, chart) -> str:
    """What was checked against the chart for an accepted row: each "above / below its required
    strength" against the Shadbala ratio, each dignity word against the D1 dignity; the rest of the
    sentence was read against its facts by hand (2026-10-22)."""
    notes = []
    sb = chart.features.shadbala.planets
    bare = _bare(sentence)
    planet_rx = re.compile(r"\b(" + "|".join(PLANETS[:7]) + r")\b")
    for m in re.finditer(r"\b(above|below|short of)\b[^.;,]*?required strength", bare):
        before = planet_rx.findall(bare[:m.start()])
        if not before:
            continue
        p, want = before[-1], m.group(1) == "above"       # the planet the phrase is about: the nearest before it
        group = [p] + ([before[-2]] if len(before) > 1 and re.search(rf"\b{before[-2]} and {p}\b", bare) else [])
        for q in group:
            ok = (sb[q].ratio >= 1) == want
            notes.append(f"{q} {'above' if want else 'below'} required strength: ratio {sb[q].ratio:.2f} "
                         f"{'ok' if ok else 'CONTRADICTED'}")
    for p in PLANETS[:7]:
        if re.search(rf"\b{p}\b[^.;]*?\bexalted\b", bare) and chart.bodies[p].dignity == "exalted":
            notes.append(f"{p} exalted: D1 dignity {chart.bodies[p].dignity} ok")
    return "; ".join(notes) or "read against its facts by hand; no strength or dignity word to compute"


def known_bad(reading) -> list[dict]:
    r1 = json.loads((ROOT / "tests" / "fixtures" / "narration_career_opus55_r1.json").read_text())["drafts"][0]
    claims = {c["finding_id"]: c["text"] for a in r1["areas"] for c in a["claims"]}
    summ = sentences(r1["summary"])
    src = "narration_career_opus55_r1.json, corrected in narration_career_edited.json"
    rows = [
        ("claim", "career", "yoga.kendra_trikona_raja@lagna", claims["yoga.kendra_trikona_raja@lagna"],
         "refers_to_another_claim", "opens 'The same conjunction', which the checker cannot see"),
        ("claim", "career", "yoga.ruchaka@lagna+sun", claims["yoga.ruchaka@sun"], "refers_to_another_claim",
         "'again forms Ruchaka', 'the same weakening'"),
        ("claim", "career", "vote:career.kp", claims["vote:career.kp"], "tag_not_offered",
         "the KP vote abstains under v2 and is not offered; the sentence also gives Ketu the cusp's star"),
        ("claim", "career", "vote:career.varga", claims["vote:career.varga"], "wrong_dignity",
         "under varga v2 Jupiter and the Sun are in friends' signs in D10, not poorly placed"),
        ("summary", None, None, summ[1], "family_not_cited",
         "names five votes and cites two, at astrologer depth"),
        ("summary", None, None, summ[2], "forbidden_word", "timing and the engine, tagged with the house vote"),
        ("summary", None, None, "Career is likely to peak soon [vote:career.house].", "forbidden_word",
         "tests/test_narrate.py INVALID: a probability word"),
        ("claim", "career", "yoga.budhaditya@lagna", "The Sun and Mercury share Aquarius, which forms Budhaditya yoga.",
         "untagged", "tests/test_narrate.py INVALID: a claim with no tag"),
        ("claim", "career", "vote:career.house", "The house vote is for career [rule:yoga.ruchaka].", "tag_not_offered",
         "tests/test_review.py: a tag the finding does not offer"),
    ]
    out = []
    for k, (where, area, fid, s, cat, why) in enumerate(rows, 1):
        origin = (f"{src}: {why}" if "INVALID" not in why and "test_review" not in why else why)
        out.append({"id": f"known_bad-{k}", "where": where, "area": area, "finding_id": fid, "sentence": s,
                    "label": "reject", "category": cat, "origin": origin, "astrologer_depth": where == "summary"})
    return out


# --- running --------------------------------------------------------------------------------------

def validator_errors(row: dict) -> list[str]:
    v = row["validator"]
    if row.get("astrologer_depth"):
        v = dict(v, family_rule=True)
    allowed = set(v["allowed"])
    ov = {k: (set(x) if isinstance(x, list) else x) for k, x in v["offered_votes"].items()}
    if v.get("full"):                                   # depth full: fact tags resolve against the whole chart
        whole = full_inputs()[2]
        if row["where"] == "analysis":
            return validate_summary(row["sentence"], allowed, offered_votes=ov, where=f"{row['area']} {row['section']}",
                                    family_rule=v["family_rule"], chains=v["chains"], facts=whole, traditions=True,
                                    judgements=True)
        errs = validate(row["sentence"], allowed, offered_votes=ov, family_rule=v["family_rule"], chains=v["chains"],
                        facts=whole)
        return errs + ([] if TAG.search(row["sentence"]) else [f"claim without a tag: {row['sentence']!r}"])
    if row["where"] == "claim":
        errs = validate(row["sentence"], allowed, offered_votes=ov, family_rule=v["family_rule"], chains=v["chains"])
        if not TAG.search(row["sentence"]):
            errs.append(f"claim without a tag: {row['sentence']!r}")
        return errs
    where = f"{row['area']} paragraph" if row["where"] == "paragraph" else "summary"
    return validate_summary(row["sentence"], allowed, offered_votes=ov, where=where, family_rule=v["family_rule"],
                            chains=v["chains"]) + (client_errors(row["sentence"]) if row["where"] == "paragraph" else [])


def load() -> list[dict]:
    return [json.loads(x) for x in BENCH.read_text().splitlines() if x.strip()]


def run_validator(rows) -> dict[str, tuple[bool, str]]:
    """row id -> (rejected, reason)."""
    out = {}
    for row in rows:
        errs = validator_errors(row)
        out[row["id"]] = (bool(errs), "; ".join(errs[:2]))
    return out


PARTIAL = ROOT / "data" / "bench_partial"      # a live run's rows as they are checked (gitignored)


def partial_path(spec: str | None, effort: str | None = None) -> Path:
    """Where a live run on `spec` (at `effort`, when it is not the default) writes its rows as it goes."""
    name = "anthropic" if not spec or spec == "anthropic" else spec.rsplit(":", 1)[-1]
    return PARTIAL / f"{re.sub(r'[^A-Za-z0-9.]+', '-', name).strip('-').lower()}{_effort_suffix(effort)}.jsonl"


def _effort_suffix(effort: str | None) -> str:
    """The run's settings in its file names: the effort when it is not the default, and the checker's
    temperature when one is sent (JYOTISH_CHECKER_TEMPERATURE, --checker-temperature; 2026-10-26)."""
    from jyotish.narrate import CONFIG
    temp = os.environ.get("JYOTISH_CHECKER_TEMPERATURE", "").strip()
    return ((f"_effort-{effort}" if effort and effort != CONFIG.checker_effort else "")
            + (f"_temp-{float(temp):g}" if temp else ""))


def run_live(rows, config=None, backend: str | None = None, resume: bool = False,
             partial: Path | None = None) -> tuple[dict[str, tuple[bool, str]], dict]:
    """Validator, then the semantic checker on every row the validator passes, on `backend` ("anthropic"
    or "openai:<base url>:<model>"; None: JYOTISH_CHECKER_BACKEND, Anthropic when unset). Rows are checked
    in chunks and each is appended to `partial` as it is checked; with `resume` the rows already there are
    not asked again. A row whose checker call failed after the backend's retries is unchecked: listed in
    usage["unchecked"], and left out of the scores. The usage names the backend (provider, host, model)."""
    from jyotish.narrate import CONFIG, ModelChecker, make_backend
    config = config or CONFIG
    checker = ModelChecker(make_backend(backend, "checker", config), config)
    partial = partial or partial_path(backend, config.checker_effort)
    partial.parent.mkdir(parents=True, exist_ok=True)
    done: dict[str, dict] = {}
    if resume and partial.exists():
        done = {r["id"]: r for r in map(json.loads, partial.read_text().splitlines()) if not r.get("unchecked")}
        partial.write_text("".join(json.dumps(r) + "\n" for r in done.values()))   # unchecked rows are asked again
    elif partial.exists():
        partial.unlink()
    v = run_validator(rows)
    out, todo = {}, []
    usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "calls": 0, "unchecked": [],
             "resumed": 0, "backend": checker.backend.describe(), "effort": checker.effort}
    for row in rows:
        if v[row["id"]][0] or "[tradition:" in row["sentence"]:      # a [tradition:] sentence is never checked
            out[row["id"]] = v[row["id"]]
        elif row["id"] in done:
            r = done[row["id"]]
            out[row["id"]] = (r["rejected"], r["reason"])
            usage["resumed"] += 1
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens"):
                usage[k] += (r.get("usage") or {}).get(k) or 0
            usage["calls"] += 1
        else:
            todo.append(row)
    size = max(8, 4 * checker.concurrency)
    for i in range(0, len(todo), size):
        chunk = todo[i:i + size]
        results = checker.check_many([(row["sentence"], row["facts"]) for row in chunk])
        with partial.open("a") as f:
            for row, (result, meta) in zip(chunk, results):
                meta = meta or {}
                bad = [p for p in result.propositions if not p.supported]
                rec = {"id": row["id"], "rejected": bool(bad), "unchecked": bool(meta.get("unchecked")),
                       "reason": "; ".join(f"{p.text!r}: {p.evidence}" for p in bad[:2]) or "supported",
                       "usage": meta.get("usage")}
                f.write(json.dumps(rec) + "\n")
                out[row["id"]] = (rec["rejected"], rec["reason"])
                if rec["unchecked"]:
                    usage["unchecked"].append(row["id"])
                    continue
                u = meta.get("usage") or {}
                for k in ("input_tokens", "output_tokens", "cache_read_input_tokens"):
                    usage[k] += u.get(k) or 0
                usage["calls"] += 1
        print(f"checked {min(i + size, len(todo))} of {len(todo)} rows ({len(usage['unchecked'])} unchecked)",
              file=sys.stderr, flush=True)
    usage["backend"] = checker.backend.describe()           # with the structured mode the server took
    return out, usage


def scores(rows, preds, unchecked=()) -> dict:
    """Precision, recall and F1, overall and per category; a row in `unchecked` (no verdict was had) is
    left out rather than counted either way."""
    rows = [r for r in rows if r["id"] not in set(unchecked)]
    return _scores(rows, preds)


def _scores(rows, preds) -> dict:
    def prf(rs):
        tp = sum(1 for r in rs if r["label"] == "reject" and preds[r["id"]][0])
        fp = sum(1 for r in rs if r["label"] == "accept" and preds[r["id"]][0])
        fn = sum(1 for r in rs if r["label"] == "reject" and not preds[r["id"]][0])
        p = tp / (tp + fp) if tp + fp else 1.0
        rec = tp / (tp + fn) if tp + fn else 1.0
        f1 = 2 * p * rec / (p + rec) if p + rec else 0.0
        return {"n": len(rs), "tp": tp, "fp": fp, "fn": fn, "precision": p, "recall": rec, "f1": f1}
    out = {"overall": prf(rows)}
    for cat in sorted({r["category"] for r in rows}):
        out[cat] = prf([r for r in rows if r["category"] == cat])
    return out


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "unknown"


def _table(s: dict, accept_note: bool = True) -> list[str]:
    out = ["| category | n | caught / false rejects | precision | recall | F1 |", "| --- | --- | --- | --- | --- | --- |"]
    for cat, x in s.items():
        caught = f"{x['fp']} false rejects" if cat == "accepted" else f"{x['tp']} of {x['tp'] + x['fn']}"
        out.append(f"| {cat} | {x['n']} | {caught} | {x['precision']:.3f} | {x['recall']:.3f} | {x['f1']:.3f} |")
    return out


def _misses(rows, preds) -> list[str]:
    out = []
    for r in rows:
        rejected, why = preds[r["id"]]
        if (r["label"] == "reject") != rejected:
            kind = "missed" if r["label"] == "reject" else "false reject"
            out.append(f"- `{r['id']}` ({r['category']}, {kind}): {r['sentence']}  \n  reason: {why or '(none given)'}")
    return out or ["None."]


def report(rows, vpred, live) -> str:
    from jyotish.narrate import CONFIG
    vs = scores(rows, vpred)
    L = ["# Checker benchmark", "",
         f"Run {date.today().isoformat()} at commit `{_commit()}` by `scripts/checker_bench.py` on "
         f"`tests/fixtures/checker_bench.jsonl` ({len(rows)} rows: {sum(r['label'] == 'accept' for r in rows)} accept, "
         f"{sum(r['label'] == 'reject' for r in rows)} reject). The positive class is reject.", "",
         "## The code validator alone", "", *_table(vs), "",
         "The validator reads tags and words, not meaning: it is meant to catch the tag and wording categories "
         f"({', '.join(sorted(WORDING))}) and to leave the semantic ones to the checker.", "",
         "Misses and false rejects (validator alone):", "", *_misses(rows, vpred), ""]
    if live is None:
        L += ["## Validator + semantic checker (live)", "",
              "Not run: no Anthropic credentials in this environment (ANTHROPIC_API_KEY unset). Run "
              "`scripts/checker_bench.py` where they are; it fills this section with the checker's precision, recall "
              f"and F1, every miss with the checker's reason, the model ({CONFIG.model}), the checker effort "
              f"({CONFIG.checker_effort}) and the cost.", ""]
    else:
        from jyotish.costs import cost
        lp, usage, seconds = live
        ls = scores(rows, lp, usage.get("unchecked", ()))
        b = usage.get("backend") or {"provider": "anthropic", "host": "api.anthropic.com", "model": CONFIG.checker_model}
        usd = cost(b.get("model"), usage, b.get("host"))
        L += ["## Validator + semantic checker (live)", "",
              f"Checker {b.get('model')} on {b.get('host')} ({b.get('provider')}"
              + (f", structured output by {b['structured']}" if b.get("structured") else "")
              + f"), checker effort {usage.get('effort') or CONFIG.checker_effort}; {usage['calls']} checker calls, "
              f"{usage['input_tokens']} input and {usage['output_tokens']} output tokens, {seconds:.0f} s"
              + (" in this invocation (the rows carried over were checked in earlier ones)" if usage.get("resumed") else "")
              + "; cost "
              + (f"USD {usd:.2f} at jyotish.costs's prices." if usd is not None else "not known (no price for this model "
                 "in jyotish.costs; never guessed).")
              + (f" {usage['resumed']} rows were carried over from an interrupted run (--resume)." if usage.get("resumed") else "")
              + (f" Unchecked (the call failed after every retry; left out of the scores): {len(usage['unchecked'])} rows, "
                 f"{', '.join(usage['unchecked'])}." if usage.get("unchecked") else " Every row was checked."),
              "", *_table(ls), "",
              "Misses and false rejects, with the checker's reason:", "", *_misses(rows, lp), ""]
    return "\n".join(L) + "\n"


def scorecard_path(model: str, effort: str | None = None) -> Path:
    """docs/checker_scorecard_<model>.md for a backend's run, beside Opus's docs/checker_scorecard.md; at a
    checker effort other than the default, docs/checker_scorecard_<model>_effort-<effort>.md, so a run at
    another effort never writes over the gate's own scorecard."""
    return ROOT / "docs" / (f"checker_scorecard_{re.sub(r'[^A-Za-z0-9.]+', '-', model).strip('-').lower()}"
                            f"{_effort_suffix(effort)}.md")


def gate_recall(text: str) -> dict[str, float]:
    """Per category, the recall of a scorecard's live section (a gate's, or a candidate's own)."""
    if LIVE_HEADING not in text:
        return {}
    out = {}
    for line in text[text.index(LIVE_HEADING):].splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and cells[0] not in ("category", "---") and re.fullmatch(r"[0-9.]+", cells[4]):
            out[cells[0]] = float(cells[4])
    return out


def rule_section(rows, preds, gate: dict[str, float], gate_name: str, unchecked=(), gate_file: str = "") -> list[str]:
    """docs/models.md's rule: the checker's backend changes for client readings only when its recall is
    not worse on any category than the gate in use."""
    here = {cat: x["recall"] for cat, x in scores(rows, preds, unchecked).items()}
    return rule_from_recall(here, gate, gate_name, gate_file)


def gate_name_of(text: str) -> str:
    """The checker a scorecard measured: its title's model, else the live section's ("Model …" / "Checker …")."""
    m = re.search(r"^# Checker benchmark: ([^\s,]+)", text, re.M) or re.search(r"^(?:Model|Checker) (\S+?)[,\s]", text, re.M)
    return m.group(1) if m else "the gate"


def rule_from_recall(here: dict[str, float], gate: dict[str, float], gate_name: str, gate_file: str = "") -> list[str]:
    """The rule's section from two per-category recall tables (this checker's, the gate's)."""
    if not gate:
        return ["## Against the gate in use", "", f"No live run of {gate_name} on record to compare with.", ""]
    where = f" ({gate_file})" if gate_file else ""
    L = ["## Against the gate in use", "",
         f"The rule (docs/models.md): this checker may gate client readings only if its recall is not worse on any "
         f"category than the gate in use, {gate_name}{where}.", "",
         "| category | recall here | recall of the gate | not worse |", "| --- | --- | --- | --- |"]
    worse = []
    for cat in sorted(set(here) & set(gate) - {"accepted", "overall"}):
        ok = round(here[cat], 3) >= gate[cat]
        worse += [] if ok else [cat]
        L.append(f"| {cat} | {here[cat]:.3f} | {gate[cat]:.3f} | {'yes' if ok else 'no'} |")
    unmeasured = sorted(set(here) - set(gate) - {"accepted", "overall"})
    # The other way round too: a category the gate measured that this run did not (every row of it
    # unchecked) is not measured, and the verdict waits for it.
    unmeasured = sorted(set(unmeasured) | (set(gate) - set(here) - {"accepted", "overall"}))
    if unmeasured:
        L += ["", f"Measured by one run and not the other (the benchmark has grown since the gate's run, or every row "
                  f"of the category was unchecked here): {', '.join(unmeasured)}. The rule cannot be applied to these "
                  "until both runs measure them."]
    L += ["", ("Verdict: worse on " + ", ".join(worse) + ": it does not pass the rule, and client readings keep the gate "
               "in use." if worse else
               "Verdict: not worse on any category both runs measured, but not yet decided: not measured by both on "
               + ", ".join(unmeasured) + "." if unmeasured else
               "Verdict: not worse on any category: it passes the rule."), ""]
    return L


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--checker-backend", help="run the live checker on this backend (openai:<base url>:<model>) and "
                                              "write docs/checker_scorecard_<model>.md beside Opus's")
    ap.add_argument("--gate", type=Path, default=None,
                    help="the gate in use's scorecard, compared against per category (default docs/models.md's gate: "
                         "docs/checker_scorecard_zai-org-glm-5.3-flash_temp-0.md)")
    ap.add_argument("--apply-rule", type=Path, default=None, metavar="SCORECARD",
                    help="rewrite this scorecard's last section against --gate, from its own table (no model called)")
    ap.add_argument("--resume", action="store_true",
                    help="carry over the rows an interrupted live run already checked (data/bench_partial/)")
    ap.add_argument("--checker-effort", choices=("none", "low", "medium", "high", "xhigh", "max"), default=None,
                    help="the checker's effort for this run (default CONFIG.checker_effort, high); an OpenAI-compatible "
                         "backend sends it as reasoning_effort, and 'none' switches reasoning off there")
    ap.add_argument("--checker-temperature", type=float, default=None,
                    help="the checker's temperature for this run (sent as `temperature`; none is sent by default)")
    a = ap.parse_args(argv)
    if a.checker_temperature is not None:
        os.environ["JYOTISH_CHECKER_TEMPERATURE"] = str(a.checker_temperature)
    from jyotish.envfile import load as load_env
    for name in load_env(ROOT / ".env"):                  # keys from the gitignored .env; never a value printed
        print(f"{name} read from .env", file=sys.stderr)
    gate_path = a.gate or GATE
    if a.apply_rule:
        text = a.apply_rule.read_text()
        here, gate_text = gate_recall(text), gate_path.read_text()
        head = text[:text.index("## Against the gate in use")] if "## Against the gate in use" in text else text
        rel = gate_path.resolve().relative_to(ROOT) if gate_path.resolve().is_relative_to(ROOT) else gate_path
        a.apply_rule.write_text(head + "\n".join(rule_from_recall(here, gate_recall(gate_text), gate_name_of(gate_text),
                                                                   str(rel))) + "\n")
        print(f"{a.apply_rule}: the rule applied against {gate_name_of(gate_text)} ({rel})")
        return 0
    if a.build:
        rows = build()
        BENCH.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        print(f"{len(rows)} rows -> {BENCH}")
        return 0
    rows = load()
    vpred = run_validator(rows)
    if a.checker_backend and a.checker_backend != "anthropic":
        # Another backend's scorecard, beside Opus's, which it never overwrites.
        t = time.time()
        from dataclasses import replace as _replace
        from jyotish.narrate import CONFIG
        config = _replace(CONFIG, checker_effort=a.checker_effort) if a.checker_effort else CONFIG
        from jyotish.narrate import BackendFatal
        try:
            lp, usage = run_live(rows, config=config, backend=a.checker_backend, resume=a.resume)
        except BackendFatal as e:                      # no balance, a refused key: stop; the rows checked so far are kept
            print(f"stopped: {e}\nThe rows checked so far are kept; run again with --resume once it is fixed.",
                  file=sys.stderr)
            return 2
        path = scorecard_path(usage["backend"]["model"], config.checker_effort)
        gate_text = gate_path.read_text() if gate_path.exists() and gate_path != path else ""
        rel = gate_path.resolve().relative_to(ROOT) if gate_path.resolve().is_relative_to(ROOT) else gate_path
        text = report(rows, vpred, (lp, usage, time.time() - t)) + \
            "\n".join(rule_section(rows, lp, gate_recall(gate_text), gate_name_of(gate_text) if gate_text else "the gate",
                                    usage.get("unchecked", ()), str(rel))) + "\n"
        title = usage["backend"]["model"] + (f" at checker effort {config.checker_effort}" if config.checker_effort != CONFIG.checker_effort else "") \
            + (f", temperature {a.checker_temperature:g}" if a.checker_temperature is not None else "")
        path.write_text(text.replace("# Checker benchmark", f"# Checker benchmark: {title}", 1))
        s = scores(rows, lp, usage.get("unchecked", ()))["overall"]
        print(f"{usage['backend']['model']} on {usage['backend']['host']}: precision {s['precision']:.3f} recall "
              f"{s['recall']:.3f} F1 {s['f1']:.3f} -> {path}")
        return 0
    live = None
    if not a.offline and os.environ.get("ANTHROPIC_API_KEY"):
        t = time.time()
        lp, usage = run_live(rows, resume=a.resume)
        live = (lp, usage, time.time() - t)
    text = report(rows, vpred, live)
    if live is None and SCORECARD.exists() and LIVE_HEADING in (old := SCORECARD.read_text()):
        # The live run on record stays, under the new validator table, with the run it came from
        # named: an offline run must not erase the only measurement of the checker.
        head = re.search(r"Run (\d{4}-\d{2}-\d{2}) at commit `([0-9a-f]+)`", old)
        kept = old[old.index(LIVE_HEADING) + len(LIVE_HEADING):]
        if "Carried over from the run of" not in kept and head:
            kept = (f"\n\n(Carried over from the run of {head.group(1)} at commit `{head.group(2)}`; the validator table "
                    "above is from this run, the live numbers are that run's.)" + kept)
        text = text[:text.index(LIVE_HEADING) + len(LIVE_HEADING)] + kept
    SCORECARD.write_text(text)
    s = scores(rows, vpred)["overall"]
    print(f"validator alone: precision {s['precision']:.3f} recall {s['recall']:.3f} F1 {s['f1']:.3f} -> {SCORECARD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
