// The astrologer's review of a conversation (SPEC Layer 8): every turn beside the engine's own answer, its
// footnotes quoting the technical sheet, the sentences removed before the client saw them and why, and the word
// warnings; a sentence of the client's answer can be rewritten, held to the turn's checks before it is saved.

import { chrome } from "./chrome.js";
import { esc, sheetBlock } from "./render.js";
import { pickLanguage, t } from "./strings.js";

pickLanguage();
chrome("review");
const sid = location.pathname.split("/").filter(Boolean).pop();
const KEY = "jyotish-reviewer-token";        // the same as the reading's review page
let token = null;
try { token = sessionStorage.getItem(KEY); } catch { /* no storage: ask each time */ }

document.querySelector("#signin-heading").textContent = t("signin.heading");
document.querySelector("#token-label").textContent = t("signin.token");
document.querySelector("#token-open").textContent = t("signin.open");
document.querySelector("#session-heading").textContent = t("session.heading");

async function api(path, payload) {
  const r = await fetch(path, { method: payload ? "POST" : "GET",
    headers: { Authorization: `Bearer ${token}`, ...(payload ? { "Content-Type": "application/json" } : {}) },
    body: payload ? JSON.stringify(payload) : undefined });
  if (r.status === 401) {
    token = null; try { sessionStorage.removeItem(KEY); } catch { /* tab memory only */ }
    throw Object.assign(new Error(t("signin.refused")), { auth: true });
  }
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : `${r.status}`);
  return data;
}

function engineBlock(engine) {
  if (!engine) return "";
  const notes = [];
  const body = engine.sentences.map((s) => s.text + s.notes.map((n) => {
    notes.push(`<li id="n-${notes.length + 1}"><span class="muted">${esc(n.area.replace("_", " "))}, point ${n.point}${n.row ? ` (${esc(n.row)})` : ""}:</span> ${esc(n.text)}</li>`);
    return `<sup><a href="#n-${notes.length}">${notes.length}</a></sup>`;
  }).join("")).join(" ");
  return `<details class="turn-engine"><summary>${esc(t("session.engine"))}</summary><p>${body}</p><ol class="small">${notes.join("")}</ol></details>`;
}

function routeLine(route) {
  if (!route) return "";
  return t("session.route", { areas: (route.areas || []).map((a) => a.replace("_", " ")).join(", "),
    direction: t(`session.direction.${route.direction}`), when: route.when ? t("session.when") : "", why: route.why ? t("session.why") : "" });
}

function turnBlock(turn) {
  const source = turn.source === "fixed" ? t("session.source.fixed", { kind: (turn.route || {}).off_limits })
    : turn.replayed && turn.source === "writer" ? t("session.source.replay")
    : turn.source ? t(`session.source.${turn.source}`) : turn.status;
  const edited = new Set((turn.edited || []).map((e) => e.i));
  const units = turn.units.map((u, i) => `<li class="turn-unit" data-target="${esc(u.target)}">
      <span class="unit-text">${esc(u.text)}</span>${edited.has(i) ? ` <span class="muted small">(${esc(t("session.edited", { by: (turn.edited.find((e) => e.i === i) || {}).by }))})</span>` : ""}
      ${turn.source !== "fixed" ? `<button class="link small" type="button" data-edit="${esc(u.target)}" data-turn="${turn.n}">${esc(t("session.edit"))}</button>` : ""}</li>`).join("");
  const removed = turn.removed.length ? `<ul class="small">${turn.removed.map((r) => `<li>${esc(r.sentence || "(no draft)")}<br><span class="muted">${esc(r.reasons.join("; "))}</span></li>`).join("")}</ul>` : `<p class="small muted">${esc(t("session.none"))}</p>`;
  const warnings = turn.warnings.length ? `<ul class="small">${turn.warnings.map((w) => `<li>${esc(w.warning)}</li>`).join("")}</ul>` : `<p class="small muted">${esc(t("session.none"))}</p>`;
  const cost = turn.timeline ? `<span class="muted small">${esc(t("session.cost", { seconds: turn.timeline.done, cost: turn.cost_usd ?? "—" }))}</span>` : "";
  return `<article class="card turn-review" data-n="${turn.n}">
    <h2 class="small">${esc(t("session.turn", { n: turn.n }))} ${cost}</h2>
    <p class="turn-question"><strong>${esc(turn.question)}</strong></p>
    <p class="small muted">${esc(routeLine(turn.route))}</p>
    <h3 class="small">${esc(t("session.client"))}</h3><p class="small muted">${esc(source)}</p>
    <ol class="turn-units">${units}</ol>
    ${engineBlock(turn.engine)}
    <details><summary>${esc(t("session.removed"))} (${turn.removed.length})</summary>${removed}</details>
    <details><summary>${esc(t("session.warnings"))} (${turn.warnings.length})</summary>${warnings}</details>
  </article>`;
}

function render(view) {
  document.querySelector("#token-form").hidden = true;
  document.querySelector("#session").hidden = false;
  document.querySelector("#review").dataset.state = "ready";
  document.querySelector("#session-check").textContent = t("session.check", { words: (view.check || {}).words || "", as_of: view.as_of });
  document.querySelector("#turns").innerHTML = view.turns.map(turnBlock).join("");
  document.querySelector("#sheets").innerHTML = `<h2 class="small">${esc(t("session.sheets"))}</h2>`
    + Object.entries(view.sheets).map(([area, sheet]) => `<details><summary>${esc(area.replace("_", " "))}</summary>${sheetBlock(sheet)}</details>`).join("");
}

document.querySelector("#turns").addEventListener("click", (e) => {
  const b = e.target.closest("[data-edit]");
  if (!b) return;
  const li = b.closest(".turn-unit");
  if (li.querySelector("form")) return;
  const form = document.createElement("form");
  form.className = "turn-edit";
  form.innerHTML = `<textarea rows="3" required>${esc(li.querySelector(".unit-text").textContent)}</textarea>
    <label class="small"><input type="checkbox" checked> ${esc(t("session.keep_tags"))}</label>
    <button class="button small" type="submit">${esc(t("session.save"))}</button>
    <button class="link small" type="button" data-cancel>${esc(t("session.cancel"))}</button><p class="small" role="status"></p>`;
  li.append(form);
  form.querySelector("[data-cancel]").addEventListener("click", () => form.remove());
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const status = form.querySelector("[role=status]");
    try {
      const r = await api(`/sessions/${encodeURIComponent(sid)}/turns/${b.dataset.turn}/review/edit`,
        { target: b.dataset.edit, text: form.querySelector("textarea").value, keep_tags: form.querySelector("input").checked });
      if (r.accepted) { render(r.review); return; }
      status.textContent = t("session.refused", { why: r.errors.join("; ") });
    } catch (err) { status.textContent = err.message; }
  });
});

async function load() {
  try { render(await api(`/sessions/${encodeURIComponent(sid)}/review`)); }
  catch (err) {
    document.querySelector("#token-form").hidden = false;
    document.querySelector("#review").dataset.state = "signin";
    if (err.auth && token === null) document.querySelector("#token-error").textContent = "";
    else document.querySelector("#token-error").textContent = err.message;
  }
}

document.querySelector("#token-form").addEventListener("submit", (e) => {
  e.preventDefault();
  token = document.querySelector("#token").value.trim();
  try { sessionStorage.setItem(KEY, token); } catch { /* tab memory only */ }
  load();
});
if (token) load(); else { document.querySelector("#token-form").hidden = false; document.querySelector("#review").dataset.state = "signin"; }
