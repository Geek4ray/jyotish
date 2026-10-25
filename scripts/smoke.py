"""The deployed service, end to end, as a reviewer meets it (CI's image job; docs/deploy.md).

    python scripts/smoke.py --url http://127.0.0.1:8001 --token=<a reviewer token>

(--token= with the sign: a token may begin with "-", which argparse would otherwise read as an option.)

Against a running service started with JYOTISH_MODEL_FIXTURE (a recorded narration replayed, no model
called): /health reports a migrated database and the replay; a reading of the reference chart is
posted and runs to done; its review page opens in Chromium (Playwright), takes the token, walks the
three intro screens and answers the first question, and the server holds the answer. Exits 0 when
all of that held, 1 with what did not."""

from __future__ import annotations

import argparse
import sys
import time

import httpx

BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": 28.1989, "lon": 76.617,
        "node": "mean", "place": "Rewari, Haryana", "question": "How will my career go, and when is the best time for a job change?",
        "as_of": "2026-10-21", "depth": "astrologer"}       # the recording is an astrologer-depth career draft


def check(ok: bool, what: str) -> None:
    print(("ok    " if ok else "FAIL  ") + what, flush=True)
    if not ok:
        raise SystemExit(1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--url", required=True)
    ap.add_argument("--token", required=True, help="a reviewer token (jyotish reviewer add <name>)")
    ap.add_argument("--timeout", type=float, default=300)
    args = ap.parse_args(argv)
    url = args.url.rstrip("/")

    h = httpx.get(f"{url}/health", timeout=10).json()
    check(h["status"] == "ok" and h["database"]["revision"] == h["database"]["head"], f"/health: {h['database']}")
    check(h["narration"] == "fixture", "/health: narration replays a recording")

    rid = httpx.post(f"{url}/readings", json=BODY, timeout=10).json()["id"]
    t = time.monotonic()
    while True:
        r = httpx.get(f"{url}/readings/{rid}", timeout=10).json()
        if r["status"] in ("done", "failed") or time.monotonic() - t > args.timeout:
            break
        time.sleep(1)
    check(r["status"] == "done", f"reading {rid}: {r['status']} ({r.get('error')})")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(f"{url}/review/{rid}")
        page.wait_for_selector("#token-form:not([hidden])")
        page.fill("#token", args.token)
        page.click("#token-open")
        for i in (1, 2, 3):
            page.wait_for_selector(f'#review[data-step="intro:{i}"]', timeout=30_000)
            page.keyboard.press("Enter")
        page.wait_for_selector('#review[data-step="match:career"]', timeout=30_000)
        check("career" in page.inner_text("#guided-panel").lower(), "the review page asks about career")
        with page.expect_response(lambda x: "/review/answer" in x.url and x.status == 200):
            page.keyboard.press("1")                                  # "agree"
        browser.close()

    view = httpx.get(f"{url}/readings/{rid}/review", headers={"Authorization": f"Bearer {args.token}"}, timeout=10).json()
    answers = [(a["step"], a["area"], a["answer"]) for a in view["answers"]]
    check(("match", "career", "agree") in answers, f"the server holds the answer: {answers}")
    print("smoke test passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
