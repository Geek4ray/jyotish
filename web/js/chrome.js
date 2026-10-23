// The header, footer and phone tab bar shared by every screen (from design/mockups).
import { withSource } from "./api.js";

const MARK = `<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#E8A33D" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2"></rect><path d="M2 2l20 20M22 2L2 22M12 2l10 10-10 10L2 12z"></path></svg>`;
const ICON = {
  home: `<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 11l8-7 8 7v9H4z"></path></svg>`,
  reading: `<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="1"></rect><path d="M3 3l18 18M21 3L3 21M12 3l9 9-9 9-9-9z"></path></svg>`,
  when: `<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path></svg>`,
};

export function chrome(current) {
  const hasReading = new URLSearchParams(location.search).has("id") || new URLSearchParams(location.search).has("src");
  const links = [["home", "/", "Home"], ...(hasReading ? [["reading", withSource("/reading.html"), "Reading"], ["when", withSource("/timing.html"), "When"]] : [])];
  const aria = (k) => (k === current ? ' aria-current="page"' : "");
  document.querySelector("#site-header").innerHTML = `
    <a class="brand" href="/">${MARK}Jyotish Engine</a>
    <nav class="site-nav" aria-label="Main">${links.map(([k, href, label]) => `<a href="${href}"${aria(k)}>${label}</a>`).join("")}
      <a href="/#honest">Honest scope</a></nav>`;
  document.querySelector("#site-footer").innerHTML = `
    <span>Classical signals computed exactly; tier and stability words come from the engine, not the writer. Probability language appears only for calibrated areas, and none are calibrated yet.</span>
    <span>Not medical, legal or financial advice. Place names and coordinates: <a href="https://www.geonames.org/">GeoNames</a>, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Positions by Swiss Ephemeris (AGPL-3.0): <a href="/source">source</a>.</span>`;
  const bar = document.querySelector("#tabbar");
  if (bar) bar.innerHTML = links.map(([k, href, label]) => `<a href="${href}"${aria(k)}>${ICON[k]}${label}</a>`).join("");
}
