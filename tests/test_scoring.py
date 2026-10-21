"""Layer 5 scoring on the reference chart. Where the simplest reading of SPEC's formula
does not give SPEC's worked-example tiers, the test asserts what the engine gives and
says why (SPEC is corrected, the formula is not tuned)."""

import json

import pytest

from jyotish.chart import analyse
from jyotish.reference import (
    REFERENCE_ASC, REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, REFERENCE_POSITIONS,
    REFERENCE_SPEEDS, reference_time_inputs,
)
from jyotish.rules import default_rules
from jyotish.scoring import AREAS, FAMILIES, RHO_FILE, confidence, family_rho, tier
from jyotish.uncertainty import assess


@pytest.fixture(scope="module")
def chart():
    return analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **reference_time_inputs())


@pytest.fixture(scope="module")
def sc(chart):
    return chart.scored


def test_nineteen_areas(sc):
    assert len(AREAS) == 18 and len(sc.areas) == 19
    assert sc.areas["synastry"].tier == "needs two charts" and sc.areas["synastry"].score_classical is None
    assert sc.weights == "classical-1.0" and sc.readings


def test_career_strong(sc):
    a = sc.areas["career"]
    assert a.tier == "strong" and a.direction == "supportive" and a.confidence > 0.7
    # v3: Saturn is the 10th lord, so it does not flag career (it did under v2); Mars
    # touches the 10th, its lord Saturn and the karaka Sun.
    assert a.polarity == ["intensity"]
    assert a.polarity_touches == {"intensity": ["house H10", "lord Saturn", "karaka Sun"]}


def test_wealth_is_moderate_not_strong(sc):
    # SPEC expects "strong". The simplest reading gives "moderate": the Jaimini family
    # votes against (the waning Moon in A2, Libra; Rahu in A11, Gemini) and the varga
    # family abstains (D2/D16 disagree), so agreement is under 0.5.
    a = sc.areas["wealth"]
    assert a.tier == "moderate" and 0.4 <= a.confidence < 0.7
    assert a.votes["arudha"] == -1 and a.votes["varga"] == 0
    assert "volatility" in a.polarity                     # Rahu in the 2nd, as SPEC's example
    assert a.polarity_touches["delay"] == ["lord Mercury", "karaka Jupiter"]


def test_marriage_flags_and_tier(sc):
    # Two-touch polarity: Saturn aspects the 7th and its lord Mars (in the 7th), so "delay";
    # Mars occupies the 7th but is its own lord and does not touch Venus, so one touch and
    # no "intensity" (SPEC's reader expected delay/intensity). Under varga v1 the tier was
    # "strong" by a hair (0.706); under v2 the varga family's weight is scaled by its
    # consistency (half the D9 pairs agree with D1, so x0.75) and the tier is "moderate",
    # as SPEC's reader expected: the Upapada family opposes. This chart is built from the
    # printed longitudes with no place, so it has no Placidus cusps and KP v2 (occupation in
    # the KP houses) is not applicable; v1 reads the fallback 7th cusp from the ascendant.
    a = sc.areas["marriage"]
    assert a.polarity == ["delay"]
    assert a.polarity_touches == {"delay": ["house H7", "lord Mars"]}
    assert a.tier == "moderate" and 0.64 < a.confidence < 0.65 and a.varga_consistency == 0.5
    assert a.votes["arudha"] == -1 and a.votes["kp"] is None and a.vote_details["kp"] == []


def test_two_touch_rule(sc):
    for name, a in sc.areas.items():
        for flag, hits in a.polarity_touches.items():
            assert flag in a.polarity
            if flag in ("delay", "intensity"):
                assert len(hits) >= 2 and len(set(hits)) == len(hits), (name, flag)
            planet = {"delay": "Saturn", "intensity": "Mars"}.get(flag)
            assert not any(h.endswith(" " + planet) for h in hits if planet), (name, flag)
    # Gains: Jupiter is both the 11th lord and the main karaka, one object, one touch.
    assert sc.areas["gains"].polarity == []
    # The literal rule flags more of this chart than the one-touch rule did (13 vs 9 areas):
    # Saturn in H1 and Mars in H7 aspect H1, H2, H3, H7, H10, where most planets sit. v3
    # removes career's and reputation's "delay" but no area loses its last flag.
    assert sum(1 for a in sc.areas.values() if a.polarity) == 13
    assert "delay" not in sc.areas["reputation"].polarity


def test_v3_lord_does_not_flag_its_own_house(chart, sc):
    from jyotish.scoring import AREAS
    for name, spec in AREAS.items():
        lord = chart.features.lordship and next(p for p, hs in chart.features.lordship.items()
                                                 if spec["houses"][0] in hs)
        for flag, planet in (("delay", "Saturn"), ("intensity", "Mars")):
            if planet == lord:
                assert flag not in sc.areas[name].polarity, name


def test_not_emphasised_is_reported_not_scored_low(chart, sc, capsys):
    from jyotish.cli import print_scored
    # Below the area's 40th percentile over the population run: children, father, gains.
    # (Under the old chart-median cut nine areas were hidden; the six that reappear
    # are all weak / mixed.)
    from jyotish.scoring import area_thresholds
    quiet = [n for n, a in sc.areas.items() if a.tier == "not emphasised"]
    assert quiet == ["children", "father", "gains"]
    cut = area_thresholds()
    assert all(sc.areas[n].score_classical < cut[n] and not sc.areas[n].emphasised for n in quiet)
    for n in ("siblings", "intellect", "fortune", "spirituality", "mind", "reputation"):
        assert sc.areas[n].tier == "weak / mixed"
    print_scored(chart)
    out = capsys.readouterr().out
    for n in quiet:
        line = next(l for l in out.splitlines() if l.strip().startswith(n + " "))
        assert line.split() == [n, "not", "emphasised"]   # no score, no tier word
    assert set(sc.top) <= {n for n, a in sc.areas.items() if a.emphasised} and len(sc.top) == 3


def test_experimental_fires_stay_out(chart):
    without = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS,
                      rules=[r for r in default_rules() if r.data["status"] != "experimental"],
                      **reference_time_inputs()).scored
    for n, a in chart.scored.areas.items():
        assert a.score_classical == without.areas[n].score_classical


def test_confidence_and_tiers():
    rho = {f: 0.0 for f in FAMILIES}
    conf, agree, total = confidence(5.0, {"house": 1, "lord": 1, "karaka": -1, "varga": 0,
                                          "arudha": None, "kp": None, "panchanga": None}, rho)
    assert (agree, total) == (2.0, 4.0) and conf == pytest.approx((2 - 1) / 4)
    assert tier(0.71) == "strong" and tier(0.7) == "moderate" and tier(0.4) == "moderate"
    assert tier(0.39) == "weak / mixed"


def test_percentiles_cached_beside_rho():
    from jyotish.scoring import PCT_FILE
    data = json.loads(PCT_FILE.read_text())
    assert data["n_charts"] == 10_000 and set(data["percentiles"]) == set(AREAS)
    for row in data["percentiles"].values():
        assert row["p10"] <= row["p25"] <= row["p40"] <= row["p50"] <= row["p75"] <= row["p90"]


def test_rho_table_cached_in_repo():
    # One table per (varga_term, kp_vote): v1 keeps the original name, v2 (the default) has its own.
    from jyotish.scoring import table_path
    for vt, kv in (("v1", "v1"), ("v2", "v1"), ("v2", "v2")):
        data = json.loads(table_path(RHO_FILE, vt, kv).read_text())
        assert data["n_charts"] == 10_000 and set(data["rho"]) == set(FAMILIES)
        assert family_rho(vt, kv) == data["rho"]
        assert all(-0.2 < r < 0.5 for r in data["rho"].values())
    assert table_path(RHO_FILE, "v1", "v1") == RHO_FILE
    assert "varga_term v2, kp_vote v2" in json.loads(table_path(RHO_FILE).read_text())["settings"]
    with pytest.raises(FileNotFoundError, match="varga_term=v1, kp_vote=v2"):
        family_rho("v1", "v2")


def test_driver_v2(sc, chart):
    # Sum of five 0-1 terms (SPEC hypothesis v2). Venus leads: highest Shadbala ratio,
    # lagna lord and a final dispositor. Saturn, at 0 under v1, now scores on Vimsopaka and
    # Sodhya Pinda (both the highest) and its yogakaraka role.
    d = sc.driver
    assert d.formula == "v2" and d.driver == "Venus" == d.ranking[0]["planet"]
    assert d.dispositor_candidates == ["Jupiter", "Mars", "Venus"]   # the final sign dispositors
    assert d.alternates == ["Jupiter", "Mars"]
    for r in d.ranking:
        assert set(r["terms"]) == {"shadbala", "vimsopaka", "rules", "pinda_rank", "roles"}
        assert all(0.0 <= x <= 1.0 for x in r["terms"].values())
        assert r["score"] == pytest.approx(sum(r["terms"].values()))
    sat = next(r for r in d.ranking if r["planet"] == "Saturn")
    assert sat["score"] > 2 and sat["terms"]["vimsopaka"] == 1.0 and sat["terms"]["pinda_rank"] == 1.0
    assert sat["terms"]["roles"] == pytest.approx(1 / 3)               # yogakaraka


def test_driver_v1_kept_for_comparison(chart):
    kw = dict(reference_time_inputs())
    kw["meta"] = kw["meta"].model_copy(update={"driver_formula": "v1"})
    c = analyse(REFERENCE_POSITIONS, REFERENCE_ASC, speeds=REFERENCE_SPEEDS, **kw)
    d = c.scored.driver
    assert d.formula == "v1" and d.driver == "Mercury"
    for r in d.ranking:
        ratio = c.features.shadbala.planets[r["planet"]].ratio
        vim = c.features.vimsopaka[r["planet"]]["shodasavarga"]
        share = r["rules_fired"] / r["rules_applicable"] if r["rules_applicable"] else 0
        assert r["score"] == pytest.approx(ratio * vim * share)
    assert {r["planet"]: r["score"] for r in d.ranking}["Saturn"] == 0.0


def test_stability_gates_narration_not_score():
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    from jyotish.chart import compute
    plain = compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False).scored
    for n, a in c.scored.areas.items():
        assert a.score_classical == plain.areas[n].score_classical
    car = c.scored.areas["career"]
    # Under KP v1 the 10th-cusp sub-lord turning from Ketu (8th: against) to Venus within a
    # minute flipped career's tier in part of the samples (0.605). Under v2 both sub-lords'
    # significations meet the matter and the denial houses at both levels, so the KP vote
    # abstains either way and every family's vote, and the tier, hold in all samples.
    assert car.stability.time == car.stability.ayanamsa == car.stability.house == 1.0
    assert set(car.vote_stability.values()) == {1.0}
    for a in c.scored.areas.values():
        if a.stability is not None:
            assert a.narrate == (a.stability.time >= 0.5)


def test_unknown_time_is_cannot_be_assessed():
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False,
               time_accuracy="unknown", n=40)
    shaky = [a for a in c.scored.areas.values() if a.stability is not None and a.stability.time < 0.5]
    assert shaky and all(a.tier == "cannot be assessed" and not a.narrate for a in shaky)


# --- SPEC Layer 5 revision (2026-10-21): varga term v2 and KP vote v2 ---------------------

@pytest.fixture(scope="module")
def timed():
    from jyotish.chart import compute
    return compute(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def _rescored(chart, **meta):
    from jyotish.scoring import score
    c = chart.model_copy(deep=True)
    c.meta = c.meta.model_copy(update=meta)
    return score(c)


def test_varga_v2_is_the_vargas_own_dignity(timed):
    sc = timed.scored
    assert timed.meta.varga_term == "v2"
    rows = {(r["planet"], r["varga"]): r for r in sc.areas["career"].vote_details["varga"]}
    # Jupiter: friendly in D10 (Aries), enemy's sign in D1. v1 scored the disagreement -1;
    # v2 scores the varga's verdict, +0.5 halved.
    jup = rows[("Jupiter", "D10")]
    assert (jup["varga_dignity"], jup["signed"], jup["agrees_with_d1"], jup["score"]) == (0.5, 0.25, False, 0.25)
    assert rows[("Mars", "D10")]["score"] == 1.0                       # exalted in Capricorn: +2 halved
    assert sc.areas["career"].varga_consistency == pytest.approx(5 / 7)
    # Health: the Sun is debilitated in D30 and D3. v1 counted that agreeing with its D1
    # enemy sign as +1 each; v2 scores -1 each, and the health varga vote turns against.
    h = {(r["planet"], r["varga"]): r for r in sc.areas["health"].vote_details["varga"]}
    assert h[("Sun", "D30")]["score"] == -1.0 and h[("Sun", "D3")]["score"] == -1.0
    assert sc.areas["health"].votes["varga"] == -1
    v1 = _rescored(timed, varga_term="v1", kp_vote="v1")
    assert v1.areas["health"].votes["varga"] == 1 and v1.areas["career"].varga_consistency is None
    assert {(r["planet"], r["varga"]): r["score"] for r in v1.areas["career"].vote_details["varga"]}[
        ("Jupiter", "D10")] == -1


def test_varga_consistency_scales_the_varga_weight(timed):
    from jyotish.scoring import family_weights
    a = timed.scored.areas["marriage"]
    rho = family_rho()
    w = family_weights(a, rho)
    assert w["varga"] == pytest.approx((1 - rho["varga"]) * (0.5 + 0.5 * a.varga_consistency))
    assert w["house"] == pytest.approx(1 - rho["house"])
    conf, agree, total = confidence(a.score_classical, a.votes, rho, w)
    assert conf == pytest.approx(a.confidence) and total == pytest.approx(a.families_total_w)


def test_kp_v2_career_abstains_at_both_levels(timed):
    a = timed.scored.areas["career"]
    assert a.votes["kp"] == 0
    star, own = a.vote_details["kp"]
    assert (star["cusp"], star["sub"], star["cusp_star"]) == (10, "Ketu", "Moon")
    assert (star["matter_houses"], star["denial_houses"]) == ([2, 6, 10, 11], [1, 5, 9])
    # Star-lord level: Ketu is in Purva Ashadha (Venus); Venus in the 11th owns 1 and 6.
    assert (star["level"], star["planet"], star["occupies"], star["owns"]) == ("star lord", "Venus", 11, [1, 6])
    assert (star["meets_matter"], star["meets_denial"], star["outcome"]) == ([6, 11], [1], "both")
    # Own level: Ketu in the 8th owns nothing; through its sign lord Jupiter (1st; 8, 11).
    assert (own["level"], own["planet"], own["occupies"], own["owns"]) == ("own", "Ketu", 8, [])
    assert [(x["planet"], x["as"], x["occupies"], x["owns"]) for x in own["via"]] == [("Jupiter", "sign lord", 1, [8, 11])]
    assert (own["significations"], own["outcome"]) == ([1, 8, 11], "both")
    assert not star["decides"] and not own["decides"]
    v1 = _rescored(timed, varga_term="v1", kp_vote="v1")
    assert v1.areas["career"].votes["kp"] == -1


def test_kp_v2_decides_at_the_star_lord_level_first(timed):
    sc = timed.scored
    # Health, 6th cusp: sub-lord Jupiter, star lord Moon in the 6th (disease): against, decided
    # there although Jupiter itself signifies 1 and 11 (recovery).
    star, own = sc.areas["health"].vote_details["kp"]
    assert (star["planet"], star["outcome"], star["decides"]) == ("Moon", "against", True)
    assert own["outcome"] == "both" and sc.areas["health"].votes["kp"] == -1
    # Marriage, 7th cusp: sub-lord Mercury, star lord Mars in the 7th owning 7 and 12: for.
    star, _ = sc.areas["marriage"].vote_details["kp"]
    assert (star["planet"], star["meets_matter"], star["meets_denial"], star["decides"]) == ("Mars", [7], [], True)
    assert sc.areas["marriage"].votes["kp"] == 1
    # The KP areas are the SPEC's seven: the 4th cusp is read for mother_home (M 4 11 12,
    # N 3 5 10) and for the mind (M 4 11, N 6 8 12).
    from jyotish.constants import KP_MATTER
    assert {n for n, a in sc.areas.items() if a.votes.get("kp") is not None} == set(KP_MATTER)
    assert sc.areas["mother_home"].votes["kp"] == -1
    # Mind: sub-lord Venus; its star lord Mercury signifies 10, 2, 5 (neither M nor N), Venus
    # itself 11 (matter) and 6 (denial): undecided at both levels, an abstention.
    star, own = sc.areas["mind"].vote_details["kp"]
    assert (star["sub"], star["matter_houses"], star["denial_houses"]) == ("Venus", [4, 11], [6, 8, 12])
    assert (star["planet"], star["outcome"], own["outcome"]) == ("Mercury", "neither", "both")
    assert sc.areas["mind"].votes["kp"] == 0


def test_kp_v2_node_adds_conjoined_aspecting_and_sign_lord(timed):
    from jyotish.scoring import _View, _significations
    v = _View(timed)
    houses, me, via = _significations(v, "Rahu")                       # Rahu in Gemini, the 2nd, alone
    assert me == {"planet": "Rahu", "occupies": 2, "occupies_by_sign": 2, "owns": []}
    assert [(x["planet"], x["as"]) for x in via] == [("Mercury", "sign lord")]
    asp = timed.model_copy(deep=True)
    asp.meta = asp.meta.model_copy(update={"node_aspects": True})
    _, _, via = _significations(_View(asp), "Rahu")                   # Mars in the 7th aspects the 2nd
    assert [(x["planet"], x["as"]) for x in via] == [("Mars", "aspecting"), ("Mercury", "sign lord")]


def test_reference_tiers_v1_and_v2(timed):
    v2 = {n: a.tier for n, a in timed.scored.areas.items()}
    v1 = {n: a.tier for n, a in _rescored(timed, varga_term="v1", kp_vote="v1").areas.items()}
    changed = {n: (v1[n], v2[n]) for n in v2 if v1[n] != v2[n]}
    assert changed == {"mother_home": ("moderate", "weak / mixed"), "health": ("strong", "weak / mixed"),
                       "debts_enemies": ("strong", "moderate"), "marriage": ("strong", "moderate")}
    assert timed.scored.top == ["career", "marriage", "longevity"]
    # Career stays moderate, 0.0003 under the strong cut: the KP abstention counts in the
    # applicable weight. With KP not applicable it would be strong (the printed-positions
    # chart, which has no KP cusps, is).
    car = timed.scored.areas["career"]
    assert car.tier == "moderate" and 0.699 < car.confidence < 0.7
    assert any("V v2" in r for r in timed.scored.readings) and any("KP v2" in r for r in timed.scored.readings)


def test_kp_occupation_is_by_placidus_house(timed):
    # Occupation counts in the KP houses (Placidus cusps); ownership stays by sign. Saturn at
    # Taurus 2.1 lies before the 1st cusp (Taurus 6.3), so it is in the 12th KP house; the
    # Sun at Aquarius 27.8 is past the 11th cusp (Aquarius 20.4).
    from jyotish.scoring import _View, _significations
    v = _View(timed)
    moved = {p: (timed.bodies[p].house, v.kp_house(p)) for p in timed.bodies if v.kp_house(p) != timed.bodies[p].house}
    assert moved == {"Sun": (10, 11), "Saturn": (1, 12)}
    houses, me, _ = _significations(v, "Saturn")
    assert (me["occupies"], me["occupies_by_sign"], me["owns"]) == (12, 1, [9, 10]) and houses == {9, 10, 12}
    # Neither is a sub-lord, star lord or node sign lord in any KP derivation of this chart,
    # so no KP vote changes with the switch from whole-sign occupation.
    for a in timed.scored.areas.values():
        for r in a.vote_details.get("kp") or []:
            assert r["occupies"] == r["occupies_by_sign"] and all(
                x["occupies"] == x["occupies_by_sign"] for x in r["via"])
    bad = timed.model_copy(deep=True)
    bad.meta = bad.meta.model_copy(update={"kp_house_system": "koch"})
    with pytest.raises(ValueError, match="kp_house_system must be placidus"):
        _View(bad).kp_house("Sun")
