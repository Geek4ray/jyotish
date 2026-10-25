"""Depth full, the client's layer (jyotish.client): after the claims and the analysis are accepted, a
second writer call writes each area's plain paragraph and the summary from the accepted text alone,
validated and checked like the summary, in the client's words. Offline: both writers replayed, the
checker stubbed."""

import json
from datetime import date

import pytest

from jyotish.client import CLIENT_PROMPT, ClientDraft, client_errors
from jyotish.narrate import (CONFIG, CheckResult, FixtureDrafter, Proposition, ReadingDraft, anthropic_client_drafter,
                             is_judgement, narrate, writer_config)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
QUESTION = "How will my career go?"
ASSESSMENT = ("Saturn, lord of the 10th house from the lagna, is in its own sign in the tenth divisional chart "
              "[fact:houses.lagna.10.lord] [fact:vargas.D10.Saturn]. "
              "I give more weight to Saturn's dignity in the tenth divisional chart than to its Shadbala "
              "[fact:vargas.D10.Saturn] [fact:shadbala.planets.Saturn.ratio].")
TIMING = "At the reading date the Vimshottari period is Jupiter-Mercury-Mercury [fact:vimshottari.current]."
REFUSED_TIMING = "Saturn's period peaks in 2031 [fact:vimshottari.periods.Saturn]."
NOT_DECIDED = "Which kind of work suits you is not settled by anything here [fact:not_computed.question_routing]."
NOT_COMPUTED = "The KP family abstains on career [fact:areas.career.votes.kp.vote]."
TRADITION = ("Phaladeepika holds that a lord of the tenth in its own sign gives a career of authority "
             "[tradition:Phaladeepika 10].")

VIEW = ("In the reading's view, that dignity counts for more than Saturn's standing in the birth chart "
        "[fact:vargas.D10.Saturn] [fact:shadbala.planets.Saturn.ratio].")
PARAGRAPH = ("Your work house is led by Saturn, which sits in its own sign in the chart of career "
             "[fact:houses.lagna.10.lord] [fact:vargas.D10.Saturn]. " + VIEW)
WHEN = "You are now in the period of Jupiter, with Mercury beneath it [fact:vimshottari.current]."
SUMMARY = "Your work house is led by Saturn, which sits in its own sign in the chart of career " \
          "[fact:houses.lagna.10.lord] [fact:vargas.D10.Saturn]."


def draft(timing=TIMING, not_decided=NOT_DECIDED, assessment=ASSESSMENT):
    return {"summary": "", "areas": [{"name": "career", "claims": [], "analysis": {
        "assessment": assessment, "timing": timing, "not_said_client": [not_decided],
        "not_said_astrologer": [NOT_COMPUTED]}}]}


class Replay:
    def __init__(self, *drafts, schema=ReadingDraft):
        self.drafts = [schema(**d) for d in drafts]
        self.calls = []
        self.last_meta = None

    def __call__(self, system, user, errors):
        self.calls.append({"system": system, "user": user, "errors": list(errors)})
        self.last_meta = {"kind": "client" if self.drafts and isinstance(self.drafts[0], ClientDraft) else "writer"}
        return self.drafts[min(len(self.calls), len(self.drafts)) - 1]


def client(*units):
    """Client drafts from (summary, paragraph) or (summary, paragraph, when); the when defaults to WHEN."""
    return Replay(*({"summary": u[0], "areas": [{"name": "career", "paragraph": u[1],
                                                  "when": u[2] if len(u) > 2 else WHEN}]} for u in units),
                  schema=ClientDraft)


class Stub:
    """Every sentence passes except one containing a refused phrase."""

    def __init__(self, refuse=()):
        self.refuse = refuse
        self.calls = []
        self.last_meta = None

    def __call__(self, sentence, data):
        self.calls.append((sentence, json.loads(data)))
        bad = next((r for r in self.refuse if r in sentence), None)
        return CheckResult(propositions=[Proposition(text=bad or sentence, supported=bad is None,
                                                     evidence="no cited fact states it" if bad else "stub")])


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def run(chart, writer, clientw, checker=None, **kw):
    return narrate(chart, QUESTION, drafter=writer, client_drafter=clientw, checker=checker or Stub(), as_of=AS_OF,
                   areas=["career"], depth="full", **kw)


# --- the client's words ------------------------------------------------------------------------

@pytest.mark.parametrize("sentence,needle", [
    ("Five of the seven families vote for career [vote:career.house].", "engine vocabulary ('families')"),
    ("The house vote is for career [vote:career.house].", "engine vocabulary ('vote')"),
    ("The lord term is the largest [fact:areas.career.contributions].", "engine vocabulary ('term')"),
    ("It sits at the 90th percentile [fact:areas.career.contributions].", "engine vocabulary ('percentile')"),
    ("The learned score is not used [fact:not_computed.learned_score].", "engine vocabulary ('learned score')"),
    ("Both house systems agree [fact:houses.system].", "engine vocabulary ('house systems')"),
    ("It holds in every sample [fact:areas.career.stability].", "engine vocabulary ('sample')"),
    ("I give more weight to Saturn [fact:vargas.D10.Saturn].", "never says 'I'"),
    ("Saturn's dignity outweighs its strength [fact:vargas.D10.Saturn].", "says 'in the reading's view'"),
    ("Saturn's dignity matters most here [fact:vargas.D10.Saturn].", "says 'in the reading's view'"),
])
def test_the_clients_words_refuse_the_engines_vocabulary_and_an_unmarked_weighing(sentence, needle):
    errs = client_errors(sentence)
    assert any(needle in e for e in errs), errs


@pytest.mark.parametrize("sentence,needle", [
    ("The 10th cusp's star decides it [fact:lagnas.kp_cusps.H10].", "('cusp')"),
    ("Its sub-lord is Ketu [fact:lagnas.kp_cusps.H10].", "('sub-lord')"),
    ("The arudha of the 10th holds Jupiter [fact:jaimini.arudhas.A10].", "('arudha')"),
    ("The dasha of Jupiter runs now [fact:vimshottari.current].", "('dasha')"),
    ("Saturn's Shadbala is low [fact:shadbala.planets.Saturn.ratio].", "('Shadbala')"),
    ("The 10th house is lowest by Bhava Bala [fact:bhava_bala.whole_sign.H10].", "('Bhava Bala')"),
    ("It has 4.51 rupas [fact:bhava_bala.whole_sign.H10.rupas].", "('rupas')"),
])
def test_the_clients_words_refuse_the_wider_engine_vocabulary(sentence, needle):
    errs = client_errors(sentence)
    assert any("engine vocabulary " + needle in e for e in errs), errs


@pytest.mark.parametrize("sentence,plain", [
    ("Your lagna is Taurus [fact:lagnas.asc.sign].", "the rising sign"),
    ("Saturn rules the 10th bhava [fact:houses.lagna.10.lord].", "house"),
    ("Mars sits in a kendra [fact:planets.Mars.house].", "angular house"),
    ("The Sun is the main karaka of your work [fact:areas.career.main_karaka].", "significator"),
])
def test_a_sanskrit_word_with_a_plain_phrase_is_refused_for_the_phrase(sentence, plain):
    errs = client_errors(sentence)
    assert any(f"say {plain!r}" in e for e in errs), errs


def test_a_sanskrit_term_with_no_plain_phrase_needs_its_gloss_in_the_same_sentence():
    bare = "Mars in its own sign in the 7th forms Ruchaka yoga [rule:yoga.ruchaka]."
    assert any("is a Sanskrit term: gloss it" in e for e in client_errors(bare))
    glossed = ("Mars in its own sign in the 7th forms Ruchaka yoga, a combination formed when Mars is in its own "
               "sign in an angular house [rule:yoga.ruchaka].")
    assert client_errors(glossed) == []
    kt = ("The Sun and Mercury form a Kendra-Trikona Raja yoga, a combination of the lord of an angular house with "
          "the lord of a trine [rule:yoga.kendra_trikona_raja].")
    assert client_errors(kt) == []                          # "kendra" and "trikona" in the rule's own name pass
    mks = ("Saturn is in marana karaka sthana (a placement in which a planet cannot give its good results) "
           "[fact:sensitive.Saturn.marana_karaka_sthana].")
    assert client_errors(mks) == []                         # "karaka" inside the term is not the plain-phrase word


def test_the_paragraph_takes_no_date_and_the_when_does():
    s = "The window from 2029-10-23 favours a change of work [fact:timing.career.windows.0]."
    assert any("dates go under When" in e for e in client_errors(s, dates=False))
    assert not any("dates go under When" in e for e in client_errors(s))


def test_a_glossed_term_reaches_the_checker_with_its_definition():
    from jyotish.client import with_glosses
    s = ("Mars forms Ruchaka yoga, a combination formed when Mars is in its own sign in an angular house "
         "[rule:yoga.ruchaka].")
    d = json.loads(with_glosses(s, json.dumps({"findings": []})))
    assert d["glossary"]["Ruchaka yoga"].startswith("The Pancha Mahapurusha combination of Mars")
    assert with_glosses("Saturn sits well [fact:vargas.D10.Saturn].", "{}") == "{}"


def test_a_weighing_marked_as_the_readings_view_is_a_judgement_and_passes_the_words():
    s = "In the reading's view, Saturn's dignity counts for more [fact:vargas.D10.Saturn]."
    assert client_errors(s) == [] and is_judgement(s)


def test_the_paragraph_cites_only_what_the_accepted_text_carries():
    accepted = {"fact:vargas.D10.Saturn"}
    assert client_errors("Saturn sits in its own sign [fact:vargas.D10.Saturn].", accepted) == []
    errs = client_errors("Saturn sits in its own sign [fact:planets.Saturn.dignity].", accepted)
    assert any("not in the accepted text" in e for e in errs)
    assert any("carries the tags" in e for e in client_errors("Saturn sits well.", accepted))


def test_the_prompt_asks_for_the_answer_first_and_the_readings_view():
    for words in ('"What the chart says for you"', "the answer to the question", "then what supports it",
                  "then what works against it", "No dates or periods", '`when`, "When"', "in dates and months",
                  "in the reading's view", "Never write \"I\"", "vote, family, term, percentile",
                  "learned score, house system, sample, cusp", "sub-lord, arudha, dasha, Shadbala, Bhava Bala, rupa",
                  "the rising sign (not lagna)", "with its gloss in the same sentence"):
        assert words in CLIENT_PROMPT, words


def test_the_client_writer_thinks_at_its_own_effort_with_its_own_schema(monkeypatch):
    import jyotish.narrate as n
    built = {}
    monkeypatch.setattr(n, "AnthropicDrafter", lambda config, client=None, schema=None, kind="writer":
                        built.update(config=config, schema=schema, kind=kind))
    anthropic_client_drafter(writer_config(CONFIG, "full", "claude-fable-5-1"), CONFIG)
    assert built["schema"] is ClientDraft and built["kind"] == "client"
    cfg = built["config"]
    assert (cfg.model, cfg.effort, cfg.thinking, cfg.max_tokens) == ("claude-fable-5-1", CONFIG.client_effort,
                                                                     "adaptive", CONFIG.client_max_tokens)


# --- the layer in a reading --------------------------------------------------------------------

def test_the_paragraph_and_summary_are_written_from_accepted_text_and_checked(chart):
    stub = Stub(refuse=("peaks in 2031",))
    w = Replay(draft(timing=REFUSED_TIMING + " " + TIMING), draft())
    c = client((SUMMARY, PARAGRAPH))
    r = run(chart, w, c, checker=stub)
    a = r.areas[0]
    assert a.paragraph == PARAGRAPH and a.when == WHEN and r.summary.text == SUMMARY and r.summary.source == "model"
    assert "fact:vimshottari.current" in a.when_cites and "fact:vargas.D10.Saturn" in a.paragraph_cites
    assert not [g for g in a.narration_gaps if g["kind"] in ("paragraph", "when")]
    # The client writer saw the accepted text only: the refused timing of attempt 1 never, the
    # accepted one, the judgement among them, the value of each fact cited, and nothing of the chart.
    sent = json.loads(c.calls[0]["user"])
    assert set(sent) == {"question", "as_of", "areas", "facts"}
    career = sent["areas"]["career"]
    assert career["timing"] == TIMING and "peaks in 2031" not in c.calls[0]["user"]
    assert career["not_decided"] == NOT_DECIDED and career["not_computed"] == NOT_COMPUTED
    assert career["judgements"] == [ASSESSMENT.split(". ", 1)[1]]
    assert set(sent["facts"]) == {"houses.lagna.10.lord", "vargas.D10.Saturn", "shadbala.planets.Saturn.ratio",
                                  "vimshottari.current", "not_computed.question_routing", "areas.career.votes.kp.vote"}
    assert sent["facts"]["vargas.D10.Saturn"] == {"sign": "Capricorn", "dignity": "own"}
    # Each sentence of the paragraph went to the checker; the weighing marked as a judgement.
    checked = {s: d for s, d in stub.calls}
    assert checked[VIEW]["judgement"] is True and "facts" in checked[VIEW] and WHEN in checked
    assert r.facts_cited["vimshottari.current"] and r.usage["client"]["calls"] == 1


def test_a_tradition_sentence_never_reaches_the_client_writer(chart):
    c = client((SUMMARY, PARAGRAPH))
    run(chart, Replay(draft(assessment=ASSESSMENT + " " + TRADITION)), c)
    assert "Phaladeepika" not in c.calls[0]["user"]


def test_a_refused_paragraph_is_retried_and_a_passed_summary_held(chart):
    from jyotish.narrate import RETRY_HEAD
    bad = "Five of the seven families vote for career [fact:vimshottari.current]."
    c = client((SUMMARY, bad), ("", PARAGRAPH))
    r = run(chart, Replay(draft()), c)
    assert r.areas[0].paragraph == PARAGRAPH and r.summary.text == SUMMARY and r.usage["client"]["attempts"] == 2
    ask = c.calls[1]["errors"][0]
    assert ask.startswith(RETRY_HEAD) and "Held: the summary; the career when." in ask and "- the career paragraph:" in ask
    assert "engine vocabulary ('families')" in ask


def test_a_paragraph_that_never_passes_is_a_gap_and_the_summary_the_engines(chart):
    bad = "Saturn's dignity outweighs its strength [fact:vargas.D10.Saturn]."
    r = run(chart, Replay(draft()), client(("Career is read here.", bad)))
    gaps = {g["finding_id"]: g for g in r.areas[0].narration_gaps}
    assert r.areas[0].paragraph is None and "paragraph" in gaps and "in the reading's view" in gaps["paragraph"]["last_error"]
    assert r.summary.source == "engine" and not r.narration_complete


def test_a_recording_made_before_the_client_layer_replays_with_gaps_not_failure(chart):
    rec = {"drafts": [draft()]}
    r = run(chart, FixtureDrafter(rec), FixtureDrafter(rec, key="client_drafts"))
    assert r.areas[0].analysis["timing"] == TIMING                      # what was accepted stands
    assert r.areas[0].paragraph is None and r.summary.source == "engine"
    assert any("no client draft" in g["last_error"] for g in r.areas[0].narration_gaps if g["finding_id"] == "paragraph")


def test_a_legacy_not_said_section_replays_as_the_astrologers_list(chart):
    old = {"summary": "", "areas": [{"name": "career", "claims": [], "analysis": {
        "assessment": ASSESSMENT, "timing": TIMING, "not_said": NOT_COMPUTED}}]}
    rec = {"drafts": [old]}
    r = run(chart, FixtureDrafter(rec), client((SUMMARY, PARAGRAPH)))
    assert r.areas[0].analysis["not_said_astrologer"] == NOT_COMPUTED and "not_said" not in r.areas[0].analysis
    assert rec["drafts"][0]["areas"][0]["analysis"]["not_said"] == NOT_COMPUTED     # the recording is untouched
    assert {g["finding_id"] for g in r.areas[0].narration_gaps if g["kind"] == "analysis"} == {"analysis.not_said_client"}


def test_the_clients_list_is_held_to_the_clients_words(chart):
    w = Replay(draft(not_decided="The KP family abstains on career [fact:areas.career.votes.kp.vote]."), draft())
    r = run(chart, w, client((SUMMARY, PARAGRAPH)))
    assert any("engine vocabulary ('family')" in e for e in w.calls[1]["errors"][0].splitlines())
    assert r.areas[0].analysis["not_said_client"] == NOT_DECIDED


# --- the page and the review step -------------------------------------------------------------

def test_the_page_puts_the_clients_layer_first_and_the_analysis_under_its_toggle(chart):
    from jyotish.page import render
    r = run(chart, Replay(draft()), client((SUMMARY, PARAGRAPH)))
    page = render(r, chart)
    career = page.split("## Career", 1)[1].split("\n## ", 1)[0]
    marks = ["### What the chart says for you", "Your work house is led by Saturn", "### When",
             "You are now in the period of Jupiter", "### What this chart does not tell", "- Which kind of work suits you",
             "- Tier: **", "<details><summary>The astrologer's analysis</summary>", "### Assessment", "### Timing",
             "### What the chart does not say", "- The KP family abstains", "</details>"]
    at = [career.index(m) for m in marks]
    assert at == sorted(at), list(zip(marks, at))
    assert career.count("Which kind of work suits you") == 1         # the client's list is not repeated below
    assert page.split("## Summary", 1)[1].lstrip().startswith("Your work house is led by Saturn")


def test_a_reviewers_edit_of_a_depth_full_paragraph_is_held_to_the_clients_words(chart):
    from jyotish.review import check_edit
    r = run(chart, Replay(draft()), client((SUMMARY, PARAGRAPH)))
    ok = check_edit(r, chart, "paragraph:career:0", "Saturn leads your work house and sits in its own sign in the "
                    "chart of career [fact:houses.lagna.10.lord] [fact:vargas.D10.Saturn].", Stub())
    assert ok["accepted"], ok["errors"]
    bad = check_edit(r, chart, "paragraph:career:0", "Five of the seven families vote for career "
                     "[fact:houses.lagna.10.lord].", Stub())
    assert not bad["accepted"] and any("engine vocabulary" in e for e in bad["errors"])
