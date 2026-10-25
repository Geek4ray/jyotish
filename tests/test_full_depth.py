"""Depth full, parts 2 and 3: the writer's settings (extended thinking, the highest effort, the
model and effort recorded), the per-area analysis (assessment, timing, what the chart does not
say), the synthesis rule in the checker, and the [tradition:] tag's limits. Offline: the writer is
replayed and the checker stubbed."""

import json
from datetime import date
from types import SimpleNamespace

import pytest

from jyotish.narrate import (
    CHECKER_PROMPT, CONFIG, AnthropicChecker, AnthropicDrafter, CheckResult, Proposition, ReadingDraft, narrate,
    system_prompt, writer_config,
)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
QUESTION = "How will my career go?"

ASSESSMENT = ("The strongest support is the varga family [fact:areas.career.contributions.strongest]. "
              "Mars is in its own sign in the 7th, so Mars is dignified in a kendra "
              "[fact:planets.Mars.dignity] [fact:planets.Mars.house].")
TIMING = "The current Vimshottari period is Jupiter-Mercury-Mercury [fact:vimshottari.current]."
NOT_SAID = "The KP family abstains on career [fact:areas.career.votes.kp.vote]."
NOT_DECIDED = "Which kind of work suits you is not settled by anything here [fact:not_computed.question_routing]."


def draft(assessment=ASSESSMENT, timing=TIMING, not_said=NOT_SAID, summary="", not_decided=NOT_DECIDED):
    # At depth full the first call writes no summary (the client's layer does); `summary` is kept
    # for the tests that show what a drafted one is refused or ignored for.
    return {"summary": summary, "areas": [{"name": "career", "claims": [], "analysis": {
        "assessment": assessment, "timing": timing, "not_said_client": [not_decided] if not_decided else None,
        "not_said_astrologer": [not_said] if not_said else None}}]}


class Replay:
    def __init__(self, *drafts):
        self.drafts = [ReadingDraft(**d) for d in drafts]
        self.calls = []
        self.last_meta = None

    def __call__(self, system, user, errors):
        self.calls.append({"system": system, "errors": list(errors)})
        self.last_meta = {"kind": "writer", "usage": {"input_tokens": 1000, "output_tokens": 200,
                                                      "cache_read_input_tokens": 0}, "seconds": 1.5}
        return self.drafts[min(len(self.calls), len(self.drafts)) - 1]


class SynthesisStub:
    """The checker's synthesis rule, as a stub: a sentence marked `synthesis` passes when each of
    its cited facts is stated in the data and its conclusion (the clause after ", so ") follows
    from them together, which the stub reads from `follows` (conclusion -> True or False); a
    conclusion it does not know follows from none of the cited facts and is rejected. Every other
    sentence passes."""

    def __init__(self, follows=None):
        self.follows = follows or {}
        self.calls = []
        self.last_meta = None

    def __call__(self, sentence, data):
        d = json.loads(data)
        self.calls.append((sentence, d))
        if not d.get("synthesis"):
            return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])
        premises = [Proposition(text=f"{p} is {v!r}", supported=True, evidence=p) for p, v in d.get("facts", {}).items()]
        conclusion = sentence.split(", so ", 1)[1].split(" [", 1)[0] if ", so " in sentence else sentence
        ok = self.follows.get(conclusion, False)
        return CheckResult(propositions=premises + [Proposition(
            text=conclusion, supported=ok, evidence="follows from the cited facts together" if ok
            else "no cited fact supports this conclusion")])


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def run(chart, *drafts, checker=None, rec=None, **kw):
    return narrate(chart, QUESTION, drafter=Replay(*drafts), checker=checker or SynthesisStub(
        {"Mars is dignified in a kendra": True}), as_of=AS_OF, areas=["career"], depth="full", recording=rec, **kw)


# --- the writer's settings --------------------------------------------------------------

def test_full_depth_writer_thinks_at_xhigh_by_default():
    # xhigh since the review of 2026-10-23: at max, B's first attempt thought through all 128,000 tokens
    assert CONFIG.full_effort == "xhigh" and CONFIG.full_thinking == "adaptive"
    w = writer_config(CONFIG, "full")
    assert (w.effort, w.thinking, w.max_tokens) == ("xhigh", "adaptive", CONFIG.full_max_tokens)
    assert writer_config(CONFIG, "full", effort="max").effort == "max"          # max by flag
    a = writer_config(CONFIG, "astrologer")
    assert (a.effort, a.thinking) == (CONFIG.effort, None)
    o = writer_config(CONFIG, "full", model="claude-sonnet-5-5", effort="high")
    assert (o.model, o.effort, o.checker_model) == ("claude-sonnet-5-5", "high", CONFIG.checker_model)
    with pytest.raises(ValueError):
        writer_config(CONFIG, "full", effort="maximum")
    with pytest.raises(ValueError):
        writer_config(CONFIG, "full", model="gpt-5")


def test_the_drafter_sends_thinking_and_effort_and_the_checker_keeps_its_own_model():
    seen = {}
    out = ReadingDraft(summary="x", areas=[])
    content = [SimpleNamespace(type="thinking", thinking="Weighing Mars against the 10th."),
               SimpleNamespace(type="text", text="{}")]

    class Stream:
        def __init__(self, **kw):
            seen["writer"] = kw

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get_final_message(self):
            return SimpleNamespace(parsed_output=out, stop_reason="end_turn", content=content, usage=None, model="m")

    def parse(**kw):
        seen["checker"] = kw
        return SimpleNamespace(parsed_output=CheckResult(propositions=[]), stop_reason="end_turn", content=[],
                               usage=None, model=kw["model"])

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=Stream, parse=parse)))
    d = AnthropicDrafter(writer_config(CONFIG, "full", model="claude-fable-5-1"), client=client)
    d("system", "payload", [])
    assert seen["writer"]["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert seen["writer"]["output_config"] == {"effort": "xhigh"} and seen["writer"]["model"] == "claude-fable-5-1"
    assert d.last_meta["thinking"] == "Weighing Mars against the 10th." and d.last_meta["effort"] == "xhigh"
    AnthropicChecker(writer_config(CONFIG, "full", model="claude-fable-5-1"), client=client)("s", "{}")
    assert seen["checker"]["model"] == CONFIG.checker_model and seen["checker"]["output_config"] == {"effort": "high"}
    assert "thinking" not in seen["checker"]


def test_model_effort_and_usage_are_recorded_in_the_reading(chart):
    r = run(chart, draft(), writer_model="claude-sonnet-5-5", writer_effort="xhigh")
    assert r.model == "claude-sonnet-5-5"
    assert r.writer == {"model": "claude-sonnet-5-5", "effort": "xhigh", "thinking": "adaptive",
                        "max_tokens": CONFIG.full_max_tokens}
    assert r.checker == {"model": CONFIG.checker_model, "effort": CONFIG.checker_effort}
    # One writer call and one call of the client's layer (EchoClient: 100 input tokens), counted together
    # under the writer and apart under `client`.
    assert r.usage["writer"]["calls"] == 2 and r.usage["writer"]["input_tokens"] == 1100
    assert r.usage["client"]["calls"] == 1 and r.usage["client"]["attempts"] == 1
    # two assessment sentences, timing, the two not-said lists; then the paragraph, the when and the summary
    assert r.usage["checker"]["calls"] == 8
    assert r.usage["wall_seconds"] >= 0


# --- the analysis ---------------------------------------------------------------------------

def test_the_prompt_asks_for_the_analysis_and_states_the_synthesis_rule():
    p = system_prompt("full")
    for words in ("`assessment`", "strongest support and the weakest", "resolve the contradiction explicitly",
                  "rank what matters most", "`timing`", "`not_said_client`", "`not_said_astrologer`",
                  "Leave `summary` empty", "synthesis sentence",
                  "each cited fact is true and the conclusion follows from them together"):
        assert words in p, words
    assert "`assessment`" not in system_prompt("astrologer")


def test_each_area_has_three_checked_sections(chart):
    r = run(chart, draft())
    a = r.areas[0]
    assert a.analysis == {"assessment": ASSESSMENT, "timing": TIMING, "not_said_client": NOT_DECIDED,
                          "not_said_astrologer": NOT_SAID}
    assert "fact:vimshottari.current" in a.analysis_cites and "fact:planets.Mars.house" in a.analysis_cites
    assert not [g for g in a.narration_gaps if g["kind"] == "analysis"]
    assert r.synthesis_sentences == 1                       # the kendra sentence: two facts, one conclusion


def test_a_missing_section_is_refused_and_regenerated(chart):
    w = Replay(draft(timing=""), draft())
    r = narrate(chart, QUESTION, drafter=w, checker=SynthesisStub({"Mars is dignified in a kendra": True}),
                as_of=AS_OF, areas=["career"], depth="full")
    assert any("no timing for career" in e for e in w.calls[1]["errors"])
    assert r.areas[0].analysis["timing"] == TIMING and r.attempts == 2


def test_the_engine_keeps_the_tier(chart):
    w = Replay(draft(assessment="Career support is strong [fact:areas.career.tier]."), draft())
    narrate(chart, QUESTION, drafter=w, checker=SynthesisStub({"Mars is dignified in a kendra": True}), as_of=AS_OF,
            areas=["career"], depth="full")
    assert any("tier language ('strong') in the career assessment" in e for e in w.calls[1]["errors"])


# --- the synthesis rule ----------------------------------------------------------------------

def test_checker_prompt_states_the_synthesis_rule():
    assert "`synthesis`" in CHECKER_PROMPT
    assert "supported when each of its cited facts is true and the conclusion follows from them together" in CHECKER_PROMPT
    assert "reject" in CHECKER_PROMPT and "none of its cited findings or facts supports" in CHECKER_PROMPT


def test_a_synthesis_is_marked_and_sent_with_every_cited_fact(chart):
    stub = SynthesisStub({"Mars is dignified in a kendra": True})
    run(chart, draft(), checker=stub)
    by = {s: d for s, d in stub.calls}
    kendra = ASSESSMENT.split(". ", 1)[1]
    assert by[kendra]["synthesis"] is True
    assert set(by[kendra]["facts"]) == {"planets.Mars.dignity", "planets.Mars.house"}
    assert "synthesis" not in by[TIMING] and "synthesis" not in by[NOT_SAID]      # one fact each


def test_a_synthesis_whose_conclusion_no_fact_supports_is_rejected(chart):
    """The stub applies the rule: the premises are true but "career will rise" follows from none of
    them, so the assessment goes back to the writer, and after the last attempt it is a gap."""
    bad = ("Mars is in its own sign in the 7th, so career will rise [fact:planets.Mars.dignity] "
           "[fact:planets.Mars.house].")
    rec = []
    r = run(chart, draft(assessment=bad), rec=rec)
    rejected = [e for e in rec if e["kind"] == "checker" and e["sentence"] == bad]
    assert len(rejected) == CONFIG.max_attempts
    assert all(not rejected[0]["result"]["propositions"][-1]["supported"] for _ in rejected)
    assert r.areas[0].analysis.get("assessment") is None
    gap = next(g for g in r.areas[0].narration_gaps if g["finding_id"] == "analysis.assessment")
    assert "no cited fact supports this conclusion" in gap["last_error"] and not r.narration_complete
    assert r.areas[0].analysis["timing"] == TIMING                       # the other sections stand



# --- the settings through the page, the command, the CLI and the service ----------------------

def test_the_page_shows_the_analysis_and_the_writers_settings(chart):
    from jyotish.page import render
    page = render(run(chart, draft()), chart)
    assert f"writer {CONFIG.model} at effort xhigh, thinking adaptive" in page
    career = page[page.index("## Career"):]
    for heading in ("### Assessment", "### Timing", "### What the chart does not say"):
        assert heading in career
    assert career.index("### Assessment") < career.index("### Timing") < career.index("### What the chart does not say")
    assert "The strongest support is the varga family[^" in career


def test_the_command_reproduces_the_writers_settings(tmp_path):
    from jyotish.cli import main
    from jyotish.service import BirthInput, read_command
    b = BirthInput(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=REFERENCE_LAT, lon=REFERENCE_LON,
                   node="mean")
    cmd = read_command(b, QUESTION, "2026-10-21", None, "full", "claude-sonnet-5-5", "xhigh")
    assert cmd.endswith("--depth full --question 'How will my career go?' --as-of 2026-10-21 "
                        "--writer-model claude-sonnet-5-5 --writer-effort xhigh")
    for bad in (["--writer-effort", "maximum"], ["--writer-model", "gpt-5"]):
        with pytest.raises(SystemExit) as e:
            main(["read", "--date", "2001-03-12", "--time", "10:10:25", "--tz", "Asia/Kolkata", "--lat", "28.2",
                  "--lon", "76.6", "--question", "x", *bad])
        assert e.value.code == 2


def test_post_readings_takes_the_writers_settings_and_records_them(tmp_path):
    import time
    from fastapi.testclient import TestClient
    from pathlib import Path
    from jyotish.api import create_app
    fixture = str(Path(__file__).parent / "fixtures" / "narration_career_edited.json")
    app = create_app(f"sqlite:///{tmp_path / 'j.db'}", model_fixture=fixture)
    body = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT,
            "lon": REFERENCE_LON, "node": "mean", "question": QUESTION, "as_of": "2026-10-21", "depth": "full",
            "writer_model": "claude-fable-5-1", "writer_effort": "xhigh"}
    with TestClient(app) as client:
        for bad in ({"writer_model": "gpt-5"}, {"writer_effort": "maximum"}):
            r = client.post("/readings", json=dict(body, **bad))
            assert r.status_code == 422 and "gpt-5" not in r.text and "maximum" not in r.text
        rid = client.post("/readings", json=body).json()["id"]
        for _ in range(900):
            done = client.get(f"/readings/{rid}").json()
            if done["status"] in ("done", "failed"):
                break
            time.sleep(0.1)
    assert done["status"] == "done", done.get("error")
    r = done["reading"]
    assert r["depth"] == "full" and r["model"] == "claude-fable-5-1"
    assert r["writer"] == {"model": "claude-fable-5-1", "effort": "xhigh", "thinking": "adaptive",
                           "max_tokens": CONFIG.full_max_tokens}
    assert "--writer-model claude-fable-5-1 --writer-effort xhigh" in r["chart"]["command"]
    # The replayed astrologer drafts have no analysis: each section is an honest gap.
    assert {g["finding_id"] for g in r["areas"][0]["narration_gaps"]} >= {
        "analysis.assessment", "analysis.timing", "analysis.not_said_client", "analysis.not_said_astrologer"}


# --- part 3: knowledge beyond the engine, [tradition:<text> <chapter>] ----------------------------

TRADITION = ("Phaladeepika holds that a lord of the tenth in its own sign in a kendra gives a career of authority "
             "[tradition:Phaladeepika 10].")


@pytest.mark.parametrize("sentence,needle", [
    ("Phaladeepika holds that the tenth lord in the 7th gives authority [tradition:Phaladeepika 10].", "numeral"),
    ("Saravali says Mars at 18 degrees of Scorpio gives courage [tradition:Saravali 22].", "numeral"),
    ("Saravali says Mars near the end of a sign in March gives courage [tradition:Saravali 22].", "date"),
    ("BPHS says the dasha of the tenth lord raises the native [tradition:BPHS 25].", "dasha"),
    ("BPHS says the Shadbala of the tenth lord decides the career [tradition:BPHS 27].", "computes"),
    ("BPHS says that in this chart Mars rules the career [tradition:BPHS 24].", "this chart"),
    ("BPHS says your Mars gives courage [tradition:BPHS 24].", "this chart"),
    ("Mars in its own sign gives courage [tradition:BPHS 24] [fact:planets.Mars.dignity].", "no other tag"),
    ("The Hora Makaranda says Mars gives courage [tradition:Hora Makaranda 4].", "not a classical text"),
    ("Saravali says Mars gives courage [tradition:Saravali].", "chapter"),
    ("Saravali says Mars gives courage [tradition:Saravali chapter four].", "chapter"),
])
def test_tradition_sentence_limits(sentence, needle):
    from jyotish.narrate import validate
    errs = validate(sentence, set(), facts={"planets": {"Mars": {"dignity": "own"}}}, traditions=True)
    assert any(needle in e for e in errs), errs


def test_tradition_sentence_within_its_limits_passes_and_belongs_to_the_analysis():
    from jyotish.narrate import validate
    assert validate(TRADITION, set(), facts={}, traditions=True) == []
    assert validate("Saravali holds that Mars in its own sign gives courage [tradition:Saravali 30.2].", set(),
                    facts={}, traditions=True) == []
    errs = validate(TRADITION, set(), facts={})                       # a claim or the summary
    assert any("belongs in the analysis" in e for e in errs)


def test_tradition_sentences_are_shown_apart_unchecked_and_recorded(chart, tmp_path, monkeypatch):
    from jyotish.narrate import TRADITION_NOTE
    from jyotish.page import render
    from jyotish.service import record_candidates
    stub = SynthesisStub({"Mars is dignified in a kendra": True})
    r = run(chart, draft(assessment=ASSESSMENT + " " + TRADITION), checker=stub)
    a = r.areas[0]
    assert TRADITION not in [s for s, _ in stub.calls]                    # never checked
    assert a.analysis["assessment"] == ASSESSMENT                         # taken out of the checked text
    assert a.traditions == [{"section": "assessment", "sentence": TRADITION, "citation": "Phaladeepika 10",
                             "text": "Phaladeepika", "chapter": "10", "verse": None, "checked": False,
                             "note": TRADITION_NOTE}]
    page = render(r, chart)
    block = page[page.index("From the texts, not computed on this chart"):]
    assert TRADITION.replace(" [tradition:Phaladeepika 10]", "") in block and TRADITION_NOTE in block
    assert page.index("From the texts") > page.index(ASSESSMENT.split(" [")[0])
    out = tmp_path / "candidate_rules.jsonl"
    monkeypatch.setenv("JYOTISH_CANDIDATE_RULES", str(out))
    assert record_candidates(r, chart, chart_id="abc123") == 1
    row = json.loads(out.read_text().splitlines()[0])
    assert row["chart_hash"] == "abc123" and row["sentence"] == TRADITION and row["citation"] == "Phaladeepika 10"
    assert row["area"] == "career" and row["status"] == "candidate" and "birth" not in json.dumps(row)


def test_tradition_sentences_are_counted_in_neither_checked_text_nor_synthesis(chart):
    r = run(chart, draft(assessment=ASSESSMENT + " " + TRADITION))
    assert r.synthesis_sentences == 1 and len(r.areas[0].traditions) == 1
    assert not any(c.startswith("tradition:") for c in r.areas[0].analysis_cites)


def test_the_prompt_offers_the_tradition_tag_at_full_depth_only():
    assert "[tradition:<text> <chapter>]" in system_prompt("full")
    assert "[tradition:" not in system_prompt("astrologer") and "[tradition:" not in system_prompt("curious")


# --- the ranking is the engine's -----------------------------------------------------------------

@pytest.mark.parametrize("sentence", [
    "The strongest support is in the lords [vote:career.lord].",
    "The weakest point is the varga family [fact:areas.career.votes.varga.vote].",
    "The least support comes from the 10th itself [fact:bhava_bala.whole_sign.H10.rank_of_12].",
])
def test_a_ranking_must_cite_the_engines_contributions(chart, sentence):
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range, validate
    whole = payload(chart, AS_OF, *full_range(AS_OF), ["career"])
    errs = validate(sentence, {"vote:career.lord"}, facts=whole, family_rule=False)
    assert any("a ranking" in e and "contributions" in e for e in errs), errs
    fixed = sentence.split(" [")[0] + " [fact:areas.career.contributions]."
    assert not [e for e in validate(fixed, set(), facts=whole, family_rule=False) if "a ranking" in e]


def test_the_prompt_sends_the_ranking_to_the_contributions():
    p = system_prompt("full")
    assert "cites [fact:areas.<area>.contributions] (its percentile) and never a ranking of your own" in p
    assert "the largest term is not a finding" in p and "percentile against 10,000 random charts" in p


def test_a_votes_or_contributions_fact_stands_for_the_vote_tags_it_states(chart):
    """B's attempt 2 refused a sentence naming every family and citing the area's votes as a fact."""
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range, offered_votes, validate
    whole = payload(chart, AS_OF, *full_range(AS_OF), ["longevity", "career"])
    votes = offered_votes(chart, ["longevity"])["longevity"]
    b = ("The votes for this area weigh houses, lords, karakas, vargas, the arudha and the panchanga "
         "[fact:areas.longevity.votes].")
    assert validate(b, set(), offered_votes=votes, facts=whole) == []
    one = "The lord vote is for longevity [fact:areas.longevity.votes.lord.vote]."
    assert validate(one, set(), offered_votes=votes, facts=whole) == []
    other = "The lord vote is for longevity [fact:areas.career.votes.lord.vote]."     # another area's vote
    assert any("does not cite [vote:longevity.lord]" in e for e in validate(other, set(), offered_votes=votes, facts=whole))


# --- part 3 of the second heading: the judgement sentence kind --------------------------------------

JUDGE = ("I give the lord family more weight than the arudha vote, since the lord family's term is the largest "
         "[fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].")


@pytest.mark.parametrize("sentence,weighs", [
    ("I weigh the lords above the arudha [vote:career.lord].", True),
    ("I give the six agreeing families more weight than the arudha vote [vote:career.lord].", True),
    ("I read Saturn's divisional dignity as the quality of what it gives [vote:career.varga].", True),
    ("I resolve this contradiction toward Shadbala [vote:career.lord].", True),
    ("Saturn gives weight to the career houses [vote:career.lord].", False),
    ("The weighting reads the lords first [vote:career.lord].", False),
])
def test_a_judgement_is_known_by_its_form(sentence, weighs):
    from jyotish.narrate import is_judgement
    assert is_judgement(sentence) is weighs


def test_a_judgement_goes_to_the_checker_marked_and_with_its_facts(chart):
    stub = SynthesisStub({"Mars is dignified in a kendra": True})
    r = run(chart, draft(assessment=ASSESSMENT + " " + JUDGE), checker=stub)
    data = dict(stub.calls)[JUDGE]
    assert data["judgement"] is True and "synthesis" not in data            # never checked as a conclusion
    assert set(data["facts"]) == {"areas.career.contributions.largest_term", "areas.career.votes.arudha.vote"}
    a = r.areas[0]
    assert a.analysis["assessment"].endswith(JUDGE) and a.judgements == [{"section": "assessment", "sentence": JUDGE}]
    assert r.judgement_sentences == 1 and r.synthesis_sentences == 1        # the kendra sentence only
    assert "`judgement` true" in CHECKER_PROMPT and "List every proposition in it" in CHECKER_PROMPT
    assert "Only the weighing itself may stand unverified" in CHECKER_PROMPT


def test_a_judgement_with_a_false_premise_is_refused(chart):
    """The checker verifies the premises: a weighing that misstates a cited fact goes back."""
    class PremiseStub(SynthesisStub):
        def __call__(self, sentence, data):
            if sentence == JUDGE:
                return CheckResult(propositions=[Proposition(text="the lord family ranks first", supported=False,
                                                             evidence="contributions.strongest is 'house'")])
            return super().__call__(sentence, data)
    r = run(chart, draft(assessment=ASSESSMENT + " " + JUDGE), checker=PremiseStub({"Mars is dignified in a kendra": True}))
    assert r.areas[0].analysis.get("assessment") is None and not r.areas[0].judgements


@pytest.mark.parametrize("sentence,needle", [
    ("I weigh the lords above the arudha.", "cites the findings and facts it weighs"),
    ("I weigh Venus at 1.33 above Saturn [vote:career.lord].", "a figure ('1.33')"),
    ("I give the lords more weight, since career support is strong [fact:areas.career.contributions].", "tier language"),
])
def test_a_judgement_keeps_to_its_limits(chart, sentence, needle):
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range, validate_summary
    whole = payload(chart, AS_OF, *full_range(AS_OF), ["career"])
    errs = validate_summary(sentence, {"vote:career.lord"}, facts=whole, family_rule=False, traditions=True,
                            judgements=True, where="career assessment")
    assert any(needle in e for e in errs), errs


def test_a_judgement_belongs_in_the_analysis(chart):
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range, validate
    whole = payload(chart, AS_OF, *full_range(AS_OF), ["career"])
    errs = validate("I weigh the lords above the arudha [vote:career.lord].", {"vote:career.lord"}, facts=whole)
    assert any("belongs in the analysis" in e for e in errs)


def test_the_10th_sign_is_refused_and_the_10th_house_from_the_lagna_cited(chart):
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range, validate
    whole = payload(chart, AS_OF, *full_range(AS_OF), ["career"])
    b = ("The timing join's full targets for career are Aquarius, the 10th sign, and Taurus, the sign of the A10 "
         "[fact:timing.career.windows.0.targets.full] [fact:jaimini.arudhas.A10] [fact:lagnas.asc.sign].")
    assert any("'10th sign' reads as the zodiac's" in e for e in validate(b, set(), facts=whole))
    fixed = b.replace("the 10th sign", "the 10th house from the lagna").replace("[fact:lagnas.asc.sign]",
                                                                               "[fact:houses.lagna.10]")
    assert validate(fixed, set(), facts=whole) == []


def test_the_prompt_asks_for_judgement_sentences_and_the_reading_date():
    p = system_prompt("full")
    for words in ("Make every weighing a judgement sentence", 'never "the 10th sign"', "at the reading date",
                  'never "over the range"'):
        assert words in p, words


def test_the_page_marks_the_reading_s_weighing(chart):
    from jyotish.page import JUDGEMENT_MARK, render
    page = render(run(chart, draft(assessment=ASSESSMENT + " " + JUDGE)), chart)
    career = page[page.index("### Assessment"):]
    assert f"{JUDGEMENT_MARK} I give the lord family more weight" in career
    assert career.count(JUDGEMENT_MARK) == 1                                  # the checked sentences are not marked


# --- validator fixes from B's attempt 2 (the engine's, not the writer's) -----------------------------

def test_a_navamsa_chain_sentence_does_not_name_the_varga_family(chart):
    from jyotish.narrate import offered_chains, offered_votes, validate
    b = ("Its navamsa chain runs from Gemini through Mercury and Venus to Saturn, self-disposited in Capricorn, and "
         "the current major period of Jupiter activates the Sun, which is in a nakshatra of Jupiter [chain:career.karaka].")
    errs = validate(b, {"chain:career.karaka"}, offered_votes=offered_votes(chart, ["career"])["career"],
                    chains=offered_chains(chart, ["career"])["career"])
    assert not [e for e in errs if "varga family" in e], errs
    named = "Its navamsa chain ends in Saturn, and the D10 places it in Capricorn [chain:career.karaka]."
    errs = validate(named, {"chain:career.karaka"}, offered_votes=offered_votes(chart, ["career"])["career"],
                    chains=offered_chains(chart, ["career"])["career"])
    assert any("names the varga family" in e for e in errs)                 # D10 is the varga family's word


def test_a_tradition_sentence_is_not_held_to_the_family_rule(chart):
    from jyotish.narrate import offered_votes, validate
    b = "BPHS reads marriage through the Upapada, the arudha of the twelfth house, and the sign second from it [tradition:BPHS 30]."
    errs = validate(b, set(), offered_votes=offered_votes(chart, ["marriage"])["marriage"], facts={}, traditions=True)
    assert errs == []


def test_a_hyphenated_rule_name_is_the_rule_s_name(chart):
    from jyotish.narrate import validate
    b = "Mars, lord-of-the-7th-in-the-7th, is scaled to 0.6 by marana karaka sthana [rule:place.l7_h7]."
    assert not [e for e in validate(b, {"rule:place.l7_h7"}) if "names none of" in e]


# --- part 4 of the second heading: section-level retries ---------------------------------------------

BAD = ("Mars is in its own sign in the 7th, so career will rise [fact:planets.Mars.dignity] "
       "[fact:planets.Mars.house].")
TIMING_2 = "Mars's own major period is laid out by the engine [fact:vimshottari.periods.Mars]."


def test_a_passed_section_is_held_and_never_rewritten(chart):
    """Attempt 1: the assessment fails the checker, the timing and the rest pass and are held. Attempt
    2 rewrites the timing too, but the held version stands and is not checked again."""
    w = Replay(draft(assessment=BAD), draft(timing=TIMING_2))
    stub = SynthesisStub({"Mars is dignified in a kendra": True})
    r = narrate(chart, QUESTION, drafter=w, checker=stub, as_of=AS_OF, areas=["career"], depth="full")
    assert r.attempts == 2 and r.areas[0].analysis == {"assessment": ASSESSMENT, "timing": TIMING,
                                                       "not_said_client": NOT_DECIDED, "not_said_astrologer": NOT_SAID}
    checked = [x for x, _ in stub.calls]
    assert TIMING_2 not in checked and checked.count(TIMING) == 1 and checked.count(NOT_SAID) == 1


def test_the_retry_asks_only_for_the_failed_units_with_the_checkers_reasons(chart):
    from jyotish.narrate import RETRY_HEAD
    w = Replay(draft(assessment=BAD), draft())
    narrate(chart, QUESTION, drafter=w, checker=SynthesisStub({"Mars is dignified in a kendra": True}), as_of=AS_OF,
            areas=["career"], depth="full")
    ask = w.calls[1]["errors"]
    assert len(ask) == 1 and ask[0].startswith(RETRY_HEAD)
    text = ask[0]
    held = text.split("Held: ", 1)[1].split("\n")[0]
    # At depth full the first call writes no summary (the client's layer does): nothing to hold or ask.
    assert "the summary" not in text and "the career timing" in held
    assert "the career not_said_client" in held and "the career not_said_astrologer" in held
    assert "the career assessment" not in held
    assert "- the career assessment:" in text and "the checker refused 'career will rise'" in text
    assert "no cited fact supports this conclusion" in text and "- the career timing" not in text


def test_every_unit_that_passes_the_validator_is_checked_in_its_attempt(chart):
    """Under whole-draft retries a validator error anywhere kept the checker away until the last
    attempt (B's attempts 1 and 2 were never checked); now the passing units are checked at once."""
    from dataclasses import replace
    stub = SynthesisStub({"Mars is dignified in a kendra": True})
    w = Replay(draft(not_said=""), draft())
    narrate(chart, QUESTION, drafter=w, checker=stub, as_of=AS_OF, areas=["career"], depth="full")
    assert TIMING in [x for x, _ in stub.calls[:5]]                    # checked in attempt 1
    old = SynthesisStub({"Mars is dignified in a kendra": True})
    w = Replay(draft(not_said=""), draft())
    narrate(chart, QUESTION, drafter=w, checker=old, as_of=AS_OF, areas=["career"], depth="full",
            config=replace(CONFIG, section_retries=False))
    assert w.calls[1]["errors"][0].startswith("no not_said_astrologer for career")   # the whole draft
    assert [x for x, _ in old.calls].count(TIMING) == 1                    # checked only once the draft passed


def test_the_drafter_sends_the_retry_instruction_as_it_is():
    from jyotish.narrate import RETRY_HEAD, retry_instruction
    seen = {}

    def parse(**kw):
        seen["messages"] = list(kw["messages"])
        return SimpleNamespace(parsed_output=ReadingDraft(summary="", areas=[]), stop_reason="end_turn", content=[],
                               usage=None, model="m")
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse)))
    d = AnthropicDrafter(CONFIG, client=client)
    d("s", "payload", [])
    ask = retry_instruction(["the summary"], {"the career timing": ["the checker refused 'x': 'y', in 'z'"]})
    d("s", "payload", [ask])
    assert seen["messages"][-1]["content"] == ask and ask.startswith(RETRY_HEAD)
    assert "Fix every one of these" not in ask


def test_the_saving_on_a_replay_of_b():
    """scripts/section_retries.py on reading B's recording: the same units held at the end, but the
    last attempt asks for the failed units only."""
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("section_retries", root / "scripts" / "section_retries.py")
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)
    m = sr.measure()
    whole, sec = m["whole_draft"], m["section_retries"]
    assert [p["writer_failed"] for p in whole["attempts"]] == [True, False, False]    # attempt 1 as recorded
    assert whole["attempts"][-1]["asked"] == "the whole draft" and sec["attempts"][-1]["asked"] < whole["attempts"][-1]["units_written"]
    assert m["last_attempt_units_saved"] > 0 and m["last_attempt_characters_saved"] > 0
    assert sec["attempts"][1]["checker_calls"] > 0 == whole["attempts"][1]["checker_calls"]   # attempt 2 now checked
    assert sec["units_held"] >= whole["units_held"] and sec["gaps"] <= whole["gaps"]



# --- the review of 2026-10-23 (docs/review_2026-10-23_depth_full.md), F1 and F2: the gate -------------

@pytest.fixture(scope="module")
def whole(chart):
    from jyotish.fullchart import payload
    from jyotish.narrate import full_range
    return payload(chart, AS_OF, *full_range(AS_OF), ["career", "marriage", "longevity"])


def _section_errors(sentence, whole):
    from jyotish.narrate import validate_summary
    return validate_summary(sentence, {"vote:career.lord", "vote:career.house"}, facts=whole, family_rule=False,
                            traditions=True, judgements=True, where="career assessment")


@pytest.mark.parametrize("sentence,needle", [
    # F1's probes, each passed by the validator before the fix
    ("I read Saturn's place in Taurus as its exaltation, so career rises sharply after forty "
     "[fact:planets.Saturn.sign].", "dignity word ('exaltation')"),
    ("I give the lord family more weight, since Saturn is exalted in the 10th [fact:areas.career.contributions].",
     "dignity word ('exalted')"),
    ("I resolve the contradiction toward a job change in 2031 [fact:vimshottari.periods.Jupiter-Venus].",
     "date ('2031')"),
    ("I read the lords as the career's backbone, which peaks after forty [fact:areas.career.contributions].",
     "no age ('after forty')"),
    ("I weigh the karaka above the house, so career rises [fact:areas.career.contributions].", "outcome ('rises')"),
    ("I give the lord family more weight in the Saturn period [fact:areas.career.contributions].", "period ('period')"),
])
def test_a_judgement_states_no_chart_proposition_its_facts_do_not(whole, sentence, needle):
    errs = _section_errors(sentence, whole)
    assert any(needle in e for e in errs), errs


def test_a_judgement_within_its_limits_passes(whole):
    ok = ("I give the lord family more weight than the arudha vote, since the lord family's term is the largest "
          "[fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].")
    assert _section_errors(ok, whole) == []
    exalted = "I weigh Venus, exalted in Pisces, above Saturn [fact:planets.Venus.dignity] [fact:planets.Venus.sign]."
    assert _section_errors(exalted, whole) == []                   # the dignity word is the cited fact's
    dated = ("I weigh the window from 2029-10-23 above the others [fact:timing.career.windows.0.start] "
             "[fact:timing.career.windows.0].")
    assert _section_errors(dated, whole) == []                     # the date is the cited fact's


@pytest.mark.parametrize("sentence", [
    "Saturn exalted in Libra, Venus debilitated in Virgo.",
    "Marriage comes late and career peaks after forty.",
    "Saturn owns the tenth and governs the career outright.",
])
def test_an_untagged_analysis_sentence_is_refused(whole, sentence):
    """F2's probes: no listed claim verb, so the old validator let them through untagged and unchecked."""
    errs = _section_errors(sentence, whole)
    assert any("every sentence here carries the tags" in e for e in errs), errs


def test_every_sentence_of_a_summary_is_checked_tagged_or_not(chart):
    """Below depth full: an untagged summary sentence goes to the checker with nothing to rest on. At
    depth full a summary drafted in the first call is not the reading's (the client's layer writes it,
    every sentence tagged): it is neither checked nor shown."""
    summary = "Mars is in its own sign [fact:planets.Mars.dignity]. Career looks layered."
    stub = SynthesisStub()
    r = run(chart, draft(summary=summary), checker=stub)
    assert "Career looks layered." not in dict(stub.calls) and "Career looks layered." not in r.summary.text
    astro = SynthesisStub()
    w = Replay({"summary": "Career looks layered.", "areas": []})
    narrate(chart, QUESTION, drafter=w, checker=astro, as_of=AS_OF, areas=["career"])
    assert [x for x, _ in astro.calls] == ["Career looks layered."]


def test_the_timing_filter_knows_ages():
    from jyotish.narrate import validate
    for s in ("Mars in the 7th brings success after forty [rule:yoga.ruchaka].",
              "Ruchaka yoga works by age 35 [rule:yoga.ruchaka].",
              "Ruchaka yoga matures in the native's forties [rule:yoga.ruchaka]."):
        assert any("timing language" in e for e in validate(s, {"rule:yoga.ruchaka"})), s
    assert not any("timing" in e for e in validate("Mars forms Ruchaka yoga in the 7th [rule:yoga.ruchaka].",
                                                   {"rule:yoga.ruchaka"}))


def test_the_checker_lists_every_proposition_of_a_judgement():
    prompt = " ".join(CHECKER_PROMPT.split())
    for words in ("List every proposition in it", "Only the weighing itself may stand unverified",
                  "whether or not anything is cited for it",
                  '"I read Saturn in Taurus as its exaltation" states that Saturn is exalted'):
        assert words in prompt, words



def test_a_contributions_fact_stands_only_for_the_families_it_names(whole):
    """F13: a part of the contributions (`largest_term`, "lord") stood for every family's vote tag."""
    from jyotish.narrate import validate
    votes = {"kp": "vote:career.kp", "lord": "vote:career.lord"}
    kp = "The KP vote is against career [fact:areas.career.contributions.largest_term]."
    assert any("does not cite [vote:career.kp]" in e for e in validate(kp, set(), offered_votes=votes, facts=whole))
    lord = "The lord vote's term is the largest [fact:areas.career.contributions.largest_term]."
    assert not any("does not cite" in e for e in validate(lord, set(), offered_votes=votes, facts=whole))


def test_every_error_reaches_the_retry_instruction(chart):
    """F13: "two claims for X" went into the errors but not the retry instruction."""
    twice = draft()
    claim = {"finding_id": "vote:career.house", "text": "The house vote is for career [vote:career.house]."}
    twice["areas"][0]["claims"] = [claim, dict(claim)]
    w = Replay(twice, draft())
    narrate(chart, QUESTION, drafter=w, checker=SynthesisStub({"Mars is dignified in a kendra": True}), as_of=AS_OF,
            areas=["career"], depth="full")
    assert "two claims for vote:career.house in career" in w.calls[1]["errors"][0]



# --- the review's F6 and F10 -------------------------------------------------------------------------

@pytest.mark.parametrize("sentence,needle", [
    ("Saturn and Jupiter together in Taurus rising, with Mars in Scorpio in the seventh, deny marriage until "
     "late [tradition:BPHS 18].", "with the sign it has on this chart (Taurus)"),
    ("A native with Venus exalted in Pisces in the eleventh becomes very wealthy [tradition:Phaladeepika 8].",
     "with the sign it has on this chart (Pisces)"),
    ("Exaltation gives a planet great strength [tradition:BPHS 3].", "strength word"),
    ("Mars in the seventh makes the native bold [tradition:Saravali 30].", "with the house it has on this chart (seventh)"),
    ("Taurus rising gives a steady temperament [tradition:Saravali 33].", "rising sign (Taurus)"),
])
def test_a_tradition_sentence_names_nothing_of_this_chart(whole, sentence, needle):
    from jyotish.narrate import validate
    errs = validate(sentence, set(), facts=whole, traditions=True, judgements=True)
    assert any(needle in e for e in errs), errs


def test_a_tradition_sentence_of_a_general_principle_passes(whole):
    from jyotish.narrate import validate
    ok = "Phaladeepika holds that a lord of the tenth in its own sign in a kendra gives a career of authority [tradition:Phaladeepika 10]."
    assert validate(ok, set(), facts=whole, traditions=True, judgements=True) == []
    other = "Saravali holds that Mars in the fourth unsettles the home [tradition:Saravali 30]."    # Mars is in the 7th
    assert validate(other, set(), facts=whole, traditions=True, judgements=True) == []


def test_not_computed_says_the_tradition_citations_are_unverified(whole):
    """F10: it said the only verses cited are checked ones, beside a tradition block that is not."""
    from jyotish.fullchart import resolve
    r = resolve(whole, "not_computed.retrieval")
    assert "[tradition:] citation is the writer's own, unverified" in r


# --- the empty first attempt (B's: thinking through all 128,000 tokens, no draft) ------------------------

def _stepping_client(stops):
    """A fake client whose streamed answers stop as `stops` says: "max_tokens" with no draft, then a draft."""
    calls = []

    class Stream:
        def __init__(self, **kw):
            calls.append(kw)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get_final_message(self):
            stop = stops[min(len(calls), len(stops)) - 1]
            out = None if stop != "end_turn" else ReadingDraft(**draft())
            return SimpleNamespace(parsed_output=out, stop_reason=stop, content=[], usage=None, model="m")
    return SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=Stream))), calls


def test_thinking_to_max_tokens_steps_the_effort_down_and_the_reading_says_so(chart):
    client, calls = _stepping_client(["max_tokens", "end_turn"])
    d = AnthropicDrafter(writer_config(CONFIG, "full"), client=client)
    r = narrate(chart, QUESTION, drafter=d, checker=SynthesisStub({"Mars is dignified in a kendra": True}), as_of=AS_OF,
                areas=["career"], depth="full")
    assert [c["output_config"]["effort"] for c in calls] == ["xhigh", "high"]
    assert r.writer["effort"] == "xhigh" and r.writer["efforts_by_attempt"] == ["xhigh", "high"]
    assert r.writer["stepped_down"] == [{"attempt": 1, "from": "xhigh", "to": "high",
                                         "why": "no draft: the writer's thinking reached max_tokens"}]
    assert r.attempts == 2 and r.areas[0].analysis["timing"] == TIMING


def test_no_step_down_for_any_other_failure_and_none_below_low(chart):
    client, calls = _stepping_client(["refusal", "end_turn"])
    r = narrate(chart, QUESTION, drafter=AnthropicDrafter(writer_config(CONFIG, "full"), client=client),
                checker=SynthesisStub({"Mars is dignified in a kendra": True}), as_of=AS_OF, areas=["career"], depth="full")
    assert [c["output_config"]["effort"] for c in calls] == ["xhigh", "xhigh"] and "stepped_down" not in r.writer
    client, calls = _stepping_client(["max_tokens", "max_tokens", "end_turn"])
    narrate(chart, QUESTION, drafter=AnthropicDrafter(writer_config(CONFIG, "full", effort="low"), client=client),
            checker=SynthesisStub(), as_of=AS_OF, areas=["career"], depth="full")
    assert [c["output_config"]["effort"] for c in calls] == ["low", "low", "low"]


def test_the_report_shows_each_attempt_of_b():
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location("compare_readings", root / "scripts" / "compare_readings.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    rec = json.loads((root / "docs" / "comparison_2026-10-23" / "b.recording.json").read_text())["calls"]
    rows = cr.per_attempt(rec)
    assert [r["attempt"] for r in rows] == [1, 2, 3]
    first = rows[0]
    assert (first["stop"], first["draft"], first["writer_out"], round(first["writer_s"])) == ("max_tokens", False, 128000, 1025)
    assert rows[2]["checks"] == 132 and rows[1]["checks"] == 0
    table = "\n".join(cr._attempt_table(rows))
    assert "| 1 | max | max_tokens | no | 246,973 / 128,000 | 1024.527 | 0 |" in table
