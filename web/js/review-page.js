// The review step (SPEC Layer 6b): the reviewer reads the reading, edits any sentence (the
// edit is accepted only if the validator and the checker pass it), adds a note per area, and
// approves. The reviewer token is the server's (JYOTISH_REVIEWERS); this page keeps it for the
// tab only.
import { chrome } from "./chrome.js";
import { esc } from "./render.js";

chrome("review");
const id = location.pathname.split("/").filter(Boolean).pop();
const form = document.querySelector("#token-form");
const body = document.querySelector("#review-body");
const main = document.querySelector("#review");
const KEY = "jyotish-reviewer-token";
let token = null;
try { token = sessionStorage.getItem(KEY); } catch { /* no storage: ask each time */ }

async function call(path, method = "GET", payload) {
  const r = await fetch(`/readings/${encodeURIComponent(id)}/review${path}`, {
    method, headers: { Authorization: `Bearer ${token}`, ...(payload ? { "Content-Type": "application/json" } : {}) },
    body: payload ? JSON.stringify(payload) : undefined });
  const data = await r.json().catch(() => ({}));
  if (r.status === 401) { token = null; try { sessionStorage.removeItem(KEY); } catch {} ; throw Object.assign(new Error("The reviewer token was not accepted."), { auth: true }); }
  if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : `request failed (${r.status})`);
  return data;
}

function render(view) {
  const r = view.reading;
  const byArea = {};
  for (const u of view.units) (byArea[u.area || "summary"] ||= []).push(u);
  const unit = (u) => `<div class="review-unit" data-target="${esc(u.target)}">
      <span class="target">${esc(u.kind)} · ${esc(u.target)}</span>
      <textarea aria-label="Edit ${esc(u.target)}">${esc(u.text)}</textarea>
      <div class="row-actions"><button class="button secondary save" type="button">Check and save</button>
      <span class="result small" role="status"></span></div></div>`;
  const REASONS = [["missing_rule", "Missing a rule"], ["wrong_weight", "Wrong weight"],
                   ["wrong_timing", "Wrong timing"], ["other", "Other"]];
  // The structured verdict (judgement data, logged; the client never sees it).
  const verdictBlock = (a) => {
    const v = (view.verdicts || {})[a.name];
    const btn = (key, label) => `<button type="button" class="button secondary verdict-choice" data-verdict="${key}" aria-pressed="${v && v.verdict === key}">${label}</button>`;
    return `<div class="verdict" data-area="${esc(a.name)}" role="group" aria-label="Your verdict on ${esc(a.name)}">
      <span class="small muted">Your verdict on this area:</span>
      ${btn("agree", "Agree")}${btn("partly", "Partly")}${btn("disagree", "Disagree")}
      <div class="verdict-reason" hidden>
        <label class="small">Why?
          <select class="reason">${["<option value=''>Choose a reason</option>", ...REASONS.map(([k, l]) => `<option value="${k}"${v && v.reason === k ? " selected" : ""}>${l}</option>`)].join("")}</select></label>
        <button type="button" class="button secondary save-verdict">Record verdict</button>
      </div>
      <span class="result small verdict-status" role="status">${v ? `Recorded: ${esc(v.verdict)}${v.reason ? ` (${esc(v.reason.replaceAll("_", " "))})` : ""}` : ""}</span>
      <p class="tiny muted">For the engine's learning only: the client never sees your verdict.</p></div>`;
  };
  const areaNote = (a) => `<div class="field note" data-area="${esc(a.name)}"><label>The astrologer's note on ${esc(a.name.replaceAll("_", " "))} (your own words, shown apart and not checked)</label>
      <textarea>${esc(a.astrologer_note ? a.astrologer_note.text : "")}</textarea>
      <div><button class="button secondary save-note" type="button">Save note</button> <span class="result small" role="status"></span></div></div>`;
  body.innerHTML = `
    <section class="identity"><span class="kicker">Review</span><h1 class="display">${esc(r.question)}</h1>
      <p class="header-line">Status: <strong id="review-status">${esc(view.review_status)}</strong> · depth ${esc(r.depth)} · chart ${esc(view.chart_id)}</p>
      <p class="muted small">Every sentence below can be edited. An edit is kept only if it passes the validator and the checker against the engine's data. A note is your own words and is shown to the client as the astrologer's note.</p></section>
    <section class="card"><h2>Summary</h2>${(byArea.summary || []).map(unit).join("")}</section>
    ${r.areas.map((a) => `<section class="card" data-area="${esc(a.name)}"><h2>${esc(a.name.replaceAll("_", " "))} · tier ${esc(a.tier)}</h2>
      ${verdictBlock(a)}
      ${(byArea[a.name] || []).map(unit).join("")}${areaNote(a)}</section>`).join("")}
    <section class="card"><h2>Approve</h2><p class="small muted">The client-facing page says "reviewed by" only after approval.</p>
      <button class="button" id="approve" type="button"${view.review_status === "reviewed" ? " disabled" : ""}>${view.review_status === "reviewed" ? "Reviewed" : "Approve this reading"}</button></section>
    <section class="card"><h2>Log</h2><ol class="small" id="history">${view.history.map((h) => `<li>${esc(h.at.slice(0, 19))} · ${esc(h.reviewer)} · ${esc(h.action)}${h.target ? ` · ${esc(h.target)}` : ""}${h.verdict ? ` · ${esc(h.verdict)}${h.reason ? ` (${esc(h.reason)})` : ""}` : ""}${h.accepted === false ? " · refused" : h.accepted ? " · accepted" : ""}</li>`).join("")}</ol></section>`;
  main.dataset.state = view.review_status;
  body.querySelectorAll(".review-unit .save").forEach((b) => b.addEventListener("click", async () => {
    const el = b.closest(".review-unit");
    const out = el.querySelector(".result");
    out.className = "result small"; out.textContent = "Checking…";
    try {
      const res = await call("/edit", "POST", { target: el.dataset.target, text: el.querySelector("textarea").value });
      if (res.accepted) { render(res.review); flash(el.dataset.target, "Accepted: it passed the validator and the checker.", true); }
      else { out.className = "result small bad"; out.textContent = `Refused: ${res.errors.join(" · ")}`; }
    } catch (e) { out.className = "result small bad"; out.textContent = e.message; if (e.auth) ask(); }
  }));
  body.querySelectorAll(".verdict").forEach((box) => {
    const area = box.dataset.area;
    const reasonBox = box.querySelector(".verdict-reason");
    const status = box.querySelector(".verdict-status");
    const send = async (verdict, reason) => {
      try { render(await call("/verdict", "POST", { area, verdict, reason: reason || null })); }
      catch (e) { status.className = "result small bad verdict-status"; status.textContent = e.message; if (e.auth) ask(); }
    };
    box.querySelectorAll(".verdict-choice").forEach((b) => b.addEventListener("click", () => {
      box.querySelectorAll(".verdict-choice").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      if (b.dataset.verdict === "agree") { reasonBox.hidden = true; send("agree"); }
      else { reasonBox.hidden = false; reasonBox.dataset.verdict = b.dataset.verdict; box.querySelector(".reason").focus(); }
    }));
    box.querySelector(".save-verdict").addEventListener("click", () => {
      const reason = box.querySelector(".reason").value;
      if (!reason) { status.className = "result small bad verdict-status"; status.textContent = "Choose a reason first."; return; }
      send(reasonBox.dataset.verdict, reason);
    });
  });
  body.querySelectorAll(".note .save-note").forEach((b) => b.addEventListener("click", async () => {
    const el = b.closest(".note");
    try { render(await call("/note", "POST", { area: el.dataset.area, text: el.querySelector("textarea").value })); }
    catch (e) { el.querySelector(".result").textContent = e.message; if (e.auth) ask(); }
  }));
  body.querySelector("#approve").addEventListener("click", async () => {
    try { render(await call("/approve", "POST")); } catch (e) { if (e.auth) ask(); }
  });
}

function flash(target, message, ok) {
  const el = body.querySelector(`.review-unit[data-target="${CSS.escape(target)}"] .result`);
  if (el) { el.className = `result small ${ok ? "ok" : "bad"}`; el.textContent = message; }
}

function ask() { form.hidden = false; body.innerHTML = ""; main.dataset.state = "signin"; }

async function open() {
  try { render(await call("")); form.hidden = true; }
  catch (e) { if (e.auth) { ask(); document.querySelector("#token-error").textContent = token === null && form.dataset.tried ? e.message : ""; } else body.innerHTML = `<p class="error">${esc(e.message)}</p>`; }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  token = document.querySelector("#token").value.trim();
  form.dataset.tried = "1";
  try { sessionStorage.setItem(KEY, token); } catch { /* tab memory only */ }
  await open();
  if (main.dataset.state === "signin") document.querySelector("#token-error").textContent = "The reviewer token was not accepted.";
});

if (token) open(); else ask();
