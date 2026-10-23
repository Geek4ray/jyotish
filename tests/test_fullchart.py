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
SECTIONS = ["chart", "constants", "houses", "not_computed", "planets", "nakshatras", "lagnas", "special_points", "sensitive", "vargas", "lordship", "roles",
            "aspects", "dispositors", "jaimini", "ashtakavarga", "shadbala", "bhava_bala", "vimsopaka", "ishta_kashta",
            "argala", "sudarshana_h10", "panchanga", "rules", "areas", "driver", "vimshottari", "yogini", "chara",
            "period_quality", "transits", "timing", "stability"]
# The compact payload on the reference chart (as of 2026-10-21, three areas, ten years of transits)
# measured 356,177 characters on 2026-10-23 at first, and 402,380 once what the engine knows was
# labelled (the stability objects, the constants, houses and not_computed blocks), 423,836 once each
# family's term said what it holds (the review's F13; docs/spec_notes_2026-10-23.md).
# The bound is there so that growth is noticed and the recorded size updated.
MEASURED_CHARS = 423_836


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



# --- what the engine knows, stated (the second depth-full heading of the spec notes) --------------

def test_every_varga_row_carries_its_label_beside_the_number(whole):
    from jyotish.scoring import DIGNITY_SCORE
    rows = [r for a in whole["areas"].values() for r in ((a["votes"].get("varga") or {}).get("derivation") or [])]
    assert rows
    for r in rows:
        assert DIGNITY_SCORE[r["varga_dignity_label"]] == r["varga_dignity"]
        assert r["varga_dignity_label"] in ("exalted", "own", "friend", "neutral", "enemy", "debilitated")
    by = {(r["planet"], r["varga"]): r for r in whole["areas"]["career"]["votes"]["varga"]["derivation"]}
    assert (by[("Mars", "D10")]["varga_sign"], by[("Mars", "D10")]["varga_dignity_label"]) == ("Capricorn", "exalted")
    assert (by[("Saturn", "D10")]["varga_sign"], by[("Saturn", "D10")]["varga_dignity_label"]) == ("Capricorn", "own")


def test_the_varga_label_reaches_the_findings_the_checker_reads(chart):
    from jyotish.narrate import findings
    vote = next(f for f in findings(chart, "career", AS_OF)[0] if f["finding_id"] == "vote:career.varga")
    assert {r["varga_dignity_label"] for r in vote["derivation"]} >= {"exalted", "own"}


def test_stability_is_a_labelled_object_with_the_ayanamsa_count(whole):
    st = resolve(whole, "stability.placements.D10.Jupiter")
    assert set(st) == {"time", "ayanamsa", "house", "label", "ayanamsas", "house_systems"}
    assert st["ayanamsa"] == 0.667 and st["ayanamsas"] == "holds under 2 of 3 ayanamsas"
    area = resolve(whole, "areas.career.stability")
    assert area["ayanamsas"] == "holds under 3 of 3 ayanamsas" and area["label"] == "stable"
    assert all(isinstance(f["stability"], dict) for f in whole["rules"].values() if f["stability"])


def test_the_arudha_derivation_names_what_it_rests_on_and_why(whole):
    d = resolve(whole, "areas.career.votes.arudha.derivation")
    assert d["rests_on"] == ["A10"] and d["padas"][0]["pada"] == "A10"
    # A10 is Taurus, holding Jupiter (a benefic) and Saturn (a malefic): the vote abstains because they balance.
    assert (d["padas"][0]["sign"], d["padas"][0]["occupants"], d["padas"][0]["benefics"]) == ("Taurus", ["Jupiter", "Saturn"],
                                                                                          ["Jupiter"])
    assert resolve(whole, "areas.career.votes.arudha.vote") == 0
    assert d["why"] == "the benefics and malefics in A10 balance: the vote abstains"
    assert resolve(whole, "areas.marriage.votes.arudha.derivation.rests_on") == ["UL", "UL2", "A7"]


def test_constants_and_houses_are_citable_facts(chart, whole):
    assert resolve(whole, "constants.signs")[10] == "Aquarius"
    assert resolve(whole, "constants.sign_lords.Aquarius") == "Saturn"
    assert resolve(whole, "constants.exaltation.Mars") == "Capricorn"
    assert resolve(whole, "constants.debilitation.Mars") == "Cancer"
    assert resolve(whole, "constants.moolatrikona.Saturn") == "Aquarius"
    h10 = resolve(whole, "houses.lagna.10")
    assert h10 == {"sign": "Aquarius", "lord": "Saturn", "occupants": ["Sun", "Mercury"]}
    assert resolve(whole, "houses.sun.10.sign") == "Scorpio" and resolve(whole, "houses.moon.1.sign") == "Libra"
    assert validate("Aquarius is the 10th house from the lagna [fact:houses.lagna.10].", set(), facts=whole) == []


def test_not_computed_states_what_the_engine_does_not_do(whole):
    nc = whole["not_computed"]
    assert {"synastry", "rectification", "probability", "special_lagnas", "never"} <= set(nc)
    assert "second chart" in nc["synastry"] and "Hora" in nc["special_lagnas"]


def test_fields_say_their_reference_point(chart, whole):
    assert "tara" not in whole["planets"]["Venus"] and whole["planets"]["Venus"]["tara_from_moon"] == "Pratyak"
    assert all("tara_from_moon" in r for r in whole["nakshatras"].values())
    row = whole["transits"]["rows"][0]
    assert {"bav_grade", "good_from_moon"} <= set(row) and "grade" not in row
    assert resolve(whole, "areas.longevity.main_karaka") == chart.scored.areas["longevity"].karakas[0]
    w = whole["timing"]["career"]["windows"][0]
    antar = w["periods"]["vimshottari"][-1]
    assert w["dignity_of"] == f"{antar} ({chart.bodies[antar].dignity})"
    assert whole["period_quality"]["Venus"]["dignity_label"] == "exalted"


def test_bhava_bala_ranks_the_twelve_houses(chart, whole):
    ws = whole["bhava_bala"]["whole_sign"]
    assert sorted(h["rank_of_12"] for h in ws.values()) == list(range(1, 13))
    weakest = min(ws, key=lambda h: ws[h]["rupas"])
    assert ws[weakest]["rank_of_12"] == 12 and weakest == "H10"


# --- the families ranked by the engine --------------------------------------------------------

def test_contributions_rank_the_families_by_term_times_weight(chart, whole):
    from jyotish.scoring import family_rho, family_weights
    a = chart.scored.areas["career"]
    w = family_weights(a, family_rho(chart.meta.varga_term, chart.meta.kp_vote))
    c = resolve(whole, "areas.career.contributions")
    by = {r["family"]: r for r in c["ranked"]}
    assert set(by) == {"house", "lord", "karaka", "varga", "panchanga"}
    assert by["lord"]["term"] == round(a.terms["lord"] + a.terms["dispositor"], 3)    # the lord vote reads both
    for fam, r in by.items():
        assert abs(r["contribution"] - r["term"] * r["weight"]) < 0.002 and r["weight"] == round(w[fam], 3)
    assert [r["contribution"] for r in c["ranked"]] == sorted((r["contribution"] for r in c["ranked"]), reverse=True)
    assert [r["rank"] for r in c["ranked"]] == [1, 2, 3, 4, 5]
    assert c["strongest"] == c["ranked"][0]["family"] == "lord" and c["weakest"] == c["ranked"][-1]["family"]
    applicable = {f for f, v in a.votes.items() if v is not None}
    shares = [r["share_of_applicable_weight"] for r in c["ranked"] + c["vote_only"]]
    assert abs(sum(shares) - 1.0) < 0.01 and {r["family"] for r in c["vote_only"]} == applicable & {"arudha", "kp"}
    assert c["abstaining"] == ["arudha", "kp"] and c["against"] == []
    assert resolve(whole, "areas.marriage.contributions.against") == ["arudha"]
    assert "contributions" not in whole["areas"]["synastry"]



# --- the review of 2026-10-23, F3, F9, F12, F13 ---------------------------------------------------

def _walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{path}.{k}" if path else str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _walk(v, f"{path}.{i}")
    yield path, node


def test_every_path_in_the_payload_resolves_to_its_value(whole):
    """F3: the rules' keys held dots and none could be cited; walking the whole payload finds any key
    that cannot be."""
    n = 0
    for path, value in _walk(whole):
        if path:
            assert resolve(whole, path) == value, path
            n += 1
    assert n > 10_000
    assert resolve(whole, "rules.place-l7_h7@lagna.status") == "draft"
    assert resolve(whole, "rules.yoga-ruchaka@lagna.id") == "yoga.ruchaka"
    assert validate("Mars in the 7th is a draft placement [fact:rules.place-l7_h7@lagna.status].", set(), facts=whole) == []


def test_no_absolute_longitude_in_the_payload(chart, whole):
    """F9: the Bhava Bala madhyas were longitudes; every position is now a sign and a degree in it."""
    for system in ("whole_sign", "sripati"):
        for h, row in whole["bhava_bala"][system].items():
            assert isinstance(row["madhya"], str) and row["madhya"].split()[0] in resolve(whole, "constants.signs"), (system, h)
    assert whole["bhava_bala"]["whole_sign"]["H1"]["madhya"].startswith("Taurus 6°")
    # No field that names a position holds a number (a figure that happens to equal a longitude, like a
    # Shadbala bala of 36.3, is not one); the header's lon is the birthplace's, not a position in the sky.
    positions = {"madhya", "cusp", "mc", "asc", "lon", "longitude", "start", "end"}
    for path, value in _walk(whole):
        key = path.rsplit(".", 1)[-1]
        if key in positions and not path.startswith(("transits", "timing", "vimshottari", "yogini", "chara", "chart.header")):
            assert not isinstance(value, float), path


def test_houses_follow_the_house_system_and_say_which(whole):
    """F12: under sripati the houses from the lagna are the bhavas, as planets.<p>.house is."""
    from datetime import datetime
    from jyotish.chart import compute
    from jyotish.reference import REFERENCE_BIRTH_UTC as utc
    assert whole["houses"]["system"] == {"lagna": "whole_sign", "moon": "whole_sign", "sun": "whole_sign"}
    sp = compute(utc, REFERENCE_LAT, REFERENCE_LON, house_system="sripati", true_node=False)
    from jyotish.fullchart import _houses
    h = _houses(sp)
    assert h["system"]["lagna"] == "sripati" and h["system"]["moon"] == "whole_sign"
    for p, b in sp.bodies.items():
        assert p in h["lagna"][str(b.house)]["occupants"], p
    assert any(sp.bodies[p].house != (sp.bodies[p].sign - sp.lagnas.asc_sign) % 12 + 1 for p in sp.bodies)   # they differ here


def test_one_term_per_family_named_for_what_it_holds(chart, whole):
    """F13: the lord family's term was the lord term alone in the votes and lord plus dispositor in
    the contributions; now one term, with the S terms it holds."""
    a = chart.scored.areas["career"]
    lord = resolve(whole, "areas.career.votes.lord")
    assert lord["term_holds"] == ["lord", "dispositor"]
    assert lord["term"] == round(a.terms["lord"] + a.terms["dispositor"], 3)
    assert resolve(whole, "areas.career.votes.house.term_holds") == ["house"]
    assert resolve(whole, "areas.career.votes.kp.term") is None


def test_the_first_maha_flag_is_computed(chart, whole):
    from jyotish.dasha import vimshottari
    first = vimshottari(chart.bodies["Moon"].lon, chart.meta.jd, levels=1)[0]
    assert whole["vimshottari"]["first_maha_starts_before_birth"] is (first.start_jd < chart.meta.jd)
