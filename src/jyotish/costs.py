"""What a reading cost: its tokens (the usage narrate records on every reading: the writer's and the
checker's calls, summed) priced per model. The prices are USD per million tokens from the Anthropic
price list as cached on 2026-10-06; thinking is billed as output and is inside output_tokens. A
model not in PRICES is counted with its tokens and no cost (`priced` false), never guessed."""

from __future__ import annotations

from typing import Any

# input, output, cache read, cache write (5-minute, 1.25 x input)
PRICES = {"claude-opus-5-5": (4.00, 20.00, 0.20, 5.00), "claude-fable-5-1": (10.00, 50.00, 0.25, 12.50),
          "claude-opus-5": (5.00, 25.00, 0.50, 6.25), "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50)}
TOKEN_KEYS = ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")


def cost(model: str | None, t: dict[str, Any]) -> float | None:
    p = PRICES.get(model or "")
    if p is None:
        return None
    return (int(t.get("input_tokens") or 0) * p[0] + int(t.get("output_tokens") or 0) * p[1]
            + int(t.get("cache_read_input_tokens") or 0) * p[2]
            + int(t.get("cache_creation_input_tokens") or 0) * p[3]) / 1e6


def tokens(side: dict[str, Any] | None) -> dict[str, int]:
    return {k: int((side or {}).get(k) or 0) for k in TOKEN_KEYS}


def reading_cost(document: dict[str, Any]) -> dict[str, Any]:
    """A finished reading's ledger values from its own record (`writer`, `checker`, `usage`)."""
    usage = document.get("usage") or {}
    writer_model = (document.get("writer") or {}).get("model") or document.get("model")
    checker_model = (document.get("checker") or {}).get("model")
    w, c = tokens(usage.get("writer")), tokens(usage.get("checker"))
    wc, cc = cost(writer_model, w), cost(checker_model, c)
    return {"writer_model": writer_model, "checker_model": checker_model, "depth": document.get("depth"),
            "writer_tokens": w, "checker_tokens": c,
            "writer_calls": int((usage.get("writer") or {}).get("calls") or 0),
            "checker_calls": int((usage.get("checker") or {}).get("calls") or 0),
            "cost_usd": None if wc is None or cc is None else round(wc + cc, 6),
            "seconds": usage.get("wall_seconds"),
            "replayed": str(document.get("narration_source", "live")).startswith("fixture:")}
