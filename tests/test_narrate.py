"""Layer 7 narration, offline: the drafter replays tests/fixtures/narration_career.json."""

import json
from datetime import date
from pathlib import Path

import pytest

from jyotish.narrate import (
    CONFIG, NarrationError, ReadingDraft, findings, narrate, route, school_conflicts, validate,
)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "narration_career.json").read_text())
VALID = FIXTURE["drafts"][-1]          # the model's accepted draft (hand-authored until re-recorded)
AS_OF = date(2026, 10, 21)
# A deliberately bad first draft: "likely", an untagged claim, an untagged summary sentence.
INVALID = {"summary": "Career is likely to peak soon. The Sun and Mercury together in the 10th house form both Budhaditya yoga and a kendra-trikona Raja yoga [rule:yoga.kendra_trikona_raja]. Mars in its own sign in the 7th forms Ruchaka yoga, weakened by Saturn's aspect and its Marana Karaka Sthana [rule:yoga.ruchaka].", "areas": [{"name": "career", "claims": [{"finding_id": "yoga.budhaditya@lagna", "text": "The Sun and Mercury share Aquarius, the 10th house, which forms Budhaditya yoga."}, {"finding_id": "yoga.kendra_trikona_raja@lagna", "text": "The Sun, lord of the 4th, joins Mercury, lord of the 5th, in the 10th house, a kendra lord with a trikona lord [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12]."}]}]}


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
    d = Replay([INVALID, VALID])
    return narrate(chart, FIXTURE["question"], drafter=d, as_of=AS_OF), d


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
    assert validate("Mercury rules trade and trading careers [rule:yoga.ruchaka].", OK) == []
    assert validate("The KP family votes against career [vote:career.kp].", {"vote:career.kp"}) == []
    assert validate("Career.", OK) == []                       # no claim verb, no tag needed


# --- the reading -----------------------------------------------------------------------

def test_regenerates_until_valid(reading_and_drafter):
    reading, d = reading_and_drafter
    # INVALID says "likely" and has untagged sentences; the fixture draft is clean.
    assert reading.attempts == 2 and len(d.calls) == 2
    assert d.calls[0]["errors"] == [] and d.calls[1]["errors"]
    assert any("probability" in e for e in d.calls[1]["errors"])
    assert any("untagged claim" in e for e in d.calls[1]["errors"])


def test_gives_up_after_max_attempts(chart):
    bad = Replay([INVALID])
    with pytest.raises(NarrationError) as e:
        narrate(chart, FIXTURE["question"], drafter=bad, as_of=AS_OF)
    assert len(bad.calls) == CONFIG.max_attempts and e.value.errors


def test_model_sees_no_longitudes_and_no_experimental_fires(reading_and_drafter):
    _, d = reading_and_drafter
    sent = d.calls[0]["user"]
    assert "lon" not in json.loads(sent)["areas"][0]["findings"][0]
    offered = {f["finding_id"] for f in json.loads(sent)["areas"][0]["findings"]}
    assert {"vote:career.kp", "vote:career.house", "vote:career.panchanga"} <= offered
    assert "vote:career.arudha" not in offered                # arudha abstained (0): no finding
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
    assert kinds == ["rule"] * 4 + ["vote"] * 6
    for kind in ("rule", "vote"):
        keys = [(c.stability if c.stability is not None else 1.0) * c.confidence
                for c in career.claims if c.kind == kind]
        assert keys == sorted(keys, reverse=True)
    assert career.claims[0].cites[0] == "rule:yoga.kendra_trikona_raja"   # 1.0 x 0.6, the top fire
    assert career.claims[-1].cites == ["vote:career.kp"]       # stability 0.605 x 1.0
    assert all(c.confidence <= 1.0 for c in career.claims)     # 1 - rho clipped (KP's rho is -0.009)
    # The KP vote against career is narrated in words, as SPEC item 8 asks.
    kp = next(c for c in career.claims if c.cites == ["vote:career.kp"])
    assert "Ketu" in kp.text and "8th" in kp.text and kp.school == "kp" and kp.stability == pytest.approx(0.605)
    raja = next(c for c in career.claims if "rule:yoga.kendra_trikona_raja" in c.cites)
    assert raja.confidence == pytest.approx(1.0 * 0.6)       # scale x confidence_base
    ruchaka = next(c for c in career.claims if "rule:yoga.ruchaka" in c.cites)
    assert ruchaka.confidence == pytest.approx(0.408 * 0.7)
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
    r = narrate(chart, "What about money?", drafter=Replay([wealth_draft]), as_of=AS_OF)
    [w] = r.areas
    assert w.name == "wealth" and w.polarity == [] and chart.scored.areas["wealth"].polarity
    assert "finance" in r.disclaimers and w.disclaimer.startswith("This is a classical indication, not financial advice")
    assert w.school_conflicts and w.school_conflicts[0]["schools"] == ["parashari", "jaimini"]
    # Marriage has no rule-backed finding on this chart, so the only sentence the model may
    # write is one that makes no claim.
    m = narrate(chart, "Will I marry?", drafter=Replay([{"summary": "No rule-backed finding for marriage.", "areas": []}]),
                as_of=AS_OF)
    assert "third_party" in m.disclaimers and m.areas[0].disclaimer.startswith("This describes the relationship")


def test_unstable_findings_go_to_their_own_section(chart):
    shaky = chart.model_copy(deep=True)
    f = next(x for x in shaky.fired_rules if x.id == "yoga.budhaditya")
    f.stability = f.stability.model_copy(update={"time": 0.3})
    ok, held = findings(shaky, "career")
    assert "yoga.budhaditya@lagna" not in {x["finding_id"] for x in ok}
    assert [x["finding_id"] for x in held] == ["yoga.budhaditya@lagna"]
    draft = dict(VALID)
    draft = {"summary": "The Sun, lord of the 4th, joins Mercury, lord of the 5th, in the 10th house [rule:yoga.kendra_trikona_raja].",
             "areas": [{"name": "career", "claims": [c for c in draft["areas"][0]["claims"]
                                                     if c["finding_id"] != "yoga.budhaditya@lagna"]}]}
    r = narrate(shaky, FIXTURE["question"], drafter=Replay([draft]), as_of=AS_OF)
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


@pytest.mark.xfail(strict=True, reason=(
    "Known gap: the recorded claude-opus-5-5 draft does not name the basis. It says 'Mars rules "
    "several career houses from its own sign in the 7th' where SPEC Layer 7 item 8 wants 'Scorpio, "
    "the 10th from the Sun'. The validator does not enforce basis naming; strict, so this fails "
    "loudly once a re-recorded draft does name it."))
def test_fixture_lord_sentence_names_the_basis():
    lord = next(c for c in VALID["areas"][0]["claims"] if c["finding_id"] == "vote:career.lord")
    assert "Scorpio, the 10th from the Sun" in lord["text"] and "lord of the 7th" not in lord["text"]
