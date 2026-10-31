"""The OpenAI-compatible backend against a stub server (2026-10-25; docs/models.md): structured output by
json_schema, the JSON-mode fallback with our validation and one retry, a server that takes neither, a
server that refuses reasoning_effort, a streamed writer call, usage and cost recorded, the three roles on
three backends in one reading, and depth full refused on a local model. The stub is a small HTTP
server; the path of its base URL says how it behaves (/schema/v1, /jsonmode/v1, /none/v1, /noeffort/v1)."""

import json
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from jyotish.narrate import (CheckResult, ModelChecker, ModelDrafter, NarrationError, OpenAIBackend, Proposition,
                             ReadingDraft, narrate, CONFIG)
from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
from jyotish.uncertainty import assess

AS_OF = date(2026, 10, 21)


class Stub:
    """What the stub answers, per schema (found by the json_schema's name, or in JSON mode by the schema's
    title in the system prompt), and every request it received."""

    def __init__(self):
        self.requests: list[tuple[str, dict]] = []
        self.answers: dict[str, object] = {}
        self.bad_json_first = False                     # JSON mode: the first reply is not the schema
        self.seen: dict = {}                            # (mode, first user message) -> requests so far


STUB = Stub()


def _schema_name(body: dict) -> str | None:
    fmt = body.get("response_format") or {}
    if fmt.get("type") == "json_schema":
        return fmt["json_schema"]["name"]
    system = body["messages"][0]["content"]
    for name in ("CheckResult", "ReadingDraft", "ClientDraft"):
        if f'"title": "{name}"' in system:
            return name
    return None


def _answer(name: str, body: dict) -> str:
    a = STUB.answers.get(name)
    if callable(a):
        return a(body)
    if name == "CheckResult" and a is None:
        first = next(m["content"] for m in body["messages"] if m["role"] == "user")
        sentence = first.split("\n")[1]
        return json.dumps({"propositions": [{"text": sentence, "supported": True, "evidence": "stub"}]})
    return json.dumps(a)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, status, obj):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _drop(self):
        """Close the connection without an answer (the client sees the server disconnect)."""
        import socket
        self.close_connection = True
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def do_POST(self):
        mode = self.path.strip("/").split("/")[0]
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        STUB.requests.append((mode, body))
        first = next((m["content"] for m in body["messages"] if m["role"] == "user"), "")
        n = STUB.seen[(mode, first)] = STUB.seen.get((mode, first), 0) + 1
        if mode == "drop" and n == 1:
            return self._drop()                         # the first try of each request: a dropped connection
        if mode == "dead" or (mode == "deadone" and "DEAD" in first):
            return self._drop()                         # every try
        if mode == "toolarge":                          # Groq's free tier: a request above its tokens a minute
            return self._send(413, {"error": {"message": "Request too large for model `openai/gpt-oss-120b` on tokens "
                                              "per minute (TPM): Limit 8000, Requested 17459", "code": "rate_limit_exceeded"}})
        if mode == "nobalance":                         # DeepInfra's answer when the balance has run out
            return self._send(402, {"error": {"message": "You need positive balance to do inference."}})
        if mode == "ratelimit" and n == 1:
            data = json.dumps({"error": {"message": "rate limited"}}).encode()
            self.send_response(429)
            self.send_header("Retry-After", "1")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        fmt = (body.get("response_format") or {}).get("type")
        if mode == "none" and fmt:
            return self._send(400, {"error": {"message": f"response_format {fmt} is not supported by this server"}})
        if mode == "jsonmode" and fmt == "json_schema":
            return self._send(400, {"error": {"message": "unsupported response_format type json_schema"}})
        if mode == "noeffort" and "reasoning_effort" in body:
            return self._send(400, {"error": {"message": "unknown parameter: reasoning_effort"}})
        name = _schema_name(body)
        content = _answer(name, body)
        if mode == "jsonmode" and STUB.bad_json_first and not any(m["role"] == "assistant" for m in body["messages"]):
            content = '{"propositions": "not a list"}'
        usage = {"prompt_tokens": 1200, "completion_tokens": 300, "prompt_tokens_details": {"cached_tokens": 200}}
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            third = max(1, len(content) // 3)
            for piece in (content[:third], content[third:2 * third], content[2 * third:]):
                self.wfile.write(b"data: " + json.dumps({"id": "s1", "model": body["model"],
                                                         "choices": [{"delta": {"content": piece}}]}).encode() + b"\n\n")
            self.wfile.write(b"data: " + json.dumps({"id": "s1", "choices": [{"delta": {}, "finish_reason": "stop"}]}).encode()
                             + b"\n\n")
            self.wfile.write(b"data: " + json.dumps({"id": "s1", "choices": [], "usage": usage}).encode() + b"\n\n")
            self.wfile.write(b"data: [DONE]\n\n")
            return
        message = {"role": "assistant", "content": content}
        if mode == "reasoning":                          # a reasoning model: its thinking first, the answer in content
            message["reasoning_content"] = ('Let me think. {"propositions": [{"text": "a draft", "supported": false, '
                                            '"evidence": "thinking"}]} No, the data states it.')
        self._send(200, {"id": "r1", "model": body["model"], "usage": usage,
                         "choices": [{"message": message, "finish_reason": "stop"}]})


@pytest.fixture(scope="module")
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture(autouse=True)
def fresh():
    STUB.requests.clear()
    STUB.answers.clear()
    STUB.seen.clear()
    STUB.bad_json_first = False


def ask(backend, sentence="Mars is in its own sign [fact:planets.Mars.dignity]."):
    return backend.structured(system="Check it.", messages=[{"role": "user", "content": f"Sentence:\n{sentence}\n\nData:\n{{}}"}],
                              schema=CheckResult, kind="checker", effort="high", thinking=None, max_tokens=4000)


def test_structured_output_by_json_schema_with_usage(server):
    b = OpenAIBackend(f"{server}/schema/v1", "stub-model", api_key="k")
    done = ask(b)
    assert done.parsed.propositions[0].supported and done.stop_reason == "end_turn"
    body = STUB.requests[0][1]
    assert body["response_format"]["type"] == "json_schema" and body["response_format"]["json_schema"]["name"] == "CheckResult"
    assert body["reasoning_effort"] == "high" and body["model"] == "stub-model"
    assert done.meta["usage"] == {"input_tokens": 1000, "output_tokens": 300, "cache_read_input_tokens": 200,
                                  "cache_creation_input_tokens": 0}
    assert done.meta["structured"] == "json_schema" and done.meta["backend"]["host"] == server.split("//")[1]
    assert b.describe()["structured"] == "json_schema" and b.describe()["local"] is True


def test_json_mode_fallback_validates_retries_once_and_keeps_the_mode(server):
    b = OpenAIBackend(f"{server}/jsonmode/v1", "stub-model")
    STUB.bad_json_first = True
    done = ask(b)
    assert done.parsed is not None and done.meta["structured"] == "json_object"
    kinds = [(r[1]["response_format"]["type"], any(m["role"] == "assistant" for m in r[1]["messages"])) for r in STUB.requests]
    assert kinds == [("json_schema", False), ("json_object", False), ("json_object", True)]   # refused, invalid, retried
    assert '"title": "CheckResult"' in STUB.requests[1][1]["messages"][0]["content"]          # the schema in the prompt
    assert "did not match the JSON schema" in STUB.requests[2][1]["messages"][-1]["content"]
    STUB.requests.clear()
    STUB.bad_json_first = False
    ask(b)
    assert [r[1]["response_format"]["type"] for r in STUB.requests] == ["json_object"]       # found once, kept


def test_a_server_with_neither_mode_is_a_clear_error_naming_it(server):
    b = OpenAIBackend(f"{server}/none/v1", "stub-model")
    with pytest.raises(NarrationError, match=r"127\.0\.0\.1:\d+ supports neither response_format json_schema nor "
                                             r"json_object.*stub-model"):
        ask(b)


def test_a_server_that_refuses_reasoning_effort_is_asked_again_without_it(server):
    b = OpenAIBackend(f"{server}/noeffort/v1", "stub-model")
    done = ask(b)
    assert done.parsed is not None and done.meta["effort_sent"] is None and done.meta["effort"] == "high"
    assert ["reasoning_effort" in r[1] for r in STUB.requests] == [True, False]


def test_a_long_writer_call_is_streamed_and_gathered(server):
    STUB.answers["ReadingDraft"] = {"summary": "", "areas": []}
    b = OpenAIBackend(f"{server}/schema/v1", "stub-writer")
    done = b.structured(system="Write.", messages=[{"role": "user", "content": "payload"}], schema=ReadingDraft,
                        kind="writer", effort="xhigh", thinking="adaptive", max_tokens=128000)
    body = STUB.requests[0][1]
    assert body["stream"] is True and body["stream_options"] == {"include_usage": True} and body["reasoning_effort"] == "high"
    assert done.parsed == ReadingDraft(summary="", areas=[]) and done.meta["usage"]["output_tokens"] == 300
    assert done.meta["effort_sent"] == "high"                  # xhigh sent as high, both recorded


def test_the_checker_runs_concurrently_on_the_open_backend(server):
    from dataclasses import replace
    c = ModelChecker(OpenAIBackend(f"{server}/schema/v1", "stub-checker"), replace(CONFIG, checker_concurrency=4))
    items = [(f"Sentence {i} [fact:planets.Mars.dignity].", "{}") for i in range(6)]
    out = c.check_many(items)
    assert [r.propositions[0].text for r, _ in out] == [s for s, _ in items]
    assert all(m["backend"]["model"] == "stub-checker" for _, m in out)


# --- in a reading ---------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chart():
    return assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)


def test_three_roles_on_three_backends_recorded_and_priced(server, chart, monkeypatch):
    import importlib.util
    from pathlib import Path
    from jyotish.costs import reading_cost
    # The client's-layer test's draft and client's view, loaded from its file (the tests are not a package).
    spec = importlib.util.spec_from_file_location("client_layer_cases", Path(__file__).with_name("test_client_layer.py"))
    cases = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cases)
    PARAGRAPH, SUMMARY, WHEN, draft = cases.PARAGRAPH, cases.SUMMARY, cases.WHEN, cases.draft
    monkeypatch.setenv("JYOTISH_ALLOW_LOCAL_FULL", "1")      # the stub is local; depth full is allowed for this test
    STUB.answers["ReadingDraft"] = draft()
    STUB.answers["ClientDraft"] = {"summary": SUMMARY, "areas": [{"name": "career", "paragraph": PARAGRAPH, "when": WHEN}]}
    import jyotish.narrate as n
    monkeypatch.setattr(n, "default_client_drafter", n.client_drafter_for)   # the real client's layer, not the suite's stub
    r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career"], depth="full",
                writer_backend=f"openai:{server}/schema/v1:stub-writer",
                checker_backend=f"openai:{server}/jsonmode/v1:stub-checker",
                client_backend=f"openai:{server}/noeffort/v1:stub-client")
    assert (r.writer["model"], r.checker["model"], r.client["model"]) == ("stub-writer", "stub-checker", "stub-client")
    assert r.writer["backend"]["base_url"].endswith("/schema/v1") and r.writer["backend"]["structured"] == "json_schema"
    assert r.checker["backend"]["base_url"].endswith("/jsonmode/v1") and r.checker["backend"]["structured"] == "json_object"
    assert r.client["backend"]["base_url"].endswith("/noeffort/v1")
    assert r.areas[0].paragraph == PARAGRAPH and r.areas[0].when == WHEN and r.summary.text == SUMMARY
    modes = {m for m, _ in STUB.requests}
    assert modes == {"schema", "jsonmode", "noeffort"}
    assert any(b.get("stream") for m, b in STUB.requests if m == "schema")          # the writer at depth full streams
    u = r.usage
    assert u["writer"]["calls"] == 1 and u["writer"]["input_tokens"] == 1000 and u["client"]["calls"] == 1
    assert u["checker"]["calls"] >= 5 and u["checker"]["output_tokens"] == 300 * u["checker"]["calls"]
    v = reading_cost(r.model_dump())
    assert v["cost_usd"] == 0.0 and v["client_calls"] == 1                          # a local server charges nothing
    assert v["backends"]["checker"]["host"] == server.split("//")[1]


def test_depth_full_on_a_local_model_is_refused_before_any_request(server, chart, monkeypatch):
    monkeypatch.delenv("JYOTISH_ALLOW_LOCAL_FULL", raising=False)
    with pytest.raises(NarrationError, match=r"about [\d,]+ tokens, to stub-writer on 127\.0\.0\.1:\d+, a local model.*"
                                             r"JYOTISH_ALLOW_LOCAL_FULL=1"):
        narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career"], depth="full",
                writer_backend=f"openai:{server}/schema/v1:stub-writer",
                checker_backend=f"openai:{server}/schema/v1:stub-checker")
    assert STUB.requests == []
    # Astrologer depth on the same local model is not refused.
    STUB.answers["ReadingDraft"] = {"summary": "Career [vote:career.house].", "areas": []}
    r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career"], depth="astrologer",
                writer_backend=f"openai:{server}/schema/v1:stub-writer", checker_backend=f"openai:{server}/schema/v1:stub-checker")
    assert r.writer["model"] == "stub-writer" and STUB.requests


# --- retries, concurrency, reasoning models (2026-10-25: the DeepInfra benchmark's ReadError) ------------

@pytest.fixture
def retries(monkeypatch):
    """Every retry the backends log, as (event, fields)."""
    import jyotish.logs
    seen = []
    monkeypatch.setattr(jyotish.logs, "event", lambda name, level=None, **f: seen.append((name, f)))
    return seen


def test_a_dropped_connection_is_retried_then_answered_and_logged(server, retries):
    b = OpenAIBackend(f"{server}/drop/v1", "stub-model", api_key="sk-must-not-appear", retry_base=0.01)
    done = ask(b)
    assert done.parsed is not None and len(STUB.requests) == 2
    assert [(n, f["attempt"], f["reason"], f["provider"], f["model"]) for n, f in retries] == \
        [("backend.retry", 1, "RemoteProtocolError", "openai-compatible", "stub-model")]
    assert "sk-must-not-appear" not in str(retries)


def test_a_429_waits_what_retry_after_asks(server, retries):
    import time
    b = OpenAIBackend(f"{server}/ratelimit/v1", "stub-model", retry_base=0.01)
    t = time.perf_counter()
    done = ask(b)
    assert done.parsed is not None and time.perf_counter() - t >= 1.0     # Retry-After: 1, not the 0.01 s backoff
    assert retries[0][1]["reason"] == "HTTP 429" and retries[0][1]["wait_s"] == 1.0


def test_a_request_that_fails_every_retry_is_an_error_naming_the_server(server, retries):
    b = OpenAIBackend(f"{server}/dead/v1", "stub-model", retry_base=0.01)
    with pytest.raises(NarrationError, match=r"127\.0\.0\.1:\d+ did not answer after 5 attempts \(model stub-model\)"):
        ask(b)
    assert len(STUB.requests) == 5 and [f["attempt"] for _, f in retries] == [1, 2, 3, 4]


@pytest.mark.parametrize("concurrency", ["1", "4"])
def test_a_sentence_that_fails_every_retry_fails_alone_as_unchecked(server, retries, monkeypatch, concurrency):
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", concurrency)
    c = ModelChecker(OpenAIBackend(f"{server}/deadone/v1", "stub-checker", retry_base=0.01))
    assert c.concurrency == int(concurrency)
    items = [("Sentence one [fact:a].", "{}"), ("Sentence DEAD [fact:b].", "{}"), ("Sentence three [fact:c].", "{}")]
    out = c.check_many(items)
    assert [r.propositions[0].supported for r, _ in out] == [True, False, True]       # the batch carries on
    bad, meta = out[1]
    assert meta["unchecked"] is True and bad.propositions[0].text == "(unchecked)"
    assert "did not answer after 5 attempts" in bad.propositions[0].evidence and meta["backend"]["model"] == "stub-checker"


def test_a_reading_counts_a_sentence_its_checker_could_not_reach(server, chart, monkeypatch):
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "1")
    STUB.answers["ReadingDraft"] = {"summary": "The house vote is for career [vote:career.house].", "areas": []}
    checker = ModelChecker(OpenAIBackend(f"{server}/dead/v1", "stub-checker", retry_base=0.001))
    r = narrate(chart, "How will my career go?", as_of=AS_OF, areas=["career"], depth="astrologer",
                writer_backend=f"openai:{server}/schema/v1:stub-writer", checker=checker)
    assert r.unchecked_sentences >= 1 and r.summary.source == "engine"          # failed, never shown as checked


def test_a_reasoning_models_answer_is_parsed_from_content_with_room_to_think(server):
    from jyotish.narrate import OPENAI_CHECKER_MAX_TOKENS
    c = ModelChecker(OpenAIBackend(f"{server}/reasoning/v1", "glm-like"))
    result = c("Mars is in its own sign [fact:planets.Mars.dignity].", "{}")
    assert result.propositions[0].supported is True and result.propositions[0].evidence == "stub"   # not the draft
    assert c.last_meta["thinking"].startswith("Let me think.")
    assert STUB.requests[0][1]["max_tokens"] == OPENAI_CHECKER_MAX_TOKENS >= 16000


def test_concurrency_defaults_by_provider_and_the_environment_overrides(monkeypatch):
    from jyotish.narrate import AnthropicBackend, checker_concurrency
    monkeypatch.delenv("JYOTISH_CHECKER_CONCURRENCY", raising=False)
    assert checker_concurrency(OpenAIBackend("https://api.deepinfra.com/v1/openai", "zai-org/GLM-4.7")) == 8
    assert checker_concurrency(OpenAIBackend("http://localhost:11434/v1", "gpt-oss:20b")) == 1
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-not-a-key")
    assert checker_concurrency(AnthropicBackend("claude-opus-5-5")) == CONFIG.checker_concurrency == 16
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "2")
    assert checker_concurrency(OpenAIBackend("https://api.deepinfra.com/v1/openai", "zai-org/GLM-4.7")) == 2


def test_batches_on_a_keep_alive_server_each_get_their_own_client(monkeypatch):
    """The fault found reproducing: one async client kept across batches, each batch a new event loop,
    so a keep-alive connection from a closed loop failed the next batch ("Event loop is closed")."""
    class KeepAlive(Handler):
        protocol_version = "HTTP/1.1"
    srv = ThreadingHTTPServer(("127.0.0.1", 0), KeepAlive)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "4")
        c = ModelChecker(OpenAIBackend(f"http://127.0.0.1:{srv.server_address[1]}/schema/v1", "m"))
        items = [(f"Sentence {i} [fact:x].", "{}") for i in range(8)]
        for _ in range(3):
            assert all(r.propositions[0].supported for r, _ in c.check_many(items))
        assert c.backend._async_client is None                                  # closed at the end of each batch
    finally:
        srv.shutdown()


def test_the_benchmark_writes_as_it_goes_and_resumes(server, tmp_path, monkeypatch):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import checker_bench as cb
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "1")
    rows = [r for r in cb.load() if not cb.run_validator([r])[r["id"]][0]][:6]
    part = tmp_path / "part.jsonl"
    spec = f"openai:{server}/schema/v1:stub-checker"
    out, usage = cb.run_live(rows, backend=spec, partial=part)
    assert len(part.read_text().splitlines()) == 6 and usage["calls"] == 6 and not usage["unchecked"]
    STUB.requests.clear()
    lines = part.read_text().splitlines()
    part.write_text("\n".join(lines[:4]) + "\n")                              # interrupted after four rows
    out2, usage2 = cb.run_live(rows, backend=spec, partial=part, resume=True)
    assert usage2["resumed"] == 4 and len(STUB.requests) == 2 and out2 == out  # only the last two asked again


def test_no_balance_stops_the_run_at_once_instead_of_failing_every_sentence(server, retries, monkeypatch):
    from jyotish.narrate import BackendFatal
    monkeypatch.setenv("JYOTISH_CHECKER_CONCURRENCY", "4")
    c = ModelChecker(OpenAIBackend(f"{server}/nobalance/v1", "stub-checker", retry_base=0.01))
    with pytest.raises(BackendFatal, match=r"cannot serve stub-checker: the account has no balance \(HTTP 402"):
        c.check_many([(f"Sentence {i} [fact:x].", "{}") for i in range(6)])
    assert retries == [] and len(STUB.requests) <= 6                   # not retried; no sentence marked unchecked
    with pytest.raises(BackendFatal):
        c("One sentence [fact:x].", "{}")


def test_checker_effort_none_switches_reasoning_off_and_is_an_openai_setting_only(server, monkeypatch):
    from dataclasses import replace
    from jyotish.narrate import AnthropicBackend, checker_effort
    c = ModelChecker(OpenAIBackend(f"{server}/schema/v1", "stub-checker"), replace(CONFIG, checker_effort="none"))
    c("Mars is in its own sign [fact:planets.Mars.dignity].", "{}")
    assert STUB.requests[0][1]["reasoning_effort"] == "none" and c.last_meta["effort_sent"] == "none"
    monkeypatch.setenv("JYOTISH_CHECKER_EFFORT", "low")                     # the environment's setting wins
    assert checker_effort(OpenAIBackend(f"{server}/schema/v1", "m")) == "low"
    monkeypatch.setenv("JYOTISH_CHECKER_EFFORT", "none")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-not-a-key")
    with pytest.raises(ValueError, match="'none' \\(reasoning off\\) is an OpenAI-compatible server's setting"):
        checker_effort(AnthropicBackend("claude-opus-5-5"))
    monkeypatch.setenv("JYOTISH_CHECKER_EFFORT", "lowest")
    with pytest.raises(ValueError, match="must be one of none, low, medium, high, xhigh, max"):
        checker_effort(OpenAIBackend(f"{server}/schema/v1", "m"))


def test_each_fast_provider_is_sent_its_own_key_and_never_another(monkeypatch):
    from jyotish.narrate import make_backend
    monkeypatch.setenv("JYOTISH_OPENAI_KEY", "deepinfra-key")
    monkeypatch.setenv("JYOTISH_CEREBRAS_KEY", "cerebras-key")
    monkeypatch.setenv("JYOTISH_CHECKER_KEY", "")
    monkeypatch.setenv("JYOTISH_WRITER_KEY", "")
    monkeypatch.delenv("JYOTISH_GROQ_KEY", raising=False)
    assert make_backend("openai:https://api.cerebras.ai/v1:gpt-oss-120b", "writer").api_key == "cerebras-key"
    assert make_backend("openai:https://api.groq.com/openai/v1:openai/gpt-oss-120b", "writer").api_key is None
    assert make_backend("openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7", "checker").api_key == "deepinfra-key"
    # Review R9: a role key is never sent to a provider with a key of its own, and a port does not hide the host.
    monkeypatch.setenv("JYOTISH_WRITER_KEY", "deepinfra-key")
    assert make_backend("openai:https://api.cerebras.ai/v1:gpt-oss-120b", "writer").api_key == "cerebras-key"
    assert make_backend("openai:https://api.groq.com:443/openai/v1:openai/gpt-oss-120b", "writer").api_key is None
    assert make_backend("openai:https://api.cerebras.ai:443/v1:gpt-oss-120b", "writer").api_key == "cerebras-key"
    assert make_backend("openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b", "writer").api_key == "deepinfra-key"


def test_a_role_s_temperature_is_sent_and_recorded(server, monkeypatch):
    from jyotish.narrate import make_backend
    monkeypatch.setenv("JYOTISH_CHECKER_TEMPERATURE", "0")
    b = make_backend(f"openai:{server}/schema/v1:stub-checker", "checker")
    done = ask(b)
    assert STUB.requests[-1][1]["temperature"] == 0.0 and done.meta["backend"]["temperature"] == 0.0
    monkeypatch.setenv("JYOTISH_CHECKER_TEMPERATURE", "")
    assert "temperature" not in (ask(make_backend(f"openai:{server}/schema/v1:stub-checker", "checker")) and STUB.requests[-1][1])


def test_groq_is_never_asked_to_stream_structured_output():
    from jyotish.narrate import OpenAIBackend, ReadingDraft
    groq = OpenAIBackend("https://api.groq.com/openai/v1", "openai/gpt-oss-120b")
    body = groq._body("s", [], ReadingDraft, "high", 64000, "json_schema", True)
    assert "stream" not in body and body["response_format"]["type"] == "json_schema"
    assert OpenAIBackend("https://api.cerebras.ai/v1", "gpt-oss-120b")._body("s", [], ReadingDraft, "high", 64000,
                                                                             "json_schema", True)["stream"] is True


def test_a_streamed_reply_retried_in_json_mode_starts_its_text_again(server):
    # Review R5: on a JSON-mode retry the streamed text restarts, and on_text is told so (None).
    STUB.bad_json_first = True
    seen = []
    b = OpenAIBackend(f"{server}/jsonmode/v1", "stub-model", api_key="k")
    done = b.structured(system="Check it.", messages=[{"role": "user", "content": "Sentence:\nMars [fact:x].\n\nData:\n{}"}],
                        schema=CheckResult, kind="checker", effort="high", thinking=None, max_tokens=4000,
                        on_text=seen.append)
    assert done.parsed is not None and None in seen
    after = "".join(x for x in seen[seen.index(None) + 1:] if x)
    assert json.loads(after)["propositions"][0]["supported"] is True


def test_the_anthropic_stream_hands_each_text_delta_to_on_text():
    # Review R5: the Anthropic path of on_text, with a stand-in client.
    from types import SimpleNamespace as NS
    from jyotish.narrate import AnthropicBackend
    final = NS(content=[], stop_reason="end_turn", usage=None, model="claude-opus-5-5", _request_id="r",
               parsed_output=CheckResult(propositions=[]))
    events = [NS(type="content_block_delta", delta=NS(type="text_delta", text=t)) for t in ('{"propo', 'sitions": []}')]
    events.insert(1, NS(type="content_block_delta", delta=NS(type="thinking_delta", thinking="hmm")))

    class Stream:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def __iter__(self): return iter(events)
        def get_final_message(self): return final
    client = NS(beta=NS(messages=NS(stream=lambda **k: Stream(), parse=None)))
    seen = []
    done = AnthropicBackend("claude-opus-5-5", client=client).structured(
        system="s", messages=[{"role": "user", "content": "x"}], schema=CheckResult, kind="checker", effort="high",
        thinking=None, max_tokens=4000, on_text=seen.append)
    assert seen == ['{"propo', 'sitions": []}'] and done.parsed == CheckResult(propositions=[])


def test_the_fast_providers_are_priced_from_their_own_pages():
    from jyotish.costs import PRICE_SOURCES, cost, price
    assert price("gpt-oss-120b", "api.cerebras.ai") == (0.35, 0.75, 0.35, 0.0)
    assert price("openai/gpt-oss-120b", "api.groq.com") == (0.15, 0.60, 0.075, 0.0)
    assert PRICE_SOURCES["api.cerebras.ai"]["read_on"] == PRICE_SOURCES["api.groq.com"]["read_on"] == "2026-10-26"
    t = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    assert cost("gpt-oss-120b", t, "api.cerebras.ai") == pytest.approx(1.10)


def test_a_request_above_the_accounts_limit_stops_at_once(server, retries):
    # 2026-10-31: Groq's free tier answers 413 to every writer call (8,000 tokens a minute against 17,459 asked);
    # it is fatal, not retried and not drafted three times.
    from jyotish.narrate import BackendFatal
    b = OpenAIBackend(f"{server}/toolarge/v1", "openai/gpt-oss-120b", api_key="k", retry_base=0.01)
    with pytest.raises(BackendFatal, match=r"larger than the account's limit allows \(HTTP 413.*Limit 8000"):
        ask(b)
    assert retries == [] and len(STUB.requests) == 1
