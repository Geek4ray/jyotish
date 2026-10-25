"""The astrologer's technical sheet (2026-10-25; docs/spec_notes_2026-10-24.md, "the two-audience page").

Per area, fifteen numbered points written by the engine from the whole-chart payload
(`fullchart.payload`), with no model call: the figures an astrologer checks by hand, each item one or
two lines and each citing the payload paths it reads, so every figure can be traced to the field that
holds it. The sheet needs only the chart, so it is made at every depth (`build`; the reading carries it
as `ReadingArea.sheet`, and a reading made before it gets it from its chart in `narrate.upgrade_reading`).

Sanskrit terms are written as the texts use them, the English beside on first use in the area's sheet
(`FIRST_USE`). Nothing here weighs or judges: the reading's weighing sentences are quoted verbatim in
point 13, marked as the reading's."""

from __future__ import annotations

from typing import Any

ORD = {1: "1st", 2: "2nd", 3: "3rd"} | {n: f"{n}th" for n in range(4, 13)}
TITLES = {
    1: "Houses (bhava)", 2: "Lords", 3: "Karakas", 4: "Rules and placements fired", 5: "Vargas",
    6: "Nakshatra, tara, dispositor chains and activation", 7: "KP", 8: "Jaimini", 9: "Panchanga",
    10: "The family votes", 11: "Periods and windows", 12: "Transits (gochara)", 13: "The reading's weighing",
    14: "Stability", 15: "Drafts, abstentions and what the engine does not compute",
}
# The English beside a Sanskrit term the first time an area's sheet uses it.
FIRST_USE = {
    "Bhava Bala": "house strength", "rupas": "units of 60 virupas", "Shadbala": "sixfold strength",
    "Baladi avastha": "age-state by degree", "karaka": "significator", "nakshatra": "lunar mansion",
    "tara": "star counted from the Moon's", "vargottama": "the same sign in the D1 and the D9",
    "marana karaka sthana": "a placement in which a planet cannot give its good results",
    "gandanta": "the junction of a water and a fire sign", "pushkara navamsa": "a nourishing navamsa",
    "pushkara bhaga": "a nourishing degree", "KP": "Krishnamurti Paddhati", "sub-lord": "lord of the cusp's sub",
    "arudha": "the image of a house", "panchanga": "the five limbs of the day", "tithi": "lunar day",
    "vara": "weekday", "nitya yoga": "the luni-solar yoga of the day", "Vimshottari": "the 120-year nakshatra dasha",
    "Yogini": "the 36-year dasha of the eight Yoginis", "Chara": "Jaimini's sign dasha",
    "BAV": "the planet's own bindus in its Ashtakavarga", "dasha sandhi": "the junction of two periods",
    "Kantaka Shani": "Saturn in a kendra from the Moon", "ashtama shani": "Saturn in the 8th from the Moon",
    "sade sati": "Saturn over the 12th, 1st and 2nd from the Moon", "yogakaraka": "a planet ruling a kendra and a trikona",
    "maraka": "a lord of the 2nd or the 7th", "boundary": "a sign or nakshatra edge within the birth-time window", "D1": "rasi chart", "D9": "navamsa", "D10": "dasamsa", "D30": "trimsamsa",
    "D2": "hora", "D3": "drekkana", "D4": "chaturthamsa", "D7": "saptamsa", "D11": "rudramsa", "D12": "dwadasamsa",
    "D16": "shodasamsa", "D20": "vimsamsa", "D24": "chaturvimsamsa",
}
VOTE_WORD = {1: "for", -1: "against", 0: "abstains", None: "not applied"}
SLOW = ("Saturn", "Jupiter", "Rahu", "Ketu")
WINDOW_NAMES = {"kantaka_shani": "Kantaka Shani", "ashtama_shani": "ashtama shani", "sade_sati": "sade sati",
                "saturn_return": "Saturn's return", "jupiter_1_5_9_11": "Jupiter in the 1st, 5th, 9th or 11th from the Moon"}


class _Words:
    """A Sanskrit term with its English the first time it is used in one sheet."""

    def __init__(self):
        self.seen: set[str] = set()

    def __call__(self, term: str) -> str:
        if term in self.seen or term not in FIRST_USE:
            return term
        self.seen.add(term)
        return f"{term} ({FIRST_USE[term]})"


def _n(x, spec: str = ".2f") -> str:
    """A figure, or a dash where the engine has none (a node's Shadbala, a missing Bhava Bala)."""
    return "—" if x is None else format(x, spec)


def _item(text: str, *facts: str) -> dict[str, Any]:
    return {"text": text, "facts": [f for f in facts if f]}


def _list(xs) -> str:
    xs = list(xs)
    return ", ".join(xs) if xs else "none"


def _lagna_house_of(data: dict, sign: str) -> int | None:
    return next((int(h) for h, row in data["houses"]["lagna"].items() if row["sign"] == sign), None)


def _bb(data: dict) -> tuple[str, dict]:
    key = (data["houses"].get("system") or {}).get("lagna", "whole_sign")
    key = key if key in data["bhava_bala"] else "whole_sign"
    return key, data["bhava_bala"][key]


def _planet_line(w: _Words, data: dict, p: str, role: str) -> dict[str, Any]:
    """Sign, degree, house, dignity, Shadbala ratio, avastha and sensitive-degree flags of a planet."""
    pl = data["planets"][p]
    parts = [f"{p} — {role}: {pl['sign']} {pl['deg']} in the {ORD[pl['house']]}"]
    if pl.get("dignity"):
        comp = pl.get("dignity_compound")
        parts.append(pl["dignity"] + (f" (compound {comp})" if comp and comp != pl["dignity"] else ""))
    facts = [f"planets.{p}"]
    sb = (data["shadbala"]["planets"] or {}).get(p)
    if sb:
        parts.append(f"{w('Shadbala')} ratio {sb['ratio']:.2f} ({sb['total_rupas']:.2f} of {sb['required_rupas']:.2f} "
                     f"{w('rupas')})")
        facts.append(f"shadbala.planets.{p}")
    if pl.get("avastha_baladi"):
        parts.append(f"{w('Baladi avastha')} {pl['avastha_baladi']}")
    flags = [k for k, v in (data["sensitive"].get(p) or {}).items() if v is True]
    if flags:
        parts.append("; ".join(w(f.replace("_", " ")) for f in flags))
        facts.append(f"sensitive.{p}")
    if pl.get("retro"):
        parts.append("retrograde")
    if pl.get("combust"):
        parts.append("combust")
    roles = (data["roles"].get(p) or [])
    if roles:
        parts.append(", ".join(w(r.replace("_", " ")) for r in roles))
        facts.append(f"roles.{p}")
    return _item("; ".join(parts) + ".", *facts)


# --- the fifteen points ---------------------------------------------------------------------------

def p1_houses(w, data, area, spec, **_):
    key, bb = _bb(data)
    items = []
    for h in spec["houses"]:
        row, b = data["houses"]["lagna"][str(h)], bb[f"H{h}"]
        items.append(_item(f"{ORD[h]} from the lagna: {row['sign']}, lord {row['lord']}, "
                           f"{'occupied by ' + _list(row['occupants']) if row['occupants'] else 'empty'}; "
                           f"{w('Bhava Bala')} {b['rupas']:.2f} {w('rupas')}, rank {b['rank_of_12']} of 12.",
                           f"houses.lagna.{h}", f"bhava_bala.{key}.H{h}"))
    for basis, name in (("moon", "the Moon"), ("sun", "the Sun")):
        parts, facts = [], []
        for h in spec["houses"]:
            row = data["houses"][basis][str(h)]
            lh = _lagna_house_of(data, row["sign"])
            b = bb.get(f"H{lh}") if lh else None
            parts.append(f"{ORD[h]} {row['sign']} (lord {row['lord']}"
                         + (f", {_list(row['occupants'])}" if row["occupants"] else "")
                         + (f"; {b['rupas']:.2f} rupas, rank {b['rank_of_12']}" if b else "") + ")")
            facts += [f"houses.{basis}.{h}"] + ([f"bhava_bala.{key}.H{lh}"] if b else [])
        items.append(_item(f"From {name}: " + "; ".join(parts) + ".", *facts))
    return items


def _lord_roles(data, area) -> dict[str, list[str]]:
    rows = ((data["areas"][area]["votes"].get("lord") or {}).get("derivation") or [])
    out: dict[str, list[str]] = {}
    for r in rows:
        if isinstance(r, dict) and r.get("lord"):
            out.setdefault(r["lord"], []).append(f"{ORD[r['house']]} from the {'lagna' if r['basis'] == 'lagna' else r['basis'].capitalize()}"
                                                 + (f" (bhavat bhavam of the {ORD[r['bhavat_bhavam_of']]})"
                                                    if r.get("bhavat_bhavam_of") else ""))
    return out


def p2_lords(w, data, area, spec, **_):
    roles = _lord_roles(data, area)
    order = list(roles) + [p for p in data["areas"][area]["lords"] if p not in roles]
    return [_planet_line(w, data, p, "lord of the " + ", ".join(roles.get(p, ["area's houses"])))
            for p in order if p in data["planets"]]


def p3_karakas(w, data, area, spec, **_):
    a = data["areas"][area]
    return [_planet_line(w, data, p, ("main " if p == a["main_karaka"] else "") + w("karaka"))
            for p in a["karakas"] if p in data["planets"]]


def _fires(data, area) -> list[tuple[str, dict]]:
    from .scoring import THEME_AREAS
    return [(k, f) for k, f in data["rules"].items()
            if any(area in THEME_AREAS.get(th, []) for th in (f.get("themes") or {}))]


def _source(rule) -> str:
    src = (rule.data.get("source") if rule is not None else None) or []
    src = src if isinstance(src, list) else [src]
    if not src:
        return "no text source (status " + (rule.data.get("status", "?") if rule is not None else "?") + ")"
    out = []
    for s in src:
        if not isinstance(s, dict):
            out.append(str(s))
            continue
        verse = s.get("verse")
        verse = verse if str(verse).startswith("not") else f"v. {verse}"
        where = f"{s.get('text')} ({s.get('edition')}) ch. {s.get('chapter')}, {verse}"
        out.append(where + (", checked" if s.get("checked") else ", not checked"))
    return "; ".join(out)


def p4_rules(w, data, area, spec, **_):
    from .rules import default_rules
    lib = {r.id: r for r in default_rules()}
    items = []
    for key, f in _fires(data, area):
        rule = lib.get(f["id"])
        name = ((rule.data.get("names") or [f["id"]])[0]) if rule is not None else f["id"]
        planets = [n for n in f["nodes"] if not n.startswith("H")]
        why = "; ".join(f.get("applied") or []) or "no reduction"
        items.append(_item(f"{name} [{f['id']}@{f['basis']}]: {_list(planets)}; {_source(rule)}; status {f['status']}; "
                           f"scale {f['scale']:.2f} ({why}).", f"rules.{key}"))
    return items or [_item("No rule or placement fired for this area.")]


def p5_vargas(w, data, area, spec, **_):
    items = []
    for v in spec.get("vargas", []):
        row = data["vargas"][v]
        planets = [f"{p} {x['sign']}" + (f" {x['dignity']}" if x.get("dignity") else "") for p, x in row.items() if p != "Asc"]
        lag = row.get("Asc", {}).get("sign")
        st = (data["stability"].get("lagna_sign_by_varga") or {}).get(v) or {}
        items.append(_item(f"{w(v)}: " + "; ".join(planets) + ".", f"vargas.{v}"))
        items.append(_item(f"{v} lagna {lag}, {st.get('samples') or 'stability not sampled'}.",
                           f"vargas.{v}.Asc", f"stability.lagna_sign_by_varga.{v}"))
    vg = [p for p, pl in data["planets"].items() if pl.get("vargottama")]
    items.append(_item(f"{w('vargottama')}: {_list(vg)}.", *([f"planets.{p}.vargottama" for p in vg] or ["planets"])))
    return items


def _primary(data, area, spec) -> tuple[str, str]:
    return data["houses"]["lagna"][str(spec["houses"][0])]["lord"], data["areas"][area]["main_karaka"]


def p6_nakshatra(w, data, area, spec, **_):
    lord, karaka = _primary(data, area, spec)
    cur = (data["vimshottari"].get("current") or "").split("-")
    items = []
    for p, role in ((lord, f"{ORD[spec['houses'][0]]} lord"), (karaka, f"main {w('karaka')}")):
        if p not in data["nakshatras"]:
            continue
        n = data["nakshatras"][p]
        items.append(_item(f"{p} ({role}): {w('nakshatra')} {n['nakshatra']} pada {n['pada']}, lord {n['lord']}; "
                           f"{w('tara')} {n['tara_from_moon']} (cycle {n.get('cycle')}).", f"nakshatras.{p}"))
        chains = []
        for kind in ("sign", "nakshatra", "navamsa"):
            d = data["dispositors"][kind]
            chain = d["chains"].get(p) or [p]
            chains.append(f"{kind} {' → '.join(chain)} (finals {_list(d['final'])})")
        items.append(_item(f"{p}'s dispositor chains: " + "; ".join(chains) + ".",
                           f"dispositors.sign.chains.{p}", f"dispositors.nakshatra.chains.{p}",
                           f"dispositors.navamsa.chains.{p}"))
        acts = []
        for lvl, q in zip(("major period", "sub-period"), cur[:2]):
            act = data["period_quality"].get(q, {}).get("activation") or []
            acts.append(f"the {q} {lvl} activates {_list(act)}" + (f" ({p} among them)" if p in act else ""))
        if acts:
            items.append(_item(f"Activation at the reading date: " + "; ".join(acts) + ".",
                               "vimshottari.current", *[f"period_quality.{q}.activation" for q in cur[:2]]))
    return items


def p7_kp(w, data, area, spec, **_):
    v = data["areas"][area]["votes"].get("kp")
    if not v:
        return [_item(f"{w('KP')}: no cusp is mapped to this area.")]
    rows = [r for r in (v.get("derivation") or []) if isinstance(r, dict)]
    if not rows:
        return [_item(f"{w('KP')}: verdict {VOTE_WORD.get(v['vote'], v['vote'])}.", f"areas.{area}.votes.kp")]
    c = rows[0]
    items = [_item(f"{w('KP')} cusp {c['cusp']}: star lord {c['cusp_star']}, {w('sub-lord')} {c['sub']}; matter houses "
                   f"{_list(map(str, c['matter_houses']))}, denial houses {_list(map(str, c['denial_houses']))}.",
                   f"lagnas.kp_cusps.H{c['cusp']}", f"areas.{area}.votes.kp.derivation")]
    for r in rows:
        items.append(_item(f"{r['level']}: {r['planet']} signifies {_list(map(str, r['significations']))} (matter "
                           f"{_list(map(str, r['meets_matter']))}, denial {_list(map(str, r['meets_denial']))}): "
                           f"{r['outcome']}{', decides' if r.get('decides') else ''}.", f"areas.{area}.votes.kp.derivation"))
    items.append(_item(f"KP verdict: {VOTE_WORD.get(v['vote'], v['vote'])}.", f"areas.{area}.votes.kp.vote"))
    return items


def p8_jaimini(w, data, area, spec, **_):
    v = data["areas"][area]["votes"].get("arudha")
    if not v or not isinstance(v.get("derivation"), dict):
        return [_item(f"Jaimini: no {w('arudha')} is mapped to this area.")]
    d = v["derivation"]
    items = [_item(f"{w('arudha')} {pd['pada']}: {pd['sign']}, {ORD[pd['house']]} from the {pd['basis']}; occupants "
                   f"{_list(pd.get('occupants', []))}; benefics {_list(pd.get('benefics', []))}.",
                   f"areas.{area}.votes.arudha.derivation", f"jaimini.arudhas.{pd['pada']}")
             for pd in d.get("padas", [])]
    items.append(_item(f"Jaimini verdict: {VOTE_WORD.get(v['vote'], v['vote'])} — {d.get('why', '')}.",
                       f"areas.{area}.votes.arudha"))
    return items


def p9_panchanga(w, data, area, spec, **_):
    pc = data["panchanga"]
    lords = [("tithi", pc.get("tithi_lord")), ("vara", pc.get("vara_lord")), ("nakshatra", pc.get("nakshatra_lord")),
             ("nitya yoga", pc.get("yoga_lord"))]
    items = [_item(f"{w(k)} lord {p}, ruling the " + _list(ORD[h] for h in (data["lordship"].get(p) or []))
                   + " from the lagna." if data["lordship"].get(p) else f"{w(k)} lord {p}, ruling no house.",
                   "panchanga", f"lordship.{p}" if p in data["lordship"] else "")
             for k, p in lords if p]
    v = data["areas"][area]["votes"].get("panchanga")
    for r in ((v or {}).get("derivation") or []):
        if isinstance(r, dict) and r.get("planet"):
            houses = "; ".join(f"{ORD[x['house']]} from the {x['basis']}" for x in r.get("rules", []))
            items.append(_item(f"For this area: {r['planet']} ({_list(r.get('role', []))} lord) rules {houses or 'none of its houses'}.",
                               f"areas.{area}.votes.panchanga.derivation"))
    return items


def _rests_on(fam: str, v: dict, data: dict) -> str:
    d = v.get("derivation")
    rows = [r for r in d if isinstance(r, dict)] if isinstance(d, list) else []
    if fam == "house" and rows:
        r = rows[0]
        return f"{ORD[r['house']]} {r['sign']}, {_n(r['bhava_bala_rupas'])} rupas, relative {_n(r['relative'], '+.2f')}"
    if fam == "lord" and rows:
        r = rows[0]
        return f"{r['lord']}, {ORD[r['house']]} lord, {r['dignity'] or 'no dignity'}, ratio {_n(r['shadbala_ratio'])}"
    if fam == "karaka" and rows:
        r = rows[0]
        return f"{r['planet']} in the {ORD[r['house']]}, {r['dignity'] or 'no dignity'}, ratio {_n(r['shadbala_ratio'])}"
    if fam == "varga" and rows:
        top = sorted(rows, key=lambda r: -abs(r.get("score", 0)))[:2]
        return f"{rows[0]['varga']}: " + ", ".join(f"{r['planet']} {r['varga_dignity_label']} ({_n(r['score'], '+.2f')})" for r in top)
    if fam == "arudha" and isinstance(d, dict):
        return d.get("why", "")
    if fam == "kp" and rows:
        dec = next((r for r in rows if r.get("decides")), rows[-1])
        return f"cusp {dec['cusp']}, {dec['level']} {dec['planet']}: {dec['outcome']}"
    if fam == "panchanga" and rows:
        return ", ".join(f"{r['planet']} ({'/'.join(r.get('role', []))})" for r in rows)
    return "—"


def p10_votes(w, data, area, spec, **_):
    a = data["areas"][area]
    pct = {r["family"]: r.get("percentile") for r in (a.get("contributions") or {}).get("ranked", [])}
    rows = [{"family": fam, "vote": VOTE_WORD.get(v["vote"], v["vote"]), "rests on": _rests_on(fam, v, data),
             "percentile": pct.get(fam)} for fam, v in a["votes"].items()]
    return [_item(f"{len(rows)} families; the percentile is each term's against 10,000 random charts.",
                  f"areas.{area}.votes", f"areas.{area}.contributions")], \
        {"columns": ["family", "vote", "rests on", "percentile"], "rows": rows}


def p11_periods(w, data, area, spec, **_):
    items = []
    vim = data["vimshottari"]
    cur = vim.get("current") or ""
    lords = cur.split("-")
    spans = []
    for i, level in zip(range(1, len(lords) + 1), ("major period", "sub-period", "sub-sub-period")):
        key = "-".join(lords[:i])
        per = vim["periods"].get(key)
        if per:
            spans.append(f"{level} {lords[i - 1]} {per['start']} → {per['end']}")
    items.append(_item(f"{w('Vimshottari')} at the reading date: " + "; ".join(spans) + ".", "vimshottari.current",
                       *[f"vimshottari.periods.{'-'.join(lords[:i])}" for i in range(1, len(lords) + 1)]))
    for p in dict.fromkeys(lords):
        if p in data["planets"]:
            pl, pq = data["planets"][p], data["period_quality"].get(p, {})
            items.append(_item(f"{p}: {pl.get('dignity') or 'no dignity (node)'}, {w('tara')} {pl['tara_from_moon']}, "
                               f"activates {_list(pq.get('activation') or [])}.", f"planets.{p}",
                               f"period_quality.{p}"))
    y = data["yogini"]["periods"][data["yogini"]["current"]]
    items.append(_item(f"{w('Yogini')}: {y['lords']} ({y['names']}) {y['start']} → {y['end']}.",
                       f"yogini.periods.{data['yogini']['current']}"))
    ch = data["chara"]["periods"][data["chara"]["current"]]
    sl = data["constants"]["sign_lords"]
    signs = ch["lords"].split("-")
    items.append(_item(f"{w('Chara')}: {ch['lords']} (lords {_list(sl.get(s, '?') for s in signs)}) {ch['start']} → "
                       f"{ch['end']}.", f"chara.periods.{data['chara']['current']}", "constants.sign_lords"))
    tm = (data.get("timing") or {}).get(area)
    if not tm:
        items.append(_item("No windows: the timing join was not run for this area."))
        return items
    for i, x in enumerate(tm["windows"]):
        items.append(_item(f"Window {x['start']} → {x['end']}: score {x['score']:.3f} (q {x['q']:.3f}, t {x['t']:.3f}), "
                           f"{_list('–'.join(v) for v in x['periods'].values())}; dignity of {x['dignity_of'] or '—'}; "
                           f"{x.get('confidence') or ''}" + (f"; tags {_list(map(w, x['tags']))}" if x["tags"] else "") + ".",
                           f"timing.{area}.windows.{i}"))
    av = tm.get("avoid")
    if av:
        items.append(_item(f"Avoid {av['start']} → {av['end']}: score {av['score']:.3f} (q {av['q']:.3f}, t {av['t']:.3f}).",
                           f"timing.{area}.avoid"))
    return items


def p12_transits(w, data, area, spec, **_):
    t = data["transits"]
    items = []
    for i, r in enumerate(t["rows"]):
        if r["body"] not in SLOW:
            continue
        grade = f"{w('BAV')} {r['bav']} {r['bav_grade']}" if r.get("bav") is not None else "no BAV (node)"
        items.append(_item(f"{r['body']} in {r['sign']} {r['start']} → {r['end']}: {ORD[r['houses']['moon']]} from the "
                           f"Moon, {ORD[r['houses']['lagna']]} from the lagna; {grade}.", f"transits.rows.{i}"))
    for i, x in enumerate(t["windows"]):
        name = WINDOW_NAMES.get(x["kind"], x["kind"].replace("_", " "))
        items.append(_item(f"{w(name)} {x['start']} → {x['end']}: {_list(x['tags'][1:])}.", f"transits.windows.{i}"))
    for i, r in enumerate(t["tara_rows"]):
        items.append(_item(f"{r['body']} in {r['nakshatra']} {r['start']} → {r['end']}: {w('tara')} {r['tara_from_moon']} "
                           f"({r['count']} from the Moon's), {'adverse' if r['adverse'] else 'not adverse'}"
                           + (f", {r['special']}" if r.get("special") else "") + ".", f"transits.tara_rows.{i}"))
    return items


def p13_weighing(w, data, area, spec, judgements=None, **_):
    if not judgements:
        return [_item("No weighing sentences: this reading's analysis has none (only depth full writes them).")]
    return [_item(f"The reading's weighing ({j['section']}): {j['sentence']}") for j in judgements]


def p14_stability(w, data, area, spec, **_):
    st = data["areas"][area].get("stability") or {}
    items = [_item(f"The area's tier: time {st.get('time')}, ayanamsa {st.get('ayanamsa')}, house {st.get('house')} "
                   f"({st.get('label')}; {st.get('ayanamsas')}; {st.get('house_systems')}).", f"areas.{area}.stability")]
    weak = []
    for key, f in _fires(data, area):
        s = f.get("stability") or {}
        if (s.get("ayanamsa") is not None and s["ayanamsa"] < 1) or (s.get("house") is not None and s["house"] < 1):
            weak.append(_item(f"{f['id']}@{f['basis']}: ayanamsa {s['ayanamsa']}, house {s['house']} "
                              f"({s.get('ayanamsas')}; {s.get('house_systems')}).", f"rules.{key}.stability"))
    places = data["stability"].get("placements") or {}
    for v in ["D1"] + [x for x in spec.get("vargas", []) if x != "D1"]:
        for p, s in (places.get(v) or {}).items():
            if (s.get("ayanamsa") is not None and s["ayanamsa"] < 1) or (s.get("house") is not None and s["house"] < 1):
                weak.append(_item(f"{p} in the {v}: ayanamsa {s['ayanamsa']}, house {s['house']} ({s.get('ayanamsas')}).",
                                  f"stability.placements.{v}.{p}"))
    return items + (weak or [_item("Every finding of this area holds under every ayanamsa and both house systems.")])


def p15_rest(w, data, area, spec, **_):
    drafts = [f"{f['id']}@{f['basis']}" for _, f in _fires(data, area) if f["status"] == "draft"]
    a = data["areas"][area]
    abst = [f"{fam} ({VOTE_WORD.get(v['vote'], v['vote'])})" for fam, v in a["votes"].items() if v["vote"] in (0, None)]
    items = [_item(f"{len(drafts)} draft placements (weigh nothing until their verse is read): {_list(drafts)}.", "rules"),
             _item(f"Abstaining or not applied: {_list(abst)}.", f"areas.{area}.votes")]
    items += [_item(f"Not computed — {k.replace('_', ' ')}: {v}", f"not_computed.{k}")
              for k, v in data["not_computed"].items()]
    return items


POINTS = [p1_houses, p2_lords, p3_karakas, p4_rules, p5_vargas, p6_nakshatra, p7_kp, p8_jaimini, p9_panchanga,
          p10_votes, p11_periods, p12_transits, p13_weighing, p14_stability, p15_rest]


def build(data: dict, area: str, judgements: list[dict] | None = None) -> dict[str, Any] | None:
    """The sheet of one area from the whole-chart payload (`data`, fullchart.payload with this area
    among its areas): {"area", "points": [{"n", "title", "items": [{"text", "facts"}], "table"?}]}. None
    for an area the engine does not map (no houses), such as synastry."""
    from .scoring import AREAS
    spec = AREAS.get(area)
    if spec is None or area not in data["areas"] or not data["areas"][area].get("votes"):
        return None
    w = _Words()
    points = []
    for n, fn in enumerate(POINTS, 1):
        out = fn(w, data, area, spec, judgements=judgements)
        items, table = out if isinstance(out, tuple) else (out, None)
        points.append({"n": n, "title": TITLES[n], "items": items, **({"table": table} if table else {})})
    return {"area": area, "points": points}


def sheets(chart, as_of, areas: list[str], judgements: dict[str, list[dict]] | None = None) -> dict[str, dict]:
    """Every area's sheet from the chart (the payload built, or taken from the cache, for these areas)."""
    from .fullchart import cached_payload
    from .narrate import full_range
    data = cached_payload(chart, as_of, *full_range(as_of), areas)
    return {a: s for a in areas if (s := build(data, a, (judgements or {}).get(a)))}
