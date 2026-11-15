"""The review of the layered answer (docs/review_2026-11-15_layered.md, H1-H5, M1-M11, L1-L7), fixed one commit per
finding; the heading "The review of the layered answer, fixed" of docs/spec_notes_2026-11-15.md. Each test fails on the
code the review read.

The property tests compose every area of random synthetic charts (scripts/synthetic_cohort.births: no one's data)
under three session keys, one per variant residue, so a fault that turns on the slot values (several planets, an
empty dignity, a node, an aspect) or on the variant is seen, not only the reference chart under one key."""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 15)
N_CHARTS = 40
KEYS = ("k0", "k1", "k2")


@pytest.fixture(scope="module")
def plans():
    """Every area's plan (no payload: the coverage tool's plans) of N_CHARTS random charts, and one weakest-areas plan."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from synthetic_cohort import births
    from jyotish.chart import compute
    from jyotish.plan import plan
    out = []
    for b in births(N_CHARTS, 7):
        c = compute(datetime.fromisoformat(f"{b['date']}T{b['time']}"), b["lat"], b["lon"], true_node=False)
        areas = [a for a in c.scored.areas if a != "synastry"]
        for a in areas:
            out.append((c, plan(c, "property", [a], "both", ["why"], as_of=AS_OF)))
        out.append((c, plan(c, "property", areas[:3], "against", [], as_of=AS_OF, weakest=True)))
    return out


@pytest.fixture(scope="module")
def composed(plans):
    """Every sentence the composer writes for those plans, under each key, draft meanings on."""
    from jyotish.bank import default_bank
    from jyotish.conversation import compose
    bank = default_bank()
    out = []
    for c, p in plans:
        for k in KEYS:
            for s in compose(p, bank, session_key=k, draft_meanings=True)["sentences"]:
                out.append((c, p, s))
    return out


# --- H1. A fact row says several planets sit in one sign when they do not ------------------------------------------

def test_h1_the_arudha_rows_over_several_signs_name_each_planet_with_its_own_sign(composed):
    seen = 0
    for c, p, s in composed:
        if s["row"] and s["signature"].startswith("family.arudha.") and ".many." in s["signature"]:
            seen += 1
            assert not re.search(r"in one of (?:these signs|them)|beside to help", s["text"]), s["text"]
            for planet in re.findall(r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b in (\w+)", s["text"]):
                assert c.bodies[planet[0]].sign_name == planet[1], s["text"]
    assert seen > 10


def test_h1_rahu_and_ketu_are_never_told_as_sharing_a_sign(composed):
    for c, p, s in composed:
        m = re.search(r"\b(?:Rahu|Ketu)\b.{0,40}\b(?:Rahu|Ketu)\b", s["text"])
        if m and s["row"]:
            assert not re.search(r"(?:sit|are) in one\b|together in|in (?:the same|one) sign", s["text"]), s["text"]


def test_h1_every_fact_variant_is_checked_on_each_shape_its_slots_take():
    """The recheck of 2026-11-15 (draft_bank.py --recheck): each fact row's checks carry the shape of the values they
    were filled with, and a row whose signature the random charts give several shapes was checked on more than one."""
    from jyotish.bank import load_bank
    # The .nohouse rule rows declare a slot no sample fills (M5): no shape can be had for them, and their checks stand.
    facts = [r for r in load_bank().rows if r.kind == "fact" and not r.signature.endswith(".nohouse")]
    assert all(c.shape is not None for r in facts for c in r.checks)
    assert all({c.variant for c in r.checks} == {0, 1, 2} for r in facts if r.checks)
    many = [r for r in facts if len({c.shape for c in r.checks}) > 1]
    assert len(many) >= 10, len(many)


def test_h1_a_shape_says_one_several_empty_and_a_node():
    from jyotish.bank import shape_of
    s = shape_of({"planets": "Ketu, Saturn and Rahu", "planet": "the Sun", "dignity": "", "house": "10th"})
    assert s == "dignity:empty,house:one,planet:one+lum,planets:many+node"


def test_h1_a_variant_refused_on_one_shape_is_never_shown_and_the_next_one_is(tmp_path):
    from jyotish.bank import BankRow
    row = BankRow(signature="family.kp.for", kind="fact", slots=["area"], drafted_by="t", drafted_on=AS_OF,
                  variants=["A {area}.", "B {area}.", "C {area}."],
                  checks=[{"variant": 1, "sentence": "B x.", "supported": False, "model": "m", "on": AS_OF, "shape": "a"},
                          {"variant": 1, "sentence": "B y.", "supported": True, "model": "m", "on": AS_OF, "shape": "b"}])
    assert row.refused() == {1}
    assert [row.usable(i) for i in range(3)] == [0, 2, 2]
    from jyotish.bank import Check
    row.checks += [Check(variant=v, sentence="x", supported=False, model="m", on=AS_OF) for v in (0, 2)]
    assert row.usable(0) is None


def test_h1_the_recheck_fills_each_shape_and_records_it(monkeypatch):
    """draft_bank.check_rows: each variant of a row is filled with every sample shape whose slots it can take and
    checked against that sample's facts; no model is called here (a stub checker)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("draft_bank", ROOT / "scripts" / "draft_bank.py")
    db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db)
    from jyotish.bank import BankRow
    from jyotish.narrate import CheckResult, Proposition
    row = BankRow(signature="family.panchanga.for.one", kind="fact", slots=["area", "planets"], drafted_by="t",
                  drafted_on=AS_OF, variants=["{planets} leans favourably for {area}.", "For {area}, {planets} leans.",
                                              "{planets} sits apart for {area}."])
    samples = [{"slots": {"area": "your career", "planets": "Mars"}, "facts": {}, "engine": "e"},
               {"slots": {"area": "your career", "planets": "the Sun and Rahu"}, "facts": {}, "engine": "e"},
               {"slots": {"area": "your career"}, "facts": {}, "engine": "e"}]                    # no planets: not used
    found = {(row.signature, "fact"): samples[0] | {"shapes": samples}}

    class Stub:
        def check_many(self, asks):
            return [(CheckResult(propositions=[Proposition(text=s, supported="apart" not in s, evidence="")]), {})
                    for s, _ in asks]
    rows, bad = db.check_rows({(row.signature, "fact"): row}, found, Stub(), "stub", {})
    assert len(row.checks) == 6 and {c.shape for c in row.checks} == {"area:one,planets:one", "area:one,planets:many+node+lum"}
    assert "the Sun and Rahu lean favourably for your career." in [c.sentence for c in row.checks]   # agreement
    assert row.refused() == {2} and list(bad) == [row.signature]
