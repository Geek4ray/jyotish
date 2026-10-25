"""Suite-wide: the chart cache (jyotish.cache) and the candidate rules (service.record_candidates)
write to temporary files, never to the user's ~/.cache or the repository's data/."""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _chart_cache_dir(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    mp.setenv("JYOTISH_CACHE_DIR", str(tmp_path_factory.mktemp("chart-cache")))
    # Candidate rules (the [tradition:] sentences of a live reading) go to a temporary file too.
    mp.setenv("JYOTISH_CANDIDATE_RULES", str(tmp_path_factory.mktemp("candidates") / "candidate_rules.jsonl"))
    yield
    mp.undo()


class EchoClient:
    """The client's layer offline (jyotish.client), for tests that are not about it: per area one
    plain sentence carrying the tags of the first accepted sentence that cites only facts and votes,
    and a summary carrying the first area's. A test about the client's layer passes its own drafter."""

    def __init__(self):
        self.calls = []
        self.last_meta = None

    def __call__(self, system, user, errors):
        import json
        import re
        from jyotish.client import ClientDraft
        from jyotish.narrate import TAG, sentences
        self.calls.append({"system": system, "user": user, "errors": list(errors)})
        self.last_meta = {"kind": "client", "usage": {"input_tokens": 100, "output_tokens": 50}, "seconds": 0.1}
        areas = json.loads(user)["areas"]
        out = []
        for name, a in areas.items():
            texts = a["claims"] + [a[k] for k in ("assessment", "timing", "not_decided", "not_computed") if a.get(k)]
            tags = next((t for x in texts for s in sentences(x) if (t := TAG.findall(s))
                         and all(k in ("fact", "vote") for k, _ in t)), None)
            para = (f"In plain words, this part of the reading rests on the chart's own figures "
                    f"{' '.join(f'[{k}:{v}]' for k, v in tags)}.") if tags else None
            timing = next((t for s in sentences(a.get("timing") or "") if (t := TAG.findall(s))
                           and all(k in ("fact", "vote") for k, _ in t)), None)
            when = (f"In plain words, the timing of this part rests on the chart's own figures "
                    f"{' '.join(f'[{k}:{v}]' for k, v in timing)}.") if timing else None
            out.append({"name": name, "paragraph": para, "when": when})
        first = next((x["paragraph"] for x in out if x["paragraph"]), None)
        summary = re.sub(r"^In plain words, this part", "In plain words, the reading", first) if first else ""
        return ClientDraft(summary=summary, areas=out)


@pytest.fixture(autouse=True)
def _offline_client_layer(monkeypatch):
    import jyotish.narrate
    monkeypatch.setattr(jyotish.narrate, "default_client_drafter", lambda *a, **k: EchoClient())
