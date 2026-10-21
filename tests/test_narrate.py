"""Layer 7 narration, offline: the drafter replays the frozen first recording and its
hand-edited copy (tests/fixtures/), with the semantic checker stubbed."""

import json
from datetime import date
from pathlib import Path

import pytest

from jyotish.narrate import (
    CONFIG, NarrationError, ReadingDraft, findings, narrate, route, school_conflicts, validate,
)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

FIXTURES = Path(__file__).parent / "fixtures"
# The first live recording (claude-opus-5-5), frozen: the live recorder writes
# narration_career.json, so a re-run never changes what these tests assert.
RECORDED = json.loads((FIXTURES / "narration_career_opus55_r1.json").read_text())
EDITED = json.loads((FIXTURES / "narration_career_edited.json").read_text())  # two hand edits, see its note
FIXTURE = EDITED
QUESTION = RECORDED["question"]
VALID = EDITED["drafts"][-1]
AS_OF = date(2026, 10, 21)
# A deliberately bad draft: "likely", untagged sentences.
INVALID = {"summary": "Career is likely to peak soon. The Sun and Mercury together in the 10th house form a "
                      "kendra-trikona raja yoga [rule:yoga.kendra_trikona_raja].",
           "areas": [{"name": "career", "claims": [{"finding_id": "yoga.budhaditya@lagna",
                                                     "text": "The Sun and Mercury share Aquarius, which forms Budhaditya yoga."}]}]}


class StubChecker:
    """Offline stand-in for the semantic checker: supports every proposition unless a
    sentence is listed in `reject` (sentence substring -> unsupported proposition)."""

    def __init__(self, reject=None):
        self.reject = reject or {}
        self.calls = []
        self.last_meta = None

    def __call__(self, sentence, derivation):
        from jyotish.narrate import CheckResult, Proposition
        self.calls.append((sentence, derivation))
        bad = [Proposition(text=p, supported=False, evidence="not in the derivation")
               for frag, p in self.reject.items() if frag in sentence]
        return CheckResult(propositions=bad or [Proposition(text=sentence, supported=True, evidence="stub")])


class Replay:
    """A drafter that returns the fixture drafts in order and records what it was sent."""

    def __init__(self, drafts):
        self.drafts = [ReadingDraft(**d) for d in drafts]
        self.calls = []

    def __call__(self, system, user, errors):
        self.calls.append({"system": system, "user": user, "errors": list(errors)})
        return self.drafts[min(len(self.calls) - 1, len(self.drafts) - 1)]


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def reading_and_drafter(chart):
    d = Replay([RECORDED["drafts"][0], VALID])
    return narrate(chart, QUESTION, drafter=d, checker=StubChecker(), as_of=AS_OF), d


# --- the validator ---------------------------------------------------------------------

OK = {"rule:yoga.ruchaka", "text:BPHS/Santhanam-1984/75/1-2"}


@pytest.mark.parametrize("text,needle", [
    ("Mars forms Ruchaka yoga.", "untagged claim"),
    ("Mars forms Ruchaka yoga [rule:yoga.hamsa].", "not offered"),
    ("Mars [rule:yoga.ruchaka] forms Ruchaka yoga in the 7th house.", "must end"),
    ("Mars likely forms Ruchaka yoga [rule:yoga.ruchaka].", "probability"),
    ("There is a 70% chance it forms [rule:yoga.ruchaka].", "probability"),
    ("Mars definitely forms Ruchaka yoga [rule:yoga.ruchaka].", "confidence"),
    ("Mars in the 7th shows when you will die [rule:yoga.ruchaka].", "death"),
    ("Mars indicates a blood disorder [rule:yoga.ruchaka].", "medical"),
    ("Mars in the 7th indicates cancer [rule:yoga.ruchaka].", "medical"),
    ("Mars in the 7th shows cancers [rule:yoga.ruchaka].", "medical"),
    ("Mars favours buying stocks this year [rule:yoga.ruchaka].", "trade"),
    ("Mars says to sell your shares [rule:yoga.ruchaka].", "trade"),
    ("The KP vote [vote:career.house] is against career.", "must end"),
    ("Your partner will fall ill when Mars rules the 7th [rule:yoga.ruchaka].", "third_party"),
])
def test_validator_rejects(text, needle):
    errs = validate(text, OK)
    assert any(needle in e for e in errs), errs


def test_validator_accepts_tagged_claims_and_plain_lines():
    assert validate("Mars in its own sign forms Ruchaka yoga [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].", OK) == []
    # "trade" names a profession; only a buy/sell/invest verb with an instrument is advice.
    assert validate("Ruchaka yoga favours trade and trading careers [rule:yoga.ruchaka].", OK) == []
    assert validate("The KP family votes against career [vote:career.kp].", {"vote:career.kp"}) == []
    assert validate("Career.", OK) == []                       # no claim verb, no tag needed


# --- the reading -----------------------------------------------------------------------

def test_recorded_draft_is_rejected_then_edited_one_accepted(reading_and_drafter):
    # The claude-opus-5-5 draft fails SPEC Layer 7 item 11 in its summary: it names four votes
    # it does not cite, tags a timing sentence with the house vote, and mentions timing. It
    # was recorded before item 8 merged Ruchaka's two bases into one finding, and before KP
    # vote v2, under which the career KP vote abstains and is no finding: its two Ruchaka
    # claims and its KP claim carry unknown finding ids, and its summary cites the KP tag
    # that is no longer offered. Its other seven claims pass the validator. The hand-edited
    # draft is accepted on the second attempt.
    reading, d = reading_and_drafter
    assert reading.attempts == 2 and len(d.calls) == 2
    errs = d.calls[1]["errors"]
    unknown = [e for e in errs if e.startswith("unknown finding id")]
    assert unknown == ["unknown finding id 'yoga.ruchaka@lagna'", "unknown finding id 'yoga.ruchaka@sun'",
                       "unknown finding id 'vote:career.kp'"]
    errs = [e for e in errs if e not in unknown]
    assert sum(1 for e in errs if e.startswith("tag not offered for this finding: [vote:career.kp]")) == 1
    for fam in ("house", "karaka", "varga", "panchanga"):
        assert any(f"names the {fam} family but does not cite [vote:career.{fam}]" in e for e in errs), fam
    assert any("[vote:career.house] on a sentence that does not name the house family" in e for e in errs)
    assert any(e.startswith("timing language") for e in errs)
    from jyotish.narrate import sentences
    summary = sentences(RECORDED["drafts"][0]["summary"])
    assert len(errs) == 7 and all(any(x in e for x in summary) for e in errs)   # the claims were clean


def test_regenerates_until_valid(chart):
    d = Replay([INVALID, VALID])
    r = narrate(chart, QUESTION, drafter=d, checker=StubChecker(), as_of=AS_OF)
    assert r.attempts == 2 and d.calls[0]["errors"] == []
    assert any("probability" in e for e in d.calls[1]["errors"])
    assert any("untagged claim" in e for e in d.calls[1]["errors"])


def test_gives_up_after_max_attempts(chart):
    bad = Replay([INVALID])
    with pytest.raises(NarrationError) as e:
        narrate(chart, QUESTION, drafter=bad, checker=StubChecker(), as_of=AS_OF)
    assert len(bad.calls) == CONFIG.max_attempts and e.value.errors


def test_model_sees_no_longitudes_and_no_experimental_fires(reading_and_drafter):
    _, d = reading_and_drafter
    sent = d.calls[0]["user"]
    assert "lon" not in json.loads(sent)["areas"][0]["findings"][0]
    offered = {f["finding_id"] for f in json.loads(sent)["areas"][0]["findings"]}
    assert {"vote:career.house", "vote:career.panchanga"} <= offered
    assert "vote:career.arudha" not in offered                # arudha abstained (0): no finding
    assert "vote:career.kp" not in offered                    # KP v2 abstains: Ketu meets M and N at both levels
    assert "kendra_trikona_raja_weak" not in sent             # experimental: excluded
    assert "certain" in d.calls[0]["system"]                  # the instructions name the banned words


def test_schema_and_engine_words_verbatim(reading_and_drafter, chart):
    reading, _ = reading_and_drafter
    assert reading.as_of == "2026-10-21" and reading.weights == "classical-1.0" and reading.model == CONFIG.model
    [career] = reading.areas
    src = chart.scored.areas["career"]
    assert career.tier == src.tier and career.stability == src.stability       # verbatim
    assert career.probability is None and career.calibrated is False and career.bin_n == 0
    assert career.score_classical == src.score_classical
    for c in career.claims:
        assert c.cites and all(t.split(":", 1)[0] in ("rule", "text", "vote") for t in c.cites)
    # Two groups (SPEC Layer 7 item 4): rule fires first, then votes, each ordered by
    # stability x its own confidence; the two scales are never ranked against each other.
    kinds = [c.kind for c in career.claims]
    assert kinds == ["rule"] * 3 + ["vote"] * 5             # Ruchaka: one claim, two bases; KP abstains
    for kind in ("rule", "vote"):
        keys = [(c.stability if c.stability is not None else 1.0) * c.confidence
                for c in career.claims if c.kind == kind]
        assert keys == sorted(keys, reverse=True)
    assert career.claims[0].cites[0] == "rule:yoga.kendra_trikona_raja"   # 1.0 x 0.6, the top fire
    # The varga vote is last: its weight is 1 - rho times 0.5 + 0.5 x consistency (5 of 7).
    assert career.claims[-1].cites == ["vote:career.varga"]
    from jyotish.scoring import family_rho
    assert career.claims[-1].confidence == pytest.approx((1 - family_rho()["varga"]) * (0.5 + 0.5 * 5 / 7))
    assert all(c.confidence <= 1.0 for c in career.claims)     # 1 - rho clipped
    assert career.school_conflicts == []                       # KP abstains: no school disagrees
    raja = next(c for c in career.claims if "rule:yoga.kendra_trikona_raja" in c.cites)
    assert raja.confidence == pytest.approx(1.0 * 0.6)       # scale x confidence_base
    ruchaka = next(c for c in career.claims if "rule:yoga.ruchaka" in c.cites)
    assert ruchaka.confidence == pytest.approx(0.408 * 0.7) and ruchaka.basis == "lagna, sun"
    assert {"text:BPHS/Santhanam-1984/75/1-2", "text:Phaladeepika/Sastri-1937/6/1"} <= set(ruchaka.cites)
    assert reading.summary.driver_planet == chart.scored.driver.driver
    assert reading.summary.top_areas == list(chart.scored.top)
    assert reading.summary.current_period == "Jupiter-Mercury"                   # Vimshottari on 2026-10-21
    assert {r["id"] for r in reading.fired_rules} >= {"yoga.ruchaka", "yoga.budhaditya"}
    assert all(r["id"] != "yoga.kendra_trikona_raja_weak" for r in reading.fired_rules)


def test_when_question_gets_engine_windows(reading_and_drafter):
    reading, _ = reading_and_drafter
    area = reading.areas[0]
    ws = area.windows
    assert len(ws) == 3 and all("2026-10-21" <= w.start < w.end <= "2036-10-21" for w in ws)
    assert ws[0].why[0]["kind"] == "dasha" and ws[-1].why[-1]["kind"] == "transit"
    for w in ws + [area.avoid_window]:
        assert set(w.q_terms) and 0 <= w.t <= 1 and w.relevant_systems and w.strongest_piece
        assert w.score == pytest.approx(0.6 * w.q + 0.4 * w.t, abs=2e-3)
    assert area.avoid_window.why[0]["lords"] == ["Jupiter", "Ketu"]
    assert any(w.truncated for w in ws)                       # Jupiter-Mercury from 2026-10-21


def test_polarity_only_for_top_three_and_disclaimers(chart):
    # Wealth is not in the top three, so its flags are not narrated; it carries the finance
    # disclaimer and names the Jaimini family's disagreement with the Parashari ones.
    wealth_draft = {"summary": "Venus in Pisces and Jupiter in Taurus exchange signs, linking the 1st and "
                               "11th houses [rule:yoga.parivartana].", "areas": [{"name": "wealth", "claims": []}]}
    r = narrate(chart, "What about money?", drafter=Replay([wealth_draft]), checker=StubChecker(), as_of=AS_OF)
    [w] = r.areas
    assert w.name == "wealth" and w.polarity == [] and chart.scored.areas["wealth"].polarity
    assert "finance" in r.disclaimers and w.disclaimer.startswith("This is a classical indication, not financial advice")
    assert w.school_conflicts and w.school_conflicts[0]["schools"] == ["parashari", "jaimini"]
    # Marriage has no rule-backed finding on this chart, so the only sentence the model may
    # write is one that makes no claim.
    m = narrate(chart, "Will I marry?", drafter=Replay([{"summary": "No rule-backed finding for marriage.", "areas": []}]),
                checker=StubChecker(), as_of=AS_OF)
    assert "third_party" in m.disclaimers and m.areas[0].disclaimer.startswith("This describes the relationship")


def test_unstable_findings_go_to_their_own_section(chart):
    shaky = chart.model_copy(deep=True)
    f = next(x for x in shaky.fired_rules if x.id == "yoga.budhaditya")
    f.stability = f.stability.model_copy(update={"time": 0.3})
    ok, held = findings(shaky, "career")
    assert "yoga.budhaditya@lagna" not in {x["finding_id"] for x in ok}
    assert [x["finding_id"] for x in held] == ["yoga.budhaditya@lagna"]
    draft = dict(VALID)
    draft = {"summary": "The Sun, lord of the 4th, joins Mercury, lord of the 5th, in the 10th house, a kendra-trikona "
                        "raja yoga [rule:yoga.kendra_trikona_raja].",
             "areas": [{"name": "career", "claims": [c for c in draft["areas"][0]["claims"]
                                                     if c["finding_id"] != "yoga.budhaditya@lagna"]}]}
    r = narrate(shaky, QUESTION, drafter=Replay([draft]), checker=StubChecker(), as_of=AS_OF)
    assert {"area": "career", "rule": "yoga.budhaditya", "basis": "lagna", "stability": 0.3} in r.depends_on_birth_time
    assert r.unstable == [{"id": "yoga.budhaditya", "basis": "lagna", "scale": 0.9, "stability": 0.3}]


def test_routing():
    class C:
        class scored:
            top = ["health", "career", "marriage"]
    assert route("When will I change jobs?", C) == (["career"], True)
    assert route("Tell me about my chart", C) == (["health", "career", "marriage"], False)


def test_vote_rows_name_their_basis(chart):
    d = chart.scored.areas["career"].vote_details
    for family in ("house", "lord"):
        assert all(r["basis"] in ("lagna", "moon", "sun") and 1 <= r["house"] <= 12 for r in d[family])
    scorpio = {(r["basis"], r["house"]) for r in d["lord"] if r["sign"] == "Scorpio"}
    assert ("sun", 10) in scorpio                             # the 10th from the Sun
    lagna7 = next(r for r in d["lord"] if r["basis"] == "lagna" and r["sign"] == "Scorpio")
    assert lagna7["house"] == 7 and lagna7["bhavat_bhavam_of"] == 10
    assert all(r["basis"] == "lagna" for r in d["karaka"] + d["kp"])
    assert {"basis": "sun", "house": 10} in d["panchanga"][0]["rules"]     # Mars




# --- SPEC Layer 7 item 11 -----------------------------------------------------------

VOTES = {"house": "vote:career.house", "lord": "vote:career.lord", "kp": "vote:career.kp",
         "karaka": "vote:career.karaka"}


@pytest.mark.parametrize("text,allowed,needle", [
    ("Career leans favourably here [vote:career.kp].", {"vote:career.kp"}, "does not name the kp family"),
    ("The KP vote is against career, while the karaka vote is for it [vote:career.kp].",
     {"vote:career.kp", "vote:career.karaka"}, "names the karaka family but does not cite"),
    ("Mars in its own sign gives courage [rule:yoga.ruchaka].", {"rule:yoga.ruchaka"}, "names none of ['Ruchaka']"),
    ("Ruchaka yoga matters most in the coming years [rule:yoga.ruchaka].", {"rule:yoga.ruchaka"}, "timing"),
    ("The engine places Ruchaka yoga first [rule:yoga.ruchaka].", {"rule:yoga.ruchaka"}, "timing"),
    ("Ruchaka yoga is strongest in 2030 [rule:yoga.ruchaka].", {"rule:yoga.ruchaka"}, "timing"),
])
def test_item_11_rejects(text, allowed, needle):
    errs = validate(text, allowed, offered_votes=VOTES)
    assert any(needle in e for e in errs), errs


def test_item_11_accepts_ordinary_words():
    # "house", "lord" and "marana karaka" in a rule claim do not name a family; a vote claim
    # that names its own family cites it.
    assert validate("Mars in its own sign in the 7th house, lord of the 7th and 12th, forms Ruchaka yoga, "
                    "weakened by a marana karaka placement [rule:yoga.ruchaka].",
                    {"rule:yoga.ruchaka"}, offered_votes=VOTES) == []
    assert validate("The KP vote is against career: the 10th cusp lies in the Moon's star, and its sub-lord Ketu "
                    "sits in the 8th house [vote:career.kp].", {"vote:career.kp"}, offered_votes=VOTES) == []
    assert validate("The house, lord and karaka votes lean for career [vote:career.house] [vote:career.lord] "
                    "[vote:career.karaka].", set(VOTES.values()), offered_votes=VOTES) == []


def test_rule_names_default_and_listed():
    from jyotish.narrate import rule_names
    assert rule_names("yoga.kendra_trikona_raja") == ["raja yoga", "kendra-trikona", "kendra trikona"]
    assert rule_names("yoga.unknown_thing") == ["unknown thing"]       # default: the id's last segment
    from jyotish.rules import load_rules
    assert all(r.data.get("names") for r in load_rules())               # all twelve carry names


# --- SPEC Layer 7 item 10: the checker ------------------------------------------------

def test_checker_rejection_goes_back_to_the_writer(chart):
    from jyotish.narrate import sentences
    # The recorded varga sentence says Jupiter and the Sun "score poorly" in the D10: true of
    # v1's agreement score, false of v2's derivation (both are in friendly signs there). The
    # checker marks that unsupported; the writer gets it back.
    recorded = next(c["text"] for c in RECORDED["drafts"][0]["areas"][0]["claims"]
                    if c["finding_id"] == "vote:career.varga")
    first = json.loads(json.dumps(VALID))
    for c in first["areas"][0]["claims"]:
        if c["finding_id"] == "vote:career.varga":
            c["text"] = recorded
    checker = StubChecker(reject={"Jupiter and the Sun score poorly": "Jupiter and the Sun score poorly in the D10"})
    d = Replay([first, VALID])
    rec = []
    r = narrate(chart, QUESTION, drafter=d, checker=checker, as_of=AS_OF, recording=rec)
    assert r.attempts == 2
    assert any("unsupported by the derivation of vote:career.varga" in e and "score poorly in the D10" in e
               for e in d.calls[1]["errors"])
    # On every attempt: one check per tagged summary sentence, then one per claim, each with
    # only the derivations it may draw on (never the question).
    n_summary = len(sentences(VALID["summary"]))
    assert len(checker.calls) == 2 * (n_summary + len(VALID["areas"][0]["claims"]))
    sentence, derivation = checker.calls[n_summary]
    assert QUESTION not in derivation and '"finding_id"' in derivation
    kinds = [e["kind"] for e in rec]
    assert kinds.count("writer") == 2 and kinds.count("checker") == len(checker.calls)
    assert rec[0]["validator_errors"] == [] and rec[0]["attempt"] == 1
    assert not any("unsupported" in c.text for a in r.areas for c in a.claims)   # never narrated


def test_recorder_saves_call_metadata(chart):
    """AnthropicDrafter / AnthropicChecker against a fake SDK client: request id, usage, model,
    effort and timestamp are recorded for every call, rejected drafts and checks included."""
    from types import SimpleNamespace
    from jyotish.narrate import AnthropicChecker, AnthropicDrafter, CheckResult, Proposition, ReadingDraft

    class Usage:
        def __init__(self, i, o):
            self.input_tokens, self.output_tokens = i, o

        def model_dump(self):
            return {"input_tokens": self.input_tokens, "output_tokens": self.output_tokens}

    drafts = [ReadingDraft(**RECORDED["drafts"][0]), ReadingDraft(**VALID)]
    n = {"w": 0, "c": 0}

    def parse(**kw):
        if kw["output_format"] is ReadingDraft:
            out = drafts[min(n["w"], 1)]
            n["w"] += 1
            rid = f"req_writer_{n['w']}"
        else:
            out = CheckResult(propositions=[Proposition(text="ok", supported=True, evidence="derivation")])
            n["c"] += 1
            rid = f"req_check_{n['c']}"
        return SimpleNamespace(parsed_output=out, stop_reason="end_turn", content=[], _request_id=rid,
                               model=kw["model"], usage=Usage(100, 20))

    async def aparse(**kw):
        return parse(**kw)

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse)))
    aclient = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=aparse)))
    rec = []
    r = narrate(chart, QUESTION, drafter=AnthropicDrafter(CONFIG, client=client),
                checker=AnthropicChecker(CONFIG, client=client, async_client=aclient), as_of=AS_OF, recording=rec)
    assert r.attempts == 2
    writers = [e for e in rec if e["kind"] == "writer"]
    checks = [e for e in rec if e["kind"] == "checker"]
    assert [w["request_id"] for w in writers] == ["req_writer_1", "req_writer_2"]
    assert writers[0]["validator_errors"] and writers[1]["validator_errors"] == []   # rejected one kept
    from jyotish.narrate import sentences
    assert len(checks) == len(sentences(VALID["summary"])) + len(VALID["areas"][0]["claims"])
    assert CONFIG.effort == "medium" and CONFIG.checker_effort == "high"
    for e in rec:
        assert e["model"] == CONFIG.model
        assert e["effort"] == (CONFIG.effort if e["kind"] == "writer" else CONFIG.checker_effort)
        assert e["usage"] == {"input_tokens": 100, "output_tokens": 20} and e["timestamp"].endswith("+00:00")
        assert e["seconds"] >= 0


# --- SPEC Layer 7 items 8 and 10, as revised after the first checked run ---------------

def test_rule_fires_across_bases_are_one_finding(chart):
    ok, _ = findings(chart, "career")
    ids = [f["finding_id"] for f in ok if f["kind"] == "rule"]
    assert ids == ["yoga.budhaditya@lagna", "yoga.kendra_trikona_raja@lagna", "yoga.ruchaka@lagna+sun"]
    r = next(f for f in ok if f["rule_id"] == "yoga.ruchaka")
    assert r["bases"] == ["lagna", "sun"] and r["planets"] == ["Mars"]
    assert [(x["basis"], x["nodes"]) for x in r["fires"]] == [("lagna", ["Mars", "H7"]), ("sun", ["Mars", "H10"])]
    assert set(r["allowed_tags"]) == {"rule:yoga.ruchaka", "text:BPHS/Santhanam-1984/75/1-2",
                                      "text:Phaladeepika/Sastri-1937/6/1"}


def test_merged_finding_takes_the_minimum_and_splits_at_half(chart):
    def with_sun_fire(time, scale):
        c = chart.model_copy(deep=True)
        f = next(x for x in c.fired_rules if x.id == "yoga.ruchaka" and x.basis == "sun")
        f.stability = f.stability.model_copy(update={"time": time})
        f.scale = scale
        return c
    ok, held = findings(with_sun_fire(0.7, 0.3), "career")
    r = next(f for f in ok if f["rule_id"] == "yoga.ruchaka")
    assert r["finding_id"] == "yoga.ruchaka@lagna+sun"
    assert r["stability"] == 0.7 and r["confidence"] == pytest.approx(0.3 * 0.7)      # min across bases
    # A basis under 0.5 goes to "depends on exact birth time" alone; the stable one is narrated.
    ok, held = findings(with_sun_fire(0.3, 0.408), "career")
    assert "yoga.ruchaka@lagna" in {f["finding_id"] for f in ok}
    assert [f["finding_id"] for f in held] == ["yoga.ruchaka@sun"]


def test_summary_sentences_are_checked_against_the_findings_they_cite(chart):
    from jyotish.narrate import sentences
    checker = StubChecker(reject={"oriented toward authority": "the yoga is oriented toward authority"})
    d = Replay([VALID, VALID])
    rec = []
    with pytest.raises(NarrationError) as e:
        narrate(chart, QUESTION, drafter=d, checker=checker, as_of=AS_OF, recording=rec)
    # The one rejected word is in the summary only, and it sends the draft back every time.
    assert any("unsupported by the derivations of yoga.kendra_trikona_raja@lagna (summary)" in x
               and "the yoga is oriented toward authority" in x for x in d.calls[1]["errors"])
    assert e.value.errors and len(d.calls) == CONFIG.max_attempts
    summary = [x for x in rec if x["kind"] == "checker" and x["finding_id"] == "summary"]
    assert len(summary) == CONFIG.max_attempts * len(sentences(VALID["summary"]))
    # Each summary sentence sees the union of its cited findings' derivations, and only those.
    five = next(x for x in summary if "[vote:career.panchanga]" in x["sentence"])
    assert five["findings"] == [f"vote:career.{f}" for f in ("house", "lord", "karaka", "varga", "panchanga")]
    data = json.loads(next(dv for s, dv in checker.calls if s == five["sentence"]))
    assert [f["finding_id"] for f in data["findings"]] == five["findings"] and QUESTION not in json.dumps(data)


def test_writer_prompt_says_each_claim_stands_alone():
    from jyotish.narrate import SYSTEM_PROMPT
    for word in ('"again"', '"the same"', '"also"', '"as above"'):
        assert word in SYSTEM_PROMPT
    assert "from the lagna and from the Sun" in " ".join(SYSTEM_PROMPT.split())


def test_merged_finding_marks_its_sudarshana_bases(chart):
    ok, _ = findings(chart, "career")
    r = next(f for f in ok if f["rule_id"] == "yoga.ruchaka")
    assert r["sudarshana_bases"] == ["sun"]
    assert [(x["basis"], x["sudarshana"], x["cited_to"]) for x in r["fires"]] == [
        ("lagna", False, "rule and text"), ("sun", True, "rule")]
    # With no lagna fire, the text tags (verses from the ascendant) are not offered.
    c = chart.model_copy(deep=True)
    c.fired_rules = [x for x in c.fired_rules if not (x.id == "yoga.ruchaka" and x.basis == "lagna")]
    ok, _ = findings(c, "career")
    sun_only = next(f for f in ok if f["rule_id"] == "yoga.ruchaka")
    assert sun_only["finding_id"] == "yoga.ruchaka@sun" and sun_only["allowed_tags"] == ["rule:yoga.ruchaka"]


def test_fixture_checker_replays_recorded_verdicts():
    from jyotish.narrate import FixtureChecker
    rec = json.loads((FIXTURES / "narration_career.json").read_text())
    checker = FixtureChecker(rec)
    rejected = next(c for c in rec["calls"] if c["kind"] == "checker"
                    and not all(p["supported"] for p in c["result"]["propositions"]))
    assert not all(p.supported for p in checker(rejected["sentence"], "").propositions)
    assert checker("A sentence never recorded [rule:yoga.ruchaka].", "").propositions == []
    assert checker.unchecked == {"A sentence never recorded [rule:yoga.ruchaka]."}


def test_windows_only_for_areas_the_question_names(chart):
    # The page's extra areas (the top three) carry no windows; an area the question names does.
    blank = {"summary": "Career.", "areas": []}
    r = narrate(chart, "When will my career and marriage improve?", drafter=Replay([blank]), checker=StubChecker(),
                as_of=AS_OF, areas=["career", "marriage", "health"])
    assert {a.name: bool(a.windows) for a in r.areas} == {"career": True, "marriage": True, "health": False}
    r = narrate(chart, QUESTION, drafter=Replay([blank]), checker=StubChecker(), as_of=AS_OF,
                areas=["career", "health", "marriage"])
    assert {a.name: bool(a.windows) for a in r.areas} == {"career": True, "health": False, "marriage": False}


# --- speed (SPEC Phase 4, item 3): the checks of an attempt run concurrently -------------

def _slow_async_client(delay, log):
    """A fake async SDK client: each parse takes `delay` seconds and logs how many are in flight."""
    import asyncio
    from types import SimpleNamespace
    from jyotish.narrate import CheckResult, Proposition
    state = {"now": 0}

    async def parse(**kw):
        state["now"] += 1
        log.append(state["now"])
        await asyncio.sleep(delay)
        state["now"] -= 1
        text = kw["messages"][0]["content"].split("\n")[1]
        return SimpleNamespace(parsed_output=CheckResult(propositions=[Proposition(text=text, supported=True,
                                                                                   evidence="fake")]),
                               stop_reason="end_turn", _request_id="req", model=kw["model"], usage=None)
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse)))


def test_checker_calls_run_concurrently_in_order():
    import time
    from dataclasses import replace
    from types import SimpleNamespace
    from jyotish.narrate import AnthropicChecker
    items = [(f"sentence {i}", "{}") for i in range(12)]
    log = []
    checker = AnthropicChecker(CONFIG, client=SimpleNamespace(), async_client=_slow_async_client(0.2, log))
    t = time.perf_counter()
    out = checker.check_many(items)
    took = time.perf_counter() - t
    assert took < 0.2 * 3                                     # 12 calls of 0.2 s, about one call's time
    assert [r.propositions[0].text for r, _ in out] == [s for s, _ in items]   # results in the order asked
    assert max(log) == 12 and all(m["seconds"] >= 0.2 for _, m in out)
    # The limit holds: no more than checker_concurrency in flight.
    log.clear()
    limited = AnthropicChecker(replace(CONFIG, checker_concurrency=4), client=SimpleNamespace(),
                               async_client=_slow_async_client(0.05, log))
    limited.check_many(items)
    assert max(log) == 4


def test_checker_concurrency_one_is_sequential_and_works_inside_a_running_loop():
    import asyncio
    from dataclasses import replace
    from types import SimpleNamespace
    from jyotish.narrate import AnthropicChecker, CheckResult, Proposition
    calls = []

    def parse(**kw):
        calls.append(kw["output_config"]["effort"])
        return SimpleNamespace(parsed_output=CheckResult(propositions=[]), stop_reason="end_turn",
                               _request_id="r", model=kw["model"], usage=None)
    seq = AnthropicChecker(replace(CONFIG, checker_concurrency=1),
                           client=SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse))))
    assert len(seq.check_many([("a", "{}"), ("b", "{}")])) == 2 and calls == [CONFIG.checker_effort] * 2

    async def inside():                                       # e.g. a web server's event loop
        log = []
        c = AnthropicChecker(CONFIG, client=SimpleNamespace(), async_client=_slow_async_client(0.01, log))
        return c.check_many([("a", "{}"), ("b", "{}")])
    assert len(asyncio.run(inside())) == 2


def test_cancer_the_sign_is_not_the_disease():
    # Capitalised Cancer is the sign and passes; lowercase cancer is the disease and is rejected.
    votes = {"arudha": "vote:marriage.arudha", "house": "vote:career.house"}
    assert validate("The arudha vote is against marriage: UL2 in Cancer holds no benefic [vote:marriage.arudha].",
                    {"vote:marriage.arudha"}, offered_votes=votes) == []
    assert validate("The house vote is for career: the 3rd in Cancer is strong in bhava bala [vote:career.house].",
                    {"vote:career.house"}, offered_votes=votes) == []
    errs = validate("The house vote is for career, though Saturn shows cancer in the 3rd [vote:career.house].",
                    {"vote:career.house"}, offered_votes=votes)
    assert errs == ["medical language ('cancer') in 'The house vote is for career, though Saturn shows cancer in "
                    "the 3rd [vote:career.house].'"]
    # The rest of the medical list stays case-insensitive.
    assert any("medical" in e for e in validate("Mars shows a Disorder [rule:yoga.ruchaka].", {"rule:yoga.ruchaka"}))
