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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const f = form.elements;
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
