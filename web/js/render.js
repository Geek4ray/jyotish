// Rendering the reading JSON (the SPEC Layer 7 output schema) into the page. Every number and
// every tier or stability word comes from the JSON: nothing here computes, rounds beyond
// display precision, or rewords an engine field. Text from the JSON is always escaped.

const TAG = /\[(rule|text|vote):([^\]\s]+)\]/g;

export function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// Numbers as page.py shows them: three significant figures for a cell, two decimals for the
// three stability numbers.
export function num(x) {
  if (x === null || x === undefined) return "–";
  if (typeof x !== "number") return esc(x);
  return Number.isInteger(x) ? String(x) : String(parseFloat(x.toPrecision(3)));
}
const fixed2 = (x) => (x === null || x === undefined ? "–" : x.toFixed(2));

function cell(v) {
  if (v === null || v === undefined) return "–";
  if (typeof v === "boolean") return v ? "yes" : "no";
  if (typeof v === "number") return num(v);
  if (Array.isArray(v)) return v.length ? v.map((x) => (x && typeof x === "object" ? compact(x) : cell(x))).join(", ") : "–";
  if (typeof v === "object") return compact(v);
  return esc(v);
}
const compact = (o) => Object.entries(o).map(([k, v]) => `${esc(k)} ${cell(v)}`).join(" ");
const human = (s) => String(s).replaceAll("_", " ");
const family = (f) => (f === "kp" ? "KP" : f);
const title = (s) => human(s).replace(/^./, (c) => c.toUpperCase());

export function table(rows, columns) {
  if (!rows || !rows.length) return `<p class="muted small">(no rows)</p>`;
  const cols = columns || [...new Set(rows.flatMap((r) => Object.keys(r)))];
  const isNum = (c) => rows.every((r) => r[c] === null || r[c] === undefined || typeof r[c] === "number");
  const head = cols.map((c) => `<th class="${isNum(c) ? "num" : ""}" scope="col">${esc(human(c))}</th>`).join("");
  const body = rows.map((r) => `<tr>${cols.map((c) => `<td class="${isNum(c) ? "num" : ""}">${cell(r[c])}</td>`).join("")}</tr>`).join("");
  return `<div class="table-scroll"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

// --- footnotes: one number per distinct tag across the page --------------------------------

export class Footnotes {
  constructor() { this.order = []; }
  number(tag) {
    if (!this.order.includes(tag)) this.order.push(tag);
    return this.order.indexOf(tag) + 1;
  }
  // Tags that follow one another (only spaces between) become one superscript: "1,2".
  group(tags) {
    const links = tags.map((tag) => {
      const n = this.number(tag);
      return `<a class="fn-ref" href="#fn-${n}" data-tag="${esc(tag)}" aria-label="footnote ${n}">${n}</a>`;
    });
    return `<sup class="fns">${links.join(",")}</sup>`;
  }
  // Claim or summary text with its tags turned into footnote references.
  text(s) {
    s = String(s);
    let out = "", last = 0, pending = [];
    const flush = () => { if (pending.length) { out += this.group(pending); pending = []; } };
    for (const m of s.matchAll(TAG)) {
      const between = s.slice(last, m.index);
      if (pending.length && between.trim() === "") {
        pending.push(`${m[1]}:${m[2]}`);
      } else {
        flush();
        out += esc(between).replace(/\s+$/, "");
        pending.push(`${m[1]}:${m[2]}`);
      }
      last = m.index + m[0].length;
    }
    flush();
    return out + esc(s.slice(last));
  }
  definition(tag) {
    const [kind, value] = [tag.slice(0, tag.indexOf(":")), tag.slice(tag.indexOf(":") + 1)];
    if (kind === "rule") return `Rule <code>${esc(value)}</code>, from the engine's rule library.`;
    if (kind === "text") {
      const [text, edition, chapter, verse] = value.split("/");
      return `${esc(text)}, ${esc(edition.replaceAll("-", " "))}, chapter ${esc(chapter)}, verse ${esc(verse)} (checked in that edition).`;
    }
    const [area, fam] = value.split(".");
    return `The ${esc(family(fam))} family's vote on ${esc(human(area))}, derived by the engine (see the claim's learner panel).`;
  }
  html() {
    return this.order.map((t, i) => `<li id="fn-${i + 1}" data-tag="${esc(t)}"><code>${esc(t)}</code>: ${this.definition(t)}</li>`).join("");
  }
}

// --- pieces -------------------------------------------------------------------------------

export function headerLine(chart) {
  if (!chart || !chart.conventions) return "";
  const c = chart.conventions;
  const local = chart.local_date ? `${esc(chart.local_date)} ${esc(chart.local_time)} (${esc(chart.tz_input)})` : "local time not given";
  // Birth data and conventions in full (the header reproduces the reading), never rounded.
  return `Born ${local} = ${esc(chart.birth_utc)} UTC, ${esc(chart.place || "place not named")} (${esc(chart.lat)}, ${esc(chart.lon)}) · `
    + `accuracy ${esc(chart.accuracy)} · ayanamsa ${esc(c.ayanamsa)} · node ${esc(c.node)} · houses ${esc(human(c.house_system))} `
    + `(KP ${esc(c.kp_house_system)}) · dasha year ${esc(c.dasha_year)} days · karaka scheme ${esc(c.karaka_scheme)}`;
}

function stabilityText(st) {
  return st ? `time ${fixed2(st.time)} · ayanamsa ${fixed2(st.ayanamsa)} · house ${fixed2(st.house)} (${esc(st.label)})` : "–";
}

function windowRows(windows, avoid) {
  const rows = [...windows.map((w) => ["window", w]), ...(avoid ? [["avoid", avoid]] : [])];
  const body = rows.map(([label, w]) => {
    const sp = w.strongest_piece;
    return `<tr class="${label === "avoid" ? "avoid" : ""}" data-window="${label}">
      <td>${label}</td><td>${esc(w.start)}</td><td>${esc(w.end)}</td>
      <td class="num">${num(w.score)}</td><td class="num">${num(w.q)}</td><td class="num">${num(w.t)}</td>
      <td>${cell(w.why.filter((x) => x.kind === "dasha" && x.system === "vimshottari").map((x) => x.lords.join("–")))}</td>
      <td>${cell(w.relevant_systems)}</td>
      <td>${sp ? `${esc(sp.start)} – ${esc(sp.end)} (score ${num(sp.score)}, t ${num(sp.t)})` : "–"}</td>
      <td class="num">${num(w.stability)}</td><td>${cell(w.sandhi)}</td><td>${cell(w.truncated)}</td></tr>`;
  }).join("");
  return `<div class="table-scroll"><table class="windows"><thead><tr><th></th><th>start</th><th>end</th>
    <th class="num">score</th><th class="num">q</th><th class="num">t</th><th>Vimshottari</th><th>systems</th>
    <th>strongest piece</th><th class="num">edge movement (days)</th><th>sandhi</th><th>truncated</th></tr></thead>
    <tbody>${body}</tbody></table></div>`;
}

const SUDARSHANA = "is the engine's Sudarshana reading (counting from that body as lagna). The texts define the yoga "
  + "from the ascendant, so the text citations belong to the lagna fire and this one is cited to the rule only.";

function derivation(d) {
  if (!d || (Array.isArray(d) && !d.length)) return `<p class="muted small">(no derivation rows)</p>`;
  if (Array.isArray(d)) return table(d);
  return Object.entries(d).map(([k, v]) => `<h3>${esc(human(k))}</h3>${Array.isArray(v) ? table(v) : `<p>${cell(v)}</p>`}`).join("");
}

export function learnerPanel(learner) {
  if (!learner) return "";
  let body;
  if (learner.kind === "rule") {
    const r = learner.rule;
    const bases = learner.fires.map((f) => f.basis);
    body = `<p>Rule block <code>${esc(r.id)}</code>, school ${esc(r.school)}, status ${esc(r.status)}, confidence base ${num(r.confidence_base)}.</p>
      ${table(Object.entries(r.when).map(([k, v]) => ({ condition: k, value: JSON.stringify(v) })))}
      <h3>Modifiers, and where each applied</h3>
      ${table(learner.modifiers.map((m) => ({ modifier: m.modifier, scale: `×${num(m.scale)}`, ...Object.fromEntries(bases.map((b) => [`from ${b}`, m.applied[b]])) })))}
      <h3>Fires</h3>
      ${table(learner.fires.map((f) => ({ basis: f.basis, nodes: f.nodes, scale: f.scale, stability: f.stability, "cited to": f.cited_to, sudarshana: f.sudarshana })))}
      ${learner.sudarshana_bases.length ? `<p class="muted">Sudarshana: the fire from the ${learner.sudarshana_bases.map(title).join(" and the ")} ${SUDARSHANA}</p>` : ""}`;
  } else {
    body = `<p>Vote ${esc(learner.direction)} (${learner.vote > 0 ? "+" : ""}${num(learner.vote)}), family ${esc(family(learner.family))}, school ${esc(learner.school)}, stability ${num(learner.stability)}, term ${num(learner.term)}.</p>
      ${derivation(learner.derivation)}`;
  }
  return `<details class="learner"><summary>What this rests on (learner)</summary><div class="learner-body">${body}</div></details>`;
}

function claimItem(c, notes) {
  // Marked where it is read when under 0.8 (SPEC Phase 4 item 3 of the page), with the engine's label.
  const shaky = c.stability !== null && c.stability !== undefined && c.stability < 0.8;
  return `<li class="claim" data-finding="${esc(c.finding_id)}"><p class="claim-text">${notes.text(c.text)}${shaky ? ` <span class="sensitive">(time-stability ${num(c.stability)}${c.stability_label ? `, ${esc(c.stability_label)}` : ""})</span>` : ""}</p>${learnerPanel(c.learner)}</li>`;
}

// Findings the writer could not narrate within the checks: named, with the last error, never hidden.
function gapsList(gaps) {
  if (!gaps.length) return "";
  return `<div class="gaps"><h3 class="small">Not narrated within the checks</h3><ul class="small">${gaps.map((g) =>
    `<li data-finding="${esc(g.finding_id)}"><code>${esc(g.finding_id)}</code> (${esc(g.kind)}), last error on attempt ${num(g.attempt)}: <span class="muted">${esc(g.last_error)}</span></li>`).join("")}</ul></div>`;
}

function conflict(sc) {
  const other = sc.schools.find((s) => s !== "parashari");
  return `<p class="conflict">School conflict: the Parashari families (${esc(sc.families[0])}) are ${esc(sc.parashari)}, the ${esc(other === "kp" ? "KP" : title(other))} family (${esc(sc.families[1])}) is ${esc(sc[other])}. The two are not averaged.</p>`;
}

function areaCard(a, notes) {
  const probability = a.probability === null || a.probability === undefined ? "not calibrated" : num(a.probability);
  const polarity = a.polarity.length
    ? a.polarity.map((p) => `${esc(p)} (${cell(a.polarity_touches[p] || [])})`).join("; ") : "none";
  return `<section class="card area" data-area="${esc(a.name)}">
    <div class="area-head"><h2>${esc(title(a.name))}</h2><span class="tier" data-tier="${esc(a.tier)}">${esc(a.tier)}</span></div>
    <dl class="facts">
      <div><dt>Stability</dt><dd class="stability num">${stabilityText(a.stability)}</dd></div>
      <div><dt>Probability</dt><dd class="probability">${probability}</dd></div>
      <div><dt>Classical score</dt><dd class="num">${num(a.score_classical)}</dd></div>
      <div><dt>Families agreeing (weighted)</dt><dd class="num">${num(a.families_agree_w)} of ${num(a.families_total_w)}</dd></div>
      <div><dt>Polarity</dt><dd class="polarity">${polarity}</dd></div>
    </dl>
    ${a.claims.length ? `<ol class="claims">${a.claims.map((c) => claimItem(c, notes)).join("")}</ol>` : (a.narration_gaps || []).length ? "" : `<p class="muted">No claims were drafted for this area.</p>`}
    ${gapsList(a.narration_gaps || [])}
    ${a.school_conflicts.map(conflict).join("")}
    ${a.windows.length || a.avoid_window ? `<h3 class="small">Windows (engine; score = 0.6 q + 0.4 t)</h3>${windowRows(a.windows, a.avoid_window)}` : ""}
    ${a.disclaimer ? `<p class="disclaimer">${esc(a.disclaimer)}</p>` : ""}
  </section>`;
}

function dependsSection(items) {
  const rows = items.map((d) => {
    const what = d.rule || d.vote || `tier ${d.tier}`;
    const extra = d.basis ? ` from ${d.basis}` : d.direction ? `, ${d.direction}` : "";
    return `<li>${esc(d.area)}: ${esc(what)}${esc(extra)}: time-stability ${num(d.stability)} (holds in that share of the birth-time samples)</li>`;
  }).join("");
  return `<section class="card depends" id="depends"><h2>Depends on exact birth time</h2>
    ${items.length ? `<ul>${rows}</ul>` : `<p class="muted">Nothing: every finding offered for these areas holds in at least half the birth-time samples.</p>`}</section>`;
}

const DISCLAIMER_TEXT = {
  health: "This is a classical indication, not a medical assessment; it diagnoses nothing.",
  longevity: "Classical longevity indications are shown as indications only; the engine does not time death.",
  finance: "This is a classical indication, not financial advice; it recommends no trade or investment.",
  third_party: "This describes the relationship as seen from this chart, not the other person's own life.",
};

// --- screens --------------------------------------------------------------------------------

export function renderReading(r) {
  const notes = new Footnotes();
  const s = r.summary;
  const summaryText = notes.text(s.text);
  const areas = r.areas.map((a) => areaCard(a, notes)).join("");
  return `
  <section class="identity">
    <span class="kicker">Your question</span>
    <h1 class="question">${esc(r.question)}</h1>
    <p class="header-line">${headerLine(r.chart)}</p>
    <p class="header-line">As of ${esc(r.as_of)} · engine ${esc(r.engine)} · weights ${esc(r.weights)} · model ${esc(r.model)} · ${num(r.attempts)} attempt(s) · narration ${esc(r.narration_source)}</p>
  </section>
  ${r.narration_complete === false ? `<p class="notice" id="incomplete">Narration incomplete: ${num(r.areas.reduce((n, a) => n + (a.narration_gaps || []).length, 0))} finding(s) were not narrated within the checks${s.source === "engine" ? ", and the summary is the engine's own" : ""}. Every engine field below is complete.</p>` : ""}
  ${r.unchecked_sentences ? `<p class="notice">Offline replay: ${num(r.unchecked_sentences)} sentence(s) have no recorded checker verdict and were not semantically checked; the code validator ran on all of them.</p>` : ""}
  <section class="card summary" data-source="${esc(s.source || "model")}"><h2>Summary</h2>
    ${s.source === "engine" ? `<p class="muted small engine-summary">Written by the engine from its fields: no drafted summary passed the checks.</p>` : ""}
    <p class="summary-text">${summaryText}</p>
    ${s.timing_line && s.source !== "engine" ? `<div class="timing-line"><span class="label">When (engine)</span><span class="timing-text">${esc(s.timing_line)}</span></div>` : ""}
    <div class="chips">
      <span class="chip">Driver: <strong>${esc(s.driver_planet)}</strong>${s.driver_alternates.length ? ` (alternates ${esc(s.driver_alternates.join(", "))})` : ""}</span>
      <span class="chip">Current period (Vimshottari): <strong>${esc(s.current_period || "–")}</strong></span>
      <span class="chip">Top areas: <strong>${esc(s.top_areas.join(", "))}</strong></span>
      <span class="chip">Birth-time window: <strong>${s.time_window_min === null ? "–" : `±${num(s.time_window_min)} min`}</strong></span>
      <span class="chip">Fired rules stable / unstable: <strong>${num(s.stable_findings)} / ${num(s.unstable_findings)}</strong></span>
      <span class="chip">Abstained areas: <strong>${esc(s.abstained_areas.join(", ") || "none")}</strong></span>
    </div>
  </section>
  ${areas}
  ${dependsSection(r.depends_on_birth_time)}
  ${r.disclaimers.length ? `<section class="card"><h2>Disclaimers</h2>${r.disclaimers.map((k) => `<p class="disclaimer">${esc(DISCLAIMER_TEXT[k] || k)}</p>`).join("")}</section>` : ""}
  <section class="card"><h2>Citations</h2><ol class="footnotes" id="footnotes">${notes.html()}</ol></section>`;
}

export function renderTiming(r) {
  const timed = r.areas.filter((a) => a.windows.length || a.avoid_window);
  const body = timed.length ? timed.map((a) => `
    <section class="card accent" data-area="${esc(a.name)}">
      <div class="area-head"><h2>${esc(title(a.name))}</h2><span class="tier" data-tier="${esc(a.tier)}">${esc(a.tier)}</span></div>
      <p class="muted small">The area's static tier is shown beside the windows, never multiplied in. Stability ${stabilityText(a.stability)}.</p>
      ${windowRows(a.windows, a.avoid_window)}
      ${a.windows.map((w, i) => `<details class="learner"><summary>Window ${i + 1}: ${esc(w.start)} – ${esc(w.end)}, q components and why</summary>
        <div class="learner-body">${table(Object.entries(w.q_terms).map(([k, v]) => ({ component: k, value: v })))}
        ${table(w.why.map((x) => (x.kind === "dasha" ? { kind: x.kind, system: x.system, lords: x.lords } : { kind: x.kind, activation: x.activation, targets: x.targets })))}</div></details>`).join("")}
    </section>`).join("") : `<section class="card"><p class="muted">This question was not a "when" question, so the engine computed no windows.</p></section>`;
  return `
  <section class="identity">
    <span class="kicker">Your question</span>
    <h1 class="question">${esc(r.question)}</h1>
    <p class="header-line">${headerLine(r.chart)}</p>
  </section>
  ${r.summary.timing_line ? `<section class="card accent"><div class="timing-line"><span class="label">When (engine)</span><span class="timing-text">${esc(r.summary.timing_line)}</span></div></section>` : ""}
  ${body}
  <p class="muted small">A window is a time when the chart's own signals for the area are activated by period and transit (score = 0.6 q + 0.4 t). It is not a guarantee of an event; whether windows coincide with real events is what the validation set measures.</p>`;
}

// The chart as soon as it is computed: lagna, Moon sign and nakshatra and the UTC moment, so a
// wrong timezone or date shows in the first second; then the reproducing header.
function chartLine(p) {
  const c = p && p.chart;
  if (!c) return "";
  return `<p class="chart-line">Lagna <strong>${esc(c.lagna)}</strong> · Moon in <strong>${esc(c.moon_sign)}</strong>, <strong>${esc(c.moon_nakshatra)}</strong> nakshatra · born <strong>${esc(c.birth_utc)}</strong> UTC</p>
    ${p.header ? `<p class="header-line">${headerLine(p.header)}</p>` : ""}
    <p class="muted tiny">If the lagna or the Moon is not what you expect, check the date, time and timezone.</p>`;
}

export function renderProgress(status) {
  const log = (status.progress && status.progress.log) || [];
  const current = log.length - 1;
  return `<section class="card" id="progress"><h2>${status.status === "failed" ? "Your reading" : "Working on your reading"}</h2>
    ${chartLine(status.progress)}
    <p class="muted small">Status: <strong class="status">${esc(status.status)}</strong>. The chart and its scores come first, then the writer drafts and the checker reads every sentence against the engine's data.</p>
    <ol class="progress-log">${log.map((x, i) => `<li${i === current ? " data-current" : ""}>${esc(x)}</li>`).join("")}</ol></section>`;
}

export function renderFailure(status) {
  const e = status.error || {};
  return `<section class="card" id="failure"><h2>The reading could not be finished</h2>
    <p class="error">${esc(e.message || "unknown error")}</p>
    ${(e.errors || []).length ? `<ul class="small">${e.errors.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : ""}</section>`;
}
