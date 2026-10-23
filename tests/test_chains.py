"""Dispositor chains as findings (chains.py; SPEC Layer 2, dispositor analysis), on the reference
chart: the chains SPEC's worked example lists, the [chain:] tag's validator rule, the checker's
facts, the learner block, and a narrated chain claim on the page."""

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from jyotish.chains import DISPOSITOR, area_chain_findings, current_lords, main_karaka
from jyotish.narrate import (ReadingDraft, _check_data, findings, learner_data, narrate, offered_chains,
                             validate)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.scoring import AREAS
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def by_id(chart, area, as_of=AS_OF):
    return {f["finding_id"]: f for f in area_chain_findings(chart, area, as_of)}


def test_career_lord_chains_on_the_reference_chart(chart):
    f = by_id(chart, "career")["chain:career.lord"]
    assert f["planet"] == "Saturn" and f["role"] == "the lord of the 10th, the area's first house"
    d = f["derivation"]
    assert [s["planet"] for s in d["sign"]["steps"]] == ["Saturn", "Venus", "Jupiter"]
    assert d["sign"]["steps"][0] == {"planet": "Saturn", "sign": "Taurus", "house": 1, "dignity": "friend"}
    assert d["sign"]["ends_in"] == ["Jupiter", "Venus"] and not d["sign"]["in_loop"]
    # SPEC: Saturn -> Sun (Krittika) -> Jupiter (PurvaBhadra) -> Moon (Rohini) -> Mars (Chitra) -> Mercury (Jyestha).
    assert [s["planet"] for s in d["nakshatra"]["steps"]] == ["Saturn", "Sun", "Jupiter", "Moon", "Mars", "Mercury"]
    assert [s["nakshatra"] for s in d["nakshatra"]["steps"]][:2] == ["Krittika", "PurvaBhadra"]
    assert d["nakshatra"]["ends_in"] == ["Mars", "Mercury"]
    assert d["navamsa"]["steps"] == [{"planet": "Saturn", "navamsa_sign": "Capricorn", "house_from_d9_lagna": 12,
                                      "dignity": "own"}]
    assert d["navamsa"]["ends_in"] == ["Saturn"] and d["exchanges"] == []
    assert "Saturn is in no nakshatra loop; its final nakshatra dispositors are Mars and Mercury" in f["facts"]
    assert "Saturn is its own final navamsa dispositor" in f["facts"]
    # The navamsa step states Saturn's house from the D9 lagna, which is 0.78 stable on this chart
    # (SPEC: the navamsa boundary 1.4 minutes of clock away); every other link holds in every sample.
    assert f["allowed_tags"] == ["chain:career.lord"]
    assert f["stability"] == pytest.approx(chart.uncertainty.varga_stability["D9"]) and 0.7 < f["stability"] < 0.85


def test_loops_exchanges_and_activation(chart):
    p = by_id(chart, "personality")
    venus = p["chain:personality.lord"]
    assert venus["planet"] == "Venus" and venus["derivation"]["sign"]["in_loop"]
    assert venus["derivation"]["sign"]["loop_with"] == ["Jupiter"]
    sign_x = venus["derivation"]["exchanges"][0]
    assert sign_x == {"kind": "sign", "planets": ["Venus", "Jupiter"], "houses": [1, 11],
                      "class_by_houses": "maha", "class_by_lordship": "dainya"}
    # Jupiter-Mercury runs on 2026-10-21: Mercury's antar activates Venus (Revati is Mercury's).
    assert current_lords(chart, AS_OF) == [("mahadasha", "Jupiter"), ("antardasha", "Mercury")]
    assert venus["derivation"]["activation"] == [{"level": "antardasha", "lord": "Mercury",
                                                  "activated": ["Mercury", "Mars", "Venus"], "how": "in a nakshatra of Mercury"}]
    sun = by_id(chart, "career")["chain:career.karaka"]
    assert sun["planet"] == "Sun" and sun["derivation"]["activation"][0]["lord"] == "Jupiter"
    assert by_id(chart, "career")["chain:career.lord"]["derivation"]["activation"] == []
    # Without a reading date there is no activation in the finding at all.
    assert "activation" not in by_id(chart, "career", None)["chain:career.lord"]["derivation"]
    mars = by_id(chart, "marriage")["chain:marriage.lord"]
    assert mars["planet"] == "Mars" and mars["derivation"]["nakshatra"]["in_loop"]
    assert {x["kind"] for x in mars["derivation"]["exchanges"]} == {"nakshatra", "navamsa"}
    assert "Mars and Mercury are in mutual nakshatra exchange: each is in the other's nakshatra" in mars["facts"]


def test_the_charts_final_dispositors(chart):
    f = by_id(chart, "personality")["chain:personality.chart"]
    assert f["planets"] == ["Jupiter", "Mars", "Venus", "Mercury", "Rahu", "Saturn"]
    nak = f["derivation"]["nakshatra"]
    assert nak["final_dispositors"] == ["Mars", "Mercury", "Rahu"]
    assert nak["ends"][0] == {"loop": ["Mars", "Mercury"], "bodies": ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter",
                                                                     "Venus", "Saturn", "Ketu"]}
    assert nak["ends"][1] == {"loop": ["Rahu"], "bodies": ["Rahu"]}
    assert "Every body but Rahu ends in the Mars–Mercury nakshatra loop" in f["facts"]
    assert "Every body but Mars ends in the Jupiter–Venus sign loop" in f["facts"]
    # One name everywhere: the chart object's loop, the finding's and the chart page's read the loop
    # from the planet earliest in graha order.
    assert [l.planets for l in chart.features.dispositors.loops if len(l.planets) > 1] == [["Jupiter", "Venus"]]
    assert chart.features.dispositors.loops[0].houses == [1, 11]              # Jupiter in the 1st, Venus in the 11th
    assert {(x["kind"], tuple(x["planets"])) for x in f["derivation"]["exchanges"]} == {
        ("sign", ("Jupiter", "Venus")), ("nakshatra", ("Mars", "Mercury")), ("navamsa", ("Jupiter", "Mars"))}
    assert all("chain:personality.chart" not in [x["finding_id"] for x in area_chain_findings(chart, a)]
               for a in AREAS if a != "personality")


def test_a_chain_is_as_stable_as_its_nakshatra_links(chart):
    # Fifteen minutes after the reference birth the lagna is within the +-2-minute window of the
    # Krittika/Rohini edge: its nakshatra, the first link of the lagna's nakshatra chain, holds in a
    # share of the samples below 1, and the chart's chain finding is no more stable than that.
    from datetime import timedelta
    near = assess(REFERENCE_BIRTH_UTC + timedelta(minutes=15), REFERENCE_LAT, REFERENCE_LON, true_node=False)
    share = near.uncertainty.nakshatras["Asc"].time
    assert near.lagnas.asc_nak == "Rohini" and 0.5 < share < 1.0
    f = by_id(near, "personality")["chain:personality.chart"]
    assert f["stability"] <= share
    # Every stamped placement a finding's steps state bounds it: on the reference chart the Moon's
    # nakshatra (Chitra, 5 degrees from an edge) and sign hold in every sample.
    u = chart.uncertainty
    assert set(u.nakshatras) == set(chart.bodies) | {"Asc"} and u.nakshatras["Moon"].time == 1.0
    assert all(0.0 <= s.time <= 1.0 and s.label for s in u.nakshatras.values())


def test_a_karaka_that_is_the_lord_is_one_finding(chart):
    for area, spec in AREAS.items():
        ids = [f["finding_id"] for f in area_chain_findings(chart, area)]
        lord = by_id(chart, area)[f"chain:{area}.lord"]["planet"]
        assert (f"chain:{area}.karaka" in ids) == (main_karaka(chart, spec) not in (None, lord)), area


def test_chain_findings_in_the_reading_data(chart):
    ok, _ = findings(chart, "career", AS_OF)
    chain = [f for f in ok if f["kind"] == "chain"]
    assert [f["finding_id"] for f in chain] == ["chain:career.lord", "chain:career.karaka"]
    assert [f["kind"] for f in ok][-2:] == ["chain", "chain"]                       # after the rules and votes
    data = _check_data(chain[0])
    assert data["facts"] == chain[0]["facts"] and data["derivation"]["sign"]["steps"]
    assert {"dispositor", "final dispositor", "nakshatra lord"} <= set(chain[0]["glossary"])
    assert "activation" in by_id(chart, "personality")["chain:personality.lord"]["derivation"]
    assert "mutual exchange" in findings(chart, "marriage", AS_OF)[0][-1]["glossary"]
    d = learner_data(chain[0])
    assert d["kind"] == "chain" and d["what"] == DISPOSITOR and d["what"].startswith("A dispositor is the lord of the sign")
    assert offered_chains(chart, ["career"]) == {"career": {"career.lord": ["Saturn"], "career.karaka": ["Sun"]}}


def test_a_chain_sentence_names_the_planet_and_the_chain():
    chains = {"career.lord": ["Saturn"]}
    tags = {"chain:career.lord"}
    ok = "Saturn's nakshatra chain runs through the Sun, Jupiter and the Moon to the Mars–Mercury loop [chain:career.lord]."
    assert validate(ok, tags, chains=chains) == []
    no_planet = "Its nakshatra chain ends in the Mars–Mercury loop [chain:career.lord]."
    assert any("names none of ['Saturn']" in e for e in validate(no_planet, tags, chains=chains))
    no_kind = "Saturn's dispositors end in the Venus–Jupiter loop [chain:career.lord]."
    assert any("names no chain (sign, nakshatra or navamsa)" in e for e in validate(no_kind, tags, chains=chains))
    # "Nakshatra lord" is the chain's word here, not a mention of the panchanga family.
    lords = "Saturn's nakshatra lord is the Sun, whose own nakshatra lord is Jupiter [chain:career.lord]."
    assert validate(lords, tags, chains=chains, offered_votes={"panchanga": "vote:career.panchanga"}) == []
    plain = "The nakshatra lord of the birth star is Mars."
    assert any("panchanga" in e for e in validate(plain, set(), offered_votes={"panchanga": "vote:career.panchanga"}))


def test_a_narrated_chain_claim_reaches_the_page(chart, tmp_path):
    from jyotish.page import render
    from jyotish.narrate import CheckResult, Proposition
    edited = json.loads((FIXTURES / "narration_career_edited.json").read_text())
    draft = copy.deepcopy(edited["drafts"][-1])
    sentence = ("Saturn, lord of the 10th, has a nakshatra chain that runs through the Sun, Jupiter and the Moon "
                "to the Mars–Mercury loop [chain:career.lord].")
    for a in draft["areas"]:
        if a["name"] == "career":
            a["claims"].append({"finding_id": "chain:career.lord", "text": sentence})

    class Drafter:
        def __call__(self, system, user, errors):
            assert "chain:career.lord" in user and "A third kind is a dispositor chain" in system
            return ReadingDraft(**draft)

    seen = []

    def checker(s, data):
        seen.append((s, data))
        return CheckResult(propositions=[Proposition(text=s, supported=True, evidence="stub")])
    r = narrate(chart, edited["question"], drafter=Drafter(), checker=checker, as_of=AS_OF)
    career = next(a for a in r.areas if a.name == "career")
    claim = next(c for c in career.claims if c.finding_id == "chain:career.lord")
    assert claim.kind == "chain" and claim.confidence is None and claim.learner["kind"] == "chain"
    assert [c.kind for c in career.claims][-1] == "chain"                           # rules, votes, then chains
    data = next(d for s, d in seen if s == sentence)
    assert "Nakshatra chain of Saturn" in data and '"facts"' in data              # the checker reads the facts
    assert "chain:career.karaka" in [g["finding_id"] for g in career.narration_gaps]
    md = render(r, chart)
    assert "The dispositor chains of the career lord, traced by the engine" in md
    assert "Dispositor chains of Saturn (the lord of the 10th, the area's first house)" in md
    assert "- Nakshatra chain of Saturn: Saturn in Krittika (Taurus, the 1st, friend) → Sun in PurvaBhadra" in md
