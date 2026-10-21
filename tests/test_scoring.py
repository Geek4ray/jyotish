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
    assert {"delay", "intensity"} <= set(a.polarity)     # Saturn and Mars aspect the 10th


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
    # no "intensity" (SPEC's reader expected delay/intensity). The tier is "strong" by a
    # hair (0.706) where the reader expected "moderate": the Upapada family opposes.
    a = sc.areas["marriage"]
    assert a.polarity == ["delay"]
    assert a.polarity_touches == {"delay": ["house H7", "lord Mars"]}
    assert a.tier == "strong" and 0.70 < a.confidence < 0.72
    assert a.votes["arudha"] == -1 and a.votes["kp"] == 1


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
    # Saturn in H1 and Mars in H7 aspect H1, H2, H3, H7, H10, where most planets sit.
    assert sum(1 for a in sc.areas.values() if a.polarity) == 13


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
    data = json.loads(RHO_FILE.read_text())
    assert data["n_charts"] == 10_000 and set(data["rho"]) == set(FAMILIES)
    assert family_rho() == data["rho"]
    assert all(-0.2 < r < 0.5 for r in data["rho"].values())


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
    # The KP 10th-cusp sub-lord turns from Ketu (8th: against) to Venus within a minute, so
    # career's tier holds in only part of the +-2 min samples.
    assert 0.3 < car.stability.time < 0.9 and car.stability.label in ("sensitive", "unstable")
    for a in c.scored.areas.values():
        if a.stability is not None:
            assert a.narrate == (a.stability.time >= 0.5)


def test_unknown_time_is_cannot_be_assessed():
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False,
               time_accuracy="unknown", n=40)
    shaky = [a for a in c.scored.areas.values() if a.stability is not None and a.stability.time < 0.5]
    assert shaky and all(a.tier == "cannot be assessed" and not a.narrate for a in shaky)
