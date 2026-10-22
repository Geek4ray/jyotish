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

// The three dispositor chains as arrows; the planets of the loop each chain ends in are marked.
function chains(d) {
  const kinds = [["sign", "Sign"], ["nakshatra", "Nakshatra"], ["navamsa", "Navamsa (D9)"]];
  return kinds.map(([k, label]) => {
    const block = d[k];
    const rows = block.rows.map((r) => {
      const inLoop = new Set(r.loop);
      const back = r.loop.length > 1 ? ` <span class="loop-back" title="back to ${esc(r.loop[0])}">⟲ ${esc(r.loop.join("–"))}</span>`
        : ` <span class="loop-back" title="self-disposited">⟲ self</span>`;
      return `<li data-planet="${esc(r.planet)}" data-kind="${k}">${r.chain.map((p) => `<span class="${inLoop.has(p) ? "in-loop" : ""}">${esc(p)}</span>`).join(" → ")}${back}</li>`;
    }).join("");
    const loops = block.loops.map((l) => `<span class="loop-chip">${esc(l.length > 1 ? `${l.join("–")} loop` : `${l[0]}, self-disposited`)}</span>`).join(" ");
    return `<div class="chain-kind" data-kind="${k}"><h3>${esc(label)}</h3><p class="small">Ends in: ${loops}</p><ul class="chain-list">${rows}</ul></div>`;
  }).join("");
}

function points(np) {
  if (!np) return `<p class="muted small">Not computed for this chart (stored before the points were).</p>`;
  const row = (name, p) => ({ point: name, from: p.origin, sign: p.sign, nakshatra: `${p.nakshatra} ${p.pada}`,
    "nakshatra lord": p.nakshatra_lord, "navamsa sign": p.navamsa_sign, "navamsa lord": p.navamsa_lord });
  const rows = Object.values(np.navamsa_64).map((p) => row("64th navamsa", p));
  const nth = (d) => ["1st", "2nd", "3rd"][d - 1];
  const rows22 = Object.values(np.drekkana_22 || {}).map((p) => ({ point: "22nd drekkana", from: p.origin,
    span: `${p.sign} ${nth(p.drekkana)} drekkana (${(p.start % 30).toFixed(0)}°–${(p.start % 30 + 10).toFixed(0)}°)`,
    "D3 sign": p.d3_sign, lord: p.lord }));
  const lag = np.nakshatra_lagnesha;
  return `${table(rows)}${rows22.length ? table(rows22) : `<p class="muted small">The 22nd drekkana: not computed for this chart (stored before it replaced the 88th pada).</p>`}
    <p class="small">Abhijit (276°40′ to 280°53′20″): ${np.abhijit.occupants.length ? esc(np.abhijit.occupants.join(", ")) : "no body or lagna in it"}.</p>
    <p class="small">Nakshatra lagnesha (lord of the lagna's nakshatra, ${esc(lag.lagna_nakshatra)}): <strong>${esc(lag.planet)}</strong>, in ${esc(lag.sign)} (the ${esc(lag.house)}), ${esc(lag.nakshatra)}, ${esc(lag.dignity || "–")}.</p>
    <p class="muted tiny">Sources: ${Object.entries(np.sources).map(([k, s]) => `${esc(k.replaceAll("_", " "))}: ${esc(s.text)}${s.checked ? "" : " (not yet checked)"}`).join(" · ")}.</p>`;
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
    <section class="card" id="bhava-bala"><h2>Bhava Bala (${esc(t.bhava_bala.unit)}, ${esc(t.bhava_bala.house_system)})</h2>${table(t.bhava_bala.rows)}</section>
    <section class="card" id="nakshatras"><h2>Nakshatras: lords, KP sub-lords, Navatara and attributes</h2>${table(t.nakshatras.rows)}
      <p class="muted tiny">Attribute sources: ${Object.entries(t.nakshatras.sources).map(([k, s]) => `${esc(k.replaceAll("_", " "))}: ${esc(s.text)}${s.chapter ? ` ch. ${esc(s.chapter)}` : ""}${s.checked ? "" : " (not yet checked)"}`).join(" · ")}.</p></section>
    <section class="card" id="nakshatra-points"><h2>Special nakshatra points</h2>${points(t.nakshatra_points)}</section>
    <section class="card" id="dispositors"><h2>Dispositor chains</h2>${chains(t.dispositors)}</section>`;
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
