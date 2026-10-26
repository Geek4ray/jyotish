import { getReading, getStatic, pollReading, source } from "./api.js";
import { chrome } from "./chrome.js";
import { renderFailure, renderProgress, renderReading, renderTiming } from "./render.js";
import { t } from "./strings.js";
import { follow } from "./live.js";

const screen = document.body.dataset.screen;          // "reading" or "timing"
chrome(screen === "timing" ? "when" : "reading");
const root = document.querySelector("#reading");

// The chart behind the reading, once the job has one (GET /readings/{id} gives its chart id).
function chartLink(status) {
  if (!status.chart_id) return "";
  const asOf = status.reading && status.reading.as_of ? `&as_of=${encodeURIComponent(status.reading.as_of)}` : "";
  return `<p class="chart-link"><a href="/chart.html?chart=${encodeURIComponent(status.chart_id)}${asOf}">The chart: D1, D9, D10, dashas and strengths →</a></p>`;
}

// The print view (2026-10-25): the client's view alone, or both views, by a switch. "Both" opens every
// "For the astrologer" toggle for the printout and closes again the ones that were closed.
function printBar() {
  return `<div class="print-bar" role="group" aria-label="${t("print.label")}"><span class="small muted">${t("print.label")}:</span>
    <label><input type="radio" name="print-view" value="client"${document.body.dataset.print === "both" ? "" : " checked"}> ${t("print.client")}</label>
    <label><input type="radio" name="print-view" value="both"${document.body.dataset.print === "both" ? " checked" : ""}> ${t("print.both")}</label>
    <button type="button" class="button secondary" id="print-go">${t("print.go")}</button></div>`;
}

document.body.dataset.print = "client";
let reopened = [];
window.addEventListener("beforeprint", () => {
  if (document.body.dataset.print !== "both") return;
  reopened = [...document.querySelectorAll("details.for-astrologer:not([open])")];
  reopened.forEach((d) => { d.open = true; });
});
window.addEventListener("afterprint", () => { reopened.forEach((d) => { d.open = false; }); reopened = []; });

function wirePrint() {
  root.querySelectorAll('input[name="print-view"]').forEach((r) =>
    r.addEventListener("change", () => { if (r.checked) document.body.dataset.print = r.value; }));
  const go = root.querySelector("#print-go");
  if (go) go.addEventListener("click", () => window.print());
}

let following = false;

function show(status) {
  // The instant page (2026-10-26): a running job with a reading shows it at once, narration pending, and
  // the narration fills in as it is written and checked (live.js); the page is drawn once, then followed.
  if (status.status === "running" && status.reading) {
    if (following) return;
    following = true;
    root.dataset.state = "pending";
    root.innerHTML = chartLink(status) + (screen === "timing" ? renderTiming(status.reading) : renderReading(status.reading));
    if (screen !== "timing") follow(status.id, root, async () => show(await getReading(status.id)));
    return;
  }
  if (following && status.status !== "done" && status.status !== "failed") return;
  root.dataset.state = status.status;
  if (status.status === "done") {
    root.innerHTML = chartLink(status) + (screen === "timing" ? renderTiming(status.reading) : printBar() + renderReading(status.reading));
    wirePrint();
    document.title = `${screen === "timing" ? "When" : "Reading"}: ${status.reading.question} — Jyotish Engine`;
  } else if (status.status === "failed") {
    root.innerHTML = chartLink(status) + renderProgress(status) + renderFailure(status);
  } else {
    root.innerHTML = chartLink(status) + renderProgress(status);
  }
}

const { id, src } = source();
try {
  if (id) await pollReading(id, show);
  else if (src) show(await getStatic(src));
  else show({ status: "failed", progress: { log: [] }, error: { message: "No reading named: start from the home page." } });
} catch (e) {
  show({ status: "failed", progress: { log: [] }, error: { message: e.message } });
}
