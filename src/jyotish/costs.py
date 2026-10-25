"""What a reading cost: its tokens (the usage narrate records on every reading: the writer's, the
checker's and, at depth full, the client's layer's calls, each summed) priced per model, each role by
its own model and backend (docs/models.md). Prices are USD per million tokens: Anthropic's from its
price list as cached on 2026-10-06 (PRICES, keyed by model); an OpenAI-compatible provider's per host
and model as read from the provider's own page on the date given (OPEN_PRICES, with `PRICE_SOURCES`);
a local server (Ollama on this machine) charges nothing per token. Thinking and reasoning are billed
as output and are inside output_tokens. A model without a price is counted with its tokens and no
cost (`priced` false), never guessed; a reading with any such role has no total cost."""

from __future__ import annotations

from typing import Any

# input, output, cache read, cache write (5-minute, 1.25 x input)
PRICES = {"claude-opus-5-5": (4.00, 20.00, 0.20, 5.00), "claude-fable-5-1": (10.00, 50.00, 0.25, 12.50),
          "claude-opus-5": (5.00, 25.00, 0.50, 6.25), "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50)}
# (host, model) -> input, output, cache read, cache write. A provider that lists no cached price is
# priced at its input price for cached tokens (what it bills when it does not discount them).
OPEN_PRICES = {
    ("api.deepinfra.com", "openai/gpt-oss-120b"): (0.037, 0.17, 0.037, 0.0),
    ("api.deepinfra.com", "openai/gpt-oss-20b"): (0.03, 0.14, 0.03, 0.0),
    ("api.deepinfra.com", "zai-org/GLM-4.7"): (0.40, 1.75, 0.08, 0.0),
    ("api.deepinfra.com", "Qwen/Qwen3.6-35B-A3B"): (0.10, 0.95, 0.10, 0.0),
    # OpenRouter's list price per model (its default endpoint); a request may be routed to a cheaper or
    # dearer endpoint, and OpenRouter returns what it charged (usage.cost, kept as provider_cost_usd).
    ("openrouter.ai", "openai/gpt-oss-120b"): (0.15, 0.60, 0.075, 0.0),
    ("openrouter.ai", "openai/gpt-oss-20b"): (0.018, 0.09, 0.009, 0.0),
    ("openrouter.ai", "z-ai/glm-4.7"): (0.54, 1.98, 0.099, 0.0),
    ("openrouter.ai", "z-ai/glm-4.7-flash"): (0.0605, 0.40, 0.0605, 0.0),
    ("openrouter.ai", "qwen/qwen3.6-35b-a3b"): (0.10, 0.95, 0.05, 0.0),
    ("openrouter.ai", "qwen/qwen3.6-27b"): (0.25, 2.00, 0.025, 0.0),
}
PRICE_SOURCES = {
    "anthropic": {"source": "https://platform.claude.com/docs/en/about-claude/pricing", "read_on": "2026-10-06"},
    "api.deepinfra.com": {"source": "https://deepinfra.com/<model id> (each model's page, Standard tier)",
                          "read_on": "2026-10-25"},
    "openrouter.ai": {"source": "https://openrouter.ai/api/v1/models (each model's list price)", "read_on": "2026-10-25"},
    "local": {"source": "a server on this machine charges nothing per token; the machine's own cost is not counted",
              "read_on": "2026-10-25"},
}
TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
LOCAL = ("localhost", "127.0.0.1", "::1", "0.0.0.0", "host.docker.internal")


def is_local(host: str | None) -> bool:
    """A server on this machine (or the local network's .local names): "localhost:11434", "[::1]:11434"."""
    host = host or ""
    name = host[1:host.index("]")] if host.startswith("[") and "]" in host else host.split(":")[0]
    return name in LOCAL or name.endswith(".local")


def price(model: str | None, host: str | None = None) -> tuple[float, float, float, float] | None:
    """The price of a model on a host: Anthropic's by model, an open provider's by (host, model), a
    local server's nothing; None when it has none (never guessed)."""
    if host and is_local(host):
        return (0.0, 0.0, 0.0, 0.0)
    if host and host != "api.anthropic.com":
        return OPEN_PRICES.get((host, model or ""))
    return PRICES.get(model or "")


def cost(model: str | None, t: dict[str, Any], host: str | None = None) -> float | None:
    p = price(model, host)
    if p is None:
        return None
    return (int(t.get("input_tokens") or 0) * p[0] + int(t.get("output_tokens") or 0) * p[1]
            + int(t.get("cache_read_input_tokens") or 0) * p[2]
            + int(t.get("cache_creation_input_tokens") or 0) * p[3]) / 1e6


def tokens(side: dict[str, Any] | None) -> dict[str, int]:
    return {k: int((side or {}).get(k) or 0) for k in TOKEN_KEYS}


def _host(role: dict[str, Any]) -> str | None:
    return ((role or {}).get("backend") or {}).get("host")


def reading_cost(document: dict[str, Any]) -> dict[str, Any]:
    """A finished reading's ledger values from its own record (`writer`, `checker`, `client`, `usage`):
    each role's tokens priced by its own model and host; the total is None when a role that made calls
    has no price."""
    usage = document.get("usage") or {}
    writer, checker, client = document.get("writer") or {}, document.get("checker") or {}, document.get("client") or {}
    writer_model = writer.get("model") or document.get("model")
    checker_model = checker.get("model")
    client_model = client.get("model") or (writer_model if usage.get("client") else None)
    w, c, k = tokens(usage.get("writer")), tokens(usage.get("checker")), tokens(usage.get("client"))
    calls = {r: int((usage.get(r) or {}).get("calls") or 0) for r in ("writer", "checker", "client")}
    parts = [(calls["writer"], cost(writer_model, w, _host(writer))), (calls["checker"], cost(checker_model, c, _host(checker))),
             (calls["client"], cost(client_model, k, _host(client) or _host(writer)))]
    total = None if any(n and v is None for n, v in parts) else round(sum(v or 0.0 for _, v in parts), 6)
    backends = {r: d["backend"] for r, d in (("writer", writer), ("checker", checker), ("client", client))
                if d.get("backend")}
    return {"writer_model": writer_model, "checker_model": checker_model, "depth": document.get("depth"),
            "writer_tokens": w, "checker_tokens": c, "writer_calls": calls["writer"], "checker_calls": calls["checker"],
            "client_model": client_model if calls["client"] else None, "client_tokens": k if calls["client"] else None,
            "client_calls": calls["client"], "backends": backends or None,
            "cost_usd": total, "seconds": usage.get("wall_seconds"),
            "replayed": str(document.get("narration_source", "live")).startswith("fixture:")}
