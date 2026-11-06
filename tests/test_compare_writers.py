"""The writer bake-off's tooling (2026-11-02): scripts/live_timing.py --turn with --writer, --writer-model and --out,
and scripts/compare_writers.py's estimate, its stop over budget and its report. No model is called: the turns are
answered offline (conversation.OfflineTurnWriter, a stub checker) and DeepInfra's listing is stubbed."""

import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import pytest

from jyotish.conversation import OfflineTurnWriter
from jyotish.narrate import CheckResult, Proposition

ROOT = Path(__file__).resolve().parents[1]


def passes(sentence, data):
    return CheckResult(propositions=[Proposition(text=sentence, supported=True, evidence="stub")])


def load(name):
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def offline(monkeypatch):
    """answer_turn answered offline, recording the config each turn was given; no .env read."""
    import jyotish.conversation as conv
    import jyotish.envfile
    seen = []
    real = conv.answer_turn

    def answer(*a, **k):
        seen.append(k.get("config"))
        return real(*a, **(k | {"drafter": OfflineTurnWriter(), "checker": passes}))
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(conv, "answer_turn", answer)
    return seen


def test_live_timing_turn_takes_a_writer_model_and_an_out_directory(offline, tmp_path, monkeypatch, capsys):
    lt = load("live_timing")
    monkeypatch.setattr(lt, "ROWS", tmp_path / "rows.jsonl")
    assert lt.main(["--label", "haiku", "--turn", "--writer", "anthropic", "--writer-model", "claude-haiku-5-5",
                    "--out", str(tmp_path / "out"), "--as-of", "2026-11-02"]) == 0
    assert {c.model for c in offline} == {"claude-haiku-5-5"}
    files = sorted(p.name for p in (tmp_path / "out").glob("*.turn.json"))
    assert files == [f"haiku-{n}.turn.json" for n in range(1, 8)]
    rows = [json.loads(x) for x in (tmp_path / "rows.jsonl").read_text().splitlines()]
    assert [r["question"] for r in rows] == list(lt.SEVEN_TURNS)


def test_the_estimate_prices_every_writer_and_stops_over_budget(monkeypatch, capsys):
    cw = load("compare_writers")
    rows, total = cw.estimate(cw.WRITERS, [12000] * 6)
    assert [r["label"] for r in rows] == [w[0] for w in cw.WRITERS]
    assert all(r["usd"] > 0 for r in rows) and abs(total - sum(r["usd"] for r in rows)) < 1e-9
    # Sonnet is the dearest writer here, gpt-oss the cheapest.
    by = {r["label"]: r["usd"] for r in rows}
    assert max(by, key=by.get) == "claude-sonnet-5-5" and min(by, key=by.get) == "gpt-oss-120b"
    import jyotish.envfile
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(cw, "served", lambda: {w[1].rsplit(":", 1)[1] for w in cw.WRITERS if w[1] != "anthropic"})
    monkeypatch.setattr(cw, "measure_calls", lambda: [12000] * 6)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-key")
    ran = []
    monkeypatch.setattr(cw, "run", lambda writers: ran.append(writers) or {})
    assert cw.main(["--budget", "0.001"]) == 2 and not ran                     # over budget: nothing runs
    assert "over the budget" in capsys.readouterr().out


def test_a_writer_not_served_is_skipped_and_said_so(monkeypatch, capsys):
    cw = load("compare_writers")
    import jyotish.envfile
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(cw, "served", lambda: {"openai/gpt-oss-120b"})
    monkeypatch.setattr(cw, "measure_calls", lambda: [12000] * 6)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-key")
    assert cw.main(["--estimate"]) == 0
    out = capsys.readouterr().out
    assert "skipped kimi-k2.6: not served by DeepInfra" in out and "not-a-key" not in out


def test_the_anthropic_writers_stop_the_run_without_their_key(monkeypatch):
    cw = load("compare_writers")
    import jyotish.envfile
    monkeypatch.setattr(jyotish.envfile, "load", lambda path: [])
    monkeypatch.setattr(cw, "served", lambda: set())
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY"):
        cw.main(["--estimate"])


def test_the_report_has_the_tables_the_affordability_and_every_turns_text(offline, tmp_path, monkeypatch):
    lt, cw = load("live_timing"), load("compare_writers")
    monkeypatch.setattr(lt, "ROWS", tmp_path / "rows.jsonl")
    monkeypatch.setattr(cw, "OUT", tmp_path / "out")
    for label in ("gpt-oss-120b", "claude-haiku-5-5"):
        lt.main(["--label", label, "--turn", "--out", str(tmp_path / "out"), "--as-of", "2026-11-02"])
    writers = [w for w in cw.WRITERS if w[0] in ("gpt-oss-120b", "claude-haiku-5-5")]
    for d in (tmp_path / "out").glob("*.turn.json"):          # offline turns carry no usage: give them a price
        doc = json.loads(d.read_text())
        if doc.get("source") != "fixed":
            doc["writer"] = {"model": "openai/gpt-oss-120b", "backend": {"host": "api.deepinfra.com"}}
            doc["usage"] = {"writer": {"input_tokens": 3000, "output_tokens": 2000},
                            "checker": {"input_tokens": 0, "output_tokens": 0}}
            d.write_text(json.dumps(doc))
    text = cw.report(writers, {"kimi-k2.6": "not served by DeepInfra"}, {}, [], 88.0)
    assert "Not run: kimi-k2.6 (not served by DeepInfra)." in text
    assert "| gpt-oss-120b |" in text and "## Affordable at INR 149 a ten-turn session" in text
    assert re.search(r"\| gpt-oss-120b \| [\d.]+ \| [\d.]+ \| [\d.]+% \| yes \|", text)
    for n in range(1, 8):
        assert f"### Turn {n}:" in text
    assert "(the fixed reply)" in text and "A chart gives no amount and makes no promise" in text


def test_haiku_is_sent_no_refusal_fallback_and_sonnet_is():
    from jyotish.narrate import AnthropicBackend, CONFIG

    class Client:
        pass
    haiku = AnthropicBackend("claude-haiku-5-5", CONFIG, client=Client())._kwargs("s", [], {}, "medium", "adaptive", 100)
    sonnet = AnthropicBackend("claude-sonnet-5-5", CONFIG, client=Client())._kwargs("s", [], {}, "medium", "adaptive", 100)
    assert "fallbacks" not in haiku and not haiku["betas"]
    assert sonnet["fallbacks"] == CONFIG.fallbacks and list(sonnet["betas"]) == list(CONFIG.betas)


def test_a_failure_for_want_of_credit_is_said_as_such_and_a_rerun_drops_it(tmp_path, monkeypatch):
    cw = load("compare_writers")
    assert cw.why('BackendFatal: x (HTTP 402: {"error":{"message":"You need positive balance"}})') == \
        "DeepInfra refused it with HTTP 402: the account has no balance"
    assert cw.why("BadRequestError: 400 Your credit balance is too low to access the Anthropic API") == \
        "Anthropic refused it with HTTP 400: the account's credit balance is too low"
    monkeypatch.setattr(cw, "OUT", tmp_path)
    (tmp_path / "failed.json").write_text(json.dumps({"kimi-k2.6": "402 balance", "glm-5.3": "402 balance"}))
    import live_timing
    monkeypatch.setattr(live_timing, "main", lambda argv: 0)
    assert cw.run([w for w in cw.WRITERS if w[0] == "kimi-k2.6"]) == {"glm-5.3": "402 balance"}
