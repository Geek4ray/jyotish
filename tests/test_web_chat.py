"""The conversation page (web/chat.html, SPEC Layer 8), driven by Playwright against the app with a replayed
narration (its turns written by conversation.OfflineTurnWriter): the birth data once and the check line; questions
answered in plain sentences with no footnote, engine word or verification mark on screen; the chart lit while an
answer is written and settled when done; the chips; the footer line; the off-limits reply; the conversation kept
across a reload; a phone's width with no sideways scroll."""

import re
from pathlib import Path

import pytest

playwright = pytest.importorskip("playwright.sync_api")

from jyotish.client import CLIENT_WORDS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EDITED = str(ROOT / "tests" / "fixtures" / "narration_career_edited.json")


@pytest.fixture(scope="module")
def url(tmp_path_factory):
    from test_web import _serve
    server, thread, base = _serve(tmp_path_factory.mktemp("chat") / "chat.db", EDITED)
    yield base
    server.should_exit = True
    thread.join(5)


@pytest.fixture(scope="module")
def page(url):
    with playwright.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:                       # browser not downloaded
            pytest.skip(f"Chromium for Playwright is not installed: {e}")
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        yield pg
        b.close()


def answered(page, k):
    """Wait for the k-th answer (1-based) to be done: the chart settles and the caret goes."""
    page.wait_for_function(f"document.querySelectorAll('.turn').length >= {k} && "
                           f"!document.querySelector('.turn:nth-child({k}) .writing') && "
                           "document.querySelector('#wheel').classList.contains('settled')", timeout=60000)
    return page.inner_text(f".turn:nth-child({k}) .answer")


def test_the_birth_data_once_then_the_check_line_and_the_chart(page, url):
    page.goto(f"{url}/chat.html")
    assert page.inner_text("#first-line").startswith("Where and when were you born?")
    page.fill("#date", "2001-03-12")
    page.fill("#time", "10:10:25")
    page.fill("#place", "Rewari")
    page.wait_for_selector("#place-list li")
    page.click("#place-list li")
    page.click("#draw")
    page.wait_for_selector("#check-line:not([hidden])")
    assert page.inner_text("#check-line") == "Taurus rising · Moon in Libra, Chitra"
    assert page.locator("#first").is_hidden() and page.locator("#wheel .body").count() == 9
    assert re.search(r"\?s=[0-9a-f]{32}$", page.url)
    assert page.inner_text("#trust") == "Checked against your chart; a real astrologer can review this."
    # Before the first question every chip names an area (review C1).
    assert page.locator("#chips button").all_inner_texts() == ["How is my career?", "What about marriage?",
                                                               "When does money come in?"]


def test_an_answer_is_plain_words_and_the_chart_lights_what_it_rests_on(page):
    page.fill("#message", "what are the challanges in my life")
    page.press("#message", "Enter")
    text = answered(page, 1)
    assert text.startswith("Let's start with the hard part")
    assert not re.search(r"\[(?:vote|rule|chain|fact|text):", text) and not CLIENT_WORDS.search(text)
    assert page.locator(".turn sup, .turn .footnote, .turn .verified, .turn .being-verified").count() == 0
    lit = page.eval_on_selector_all("#wheel .lit", "els => els.map(e => e.dataset.planet || 'H' + e.dataset.house)")
    assert "H9" in lit and "Sun" in lit                  # the father's house and its significator


def test_the_chips_carry_the_conversation_and_death_gets_the_fixed_reply(page):
    assert page.locator("#chips button").all_inner_texts() == ["and marriage?", "when?", "why?"]
    page.click("#chips button:has-text('and marriage?')")
    assert "marriage" in answered(page, 2)
    page.fill("#message", "will I die early?")
    page.press("#message", "Enter")
    assert answered(page, 3).startswith("Tatva does not answer questions about death")


def test_the_conversation_is_kept_across_a_reload(page):
    page.reload()
    page.wait_for_selector(".turn:nth-child(3)")
    assert page.locator(".turn").count() == 3 and page.locator("#first").is_hidden()
    assert page.inner_text(".turn:nth-child(1) .asked") == "what are the challanges in my life"


def test_a_phone_width_has_no_sideways_scroll(page):
    page.set_viewport_size({"width": 390, "height": 844})
    page.reload()
    page.wait_for_selector(".turn:nth-child(3)")
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.set_viewport_size({"width": 1280, "height": 900})
