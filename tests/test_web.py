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
    assert gaps and all(f.startswith(("place.", "chain:")) and "no claim was drafted" in t for f, t in gaps)
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
    # The nakshatra table, the special points and the dispositor chains as arrows, loops marked.
    assert page.locator("#nakshatras tbody tr").count() == 10
    assert "Tvashtar" in page.inner_text("#nakshatras") and "not yet checked" in page.inner_text("#nakshatras")
    assert "Nakshatra lagnesha" in page.inner_text("#nakshatra-points") and "22nd drekkana" in page.inner_text("#nakshatra-points")
    assert "88th pada" not in page.inner_text("#nakshatra-points") and "Sagittarius 1st drekkana" in page.inner_text("#nakshatra-points")
    sat = page.locator('#dispositors li[data-planet="Saturn"][data-kind="nakshatra"]')
    assert sat.inner_text().startswith("Saturn → Sun → Jupiter → Moon → Mars → Mercury")
    assert sat.locator(".in-loop").all_inner_texts() == ["Mars", "Mercury"]
    assert "Mars–Mercury loop" in page.inner_text('#dispositors .chain-kind[data-kind="nakshatra"]')



def test_other_placements_sit_with_the_astrologers_reading(page, curious_url):
    submit_reference(page, curious_url, depth="curious")
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    career = page.locator('section.area[data-area="career"]')
    other = career.locator("details.astrologer details.other-placements")
    assert other.count() == 1 and not other.locator("li").first.is_visible()      # inside the collapsed toggle
    career.locator("details.astrologer > summary").click()
    other.locator("summary").click()
    li = other.locator('li[data-rule="place.mercury_h10"]')
    assert li.is_visible() and "(draft effect, verse not yet read)" in li.inner_text()


def test_curious_paragraph_gap_opens_the_claims_on_the_site(page, curious_url):
    # The same reading with career's paragraph turned into a gap: the gap note sits above the
    # astrologer's reading, which is open; marriage's paragraph passed and keeps the toggle.
    submit_reference(page, curious_url, depth="curious")
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    reading = page.evaluate("fetch(location.pathname.replace('reading.html', 'readings/') + new URLSearchParams(location.search).get('id')).then(r => r.json())")["reading"]
    for a in reading["areas"]:
        if a["name"] == "career":
            a["paragraph"], a["paragraph_cites"] = None, []
            a["narration_gaps"] = [{"finding_id": "paragraph", "kind": "paragraph", "attempt": 3,
                                    "last_error": "unsupported: 'the house of career'"}] + a["narration_gaps"]
    page.route(f"{curious_url}/gap-reading.json", lambda route: route.fulfill(json=reading))
    page.goto(f"{curious_url}/reading.html?src=/gap-reading.json")
    page.wait_for_selector("#reading[data-state=done]")
    career = page.locator('section.area[data-area="career"]')
    assert career.locator("p.paragraph").count() == 0
    toggle = career.locator("details.astrologer")
    assert toggle.get_attribute("open") is not None and career.locator("li.claim").first.is_visible()
    order = career.evaluate("""el => [...el.querySelectorAll('.gap-lead, .gaps, details.astrologer')].map(e => e.className)""")
    assert order == ["gap-lead muted", "gaps", "astrologer"]                # the gap note above the claims, once
    assert career.locator('.gaps li[data-finding="paragraph"]').count() == 1
    marriage = page.locator('section.area[data-area="marriage"]')
    assert marriage.locator("details.astrologer").get_attribute("open") is None
    assert marriage.locator(".gap-lead").count() == 0


def test_fired_chip_counts_rules_and_drafts_apart(page, base_url):
    submit_reference(page, base_url)
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    chips = page.inner_text(".summary .chips")
    assert "Fired: 5 rules, 32 draft placements" in chips and "Rules stable / unstable: 5 / 0" in chips
    # The example reading predates the split and keeps its one chip.
    page.goto(f"{base_url}/reading.html?src=/examples/reference_reading.json")
    page.wait_for_selector("#reading[data-state=done]")
    assert "Fired rules stable / unstable: 5 / 0" in page.inner_text(".summary .chips")


# --- the guided review (review mode) and the judge page (blind mode) --------------------------

ENGINE_WORDS = __import__("re").compile(r"\b(votes?|tests?|famil(?:y|ies)|checker)\b", __import__("re").I)
CURIOUS_BODY = {"date": "2001-03-12", "time": "10:10:25", "tz": "Asia/Kolkata", "lat": 28.1989, "lon": 76.617,
                "node": "mean", "place": "Rewari, Haryana", "depth": "curious", "as_of": "2026-10-21",
                "question": "How will my career go, and when is the best time for a job change?"}


@pytest.fixture(scope="module")
def guided_url(tmp_path_factory):
    from jyotish.narrate import CheckResult, Proposition

    def checker(sentence, data):
        ok = "REJECTED" not in sentence
        return CheckResult(propositions=[Proposition(text=sentence if ok else "REJECTED", supported=ok, evidence="stub")])
    server, thread, url = _serve(tmp_path_factory.mktemp("guided") / "g.db", str(ROOT / "tests" / "fixtures" / "narration_curious.json"),
                                 reviewers={"tok-1": "judge-1", "tok-2": "judge-2", "tok-3": "judge-3"}, review_checker=checker)
    yield url
    server.should_exit = True
    thread.join(5)


def new_reading(url):
    import httpx
    rid = httpx.post(f"{url}/readings", json=CURIOUS_BODY).json()["id"]
    for _ in range(600):
        s = httpx.get(f"{url}/readings/{rid}").json()
        if s["status"] in ("done", "failed"):
            break
        time.sleep(0.1)
    assert s["status"] == "done"
    return rid, s["reading"]


def sign_in(pg, url, rid, token, blind=False):
    pg.goto(f"{url}/review/{rid}" + ("?mode=blind" if blind else ""))
    pg.wait_for_selector("#token-form:not([hidden])")
    pg.fill("#token", token)
    pg.click("#token-open")


def at(pg, key):
    pg.wait_for_selector(f'#review[data-step="{key}"]')


def plain_words(pg):
    # The page's own words, the chart's and the questions', never the engine's vocabulary. The
    # reading under review (.quoted) is the client's text and is left out.
    text = pg.evaluate("""() => { const m = document.querySelector('#guided').cloneNode(true);
        m.querySelectorAll('.quoted').forEach(e => e.remove()); return m.innerText; }""")
    assert not ENGINE_WORDS.search(text), ENGINE_WORDS.search(text).group(0)


def key(pg, k):
    # A choice saves at once: wait for the answer to reach the server.
    with pg.expect_response(lambda r: "/review/answer" in r.url and r.status == 200):
        pg.keyboard.press(k)


def progress(pg):
    bar = pg.locator("#guided-progress .bar")
    return int(bar.get_attribute("aria-valuenow")), int(bar.get_attribute("aria-valuemax"))


def test_guided_review_whole_flow(browser, guided_url):
    rid, reading = new_reading(guided_url)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    client = ctx.new_page()
    client.goto(f"{guided_url}/reading.html?id={rid}")
    client.wait_for_selector("#reading[data-state=done]")
    assert client.locator(".reviewed-by").count() == 0
    rev = ctx.new_page()
    sign_in(rev, guided_url, rid, "wrong")
    rev.wait_for_selector("#token-error:has-text('not accepted')")
    rev.fill("#token", "tok-1")
    rev.click("#token-open")
    at(rev, "intro:1")
    # The chart, fixed on the left: D1 and D9, the dasha tables with the current period.
    rev.wait_for_selector('#guided-chart svg [data-varga="D9"]')
    assert rev.locator('#guided-chart [data-varga="D1"]').count() == 1 and rev.locator('#guided-chart [data-varga="D10"]').count() == 0
    assert rev.inner_text("#guided-chart .current-period") == "Current period on 2026-10-21: Jupiter – Mercury – Mercury"
    assert rev.locator("#guided-chart tr.current").count() == 2                     # the maha and the antar
    assert rev.evaluate("getComputedStyle(document.querySelector('#guided-chart')).position") == "sticky"
    # Step 0: three screens, once per reviewer; the third says the note goes out in their name.
    for i in (1, 2, 3):
        at(rev, f"intro:{i}")
        plain_words(rev)
        assert progress(rev)[0] == i
        if i == 3:
            assert "under your name (judge-1)" in rev.inner_text("#guided-panel")
        rev.keyboard.press("Enter")
    # (1) The paragraph in full, then the question; 2 is Partly, and it saves at once.
    at(rev, "match:career")
    quote = rev.inner_text("#guided-panel blockquote.quoted")
    assert quote.startswith("In your chart the Sun and Mercury sit together") and "[" not in quote
    assert "Does this match your reading of the chart for career?" in rev.inner_text("#guided-panel")
    plain_words(rev)
    n0, total0 = progress(rev)
    key(rev, "2")
    rev.wait_for_selector('.choice[data-value="partly"][aria-pressed="true"]')
    assert progress(rev)[1] == total0 + 1                                            # "What is off?" joins
    # Beside the choices, in his own words; Ctrl+Enter sends them in the same answer row and goes on.
    assert rev.locator(".question-row #own-words").count() == 1
    rev.fill("#own-words", "The 10th lord carries the reading here.")
    rev.press("#own-words", "Control+Enter")
    # (2) What is off: several, and a line; Enter in the line goes on.
    at(rev, "off:career")
    assert progress(rev)[0] == n0 + 1
    plain_words(rev)
    key(rev, "1")
    key(rev, "3")
    rev.fill("#off-line", "The 10th lord's weakness is underplayed")
    rev.press("#off-line", "Enter")
    # (3) Each sentence a card: a rewrite shows the facts beside it and is read back.
    at(rev, "sentences:career")
    cards = rev.locator(".sentence-card")
    assert cards.count() == len(__import__("jyotish.narrate", fromlist=["sentences"]).sentences(reading["areas"][0]["paragraph"]))
    cards.first.locator(".open-rewrite").click()
    assert any("Budhaditya yoga, formed by Sun and Mercury" in f for f in rev.locator(".rewrite .facts li").all_inner_texts())
    rev.fill("#rw-text", "The Sun and Mercury join in the 10th, a strong pairing forming Budhaditya yoga and a raja yoga.")
    rev.click(".check-rewrite")
    rev.wait_for_selector('.reasons li[data-code="tier"]')
    assert rev.inner_text('.reasons li[data-code="tier"]') == "Leave out “strong”: how strong the area is, is stated separately."
    plain_words(rev)
    rev.fill("#rw-text", "REJECTED: the Sun and Mercury form Budhaditya yoga and a raja yoga in the 10th.")
    rev.click(".check-rewrite")
    rev.wait_for_selector('.reasons li[data-code="unsupported"]')
    assert rev.inner_text('.reasons li[data-code="unsupported"]').startswith("The chart facts beside it do not show this")
    rewrite = "The Sun and Mercury join in the 10th, forming Budhaditya yoga and a raja yoga."
    rev.fill("#rw-text", rewrite)
    rev.click(".check-rewrite")
    rev.wait_for_selector(".sentence-card.rewritten .accepted")
    rev.fill("#own-words", "The second and fourth sentences overlap.")
    rev.press("#own-words", "Control+Enter")
    # (4) The note; the tab closes with it half written, and nothing is lost.
    at(rev, "note:career")
    assert "the client sees this as the astrologer's own words" in rev.inner_text("#guided-panel").lower()
    note = "Seen often in my practice: recognition comes late."
    rev.fill("#note-text", note)
    rev.close()
    rev = ctx.new_page()
    sign_in(rev, guided_url, rid, "tok-1")
    at(rev, "note:career")                                                           # reopens where it was left
    assert rev.input_value("#note-text") == note
    rev.press("#note-text", "Control+Enter")
    # (5) The best period: 2 is Earlier, with a range. Words typed and not yet sent survive a reload.
    at(rev, "period:career")
    assert rev.inner_text(".engine-period") == "Oct 2029 to Jun 2032"
    plain_words(rev)
    rev.fill("#own-words", "Saturn's return pulls it forward.")
    rev.reload()
    at(rev, "period:career")
    assert rev.input_value("#own-words") == "Saturn's return pulls it forward."
    rev.locator("#guided-panel").focus()
    assert not rev.locator(".your-period").is_visible()
    rev.keyboard.press("2")                                  # Earlier: saved once the range is given
    assert rev.locator(".your-period").is_visible()
    rev.fill("#yours-from", "2027-10")
    rev.fill("#yours-to", "2028-12")
    rev.press("#yours-to", "Enter")
    # The other areas: Agree needs no "what is off", and neither has a period.
    for area in ("marriage", "longevity"):
        at(rev, f"match:{area}")
        key(rev, "1")
        rev.keyboard.press("Enter")
        at(rev, f"sentences:{area}")
        rev.keyboard.press("Enter")
        at(rev, f"note:{area}")
        rev.keyboard.press("Enter")
    # The last question, after the areas.
    at(rev, "whole")
    assert "Anything about the reading as a whole?" in rev.inner_text("#guided-panel")
    plain_words(rev)
    rev.fill("#whole-text", "Sound, but it underplays the 10th lord.")
    rev.press("#whole-text", "Control+Enter")
    at(rev, "summary")
    plain_words(rev)
    line = lambda step: rev.inner_text(f'.summary-line[data-step="{step}"]')
    assert "Partly" in line("match:career") and "“The 10th lord carries the reading here.”" in line("match:career")
    assert "A combination is missing; The timing; The 10th lord's weakness is underplayed" in line("off:career")
    assert "1" in line("sentences:career") and "“The second and fourth sentences overlap.”" in line("sentences:career")
    assert note in line("note:career")
    assert "Earlier: Oct 2027 to Dec 2028" in line("period:career") and "Saturn's return pulls it forward." in line("period:career")
    assert "Sound, but it underplays the 10th lord." in line("whole")
    assert rev.locator(".summary-line").count() == rev.locator(".summary-line .change").count()
    # Changing either the choice or the words: back to that question, then the summary again.
    rev.click('.summary-line[data-step="match:career"] .change')
    at(rev, "match:career")
    assert rev.input_value("#own-words") == "The 10th lord carries the reading here."
    key(rev, "3")
    rev.fill("#own-words", "On reflection the 10th lord decides it.")
    with rev.expect_response(lambda r: "/review/answer" in r.url and r.status == 200):
        rev.press("#own-words", "Control+Enter")
    rev.reload()
    at(rev, "summary")
    assert "Disagree" in line("match:career") and "“On reflection the 10th lord decides it.”" in line("match:career")
    assert rev.inner_text(".approve-line") == "The client will see: reviewed by judge-1"
    rev.click(".approve")
    at(rev, "done")
    assert "reviewed by judge-1" in rev.inner_text("#guided-panel")
    # The client's page: reviewed, the note in the reviewer's name, the rewritten sentence.
    client.reload()
    client.wait_for_selector("#reading[data-state=done]")
    assert "Reviewed by judge-1" in client.inner_text(".reviewed-by")
    c_career = client.locator('section.area[data-area="career"]')
    assert note in c_career.locator(".astrologer-note").inner_text()
    assert c_career.locator("p.paragraph").inner_text().startswith(rewrite[:-1])
    assert "underplayed" not in client.inner_text("#reading") and "Partly" not in client.inner_text("#reading")
    # Every answer is in the log, with its step, area, answer, reviewer and time.
    log = rev.evaluate(f"""fetch('/readings/{rid}/review', {{headers: {{Authorization: 'Bearer tok-1'}}}}).then(r => r.json())""")["history"]
    answers = [(h["step"], h["area"]) for h in log if h["action"] == "answer"]
    for step in [("intro", None), ("match", "career"), ("off", "career"), ("sentences", "career"), ("note", "career"),
                 ("period", "career"), ("match", "marriage"), ("note", "longevity")]:
        assert step in answers, step
    period = next(h for h in log if h["step"] == "period")
    assert period["answer"] == {"choice": "earlier", "from": "2027-10", "to": "2028-12"}
    assert period["reviewer"] == "judge-1" and period["at"] and period["mode"] == "review"
    assert period["comment"] == "Saturn's return pulls it forward."
    assert [h["comment"] for h in log if h["step"] == "match" and h["area"] == "career"][-1] == "On reflection the 10th lord decides it."
    assert next(h for h in log if h["step"] == "whole")["answer"] == {"text": "Sound, but it underplays the 10th lord."}
    client.reload()
    client.wait_for_selector("#reading[data-state=done]")
    shown = client.inner_text("#reading")
    assert not any(w in shown for w in ("10th lord carries", "Saturn's return pulls", "underplays the 10th lord"))
    ctx.close()


def test_judge_page_hides_the_reading_until_answered_from_the_chart(browser, guided_url):
    rid, reading = new_reading(guided_url)
    para = {a["name"]: a["paragraph"] for a in reading["areas"]}
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    rev = ctx.new_page()
    sign_in(rev, guided_url, rid, "tok-2", blind=True)
    at(rev, "intro:1")
    assert rev.title().startswith("Judge") and rev.locator(".blind-note").is_visible()
    for i in (1, 2, 3):
        rev.keyboard.press("Enter")
    at(rev, "blind_reading:career")
    plain_words(rev)
    # Not hidden but absent: the server has not sent the paragraph or the windows.
    content = rev.content()
    assert para["career"][:50] not in content and "Oct 2029" not in content and rev.locator(".quoted").count() == 0
    view = rev.evaluate(f"""fetch('/readings/{rid}/review?mode=blind', {{headers: {{Authorization: 'Bearer tok-2'}}}}).then(r => r.json())""")
    assert all(a.get("hidden") for a in view["reading"]["areas"]) and view["units"] == []
    key(rev, "1")
    rev.fill("#own-words", "Saturn in the 1st, the 10th lord, holds it up.")
    rev.press("#own-words", "Control+Enter")
    at(rev, "blind_period:career")
    rev.fill("#own-from", "2027-06")
    rev.fill("#own-to", "2028-12")
    rev.fill("#own-words", "Mercury's sub-period.")
    rev.press("#own-to", "Enter")
    # Now shown: the same flow as the review, with their own answers beside the engine's.
    at(rev, "match:career")
    assert rev.inner_text("blockquote.quoted").startswith("In your chart the Sun and Mercury")
    assert rev.inner_text(".own") == "Your reading from the chart alone: Promising"
    key(rev, "1")
    rev.keyboard.press("Enter")
    at(rev, "sentences:career")
    rev.keyboard.press("Enter")
    at(rev, "note:career")
    rev.keyboard.press("Enter")
    at(rev, "period:career")
    assert rev.inner_text(".engine-period") == "Oct 2029 to Jun 2032"
    assert rev.inner_text(".own") == "Your period from the chart alone: Jun 2027 to Dec 2028"
    key(rev, "1")
    rev.keyboard.press("Enter")
    # The next area is withheld again until answered; without windows it asks no period.
    at(rev, "blind_reading:marriage")
    assert para["marriage"][:50] not in rev.content()
    key(rev, "3")
    rev.keyboard.press("Enter")
    at(rev, "match:marriage")
    assert rev.inner_text("blockquote.quoted")[:40] == __import__("jyotish.review", fromlist=["plain"]).plain(para["marriage"])[:40]
    key(rev, "2")
    rev.keyboard.press("Enter")
    at(rev, "off:marriage")
    key(rev, "5")
    rev.keyboard.press("Enter")
    for step in ("sentences:marriage", "note:marriage"):
        at(rev, step)
        rev.keyboard.press("Enter")
    at(rev, "blind_reading:longevity")
    key(rev, "2")
    rev.keyboard.press("Enter")
    at(rev, "match:longevity")
    key(rev, "1")
    for step in ("match:longevity", "sentences:longevity", "note:longevity"):
        at(rev, step)
        rev.keyboard.press("Enter")
    at(rev, "whole")
    rev.fill("#whole-text", "Close to my own reading.")
    rev.press("#whole-text", "Control+Enter")
    at(rev, "summary")
    plain_words(rev)
    line = lambda step: rev.inner_text(f'.summary-line[data-step="{step}"]')
    assert "Promising" in line("blind_reading:career") and "“Saturn in the 1st, the 10th lord, holds it up.”" in line("blind_reading:career")
    assert "Jun 2027 to Dec 2028" in line("blind_period:career") and "Mercury's sub-period." in line("blind_period:career")
    assert "Difficult" in line("blind_reading:marriage")
    # Answers from the chart alone stand once the reading is shown: no way back to change them.
    assert rev.locator('.summary-line[data-step^="blind_"] .change').count() == 0
    assert rev.locator('.summary-line[data-step="match:career"] .change').count() == 1
    assert "Close to my own reading." in line("whole")
    rev.click(".approve")
    at(rev, "done")
    log = rev.evaluate(f"""fetch('/readings/{rid}/review?mode=blind', {{headers: {{Authorization: 'Bearer tok-2'}}}}).then(r => r.json())""")
    blind = [(a["step"], a["area"]) for a in log["answers"] if a["mode"] == "blind"]
    assert blind.index(("blind_reading", "career")) < blind.index(("blind_period", "career")) < blind.index(("match", "career"))
    assert ("blind_period", "marriage") not in blind
    rows = {(a["step"], a["area"]): a for a in log["answers"] if a["mode"] == "blind"}
    assert rows[("blind_reading", "career")]["comment"] == "Saturn in the 1st, the 10th lord, holds it up."
    assert rows[("blind_period", "career")]["comment"] == "Mercury's sub-period."
    assert rows[("whole", None)]["answer"] == {"text": "Close to my own reading."}
    ctx.close()


def test_guided_review_on_a_phone(browser, guided_url):
    rid, _ = new_reading(guided_url)
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    rev = ctx.new_page()
    sign_in(rev, guided_url, rid, "tok-3")
    at(rev, "intro:1")
    rev.wait_for_selector('#guided-chart svg [data-varga="D1"]')
    chart, panel = rev.locator("#guided-chart").bounding_box(), rev.locator("#guided-panel").bounding_box()
    assert chart["y"] + chart["height"] <= panel["y"]                                    # the chart above the questions
    assert rev.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    rev.locator(".next").tap()
    at(rev, "intro:2")
    ctx.close()


def test_every_label_comes_from_the_strings_file():
    import re
    strings = (ROOT / "web" / "js" / "strings.js").read_text()
    en = set(re.findall(r'^\s+"([\w.]+)":', strings, re.M))
    page = "".join((ROOT / "web" / "js" / f).read_text() for f in ("review-page.js", "compare-page.js"))
    used = set(re.findall(r'\bt\("([\w.]+)"', page))
    assert used and used <= en, used - en
    dynamic = {"intro.{}.heading": ("1", "2", "3"), "intro.{}.body": ("1", "2", "3"),
               "blind_reading.{}": ("promising", "mixed", "difficult"), "match.{}": ("agree", "partly", "disagree"),
               "off.{}": ("missing_combination", "weight", "timing", "wording", "other"),
               "period.{}": ("yes", "earlier", "later", "different"),
               "reason.{}": ("unsupported", "timing", "probability", "confidence", "death", "medical", "trade",
                             "third_party", "tier", "name", "other")}
    for pattern, values in dynamic.items():
        assert {pattern.format(v) for v in values} <= en, pattern
    from jyotish.review import OFF, OWN_READING, PERIOD
    assert set(OFF) == set(dynamic["off.{}"]) and set(PERIOD) == set(dynamic["period.{}"]) and set(OWN_READING) == set(dynamic["blind_reading.{}"])
    from jyotish.scoring import AREAS
    assert {f"areaname.{a}" for a in AREAS} <= en
    # The labels speak as an astrologer would.
    values = re.findall(r'^\s+"[\w.]+": "(.*)",$', strings, re.M)
    assert values and not any(ENGINE_WORDS.search(v) for v in values)


@pytest.fixture(scope="module")
def full_url(tmp_path_factory):
    server, thread, url = _serve(tmp_path_factory.mktemp("full") / "f.db",
                                 str(ROOT / "tests" / "fixtures" / "narration_full_handmade.json"))
    yield url
    server.should_exit = True
    thread.join(5)


def test_full_depth_reading_on_the_site(page, full_url):
    """Depth full on the site, from a hand-written fixture: the three sections of the analysis in
    order, a section that did not pass shown as not narrated, a fact's footnote with its value, and
    the [tradition:] sentence set apart from the checked text."""
    submit_reference(page, full_url, question="How will my career go?", depth="full")
    page.wait_for_selector("#reading[data-state=done]", timeout=60_000)
    career = page.locator('section.area[data-area="career"]')
    sections = career.locator(".analysis-section")
    assert sections.evaluate_all("els => els.map(e => e.dataset.section)") == ["assessment", "timing", "not_said"]
    assert career.locator('.analysis-section[data-section="assessment"] p').inner_text().startswith(
        "The strongest support is Mars in its own sign")
    marriage = page.locator('section.area[data-area="marriage"] .analysis-section[data-section="timing"]')
    assert "Not narrated within the checks" in marriage.inner_text()
    note = page.locator('#footnotes li[data-tag="fact:planets.Mars.dignity"]')
    assert note.inner_text().endswith('computed by the engine: "own".')
    assert "not semantically checked" in page.inner_text("#reading")          # no verdicts were recorded
    # The [tradition:] sentence is out of the checked section and set apart, with the engine's line.
    assert "Phaladeepika holds" not in career.locator('.analysis-section[data-section="assessment"]').inner_text()
    trad = career.locator("aside.traditions")
    assert trad.locator("h3").inner_text() == "From the texts, not computed on this chart"
    assert trad.locator("li").inner_text().startswith("Phaladeepika holds that a lord of the tenth")
    assert "(Phaladeepika 10; unverified)" in trad.locator("li").inner_text()
    assert "has not checked this" in trad.locator(".tradition-note").inner_text()



@pytest.fixture(scope="module")
def compare_url(tmp_path_factory):
    server, thread, url = _serve(tmp_path_factory.mktemp("cmp") / "c.db", EDITED, reviewers={"tok-1": "judge-1"})
    yield url
    server.should_exit = True
    thread.join(5)


def test_blind_comparison_page(page, compare_url):
    """/compare/{a}/{b}: the reviewer signs in, sees A and B with no settings, answers the one
    question, and only then sees which settings made which reading."""
    import requests
    body = dict(CURIOUS_BODY, depth="astrologer")
    ids = [requests.post(f"{compare_url}/readings", json=dict(body, writer_effort=e)).json()["id"]
           for e in ("medium", "max")]
    for rid in ids:
        for _ in range(600):
            if requests.get(f"{compare_url}/readings/{rid}").json()["status"] in ("done", "failed"):
                break
            time.sleep(0.1)
    page.goto(f"{compare_url}/compare/{ids[0]}/{ids[1]}")
    page.fill("#token", "tok-1")
    page.click("#token-open")
    page.wait_for_selector("#compare[data-state=blind]")
    for label in "AB":
        col = page.locator(f"#reading-{label}")
        assert col.locator(".compare-label").inner_text() == f"Reading {label}"
        assert col.locator("section.area").count() >= 1
        text = col.inner_text()
        assert "effort" not in text and "claude-" not in text and "attempt(s)" not in text
    assert page.locator("#compare-reveal").is_hidden()
    assert page.inner_text("#compare-heading") == "Which reading would you give the client, and why?"
    page.check("input[name=choice][value=A]")
    page.fill("#compare-why", "A says what the 10th lord does; B only lists the votes.")
    page.click("#compare-submit")
    page.wait_for_selector("#compare[data-state=revealed]")
    reveal = page.inner_text("#compare-reveal")
    assert "You chose reading A (judge-1)." in reveal and "A says what the 10th lord does" in reveal
    assert "effort medium" in reveal and "effort max" in reveal
    assert page.locator("#compare-form").is_hidden()
