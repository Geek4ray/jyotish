import { postReading } from "./api.js";
import { chrome } from "./chrome.js";

chrome("home");
const form = document.querySelector("#birth-form");
const tz = form.elements.tz;
if (!tz.value) {
  try { tz.value = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch { /* leave empty */ }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const f = form.elements;
  const time = f.time.value.length === 5 ? `${f.time.value}:00` : f.time.value;
  const body = {
    date: f.date.value, time, tz: f.tz.value.trim(), lat: Number(f.lat.value), lon: Number(f.lon.value),
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
