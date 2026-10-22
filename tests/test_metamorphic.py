"""Metamorphic tests: label-free checks that the engine's outputs move only where the engine says
they may (SPEC Layer 1b, Layer 7). On the reference chart and three synthetic births
(tests/fixtures/births.json; no other births were in the fixtures).

  - birth time +-1 minute changes nothing the sampler marked stable (a fire, a varga sign, a nakshatra,
    a tier), and everything that changed is something the sampler saw change (time share under 1, or a
    fire seen only elsewhere in the window).
    The exact-accuracy sampler draws +-2 minutes; a finding whose boundary is d minutes away holds in
    1 - (2 - d)/4 of the window, so "stable" (over 0.8) puts the boundary beyond 1.2 minutes;
  - a 1'' change of ayanamsa moves every position by 1'' and changes nothing else: no sign, nakshatra,
    pada, varga sign, KP sub-lord, fire or tier, except where the 1'' crosses an edge, which the test
    allows and names (a body within 1'' of a pada edge, one chart in 500; review 2026-10-23, F14);
  - another sampler seed gives the same stability class on at least 95% of findings;
  - three paraphrases of one career question route to the same areas, the same tier and the same
    offered findings.
The narration-side invariants (a reworded question, a swapped writer model: the same accepted claim
set) call the Anthropic API and run only under JYOTISH_LIVE_NARRATION=1; they record every call to
tests/fixtures/metamorphic_live.json, as the live narration test does."""

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from jyotish.chart import compute
from jyotish.uncertainty import assess, label, placements, rule_keys

FIXTURES = Path(__file__).parent / "fixtures"
BIRTHS = json.loads((FIXTURES / "births.json").read_text())["births"]
IDS = [b["name"] for b in BIRTHS]
AS_OF = date(2026, 10, 21)
QUESTIONS = ["How will my career go, and when is the best time for a job change?",
             "What does my chart say about my work, and when should I change jobs?",
             "When is a good time to switch jobs, and how does my profession look?"]
LIVE = os.environ.get("JYOTISH_LIVE_NARRATION") == "1"


def _utc(b):
    return datetime.fromisoformat(b["utc"])


@pytest.fixture(scope="module", params=BIRTHS, ids=IDS)
def birth(request):
    b = request.param
    return b, assess(_utc(b), b["lat"], b["lon"], true_node=False, seed=0)


def _tiers(chart):
    return {n: a.tier for n, a in chart.scored.areas.items()}


@pytest.mark.parametrize("minutes", [-1, 1])
def test_a_minute_changes_nothing_marked_stable(birth, minutes):
    b, c = birth
    u = c.uncertainty
    other = compute(_utc(b) + timedelta(minutes=minutes), b["lat"], b["lon"], true_node=False)
    # Fired rules: one that vanished was not stable; one that appeared was seen elsewhere in the window.
    shares = {(f.id, f.basis, tuple(n for n in f.nodes if not n.startswith("H"))): f.stability.time
              for f in c.fired_rules}
    elsewhere = {(r.id, r.basis, tuple(r.planets)) for r in u.rules_elsewhere}
    here, there = rule_keys(c), rule_keys(other)
    for k in here - there:
        assert label(shares[k]) != "stable" and shares[k] < 1.0, (k, shares[k])
    for k in there - here:
        assert k in elsewhere, k
    # Varga signs: every change was seen by the sampler, and none was marked stable.
    before, after = placements(c), placements(other)
    changed = [k for k in before if after.get(k) != before[k]]
    for varga, body in changed:
        st = u.placements[varga][body]
        assert st.label != "stable" and st.time < 1.0, (varga, body, st)
    # Nakshatras likewise: a body or the lagna whose nakshatra changed was never marked stable.
    from jyotish.uncertainty import nakshatras
    for k, idx in nakshatras(c).items():
        if nakshatras(other)[k] != idx:
            st = u.nakshatras[k]
            assert st.label != "stable" and st.time < 1.0, (k, st)
    # Tiers likewise.
    for name, tier in _tiers(other).items():
        if tier != c.scored.areas[name].tier:
            st = c.scored.areas[name].stability
            assert st is not None and st.label != "stable", (name, st)
    # And the sampler is not vacuous: something in the window does move on these charts.
    assert any(s.time < 1.0 for v in u.placements.values() for s in v.values())


def test_one_arcsecond_of_ayanamsa_moves_positions_and_nothing_else(birth, monkeypatch):
    import swisseph as swe
    import jyotish.ephemeris as eph
    b, c = birth
    jd = c.meta.jd
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    shifted = swe.get_ayanamsa_ut(jd) + 1.0 / 3600.0

    class Shifted:                                  # Swiss Ephemeris with Lahiri + 1'' at the birth
        def __getattr__(self, name):
            return getattr(swe, name)

        @staticmethod
        def set_sid_mode(mode, t0=0, ayan_t0=0):
            swe.set_sid_mode(swe.SIDM_USER, jd, shifted)
    monkeypatch.setattr(eph, "swe", Shifted())
    try:
        d = compute(_utc(b), b["lat"], b["lon"], true_node=False)
    finally:
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    import math

    def near_edge(lon: float, parts: int) -> bool:         # within the 1'' shift of an edge of a 360/parts division
        x = lon * parts / 360.0
        return min(x - math.floor(x), math.ceil(x) - x) * (360.0 / parts) * 3600 <= 1.0 + 1e-9
    at_edge = []
    for p, body in c.bodies.items():
        delta = ((c.bodies[p].lon - d.bodies[p].lon + 180) % 360 - 180) * 3600
        assert delta == pytest.approx(1.0, abs=0.01), (p, delta)
        for what, parts, before, after in (("sign", 12, body.sign, d.bodies[p].sign), ("nakshatra", 27, body.nak, d.bodies[p].nak),
                                           ("pada", 108, body.pada, d.bodies[p].pada)):
            if before != after:                                   # only where the 1'' crosses an edge
                assert near_edge(body.lon, parts), (p, what, body.lon)
                at_edge.append((p, what))
    assert ((c.lagnas.asc - d.lagnas.asc) * 3600) == pytest.approx(1.0, abs=0.01)
    if near_edge(c.lagnas.asc, 108):
        at_edge.append(("Asc", "pada"))
    kp_moved = c.lagnas.cusp_lords_kp != d.lagnas.cusp_lords_kp          # a cusp within 1'' of a KP sub edge
    if not at_edge and not kp_moved:
        assert rule_keys(c) == rule_keys(d) and _tiers(c) == _tiers(d)
    else:                                                        # a fire or tier may follow the crossing
        print(f"edge crossed by the 1'' shift: {at_edge or 'a KP sub-lord'}; fires and tiers not compared")
    from jyotish.vargas import VARGAS
    lon = {p: x.lon for p, x in c.bodies.items()} | {"Asc": c.lagnas.asc}
    for (varga, body), sign in placements(c).items():
        if placements(d)[(varga, body)] != sign:          # only where the 1'' crosses an edge
            assert VARGAS[varga](lon[body] - 1.5 / 3600) != VARGAS[varga](lon[body] + 0.5 / 3600), (varga, body)
    for name, a in c.scored.areas.items():
        if a.score_classical is not None:
            assert d.scored.areas[name].score_classical == pytest.approx(a.score_classical, abs=1e-3)


def _classes(chart):
    u = chart.uncertainty
    out = {("rule",) + (f.id, f.basis, tuple(f.nodes)): f.stability.label for f in chart.fired_rules}
    out |= {("varga", v, b): s.label for v, xs in u.placements.items() for b, s in xs.items()}
    out |= {("tier", n): a.stability.label for n, a in chart.scored.areas.items() if a.stability is not None}
    return out


def test_another_sampler_seed_agrees_on_the_stability_classes(birth):
    b, c = birth
    other = assess(_utc(b), b["lat"], b["lon"], true_node=False, seed=1)
    x, y = _classes(c), _classes(other)
    common = set(x) & set(y)
    assert len(common) >= 0.95 * len(x)
    agree = sum(x[k] == y[k] for k in common) / len(common)
    assert agree >= 0.95, agree


def test_paraphrases_route_to_the_same_areas_tier_and_findings():
    from jyotish.narrate import findings, payload, route
    b = BIRTHS[0]
    c = assess(_utc(b), b["lat"], b["lon"], true_node=False, seed=0)
    routes = [route(q, c) for q in QUESTIONS]
    assert all(r == routes[0] for r in routes) and routes[0] == (["career"], True)
    tiers = {q: [c.scored.areas[a].tier for a in route(q, c)[0]] for q in QUESTIONS}
    assert len({tuple(v) for v in tiers.values()}) == 1
    offered = [{f["finding_id"] for a in route(q, c)[0] for f in findings(c, a, AS_OF)[0]} for q in QUESTIONS]
    assert all(o == offered[0] for o in offered) and len(offered[0]) > 10
    tags = [set(payload(c, q, route(q, c)[0], "curious", AS_OF)[1]) for q in QUESTIONS]
    assert all(t == tags[0] for t in tags)


# --- the narration side: live only ----------------------------------------------------------------

@pytest.fixture(scope="module")
def live_recording():
    calls: list = []
    yield calls
    if calls:
        (FIXTURES / "metamorphic_live.json").write_text(json.dumps(
            {"note": "Recorded by tests/test_metamorphic.py under JYOTISH_LIVE_NARRATION=1.", "calls": calls},
            indent=2, ensure_ascii=False, default=str) + "\n")


def _accepted(reading):
    return {(a.name, c.finding_id) for a in reading.areas for c in a.claims}


@pytest.mark.live
@pytest.mark.skipif(not LIVE, reason="set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API")
def test_live_a_reworded_question_gives_the_same_claim_set(live_recording):
    from jyotish.narrate import CONFIG, AnthropicChecker, AnthropicDrafter, narrate
    b = BIRTHS[0]
    c = assess(_utc(b), b["lat"], b["lon"], true_node=False, seed=0)
    sets = []
    for q in QUESTIONS[:2]:
        rec: list = []
        r = narrate(c, q, drafter=AnthropicDrafter(CONFIG), checker=AnthropicChecker(CONFIG), as_of=AS_OF,
                    recording=rec, depth="curious")
        live_recording.append({"test": "reworded", "question": q, "model": CONFIG.model,
                               "accepted": sorted(map(list, _accepted(r))), "calls": rec})
        sets.append(_accepted(r))
    assert sets[0] == sets[1], sets[0] ^ sets[1]


@pytest.mark.live
@pytest.mark.skipif(not LIVE, reason="set JYOTISH_LIVE_NARRATION=1 to call the Anthropic API")
def test_live_a_swapped_writer_model_gives_the_same_claim_set(live_recording):
    from dataclasses import replace
    from jyotish.narrate import CONFIG, AnthropicChecker, AnthropicDrafter, narrate
    b = BIRTHS[0]
    c = assess(_utc(b), b["lat"], b["lon"], true_node=False, seed=0)
    other = replace(CONFIG, model=os.environ.get("JYOTISH_SWAP_MODEL", "claude-sonnet-5-5"))
    sets = []
    for cfg in (CONFIG, other):
        rec: list = []
        r = narrate(c, QUESTIONS[0], drafter=AnthropicDrafter(cfg), checker=AnthropicChecker(CONFIG), as_of=AS_OF,
                    recording=rec, depth="curious")
        live_recording.append({"test": "writer swapped", "model": cfg.model, "accepted": sorted(map(list, _accepted(r))),
                               "calls": rec})
        sets.append(_accepted(r))
    assert sets[0] == sets[1], sets[0] ^ sets[1]
