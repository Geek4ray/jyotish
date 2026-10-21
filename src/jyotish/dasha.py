"""Dashas: Vimshottari to any depth, Yogini and Chara (Jaimini) to two levels. Dates are
Julian days; the year length is one setting for all three (Layer 4 of the spec: 365.25
solar, 360 savana, 365.2564 sidereal)."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import (
    CHARA_CO_LORD, EXALTATION, GRAHAS, MOOLATRIKONA, OWN_SIGNS, RATH_NODE_EXALTATION, SAVYA,
    SEVEN, SIGN_LORD, SIGNS, VIMSHOTTARI_ORDER, VIMSHOTTARI_TOTAL, VIMSHOTTARI_YEARS,
    YOGINI_TOTAL, YOGINIS,
)
from .nakshatra import nakshatra_of

YEAR_LENGTHS = {"solar": 365.25, "savana": 360.0, "sidereal": 365.2564}


@dataclass(frozen=True)
class Period:
    lords: tuple[str, ...]   # (maha,) or (maha, antar) or deeper: planets, or signs for Chara
    start_jd: float
    end_jd: float
    names: tuple[str, ...] | None = None   # yogini names for Yogini dasha

    @property
    def level(self) -> int:
        return len(self.lords)

    @property
    def lord(self) -> str:
        return self.lords[-1]


def _sequence_from(lord: str) -> list[str]:
    i = VIMSHOTTARI_ORDER.index(lord)
    return VIMSHOTTARI_ORDER[i:] + VIMSHOTTARI_ORDER[:i]


def vimshottari(moon_lon: float, birth_jd: float, levels: int = 2,
                year_length: float = 365.25) -> list[Period]:
    """All periods from birth through the full 120-year cycle, to `levels` deep,
    starting with the balance of the birth nakshatra lord."""
    pos = nakshatra_of(moon_lon)
    first = pos.lord
    balance_fraction = 1.0 - pos.fraction
    periods: list[Period] = []
    cursor = birth_jd
    for i, maha in enumerate(_sequence_from(first)):
        years = VIMSHOTTARI_YEARS[maha]
        length_days = years * year_length
        if i == 0:
            # The elapsed part of the first maha dasha lies before birth; sub-periods are
            # laid out from the true start so that the antar at birth is correct.
            true_start = cursor - (1.0 - balance_fraction) * length_days
        else:
            true_start = cursor
        end = true_start + length_days
        periods.append(Period((maha,), true_start, end))
        if levels >= 2:
            periods.extend(_subdivide((maha,), true_start, length_days, levels, 2))
        cursor = end
    # Drop sub-periods that ended before birth; keep the maha so the balance is visible.
    return [p for p in periods if p.end_jd > birth_jd or p.level == 1]


def _subdivide(lords: tuple[str, ...], start: float, length_days: float,
               max_level: int, level: int) -> list[Period]:
    out: list[Period] = []
    cursor = start
    for sub in _sequence_from(lords[-1]):
        sub_len = length_days * VIMSHOTTARI_YEARS[sub] / VIMSHOTTARI_TOTAL
        p = Period(lords + (sub,), cursor, cursor + sub_len)
        out.append(p)
        if level < max_level:
            out.extend(_subdivide(p.lords, cursor, sub_len, max_level, level + 1))
        cursor += sub_len
    return out


def period_at(periods: list[Period], jd: float, level: int) -> Period | None:
    for p in periods:
        if p.level == level and p.start_jd <= jd < p.end_jd:
            return p
    return None


def _yogini_index(moon_lon: float) -> int:
    """0-7 into YOGINIS: (nakshatra number + 3) mod 8, 0 meaning the 8th."""
    n = nakshatra_of(moon_lon).index + 1
    return ((n + 3) % 8 - 1) % 8


def yogini(moon_lon: float, birth_jd: float, levels: int = 2,
           year_length: float = 365.25, cycles: int = 3) -> list[Period]:
    """Yogini maha and antar periods from birth for `cycles` rounds of 36 years (three
    rounds cover 108 years), starting with the balance of the birth yogini."""
    if levels not in (1, 2):
        raise ValueError("Yogini dasha is built to two levels")
    first = _yogini_index(moon_lon)
    elapsed = nakshatra_of(moon_lon).fraction
    periods: list[Period] = []
    cursor = None
    for k in range(8 * cycles):
        i = (first + k) % 8
        name, planet, years = YOGINIS[i]
        length = years * year_length
        start = birth_jd - elapsed * length if k == 0 else cursor
        periods.append(Period((planet,), start, start + length, (name,)))
        if levels == 2:
            sub = start
            for j in range(8):
                sname, splanet, syears = YOGINIS[(i + j) % 8]
                sub_len = length * syears / YOGINI_TOTAL
                if sub + sub_len > birth_jd:
                    periods.append(Period((planet, splanet), sub, sub + sub_len, (name, sname)))
                sub += sub_len
        cursor = start + length
    return periods


# --- Chara (Jaimini) dasha -------------------------------------------------------------
#
# Three variants, each a CharaRules value. Sources, read for this implementation:
#  - Raman: B.V. Raman, Studies in Jaimini Astrology, ch. V, Arts. 75-88 (primary text).
#  - K.N. Rao: his article "Jaimini's Chara Dasha - My Approach, Part 1" (Saptarishis) and
#    secondary accounts of his book Predicting through Jaimini's Chara Dasha (a lesson PDF
#    quoting its tables; U.K. Jha; P.V.R. Narasimha Rao, 2005). The book itself was not read.
#  - Rath: Sanjay Rath, Narayana Dasa (Sagar), pp. 34-35, 40-44, 48-52, where Chara dasa is
#    the movable-lagna form of Narayana dasa. His Upadesa Sutras translation was not read.
# Where a source is silent, the choice made is named in the CharaRules field comment.

@dataclass(frozen=True)
class CharaRules:
    start: str             # "lagna" | "stronger_of_1_7"
    order: str             # "regular" | "narayana" (movable regular, fixed by 6ths, dual by trines)
    exaltation_adjust: bool   # +1 exalted lord, -1 debilitated (capped at 12)
    node_exaltation: bool  # apply the adjustment to Rahu and Ketu (Rath's table only)
    dual_lord: str         # "kn_rao" | "raman" | "rath": choosing between Mars/Ketu, Saturn/Rahu
    second_cycle: str      # "twelve_minus" | "repeat" | "none"
    antar_start: str       # "next" (maha sign last) | "lord_of_stronger" (Rath)
    antar_direction: str   # "ninth_from_maha" (savya 9th -> zodiacal) | "odd_even" (Rath)
    saturn_ketu: bool      # Rath's exceptions: Saturn in the sign -> zodiacal; Ketu -> reversed


CHARA_VARIANTS = {
    # Direction by the 9th from the lagna (the same rule as Raman); years without the +-1
    # (his article: he neither adds nor deducts for exaltation). Scorpio/Aquarius: the
    # sources give only "the stronger", ending with degrees, so: more planets with the lord,
    # then the higher degree. Second cycle: no stated rule; his worked example repeats the
    # first-cycle years, so "repeat". Antardashas as Raman (U.K. Jha: he kept Raman's rule).
    "kn_rao": CharaRules(start="lagna", order="regular", exaltation_adjust=False,
                         node_exaltation=False, dual_lord="kn_rao", second_cycle="repeat",
                         antar_start="next", antar_direction="ninth_from_maha", saturn_ketu=False),
    # Arts. 76-88. The book does not mention a second cycle, so none is laid out.
    "raman": CharaRules(start="lagna", order="regular", exaltation_adjust=True,
                        node_exaltation=False, dual_lord="raman", second_cycle="none",
                        antar_start="next", antar_direction="ninth_from_maha", saturn_ketu=False),
    # Narayana Dasa pp. 40-52. Direction by the sign in the 9th bhava (read as the 9th from
    # the lagna); Saturn in the starting sign makes the order regular and zodiacal (J.S.
    # 2.4.33), Ketu there reverses it (J.S. 1.1.8). Ketu's reversal is applied to the starting
    # sign and to each dasa's antardashas, not mid-sequence.
    "rath": CharaRules(start="stronger_of_1_7", order="narayana", exaltation_adjust=True,
                       node_exaltation=True, dual_lord="rath", second_cycle="twelve_minus",
                       antar_start="lord_of_stronger", antar_direction="odd_even", saturn_ketu=True),
}

_MODALITY_RANK = {0: 0, 1: 1, 2: 2}   # movable < fixed < dual


def _modality(sign: int) -> int:
    return sign % 3   # Aries movable, Taurus fixed, Gemini dual, and so on


def rashi_aspects(sign: int) -> set[int]:
    """Jaimini sign aspect: movable signs aspect the fixed signs except the adjacent one,
    fixed signs the movable except the adjacent one, dual signs the other duals."""
    m = _modality(sign)
    if m == 2:
        return {s for s in range(12) if _modality(s) == 2 and s != sign}
    target = 1 if m == 0 else 0
    adjacent = {(sign + 1) % 12, (sign - 1) % 12}
    return {s for s in range(12) if _modality(s) == target and s not in adjacent}


class _Sky:
    """Signs and degrees the Chara rules read; nine grahas."""

    def __init__(self, positions: dict[str, float], lagna_sign: int):
        self.lagna = lagna_sign
        self.sign = {p: int((positions[p] % 360.0) // 30) for p in GRAHAS}
        self.deg = {p: positions[p] % 30.0 for p in GRAHAS}
        self.deg["Rahu"] = 30.0 - self.deg["Rahu"]   # nodes counted backwards (chara karaka degree)
        self.deg["Ketu"] = 30.0 - self.deg["Ketu"]
        self.lord = SIGN_LORD
        self.exaltation = {p: s for p, (s, _) in EXALTATION.items()}
        self.occupants = {s: [p for p in GRAHAS if self.sign[p] == s] for s in range(12)}

    def exalted(self, p: str, rules: CharaRules) -> int:
        """+1 exalted, -1 debilitated, 0 otherwise (by sign)."""
        ex = self.exaltation.get(p)
        if ex is None:
            if not rules.node_exaltation:
                return 0
            ex = RATH_NODE_EXALTATION[p]
        if self.sign[p] == ex:
            return 1
        if self.sign[p] == (ex + 6) % 12:
            return -1
        return 0


def _count(sign: int, target: int) -> int:
    """Signs from `sign` to `target` inclusive, forward from odd-footed signs and backward
    from even-footed ones, minus one; 0 means the lord is in the sign."""
    return (target - sign) % 12 if sign in SAVYA else (sign - target) % 12


def _years_to(sign: int, lord: str, sky: _Sky, rules: CharaRules) -> int:
    n = _count(sign, sky.sign[lord])
    years = 12 if n == 0 else n
    if rules.exaltation_adjust:
        years += sky.exalted(lord, rules)
    return max(0, min(12, years))


def _dignity_status(sign: int, sky: _Sky) -> tuple[int, int, int]:
    """(exalted, moolatrikona, own) counts among the sign's occupants, for Rath's rule 3."""
    ex = mt = own = 0
    for p in sky.occupants[sign]:
        if p not in SEVEN:
            continue
        if sky.exaltation[p] == sign:
            ex += 1
        elif MOOLATRIKONA[p][0] == sign:
            mt += 1
        elif sign in OWN_SIGNS[p]:
            own += 1
    return ex, mt, own


def _rath_stronger(a: int, b: int, sky: _Sky, rules: CharaRules) -> int:
    """Narayana Dasa pp. 34-35, first source rules 2, 3, 4, 6, 7, 8, then the second source
    (aspect of Mercury, Jupiter or the sign's lord). A full tie keeps `a`."""
    tests = [
        lambda s: len(sky.occupants[s]),
        lambda s: _dignity_status(s, sky),
        lambda s: _MODALITY_RANK[_modality(s)],
        lambda s: sky.deg[sky.lord[s]],
        lambda s: int((sky.sign[sky.lord[s]] % 2 == 0) == (s % 2 == 1)),   # rule 7
        lambda s: _sign_years(s, sky, rules),
        lambda s: int(any(s in rashi_aspects(sky.sign[p]) for p in ("Mercury", "Jupiter", sky.lord[s]))),
    ]
    for t in tests:
        ta, tb = t(a), t(b)
        if ta != tb:
            return a if ta > tb else b
    return a


def _dual_lord(sign: int, sky: _Sky, rules: CharaRules) -> str | None:
    """The lord to count to for Scorpio or Aquarius; None means both lords are in the sign
    (12 years in every variant)."""
    a, b = sky.lord[sign], CHARA_CO_LORD[sign]
    in_a, in_b = sky.sign[a] == sign, sky.sign[b] == sign
    if in_a and in_b:
        return None
    if in_a != in_b:
        return b if in_a else a          # one in the sign: count to the other
    if sky.sign[a] == sky.sign[b]:
        return a                          # together elsewhere: same count either way
    ya, yb = _years_to(sign, a, sky, rules), _years_to(sign, b, sky, rules)
    na, nb = len(sky.occupants[sky.sign[a]]) - 1, len(sky.occupants[sky.sign[b]]) - 1
    if rules.dual_lord == "kn_rao":
        if na != nb:
            return a if na > nb else b
        return a if sky.deg[a] >= sky.deg[b] else b
    if rules.dual_lord == "raman":
        # Art. 86: associates, then dual > fixed > movable, then more years; a debilitated
        # winner against an exalted rival yields to the exalted one.
        if na != nb:
            win = a if na > nb else b
        elif _modality(sky.sign[a]) != _modality(sky.sign[b]):
            win = a if _MODALITY_RANK[_modality(sky.sign[a])] > _MODALITY_RANK[_modality(sky.sign[b])] else b
        else:
            win = a if ya >= yb else b
        other = b if win == a else a
        if sky.exalted(win, rules) < 0 and sky.exalted(other, rules) > 0:
            win = other
        return win
    if rules.dual_lord == "rath":
        # The stronger of the signs the lords occupy; equal strength -> the larger period.
        s = _rath_stronger(sky.sign[a], sky.sign[b], sky, rules)
        if s == sky.sign[a] and s != sky.sign[b]:
            return a
        if s == sky.sign[b] and s != sky.sign[a]:
            return b
        return a if ya >= yb else b
    raise ValueError(rules.dual_lord)


def _sign_years(sign: int, sky: _Sky, rules: CharaRules) -> int:
    if sign in CHARA_CO_LORD:
        lord = _dual_lord(sign, sky, rules)
        if lord is None:
            return 12
    else:
        lord = sky.lord[sign]
    return _years_to(sign, lord, sky, rules)


def _sequence(start: int, direct: bool, order: str) -> list[int]:
    step = 1 if direct else -1
    if order == "regular" or _modality(start) == 0:
        return [(start + step * k) % 12 for k in range(12)]
    if _modality(start) == 1:      # fixed: each next dasa is the 6th from the last
        return [(start + step * 5 * k) % 12 for k in range(12)]
    out = []                       # dual: the sign and its trines, then the 10th and its trines
    kendra = start
    for _ in range(4):
        out += [(kendra + step * t) % 12 for t in (0, 4, 8)]
        kendra = (kendra + step * 9) % 12
    return out


def chara_sequence(positions: dict[str, float], lagna_sign: int,
                   variant: str = "kn_rao") -> list[tuple[int, int]]:
    """First-cycle (sign, years) for the twelve mahadashas, in order."""
    rules = CHARA_VARIANTS[variant]
    sky = _Sky(positions, lagna_sign)
    start = lagna_sign
    if rules.start == "stronger_of_1_7":
        start = _rath_stronger(lagna_sign, (lagna_sign + 6) % 12, sky, rules)
    direct = (lagna_sign + 8) % 12 in SAVYA
    order = rules.order
    if rules.saturn_ketu:
        if sky.sign["Saturn"] == start:
            direct, order = True, "regular"
        if sky.sign["Ketu"] == start:
            direct = not direct
    return [(s, _sign_years(s, sky, rules)) for s in _sequence(start, direct, order)]


def _antar_signs(maha: int, sky: _Sky, rules: CharaRules) -> list[int]:
    if rules.antar_direction == "ninth_from_maha":
        direct = (maha + 8) % 12 in SAVYA
    else:
        direct = maha % 2 == 0          # odd sign (Aries = 0) -> zodiacal
    if rules.saturn_ketu:
        if sky.sign["Saturn"] == maha:
            direct = True
        if sky.sign["Ketu"] == maha:
            direct = not direct
    step = 1 if direct else -1
    if rules.antar_start == "next":
        return [(maha + step * k) % 12 for k in range(1, 13)]   # the maha sign comes last
    stronger = _rath_stronger(maha, (maha + 6) % 12, sky, rules)
    first = sky.sign[sky.lord[stronger]]
    return [(first + step * k) % 12 for k in range(12)]


def chara(positions: dict[str, float], lagna_sign: int, birth_jd: float, levels: int = 2,
          year_length: float = 365.25, variant: str = "kn_rao") -> list[Period]:
    """Chara maha and antar dashas from birth (Chara dasha has no balance: the first sign
    runs its full period from birth). Periods are named by sign (see constants.SIGNS);
    zero-year signs in a second cycle are skipped."""
    if levels not in (1, 2):
        raise ValueError("Chara dasha is built to two levels")
    rules = CHARA_VARIANTS[variant]
    sky = _Sky(positions, lagna_sign)
    first = chara_sequence(positions, lagna_sign, variant)
    cycles = [first]
    if rules.second_cycle == "twelve_minus":
        cycles.append([(s, 12 - y) for s, y in first])
    elif rules.second_cycle == "repeat":
        cycles.append(list(first))
    periods: list[Period] = []
    cursor = birth_jd
    for cycle in cycles:
        for sign, years in cycle:
            if years <= 0:
                continue
            length = years * year_length
            periods.append(Period((SIGNS[sign],), cursor, cursor + length))
            if levels == 2:
                sub_len = length / 12.0
                for k, a in enumerate(_antar_signs(sign, sky, rules)):
                    periods.append(Period((SIGNS[sign], SIGNS[a]), cursor + k * sub_len,
                                          cursor + (k + 1) * sub_len))
            cursor += length
    return periods
