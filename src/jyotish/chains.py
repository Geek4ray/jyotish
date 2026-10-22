"""Dispositor chains as findings of the reading (SPEC Layer 2, dispositor analysis; Layer 7
item 8).

For each area there is one chain finding for the area's primary lord (the lord of its first
house from the lagna) and one for its main karaka (the first karaka of the area's signal list).
A karaka that is the primary lord as well is the lord's finding only. Each finding carries:
  - the sign chain to its end, each step with the planet, its sign, its house from the lagna and
    its dignity; the nakshatra chain the same way, each step with its nakshatra too; and the
    navamsa chain, with the D9 sign, the house from the D9 lagna and the dignity there;
  - per chain, the loop it ends in, and whether the planet is in that loop and with whom;
  - every mutual exchange (sign, nakshatra or navamsa) the planet is part of;
  - the Nadi activation of the current mahadasha and antardasha lords (SPEC Layer 2: a period
    activates its lord, the planets in its nakshatras and its own nakshatra lord), where the
    planet is in that set. Only with a reading date (`as_of`).
One finding more per chart, in the personality area: the final dispositors of the whole chart in
each chain, with the bodies (the lagna included) that end in each.

The rows are the engine's; `facts` states them in sentences, and those are what the semantic
checker reads a [chain:<area>.<lord|karaka|chart>] sentence against. Stability: the smallest
time-share of what the chains' steps state: the D1 sign of every planet passed (every step names
its sign and house) and of the lagna (the house numbers), the D9 sign of every planet in the
navamsa chain and of the D9 lagna, and the nakshatra of every planet in the nakshatra chain,
from the sampler's nakshatra block (review 2026-10-23, F6). A chart stored before that block
existed gives the number without the nakshatra links."""

from __future__ import annotations

from datetime import date
from typing import Any

from .constants import EXALTATION, GRAHAS, SIGN_LORD, SIGNS
from .dignity import natural_relation
from .models import Chart

KINDS = ("sign", "nakshatra", "navamsa")
KIND_WORDS = {"sign": "sign", "nakshatra": "nakshatra", "navamsa": "navamsa"}
_ORD = {1: "1st", 2: "2nd", 3: "3rd"} | {n: f"{n}th" for n in range(4, 13)}
DISPOSITOR = ("A dispositor is the lord of the sign (or nakshatra, or navamsa sign) a planet occupies; following "
              "each lord to its own lord ends in a final dispositor, a planet in its own sign, or a loop of planets "
              "that hold each other's signs.")


def sign_dignity(planet: str, sign: int) -> str:
    """Dignity by sign alone (a varga sign has no degree, so no moolatrikona)."""
    if planet not in EXALTATION:
        return "node"
    ex = EXALTATION[planet][0]
    if sign == ex:
        return "exalted"
    if sign == (ex + 6) % 12:
        return "debilitated"
    if SIGN_LORD[sign] == planet:
        return "own"
    return natural_relation(planet, SIGN_LORD[sign])


def _next(chart: Chart, kind: str, p: str) -> str:
    b = chart.bodies[p]
    if kind == "sign":
        return SIGN_LORD[b.sign]
    if kind == "nakshatra":
        return b.nak_lord
    return SIGN_LORD[chart.vargas["D9"][p]]


def _step(chart: Chart, kind: str, p: str) -> dict[str, Any]:
    b = chart.bodies[p]
    if kind == "navamsa":
        s = chart.vargas["D9"][p]
        return {"planet": p, "navamsa_sign": SIGNS[s], "house_from_d9_lagna": (s - chart.vargas["D9"]["Asc"]) % 12 + 1,
                "dignity": sign_dignity(p, s)}
    row = {"planet": p, "sign": b.sign_name, "house": b.house, "dignity": b.dignity or "node"}
    if kind == "nakshatra":
        row = {"planet": p, "nakshatra": b.nak_name, "nakshatra_lord": b.nak_lord, **{k: row[k] for k in ("sign", "house", "dignity")}}
    return row


def _canonical(loop: list[str]) -> list[str]:
    """A loop read from the planet that comes first in the graha order, so one loop has one name."""
    i = min(range(len(loop)), key=lambda k: GRAHAS.index(loop[k]))
    return loop[i:] + loop[:i]


def _path(chart: Chart, kind: str, start: str) -> tuple[list[str], list[str]]:
    """The chain from `start` and the loop it ends in (a self-disposited planet is a loop of one)."""
    path, cur = [start], start
    while True:
        nxt = _next(chart, kind, cur)
        if nxt in path:
            return path, _canonical(path[path.index(nxt):])
        path.append(nxt)
        cur = nxt


def _and(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def _loop_words(loop: list[str]) -> str:
    return f"{loop[0]}, self-disposited" if len(loop) == 1 else f"the {'–'.join(loop)} loop"


def chain(chart: Chart, kind: str, planet: str) -> dict[str, Any]:
    path, loop = _path(chart, kind, planet)
    return {"kind": kind, "steps": [_step(chart, kind, p) for p in path], "ends_in": loop,
            "in_loop": planet in loop and len(loop) > 1, "loop_with": [p for p in loop if p != planet] if planet in loop else []}


def exchanges(chart: Chart, planet: str) -> list[dict[str, Any]]:
    """Mutual exchanges the planet is part of: two planets each in the other's sign, nakshatra
    or navamsa sign (the sign one is Parivartana, with its class from the chart's features)."""
    out = []
    for kind in KINDS:
        other = _next(chart, kind, planet)
        if other != planet and _next(chart, kind, other) == planet:
            row = {"kind": kind, "planets": [planet, other]}
            if kind == "sign":
                loop = next((l for l in chart.features.dispositors.loops if sorted(l.planets) == sorted([planet, other])), None)
                if loop is not None and loop.houses:
                    row |= {"houses": loop.houses, "class_by_houses": loop.class_by_houses,
                            "class_by_lordship": loop.class_by_lordship}
            out.append(row)
    return out


def current_lords(chart: Chart, as_of: date) -> list[tuple[str, str]]:
    """(level, lord) of the Vimshottari mahadasha and antardasha running on `as_of`."""
    import swisseph as swe
    jd = swe.julday(as_of.year, as_of.month, as_of.day, 0.0)
    out = []
    for level, n in (("mahadasha", 1), ("antardasha", 2)):
        p = next((p for p in chart.dashas.get("vimshottari", []) if len(p.lords) == n and p.start_jd <= jd < p.end_jd), None)
        if p is not None:
            out.append((level, p.lords[-1]))
    return out


def activation(chart: Chart, planet: str, as_of: date) -> list[dict[str, Any]]:
    from .timing import activation_set
    out = []
    for level, lord in current_lords(chart, as_of):
        group = [lord] + activation_set(chart, lord)
        if planet in group:
            out.append({"level": level, "lord": lord, "activated": group,
                        "how": "the period's lord itself" if planet == lord else
                               f"in a nakshatra of {lord}" if chart.bodies[planet].nak_lord == lord else
                               f"lord of {lord}'s nakshatra"})
    return out


# --- facts in sentences (what the checker reads) ---------------------------------------------

def _step_words(kind: str, s: dict) -> str:
    if kind == "navamsa":
        return f"{s['planet']} in {s['navamsa_sign']} ({_ORD[s['house_from_d9_lagna']]} from the D9 lagna, {s['dignity']})"
    where = f"{s['sign']}, the {_ORD[s['house']]}, {s['dignity']}"
    return f"{s['planet']} in {s['nakshatra']} ({where})" if kind == "nakshatra" else f"{s['planet']} in {where}"


def chain_facts(c: dict) -> list[str]:
    kind, steps, loop = c["kind"], c["steps"], c["ends_in"]
    arrow = " → ".join(_step_words(kind, s) for s in steps)
    first = steps[0]["planet"]
    out = [f"{kind.capitalize()} chain of {first}: {arrow}; it ends in {_loop_words(loop)}"]
    if c["in_loop"]:
        out.append(f"{first} is in the {kind} loop, with {', '.join(c['loop_with'])}")
    elif loop == [first]:
        out.append(f"{first} is its own final {kind} dispositor")
    else:
        out.append(f"{first} is in no {kind} loop; its final {kind} dispositor"
                   f"{'s are' if len(loop) > 1 else ' is'} {_and(loop)}")
    return out


def _exchange_words(x: dict) -> str:
    a, b = x["planets"]
    what = {"sign": "sign", "nakshatra": "nakshatra", "navamsa": "navamsa sign"}[x["kind"]]
    extra = (f", the {_ORD[x['houses'][0]]} and {_ORD[x['houses'][1]]} houses exchanged ({x['class_by_houses']} "
             f"Parivartana by the houses, {x['class_by_lordship']} by every house the two rule)") if x.get("houses") else ""
    return f"{a} and {b} are in mutual {x['kind']} exchange: each is in the other's {what}{extra}"


def _activation_words(planet: str, x: dict) -> str:
    level = {"mahadasha": "major period (mahadasha)", "antardasha": "sub-period (antardasha)"}[x["level"]]
    return (f"{planet} is activated by the current {level} of {x['lord']} ({x['how']}); that period activates "
            f"{', '.join(x['activated'])}")


# --- the findings -----------------------------------------------------------------------------

def _stability(chart: Chart, chains: dict[str, dict]) -> float | None:
    """The smallest time-share among the placements the chains' steps state (see the module
    docstring); `chains` maps the kind to its chain, or to {"steps": [...]} over any planets."""
    u = chart.uncertainty
    if u is None:
        return None
    d1, d9, naks = u.placements.get("D1", {}), u.placements.get("D9", {}), u.nakshatras or {}
    vals: list[float] = []

    def add(block: dict, key: str) -> None:
        if key in block:
            vals.append(block[key].time)
    add(d1, "Asc")
    for kind, c in chains.items():
        for s in c["steps"]:
            add(d1, s["planet"])
            if kind == "navamsa":
                add(d9, s["planet"])
                add(d9, "Asc")
            if kind == "nakshatra":
                add(naks, s["planet"])
    return min(vals) if vals else None


def main_karaka(chart: Chart, spec: dict) -> str | None:
    k = spec["karakas"][0] if spec.get("karakas") else None
    if k is None:
        return None
    if k in GRAHAS:
        return k
    if k.startswith("L") and k[1:].isdigit():
        return SIGN_LORD[(chart.lagnas.asc_sign + int(k[1:]) - 1) % 12]
    return chart.features.jaimini.karakas.get(k)


def planet_finding(chart: Chart, area: str, role: str, planet: str, what: str, as_of: date | None) -> dict[str, Any]:
    chains = {k: chain(chart, k, planet) for k in KINDS}
    ex = exchanges(chart, planet)
    act = activation(chart, planet, as_of) if as_of is not None else None
    facts = [f"{planet} is {what}"] + [f for k in KINDS for f in chain_facts(chains[k])] + [_exchange_words(x) for x in ex]
    if act is not None:
        facts += [_activation_words(planet, x) for x in act] or [f"{planet} is in neither current period's activation set"]
    tag = f"chain:{area}.{role}"
    return {"finding_id": tag, "kind": "chain", "chain": role, "planet": planet, "planets": [planet], "role": what,
            "school": "parashari", "basis": "lagna",
            "derivation": {"sign": chains["sign"], "nakshatra": chains["nakshatra"], "navamsa": chains["navamsa"],
                           "exchanges": ex, **({"activation": act, "as_of": as_of.isoformat()} if act is not None else {})},
            "facts": facts, "allowed_tags": [tag], "stability": _stability(chart, chains), "confidence": None}


def chart_finding(chart: Chart) -> dict[str, Any]:
    """The final dispositors of the whole chart in each chain, and which bodies end in each."""
    d = chart.features.dispositors
    rows, facts, finals = {}, [], []
    asc_next = {"sign": SIGN_LORD[chart.lagnas.asc_sign], "nakshatra": chart.lagnas.asc_nak_lord,
                "navamsa": SIGN_LORD[chart.vargas["D9"]["Asc"]]}
    for kind in KINDS:
        ends: dict[tuple, list[str]] = {}
        for p in GRAHAS:
            _, loop = _path(chart, kind, p)
            ends.setdefault(tuple(loop), []).append(p)
        _, lagna_loop = _path(chart, kind, asc_next[kind])
        ends.setdefault(tuple(lagna_loop), []).insert(0, "Lagna")
        final = {"sign": d.final_sign, "nakshatra": d.final_nakshatra, "navamsa": d.final_navamsa}[kind]
        rows[kind] = {"final_dispositors": final,
                      "ends": [{"loop": list(loop), "bodies": bodies} for loop, bodies in
                               sorted(ends.items(), key=lambda kv: -len(kv[1]))]}
        finals += [p for p in final if p not in finals]
        parts = [f"{_and(e['bodies'])} end{'s' if len(e['bodies']) == 1 else ''} in {_loop_words(e['loop'])}"
                 for e in rows[kind]["ends"]]
        facts.append(f"Final {kind} dispositors of the chart: {_and(final)}; " + "; ".join(parts))
        others = [b for e in rows[kind]["ends"][1:] for b in e["bodies"]]
        big = rows[kind]["ends"][0]
        if len(big["loop"]) > 1:
            facts.append(f"Every body but {_and(others)} ends in the {'–'.join(big['loop'])} {kind} loop"
                         if others else f"Every body ends in the {'–'.join(big['loop'])} {kind} loop")
    for kind in KINDS:
        for p in GRAHAS:
            for x in exchanges(chart, p):
                if x["kind"] == kind and x["planets"][0] == p and p < x["planets"][1]:
                    facts.append(_exchange_words(x))
    rows["exchanges"] = [x for p in GRAHAS for x in exchanges(chart, p) if x["planets"][0] < x["planets"][1]]
    tag = "chain:personality.chart"
    # Every body's chain of every kind, and the lagna's nakshatra, which starts its nakshatra chain.
    everything = {kind: {"steps": [{"planet": p} for p in GRAHAS] + ([{"planet": "Asc"}] if kind == "nakshatra" else [])}
                  for kind in KINDS}
    return {"finding_id": tag, "kind": "chain", "chain": "chart", "planet": None, "planets": finals,
            "role": "the final dispositors of the whole chart", "school": "parashari", "basis": "lagna",
            "derivation": rows, "facts": facts, "allowed_tags": [tag],
            "stability": _stability(chart, everything), "confidence": None}


def area_chain_findings(chart: Chart, area: str, as_of: date | None = None) -> list[dict[str, Any]]:
    from .scoring import AREAS
    spec = AREAS.get(area)
    if spec is None or not spec.get("houses"):
        return []
    first = spec["houses"][0]
    lord = SIGN_LORD[(chart.lagnas.asc_sign + first - 1) % 12]
    out = [planet_finding(chart, area, "lord", lord, f"the lord of the {_ORD[first]}, the area's first house", as_of)]
    k = main_karaka(chart, spec)
    if k is not None and k != lord:
        out.append(planet_finding(chart, area, "karaka", k, f"the area's main significator (karaka), {spec['karakas'][0]}"
                                  if spec["karakas"][0] != k else "the area's main significator (karaka)", as_of))
    if area == "personality":
        out.append(chart_finding(chart))
    return out
