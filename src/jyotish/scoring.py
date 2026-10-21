"""Layer 5: life-area scores, confluence confidence, tiers, polarity and the driver planet
(SPEC Layer 5). Classical weight set "classical-1.0".

S_area = sum_h w_h B_h + sum_{p in L u K} w_p D_p (beta_p / beta_req_p)
         + sum_r c_r b_r theta_r + lambda V + nu sum T_p + kappa sum_{p in L} Delta_p + pi P

Where SPEC leaves a quantity open, the simplest reading is taken and named here (and in
READINGS, which the scored block carries so a reading can always say what it assumed):

  weights      w_lord 3, w_occupant (house term) 2, w_karaka 2 (SPEC's 3:2:2); c 1;
               lambda 1; nu = kappa = pi = 0.5 ("small": a quarter of the karaka weight).
  bases        every house and lord term is computed from the lagna, the Moon and the Sun
               and combined 3:2:1; karakas, varga, Navatara, dispositor and panchanga terms
               do not depend on the basis.
  B_h          Bhava Bala (whole sign) as a z-score among the chart's twelve houses,
               clipped to +-2 and halved, so -1..+1. From the Moon or the Sun, house h is
               the lagna-house holding that sign.
  Bhavat       each area also reads the Bhavat Bhavam of its first house (the house as
  Bhavam       far from it as it is from the lagna) as one more house.
  D_p          D1 dignity: exalted +2, moolatrikona +1, own +1, friend +0.5, neutral 0,
               enemy -0.5, debilitated -2; nodes 0. Multiplied by the Shadbala ratio.
  theta_r      a fire's scaled themes that map to the area (THEME_AREAS), times the basis
               weight 1, 2/3, 1/3. Experimental fires are left out.
  V            for each lord and karaka (not nodes) and each of the area's vargas: +1 when
               the D1 and varga dignities have the same sign, -1 when opposite, 0 if either
               is 0; +1 more for a vargottama planet when the varga is D9. Averaged.
  T_p          Navatara: Vipat, Pratyak, Vadha -1; Janma 0; the rest +1; halved in the
               2nd and 3rd cycles.
  Delta_p      D of the lord's final sign dispositor (mean over a loop).
  P            panchanga lords (tithi, vara, nakshatra, nitya-yoga; the karana lord is not
               computed) that are the area's lords or karakas: sum of (Shadbala ratio - 1).

Confluence. Each signal family votes +1 / 0 / -1 on the area (or is not applicable):
D1 house (house term), D1 lord (lord and dispositor terms), karaka, varga, Jaimini arudha
(natural benefics minus malefics in the area's padas), KP sub-lord (+1 if the cusp's
sub-lord occupies or owns an area house, -1 if instead a 6/8/12 house the area does not
include), panchanga. Dasha and transit activation are timing families and are not
applicable to the static score. Each family's vote is weighted 1 - rho, rho its mean
correlation with the other families over 10,000 random charts (data/family_rho.json,
made by scripts/family_rho.py). Direction = sign of S. Confidence = (weight agreeing -
weight opposing) / weight applicable, floored at 0: opposing votes are the "penalty for
strong contradiction". Tier: > 0.7 strong, 0.4-0.7 moderate, else weak / mixed.
Areas whose S x confidence is below the chart's median are "not emphasised": reported as
such, not as a low score.

Polarity (simplest named reading of SPEC's "signed contributions"): a malefic occupying
or aspecting (whole-sign drishti) the area's first house from the lagna flags it: Saturn
"delay", Mars "intensity", Rahu "volatility", Ketu "detachment".

Driver: Shadbala ratio x Vimsopaka (Shodasavarga) x (non-experimental rules fired on the
planet / rules that could fire on it). Dasha proximity is dropped (SPEC). Final sign
dispositors are candidates regardless and are shown as alternates; the current
Vimshottari lords are reported separately with their as-of date.

Stability never enters S. uncertainty.assess fills each area's three stability numbers
(the share of samples with the same tier) and `narrate` is false below 0.5 on time."""

from __future__ import annotations

import json
import statistics
from functools import lru_cache
from pathlib import Path

from .constants import EXALTATION, GRAHAS, SEVEN, SIGN_LORD
from .dignity import aspected_houses, house_of, natural_relation
from .models import AreaScore, Chart, Driver, Scored
from .shadbala import natural_benefics
from .vargas import VARGAS

WEIGHTS = {"lord": 3.0, "occupant": 2.0, "karaka": 2.0, "rule": 1.0, "varga": 1.0,
           "navatara": 0.5, "dispositor": 0.5, "panchanga": 0.5}
BASIS_WEIGHT = {"lagna": 3.0, "moon": 2.0, "sun": 1.0}
FIRE_BASIS = {"lagna": 1.0, "moon": 2.0 / 3.0, "sun": 1.0 / 3.0}
DIGNITY_SCORE = {"exalted": 2.0, "moolatrikona": 1.0, "own": 1.0, "friend": 0.5,
                 "neutral": 0.0, "enemy": -0.5, "debilitated": -2.0, "node": 0.0}
TARA_ADVERSE = {"Vipat", "Pratyak", "Vadha"}
FAMILIES = ["house", "lord", "karaka", "varga", "arudha", "kp", "panchanga"]
POLARITY = {"Saturn": "delay", "Mars": "intensity", "Rahu": "volatility", "Ketu": "detachment"}
RHO_FILE = Path(__file__).with_name("data") / "family_rho.json"

READINGS = [
    "weights lord 3, occupant 2, karaka 2, rule 1, varga 1, navatara/dispositor/panchanga 0.5",
    "houses and lords combined from lagna, Moon, Sun 3:2:1",
    "B_h: Bhava Bala z-score among the chart's 12 houses, clipped +-2, halved",
    "Bhavat Bhavam of each area's first house added as a house",
    "D_p: exalted +2, MT/own +1, friend +0.5, neutral 0, enemy -0.5, debilitated -2",
    "V: D1 vs varga dignity sign agreement, +1 vargottama in D9",
    "T_p: adverse tara -1, Janma 0, others +1, halved in cycles 2-3",
    "confidence: (agree - oppose) / applicable, 1 - rho weights; not emphasised below median S x confidence",
    "polarity: Saturn/Mars/Rahu/Ketu on the first house from the lagna",
    "driver: Shadbala ratio x Shodasavarga Vimsopaka x fired/applicable rules",
]

# The SPEC Layer 5 table, rows 1-18 (19, synastry, needs two charts). Houses from the
# lagna; "karakas" may name planets, chara karakas (AK ... DK) or house lords ("L6").
# "extra_signs" are signs counted from a planet ("Saturn:3" = 3rd from Saturn). Varga
# entries are varga names (SPEC's qualifiers such as "(9th)" are read as the plain
# varga). "arudha" names padas; "UL2" is the 2nd from the Upapada, "AL10" the 10th from
# the AL; "karakamsa" and "chandra" are the Karakamsa and the Moon's sign. "kp" names cusps.
# Not computed yet and so not applicable: Indu lagna (2), Roga Saham (7).
AREAS = {
    "personality": dict(houses=[1], karakas=["Sun", "L1", "AK"], vargas=["D1", "D9"],
                        arudha=["AL"], kp=[1]),
    "wealth": dict(houses=[2, 11, 5, 9], karakas=["Jupiter", "Venus"], vargas=["D2", "D16"],
                   arudha=["A2", "A11"]),
    "siblings": dict(houses=[3, 11], karakas=["Mars", "Mercury", "BK"], vargas=["D3"], arudha=["A3"]),
    "mother_home": dict(houses=[4, 11, 12], karakas=["Moon", "Mars", "Venus", "MK"],
                        vargas=["D4", "D12"], arudha=["A4"]),
    "children": dict(houses=[5, 9, 11], karakas=["Jupiter", "PK"], vargas=["D7"], arudha=["A5"], kp=[5]),
    "intellect": dict(houses=[4, 5, 2, 9], karakas=["Mercury", "Jupiter"], vargas=["D24"],
                      arudha=["A4", "A5"]),
    "health": dict(houses=[1, 6, 8, 12], extra_signs=["Saturn:3", "Saturn:8"],
                   karakas=["Sun", "Saturn", "Mars", "L6"], vargas=["D30", "D3"], kp=[6]),
    "debts_enemies": dict(houses=[6, 8, 12], karakas=["Mars", "Saturn", "Rahu"], vargas=["D30"],
                          arudha=["A6"]),
    "marriage": dict(houses=[7, 2, 11, 8], karakas=["Venus", "Jupiter", "DK"], vargas=["D9"],
                     arudha=["UL", "UL2", "A7"], kp=[7]),
    "longevity": dict(houses=[1, 8, 3], karakas=["Saturn", "L8", "L1"], vargas=["D30", "D9"],
                      mks=True),
    "father": dict(houses=[9, 10], karakas=["Sun", "PiK"], vargas=["D12"], arudha=["A9"]),
    "fortune": dict(houses=[9, 5, 12], karakas=["Jupiter", "PiK"], vargas=["D20", "D9"], arudha=["A9"]),
    "career": dict(houses=[10, 6, 2, 11], karakas=["Sun", "Saturn", "Mercury", "AmK"],
                   vargas=["D10"], arudha=["A10"], kp=[10]),
    "gains": dict(houses=[11, 2, 5], karakas=["Jupiter"], vargas=["D11"], arudha=["A11"]),
    "foreign": dict(houses=[9, 12, 3, 7], karakas=["Rahu", "Moon", "L12"], vargas=["D4", "D9"],
                    arudha=["A9", "A12"]),
    "spirituality": dict(houses=[12, 9, 5, 8], karakas=["Ketu", "Jupiter", "Saturn"], vargas=["D20"],
                         arudha=["karakamsa", "A12"]),
    "mind": dict(houses=[1, 4, 5], karakas=["Moon", "Mercury"], vargas=["D1", "D24"],
                 arudha=["chandra"], kp=[4]),
    "reputation": dict(houses=[10, 1, 4], karakas=["Sun", "Jupiter"], vargas=["D10"],
                       arudha=["AL", "AL10"]),
}
# Which life areas a rule theme speaks to (a mapping, not a weight).
THEME_AREAS = {
    "courage": ["siblings", "personality"], "leadership": ["career", "reputation"],
    "physical_vigour": ["personality", "health"], "conflict": ["debts_enemies"],
    "intellect": ["intellect"], "communication": ["siblings", "intellect"], "commerce": ["wealth", "career"],
    "wisdom": ["intellect", "fortune"], "dharma": ["fortune"], "reputation": ["reputation", "career"],
    "comforts": ["mother_home"], "relationships": ["marriage"], "arts": ["intellect"],
    "authority": ["career", "reputation"], "discipline": ["career"], "endurance": ["longevity"],
    "wealth": ["wealth", "gains"], "rise_after_struggle": ["career"], "career": ["career"],
    "fortune": ["fortune", "wealth"], "house_linkage": [],
}


@lru_cache(maxsize=1)
def family_rho() -> dict[str, float]:
    """Mean correlation of each family with the others (data/family_rho.json); zeros if
    the table has not been made."""
    if RHO_FILE.exists():
        return json.loads(RHO_FILE.read_text())["rho"]
    return {f: 0.0 for f in FAMILIES}


def _sgn(x: float, eps: float = 1e-9) -> int:
    return 1 if x > eps else -1 if x < -eps else 0


class _View:
    """What scoring reads from one chart."""

    def __init__(self, chart: Chart):
        self.c = chart
        self.f = chart.features
        self.lagna = chart.lagnas.asc_sign
        self.sign = {p: b.sign for p, b in chart.bodies.items()}
        self.lon = {p: b.lon for p, b in chart.bodies.items()}
        self.base = {"lagna": self.lagna, "moon": self.sign["Moon"], "sun": self.sign["Sun"]}
        bb = self.f.bhava_bala.whole_sign
        vals = [bb[h].total for h in range(1, 13)]
        mu, sd = statistics.mean(vals), statistics.pstdev(vals) or 1.0
        self.B = {h: max(-2.0, min(2.0, (bb[h].total - mu) / sd)) / 2.0 for h in range(1, 13)}
        self.ratio = {p: x.ratio for p, x in self.f.shadbala.planets.items()}
        self.D = {p: DIGNITY_SCORE[chart.bodies[p].dignity or "node"] for p in GRAHAS}
        self.benefics = natural_benefics(self.lon, chart.meta.mercury_nature)

    def lagna_house(self, sign: int) -> int:
        return house_of(sign, self.lagna)

    def sign_of_house(self, h: int, basis: str) -> int:
        return (self.base[basis] + h - 1) % 12

    def lord_of(self, h: int, basis: str) -> str:
        return SIGN_LORD[self.sign_of_house(h, basis)]

    def strength(self, p: str) -> float:
        return self.D[p] * self.ratio.get(p, 0.0)

    def tara(self, p: str) -> float:
        t = self.c.bodies[p].tara
        v = -1.0 if t.name in TARA_ADVERSE else 0.0 if t.name == "Janma" else 1.0
        return v if t.cycle == 1 else v / 2.0

    def final_dispositor(self, p: str) -> float:
        chain = self.f.dispositors.sign[p]
        loop = next((l.planets for l in self.f.dispositors.loops if chain[-1] in l.planets), [chain[-1]])
        return statistics.mean(self.D[q] for q in loop)

    def varga_dignity(self, p: str, varga: str) -> float:
        """Dignity of a planet's varga sign. A varga has no degree, so moolatrikona is not
        read: exalted, debilitated, own, or the natural relation with the sign's lord."""
        s = VARGAS[varga](self.lon[p])
        if s == EXALTATION[p][0]:
            return 2.0
        if s == (EXALTATION[p][0] + 6) % 12:
            return -2.0
        if SIGN_LORD[s] == p:
            return 1.0
        return DIGNITY_SCORE[natural_relation(p, SIGN_LORD[s])]


def _karakas(v: _View, names: list[str]) -> list[str]:
    out = []
    for k in names:
        if k in GRAHAS:
            out.append(k)
        elif k.startswith("L") and k[1:].isdigit():
            out.append(v.lord_of(int(k[1:]), "lagna"))
        else:
            out.append(v.f.jaimini.karakas[k])
    return list(dict.fromkeys(out))


def _houses(spec: dict) -> list[int]:
    hs = list(spec["houses"])
    first = hs[0]
    derived = (2 * first - 2) % 12 + 1          # the first house's Bhavat Bhavam
    if derived not in hs:
        hs.append(derived)
    return hs


def _arudha_signs(v: _View, names: list[str]) -> list[int]:
    a = v.f.jaimini.arudhas
    out = []
    for n in names:
        if n == "UL2":
            out.append((a["UL"] + 1) % 12)
        elif n == "AL10":
            out.append((a["AL"] + 9) % 12)
        elif n == "karakamsa":
            out.append(v.f.jaimini.karakamsa)
        elif n == "chandra":
            out.append(v.sign["Moon"])
        else:
            out.append(a[n])
    return out


def _kp_vote(v: _View, cusp: int, area_houses: list[int]) -> int | None:
    lords = v.c.lagnas.cusp_lords_kp.get(cusp)
    if not lords:
        return None
    sub = lords["sub"]
    signified = {v.c.bodies[sub].house} | set(v.f.lordship.get(sub, []))
    if signified & set(area_houses):
        return 1
    if signified & ({6, 8, 12} - set(area_houses)):
        return -1
    return 0


def score_area(v: _View, name: str, spec: dict) -> dict:
    houses = _houses(spec)
    karakas = _karakas(v, spec["karakas"])
    house_term = lord_term = disp_term = 0.0
    lords_all: set[str] = set()
    for basis, bw in BASIS_WEIGHT.items():
        ht = sum(WEIGHTS["occupant"] * v.B[v.lagna_house(v.sign_of_house(h, basis))] for h in houses)
        if basis == "lagna":
            for ref in spec.get("extra_signs", []):
                planet, k = ref.split(":")
                ht += WEIGHTS["occupant"] * v.B[v.lagna_house((v.sign[planet] + int(k) - 1) % 12)]
        lords = [v.lord_of(h, basis) for h in houses]
        lords_all.update(lords)
        lt = sum(WEIGHTS["lord"] * v.strength(p) for p in lords)
        dt = sum(WEIGHTS["dispositor"] * v.final_dispositor(p) for p in lords)
        house_term += bw * ht / 6.0
        lord_term += bw * lt / 6.0
        disp_term += bw * dt / 6.0
    karaka_term = sum(WEIGHTS["karaka"] * v.strength(p) for p in karakas)

    rule_term = 0.0
    for f in v.c.fired_rules:
        if f.status == "experimental":
            continue
        theta = sum(val for th, val in f.themes.items() if name in THEME_AREAS.get(th, []))
        rule_term += WEIGHTS["rule"] * FIRE_BASIS[f.basis] * theta

    vparts = []
    for p in [q for q in dict.fromkeys(list(lords_all) + karakas) if q in SEVEN]:
        for varga in spec["vargas"]:
            d1, dv = _sgn(v.D[p]), _sgn(v.varga_dignity(p, varga))
            x = 0 if d1 == 0 or dv == 0 else (1 if d1 == dv else -1)
            if varga == "D9" and v.c.bodies[p].vargottama:
                x += 1
            vparts.append(x)
    V = statistics.mean(vparts) if vparts else 0.0
    nav = sum(v.tara(p) for p in dict.fromkeys(list(lords_all) + karakas))
    pl = v.c.panchanga
    touching = []
    if pl is not None:
        touching = [p for p in dict.fromkeys([pl.tithi_lord, pl.vara_lord, pl.nakshatra_lord, pl.yoga_lord])
                    if p in SEVEN and (p in lords_all or p in karakas)]
    P = sum(v.ratio[p] - 1.0 for p in touching)

    S = (house_term + lord_term + karaka_term + rule_term + WEIGHTS["varga"] * V
         + WEIGHTS["navatara"] * nav + disp_term + WEIGHTS["panchanga"] * P)

    arudha_signs = _arudha_signs(v, spec.get("arudha", []))
    occ = [p for s in arudha_signs for p in GRAHAS if v.sign[p] == s]
    arudha_vote = (_sgn(sum(1 if p in v.benefics else -1 for p in occ)) if arudha_signs else None)
    if spec.get("mks"):
        mks = sum(1 for b in v.c.bodies.values() if b.marana_karaka_sthana)
        arudha_vote = -1 if mks else 0
    kp_votes = [x for x in (_kp_vote(v, c, spec["houses"]) for c in spec.get("kp", [])) if x is not None]
    votes = {
        "house": _sgn(house_term), "lord": _sgn(lord_term + disp_term), "karaka": _sgn(karaka_term),
        "varga": _sgn(V), "arudha": arudha_vote,
        "kp": _sgn(sum(kp_votes)) if kp_votes else None,
        "panchanga": _sgn(P) if touching else None,
    }

    polarity = []
    first = spec["houses"][0]
    for planet, flag in POLARITY.items():
        h = v.c.bodies[planet].house
        on = h == first or (planet in SEVEN and first in aspected_houses(planet, h))
        if on:
            polarity.append(flag)
    terms = {"house": house_term, "lord": lord_term, "karaka": karaka_term, "rules": rule_term,
             "varga": WEIGHTS["varga"] * V, "navatara": WEIGHTS["navatara"] * nav,
             "dispositor": disp_term, "panchanga": WEIGHTS["panchanga"] * P}
    return {"S": S, "votes": votes, "polarity": polarity, "terms": terms,
            "lords": sorted(lords_all), "karakas": karakas}


def confidence(S: float, votes: dict[str, int | None], rho: dict[str, float]) -> tuple[float, float, float]:
    direction = _sgn(S)
    applicable = {f: x for f, x in votes.items() if x is not None}
    w = {f: 1.0 - rho.get(f, 0.0) for f in applicable}
    total = sum(w.values())
    agree = sum(w[f] for f, x in applicable.items() if direction and x == direction)
    oppose = sum(w[f] for f, x in applicable.items() if direction and x == -direction)
    conf = max(0.0, (agree - oppose) / total) if total else 0.0
    return conf, agree, total


def tier(conf: float) -> str:
    return "strong" if conf > 0.7 else "moderate" if conf >= 0.4 else "weak / mixed"


def _driver(v: _View, rules) -> Driver:
    fired: dict[str, set[str]] = {p: set() for p in SEVEN}
    for f in v.c.fired_rules:
        if f.status == "experimental":
            continue
        for n in f.nodes:
            if n in fired:
                fired[n].add(f.id)
    applicable = {p: 0 for p in SEVEN}
    for r in rules:
        if r.data["status"] == "experimental":
            continue
        w = r.data["when"]
        sides = [w["pair"]["a"], w["pair"]["b"]] if "pair" in w else [w]
        cand = set()
        for side in sides:
            cand |= {side["planet"]} if "planet" in side else set(side.get("planet_in", SEVEN))
        for p in cand & set(SEVEN):
            applicable[p] += 1
    comp = {}
    for p in SEVEN:
        rules_share = len(fired[p]) / applicable[p] if applicable[p] else 0.0
        comp[p] = v.ratio[p] * v.f.vimsopaka[p]["shodasavarga"] * rules_share
    ranking = sorted(SEVEN, key=lambda p: -comp[p])
    finals = [p for p in v.f.dispositors.final_sign if p in SEVEN]
    current = {}
    if v.c.meta.jd is not None and v.c.dashas.get("vimshottari"):
        current = {"system": "vimshottari", "as_of_jd": v.c.meta.jd}
    return Driver(driver=ranking[0], ranking=[{"planet": p, "score": comp[p],
                                               "rules_fired": len(fired[p]), "rules_applicable": applicable[p]}
                                              for p in ranking],
                  dispositor_candidates=finals,
                  alternates=[p for p in finals if p != ranking[0]], current_period=current)


def current_period(chart: Chart, as_of_jd: float) -> dict:
    out = {"as_of_jd": as_of_jd}
    for p in chart.dashas.get("vimshottari", []):
        if p.start_jd <= as_of_jd < p.end_jd:
            out["maha" if len(p.lords) == 1 else "antar"] = p.lords[-1]
    return out


def score(chart: Chart, rules=None) -> Scored | None:
    """The scored block, or None when Shadbala or Bhava Bala is missing."""
    if chart.features.shadbala is None or chart.features.bhava_bala is None:
        return None
    from .rules import default_rules
    rules = default_rules() if rules is None else rules
    v = _View(chart)
    rho = family_rho()
    raw = {name: score_area(v, name, spec) for name, spec in AREAS.items()}
    rows = {}
    for name, r in raw.items():
        conf, agree, total = confidence(r["S"], r["votes"], rho)
        rows[name] = (r, conf, agree, total)
    emphasis = {n: x[0]["S"] * x[1] for n, x in rows.items()}
    cut = statistics.median(emphasis.values())
    areas = {}
    for name, (r, conf, agree, total) in rows.items():
        emphasised = emphasis[name] >= cut and emphasis[name] > 0
        areas[name] = AreaScore(
            score_classical=r["S"], score_learned=None,
            tier=tier(conf) if emphasised else "not emphasised", confidence=conf,
            direction={1: "supportive", -1: "adverse", 0: "neutral"}[_sgn(r["S"])],
            emphasised=emphasised, families_agree_w=agree, families_total_w=total,
            votes=r["votes"], polarity=r["polarity"], terms=r["terms"],
            lords=r["lords"], karakas=r["karakas"])
    areas["synastry"] = AreaScore(score_classical=None, score_learned=None, tier="needs two charts",
                                  confidence=None, direction="neutral", emphasised=False,
                                  families_agree_w=0.0, families_total_w=0.0, votes={}, polarity=[],
                                  terms={}, lords=[], karakas=[])
    ranked = sorted((n for n in areas if areas[n].emphasised), key=lambda n: -emphasis[n])
    return Scored(weights="classical-1.0", readings=READINGS, areas=areas, top=ranked[:3],
                  driver=_driver(v, rules))
