"""How often a composed sentence is true of its chart (review 2026-11-15, L5): the gate checker on a fixed sample of
composed fact sentences from random synthetic charts (scripts/synthetic_cohort.births, no one's data), each read
against its plan item's facts, the engine's own sentence, the dignity words and the glossary, as the drafted
variants were (scripts/draft_bank.check_data). Writes docs/composed_check_<date>.json, which scripts/evaluate.py
reports as bank.composed_supported, never gated. The expected cost is printed first; above --budget nothing is
called; no key is printed.

    .venv/bin/python scripts/composed_check.py              # 120 sentences from 60 charts, seed 21
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
AS_OF = date(2026, 11, 15)


def sample(charts: int, per_chart: int, seed: int) -> list[dict]:
    """Up to `per_chart` composed fact sentences (from the bank, not the engine's own) of one random area of each
    chart, each with what it is checked against; the same charts, areas and sentences for the same seed."""
    from synthetic_cohort import births
    from jyotish.chart import compute
    from jyotish.conversation import compose
    from jyotish.plan import plan
    from draft_bank import check_data
    rng = random.Random(seed)
    out = []
    for n, b in enumerate(births(charts, seed)):
        c = compute(datetime.fromisoformat(f"{b['date']}T{b['time']}"), b["lat"], b["lon"], true_node=False)
        areas = sorted(a for a in c.scored.areas if a not in ("synastry", "longevity", "health")
                       and c.scored.areas[a].score_classical is not None)
        area = rng.choice(areas)
        p = plan(c, "check", [area], "both", ["why"], as_of=AS_OF)
        got = [s for s in compose(p, session_key=f"cc{n}")["sentences"] if s["row"] and s["row"]["kind"] == "fact"]
        for s in rng.sample(got, min(per_chart, len(got))):
            item = p.items[s["item"]]
            out.append({"chart": n, "area": area, "signature": s["signature"], "variant": s["row"]["variant"],
                        "sentence": s["text"], "data": check_data({"facts": item.facts, "engine": item.engine})})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--charts", type=int, default=60)
    ap.add_argument("--per-chart", type=int, default=2)
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--budget", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    from jyotish import envfile
    print(f"read from .env: {envfile.load(ROOT / '.env')}")                # names only, never a value
    from jyotish.costs import cost, price
    from jyotish.narrate import CONFIG, ModelChecker, make_backend
    rows = sample(a.charts, a.per_chart, a.seed)
    pc = price("zai-org/GLM-5.3-Flash", "api.deepinfra.com")
    usd = len(rows) * (4200 * pc[0] + 1800 * pc[1]) / 1e6
    print(f"{len(rows)} composed sentences from {a.charts} random charts; expected USD {usd:.3f} (budget {a.budget})")
    if usd > a.budget:
        print("over the budget: nothing checked")
        return 2
    checker = ModelChecker(make_backend(os.environ.get("JYOTISH_CHECKER_BACKEND"), "checker", CONFIG), CONFIG)
    model = checker.backend.describe().get("model")
    results = checker.check_many([(r["sentence"], json.dumps(r["data"], default=str, indent=1)) for r in rows])
    spent, refused, unchecked = 0.0, [], 0
    for r, (res, meta) in zip(rows, results):
        spent += cost(model, (meta or {}).get("usage") or {}, "api.deepinfra.com") or 0
        if (meta or {}).get("unchecked") or any(p.text in ("(unchecked)", "(no verdict)") for p in res.propositions):
            unchecked += 1
            continue
        if not all(p.supported for p in res.propositions):
            refused.append({"signature": r["signature"], "variant": r["variant"], "area": r["area"],
                            "sentence": r["sentence"],
                            "evidence": "; ".join(p.evidence for p in res.propositions if not p.supported)[:400]})
    checked = len(rows) - unchecked
    report = {"date": date.today().isoformat(), "checker": model, "charts": a.charts, "seed": a.seed,
              "sentences": len(rows), "checked": checked, "unchecked": unchecked, "supported": checked - len(refused),
              "share": round((checked - len(refused)) / checked, 4) if checked else None, "refused": refused,
              "usd": round(spent, 4)}
    out = a.out or ROOT / "docs" / f"composed_check_{date.today().isoformat()}.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"{report['supported']} of {checked} checked sentences supported ({report['share']}); {unchecked} unchecked; "
          f"USD {spent:.4f} -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
