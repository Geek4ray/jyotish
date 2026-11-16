"""The answer plan (SPEC Layer 8, "The layered answer", rev 134; set 2026-11-15): for a turn's routed areas,
direction and question kinds, what the answer says, picked by the engine before any sentence is written.

Per area, in this order: the verdict line (the tier in plain words with the overall lean) and, where the area
depends on the birth time, its stability line; the two or three family findings that help and the one or two that
are hard, by each family's term as a percentile of 10,000 random charts (review L1); every fired cited rule of the area (a rule with a
checked source, not a draft placement), with the reductions its modifiers applied; the hidden weaknesses of the
area's main lord (the lord of its first house from the rising sign) and main significator (its first karaka) that
the lean does not show (marana karaka sthana, a Mrita avastha, a Shadbala ratio under 1); the Vimshottari period
running at the turn's date; and on a "when" turn the most and least favourable stretches with their caveat. The
question's kinds open the plan (one opening per kind, as narrate.OPENING).

Every item carries a bank signature (`data/bank/*.yaml`), its slots (the chart's values for the bank's variants),
the finding tags it rests on, the facts it states (what the checker reads it against), the engine's own sentence
(the fallback when no bank row is found) and its notes into the area's sheet. What the plan leaves out is listed
with the reason, for the worksheet. Deterministic: the same chart, route, kinds and date give the same plan.

The plan reads the chart object; the whole-chart payload (`data`) adds the sheet's notes and, on a "when" turn, the
stretches (the timing join). Without it (the coverage tool over 1,000 random charts) the stretch items are the
fixed signatures a "when" turn would carry.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from .constants import SIGN_LORD

# The parts of an answer, in the plan's order within an area.
PARTS = ("opening", "verdict", "stability", "helps", "hard", "rule", "weakness", "period", "stretch")
HELPS, HARD = 3, 2                            # at most: the two or three that help, the one or two that are hard
TIER_KEY = {"strong": "strong", "moderate": "moderate", "weak / mixed": "mixed", "not emphasised": "not_emphasised",
            "cannot be assessed": "cannot", "needs two charts": "two_charts"}
LEAN = {"supportive": "favourably", "adverse": "unfavourably"}
# A modifier a rule's fire applied (rules.py: "<condition> -> x<scale>"), in plain words for the client: the slot
# {reductions} of a reduced rule's row. A condition not listed here keeps the rule's full row out of the answer
# (the plan says so in `left_out`), rather than reaching the client in the engine's words.
REDUCTION_PLAIN = [
    (re.compile(r"^aspected_by: \[([A-Za-z, ]+)\]"), lambda m: f"{_and([_the(p) for p in m.group(1).split(', ')])}'s aspect on it"),
    (re.compile(r"^tara_from_moon in "), lambda m: "an unhelpful star counted from your Moon"),
    (re.compile(r"^marana_karaka_sthana"), lambda m: "a house that drains it"),
    (re.compile(r"^avastha in \[[a-z, ]+\] \(([A-Za-z]+)\)"), lambda m: f"{_the(m.group(1))} being in a feeble state"),
    (re.compile(r"^shadbala_ratio < 1"), lambda m: "too little strength"),
    (re.compile(r"^combust"), lambda m: "lying too close to the Sun"),
    (re.compile(r"^dignity: (great enemy|enemy)"), lambda m: "an unfriendly sign"),
    (re.compile(r"^dignity == debilitated|^dignity: debilitated"), lambda m: "a sign where it is least at ease"),
    (re.compile(r"^\{?'?lord_of'?: \[6, 8, 12\]"), lambda m: "its rule over a difficult house"),
    (re.compile(r"^class_by_(houses|lordship) == (dainya|kahala)"), lambda m: "a difficult house in the exchange"),
]
# Each rule's name with its condition in plain words, as the rule file's `when` states it (rules/yoga.*.yaml): the slot
# {named} of a rule's row and the engine's own sentence, so a Sanskrit name never reaches the client unglossed.
RULE_PLAIN = {
    "yoga.ruchaka": "Mars in its own or exalted sign in an angular house",
    "yoga.bhadra": "Mercury in its own or exalted sign in an angular house",
    "yoga.hamsa": "Jupiter in its own or exalted sign in an angular house",
    "yoga.malavya": "Venus in its own or exalted sign in an angular house",
    "yoga.sasa": "Saturn in its own or exalted sign in an angular house",
    "yoga.budhaditya": "the Sun and Mercury together in one sign",
    "yoga.gaja_kesari": "Jupiter in an angular house from the Moon",
    "yoga.gaja_kesari_bphs": "Jupiter in an angular house, joined or aspected by a helpful planet",
    "yoga.kendra_trikona_raja": "the rulers of an angular house and of a trine house, {relation}",
    "yoga.kendra_trikona_raja_weak": "the rulers of an angular house and of a trine house, {relation}, one also "
                                     "ruling a difficult house",
    "yoga.neecha_bhanga": "a planet's fall in its sign undone by the planets that rule that sign",
    "yoga.parivartana": "two planets each in the other's sign",
}
# How a pair rule's two planets are related, as its fire records it (rules.py `details.relations`): the gloss of a
# Kendra-Trikona raja yoga says which (review 2026-11-15, H2: "joined" was told for a yoga formed by aspect).
RELATION_PLAIN = {"conjunction": "together in one sign", "mutual_aspect": "aspecting each other",
                  "exchange": "each in the other's sign"}
# A hidden weakness of the main lord or significator: the body field, and its signature.
WEAKNESSES = ("mks", "mrita", "low_strength")
# Each weakness as said in the planet's one sentence ({weaknesses}; decision 2), with its own house or sign.
WEAKNESS_PLAIN = {"mks": "sits in your {house} house, which drains it",
                  "mrita": "is in a feeble state by its degree in {sign}",
                  "low_strength": "has less strength than it needs to give fully what it promises"}
# What a chart cannot give, said once for every part that needs it (SPEC Layer 8 rev 136, "The shaped answer",
# decision 1: the three-part question opened on two such lines). The kinds that need a line, in this order; an amount
# line also says there is no yes or no, and a change of job's line also says there is no date. The line's signature is
# "opening." and its kinds joined by dots, its engine sentence one of these.
CANNOT_GIVE = ("amount", "yes_no", "when", "change")
CANNOT_LINE = {
    "amount": "A chart gives no amount and makes no promise; what it shows is how well it supports {label}.",
    "yes_no": "A chart cannot answer yes or no; what it shows is which way it leans for {label}.",
    "when": "A chart gives no date for an event; what it shows are the stretches it reads as more and less "
            "favourable for {label}.",
    "change": "A chart gives no date for leaving or changing a job; what it shows are the period you are in and the "
              "stretches it reads as more and less favourable for {label}.",
    "amount.when": "A chart gives no amount and no date and makes no promise; what it shows is how well it supports "
                   "{label} and the stretches it reads as more and less favourable.",
    "yes_no.when": "A chart cannot answer yes or no or give a date; what it shows is which way it leans for {label} "
                   "and the stretches it reads as more and less favourable.",
    "amount.change": "A chart gives no amount, makes no promise and gives no date for leaving or changing a job; what "
                     "it shows is how well it supports {label}, the period you are in and the stretches it reads as "
                     "more and less favourable.",
    "yes_no.change": "A chart cannot answer yes or no or give a date for leaving or changing a job; what it shows is "
                     "which way it leans for {label}, the period you are in and the stretches it reads as more and "
                     "less favourable.",
}


def cannot_give(kinds: list[str], when: bool = True) -> list[str]:
    """The kinds a cannot-give line says, in CANNOT_GIVE's order: "when" only on a turn that gives stretches."""
    need = [k for k in CANNOT_GIVE if k in kinds and (k not in ("when", "change") or when)]
    if "amount" in need and "yes_no" in need:
        need.remove("yes_no")
    if "change" in need and "when" in need:
        need.remove("when")
    return need


class PlanItem(BaseModel):
    part: str                                       # one of PARTS
    signature: str                                  # the bank row this item looks for
    area: str | None = None
    slots: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)   # the finding tags it rests on (vote:, rule:)
    facts: dict[str, Any] = Field(default_factory=dict)   # what the chart states for it: what a fact row is checked against
    engine: str                                     # the engine's own sentence: the fallback when no row is found
    notes: list[dict[str, Any]] = Field(default_factory=list)   # notes into the area's sheet
    # The meaning row's signature, where it is not the item's own (a vocation item reads its planet's kinds of work,
    # `vocation.works.<planet>`; decision 3).
    meaning: str | None = None


class AnswerPlan(BaseModel):
    question: str
    areas: list[str]
    direction: str
    kinds: list[str]
    when: bool
    as_of: str
    items: list[PlanItem]
    left_out: list[dict[str, Any]] = Field(default_factory=list)   # {area, what, why}: the worksheet's last column
    # The message's asks in the order asked, {kind, areas} (conversation.parts_of; decision 1). Empty for a plan made
    # with none (the coverage and drafting tools): the composer reads it as one general ask, then "when", then "why".
    parts: list[dict[str, Any]] = Field(default_factory=list)

    def signatures(self) -> list[str]:
        return [i.signature for i in self.items]


def _the(planet: str) -> str:
    return f"the {planet}" if planet in ("Sun", "Moon") else planet


def _and(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def reductions_plain(applied: list[str]) -> tuple[list[str], list[str]]:
    """(plain phrases, conditions with no plain phrase) for a fire's applied modifiers that reduce it (scale < 1)."""
    plain, unknown = [], []
    for a in applied:
        cond, _, scale = a.rpartition(" -> x")
        try:
            if float(scale) >= 1:
                continue
        except ValueError:
            pass
        for rx, say in REDUCTION_PLAIN:
            if (m := rx.search(cond)):
                plain.append(say(m))
                break
        else:
            unknown.append(cond)
    return list(dict.fromkeys(plain)), unknown


def _stub_sheet() -> dict:
    """A sheet with no items: narrate's sentence helpers write their text and find no note."""
    return {"points": [{"n": 10, "table": {"rows": []}}]}


def _main_lord(chart, area: str) -> tuple[str, int] | None:
    from .scoring import AREAS
    spec = AREAS.get(area) or {}
    houses = spec.get("houses") or []
    if not houses:
        return None
    return SIGN_LORD[(chart.lagnas.asc_sign + houses[0] - 1) % 12], houses[0]


def _area_data(chart, area: str, data: dict | None) -> dict:
    """The area's fields as the payload states them (data["areas"][area]), from the chart object when no payload."""
    if data is not None and area in data.get("areas", {}):
        return data["areas"][area]
    a = chart.scored.areas[area]
    st = a.stability
    st = st.model_dump() if hasattr(st, "model_dump") else st
    return {"tier": a.tier, "direction": a.direction, "stability": st, "main_karaka": a.karakas[0] if a.karakas else None,
            "votes": {f: {"vote": v, "derivation": a.vote_details.get(f)} for f, v in a.votes.items()}}


def about(chart, area: str, label: str) -> dict[str, Any]:
    """What an area item is about, as the chart and the engine's area table state it: the area and its words, its
    houses from the rising sign (the first is its main house), the lord of that house and its karakas (the first is
    its main significator). Every item's facts carry it, so the checker reads "the main one, your 10th house" or
    "the planets that signify your career" against a stated fact."""
    from .scoring import AREAS
    spec = AREAS.get(area) or {}
    a = chart.scored.areas.get(area)
    ml = _main_lord(chart, area)
    return {"area": area, "area_words": label, "area_houses_from_rising_sign": spec.get("houses"),
            "main_house": ml[1] if ml else None, "main_house_lord": ml[0] if ml else None,
            "significators": a.karakas if a is not None else None,
            "main_significator": a.karakas[0] if a is not None and a.karakas else None}


def _family_item(chart, fam: str, v: dict, area: str, label: str, part: str, data: dict | None, sheet: dict,
                 term: float | None) -> PlanItem | None:
    from .narrate import DIGNITY_PLAIN, _ORD, _family_sentence, _rel_phrase
    side = "for" if v["vote"] > 0 else "against"
    pseudo = data if data is not None else {"areas": {area: _area_data(chart, area, None)}}
    s = _family_sentence(fam, v, label, pseudo, area, sheet)
    if s is None:
        return None
    der = v.get("derivation")
    rows = [r for r in der if isinstance(r, dict)] if isinstance(der, list) else []
    dig = lambda d: DIGNITY_PLAIN.get(d, "")
    slots: dict[str, str] = {"area": label}
    sig = f"family.{fam}.{side}"
    if fam == "house":
        r = rows[0]
        agrees = (r["relative"] > 0) == (v["vote"] > 0) and r["relative"] != 0
        sig += ".agrees" if agrees else ".though"
        slots |= {"house": _ORD[r["house"]], "sign": r["sign"], "standing": _rel_phrase(r["relative"])}
    elif fam == "lord":
        r = rows[0]
        slots |= {"planet": _the(r["lord"]), "ruled_house": _ORD[r["house"]], "sign": r["lord_sign"],
                  "house": _ORD[r["lord_house_from_lagna"]], "dignity": dig(r.get("dignity"))}
    elif fam == "karaka":
        main = pseudo["areas"][area].get("main_karaka")
        r = next((x for x in rows if x["planet"] == main), rows[0])
        slots |= {"planet": _the(r["planet"]), "sign": r["sign"], "house": _ORD[r["house"]], "dignity": dig(r.get("dignity"))}
    elif fam == "varga":
        from .narrate import VARGA_PLAIN, varga_row
        r, own = varga_row(rows, v["vote"], area)
        slots |= {"planet": _the(r["planet"]), "sign": r["varga_sign"], "dignity": dig(r.get("varga_dignity_label"))}
        if not own:
            # Not the area's own divisional chart: named as what it is (`.other`, {varga}; the open wording of
            # 2026-11-15, fixed 2026-11-16).
            sig += ".other"
            slots["varga"] = VARGA_PLAIN.get(r["varga"], "a divisional chart")
    elif fam == "arudha":
        padas = der["padas"]
        signs = list(dict.fromkeys(p["sign"] for p in padas))
        occ = list(dict.fromkeys(o for p in padas for o in p.get("occupants", [])))
        ben = list(dict.fromkeys(b for p in padas for b in p.get("benefics", [])))
        hard = [o for o in occ if o not in ben]
        n = "many" if len(signs) > 1 else "one"
        slots["signs"] = _and(signs)
        # Over several signs each planet is named with its own sign (review 2026-11-15, H1: "Ketu, Saturn and Rahu
        # sit in one of these signs" told a placement no chart can have): {placed}, {helpers_placed}.
        sign_of = {}
        for p in padas:
            for o in p.get("occupants", []):
                sign_of.setdefault(o, p["sign"])
        placed = lambda ps: _and([f"{_the(p)} in {sign_of[p]}" if p in sign_of else _the(p) for p in ps])
        if v["vote"] < 0 and hard:
            sig += f".{n}.hard" + (".helped" if ben else ".alone")
            slots["planets"] = _and([_the(p) for p in hard])
            slots["sits"] = "sits" if len(hard) == 1 else "sit"
            if n == "many":
                slots["placed"] = placed(hard)
            if ben:
                slots["helpers"] = _and([_the(p) for p in ben])
                if n == "many":
                    slots["helpers_placed"] = placed(ben)
        elif v["vote"] > 0 and ben:
            sig += f".{n}.helped"
            slots["helpers"] = _and([_the(p) for p in ben])
            slots["sits"] = "sits" if len(ben) == 1 else "sit"
            if n == "many":
                slots["helpers_placed"] = placed(ben)
        else:
            sig += f".{n}.plain"
    elif fam == "panchanga":
        from .narrate import panchanga_ruled
        planets = list(dict.fromkeys(r["planet"] for r in rows))
        sig += ".many" if len(planets) > 1 else ".one"
        # Each with what it rules on the day of birth (2026-11-16): {ruled} for several, {ruler} for one; no bare
        # {planets}, so no row can call them all "the rulers of the day".
        slots["ruled" if len(planets) > 1 else "ruler"] = panchanga_ruled(rows)
    extra = {}
    if fam == "panchanga":
        # What each role is, so "which rules the lunar day" is checked against a stated fact (2026-11-16).
        from .narrate import PANCHANGA_ROLE
        extra["panchanga_roles"] = {r: f"the planet in this role is the lord (ruler) of the {r}: in plain words, it "
                                       f"rules {w}" for r, w in PANCHANGA_ROLE.items()}
        extra["panchanga_roles"]["vara"] += " (the weekday of birth: only this lord is the ruler of the day)"
    return PlanItem(part=part, signature=sig, area=area, slots=slots, tags=[f"vote:{area}.{fam}"],
                    facts={"family": fam, "lean": "favourable" if v["vote"] > 0 else "unfavourable", "term": term,
                           "derivation": der, "about": about(chart, area, label)} | extra, engine=s.text,
                    notes=s.notes)


def _rule_item(chart, f: dict, area: str, label: str) -> tuple[PlanItem | None, str | None]:
    """A fired cited rule: its full row, or its reduced row naming the reductions (each fire's, merged)."""
    from .narrate import _ORD, rule_names
    applied = [a for x in f["fires"] for a in x["modifiers_applied"]]
    plain, unknown = reductions_plain(applied)
    if unknown:
        return None, f"a reduction with no plain words yet ({', '.join(unknown)})"
    name = rule_names(f["rule_id"])[0]
    houses = sorted({int(n[1:]) for x in f["fires"] if x["basis"] == "lagna" for n in x["nodes"] if n.startswith("H")})
    planets = [_the(p) for p in f["planets"]]
    relations = list(dict.fromkeys(r for x in f["fires"] for r in (x.get("details") or {}).get("relations") or []))
    gloss = RULE_PLAIN.get(f["rule_id"])
    if gloss and "{relation}" in gloss:
        if not relations or any(r not in RELATION_PLAIN for r in relations):
            return None, f"a relation with no plain words yet ({', '.join(relations) or 'none recorded'})"
        gloss = gloss.format(relation=_and([RELATION_PLAIN[r] for r in relations]))
    # A rule counted from several points (the rising sign, the Moon, the Sun) whose fires here are none from the
    # rising sign: the gloss says what the angle is counted from (review H2: the gloss holds for every basis).
    bases = [x["basis"] for x in f["fires"]]
    if gloss and "angular house" in gloss and "from the Moon" not in gloss and "lagna" not in bases:
        froms = _and([{"moon": "your Moon", "sun": "your Sun"}.get(b, b) for b in dict.fromkeys(bases)])
        gloss = gloss.replace("an angular house", f"an angular house from {froms}", 1)
    named = f"{name} ({gloss})" if gloss else name
    # Each planet with its own house from the rising sign, or one house for them all ({placed}): "Mercury in your 1st
    # house and Jupiter in your 7th house", never "Mercury and Jupiter in your 1st and 7th house" (review H2).
    placed = ""
    if houses and f["planets"] and all(p in chart.bodies for p in f["planets"]):
        at = {p: chart.bodies[p].house for p in f["planets"]}
        if len(set(at.values())) == 1:
            placed = f"{_and(planets)} in your {_ORD[next(iter(at.values()))]} house"
        else:
            placed = _and([f"{_the(p)} in your {_ORD[h]} house" for p, h in at.items()])
    slots = {"area": label, "name": name, "named": named, "planets": _and(planets) if planets else "",
             "houses": _and([_ORD[h] for h in houses]) if houses else "", "placed": placed}
    if plain:
        slots["reductions"] = _and(plain)
    who = (f", formed by {placed}," if placed else f", formed by {slots['planets']}," if planets else "")
    engine = (f"Your chart holds {named}{who} which bears on {label}"
              + (f", though it is weakened by {slots['reductions']}." if plain else "."))
    sig = f"rule.{f['rule_id']}.{'reduced' if plain else 'full'}"
    if not houses:
        sig += ".nohouse"
    return PlanItem(part="rule", signature=sig, area=area, slots=slots, tags=list(f["allowed_tags"]),
                    facts={"rule_id": f["rule_id"], "names": rule_names(f["rule_id"]), "fires": f["fires"],
                           "planets": f["planets"], "houses": houses, "reductions": plain, "relations": relations,
                           "planet_houses": {p: chart.bodies[p].house for p in f["planets"] if p in chart.bodies},
                           "about": about(chart, area, label)}, engine=engine), None


def _weakness_items(chart, area: str, label: str, data: dict | None, sheet: dict) -> list[PlanItem]:
    from .narrate import _ORD, _sheet_note
    ad = _area_data(chart, area, data)
    who: list[tuple[str, str, str]] = []
    ml = _main_lord(chart, area)
    if ml:
        who.append((ml[0], f"the ruler of your {_ORD[ml[1]]} house", "lord"))
    k = ad.get("main_karaka")
    # "the main planet for your father", never "of" (review 2026-11-15, L6: read as the father's planet).
    if k and k not in [w[0] for w in who]:
        who.append((k, f"the main planet for {label}", "karaka"))
    elif k:
        who[0] = (who[0][0], who[0][1] + f" and the main planet for {label}", "lord+karaka")
    sb = chart.features.shadbala.planets if chart.features.shadbala else {}
    out = []
    for planet, role, kind in who:
        b = chart.bodies.get(planet)
        if b is None:
            continue
        ratio = sb[planet].ratio if planet in sb else None
        found = [("mks", b.marana_karaka_sthana, {"marana_karaka_sthana": True, "house": b.house}),
                 ("mrita", b.avastha_baladi == "Mrita", {"avastha_baladi": "Mrita"}),
                 ("low_strength", ratio is not None and ratio < 1, {"shadbala_ratio": round(ratio or 0, 2)})]
        found = [(w, fact) for w, on, fact in found if on]
        if not found:
            continue
        # One sentence per planet, its weaknesses in one list (SPEC Layer 8 rev 136, "The shaped answer", decision 2:
        # the three-part question had three of Saturn's in a row). Each is said with its own place, never "whatever
        # the sign says" (the row that composed "no matter what Taurus says").
        said = [WEAKNESS_PLAIN[w].format(house=_ORD[b.house], sign=b.sign_name) for w, _ in found]
        weaknesses = said[0] if len(said) == 1 else f"{said[0]}, and it {said[1]}" if len(said) == 2 else \
            "; it ".join(said[:-1]) + f"; and it {said[-1]}"
        slots = {"area": label, "planet": _the(planet), "role": role, "weaknesses": weaknesses}
        engine = f"{role[0].upper() + role[1:]}, {_the(planet)}, {weaknesses}."
        notes = [n for n in [_sheet_note(sheet, 2 if "lord" in kind else 3, f"planets.{planet}", area)] if n]
        facts = {"planet": planet, "role": kind, "sign": b.sign_name, "house": b.house, "weaknesses": [w for w, _ in found],
                 "about": about(chart, area, label)}
        for _, fact in found:
            facts |= fact
        out.append(PlanItem(part="weakness", signature="weakness.planet", area=area, slots=slots,
                            tags=[f"vote:{area}.{'lord' if 'lord' in kind else 'karaka'}"], facts=facts,
                            engine=engine, notes=notes))
    return out


# The field of work (SPEC Layer 8 rev 136, "The shaped answer", decision 3): what the engine computes and nothing
# else, nothing of it weighing in scoring. The 10th house from the rising sign (its sign and its ruler, with the
# ruler's sign and house), each planet in it, and each of the seven planets the D10 holds in its own or exalted sign
# (scoring.varga_dignity_word, the varga vote's words). In that order of preference, the first of each kind before
# the second of any: the 10th and its ruler, a planet in it, a strong D10 planet, then the rest. Each item's meaning
# is its planet's kinds of work (`vocation.works.<planet>@career`, draft until the astrologer approves it). The
# classical karmajiva lord (the ruler of the navamsa the 10th lord occupies) is left out: its method was not read in
# a named edition (docs/spec_notes_2026-11-16.md).
VOCATION_DIGNITY = {"exalted": "exalted, where it is at its best", "own": "in its own sign"}


def _vocation_items(chart, label: str) -> list[PlanItem]:
    from .constants import SIGNS
    from .narrate import _ORD
    from .scoring import varga_dignity_word
    asc = chart.lagnas.asc_sign
    tenth = (asc + 9) % 12
    ruler = SIGN_LORD[tenth]
    rb = chart.bodies[ruler]
    about_ = about(chart, "career", label)
    first = PlanItem(part="vocation", signature="vocation.tenth", area="career", meaning=f"vocation.works.{ruler.lower()}",
                     slots={"area": label, "sign": SIGNS[tenth], "planet": _the(ruler), "in_sign": rb.sign_name,
                            "house": _ORD[rb.house]},
                     facts={"tenth_house_sign": SIGNS[tenth], "tenth_house_ruler": ruler, "ruler_sign": rb.sign_name,
                            "ruler_house": rb.house, "about": about_},
                     engine=f"Your 10th house, the house of work, is in {SIGNS[tenth]}, and its ruler, {_the(ruler)}, "
                            f"sits in {rb.sign_name} in your {_ORD[rb.house]} house.")
    order = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
    inside = [PlanItem(part="vocation", signature="vocation.in_tenth", area="career",
                       meaning=f"vocation.works.{p.lower()}", slots={"area": label, "planet": _the(p)},
                       facts={"planet": p, "house": 10, "sign": chart.bodies[p].sign_name, "about": about_},
                       engine=f"{_the(p)[0].upper() + _the(p)[1:]} sits in your 10th house, the house of work.")
              for p in order if p in chart.bodies and chart.bodies[p].house == 10]
    d10 = chart.vargas.get("D10") or {}
    strong = []
    for p in order[:7]:
        if p not in d10:
            continue
        word = varga_dignity_word(p, d10[p])
        if word in VOCATION_DIGNITY:
            strong.append(PlanItem(part="vocation", signature="vocation.d10", area="career",
                                   meaning=f"vocation.works.{p.lower()}",
                                   slots={"area": label, "planet": _the(p), "sign": SIGNS[d10[p]],
                                          "dignity": VOCATION_DIGNITY[word]},
                                   facts={"planet": p, "varga": "D10", "varga_sign": SIGNS[d10[p]],
                                          "varga_dignity_label": word, "about": about_},
                                   engine=f"In the divisional chart for work, {_the(p)} is in {SIGNS[d10[p]]}, "
                                          f"{VOCATION_DIGNITY[word]}."))
    rest = inside[1:] + strong[1:]
    return [first] + inside[:1] + strong[:1] + rest


def _period_item(chart, area: str, label: str, as_of: date) -> PlanItem | None:
    import swisseph as swe
    from .chains import current_lords
    lords = dict(current_lords(chart, as_of))
    if "mahadasha" not in lords or "antardasha" not in lords:
        return None
    jd = swe.julday(as_of.year, as_of.month, as_of.day, 0.0)
    p = next((p for p in chart.dashas.get("vimshottari", []) if len(p.lords) == 2 and p.start_jd <= jd < p.end_jd), None)
    y, m, d, _ = swe.revjul(p.end_jd)
    until = date(y, m, int(d)).strftime("%B %Y")
    a = chart.scored.areas[area]
    touched = [x for x in (lords["mahadasha"], lords["antardasha"]) if x in a.lords or x in a.karakas]
    maha, antar = _the(lords["mahadasha"]), _the(lords["antardasha"])
    slots = {"area": label, "maha": maha, "antar": antar, "until": until}
    # A lord in its own sub-period is one planet (review L6: "the period of Mercury, within that of Mercury ...
    # neither rules nor signifies"): `.same`, said as its own sub-period.
    same = lords["mahadasha"] == lords["antardasha"]
    within = "in its own sub-period" if same else f"within that of {antar}"
    if touched:
        slots["touching"] = _and([_the(x) for x in dict.fromkeys(touched)])
        engine = (f"You are in the period of {maha}, {within}, until {until}; "
                  f"{slots['touching']} {'has' if len(set(touched)) == 1 else 'have'} a hand in {label}.")
    else:
        engine = (f"You are in the period of {maha}, {within}, until {until}; "
                  f"{'it neither rules' if same else 'neither rules'} nor signifies {label}.")
    sig = f"period.now.{'touches' if touched else 'apart'}" + (".same" if same else "")
    return PlanItem(part="period", signature=sig, area=area,
                    slots=slots, facts={"mahadasha": lords["mahadasha"], "antardasha": lords["antardasha"],
                                        "until": until, "area_lords": a.lords, "area_karakas": a.karakas,
                                        "touching": touched, "about": about(chart, area, label)},
                    engine=engine)


def _stretch_items(area: str, label: str, data: dict | None, sheet: dict, hard_first: bool) -> list[PlanItem]:
    from .narrate import NO_STRETCHES, _months, _window_sentences
    if area in NO_STRETCHES:
        return []
    if data is None:                                 # the coverage tool: the signatures a "when" turn carries
        return [PlanItem(part="stretch", signature=s, area=area, engine="",
                         slots={"area": label, "when": ""} if "caveat" not in s else {}) for s in
                ("stretch.most.first", "stretch.least.second", "stretch.caveat.two")]
    sents = _window_sentences(area, label, data, sheet, hard_first)
    if not sents:
        return []
    tm = (data.get("timing") or {}).get(area) or {}
    ws, av = tm.get("windows") or [], tm.get("avoid")
    i = max(range(len(ws)), key=lambda k: ws[k]["score"])
    pieces = [("most", _months(ws[i]["start"], ws[i]["end"]), {"window": ws[i]})]
    if av:
        pieces.append(("least", _months(av["start"], av["end"]), {"window": av}))
        if hard_first:
            pieces.reverse()
    out = []
    for k, ((kind, when, fact), s) in enumerate(zip(pieces, sents)):
        out.append(PlanItem(part="stretch", signature=f"stretch.{kind}.{'first' if k == 0 else 'second'}", area=area,
                            slots={"area": label, "when": when}, facts=fact, engine=s.text, notes=s.notes))
    caveat = sents[-1]
    out.append(PlanItem(part="stretch", signature=f"stretch.caveat.{'two' if len(pieces) > 1 else 'one'}", area=area,
                        engine=caveat.text, notes=caveat.notes))
    return out


# A family that votes with no term in the score (arudha, KP) has no percentile; it is ranked as the middle of the
# population (review 2026-11-15, L1), neither unusually strong nor unusually weak.
NO_TERM_PERCENTILE = 50.0


def _percentiles(chart, a, area: str) -> dict[str, float | None]:
    """Each voting family's term as a percentile of its terms over 10,000 random charts (fullchart.contributions, as
    depth full ranks "the strongest support"): the terms are on different scales (the lord term sums fifteen rows),
    so a term compared with a vote, as before, decided by its scale which families were said (review L1). None for a
    family with no term."""
    from .fullchart import contributions
    pct = {r["family"]: r.get("percentile") for r in contributions(a, area, chart)["ranked"]}
    return {f: pct.get(f) for f, v in a.votes.items() if v}


def plan(chart, question: str, areas: list[str], direction: str, kinds: list[str], *, as_of: date,
         when: bool = False, weakest: bool = False, data: dict | None = None,
         parts: list[dict] | None = None) -> AnswerPlan:
    """The plan for one turn (the module docstring)."""
    from .narrate import CLIENT_AREA, OPENING, STABILITY_PLAIN, TIER_SENTENCE, _and as n_and, _cap, _sheet_note, findings
    from .sheet import build
    items: list[PlanItem] = []
    left: list[dict[str, Any]] = []
    parts = [dict(p) for p in parts or []]
    labels = {a: CLIENT_AREA.get(a, a.replace("_", " ")) for a in areas}
    joined = n_and([labels[a] for a in areas]) if areas else "this part of your life"
    # One line of what a chart cannot give, for every part that needs it, about those parts' areas (decision 1).
    need = cannot_give(kinds, when)
    if need:
        asked = [a for p in parts if cannot_give([p["kind"]], when) for a in p.get("areas") or areas]
        asked = [a for a in dict.fromkeys(asked) if a in labels] or list(areas)
        said = n_and([labels[a] for a in asked]) if asked else "this part of your life"
        key = ".".join(need)
        items.append(PlanItem(part="opening", signature=f"opening.{key}", slots={"area": said},
                              facts={"question_kinds": need, "areas": asked, "area_words": said},
                              engine=CANNOT_LINE[key].format(label=said)))
    if "why" in kinds:
        items.append(PlanItem(part="opening", signature="opening.why", slots={"area": joined},
                              facts={"question_kind": "why", "areas": list(areas), "area_words": joined},
                              engine=OPENING["why"].format(label=joined)))
    if weakest and areas:
        adverse = [a for a in areas if _area_data(chart, a, data).get("direction") == "adverse"]
        if adverse:
            items.append(PlanItem(part="opening", signature="opening.weakest.adverse",
                                  slots={"areas": n_and([labels[a] for a in adverse])},
                                  engine=f"On balance, your chart works against you in {n_and([labels[a] for a in adverse])}."))
        else:
            items.append(PlanItem(part="opening", signature="opening.weakest.none", slots={"areas": joined},
                                  engine=f"No part of your chart works against you on balance; the parts it supports "
                                         f"least are {joined}."))
    for area in areas:
        label = labels[area]
        if area not in chart.scored.areas or chart.scored.areas[area].score_classical is None:
            tier = chart.scored.areas[area].tier if area in chart.scored.areas else "needs two charts"
            tier = tier if tier in TIER_KEY else "cannot be assessed"
            items.append(PlanItem(part="verdict", signature=f"verdict.{TIER_KEY[tier]}", area=area,
                                  slots={"area": label, "Area": _cap(label)},
                                  engine=TIER_SENTENCE[tier].format(label=label, Label=_cap(label), lean="")))
            continue
        ad = _area_data(chart, area, data)
        sheet = build(data, area) if data is not None else None
        sheet = sheet or _stub_sheet()
        a = chart.scored.areas[area]
        lean = LEAN.get(ad.get("direction"), "neither way")
        tier = ad["tier"]
        st_note = _sheet_note(sheet, 14, f"areas.{area}.stability", area)
        items.append(PlanItem(part="verdict", signature=f"verdict.{TIER_KEY[tier]}", area=area,
                              slots={"area": label, "Area": _cap(label), "lean": lean},
                              tags=[f"vote:{area}.{f}" for f, v in a.votes.items() if v],
                              facts={"tier": tier, "direction": ad.get("direction"), "about": about(chart, area, label)},
                              engine=TIER_SENTENCE[tier].format(label=label, Label=_cap(label), lean=lean),
                              notes=[n for n in [_sheet_note(sheet, 10, None, area), st_note] if n]))
        label_st = (ad.get("stability") or {}).get("label")
        if label_st in STABILITY_PLAIN:
            items.append(PlanItem(part="stability", signature=f"stability.{label_st}", area=area,
                                  facts={"stability": ad.get("stability")}, engine=STABILITY_PLAIN[label_st],
                                  notes=[st_note] if st_note else []))
        # The family findings, by the strength of their terms in the area's score.
        voted = [(f, v) for f, v in ad["votes"].items() if v["vote"] in (1, -1)]
        pct = _percentiles(chart, a, area)
        rank = {f: NO_TERM_PERCENTILE if pct.get(f) is None else pct[f] for f, _ in voted}
        # What helps most: the highest percentiles; what is hardest: the lowest.
        helps = sorted([x for x in voted if x[1]["vote"] > 0], key=lambda x: (-rank[x[0]], x[0]))
        hard = sorted([x for x in voted if x[1]["vote"] < 0], key=lambda x: (rank[x[0]], x[0]))
        for part, chosen, rest in (("helps", helps[:HELPS], helps[HELPS:]), ("hard", hard[:HARD], hard[HARD:])):
            for fam, v in chosen:
                it = _family_item(chart, fam, v, area, label, part, data, sheet, a.terms.get(fam))
                if it is not None:
                    it.facts["percentile"] = pct.get(fam)
                    it.facts["ranked_at"] = rank[fam]
                if it is None:
                    left.append({"area": area, "what": f"vote:{area}.{fam}", "why": "no sentence for this derivation"})
                else:
                    items.append(it)
            for fam, _ in rest:
                left.append({"area": area, "what": f"vote:{area}.{fam}",
                             "why": f"a less unusual term (by percentile) than the {len(chosen)} that "
                                    f"{'help' if part == 'helps' else 'are hard'}"})
        for fam, v in ad["votes"].items():
            if v["vote"] == 0:
                left.append({"area": area, "what": f"vote:{area}.{fam}", "why": "abstains"})
        # Every fired cited rule; the draft placements, the chains and what depends on the birth time stay out.
        ok, shaky = findings(chart, area, as_of)
        for f in ok:
            if f["kind"] == "rule" and f.get("status") != "draft":
                it, why = _rule_item(chart, f, area, label)
                if it is None:
                    left.append({"area": area, "what": f["finding_id"], "why": why})
                else:
                    items.append(it)
            elif f["kind"] == "rule":
                left.append({"area": area, "what": f["finding_id"],
                             "why": "a draft placement: drafted from principles, not read in its verse"})
            elif f["kind"] == "chain":
                left.append({"area": area, "what": f["finding_id"], "why": "a chain of sign rulers: the sheet's"})
        for f in shaky:
            left.append({"area": area, "what": f["finding_id"], "why": "depends on the exact birth time"})
        items += _weakness_items(chart, area, label, data, sheet)
        if area == "career" and any(p.get("kind") == "vocation" and area in (p.get("areas") or areas) for p in parts):
            items += _vocation_items(chart, label)
        if (it := _period_item(chart, area, label, as_of)):
            items.append(it)
        if when:
            items += _stretch_items(area, label, data, sheet, hard_first=direction == "against")
    items, left = _once(items, left, labels)
    return AnswerPlan(question=question, areas=list(areas), direction=direction, kinds=list(kinds), when=when,
                      as_of=as_of.isoformat(), items=items, left_out=left, parts=parts)


def _once(items: list[PlanItem], left: list[dict], labels: dict[str, str]) -> tuple[list[PlanItem], list[dict]]:
    """A turn over several areas says each rule, each hidden weakness and the period once (2026-11-15: the weakest
    areas' answer told Saturn's three weaknesses twice and the period three times). A rule names every area it bears
    on; a weakness is said for its first area; the period is one item, with every area its lords touch."""
    from .narrate import _and as n_and
    out: list[PlanItem] = []
    rules: dict[str, PlanItem] = {}
    weak: set[tuple] = set()
    periods = [i for i in items if i.part == "period"]
    for i in items:
        if i.part == "rule":
            key = i.facts.get("rule_id"), tuple(i.facts.get("planets") or []), tuple(i.facts.get("houses") or [])
            if key in rules:
                first = rules[key]
                first.facts.setdefault("areas", [first.area]).append(i.area)
                first.slots["area"] = n_and([labels[a] for a in first.facts["areas"]])
                # Each area's own words, for its own meaning row (review M7).
                first.facts["area_labels"] = {a: labels[a] for a in first.facts["areas"]}
                continue
            rules[key] = i
        elif i.part == "weakness":
            key = i.facts.get("planet"), i.slots.get("weaknesses")
            if key in weak:
                left.append({"area": i.area, "what": f"{i.signature}:{i.facts.get('planet')}",
                             "why": "said for an earlier area of this answer"})
                continue
            weak.add(key)
        elif i.part == "period" and len(periods) > 1:
            continue
        out.append(i)
    if len(periods) > 1:
        p0 = periods[0]
        touched = [p.area for p in periods if p.signature.startswith("period.now.touches")]
        lords = [x for p in periods for x in (p.facts.get("touching") or [])]
        slots = dict(p0.slots) | {"area": n_and([labels[a] for a in (touched or [p.area for p in periods])])}
        # Each lord with the areas it has a hand in (review 2026-11-15, M7: "Jupiter and Mercury have a hand in your
        # father, your reputation and ..." where Mercury touches no reputation).
        hands = {x: [p.area for p in periods if x in (p.facts.get("touching") or [])] for x in dict.fromkeys(lords)}
        the = lambda x: "the " + x if x in ("Sun", "Moon") else x
        same = p0.facts.get("mahadasha") == p0.facts.get("antardasha")
        sig = ("period.now.touches" if touched else "period.now.apart") + (".same" if same else "")
        if touched:
            slots["touching"] = n_and([the(x) for x in hands])
        if touched and len({tuple(v) for v in hands.values()}) > 1:
            sig = "period.now.touches.each"
            parts = [f"{the(x)} {'has a hand ' if k == 0 else ''}in {n_and([labels[a] for a in v])}"
                     for k, (x, v) in enumerate(hands.items())]
            slots["hands"] = ", ".join(parts[:-1]) + ", and " + parts[-1]
            engine = (f"You are in the period of {slots['maha']}, within that of {slots['antar']}, until "
                      f"{slots['until']}; {slots['hands']}.")
        else:
            within = "in its own sub-period" if same else f"within that of {slots['antar']}"
            engine = (f"You are in the period of {slots['maha']}, {within}, until {slots['until']}; "
                      + (f"{slots['touching']} {'have' if ' and ' in slots['touching'] else 'has'} a hand in {slots['area']}."
                         if touched else f"{'it neither rules' if same else 'neither rules'} nor signifies {slots['area']}."))
        item = p0.model_copy(update={"signature": sig, "slots": slots, "engine": engine, "area": p0.area,
                                     "facts": p0.facts | {"areas": [p.area for p in periods], "touched_areas": touched,
                                                          "hands": hands}})
        at = next(k for k, i in enumerate(out) if i.part in ("stretch",)) if any(i.part == "stretch" for i in out) else len(out)
        out.insert(at, item)
    return out, left
