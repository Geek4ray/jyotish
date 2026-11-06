"""Ray's first use of the live chat (2026-11-02; "how much money will i earn in my life, will i be rich", then
"whan and how"), each fix's test (docs/spec_notes_2026-11-02.md): the writer's material in plain words only, the
never-show list as refusals, "when", "why" and "how" read with the same spelling tolerance as area words, and the
question answered as asked."""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

from jyotish.conversation import OfflineTurnWriter, Route, _material, route_turn
from jyotish.narrate import engine_reading
from jyotish.scoring import AREAS
from jyotish.uncertainty import assess

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 11, 2)
BIRTHS = json.loads((ROOT / "tests" / "fixtures" / "births.json").read_text())["births"]
MONEY = "how much money will i earn in my life, will i be rich"


def _chart(b):
    return assess(datetime.fromisoformat(b["utc"]), b["lat"], b["lon"], true_node=False, seed=0)


@pytest.fixture(scope="module")
def charts():
    return {b["name"]: _chart(b) for b in BIRTHS}


@pytest.fixture(scope="module")
def chart(charts):
    return charts["reference"]


def as_of(b) -> date:
    born = datetime.fromisoformat(b["utc"]).date()
    return AS_OF if born < AS_OF else born.replace(year=born.year + 30)


def material(chart, message, route, when=AS_OF):
    engine = engine_reading(chart, message, "both" if route.why else route.direction, route.areas, as_of=when,
                            when=route.when, weakest=route.areas_from == "weakest" and not route.why)
    return _material(chart, message, route, engine, [], when)


# --- 1. the writer's material is plain words only -------------------------------------------------------------------

# A label the writer copied back to the client, or engine vocabulary: none is in what the writer is given. "for" and
# "against" are refused as labels (a value, "is for", "are against"); "works against" is the material's own lean word.
LABELS = re.compile(r"\bvotes?\b|\bfamil(?:y|ies)\b|\btiers?\b|\bmarked as\b|\bindications?\b|\bverdict\b|"
                    r"\bderivation\b|\bglossary\b|\bfinding_id\b|\bscores?\b|\bKP\b|\bKrishnamurti\b|\bD\d{1,2}\b|"
                    r"\barudha|\bdasha|\bcusp|\bsub-?lord|\bShadbala|\bBhava Bala|\bkaraka|\blagna\b|"
                    r"\"(?:for|against)\"|\b(?:is|are) (?:for|against)\b|(?<!work )(?<!works )\bagainst\b", re.I)


@pytest.mark.parametrize("name", [b["name"] for b in BIRTHS])
def test_1_the_writers_material_carries_no_label_on_any_area_or_direction(charts, name):
    chart = charts[name]
    when = as_of(next(b for b in BIRTHS if b["name"] == name))
    for area in AREAS:
        if area == "synastry":
            continue
        for direction in ("against", "for", "both"):
            user = material(chart, "q", Route(areas=[area], direction=direction), when)[0]
            m = LABELS.search(user)
            assert m is None, (name, area, direction, m.group(0), user[max(0, m.start() - 80):m.end() + 40])


def test_1_the_material_is_the_engines_answer_and_one_plain_sentence_per_finding(chart):
    user, finding_data, tags, votes, chains, handles = material(chart, MONEY, route_turn(MONEY, chart))
    body = json.loads(user)
    assert set(body) == {"message", "asked_about", "asks_when", "asks_why", "asks_how", "earlier_turns",
                         "engine_answer", "areas"}
    assert body["asked_about"] == "the good and the hard"
    (area,) = body["areas"]
    assert area["area"] == "money" and all(set(f) == {"tag", "says"} for f in area["findings"])
    says = {f["tag"]: f["says"] for f in area["findings"]}
    # Each finding's tag is a handle for its own tag; the engine's sentences cite the same handles.
    assert all(re.fullmatch(r"f\d+", t) for t in says) and set(handles.real) >= set(says)
    assert {handles.real[t] for t in says} <= tags
    assert all(re.fullmatch(r"f\d+", t) for s in body["engine_answer"] for t in s["tags"])
    # Frozen: which way each finding leans, in the material's own words.
    assert "The signs that show how others see money, Libra and Cancer, work against it: the Moon sits there, with " \
           "no helpful planet beside." in says.values()
    assert "Taken together, the houses that govern money support it: the main one, the 2nd house from your rising " \
           "sign, in Gemini, is better supported than most of your twelve houses." in says.values()
    assert "Jupiter and Venus form the Parivartana yoga, which is an exchange of signs: two planets each sitting in " \
           "the sign the other rules, joining the 1st and 11th houses; it supports money." in says.values()
    assert "Mercury, the ruler of the 2nd house, sits in the 10th house; the 2nd is a house of money; it is a " \
           "placement only, with no lean of its own." in says.values()
    assert len(user) < 6000                            # 45,053 characters before (the findings' whole data)


def test_1_a_handle_is_put_back_to_its_findings_tag_before_the_checks(chart):
    *_, handles = material(chart, MONEY, route_turn(MONEY, chart))
    h = handles.of["vote:wealth.house"]
    assert handles.to_real(f"Your money houses are well placed [{h}].") == "Your money houses are well placed " \
                                                                         "[vote:wealth.house]."
    two = handles.of["rule:yoga.parivartana"]
    assert handles.to_real(f"Two planets trade places [{h}, {two}].").endswith(
        "[vote:wealth.house] [rule:yoga.parivartana].")
    assert handles.to_real("A made-up one [f999].") == "A made-up one [f999]."           # refused as not offered
    assert handles.to_handles("tag not offered for this finding: [vote:wealth.house]") == \
        f"tag not offered for this finding: [{h}]"


def test_1_a_turn_cites_handles_and_is_checked_against_the_real_findings(chart):
    from jyotish.conversation import OfflineTurnWriter, answer_turn
    from jyotish.narrate import CheckResult, Proposition
    seen = []

    def checker(sentence, data):
        seen.append(data)
        return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])
    route = route_turn(MONEY, chart)
    doc = answer_turn(chart, MONEY, route, as_of=AS_OF, drafter=OfflineTurnWriter(), checker=checker)
    assert doc["source"] == "writer" and doc["accepted"]
    assert all("[f" not in s for s in doc["accepted"]) and any("[vote:wealth.house]" in s for s in doc["accepted"])
    assert any('"family": "house"' in d for d in seen)         # the checker reads the finding's whole data
    assert not any("[" in s for s in doc["shown"])


# --- 2. what the conversation never shows, as refusals -------------------------------------------------------------

def passes(sentence, data):
    from jyotish.narrate import CheckResult, Proposition
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


def judged(chart, sentence, areas=("wealth",)):
    from jyotish.conversation import check_sentence, held_to
    tags, votes, chains, finding_data = held_to(chart, Route(areas=list(areas)), AS_OF)
    return check_sentence(sentence, tags, votes, chains, finding_data, passes)


RAY = ["The image point of wealth is marked as against. [vote:wealth.arudha]",
       "The overall wealth indications are for. [vote:wealth.house]",
       "The image point of wealth (arudha) falls in Libra and Cancer. [vote:wealth.arudha]"]
NEVER = ["The KP analysis of the second house favours money. [vote:wealth.kp]",
         "The Krishnamurti reading of the second house favours money. [vote:wealth.kp]",
         "The houses of money vote favourably. [vote:wealth.house]",
         "The house family leans favourably for money. [vote:wealth.house]",
         "Both families agree on money. [vote:wealth.house]",
         "In the D2, Venus is placed well. [vote:wealth.varga]",
         "The houses of money score well. [vote:wealth.house]",
         "Your Jupiter dasha favours money. [vote:wealth.karaka]",
         "The cusp of the second house favours money. [vote:wealth.kp]",
         "The sub-lord of the second house favours money. [vote:wealth.kp]",
         "Mercury's Shadbala favours money. [vote:wealth.lord]",
         "The Bhava Bala of the second house favours money. [vote:wealth.house]",
         "The planets that signify money are against. [vote:wealth.karaka]",
         "The houses of money count for, on balance. [vote:wealth.house]"]


@pytest.mark.parametrize("sentence", RAY + NEVER)
def test_2_the_never_show_list_refuses_each_word_with_what_to_say_instead(chart, sentence):
    ok, refusals, warnings, _ = judged(chart, sentence)
    assert not ok and any(r.startswith("never shown to the client") and ": say " in r for r in refusals), refusals
    assert warnings == []                                  # a refused sentence's word warnings are not kept


@pytest.mark.parametrize("sentence", [
    "Your family and your money are both matters of the 2nd house. [vote:wealth.house]",
    "The house of money and family sits in Gemini. [vote:wealth.house]",
    "Family life is one of the things the 2nd house governs. [vote:wealth.house]",
    "Jupiter sits in Taurus, a sign of Scorpio's opposite. [vote:wealth.karaka]",
    "Taken together, the houses that govern money support it. [vote:wealth.house]",
    "The signs that show how others see money work against it. [vote:wealth.arudha]",
    "This part of the reading is for you to keep in mind. [vote:wealth.house]"])
def test_2_ordinary_words_are_not_refused(chart, sentence):
    from jyotish.client import never_show
    assert never_show(sentence) == [], sentence


def test_2_the_softer_rules_stay_warnings(chart):
    for sentence in ("I see Jupiter in Taurus, in an unfriendly sign. [vote:wealth.karaka]",
                     "Venus sits in Revati, a nakshatra of Mercury. [vote:wealth.karaka]",
                     "Its 2nd house sits in Gemini. [vote:wealth.house]"):
        from jyotish.client import never_show
        assert never_show(sentence) == [], sentence
    ok, refusals, warnings, _ = judged(chart, "I see Jupiter in Taurus, in an unfriendly sign. [vote:wealth.karaka]")
    assert ok and refusals == [] and any("never says 'I'" in w for w in warnings)


class OneMarked(OfflineTurnWriter):
    """Writes three tagged sentences, the second a vote line copied ("marked as"); asked again, rewrites that one."""
    def __init__(self):
        self.calls = []

    def __call__(self, system, user, errors):
        from jyotish.conversation import TurnDraft
        from jyotish.narrate import RETRY_HEAD
        self.calls.append(errors)
        said = [x for x in json.loads(user)["engine_answer"] if x["tags"]][:3]
        self.last_meta = {"kind": "writer", "replayed": True}
        if errors and errors[0].startswith(RETRY_HEAD):
            return TurnDraft(answer=f"{said[1]['text'][:-1]} [{said[1]['tags'][0]}].")
        out = [f"{x['text'][:-1]} [{x['tags'][0]}]." for x in said]
        out[1] = f"The planets that rule the houses of money are marked as for [{said[1]['tags'][0]}]."
        return TurnDraft(answer=" ".join(out))


def test_2_a_refused_sentence_is_retried_alone_and_never_shown(chart):
    from jyotish.conversation import OfflineTurnWriter, answer_turn  # noqa: F401
    from jyotish.narrate import RETRY_HEAD
    writer = OneMarked()
    route = route_turn(MONEY, chart)
    doc = answer_turn(chart, MONEY, route, as_of=AS_OF, drafter=writer, checker=passes)
    assert len(writer.calls) == 2 and writer.calls[1][0].startswith(RETRY_HEAD)
    retry = writer.calls[1][0]
    assert "- sentence 2 (" in retry and "never shown to the client ('marked as')" in retry and "[vote:" not in retry
    assert any("marked as" in x["sentence"] for x in doc["removed"])
    assert len(doc["shown"]) == 3 and not any("marked" in s for s in doc["shown"])


def test_2_every_engine_sentence_the_client_can_see_passes_the_never_show_list(charts):
    from jyotish.client import never_show
    for b in BIRTHS:
        chart, when = charts[b["name"]], as_of(b)
        for area in AREAS:
            if area == "synastry":
                continue
            for direction in ("against", "for", "both"):
                ans = engine_reading(chart, "q", direction, [area], as_of=when, when=True)
                for s in ans.sentences:
                    assert never_show(s.text) == [], (b["name"], area, s.text)


def test_2_the_sentences_of_rays_screen_are_benchmark_rows_the_validator_refuses():
    import importlib.util
    spec = importlib.util.spec_from_file_location("checker_bench", ROOT / "scripts" / "checker_bench.py")
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    rows = {r["id"]: r for r in bench.load()}
    ids = ["live-ans-ray-image-point-marked", "live-ans-ray-indications-are-for", "live-ans-ray-arudha",
           "live-ans-house-family-is-for", "live-ans-kp-analysis"]
    for rid in ids:
        r = rows[rid]
        assert (r["where"], r["category"], r["label"]) == ("answer", "client_words", "reject")
        assert any(e.startswith("never shown to the client") for e in bench.validator_errors(r)), rid
    assert [r["sentence"] for r in rows.values() if r["id"] in ids[:2]] == [RAY[0], RAY[1]]


# --- 3. "when", "why" and "how", read with the spelling tolerance area words have -------------------------------------

@pytest.mark.parametrize("message,when,why,how", [
    ("whan and how", True, False, True), ("wen will i marry", True, False, False), ("whne?", True, False, False),
    ("kab hogi shaadi", True, False, False), ("when?", True, False, False), ("wy?", False, True, False),
    ("kyun", False, True, False), ("kyon?", False, True, False), ("but how?", False, False, True),
    ("paisa kaise aayega", False, False, True), ("how?", False, False, True), ("when and why", True, True, False),
    # never read as one: common words a letter away, and "how" asking how something is
    ("i went to school", False, False, False), ("who am i", False, False, False), ("how is my career", False, False, False),
    (MONEY, False, False, False), ("how about marriage", False, False, False), ("then what", False, False, False),
    ("how soon will i marry", True, False, False), ("how come?", False, True, False)])
def test_3_when_why_and_how_are_read_with_spelling_tolerance(chart, message, when, why, how):
    last = route_turn(MONEY, chart)
    route = route_turn(message, chart, last)
    assert (route.when, route.why, route.how) == (when, why, how), route


def answered(chart, writer_cls=None, messages=(MONEY, "whan and how")):
    from jyotish.conversation import answer_turn
    out, last, history = [], None, []
    for m in messages:
        route = route_turn(m, chart, last)
        doc = answer_turn(chart, m, route, as_of=AS_OF, history=list(history),
                          drafter=(writer_cls or OfflineTurnWriter)(), checker=passes)
        out.append((route, doc))
        history.append({"question": m, "answer": " ".join(doc["shown"])})
        last = route
    return out


def test_3_whan_and_how_after_the_money_question_gives_the_stretches_and_restates_nothing(chart):
    from jyotish.conversation import restates
    from jyotish.narrate import sentences
    (r1, first), (r2, second) = answered(chart)
    assert r2.areas == ["wealth"] and r2.follow_up and "areas" in r2.carried and r2.when and r2.how
    assert any("favourable stretch for money" in s for s in second["shown"])
    assert second["shown"][-1] == "Neither stretch is a prediction of when you will act."
    said = [x for s in first["shown"] for x in sentences(s)]
    for s in second["shown"]:
        if s in OfflineTurnWriter.OPENER.values():          # the offline stub's opener, not the chart
            continue
        assert s not in said and restates(s, [" ".join(first["shown"])]) is None, s
    assert not any(e["text"] in " ".join(first["shown"]) for e in second["engine"]["sentences"])


class Repeats(OfflineTurnWriter):
    """On a follow-up, writes again the first sentence the client read on the last turn, then the engine's."""
    def __call__(self, system, user, errors):
        from jyotish.conversation import TurnDraft
        body = json.loads(user)
        draft = super().__call__(system, user, errors)
        if body["earlier_turns"] and not errors:
            from jyotish.narrate import sentences
            area = next(f for a in body["areas"] for f in a["findings"] if "houses that govern" in f["says"])
            old = sentences(body["earlier_turns"][-1]["answer"])[1]
            return TurnDraft(answer=f"{old[:-1]} [{area['tag']}]. " + draft.answer)
        return draft


def test_3_a_writers_sentence_that_restates_the_last_answer_is_refused_and_retried(chart):
    (_, first), (_, second) = answered(chart, Repeats)
    assert any(any("restates a sentence an earlier answer gave" in r for r in x["reasons"]) for x in second["removed"])
    assert not (set(second["shown"]) & set(first["shown"])) - set(OfflineTurnWriter.OPENER.values())


def test_3_a_follow_up_naming_an_area_is_new_by_its_area(chart):
    (_, first), (r2, second) = answered(chart, messages=("how is my career", "and marriage?"))
    assert r2.areas == ["marriage"] and "areas" not in r2.carried
    assert not any("restates" in r for x in second["removed"] for r in x["reasons"])
