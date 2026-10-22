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
  V            (Meta.varga_term) v2, the default (SPEC revision 2026-10-21): the varga's
               own verdict, the mean over the area's lords and karakas (not nodes) and its
               vargas of the signed varga dignity (-2..+2 halved to -1..+1), +1 for a
               vargottama planet when the varga is D9. The share of (planet, varga) pairs
               whose D1 and varga dignities have the same sign (both zero counts as the
               same) is the area's varga_consistency, and scales the varga family's weight
               in the confluence by 0.5 + 0.5 x share. v1, kept for comparison: +1 when the
               D1 and varga dignities have the same sign, -1 when opposite, 0 if either is 0
               (two negatives agreeing counted for the area), +1 vargottama in D9.
  T_p          Navatara: Vipat, Pratyak, Vadha -1; Janma 0; the rest +1; halved in the
               2nd and 3rd cycles.
  Delta_p      D of the lord's final sign dispositor (mean over a loop).
  P            panchanga lords (tithi, vara, nakshatra, nitya-yoga; the karana lord is not
               computed) that are the area's lords or karakas: sum of (Shadbala ratio - 1).

Confluence. Each signal family votes +1 / 0 / -1 on the area (or is not applicable):
D1 house (house term), D1 lord (lord and dispositor terms), karaka, varga, Jaimini arudha
(natural benefics minus malefics in the area's padas), KP sub-lord (Meta.kp_vote, below),
panchanga. Dasha and transit activation are timing families and are not
applicable to the static score. Each family's vote is weighted 1 - rho, rho its mean
correlation with the other families over 10,000 random charts (data/family_rho.json,
made by scripts/family_rho.py). Direction = sign of S. Confidence = (weight agreeing -
weight opposing) / weight applicable, floored at 0: opposing votes are the "penalty for
strong contradiction". Tier: > 0.7 strong, 0.4-0.7 moderate, else weak / mixed.
An area is "not emphasised" when its S is below the 40th percentile of that area's S over
the 10,000-chart population run (data/area_percentiles.json, made by scripts/family_rho.py
with the rho table), never below the chart's own median (SPEC Layer 5 revision). It is
reported as such, not as a low score. Emphasised areas are ranked by S x confidence.

Polarity: Saturn "delay" and Mars "intensity" need at least two touches (occupy, conjoin
or aspect, whole-sign) among the area's first house, that house's lord and the area's
main karaka (its first listed); a planet does not touch itself, and a lord that is also
the main karaka is one object, one touch. A malefic that is itself the lord of the primary
house does not flag the area (v3: Mars in its own 7th is not an affliction of the 7th).
Rahu "volatility" and Ketu "detachment" need one touch of the first house. Each flag
records the touches that raised it.

Driver (Meta.driver_formula). "v2", the default (SPEC hypothesis v2): the sum, equal
weights, of five terms each scaled 0-1 across the chart's seven planets (min-max): Shadbala
ratio, Shodasavarga Vimsopaka, rules fired / rules applicable, Sodhya Pinda rank, and a
lordship-role term (the share held of yogakaraka, lagna lord, final sign dispositor; 0-1 by
construction). "v1", kept for comparison: Shadbala ratio x Vimsopaka x rules share, which
gives 0 to any planet with no rule fired. Dasha proximity is dropped (SPEC). Final sign
dispositors are shown as alternates; the current Vimshottari lords are reported apart.

KP (Meta.kp_vote). v2, the default (SPEC revision 2026-10-21): the areas in
constants.KP_MATTER have a cusp, matter houses M and denial houses N. The cusp's sub-lord
signifies, in the KP four-fold order, the house its star lord occupies, the houses its star
lord owns, the house it occupies, the houses it owns (occupation in the KP houses, the
Placidus cusps of Meta.kp_house_system; ownership by sign from the lagna, as before); a
node adds the occupation and ownership of the planets conjoined with it (and, with
Meta.node_aspects, of the planets aspecting its sign), then of its sign lord. Decided at the
star-lord level first: +1 when its significations meet M and not N, -1 when N and not M;
if both or neither, the same test at the sub-lord's own level; else 0 (an abstention). v1,
kept for comparison: +1 if the sub-lord occupies or owns an area house, -1 if instead a
6/8/12 house the area does not include (whole-sign occupation); cusps from the area table.

The rho and percentile tables are measured per (varga_term, kp_vote): the v1 pair keeps
family_rho.json / area_percentiles.json, other pairs add ".varga-<v>.kp-<v>" to the name.

Stability never enters S. uncertainty.assess fills each area's three stability numbers
(the share of samples with the same tier) and `narrate` is false below 0.5 on time."""

from __future__ import annotations

import json
import statistics
from functools import lru_cache
from pathlib import Path

from .constants import EXALTATION, GRAHAS, KP_MATTER, SEVEN, SIGN_LORD, SIGNS
from .dignity import aspected_houses, house_of, natural_relation
from .models import AreaScore, Chart, Driver, Scored
from .shadbala import natural_benefics
from .rules import OUT_OF_DEFAULT
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
PCT_FILE = Path(__file__).with_name("data") / "area_percentiles.json"
EMPHASIS_PERCENTILE = "p40"

READINGS_VARGA = {
    "v1": "V v1: D1 vs varga dignity sign agreement, +1 vargottama in D9",
    "v2": "V v2: mean signed varga dignity halved, +1 vargottama in D9; consistency share scales the varga weight 0.5 + 0.5 x share",
}
READINGS_KP = {
    "v1": "KP v1: sub-lord occupies/owns an area house +1, else a 6/8/12 outside them -1",
    "v2": "KP v2: KP matter/denial houses, four-fold significations, star-lord level then own level, else abstain; "
          "occupation in the Placidus KP houses, ownership by sign",
}
READINGS = [
    "weights lord 3, occupant 2, karaka 2, rule 1, varga 1, navatara/dispositor/panchanga 0.5",
    "houses and lords combined from lagna, Moon, Sun 3:2:1",
    "B_h: Bhava Bala z-score among the chart's 12 houses, clipped +-2, halved",
    "Bhavat Bhavam of each area's first house added as a house",
    "D_p: exalted +2, MT/own +1, friend +0.5, neutral 0, enemy -0.5, debilitated -2",
    "T_p: adverse tara -1, Janma 0, others +1, halved in cycles 2-3",
    "confidence: (agree - oppose) / applicable, 1 - rho weights; not emphasised: S below the area's population p40",
    "polarity v3: Saturn/Mars need 2 of first house, its lord, main karaka, and are not its lord; Rahu/Ketu 1",
    "driver v2: sum of min-max scaled Shadbala ratio, Vimsopaka, rules share, Sodhya Pinda rank, role share",
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


def table_path(base: Path, varga_term: str = "v2", kp_vote: str = "v2") -> Path:
    """The population table for a (varga_term, kp_vote) pair: the v1 pair keeps the
    original file name; any other pair adds ".varga-<v>.kp-<v>"."""
    if (varga_term, kp_vote) == ("v1", "v1"):
        return base
    return base.with_name(f"{base.stem}.varga-{varga_term}.kp-{kp_vote}{base.suffix}")


# Set by scripts/family_rho.py only: the population run records votes and S, which do not
# depend on these tables, so a table not yet made reads as rho 0 and no emphasis cut there.
POPULATION_RUN = False


def _table(base: Path, varga_term: str, kp_vote: str) -> dict:
    path = table_path(base, varga_term, kp_vote)
    if not path.exists() and POPULATION_RUN:
        if base == RHO_FILE:
            return {"rho": {f: 0.0 for f in FAMILIES}}
        return {"percentiles": {a: {EMPHASIS_PERCENTILE: float("-inf")} for a in AREAS}}
    if not path.exists():
        raise FileNotFoundError(f"{path.name} has not been made for varga_term={varga_term}, kp_vote={kp_vote}: "
                                "run scripts/family_rho.py with those settings")
    return json.loads(path.read_text())


@lru_cache(maxsize=None)
def family_rho(varga_term: str = "v2", kp_vote: str = "v2") -> dict[str, float]:
    """Mean correlation of each family with the others, measured with these vote versions."""
    return _table(RHO_FILE, varga_term, kp_vote)["rho"]


@lru_cache(maxsize=None)
def area_thresholds(varga_term: str = "v2", kp_vote: str = "v2") -> dict[str, float]:
    """Each area's 40th-percentile S over the population run, with these vote versions."""
    data = _table(PCT_FILE, varga_term, kp_vote)["percentiles"]
    return {a: v[EMPHASIS_PERCENTILE] for a, v in data.items()}


def family_weights(area, rho: dict[str, float]) -> dict[str, float]:
    """Each family's confluence weight on an area: 1 - rho, and for the varga family under
    v2 times 0.5 + 0.5 x the area's varga_consistency."""
    w = {f: 1.0 - rho.get(f, 0.0) for f in FAMILIES}
    share = area.get("varga_consistency") if isinstance(area, dict) else getattr(area, "varga_consistency", None)
    if share is not None:
        w["varga"] *= 0.5 + 0.5 * share
    return w


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

    def kp_house(self, p: str) -> int:
        """The KP house a planet occupies: the cusp interval (Meta.kp_house_system) holding
        its sidereal longitude, cusp n up to cusp n+1."""
        if self.c.meta.kp_house_system != "placidus":
            raise ValueError(f"kp_house_system must be placidus, not {self.c.meta.kp_house_system!r}")
        cusps = self.c.lagnas.cusps_placidus
        lon = self.lon[p]
        for n in range(1, 13):
            start, end = cusps[n], cusps[n % 12 + 1]
            if (lon - start) % 360.0 < (end - start) % 360.0:
                return n
        raise ValueError(f"{p} at {lon} is in no KP house")

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


def _significations(v: _View, p: str) -> tuple[set[int], dict, list[dict]]:
    """A planet's own occupation (its KP house, Placidus) and ownership (by sign from the
    lagna); for a node, plus those of the planets conjoined with it (same sign; and aspecting
    its sign, with Meta.node_aspects) and then of its sign lord. Returns (houses, own, via)."""
    def own(q):
        return {"planet": q, "occupies": v.kp_house(q), "occupies_by_sign": v.c.bodies[q].house,
                "owns": list(v.f.lordship.get(q, []))}
    me = own(p)
    houses = {me["occupies"], *me["owns"]}
    via = []
    if p in ("Rahu", "Ketu"):
        conj = [q for q in SEVEN if v.sign[q] == v.sign[p]]
        asp = ([q for q in SEVEN if q not in conj
                and v.lagna_house(v.sign[p]) in aspected_houses(q, v.c.bodies[q].house)]
               if v.c.meta.node_aspects else [])
        for q, how in [(q, "conjoined") for q in conj] + [(q, "aspecting") for q in asp] + \
                [(SIGN_LORD[v.sign[p]], "sign lord")]:
            row = dict(own(q), **{"as": how})
            via.append(row)
            houses |= {row["occupies"], *row["owns"]}
    return houses, me, via


def _kp_level(v: _View, level: str, p: str, M: set[int], N: set[int]) -> dict:
    sig, me, via = _significations(v, p)
    m, n = sig & M, sig & N
    vote = 1 if m and not n else -1 if n and not m else 0
    return {"level": level, "planet": p, "occupies": me["occupies"], "occupies_by_sign": me["occupies_by_sign"],
            "owns": me["owns"], "via": via,
            "significations": sorted(sig), "meets_matter": sorted(m), "meets_denial": sorted(n),
            "outcome": {1: "for", -1: "against"}[vote] if vote else ("both" if m else "neither"), "vote": vote}


def _kp_vote_v2(v: _View, area: str) -> tuple[int | None, list[dict]]:
    """SPEC Layer 5, KP v2: decide at the sub-lord's star-lord level, then its own level,
    else abstain (0). Every level is a derivation row."""
    spec = KP_MATTER.get(area)
    if spec is None:
        return None, []
    lords = v.c.lagnas.cusp_lords_kp.get(spec["cusp"])
    if not lords or not v.c.lagnas.cusps_placidus:
        return None, []         # no KP houses (no Placidus cusps without a place): not applicable
    sub = lords["sub"]
    M, N = set(spec["matter"]), set(spec["denial"])
    levels = [_kp_level(v, "star lord", v.c.bodies[sub].nak_lord, M, N), _kp_level(v, "own", sub, M, N)]
    decided = next((x for x in levels if x["vote"]), None)
    rows = [{"cusp": spec["cusp"], "basis": "lagna", "cusp_star": lords["star"], "sub": sub,
             "matter_houses": spec["matter"], "denial_houses": spec["denial"], **x,
             "decides": x is decided} for x in levels]
    return (decided["vote"] if decided else 0), rows


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
        if f.status in OUT_OF_DEFAULT:
            continue
        theta = sum(val for th, val in f.themes.items() if name in THEME_AREAS.get(th, []))
        rule_term += WEIGHTS["rule"] * FIRE_BASIS[f.basis] * theta

    vparts, agree, varga_rows = [], [], []
    v2 = v.c.meta.varga_term == "v2"
    if v.c.meta.varga_term not in ("v1", "v2"):
        raise ValueError(f"varga_term must be v1 or v2, not {v.c.meta.varga_term!r}")
    # Lords in the fixed planet order: lords_all is a set, and a set of strings iterates in a
    # different order in every process (hash randomisation), which reordered the derivation
    # rows the writer and checker are sent from one run to the next.
    lords_ordered = [p for p in GRAHAS if p in lords_all]
    for p in [q for q in dict.fromkeys(lords_ordered + karakas) if q in SEVEN]:
        for varga in spec["vargas"]:
            dignity = v.varga_dignity(p, varga)
            d1, dv = _sgn(v.D[p]), _sgn(dignity)
            vott = varga == "D9" and v.c.bodies[p].vargottama
            if v2:
                x = dignity / 2.0 + (1 if vott else 0)
            else:
                x = 0 if d1 == 0 or dv == 0 else (1 if d1 == dv else -1)
                x += 1 if vott else 0
            vparts.append(x)
            agree.append(d1 == dv)
            row = {"planet": p, "varga": varga, "d1": v.c.bodies[p].dignity,
                   "varga_sign": SIGNS[VARGAS[varga](v.lon[p])], "varga_dignity": dignity}
            if v2:
                row |= {"signed": dignity / 2.0, "vargottama_d9": vott, "agrees_with_d1": d1 == dv}
            varga_rows.append(dict(row, score=x))
    V = statistics.mean(vparts) if vparts else 0.0
    consistency = statistics.mean(agree) if (v2 and agree) else None
    nav = sum(v.tara(p) for p in dict.fromkeys(lords_ordered + karakas))
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
    details = _vote_details(v, spec, houses, karakas, lords_all, varga_rows, arudha_signs, occ, touching)
    if v.c.meta.kp_vote == "v2":
        kp, details["kp"] = _kp_vote_v2(v, name)
    elif v.c.meta.kp_vote == "v1":
        kp_votes = [x for x in (_kp_vote(v, c, spec["houses"]) for c in spec.get("kp", [])) if x is not None]
        kp = _sgn(sum(kp_votes)) if kp_votes else None
    else:
        raise ValueError(f"kp_vote must be v1 or v2, not {v.c.meta.kp_vote!r}")
    votes = {
        "house": _sgn(house_term), "lord": _sgn(lord_term + disp_term), "karaka": _sgn(karaka_term),
        "varga": _sgn(V), "arudha": arudha_vote,
        "kp": kp,
        "panchanga": _sgn(P) if touching else None,
    }

    polarity, touches = _polarity(v, spec["houses"][0], karakas[0] if karakas else None)
    terms = {"house": house_term, "lord": lord_term, "karaka": karaka_term, "rules": rule_term,
             "varga": WEIGHTS["varga"] * V, "navatara": WEIGHTS["navatara"] * nav,
             "dispositor": disp_term, "panchanga": WEIGHTS["panchanga"] * P}
    return {"S": S, "votes": votes, "polarity": polarity, "touches": touches, "terms": terms,
            "lords": sorted(lords_all), "karakas": karakas, "details": details,
            "varga_consistency": consistency}


def _vote_details(v: _View, spec, houses, karakas, lords_all, varga_rows, arudha_signs, occ, touching) -> dict:
    """What each family's vote used, in chart terms (no longitudes), for narration. Every row
    with a house names the basis (lagna, moon, sun) it is counted from and the house number
    from that basis, so Scorpio for a Taurus lagna and an Aquarius Sun is "the 10th from the
    Sun" (an area house there), and "the 7th from the lagna" only as the 10th's Bhavat Bhavam."""
    bb = v.f.bhava_bala.whole_sign
    primary = spec["houses"][0]
    derived = {h for h in houses if h not in spec["houses"]}
    house, lords = [], []
    for basis in BASIS_WEIGHT:
        for h in houses:
            sign = v.sign_of_house(h, basis)
            lh = v.lagna_house(sign)
            row = {"basis": basis, "house": h, "sign": SIGNS[sign]}
            if h in derived:
                row["bhavat_bhavam_of"] = primary
            house.append(dict(row, bhava_bala_rupas=round(bb[lh].rupas, 2), relative=round(v.B[lh], 2)))
            p = SIGN_LORD[sign]
            lords.append(dict(row, lord=p, lord_sign=SIGNS[v.sign[p]], lord_house_from_lagna=v.c.bodies[p].house,
                              dignity=v.c.bodies[p].dignity, shadbala_ratio=round(v.ratio[p], 2),
                              final_dispositor=v.f.dispositors.sign[p][-1]))

    def area_house_of(sign: int) -> list[dict]:
        """Every basis from which a sign is one of the area's houses."""
        return [{"basis": b, "house": h} for b in BASIS_WEIGHT for h in houses if v.sign_of_house(h, b) == sign]

    karaka = [{"planet": p, "basis": "lagna", "house": v.c.bodies[p].house, "sign": SIGNS[v.sign[p]],
               "area_house_from": area_house_of(v.sign[p]), "dignity": v.c.bodies[p].dignity,
               "shadbala_ratio": round(v.ratio.get(p, 0.0), 2) if p in SEVEN else None} for p in karakas]
    pads = spec.get("arudha", [])
    arudha = {"padas": [{"pada": n, "basis": "lagna", "house": v.lagna_house(s), "sign": SIGNS[s],
                         "occupants": [q for q in GRAHAS if v.sign[q] == s],
                         "benefics": [q for q in GRAHAS if v.sign[q] == s and q in v.benefics]}
                        for n, s in zip(pads, arudha_signs)]}
    if spec.get("mks"):
        arudha = {"marana_karaka_sthana": [{"planet": q, "basis": "lagna", "house": b.house}
                                           for q, b in v.c.bodies.items() if b.marana_karaka_sthana]}
    kp = []
    for c in spec.get("kp", []):
        lords_c = v.c.lagnas.cusp_lords_kp.get(c)
        if lords_c:
            sub = lords_c["sub"]
            kp.append({"cusp": c, "basis": "lagna", "star": lords_c["star"], "sub": sub,
                       "sub_house": v.c.bodies[sub].house, "sub_owns": v.f.lordship.get(sub, []),
                       "area_houses": spec["houses"]})
    pl = v.c.panchanga
    panchanga = [{"planet": q, "role": [r for r, x in (("tithi", pl.tithi_lord), ("vara", pl.vara_lord),
                                                       ("nakshatra", pl.nakshatra_lord), ("yoga", pl.yoga_lord))
                                         if x == q],
                  "rules": [{"basis": b, "house": h} for b in BASIS_WEIGHT for h in houses
                            if SIGN_LORD[v.sign_of_house(h, b)] == q],
                  "karaka": q in karakas, "shadbala_ratio": round(v.ratio[q], 2)} for q in touching]
    return {"house": house, "lord": lords, "karaka": karaka, "varga": varga_rows, "arudha": arudha,
            "kp": kp, "panchanga": panchanga}


def _touches_sign(v: _View, planet: str, sign: int) -> bool:
    """Occupies or conjoins (same sign) or aspects (whole-sign graha drishti) a sign."""
    h = v.c.bodies[planet].house
    target = v.lagna_house(sign)
    return h == target or (planet in SEVEN and target in aspected_houses(planet, h))


def _polarity(v: _View, first: int, main_karaka: str | None) -> tuple[list[str], dict[str, list[str]]]:
    """Saturn (delay) and Mars (intensity) flag an area when they touch at least two of its
    first house, that house's lord and its main karaka (SPEC Layer 5); a planet does not
    touch itself. Rahu (volatility) and Ketu (detachment) keep the single touch of the
    first house (SPEC's two-touch rule names delay/intensity only)."""
    house_sign = v.sign_of_house(first, "lagna")
    lord = v.lord_of(first, "lagna")
    flags, record = [], {}
    for planet, flag in POLARITY.items():
        hits = []
        if _touches_sign(v, planet, house_sign):
            hits.append(f"house H{first}")
        if planet in ("Saturn", "Mars"):
            if lord == planet:
                continue          # v3: the lord of the primary house does not afflict it
            if _touches_sign(v, planet, v.sign[lord]):
                hits.append(f"lord {lord}")
            if (main_karaka and main_karaka not in (planet, lord)
                    and _touches_sign(v, planet, v.sign[main_karaka])):
                hits.append(f"karaka {main_karaka}")
            needed = 2
        else:
            needed = 1
        if len(hits) >= needed:
            flags.append(flag)
            record[flag] = hits
    return flags, record


def confidence(S: float, votes: dict[str, int | None], rho: dict[str, float],
               weights: dict[str, float] | None = None) -> tuple[float, float, float]:
    """`weights` overrides 1 - rho per family (family_weights: the varga consistency)."""
    direction = _sgn(S)
    applicable = {f: x for f, x in votes.items() if x is not None}
    w = {f: (weights[f] if weights and f in weights else 1.0 - rho.get(f, 0.0)) for f in applicable}
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
        if f.status in OUT_OF_DEFAULT:
            continue
        for n in f.nodes:
            if n in fired:
                fired[n].add(f.id)
    applicable = {p: 0 for p in SEVEN}
    for r in rules:
        if r.data["status"] in OUT_OF_DEFAULT:
            continue
        w = r.data["when"]
        sides = [w["pair"]["a"], w["pair"]["b"]] if "pair" in w else [w]
        cand = set()
        for side in sides:
            cand |= {side["planet"]} if "planet" in side else set(side.get("planet_in", SEVEN))
        for p in cand & set(SEVEN):
            applicable[p] += 1
    share = {p: len(fired[p]) / applicable[p] if applicable[p] else 0.0 for p in SEVEN}
    finals = [p for p in v.f.dispositors.final_sign if p in SEVEN]
    formula = v.c.meta.driver_formula
    terms: dict[str, dict[str, float]] = {}
    if formula == "v1":
        comp = {p: v.ratio[p] * v.f.vimsopaka[p]["shodasavarga"] * share[p] for p in SEVEN}
    elif formula == "v2":
        pinda = {p: v.f.ashtakavarga.pinda[p].sodhya for p in SEVEN}
        roles = {p: (("yogakaraka" in v.f.roles[p]) + ("lagna_lord" in v.f.roles[p]) + (p in finals)) / 3.0
                 for p in SEVEN}
        raw = {"shadbala": v.ratio, "vimsopaka": {p: v.f.vimsopaka[p]["shodasavarga"] for p in SEVEN},
               "rules": share, "pinda_rank": _ranks(pinda)}
        terms = {name: _minmax(vals) for name, vals in raw.items()}
        terms["roles"] = roles
        comp = {p: sum(terms[t][p] for t in terms) for p in SEVEN}
    else:
        raise ValueError(f"driver_formula must be v1 or v2, not {formula!r}")
    ranking = sorted(SEVEN, key=lambda p: -comp[p])
    current = {}
    if v.c.meta.jd is not None and v.c.dashas.get("vimshottari"):
        current = {"system": "vimshottari", "as_of_jd": v.c.meta.jd}
    rows = []
    for p in ranking:
        row = {"planet": p, "score": comp[p], "rules_fired": len(fired[p]), "rules_applicable": applicable[p]}
        if terms:
            row["terms"] = {t: terms[t][p] for t in terms}
        rows.append(row)
    return Driver(driver=ranking[0], formula=formula, ranking=rows, dispositor_candidates=finals,
                  alternates=[p for p in finals if p != ranking[0]], current_period=current)


def _minmax(vals: dict[str, float]) -> dict[str, float]:
    """Scale to 0-1 across the seven planets; all equal -> 0."""
    lo, hi = min(vals.values()), max(vals.values())
    return {p: (x - lo) / (hi - lo) if hi > lo else 0.0 for p, x in vals.items()}


def _ranks(vals: dict[str, float]) -> dict[str, float]:
    """Rank 0 (lowest) to 6 (highest), ties sharing the mean rank."""
    order = sorted(vals.values())
    return {p: statistics.mean(i for i, x in enumerate(order) if x == v) for p, v in vals.items()}


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
    vt, kv = chart.meta.varga_term, chart.meta.kp_vote
    rho = family_rho(vt, kv)
    raw = {name: score_area(v, name, spec) for name, spec in AREAS.items()}
    rows = {}
    for name, r in raw.items():
        conf, agree, total = confidence(r["S"], r["votes"], rho, family_weights(r, rho))
        rows[name] = (r, conf, agree, total)
    emphasis = {n: x[0]["S"] * x[1] for n, x in rows.items()}
    cut = area_thresholds(vt, kv)
    areas = {}
    for name, (r, conf, agree, total) in rows.items():
        emphasised = r["S"] >= cut[name]
        areas[name] = AreaScore(
            score_classical=r["S"], score_learned=None,
            tier=tier(conf) if emphasised else "not emphasised", confidence=conf,
            direction={1: "supportive", -1: "adverse", 0: "neutral"}[_sgn(r["S"])],
            emphasised=emphasised, families_agree_w=agree, families_total_w=total,
            votes=r["votes"], vote_details=r["details"], varga_consistency=r["varga_consistency"],
            polarity=r["polarity"],
            polarity_touches=r["touches"], terms=r["terms"],
            lords=r["lords"], karakas=r["karakas"])
    areas["synastry"] = AreaScore(score_classical=None, score_learned=None, tier="needs two charts",
                                  confidence=None, direction="neutral", emphasised=False,
                                  families_agree_w=0.0, families_total_w=0.0, votes={}, polarity=[],
                                  terms={}, lords=[], karakas=[])
    ranked = sorted((n for n in areas if areas[n].emphasised), key=lambda n: -emphasis[n])
    readings = READINGS[:5] + [READINGS_VARGA[vt], READINGS_KP[kv]] + READINGS[5:]
    return Scored(weights="classical-1.0", readings=readings, areas=areas, top=ranked[:3],
                  driver=_driver(v, rules))
