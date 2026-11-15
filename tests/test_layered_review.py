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
    """Every sentence the composer writes for those plans with every row's variant 1, 2 and 3 in turn (the session's
    pick fixed, review M10), draft meanings on."""
    import jyotish.conversation as conv
    from jyotish.bank import default_bank
    bank = default_bank()
    out = []
    with pytest.MonkeyPatch.context() as mp:
        for v in range(3):
            mp.setattr(conv, "variant_of", lambda key, signature, v=v: v)
            for c, p in plans:
                for s in conv.compose(p, bank, session_key=f"v{v}", draft_meanings=True)["sentences"]:
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
    facts = [r for r in load_bank().rows if r.kind == "fact"]
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
                          {"variant": 1, "sentence": "B y.", "supported": True, "model": "m", "on": AS_OF, "shape": "b"}]
                  + [{"variant": v, "sentence": "x", "supported": True, "model": "m", "on": AS_OF} for v in (0, 2)])
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


# --- H2. "Raja yoga (… joined)" is told for a yoga formed by aspect or exchange -------------------------------------

PLACED = re.compile(r"\b(?:the )?(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu) in your (\d+)(?:st|nd|rd|th) house")


def test_h2_the_raja_yoga_says_how_its_rulers_are_related_on_the_reference_chart():
    from jyotish.conversation import plan_turn, route_turn
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    p = plan_turn(c, "how is my career", route_turn("how is my career", c), as_of=AS_OF)
    raja = next(i for i in p.items if i.signature.startswith("rule.yoga.kendra_trikona_raja"))
    assert raja.slots["named"] == "raja yoga (the rulers of an angular house and of a trine house, together in one sign)"
    assert raja.slots["placed"] == "the Sun and Mercury in your 10th house" and raja.facts["relations"] == ["conjunction"]


def test_h2_no_rule_sentence_tells_a_relation_or_a_house_its_fire_does_not_have(composed):
    """Over the random charts: a raja yoga's gloss names the relations its fires record, never "joined"; every planet
    a rule sentence places is in that house; no list of houses is followed by a singular "house"."""
    from jyotish.plan import RELATION_PLAIN
    seen = {"raja": 0, "placed": 0}
    for c, p, s in composed:
        if s["part"] != "rule":
            continue
        assert not re.search(r"\b\d+(?:st|nd|rd|th) and (?:your )?\d+(?:st|nd|rd|th) house\b", s["text"]), s["text"]
        item = next(i for i in p.items if i.signature == s["signature"] and i.area == s["area"])
        if item.facts["rule_id"].startswith("yoga.kendra_trikona_raja"):
            seen["raja"] += 1
            assert "joined" not in s["text"]
            for r in item.facts["relations"]:
                assert RELATION_PLAIN[r] in item.slots["named"]
        if s["row"] and item.slots.get("placed"):
            for planet, house in PLACED.findall(s["text"]):
                seen["placed"] += 1
                assert c.bodies[planet].house == int(house), s["text"]
    assert seen["raja"] > 5 and seen["placed"] > 20, seen


def test_h2_a_relation_with_no_plain_words_keeps_the_rule_out():
    from jyotish.plan import _rule_item
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    f = {"rule_id": "yoga.kendra_trikona_raja", "planets": ["Sun", "Mercury"], "allowed_tags": [],
         "fires": [{"basis": "lagna", "nodes": ["Sun", "Mercury", "H10"], "modifiers_applied": [],
                    "details": {"relations": ["dristi_by_sign"]}}]}
    item, why = _rule_item(c, f, "career", "your career")
    assert item is None and "dristi_by_sign" in why


def test_h2_a_rule_fired_only_from_the_moon_says_its_angle_is_counted_from_the_moon():
    from jyotish.plan import _rule_item
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    f = {"rule_id": "yoga.ruchaka", "planets": ["Mars"], "allowed_tags": [],
         "fires": [{"basis": "moon", "nodes": ["Mars"], "modifiers_applied": [], "details": {}}]}
    item, _ = _rule_item(c, f, "career", "your career")
    assert item.signature == "rule.yoga.ruchaka.full.nohouse"
    assert item.slots["named"] == "Ruchaka (Mars in its own or exalted sign in an angular house from your Moon)"


# --- H3. "Right" on one variant approves all three, and the worksheet shows only one --------------------------------

def _meaning_row(**kw):
    from jyotish.bank import BankRow
    return BankRow(**{"signature": "rule.yoga.ruchaka.reduced@career", "kind": "meaning", "slots": ["area"],
                      "source": "BPHS 75.1-2", "drafted_by": "t", "drafted_on": AS_OF,
                      "variants": ["Zero for {area}.", "One for {area}.", "Two for {area}."]} | kw)


def test_h3_right_on_one_variant_approves_that_variant_only():
    from jyotish.bank import approve, row_errors
    r = _meaning_row()
    approve(r, 1, "astrologer-1", AS_OF)
    assert r.approved_variants == [1] and r.status == "draft" and not row_errors(r)
    assert [r.approved(i) for i in range(3)] == [False, True, False]
    for i in (0, 2):
        approve(r, i, "astrologer-1", AS_OF)
    assert r.status == "approved" and not row_errors(r)
    assert row_errors(_meaning_row(approved_variants=[0, 1, 2], status="draft", approved_by="a", approved_on=AS_OF))


def test_h3_a_public_client_reads_only_an_approved_variant_or_an_approved_sibling(tmp_path):
    from jyotish.bank import Bank
    from jyotish.conversation import compose, plan_turn, route_turn, variant_of
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    p = plan_turn(c, "how is my career", route_turn("how is my career", c), as_of=AS_OF)
    sig = "rule.yoga.ruchaka.reduced@career"
    keys = {variant_of(k, sig): k for k in (f"k{n}" for n in range(30))}
    meaning = lambda bank, key: [s for s in compose(p, bank, session_key=key, draft_meanings=False)["sentences"]
                                 if s["row"] and s["row"]["kind"] == "meaning"]
    none = Bank([_meaning_row()], "v")
    assert all(meaning(none, keys[i]) == [] for i in range(3))                 # nothing approved: nothing shown
    one = Bank([_meaning_row(approved_variants=[2], approved_by="a", approved_on=AS_OF)], "v")
    for i in range(3):                                                         # every session reads variant 2
        got = meaning(one, keys[i])
        assert [s["row"]["variant"] for s in got] == [2] and got[0]["text"] == "Two for your career."
    shown = [s["row"]["variant"] for s in compose(p, none, session_key=keys[0], draft_meanings=True)["sentences"]
             if s["row"] and s["row"]["kind"] == "meaning"]
    assert shown == [0]                                                        # testing: the session's own pick


def test_h3_the_worksheet_shows_every_variant_and_which_are_approved():
    from jyotish.bank import Bank
    from jyotish.conversation import worksheet
    row = _meaning_row(approved_variants=[0], approved_by="a", approved_on=AS_OF, file="meanings.yaml")
    doc = {"source": "composer", "plan": {"items": [{"signature": "rule.yoga.ruchaka.reduced", "area": "career"}]},
           "composed": {"sentences": [{"text": "Two for your career.", "signature": "rule.yoga.ruchaka.reduced",
                                       "part": "rule", "area": "career", "item": 0,
                                       "row": {"signature": row.signature, "kind": "meaning", "variant": 2}}]}}
    s = worksheet(doc, Bank([row], "v"))["sentences"][0]
    assert s["bank_row"]["variants"] == row.variants and s["bank_row"]["approved_variants"] == [0]
    js = (ROOT / "web" / "js" / "review-session.js").read_text()
    assert "ws.right_scope" in js and "approved_variants" in js


# --- H4. An astrologer's rewrite can become one chart's values for every chart ---------------------------------------

def test_h4_a_rewrite_starting_with_a_capitalised_value_is_templated():
    from jyotish.bank import template
    slots = {"planet": "the Sun", "role": "the main planet of your career", "sign": "Aquarius"}
    assert (template("The Sun, the main planet of your career, is in a feeble state by its degree in Aquarius.", slots)
            == "{planet}, {role}, is in a feeble state by its degree in {sign}.")


def test_h4_two_items_of_one_signature_keep_their_own_facts_on_the_worksheet():
    """The reference chart's career: weakness.mrita for Saturn (the 10th lord) and for the Sun (the main
    significator). Each sentence's worksheet row shows its own planet's facts and slots."""
    from jyotish.conversation import compose, plan_turn, route_turn, worksheet
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    p = plan_turn(c, "how is my career", route_turn("how is my career", c), as_of=AS_OF)
    assert [i.facts["planet"] for i in p.items if i.signature == "weakness.mrita"] == ["Saturn", "Sun"]
    doc = {"source": "composer", "plan": p.model_dump(), "composed": compose(p, session_key="s")}
    mrita = [s for s in worksheet(doc)["sentences"] if s["looked_at"]["signature"] == "weakness.mrita"]
    assert [s["looked_at"]["facts"]["planet"] for s in mrita] == ["Saturn", "Sun"]
    for s in mrita:
        planet = s["looked_at"]["facts"]["planet"]
        assert planet in s["told"] and s["looked_at"]["slots"]["sign"] == c.bodies[planet].sign_name


def test_h4_a_rewrite_whose_slots_are_not_the_variants_is_refused():
    from jyotish.bank import rewrite_errors, template
    old = "{role}, {planet}, is in a feeble state by its degree in {sign}."
    slots = {"planet": "Saturn", "role": "the ruler of your 10th house", "sign": "Taurus"}
    ok = template("The ruler of your 10th house, Saturn, is feeble by its degree in Taurus.", slots)
    assert rewrite_errors(old, ok) == []
    left = template("Saturn is feeble in Taurus, as it is for everyone.", {"planet": "the Sun", "sign": "Aquarius"})
    assert left == "Saturn is feeble in Taurus, as it is for everyone." and rewrite_errors(old, left)


@pytest.fixture
def h4_db(tmp_path):
    """A bank of one fact row and a database with one "change" verdict on its variant 0."""
    import shutil
    from sqlalchemy.orm import sessionmaker
    from jyotish.bank import BankRow, dump_rows
    from jyotish.db import BankReviewRow, migrate
    d = tmp_path / "bank"
    d.mkdir()
    shutil.copy(ROOT / "data" / "bank" / "bank.schema.json", d)
    row = BankRow(signature="weakness.mrita", kind="fact", slots=["planet", "role", "sign"], drafted_by="t",
                  drafted_on=AS_OF, variants=["{role}, {planet}, is in a feeble state by its degree in {sign}."] * 3)
    (d / "weaknesses.yaml").write_text(dump_rows([row]))
    url = f"sqlite:///{tmp_path / 'h4.db'}"
    S = sessionmaker(migrate(url))
    slots = {"planet": "Saturn", "role": "the ruler of your 10th house", "sign": "Taurus",
             "_facts": {"planet": "Saturn", "avastha_baladi": "Mrita", "sign": "Taurus"}, "_engine": "e", "_i": 3}
    with S.begin() as s:
        s.add(BankReviewRow(signature="weakness.mrita", kind="fact", variant=0, verdict="change",
                            words="The ruler of your 10th house, Saturn, sits feeble by its degree in Taurus.",
                            sentence="x", slots=slots, reviewer_id="astrologer-1"))
    return d, url, S


class _Checker:
    def __init__(self, ok):
        self.ok, self.asked = ok, []

    def ask_one(self, sentence, data):
        from jyotish.narrate import CheckResult, Proposition
        self.asked.append((sentence, json.loads(data)))
        return CheckResult(propositions=[Proposition(text=sentence, supported=self.ok, evidence="stub")]), {}


def test_h4_a_rewritten_fact_variant_is_checked_against_its_facts_and_refused_if_not_stated(h4_db):
    from jyotish.bank import apply_reviews, load_bank
    d, url, _ = h4_db
    assert apply_reviews(url, d, today=AS_OF)["refused"][0]["why"][0].startswith("a rewritten fact sentence is checked")
    no = _Checker(False)
    rep = apply_reviews(url, d, today=AS_OF, checker=no)
    assert rep["refused"] and "not stated by the facts" in rep["refused"][0]["why"][0]
    assert no.asked[0][0] == "the ruler of your 10th house, Saturn, sits feeble by its degree in Taurus."
    assert no.asked[0][1]["facts"]["avastha_baladi"] == "Mrita"
    assert load_bank(d).fact("weakness.mrita").variants[0].endswith("is in a feeble state by its degree in {sign}.")
    yes = _Checker(True)
    rep = apply_reviews(url, d, today=AS_OF, checker=yes)
    row = load_bank(d).fact("weakness.mrita")
    assert rep["rewritten"] and row.variants[0] == "{role}, {planet}, sits feeble by its degree in {sign}."
    assert [c.variant for c in row.checks] == [0] and row.checks[0].supported


def test_h4_after_the_conversation_is_erased_a_fact_rewrite_is_refused_not_written_literally(h4_db):
    from jyotish.bank import apply_reviews, load_bank
    from jyotish.db import BankReviewRow
    d, url, S = h4_db
    with S.begin() as s:                                   # what erase_sessions leaves: the slots, not the facts
        r = s.query(BankReviewRow).one()
        r.slots = {k: v for k, v in r.slots.items() if k not in ("_facts", "_engine")}
    rep = apply_reviews(url, d, today=AS_OF, checker=_Checker(True))
    assert rep["refused"] and "erased with the conversation" in rep["refused"][0]["why"][0]
    assert "Saturn" not in "".join(load_bank(d).fact("weakness.mrita").variants)


# --- H5. A subject's erasure fails on Postgres once a bank verdict exists, and leaves the stored answers -------------

def test_h5_a_subjects_erasure_with_a_bank_verdict_and_a_stored_answer_holds_under_foreign_keys(tmp_path):
    """SQLite with foreign keys on, as Postgres enforces them: a subject, a conversation of its birth with one turn,
    an astrologer's verdict on that turn and a stored answer of the birth; outcomes.erase removes the turn and the
    answer and keeps the verdict, its turn taken off."""
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    from jyotish import outcomes as oc
    from jyotish.api import SubjectRow
    from jyotish.db import AnswerRow, BankReviewRow, SessionRow, TurnRow, migrate
    url = f"sqlite:///{tmp_path / 'fk.db'}"
    rows = oc.read_sheet(ROOT / "docs" / "intake_template.csv")
    with sessionmaker(migrate(url)).begin() as s:            # the import, without foreign keys (its own fault, apart)
        oc.add_consent(s, "C-0001", "S-0001", "v1", "backlog", "clerk-1")
        assert oc.import_rows(s, rows, entered_by="clerk-1", today=AS_OF).accepted
    engine = create_engine(url)
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    S = sessionmaker(migrate(engine))
    with S.begin() as s:
        bkey = s.get(SubjectRow, "S-0001").birth_key
        s.add(SessionRow(id="s" * 32, birth_key=bkey, birth={}, as_of=AS_OF.isoformat()))
        s.flush()
        s.add(TurnRow(id="t" * 32, session_id="s" * 32, n=1, birth_key=bkey, question="q", status="done"))
        s.flush()
        s.add(BankReviewRow(signature="weakness.mks", kind="fact", variant=0, verdict="right", sentence="x",
                            slots={"planet": "Saturn"}, turn_id="t" * 32, reviewer_id="astrologer-1"))
        s.add(AnswerRow(key="k" * 64, birth_key=bkey, bank_version="v", document={"plan": {"question": "q"}}))
    with S.begin() as s:
        counts = oc.erase(s, "S-0001", "dpo-1")
    assert counts["turns"] == 1 and counts["answers"] == 1 and counts["bank_verdicts_kept"] == 1
    with S() as s:
        assert s.query(TurnRow).count() == 0 and s.query(AnswerRow).count() == 0
        v = s.query(BankReviewRow).one()
        assert v.turn_id is None and v.verdict == "right"


# --- M1. The polisher's check misses omissions and invented causes ----------------------------------------------------

COMPOSED = ("No chart can name an amount or promise anything to you; it shows how well it supports your career. "
            "For your career, most of what the chart shows agrees, and on balance it leans favourably.\n\n"
            "The ruler of your 10th house, Saturn, sits in your 1st house, a house that drains it. Saturn has less "
            "strength than it needs to give fully what it promises.\n\n"
            "The most favourable stretch for your career runs from October 2029 to June 2032. Neither stretch is a "
            "prediction of when you will act.")


@pytest.mark.parametrize("polished,why", [
    (COMPOSED.replace("Saturn, sits in your 1st house, a house that drains it. Saturn has", "Saturn, sits in your 1st "
                      "house, a house that drains it, so it has"), "adds a cause"),
    (COMPOSED.replace(" from October 2029 to June 2032", " soon"), "leaves out the date"),
    (COMPOSED.replace("leans favourably", "is good"), "leaves out the lean"),
    (COMPOSED.replace("No chart can name an amount or promise anything to you; it shows how well it supports your "
                      "career. For your career", "For your career").replace("leans favourably.", "leans favourably. "
                      "No chart can name an amount or promise anything to you; it shows how well it supports your "
                      "career."), "opening sentence"),
    (COMPOSED.replace(" Neither stretch is a prediction of when you will act.", "").replace(
        "The most favourable", "Neither stretch is a prediction of when you will act. The most favourable"), "caveat"),
    (COMPOSED.replace("Saturn", "Jupiter", 1), "adds the planet"),
])
def test_m1_the_code_refuses_a_polished_text_that_drops_moves_or_adds_before_any_call(polished, why):
    from jyotish.conversation import polish_errors
    assert polish_errors(COMPOSED, COMPOSED) == []
    errs = polish_errors(COMPOSED, polished)
    assert any(why in e for e in errs), errs


def test_m1_the_committed_polished_career_turn_is_refused_for_its_invented_cause():
    from jyotish.conversation import polish_errors
    doc = json.loads((ROOT / "docs" / "layered_2026-11-15" / "layered-polished-1.turn.json").read_text())
    assert doc["polish"]["used"] is True                                   # shown live, before this fix
    assert polish_errors(doc["polish"]["composed"], doc["polish"]["text"]) == [
        "the polished text adds a cause the composed text does not state (so)"]
    bench = [json.loads(x) for x in (ROOT / "tests" / "fixtures" / "checker_bench.jsonl").read_text().splitlines()]
    row = next(r for r in bench if r["id"] == "live-polish-career-saturn-cause")
    assert row["label"] == "reject" and row["where"] == "polish" and row["sentence"] == doc["polish"]["text"]


def test_m1_the_checker_is_asked_both_ways_and_an_omission_refuses_the_polish():
    from jyotish.conversation import polish
    from jyotish.narrate import CheckResult, Completion, Proposition

    class Polisher:
        model = "stub"

        def structured(self, **kw):
            from jyotish.conversation import PolishDraft
            return Completion(parsed=PolishDraft(text=COMPOSED), assistant={}, stop_reason="end_turn", meta={})

    class Checker:
        def __init__(self):
            self.asked = []

        def ask_one(self, sentence, data):
            self.asked.append((sentence, data))
            back = next(iter(json.loads(data))).startswith("polished answer")
            return CheckResult(propositions=[Proposition(text="x", supported=not back, evidence="left out")]), {}
    ch = Checker()
    out = polish(COMPOSED, backend=Polisher(), checker=ch)
    assert len(ch.asked) == 2 and ch.asked[1][0] == COMPOSED and "polished answer" in ch.asked[1][1]
    assert out["used"] is False and out["refusals"] == ["left out of the polished text: x (left out)"]


# --- M2. The polisher is hard-wired to Anthropic, and its failure fails the turn ----------------------------------------

def test_m2_with_no_anthropic_key_a_polished_turn_shows_the_composed_text(monkeypatch):
    from jyotish.conversation import answer_turn, route_turn
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("JYOTISH_POLISHER_BACKEND", raising=False)
    m = "how is my career"
    doc = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="m2")
    assert doc["source"] == "composer" and doc["shown"] and not doc["polish"]["used"]
    assert doc["polish"]["refusals"][0].startswith("the polisher could not be reached")


def test_m2_the_polisher_is_a_role_on_an_openai_compatible_host_and_health_reports_it(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    from jyotish.narrate import CONFIG, OpenAIBackend, make_backend
    monkeypatch.setenv("JYOTISH_POLISHER_BACKEND", "openai:https://api.deepinfra.com/v1/openai:Qwen/Qwen3.6-35B-A3B")
    monkeypatch.setenv("JYOTISH_POLISHER_KEY", "not-a-key")
    b = make_backend(None, "polisher", CONFIG, model="claude-haiku-5-5")
    assert isinstance(b, OpenAIBackend) and b.model == "Qwen/Qwen3.6-35B-A3B"
    sent = {}

    def structured(**kw):
        sent.update(kw)
        raise RuntimeError("stub: no call")
    b.structured = structured
    from jyotish.conversation import polish
    out = polish("Your career leans favourably.", backend=b, checker=object())
    assert isinstance(sent["system"], str) and out["refusals"][0].startswith("the polisher could not be reached")
    with TestClient(create_app(f"sqlite:///{tmp_path / 'h.db'}")) as c:
        assert "polisher" not in c.get("/health").json()
        monkeypatch.setenv("JYOTISH_POLISH", "1")
        h = c.get("/health").json()
        assert h["polisher"] == {"provider": "openai-compatible", "host": "api.deepinfra.com",
                                 "model": "Qwen/Qwen3.6-35B-A3B", "ready": True}
        assert "not-a-key" not in json.dumps(h)


# --- M3. A stored answer crosses conversations ------------------------------------------------------------------------

def test_m3_a_second_conversation_reads_its_own_variants_and_its_follow_up_repeats_nothing(monkeypatch):
    """The review's reproduction on the reference chart: "how is my career" then "why?". With turn 1 served from
    another conversation's store the "why?" restated every reason; now each conversation's turn 1 is its own."""
    from jyotish.conversation import answer_turn, route_turn
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    monkeypatch.setenv("JYOTISH_LAYERED", "1")

    class Store:
        def __init__(self):
            self.rows = {}

        def get(self, key):
            return dict(self.rows[key]) if key in self.rows else None

        def put(self, key, document, *, bank_version, birth_key=None):
            self.rows.setdefault(key, document)
    store = Store()
    m = "how is my career"
    a1 = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="conv-a", store=store, birth_key="bk")
    b1 = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="conv-b", store=store, birth_key="bk")
    assert not b1["stored"]["served"] and b1["shown"] != a1["shown"]          # B's own variants
    assert all("question" not in d.get("plan", {}) for d in store.rows.values())
    last = route_turn(m, c)
    why = answer_turn(c, "why?", route_turn("why?", c, last), as_of=AS_OF, session_key="conv-b", store=store,
                      history=[{"question": m, "answer": " ".join(b1["shown"])}])
    assert len(why["shown"]) <= 2, why["shown"]


# --- M4. A follow-up after a polished turn repeats everything --------------------------------------------------------

class _JoinPolisher:
    """A polish that joins each paragraph's first two sentences: the client reads none of the composed sentences as
    they were composed."""
    model = "stub"

    def describe(self):
        return {"provider": "anthropic", "host": "api.anthropic.com", "model": "stub"}

    def structured(self, *, messages, schema, **kw):
        from jyotish.narrate import Completion
        text = "\n\n".join(re.sub(r"^([^.]+)\. ([A-Z])", lambda m: m.group(1) + "; " + m.group(2).lower(), p, count=1)
                           for p in messages[0]["content"].split("\n\n"))
        return Completion(parsed=schema(text=text), assistant={}, stop_reason="end_turn", meta={})


def test_m4_a_follow_up_after_a_polished_turn_leaves_out_what_was_composed(monkeypatch):
    from jyotish.conversation import answer_turn, route_turn, said_keys_of
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    m = "how is my career"
    plain = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="m4")
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    pol = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="m4", polisher=_JoinPolisher(),
                      checker=_Checker(True))
    assert pol["source"] == "polished" and said_keys_of(pol) == said_keys_of(plain)
    monkeypatch.delenv("JYOTISH_POLISH")
    last = route_turn(m, c)
    after = lambda first, keys: answer_turn(c, "why?", route_turn("why?", c, last), as_of=AS_OF, session_key="m4",
                                            history=[{"question": m, "answer": " ".join(first["shown"]),
                                                      **({"said_keys": said_keys_of(first)} if keys else {})}])
    base = after(plain, keys=False)                       # the text filter, after a plain turn
    assert len(base["shown"]) <= 2
    assert len(after(pol, keys=False)["shown"]) >= len(base["shown"]) + 3   # the fault: the text filter misses it
    assert after(pol, keys=True)["shown"] == base["shown"]


# --- M5. The ".nohouse" rule rows are never used, and the coverage figure counts them as found -----------------------

def test_m5_a_row_declaring_a_slot_no_variant_uses_does_not_load():
    from jyotish.bank import BankRow, row_errors
    r = BankRow(signature="rule.yoga.sasa.full.nohouse", kind="fact", slots=["area", "houses", "named", "planets"],
                drafted_by="t", drafted_on=AS_OF, variants=["Your chart holds {named}, formed by {planets}, for {area}."] * 3)
    assert any("declares a slot no variant uses: ['houses']" in e for e in row_errors(r))


def test_m5_fills_is_the_composers_rule_and_the_coverage_tools():
    from jyotish.bank import BankRow, fills
    r = BankRow(signature="x.y", kind="fact", slots=["area", "dignity", "planets"], drafted_by="t", drafted_on=AS_OF,
                variants=["{planets} for {area}{dignity}."] * 3,
                checks=[{"variant": v, "sentence": "x", "supported": True, "model": "m", "on": AS_OF} for v in range(3)])
    assert fills(r, {"area": "your career", "planets": "Mars", "dignity": ""})
    assert not fills(r, {"area": "your career", "planets": "", "dignity": ""})      # an empty slot: the engine's
    assert not fills(r, {"area": "your career"})
    import inspect
    from jyotish import bank
    assert "fills(bank.fact(sig), slots)" in inspect.getsource(bank.coverage)


def test_m5_a_rule_fired_with_no_house_is_told_from_the_bank(composed):
    nohouse = [s for c, p, s in composed if s["part"] == "rule" and s["signature"].endswith(".nohouse")]
    assert nohouse and sum(s["row"] is not None for s in nohouse) / len(nohouse) > 0.9


# --- M6. Grammar faults the composer puts in front of clients ----------------------------------------------------------

P = r"(?:the )?(?:Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)"
SINGULAR = r"(?:sits|has|is|leans|holds|forms|bears|falls|lies|stands|rules|gives)"


def test_m6_no_doubled_comma_no_plural_verb_after_a_role_and_no_list_with_a_singular_verb(composed):
    for c, p, s in composed:
        t = s["text"]
        assert not re.search(r",\s*,", t), t
        assert not re.search(rf"\b{P} and {P} {SINGULAR}\b", t), t                       # "the Sun and Mercury sits"
        assert not re.search(rf"\b{P} and {P} [^,;.]*?\band {SINGULAR}\b", t), t          # "... sit ... and forms"
        assert not re.search(r"\b(?:main planet|ruler)[^,;.]* and the main planet[^,;.]* (?:are|sit|have)\b", t), t


def test_m6_agreement_mends_the_second_verb_and_leaves_a_role_singular():
    from jyotish.bank import agree, tidy
    assert agree("{planets} sits in your 10th house and forms a yoga.", {"planets": "the Sun and Mercury"}) == \
        "{planets} sit in your 10th house and form a yoga."
    assert agree("When {role} sits in", {"role": "the ruler of your 2nd house and the main planet for money"}) == \
        "When {role} sits in"
    assert tidy("in your 12th house,, and together") == "in your 12th house, and together"
    assert tidy("in your 12th house, , and together") == "in your 12th house, and together"


# --- M7. Merging several areas into one item overstates what each area has ----------------------------------------------

def _reference():
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_m7_the_merged_period_names_each_lord_with_its_own_areas():
    from jyotish.conversation import compose, plan_turn, route_turn
    c = _reference()
    m = "what are the challenges in my life"
    p = plan_turn(c, m, route_turn(m, c), as_of=AS_OF)
    period = next(i for i in p.items if i.part == "period")
    assert period.signature == "period.now.touches.each"
    assert period.facts["hands"] == {"Jupiter": ["father", "reputation", "siblings"], "Mercury": ["father", "siblings"]}
    told = next(s["text"] for s in compose(p, session_key="m7")["sentences"] if s["part"] == "period")
    assert "Mercury in your father and brothers, sisters and courage" in told and "Mercury have a hand" not in told


def test_m7_the_merged_period_over_random_charts_never_gives_a_lord_an_area_it_does_not_touch(plans):
    for c, p in plans:
        for i in p.items:
            if i.signature == "period.now.touches.each":
                a = {x: set(v) for x, v in i.facts["hands"].items()}
                lords = {ar: set(c.scored.areas[ar].lords) | set(c.scored.areas[ar].karakas) for ar in i.facts["areas"]}
                assert all(x in lords[ar] for x, v in a.items() for ar in v), (i.facts["hands"], lords)


def test_m7_a_rule_said_for_several_areas_reads_each_areas_own_meaning_row():
    from jyotish.bank import Bank, BankRow
    from jyotish.conversation import compose, plan_turn, route_turn
    c = _reference()
    m = "what are the challenges in my life"
    p = plan_turn(c, m, route_turn(m, c), as_of=AS_OF)
    rule = next(i for i in p.items if i.part == "rule" and len(i.facts.get("areas") or []) > 1)
    rows = [BankRow(signature=f"{rule.signature}@{a}", kind="meaning", slots=["area"], source="BPHS 1.1",
                    drafted_by="t", drafted_on=AS_OF, variants=[f"For {{area}} ({a})."] * 3) for a in rule.facts["areas"]]
    told = [s for s in compose(p, Bank(rows, "v"), session_key="m7", draft_meanings=True)["sentences"]
            if s["row"] and s["row"]["kind"] == "meaning"]
    labels = rule.facts["area_labels"]
    assert [s["text"] for s in told] == [f"For {labels[a]} ({a})." for a in rule.facts["areas"]]
    assert [s["area"] for s in told] == rule.facts["areas"]


# --- M8. A withdrawal cannot be undone, and an older verdict can override a newer one --------------------------------

def _verdict_db(tmp_path, verdicts):
    import shutil
    from sqlalchemy.orm import sessionmaker
    from jyotish.bank import BankRow, dump_rows
    from jyotish.db import BankReviewRow, migrate
    d = tmp_path / "bank"
    d.mkdir()
    shutil.copy(ROOT / "data" / "bank" / "bank.schema.json", d)
    row = BankRow(signature="rule.yoga.ruchaka.reduced@career", kind="meaning", slots=["area"], source="BPHS 75.1",
                  drafted_by="t", drafted_on=AS_OF, variants=["Zero for {area}.", "One for {area}.", "Two for {area}."])
    (d / "meanings.yaml").write_text(dump_rows([row]))
    url = f"sqlite:///{tmp_path / 'm8.db'}"
    with sessionmaker(migrate(url)).begin() as s:
        for variant, verdict, words in verdicts:                         # in the order given: oldest first
            s.add(BankReviewRow(signature=row.signature, kind="meaning", variant=variant, verdict=verdict, words=words,
                                sentence="x", slots={"area": "your career"}, reviewer_id="astrologer-1"))
            s.flush()
    return d, url


def test_m8_a_newer_right_is_not_undone_by_an_older_wrong(tmp_path):
    from jyotish.bank import apply_reviews, load_bank
    d, url = _verdict_db(tmp_path, [(0, "wrong", "not this reading"), (1, "right", None)])
    apply_reviews(url, d, today=AS_OF)
    r = load_bank(d).meaning("rule.yoga.ruchaka.reduced", "career")
    assert r is not None and r.approved_variants == [1]                     # the latest verdict on the row decides


def test_m8_a_row_withdrawn_and_then_rewritten_is_shown_again(tmp_path):
    from jyotish.bank import apply_reviews, load_bank
    d, url = _verdict_db(tmp_path, [(0, "wrong", "not this reading")])
    apply_reviews(url, d, today=AS_OF)
    assert load_bank(d).meaning("rule.yoga.ruchaka.reduced", "career") is None
    from sqlalchemy.orm import sessionmaker
    from jyotish.db import BankReviewRow, migrate
    with sessionmaker(migrate(url)).begin() as s:
        s.add(BankReviewRow(signature="rule.yoga.ruchaka.reduced@career", kind="meaning", variant=2, verdict="change",
                            words="Tradition reads it as courage for your career.", sentence="x",
                            slots={"area": "your career"}, reviewer_id="astrologer-1"))
    rep = apply_reviews(url, d, today=AS_OF)
    r = load_bank(d).meaning("rule.yoga.ruchaka.reduced", "career")
    assert rep["rewritten"] and r is not None and r.withdrawn_by is None
    assert r.variants[2] == "Tradition reads it as courage for {area}." and r.approved_variants == [2]


# --- M9. Meaning rows that are wrong in substance -----------------------------------------------------------------------

def test_m9_the_meaning_rows_the_review_named_say_what_their_rule_and_weakness_are():
    from jyotish.bank import load_bank
    rows = {r.signature: r for r in load_bank().rows if r.kind == "meaning"}
    words = lambda prefix: " ".join(v for s, r in rows.items() if s.startswith(prefix) for v in r.variants)
    gk = words("rule.yoga.gaja_kesari.")
    assert "lion" in gk and not re.search(r"the lion combination|means a lion", gk)   # the elephant and the lion
    assert "named for discipline" not in words("rule.yoga.sasa.")                       # Sasa is the hare
    assert "named for courage" not in words("rule.yoga.ruchaka.")                       # Ruchaka is radiant
    assert "short of the strength" not in words("weakness.mks@")                        # that is low strength
    for area in ("marriage", "wealth"):
        assert all("{planet}" in v for v in rows[f"weakness.mks@{area}"].variants)        # the planet is named
    for s in ("rule.yoga.gaja_kesari_bphs.reduced@career", "rule.yoga.gaja_kesari_bphs.reduced@wealth"):
        assert not any("Moon" in v for v in rows[s].variants)


def test_m9_a_meaning_row_with_a_house_never_counts_a_rising_sign_rule_from_the_moon():
    from jyotish.bank import BankRow, row_errors
    mk = lambda sig: BankRow(signature=sig, kind="meaning", slots=["area", "planets"], source="BPHS 1.1",
                             drafted_by="t", drafted_on=AS_OF,
                             variants=["With {planets} at an angle from the Moon, it favours {area}."] * 3)
    assert any("counts from the Moon" in e for e in row_errors(mk("rule.yoga.gaja_kesari_bphs.full@career")))
    assert not row_errors(mk("rule.yoga.gaja_kesari_bphs.full.nohouse@career"))      # fired from the Moon only
    assert not row_errors(mk("rule.yoga.gaja_kesari.full.nohouse@career"))           # counted from the Moon alone


# --- M10. The frozen texts and the tests would not catch these regressions ------------------------------------------

def test_m10_no_composed_sentence_on_any_variant_carries_a_slot_or_a_never_show_word(composed):
    from jyotish.client import never_show
    from jyotish.narrate import TIER_WORDS
    variants = {s["row"]["variant"] for c, p, s in composed if s["row"]}
    assert variants == {0, 1, 2}
    for c, p, s in composed:
        assert "{" not in s["text"] and "}" not in s["text"], s["text"]
        assert not never_show(s["text"]) and not TIER_WORDS.search(s["text"]), s["text"]
        assert s["text"][:1].isupper() and s["text"].endswith((".", "?")), s["text"]


def test_m10_the_frozen_turns_hold_every_variant():
    frozen = json.loads((ROOT / "tests" / "fixtures" / "layered_seven_turns.json").read_text())
    assert sorted(frozen["variants"]) == ["0", "1", "2"]
    assert len({json.dumps(t) for t in frozen["variants"].values()}) == 3        # three different answers


# --- M11. Any reviewer can approve bank rows --------------------------------------------------------------------------

def test_m11_only_the_astrologers_token_stores_a_bank_verdict(tmp_path, monkeypatch):
    import time
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import sessionmaker
    from jyotish.api import create_app
    from jyotish.conversation import OfflineTurnWriter
    from jyotish.db import BankReviewRow, issue_token, migrate
    from jyotish.reference import REFERENCE_LAT, REFERENCE_LON
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    url = f"sqlite:///{tmp_path / 'm11.db'}"
    with sessionmaker(migrate(url)).begin() as s:                       # `jyotish astrologer add` stores its hash
        token = issue_token(s, "astrologer", "astrologer-1")
    app = create_app(url, turn_writer=OfflineTurnWriter, reviewers={"tok-judge": "judge-1"}, astrologers={},
                     today=lambda: AS_OF)
    birth = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT,
             "lon": REFERENCE_LON, "node": "mean", "place": "Rewari, Haryana"}
    judge, astro = {"Authorization": "Bearer tok-judge"}, {"Authorization": f"Bearer {token}"}
    with TestClient(app) as c:
        sid = c.post("/sessions", json=birth).json()["id"]
        n = c.post(f"/sessions/{sid}/turns", json={"message": "how is my career"}).json()["n"]
        t = time.monotonic()
        while c.get(f"/sessions/{sid}/turns/{n}").json()["status"] not in ("done", "failed"):
            assert time.monotonic() - t < 90
            time.sleep(0.05)
        assert c.get(f"/sessions/{sid}/turns/{n}/worksheet", headers=judge).status_code == 200     # a reviewer reads
        assert c.get(f"/sessions/{sid}/turns/{n}/worksheet", headers=astro).status_code == 200     # so does he
        v = {"i": 0, "verdict": "right"}
        assert c.post(f"/sessions/{sid}/turns/{n}/worksheet/verdict", json=v, headers=judge).status_code == 401
        assert c.post(f"/sessions/{sid}/turns/{n}/worksheet/verdict", json=v, headers=astro).status_code == 200
    with sessionmaker(migrate(url))() as s:
        assert [r.reviewer_id for r in s.query(BankReviewRow)] == ["astrologer-1"]


def test_m11_the_cli_issues_an_astrologers_token(tmp_path, capsys):
    from jyotish.cli import main
    db = f"sqlite:///{tmp_path / 'c.db'}"
    with pytest.raises(SystemExit) as done:
        main(["astrologer", "add", "astrologer-1", "--database", db])
    assert done.value.code == 0 and "astrologer astrologer-1: token" in capsys.readouterr().out


# --- L1. "The strongest family terms" compares two different units ------------------------------------------------------

def test_l1_families_are_ranked_by_percentile_and_a_vote_with_no_term_at_the_middle(plans):
    from jyotish.plan import NO_TERM_PERCENTILE
    seen = 0
    for c, p in plans:
        for part, desc in (("helps", True), ("hard", False)):
            items = [i for i in p.items if i.part == part and i.area == p.areas[0]]
            ranks = [i.facts["ranked_at"] for i in items]
            assert ranks == sorted(ranks, reverse=desc)
            for i in items:
                fam = i.facts["family"]
                assert (i.facts["percentile"] is None) == (fam in ("arudha", "kp"))
                if i.facts["percentile"] is None:
                    assert i.facts["ranked_at"] == NO_TERM_PERCENTILE
                    seen += 1
    assert seen > 5                                  # arudha and KP are said, by percentile, not hidden by scale


# --- L2. Once polished, the worksheet and the chart wheel point at the wrong sentences --------------------------------

def test_l2_a_polished_sentence_lights_what_its_own_words_name_and_the_worksheet_says_it_is_composed(monkeypatch):
    from jyotish.conversation import answer_turn, focus_of, route_turn, worksheet
    c = _reference()
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_POLISH", "1")
    events = []
    m = "how is my career"
    doc = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="l2", polisher=_JoinPolisher(),
                      checker=_Checker(True), emit=events.append)
    assert doc["source"] == "polished" and len(doc["shown"]) < len(doc["composed"]["sentences"])
    texts = [e["text"] for e in events if e["type"] == "text"]
    lit = iter([e for e in events if e["type"] == "light" and e.get("stage") == "sentence"])
    for t in texts:
        f = focus_of(t, c)
        if f["planets"] or f["houses"]:
            e = next(lit)
            assert (e["planets"], e["houses"]) == (f["planets"], f["houses"])
    assert worksheet(doc)["told_is"] == "composed"
    js = (ROOT / "web" / "js" / "review-session.js").read_text()
    assert 'toldIs === "composed" ? "ws.composed"' in js


# --- L3. apply-reviews writes the bank inside the database transaction ---------------------------------------------------

def test_l3_a_bank_that_would_not_load_is_never_written_and_its_verdicts_stay_pending(tmp_path, monkeypatch):
    import jyotish.bank as bank
    from sqlalchemy.orm import sessionmaker
    from jyotish.db import BankReviewRow, migrate
    d, url = _verdict_db(tmp_path, [(1, "right", None)])
    before = {p.name: p.read_text() for p in d.glob("*.yaml")}
    real = bank.load_bank
    calls = []

    def failing(directory=None, strict=True):
        calls.append(Path(directory) if directory is not None else None)
        if len(calls) > 1:                                         # the first load is the bank read; then the check
            raise bank.BankError("the written bank does not stand")
        return real(directory, strict)
    monkeypatch.setattr(bank, "load_bank", failing)
    with pytest.raises(bank.BankError):
        bank.apply_reviews(url, d, today=AS_OF)
    assert {p.name: p.read_text() for p in d.glob("*.yaml")} == before        # nothing written in place
    assert calls[1] != d                                                       # the check read a staged copy
    with sessionmaker(migrate(url))() as s:
        assert s.query(BankReviewRow).one().applied_at is None                 # still pending: applied once, later
    monkeypatch.setattr(bank, "load_bank", real)
    assert bank.apply_reviews(url, d, today=AS_OF)["approved"]


# --- L4. A transient checker failure on the polished text is stored for the day ---------------------------------------

def test_l4_a_polish_refused_for_want_of_a_verdict_is_not_stored(monkeypatch):
    from jyotish.conversation import answer_turn, route_turn
    from jyotish.narrate import CheckResult, Proposition
    c = _reference()
    monkeypatch.setenv("JYOTISH_LAYERED", "1")
    monkeypatch.setenv("JYOTISH_POLISH", "1")

    class Unchecked:                                    # what ModelChecker returns after its retries fail
        def ask_one(self, sentence, data):
            return CheckResult(propositions=[Proposition(text="(unchecked)", supported=False, evidence="timeout")]), \
                {"kind": "checker", "unchecked": True}

    class Store:
        def __init__(self):
            self.rows = {}

        def get(self, key):
            return self.rows.get(key)

        def put(self, key, document, *, bank_version, birth_key=None):
            self.rows[key] = document
    store = Store()
    m = "how is my career"
    doc = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="l4", polisher=_JoinPolisher(),
                      checker=Unchecked(), store=store)
    assert doc["source"] == "composer" and "stored" not in doc and store.rows == {}
    refused = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="l4", polisher=_JoinPolisher(),
                          checker=_Checker(False), store=store)                    # a real refusal is stored
    assert refused["source"] == "composer" and refused["stored"]["served"] is False and len(store.rows) == 1


# --- L5. The scorecard's composer share is 100% by construction, and composed sentences have no correctness figure ----

def test_l5_the_composed_check_samples_bank_sentences_with_their_facts_and_its_report_is_committed():
    import importlib.util
    spec = importlib.util.spec_from_file_location("composed_check", ROOT / "scripts" / "composed_check.py")
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)
    rows = cc.sample(4, 2, 21)
    assert rows and all(r["sentence"] and r["data"]["facts"] and r["signature"] for r in rows)
    assert cc.sample(4, 2, 21) == rows                                       # the same sentences for the same seed
    report = json.loads(sorted((ROOT / "docs").glob("composed_check_*.json"))[-1].read_text())
    assert report["checked"] >= 100 and 0 < report["share"] <= 1 and report["checker"]


def test_l5_composes_is_the_turns_rule_and_a_question_with_no_area_keeps_the_writer():
    from jyotish.conversation import composes, route_turn
    c = _reference()
    assert composes(route_turn("how is my career", c))
    assert not composes(route_turn("what should I know", c))
    assert not composes(route_turn("will I die early?", c))


# --- L6. Wording a client would stumble on ------------------------------------------------------------------------------

def test_l6_the_wordings_the_review_named_are_gone_from_every_variant(composed):
    from jyotish.bank import load_bank
    text = " ".join(v for r in load_bank().rows for v in r.variants)
    assert "is not something this chart" not in text and "least favourable stretch in the chart" not in text
    assert "lies behind it." not in text and "among your twelve houses" not in text
    for c, p, s in composed:
        assert "the main planet of " not in s["text"], s["text"]
        assert not re.search(r"period of (\w+), within that of \1\b", s["text"]), s["text"]
        assert not re.search(r"^(?:Brothers, sisters and courage|Your \w+) (?:draws|is where|is an area)", s["text"])


def test_l6_a_lord_in_its_own_sub_period_is_said_as_one_planet():
    from jyotish.bank import load_bank
    from jyotish.plan import _period_item
    c = _reference()
    for d in (date(2026, 11, 15), date(2030, 1, 1), date(2041, 6, 1), date(2045, 6, 1), date(2060, 6, 1)):
        it = _period_item(c, "career", "your career", d)
        if it.facts["mahadasha"] == it.facts["antardasha"]:
            assert it.signature.endswith(".same") and "in its own sub-period" in it.engine
            break
    else:
        pytest.skip("no own sub-period among the dates tried")
    assert load_bank().fact("period.now.apart.same") is not None


def test_l6_a_fact_variant_no_check_supported_is_never_shown():
    from jyotish.bank import BankRow, fills
    r = BankRow(signature="period.now.touches.same", kind="fact", slots=["area"], drafted_by="t", drafted_on=AS_OF,
                variants=["A {area}.", "B {area}.", "C {area}."])
    assert r.refused() == {0, 1, 2} and not fills(r, {"area": "your career"})


# --- L7. Smaller readings to settle ----------------------------------------------------------------------------------

def test_l7_a_served_stored_answer_lights_the_chart_wheel_as_the_first_one_did(monkeypatch):
    from jyotish.conversation import answer_turn, route_turn
    c = _reference()
    monkeypatch.setenv("JYOTISH_LAYERED", "1")

    class Store:
        rows = {}

        def get(self, key):
            return dict(self.rows[key]) if key in self.rows else None

        def put(self, key, document, *, bank_version, birth_key=None):
            self.rows[key] = document
    store, m = Store(), "how is my career"
    lights = lambda ev: [(e["planets"], e["houses"]) for e in ev if e["type"] == "light" and e.get("stage") == "sentence"]
    first, again = [], []
    answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="l7", store=store, emit=first.append)
    doc = answer_turn(c, m, route_turn(m, c), as_of=AS_OF, session_key="l7", store=store, emit=again.append)
    assert doc["stored"]["served"] and lights(again) and len(lights(again)) == len(lights(first))
