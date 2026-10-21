<!-- Exported from the living spec at https://claude.ai/artifact/2og4z1HiFMu5N3RLX3BVci on 2026-10-21 (doc rev 85). The doc is the source of truth; edit there and re-export. The two diagrams (architecture, roadmap) do not export; the phase table in Build phases carries the roadmap. -->

# Jyotish AI Engine — Full Build Spec

Oct 21, 2026 · @Ray

## Goal and honest scope

Build a Jyotish engine that computes every classical quantity from birth data, scores each life area with a stated confidence, narrates with cited rules, and measures its own accuracy against real outcomes. The thesis: Jyotish is already a rule system with numeric strengths (Shadbala, Ashtakavarga, dasha), so it can be implemented exactly, then calibrated on data.

What the engine will not claim: "precise" prediction of anything about anyone. No system has demonstrated that, and an app that promises it will be wrong in public. The product promise is: *every &#91;image: Screenshot 2026-10-21 at 13.24.44.png\]classical signal, computed exactly, weighed transparently, with a confidence you can audit.* The validation layer (Layer 6) is what lets the promise grow only as far as the evidence does.

The precision ceiling is fixed by three things no engine removes: birth-time error (4 minutes moves D60 by a sign; most recorded times are rounded to 5–15 minutes), the texts disagreeing with each other across schools and recensions, and the absence of a demonstrated empirical signal. So the engine is precise in *computation and reproducibility*, and reports every finding with its stability under those three uncertainties (Layer 1b). It is never precise about outcomes, and the product wording enforces that.

Three users: the curious person (one chart, plain-language reading), the learner (sees every rule that fired and why), and the practising astrologer (full vargas, dashas, strengths, exportable). The same engine serves all three; only the narration depth changes.

Excluded by design, so nobody wonders later: Prashna (horary), Muhurta (electional), Lal Kitab, Western tropical techniques, Bhrigu-leaf Nadi readings, and any death timing. Prashna and Muhurta are candidate products after validation; the rest are out of scope permanently.

## System architecture

Eight layers, each pure and testable on its own; data flows down, the uncertainty layer stamps every later finding with a stability, and the validation layer feeds calibrated weights back into scoring.

&#91;embedded content: engine architecture · 8 layers, 2 feedback paths\]

Layers 1 to 6 are deterministic: the same birth data always yields the same JSON. The LLM only turns that JSON into language, which is what makes the output auditable and the hallucination surface small.

## Layer 1 — Astronomical core

This layer must match the best desktop software (Jagannatha Hora, Parashara's Light) to the arc-second; everything above it inherits its errors. Inputs: date, time, place (lat/long), timezone with historical DST; output: sidereal positions of every body and every derived point.

| Component | Spec | Note |
| --- | --- | --- |
| Ephemeris | Swiss Ephemeris (DE441 files) via `pyswisseph` | Also drives sunrise/sunset for Hora, Kala and panchanga |
| Ayanamsa | Lahiri default; Raman, KP, True Chitrapaksha switchable; the KP module always pairs the KP ayanamsa with Placidus cusps | Store the value used with every chart |
| Nodes | True Rahu/Ketu default, mean switchable | Both retained, difference logged |
| Lagna | Ascendant, MC, plus Bhava Madhya and Sandhi for Sripati and equal-house bhava charts, and Placidus cusps for KP | House system a per-chart setting |
| Vargas | All 16 Parashari: D1, D2 (hora), D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 | Plus D11 (Rudramsa, used for gains) in production; D81, D108, D144 for research; D150 (Nadiamsa) for the rectification tier only |
| Nakshatra | Pada, lord, nakshatra of every body, Tara from Moon, Nadi segment | Needed for Vimshottari and KP |
| Special lagnas | Hora, Ghati, Bhava, Varnada, Sree, Indu | Jaimini and Tajaka work |
| Sensitive points | Gulika, Mandi, 11 upagrahas, Yogi/Avayogi points, Bhrigu Bindu | Rules reference them |
| Panchanga | Tithi, vara, nakshatra, yoga, karana at birth; Sunrise-based day/night birth flag | Several yogas depend on day/night |
| Speed and state | Retrograde, stationary, combust (per-planet orb), eclipse proximity | Combustion orbs from BPHS |

Validation of this layer alone: 1,000 random births computed here and in a second implementation that has a batch interface (PyJHora or Maitreya; Jagannatha Hora has no CLI and is used for manual spot checks), every position agreeing within 1 arc-second, and varga assignments compared boundary-aware (a body within 1″ of a D60 edge may legitimately differ). No later layer is built until this passes.

## Layer 1b — Rectification and uncertainty

Every chart carries a birth-time window, and every finding is reported with how well it survives that window. The layer has two parts that run at different times, so that scoring never depends on its own output: a sampler that runs before scoring and needs only the accuracy class, and a rectifier that runs after scoring and uses the timing join. Without this layer, D16 and above are noise for most users and the scoring is false precision.

**A. Uncertainty sampler (runs before Layer 2)**

- Posterior by accuracy class: exact → uniform over ±2 min (the rounding interval); within 15 min → uniform over ±15; approximate → Gaussian, σ = 30 min; unknown → uniform over the whole day, in which case only lagna-independent findings (Moon, nakshatra, dasha from the Moon's day range, planet-to-planet aspects) are narrated at all.
- Draw 200 birth times from that posterior; also recompute under three ayanamsas (Lahiri, Raman, KP) and two house systems (whole sign, Sripati). These are three separate axes, not one pool: epistemic uncertainty about the clock is a different thing from a doctrinal choice.
- Every fired rule, area score and timing window gets three numbers: time-stability (share of birth-time samples in which it holds), ayanamsa-robustness and house-robustness. Below 0.5 on time-stability it is shown as *unstable* and excluded from the default narration; 0.5–0.8 *sensitive*; above 0.8 *stable*. A finding that is stable in time but flips under Raman is reported as "holds under Lahiri only", never as unstable.
- Stable findings are what the LLM narrates first. This stability report is the engine's most distinctive output and the most honest thing an astrology product can show.

**B. Rectifier (runs after Layer 5, only when the user supplies dated events)**

- Input: the posterior from A and any dated events the user knows (marriage, first child, a job change, a parent's death, a major move).
- Method: one sweep across the window in 1-minute steps; at each candidate time, compute lagna, vargas and dasha, then score how well every known event lands in a high-activation window (Layer 5's timing join) and in the classically indicated vargas (D7 for children, D9 for marriage, D10 for career, D12 for parents). Add the Nadi and KP checks (ruling planets at birth, sub-lord of the lagna cusp agreeing with the sex and the first event; D150 Nadiamsa in the research tier). Output: a narrowed posterior, which replaces A's for that user on the next run — not a single "rectified" time.
- The user sees the window narrowing as they add events, and which conclusions flipped.
- A chart whose posterior has been narrowed by events is tagged `rectified` and is excluded from Layer 6 validation, because its time was fitted to the very outcomes the validation would test.

## Layer 2 — Feature engine

Every classical quantity becomes a number or a tag on the chart object. This is the layer that makes the later scoring possible: no rule may read raw longitudes, only features.

**Dignity and relationships**

- Five-fold dignity per planet per varga: exalted (with deep-exaltation degree distance), moolatrikona, own, friend, neutral, enemy, debilitated; Neecha Bhanga checks.
- Naisargika (natural) + Tatkalika (temporal) friendship → compound relationship, computed per chart, not from a static table.
- Lordship map for the lagna: functional benefic / malefic / yogakaraka / maraka per BPHS rules for each of the 12 lagnas.

**Aspects and contacts**

- Graha drishti with Parashari special aspects; Sphuta drishti (fractional strength by degree) as the numeric version. Node aspects (5th, 7th, 9th from Rahu and Ketu) are a per-chart setting, off by default.
- Rashi drishti (Jaimini sign aspects) kept separately.
- Conjunction with orb; planetary war (graha yuddha) winner.

**Dispositor analysis (three chains, computed as graphs)**

- Sign dispositor chain: planet → lord of its sign → that lord's sign lord, until a loop or a self-disposited planet. Outputs: final dispositor(s), mutual-reception loops (every Parivartana with its Maha / Khala / Dainya class by the houses exchanged, and the secondary lordships that taint it), chain depth per planet, and which planets funnel into which. A planet whose chain ends in an exalted or own-sign planet inherits support; one ending in a debilitated planet inherits weakness.
- Nakshatra dispositor chain: planet → lord of its nakshatra → lord of that planet's nakshatra. Mutual nakshatra exchange is flagged (it is the nakshatra-level Parivartana). This is the chain Nadi and KP reasoning runs on, and the chain that decides activation in dasha: planets sitting in the dasha lord's nakshatras are activated along with it.
- Navamsa dispositor chain: the same on D9, to see whether a D1 support survives the D9 sign placement.
- Dasha-lord relations derived from these: dasha lord's dispositor, planets in the dasha lord's nakshatras, dasha lord's own nakshatra lord. All three feed Layer 4's period quality.

**Sudarshana (triple-lagna) reading**

- Every rule with a house condition is evaluated three times — from the Lagna, from the Moon (Chandra lagna) and from the Sun (Surya lagna) — and each fire records its \`basis\`. Scoring (Layer 5) weights the three bases 3:2:1 by default. This per-fire basis is the only Sudarshana mechanism; there are no separate "Sudarshana variants" of rules.

**Bhava chalit and boundaries**

- Planets within 3° of a sign boundary or a bhava sandhi get a `boundary` flag; their house under whole-sign, Sripati and KP cusps is recorded, and any rule that depends on the house is marked sensitive (Layer 1b).

**Sensitive degrees and conditions**

- Gandanta (water–fire junctions, with the Moon and the lagna checked first), Mrityu Bhaga per planet per sign, Pushkara navamsa and Pushkara bhaga, nakshatra sandhi, degree-exact Vargottama, deep-exaltation and deep-debilitation distance, Vargottama in D9 and D60.
- Planetary avasthas and sayanadi states; Graha yuddha; combustion with the retrograde-planet orb variant.

**Panchanga lords at birth**

- Tithi lord, vara lord, karana lord, nitya-yoga lord and the birth nakshatra lord are computed and placed in the chart; their strength and house enter the scoring as a small, separate signal family (Tajaka and Muhurta texts use them; here they are a tie-breaker, not a driver).

**Strength modules (all numeric)**

| Module | Output | Used by |
| --- | --- | --- |
| Shadbala | 6 components per planet in virupas + ratio to required minimum | Scoring weights, dasha quality |
| Bhava Bala | Strength per house | Life-area base score |
| Vimsopaka Bala | 20-point varga-weighted dignity (Shadvarga, Saptavarga, Dasavarga, Shodasavarga) | Varga confirmation |
| Ishta / Kashta Phala | Benefic vs malefic yield per planet | Dasha result sign |
| Ashtakavarga | BAV (8 tables × 12 signs), SAV (0–8 per sign), Sodhya Pinda, Trikona and Ekadhipatya reductions | Transit scoring, house strength |
| Avasthas | Baladi (forward in odd signs, reversed in even signs), Jagradadi, Deeptadi, Lajjitadi, Sayanadi | Narration nuance, minor weight |

**Jaimini layer**

- Chara karakas (8-karaka scheme default, 7 switchable): AK, AmK, BK, MK, PiK, PK, GK, DK.
- Arudha padas for all 12 houses (A1–A12), with the exception rules for 1st/7th placement; Upapada (UL) and its 2nd house.
- Karakamsa (AK's navamsa sign) and Swamsa; Argala and Virodhargala on every house and on the Arudha lagna; Jaimini Raja yoga rules (AK–AmK, AK–5th lord, AL–A7 relations, Yogada and Kevala/Maha Yogada through the Hora and Ghatika lagnas); Rashi drishti used for the Jaimini rule family only.

**Nakshatra layer (used, not just displayed)**

- Per planet and per cusp: nakshatra, pada, nakshatra lord, sub lord and sub-sub lord (KP), the pada's navamsa sign, and the nakshatra's attributes (deity, gana, yoni, nadi, tri-nadi segment adi/madhya/antya, gender, direction, activity). Attributes feed narration and synastry; lords feed scoring.
- **Navatara** from the Moon's nakshatra (Janma tara as 1): Janma, Sampat, Vipat, Kshema, Pratyak, Sadhaka, Vadha, Mitra, Ati-mitra, repeating over three cycles (with the cycle recorded, since the second and third cycles are read as milder). Computed for every planet, the lagna, every cusp, and later for every dasha lord and every transiting body. Used three ways: natal (a planet in Vipat, Pratyak or Vadha tara from Janma carries a penalty, Sampat, Kshema, Sadhaka, Mitra, Ati-mitra a bonus), dasha (the period lord's tara grades the period — the classical rule that a Vipat/Vadha-tara lord's dasha is troubled), and transit (Moon and slow planets crossing adverse taras; the daily Tara bala).
- Special nakshatra positions: lagna nakshatra lord (the "nakshatra lagnesha"), 88th-degree and 64th-navamsa points, Abhijit, the Moon's distance from nakshatra sandhi.
- KP significator table per house (occupant → star lord → owner → aspect), ruling planets, cuspal sub-lord significations; the house a planet "gives" is the house of its nakshatra lord, which is the KP core and runs on the nakshatra dispositor chain above.
- Nadi activation rule: a dasha activates the lord, the planets in its nakshatras, and the planets whose nakshatras it sits in — recorded as an explicit edge set per period.

**Synastry module (two charts)**

- Takes a `pairing` document (Data schema) holding two chart ids. Computes Ashtakoota — Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoota, Nadi, 36 points with the classical exceptions (Nadi dosha cancelled by same-rashi different-nakshatra, etc.) — Mangal dosha matching with cancellations, dasha-sandhi overlap, and each chart's 7th lord, UL and DK against the other's lagna and Moon.

Output of this layer is the `features` block of the chart JSON (Data schema below). It is pure: same input, same output, no randomness, unit-tested against worked examples from BPHS and Dr. B.V. Raman's textbooks.

## Layer 3 — Knowledge graph and rule library

The chart becomes a graph so that "how are things interrelated" is a query, not a judgment call. Rules are data files, not code, so astrologers can add and version them without touching the engine.

**Nodes:** 9 grahas, 12 bhavas, 12 rashis, 27 nakshatras, 16 vargas (each varga is its own sub-graph), arudhas, karakas, cusps.

**Edges (typed, with a numeric weight where the tradition gives one):**

| Edge | From → To | Weight source |
| --- | --- | --- |
| rules | graha → bhava, graha → rashi | lordship (1.0), co-lordship split |
| occupies | graha → bhava, graha → rashi, graha → nakshatra | dignity score |
| aspects | graha → graha, graha → bhava | Sphuta drishti 0–60 virupas |
| conjoins | graha ↔ graha | orb-scaled, war winner flagged |
| disposits | graha → graha | chain depth |
| karaka\_of | graha → bhava (naisargika), chara karaka → theme | fixed table |
| arudha\_of | rashi → bhava | fixed |
| star\_lord\_of / sub\_lord\_of | graha → graha, cusp → graha | KP tables |
| dasha\_active | graha → time window | from Layer 4 |

Added edges: `nakshatra_lord_of` (graha → graha, the nakshatra dispositor chain), `navamsa_lord_of`, `rashi_aspects` (rashi → rashi, the Jaimini sign aspects the Jaimini rule family runs on), `argala_on` / `virodhargala_on` (graha → bhava, signed), `tara_from_moon` (graha → Navatara class), `panchanga_lord` (tithi/vara/karana/yoga → graha), and `activated_by` (graha → dasha lord, from the Nadi activation rule). Every house-dependent edge carries `basis` ∈ {lagna, moon, sun}.

**Rule file format (YAML, one rule per block):**

```yaml
id: yoga.ruchaka
family: pancha_mahapurusha
school: parashari            # parashari | jaimini | kp | nadi | tajaka | regional:<name>
source:
  - {text: BPHS, edition: Santhanam 1984, chapter: 75, verse: 2, checked: false}
  - {text: Phaladeepika, edition: Sastri 1937, chapter: 6, verse: 1, checked: false}
status: classical_unconfirmed   # classical_unconfirmed | classical_rejected | experimental | not_testable_yet | data_confirmed
when:
  planet: Mars
  dignity_in: [own, moolatrikona, exalted]
  house_in: [1, 4, 7, 10]
  basis: [lagna, moon, sun]  # evaluated once per basis; each fire records which
modifiers:                   # applied in file order; scales are initial values until Layer 6 calibrates them
  - if: shadbala_ratio < 1.0      # weak Mars
    scale: 0.5
  - if: {aspected_by: [Saturn]}
    scale: 0.8
  - if: tara_from_moon in [vipat, pratyak, vadha]
    scale: 0.85
  - if: marana_karaka_sthana
    scale: 0.6
themes: { courage: +3, leadership: +3, physical_vigour: +2, conflict: +1 }
outcomes: [career_status, litigation]   # Layer 6 maps themes to measured outcomes through this
confidence_base: 0.7
stability_min: 0.5           # drop from default narration below this (Layer 1b)
narration_key: ruchaka
```

The engine evaluates every rule against the graph and emits a list of `fired_rules`, each with the rule id, the basis, the matched nodes, the applied scale, which modifiers applied and the theme contributions; a modifier that needs a quantity the chart did not compute (Shadbala on a chart with no birth time) is reported as not evaluated, never silently skipped. Rule files are validated against `rules/rule.schema.json` on load, and a bad file stops the load naming the file and field. Two-planet rules (Raja yogas, Parivartana) use a `pair` condition with `related_by` ∈ {conjunction, mutual\_aspect, exchange}. Every `source` carries `checked: true|false`: a rule whose citations are unchecked still runs, but counts as cited only once a person has verified chapter and verse against the named edition. The learner can see exactly why a theme scored what it did.

**Rule library, in build order:**

1. Pancha Mahapurusha (5), Raja yogas by lordship (kendra–trikona, Dharma-Karmadhipati, Viparita), Dhana yogas, Neecha Bhanga, Parivartana (3 kinds, classified by houses exchanged).
2. Lunar and solar: Gaja Kesari, Sunapha/Anapha/Durudhara, Kemadruma with cancellations, Budhaditya, Chandra-Mangala, Adhi yoga.
3. Afflictions: Kala Sarpa (and its 12 named forms), Grahan, Pitru dosha markers, Mangal dosha (with all classical cancellations), Guru-Chandala, Shrapit, Daridra, Marana Karaka Sthana, dagdha and tithi-shunya rashis.
4. Nabhasa yogas (32), Chara-Sthira-Dwiswabhava patterns.
5. Jaimini: Karakamsa yogas, Arudha–UL relations, Argala, Raja yogas by AK/AmK/5th-lord.
6. KP: cusp sub-lord significations for the 12 houses, ruling planets.
7. Varga-specific: D9 vargottama and Pushkara, D10 Amatyakaraka placement, D7 Santana, D30 trimsamsa deities, D60 shashtiamsa deities with their benefic/malefic class.
8. Stri Jataka (BPHS ch. 80 and Saravali's female-chart rules: Jupiter and the 8th for marital life, Mangalya), Balarishta and its cancellations (reported as indications only).

Target: 300+ rules by launch, each with a text source and edition. Statuses: a cited rule starts `classical_unconfirmed` and stays in default scoring; `classical_rejected` after a powered null result in Layer 6 (shown to learners as classical, disconfirmed); `not_testable_yet` when no measured outcome maps to its themes or the test is under-powered; `experimental` for an uncited rule, excluded from default scoring; `data_confirmed` after a powered positive result.

## Layer 4 — Time engine

Timing is where predictions become testable, so this layer produces dated windows with a quality score, not just period names. Several independent dasha systems run in parallel; agreement between them raises confidence (Layer 5).

**Dasha systems**

| System | Scope | Depth | Why it is in |
| --- | --- | --- | --- |
| Vimshottari | Universal default | 5 levels (maha → antar → pratyantar → sookshma → prana) | The standard; all texts assume it |
| Yogini | Universal | 2 levels | Cheap second opinion, popular in North India |
| Chara (Jaimini) | Universal, sign-based | 2 levels | Independent logic; K.N. Rao variant default |
| Ashtottari, Shodashottari, Dwadashottari, Panchottari, Shatabdika, Chaturashiti-sama, Dwisaptati-sama, Shashtihayani | Conditional (lagna/nakshatra conditions from BPHS) | 2 levels | Engine turns them on only when their condition holds |
| Kalachakra, Narayana, Sudasa | Universal nakshatra-based (Kalachakra); Jaimini sign-based for wealth and rise | 1 level | Research tier |

Each period is enriched: dasha lord's house, lordships, dignity, Shadbala, Ishta/Kashta, houses it aspects, its position from the maha lord (for antar), and the Vimshottari rule set for sub-period interaction (e.g. 6/8 or 2/12 between maha and antar lords).

Settings that move dates by months and must be explicit on every chart: dasha year length (365.25-day solar, 360-day savana, 365.2564 sidereal), the Moon's exact longitude at birth (so the dasha balance follows the birth-time posterior from Layer 1b), and the ayanamsa. Each period also carries its lord's Navatara class from the Moon, its lord's dispositor and nakshatra-lord, and the Nadi activation set, so period quality is a function of the lord *and* what the lord drags in.

**Transits (gochar)**

- Saturn, Jupiter, Rahu/Ketu as the slow movers; Mars and Sun for month-level triggers.
- Every transit scored three ways: from Moon (classical gochar tables), from Lagna, and by Ashtakavarga (BAV points of the transiting planet in that sign; SAV of the sign; Kakshya of the exact degree).
- Vedha and Vipareeta Vedha applied to classical gochar results.
- Named windows: Sade Sati (with Moon-sign and Ashtakavarga grading), Kantaka Shani, Ashtama Shani, Jupiter over 1/5/9/11 from Moon, nodal return at 18.6 years, Saturn return at 29.5.
- Double-transit test (K.N. Rao): Saturn and Jupiter both touching a house or its lord marks the event window; implemented as a boolean feature per house per month.

Also scored: Rahu–Ketu transits over natal planets and cusps (the nodal axis crossing the lagna, Moon, 7th lord or Atmakaraka is a named window), eclipses within 3° of natal points, the transiting Moon's Navatara and Tara bala for day-level questions, Murthi Nirnaya (the Moon's position from the natal Moon at the moment a slow planet enters a sign, grading that whole transit gold, silver, copper or iron), and the Saturn–Jupiter–node triple when all three touch one house in the same year. Dasha sandhi — the last and first months of adjoining maha and antar periods — is flagged on the timeline as an unstable window, and nothing is predicted into it with more than moderate confidence.

**Varshaphal (Tajaka annual chart)**

- Solar return chart, Muntha, year lord by the five-candidate rule, Tajaka aspects and the sixteen Tajaka yogas (Ithasala, Ishrafa, Nakta, Yamaya, Manau, Kamboola, Radda and the rest), Sahams (Punya, Vivaha, Karma, Roga, etc.), Mudda dasha.
- Used as a year-level tie-breaker when Vimshottari and transits disagree. Tithi Pravesha (the lunar annual chart) is computed alongside for research comparison.

**Output:** a timeline of tagged rows, one type per source: dasha rows (system, level, lord, start, end, quality, tara, activation set), transit rows (body, sign, house under each basis, BAV and SAV, Vedha, Murthi class, start, end) and Varshaphal rows (year, year lord, Muntha, Sahams, Mudda period). Any "when" question becomes a `TimingQuery` — area, date range, systems to use, Sudarshana basis, the question text — that Layer 7's translation must validate against the schema before the engine runs it, joined with the static scores from Layer 5.

## Layer 5 — Scoring and inference

Every life area gets a score, a confidence and a dominance rank, computed from a fixed signal list so two astrologers (or two runs) cannot disagree about what was counted. Confidence is a measure of agreement between independent signals, not a claim about the world until Layer 6 calibrates it.

**Signal lists per life area** (house, lord, karaka, varga, arudha). All 19 areas. Every house is also read as its derived house (Bhavat Bhavam: the 4th from the 10th for career stability, the 7th from the 7th for the partner's health, the 5th from the 5th for grandchildren) and from the Moon and Sun.

| # | Life area | Houses (from Lagna; also Moon, Sun) | Karakas | Varga | Jaimini / KP |
| --- | --- | --- | --- | --- | --- |
| 1 | Personality and vitality | 1; lagna lord | Sun, lagna lord, AK | D1, D9 lagna | AL; KP 1st cusp |
| 2 | Wealth and income | 2, 11, 5, 9 | Jupiter, Venus | D2 (hora), D16 | A2, A11; Indu lagna |
| 3 | Siblings, courage, communication | 3; 11 for elder | Mars, Mercury, BK | D3 | A3 |
| 4 | Mother, home, property, vehicles | 4, 11, 12 | Moon, Mars, Venus, MK | D4, D12 | A4 |
| 5 | Children | 5, 9, 11 | Jupiter, PK | D7 | A5; KP 5th cusp |
| 6 | Intellect, education, creativity | 4, 5, 2, 9 | Mercury, Jupiter | D24 | A4, A5 |
| 7 | Health and disease | 1, 6, 8, 12; 3rd and 8th from Saturn | Sun, Saturn, Mars, 6th lord | D30, D3 | Roga Saham; KP 6th cusp |
| 8 | Debts, enemies, litigation | 6, 8, 12; 6th from Moon | Mars, Saturn, Rahu | D30 | A6 |
| 9 | Marriage and partnership | 7, 2, 11, 8 | Venus (m), Jupiter (f), DK | D9 | UL, 2nd from UL, A7; KP 7th cusp |
| 10 | Longevity and crises (indications only) | 1, 8, 3; Saturn | Saturn, 8th lord, lagna lord | D30, D9 | Marana Karaka Sthana; no death timing |
| 11 | Father and lineage | 9, 10; Sun | Sun, PiK | D12 | A9 |
| 12 | Fortune, dharma, higher learning | 9, 5, 12 | Jupiter, PiK | D20, D9 (9th) | A9 |
| 13 | Career and status | 10, 6, 2, 11; 10th from Moon and Sun | Sun, Saturn, Mercury, AmK | D10 | A10; KP 10th cusp |
| 14 | Gains and networks | 11, 2, 5 | Jupiter | D11 | A11 |
| 15 | Foreign residence and travel | 9, 12, 3, 7; Rahu | Rahu, Moon, 12th lord | D4 (9th), D9 lagna lord | A9, A12 |
| 16 | Spirituality and moksha | 12, 9, 5, 8; Ketu | Ketu, Jupiter, Saturn | D20 | Karakamsa, A12 |
| 17 | Mental and emotional life | 1, 4, 5; Moon | Moon, Mercury | D1 from Moon, D24 | Chandra lagna; KP 4th cusp |
| 18 | Reputation and public life | 10, 1, 4; AL | Sun, Jupiter | D10 | AL and its 10th |
| 19 | Synastry (two charts) | 7 and 1 of each; both Moons | Venus, Jupiter, DK, UL | D9 of both | Ashtakoota, UL match, dasha sandhi |

Every row is evaluated from the Lagna, the Moon and the Sun (Sudarshana), weighted 3:2:1, with the Moon-based reading taking the lead for emotional and timing questions. A 19th area, **synastry** (two charts): Ashtakoota with its exceptions, Mangal dosha with the full cancellation list, dasha-sandhi overlap, each person's 7th lord and UL against the other's lagna and Moon, nakshatra attribute matching (gana, yoni, nadi) as narration only, and a combined timing join for both charts. Dispositor chains enter every area through the lord columns: a lord's score is adjusted by the dignity of its final dispositor, and a Parivartana involving the area's lord is a named signal of its own.

**Scoring formula per life area**

```latex
S_{area} = \sum_{h \in H} w_h B_h + \sum_{p \in L \cup K} w_p D_p \frac{\beta_p}{\beta^{req}_p} + \sum_{r \in R_{area}} c_r b_r \theta_r + \lambda V_{area} + \nu \sum_{p \in L \cup K} T_p + \kappa \sum_{p \in L} \Delta_p + \pi P_{area}
```

where B\_h is Bhava Bala (normalised), D\_p is dignity on a −2…+2 scale, β is Shadbala against its required minimum, θ\_r is each fired rule's theme contribution scaled by its modifiers and b\_r is the basis weight of that fire (1 from the Lagna, 2/3 from the Moon, 1/3 from the Sun), V\_area is the varga term (the mean signed dignity of the area's lords and karakas in the area's vargas, vargottama as a bonus; the D1–varga agreement is a consistency number, not the direction — revised 2026-10-21, below), T\_p is the Navatara class of each lord and karaka on a −1…+1 scale, Δ\_p is the dignity of each lord's final dispositor (so a lord inherits support or weakness from its chain), and P\_area is the small panchanga-lord term (the birth tithi, vara, karana and yoga lords' strength where they touch the area). Stability is *not* a factor in S: it is reported beside the score as three numbers (Layer 1b) and gates narration, so an unknown birth time produces "cannot be assessed", never a low score. Weights w, c, λ, ν, κ, π start from classical proportion (lord : occupant : karaka ≈ 3 : 2 : 2; ν, κ, π small) and are the classical weight set; Layer 6 produces a separate, named learned set, and the classical set stays the default until a learned set passes the sequestered test and is promoted in a numbered release.

**Varga term and KP vote (revised 2026-10-21, from the first full reading).** Two family votes were found to carry the wrong sign once the narration stated the engine's reasoning in words. *Varga.* v1 scored the agreement between a planet's D1 dignity and its dignity in the area's varga, so two negatives agreeing counted +1: the Sun, debilitated in D30 and in an enemy's sign in D1, voted *for* health, and Jupiter, friendly in D10 but in an enemy's sign in D1, voted *against* career. V is now the varga's own verdict: the mean over the area's lords and karakas of their signed dignity in each of the area's vargas (−2…+2 scaled to −1…+1), +1 for vargottama in D9; the share of planets whose D1 and varga dignities agree in sign is reported as `varga_consistency` and scales the varga family's weight in the confluence by 0.5 + 0.5 × share. *KP.* v1 counted a cusp sub-lord as "for" when it occupied or owned any of the area's own houses and "against" when it touched 6, 8 or 12 outside them, which reads a dusthana as supportive wherever the area's matter is a dusthana: the 6th-cusp sub-lord owning the 8th voted for health, and the 8th was a marriage-promising house. The vote now follows KP practice. Each area with a cusp has its matter houses M and its denial houses N from the KP readers (cited `checked: false` until read in the named edition; where N is the 12th from each house of M, that is Krishnamurti's own principle that the 12th to a house denies it): personality, cusp 1, M 1 5 9 11, N 6 8 12; mother and home, cusp 4, M 4 11 12 (property acquired), N 3 5 10 (property sold); children, cusp 5, M 2 5 11, N 1 4 10; health, cusp 6, M 1 5 11 (recovery and health), N 6 8 12 (disease); marriage, cusp 7, M 2 7 11, N 1 6 10; career, cusp 10, M 2 6 10 11, N 1 5 9; mind, cusp 4 as well (peace of mind), M 4 11, N 6 8 12. Occupation is counted in the KP houses (Placidus cusps, \`Meta.kp\_house\_system\`), as KP practice counts it; ownership is by sign and unaffected; the chart's ayanamsa stays, and the ayanamsa axis of the stability report shows what the KP ayanamsa would change. A planet's significations are the KP four-fold table in order of strength: the house its star lord occupies, the houses its star lord owns, the house it occupies, the houses it owns; a node adds the significations of the planets conjoined with it and then of its sign lord (aspects follow `Meta.node_aspects`). The vote is decided at the star-lord level first: +1 when those significations meet M and not N, −1 when N and not M; if both or neither, the same test at the planet's own level; 0 if still undecided, which is an abstention, not a weak vote. The reference chart's career KP vote under v1 was −1 (Ketu in the 8th, owning nothing) and flipped the tier on the birth minute; under v2 Ketu signifies through Purva Ashadha's lord Venus (the 11th; owns 1 and 6) and its sign lord Jupiter (the 1st; owns 8 and 11), meeting M and N at both levels — what the engine then reports is the result, and the stability report says what the tier depends on next. *Open reading kept as is:* the house family counts a strong dusthana as support for the area whose matter the dusthana is (the 6th for overcoming disease, the 8th for longevity), Bhava Bala's own reading that a strong bhava flourishes; it stays, and is listed with the other open readings for Layer 6.

The linear sum is the interpretable default. The tree model in Layer 6 is allowed to learn interactions (cancellations, conditional yogas); wherever the two disagree on an area by more than 0.15, the reading says so and shows both.

**Confluence and confidence**

- Count the signal *families* that agree on the direction of a theme: D1 house, D1 lord, karaka, varga, Jaimini arudha, KP sub-lord, panchanga lords, dasha activation, transit activation. They are not independent — all are functions of the same ten longitudes — so each family's vote is weighted by 1 − ρ, where ρ is its mean correlation with the other families measured on 10,000 random charts; confidence = weighted agreement / weighted applicable, with a penalty for strong contradiction (e.g. exalted 7th lord but afflicted UL).
- Output tiers: weighted agreement above 0.7 → "strong"; 0.4–0.7 → "moderate"; below, or mixed → "weak / mixed", and the narration must say so in words. Tier boundaries are re-mapped by the calibration map in Layer 6 when one exists; until then they are classical convention, and the product says so.

**Dominance model ("what is dominant")**

- Rank planets by a composite *sum* of standardised terms, never a product (a product gives zero to any planet with no rule fired, whatever its lordship): Shadbala ratio, Vimsopaka (Shodasavarga), rules fired as a share of rules applicable, Sodhya Pinda rank, a lordship-role term (yogakaraka, lagna lord, final dispositor), each scaled to 0–1 and summed with equal weights (hypothesis v2, 2026-10-21; v1's product was implemented and rejected on the reference chart). The top planet is the chart's *driver*; the dispositor-graph finals are shown beside it as alternates.
- Rank life areas by S\_area × confidence. An area is "not emphasised" when its S falls below the 40th percentile of that area's distribution over the 10,000-chart population run (cached beside the family-correlation table), never below the chart's own median — a chart-relative cut hides half of every chart by construction. Not-emphasised areas are reported as such, not scored low.
- Polarity: each theme carries signed contributions, so "wealth: strong, but with volatility (Rahu in the 2nd)" is a native output. A delay/intensity flag from Saturn or Mars requires the malefic to touch at least two of the area's primary house, that house's lord and the area's main karaka (occupy, conjoin or aspect), and a malefic that is itself the lord of the primary house does not flag that house (v3: Mars in its own 7th is not an affliction of the 7th). Each flag records its touches. On the reference chart the two-touch rule still flags 13 of 18 areas, because Saturn in the 1st and Mars in the 7th between them aspect five of the chart's occupied houses; that is a fact about the chart, so the narration mentions polarity only for the top three areas and reports it with its touches.

The driver-planet formula is a hypothesis, not a classical rule. "Rules fired" is normalised by the rules applicable to that planet, so Mars and Saturn do not win by having a larger rule library; dasha proximity is dropped from the static driver and the current period lord is reported separately with an `as_of` date. Where the sign-dispositor graph collapses into one loop or one final dispositor, that planet is a driver candidate regardless of the formula, and the alternates are shown side by side. The formula is validated in Layer 6 like any rule.

**Timing join (v2.1, 2026-10-21; v1 was implemented and showed one gap, v2 was implemented and showed the next).** Period quality q ∈ \[0, 1\] for every dasha period (any system, any level) is the mean of six named components: the lord's dignity (−2…+2 mapped to 0–1), Shadbala ratio clipped to 0–1, Ishta share (Ishta / (Ishta + Kashta)), tara class (adverse 0, neutral 0.5, supportive 1), relevance to the area (1 when the lord rules, occupies or aspects an area house, is its karaka, or is activated through the Nadi nakshatra chain; else 0), and the maha–antar relation (6/8 or 2/12 between the lords → 0, else 1). A window exists only where the Vimshottari maha or antar lord is relevant to the area; Yogini and Chara add to confluence when their lords are relevant too. Transit activation t ∈ \[0, 1\] is the mean over Saturn, Jupiter and the nodal axis of a touch credit against K.N. Rao's double-transit targets — the area's primary house, that house's lord and its main karaka, by occupation or whole-sign aspect, credit 1 — with the secondary houses and their lords at credit ½; Saturn and Jupiter both on a full target = 1. v2 had counted every area house and lord as a full target, and on the reference chart that gave t = 1.0 in 33 of the 37 slow-mover slices of 2026–2036 (career has four houses plus their lords, so Saturn or Jupiter nearly always touched one); under the Rao targets the same decade ranges from 0 to 1, so the transit term ranks windows again instead of handing the ranking to the dasha term alone. Joint = 0.6 q + 0.4 t; the area's static tier is narrated beside the window, never multiplied in, because it is the same for every window and cannot rank them. Windows are the gated Vimshottari antars cut at slow-mover ingresses; adjacent pieces with the same maha and antar and joint within 0.1 are merged; a piece shorter than a month is absorbed by its neighbour, which keeps its own label and lists the piece in its derivation; a window cut by the edge of the queried range is marked truncated. The answer gives the top three windows and one "avoid" window (the lowest joint), each with its q components, its t, the systems whose lords are relevant, its strongest piece of at least a month, and its edge movement under the birth-time and ayanamsa axes. Sandhi (the last and first months of adjoining periods) caps confidence at moderate. This is what makes "a good window for a job change 2030–31" a computed statement with a visible derivation.

## Layer 6 — Validation and learning

No published study has shown Jyotish predictions beating chance at scale, so this layer is the only honest path to the word "probability". The design assumes nothing and measures everything; if signal exists, the weights find it, and if it does not, the product still ships as a transparent classical engine with honest confidence language.

**Outcome dataset**

- Every outcome is a triple (event type, age at event, censor age), never a bare yes/no: marriage → age at first marriage or censored at current age; divorce; first child; occupational status → ISCO-08 mapped to an ISEI score at age 35, plus tenure changes; relocation abroad → age at first; major surgery or chronic diagnosis → age at first; parental loss; property purchase. Self-reported diagnoses carry a `self_report` flag.
- A theme-to-outcome mapping table (rule `outcomes` field) states which measured outcome each area and each rule family is tested against; a rule whose themes map to nothing measured is `not_testable_yet`, not "unconfirmed".
- Capture is outcomes-first: the app asks for dated events *before* it shows any reading and stores the pre-reading timestamp; events entered after a reading are flagged `after` and excluded from all tests. This is the main source over time, and the ordering is what makes it usable.
- Other sources: public figures with documented birth times (Astro-Databank, Rodden AA/A only — CC BY-NC-SA, so research track only and never for calibrating commercial weights without written permission; and a famous-by-selection sample, so excluded from the career and reputation areas) and partner astrologers' consenting client files. Every test is stratified by source. Charts tagged `rectified` (Layer 1b) are excluded.
- Target: 2,000 charts with ≥3 dated outcomes each for the first analysis; 20,000 for per-rule estimates and any calibration. A power table per area and per test is part of the pre-registration: with 2,000 charts a rule that fires on 5% of them (n ≈ 100) has roughly 0.2 power to detect a 5-point lift at α = 0.01; at 20,000 it has roughly 0.9. Most rules are `not_testable_yet` until the second cohort, and the product says so.

**Tests, in order of strictness**

1. **Splits.** A sequestered final cohort (25%) is frozen with the first dataset and scored once per numbered release, never used for development. The remaining 75% is the development set, used with grouped K-fold cross-validation (groups = household, family and birth-place cluster so that related charts never straddle a fold), stratified by birth-year decade, sex and region so that era and regional base rates are represented in every fold rather than held out.
2. **Permutation null, per area.** Permute outcome labels across charts within birth-year × sex × region strata, ≥1,000 permutations; report each area's lift with a 95% interval and Benjamini–Hochberg correction across areas. This replaces "random charts", whose slow-planet signs are shared with the real charts and so are not a null.
3. **Incremental validity.** Nested models: covariates (age, sex, country, era, socio-economic class where known) versus covariates plus the \~50 area-level engine terms; likelihood-ratio test and DeLong on AUC. The engine counts only if it adds lift *on top of* demographics in one model, not by beating two baselines separately.
4. **Timing, as survival.** Dated outcomes are time-to-event with censoring. The engine's window activation is a time-varying covariate in a discrete-time hazard model; windows are compared against coverage-matched random windows, never "top-3 vs 3 random", because maha windows can span 40 years.
5. **Abstention accounting.** A finding under the stability gate is an abstention, not a hit or a miss. Every accuracy number is reported with its coverage (the share of charts on which the engine made the prediction at all).
6. **Per-rule effects.** Effect size with interval for every rule with a mapped outcome; demotion to `classical_rejected` only on a powered null (power ≥ 0.8 for a 5-point lift); otherwise `not_testable_yet`.
7. **Calibration.** A Platt or isotonic map from the confidence score to observed frequency is fitted on development folds and evaluated on the sequestered cohort with expected calibration error. Probability language is enabled per area only when the sequestered cohort has ≥200 positives in every bin the map uses — realistically the 20,000-chart cohort.
8. **School-split.** Rule families (Parashari, Jaimini, KP, Nadi) are compared on development folds; the chosen family per area is then estimated once on the sequestered cohort, so the winner's curse is paid on development data.
9. **Decoy (Barnum) test.** Pre-registered n (300 raters) and minimum separation (Cohen's d ≥ 0.3). Each rater sees their own reading and a demographically matched stranger's, with age- and era-revealing sentences (Saturn return, Sade Sati dates) stripped from both. If ratings do not separate, the narration is too vague whatever the scores say.
10. **Pre-registration.** Before each release's analysis, the rule set, weight set, split definition and analysis code are hashed and published; results go in a public changelog, positive or negative.

The three-astrologer agreement gate in Phase 3 measures fidelity to the tradition, not truth; it is a build gate, never evidence, and the reviewers see charts without names.

**Learning**

- First model: regularised logistic regression from the \~50 area-level terms of the Layer 5 formula (not the thousands of raw Layer 2 numbers) to each outcome, with grouped cross-validation; a small gradient-boosted tree on the same terms is allowed to find interactions (cancellations, conditional yogas), and wherever it disagrees with the linear score by more than 0.15 the reading says so. Effects are shown standardised, beside the classical weights, never as raw coefficients on different scales.
- Learned weights are a separate, named set. The classical set stays the default until a learned set passes the sequestered test and is promoted in a numbered release; users and astrologers can toggle between the two at any time.

* Never train on outcomes flagged `after` (entered once a reading was shown), on `rectified` charts, or on the sequestered cohort.

**What counts as evidence, written into the product.** A finding is reported as a probability only when its area has a calibration map evaluated on the sequestered cohort with n ≥ 200 positives per bin; the reading schema carries `probability: null`, `calibrated: false` and `bin_n` until then. Everything else is reported as "the classical signals point to X, confidence moderate, stable under a 4-minute window". This wording rule is enforced in Layer 7's output schema, not left to the LLM.

## Layer 7 — Narration with retrieval

The language model never sees raw longitudes. It receives the scored JSON (fired rules, area scores, confidence tiers, dasha windows) plus retrieved passages from the classical texts, and writes a reading that cites a rule id for every claim. This is what stops the usual AI-astrology failure, where the model invents yogas that are not in the chart.

**Retrieval corpus**

- Brihat Parashara Hora Shastra, Phaladeepika, Saravali, Brihat Jataka, Jataka Parijata, Uttara Kalamrita, Jaimini Sutras with commentary, Tajaka Neelakanthi; plus the modern reference set (B.V. Raman, K.N. Rao, Sanjay Rath on Jaimini, K.S. Krishnamurti for KP).
- Chunked by shloka with metadata (text, chapter, verse, topic tags, which rule ids cite it). Embeddings for semantic search, BM25 for exact term lookup, hybrid rank.
- Each `narration_key` in a rule maps to the shlokas the writer may quote or paraphrase.

Licensing: the Sanskrit originals are public domain; most English translations in print (Santhanam's BPHS and Saravali, Rath's Jaimini) are not. The corpus holds the Sanskrit text, public-domain translations (Iyer's Brihat Jataka 1885, Sastri's Phaladeepika where confirmed), and in-house translations of the rest; the LLM quotes a shloka only from those, and cites the printed translation by chapter and verse without reproducing it.

**Prompt contract**

1. Input: `chart.scored` JSON, user's question, depth setting (curious / learner / astrologer), retrieved shlokas.
2. Every sentence that makes a claim ends with a citation tag `[rule:yoga.ruchaka]`, `[text:BPHS/Santhanam-1984/75/1-2]` (text / edition / chapter / verse, only for a source marked `checked`) or `[vote:career.kp]`. Output is validated: a sentence with a claim-verb and no tag is rejected and regenerated, and so is a tag the engine did not offer for that finding.
3. Confidence words come from the JSON tier field verbatim and are placed by the engine beside the prose, not written by the model, which writes none; it may not upgrade "moderate" to "certain".
4. Claims are ordered in two groups: the rule fires first, by stability × (the fire's scale × the rule's `confidence_base`), then the family votes, by stability × (1 − ρ)·|vote| with 1 − ρ clipped to 1. The two confidences are on different scales — a rule's is the text's own confidence in the yoga, capped at 0.7, a vote's is the family's independence weight, near 1 — so they are not ranked against each other: ranked together, every vote outranked the Raja yoga on the reference chart. The area's confidence is the same for every claim in the area and cannot order them. Findings with stability under 0.5 are left out of the default narration and listed under "depends on exact birth time".
5. Where rule families from different schools disagree on an area, the narration names both schools and the disagreement; it never averages them into one claim.
6. Forbidden content is enforced in code: no death timing, no medical diagnosis, no financial trade advice, no claims about a third party's own life — the mother, partner, children, father and synastry areas report the relationship as seen from this chart, never the other person's fate; these areas return the classical indications with a fixed disclaimer block. The trade filter matches a buy / sell / invest verb together with an instrument word (stocks, shares, crypto, securities, …), not the bare words "trade" or "trading", which name a profession.
7. Learner mode appends, per claim, the rule block that fired, the feature values that satisfied it, and the dispositor and Navatara context of the planets involved.
8. Findings the model may narrate are of two kinds. The non-experimental fired rules whose themes map to the area, tagged by rule id and by each checked source; fires of the same rule on the same planets from different bases are offered as one finding (`yoga.ruchaka@lagna+sun`) listing its bases with each basis's fire shown separately, at the minimum stability and confidence across them, so the reader gets "Ruchaka forms from the lagna and from the Sun" once, not two near-identical sentences that cannot refer to each other; a basis under 0.5 time-stability is split off before the merge and goes to "depends on exact birth time" on its own, so an unstable basis never pulls a stable one out of the reading. A text's verse defines a yoga from the ascendant; the Moon and Sun bases are the engine's Sudarshana reading (Layer 2), so the text tags belong to the lagna fire and the other bases are cited to the rule — the merged finding marks its non-lagna bases `sudarshana` and learner mode says so beside the claim. And the area's family votes (house, lord, karaka, varga, arudha, KP, panchanga), one finding per family that voted (an abstention is not a finding), tagged `[vote:<area>.<family>]` and carrying the vote's derivation: the houses with their Bhava Bala, the lords and karakas with house, dignity, Shadbala ratio and final dispositor, each planet's D1 against varga dignity, the arudha padas and their occupants, the cusp's star and sub-lord with the sub-lord's house and lordships, the panchanga lords with their roles — never a longitude. Every derivation row names the basis (lagna, Moon or Sun) under which its house is an area house, so that Scorpio, the 10th from the Sun, is narrated as that and not as "the 7th". Each vote carries its own time-stability from the sampler; a vote under 0.5 goes to "depends on exact birth time" like a rule. The rule library is small and most of what decides a tier is in the votes, so a reading that cites only rules cannot say why an area is moderate; the KP vote against career on the reference chart (10th-cusp sub-lord Ketu) is the case in point.
9. Implementation (2026-10-21, `narrate.py`): the engine owns tier, stability, ordering, the depends-on-birth-time section, school conflicts, polarity (top three areas only), windows and disclaimers; the model receives finding ids, rule ids, planets, houses, modifiers, stability and allowed tags — never a longitude — and returns structured output (one tagged claim per finding and a two-to-three-sentence summary) through the Anthropic SDK; a code validator rejects an untagged claim verb, an unoffered tag, probability or confidence words, death timing, medical diagnosis, trade advice or a third party's fate, and sends the errors back for up to three attempts. Model name and settings live in one config. The offline suite replays a fixture recorded from the live model (`JYOTISH_LIVE_NARRATION=1` re-records it); the recorder keeps every draft, accepted or rejected, with the request id, token usage, model, effort and time. A "when" question also returns the timing windows with their q components, t, relevant systems, strongest piece, truncation flag and the avoid window. Not yet built: the retrieval corpus (the only citable texts are the verified sources on rules), the model-drafted question-to-query translation (routing is by keyword), learner depth.
10. Semantic check (added 2026-10-21 after the first recorded reading). The validator checks tags and words, not meaning, and the first real draft showed the gap: "the 10th cusp's sub-lord Ketu, in the star of the Moon, sits in the 8th house" is true of the cusp (Shravana, the Moon's star, sub-lord Ketu) and false of Ketu (Purva Ashadha, Venus's star), and a reader attaches the appositive to Ketu. So every claim goes through a second structured call, the checker: given the sentence and the finding's derivation only (never the question, never the other findings), it lists the propositions the sentence makes and marks each as stated in the derivation or not. One unsupported proposition rejects the claim, with that proposition as the error the writer gets back. The checker's output is never narrated and is kept in the recording. An ambiguous sentence is rejected the same way, because the checker reads it as a reader would. What the first checked run (2026-10-21, below) added: the checker is a sample, not a verdict — it passed two sentences on one attempt and rejected the identical text on the next — so it runs on every claim of every attempt, never only on the rewritten ones, and at a higher effort than the writer (`checker_effort`, high; the model offers xhigh and max at more cost, and the setting, not this text, decides); the summary's sentences are checked too, each against the union of the derivations of the findings it cites, because a word placed only in the summary otherwise reaches the reader unchecked; the writer's prompt says that each claim stands alone and may not refer to another ("again", "the same", "also", "as above"), since the checker cannot see the other finding and will always reject the reference — said in the prompt, not enforced by the validator, because "also" is often legitimate.
11. Validator additions from the same reading. A `[vote:<area>.<family>]` tag is valid on a sentence only if the sentence names that family (house, lord, karaka, varga, arudha or pada, KP, cusp or sub-lord, panchanga, tithi, weekday or nakshatra lord), and a sentence that names a family whose vote was offered must cite it: the recorded summary named five votes and cited two, and tagged a sentence about timing with the house vote. A `[rule:…]` tag is valid only if the sentence contains one of the rule's `names` (an optional list in the rule file — "Ruchaka"; "raja yoga", "kendra-trikona" — defaulting to the id's last segment). The model's text may not mention timing, windows, dates or the engine, which state themselves. The wording of a basis is offered in the derivation, not enforced: "Mars rules several career houses from its own sign in the 7th" is true and stays; a test of the model's phrasing does not belong in the engine's suite.

**Conversational layer** Follow-up questions are routed first to the engine ("when will I buy a house" → timing join on the property area), and only the result goes to the model. The model drafts the question-to-query translation; the engine runs it; the model narrates the output. No chart fact originates in the model.

**Output schema (per reading)**

```json
{
  "as_of": "2026-10-21", "weights": "classical-1.0", "engine": "1.0.0",
  "summary": {"driver_planet": "Saturn", "driver_alternates": ["Venus", "Mars"], "current_period": "Rahu-Saturn",
              "top_areas": ["career", "wealth", "marriage"],
              "time_window_min": 4, "stable_findings": 11, "unstable_findings": 3, "abstained_areas": []},
  "areas": [{"name": "career", "score_classical": 0.78, "score_learned": null, "model_disagreement": null,
             "tier": "strong", "stability": {"time": 0.91, "ayanamsa": 1.0, "house": 0.95},
             "probability": null, "calibrated": false, "bin_n": 0,
             "families_agree_w": 4.1, "families_total_w": 5.6, "polarity": [],
             "claims": [{"text": "...", "cites": ["rule:yoga.budhaditya", "text:Phaladeepika/Sastri-1937/6/3"],
                         "school": "parashari", "basis": "lagna", "stability": 0.95}],
             "school_conflicts": [],
             "windows": [{"kind": "dasha+transit", "start": "2027-03", "end": "2028-11", "score": 0.71,
                          "stability": 0.7, "sandhi": false,
                          "why": [{"kind": "dasha", "lord": "Mercury", "level": 2, "tara": "janma"},
                                  {"kind": "transit", "body": "Jupiter", "house": 10, "basis": "moon", "sav": 30}]}]}],
  "fired_rules": [{"id": "yoga.ruchaka", "basis": "lagna", "scale": 0.6, "stability": 0.98},
                  {"id": "yoga.parivartana", "basis": "lagna", "scale": 0.9, "stability": 1.0}],
  "unstable": [{"id": "varga.d60_lagna_lord_dignity", "stability": 0.5}],
  "disclaimers": ["health", "longevity", "finance", "third_party"]
}
```

## Data schema — the chart object

One JSON document per chart, versioned by engine release, so a reading can always be reproduced. Top-level keys map one-to-one to the layers. Values below are the reference chart's where the worked example fixes them (karakas, arudhas, dispositors, KP cusp, Ashtakavarga, Shadbala) and illustrative elsewhere (Bhava Bala, scores).

```json
{
  "meta": {"engine": "1.0.0", "weights": "classical-1.0", "ayanamsa": "lahiri", "ayanamsa_value": 23.87, "jd": 2451981.0,
           "node": "true", "node_aspects": false, "house_system": "whole_sign", "kp_house_system": "placidus",
           "dasha_year": 365.25, "karaka_scheme": 8, "time_accuracy": "exact",
           "cache_key": "sha256(birth + every meta setting + engine + weights)"},
  "birth": {"utc": "...", "lat": 0, "lon": 0, "tz": "Asia/Kolkata",
            "time_posterior": {"shape": "uniform", "center_utc": "...", "half_width_min": 2, "samples": 200, "rectified": false}},
  "bodies": {"Sun": {"lon": 327.80, "sign": 11, "deg": 27.80, "nak": 25, "pada": 3,
                     "nak_lord": "Jupiter", "sub_lord": "Saturn", "sub_sub_lord": "Mercury",
                     "tara": {"class": "vipat", "n": 12, "cycle": 2, "special": "desha"},
                     "avastha": {"baladi": "vriddha", "jagradadi": "swapna"},
                     "speed": 1.01, "retro": false, "combust": false, "boundary": false, "war": null}},
  "lagnas": {"asc": 36.16, "asc_nak": 3, "asc_nak_lord": "Sun", "asc_tara": "mitra", "mc": 0,
             "hora": 0, "ghati": 0, "indu": 0, "sree": 0, "varnada": 0,
             "cusps_placidus": {"7": 216.16}},
  "panchanga": {"tithi": 0, "tithi_lord": "", "vara_lord": "", "karana_lord": "", "yoga_lord": "", "day_birth": true},
  "vargas": {"D1": {"asc_sign": 2, "Sun": 11}, "D9": {"asc_sign": 11, "Sun": 3}},
  "features": {
    "dignity": {"Venus": {"D1": "exalted", "D9": "friend", "deep_exalt_dist": 3.35},
                "Moon":  {"D1": "neutral", "D1_compound": "enemy", "D9": "own"}},
    "lordship": {"Saturn": {"houses": [9, 10], "role": "yogakaraka"}, "Mars": {"houses": [7, 12], "role": "maraka"}},
    "aspects": [{"from": "Saturn", "to": "Sun", "kind": "10th", "virupa": 45.2}],
    "rashi_aspects": [{"from": 2, "to": [8, 5, 11]}],
    "strength": {"shadbala": {"Saturn": {"sthana": 178.04, "dig": 1.35, "kala": 28.54, "chesta": 23.47, "naisargika": 8.57, "drik": -32.71,
                                           "total": 207.26, "required": 300, "ratio": 0.69}},
                 "bhava_bala": {"10": 0}, "vimsopaka": {"Saturn": {"shadvarga": 0, "dasavarga": 0, "shodasavarga": 0}},
                 "ishta_kashta": {"Saturn": {"ishta": 0, "kashta": 0}}},
    "ashtakavarga": {"SAV": [22, 24, 23, 30, 33, 26, 28, 27, 37, 24, 29, 34],
                     "BAV": {"Saturn": [2, 2, 0, 3, 5, 5, 5, 2, 3, 3, 3, 6]},
                     "pinda": {"Saturn": {"rasi": 150, "graha": 83, "sodhya": 233}},
                     "kakshya": {"Saturn": "Saturn"}, "kakshya_bindu": {"Saturn": false}},
    "dispositors": {
      "sign":      {"Sun": ["Saturn", "Venus", "Jupiter", "Venus"], "Mars": ["Mars"]},
      "nakshatra": {"Mars": ["Mercury", "Mars"], "Mercury": ["Mars", "Mercury"]},
      "navamsa":   {"Venus": ["Saturn", "Saturn"]},
      "loops": [{"planets": ["Venus", "Jupiter"], "houses": [1, 11], "class_by_houses": "maha",
                 "class_by_lordship": "dainya", "taint": [6, 8]}],
      "final_sign": ["Mars"], "final_nakshatra": ["Mars", "Mercury"], "final_navamsa": ["Saturn"]},
    "sudarshana": {"H10": {"from_lagna": ["Sun", "Mercury"], "from_moon": [], "from_sun": ["Mars"]}},
    "sensitive": {"gandanta": [], "mrityu_bhaga": [], "pushkara_navamsa": ["Rahu"], "pushkara_bhaga": [],
                  "marana_karaka_sthana": ["Mars", "Saturn"], "boundary": ["Moon", "Mercury", "Saturn"]},
    "jaimini": {"AK": "Sun", "AmK": "Venus", "BK": "Mars", "MK": "Rahu", "PiK": "Jupiter",
                "PK": "Saturn", "GK": "Moon", "DK": "Mercury", "karakamsa": 3,
                "AL": 10, "UL": 3, "A2": 7, "A7": 5, "A10": 2,
                "argala": {"H10": {"by": ["Venus", "Jupiter", "Saturn", "Ketu"], "blocked_by": ["Mars"]}}},
    "kp": {"cusps": {"7": {"lon": 216.16, "star": "Saturn", "sub": "Mercury", "sub_sub": "Sun"}}, "ruling_planets": []}
  },
  "fired_rules": [{"id": "yoga.ruchaka", "school": "parashari", "basis": "lagna", "nodes": ["Mars", "H7"],
                   "scale": 0.6, "themes": {"courage": 3}, "stability": {"time": 0.98, "ayanamsa": 1.0, "house": 1.0}}],
  "dashas": {"vimshottari": [{"lord": "Mars", "level": 1, "start": "birth", "balance_years": 2.75, "quality": 0.62,
                               "tara": "pratyak", "sandhi": false, "activates": ["Moon", "Mercury"]}]},
  "scored": {"areas": {"career": {"score_classical": 0.78, "score_learned": null, "tier": "strong",
                                   "stability": {"time": 0.91, "ayanamsa": 1.0, "house": 0.95},
                                   "families_agree_w": 4.1, "families_total_w": 5.6}}},
  "uncertainty": {"samples": 200, "half_width_min": 2, "ayanamsas": ["lahiri", "raman", "kp"], "house_systems": ["whole_sign", "sripati"],
                  "varga_stability": {"D9": 0.78, "D10": 0.80, "D60": 0.43},
                  "varga_ayanamsa": {"D9": 0.67, "D12": 0.67}, "dasha_boundary_days": {"time": 3.7, "ayanamsa": 277}}
}
```

The `varga_stability` values above are the engine's for the reference chart at its true time under a ±2-minute uniform window (200 samples): D9 0.78 (the navamsa boundary is about 1.4 minutes of clock away), D10 0.80, D60 0.43. They are computed from the posterior, never typed. The same run gives the ayanamsa axis separately: the D9 and D12 lagnas hold under Lahiri and KP but not Raman (0.67), and Vimshottari maha boundaries move 277 days across the three ayanamsas against ±3.7 days across the time samples — which is why the axes are never pooled.

Storage: Postgres with JSONB for the chart object; a `pairing` document (two chart ids plus the synastry block) for the two-chart case; relational tables for outcomes (chart\_id, event, age\_at\_event, censor\_age, source, entered\_before\_reading), rule fires (run\_id, chart\_id, sample\_id, rule\_id, basis, scale, stability) and runs (run\_id, chart\_id, engine\_version, weights\_version, settings hash, timestamp), so Layer 6 queries are plain SQL and any reading can be reproduced from its run row.

## Tech stack

Python for the engine because the astronomy and the statistics libraries live there; TypeScript for the product.

| Part | Choice | Reason |
| --- | --- | --- |
| Ephemeris | `pyswisseph` with full DE441 files | Reference-grade; what the desktop programs use |
| Engine | Python 3.12, pure functions, `pydantic` models, `numpy` | Deterministic, unit-testable |
| Reference check | Jagannatha Hora exports for the Layer 1 cross-test; open-source `jhora` library as a second implementation to diff against | Catch our own arithmetic errors |
| Rules | YAML files in a git repo, loaded by a small evaluator; JSON Schema for the rule format | Astrologers edit without code |
| Retrieval | `pgvector` in Postgres + BM25 via `tantivy`; shloka corpus as versioned markdown | Hybrid search, one database |
| Learning | `scikit-learn` logistic regression, `lightgbm` for the tree variant, `statsmodels` for the baseline tests | Interpretable, standard |
| API | FastAPI, one endpoint per layer, chart object cached by birth-data hash | Reproducible, cheap to re-score |
| Narration | Claude via API with structured output (JSON schema enforced), prompt-cached corpus header | Citation enforcement, low cost per reading |
| Web | Next.js, chart rendering in SVG (North and South Indian styles), server components for the reading | Fast on phones |
| Data | Postgres (charts, outcomes, rule fires), S3 for ephemeris and corpus files | One store for app and research |
| Ops | Docker, GitHub Actions running the Layer 1 and rule-library test suites on every commit | Nothing ships with a changed longitude |

Compute budget: one reading is not one chart but roughly 1,200 (200 birth-time samples × 3 ayanamsas × 2 house systems). Layers 1 and 2 are vectorised with `numpy` over the sample axis, so a full reading computes in a few seconds on one core. The single cache key is `sha256(birth data, every meta setting — ayanamsa, node type, node aspects, house system, dasha year, karaka scheme, accuracy class — engine version, weights version)`; a change to any of them is a new run row. The rectification sweep is one pass over the window (its width from the accuracy class) with every known event scored at each candidate time, and runs interactively. Rules are evaluated once per sample and per basis, and each stability number is the share of samples on its axis in which the rule fires.

Licensing, corrected after audit: Swiss Ephemeris — including its Moshier routines — is AGPL-3.0 or a paid Astrodienst licence; there is no LGPL fallback. A commercial product either budgets the Astrodienst professional licence or computes positions from JPL kernels with `jplephem` / `skyfield` (MIT) plus an in-house sidereal conversion, validated against Swiss Ephemeris in development. PyJHora and Maitreya are GPL-family and are used only as development-time reference implementations for the Layer 1 cross-check, never linked into the product. Astro-Databank is CC BY-NC-SA and is confined to the non-commercial research track unless written permission is obtained. Classical-text translations are covered under Layer 7.

## Build phases

Six phases, each with a gate that must pass before the next starts; week counts are estimates for one engineer plus one astrologer-reviewer working full time.

&#91;embedded content: build roadmap · 6 phases, 5 gates\]

No phase skips its gate: a scoring layer built on an ephemeris that is 2° off is worthless, and an LLM reading on an unvalidated rule set is the product everyone already has.

The same phases as a table, so the plan survives export and the gates are quotable:

| Phase | Weeks | Scope | Gate |
| --- | --- | --- | --- |
| 0 Astronomical core | 1–4 | Ephemeris, ayanamsa, lagna, Placidus cusps, 16 vargas, nakshatras, special lagnas, panchanga, posterior sampler | Within 1″ of PyJHora/Maitreya on 1,000 births; boundary-aware varga match |
| 1 Feature engine | 5–10 | Dignity, lordship, aspects, Shadbala, Ashtakavarga, dispositor chains, Navatara, Jaimini, KP, synastry module | BPHS and Raman worked examples reproduce; reference chart prints the worked-example section exactly |
| 2 Rules and time | 11–18 | First 100 YAML rules with editions, Vimshottari to 5 levels, Yogini, Chara, transits with Ashtakavarga, tagged timeline, TimingQuery | Every rule cited with edition; dasha dates match reference software under each year-length setting |
| 3 Scoring and narration | 19–26 | 19 areas, confluence with measured family correlation, three stability numbers, rectifier, LLM with citation enforcement | Three blinded astrologers agree on top areas in 35 of 50 charts (a build gate, not evidence) |
| 4 Product and beta | 27–34 | Web app, chart rendering, learner mode, outcomes-first onboarding, rule library to 300 | 500 beta users, 2,000 dated outcomes captured before any reading was shown |
| 5 Validation | 35–44 | Sequestered split, permutation null, nested models, survival timing, abstention accounting, decoy test, pre-registration | Results published either way; probability wording stays off until the 20,000-chart cohort calibrates |

**What was done first, and what comes next (Phase 4, from 2026-10-21)**

1. Done, 2026-10-21, in the order the phases list: the astronomical core against the reference app; the feature engine printing the worked example; the first twelve rules, three dasha systems, transits, the tagged timeline and TimingQuery; the sampler stamping every finding; Layer 5 scoring with measured family correlation, polarity v3, driver v2, varga v2 and KP v2; timing join v2.1; Layer 7 narration with the validator and the checker; `jyotish read` and `jyotish page`. Six readings of the reference chart audited claim by claim (Worked example). What the SPEC promised and the code does not yet have: special lagnas, the synastry module, the rectifier, the retrieval corpus, learner-mode dispositor and Navatara context, the model-drafted question-to-query translation, and all of Layer 6.
2. Phase 4 starts from the reading as it stands (`examples/reference_reading.json` in the repo, the SPEC output schema) and the four mockups (`design/mockups`, exported from the design canvas). First, the engine answers the question it was asked: when the question is a "when", the page's summary carries an engine-written timing line — the best window with its lords and strongest piece, and the avoid window — since the model may not write about timing and the sixth reading answered "when is the best time" only in a table.
3. Speed: a live reading takes ten to fifteen minutes because the checker calls run one after another; they are independent, so they run concurrently, and the chart (`assess`, 200 samples) is cached by birth data and conventions. Target: a reading in under two minutes, measured on the reference chart and written here.
4. The service: `POST /readings` with birth data and a question returns a job id; `GET /readings/{id}` returns the reading JSON and the page once done, with progress (chart, score, draft n, check n) while it runs. The model key lives on the server only. Charts and readings are stored as the Data schema says (Postgres, JSONB), keyed by chart id, so a reading is reproducible from its header.
5. The front-end from the mockups: Home (birth-data form with the accuracy class, and the honest-scope text), Reading (summary with its engine fields, areas with tier, three stability numbers and polarity touches, claims with their citations as footnotes, the learner panel per claim rendered from the derivation), Timing (the windows table with q, t, strongest piece and the avoid window), and the phone layout. Every number on a screen comes from the reading JSON; the UI invents nothing, and the wording rules of Layer 6 (no probability until calibrated, tier words verbatim, "depends on exact birth time" shown, not hidden) are enforced in the components, not in copy.
6. Outcomes-first capture (Layer 6): before a reading is shown, the dated-events form (marriage, children, job changes, moves, illnesses, with the age and the censor age) is offered and stored with the chart id; readings never update an outcome. This is the only way Layer 6 ever gets data that is not contaminated by the reading.
7. The beta gate stays as the phase table says; the gate we can run ourselves before any user sees a reading is twenty real charts, each read live and audited the way the reference chart's six readings were, with every fault going into the SPEC first.

## Worked example — the reference chart

The Taurus-lagna chart from the app screenshots is the engine's reference case, used with its owner's consent to test every feature as it is built: born 2001-03-12 at 10:10:25 IST in Rewari, Haryana (28.20 N, 76.62 E). Every layer must reproduce the values below before anything else is built. Layer 1 values come from the app's screenshots, which were made with the time entered as 10:10:00, and are the target the ephemeris must match at that time. At the true time, 10:10:25, the ascendant is 06°17'31" Taurus (7 arc-minutes later) and the Moon 15" further on; every house, sign and varga conclusion below is unchanged except the D24 lagna. Those 25 seconds are themselves a demonstration of Layer 1b.

**Layer 1 targets (D1, Lahiri)**

| Body | Sign | Degree | Nakshatra-pada | D9 sign |
| --- | --- | --- | --- | --- |
| Ascendant | Taurus | 06°09'50" | Krittika-3 | Aquarius |
| Sun | Aquarius | 27°47'55" | PurvaBhadra-3 | Gemini |
| Moon | Libra | 01°25'19" | Chitra-3 | Libra (vargottama) |
| Mars | Scorpio | 18°37'10" | Jyestha-1 | Sagittarius |
| Mercury | Aquarius | 00°22'00" | Dhanishtha-3 | Libra |
| Jupiter | Taurus | 10°38'44" | Rohini-1 | Aries |
| Venus (R) | Pisces | 23°39'19" | Revathi-3 | Aquarius |
| Saturn | Taurus | 02°06'21" | Krittika-2 | Capricorn |
| Rahu (R) | Gemini | 18°05'56" | Aridra-4 | Pisces |
| Ketu (R) | Sagittarius | 18°05'56" | PurvaAshadha-2 | Virgo |

**Layer 2 expected features**

- Lordship: Venus 1/6, Mercury 2/5, Moon 3, Sun 4, Mars 7/12, Jupiter 8/11, Saturn 9/10 → Saturn = yogakaraka. Marakas by lordship: Mars (7th) and Mercury (2nd); Venus, as lagna lord, is exempt.
- Dignity (natural friendships first; compound in brackets where it differs): Venus exalted (3°21' short of deep exaltation at 27° Pisces); Mars own sign; Saturn in a friend's sign (Venus); Mercury in a neutral sign (Saturn); Sun in an enemy's sign (Saturn); Jupiter in an enemy's sign (Venus); Moon in a neutral sign (Venus) \[compound: enemy, because Venus is 6th from the Moon\].
- Baladi avasthas (forward in odd signs, reversed in even): Moon 1°25' Libra (odd) = Bala, infant; Mercury 0°22' Aquarius (odd) = Bala; Saturn 2°06' Taurus (even) = Mrita, dead; Jupiter 10°38' Taurus = Vriddha, old. The yogakaraka is in Mrita avastha, which the scoring must weigh against its placement.
- Marana Karaka Sthana: Mars in the 7th and Saturn in the 1st are both in MKS; Ruchaka and the yogakaraka-in-lagna fires both carry the 0.6 modifier.
- Boundary flags: Moon, Mercury, Saturn and the Sun (27°48', within 3° of the Pisces edge) are flagged; every fire that depends on their house or sign is marked sensitive.
- D9 dignity: Saturn own sign (Capricorn); Moon vargottama (Libra); Venus in Aquarius (friend's sign); Mars in Sagittarius (friend's); Jupiter in Aries (friend's); Mercury in Libra (friend's); Sun in Gemini (neutral).
- Aspects: Saturn (H1) → H3, H7 (Mars), H10 (Sun, Mercury). Jupiter (H1) → H5, H7 (Mars), H9. Mars (H7) → H1 (Jupiter, Saturn), H10, H2 (Rahu). Mutual Mars–Saturn and Mars–Jupiter aspects across 1/7. Node aspects off by default.
- Jaimini chara karakas, 8-karaka scheme (Rahu counted as 30° − 18°05' = 11°54'): AK Sun 27°47', AmK Venus 23°39', BK Mars 18°37', MK Rahu 11°54', PiK Jupiter 10°38', PK Saturn 2°06', GK Moon 1°25', DK Mercury 0°22'. 7-karaka scheme (no Rahu; Matri and Pitri karakas merge into MK): AK Sun, AmK Venus, BK Mars, MK Jupiter, PK Saturn, GK Moon, DK Mercury. DK is Mercury under both, sitting in the 10th with the Sun. Karakamsa (AK's navamsa) = Gemini.
- Arudha padas, with the 1st/7th exception applied: AL = Capricorn (H9; Venus is 11th from Taurus, 11th from Pisces). UL = Gemini (H2, with Rahu in it; Mars is 8th from Aries, 8th from Scorpio). A7: Mars sits in the 7th itself, so the pada would be Scorpio — the exception takes the 10th from it → Leo (H4). A10: Saturn is 4th from Aquarius, 4th from Taurus = Leo, which is the 7th from Aquarius — the exception takes the 10th from Leo → **Taurus**, the lagna itself, with Jupiter and Saturn. A2 = Libra (H6, with the Moon).
- Sudarshana 10th house: from the Lagna, Aquarius with Sun and Mercury; from the Moon, Cancer, empty; from the Sun, Scorpio, with Mars in own sign.
- KP 7th cusp (Scorpio 06°09'50" under whole-sign; Placidus moves it slightly): Anuradha, star lord Saturn, sub lord Mercury (2°49'50" into the nakshatra, past Saturn's 2°06'40" sub), sub-sub lord Sun.
- Pushkara: Rahu at 18°05' Gemini is in a Pushkara navamsa (16°40'–20° of an air sign, the Pisces navamsa) and within a degree of the Pushkara bhaga (18° Gemini); the Moon at 1°25' Libra is in neither.

**Dispositor chains on the reference chart**

- Sign chain: every planet except Mars funnels into one loop. Sun, Mercury → Saturn (Aquarius lord) → Venus (Taurus lord) → Jupiter (Pisces lord) → Venus. Moon → Venus. Rahu → Mercury → Saturn → Venus. Ketu → Jupiter. Mars is self-disposited in Scorpio. Final sign dispositors: the Venus–Jupiter loop and Mars.
- Nakshatra chain, followed to termination: Lagna and Saturn → Sun (Krittika) → Jupiter (PurvaBhadra) → Moon (Rohini) → Mars (Chitra) ⇄ Mercury (Jyestha / Dhanishtha, a mutual nakshatra exchange). Venus → Mercury (Revati). Ketu → Venus → Mercury. Rahu → Rahu (Ardra, self). So every body except Rahu ends in the Mars–Mercury loop: final nakshatra dispositors are Mars and Mercury, with Rahu self-disposited.
- Navamsa chain: Venus (Aquarius) → Saturn (Capricorn, own); Sun, Moon, Mercury and Ketu also end in Saturn through Mercury and Venus. Jupiter (Aries navamsa) and Mars (Sagittarius navamsa) are in mutual navamsa exchange — a D9 Parivartana — and Rahu (Pisces navamsa) feeds into it. Final navamsa dispositors: Saturn and the Jupiter–Mars loop.

**Navatara from the Moon (Chitra = Janma).** Counted from Chitra as 1 through three cycles of nine. Special taras by absolute count are recorded as well: the Sun in PurvaBhadra is the 12th (Desha), Mercury in Dhanishtha the 10th (Karma), Jupiter in Rohini the 18th (Samudaya); none of the bodies falls on the 16th (Sanghatika), 19th (Adhana), 23rd (Vinasha), 25th (Manasa) or 27th (Jati). The "2nd and 3rd cycle milder" reading applies to the nine-fold class only, never to a special tara.

| Body | Nakshatra | Tara | Cycle | Read as |
| --- | --- | --- | --- | --- |
| Lagna | Krittika | Mitra (8) | 2 | supportive |
| Sun | PurvaBhadra | Vipat (3) | 2 | adverse; Sun dasha flagged |
| Moon | Chitra | Janma (1) | 1 | neutral, personal |
| Mars | Jyestha | Pratyak (5) | 1 | adverse; first dasha flagged |
| Mercury | Dhanishtha | Janma (1) | 2 | neutral |
| Jupiter | Rohini | Ati-mitra (9) | 2 | supportive |
| Venus | Revati | Pratyak (5) | 2 | adverse, milder (2nd cycle) |
| Saturn | Krittika | Mitra (8) | 2 | supportive |
| Rahu | Ardra | Sampat (2) | 3 | supportive |
| Ketu | PurvaAshadha | Vadha (7) | 1 | adverse; Ketu dasha flagged |

**Ashtakavarga (computed 2026-10-21, verified by hand for the Sun and Saturn rows)**

|  | Ari | Tau | Gem | Can | Leo | Vir | Lib | Sco | Sag | Cap | Aqu | Pis | Total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sun | 2 | 3 | 3 | 4 | 6 | 4 | 4 | 4 | 5 | 3 | 5 | 5 | 48 |
| Moon | 5 | 3 | 2 | 6 | 5 | 5 | 3 | 4 | 6 | 2 | 3 | 5 | 49 |
| Mars | 3 | 3 | 3 | 3 | 4 | 1 | 3 | 3 | 5 | 2 | 5 | 4 | 39 |
| Mercury | 3 | 5 | 6 | 5 | 4 | 1 | 5 | 5 | 6 | 5 | 4 | 5 | 54 |
| Jupiter | 4 | 5 | 5 | 4 | 6 | 4 | 4 | 7 | 5 | 2 | 6 | 4 | 56 |
| Venus | 3 | 3 | 4 | 5 | 3 | 6 | 4 | 2 | 7 | 7 | 3 | 5 | 52 |
| Saturn | 2 | 2 | 0 | 3 | 5 | 5 | 5 | 2 | 3 | 3 | 3 | 6 | 39 |
| Lagna | 3 | 5 | 2 | 6 | 4 | 4 | 4 | 5 | 3 | 3 | 4 | 6 | 49 |
| **SAV** | 22 | 24 | 23 | 30 | 33 | 26 | 28 | 27 | 37 | 24 | 29 | 34 | 337 |

Reading for the chart: the strongest signs are Sagittarius (H8, 37), Pisces (H11, 34) and Leo (H4, 33); the weakest are Aries (H12, 22), Gemini (H2, 23), Taurus (H1, 24) and Capricorn (H9, 24). The 10th house, Aquarius, holds 29, just above the 28 mean. After Trikona and Ekadhipatya reduction (occupants = seven planets, no zero exemption, BPHS ch. 68) the Sodhya Pindas are Sun 122, Moon 85, Mars 130, Mercury 122, Jupiter 198, Venus 121, Saturn 233. Kakshya: the Sun sits in the Lagna's kakshya with a bindu, the Moon in Saturn's with a bindu, Mars in Venus's without, Saturn in its own without.

**Shadbala (computed 2026-10-21 at 10:10:00; every Sthana, Dig and Kala component checked by hand)**

| Planet | Sthana | Dig | Kala | Chesta | Naisargika | Drik | Total | Required | Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sun | 219.9 | 47.5 | 125.8 | 51.6 | 60.0 | −24.9 | 479.8 | 390 | 1.23 |
| Moon | 70.5 | 36.3 | 197.1 | 97.6 | 51.4 | 5.5 | 458.3 | 360 | 1.27 |
| Mars | 211.9 | 39.5 | 84.6 | 37.3 | 17.1 | 0.7 | 391.1 | 300 | 1.30 |
| Mercury | 209.9 | 28.1 | 208.4 | 33.9 | 25.7 | −5.8 | 500.2 | 420 | 1.19 |
| Jupiter | 180.9 | 58.5 | 213.8 | 25.9 | 34.3 | −35.9 | 477.4 | 390 | 1.22 |
| Venus | 207.9 | 21.2 | 135.6 | 52.1 | 42.9 | −20.3 | 439.4 | 330 | 1.33 |
| Saturn | 178.0 | 1.4 | 28.5 | 23.5 | 8.6 | −32.7 | 207.3 | 300 | 0.69 |

Saturn is the only planet below its required minimum: 4° from the ascendant, its weakest Dig point, with low Kala (nocturnal planet, day birth) and Mars's full aspect in Drik. Conventions used: BPHS Drekkana sex assignment and Saptavargaja scale, Dig from the ascendant and MC, apparent noon, Mercury malefic by association, Moon's Paksha and Sun's Ayana doubled, 24° obliquity, Chesta by the BPHS kendra method with modern mean motions, Abda and Masa lords by ahargana from the Kali epoch. Each is a `Meta` setting. Not yet compared with Jagannatha Hora; the Abda/Masa and Yuddha rules are the ones to check there.

**Layer 3 expected rule fires**

- `yoga.ruchaka` fires twice: from the lagna (Mars own sign in H7) and from the Sun (Mars is 10th from Aquarius), not from the Moon (2nd from Libra). Scale 0.408 both times: Saturn's aspect 0.8 × Pratyak tara 0.85 × Marana Karaka Sthana 0.6; the Shadbala modifier does not apply, Mars's ratio being 1.30.
- `yoga.parivartana` (Venus–Jupiter) fires at 0.8 — see below.
- `yoga.budhaditya` (Sun + Mercury, H10) fires at 0.9: Mercury at 0°22' is in Bala avastha and carries a boundary flag; not combust (27° apart).
- `yoga.kendra_trikona_raja` fires once under BPHS 34.15 as read with ch. 7 vv. 33–36 (a lord who also owns the 6th, 8th or 12th makes no Raja yoga): Sun (4th lord) with Mercury (5th lord) in H10, scale 1.0. The Mars–Saturn mutual aspect (7th and 9th lords) is excluded because Mars owns the 12th; it fires only under the uncited, \`experimental\` rule yoga.kendra\_trikona\_raja\_weak at 0.75, which is outside default scoring. yoga.gaja\_kesari\_bphs (BPHS 36.3–4, stricter than Phaladeepika's Kesari) does not fire either: Jupiter is in an enemy's sign.
- `lord.yogakaraka_in_lagna` (Saturn) — not yet a rule file; expected scale 0.6 × 0.8 × 0.5: Marana Karaka Sthana, Mrita avastha, and Shadbala below its required minimum (0.69).
- `lord.lagna_exalted` (Venus) — not yet a rule file; expected full scale.
- `affliction.mangal_dosha` — not yet a rule file; expected to fire from the Lagna (Mars in H7) and from the Moon (Mars 2nd from Libra), not from Venus (9th from Pisces), with cancellation modifiers for Mars in own sign and for Jupiter's aspect.
- `yoga.gaja_kesari`, `yoga.neecha_bhanga`, and the other four Mahapurusha yogas (Bhadra, Hamsa, Malavya, Sasa) do **not** fire; Gaja Kesari because Jupiter is 8th from the Moon.
- `affliction.kala_sarpa` — not yet a rule file; must not fire: planets on both sides of the Rahu–Ketu axis.

Missed in the first draft and caught by the dispositor pass: `yoga.parivartana` fires between Venus (in Pisces, Jupiter's sign) and Jupiter (in Taurus, Venus's sign). Classified both ways, because the modern texts define it both ways: by the houses exchanged it is the 1st and the 11th → **Maha Parivartana**; by the lordships of the exchanging planets (Venus 6th, Jupiter 8th) it is **Dainya**. The Dainya/Khala/Maha classification is from B.V. Raman's *Three Hundred Important Combinations*; its attribution to Uttara Kalamrita, common in secondary literature, could not be confirmed in the Sastri edition and is not claimed. The fire carries `class_by_houses: maha`, `class_by_lordship: dainya` and a 0.8 scale for the Dainya reading, and the narration states both. This is exactly the kind of signal a human reader skips and a graph engine cannot.

**Layer 4 expected timing**

- Vimshottari starts in Mars dasha (Moon in Chitra). Chitra runs Virgo 23°20' to Libra 6°40'; the Moon has covered 8°05'19" of its 13°20', so 39.3% remains → Mars balance at birth ≈ 2 years 9 months (365.25-day year).
- Order: Mars 7y → Rahu 18 → Jupiter 16 → Saturn 19 → Mercury 17 → Ketu 7 → Venus 20 → Sun 6 → Moon 10.
- Navatara of the dasha lords: Mars Pratyak, Rahu Sampat, Jupiter Ati-mitra, Saturn Mitra, Mercury Janma, Ketu Vadha, Venus Pratyak (2nd cycle), Sun Vipat (2nd cycle), Moon Janma.

**Other dashas (computed 2026-10-21)**

- Yogini: Chitra gives Mangala (Moon, 1 y) first, 0.393 y left at birth — the same fraction as the Vimshottari balance; the Siddha antardasha runs at birth. Then Pingala 2, Dhanya 3, Bhramari 4, Bhadrika 5, Ulka 6, Siddha 7, Sankata 8.
- Chara, K.N. Rao variant (default): the 9th from Taurus is Capricorn, not a savya sign, so the sequence runs anti-zodiacally — Taurus 10, Aries 7, Pisces 10, … Gemini 8, first cycle 85 years; the second cycle repeats the first (his worked example, not a stated rule). Raman's variant gives 87 (exalted Venus adds a year to Taurus and Libra); Rath's Narayana form gives 88 and runs zodiacally because Saturn sits in the starting sign. Every variant caps a sign at 12 years; only Rath states the cap. All three are `Meta.chara_variant` settings.
- Citations: 16 of the 17 rule sources are now `checked: true` against the scanned editions. Two corrections came out of that: Budhaditya is not named in Phaladeepika and is cited to 18.1 (effects of the Sun with Mercury) with a note; the kendra-trikona Raja yoga is BPHS 34.11–12 with 34.15, not ch. 39.

**Transits (computed 2026-10-21; ingress dates checked against published Lahiri ephemerides)**

- Sade Sati: 2009-09-09 to 2017-01-26, again 2017-06-21 to 2017-10-26 (Saturn's retrograde slip back into Scorpio), and from 2038. Nodal returns 2019 and 2038 (mean node); Saturn return 2029–2031. Returns count only after half a revolution, which stopped them registering at birth.
- On 2026-10-21: Saturn in Pisces (6th from the Moon, good, BAV 6, SAV 34, Murthi gold), Jupiter in Cancer until 2026-10-31 (10th from the Moon, not good), Rahu in Aquarius / Ketu in Leo (Ketu's 11th is good but Vedha'd by the Moon), Mars in Cancer, Sun in Libra. No named window active.
- Sources: gochara and Vedha tables from Phaladeepika 26.3–8 and the Ashtakavarga transit grading from 23.11, both read in the 1937 edition; Vipareeta Vedha and Murthi Nirnaya are from later texts and marked unverified; a 0-bindu transit is reported as "severe" and no further, because 23.11's reading of it concerns death. Rahu and Ketu are exempted from Vedha on each other (always 7th apart; the text never names the nodes), an engine choice recorded in the table.

**Stability report (computed 2026-10-21; Layer 1b connected to the rules)**

- Time axis, 200 samples, uniform ±2 min at 10:10:25: every fired rule holds in 100% of samples. Lagna by varga: D1 1.00, D9 0.78, D10 0.80, D12 1.00, D30 1.00, D60 0.43. Vimshottari maha boundaries move ±3.7 days (sd 2.3).
- Ayanamsa axis (Lahiri, Raman, KP): every fire holds; the D9 and D12 lagnas do not — under Raman the ascendant passes 6°40' Taurus and the navamsa lagna becomes Pisces. Vimshottari boundaries move 277 days across the three.
- House axis (whole sign, Sripati): under Sripati the Sun moves to H11, Venus to H12, Rahu to H3, Ketu to H9; Saturn rules the 10th and 11th and is no longer yogakaraka; the Sun–Mercury kendra-trikona Raja yoga dissolves (house-robustness 0.50). Ruchaka, Budhaditya and the Parivartana hold.
- Sripati convention: bhava madhyas at the ascendant, IC, descendant and MC with each quadrant trisected; sandhis at the midpoints; a house's lord is the lord of the sign on its madhya; houses from the Moon and Sun stay whole-sign. The rule follows the usual summary of Sripati Paddhati; the verse was not read.

**Bhava Bala, Vimsopaka, Ishta/Kashta and Argala (computed 2026-10-21)**

- Bhava Bala (BPHS 27.26–31 in Santhanam's edition — not ch. 28; the day/night term goes by the sign's rising type, not by the sex of planets, and each house gains 60 for Jupiter or Mercury in it and loses 60 for Saturn, Mars or the Sun), in rupas, whole sign: H1 7.2, H2 8.9, H3 7.7, H4 8.5, H5 9.0, H6 8.2, H7 7.4, H8 9.0, H9 4.6, H10 4.5, H11 8.2, H12 6.7. The 10th is the weakest house: its lord Saturn is weak and the Sun sits in it. Settings: rising-sign table (BPHS vs Phaladeepika) and twilight width (24 min default; the verse does not define it).
- Vimsopaka (BPHS 7.17–25), Shadvarga/Saptavarga/Dasavarga/Shodasavarga: Venus 13.8/14.5/15.7/15.6 and Saturn 17.2/15.5/16.4/16.4 are "full"; Mercury 15.3/15.2/14.5/14.5 and Mars 13.8/13.3/11.7/11.8 "mediocre"; Sun, Moon and Jupiter "some". Ishta/Kashta by BPHS 28.2–6 (the mean of Uchcha and Chesta): Venus 55.5/4.5, Mars 37.1/22.9, Sun 36.6/23.4, Jupiter 33.9/26.1, Moon 29.7/30.3, Mercury 24.4/35.6, Saturn 13.8/46.2; the square-root form is a setting marked unverified.
- Argala (Jaimini Upadesa Sutras 1.1.4–9 as read in Rath's srath.com article; BPHS 31.2–9 read in Santhanam): on H10, Venus from the 2nd and Ketu from the 11th unobstructed; Jupiter and Saturn from the 4th prevail over Mars's obstruction from the 10th; Rahu's secondary Argala from the 5th prevails over the Moon. The node rule is Rath's: when Ketu occupies the sign being judged, everything is counted backwards from it — which applies to H8 (Sagittarius) on this chart; BPHS's other reading is a setting. Which side prevails follows Rath's order (the Atmakaraka's sign, then more planets, dignity, dual over fixed over movable, Jupiter's aspect; a dead heat is Bandhana — H5 and H11 here), taken from Google Books snippets of his 1997 translation and so marked unverified. Rath's further pairs (8th obstructed from the 6th, 7th from the 1st) are not computed.

**Layer 5 expected ranking (classical weights, before calibration)**

- Engine result under the v1 votes (classical weights, 2026-10-21; tiers are agreement between signal families with 1 − ρ weighting, where ρ ranges 0.08 (lord) to −0.01 (KP) on the 10,000-chart run): career **strong** (0.83); marriage **strong** by a hair (0.71, the Upapada family voting against, six others for); wealth **moderate** (0.49; the Arudha family votes against because the waning Moon sits in A2, and the varga family abstains); health and debts/enemies strong; longevity and mother/home moderate; personality and foreign weak/mixed; nine areas not emphasised. Polarity flags as implemented under v1: delay/intensity on career, marriage and health, volatility on wealth.
- Classical reader's expectation before any code (kept for Layer 6 to adjudicate, never as a target the code was tuned to): career strong, wealth strong, marriage moderate with a delay/intensity flag. The engine and the reader disagree on wealth and marriage; the tests assert the engine and say why.
- Under the v1 KP vote career depended on the birth minute: moderate at 10:10:25 and strong a minute later, because the 10th-cusp sub-lord switches from Ketu to Venus; the tier held in 61% of ±2-minute samples, and the printed-position chart, with no KP cusps, showed strong. That was the stability report doing its job on a vote later found to be wrongly defined.
- Engine result under the v2 votes (varga v2, KP v2; 2026-10-21; ρ and p40 tables regenerated per setting pair over the same 10,000 charts, ρ moving under 0.01 per family): career **moderate** at confidence 0.6997 against the 0.7 cut, stable on every axis (1.00 / 1.00 / 1.00) — all seven family votes hold in every sample; the KP vote abstains, since Ketu's star lord Venus (11th; owns 1 and 6) meets both the matter houses (6, 11) and a denial house (1), and Ketu itself through its sign lord Jupiter (1st; owns 8 and 11) does the same. What holds career under the cut is 0.0003 of confidence, from two named readings kept as the spec's: an abstention counts in the applicable weight (KP's "both" is a mixed verdict, not an absence — a cusp with no sub-lord is the absence), and the varga consistency scaling (5 of 7 career planets agree between D1 and D10, weight 0.978 → 0.839); either reading reversed would make career strong, and both are listed for Layer 6. Marriage **moderate** (0.696; no vote changed, but only half its varga pairs agree, weight ×0.75). Health **weak / mixed** (0.325): the varga vote turns against on the Sun debilitated in D30 and D3, and the KP vote turns against because the 6th-cusp sub-lord Jupiter's star lord is the Moon in the 6th — a disease house; health is 0.91 on time (the KP vote changes inside the ±2-minute window) and 0.67 on ayanamsa. Debts/enemies moderate (varga against; 0.67 on ayanamsa); mother/home weak/mixed (a new KP vote against: star lord Mercury owns the 5th, a denial house). Top three: career, marriage, longevity. Votes that moved from v1 to v2 — varga: siblings, health, debts/enemies, father, gains +1 → −1, children 0 → −1, intellect −1 → +1; KP: personality 0 → −1, mother/home none → −1, children +1 → 0, health +1 → −1, career −1 → 0, mind +1 → none.
- Driver under the v1 product formula: Mercury 6.92, Sun 5.94, Venus 5.20, Mars 3.85, Jupiter 1.98, Moon 0, Saturn 0 — Saturn scores zero because no rule fires on him, which is why v1 was rejected and the sum formula above adopted. Dispositor-graph alternates: Jupiter, Mars, Venus.

* Driver under v2 (sum of five 0–1 terms, min–max scaled across the chart's seven planets): Venus 3.23, Mars 2.84, Mercury 2.75, Jupiter 2.44, Sun 2.36, Saturn 2.33, Moon 0.91. Venus is exalted lagna lord, Amatyakaraka and in the dispositor loop; Saturn has the top Vimsopaka and Sodhya Pinda and the yogakaraka role but the lowest Shadbala ratio and no rule fired, so it ranks sixth — the "strong role, weakened condition" reading in one number.
* Population cut (40th percentile per area over the 10,000-chart run): three areas not emphasised (children, father, gains); siblings, intellect, fortune, spirituality, mind and reputation are weak/mixed; career, wealth and marriage unchanged.
* Timing v1, "career, 2026–2036": the top windows fall in May 2030 – March 2031 during Vimshottari Jupiter–Venus, when Jupiter and Saturn together touch the 10th or its lord; edges move ±0.5 day across birth-time samples and about 40 days across ayanamsas. Under v1 the transit term (up to 1.0) dominated a dasha-quality term of 0.1–0.26 and every sub-period boundary cut the decade into month-long windows, which is why the join is revised to v2 above.

**Timing v2, polarity v3 and the first narrated reading (computed 2026-10-21)**

- Timing v2 as implemented, "career, 2026–2036" (area moderate, reported beside the windows): Oct 2029 – Jun 2032 Jupiter–Venus, joint 0.89 (q 0.82), strong; Jan – Aug 2026 Jupiter–Saturn, 0.85 (q 0.76), strong; Aug 2026 – Nov 2028 Jupiter–Mercury, 0.84 (q 0.73), moderate (sandhi: the 2028 Chara and Yogini maha changes); avoid Nov 2028 – Oct 2029 Jupiter–Ketu, 0.60 (q 0.33; Ketu 8th from Jupiter, in Vadha tara). Edges move ±3.7 days over the birth-time samples and 277 days across ayanamsas. The transit term was 1.0 for every window, which is why the targets are narrowed in v2.1.
- Timing v2.1, engine result (the prototype reproduced on every window). Targets for career: Aquarius (H10) and Taurus (Saturn, its lord, and the lagna) in full; Gemini, Libra and Pisces at half. "Career, 2026–2036": Oct 2029 – Jun 2032 Jupiter–Venus, 0.84 (q 0.82, t 0.88), strong, strongest piece May – Sep 2030 at 0.89 with Saturn in Taurus and Jupiter in Libra both on a full target; Oct 2027 – Feb 2028 Jupiter–Mercury, 0.84 (t 1.0: Saturn in Pisces aspecting Taurus, Jupiter in Leo aspecting Aquarius), moderate (sandhi); Jan – Aug 2026 Jupiter–Saturn, 0.83 (t 0.95), strong, truncated by the range start; avoid Nov 2028 – Aug 2029 Jupiter–Ketu, 0.47 (q 0.33, t 0.67), with the 5–23 Oct 2029 sliver absorbed into it and listed. From 2026-10-21 the first two windows are the same and the third is Oct 2026 – Jan 2027 Jupiter–Mercury (0.83, truncated). Across the decade t runs from below 0.7 to 1.0, so the transit term ranks windows again. The sampler's edge movement is unchanged (±3.7 days by time, 277 days by ayanamsa).
- Polarity v3: career loses "delay" (Saturn is the 10th lord) and keeps "intensity" (Mars touches H10, its lord Saturn and the karaka Sun); reputation loses "delay"; marriage unchanged; 13 of 18 areas still carry a flag; no tier changes.
- First narrated reading, "How will my career go, and when is the best time for a job change?", from the hand-authored fixture (the model has not yet been called): routed to career as a "when" question; four rule findings offered (Kendra-Trikona Raja and Budhaditya from the lagna, Ruchaka from the lagna and from the Sun); every tag in the draft is one the engine offered and every sentence checks against the chart (Sun, 4th lord, with Mercury, 5th lord, in the 10th; Mercury at 0°22′ in Bala avastha; Mars own-sign in the 7th and 10th from the Sun; the three Ruchaka modifiers). Engine fields beside the prose: tier moderate, stability 0.605 / 0.67 / 0.5 (sensitive), driver Venus with Jupiter and Mars as alternates, current period Jupiter–Mercury, abstained children, father, gains and synastry; polarity intensity with its three touches; school conflict KP against the four Parashari families.
- Second reading, with the votes as findings: career offers ten findings, the four rule fires and six votes (arudha abstains). Each vote sentence of the re-authored fixture was checked against the engine's derivation: the house vote for, with the 10th itself the weakest of the twelve houses at 4.51 rupas of Bhava Bala (the 9th next at 4.62) and the career houses from the three bases still leaning for; the lord vote for, Venus (6th lord) exalted in the 11th at Shadbala ratio 1.33 and Mars own-sign outweighing Saturn (10th lord) in a friend's sign at 0.69 and Jupiter (11th lord) in an enemy's sign; the karaka vote for, led by Venus as Amatyakaraka against the Sun in an enemy's sign; the varga vote for, narrowly, Venus, Saturn and Mars agreeing between D1 and D10 while the Sun and Jupiter do not; the KP vote against, the 10th-cusp sub-lord Ketu in the 8th owning no house, holding in 61% of birth-time samples; the panchanga vote for, Mars (tithi 18 and Chitra lord) and the Moon (Monday) both area lords above their required Shadbala. The ordering under the single stability × confidence rule put all six votes (0.92–1.0, from 1 − ρ) above the Raja yoga (0.60, from scale × confidence\_base) and Ruchaka last (0.29), which is why item 4 now orders in two groups. The derivation rows for Scorpio (10th from the Sun) are labelled "house 7", which the fixture narrates as "lord of the 7th" — true from the lagna, the wrong reason; item 8 now requires the basis on every row.
- Items 4 and 8 as implemented (2026-10-21): career's claims now run Kendra-Trikona Raja (1.0 × 0.6), Budhaditya, Ruchaka from the lagna and from the Sun, then the six votes with KP last on its 0.605 stability; 1 − ρ clipped to 1. The house and lord rows are built from all three bases with the house number from each: Scorpio appears three times — the 10th from the Sun, the 2nd from the Moon, and from the lagna as the 7th marked as the 10th's Bhavat Bhavam, which is the reason the earlier row said "house 7" and the sampler-era reading could not state. Karaka, KP and arudha rows say they are counted from the lagna; panchanga rows list each basis and house their lord rules. The fixture's lord sentence now reads "Mars, lord of Scorpio, the 10th from the Sun".
- Third reading, the first from the real model (claude-opus-5-5, effort medium, 17 seconds, accepted on the first attempt with zero validator errors; frozen as `narration_career_opus55_r1.json`): a three-sentence summary and ten claims. Every number and placement the model wrote matches the engine — the 4th lord with the 2nd/5th lord in the 10th, Mercury's avastha reduction, the three Ruchaka modifiers from both bases, H10 weak with H2, H6 and H11 strong, Saturn friendly and weak in the lagna, Venus exalted in the 11th, the D10 split, Ketu in the 8th owning no career house, Mars and the Moon as panchanga lords. What the validator could not see: the KP sentence's appositive attaches "in the star of the Moon" to Ketu, which is in Purva Ashadha (Venus) — the cusp is in the Moon's star — so the sentence reads false (item 10); the summary's timing sentence is tagged with the house vote and its five-family sentence cites two votes (item 11); "the 10th from the Moon holds up well" for a house at +0.06 relative Bhava Bala is generous, not false. The validator found nothing to reject, which means the writer is good and the checks were too narrow; the Ketu sentence is the first error of meaning on record and the reason the checker exists.
- Fourth reading, the first through validator and checker (claude-opus-5-5, 4½ minutes, 33 calls: three writer drafts and ten checker calls per draft; accepted on the third attempt; the validator passed all three drafts, so every retry was the checker's). The KP sentence came out right unprompted: "the 10th cusp lies in the Moon's star, and its sub-lord Ketu sits in the 8th house and owns no houses". Four rejections, all correct against the derivations: Ruchaka from the Sun said "again" and "the same weakening", referring to the lagna fire the checker cannot see; the varga vote said "slightly", which the scores (+1, +1, +1, 0, 0, −1, −1) support but the derivation never states; the house vote called the 2nd, 6th and 11th "strong" with no basis named, and from the Moon the 2nd (Scorpio) is −0.04 — a real ambiguity, caught; the karaka vote called Saturn's 0.69 "modest", which the checker read as weak. The house and karaka sentences had passed unchanged on attempt 1 and were rejected on attempt 2: the checker is a sample, hence item 10's revisions. The accepted draft was audited claim by claim against the engine and holds, including the attempt-3 wording "stronger than average" (each house's relative value is its Bhava Bala against the chart's own twelve) and the panchanga sentence's "the Moon rules the 10th from the Moon and the 6th from the Sun" (the Moon is in Libra; both are Cancer).
- Fifth reading, the first complete one: `jyotish read` on the birth data, live, three areas (career as asked, then the chart's top three — health, career, marriage), three attempts, 23 claims, 0 unchecked sentences, 539-line page with every learner table rendered by the engine. The first run crashed in the page renderer on the marriage arudha vote, whose derivation is a dict of padas, not a list of rows — the first area where arudha voted (Rahu in the Upapada, against); the reading JSON had already been written, `jyotish page --from` re-rendered it without a model call, and a test now renders every family's derivation in all 18 areas (three shapes: rows; padas; marana karaka sthana for longevity). Every one of the 23 claims matches its derivation table. Two faults in the scoring were visible only once stated in words — the varga vote ("the Sun in Libra scores positively" for health, with the Sun debilitated in D30; "Jupiter in Aries scores negatively" for career, with Jupiter friendly in D10) and the KP vote ("its sub-lord Jupiter … owns the 8th and 11th" counted for health) — and are revised in Layer 5 above. The marriage section reads as an astrologer would: six families for, the Jaimini family against on Rahu in the Upapada with no benefic, a delay flag from Mars on the 7th and its lord, and the disclaimer that it describes the relationship from this chart only.
- Sixth reading, under varga v2 and KP v2, kept in the repo as `examples/reference_reading.{json,md}`: career (asked), marriage and longevity (the new top three), three attempts, 21 claims, 0 unchecked. Every claim audited against its derivation table and holding: the career varga sentence now reads the D10 as it is (Mars exalted in Capricorn best, Saturn own, the Sun, Venus and Jupiter friendly, the Moon and Mercury neutral); the marriage KP chain is stated through the star lord (the sub-lord Mercury in Dhanishta, so Mars — in and ruling the 7th — signifies 7 and decides for, while Mercury's own level is mixed); the longevity varga names the Moon vargottama in D9 as the highest score and Jupiter in Virgo in D30 as the one negative. Career has no KP claim and no school conflict, since the vote abstains; its tier is moderate at 0.70, stable in every sample. One gap for the product, not the engine: the question asked when, and the summary did not say — the model may not write about timing, so the engine will write that line itself (Phase 4, item 2).

The first engineering milestone is making the code print exactly this section. As of 2026-10-21 it does: \`tests/test\_reference\_chart.py\` in the repo encodes every value above and passes, and \`jyotish recover\` finds the instant behind the printed positions (2001-03-12 04:40 UTC), at which the engine matches the app within 0.4 arc-seconds on all seven planets; the app uses the mean node.

## Audit log

What each review pass changed, newest first.

| Date | Pass | Change |
| --- | --- | --- |
| 2026-10-21 | 5 — first complete reading, read as an astrologer | Layer 5: varga term revised from D1–varga agreement to the varga's own signed dignity, with agreement as a consistency weight; KP vote revised to KP practice (matter and denial houses per cusp from the readers, four-fold significations through the star lord, node substitution, abstention when undecided); the dusthana-strength reading of the house family recorded as open. Layer 7: checker runs on every claim of every attempt at a higher effort, checks the summary, writer told each claim stands alone; one finding per rule across bases with the Sudarshana mark; jyotish read and jyotish page; chart header makes every page reproducible. Five readings of the reference chart recorded in the worked example, each audited claim by claim. |
| 2026-10-21 | 4 — engine audit, Layers 5 and 7 | Timing join v2.1: K.N. Rao double-transit targets after v2's transit term saturated at 1.0 across the reference decade; truncation mark; strongest piece per window; the avoid window and q components in the answer. Prompt contract: family votes as narratable findings with \[vote:…\] tags; claim confidence = scale × confidence\_base; the implemented validator and its trade-filter correction; what is not yet built (retrieval corpus, query translation, learner depth). Polarity v3 results recorded. First narrated reading audited tag by tag against the engine. |
| 2026-10-21 | 3 — independent reviewer + arithmetic check | Worked example corrected (A10 = Taurus under the Jaimini exception, Rahu in Pushkara navamsa, Mars and Saturn in Marana Karaka Sthana, Saturn Mrita and Jupiter Vriddha avasthas, Moon compound enemy, Mangal dosha fire, Parivartana classed both ways, special taras, KP sub-sub lord, Mars balance 2y 9m); Layer 1b split into a pre-scoring sampler and a post-scoring rectifier to break the 1b–5–6 cycle; stability reported as three numbers and removed from the score; Layer 6 rewritten (sequestered split, permutation null, nested models, survival timing, abstention accounting, power, calibration map, outcomes-first capture, rectified charts excluded); Placidus cusps, rashi-aspect edges, synastry module, pairing document, tagged timeline rows, TimingQuery, rule editions and five statuses, per-fire basis as the only Sudarshana mechanism; schemas unified with the example; licensing corrected (no LGPL fallback, ADB non-commercial, GPL references kept out of the product); phase table added |
| 2026-10-21 | 2 — structural re-read | Eight-layer diagram; all 19 areas tabulated with Bhavat Bhavam; formula carries Navatara and dispositor terms; both JSON schemas rebuilt; Stri Jataka, MKS, D30/D60 deities, Tithi Pravesha, scope exclusions, compute budget, cohort-aware splits |
| 2026-10-21 | 1 — knowledge audit | Dispositor chains (three), Navatara, full nakshatra layer, rectification and uncertainty, Sudarshana, bhava chalit, sensitive degrees, panchanga lords, Argala, school field, dasha year length, nodal transits, synastry area, covariate baseline, decoy test |
| 2026-10-21 | 0 — first draft | Seven-layer spec, worked example on the reference chart |
