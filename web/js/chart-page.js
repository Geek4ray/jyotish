// The chart display: the engine's SVG (D1, D9, D10, North-Indian) and its tables, all from
// GET /charts/{id}/chart.svg and /charts/{id}/tables.json. Nothing here computes.
import { chrome } from "./chrome.js";
import { esc, num, table } from "./render.js";

chrome("chart");
const root = document.querySelector("#chart");
const params = new URLSearchParams(location.search);
const id = params.get("chart");
const asOf = params.get("as_of");

function period(p) {
  return `<span>${esc(p.lords.join("–"))}: ${esc(p.start)} to ${esc(p.end)}${p.current ? " <strong class=\"current\">(now)</strong>" : ""}</span>`;
}

function dashaTree(v) {
  return `<p class="small">Current period on ${esc(v.as_of)}: <strong class="current-period">${esc(v.current.join(" – "))}</strong></p>
    <ul class="dasha-tree">${v.mahas.map((m) => `<li data-lords="${esc(m.lords.join("-"))}"${m.current ? " data-current" : ""}>
      <details${m.current ? " open" : ""}><summary>${period(m)}</summary>
        <ul>${m.antars.map((a) => `<li data-lords="${esc(a.lords.join("-"))}"${a.current ? " data-current" : ""}>
          <details${a.current ? " open" : ""}><summary>${period(a)}</summary>
            <ul>${a.pratyantars.map((x) => `<li data-lords="${esc(x.lords.join("-"))}"${x.current ? " data-current" : ""}>${period(x)}</li>`).join("")}</ul>
          </details></li>`).join("")}</ul>
      </details></li>`).join("")}</ul>
    <p class="muted tiny">${esc(v.note)}</p>`;
}

function render(t, svgText) {
  const c = t.chart;
  const av = t.ashtakavarga;
  const bavRows = Object.entries(av.bav).map(([p, row]) => ({ planet: p, ...Object.fromEntries(av.signs.map((s, i) => [s.slice(0, 3), row[i]])) }));
  bavRows.push({ planet: "SAV", ...Object.fromEntries(av.signs.map((s, i) => [s.slice(0, 3), av.sav[i]])) });
  return `
    <section class="identity">
      <span class="kicker">The chart</span>
      <h1 class="display">${esc(c.lagna)} lagna, ascendant ${esc(c.ascendant_degree)} in ${esc(c.ascendant_nakshatra)}</h1>
      <p class="header-line">Born ${esc(c.birth_utc)} UTC · ayanamsa ${esc(c.ayanamsa)} · node ${esc(c.node)} · houses ${esc(c.house_system)} · engine ${esc(c.engine)}</p>
    </section>
    <section class="card chart-figure" id="chart-svg">${svgText}</section>
    <section class="card" id="planets"><h2>Planets</h2>${table(t.planets)}</section>
    <section class="card" id="vimshottari"><h2>Vimshottari to the pratyantar</h2>${dashaTree(t.vimshottari)}</section>
    <section class="card" id="shadbala"><h2>Shadbala (${esc(t.shadbala.unit)})</h2>${table(t.shadbala.rows)}</section>
    <section class="card" id="ashtakavarga"><h2>Ashtakavarga: BAV by planet and SAV, by sign</h2>${table(bavRows)}</section>
    <section class="card" id="bhava-bala"><h2>Bhava Bala (${esc(t.bhava_bala.unit)}, ${esc(t.bhava_bala.house_system)})</h2>${table(t.bhava_bala.rows)}</section>`;
}

try {
  if (!id) throw new Error("No chart named: open it from a reading.");
  const q = asOf ? `?as_of=${encodeURIComponent(asOf)}` : "";
  const [tr, sr] = await Promise.all([fetch(`/charts/${encodeURIComponent(id)}/tables.json${q}`),
                                      fetch(`/charts/${encodeURIComponent(id)}/chart.svg`)]);
  if (!tr.ok || !sr.ok) throw new Error(tr.status === 404 ? "No such chart." : `could not load the chart (${tr.status})`);
  root.innerHTML = render(await tr.json(), await sr.text());
  root.dataset.state = "done";
} catch (e) {
  root.innerHTML = `<section class="card"><p class="error">${esc(e.message)}</p></section>`;
  root.dataset.state = "failed";
}
