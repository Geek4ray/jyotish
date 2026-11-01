// Tatva, the conversation (SPEC Layer 8): the birth data once, then questions one after another. The client sees
// one answer in plain words, each sentence appearing once it has passed the checks (the server sends nothing else),
// and beside it the chart lights the houses and planets the answer rests on while it is written, settling when it
// is done. No footnote, no engine word, no verification mark: those are the astrologer's, on /review and in the JSON.

import { t } from "./strings.js";

const $ = (s) => document.querySelector(s);
const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn",
  "Aquarius", "Pisces"];
const ABBR = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];
const SHORT = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke" };
const ORD = (n) => n + (n % 10 === 1 && n !== 11 ? "st" : n % 10 === 2 && n !== 12 ? "nd" : n % 10 === 3 && n !== 13 ? "rd" : "th");
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

let sid = null, ascSign = 0, busy = false;

// --- the first message: birth data -------------------------------------------------------------------------
$("#first-line").textContent = t("chat.first");
$("#trust").textContent = t("chat.trust");
$("#message").placeholder = t("chat.placeholder");

const form = $("#birth-form");
const place = $("#place"), listEl = $("#place-list");
let results = [], active = -1, chosen = null, timer = null;

function showList() {
  listEl.innerHTML = results.map((p, i) => `<li role="option" id="place-${i}" data-i="${i}" aria-selected="${i === active}">${esc(p.label)}</li>`).join("");
  listEl.hidden = !results.length;
  place.setAttribute("aria-expanded", String(!!results.length));
}
function choose(p) {
  chosen = p;
  place.value = p.label;
  $("#lat").value = p.lat; $("#lon").value = p.lon; $("#tz").value = p.timezone;
  results = []; showList();
}
place.addEventListener("input", () => {
  chosen = null;
  clearTimeout(timer);
  const q = place.value.trim();
  if (q.length < 2) { results = []; showList(); return; }
  timer = setTimeout(async () => {
    try {
      const r = await fetch(`/places?q=${encodeURIComponent(q)}&limit=8`);
      results = r.ok ? await r.json() : [];
    } catch { results = []; }
    active = -1;
    showList();
  }, 150);
});
place.addEventListener("keydown", (e) => {
  if (listEl.hidden) return;
  if (e.key === "ArrowDown") { active = Math.min(active + 1, results.length - 1); showList(); e.preventDefault(); }
  else if (e.key === "ArrowUp") { active = Math.max(active - 1, 0); showList(); e.preventDefault(); }
  else if (e.key === "Enter" && active >= 0) { choose(results[active]); e.preventDefault(); }
  else if (e.key === "Escape") { results = []; showList(); }
});
listEl.addEventListener("mousedown", (e) => {
  const li = e.target.closest("li");
  if (li) { choose(results[Number(li.dataset.i)]); e.preventDefault(); }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = $("#birth-status");
  const date = $("#date").value, time = $("#time").value;
  if (!date || !time) { status.textContent = t("chat.date_time"); return; }
  if (!chosen) { status.textContent = t("chat.place_pick"); return; }
  $("#draw").disabled = true;
  status.textContent = t("chat.drawing");
  const body = { date, time: time.length === 5 ? `${time}:00` : time, tz: chosen.timezone, lat: chosen.lat, lon: chosen.lon,
    node: "mean", place: chosen.label };
  try {
    const r = await fetch("/sessions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(typeof data.detail === "string" ? data.detail : `${r.status}`);
    history.replaceState(null, "", `?s=${encodeURIComponent(data.id)}`);
    await open(data);
  } catch (err) {
    status.textContent = t("chat.failed_birth", { why: err.message });
    $("#draw").disabled = false;
  }
});

// --- the session ---------------------------------------------------------------------------------------------
async function open(session) {
  sid = session.id;
  $("#first").hidden = true;
  const line = $("#check-line");
  line.textContent = t("chat.check", session.check);
  line.hidden = false;
  $("#ask-area").hidden = false;
  await drawWheel(session.chart_id);
  const turns = Array.isArray(session.turns) ? session.turns : [];
  answered = turns.length;
  chips();
  for (const turn of turns) {
    const answer = addTurn(turn.question);
    if (turn.status === "done") render(answer, turn.answer || [], turn.paragraphs || [0]);
    else if (turn.status === "failed") sorry(answer);
    else follow(turn.n, answer);
  }
  $("#message").focus();
}

// Before the first question each chip names an area, so none is read as a question about the chart's top areas
// (SPEC Layer 8, review C1); once a question is answered, the follow-ups.
const FIRST_CHIPS = ["chat.chip.first.career", "chat.chip.first.marriage", "chat.chip.first.money"];
const NEXT_CHIPS = ["chat.chip.marriage", "chat.chip.when", "chat.chip.why"];
let answered = 0;
function chips() {
  $("#chips").innerHTML = (answered ? NEXT_CHIPS : FIRST_CHIPS)
    .map((k) => `<button type="button">${esc(t(k))}</button>`).join("");
}
$("#chips").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (b) ask(b.textContent);
});
$("#ask-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const m = $("#message").value.trim();
  if (m) ask(m);
});

function addTurn(question) {
  const li = document.createElement("li");
  li.className = "turn";
  li.innerHTML = `<div class="asked"></div><div class="said"><span class="mark" aria-hidden="true"><span></span></span>
    <div class="answer"><p class="waiting writing">${esc(t("chat.reading"))}</p></div></div>`;
  li.querySelector(".asked").textContent = question;
  $("#conversation").append(li);
  li.scrollIntoView({ block: "end", behavior: "smooth" });
  return li.querySelector(".answer");
}

function render(answer, sentences, paragraphs) {
  answer.innerHTML = "";
  const starts = new Set(paragraphs);
  let p = null;
  sentences.forEach((s, i) => {
    if (!p || starts.has(i)) { p = document.createElement("p"); answer.append(p); }
    p.textContent = p.textContent ? `${p.textContent} ${s}` : s;
  });
}

function sorry(answer) {
  answer.innerHTML = `<p class="sorry">${esc(t("chat.sorry"))}</p>`;
}

async function ask(message) {
  if (busy) { $("#reading-now").textContent = t("chat.busy"); return; }
  busy = true;
  $("#send").disabled = true;
  $("#message").value = "";
  const answer = addTurn(message);
  if (!answered++) chips();
  try {
    const r = await fetch(`/sessions/${encodeURIComponent(sid)}/turns`, { method: "POST",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message }) });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.detail || r.status);
    follow(data.n, answer);
  } catch {
    sorry(answer);
    done();
  }
}

function done() {
  busy = false;
  $("#send").disabled = false;
  $("#wheel").classList.add("settled");
  $("#reading-now").textContent = "";
  document.querySelectorAll(".writing").forEach((x) => x.classList.remove("writing"));
}

// The answer as it is written: `light` (what to light on the chart), `text` (a sentence that passed, with whether it
// opens a paragraph), `done`. Server-sent events, with polling where they are not available.
function follow(n, answer) {
  busy = true;
  $("#send").disabled = true;
  $("#wheel").classList.remove("settled");
  document.querySelectorAll("#wheel .lit").forEach((x) => x.classList.remove("lit", "now"));
  let started = false, p = null;
  const on = (e) => {
    if (e.type === "light") light(e.houses || [], e.planets || []);
    else if (e.type === "text") {
      if (!started) { answer.innerHTML = ""; started = true; }
      if (!p || e.para) { if (p) p.classList.remove("writing"); p = document.createElement("p"); answer.append(p); }
      p.classList.add("writing");
      p.textContent = p.textContent ? `${p.textContent} ${e.text}` : e.text;
    } else if (e.type === "done") {
      if (e.status === "failed" && !started) sorry(answer);
      done();
      return true;
    }
    return false;
  };
  const base = `/sessions/${encodeURIComponent(sid)}/turns/${n}`;
  if (window.EventSource) {
    const src = new EventSource(`${base}/events`);
    let finished = false;
    for (const kind of ["light", "text", "done"]) {
      src.addEventListener(kind, (m) => { if (on(JSON.parse(m.data))) { finished = true; src.close(); } });
    }
    src.onerror = () => { if (!finished) { src.close(); poll(base, on); } };
  } else poll(base, on);
}

async function poll(base, on, since = 0) {
  for (let misses = 0; misses < 5;) {
    try {
      const res = await fetch(`${base}/live?since=${since}`);
      if (!res.ok) { misses++; throw new Error(String(res.status)); }
      misses = 0;
      const r = await res.json();
      for (const e of r.events) if (on(e)) return;
      since = r.version;
      if (r.done) {
        const turn = await (await fetch(base)).json();
        on({ type: "done", status: turn.status });
        return;
      }
    } catch { /* try again, up to five refusals in a row */ }
    await new Promise((res) => setTimeout(res, 700));
  }
  on({ type: "done", status: "failed" });
}

// --- the chart, alive ----------------------------------------------------------------------------------------
const C = 170, R_OUT = 150, R_IN = 112, R_HUB = 40, R_BODY = 92;
const NS = "http://www.w3.org/2000/svg";

function degrees(s) {
  const m = String(s).match(/(\d+)°(\d+)′(\d+)?/);
  return m ? Number(m[1]) + Number(m[2]) / 60 + Number(m[3] || 0) / 3600 : 15;
}
let ascLon = 0;
const at = (lon, r) => {
  const a = ((180 + lon - ascLon) * Math.PI) / 180;
  return [C + r * Math.cos(a), C - r * Math.sin(a)];
};
const f = (x) => x.toFixed(1);

function sectorPath(k) {
  const [a0, a1] = [k * 30, k * 30 + 30];
  const [x0, y0] = at(a0, R_OUT), [x1, y1] = at(a1, R_OUT), [x2, y2] = at(a1, R_HUB), [x3, y3] = at(a0, R_HUB);
  return `M${f(x0)},${f(y0)} A${R_OUT},${R_OUT} 0 0 0 ${f(x1)},${f(y1)} L${f(x2)},${f(y2)} A${R_HUB},${R_HUB} 0 0 1 ${f(x3)},${f(y3)} Z`;
}

async function drawWheel(chartId) {
  const svg = $("#wheel");
  let planets = [];
  try { planets = (await (await fetch(`/charts/${encodeURIComponent(chartId)}/tables.json`)).json()).planets; } catch { return; }
  const asc = planets.find((p) => p.planet === "Ascendant");
  ascSign = SIGNS.indexOf(asc.sign);
  ascLon = ascSign * 30 + degrees(asc.degree);
  svg.setAttribute("aria-label", t("chat.wheel", { lagna: asc.sign }));
  let out = "";
  for (let k = 0; k < 12; k++) {
    const house = ((k - ascSign + 12) % 12) + 1;
    out += `<path class="sector" data-house="${house}" d="${sectorPath(k)}"/>`;
  }
  out += `<circle class="ring outer" cx="${C}" cy="${C}" r="164"/><circle class="ring" cx="${C}" cy="${C}" r="${R_OUT}"/>`
    + `<circle class="ring" cx="${C}" cy="${C}" r="${R_IN}"/><circle class="ring outer" cx="${C}" cy="${C}" r="${R_HUB}"/>`;
  for (let k = 0; k < 12; k++) {
    const [x0, y0] = at(k * 30, R_OUT), [x1, y1] = at(k * 30, R_IN);
    out += `<line class="spoke" x1="${f(x0)}" y1="${f(y0)}" x2="${f(x1)}" y2="${f(y1)}"/>`;
    const [lx, ly] = at(k * 30 + 15, (R_OUT + R_IN) / 2);
    const house = ((k - ascSign + 12) % 12) + 1;
    out += `<text class="sign${k === ascSign ? " rising" : ""}" data-house="${house}" x="${f(lx)}" y="${f(ly)}">${ABBR[k]}</text>`;
  }
  const [ax0, ay0] = at(ascLon, 164), [ax1, ay1] = at(ascLon, R_IN);
  out += `<line class="asc" x1="${f(ax0)}" y1="${f(ay0)}" x2="${f(ax1)}" y2="${f(ay1)}"/>`;
  const placed = {};
  for (const p of planets.filter((x) => SHORT[x.planet])) {
    const k = SIGNS.indexOf(p.sign), j = (placed[k] = (placed[k] ?? -1) + 1);
    const lon = k * 30 + Math.min(28, Math.max(2, degrees(p.degree)));
    const [x, y] = at(lon, R_BODY - j * 15);
    out += `<g class="body" data-planet="${p.planet}"><circle class="halo" cx="${f(x)}" cy="${f(y)}" r="14"/>`
      + `<circle class="dot" cx="${f(x)}" cy="${f(y)}" r="4"/><text x="${f(x + 7)}" y="${f(y - 6)}">${SHORT[p.planet]}</text></g>`;
  }
  svg.innerHTML = out;
  $("#sky").hidden = false;
}

function clearNow() { document.querySelectorAll("#wheel .now").forEach((x) => x.classList.remove("now")); }

// Light what a sentence rests on: the newest pulses until the next, everything lit stays lit until the answer
// is done, when the chart settles.
function light(houses, planets) {
  clearNow();
  for (const h of houses) document.querySelectorAll(`#wheel [data-house="${h}"]`).forEach((x) => x.classList.add("lit", "now"));
  for (const p of planets) document.querySelectorAll(`#wheel [data-planet="${p}"]`).forEach((x) => x.classList.add("lit", "now"));
  const said = [...planets.map((p) => (p === "Sun" || p === "Moon" ? `the ${p}` : p)),
    ...houses.map((h) => t("chat.house", { n: ORD(h) }))];
  if (said.length) $("#reading-now").textContent = t("chat.lit", { what: said.join(", ") });
}

// --- start -----------------------------------------------------------------------------------------------------
const asked = new URLSearchParams(location.search).get("s");
if (asked) {
  fetch(`/sessions/${encodeURIComponent(asked)}`).then((r) => (r.ok ? r.json() : null)).then((s) => {
    if (s) open(s);
  });
}
