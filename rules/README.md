# Rule library

One YAML file per rule, named `<id>.yaml`, loaded and validated by `jyotish.rules`
(SPEC Layer 3) against [`rule.schema.json`](rule.schema.json). Rules are data: an
astrologer can add one without touching the engine. A file that fails the schema stops
the load with the file name and the field at fault. Every rule carries:

| key | meaning |
| --- | --- |
| `id` | `family.name`, stable forever (narration and validation hang on it) |
| `family` | yoga group, e.g. `pancha_mahapurusha`, `raja`, `affliction`, `lunar` |
| `school` | `parashari`, `jaimini`, `kp`, `nadi`, `tajaka`, `regional:<name>` |
| `source` | list of `{text, edition, chapter, verse}`, optional `checked` and `note`; `checked: false` means the chapter/verse has not yet been verified against that edition. Sanskrit originals are public domain, translations are cited by edition and never quoted |
| `status` | `classical_unconfirmed` (cited, default scoring) · `classical_rejected` (powered null in validation) · `not_testable_yet` · `experimental` (uncited, excluded from default) · `data_confirmed` |
| `when` | the subject and its conditions; `basis` lists which of lagna / moon / sun it is evaluated from, and each fire records its basis |
| `modifiers` | `{if, scale}` (and `of` for pair rules) applied in file order |
| `report` | named extras attached to each fire: `parivartana_class`, `neecha_bhanga`, `lordships` |
| `themes` | signed contributions per theme, multiplied by the fire's scale |
| `outcomes` | the measured outcomes (SPEC Layer 6 mapping table) this rule is tested against |
| `confidence_base`, `stability_min`, `narration_key` | as in SPEC |

## Writing `when`

The subject is one planet (`planet: Mars`), any of a list (`planet_in: [...]`), or a pair:

```yaml
when:
  pair:
    a: {lord_of: [1, 4, 7, 10]}       # each side is itself a condition set
    b: {lord_of: [1, 5, 9]}
    related_by: [conjunction, mutual_aspect, exchange]
  basis: [lagna]
```

Conditions are feature keys. A list means "any of": `house_in: [1, 4, 7, 10]`,
`aspected_by: [Saturn]`, `lord_of: [6, 8, 12]`. A boolean or scalar means "equals".
`all`, `any` and `not` combine condition sets. The features are:

| feature | value | depends on basis |
| --- | --- | --- |
| `dignity`, `dignity_compound` | exalted, moolatrikona, own, friend, neutral, enemy, debilitated | no |
| `house` | 1-12 from the basis | yes |
| `sign` | 0-11 (Aries = 0) | no |
| `lord_of` | houses the planet rules from the basis | yes |
| `avastha` | Baladi: bala, kumara, yuva, vriddha, mrita | no |
| `tara_from_moon` | janma, sampat, vipat, kshema, pratyak, sadhaka, vadha, mitra, atimitra | no |
| `combust`, `retro`, `marana_karaka_sthana`, `vargottama`, `boundary` | true / false | no |
| `aspected_by`, `conjoined_with` | planets (whole-sign drishti; nodes do not aspect) | no |
| `dispositor_house` | house of the lord of the planet's sign | yes |
| `exaltation_lord_house` | house of the lord of the planet's exaltation sign | yes |
| `exalted_here_house` | house of the planet exalted in this planet's sign | yes |
| `aspected_by_dispositor` | true / false | no |
| `conjoined_with_benefic`, `aspected_by_benefic` | true / false; benefics as Shadbala's Drik bala: Jupiter, Venus, waxing Moon, Mercury by `Meta.mercury_nature` | no |
| `shadbala_ratio` | Shadbala total / required (in string conditions only) | no |

A rule that uses no basis-dependent feature must name a single basis, or it would fire
the same thing three times.

## Writing `modifiers`

`if` is a condition set as above, or a short string: a bare feature
(`marana_karaka_sthana`), a comparison (`shadbala_ratio < 1.0`, `dignity == debilitated`)
or a membership test (`tara_from_moon in [vipat, pratyak, vadha]`). In a pair rule, `of`
names the side the condition is about (`a`, `b`, a planet name) or `pair` for the pair's
own features: `class_by_houses`, `class_by_lordship` (Parivartana classes), `relations`.

Conditions are three-valued. If the chart lacks a feature (Shadbala needs the birth
moment), a `when` that needs it does not fire, and a modifier that needs it is not
applied and is listed in the fire's `unknown`, so the narration can say what was not
assessed.

## Files

The first ten rules: the five Pancha Mahapurusha (`yoga.ruchaka`, `yoga.bhadra`,
`yoga.hamsa`, `yoga.malavya`, `yoga.sasa`), `yoga.budhaditya`, `yoga.gaja_kesari`,
`yoga.neecha_bhanga`, `yoga.kendra_trikona_raja` and `yoga.parivartana`, plus
`yoga.gaja_kesari_bphs` (BPHS 36.3-4, kept apart from Phaladeepika's Kesari). On the
reference chart, Ruchaka fires from the lagna and from the Sun at 0.408 (Saturn's aspect
0.8 × Pratyak tara 0.85 × Marana Karaka Sthana 0.6; Mars's Shadbala ratio is 1.30, so the
weak-Mars modifier does not apply).
