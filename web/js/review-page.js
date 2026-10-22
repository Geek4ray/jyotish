// The guided review (SPEC Layer 6b): the chart on the left, the questions on the right, one
// step at a time. Every answer is saved to the server as it is given (POST .../review/answer,
// logged with step, area, answer, reviewer and time); text being typed is kept in this
// browser until it is sent, so closing the tab loses nothing. The page reopens at the first
// step not yet answered. ?mode=blind is the judge page: the same flow, but for each area the
// reviewer first answers from the chart alone, and the server sends the engine's reading and
// period only after. Every question but the note has an optional box for the reviewer's own words,
// sent in the same answer row (Ctrl+Enter sends it and goes on), and a last question asks about the
// reading as a whole. Answers and words are judgements: never shown to the client, never checked.
// Every label comes from strings.js.
import { chrome } from "./chrome.js";
import { esc } from "./render.js";
import { pickLanguage, t } from "./strings.js";

pickLanguage();
chrome("review");
const params = new URLSearchParams(location.search);
const MODE = params.get("mode") === "blind" ? "blind" : "review";
const id = location.pathname.split("/").filter(Boolean).pop();
const main = document.querySelector("#review");
const form = document.querySelector("#token-form");
const layout = document.querySelector("#guided");
const panel = document.querySelector("#guided-panel");
const progressBox = document.querySelector("#guided-progress");
const chartBox = document.querySelector("#guided-chart");
const KEY = "jyotish-reviewer-token";
let token = null;
try { token = sessionStorage.getItem(KEY); } catch { /* no storage: ask each time */ }

document.title = `${t(MODE === "blind" ? "title.blind" : "title")} — Jyotish Engine`;
document.querySelector("#signin-heading").textContent = t("signin.heading");
document.querySelector("#token-label").textContent = t("signin.token");
document.querySelector("#token-open").textContent = t("signin.open");
document.querySelector("#guided-keys").textContent = `${t("nav.keys")} · ${t("nav.keys_text")}`;

const state = { view: null, at: null, chartDrawn: false, local: {} };

// --- the server ---------------------------------------------------------------------------

async function call(path, method = "GET", payload) {
  const sep = path.includes("?") ? "&" : "?";
  const r = await fetch(`/readings/${encodeURIComponent(id)}/review${path}${sep}mode=${MODE}`, {
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

function saved(text, bad = false) {
  const el = panel.querySelector(".save-state");
  if (el) { el.textContent = text; el.classList.toggle("bad", bad); }
}

// The reviewer's own words on this step, when it has the box.
function words() {
  const box = panel.querySelector("#own-words");
  return box ? box.value.trim() : undefined;
}

async function answer(step, area, value) {
  saved(t("saving"));
  const comment = words();
  try {
    state.view = await call("/answer", "POST", { step, area, answer: value, mode: MODE, ...(comment !== undefined ? { comment } : {}) });
    if (comment !== undefined) dropDraft(`c:${step}:${area}`);
    saved(t("saved"));
    return true;
  } catch (e) {
    saved(t("save_failed", { message: e.message }), true);
    if (e.auth) ask();
    return false;
  }
}

// --- text kept in this browser until it is sent -------------------------------------------

const draftKey = (k) => `jyotish-review:${id}:${state.view ? state.view.reviewer : ""}:${MODE}:${k}`;
function draft(k, value) {
  try { if (value === undefined) return JSON.parse(localStorage.getItem(draftKey(k)) ?? "null"); localStorage.setItem(draftKey(k), JSON.stringify(value)); }
  catch { return null; }
  return value;
}
function dropDraft(k) { try { localStorage.removeItem(draftKey(k)); } catch { /* nothing kept */ } }

// --- the steps ----------------------------------------------------------------------------

const areas = () => state.view.reading.areas;
const areaName = (n) => { try { return t(`areaname.${n}`); } catch { return n.replaceAll("_", " "); } };
const hasWindows = (a) => (a.hidden ? a.has_windows : (a.windows || []).length > 0);
function latestRow(area, step) {
  const xs = state.view.answers.filter((x) => x.mode === MODE && x.step === step && (x.area ?? null) === (area ?? null));
  return xs.length ? xs[xs.length - 1] : undefined;
}
function latest(area, step) {
  const row = latestRow(area, step);
  return row ? row.answer : undefined;
}
const COMMENTED = new Set(["blind_reading", "blind_period", "match", "off", "sentences", "period"]);

function steps() {
  const v = state.view;
  const out = [];
  if (!v.intro_done) for (const i of [1, 2, 3]) out.push({ k: "intro", i, key: `intro:${i}` });
  areas().forEach((a, n) => {
    const at = (k) => ({ k, area: a.name, n, key: `${k}:${a.name}` });
    if (MODE === "blind") {
      out.push(at("blind_reading"));
      if (hasWindows(a)) out.push(at("blind_period"));
    }
    out.push(at("match"));
    const m = latest(a.name, "match");
    if (m !== undefined && m !== "agree") out.push(at("off"));
    out.push(at("sentences"), at("note"));
    if (hasWindows(a)) out.push(at("period"));
  });
  out.push({ k: "whole", key: "whole" }, { k: "summary", key: "summary" }, { k: "done", key: "done" });
  return out;
}

function answered(s) {
  if (s.k === "intro") return state.view.intro_done;
  if (s.k === "whole") return latest(null, "whole") !== undefined;
  if (s.k === "summary" || s.k === "done") return state.view.review_status === "reviewed";
  return latest(s.area, s.k) !== undefined;
}

function resume() {
  const all = steps();
  if (state.view.review_status === "reviewed") return "done";
  const first = all.find((s) => s.k !== "done" && !answered(s));
  return (first || all.find((s) => s.k === "summary")).key;
}

function here() {
  const all = steps();
  let i = all.findIndex((s) => s.key === state.at);
  if (i < 0) { state.at = resume(); i = all.findIndex((s) => s.key === state.at); }
  return { all, i, s: all[i] };
}

function go(key) {
  state.at = key;
  state.local = {};
  render();
  panel.focus({ preventScroll: true });
}

function goNext() {
  const { all, i } = here();
  if (i + 1 < all.length) go(all[i + 1].key);
}

function goBack() {
  const { all, i } = here();
  if (i > 0) go(all[i - 1].key);
}

// --- pieces -------------------------------------------------------------------------------

const month = (iso) => {
  if (!iso) return "";
  const d = new Date(`${iso.length === 7 ? `${iso}-01` : iso}T00:00:00`);
  return d.toLocaleDateString(document.documentElement.lang, { month: "short", year: "numeric" });
};

// "In your own words": beside the choices, kept in this browser until it is sent.
function ownWords(s) {
  const row = latestRow(s.area, s.k);
  const value = draft(`c:${s.key}`) ?? (row && row.comment) ?? "";
  return `<div class="own-words field"><label for="own-words">${esc(t("comment.label"))}</label>
    <textarea id="own-words" rows="4">${esc(value)}</textarea><p class="tiny muted">${esc(t("comment.hint"))}</p></div>`;
}

function beside(s, body) {
  return `<div class="question-row"><div class="question-body">${body}</div>${ownWords(s)}</div>`;
}

function choices(options, current) {
  return `<div class="choices" role="group">${options.map(([value, label], i) =>
    `<button type="button" class="choice" data-value="${esc(value)}" data-key="${i + 1}" aria-pressed="${current === value}"><span class="choice-key">${i + 1}</span>${esc(label)}</button>`).join("")}</div>`;
}

function rangeInputs(prefix, value) {
  value = value || {};
  return `<div class="field-row range">
    <div class="field"><label for="${prefix}-from">${esc(t("period.from"))}</label><input id="${prefix}-from" type="month" value="${esc((value.from || "").slice(0, 7))}"></div>
    <div class="field"><label for="${prefix}-to">${esc(t("period.to"))}</label><input id="${prefix}-to" type="month" value="${esc((value.to || "").slice(0, 7))}"></div></div>`;
}

function readRange(prefix) {
  const from = panel.querySelector(`#${prefix}-from`).value;
  const to = panel.querySelector(`#${prefix}-to`).value;
  return from && to && to >= from ? { from, to } : null;
}

const areaUnits = (area) => {
  const us = state.view.units.filter((u) => u.area === area);
  const para = us.filter((u) => u.kind === "paragraph");
  return para.length ? para : us.filter((u) => u.kind === "claim");
};

const areaOf = (name) => areas().find((a) => a.name === name);

function quoted(area) {
  const us = areaUnits(area);
  return `<blockquote class="quoted paragraph-quote">${us.map((u) => esc(u.plain)).join(" ")}</blockquote>`;
}

function footer(nextLabel = t("nav.next"), { back = true } = {}) {
  return `<div class="step-nav">
    ${back ? `<button type="button" class="button secondary back">${esc(t("nav.back"))}</button>` : "<span></span>"}
    <span class="save-state small muted" role="status"></span>
    <button type="button" class="button next">${esc(nextLabel)}</button></div>`;
}

function stepHead(s) {
  if (!s.area) return "";
  return `<p class="kicker">${esc(t("area.of", { n: s.n + 1, total: areas().length }))}</p>
    <h2 class="display step-area">${esc(areaName(s.area))}</h2>`;
}

// --- each step ----------------------------------------------------------------------------

const VIEWS = {
  intro(s) {
    const blind = MODE === "blind" && s.i === 1 ? `<p class="blind-note">${esc(t("intro.blind"))}</p>` : "";
    return `<p class="kicker">${s.i} / 3</p><h2 class="display">${esc(t(`intro.${s.i}.heading`))}</h2>
      <p class="lead">${esc(t(`intro.${s.i}.body`, { name: state.view.reviewer }))}</p>${blind}
      ${footer(s.i === 3 ? t("nav.begin") : t("nav.next"), { back: s.i > 1 })}`;
  },
  blind_reading(s) {
    const cur = state.local.choice ?? latest(s.area, s.k);
    return `${stepHead(s)}<h3 class="question">${esc(t("blind_reading.q", { area: areaName(s.area) }))}</h3>
      ${beside(s, choices(["promising", "mixed", "difficult"].map((x) => [x, t(`blind_reading.${x}`)]), cur))}${footer()}`;
  },
  blind_period(s) {
    const cur = draft(s.key) || latest(s.area, s.k);
    return `${stepHead(s)}<h3 class="question">${esc(t("blind_period.q", { area: areaName(s.area) }))}</h3>
      ${beside(s, `<p class="small muted">${esc(t("blind_period.hint"))}</p>${rangeInputs("own", cur)}`)}${footer()}`;
  },
  match(s) {
    const cur = state.local.choice ?? latest(s.area, s.k);
    const own = MODE === "blind" ? latest(s.area, "blind_reading") : undefined;
    return `${stepHead(s)}<p class="small muted">${esc(t("match.lead", { area: areaName(s.area) }))}</p>${quoted(s.area)}
      ${own ? `<p class="small own">${esc(t("match.your_blind", { answer: t(`blind_reading.${own}`) }))}</p>` : ""}
      <h3 class="question">${esc(t("match.q", { area: areaName(s.area) }))}</h3>
      ${beside(s, choices(["agree", "partly", "disagree"].map((x) => [x, t(`match.${x}`)]), cur))}${footer()}`;
  },
  off(s) {
    const cur = draft(s.key) || latest(s.area, s.k) || { reasons: [], line: "" };
    state.local.off = state.local.off || { reasons: [...cur.reasons], line: cur.line || "" };
    const on = new Set(state.local.off.reasons);
    return `${stepHead(s)}<h3 class="question">${esc(t("off.q"))}</h3><p class="small muted">${esc(t("off.hint"))}</p>
      ${beside(s, `<div class="choices multi" role="group">${["missing_combination", "weight", "timing", "wording", "other"].map((x, i) =>
        `<button type="button" class="choice toggle" data-value="${x}" data-key="${i + 1}" aria-pressed="${on.has(x)}"><span class="choice-key">${i + 1}</span>${esc(t(`off.${x}`))}</button>`).join("")}</div>
      <div class="field"><label for="off-line">${esc(t("off.line"))}</label><input id="off-line" type="text" value="${esc(state.local.off.line)}"></div>`)}
      ${footer()}`;
  },
  sentences(s) {
    const us = areaUnits(s.area);
    const prev = (latest(s.area, s.k) || {}).decisions || {};
    state.local.decisions = state.local.decisions || { ...prev };
    const cards = us.map((u) => {
      const d = state.local.decisions[u.target] || "keep";
      const open = state.local.open === u.target;
      const rewrite = open ? `<div class="rewrite">
          <div class="field"><label for="rw-text">${esc(t("sentences.rewrite"))}</label>
            <textarea id="rw-text" rows="4">${esc(draft(`rw:${u.target}`) ?? u.plain)}</textarea></div>
          <div class="facts"><h4 class="small">${esc(t("sentences.facts"))}</h4>
            ${u.facts.length ? `<ul class="small">${u.facts.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>` : `<p class="small muted">${esc(t("sentences.no_facts"))}</p>`}</div>
          <div class="rewrite-actions"><button type="button" class="button check-rewrite">${esc(t("sentences.check"))}</button>
            <button type="button" class="button secondary cancel-rewrite">${esc(t("sentences.cancel"))}</button></div>
          <div class="rewrite-result small" role="status">${state.local.result || ""}</div></div>` : "";
      return `<div class="sentence-card${d === "rewritten" ? " rewritten" : ""}" data-target="${esc(u.target)}">
        <p class="quoted">${esc(u.plain)}</p>
        <div class="sentence-actions">
          ${d === "rewritten" ? `<span class="badge">${esc(t("sentences.rewritten"))}</span>` : ""}
          <button type="button" class="button secondary keep" aria-pressed="${d === "keep" && !open}">${esc(t("sentences.keep"))}</button>
          <button type="button" class="button secondary open-rewrite" aria-pressed="${open}">${esc(t("sentences.rewrite"))}</button></div>
        ${rewrite}</div>`;
    }).join("");
    return `${stepHead(s)}<h3 class="question">${esc(t("sentences.q"))}</h3><p class="small muted">${esc(t("sentences.hint"))}</p>
      ${us.length ? `<div class="sentence-cards">${cards}</div>` : `<p class="muted">${esc(t("sentences.none"))}</p>`}
      ${ownWords(s)}${footer()}`;
  },
  note(s) {
    const a = areaOf(s.area);
    const cur = draft(s.key) ?? (latest(s.area, s.k) || {}).text ?? (a.astrologer_note ? a.astrologer_note.text : "");
    return `${stepHead(s)}<h3 class="question">${esc(t("note.q"))}</h3><p class="small muted">${esc(t("note.hint"))}</p>
      <div class="field"><label for="note-text">${esc(t("note.label", { area: areaName(s.area) }))}</label>
        <textarea id="note-text" rows="6">${esc(cur)}</textarea></div>${footer()}`;
  },
  period(s) {
    const a = areaOf(s.area);
    const own = MODE === "blind" ? latest(s.area, "blind_period") : undefined;
    const cur = state.local.period || draft(s.key) || latest(s.area, s.k) || (own ? { from: own.from, to: own.to } : {});
    state.local.period = cur;
    const best = a.windows[0];
    return `${stepHead(s)}<p class="small muted">${esc(t("period.engine", { area: areaName(s.area) }))}</p>
      <p class="engine-period quoted">${esc(t("period.range", { start: month(best.start), end: month(best.end) }))}</p>
      ${a.avoid_window ? `<p class="small muted">${esc(t("period.avoid", { start: month(a.avoid_window.start), end: month(a.avoid_window.end) }))}</p>` : ""}
      ${own ? `<p class="small own">${esc(t("period.your_blind", { start: month(own.from), end: month(own.to) }))}</p>` : ""}
      <h3 class="question">${esc(t("period.q"))}</h3>
      ${beside(s, `${choices(["yes", "earlier", "later", "different"].map((x) => [x, t(`period.${x}`)]), cur.choice)}
      <div class="your-period"${cur.choice && cur.choice !== "yes" ? "" : " hidden"}>
        <p class="small">${esc(t("period.yours"))}</p>${rangeInputs("yours", cur)}</div>`)}${footer(t("nav.next"))}`;
  },
  whole() {
    const cur = draft("whole") ?? (latest(null, "whole") || {}).text ?? "";
    return `<p class="kicker">${esc(t("whole.label"))}</p><h2 class="display">${esc(t("whole.q"))}</h2>
      <p class="small muted">${esc(t("whole.hint"))}</p>
      <div class="field"><label for="whole-text">${esc(t("whole.label"))}</label><textarea id="whole-text" rows="6">${esc(cur)}</textarea></div>
      ${footer()}`;
  },
  summary() {
    const v = state.view;
    const range = (x) => t("period.range", { start: month(x.from), end: month(x.to) });
    const says = {
      blind_reading: (a) => t(`blind_reading.${a}`),
      blind_period: (a) => range(a),
      match: (a) => t(`match.${a}`),
      off: (a) => [...a.reasons.map((x) => t(`off.${x}`)), a.line].filter(Boolean).join("; "),
      sentences: (a) => String(Object.values(a.decisions || {}).filter((x) => x === "rewritten").length),
      note: (a) => a.text,
      period: (a) => (a.choice === "yes" ? t("period.yes") : `${t(`period.${a.choice}`)}: ${range(a)}`),
      whole: (a) => a.text,
    };
    const label = { blind_reading: "summary.blind_reading", blind_period: "summary.blind_period", match: "summary.match",
                    off: "summary.off", sentences: "summary.sentences", note: "summary.note", period: "summary.period",
                    whole: "summary.whole" };
    // One line per question: what was chosen, the reviewer's words, and a way back to change either.
    const line = (st) => {
      const row = latestRow(st.area ?? null, st.k);
      const chosen = row ? says[st.k](row.answer) : "";
      return `<li class="summary-line" data-step="${esc(st.key)}"><span class="q">${esc(t(label[st.k]))}</span>
        <span class="a">${chosen ? esc(chosen) : esc(t("summary.empty"))}</span>
        ${row && row.comment ? `<span class="words">${esc(t("summary.words", { words: row.comment }))}</span>` : ""}
        ${st.k.startsWith("blind_") ? "" : `<button type="button" class="button secondary change" data-go="${esc(st.key)}">${esc(t("summary.change"))}</button>`}</li>`;
    };
    const all = steps().filter((x) => x.k in says);
    const blocks = areas().map((a) => `<section class="summary-area" data-area="${esc(a.name)}"><h3>${esc(areaName(a.name))}</h3>
      <ul class="summary-lines">${all.filter((x) => x.area === a.name).map(line).join("")}</ul></section>`).join("");
    const whole = all.filter((x) => x.k === "whole").map(line).join("");
    return `<h2 class="display">${esc(t("summary.heading"))}</h2>${blocks}
      <section class="summary-area" data-area=""><ul class="summary-lines">${whole}</ul></section>
      <div class="approve-box"><p class="approve-line">${esc(t("summary.approve_line", { name: v.reviewer }))}</p>
        <button type="button" class="button approve big">${esc(t("summary.approve"))}</button></div>
      <div class="step-nav"><button type="button" class="button secondary back">${esc(t("nav.back"))}</button><span class="save-state small muted" role="status"></span><span></span></div>`;
  },
  done() {
    const by = state.view.reading.review && state.view.reading.review.reviewed_by;
    return `<h2 class="display">${esc(t("done.heading"))}</h2>
      <p class="lead">${esc(t(by && by !== state.view.reviewer ? "done.already" : "done.body", { name: by || state.view.reviewer }))}</p>
      <p><a class="button" href="/reading.html?id=${encodeURIComponent(id)}">${esc(t("done.client"))}</a></p>`;
  },
};

// --- what Next does on each step ----------------------------------------------------------

const NEXT = {
  async intro(s) {
    if (s.i < 3) return goNext();
    if (await answer("intro", null, "done")) go(resume());
  },
  async blind_reading(s) { return chosen(s); },
  async blind_period(s) {
    const r = readRange("own");
    if (!r) return saved(t("period.need_range"), true);
    if (await answer(s.k, s.area, r)) { dropDraft(s.key); goNext(); }
  },
  async match(s) { return chosen(s); },
  async off(s) {
    const v = state.local.off;
    v.line = panel.querySelector("#off-line").value;
    if (!v.reasons.length) return saved(t("choose_first"), true);
    if (await answer(s.k, s.area, { reasons: v.reasons, line: v.line.trim() })) { dropDraft(s.key); goNext(); }
  },
  async sentences(s) {
    if (await answer(s.k, s.area, { decisions: state.local.decisions })) goNext();
  },
  async note(s) {
    const text = panel.querySelector("#note-text").value;
    const a = areaOf(s.area);
    const before = a.astrologer_note ? a.astrologer_note.text : "";
    try {
      if (text.trim() !== before) state.view = await call("/note", "POST", { area: s.area, text });
    } catch (e) { saved(t("save_failed", { message: e.message }), true); if (e.auth) ask(); return; }
    if (await answer(s.k, s.area, { text: text.trim() })) { dropDraft(s.key); goNext(); }
  },
  async period(s) {
    const cur = state.local.period;
    if (!cur.choice) return saved(t("choose_first"), true);
    let value = { choice: cur.choice };
    if (cur.choice !== "yes") {
      const r = readRange("yours");
      if (!r) return saved(t("period.need_range"), true);
      value = { ...value, ...r };
    }
    if (await answer(s.k, s.area, value)) { dropDraft(s.key); goNext(); }
  },
  async whole() {
    const text = panel.querySelector("#whole-text").value.trim();
    if (await answer("whole", null, { text })) { dropDraft("whole"); goNext(); }
  },
  async summary() {},
  async done() {},
};

async function chosen(s) {
  const row = latestRow(s.area, s.k);
  if (row === undefined) return saved(t("choose_first"), true);
  // Words typed after the choice was saved go in a new answer row with the same choice.
  if ((words() || "") !== (row.comment || "") && !(await answer(s.k, s.area, row.answer))) return;
  goNext();
}

async function next() {
  const { s } = here();
  await NEXT[s.k](s);
}

// --- events on the current step -----------------------------------------------------------

function bind(s) {
  panel.querySelector(".next")?.addEventListener("click", next);
  panel.querySelector(".back")?.addEventListener("click", goBack);
  panel.querySelector("#own-words")?.addEventListener("input", (e) => draft(`c:${s.key}`, e.target.value));
  if (s.k === "whole") panel.querySelector("#whole-text").addEventListener("input", (e) => draft("whole", e.target.value));
  if (["blind_reading", "match"].includes(s.k)) {
    panel.querySelectorAll(".choice").forEach((b) => b.addEventListener("click", async () => {
      state.local.choice = b.dataset.value;
      panel.querySelectorAll(".choice").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      if (await answer(s.k, s.area, b.dataset.value)) {
        delete state.local.choice;
        if (s.k === "match") render();                  // "What is off?" joins or leaves the steps
      }
    }));
  }
  if (s.k === "blind_period") {
    panel.querySelectorAll("input").forEach((i) => i.addEventListener("input", () =>
      draft(s.key, { from: panel.querySelector("#own-from").value, to: panel.querySelector("#own-to").value })));
  }
  if (s.k === "off") {
    const save = () => draft(s.key, { reasons: state.local.off.reasons, line: panel.querySelector("#off-line").value });
    panel.querySelectorAll(".choice").forEach((b) => b.addEventListener("click", async () => {
      const on = new Set(state.local.off.reasons);
      on.has(b.dataset.value) ? on.delete(b.dataset.value) : on.add(b.dataset.value);
      state.local.off.reasons = ["missing_combination", "weight", "timing", "wording", "other"].filter((x) => on.has(x));
      b.setAttribute("aria-pressed", String(on.has(b.dataset.value)));
      save();
      if (state.local.off.reasons.length)
        await answer(s.k, s.area, { reasons: state.local.off.reasons, line: panel.querySelector("#off-line").value.trim() });
    }));
    panel.querySelector("#off-line").addEventListener("input", (e) => { state.local.off.line = e.target.value; save(); });
  }
  if (s.k === "sentences") bindSentences(s);
  if (s.k === "note") panel.querySelector("#note-text").addEventListener("input", (e) => draft(s.key, e.target.value));
  if (s.k === "period") {
    const box = panel.querySelector(".your-period");
    const keep = () => {
      const p = state.local.period;
      const from = panel.querySelector("#yours-from").value, to = panel.querySelector("#yours-to").value;
      state.local.period = { ...p, from, to };
      draft(s.key, state.local.period);
    };
    panel.querySelectorAll(".choice").forEach((b) => b.addEventListener("click", async () => {
      state.local.period = { ...state.local.period, choice: b.dataset.value };
      panel.querySelectorAll(".choice").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      box.hidden = b.dataset.value === "yes";
      draft(s.key, state.local.period);
      if (b.dataset.value === "yes") { if (await answer(s.k, s.area, { choice: "yes" })) dropDraft(s.key); }
      else if (readRange("yours")) await answer(s.k, s.area, { choice: b.dataset.value, ...readRange("yours") });
      else panel.querySelector("#yours-from").focus();
    }));
    panel.querySelectorAll(".your-period input").forEach((i) => i.addEventListener("input", keep));
  }
  if (s.k === "summary") {
    panel.querySelectorAll(".change").forEach((b) => b.addEventListener("click", () => go(b.dataset.go)));
    panel.querySelector(".approve").addEventListener("click", async () => {
      try { state.view = await call("/approve", "POST"); go("done"); }
      catch (e) { saved(t("save_failed", { message: e.message }), true); if (e.auth) ask(); }
    });
  }
}

function bindSentences(s) {
  panel.querySelectorAll(".sentence-card").forEach((card) => {
    const target = card.dataset.target;
    card.querySelector(".keep").addEventListener("click", () => {
      if (state.local.decisions[target] !== "rewritten") state.local.decisions[target] = "keep";
      state.local.open = null; state.local.result = ""; render();
    });
    card.querySelector(".open-rewrite").addEventListener("click", () => {
      state.local.open = target; state.local.result = ""; render();
      panel.querySelector("#rw-text").focus();
    });
    const box = card.querySelector(".rewrite");
    if (!box) return;
    const area = box.querySelector("#rw-text");
    area.addEventListener("input", () => draft(`rw:${target}`, area.value));
    box.querySelector(".cancel-rewrite").addEventListener("click", () => { state.local.open = null; state.local.result = ""; render(); });
    box.querySelector(".check-rewrite").addEventListener("click", async () => {
      const out = box.querySelector(".rewrite-result");
      out.className = "rewrite-result small"; out.textContent = t("sentences.checking");
      try {
        const res = await call("/edit", "POST", { target, text: area.value, keep_tags: true });
        state.view = res.review;
        if (res.accepted) {
          state.local.decisions[target] = "rewritten";
          state.local.open = null;
          state.local.result = "";
          dropDraft(`rw:${target}`);
          render();
          const done = panel.querySelector(`.sentence-card[data-target="${CSS.escape(target)}"] .sentence-actions`);
          done?.insertAdjacentHTML("beforeend", `<span class="ok small accepted">${esc(t("sentences.accepted"))}</span>`);
          await answer(s.k, s.area, { decisions: state.local.decisions });
        } else {
          state.local.result = `<p class="bad">${esc(t("sentences.refused"))}</p><ul class="reasons">${res.reasons.map((r) =>
            `<li data-code="${esc(r.code)}">${esc(t(`reason.${r.code}`, { detail: r.detail }))}</li>`).join("")}</ul>`;
          out.className = "rewrite-result small"; out.innerHTML = state.local.result;
        }
      } catch (e) { out.className = "rewrite-result small bad"; out.textContent = e.message; if (e.auth) ask(); }
    });
  });
}

// --- the page -----------------------------------------------------------------------------

function render() {
  const { all, i, s } = here();
  const counted = all.filter((x) => x.k !== "done");
  const n = Math.min(i + 1, counted.length);
  progressBox.innerHTML = `<div class="bar" role="progressbar" aria-valuemin="1" aria-valuemax="${counted.length}" aria-valuenow="${n}" aria-label="${esc(t("progress", { n, total: counted.length }))}"><span style="width:${(100 * n / counted.length).toFixed(1)}%"></span></div>
    <span class="small muted">${esc(t("progress", { n, total: counted.length }))}</span>`;
  panel.dataset.step = s.k;
  panel.dataset.area = s.area || "";
  panel.innerHTML = VIEWS[s.k](s);
  main.dataset.state = state.view.review_status;
  main.dataset.step = s.key;
  bind(s);
}

document.addEventListener("keydown", (e) => {
  if (!state.view || layout.hidden || e.altKey) return;
  const tag = e.target.tagName;
  if (tag === "TEXTAREA") {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); next(); }
    return;
  }
  if (tag === "INPUT") {
    if (e.key === "Enter") { e.preventDefault(); next(); }
    return;
  }
  if (e.ctrlKey || e.metaKey) return;
  if (/^[1-9]$/.test(e.key)) {
    const b = panel.querySelector(`.choice[data-key="${e.key}"]`);
    if (b) { e.preventDefault(); b.click(); }
  } else if (e.key === "Enter") {
    if (tag === "BUTTON" && !e.target.classList.contains("choice") && !e.target.classList.contains("next")) return;
    if (tag === "A") return;
    e.preventDefault();
    next();
  }
});

// --- the chart, fixed on the left ---------------------------------------------------------

async function drawChart() {
  if (state.chartDrawn) return;
  state.chartDrawn = true;
  chartBox.innerHTML = `<h2 id="chart-heading">${esc(t("chart.heading"))}</h2><p class="small muted">${esc(t("chart.loading"))}</p>`;
  const asOf = state.view.reading.as_of;
  const cid = encodeURIComponent(state.view.chart_id);
  const [svg, tables] = await Promise.all([
    fetch(`/charts/${cid}/chart.svg?vargas=D1,D9`).then((r) => r.text()),
    fetch(`/charts/${cid}/tables.json${asOf ? `?as_of=${encodeURIComponent(asOf)}` : ""}`).then((r) => r.json())]);
  const v = tables.vimshottari;
  const maha = v.mahas.find((m) => m.current) || v.mahas[0];
  const row = (p, label) => `<tr${p.current ? ' class="current"' : ""}><td>${esc(label)}${p.current ? ` <strong>(${esc(t("chart.now"))})</strong>` : ""}</td><td>${esc(p.start)}</td><td>${esc(p.end)}</td></tr>`;
  const head = `<tr><th></th><th>${esc(t("chart.from"))}</th><th>${esc(t("chart.to"))}</th></tr>`;
  chartBox.innerHTML = `<h2 id="chart-heading">${esc(t("chart.heading"))}</h2>
    <div class="chart-figure">${svg}</div>
    <h3 class="small">${esc(t("chart.dasha"))}</h3>
    <p class="small current-period">${esc(t("chart.current", { date: v.as_of, period: v.current.join(" – ") }))}</p>
    <div class="dasha-tables"><table class="dasha-table small"><caption>${esc(t("chart.maha"))}</caption>${head}${v.mahas.map((m) => row(m, m.lords[0])).join("")}</table>
    <table class="dasha-table small"><caption>${esc(t("chart.antar", { maha: maha.lords[0] }))}</caption>${head}${maha.antars.map((a) => row(a, a.lords[1])).join("")}</table></div>`;
}

// --- sign-in ------------------------------------------------------------------------------

function ask() { form.hidden = false; layout.hidden = true; main.dataset.state = "signin"; }

async function open() {
  try {
    state.view = await call("");
    form.hidden = true;
    layout.hidden = false;
    state.at = resume();
    render();
    drawChart().catch(() => { chartBox.innerHTML = `<p class="error small">${esc(t("chart.heading"))}: —</p>`; });
  } catch (e) {
    if (e.auth) ask();
    else { layout.hidden = false; panel.innerHTML = `<p class="error">${esc(e.message)}</p>`; }
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  token = document.querySelector("#token").value.trim();
  try { sessionStorage.setItem(KEY, token); } catch { /* tab memory only */ }
  await open();
  if (main.dataset.state === "signin") document.querySelector("#token-error").textContent = t("signin.refused");
});

if (token) open(); else ask();
