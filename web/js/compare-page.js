// The blind comparison (SPEC Layer 7, depth full; scripts/compare_readings.py): two readings of the
// same chart and question, shown as A and B with their settings withheld by the server, and one
// question, "which reading would you give the client, and why". The answer is logged with the
// reviewer (POST /compare/{a}/{b}/answer); only then does the server reveal which settings made
// which reading. An answer is final: once the settings are seen, the choice is no longer blind.
// The server decides which reading is A for this reviewer, so the URL's order says nothing.
// Every label comes from strings.js.
import { chrome } from "./chrome.js";
import { esc, renderReading } from "./render.js";
import { pickLanguage, t } from "./strings.js";

pickLanguage();
chrome("compare");
const [, , a, b] = location.pathname.split("/");
const main = document.querySelector("#compare");
const form = document.querySelector("#token-form");
const body = document.querySelector("#compare-body");
const question = document.querySelector("#compare-form");
const reveal = document.querySelector("#compare-reveal");
const KEY = "jyotish-reviewer-token";
let token = null;
try { token = sessionStorage.getItem(KEY); } catch { /* no storage: ask each time */ }

document.title = `${t("compare.title")} — Jyotish Engine`;
document.querySelector("#signin-heading").textContent = t("signin.heading");
document.querySelector("#token-label").textContent = t("signin.token");
document.querySelector("#token-open").textContent = t("compare.open");
document.querySelector("#compare-lead").textContent = t("compare.lead");
document.querySelector("#compare-heading").textContent = t("compare.question");
document.querySelector("#compare-why-label").textContent = t("compare.why");
document.querySelector("#compare-submit").textContent = t("compare.submit");
document.querySelector("#compare-choices").innerHTML = ["A", "B"].map((x) =>
  `<label class="choice"><input type="radio" name="choice" value="${x}" required> ${esc(t("compare.choice", { label: x }))}</label>`).join("");

async function call(path, method = "GET", payload) {
  const r = await fetch(`/compare/${encodeURIComponent(a)}/${encodeURIComponent(b)}${path}`, {
    method, headers: { Authorization: `Bearer ${token}`, ...(payload ? { "Content-Type": "application/json" } : {}) },
    body: payload ? JSON.stringify(payload) : undefined });
  const data = await r.json().catch(() => ({}));
  if (r.status === 401) {
    token = null; try { sessionStorage.removeItem(KEY); } catch { /* tab memory only */ }
    throw Object.assign(new Error(t("signin.refused")), { auth: true });
  }
  if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : `request failed (${r.status})`);
  return data;
}

function settings(s) {
  return t("compare.settings", { model: s.model || "–", effort: s.effort || "–", depth: s.depth || "–" });
}

function show(view) {
  for (const label of ["A", "B"]) document.querySelector(`#reading-${label}`).innerHTML =
    `<h2 class="compare-label">${esc(t("compare.reading", { label }))}</h2>${renderReading(view.readings[label])}`;
  body.hidden = false;
  main.dataset.state = view.answer ? "revealed" : "blind";
  if (!view.answer) return;
  question.hidden = true;
  const ans = view.answer;
  reveal.hidden = false;
  reveal.innerHTML = `<h2>${esc(t("compare.revealed"))}</h2>
    <p class="compare-choice">${esc(t("compare.you_chose", { label: ans.choice, reviewer: ans.reviewer }))}</p>
    <blockquote class="compare-why">${esc(ans.why)}</blockquote>
    <dl class="facts">${["A", "B"].map((x) => `<div data-label="${x}"><dt>${esc(t("compare.reading", { label: x }))}</dt>
      <dd>${esc(settings(view.reveal[x]))}</dd></div>`).join("")}</dl>`;
}

function ask() { form.hidden = false; body.hidden = true; main.dataset.state = "signin"; }

async function open() {
  try {
    const view = await call("/view");
    form.hidden = true;
    show(view);
  } catch (e) {
    if (e.auth) ask();
    else {
      form.hidden = true; body.hidden = false; question.hidden = true; main.dataset.state = "error";
      reveal.hidden = false; reveal.innerHTML = `<p class="error">${esc(e.message)}</p>`;
    }
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  token = document.querySelector("#token").value.trim();
  try { sessionStorage.setItem(KEY, token); } catch { /* tab memory only */ }
  await open();
  if (main.dataset.state === "signin") document.querySelector("#token-error").textContent = t("signin.refused");
});

question.addEventListener("submit", async (e) => {
  e.preventDefault();
  const choice = question.querySelector("input[name=choice]:checked")?.value;
  const why = document.querySelector("#compare-why").value.trim();
  const err = document.querySelector("#compare-error");
  if (!choice || !why) { err.textContent = t("compare.both"); return; }
  try { show(await call("/answer", "POST", { choice, why })); } catch (x) { err.textContent = x.message; }
});

if (token) open(); else ask();
