// The reading service (src/jyotish/api.py). The model key lives on the server only; the
// browser sends birth data and a question, never a key.

export async function postReading(body) {
  const r = await fetch("/readings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.map((d) => `${(d.loc || []).slice(1).join(".")}: ${d.msg}`).join("; ") : r.statusText;
    throw new Error(detail || `request failed (${r.status})`);
  }
  return data;
}

export async function getReading(id) {
  const r = await fetch(`/readings/${encodeURIComponent(id)}`);
  if (!r.ok) throw new Error(r.status === 404 ? "No such reading." : `request failed (${r.status})`);
  return r.json();
}

// A reading JSON file served by the site (e.g. /examples/reference_reading.json), shown as a
// finished reading. Same-origin paths only.
export async function getStatic(src) {
  const url = new URL(src, location.href);
  if (url.origin !== location.origin) throw new Error("Only readings served by this site can be shown.");
  const r = await fetch(url);
  if (!r.ok) throw new Error(`could not load ${url.pathname} (${r.status})`);
  return { status: "done", reading: await r.json() };
}

// Poll GET /readings/{id} until done or failed, calling onStatus after each poll.
export async function pollReading(id, onStatus, { interval = 1500, signal } = {}) {
  for (;;) {
    const status = await getReading(id);
    onStatus(status);
    if (status.status === "done" || status.status === "failed") return status;
    await new Promise((res, rej) => {
      const t = setTimeout(res, interval);
      signal?.addEventListener("abort", () => { clearTimeout(t); rej(new DOMException("aborted", "AbortError")); });
    });
  }
}

// The reading named by the page's URL: ?id=<job id> polls the service, ?src=<path> loads a file.
export function source() {
  const p = new URLSearchParams(location.search);
  return { id: p.get("id"), src: p.get("src") };
}

export function withSource(page) {
  const { id, src } = source();
  return id ? `${page}?id=${encodeURIComponent(id)}` : src ? `${page}?src=${encodeURIComponent(src)}` : page;
}
