<!-- Exported from the living spec at https://claude.ai/artifact/2og4z1HiFMu5N3RLX3BVci on 2026-10-21 (doc rev 58). The doc is the source of truth; edit there and re-export. The two diagrams (architecture, roadmap) do not export; the phase table in Build phases carries the roadmap. -->

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
  - {text: BPHS, edition: Santhanam 1984, chapter: 75, verse: 2}
  - {text: Phaladeepika, edition: Sastri 1937, chapter: 6, verse: 1}
status: classical_unconfirmed   # classical_unconfirmed | classical_rejected | experimental | not_testable_yet | data_confirmed
when:
  planet: Mars
  dignity_in: [own, exalted]
  house_in: [1, 4, 7, 10]
  basis: [lagna, moon, sun]  # evaluated once per basis; each fire records which
modifiers:
  - if: shadbala_ratio < 1.0      # weak Mars
    scale: 0.5
  - if: aspected_by: [Saturn]
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

The engine evaluates every rule against the graph and emits a list of `fired_rules`, each with the rule id, the matched nodes, the applied scale and the theme contributions. The learner can see exactly why a theme scored what it did.

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

where B\_h is Bhava Bala (normalised), D\_p is dignity on a −2…+2 scale, β is Shadbala against its required minimum, θ\_r is each fired rule's theme contribution scaled by its modifiers and b\_r is the basis weight of that fire (1 from the Lagna, 2/3 from the Moon, 1/3 from the Sun), V\_area is the varga-confirmation term (agreement between D1 and the area's varga, vargottama as a bonus), T\_p is the Navatara class of each lord and karaka on a −1…+1 scale, Δ\_p is the dignity of each lord's final dispositor (so a lord inherits support or weakness from its chain), and P\_area is the small panchanga-lord term (the birth tithi, vara, karana and yoga lords' strength where they touch the area). Stability is *not* a factor in S: it is reported beside the score as three numbers (Layer 1b) and gates narration, so an unknown birth time produces "cannot be assessed", never a low score. Weights w, c, λ, ν, κ, π start from classical proportion (lord : occupant : karaka ≈ 3 : 2 : 2; ν, κ, π small) and are the classical weight set; Layer 6 produces a separate, named learned set, and the classical set stays the default until a learned set passes the sequestered test and is promoted in a numbered release.

The linear sum is the interpretable default. The tree model in Layer 6 is allowed to learn interactions (cancellations, conditional yogas); wherever the two disagree on an area by more than 0.15, the reading says so and shows both.

**Confluence and confidence**

- Count the signal *families* that agree on the direction of a theme: D1 house, D1 lord, karaka, varga, Jaimini arudha, KP sub-lord, panchanga lords, dasha activation, transit activation. They are not independent — all are functions of the same ten longitudes — so each family's vote is weighted by 1 − ρ, where ρ is its mean correlation with the other families measured on 10,000 random charts; confidence = weighted agreement / weighted applicable, with a penalty for strong contradiction (e.g. exalted 7th lord but afflicted UL).
- Output tiers: weighted agreement above 0.7 → "strong"; 0.4–0.7 → "moderate"; below, or mixed → "weak / mixed", and the narration must say so in words. Tier boundaries are re-mapped by the calibration map in Layer 6 when one exists; until then they are classical convention, and the product says so.

**Dominance model ("what is dominant")**

- Rank planets by composite strength: Shadbala ratio × Vimsopaka × number of rules fired × dasha proximity. The top planet is the chart's *driver*; its house and lordships set the chart's primary theme.
- Rank life areas by S\_area × confidence. The top three are presented first; areas under a threshold are reported as "not emphasised" rather than guessed at.
- Polarity: each theme carries signed contributions, so "wealth: strong, but with volatility (Rahu in 2nd aspect)" is a native output, not a hedge added by the LLM.

The driver-planet formula is a hypothesis, not a classical rule. "Rules fired" is normalised by the rules applicable to that planet, so Mars and Saturn do not win by having a larger rule library; dasha proximity is dropped from the static driver and the current period lord is reported separately with an `as_of` date. Where the sign-dispositor graph collapses into one loop or one final dispositor, that planet is a driver candidate regardless of the formula, and the alternates are shown side by side. The formula is validated in Layer 6 like any rule.

**Timing join** A question with a "when" takes the static S\_area, multiplies by the dasha quality score of each window from Layer 4, adds the transit activation of the area's houses, and returns the top windows with their joint score. This is what makes "marriage likely 2028–2029" a computed statement with a visible derivation.

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
2. Every sentence that makes a claim ends with a citation tag `[rule:yoga.ruchaka]` or `[text:BPHS 75.2]`. Output is validated: a sentence with a claim-verb and no tag is rejected and regenerated.
3. Confidence words are taken from the JSON tier field verbatim; the model may not upgrade "moderate" to "certain".
4. Claims are ordered by stability × confidence; findings with stability under 0.5 are left out of the default narration and listed under "depends on exact birth time".
5. Where rule families from different schools disagree on an area, the narration names both schools and the disagreement; it never averages them into one claim.
6. Forbidden content is enforced in code: no death timing, no medical diagnosis, no financial trade advice, no claims about a third party's own life — the mother, partner, children, father and synastry areas report the relationship as seen from this chart, never the other person's fate; these areas return the classical indications with a fixed disclaimer block.
7. Learner mode appends, per claim, the rule block that fired, the feature values that satisfied it, and the dispositor and Navatara context of the planets involved.

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

One JSON document per chart, versioned by engine release, so a reading can always be reproduced. Top-level keys map one-to-one to the layers. Values below are the reference chart's where the worked example fixes them (karakas, arudhas, dispositors, KP cusp, Ashtakavarga) and illustrative elsewhere (Shadbala, scores).

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
    "strength": {"shadbala": {"Saturn": {"sthana": 0, "dig": 0, "kala": 0, "chesta": 0, "naisargika": 0, "drik": 0,
                                           "total": 412.3, "required": 300, "ratio": 1.37}},
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
                  "varga_stability": {"D9": 0.99, "D10": 0.67, "D60": 0.5}}
}
```

The `varga_stability` values above are what a lagna at Taurus 6°09'50" actually gives under a ±2-minute uniform window: the D9 boundary is 30' ahead (about 2 minutes of clock), the D10 boundary 9'50" behind (about 40 seconds), and D60 cells are 30' wide, so D9 is near-certain, D10 flips in a third of samples and D60 in half. They are computed from the posterior, never typed.

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

**What we do first, this week**

1. Set up the repo, `pyswisseph`, and the chart-object `pydantic` model, including the `time_posterior` and `uncertainty` blocks from the start.
2. Compute the reference chart (Taurus lagna, section below) and diff every body and every varga against the app screenshots and Jagannatha Hora.
3. Write the lordship table for all 12 lagnas, the five-fold dignity function, the three dispositor chains and the Navatara function, with tests; the reference chart must print its Venus–Jupiter loop, its Mars anchor and its tara table exactly as below.
4. Draft the first 10 rules in YAML (the Pancha Mahapurusha five, Budhaditya, Gaja Kesari, Neecha Bhanga, kendra-trikona Raja yoga, Parivartana) and run them on the reference chart across a ±10-minute birth-time sweep to produce the first stability numbers.

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

**Layer 3 expected rule fires**

- `yoga.ruchaka` (Mars own sign in H7 kendra, basis lagna) — scale 0.6 after the Marana Karaka Sthana modifier.
- `yoga.parivartana` (Venus–Jupiter) — see below.
- `yoga.budhaditya` (Sun + Mercury, H10) — scale 0.9: Mercury at 0°22' is in Bala avastha and carries a boundary flag; not combust (27° apart).
- `lord.yogakaraka_in_lagna` (Saturn) — scale 0.6 × 0.8: Marana Karaka Sthana and Mrita avastha.
- `lord.lagna_exalted` (Venus) — full scale.
- `affliction.mangal_dosha` — fires from the Lagna (Mars in H7) and from the Moon (Mars 2nd from Libra), not from Venus (9th from Pisces); cancellation modifiers apply for Mars in own sign and for Jupiter's aspect, so the net scale is small and the reading names the dosha and its cancellations together.
- `yoga.gaja_kesari` — does **not** fire: Jupiter is 8th from the Moon.
- `affliction.kala_sarpa` — does **not** fire: planets on both sides of the Rahu–Ketu axis.

Missed in the first draft and caught by the dispositor pass: `yoga.parivartana` fires between Venus (in Pisces, Jupiter's sign) and Jupiter (in Taurus, Venus's sign). Classified both ways, because the texts define it both ways: by the houses exchanged it is the 1st and the 11th → **Maha Parivartana**; by the lordships of the exchanging planets (Venus 6th, Jupiter 8th) it is **Dainya** under Uttara Kalamrita. The fire carries `class_by_houses: maha`, `class_by_lordship: dainya`, and the narration states both. This is exactly the kind of signal a human reader skips and a graph engine cannot.

**Layer 4 expected timing**

- Vimshottari starts in Mars dasha (Moon in Chitra). Chitra runs Virgo 23°20' to Libra 6°40'; the Moon has covered 8°05'19" of its 13°20', so 39.3% remains → Mars balance at birth ≈ 2 years 9 months (365.25-day year).
- Order: Mars 7y → Rahu 18 → Jupiter 16 → Saturn 19 → Mercury 17 → Ketu 7 → Venus 20 → Sun 6 → Moon 10.
- Navatara of the dasha lords: Mars Pratyak, Rahu Sampat, Jupiter Ati-mitra, Saturn Mitra, Mercury Janma, Ketu Vadha, Venus Pratyak (2nd cycle), Sun Vipat (2nd cycle), Moon Janma.

**Layer 5 expected ranking (classical weights, before calibration)**

- Driver planet: Saturn leads on lordship (yogakaraka, H1, aspects H10, own sign in D9) but carries Marana Karaka Sthana and Mrita avastha, so the reading presents it as "strong role, weakened condition"; Venus (exalted lagna lord, AmK) and Mars (own-sign kendra, the only self-disposited planet, final nakshatra dispositor with Mercury) are the alternates, and all three are shown with the dispositor graph that produced them.
- Top areas: career (H10 with Sun and Mercury, 10th lord Saturn in H1, Budhaditya, AmK Venus exalted, A10 on the lagna itself) → strong, with a sensitivity note for Mercury's boundary flag; wealth (lagna lord exalted in H11, the 1st–11th Parivartana, 2nd lord with the Sun in H10) → strong; marriage (Ruchaka in H7 but Mars in MKS, 7th lord in own sign, Saturn's aspect on H7, Mars's on H1, Rahu in the Upapada and in a Pushkara navamsa, DK Mercury in Bala avastha, Mangal dosha with cancellations) → moderate with a "delay or intensity" polarity flag.

The first engineering milestone is making the code print exactly this section. As of 2026-10-21 it does: \`tests/test\_reference\_chart.py\` in the repo encodes every value above and passes, and \`jyotish recover\` finds the instant behind the printed positions (2001-03-12 04:40 UTC), at which the engine matches the app within 0.4 arc-seconds on all seven planets; the app uses the mean node.

## Audit log

What each review pass changed, newest first.

| Date | Pass | Change |
| --- | --- | --- |
| 2026-10-21 | 3 — independent reviewer + arithmetic check | Worked example corrected (A10 = Taurus under the Jaimini exception, Rahu in Pushkara navamsa, Mars and Saturn in Marana Karaka Sthana, Saturn Mrita and Jupiter Vriddha avasthas, Moon compound enemy, Mangal dosha fire, Parivartana classed both ways, special taras, KP sub-sub lord, Mars balance 2y 9m); Layer 1b split into a pre-scoring sampler and a post-scoring rectifier to break the 1b–5–6 cycle; stability reported as three numbers and removed from the score; Layer 6 rewritten (sequestered split, permutation null, nested models, survival timing, abstention accounting, power, calibration map, outcomes-first capture, rectified charts excluded); Placidus cusps, rashi-aspect edges, synastry module, pairing document, tagged timeline rows, TimingQuery, rule editions and five statuses, per-fire basis as the only Sudarshana mechanism; schemas unified with the example; licensing corrected (no LGPL fallback, ADB non-commercial, GPL references kept out of the product); phase table added |
| 2026-10-21 | 2 — structural re-read | Eight-layer diagram; all 19 areas tabulated with Bhavat Bhavam; formula carries Navatara and dispositor terms; both JSON schemas rebuilt; Stri Jataka, MKS, D30/D60 deities, Tithi Pravesha, scope exclusions, compute budget, cohort-aware splits |
| 2026-10-21 | 1 — knowledge audit | Dispositor chains (three), Navatara, full nakshatra layer, rectification and uncertainty, Sudarshana, bhava chalit, sensitive degrees, panchanga lords, Argala, school field, dasha year length, nodal transits, synastry area, covariate baseline, decoy test |
| 2026-10-21 | 0 — first draft | Seven-layer spec, worked example on the reference chart |
