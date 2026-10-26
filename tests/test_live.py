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

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Handler.requests.append(body)
        name = body["response_format"]["json_schema"]["name"]
        users = [m["content"] for m in body["messages"] if m["role"] == "user"]
        if name == "CheckResult":
            time.sleep(Handler.delay * 10)
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


def test_the_log_numbers_events_and_the_api_serves_them(tmp_path, backends):
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
