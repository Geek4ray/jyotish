import { getStatic, pollReading, source } from "./api.js";
import { chrome } from "./chrome.js";
import { renderFailure, renderProgress, renderReading, renderTiming } from "./render.js";

const screen = document.body.dataset.screen;          // "reading" or "timing"
chrome(screen === "timing" ? "when" : "reading");
const root = document.querySelector("#reading");

// The chart behind the reading, once the job has one (GET /readings/{id} gives its chart id).
function chartLink(status) {
  if (!status.chart_id) return "";
  const asOf = status.reading && status.reading.as_of ? `&as_of=${encodeURIComponent(status.reading.as_of)}` : "";
  return `<p class="chart-link"><a href="/chart.html?chart=${encodeURIComponent(status.chart_id)}${asOf}">The chart: D1, D9, D10, dashas and strengths →</a></p>`;
}

function show(status) {
  root.dataset.state = status.status;
  if (status.status === "done") {
    root.innerHTML = chartLink(status) + (screen === "timing" ? renderTiming(status.reading) : renderReading(status.reading));
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
