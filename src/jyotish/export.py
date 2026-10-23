"""The review step's judgement data as preference files (`jyotish export-reviews`).

    data/preferences/rewrites.jsonl     one row per accepted rewrite: the reading, the chart hash, the
                                        area and step, the sentence before and after (with and without
                                        its tags), the chart facts shown beside it (stored with the edit;
                                        recomputed, and said so, for a row from before that), the
                                        reviewer, the time
    data/preferences/judgements.jsonl   one row per (reading, reviewer, mode, area) with the latest answer
                                        to each question (agree / partly / disagree, what is off, the best
                                        period, in blind mode the reviewer's own reading and period), the
                                        reviewer's own words on each, the note; and one row per (reading,
                                        reviewer, mode) with area null for the reading as a whole; and one
                                        row per blind comparison (kind "compare": the two readings, which
                                        was shown as A, the choice, the reviewer's why, each one's settings)

These are judgements, not outcomes: what a practising astrologer thought of a reading, never what
happened to its client. They live in data/preferences/, apart from any outcome log (SPEC Layer 6b:
the two never touch), and the first line of each file says so. Both files are client data and are
gitignored. Birth data is left out unless `with_birth_data`; the chart hash is kept, and it is the
key of a stored chart computed from birth data, so it identifies a chart to anyone holding the
database: treat the files as the database is treated."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

OUT = Path("data") / "preferences"
HEADER = ("These are judgements, not outcomes: a reviewing astrologer's answers on engine readings (SPEC "
          "Layer 6b). They say what the reviewer thought, never what happened to the client, and are kept apart "
          "from any outcome log. Client data: not for the repository.")
STEP_FIELDS = ("match", "off", "sentences", "note", "period", "blind_reading", "blind_period")


def _header(kind: str, with_birth: bool) -> dict:
    return {"kind": "header", "file": kind, "note": HEADER, "exported_at": datetime.now(timezone.utc).isoformat(),
            "with_birth_data": with_birth}


def export_reviews(database_url: str, out_dir: Path | str = OUT, with_birth_data: bool = False) -> dict[str, int]:
    """Write the two files; returns the number of rows in each (headers not counted)."""
    from sqlalchemy.orm import sessionmaker

    from .db import ChartRow, ReadingRow, ReviewRow, migrate
    from .models import Chart
    from .review import facts, plain, sentence_facts, units
    from .narrate import Reading

    Session = sessionmaker(migrate(database_url))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rewrites, judgements = [], []
    with Session() as s:
        readings = {r.id: r for r in s.query(ReadingRow).all()}
        charts = {c.id: c for c in s.query(ChartRow).all()}
        fact_cache: dict = {}

        def birth(chart_id):
            c = charts.get(chart_id)
            return c.birth if (with_birth_data and c is not None) else None

        def shown_facts(row, before: str, area: str) -> list[str]:
            reading = readings.get(row.reading_id)
            chart = charts.get(row.chart_id)
            if reading is None or chart is None or reading.document is None:
                return []
            names = [a["name"] for a in reading.document["areas"]]
            key = (row.chart_id, tuple(names), reading.document["as_of"])
            if key not in fact_cache:
                fact_cache[key] = facts(Chart.model_validate(chart.document), names,
                                        date.fromisoformat(reading.document["as_of"]))
            return sentence_facts(before, fact_cache[key].get(area, []))

        for row in s.query(ReviewRow).filter_by(action="edit", accepted=True).order_by(ReviewRow.id):
            kind, _, rest = (row.target or "").partition(":")
            area = row.area or (rest.split(":", 1)[0] if kind in ("claim", "paragraph") else None)
            x = {"reading_id": row.reading_id, "chart_hash": row.chart_id, "area": area,
                 "step": "sentences" if row.mode in ("review", "blind") else "edit", "target": row.target,
                 "mode": row.mode, "original": row.before, "rewritten": row.after,
                 "original_plain": plain(row.before or ""), "rewritten_plain": plain(row.after or ""),
                 # The facts the page showed, stored with the edit since 2026-10-23; an older row's are
                 # recomputed with the engine of today, and the row says which it got.
                 "facts_shown": row.facts if row.facts is not None else (shown_facts(row, row.before or "", area) if area else []),
                 "facts_shown_source": "stored at review" if row.facts is not None else "recomputed with the current engine",
                 "reviewer": row.reviewer_id, "at": row.created_at.isoformat()}
            if with_birth_data:
                x["birth"] = birth(row.chart_id)
            rewrites.append(x)

        groups: dict[tuple, dict[str, Any]] = {}
        for row in s.query(ReviewRow).filter_by(action="answer").order_by(ReviewRow.id):
            if row.step == "intro":
                continue
            key = (row.reading_id, row.reviewer_id, row.mode or "review", row.area)
            g = groups.setdefault(key, {"reading_id": row.reading_id, "chart_hash": row.chart_id,
                                        "reviewer": row.reviewer_id, "mode": row.mode or "review", "area": row.area,
                                        "answers": {}, "comments": {}, "first_at": row.created_at.isoformat()})
            g["answers"][row.step] = row.answer                    # the latest answer to each question
            if row.comment:
                g["comments"][row.step] = row.comment
            elif row.step in g["comments"]:
                del g["comments"][row.step]
            g["last_at"] = row.created_at.isoformat()
        for g in groups.values():
            a = g.pop("answers")
            if g["area"] is None:
                g |= {"whole_reading": (a.get("whole") or {}).get("text")}
            else:
                off = a.get("off")
                g |= {"verdict": a.get("match"), "what_is_off": off.get("reasons") if off else None,
                      "what_is_off_line": off.get("line") if off else None, "best_period": a.get("period"),
                      "own_reading": a.get("blind_reading"), "own_period": a.get("blind_period"),
                      "note": (a.get("note") or {}).get("text"),
                      "sentences": (a.get("sentences") or {}).get("decisions")}
            if with_birth_data:
                g["birth"] = birth(g["chart_hash"])
            judgements.append(g)

        for row in s.query(ReviewRow).filter_by(action="compare").order_by(ReviewRow.id):
            a = row.answer or {}
            x = {"kind": "compare", "readings": sorted((a.get("shown_as") or {}).values()), "chart_hash": row.chart_id,
                 "reviewer": row.reviewer_id, "shown_as": a.get("shown_as"), "choice": a.get("choice"),
                 "chosen_reading": a.get("chosen"), "why": row.comment, "settings": a.get("settings"),
                 "at": row.created_at.isoformat()}
            if with_birth_data:
                x["birth"] = birth(row.chart_id)
            judgements.append(x)

    for name, rows in (("rewrites.jsonl", rewrites), ("judgements.jsonl", judgements)):
        lines = [_header(name, with_birth_data)] + rows
        (out / name).write_text("".join(json.dumps(r, ensure_ascii=False, default=str) + "\n" for r in lines))
    return {"rewrites": len(rewrites), "judgements": len(judgements)}
