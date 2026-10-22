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


def _serve(db, fixture, **app_kw):
    import uvicorn
    from jyotish.api import create_app
    app = create_app(f"sqlite:///{db}", model_fixture=fixture, **app_kw)
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


def submit_reference(page, url, question="How will my career go, and when is the best time for a job change?",
                     depth="astrologer"):
    page.goto(f"{url}/")
    page.fill("#date", "2001-03-12")
    page.fill("#time", "10:10:25")
    page.select_option("#tz", "Asia/Kolkata")
    page.fill("#place", "Rewari, Haryana")
    page.fill("#lat", "28.1989")
    page.fill("#lon", "76.617")
    page.select_option("#node", "mean")
    page.select_option("#depth", depth)
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
    assert "Ascendant (lagna) Taurus" in line and "Moon in Libra, Chitra nakshatra" in line and "04:40:25 UTC" in line
    assert "Rewari, Haryana (28.1989, 76.617)" in page.inner_text("#progress .header-line")
    assert page.locator("#failure").is_visible()


def test_place_autocomplete_fills_coordinates_and_timezone(page, base_url):
    page.goto(f"{base_url}/")
    page.fill("#place", "rewar")
    page.wait_for_selector("#place-list li")
    first = page.locator("#place-list li").first
    assert first.inner_text().startswith("Rewāri, Haryana, India")
    first.dispatch_event("mousedown")
    assert page.input_value("#place") == "Rewāri, Haryana, India"
    assert page.input_value("#lat") == "28.199" and page.input_value("#lon") == "76.6183"
    assert page.input_value("#tz") == "Asia/Kolkata"
    assert "Filled from GeoNames" in page.inner_text("#place-status")
    # A hand correction is kept, and said.
    page.fill("#lat", "28.1989")
    assert "corrected by hand" in page.inner_text("#place-status")
    assert page.input_value("#lat") == "28.1989"
    # Keyboard: arrow down and Enter choose too.
    page.fill("#place", "bombay")
    page.wait_for_selector("#place-list li")
    page.press("#place", "ArrowDown")
    page.press("#place", "Enter")
    assert page.input_value("#place") == "Mumbai, Maharashtra, India" and page.input_value("#tz") == "Asia/Kolkata"


def test_form_refuses_empty_and_null_island_coordinates(page, base_url):
    page.goto(f"{base_url}/")
    assert page.get_attribute("#lat", "placeholder") == "e.g. 28.1989"
    assert page.get_attribute("#lon", "placeholder") == "e.g. 76.6170"
    assert page.input_value("#node") == "mean"                                       # the form's default
    assert page.eval_on_selector_all("#node option", "els => els.map(e => e.value)") == ["mean", "true"]
    posts = []
    page.on("request", lambda r: posts.append(r.url) if r.method == "POST" else None)
    page.fill("#date", "2001-03-12")
    page.fill("#time", "10:10:25")
    page.fill("#question", "When is the best time for a job change?")
    page.click("button[type=submit]")
    assert "Enter the birthplace's latitude and longitude" in page.inner_text("#form-error")
    page.fill("#lat", "0")
    page.fill("#lon", "0")
    page.click("button[type=submit]")
    assert "Gulf of Guinea" in page.inner_text("#form-error")
    page.fill("#lat", "95")
    page.fill("#lon", "76.6")
    page.click("button[type=submit]")
    assert "Latitude must be between -90 and 90" in page.inner_text("#form-error")
    assert posts == [] and page.url.endswith("/")


def test_check_line_after_chart_names_place_and_coordinates(page, servers):
    submit_reference(page, servers["fails"])
    page.wait_for_selector("#reading[data-state=failed]", timeout=60_000)
    line = page.inner_text(".chart-line")
    assert line.startswith("Rewari, Haryana, at 28.1989° N, 76.6170° E (timezone Asia/Kolkata).")
    assert "Ascendant (lagna) Taurus; Moon in Libra, Chitra nakshatra." in line


def test_footer_carries_the_geonames_attribution(page, base_url):
    for path in ("/", "/reading.html?src=/examples/reference_reading.json"):
        page.goto(f"{base_url}{path}")
        footer = page.inner_text("#site-footer")
        assert "GeoNames" in footer and "CC BY 4.0" in footer
        assert page.get_attribute("#site-footer a[href*='creativecommons.org/licenses/by/4.0']", "href")


@pytest.fixture(scope="module")
def curious_url(tmp_path_factory):
    server, thread, url = _serve(tmp_path_factory.mktemp("curious") / "c.db",
                                 str(ROOT / "tests" / "fixtures" / "narration_curious.json"))
    yield url
    server.should_exit = True
    thread.join(5)


def test_curious_reading_on_the_site(page, curious_url):
    page.goto(f"{curious_url}/")
    assert page.input_value("#depth") == "curious"                        # the form's default
    submit_reference(page, curious_url, depth="curious")
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    career = page.locator('section.area[data-area="career"]')
    assert career.locator("p.paragraph").inner_text().startswith("In your chart the Sun and Mercury sit together")
    # The recording predates the placement library: its placement findings are listed as gaps,
    # every one "no claim was drafted"; nothing else is missing and every sentence was checked.
    gaps = page.eval_on_selector_all(".gaps li", "els => els.map(e => [e.dataset.finding, e.textContent])")
    assert gaps and all(f.startswith("place.") and "no claim was drafted" in t for f, t in gaps)
    assert "Offline replay" not in page.inner_text("#reading")
    assert page.locator('section.area[data-area="longevity"] p.paragraph').count() == 1
    toggle = career.locator("details.astrologer")
    assert toggle.count() == 1 and toggle.get_attribute("open") is None    # the claims are one click away
    assert toggle.locator(":scope > summary").inner_text() == "Show the astrologer's reading"
    assert not career.locator("li.claim").first.is_visible()
    toggle.locator(":scope > summary").click()
    assert career.locator("li.claim").first.is_visible() and toggle.locator("details.learner").count() >= 1
    assert page.inner_text(".summary .timing-note") == ("These are periods the engine scores as favourable for career; "
                                                         "it does not predict when you will act.")
    # Every tag, the paragraphs' included, is a footnote.
    footnotes = set(page.eval_on_selector_all("#footnotes li", "els => els.map(e => e.dataset.tag)"))
    reading = page.evaluate("fetch(location.pathname.replace('reading.html', 'readings/') + new URLSearchParams(location.search).get('id')).then(r => r.json())")
    tags = set(reading["reading"]["summary"]["cites"])
    for a in reading["reading"]["areas"]:
        tags |= set(a["paragraph_cites"]) | {t for c in a["claims"] for t in c["cites"]}
    assert footnotes == tags


def test_chart_page_and_the_link_from_the_reading(page, base_url):
    submit_reference(page, base_url)
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    link = page.locator(".chart-link a")
    assert link.is_visible() and "/chart.html?chart=" in link.get_attribute("href")
    link.click()
    page.wait_for_selector("#chart[data-state=done]")
    assert page.locator("#chart-svg svg g[data-varga]").count() == 3
    assert page.locator('#chart-svg text[data-planet="Venus"]').first.text_content() == "Ve 23° R"   # SVG text
    assert page.inner_text(".current-period") == "Jupiter – Mercury – Mercury"
    assert page.locator(".dasha-tree li[data-current]").count() == 3                 # maha, antar, pratyantar
    assert page.locator("#shadbala tbody tr").count() == 7 and page.locator("#bhava-bala tbody tr").count() == 12
    assert page.locator("#ashtakavarga tbody tr").count() == 8                       # seven BAV rows and SAV
    assert page.locator("#planets tbody tr").count() == 10



@pytest.fixture(scope="module")
def review_url(tmp_path_factory):
    from jyotish.narrate import CheckResult, Proposition

    def checker(sentence, data):
        ok = "REJECTED" not in sentence
        return CheckResult(propositions=[Proposition(text=sentence, supported=ok, evidence="stub")])
    server, thread, url = _serve(tmp_path_factory.mktemp("review") / "r.db", EDITED,
                                 reviewers={"web-token": "judge-1"}, review_checker=checker)
    yield url
    server.should_exit = True
    thread.join(5)


def test_review_page_edit_note_and_approve(browser, review_url):
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    client = ctx.new_page()
    submit_reference(client, review_url)
    client.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    rid = client.url.split("id=")[1]
    assert client.locator(".reviewed-by").count() == 0 and client.locator(".astrologer-note").count() == 0
    rev = ctx.new_page()
    rev.goto(f"{review_url}/review/{rid}")
    rev.wait_for_selector("#token-form:not([hidden])")
    rev.fill("#token", "wrong")
    rev.click("#token-form button[type=submit]")
    rev.wait_for_selector("#token-error:has-text('not accepted')")
    rev.fill("#token", "web-token")
    rev.click("#token-form button[type=submit]")
    rev.wait_for_selector("#review[data-state=draft]")
    unit = rev.locator('.review-unit[data-target="claim:career:vote:career.house"]')
    # A refused edit says why and changes nothing.
    unit.locator("textarea").fill("The house vote is for career.")
    unit.locator(".save").click()
    rev.wait_for_selector('.review-unit[data-target="claim:career:vote:career.house"] .result.bad')
    assert "claim without a tag" in unit.locator(".result").inner_text()
    # An accepted one replaces the sentence.
    new = "The house vote is for career, though the 10th house is the lowest in strength [vote:career.house]."
    unit.locator("textarea").fill(new)
    unit.locator(".save").click()
    rev.wait_for_selector('.review-unit[data-target="claim:career:vote:career.house"] .result.ok')
    note = rev.locator('.note[data-area="career"]')
    note.locator("textarea").fill("Seen often in my practice: recognition comes late.")
    note.locator(".save-note").click()
    rev.wait_for_function("document.querySelector('#history').textContent.includes('note')")
    rev.click("#approve")
    rev.wait_for_selector("#review[data-state=reviewed]")
    assert "approve" in rev.inner_text("#history") and "accepted" in rev.inner_text("#history")
    client.reload()
    client.wait_for_selector("#reading[data-state=done]")
    assert "Reviewed by judge-1" in client.inner_text(".reviewed-by")
    aside = client.locator('section.area[data-area="career"] .astrologer-note')
    assert "Seen often in my practice" in aside.inner_text() and "not checked by the engine" in aside.inner_text()
    claim = client.locator('section.area[data-area="career"] li.claim[data-finding="vote:career.house"] .claim-text')
    assert claim.inner_text().startswith("The house vote is for career, though the 10th house is the lowest in strength")
    # The note is set apart from the checked text: not inside the claims list.
    assert client.locator('section.area[data-area="career"] ol.claims .astrologer-note').count() == 0
    ctx.close()


def test_other_placements_sit_with_the_astrologers_reading(page, curious_url):
    submit_reference(page, curious_url, depth="curious")
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    career = page.locator('section.area[data-area="career"]')
    other = career.locator("details.astrologer details.other-placements")
    assert other.count() == 1 and not other.locator("li").first.is_visible()      # inside the collapsed toggle
    career.locator("details.astrologer > summary").click()
    other.locator("summary").click()
    assert other.locator('li[data-rule="place.mercury_h10"]').is_visible()
