# Rule library

One YAML file per rule, loaded by the evaluator (SPEC Layer 3; evaluator not yet written).
Rules are data: an astrologer can add one without touching the engine. Every rule carries:

| key | meaning |
| --- | --- |
| `id` | `family.name`, stable forever (narration and validation hang on it) |
| `family` | yoga group, e.g. `pancha_mahapurusha`, `raja`, `affliction`, `lunar` |
| `school` | `parashari`, `jaimini`, `kp`, `nadi`, `tajaka`, `regional:<name>` |
| `source` | list of `{text, edition, chapter, verse}`; Sanskrit originals are public domain, translations are cited by edition and never quoted |
| `status` | `classical_unconfirmed` (cited, default scoring) · `classical_rejected` (powered null in validation) · `not_testable_yet` · `experimental` (uncited, excluded from default) · `data_confirmed` |
| `when` | the condition over chart features; `basis` lists which of lagna / moon / sun it is evaluated from, and each fire records its basis |
| `modifiers` | `{if, scale}` pairs applied in order |
| `themes` | signed contributions per theme |
| `outcomes` | the measured outcomes (SPEC Layer 6 mapping table) this rule is tested against |
| `confidence_base`, `stability_min`, `narration_key` | as in SPEC |

`yoga.ruchaka.yaml` is the worked example from SPEC.md and the first rule the evaluator
must fire on the reference chart at scale 0.408 (Saturn's aspect 0.8 × Pratyak tara 0.85 ×
Marana Karaka Sthana 0.6; the Shadbala cut does not apply, Mars's ratio being 1.30).
