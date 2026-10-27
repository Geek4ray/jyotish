// The live narration (2026-10-26): the reading's sentences as the writer drafts them and the checker
// reads them. A sentence is shown "being verified" until the checker passes it, then "verified"; a unit
// the validator or the checker refuses is removed, and the writer's replacement comes the same way.
// Server-sent events (GET /readings/{id}/events), with polling by version number as the fallback
// (GET /readings/{id}/live?since=N). Nothing here is the reading: when it is done the page is drawn
// again from GET /readings/{id}, which holds only what passed.
import { esc } from "./render.js";
import { t } from "./strings.js";

const TAG = /\s*\[(rule|text|vote|chain|fact|tradition):[^\]]*\]/g;
const plain = (text) => text.replace(TAG, "").replace(/\s+([.,;])/g, "$1").trim();

function kindLabel(unit) {
  const [kind, , sec] = unit.split(":");
  return t(kind === "analysis" ? `live.kind.${sec}` : `live.kind.${kind}`);
}

// Whose view a unit streams into: the client's (the paragraph, the when, what this chart does not tell),
// the astrologer's (the claims and the analysis), or the summary's card.
const CLIENT_UNITS = /^(paragraph|when):|^analysis:[^:]+:not_said_client$/;

function container(root, unit) {
  if (unit === "summary") return root.querySelector('.live-units[data-area="summary"]');
  const area = unit.split(":")[1];
  const audience = CLIENT_UNITS.test(unit) ? "client" : "astrologer";
  return root.querySelector(`.live-units[data-area="${CSS.escape(area)}"][data-audience="${audience}"]`);
}

function unitEl(root, unit) {
  const box = container(root, unit);
  if (!box) return null;
  let el = box.querySelector(`.live-unit[data-unit="${CSS.escape(unit)}"]`);
  if (!el) {
    el = document.createElement("div");
    el.className = "live-unit";
    el.dataset.unit = unit;
    el.innerHTML = `<span class="live-kind small">${esc(kindLabel(unit))}</span><p class="live-text"></p>`;
    box.appendChild(el);
  }
  return el;
}

// A [tradition:] sentence is never checked: it keeps its own mark and is never turned "verified"; a
// judgement, once its premises pass, says the weighing is the reading's (review R3).
function sentenceHtml(i, text, mark) {
  const state = mark === "tradition" ? t("live.tradition") : t("live.verifying");
  return `<span class="live-sentence ${mark === "tradition" ? "unchecked" : "verifying"}" data-i="${i}"${mark ? ` data-mark="${esc(mark)}"` : ""}>${esc(plain(text))} <span class="live-state">${esc(state)}</span></span> `;
}

function verify(span) {
  if (!span.classList.contains("verifying")) return;
  span.classList.replace("verifying", "verified");
  span.querySelector(".live-state").textContent = span.dataset.mark === "judgement" ? t("live.judgement") : t("live.verified");
}

export function applyEvent(root, e) {
  if (e.type === "sentence") {
    const el = unitEl(root, e.unit);
    if (el) el.querySelector(".live-text").insertAdjacentHTML("beforeend", sentenceHtml(e.i, e.text, e.mark));
  } else if (e.type === "unit") {
    const el = unitEl(root, e.unit);
    if (el) el.querySelector(".live-text").innerHTML = e.sentences.map((s, i) => sentenceHtml(i, s, (e.marks || [])[i])).join("");
  } else if (e.type === "verified") {
    const span = root.querySelector(`.live-unit[data-unit="${CSS.escape(e.unit)}"] .live-sentence[data-i="${e.i}"]`);
    if (span) verify(span);
  } else if (e.type === "accepted") {
    const el = root.querySelector(`.live-unit[data-unit="${CSS.escape(e.unit)}"]`);
    if (el) {
      el.classList.add("accepted");
      for (const i of e.verified || []) {
        const span = el.querySelector(`.live-sentence[data-i="${i}"]`);
        if (span) verify(span);
      }
    }
  } else if (e.type === "removed") {
    const el = root.querySelector(`.live-unit[data-unit="${CSS.escape(e.unit)}"]`);
    if (el) el.remove();
  } else if (e.type === "area") {
    const mark = root.querySelector(`.pending[data-area="${CSS.escape(e.area)}"] .pending-mark`);
    if (mark) mark.textContent = t("live.area_done");
  }
}

// Follow a reading's live view until it is done; `onDone(status)` then draws the stored reading.
export function follow(id, root, onDone) {
  let version = 0;
  let finished = false;
  const apply = (e) => {
    if (finished || (e.seq && e.seq <= version)) return;
    if (e.seq) version = e.seq;
    root.dataset.live = String(version);
    if (e.type === "done") {
      finished = true;
      onDone(e.status || "done");
      return;
    }
    applyEvent(root, e);
  };
  const poll = async () => {
    root.dataset.liveMode = "poll";
    while (!finished) {
      let body = null;
      try {
        const r = await fetch(`/readings/${encodeURIComponent(id)}/live?since=${version}`);
        body = r.ok ? await r.json() : null;
      } catch { body = null; }
      if (!body) { finished = true; onDone("unknown"); return; }
      body.events.forEach(apply);
      if (body.done && !finished) { finished = true; onDone(body.status); return; }
      await new Promise((res) => setTimeout(res, 1000));
    }
  };
  if (!window.EventSource || new URLSearchParams(location.search).get("live") === "poll") return poll();
  root.dataset.liveMode = "sse";
  const es = new EventSource(`/readings/${encodeURIComponent(id)}/events?since=${version}`);
  for (const type of ["sentence", "unit", "verified", "accepted", "removed", "area", "done"]) {
    es.addEventListener(type, (m) => {
      const e = JSON.parse(m.data);
      if (e.type === "done") es.close();
      apply(e);
    });
  }
  es.onerror = () => {
    // The browser reconnects by itself (Last-Event-ID); a stream that is closed for good falls back to polling.
    if (!finished && es.readyState === EventSource.CLOSED) poll();
  };
}
