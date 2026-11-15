"""The layered answer (SPEC Layer 8 rev 134, "The layered answer"; docs/spec_notes_2026-11-15.md): the answer plan,
the sentence bank, the composer, the polisher, the worksheet and the stored answer, each step's tests, on the
reference chart first."""

import json
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
                 variants=["It supports {area}.", "It is good for {area}.", "{area} gains from it."])
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
    assert all(r.status == "draft" and r.drafted_by == "claude-sonnet-5-5" for r in bank.rows)
    facts = [r for r in bank.rows if r.kind == "fact"]
    assert all(sorted(c.variant for c in r.checks) == [0, 1, 2] and all(c.supported for c in r.checks) for r in facts)
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
    fact = row(signature="rule.yoga.ruchaka.reduced", slots=["area", "name", "planets", "houses", "reductions"],
               variants=["{name}, a combination of Mars, is in your chart: {planets} in your {houses} house, weakened "
                         "by {reductions}.",
                         "Your chart holds {name} (a combination of Mars), with {planets} in your {houses} house, though "
                         "{reductions} weaken it.",
                         "{planets} in your {houses} house forms {name}, a combination of Mars, weakened by {reductions}."])
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
                                "[text:Phaladeepika/Sastri-1937/6/1].") or "[rule:yoga.ruchaka]" in r["tagged"]
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
    for bad in (refused, fact | {"slots": fact["slots"] + ["dignity"]}):
        c = compose(career(chart, data), load_bank(write_bank(tmp_path, [bad])), session_key="s1")
        assert next(s for s in c["sentences"] if s["signature"] == "rule.yoga.ruchaka.reduced")["row"] is None


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
    file): a change to the plan, the bank or the composer shows here. JYOTISH_RECORD_FIXTURE=1 writes them anew."""
    import os
    from jyotish.bank import default_bank
    docs = seven_turns(chart, monkeypatch)
    got = {"bank": default_bank().version, "turns": [{"question": m, "source": d["source"], "shown": d["shown"],
                                                      "paragraphs": d["paragraphs"]} for m, d in zip(SEVEN, docs)]}
    if os.environ.get("JYOTISH_RECORD_FIXTURE"):
        FROZEN.write_text(json.dumps(got, indent=1, ensure_ascii=False) + "\n")
    frozen = json.loads(FROZEN.read_text())
    assert got == frozen
    assert [d["source"] for d in docs] == ["composer"] * 4 + ["fixed"] + ["composer"] * 2
    from jyotish.client import never_show
    assert not [s for d in docs for s in d["shown"] if never_show(s)]


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
    assert len(chk.asked) == 1 and doc["polish"]["composed"] in json.loads(chk.asked[0][1]).values()
    # Refused by the checker: the composed text is shown, and both calls are still recorded and priced.
    bad = answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF, session_key="s", polisher=StubPolisher(joined),
                      checker=StubChecker(ok=False))
    assert bad["source"] == "composer" and bad["shown"] == plain["shown"] and not bad["polish"]["used"]
    assert bad["polish"]["refusals"][0].startswith("not in the composed text")
    assert bad["usage"]["polisher"]["cache_read_input_tokens"] == 800 and bad["usage"]["checker"]["calls"] == 1


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
                      polisher=StubPolisher(lambda t: "**Your** career <b>leans</b> favourably."))
    assert doc["shown"] == ["Your career leans favourably."]


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
    assert v["cost_usd"] == pytest.approx(haiku + glm, abs=1e-6)
    assert v["backends"]["polisher"]["model"] == "claude-haiku-5-5"
    monkeypatch.delenv("JYOTISH_POLISH")
    assert reading_cost(answer_turn(chart, m, route_turn(m, chart), as_of=AS_OF))["cost_usd"] == 0
