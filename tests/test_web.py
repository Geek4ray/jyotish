"""The website (web/), headless: Playwright drives Chromium against the FastAPI app, which
serves web/ at / and examples/ at /examples. Skipped when Playwright or its browser is not
installed (.venv/bin/pip install playwright && .venv/bin/playwright install chromium)."""

import json
import socket
import threading
import time
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "examples" / "reference_reading.json").read_text())
EDITED = str(ROOT / "tests" / "fixtures" / "narration_career_edited.json")


def _serve(db, fixture):
    import uvicorn
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{db}", model_fixture=fixture)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(200):
        if server.started:
            break
        time.sleep(0.05)
    return server, thread, f"http://127.0.0.1:{port}"


@pytest.fixture(scope="module")
def servers(tmp_path_factory):
    """Three apps: the edited fixture (a complete reading), the frozen first recording (a
    reading with narration gaps), and a fixture that does not exist (a job that fails after
    the chart)."""
    d = tmp_path_factory.mktemp("web")
    out = {name: _serve(d / f"{name}.db", fixture) for name, fixture in
           (("ok", EDITED), ("gaps", str(ROOT / "tests" / "fixtures" / "narration_career_opus55_r1.json")),
            ("fails", str(d / "missing.json")))}
    yield {name: url for name, (_, _, url) in out.items()}
    for server, thread, _ in out.values():
        server.should_exit = True
        thread.join(5)


@pytest.fixture(scope="module")
def base_url(servers):
    return servers["ok"]


def submit_reference(page, url, question="How will my career go, and when is the best time for a job change?"):
    page.goto(f"{url}/")
    page.fill("#date", "2001-03-12")
    page.fill("#time", "10:10:25")
    page.select_option("#tz", "Asia/Kolkata")
    page.fill("#place", "Rewari, Haryana")
    page.fill("#lat", "28.1989")
    page.fill("#lon", "76.617")
    page.select_option("#node", "mean")
    page.fill("#question", question)
    page.click("button[type=submit]")
    page.wait_for_url("**/reading.html?id=*")


@pytest.fixture(scope="module")
def browser():
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:                       # browser not downloaded
            pytest.skip(f"Chromium for Playwright is not installed: {e}")
        yield b
        b.close()


@pytest.fixture
def page(browser):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    yield pg
    ctx.close()
    assert not errors, errors


def open_reading(page, base_url, screen="reading"):
    page.goto(f"{base_url}/{screen}.html?src=/examples/reference_reading.json")
    page.wait_for_selector("#reading[data-state=done]")


def json_tags(reading):
    tags = set(reading["summary"]["cites"])
    for a in reading["areas"]:
        for c in a["claims"]:
            tags |= set(c["cites"])
    return tags


def test_every_tag_in_the_json_is_a_footnote(page, base_url):
    open_reading(page, base_url)
    footnotes = page.eval_on_selector_all("#footnotes li", "els => els.map(e => e.dataset.tag)")
    assert set(footnotes) == json_tags(EXAMPLE) and len(footnotes) == len(set(footnotes))
    # Every reference in the text points at the footnote of its own tag, and no raw tag is left.
    refs = page.eval_on_selector_all("a.fn-ref", "els => els.map(e => [e.dataset.tag, e.getAttribute('href')])")
    numbered = {t: f"#fn-{i}" for i, t in enumerate(footnotes, 1)}
    assert refs and all(numbered[t] == href for t, href in refs)
    body = page.inner_text("#reading")
    assert "[rule:" not in body and "[vote:" not in body and "[text:" not in body


def test_engine_fields_verbatim(page, base_url):
    open_reading(page, base_url)
    s = EXAMPLE["summary"]
    assert page.inner_text(".timing-text") == s["timing_line"]
    chips = page.inner_text(".summary .chips")
    for value in (s["driver_planet"], s["current_period"], ", ".join(s["top_areas"]), ", ".join(s["abstained_areas"])):
        assert value in chips
    for a in EXAMPLE["areas"]:
        card = page.locator(f'section.area[data-area="{a["name"]}"]')
        assert card.locator(".tier").inner_text() == a["tier"]                        # tier word verbatim
        st = a["stability"]
        assert card.locator(".stability").inner_text() == \
            f'time {st["time"]:.2f} · ayanamsa {st["ayanamsa"]:.2f} · house {st["house"]:.2f} ({st["label"]})'
        assert a["probability"] is None and card.locator(".probability").inner_text() == "not calibrated"
        assert card.locator("li.claim").count() == len(a["claims"])
        for p in a["polarity"]:
            assert p in card.locator(".polarity").inner_text()
        for sc in a["school_conflicts"]:
            assert "School conflict" in card.inner_text()
    assert page.locator("#depends").is_visible()                                       # always shown
    assert "Depends on exact birth time" in page.inner_text("#depends")


def test_learner_panels_collapsed_and_from_the_json(page, base_url):
    open_reading(page, base_url)
    n = sum(len(a["claims"]) for a in EXAMPLE["areas"])
    assert page.locator("details.learner").count() == n
    assert page.eval_on_selector_all("details.learner", "els => els.filter(e => e.open).length") == 0
    ruchaka = page.locator('li.claim[data-finding="yoga.ruchaka@lagna+sun"] details.learner')
    ruchaka.locator("summary").click()
    text = ruchaka.inner_text()
    assert "marana_karaka_sthana" in text and "Sudarshana: the fire from the Sun" in text
    kp = page.locator('li.claim[data-finding="vote:marriage.kp"] details.learner')
    kp.locator("summary").click()
    assert "star lord" in kp.inner_text() and "matter houses" in kp.inner_text()


def test_timing_screen_windows_and_avoid(page, base_url):
    open_reading(page, base_url, "timing")
    career = next(a for a in EXAMPLE["areas"] if a["name"] == "career")
    rows = page.locator('section[data-area="career"] table.windows tbody tr')
    assert rows.count() == len(career["windows"]) + 1
    avoid = page.locator('section[data-area="career"] tr[data-window="avoid"]').inner_text()
    w = career["avoid_window"]
    assert w["start"] in avoid and w["end"] in avoid and str(w["q"]) in avoid and str(w["t"]) in avoid
    first = rows.nth(0).inner_text()
    sp = career["windows"][0]["strongest_piece"]
    assert career["windows"][0]["start"] in first and sp["start"] in first and sp["end"] in first


def test_phone_layout(browser, base_url):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    pg = ctx.new_page()
    pg.goto(f"{base_url}/reading.html?src=/examples/reference_reading.json")
    pg.wait_for_selector("#reading[data-state=done]")
    assert pg.evaluate("document.documentElement.scrollWidth <= innerWidth")             # no sideways scroll
    assert pg.locator("#tabbar").is_visible() and not pg.locator(".site-nav").is_visible()
    assert pg.locator("#tabbar a").all_inner_texts() == ["Home", "Reading", "When"]
    ctx.close()


def test_home_form_runs_a_reading_through_the_api(page, base_url):
    page.goto(f"{base_url}/")
    assert "What the engine will not claim" in page.inner_text("#honest")
    submit_reference(page, base_url)
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    assert page.inner_text(".question") == "How will my career go, and when is the best time for a job change?"
    assert "Rewari, Haryana (28.1989, 76.617)" in page.inner_text(".header-line")
    assert page.locator("section.area").count() == 3 and page.locator(".timing-text").is_visible()



@pytest.mark.parametrize("zone,expected", [("America/New_York", "America/New_York"), ("Asia/Kolkata", "Asia/Kolkata"),
                                           ("Europe/Berlin", "Europe/Berlin")])
def test_timezone_defaults_to_the_browsers_with_kolkata_first(browser, base_url, zone, expected):
    ctx = browser.new_context(timezone_id=zone)
    pg = ctx.new_page()
    pg.goto(f"{base_url}/")
    options = pg.eval_on_selector_all("#tz option", "els => els.map(e => e.value)")
    assert options[0] == "Asia/Kolkata" and len(options) > 100 and "Asia/Calcutta" not in options
    assert pg.input_value("#tz") == expected
    ctx.close()


def test_reading_with_gaps_shows_them_and_the_engine_summary(page, servers):
    submit_reference(page, servers["gaps"])
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    assert page.locator("#incomplete").is_visible()
    assert page.locator('.summary[data-source="engine"] .engine-summary').is_visible()
    assert page.inner_text(".summary-text").startswith("Career: tier moderate")
    gaps = page.locator('section.area[data-area="career"] .gaps')
    assert "Not narrated within the checks" in gaps.inner_text()
    assert gaps.locator('li[data-finding="yoga.ruchaka@lagna+sun"]').count() == 1
    assert page.locator('section.area[data-area="career"] li.claim').count() >= 1     # the claims that passed


def test_failed_job_still_shows_the_chart(page, servers):
    submit_reference(page, servers["fails"])
    page.wait_for_selector("#reading[data-state=failed]", timeout=60_000)
    line = page.inner_text(".chart-line")
    assert "Lagna Taurus" in line and "Moon in Libra, Chitra nakshatra" in line and "2001-03-12T04:40:25+00:00" in line
    assert "Rewari, Haryana (28.1989, 76.617)" in page.inner_text("#progress .header-line")
    assert page.locator("#failure").is_visible()
