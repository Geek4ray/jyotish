"""The live narration (2026-10-26; jyotish.live) against a stub OpenAI-compatible server: the areas
written in parallel, each draft streamed in small pieces, a sentence shown being verified, verified
when the checker passes it, removed when it refuses it and the writer's replacement streamed the
same way; the summary last; the API's server-sent events and the polling fallback."""

import json
import threading
import time
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from jyotish.live import JsonStrings, Live, LiveLog
from jyotish.narrate import narrate
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)
FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "narration_career_edited.json").read_text())
DRAFT = FIXTURE["drafts"][0]
AREA = {a["name"]: a for a in DRAFT["areas"]}
REFUSED = AREA["career"]["claims"][0]["text"]                   # the checker refuses this sentence, once written
REPLACEMENT = REFUSED.replace("The Sun and Mercury conjoined in the 10th house form",
                              "In the 10th house the Sun and Mercury, conjoined, form")
UNIT = f"claim:career:{AREA['career']['claims'][0]['finding_id']}"


class Handler(BaseHTTPRequestHandler):
    requests: list = []
    claims: dict = {"career": AREA["career"]["claims"]}     # the other areas' from their votes (the chart fixture)
    delay = 0.0                                             # seconds between streamed pieces and before a verdict
    check_delay = None                                      # seconds before a verdict (default: 10 x delay)
    answer = None                                           # (schema name, body, user messages) -> content, or None

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Handler.requests.append(body)
        name = body["response_format"]["json_schema"]["name"]
        users = [m["content"] for m in body["messages"] if m["role"] == "user"]
        own = Handler.answer(name, body, users) if Handler.answer else None
        if own is not None:
            content = own
        elif name == "CheckResult":
            time.sleep(Handler.delay * 10 if Handler.check_delay is None else Handler.check_delay)
            sentence = users[0].split("\n")[1]
            ok = sentence != REFUSED
            content = json.dumps({"propositions": [{"text": sentence, "supported": ok,
                                                    "evidence": "stub" if ok else "not in the data"}]})
        elif name == "SummaryDraft":
            content = json.dumps({"summary": DRAFT["summary"]})
        else:                                                   # one area's draft: the area named in its payload
            area = next(n for n in Handler.claims if f"{n}.house" in users[0])
            claims = [dict(c) for c in Handler.claims[area]]
            if area == "career" and len(users) > 1:             # the retry: the refused claim rewritten
                claims[0]["text"] = REPLACEMENT
            content = json.dumps({"summary": "", "areas": [{"name": area, "claims": claims}]})
        usage = {"prompt_tokens": 100, "completion_tokens": 50}
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            for i in range(0, len(content), 40):               # small pieces, as a model streams
                self.wfile.write(b"data: " + json.dumps({"id": "s", "choices": [{"delta": {"content": content[i:i + 40]}}]}).encode()
                                 + b"\n\n")
                self.wfile.flush()
                time.sleep(Handler.delay)
            self.wfile.write(b"data: " + json.dumps({"id": "s", "choices": [{"delta": {}, "finish_reason": "stop"}],
                                                     "usage": usage}).encode() + b"\n\ndata: [DONE]\n\n")
            return
        data = json.dumps({"id": "r", "model": body["model"], "usage": usage,
                           "choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


@pytest.fixture(scope="module")
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/v1"
    srv.shutdown()


@pytest.fixture(scope="module")
def chart():
    from jyotish.narrate import engine_line, findings
    c = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    for name in c.scored.areas:                 # a vote claim per family: the engine's line with its tag
        if name != "career":
            Handler.claims[name] = [{"finding_id": f["finding_id"], "text": engine_line(f, name)[:-1] + f" [{f['allowed_tags'][0]}]."}
                                    for f in findings(c, name, AS_OF)[0] if f["kind"] == "vote"]
    return c


@pytest.fixture
def backends(server, monkeypatch):
    monkeypatch.setenv("JYOTISH_OPENAI_KEY", "stub-key")
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "4")
    monkeypatch.setenv("JYOTISH_WRITER_BACKEND", f"openai:{server}:stub-writer")
    monkeypatch.setenv("JYOTISH_CHECKER_BACKEND", f"openai:{server}:stub-checker")
    Handler.requests.clear()
    return server


def test_json_strings_reports_each_field_as_it_grows_and_closes():
    seen = []
    reader = JsonStrings(lambda path, value, done: seen.append((path, value, done)))
    text = json.dumps({"summary": "A. B [vote:x].", "areas": [{"name": "career", "claims": [{"finding_id": "f", "text": "C \"q\"."}]}]})
    for i in range(0, len(text), 3):
        reader.feed(text[i:i + 3])
    closed = [(p, v) for p, v, d in seen if d]
    assert closed == [(("summary",), "A. B [vote:x]."), (("areas", 0, "name"), "career"),
                      (("areas", 0, "claims", 0, "finding_id"), "f"), (("areas", 0, "claims", 0, "text"), 'C "q".')]
    growing = [v for p, v, d in seen if p == ("summary",) and not d]
    assert growing and all("A. B [vote:x].".startswith(v) for v in growing)


@pytest.fixture
def streamed(chart, backends):
    events = []
    lock = threading.Lock()

    def emit(e):
        with lock:
            events.append(e)
    live = Live(emit)
    r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career", "marriage"], live=live)
    return r, events, live


def test_a_sentence_is_shown_removed_and_its_replacement_verified(streamed):
    r, events, _ = streamed
    mine = [e for e in events if e.get("unit") == UNIT]
    kinds = [e["type"] for e in mine]
    # Shown being verified, removed by the checker, the replacement shown, verified, accepted.
    assert kinds[0] == "sentence" and mine[0]["text"] == REFUSED
    removed = kinds.index("removed")
    assert mine[removed]["why"] == "the checker"
    again = [e for e in mine[removed:] if e["type"] in ("sentence", "unit")]
    assert again and (again[0].get("text") == REPLACEMENT or again[0].get("sentences") == [REPLACEMENT])
    assert kinds[-2:] == ["verified", "accepted"] or kinds[-1] == "accepted"
    assert "verified" in kinds[removed:]
    career = next(a for a in r.areas if a.name == "career")
    assert any(c.text == REPLACEMENT for c in career.claims) and not any(c.text == REFUSED for c in career.claims)


def test_the_areas_are_written_in_parallel_and_the_summary_last(streamed):
    r, events, live = streamed
    drafts = [b for b in Handler.requests if b["response_format"]["json_schema"]["name"] == "ReadingDraft"]
    assert all(b.get("stream") for b in drafts)                     # every writer call is streamed
    assert len(drafts) == 3                                         # career twice (one retry), marriage once
    assert all("This call writes this one area only" in b["messages"][0]["content"] or
               "This call writes this one area only" in json.dumps(b["messages"]) for b in drafts)
    summary_at = next(i for i, e in enumerate(events) if e.get("unit") == "summary")
    areas_done = [i for i, e in enumerate(events) if e["type"] == "area"]
    assert len(areas_done) == 2 and max(areas_done) < summary_at   # the summary after every area
    assert r.summary.source == "model" and r.summary.text == DRAFT["summary"]
    assert [a.name for a in r.areas] == ["career", "marriage"]
    assert r.usage["parallel_areas"] == 2 and r.usage["writer"]["calls"] == 4    # three area calls, one summary
    t = live.timeline
    assert 0 < t["first_sentence_s"] <= t["first_verified_s"] and t["first_area_s"] > 0


def test_every_shown_sentence_is_verified_or_removed_by_the_end(streamed):
    _, events, _ = streamed
    state = {}
    for e in events:
        if e["type"] in ("sentence", "unit"):
            state[e["unit"]] = "verifying"
        elif e["type"] in ("removed", "accepted"):
            state[e["unit"]] = e["type"]
    assert state and all(v in ("removed", "accepted") for v in state.values())


def test_the_log_numbers_events_and_the_api_serves_them(tmp_path, backends, chart):
    log = LiveLog()
    assert log.append("r1", {"type": "sentence"}) == 1 and log.append("r1", {"type": "done"}) == 2
    events, version, done = log.since("r1", 1)
    assert [e["seq"] for e in events] == [2] and version == 2 and done

    from fastapi.testclient import TestClient
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{tmp_path / 'live.db'}")
    body = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
            "node": "mean", "place": "Rewari, Haryana", "question": "How will my career go?", "as_of": "2026-10-21",
            "depth": "astrologer"}
    with TestClient(app) as c:
        rid = c.post("/readings", json=body).json()["id"]
        with c.stream("GET", f"/readings/{rid}/events") as s:          # server-sent events until done
            text = "".join(s.iter_text())
        assert "event: sentence" in text and "event: removed" in text and "event: done" in text
        ids = [int(x.split(": ")[1]) for x in text.splitlines() if x.startswith("id: ")]
        assert ids == sorted(ids) and ids[0] == 1
        polled = c.get(f"/readings/{rid}/live", params={"since": 0}).json()   # the fallback
        assert polled["done"] and polled["version"] == len(polled["events"]) == ids[-1]
        assert c.get(f"/readings/{rid}/live", params={"since": polled["version"]}).json()["events"] == []
        done = c.get(f"/readings/{rid}").json()
        assert done["status"] == "done"
        timeline = done["reading"]["usage"]["timeline"]
        assert timeline["instant_s"] <= timeline["first_sentence_s"] <= timeline["done_s"]
        bare = lambda t: t.split(" [")[0]                       # the page renders tags as footnotes
        assert bare(REFUSED) not in done["page"] and bare(REPLACEMENT) in done["page"]   # only what passed


def test_a_removed_text_seen_again_is_not_shown_and_a_replacement_is():
    # The race CI met (2026-10-26): the checker's verdict removed the unit before the loop validated the
    # same draft; the loop's text must not bring the refused sentence back.
    events = []
    live = Live(events.append)
    live.stream("claim:career:x", "Refused one [rule:x].", True)
    live.removed("claim:career:x", "the checker")
    live.text("claim:career:x", "Refused one [rule:x].")
    live.stream("claim:career:x", "Refused", False)
    assert [e["type"] for e in events] == ["sentence", "removed"]
    live.stream("claim:career:x", "The replacement [rule:x].", True)
    assert events[-1] == {"type": "sentence", "unit": "claim:career:x", "area": "career", "kind": "claim", "i": 0,
                          "text": "The replacement [rule:x].", "mark": None}
    # A text removed and then accepted on a later check (the same text sent again) is shown again, accepted.
    live.stream("summary", "Same text [vote:a].", True)
    live.removed("summary", "the checker")
    live.accepted("summary")
    assert [e["type"] for e in events[-3:]] == ["removed", "unit", "accepted"]
    assert events[-2]["sentences"] == ["Same text [vote:a]."]


def test_a_late_verdict_for_a_replaced_text_is_dropped():
    from concurrent.futures import Future
    from jyotish.narrate import CheckResult, Proposition
    events = []
    live = Live(events.append)
    live.stream("claim:career:x", "The replacement [rule:x].", True)
    late = Future()
    late.set_result((CheckResult(propositions=[Proposition(text="old", supported=False, evidence="no")]), None))
    live._verdict("claim:career:x", "The refused text [rule:x].", late)
    assert [e["type"] for e in events] == ["sentence"]              # not removed by the old text's verdict


def test_a_verdict_before_the_loop_validates_does_not_bring_the_sentence_back(chart, backends):
    # CI's order (2026-10-26): the stream is slow and the checker quick, so the refused claim's verdict
    # comes while the writer is still streaming the rest of the area, before the loop validates it.
    Handler.delay, Handler.check_delay = 0.01, 0.0
    try:
        events = []
        narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career", "marriage"], live=Live(events.append))
    finally:
        Handler.delay, Handler.check_delay = 0.0, None
    mine = [e for e in events if e.get("unit") == UNIT]
    removed = [e["type"] for e in mine].index("removed")
    shown_after = [e.get("text") or " ".join(e.get("sentences", [])) for e in mine[removed:] if e["type"] in ("sentence", "unit")]
    assert shown_after and all(t == REPLACEMENT for t in shown_after)
    assert mine[-1]["type"] == "accepted"


def test_a_tradition_sentence_is_never_marked_verified_and_a_judgement_is_marked_as_the_readings():
    # Review R3: at depth full a section may carry a [tradition:] sentence (never checked); the section's
    # acceptance must not turn it "verified", and a judgement's weighing is the reading's own.
    events = []
    live = Live(events.append)
    text = ("Saturn rules the 10th [fact:houses.lagna.10.lord]. The texts call it slow [tradition:BPHS 24]. "
            "I weigh the lord above the karaka [fact:houses.lagna.10.lord].")
    live.stream("analysis:career:assessment", text, True)
    marks = [e.get("mark") for e in events if e["type"] == "sentence"]
    assert marks == [None, "tradition", "judgement"]
    live.accepted("analysis:career:assessment")
    assert events[-1] == {"type": "accepted", "unit": "analysis:career:assessment", "verified": [0, 2]}


def test_a_live_recording_replays_offline_through_the_same_per_area_loop(chart, backends, tmp_path):
    # Review R5: a recording made in live mode keeps each unit's drafts and replays through the per-area
    # loop, the summary from its own drafts; the replay accepts what the live run accepted.
    from jyotish.narrate import recording_fixture
    from jyotish.service import BirthInput, make_reading
    birth = BirthInput(date="2001-03-12", time="10:10:25", tz="Asia/Kolkata", lat=REFERENCE_LAT, lon=REFERENCE_LON,
                       node="mean", place="Rewari, Haryana")
    recording = []
    live, _ = make_reading(birth, "How will my career go?", chart=chart, as_of=AS_OF.isoformat(), recording=recording)
    fixture = recording_fixture(recording)
    areas = [a.name for a in live.areas]
    assert fixture["live"] and set(fixture["scoped_drafts"]) == set(areas) | {"summary"}
    assert len(fixture["scoped_drafts"]["career"]) >= 2                  # the refused claim's retry at least
    assert fixture["scoped_drafts"]["summary"] == [{"summary": DRAFT["summary"]}]
    path = tmp_path / "live.recording.json"
    path.write_text(json.dumps({"question": "How will my career go?", **fixture, "calls": recording}, default=str))
    Handler.requests.clear()
    replayed, _ = make_reading(birth, "How will my career go?", chart=chart, as_of=AS_OF.isoformat(),
                               model_fixture=str(path))
    assert Handler.requests == []                                    # offline
    assert replayed.usage["parallel_areas"] == len(areas) and replayed.summary.text == live.summary.text
    texts = lambda r: {a.name: [c.text for c in a.claims] for a in r.areas}
    assert texts(replayed) == texts(live)


def test_curious_depth_streams_each_paragraph_and_holds_it(chart, backends):
    # Review R5: curious, the form's default depth, in live mode: each area's paragraph is a unit of its
    # own, shown, checked and accepted; the summary is the writer's own call.
    from jyotish.narrate import engine_line, findings
    votes = {n: [f for f in findings(chart, n, AS_OF)[0] if f["kind"] == "vote"][:2] for n in ("career", "marriage")}
    para = {n: " ".join(engine_line(f, n)[:-1] + f" [{f['allowed_tags'][0]}]." for f in votes[n]) for n in votes}

    def answer(name, body, users):
        if name in ("ReadingDraft",):
            area = next(n for n in Handler.claims if f"{n}.house" in users[0])
            return json.dumps({"summary": "", "areas": [{"name": area, "claims": Handler.claims[area][3:],
                                                         "paragraph": para[area]}]})
        return None
    Handler.answer = answer
    try:
        events = []
        r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career", "marriage"], depth="curious",
                    live=Live(events.append))
    finally:
        Handler.answer = None
    for n in ("career", "marriage"):
        unit = [e["type"] for e in events if e.get("unit") == f"paragraph:{n}"]
        assert unit[0] == "sentence" and unit[-1] == "accepted"
        assert next(a for a in r.areas if a.name == n).paragraph == para[n]


def test_depth_full_runs_the_clients_layer_per_area_and_the_summary_last(chart, backends, monkeypatch):
    # Review R5: depth full in live mode: each area's analysis, then its client's paragraph and when as
    # soon as it is accepted; the summary by the client's layer after every area; a tradition sentence
    # never marked verified (R3).
    import jyotish.narrate as n
    monkeypatch.setenv("JYOTISH_ALLOW_LOCAL_FULL", "1")
    monkeypatch.setattr(n, "default_client_drafter", n.client_drafter_for)       # the real client's layer
    monkeypatch.setenv("JYOTISH_CLIENT_BACKEND", f"openai:{backends}:stub-client")
    trad = "The texts associate the lord of the tenth with one's work [tradition:BPHS 24]."
    analysis = {"assessment": "The 10th house from the lagna holds the Sun and Mercury [fact:houses.lagna.10]. " + trad,
                "timing": "The running Vimshottari period is Jupiter-Mercury-Mercury [fact:vimshottari.current].",
                "not_said_client": ["Which employer comes next is not decided here [fact:houses.lagna.10]."],
                "not_said_astrologer": ["The learned score is not computed [fact:not_computed]."]}
    para = "In plain words, the 10th house from the rising sign holds the Sun and Mercury [fact:houses.lagna.10]."
    when = "In plain words, the running period is Jupiter-Mercury-Mercury [fact:vimshottari.current]."

    def answer(name, body, users):
        if name == "ClientDraft":
            names = [x for x in ("career", "marriage") if f'"{x}"' in users[0]]
            return json.dumps({"summary": para, "areas": [{"name": x, "paragraph": para, "when": when} for x in names]})
        if name == "ReadingDraft":
            area = next(x for x in ("career", "marriage") if f"{x}.house" in users[0])
            claims = [c for c in Handler.claims[area] if c["finding_id"].startswith("vote:")] if area != "career" else \
                [c for c in Handler.claims["career"] if c["finding_id"].startswith("vote:")]
            return json.dumps({"summary": "", "areas": [{"name": area, "claims": claims, "analysis": analysis}]})
        return None
    Handler.answer = answer
    try:
        events = []
        r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career", "marriage"], depth="full",
                    live=Live(events.append))
    finally:
        Handler.answer = None
    client_calls = [b for b in Handler.requests if b["response_format"]["json_schema"]["name"] == "ClientDraft"]
    assert len(client_calls) >= 3                                    # one per area, then the summary
    order = [e.get("unit") or e["type"] for e in events if e["type"] in ("accepted", "area")]
    assert order.index("summary") > max(i for i, x in enumerate(order) if x in ("paragraph:career", "paragraph:marriage"))
    assert r.summary.source == "model" and all(a.paragraph == para for a in r.areas)
    tradition = [e for e in events if e["type"] == "sentence" and e.get("mark") == "tradition"]
    assert tradition
    for e in tradition:
        accepted = [x for x in events if x["type"] == "accepted" and x["unit"] == e["unit"]]
        assert all(e["i"] not in x["verified"] for x in accepted)



def test_the_summary_call_is_sent_the_accepted_claims_not_the_whole_payload(streamed):
    # Review R6: the summary's call carried the reading's whole payload again (about 50,000 tokens).
    r, _, _ = streamed
    body = next(b for b in Handler.requests if b["response_format"]["json_schema"]["name"] == "SummaryDraft")
    sent = json.loads(body["messages"][1]["content"].split("\n\nThis call")[0])
    assert set(sent) == {"question", "depth", "areas"} and "findings" not in json.dumps(sent)
    assert [a["claims"] for a in sent["areas"]] == [[c.text for c in a.claims] for a in r.areas]


def test_jyotish_live_0_writes_the_reading_in_one_call(chart, backends, monkeypatch):
    from jyotish.narrate import live_enabled
    monkeypatch.setenv("JYOTISH_LIVE", "0")
    assert not live_enabled()
    Handler.requests.clear()
    r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career", "marriage"])
    drafts = [b for b in Handler.requests if b["response_format"]["json_schema"]["name"] in ("ReadingDraft", "SummaryDraft")]
    assert "parallel_areas" not in r.usage and drafts and all(
        b["response_format"]["json_schema"]["name"] == "ReadingDraft" for b in drafts)


def test_a_reading_takes_a_bounded_number_of_live_streams(tmp_path, backends, chart, monkeypatch):
    # Review R7: each stream is a coroutine (no worker thread held), and one reading takes at most
    # STREAMS_PER_READING at once.
    import jyotish.api as api
    from fastapi.testclient import TestClient
    monkeypatch.setattr(api, "STREAMS_PER_READING", 0)
    app = api.create_app(f"sqlite:///{tmp_path / 'cap.db'}")
    body = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": REFERENCE_LAT, "lon": REFERENCE_LON,
            "node": "mean", "place": "Rewari, Haryana", "question": "How will my career go?", "as_of": "2026-10-21",
            "depth": "astrologer"}
    with TestClient(app) as c:
        rid = c.post("/readings", json=body).json()["id"]
        r = c.get(f"/readings/{rid}/events")
        assert r.status_code == 429 and r.headers["retry-after"] == "5"
    import inspect
    assert inspect.iscoroutinefunction(next(rt.endpoint for rt in app.routes if getattr(rt, "path", "") == "/readings/{reading_id}/events"))


def test_the_live_view_bookkeeping_review_r8():
    from jyotish.live import SharedChecker
    from jyotish.narrate import CheckResult, Proposition
    events = []
    live = Live(events.append)
    # A stream that starts again withdraws what it showed; the same text may then be shown again.
    feed = live.draft_stream(lambda u: False)
    text = json.dumps({"summary": "One [vote:a]. Two [vote:b]."})
    feed(text[:30])
    feed(None)
    assert events[-1] == {"type": "removed", "unit": "summary", "why": "the stream started again"}
    feed(text)
    assert [e["type"] for e in events[-2:]] == ["sentence", "sentence"]
    # A unit the loop never decided on is swept after the attempt.
    live.stream("claim:career:unknown", "A claim for no finding [rule:x].", True)
    live.sweep(("claim:career:",))
    assert events[-1]["type"] == "removed" and events[-1]["unit"] == "claim:career:unknown"
    # A verdict matches its sentence exactly, not as a substring.
    live.stream("paragraph:career", "Ketu decides [vote:career.kp].", True)
    from concurrent.futures import Future
    late = Future()
    late.set_result((CheckResult(propositions=[Proposition(text="x", supported=False, evidence="no")]), None))
    live._verdict("paragraph:career", "As the KP vote shows, Ketu decides [vote:career.kp].", late)
    assert events[-1]["type"] == "sentence"
    # Checks are keyed per area; every run is kept, and one no loop consumed is reported as unused.
    calls = []
    shared = SharedChecker(lambda s, d: calls.append(s) or CheckResult(propositions=[]), 2)
    a, _ = shared.submit("Same sentence.", "{}", owner="career")
    b, _ = shared.submit("Same sentence.", "{}", owner="marriage")
    assert a is not b
    shared.check_many([("Same sentence.", "{}")], owners=["career"])
    b.result()
    assert len(shared.runs) == 2 and [r[3] for r in shared.unused()] == ["marriage"]
    shared.close()


def test_a_running_readings_log_is_never_evicted():
    log = LiveLog(keep=1)
    log.append("running", {"type": "sentence"})
    log.append("finished", {"type": "done"})
    log.append("another", {"type": "sentence"})
    assert log.known("running") and not log.known("finished")
    events, version, _ = log.since("running", 0)
    assert version == 1 and log.append("running", {"type": "verified"}) == 2
