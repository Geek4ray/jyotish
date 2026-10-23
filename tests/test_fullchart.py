"""Depth full, part 1: the whole chart to the writer (fullchart.payload) and the [fact:<path>] tag,
offline on the reference chart, with the writer replayed and the checker stubbed."""

from datetime import date
from types import SimpleNamespace

import pytest

from jyotish.fullchart import dumps, payload, resolve
from jyotish.narrate import (
    CONFIG, STREAM_ABOVE, AnthropicDrafter, ReadingDraft, full_range, narrate, system_prompt, validate, writer_config,
)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
QUESTION = "How will my career go?"
SECTIONS = ["chart", "planets", "nakshatras", "lagnas", "special_points", "sensitive", "vargas", "lordship", "roles",
            "aspects", "dispositors", "jaimini", "ashtakavarga", "shadbala", "bhava_bala", "vimsopaka", "ishta_kashta",
            "argala", "sudarshana_h10", "panchanga", "rules", "areas", "driver", "vimshottari", "yogini", "chara",
            "period_quality", "transits", "timing", "stability"]
# The compact payload on the reference chart (as of 2026-10-21, three areas, ten years of transits)
# measured 356,177 characters on 2026-10-23 (docs/spec_notes_2026-10-23.md). The bound is there so
# that growth is noticed and the recorded size updated.
MEASURED_CHARS = 356_177


@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


@pytest.fixture(scope="module")
def whole(chart):
    return payload(chart, AS_OF, *full_range(AS_OF), ["career", "marriage", "longevity"])


class Stub:
    def __init__(self):
        self.calls = []
        self.last_meta = None

    def __call__(self, sentence, data):
        from jyotish.narrate import CheckResult, Proposition
        self.calls.append((sentence, data))
        return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


class Replay:
    def __init__(self, draft):
        self.draft = ReadingDraft(**draft)
        self.calls = []

    def __call__(self, system, user, errors):
        self.calls.append({"system": system, "user": user, "errors": errors})
        return self.draft


def test_every_section_is_present_and_every_value_the_charts_own(chart, whole):
    assert list(whole) == SECTIONS
    assert resolve(whole, "planets.Mars.dignity") == chart.bodies["Mars"].dignity == "own"
    assert resolve(whole, "vargas.D9.Mars") == ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
                                               "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
                                               "Pisces"][chart.vargas["D9"]["Mars"]]
    assert resolve(whole, "shadbala.planets.Mars.ratio") == round(chart.features.shadbala.planets["Mars"].ratio, 2)
    assert resolve(whole, "areas.career.tier") == chart.scored.areas["career"].tier
    assert resolve(whole, "areas.career.votes.kp.vote") == chart.scored.areas["career"].votes["kp"]
    assert resolve(whole, "ashtakavarga.SAV") == chart.features.ashtakavarga.SAV
    assert len(whole["vargas"]) == 17                          # D1 and the sixteen vargas
    assert {f["status"] for f in whole["rules"].values()} >= {"draft", "experimental", "classical_unconfirmed"}
    assert len(whole["rules"]) == len(chart.fired_rules)       # every fire, placements and experimental ones too


def test_dashas_to_the_pratyantar_with_the_current_period(chart, whole):
    from jyotish.narrate import Reading  # noqa: F401  (the reading's current period is the payload's)
    vim = whole["vimshottari"]
    levels = {len(k.split("-")) for k in vim["periods"]}
    assert levels == {1, 2, 3}
    assert sum(1 for k in vim["periods"] if "-" not in k) == 9
    cur = vim["current"].split("-")
    assert len(cur) == 3
    row = vim["periods"][vim["current"]]
    assert row["start"] <= AS_OF.isoformat() < row["end"]
    assert "start_spread_days" in vim["periods"]["-".join(cur[:2])]      # a maha or antar carries its sampler stamp
    for system in ("yogini", "chara"):
        i = whole[system]["current"]
        assert whole[system]["periods"][i]["start"] <= AS_OF.isoformat() < whole[system]["periods"][i]["end"]


def test_transits_and_windows_for_the_range_and_no_longitudes(chart, whole):
    tr = whole["transits"]
    assert tr["range"] == {"start": "2026-10-21", "end": full_range(AS_OF)[1].isoformat()}
    assert {r["body"] for r in tr["rows"]} == {"Sun", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"}
    assert tr["windows"] and all(w["start"] < tr["range"]["end"] for w in tr["windows"])
    assert set(whole["timing"]) == {"career", "marriage", "longevity"}
    text = dumps(whole)
    assert f"{chart.bodies['Mars'].lon:.3f}" not in text and f"{chart.lagnas.asc:.3f}" not in text


def test_payload_size_is_recorded(whole):
    n = len(dumps(whole))
    assert abs(n - MEASURED_CHARS) / MEASURED_CHARS < 0.10, f"payload is {n} characters: update the recorded size"


def test_resolve_takes_keys_and_list_indices_and_refuses_the_rest(whole):
    assert resolve(whole, "yogini.periods.0.lords") == whole["yogini"]["periods"][0]["lords"]
    for bad in ("planets.Pluto", "planets.Mars.dignity.x", "yogini.periods.99999", "planets..Mars", "planets.Mars "):
        with pytest.raises(KeyError):
            resolve(whole, bad)


# --- the [fact:] tag ---------------------------------------------------------------------

def test_fact_tag_is_valid_where_its_path_exists(whole):
    ok = "Mars is in its own sign [fact:planets.Mars.dignity]."
    assert validate(ok, set(), facts=whole) == []
    bad = validate("Mars is in its own sign [fact:planets.Mars.dignty].", set(), facts=whole)
    assert len(bad) == 1 and "no field at path 'planets.Mars.dignty'" in bad[0]
    assert any("not offered" in e for e in validate(ok, set()))          # no whole chart: no fact is offered


def test_a_sentence_citing_a_fact_may_state_timing_and_one_without_may_not(whole):
    dated = "The current Vimshottari period is Jupiter-Mercury, from 2025-11-17 [fact:vimshottari.current]."
    assert validate(dated, set(), facts=whole) == []
    assert any("timing language" in e for e in validate("The dasha favours career [rule:yoga.ruchaka].",
                                                         {"rule:yoga.ruchaka"}, facts=whole))


def test_full_depth_writer_gets_the_chart_and_the_checker_the_cited_value(chart):
    import json
    draft = {"summary": "Mars is in its own sign [fact:planets.Mars.dignity].",
             "areas": [{"name": "career", "claims": [{"finding_id": "vote:career.house", "text":
                        "The house vote is for career, with the 10th at 4.51 rupas [vote:career.house] "
                        "[fact:bhava_bala.whole_sign.H10.rupas]."}]}]}
    w, c = Replay(draft), Stub()
    r = narrate(chart, QUESTION, drafter=w, checker=c, as_of=AS_OF, areas=["career"], depth="full")
    body = json.loads(w.calls[0]["user"])
    assert body["depth"] == "full" and list(body["chart"]) == SECTIONS
    assert "\n" not in w.calls[0]["user"]                                     # compact
    data = {s: json.loads(d) for s, d in c.calls}
    assert data[draft["summary"]]["facts"] == {"planets.Mars.dignity": "own"}
    claim = draft["areas"][0]["claims"][0]["text"]
    assert data[claim]["facts"] == {"bhava_bala.whole_sign.H10.rupas":
                                    round(chart.features.bhava_bala.whole_sign[10].rupas, 2)}
    assert data[claim]["finding"]["finding_id"] == "vote:career.house"
    assert r.facts_cited == {"planets.Mars.dignity": "own",
                             "bhava_bala.whole_sign.H10.rupas": round(chart.features.bhava_bala.whole_sign[10].rupas, 2)}
    assert r.depth == "full" and r.summary.source == "model"


def test_full_depth_prompt_and_max_tokens():
    full, base = system_prompt("full"), system_prompt("astrologer")
    assert "[fact:<path>]" in full and "[fact:" not in base
    assert "do not mention timing" in base and "do not mention timing" not in full
    assert writer_config(CONFIG, "full").max_tokens == CONFIG.full_max_tokens > STREAM_ABOVE
    assert writer_config(CONFIG, "astrologer").max_tokens == CONFIG.max_tokens


def test_a_long_request_is_streamed_and_the_payload_cached():
    """AnthropicDrafter sends max_tokens above STREAM_ABOVE through messages.stream, and marks the
    first user message (the payload) for the prompt cache."""
    seen = {}
    draft = ReadingDraft(summary="x", areas=[])

    class Stream:
        def __init__(self, **kw):
            seen.update(kw, how="stream")

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def get_final_message(self):
            return SimpleNamespace(parsed_output=draft, stop_reason="end_turn", content=[], usage=None, model="m")

    def parse(**kw):
        seen.update(kw, how="parse")
        return SimpleNamespace(parsed_output=draft, stop_reason="end_turn", content=[], usage=None, model="m")

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=Stream, parse=parse)))
    AnthropicDrafter(writer_config(CONFIG, "full"), client=client)("system", "payload", [])
    assert seen["how"] == "stream" and seen["max_tokens"] == CONFIG.full_max_tokens
    assert seen["messages"][0]["content"][0]["cache_control"] == {"type": "ephemeral"}
    AnthropicDrafter(CONFIG, client=client)("system", "payload", [])
    assert seen["how"] == "parse" and seen["max_tokens"] == CONFIG.max_tokens


def test_page_footnotes_a_fact_with_its_value(chart):
    from jyotish.page import render
    draft = {"summary": "Mars is in its own sign [fact:planets.Mars.dignity].", "areas": []}
    r = narrate(chart, QUESTION, drafter=Replay(draft), checker=Stub(), as_of=AS_OF, areas=["career"], depth="full")
    page = render(r, chart)
    assert "`fact:planets.Mars.dignity`: The chart's field `planets.Mars.dignity`, computed by the engine: `\"own\"`." in page
