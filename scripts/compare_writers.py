"""The writer bake-off (2026-11-02, after Ray's first live turns): the seven-turn conversation on the reference chart
(scripts/live_timing.py SEVEN_TURNS, tests/test_conversation.py) run once on each writer, the checker unchanged
(GLM-5.3-Flash at temperature 0 on DeepInfra, from .env), and docs/writers_2026-11-02.md written: per writer the
seconds to the first verified sentence and to done, the removed share, the word warnings and the cost per turn; then
the text the client read on every turn, writer by writer, so Ray chooses the voice by reading it; and which writers
are affordable at INR 149 a ten-turn session. The script chooses no writer.

Before any model is called it lists DeepInfra's models (a writer not served is skipped and said so), checks that the
anthropic writers' key is in the environment by name (the anthropic SDK reads ANTHROPIC_API_KEY; the key is never
printed), and prints the expected cost per writer and in all, stopping when the total is over --budget (USD 4).

    .venv/bin/python scripts/compare_writers.py --estimate        # the estimate only, no model call
    .venv/bin/python scripts/compare_writers.py                   # run, then write the report
    .venv/bin/python scripts/compare_writers.py --report-only     # the report from the records already written
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

DEEPINFRA = "https://api.deepinfra.com/v1/openai"
OUT = ROOT / "docs" / "writers_2026-11-02"
REPORT = ROOT / "docs" / "writers_2026-11-02.md"
AS_OF = "2026-11-02"
# (label, backend spec, model on the anthropic backend, note). The DeepInfra picks are what its /models listed on
# 2026-11-06 for what was asked: the largest Qwen3.6 (35B-A3B, 35B parameters in all; the 27B is dense), the latest
# DeepSeek V3 (V3.2), the latest Kimi K2 (K2.6) and GLM-5 (5.3; 5.3-Flash is the checker).
WRITERS = [
    ("gpt-oss-120b", f"openai:{DEEPINFRA}:openai/gpt-oss-120b", None, "the baseline, the writer in use"),
    ("qwen3.6-35b-a3b", f"openai:{DEEPINFRA}:Qwen/Qwen3.6-35B-A3B", None, "the largest Qwen3.6 by parameters"),
    ("deepseek-v3.2", f"openai:{DEEPINFRA}:deepseek-ai/DeepSeek-V3.2", None, "the latest DeepSeek V3"),
    ("kimi-k2.6", f"openai:{DEEPINFRA}:moonshotai/Kimi-K2.6", None, "the latest Kimi K2"),
    ("glm-5.3", f"openai:{DEEPINFRA}:zai-org/GLM-5.3", None, "the latest GLM-5 (5.3-Flash is the checker)"),
    ("claude-haiku-5-5", "anthropic", "claude-haiku-5-5", "the writer role only"),
    ("claude-sonnet-5-5", "anthropic", "claude-sonnet-5-5", "the writer role only"),
]
ANTHROPIC_KEY = "ANTHROPIC_API_KEY"         # what anthropic.Anthropic() reads (narrate.AnthropicBackend passes none)
# The estimate's assumptions: per writer call, the characters sent (measured offline below) at 3.5 a token and at
# most OUT_PER_CALL tokens out (reasoning included); every answered turn taking all CONFIG.max_attempts calls; the
# checker's tokens per answered turn as the live five-turn conversation of 2026-11-01 measured them (docs/live_2026-11-01,
# 16,773 in and 7,074 out on average over its four answered turns), at GLM-5.3-Flash's price.
CHARS_PER_TOKEN = 3.5
OUT_PER_CALL = 8000
CHECKER_TOKENS = (16773, 7074)
# The price of a ten-turn session to the client, and what is left of it for the models: GST at 18% and a 2% payment
# fee taken off (the report says so; neither is a quoted rate for this business).
SESSION_INR, SESSION_TURNS, GST, FEE = 149, 10, 0.18, 0.02


def served() -> set[str]:
    """DeepInfra's model ids (the writer's key, never printed)."""
    import httpx
    key = os.environ.get("JYOTISH_WRITER_KEY") or os.environ.get("JYOTISH_OPENAI_KEY")
    r = httpx.get(f"{DEEPINFRA}/models", headers={"Authorization": f"Bearer {key}"}, timeout=60)
    r.raise_for_status()
    return {m["id"] for m in r.json()["data"]}


def model_of(spec: str, model: str | None) -> tuple[str, str]:
    """(model, host) of a writer."""
    if spec == "anthropic":
        return model, "api.anthropic.com"
    return spec.rsplit(":", 1)[1], "api.deepinfra.com"


def measure_calls() -> list[int]:
    """The characters each answered turn's first writer call sends (system prompt and message), one per answered
    turn of the seven, measured by running the conversation offline (conversation.OfflineTurnWriter, a stub
    checker); a retry sends its instruction besides, which OUT_PER_CALL's margin covers."""
    from datetime import date as _date

    from jyotish.conversation import OfflineTurnWriter, answer_turn, route_turn
    from jyotish.narrate import CheckResult, Proposition
    from jyotish.reference import REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON
    from jyotish.uncertainty import assess
    from live_timing import SEVEN_TURNS
    chart = assess(REFERENCE_BIRTH_UTC, REFERENCE_LAT, REFERENCE_LON, true_node=False)
    sizes: list[int] = []

    class Measure(OfflineTurnWriter):
        def __call__(self, system, user, errors):
            if not errors:                          # a turn's first call; the estimate prices every attempt itself
                sizes.append(len(system) + len(user))
            return super().__call__(system, user, errors)

    ok = lambda s, d: CheckResult(propositions=[Proposition(text=s, supported=True, evidence="estimate")])
    last, history = None, []
    for m in SEVEN_TURNS:
        route = route_turn(m, chart, last)
        doc = answer_turn(chart, m, route, as_of=_date.fromisoformat(AS_OF), history=list(history),
                          drafter=Measure(), checker=ok)
        history.append({"question": m, "answer": " ".join(doc["shown"])})
        if not route.off_limits:
            last = route
    return sizes


def estimate(writers, sizes: list[int]) -> tuple[list[dict], float]:
    from jyotish.costs import price
    from jyotish.narrate import CONFIG
    attempts = CONFIG.max_attempts
    cin, cout, *_ = price("zai-org/GLM-5.3-Flash", "api.deepinfra.com")
    checker = len(sizes) * (CHECKER_TOKENS[0] * cin + CHECKER_TOKENS[1] * cout) / 1e6
    rows, total = [], 0.0
    for label, spec, model, _ in writers:
        name, host = model_of(spec, model)
        p = price(name, host)
        if p is None:
            raise SystemExit(f"{label}: no price for {name} on {host} in jyotish.costs (never guessed): add it first")
        tokens_in = sum(s / CHARS_PER_TOKEN for s in sizes) * attempts
        tokens_out = len(sizes) * attempts * OUT_PER_CALL
        writer = (tokens_in * p[0] + tokens_out * p[1]) / 1e6
        rows.append({"label": label, "writer_usd": writer, "checker_usd": checker, "usd": writer + checker,
                     "tokens_in": round(tokens_in), "tokens_out": tokens_out})
        total += writer + checker
    return rows, total


def run(writers) -> dict[str, str]:
    """Each writer's seven turns through scripts/live_timing.py (its rows appended to docs/live_timings.jsonl, its
    turns' records to OUT); a writer that fails is recorded with its error and the next one runs. The failures are
    kept in OUT/failed.json across runs: a writer run again (--only) drops its old failure or records its new one."""
    import live_timing
    OUT.mkdir(parents=True, exist_ok=True)
    failed = json.loads((OUT / "failed.json").read_text()) if (OUT / "failed.json").exists() else {}
    for label, *_ in writers:
        failed.pop(label, None)
    for label, spec, model, _ in writers:
        argv = ["--label", label, "--turn", "--writer", spec, "--out", str(OUT), "--as-of", AS_OF]
        if model:
            argv += ["--writer-model", model]
        print(f"--- {label}", flush=True)
        try:
            live_timing.main(argv)
        except Exception as e:                          # noqa: BLE001 (one writer's failure is its row)
            failed[label] = f"{type(e).__name__}: {str(e)[:300]}"
            print(f"{label} failed: {failed[label]}", flush=True)
    (OUT / "failed.json").write_text(json.dumps(failed, indent=1) + "\n")
    return failed


def turns_of(label: str) -> list[dict]:
    out = []
    for n in range(1, 8):
        f = OUT / f"{label}-{n}.turn.json"
        out.append(json.loads(f.read_text()) if f.exists() else None)
    return out


def why(error: str) -> str:
    """A failure in a line: a provider's want of credit said as such, anything else its first 160 characters."""
    if "402" in error and "balance" in error:
        return "DeepInfra refused it with HTTP 402: the account has no balance"
    if "credit balance is too low" in error:
        return "Anthropic refused it with HTTP 400: the account's credit balance is too low"
    return error[:160]


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _s(x, nd=1):
    return "–" if x is None else f"{x:.{nd}f}"


def report(writers, skipped: dict[str, str], failed: dict[str, str], estimates: list[dict], usd_inr: float) -> str:
    from jyotish.costs import reading_cost
    from live_timing import SEVEN_TURNS
    lines = ["# The writer bake-off, 2026-11-02", "",
             f"Written by `scripts/compare_writers.py` on {date.today().isoformat()}: the seven-turn conversation on "
             "the reference chart (Ray's first live turns of 2026-11-02 after the five of SPEC Layer 8's tests), once "
             "per writer, as of 2026-11-02, after the four fixes of that day (docs/spec_notes_2026-11-02.md). The "
             "checker is the same for every writer: GLM-5.3-Flash at temperature 0 on DeepInfra. One run each: the "
             "numbers are one sample per turn, not a distribution. The script chooses no writer; Ray chooses the voice "
             "by reading the turns below.", ""]
    if skipped:
        lines += ["Not run: " + "; ".join(f"{k} ({v})" for k, v in skipped.items()) + ".", ""]
    if failed:
        lines += ["Not run to the end: " + "; ".join(f"{k} ({why(v)})" for k, v in failed.items()) + ". Each such "
                  "writer runs again with `scripts/compare_writers.py --only <label> …`, and the report is then "
                  "rewritten with every writer that has records.", ""]
    lines += ["## Per writer", "",
              "Means over the six answered turns (the fifth is the fixed reply and calls no model). First verified: "
              "seconds to the first sentence shown to the client; done: seconds to the whole answer; removed: sentences "
              "refused of those the writer wrote, retries included; warnings: word warnings on the turn; cost: writer "
              "and checker together, USD, at jyotish.costs's prices.", "",
              "| writer | first verified s | done s | removed share | warnings / turn | engine's answer shown | "
              "opened on the question | USD / turn | estimate USD (7 turns) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    per: dict[str, dict] = {}
    est = {e["label"]: e for e in estimates}
    for label, spec, model, note in writers:
        docs = [d for d in turns_of(label) if d and d.get("source") != "fixed"]
        if not docs:
            continue
        costs = [reading_cost(d)["cost_usd"] for d in docs]
        t = [d.get("timeline") or {} for d in docs]
        removed = sum(sum(1 for x in d.get("removed") or [] if x.get("sentence")) for d in docs)
        written = removed + sum(len(d.get("accepted") or []) for d in docs)
        opened = [d.get("opened_by") for d in docs if d.get("opened_by")]
        per[label] = {"usd_turn": _mean(costs), "costs": costs}
        lines.append(f"| {label} | {_s(_mean([x.get('first_verified') for x in t]))} | {_s(_mean([x.get('done') for x in t]))} | "
                     f"{_s(removed / written if written else None, 2)} | {_s(_mean([len(d.get('warnings') or []) for d in docs]))} | "
                     f"{sum(1 for d in docs if d.get('source') == 'engine')} of {len(docs)} | "
                     f"{sum(1 for o in opened if o == 'writer')} of {len(opened)} by the writer | "
                     f"{_s(_mean(costs), 4) if None not in costs else 'unpriced'} | {_s(est.get(label, {}).get('usd'), 3)} |")
    lines += ["", "Per turn, seconds to the first verified sentence / to done, the removed share and the cost (USD):", "",
              "| writer | " + " | ".join(f"{n}" for n in range(1, 8)) + " |", "| --- |" + " --- |" * 7]
    for label, *_ in writers:
        docs = turns_of(label)
        if not any(docs):
            continue
        cells = []
        for d in docs:
            if d is None:
                cells.append("–")
            elif d.get("source") == "fixed":
                cells.append("fixed reply")
            else:
                t = d.get("timeline") or {}
                rem = sum(1 for x in d.get("removed") or [] if x.get("sentence"))
                wr = rem + len(d.get("accepted") or [])
                c = reading_cost(d)["cost_usd"]
                cells.append(f"{_s(t.get('first_verified'))} / {_s(t.get('done'))}; {_s(rem / wr if wr else None, 2)}; "
                             f"{_s(c, 4) if c is not None else 'unpriced'}")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    net = SESSION_INR / (1 + GST) * (1 - FEE)
    lines += ["", f"## Affordable at INR {SESSION_INR} a ten-turn session", "",
              f"Ten turns at the writer's mean cost per answered turn, at USD 1 = INR {usd_inr:g} (`--usd-inr`; a rate "
              f"given to the script, not looked up). Of INR {SESSION_INR}, INR {net:.2f} is left after GST at "
              f"{GST:.0%} and a payment fee of {FEE:.0%} (assumed, not quoted rates); a writer is affordable when "
              "ten turns cost less than that, and the share says how much of it they take. Hosting, the database and "
              "the astrologer's time are not counted.", "",
              "| writer | USD / ten turns | INR / ten turns | share of what is left | affordable |", "| --- | --- | --- | --- | --- |"]
    for label, *_ in writers:
        p = per.get(label)
        if not p or p["usd_turn"] is None or None in p["costs"]:
            continue
        usd = p["usd_turn"] * SESSION_TURNS
        inr = usd * usd_inr
        lines.append(f"| {label} | {usd:.3f} | {inr:.2f} | {inr / net:.1%} | {'yes' if inr < net else 'no'} |")
    lines += ["", "## What the client read, turn by turn", "",
              "Each turn's answer as the client's screen showed it (`shown`), writer by writer, in the order above. "
              "Paragraph breaks are as the answer gave them.", ""]
    for n, message in enumerate(SEVEN_TURNS, 1):
        lines += [f"### Turn {n}: “{message}”", ""]
        for label, *_ in writers:
            d = turns_of(label)[n - 1]
            if d is None:
                continue
            paras = set(d.get("paragraphs") or [0])
            body, cur = [], []
            for i, s in enumerate(d.get("shown") or []):
                if i in paras and cur:
                    body.append(" ".join(cur))
                    cur = []
                cur.append(s)
            if cur:
                body.append(" ".join(cur))
            src = d.get("source")
            tag = {"engine": " (the engine's own answer: no writer sentence passed)", "fixed": " (the fixed reply)"}.get(src, "")
            lines += [f"**{label}**{tag}", ""] + [f"> {b}" + ("\n>" if k < len(body) - 1 else "") for k, b in enumerate(body)] + [""]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true", help="print the expected cost and stop")
    ap.add_argument("--report-only", action="store_true", help="write the report from the records in docs/writers_2026-11-02")
    ap.add_argument("--budget", type=float, default=4.0, help="stop before running when the expected total is over it")
    ap.add_argument("--usd-inr", type=float, default=88.0, help="the exchange rate the affordability table uses")
    ap.add_argument("--only", nargs="*", help="run only these writers (labels)")
    a = ap.parse_args(argv)
    from jyotish.envfile import load as load_env
    print("read from .env:", load_env(ROOT / ".env"))            # names only, never a value
    writers = [w for w in WRITERS if not a.only or w[0] in a.only]
    skipped: dict[str, str] = {}
    have = served()
    for label, spec, model, _ in list(writers):
        if spec != "anthropic" and spec.rsplit(":", 1)[1] not in have:
            skipped[label] = "not served by DeepInfra"
    if any(spec == "anthropic" for _, spec, _, _ in writers) and not os.environ.get(ANTHROPIC_KEY):
        raise SystemExit(f"the anthropic writers need {ANTHROPIC_KEY} (what anthropic.Anthropic() reads), and it is "
                         "not set: stopping before any run")
    writers = [w for w in writers if w[0] not in skipped]
    if a.report_only:
        failed = json.loads((OUT / "failed.json").read_text()) if (OUT / "failed.json").exists() else {}
        every = [w for w in WRITERS if w[0] not in skipped]
        REPORT.write_text(report(every, skipped, failed, estimate(every, measure_calls())[0], a.usd_inr))
        print(f"-> {REPORT}")
        return 0
    sizes = measure_calls()
    rows, total = estimate(writers, sizes)
    print(f"expected cost (seven turns, {len(sizes)} answered turns, every turn taking every attempt, "
          f"{OUT_PER_CALL} tokens out a call):")
    for r in rows:
        print(f"  {r['label']:20} writer {r['writer_usd']:.3f}  checker {r['checker_usd']:.3f}  total {r['usd']:.3f} USD")
    print(f"  {'all':20} {total:.3f} USD (budget {a.budget:g})")
    for k, v in skipped.items():
        print(f"  skipped {k}: {v}")
    if total > a.budget:
        print("over the budget: stopping before any run")
        return 2
    if a.estimate:
        return 0
    failed = run(writers)
    # The report has every writer with records, not only the ones this run ran (--only).
    every = [w for w in WRITERS if w[0] not in skipped]
    REPORT.write_text(report(every, skipped, failed, estimate(every, sizes)[0], a.usd_inr))
    print(f"-> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
