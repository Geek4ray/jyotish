"""The narration's model as a backend (2026-10-25; docs/models.md): the backend spec, the pricing per
role and host, and what /health says. The stub OpenAI-compatible server's tests are below them."""

import pytest

from jyotish.costs import OPEN_PRICES, PRICES, cost, is_local, price, reading_cost
from jyotish.narrate import CONFIG, AnthropicBackend, OpenAIBackend, backend_spec, backends_status, make_backend


@pytest.mark.parametrize("spec,url,model", [
    ("openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b", "https://api.deepinfra.com/v1/openai",
     "openai/gpt-oss-120b"),
    ("openai:https://openrouter.ai/api/v1:z-ai/glm-4.7", "https://openrouter.ai/api/v1", "z-ai/glm-4.7"),
    ("openai:http://localhost:11434/v1:gpt-oss:20b", "http://localhost:11434/v1", "gpt-oss:20b"),   # a port, a tag
    ("openai:http://127.0.0.1:11434/v1:qwen3.6:27b", "http://127.0.0.1:11434/v1", "qwen3.6:27b"),
])
def test_an_openai_spec_names_its_base_url_with_its_path_and_its_model(spec, url, model):
    b = make_backend(spec, "checker")
    assert isinstance(b, OpenAIBackend) and (b.base_url, b.model) == (url, model)


def test_anthropic_is_the_default_and_a_bad_spec_says_what_a_good_one_looks_like(monkeypatch):
    for role in ("writer", "checker", "client"):
        monkeypatch.delenv(f"JYOTISH_{role.upper()}_BACKEND", raising=False)
        assert backend_spec(role) == "anthropic"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-not-a-key")
    b = make_backend(None, "checker")
    assert isinstance(b, AnthropicBackend) and b.model == CONFIG.checker_model
    with pytest.raises(ValueError, match="openai:<base url with its path>:<model>"):
        make_backend("openai:localhost:gpt-oss", "writer")


def test_the_key_is_the_roles_own_else_the_shared_one(monkeypatch):
    monkeypatch.setenv("JYOTISH_OPENAI_KEY", "shared")
    monkeypatch.setenv("JYOTISH_CHECKER_KEY", "checker-only")
    assert make_backend("openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7", "checker").api_key == "checker-only"
    assert make_backend("openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b", "writer").api_key == "shared"


def test_openrouter_is_sent_its_data_policy_and_others_are_not():
    o = make_backend("openai:https://openrouter.ai/api/v1:z-ai/glm-4.7", "checker")
    assert o.extra == {"provider": {"data_collection": "deny", "zdr": True, "require_parameters": True}}
    assert make_backend("openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7", "checker").extra == {}


def test_prices_by_host_and_model_local_free_and_unknown_none():
    t = {"input_tokens": 1_000_000, "output_tokens": 1_000_000, "cache_read_input_tokens": 1_000_000}
    assert cost("claude-opus-5-5", t) == pytest.approx(4 + 20 + 0.2)
    assert cost("openai/gpt-oss-120b", t, "api.deepinfra.com") == pytest.approx(0.037 + 0.17 + 0.037)
    assert cost("zai-org/GLM-4.7", t, "api.deepinfra.com") == pytest.approx(0.40 + 1.75 + 0.08)
    assert cost("gpt-oss:20b", t, "localhost:11434") == 0.0 and is_local("[::1]:11434") and not is_local("openrouter.ai")
    assert price("some/unlisted-model", "api.deepinfra.com") is None and cost("some/unlisted-model", t, "x.y") is None
    assert all(len(p) == 4 for p in list(PRICES.values()) + list(OPEN_PRICES.values()))


def test_a_reading_is_priced_role_by_role_and_unpriced_when_one_role_is():
    doc = {"depth": "full", "writer": {"model": "openai/gpt-oss-120b", "backend": {"host": "api.deepinfra.com"}},
           "checker": {"model": "claude-opus-5-5", "backend": {"host": "api.anthropic.com"}},
           "client": {"model": "gpt-oss:20b", "backend": {"host": "localhost:11434"}},
           "usage": {"writer": {"calls": 2, "input_tokens": 100_000, "output_tokens": 20_000},
                     "checker": {"calls": 10, "input_tokens": 50_000, "output_tokens": 10_000},
                     "client": {"calls": 1, "input_tokens": 5_000, "output_tokens": 1_000}}}
    v = reading_cost(doc)
    want = (100_000 * 0.037 + 20_000 * 0.17) / 1e6 + (50_000 * 4 + 10_000 * 20) / 1e6 + 0.0
    assert v["cost_usd"] == pytest.approx(want, abs=1e-6) and v["client_calls"] == 1 and v["client_model"] == "gpt-oss:20b"
    assert v["backends"]["writer"]["host"] == "api.deepinfra.com"
    doc["checker"] = {"model": "some/unlisted", "backend": {"host": "api.example.com"}}
    assert reading_cost(doc)["cost_usd"] is None                         # never guessed


def test_health_says_which_roles_are_ready_and_never_a_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("JYOTISH_WRITER_BACKEND", "openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b")
    monkeypatch.setenv("JYOTISH_CHECKER_BACKEND", "openai:http://localhost:11434/v1:qwen3.6:27b")
    monkeypatch.delenv("JYOTISH_CLIENT_BACKEND", raising=False)
    monkeypatch.setenv("JYOTISH_OPENAI_KEY", "sk-secret-value")
    s = backends_status()
    assert s["writer"] == {"provider": "openai-compatible", "host": "api.deepinfra.com", "model": "openai/gpt-oss-120b",
                           "ready": True}
    assert s["checker"]["ready"] is True                                 # local: no key needed
    assert s["client"] == {"provider": "anthropic", "ready": False}      # no Anthropic key
    assert "sk-secret-value" not in str(s)


# --- depth full on an open model (part 2) ----------------------------------------------------------

def test_depth_full_on_a_local_model_is_refused_naming_the_payload_unless_allowed(monkeypatch):
    from jyotish.narrate import NarrationError, OpenAIBackend, full_depth_guard
    local = OpenAIBackend("http://localhost:11434/v1", "gpt-oss:20b")
    monkeypatch.delenv("JYOTISH_ALLOW_LOCAL_FULL", raising=False)
    with pytest.raises(NarrationError, match=r"300,000 characters, about 104,530 tokens.*JYOTISH_ALLOW_LOCAL_FULL=1"):
        full_depth_guard(local, "s" * 100_000, "u" * 200_000)
    monkeypatch.setenv("JYOTISH_ALLOW_LOCAL_FULL", "1")
    full_depth_guard(local, "s" * 100_000, "u" * 200_000)            # allowed: the Modelfile's num_ctx decides


def test_depth_full_on_a_hosted_model_too_small_for_the_chart_is_refused_before_any_call():
    from jyotish.narrate import CONTEXT_TOKENS, NarrationError, OpenAIBackend, full_depth_guard
    msg = "x" * 560_613                                               # depth full on the reference chart
    with pytest.raises(NarrationError, match="exceed openai/gpt-oss-120b's context window of 131,072"):
        full_depth_guard(OpenAIBackend("https://api.deepinfra.com/v1/openai", "openai/gpt-oss-120b"), "", msg)
    with pytest.raises(NarrationError, match="202,752"):
        full_depth_guard(OpenAIBackend("https://api.deepinfra.com/v1/openai", "zai-org/GLM-4.7"), "", msg)
    full_depth_guard(OpenAIBackend("https://api.deepinfra.com/v1/openai", "Qwen/Qwen3.6-35B-A3B"), "", msg)
    full_depth_guard(OpenAIBackend("https://api.example.com/v1", "unlisted/model"), "", msg)   # unknown: the server decides
    full_depth_guard(None, "", msg)                                   # Anthropic, a replay or a stand-in: not this guard
    assert CONTEXT_TOKENS["Qwen/Qwen3.6-35B-A3B"] == 262_144


def test_models_md_names_the_variables_the_prices_and_the_rule():
    from pathlib import Path
    doc = (Path(__file__).resolve().parents[1] / "docs" / "models.md").read_text()
    for needle in ("JYOTISH_WRITER_BACKEND=openai:https://api.deepinfra.com/v1/openai:openai/gpt-oss-120b",
                   "JYOTISH_CHECKER_BACKEND=openai:https://openrouter.ai/api/v1:z-ai/glm-4.7",
                   '"data_collection": "deny", "zdr": true, "require_parameters": true',
                   "JYOTISH_ALLOW_LOCAL_FULL=1", "195,340 tokens", "not worse **on any category**",
                   "read from the providers' own pages on **2026-10-25**"):
        assert needle in doc, needle
    for (host, model), p in OPEN_PRICES.items():
        if host == "api.deepinfra.com" and model in ("openai/gpt-oss-120b", "zai-org/GLM-4.7", "Qwen/Qwen3.6-35B-A3B"):
            fmt = lambda x: f"{x:.2f}" if round(x, 2) == x else f"{x:g}"
            assert f"{fmt(p[0])} / {fmt(p[1])}" in doc, (model, p)      # the doc's prices are the engine's


# --- measurement (part 3) ---------------------------------------------------------------------------

def _bench():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import checker_bench
    return checker_bench


def test_a_backends_scorecard_sits_beside_opuss_under_its_own_name():
    cb = _bench()
    assert cb.scorecard_path("zai-org/GLM-4.7").name == "checker_scorecard_zai-org-glm-4.7.md"
    assert cb.scorecard_path("gpt-oss:20b").name == "checker_scorecard_gpt-oss-20b.md"
    assert cb.scorecard_path("Qwen/Qwen3.6-35B-A3B").parent == cb.SCORECARD.parent and cb.SCORECARD.name == "checker_scorecard.md"


def test_the_gates_recall_is_read_per_category_from_its_scorecard():
    cb = _bench()
    gate = cb.gate_recall(cb.SCORECARD.read_text())
    assert gate["overall"] == 0.973 and gate["dignity_changed"] == 1.0 and "accepted" in gate


def test_the_rule_passes_only_when_not_worse_on_any_category_and_waits_for_the_unmeasured():
    cb = _bench()
    rows = [{"id": "a", "label": "reject", "category": "sign_changed"}, {"id": "b", "label": "reject", "category": "negated"},
            {"id": "c", "label": "accept", "category": "accepted"}]
    caught = {"a": (True, ""), "b": (True, ""), "c": (False, "")}
    text = "\n".join(cb.rule_section(rows, caught, {"sign_changed": 1.0, "negated": 1.0}, "Opus"))
    assert "it passes the rule" in text
    missed = dict(caught, b=(False, ""))
    assert "worse on negated: it does not pass the rule" in "\n".join(cb.rule_section(rows, missed, {"sign_changed": 1.0,
                                                                                                     "negated": 1.0}, "Opus"))
    waits = "\n".join(cb.rule_section(rows, caught, {"sign_changed": 1.0}, "Opus"))
    assert "not yet decided: not measured by both on negated" in waits
    # And the other way round: a category the gate measured that this run did not (all unchecked) waits too.
    unmeasured_here = "\n".join(cb.rule_section(rows[:1] + rows[2:], {"a": (True, ""), "c": (False, "")},
                                                 {"sign_changed": 1.0, "negated": 1.0}, "GLM"))
    assert "not yet decided: not measured by both on negated" in unmeasured_here and "passes the rule" not in unmeasured_here


def test_the_scripts_env_file_sets_only_unset_keys_and_returns_names_only(tmp_path, monkeypatch):
    from jyotish.envfile import load
    env = tmp_path / ".env"
    env.write_text("# a comment\nPOSTGRES_PASSWORD=not-read\nexport JYOTISH_OPENAI_KEY='sk-from-file'\n"
                   "ANTHROPIC_API_KEY=already-there\nJYOTISH_CHECKER_CONCURRENCY=2\n")
    # Set empty through monkeypatch (empty counts as unset for load()), so what load() sets is undone after.
    for name in ("JYOTISH_OPENAI_KEY", "JYOTISH_CHECKER_CONCURRENCY", "POSTGRES_PASSWORD"):
        monkeypatch.setenv(name, "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "from-the-shell")
    names = load(env)
    import os
    assert names == ["JYOTISH_OPENAI_KEY", "JYOTISH_CHECKER_CONCURRENCY"] and "sk-from-file" not in str(names)
    assert os.environ["JYOTISH_OPENAI_KEY"] == "sk-from-file" and os.environ["ANTHROPIC_API_KEY"] == "from-the-shell"
    assert os.environ["POSTGRES_PASSWORD"] == "" and load(tmp_path / "missing") == []


# --- the gate in use: GLM-4.7 (2026-10-25), GLM-5.3-Flash at temperature 0 (2026-10-31) -------------

def test_the_gate_in_use_is_glm_53_flash_at_temperature_0_and_it_passed_against_glm_47():
    cb = _bench()
    assert cb.GATE.name == "checker_scorecard_zai-org-glm-5.3-flash_temp-0.md"
    text = cb.GATE.read_text()
    assert cb.gate_name_of(text) == "zai-org/GLM-5.3-Flash"                       # not "…Flash," from the title
    assert "the gate in use, zai-org/GLM-4.7" in text and "Verdict: not worse on any category: it passes the rule" in text
    flash, glm = cb.gate_recall(text), cb.gate_recall(cb.PREVIOUS_GATE.read_text())
    assert sorted(flash) == sorted(glm) and all(v == 1.0 for v in flash.values())
    qwen = cb.gate_recall(cb.scorecard_path("Qwen/Qwen3.6-35B-A3B").read_text())
    assert "does not pass the rule" in "\n".join(cb.rule_from_recall(qwen, flash, "zai-org/GLM-5.3-Flash"))


def test_the_previous_gate_is_glm_and_qwen_does_not_pass_against_it():
    cb = _bench()
    assert cb.PREVIOUS_GATE.name == "checker_scorecard_zai-org-glm-4.7.md"
    gate_text = cb.PREVIOUS_GATE.read_text()
    assert cb.gate_name_of(gate_text) == "zai-org/GLM-4.7" and cb.gate_name_of(cb.SCORECARD.read_text()) == "claude-opus-5-5"
    glm = cb.gate_recall(gate_text)
    assert glm["overall"] == 1.0 and all(v == 1.0 for v in glm.values())
    qwen = cb.gate_recall(cb.scorecard_path("Qwen/Qwen3.6-35B-A3B").read_text())
    verdict = "\n".join(cb.rule_from_recall(qwen, glm, "zai-org/GLM-4.7"))
    assert "worse on contradicts_its_fact, judgement_premise, unstated_claim: it does not pass the rule" in verdict
    assert "Verdict: not worse" not in verdict
    committed = cb.scorecard_path("Qwen/Qwen3.6-35B-A3B").read_text()
    assert "the gate in use, zai-org/GLM-4.7" in committed and "does not pass the rule" in committed


def test_compose_passes_each_roles_backend_to_the_service():
    import yaml
    from pathlib import Path
    env = yaml.safe_load((Path(__file__).resolve().parents[1] / "docker-compose.yml").read_text())["services"]["app"]["environment"]
    for name in ("JYOTISH_WRITER_BACKEND", "JYOTISH_CHECKER_BACKEND", "JYOTISH_CLIENT_BACKEND", "JYOTISH_OPENAI_KEY",
                 "JYOTISH_CHECKER_CONCURRENCY", "JYOTISH_CHECKER_TEMPERATURE"):
        assert env[name] == "${%s:-}" % name, name


def test_a_run_at_another_checker_effort_never_writes_over_the_gates_scorecard():
    cb = _bench()
    assert cb.scorecard_path("zai-org/GLM-4.7", "low").name == "checker_scorecard_zai-org-glm-4.7_effort-low.md"
    assert cb.scorecard_path("zai-org/GLM-4.7", "high") == cb.scorecard_path("zai-org/GLM-4.7") == cb.PREVIOUS_GATE
    assert cb.partial_path("openai:https://api.deepinfra.com/v1/openai:zai-org/GLM-4.7", "low").name == \
        "zai-org-glm-4.7_effort-low.jsonl"
    assert cb.gate_name_of("# Checker benchmark: zai-org/GLM-4.7 at checker effort low\n") == "zai-org/GLM-4.7"


def test_a_reasoning_off_run_has_its_own_scorecard():
    cb = _bench()
    assert cb.scorecard_path("zai-org/GLM-4.7", "none").name == "checker_scorecard_zai-org-glm-4.7_effort-none.md"
