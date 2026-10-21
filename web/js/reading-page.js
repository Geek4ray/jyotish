import { getStatic, pollReading, source } from "./api.js";
import { chrome } from "./chrome.js";
import { renderFailure, renderProgress, renderReading, renderTiming } from "./render.js";

const screen = document.body.dataset.screen;          // "reading" or "timing"
chrome(screen === "timing" ? "when" : "reading");
const root = document.querySelector("#reading");

function show(status) {
  root.dataset.state = status.status;
  if (status.status === "done") {
    root.innerHTML = screen === "timing" ? renderTiming(status.reading) : renderReading(status.reading);
    document.title = `${screen === "timing" ? "When" : "Reading"}: ${status.reading.question} — Jyotish Engine`;
  } else if (status.status === "failed") {
    root.innerHTML = renderProgress(status) + renderFailure(status);
  } else {
    root.innerHTML = renderProgress(status);
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
