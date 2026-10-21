import { postReading } from "./api.js";
import { chrome } from "./chrome.js";

chrome("home");
const form = document.querySelector("#birth-form");
// The timezone list: Asia/Kolkata first, then every zone the browser knows; the browser's own
// zone is preselected. Browsers may still report the old name Asia/Calcutta.
const ALIASES = { "Asia/Calcutta": "Asia/Kolkata" };
const FALLBACK = ["Asia/Kolkata", "UTC", "Europe/London", "America/New_York", "America/Los_Angeles", "Asia/Dubai",
  "Asia/Singapore", "Australia/Sydney"];
function zones() {
  let all;
  try { all = Intl.supportedValuesOf("timeZone"); } catch { all = FALLBACK; }
  all = [...new Set(all.map((z) => ALIASES[z] || z))];
  return ["Asia/Kolkata", ...all.filter((z) => z !== "Asia/Kolkata")];
}
function browserZone() {
  try {
    const z = Intl.DateTimeFormat().resolvedOptions().timeZone;
    return ALIASES[z] || z;
  } catch { return "Asia/Kolkata"; }
}
const tz = form.elements.tz;
const list = zones();
const mine = browserZone();
if (mine && !list.includes(mine)) list.splice(1, 0, mine);
tz.innerHTML = list.map((z) => `<option value="${z}">${z.replaceAll("_", " ")}</option>`).join("");
tz.value = list.includes(mine) ? mine : "Asia/Kolkata";

// --- Place: GeoNames autocomplete that fills latitude, longitude and timezone together ------
const place = form.elements.place, lat = form.elements.lat, lon = form.elements.lon;
const listEl = document.querySelector("#place-list");
const status = document.querySelector("#place-status");
let results = [], active = -1, chosen = null, timer = null;

function setZone(zone) {
  if (![...tz.options].some((o) => o.value === zone)) tz.add(new Option(zone.replaceAll("_", " "), zone), 1);
  tz.value = zone;
}
function closeList() { listEl.hidden = true; place.setAttribute("aria-expanded", "false"); active = -1; }
function showList() {
  listEl.innerHTML = results.map((p, i) => `<li role="option" id="place-${i}" data-i="${i}" aria-selected="${i === active}">
      ${escapeHtml(p.label)}<small>${p.lat.toFixed(4)}, ${p.lon.toFixed(4)} · ${escapeHtml(p.timezone)}</small></li>`).join("");
  listEl.hidden = !results.length;
  place.setAttribute("aria-expanded", String(!!results.length));
  if (active >= 0) place.setAttribute("aria-activedescendant", `place-${active}`);
}
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`); }
function choose(p) {
  chosen = p;
  place.value = p.label;
  lat.value = p.lat;
  lon.value = p.lon;
  setZone(p.timezone);
  closeList();
  status.innerHTML = `<span class="place-status-ok">Filled from GeoNames:</span> ${escapeHtml(p.label)}, ${p.lat}, ${p.lon}, ${escapeHtml(p.timezone)}. Correct the coordinates or timezone below if the birth was elsewhere in the town.`;
  status.dataset.source = "geonames";
}
place.addEventListener("input", () => {
  chosen = null;
  clearTimeout(timer);
  const q = place.value.trim();
  if (q.length < 2) { results = []; closeList(); return; }
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
  else if (e.key === "Escape") closeList();
});
listEl.addEventListener("mousedown", (e) => {
  const li = e.target.closest("li[data-i]");
  if (li) { choose(results[Number(li.dataset.i)]); e.preventDefault(); }
});
place.addEventListener("blur", () => setTimeout(closeList, 100));
// A hand correction after choosing a place is kept, and said.
for (const el of [lat, lon, tz]) {
  el.addEventListener("input", () => {
    if (status.dataset.source === "geonames") {
      status.textContent = "Coordinates or timezone corrected by hand; the reading uses the values below.";
      status.dataset.source = "manual";
    }
  });
}

// Refused before sending (the API refuses them too): empty or out-of-range coordinates, and
// 0, 0, which is what a form left at its defaults would send.
function coordinateProblem() {
  if (lat.value.trim() === "" || lon.value.trim() === "") return "Enter the birthplace's latitude and longitude, or choose the place from the list.";
  const a = Number(lat.value), b = Number(lon.value);
  if (!Number.isFinite(a) || a < -90 || a > 90) return "Latitude must be between -90 and 90.";
  if (!Number.isFinite(b) || b < -180 || b > 180) return "Longitude must be between -180 and 180.";
  if (a === 0 && b === 0) return "Latitude and longitude are both 0, a point in the Gulf of Guinea: enter the birthplace's coordinates.";
  return null;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const f = form.elements;
  const problem = coordinateProblem();
  if (problem) {
    document.querySelector("#form-error").textContent = problem;
    (lat.value.trim() === "" ? lat : lon).focus();
    return;
  }
  const time = f.time.value.length === 5 ? `${f.time.value}:00` : f.time.value;
  const body = {
    date: f.date.value, time, tz: f.tz.value, lat: Number(f.lat.value), lon: Number(f.lon.value),
    accuracy: f.accuracy.value, node: f.node.value, question: f.question.value.trim(),
    ...(f.place.value.trim() ? { place: f.place.value.trim() } : {}),
  };
  const out = document.querySelector("#form-error");
  out.textContent = "";
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    const job = await postReading(body);
    location.assign(`/reading.html?id=${encodeURIComponent(job.id)}`);
  } catch (e) {
    out.textContent = e.message;
    button.disabled = false;
  }
});
