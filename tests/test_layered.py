"""The layered answer (SPEC Layer 8 rev 134, "The layered answer"; docs/spec_notes_2026-11-15.md): the answer plan,
the sentence bank, the composer, the polisher, the worksheet and the stored answer, each step's tests, on the
reference chart first."""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import plan_turn, route_turn
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 15)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def data(chart):
    from jyotish.fullchart import cached_payload
    from jyotish.narrate import full_range
    return cached_payload(chart, AS_OF, *full_range(AS_OF), [a for a in chart.scored.areas if a != "synastry"])


@pytest.fixture(scope="module")
def charts(chart):
    out = {"reference": chart}
    for b in BIRTHS:
        if b["name"] != "reference":
            out[b["name"]] = assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)
    return out


def career(chart, data=None, message="how is my career"):
    return plan_turn(chart, message, route_turn(message, chart), as_of=AS_OF, data=data)


# --- 1. The answer plan ------------------------------------------------------------------------------------------------

def test_1_the_career_plan_holds_the_yogas_with_their_reductions_and_saturns_hidden_weakness(chart, data):
    """The sample worksheet of 2026-11-15 (career, the reference chart): three fired yogas never reached the client,
    and the tenth lord's marana karaka sthana was told as "a friendly sign"."""
    p = career(chart, data)
    sig = p.signatures()
    assert "rule.yoga.budhaditya.reduced" in sig                   # Mercury in a feeble state (bala/mrita) reduces it
    assert "rule.yoga.kendra_trikona_raja.full" in sig
    ruchaka = next(i for i in p.items if i.signature.startswith("rule.yoga.ruchaka"))
    assert ruchaka.signature == "rule.yoga.ruchaka.reduced"
    assert ruchaka.slots["reductions"] == ("Saturn's aspect on it, an unhelpful star counted from your Moon and a "
                                           "house that drains it")
    mks = next(i for i in p.items if i.signature == "weakness.mks")
    assert mks.facts["planet"] == "Saturn" and mks.facts["house"] == 1 and mks.slots["role"] == "the ruler of your 10th house"
    assert "drains" in mks.engine and "friendly" not in mks.engine
    assert {i.signature for i in p.items if i.facts.get("planet") == "Saturn"} == {
        "weakness.mks", "weakness.mrita", "weakness.low_strength"}     # ratio 0.69, Mrita, 1st house


def test_1_the_plan_is_in_order_helps_by_the_strongest_terms_and_says_what_it_left_out(chart, data):
    p = career(chart, data)
    order = [i.part for i in p.items]
    from jyotish.plan import PARTS
    assert order == sorted(order, key=PARTS.index)
    helps = [i for i in p.items if i.part == "helps"]
    terms = chart.scored.areas["career"].terms
    assert 2 <= len(helps) <= 3 and [i.facts["strength"] for i in helps] == sorted((i.facts["strength"] for i in helps), reverse=True)
    assert min(i.facts["term"] for i in helps) >= max(terms[f] for f in ("varga", "panchanga"))
    left = {x["what"]: x["why"] for x in p.left_out}
    assert left["vote:career.varga"].startswith("a weaker term") and left["vote:career.kp"] == "abstains"
    assert left["place.sun_h10@lagna"].startswith("a draft placement")
    assert left["chain:career.lord"].startswith("a chain")
    assert p.items[-1].signature == "period.now.touches" and p.items[-1].slots["maha"] == "Jupiter"


def test_1_a_when_turn_ends_with_the_stretches_and_the_plan_is_the_same_without_the_payload(chart, data):
    m = "when will my career rise"
    p = plan_turn(chart, m, route_turn(m, chart), as_of=AS_OF, data=data)
    assert p.signatures()[-3:] == ["stretch.most.first", "stretch.least.second", "stretch.caveat.two"]
    assert p.items[-1].engine == "Neither stretch is a prediction of when you will act."
    assert "opening.when" in p.signatures()
    # The chart object alone gives the same items (the coverage tool's path), without notes or stretch texts.
    assert career(chart).signatures() == career(chart, data).signatures()
    assert [i.engine for i in career(chart).items] == [i.engine for i in career(chart, data).items]


def test_1_hard_findings_come_by_the_most_negative_term(charts, data):
    found = 0
    for name, c in charts.items():
        for area in c.scored.areas:
            if area == "synastry" or c.scored.areas[area].score_classical is None:
                continue
            p = plan_turn(c, "tell me", route_turn(f"how is my {area.replace('_', ' ')}", c).model_copy(
                update={"areas": [area]}), as_of=AS_OF)
            hard = [i for i in p.items if i.part == "hard"]
            assert len(hard) <= 2 and len([i for i in p.items if i.part == "helps"]) <= 3
            assert [i.facts["strength"] for i in hard] == sorted(i.facts["strength"] for i in hard)
            found += len(hard)
    assert found


def test_1_every_engine_sentence_of_a_plan_passes_the_never_show_list(charts):
    """An item with no bank row falls back to its engine sentence (step 4): every one is in the client's words."""
    from jyotish.client import never_show
    for name, c in charts.items():
        areas = [a for a in c.scored.areas if a != "synastry"]
        p = plan_turn(c, "how much will i earn", route_turn("how is my career", c).model_copy(update={"areas": areas}),
                      as_of=AS_OF)
        for i in p.items:
            assert never_show(i.engine) == [], (name, i.signature, i.engine)


def test_1_a_reduction_with_no_plain_words_keeps_the_rule_out_and_says_so():
    from jyotish.plan import reductions_plain
    assert reductions_plain(["marana_karaka_sthana -> x0.6", "aspected_by: [Saturn] -> x0.8"]) == (
        ["a house that drains it", "Saturn's aspect on it"], [])
    assert reductions_plain(["kp_sub_lord in [6, 8] -> x0.7"]) == ([], ["kp_sub_lord in [6, 8]"])
    assert reductions_plain(["dignity: friend -> x1.1"]) == ([], [])          # a boost is not a reduction


# --- 2. The sentence bank ----------------------------------------------------------------------------------------------

def row(**kw):
    base = {"signature": "family.lord.for", "kind": "fact", "slots": ["area", "planet", "ruled_house", "sign", "house", "dignity"],
            "variants": ["{planet}, which rules your {ruled_house} house, sits in {sign} in your {house} house, {dignity}, "
                         "and supports {area}.",
                         "The ruler of your {ruled_house} house, {planet}, is in {sign} in your {house} house, {dignity}; "
                         "it supports {area}.",
                         "Supporting {area}: {planet}, ruler of the {ruled_house} house, placed in {sign} in your "
                         "{house} house, {dignity}."],
            "drafted_by": "test", "drafted_on": "2026-11-15", "status": "draft"}
    return base | kw


def write_bank(tmp_path, rows, name="family.yaml"):
    import shutil
    import yaml
    d = tmp_path / "bank"
    d.mkdir(exist_ok=True)
    shutil.copy(ROOT / "data" / "bank" / "bank.schema.json", d)
    (d / name).write_text(yaml.safe_dump(rows, sort_keys=False))
    return d


def test_2_a_good_row_loads_and_fills_with_the_charts_values(tmp_path):
    from jyotish.bank import load_bank
    bank = load_bank(write_bank(tmp_path, [row()]))
    r = bank.fact("family.lord.for")
    assert len(bank) == 1 and r.status == "draft" and len(bank.version) == 12
    slots = {"area": "your career", "planet": "Saturn", "ruled_house": "10th", "sign": "Taurus", "house": "1st",
             "dignity": "in a friendly sign"}
    assert r.fill(0, slots) == ("Saturn, which rules your 10th house, sits in Taurus in your 1st house, in a friendly "
                                "sign, and supports your career.")
    assert r.fill(1, slots | {"dignity": ""}) == ("The ruler of your 10th house, Saturn, is in Taurus in your 1st "
                                                  "house; it supports your career.")


@pytest.mark.parametrize("bad,why", [
    (row(variants=["{planet} sits in {nakshatra}.", "a.", "b."]), "does not declare"),
    (row(variants=["The vote of {planet} supports {area}.", "a.", "b."]), "never shown to the client ('vote')"),
    (row(variants=["{planet} is a strong support for {area}.", "a.", "b."]), "tier word"),
    (row(variants=["The KP reading favours {area}.", "a.", "b."]), "never shown"),
    (row(signature="rule.yoga.ruchaka.full@career", kind="meaning", slots=[], variants=["a.", "b.", "c."]),
     "carries its source"),
    (row(signature="rule.yoga.ruchaka.full", kind="meaning", source="BPHS 75.1", slots=[], variants=["a.", "b.", "c."]),
     "names its area"),
    (row(signature="family.lord.for@career"), "only a meaning row names one"),
    (row(status="approved"), "names who approved it"),
    (row(variants=["{planet sits.", "a.", "b."]), "broken slot"),
])
def test_2_a_row_that_cannot_stand_is_a_load_error_with_its_reason(tmp_path, bad, why):
    from jyotish.bank import BankError, load_bank
    with pytest.raises(BankError, match=why.replace("(", r"\(").replace(")", r"\)")):
        load_bank(write_bank(tmp_path, [bad]))
    assert len(load_bank(write_bank(tmp_path, [bad, row(signature="family.karaka.for", slots=["area"],
                                                         variants=["It supports {area}.", "b.", "c."])]),
                         strict=False)) == 1


def test_2_the_schema_refuses_two_variants_and_a_second_row_is_refused(tmp_path):
    from jyotish.bank import BankError, load_bank
    with pytest.raises(BankError, match="too short|should be non-empty|at least"):
        load_bank(write_bank(tmp_path, [row(variants=["a.", "b."])]))
    with pytest.raises(BankError, match="a second fact row"):
        load_bank(write_bank(tmp_path, [row(), row()]))


def test_2_the_committed_bank_loads_with_every_row_standing():
    from jyotish.bank import load_bank
    bank = load_bank()
    assert all(r.kind == "fact" or r.source for r in bank.rows)


def test_2_coverage_counts_the_plan_items_that_find_a_row_whose_slots_they_fill(tmp_path):
    from jyotish.bank import coverage, load_bank
    empty = coverage(6, seed=3, bank=load_bank(write_bank(tmp_path, [])), workers=1)
    assert empty["items"] > 100 and empty["share"] == 0 and empty["missing"]
    lord = row()
    narrow = row(signature="family.karaka.for", slots=["area", "nakshatra"],
                 variants=["It supports {area} from {nakshatra}.", "It is good for {area}.", "{area} gains from it."])
    res = coverage(6, seed=3, bank=load_bank(write_bank(tmp_path, [lord, narrow])), workers=1)
    missing = dict(res["missing"])
    assert "family.lord.for" not in missing and "family.karaka.for" in missing    # a slot the plan does not fill
    assert 0 < res["by_part"]["helps"] < 1 and res["rows"] == 2 and res["approved_share"] == 0


# --- 3. The drafted bank -----------------------------------------------------------------------------------------------

def load_script(name):
    import importlib.util
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_3_the_drafted_rows_are_drafts_from_sonnet_and_every_fact_variant_was_checked_and_supported():
    from jyotish.bank import load_bank
    bank = load_bank()
    assert len(bank) > 60
    # Drafted by Sonnet; rows rewritten after the review of 2026-11-15 name the model that rewrote them and why.
    assert all(r.status == "draft" and (r.drafted_by == "claude-sonnet-5-5" or "review" in r.drafted_by)
               for r in bank.rows)
    facts = [r for r in bank.rows if r.kind == "fact"]
    # Every fact variant was checked (on each slot shape since the review's H1); a variant refused on a shape is
    # never shown, and every fact row keeps at least one variant no check refused.
    assert all({c.variant for c in r.checks} == {0, 1, 2} and len(r.refused()) < 3 for r in facts)
    assert all(c.model == "zai-org/GLM-5.3-Flash" for r in facts for c in r.checks)
    meanings = [r for r in bank.rows if r.kind == "meaning"]
    assert meanings and all(r.area in ("career", "marriage", "wealth") and r.source for r in meanings)
    assert all(r.source.startswith(("BPHS", "Phaladeepika", "Marana", "Baladi", "Shadbala", "Saravali", "Jataka",
                                    "Brihat")) for r in meanings), {r.source for r in meanings}
    # The openings, the periods and the stretches were drafted with the three areas (the request of 2026-11-15).
    sigs = {r.signature for r in facts}
    assert {"opening.amount", "opening.when"} <= sigs and any(s.startswith("period.now") for s in sigs)
    assert any(s.startswith("stretch.") for s in sigs)


def test_3_the_drafting_script_prices_first_and_stops_above_its_budget(monkeypatch, capsys):
    db = load_script("draft_bank")
    found = db._signatures(4, 1)
    kinds = {k[1] for k in found}
    assert kinds == {"fact", "meaning"} and all(k[0].split("@")[1] in db.AREAS for k in found if k[1] == "meaning")
    usd, parts = db.estimate(found)
    assert usd > 0 and parts["rows"] == len(found)
    import jyotish.envfile
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(db, "_signatures", lambda n, s: found)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-key")
    monkeypatch.setattr(db, "draft", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no model call")))
    assert db.main(["--budget", "0.0001", "--redraft"]) == 2
    out = capsys.readouterr().out
    assert "over the budget" in out and "not-a-key" not in out


def test_3_a_fact_variant_is_checked_against_its_facts_its_area_and_the_glossary(chart, data):
    db = load_script("draft_bank")
    item = next(i for i in career(chart, data).items if i.signature == "family.lord.for")
    d = db.check_data({"facts": item.facts, "engine": item.engine, "slots": item.slots})
    assert d["facts"]["about"]["main_house"] == 10 and d["facts"]["about"]["main_house_lord"] == "Saturn"
    assert "the engine's own sentence (the row says this, in other words)" in d and "friend" in d["the engine's plain words for a dignity"]


# --- 4. The composer ---------------------------------------------------------------------------------------------------

def ruchaka_rows():
    fact = row(signature="rule.yoga.ruchaka.reduced", slots=["area", "name", "placed", "reductions"],
               variants=["{name}, a combination of Mars, is in your chart: {placed}, weakened by {reductions} for {area}.",
                         "Your chart holds {name} (a combination of Mars), with {placed}, though {reductions} weaken it "
                         "for {area}.",
                         "{placed} forms {name}, a combination of Mars, weakened by {reductions} for {area}."])
    meaning = row(signature="rule.yoga.ruchaka.reduced@career", kind="meaning", slots=["area"], source="BPHS 75.1-2",
                  variants=["Ruchaka, a combination of Mars, is traditionally read as courage in {area}, here less so.",
                            "Texts link Ruchaka, Mars's combination, with drive in {area}; reduced here.",
                            "Ruchaka, a combination of Mars, is said to lend {area} vigour, held back here."])
    return [fact, meaning]


def test_4_the_composer_fills_the_plan_from_the_bank_and_falls_back_to_the_engines_sentence(chart, data, tmp_path):
    from jyotish.bank import load_bank
    from jyotish.conversation import compose, variant_of
    bank = load_bank(write_bank(tmp_path, ruchaka_rows()))
    p = career(chart, data)
    c = compose(p, bank, session_key="s1", draft_meanings=False)
    by = {s["signature"]: s for s in c["sentences"]}
    r = by["rule.yoga.ruchaka.reduced"]
    v = variant_of("s1", "rule.yoga.ruchaka.reduced")
    assert r["row"] == {"signature": "rule.yoga.ruchaka.reduced", "kind": "fact", "variant": v, "status": "draft",
                        "file": "family.yaml"}
    assert "Mars in your 7th house" in r["text"] and "a house that drains it" in r["text"]
    assert r["tagged"].endswith("[rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2] "
                                "[text:Phaladeepika/Sastri-1937/6/1].")
    # No row: the engine's sentence. A draft meaning is not shown unless JYOTISH_SHOW_DRAFT_MEANINGS is on.
    assert by["weakness.mks"]["row"] is None and by["weakness.mks"]["text"] == next(
        i.engine for i in p.items if i.signature == "weakness.mks")
    assert not [s for s in c["sentences"] if (s["row"] or {}).get("kind") == "meaning"]
    shown = compose(p, bank, session_key="s1", draft_meanings=True)
    meant = [s for s in shown["sentences"] if (s["row"] or {}).get("kind") == "meaning"]
    assert [s["signature"] for s in meant] == ["rule.yoga.ruchaka.reduced"] and "Ruchaka" in meant[0]["text"]
    i = [s["signature"] for s in shown["sentences"]].index("rule.yoga.ruchaka.reduced")
    assert shown["sentences"][i + 1] is meant[0]                     # the meaning follows its fact
    assert c["from_bank"] == 1 and c["from_engine"] == len(c["sentences"]) - 1


def test_4_the_variant_is_a_hash_of_the_session_stable_across_turns(chart, data, tmp_path):
    from jyotish.bank import load_bank
    from jyotish.conversation import compose, variant_of
    bank = load_bank(write_bank(tmp_path, ruchaka_rows()))
    p = career(chart, data)
    texts = lambda key: [s["text"] for s in compose(p, bank, session_key=key)["sentences"]]
    assert texts("a") == texts("a")
    keys = [f"s{n}" for n in range(12)]
    assert len({variant_of(k, "rule.yoga.ruchaka.reduced") for k in keys}) == 3
    assert len({tuple(texts(k)) for k in keys}) == 3


def test_4_a_row_refused_by_the_checker_or_wanting_a_slot_is_not_used(chart, data, tmp_path):
    from jyotish.bank import load_bank
    from jyotish.conversation import compose
    fact, _ = ruchaka_rows()
    refused = fact | {"checks": [{"variant": 0, "sentence": "x", "supported": False, "evidence": "no", "model": "m",
                                  "on": "2026-11-15"}]}
    # All three variants refused, or a slot the item does not fill: the engine's sentence. One refused variant: the
    # next variant is shown in its place (the review of 2026-11-15, H1).
    every = fact | {"checks": [refused["checks"][0] | {"variant": v} for v in range(3)]}
    wants = fact | {"slots": fact["slots"] + ["nakshatra"],                    # a slot the item does not fill
                    "variants": [v.replace("{placed}", "{placed} in {nakshatra}") for v in fact["variants"]]}
    for bad in (every, wants):
        c = compose(career(chart, data), load_bank(write_bank(tmp_path, [bad])), session_key="s1")
        assert next(s for s in c["sentences"] if s["signature"] == "rule.yoga.ruchaka.reduced")["row"] is None
    from jyotish.conversation import variant_of
    key = next(k for k in ("s0", "s1", "s2", "s3", "s4", "s5") if variant_of(k, fact["signature"]) == 0)
    c = compose(career(chart, data), load_bank(write_bank(tmp_path, [refused])), session_key=key)
    assert next(s for s in c["sentences"] if s["signature"] == "rule.yoga.ruchaka.reduced")["row"]["variant"] == 1


def test_4_paragraphs_are_the_answer_what_helps_what_is_hard_then_the_timing(chart, data):
    from jyotish.conversation import PARAGRAPHS, compose
    m = "when will my career rise"
    c = compose(plan_turn(chart, m, route_turn(m, chart), as_of=AS_OF, data=data), session_key="s")
    parts = [s["part"] for s in c["sentences"]]
    groups = [next(k for k, v in PARAGRAPHS.items() if p in v) for p in parts]
    starts = [i for i in range(len(groups)) if i == 0 or groups[i] != groups[i - 1]]
    assert c["paragraphs"] == starts and [groups[i] for i in starts] == ["answer", "helps", "hard", "timing"]
    assert parts[-1] == "stretch" and c["sentences"][-1]["signature"] == "stretch.caveat.two"
    against = compose(plan_turn(chart, "what is hard in my career", route_turn("what is hard in my career", chart),
                                as_of=AS_OF, data=data))
    order = list(dict.fromkeys(next(k for k, v in PARAGRAPHS.items() if s["part"] in v) for s in against["sentences"]))
    assert order.index("hard") < order.index("helps")


def test_4_answer_turn_composes_by_default_and_keeps_the_writer_for_an_unplaced_question(chart, monkeypatch):
    from jyotish.conversation import OfflineTurnWriter, answer_turn
    monkeypatch.delenv("JYOTISH_LAYERED", raising=False)
    calls = []

    class Writer(OfflineTurnWriter):
        def __call__(self, *a):
            calls.append(1)
            return super().__call__(*a)

    def passes(s, d):
        from jyotish.narrate import CheckResult, Proposition
        return CheckResult(propositions=[Proposition(text=s, supported=True, evidence="stub")])
    m = "how is my career"
    doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, drafter=Writer(), checker=passes, session_key="s")
    assert doc["source"] == "composer" and not calls and doc["plan"]["areas"] == ["career"]
    assert doc["usage"] == {"wall_seconds": doc["timeline"]["done"]} and doc["removed"] == []
    unplaced = route_turn("tell me something", chart)
    assert unplaced.areas_from == "top"
    doc = answer_turn(chart, "tell me something", unplaced, as_of=AS_OF, drafter=Writer(), checker=passes)
    assert doc["source"] in ("writer", "engine") and calls
    monkeypatch.setenv("JYOTISH_LAYERED", "0")
    assert answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, drafter=Writer(), checker=passes)["source"] != "composer"


def test_4_a_follow_up_repeats_nothing_and_a_why_with_nothing_new_says_so(chart, data):
    from jyotish.conversation import compose
    from jyotish.narrate import OPENING_SAID
    m = "how much money will i earn in my life, will i be rich"
    first = compose(plan_turn(chart, m, route_turn(m, chart), as_of=AS_OF, data=data), session_key="s")
    said = [" ".join(s["text"] for s in first["sentences"])]
    last = route_turn(m, chart)
    r = route_turn("whan and how", chart, last)
    again = compose(plan_turn(chart, "whan and how", r, as_of=AS_OF, data=data), session_key="s", said_before=said)
    texts = [s["text"] for s in again["sentences"]]
    assert again["sentences"][-1]["signature"] == "stretch.caveat.two"
    assert not set(texts) & {s["text"] for s in first["sentences"]} - {texts[-1]}
    assert OPENING_SAID in texts


SEVEN = ["what are the challanges in my life", "and marriage?", "when?", "why do you say that?", "will I die early?",
         "how much money will i earn in my life, will i be rich", "whan and how"]
FROZEN = ROOT / "tests" / "fixtures" / "layered_seven_turns.json"


def seven_turns(chart, monkeypatch, **kw):
    """The seven-turn conversation of tests/test_conversation.py, composed (session key "seven"), each turn given the
    earlier turns as the client read them."""
    from jyotish.conversation import answer_turn
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    out, last, history = [], None, []
    for m in SEVEN:
        route = route_turn(m, chart, last)
        doc = answer_turn(chart, m, route, as_of=date(2026, 10, 21), history=list(history), session_key="seven", **kw)
        out.append(doc)
        history.append({"question": m, "answer": " ".join(doc["shown"])})
        if not route.off_limits:
            last = route
    return out


def test_4_the_seven_turns_composed_are_frozen(chart, monkeypatch):
    """The composed answers of the seven turns on the reference chart with the committed bank (its version is in the
    file), once with every row's variant 1, 2 and 3 (review M10: one session key froze one variant per row, and a
    fault in the other two never showed): a change to the plan, the bank or the composer shows here.
    JYOTISH_RECORD_FIXTURE=1 writes them anew; a change is read, not only recorded."""
    import os
    import jyotish.conversation as conv
    from jyotish.bank import default_bank
    from jyotish.client import never_show
    got = {"bank": default_bank().version, "variants": {}}
    for v in range(3):
        monkeypatch.setattr(conv, "variant_of", lambda key, signature, v=v: v)
        docs = seven_turns(chart, monkeypatch)
        got["variants"][str(v)] = [{"question": m, "source": d["source"], "shown": d["shown"],
                                    "paragraphs": d["paragraphs"]} for m, d in zip(SEVEN, docs)]
        assert [d["source"] for d in docs] == ["composer"] * 4 + ["fixed"] + ["composer"] * 2
        assert not [s for d in docs for s in d["shown"] if never_show(s) or "{" in s or "}" in s]
    if os.environ.get("JYOTISH_RECORD_FIXTURE"):
        FROZEN.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n")
    assert got == json.loads(FROZEN.read_text())


# --- 5. The polisher ---------------------------------------------------------------------------------------------------

class StubPolisher:
    """Haiku's place: returns `make(composed)` as the polished text, recording each request."""
    model = "claude-haiku-5-5"

    def __init__(self, make):
        self.make, self.calls = make, []

    def describe(self):
        return {"provider": "anthropic", "host": "api.anthropic.com", "model": self.model}

    def structured(self, *, system, messages, schema, kind, effort, thinking, max_tokens, on_text=None):
        from jyotish.narrate import Completion
        self.calls.append({"system": system, "messages": messages, "kind": kind, "effort": effort})
        usage = {"input_tokens": 300, "output_tokens": 200, "cache_read_input_tokens": 800,
                 "cache_creation_input_tokens": 0}
        return Completion(parsed=schema(text=self.make(messages[0]["content"])), assistant={}, stop_reason="end_turn",
                          meta={"kind": kind, "usage": usage, "backend": self.describe()})


class StubChecker:
    def __init__(self, ok=True):
        self.ok, self.asked = ok, []
        self.backend = type("B", (), {"describe": lambda self: {"provider": "openai", "host": "api.deepinfra.com",
                                                                 "model": "zai-org/GLM-5.3-Flash"}})()

    def ask_one(self, sentence, data):
        from jyotish.narrate import CheckResult, Proposition
        self.asked.append((sentence, data))
        return CheckResult(propositions=[Proposition(text=sentence[:40], supported=self.ok, evidence="stub")]), \
            {"kind": "checker", "usage": {"input_tokens": 1000, "output_tokens": 400}}


def joined(text):
    """A polish that joins each paragraph's first two sentences with a semicolon: states nothing new."""
    import re
    out = []
    for para in text.split("\n\n"):
        out.append(re.sub(r"^([^.]+)\. ([A-Z])", lambda m: m.group(1) + "; " + m.group(2).lower(), para, count=1))
    return "\n\n".join(out)


def test_5_the_polisher_is_off_by_default_and_used_only_when_the_checker_finds_every_proposition(chart, monkeypatch):
    from jyotish.conversation import answer_turn
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    m = "how is my career"
    plain = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="s")
    assert plain["source"] == "composer" and "polish" not in plain
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    pol, chk = StubPolisher(joined), StubChecker(ok=True)
    doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="s", polisher=pol, checker=chk)
    assert doc["source"] == "polished" and doc["polish"]["used"] and doc["shown"] != plain["shown"]
    assert len(doc["shown"]) < len(plain["shown"]) and doc["paragraphs"][0] == 0
    # The stable prefix is cached; the composed answer follows in the message.
    sys_block = pol.calls[0]["system"][0]
    assert sys_block["cache_control"] == {"type": "ephemeral"} and pol.calls[0]["effort"] == "low"
    assert pol.calls[0]["messages"][0]["content"] == doc["polish"]["composed"]
    # Asked both ways (review M1): the polished text against the composed, and the composed against the polished.
    assert len(chk.asked) == 2 and doc["polish"]["composed"] in json.loads(chk.asked[0][1]).values()
    assert chk.asked[1][0] == doc["polish"]["composed"]
    # Refused by the checker: the composed text is shown, and both calls are still recorded and priced.
    bad = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="s", polisher=StubPolisher(joined),
                      checker=StubChecker(ok=False))
    assert bad["source"] == "composer" and bad["shown"] == plain["shown"] and not bad["polish"]["used"]
    assert bad["polish"]["refusals"][0].startswith("not in the composed text")
    assert bad["usage"]["polisher"]["cache_read_input_tokens"] == 800 and bad["usage"]["checker"]["calls"] == 2


def test_5_a_polished_text_with_an_engine_word_or_markdown_is_refused_before_the_checker(chart, monkeypatch):
    from jyotish.conversation import answer_turn
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    m = "how is my career"
    for make, why in ((lambda t: "The vote is for your career.", "never shown"),
                      (lambda t: "Your career is strong.", "tier word")):
        chk = StubChecker()
        doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, polisher=StubPolisher(make), checker=chk)
        assert doc["source"] == "composer" and not chk.asked and any(why in r for r in doc["polish"]["refusals"])
    # Markdown and HTML are taken off before anything is checked (conversation.unbullet): never shown as marks.
    doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, checker=StubChecker(),
                      polisher=StubPolisher(lambda t: "**" + joined(t).replace(" leans ", " <b>leans</b> ", 1)))
    assert doc["source"] == "polished" and not [x for x in doc["shown"] if re.search(r"[*<>]", x)]


def test_5_the_polisher_and_its_cache_tokens_are_priced(chart, monkeypatch):
    from jyotish.conversation import answer_turn
    from jyotish.costs import cost, reading_cost
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    m = "how is my career"
    doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, polisher=StubPolisher(joined), checker=StubChecker())
    v = reading_cost(doc)
    haiku = cost("claude-haiku-5-5", {"input_tokens": 300, "output_tokens": 200, "cache_read_input_tokens": 800})
    glm = cost("zai-org/GLM-5.3-Flash", {"input_tokens": 1000, "output_tokens": 400}, "api.deepinfra.com")
    assert haiku == pytest.approx((300 * 0.10 + 200 * 0.50 + 800 * 0.01) / 1e6)     # cache reads at 0.1 x input
    assert v["cost_usd"] == pytest.approx(haiku + 2 * glm, abs=1e-6)               # the check both ways (M1)
    assert v["backends"]["polisher"]["model"] == "claude-haiku-5-5"
    monkeypatch.delenv("JYOTISH_POLISH")
    assert reading_cost(answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF))["cost_usd"] == 0


# --- 6. The worksheet ----------------------------------------------------------------------------------------------------

AUTH = {"Authorization": "Bearer tok-ws"}
BIRTH = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
         "node": "mean", "place": "Rewari, Haryana"}


@pytest.fixture(scope="module")
def ws_bank(tmp_path_factory):
    import shutil
    import yaml
    d = tmp_path_factory.mktemp("ws-bank")
    shutil.copy(ROOT / "data" / "bank" / "bank.schema.json", d)
    (d / "rules.yaml").write_text("# the test bank\n" + yaml.safe_dump(ruchaka_rows(), sort_keys=False))
    return d


@pytest.fixture(scope="module")
def ws_app(tmp_path_factory, ws_bank):
    from jyotish.api import create_app
    from jyotish.conversation import OfflineTurnWriter
    mp = pytest.MonkeyPatch()
    mp.setenv("JYOTISH_LAYERED", "1")
    import jyotish.bank
    mp.setattr(jyotish.bank, "BANK_DIR", ws_bank)
    db = tmp_path_factory.mktemp("ws") / "jyotish.db"

    def passes(s, d):
        from jyotish.narrate import CheckResult, Proposition
        return CheckResult(propositions=[Proposition(text=s, supported=True, evidence="stub")])
    app = create_app(f"sqlite:///{db}", turn_writer=OfflineTurnWriter, turn_checker=lambda: passes,
                     reviewers={"tok-judge": "judge-1"}, astrologers={"tok-ws": "astrologer-1"},
                     review_checker=passes, today=lambda: AS_OF)
    yield app, f"sqlite:///{db}"
    mp.undo()


@pytest.fixture(scope="module")
def ws_client(ws_app):
    from fastapi.testclient import TestClient
    import time
    app, _ = ws_app
    with TestClient(app) as c:
        sid = c.post("/sessions", json=BIRTH).json()["id"]
        for m in ("how is my career", "will I die early?"):
            n = c.post(f"/sessions/{sid}/turns", json={"message": m}).json()["n"]
            t = time.monotonic()
            while c.get(f"/sessions/{sid}/turns/{n}").json()["status"] not in ("done", "failed"):
                assert time.monotonic() - t < 90
                time.sleep(0.05)
        yield c, sid


def test_6_the_worksheet_shows_per_sentence_what_was_looked_at_derived_told_and_the_row(ws_client):
    c, sid = ws_client
    assert c.get(f"/sessions/{sid}/turns/1/worksheet").status_code == 401
    ws = c.get(f"/sessions/{sid}/turns/1/worksheet", headers=AUTH).json()
    assert ws["source"] == "composer" and ws["n"] == 1
    told = [s["told"] for s in ws["sentences"]]
    assert told == c.get(f"/sessions/{sid}/turns/1").json()["answer"]
    r = next(s for s in ws["sentences"] if s["looked_at"]["signature"] == "rule.yoga.ruchaka.reduced")
    assert r["bank_row"]["kind"] == "fact" and len(r["bank_row"]["variants"]) == 3 and r["bank_row"]["status"] == "draft"
    assert r["looked_at"]["facts"]["reductions"] and r["looked_at"]["tags"][0] == "rule:yoga.ruchaka"
    mks = next(s for s in ws["sentences"] if s["looked_at"]["signature"] == "weakness.mks")
    assert mks["bank_row"] is None and mks["engine"] == mks["told"] and mks["derived"]          # the sheet's points
    lord = next(s for s in ws["sentences"] if s["looked_at"]["signature"] == "family.lord.for")
    assert any(d["point"] == 10 for d in lord["derived"])
    assert {x["what"] for x in ws["left_out"]} >= {"vote:career.kp", "place.sun_h10@lagna"}
    fixed = c.get(f"/sessions/{sid}/turns/2/worksheet", headers=AUTH).json()
    assert fixed["source"] == "fixed" and fixed["sentences"][0]["bank_row"] is None


def test_6_a_verdict_is_stored_against_the_bank_row_and_exported(ws_client, ws_app, tmp_path):
    from jyotish.export import export_reviews
    c, sid = ws_client
    _, url = ws_app
    ws = c.get(f"/sessions/{sid}/turns/1/worksheet", headers=AUTH).json()
    i = next(s["i"] for s in ws["sentences"] if s["looked_at"]["signature"] == "rule.yoga.ruchaka.reduced")
    bad = c.post(f"/sessions/{sid}/turns/1/worksheet/verdict", json={"i": i, "verdict": "change"}, headers=AUTH)
    assert bad.status_code == 422 and "needs your words" in bad.json()["detail"]
    j = next(s["i"] for s in ws["sentences"] if s["looked_at"]["signature"] == "weakness.mks")
    out = c.post(f"/sessions/{sid}/turns/1/worksheet/verdict", headers=AUTH,
                 json={"i": j, "verdict": "right"}).json()
    assert out["sentences"][j]["verdicts"][0]["verdict"] == "right"
    n = export_reviews(url, tmp_path)
    rows = [json.loads(x) for x in (tmp_path / "bank_reviews.jsonl").read_text().splitlines()][1:]
    assert n["bank"] == 1 and rows[0]["signature"] == "weakness.mks" and rows[0]["kind"] is None
    assert rows[0]["reviewer"] == "astrologer-1" and "_i" not in rows[0]["slots"]


def test_6_apply_reviews_writes_approvals_rewrites_and_withdrawals_back_to_the_bank(ws_client, ws_app, ws_bank):
    from jyotish.bank import apply_reviews, load_bank
    c, sid = ws_client
    _, url = ws_app
    ws = c.get(f"/sessions/{sid}/turns/1/worksheet", headers=AUTH).json()
    fact = next(s for s in ws["sentences"] if s["looked_at"]["signature"] == "rule.yoga.ruchaka.reduced")
    slots = fact["looked_at"]["slots"]
    rewrite = (f"{slots['name']}, a combination of courage, is in your chart, with {slots['placed']}, though "
               f"{slots['reductions']} hold it back for {slots['area']}.")
    c.post(f"/sessions/{sid}/turns/1/worksheet/verdict", headers=AUTH,
           json={"i": fact["i"], "verdict": "change", "words": rewrite})
    checker = StubChecker()                                    # a rewritten fact sentence is checked (review H4)
    rep = apply_reviews(url, ws_bank, today=AS_OF, checker=checker)
    assert [x["signature"] for x in rep["rewritten"]] == ["rule.yoga.ruchaka.reduced"]
    assert checker.asked and "Mars in your 7th house" in checker.asked[0][0]
    assert [x["signature"] for x in rep["no_row"]] == ["weakness.mks"]          # the engine's sentence: for drafting
    row = load_bank(ws_bank).fact("rule.yoga.ruchaka.reduced")
    v = fact["bank_row"]["variant"]
    assert row.variants[v] == ("{name}, a combination of courage, is in your chart, with {placed}, though "
                               "{reductions} hold it back for {area}.")
    # The variant he rewrote is approved; the other two are not, as he never read them (review H3).
    assert row.approved_variants == [v] and row.status == "draft"
    assert row.approved_by == row.rewritten_by == "astrologer-1"
    assert (ws_bank / "rules.yaml").read_text().startswith("# the test bank")
    assert apply_reviews(url, ws_bank, today=AS_OF, checker=checker) == {k: [] for k in rep} | {"no_row": rep["no_row"]}
    # Wrong: the row is withdrawn and never shown again; the next turn falls back to the engine's sentence.
    c.post(f"/sessions/{sid}/turns/1/worksheet/verdict", headers=AUTH,
           json={"i": fact["i"], "verdict": "wrong", "words": "Ruchaka does not bear on career here."})
    assert [x["signature"] for x in apply_reviews(url, ws_bank, today=AS_OF)["withdrawn"]] == ["rule.yoga.ruchaka.reduced"]
    assert load_bank(ws_bank).fact("rule.yoga.ruchaka.reduced") is None
    assert load_bank(ws_bank).row("rule.yoga.ruchaka.reduced", "fact").withdrawn_why.startswith("Ruchaka does not")


def test_6_a_rewrite_that_would_not_stand_is_refused_and_left_as_it_was(tmp_path):
    from jyotish.bank import template
    assert template("Mars sits in your 7th house.", {"planet": "Mars", "house": "7th"}) == "{planet} sits in your {house} house."
    assert template("Mars and Mars's aspect", {"planets": "Mars", "reductions": "Mars's aspect"}) == "{planets} and {reductions}"


def test_6_erasing_the_conversation_keeps_the_verdict_without_its_turn(ws_client, ws_app):
    from sqlalchemy.orm import sessionmaker
    from jyotish.db import BankReviewRow, migrate
    from jyotish.outcomes import erase_sessions
    c, sid = ws_client
    _, url = ws_app
    S = sessionmaker(migrate(url))
    with S.begin() as s:
        assert s.query(BankReviewRow).filter(BankReviewRow.turn_id.isnot(None)).count()
        erase_sessions(s, [sid], "test")
    with S.begin() as s:
        rows = s.query(BankReviewRow).all()
        # The turn is taken off; the slots (planet and sign names) stay for a rewrite, the facts go (review H4).
        assert rows and all(r.turn_id is None for r in rows)
        assert all(r.slots and "_facts" not in r.slots and "_engine" not in r.slots for r in rows)


def test_6_the_session_review_page_opens_the_worksheet_and_saves_a_verdict(tmp_path):
    """The astrologer's page (DoD 8 is still his first hour; this is the page working): the worksheet under a composed
    turn, per sentence what was told and the row behind it, and a verdict saved from it."""
    playwright = pytest.importorskip("playwright.sync_api")
    import httpx
    import sys
    sys.path.insert(0, str(ROOT / "tests"))
    from test_web import _serve
    mp = pytest.MonkeyPatch()
    mp.setenv("JYOTISH_LAYERED", "1")
    server, thread, base = _serve(tmp_path / "ws.db", str(ROOT / "tests" / "fixtures" / "narration_career_edited.json"),
                                  astrologers={"tok-page": "astrologer-1"}, today=lambda: AS_OF)
    try:
        with httpx.Client(base_url=base, timeout=90) as c:
            sid = c.post("/sessions", json=BIRTH).json()["id"]
            n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
            import time
            t = time.monotonic()
            while c.get(f"/sessions/{sid}/turns/{n}").json()["status"] != "done":
                assert time.monotonic() - t < 90
                time.sleep(0.1)
        with playwright.sync_playwright() as p:
            try:
                b = p.chromium.launch()
            except Exception as e:
                pytest.skip(f"Chromium for Playwright is not installed: {e}")
            page = b.new_page()
            page.goto(f"{base}/review/sessions/{sid}")
            page.fill("#token", "tok-page")
            page.click("#token-open")
            page.wait_for_selector("details.worksheet")
            page.click("details.worksheet summary")
            page.wait_for_selector(".ws-sentence")
            assert page.locator(".ws-sentence").count() >= 5
            assert "The bank row behind it" in page.inner_text(".ws-sentence >> nth=1")
            page.click(".ws-sentence >> nth=1 >> button[type=submit]")
            page.wait_for_function("document.querySelector('.ws-sentence:nth-child(2) [role=status]')"
                                   ".textContent.startsWith('Saved')")
            b.close()
        with httpx.Client(base_url=base) as c:
            ws = c.get(f"/sessions/{sid}/turns/1/worksheet", headers={"Authorization": "Bearer tok-page"}).json()
            assert ws["sentences"][1]["verdicts"][0]["verdict"] == "right"
    finally:
        server.should_exit = True
        thread.join(5)
        mp.undo()


# --- 7. The stored answer ---------------------------------------------------------------------------------------------

class DictStore:
    def __init__(self):
        self.rows, self.hits = {}, 0

    def get(self, key):
        if key in self.rows:
            self.hits += 1
            return dict(self.rows[key]["document"])
        return None

    def put(self, key, document, *, bank_version, birth_key=None):
        self.rows.setdefault(key, {"document": document, "bank": bank_version, "birth_key": birth_key})


def test_7_the_same_chart_routed_question_and_bank_are_served_the_stored_answer(chart, monkeypatch, tmp_path):
    from jyotish.bank import load_bank
    from jyotish.conversation import answer_turn
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    store = DictStore()
    m = "how is my career"
    first = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="a", store=store, birth_key="bk")
    assert first["stored"] == {"key": first["stored"]["key"], "served": False} and len(store.rows) == 1
    assert store.rows[first["stored"]["key"]]["birth_key"] == "bk"
    # The same session, the same question in other words routed the same way: the stored answer, no plan made.
    again = answer_turn(chart, "career?", route_turn("career?", chart), as_of=AS_OF, session_key="a", store=store)
    assert again["stored"]["served"] and again["shown"] == first["shown"] and "plan" in again
    assert "plan" not in again["timeline"] and store.hits == 1
    assert again["question"] == "career?" and "question" not in again["plan"]       # the asker's own words only
    # Another session is never served it (review M3): its own variants, its own answer.
    other = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="b", store=store)
    assert not other["stored"]["served"] and store.hits == 1
    # Another day, another bank or another question: answered afresh.
    other_day = answer_turn(chart, m, route_turn(m, chart), as_of=date(2026, 12, 1), store=store)
    assert not other_day["stored"]["served"]
    bank = load_bank(write_bank(tmp_path, ruchaka_rows()))
    assert not answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, store=store, bank=bank)["stored"]["served"]
    mar = "how is my marriage"
    assert not answer_turn(chart, mar, route_turn(mar, chart), as_of=AS_OF, store=store)["stored"]["served"]
    assert len(store.rows) == 5


def test_7_the_database_store_counts_hits_and_an_erasure_removes_the_charts_answers(chart, monkeypatch, tmp_path):
    from sqlalchemy.orm import sessionmaker
    from jyotish.conversation import answer_turn
    from jyotish.db import AnswerRow, AnswerStore, SessionRow, migrate
    from jyotish.outcomes import erase_sessions
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    S = sessionmaker(migrate(f"sqlite:///{tmp_path / 'a.db'}"))
    store = AnswerStore(S)
    m = "how is my career"
    for _ in range(3):
        doc = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, store=store, birth_key="bk-1")
    with S.begin() as s:
        row = s.get(AnswerRow, doc["stored"]["key"])
        assert row.hits == 2 and row.birth_key == "bk-1" and row.document["shown"] == doc["shown"]
        s.add(SessionRow(id="s1", birth_key="bk-1", birth={}, as_of=AS_OF.isoformat()))
    with S.begin() as s:
        counts = erase_sessions(s, ["s1"], "test")
        assert counts["answers"] == 1 and s.query(AnswerRow).count() == 0


# --- 8. Measured ------------------------------------------------------------------------------------------------------

@pytest.fixture
def real_bank(monkeypatch):
    """The committed bank, whatever an earlier module-scoped fixture (the worksheet's test bank) set."""
    import jyotish.bank
    monkeypatch.setattr(jyotish.bank, "BANK_DIR", ROOT / "data" / "bank")


def test_8_live_timing_times_the_seven_turns_composed_and_polished(tmp_path, monkeypatch, real_bank):
    """scripts/live_timing.py --turn --layered on [--polish]: each row says how many sentences came from the bank and
    whether the polished text was shown; offline here (a stub polisher and checker)."""
    lt = load_script("live_timing")
    import jyotish.conversation as conv
    import jyotish.envfile
    # live_timing sets JYOTISH_LAYERED and JYOTISH_POLISH in os.environ: set here first, so the test restores them.
    monkeypatch.setenv("JYOTISH_LAYERED", "0")
    monkeypatch.setenv("JYOTISH_POLISH", "")
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(lt, "ROWS", tmp_path / "rows.jsonl")
    real = conv.answer_turn
    monkeypatch.setattr(conv, "answer_turn", lambda *a, **k: real(*a, **(k | {"polisher": StubPolisher(joined),
                                                                               "checker": StubChecker()})))
    for flags in ([], ["--polish"]):
        monkeypatch.delenv("JYOTISH_POLISH", raising=False)
        assert lt.main(["--label", "l" + "".join(flags), "--turn", "--layered", "on", *flags, "--as-of", "2026-11-02",
                        "--out", str(tmp_path / "out")]) == 0
    rows = [json.loads(x) for x in (tmp_path / "rows.jsonl").read_text().splitlines()]
    composed, polished = rows[:7], rows[7:]
    assert [r["source"] for r in composed] == ["composer"] * 4 + ["fixed"] + ["composer"] * 2
    assert all(r["from_bank"] > 0 for r in composed if r["source"] != "fixed" and r["turn"] != 4)
    assert all(r["polished"] is None for r in composed if r["source"] != "fixed")
    assert [r["source"] for r in polished if r["source"] != "fixed"] == ["polished"] * 6
    assert all(r["polished"] is True and r["polish_refusals"] == 0 for r in polished if r["source"] != "fixed")


def test_8_the_scorecard_reports_the_layered_answer_never_gated(monkeypatch, tmp_path, real_bank):
    ev = load_script("evaluate")
    monkeypatch.setattr(ev, "DOCS", tmp_path)
    (tmp_path / "live_timings.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [
        {"kind": "turn", "date": "2026-11-15", "label": "c-1", "source": "composer", "from_bank": 8, "polished": None,
         "cost_usd": 0.0, "done_s": 0.1},
        {"kind": "turn", "date": "2026-11-15", "label": "p-1", "source": "polished", "from_bank": 8, "polished": True,
         "cost_usd": 0.002, "done_s": 9.0},
        {"kind": "turn", "date": "2026-11-15", "label": "w-1", "source": "writer", "cost_usd": 0.01, "done_s": 60}]))
    card = ev.Card()
    ev.layered(card, charts=4)
    n = card.numbers
    from jyotish.bank import load_bank
    assert 0 < n["bank.coverage"]["value"] <= 1 and n["bank.rows"]["value"] == len(load_bank())
    assert n["layered.composer_share"]["value"] == 1.0 and n["layered.polished.cost_usd"]["value"] == 0.002
    assert not any(v["gate"] for k, v in n.items() if k.startswith(("bank.", "layered.")))
