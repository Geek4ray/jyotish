# Checker benchmark: Qwen/Qwen3.6-35B-A3B

Run 2026-10-25 at commit `749b891` by `scripts/checker_bench.py` on `tests/fixtures/checker_bench.jsonl` (147 rows: 61 accept, 86 reject). The positive class is reject.

## The code validator alone

| category | n | caught / false rejects | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- |
| overall | 147 | 22 of 86 | 1.000 | 0.256 | 0.407 |
| accepted | 61 | 0 false rejects | 1.000 | 1.000 | 1.000 |
| cites_too_narrowly | 2 | 0 of 2 | 1.000 | 0.000 | 0.000 |
| contradicts_its_fact | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |
| dasha_lord_changed | 6 | 0 of 6 | 1.000 | 0.000 | 0.000 |
| dignity_changed | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| family_not_cited | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| forbidden_word | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| house_changed | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| judgement_premise | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| negated | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| nth_sign | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| planet_swapped | 9 | 1 of 9 | 1.000 | 0.111 | 0.200 |
| ranking_not_cited | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| refers_to_another_claim | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| sign_changed | 5 | 0 of 5 | 1.000 | 0.000 | 0.000 |
| synthesis_does_not_follow | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |
| tag_not_offered | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| tier_word | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| unstated_claim | 2 | 0 of 2 | 1.000 | 0.000 | 0.000 |
| unsupported_clause | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| untagged | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| untagged_unsupported | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |
| wrong_dignity | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |

The validator reads tags and words, not meaning: it is meant to catch the tag and wording categories (family_not_cited, forbidden_word, nth_sign, ranking_not_cited, refers_to_another_claim, tag_not_offered, tier_word, untagged) and to leave the semantic ones to the checker.

Misses and false rejects (validator alone):

- `planet_swapped-1` (planet_swapped, missed): Jupiter and Mercury together in the 10th, a career house, form Budhaditya yoga and Kendra-Trikona Raja yoga, which the tradition links with intellect, communication, authority and reputation [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja].  
  reason: (none given)
- `planet_swapped-2` (planet_swapped, missed): Mars forms Ruchaka yoga, tied to courage and leadership, counted from Jupiter in the 10th, a career house, though in a reduced form [rule:yoga.ruchaka].  
  reason: (none given)
- `planet_swapped-3` (planet_swapped, missed): The house test favours career: the 10th, a career house, in Aquarius is the weakest house by strength, but the 2nd, the 6th and the 11th, career houses, are strong, as are the 6th and 11th from the Moon and the 2nd and 11th from Jupiter, career houses [vote:career.house].  
  reason: (none given)
- `planet_swapped-4` (planet_swapped, missed): The panchanga test favours career: Mars, ruler of the birth tithi and nakshatra, rules the 7th, the 10th's Bhavat Bhavam, and the 10th from Jupiter, a career house, and the Moon, ruler of the vara, rules the 10th from the Moon, a career house, both above their required strength [vote:career.panchanga].  
  reason: (none given)
- `planet_swapped-5` (planet_swapped, missed): The significator test favours career: Jupiter and Mercury, both above their required strength, sit in the 10th, a career house, and Venus is exalted in the 11th, a career house, while Saturn in the 1st falls short of its required strength [vote:career.karaka].  
  reason: (none given)
- `planet_swapped-6` (planet_swapped, missed): The lord test favours career: Saturn, lord of the 10th, sits in a friend's sign in the 1st but below its required strength, while Venus, lord of the 6th, is exalted in the 11th, Mercury, lord of the 2nd, is above its required strength in the 10th, and Jupiter, lord of the 7th, the 10th's Bhavat Bhavam, is in its own sign [vote:career.lord].  
  reason: (none given)
- `planet_swapped-7` (planet_swapped, missed): Jupiter and Mercury sit together in the 10th, a career house, forming Budhaditya yoga, the combination of Mercury and the Sun in the same sign, and Kendra-Trikona Raja yoga, a combination joining the lord of an angular house with the lord of a trine house [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja].  
  reason: (none given)
- `planet_swapped-9` (planet_swapped, missed): Mars adds Ruchaka yoga, the great-person combination of Mars, counted from the ascendant and from Jupiter [rule:yoga.ruchaka].  
  reason: (none given)
- `house_changed-1` (house_changed, missed): The Sun and Mercury together in the 1st, a career house, form Budhaditya yoga and Kendra-Trikona Raja yoga, which the tradition links with intellect, communication, authority and reputation [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja].  
  reason: (none given)
- `house_changed-2` (house_changed, missed): Mars forms Ruchaka yoga, tied to courage and leadership, counted from the Sun in the 1st, a career house, though in a reduced form [rule:yoga.ruchaka].  
  reason: (none given)
- `house_changed-3` (house_changed, missed): Most of the career tests lean in favour, while the 1st house itself scores lowest by house strength [vote:career.house] [vote:career.lord] [vote:career.karaka] [vote:career.varga] [vote:career.panchanga].  
  reason: (none given)
- `house_changed-4` (house_changed, missed): The Sun, lord of the 4th, joins Mercury, lord of the 2nd and the 5th, in the 1st, a career house, forming Kendra-Trikona Raja yoga [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12].  
  reason: (none given)
- `house_changed-5` (house_changed, missed): The Sun and Mercury sit together in the 1st, a career house, forming Budhaditya yoga, with its strength trimmed because Mercury is in a weak degree state [rule:yoga.budhaditya] [text:Phaladeepika/Sastri-1937/18/1].  
  reason: (none given)
- `house_changed-6` (house_changed, missed): Mercury, lord of the 2nd, a career house, sits in the 1st, a career house [rule:place.l2_h10].  
  reason: (none given)
- `house_changed-7` (house_changed, missed): Mercury, lord of the 5th, sits in the 1st, a career house [rule:place.l5_h10].  
  reason: (none given)
- `house_changed-8` (house_changed, missed): Mars forms Ruchaka yoga from the lagna and from the Sun, sitting in the 7th, the 1st's Bhavat Bhavam, and in the 10th from the Sun, a career house, though it is reduced by Saturn's aspect, an adverse tara from the Moon and Mars standing in a marana karaka sthana [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].  
  reason: (none given)
- `house_changed-9` (house_changed, missed): The Sun sits in the 1st, a career house [rule:place.sun_h10].  
  reason: (none given)
- `sign_changed-1` (sign_changed, missed): The house test favours career: the 10th, a career house, in Gemini is the weakest house by strength, but the 2nd, the 6th and the 11th, career houses, are strong, as are the 6th and 11th from the Moon and the 2nd and 11th from the Sun, career houses [vote:career.house].  
  reason: (none given)
- `sign_changed-2` (sign_changed, missed): The dasamsa, the career chart, favours career: Mars and Saturn both fall in Taurus with good dignity, the Sun, Jupiter and Venus are mildly well placed, and the Moon and Mercury are neutral [vote:career.varga].  
  reason: (none given)
- `sign_changed-3` (sign_changed, missed): The Jaimini image-point test goes against marriage: the Upapada falls in Libra in the 2nd, a marriage house, holding Rahu and no benefic, and the sign after it and the A7 are empty of benefics [vote:marriage.arudha].  
  reason: (none given)
- `sign_changed-4` (sign_changed, missed): The navamsa favours marriage: Saturn in Capricorn scores best, Mars, Mercury, Jupiter and Venus are mildly well placed, and the Sun in Libra is neutral [vote:marriage.varga].  
  reason: (none given)
- `sign_changed-5` (sign_changed, missed): The divisional-chart test is favourable: the Moon is vargottama in Libra and Saturn falls in Capricorn in the navamsa, while Jupiter in Capricorn in the trimsamsa is poorly placed [vote:longevity.varga].  
  reason: (none given)
- `dignity_changed-1` (dignity_changed, missed): The significator test favours career: the Sun and Mercury, both above their required strength, sit in the 10th, a career house, and Venus is debilitated in the 11th, a career house, while Saturn in the 1st falls short of its required strength [vote:career.karaka].  
  reason: (none given)
- `dignity_changed-2` (dignity_changed, missed): The lord test favours career: Saturn, lord of the 10th, sits in a friend's sign in the 1st but below its required strength, while Venus, lord of the 6th, is debilitated in the 11th, Mercury, lord of the 2nd, is above its required strength in the 10th, and Mars, lord of the 7th, the 10th's Bhavat Bhavam, is in its own sign [vote:career.lord].  
  reason: (none given)
- `dignity_changed-3` (dignity_changed, missed): The significator test favours marriage: Venus is debilitated in the 11th, a marriage house, Jupiter sits in an enemy's sign in the 1st yet above its required strength, and Mercury is neutral in the 10th [vote:marriage.karaka].  
  reason: (none given)
- `dignity_changed-4` (dignity_changed, missed): The lord test favours marriage: Mars, lord of the 7th, a marriage house, sits in its own sign in the 7th above its required strength, and Venus, lord of the 1st, the 7th's Bhavat Bhavam, is debilitated in the 11th [vote:marriage.lord].  
  reason: (none given)
- `dignity_changed-5` (dignity_changed, missed): The navamsa favours marriage: Saturn in Capricorn scores best, Mars, Mercury, Jupiter and Venus are mildly well placed, and the Sun in Gemini is exalted [vote:marriage.varga].  
  reason: (none given)
- `dignity_changed-6` (dignity_changed, missed): Mars, lord of the 7th and lord of the 12th, sits in the 7th, a marriage house, in its own sign, while Venus, ruling the 1st, sits debilitated, in the sign where the texts hold a planet at its peak, in the 11th [rule:place.l7_h7] [rule:place.l12_h7] [rule:place.venus_h11] [vote:marriage.lord].  
  reason: (none given)
- `dignity_changed-7` (dignity_changed, missed): The significator test is favourable: Saturn and Jupiter sit in the 1st, a longevity house, Saturn in a friend's sign but below its required strength, and Venus is debilitated in the 11th [vote:longevity.karaka].  
  reason: (none given)
- `dignity_changed-8` (dignity_changed, missed): The lord test is favourable: Venus, lord of the 1st, is debilitated in the 11th, Jupiter, lord of the 8th, sits in an enemy's sign in the 1st above its required strength, and the Moon, lord of the 3rd, is neutral in the 6th [vote:longevity.lord].  
  reason: (none given)
- `dignity_changed-9` (dignity_changed, missed): Ketu, the Moon's south node, sits in the 8th, while Saturn and Jupiter share the 1st and Venus, ruler of the 1st, sits debilitated, in the sign where the texts hold a planet at its peak, in the 11th [rule:place.ketu_h8] [vote:longevity.karaka] [vote:longevity.lord].  
  reason: (none given)
- `negated-1` (negated, missed): Mars does not form Ruchaka yoga, tied to courage and leadership, counted from the Sun in the 10th, a career house, though in a reduced form [rule:yoga.ruchaka].  
  reason: (none given)
- `negated-2` (negated, missed): The Sun and Mercury do not sit together in the 10th, a career house, forming Budhaditya yoga, with its strength trimmed because Mercury is in a weak degree state [rule:yoga.budhaditya] [text:Phaladeepika/Sastri-1937/18/1].  
  reason: (none given)
- `negated-3` (negated, missed): Mercury, lord of the 2nd, a career house, does not sit in the 10th, a career house [rule:place.l2_h10].  
  reason: (none given)
- `negated-4` (negated, missed): Mercury, lord of the 5th, does not sit in the 10th, a career house [rule:place.l5_h10].  
  reason: (none given)
- `negated-5` (negated, missed): Mars does not form Ruchaka yoga from the lagna and from the Sun, sitting in the 7th, the 10th's Bhavat Bhavam, and in the 10th from the Sun, a career house, though it is reduced by Saturn's aspect, an adverse tara from the Moon and Mars standing in a marana karaka sthana [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].  
  reason: (none given)
- `negated-6` (negated, missed): The Sun does not sit in the 10th, a career house [rule:place.sun_h10].  
  reason: (none given)
- `negated-7` (negated, missed): The house test does not favour career: the 10th, a career house, in Aquarius is the weakest house by strength, but the 2nd, the 6th and the 11th, career houses, are strong, as are the 6th and 11th from the Moon and the 2nd and 11th from the Sun, career houses [vote:career.house].  
  reason: (none given)
- `negated-8` (negated, missed): The panchanga test does not favour career: Mars, ruler of the birth tithi and nakshatra, rules the 7th, the 10th's Bhavat Bhavam, and the 10th from the Sun, a career house, and the Moon, ruler of the vara, rules the 10th from the Moon, a career house, both above their required strength [vote:career.panchanga].  
  reason: (none given)
- `negated-9` (negated, missed): The significator test does not favour career: the Sun and Mercury, both above their required strength, sit in the 10th, a career house, and Venus is exalted in the 11th, a career house, while Saturn in the 1st falls short of its required strength [vote:career.karaka].  
  reason: (none given)
- `unsupported_clause-1` (unsupported_clause, missed): The Sun and Mercury together in the 10th, a career house, form Budhaditya yoga and Kendra-Trikona Raja yoga, which the tradition links with intellect, communication, authority and reputation, and the 12th house adds its support [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja].  
  reason: (none given)
- `unsupported_clause-2` (unsupported_clause, missed): Mars forms Ruchaka yoga, tied to courage and leadership, counted from the Sun in the 10th, a career house, though in a reduced form, and the 12th house adds its support [rule:yoga.ruchaka].  
  reason: (none given)
- `unsupported_clause-3` (unsupported_clause, missed): Most of the career tests lean in favour, while the 10th house itself scores lowest by house strength, and the 12th house adds its support [vote:career.house] [vote:career.lord] [vote:career.karaka] [vote:career.varga] [vote:career.panchanga].  
  reason: (none given)
- `unsupported_clause-4` (unsupported_clause, missed): The Sun, lord of the 4th, joins Mercury, lord of the 2nd and the 5th, in the 10th, a career house, forming Kendra-Trikona Raja yoga, and Jupiter's aspect on the 10th strengthens it [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12].  
  reason: (none given)
- `unsupported_clause-5` (unsupported_clause, missed): The Sun and Mercury sit together in the 10th, a career house, forming Budhaditya yoga, with its strength trimmed because Mercury is in a weak degree state, and Jupiter's aspect on the 10th strengthens it [rule:yoga.budhaditya] [text:Phaladeepika/Sastri-1937/18/1].  
  reason: (none given)
- `unsupported_clause-6` (unsupported_clause, missed): Mercury, lord of the 2nd, a career house, sits in the 10th, a career house, and Jupiter's aspect on the 10th strengthens it [rule:place.l2_h10].  
  reason: (none given)
- `unsupported_clause-7` (unsupported_clause, missed): Mercury, lord of the 5th, sits in the 10th, a career house, and Jupiter's aspect on the 10th strengthens it [rule:place.l5_h10].  
  reason: (none given)
- `unsupported_clause-8` (unsupported_clause, missed): Mars forms Ruchaka yoga from the lagna and from the Sun, sitting in the 7th, the 10th's Bhavat Bhavam, and in the 10th from the Sun, a career house, though it is reduced by Saturn's aspect, an adverse tara from the Moon and Mars standing in a marana karaka sthana, and Jupiter's aspect on the 10th strengthens it [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].  
  reason: (none given)
- `unsupported_clause-9` (unsupported_clause, missed): The Sun sits in the 10th, a career house, and Jupiter's aspect on the 10th strengthens it [rule:place.sun_h10].  
  reason: (none given)
- `dasha_lord_changed-1` (dasha_lord_changed, missed): The Sun and Mercury sit together in the 10th, a career house, forming Budhaditya yoga, the combination of Mercury and the Sun in the same sign, and Kendra-Trikona Raja yoga, a combination joining the lord of an angular house with the lord of a trine house, and the current major period of Saturn activates the Sun through its nakshatra [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja] [chain:career.karaka].  
  reason: (none given)
- `dasha_lord_changed-2` (dasha_lord_changed, missed): The Sun and Mercury sit together in the 10th, a career house, forming Budhaditya yoga, the combination of Mercury and the Sun in the same sign, and Kendra-Trikona Raja yoga, a combination joining the lord of an angular house with the lord of a trine house, and the current major period of Venus activates the Sun through its nakshatra [rule:yoga.budhaditya] [rule:yoga.kendra_trikona_raja] [chain:career.karaka].  
  reason: (none given)
- `dasha_lord_changed-3` (dasha_lord_changed, missed): Mars, lord of the 7th and lord of the 12th, sits in the 7th, a marriage house, in its own sign, while Venus, ruling the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th, and the current major period of Ketu activates Mars through its nakshatra [rule:place.l7_h7] [rule:place.l12_h7] [rule:place.venus_h11] [vote:marriage.lord] [chain:marriage.lord].  
  reason: (none given)
- `dasha_lord_changed-4` (dasha_lord_changed, missed): Mars, lord of the 7th and lord of the 12th, sits in the 7th, a marriage house, in its own sign, while Venus, ruling the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th, and the current major period of Jupiter activates Mars through its nakshatra [rule:place.l7_h7] [rule:place.l12_h7] [rule:place.venus_h11] [vote:marriage.lord] [chain:marriage.lord].  
  reason: (none given)
- `dasha_lord_changed-5` (dasha_lord_changed, missed): Ketu, the Moon's south node, sits in the 8th, while Saturn and Jupiter share the 1st and Venus, ruler of the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th, and the current major period of Saturn activates Venus through its nakshatra [rule:place.ketu_h8] [vote:longevity.karaka] [vote:longevity.lord] [chain:longevity.lord].  
  reason: (none given)
- `dasha_lord_changed-6` (dasha_lord_changed, missed): Ketu, the Moon's south node, sits in the 8th, while Saturn and Jupiter share the 1st and Venus, ruler of the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th, and the current major period of Rahu activates Venus through its nakshatra [rule:place.ketu_h8] [vote:longevity.karaka] [vote:longevity.lord] [chain:longevity.lord].  
  reason: (none given)
- `known_bad-4` (wrong_dignity, missed): The varga vote leans narrowly for career in the D10: Saturn, Mars and Venus score well there, while Jupiter and the Sun score poorly and Mercury and the Moon are neutral [vote:career.varga].  
  reason: (none given)
- `b-ranking-career-fixed` (contradicts_its_fact, missed): The strongest support is in the lords, as the lord vote shows: Venus, lord of the 6th, is exalted in the 11th at a Shadbala ratio of 1.33, Mars, lord of the 7th and of the 10th from the Sun, is in its own sign at 1.3, and Mercury, lord of the 2nd, sits in the 10th at 1.19 [vote:career.lord] [fact:areas.career.contributions].  
  reason: (none given)
- `b-arudha` (cites_too_narrowly, missed): The arudha vote is 0, so the A10 gives no verdict on how the career appears [fact:areas.career.votes.arudha.vote].  
  reason: (none given)
- `b-synastry` (cites_too_narrowly, missed): This chart says nothing about a partner's own chart or life, and the engine's synastry area needs two charts [fact:areas.synastry.tier].  
  reason: (none given)
- `b-hyphen` (unstated_claim, missed): A second tension sits in Mars itself: its place in the 7th is a marana karaka sthana, for which the lord-of-the-7th-in-the-7th and lord-of-the-12th-in-the-7th placements are scaled to 0.6, while its Shadbala ratio stays at 1.3, and the facts leave the net quality of that placement open [rule:place.l7_h7] [rule:place.l12_h7] [fact:sensitive.Mars.marana_karaka_sthana] [fact:shadbala.planets.Mars.ratio].  
  reason: (none given)
- `b-votes-fact` (unstated_claim, missed): The votes for this area weigh houses, lords, karakas, vargas, the arudha and the panchanga, and this reading draws no medical statement from them [fact:areas.longevity.votes].  
  reason: (none given)
- `kind-judgement-premise` (judgement_premise, missed): I give the lord family more weight than the arudha vote, since the arudha vote is against career [fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].  
  reason: (none given)
- `kind-synthesis-does-not-follow` (synthesis_does_not_follow, missed): Mars is in its own sign in the 7th house from the lagna, so Mars rules the 10th house from the lagna [fact:planets.Mars.dignity] [fact:houses.lagna.7].  
  reason: (none given)
- `kind-untagged-summary` (untagged_unsupported, missed): Saturn exalted in Libra, Venus debilitated in Virgo.  
  reason: (none given)

## Validator + semantic checker (live)

Checker Qwen/Qwen3.6-35B-A3B on api.deepinfra.com (openai-compatible, structured output by json_schema), checker effort high; 124 checker calls, 305556 input and 526055 output tokens, 441 s; cost USD 0.53 at jyotish.costs's prices. Every row was checked.

| category | n | caught / false rejects | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- |
| overall | 147 | 83 of 86 | 0.965 | 0.965 | 0.965 |
| accepted | 61 | 3 false rejects | 0.000 | 1.000 | 0.000 |
| cites_too_narrowly | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| contradicts_its_fact | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |
| dasha_lord_changed | 6 | 6 of 6 | 1.000 | 1.000 | 1.000 |
| dignity_changed | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| family_not_cited | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| forbidden_word | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| house_changed | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| judgement_premise | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| negated | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| nth_sign | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| planet_swapped | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| ranking_not_cited | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| refers_to_another_claim | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| sign_changed | 5 | 5 of 5 | 1.000 | 1.000 | 1.000 |
| synthesis_does_not_follow | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| tag_not_offered | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| tier_word | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| unstated_claim | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| unsupported_clause | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| untagged | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| untagged_unsupported | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| wrong_dignity | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |

Misses and false rejects, with the checker's reason:

- `accept-26` (accepted, false reject): The house test favours marriage: the 2nd, the 8th and the 11th, marriage houses, are strong, the 7th, a marriage house, is middling, and the 1st from the Sun, the 7th's Bhavat Bhavam, is the weakest [vote:marriage.house].  
  reason: 'The 2nd, the 8th and the 11th are strong.': Data: Provides `bhava_bala_rupas` values for these houses but does not state or define them as 'strong'.; 'The 7th is middling.': Data: Provides `bhava_bala_rupas` values for the 7th house but does not state or define them as 'middling'.
- `accept-31` (accepted, false reject): Mars, lord of the 7th and lord of the 12th, sits in the 7th, a marriage house, in its own sign, while Venus, ruling the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th [rule:place.l7_h7] [rule:place.l12_h7] [rule:place.venus_h11] [vote:marriage.lord].  
  reason: 'Mars sits in its own sign': Unsupported. The cited findings (`place.l7_h7`, `place.l12_h7`) and their placement objects do not state the sign Mars occupies or its dignity.
- `b-ranking-career-fixed` (contradicts_its_fact, missed): The strongest support is in the lords, as the lord vote shows: Venus, lord of the 6th, is exalted in the 11th at a Shadbala ratio of 1.33, Mars, lord of the 7th and of the 10th from the Sun, is in its own sign at 1.3, and Mercury, lord of the 2nd, sits in the 10th at 1.19 [vote:career.lord] [fact:areas.career.contributions].  
  reason: supported
- `b-hyphen` (unstated_claim, missed): A second tension sits in Mars itself: its place in the 7th is a marana karaka sthana, for which the lord-of-the-7th-in-the-7th and lord-of-the-12th-in-the-7th placements are scaled to 0.6, while its Shadbala ratio stays at 1.3, and the facts leave the net quality of that placement open [rule:place.l7_h7] [rule:place.l12_h7] [fact:sensitive.Mars.marana_karaka_sthana] [fact:shadbala.planets.Mars.ratio].  
  reason: supported
- `kind-judgement-premise` (judgement_premise, missed): I give the lord family more weight than the arudha vote, since the arudha vote is against career [fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].  
  reason: supported
- `kind-untagged-framing` (accepted, false reject): Three areas follow, career first.  
  reason: 'There are exactly three areas to be discussed.': The data contains no findings, facts, or statements indicating the number of areas.; 'Career is the first of these three areas.': Appositive phrase 'career first' attaches to 'Three areas'. The data contains no findings, facts, or statements mentioning career or establishing a sequence.

## Against the gate in use

The rule (docs/models.md): this checker may gate client readings only if its recall is not worse on any category than Opus's last live run (docs/checker_scorecard.md).

| category | recall here | recall of the gate | not worse |
| --- | --- | --- | --- |
| dasha_lord_changed | 1.000 | 1.000 | yes |
| dignity_changed | 1.000 | 1.000 | yes |
| family_not_cited | 1.000 | 1.000 | yes |
| forbidden_word | 1.000 | 1.000 | yes |
| house_changed | 1.000 | 1.000 | yes |
| negated | 1.000 | 1.000 | yes |
| planet_swapped | 1.000 | 1.000 | yes |
| refers_to_another_claim | 1.000 | 0.000 | yes |
| sign_changed | 1.000 | 1.000 | yes |
| tag_not_offered | 1.000 | 1.000 | yes |
| tier_word | 1.000 | 1.000 | yes |
| unsupported_clause | 1.000 | 1.000 | yes |
| untagged | 1.000 | 1.000 | yes |
| wrong_dignity | 1.000 | 1.000 | yes |

Not in the gate's last run (the benchmark has grown since): cites_too_narrowly, contradicts_its_fact, judgement_premise, nth_sign, ranking_not_cited, synthesis_does_not_follow, unstated_claim, untagged_unsupported. The rule cannot be applied to these until the gate is run again (scripts/checker_bench.py with ANTHROPIC_API_KEY).

Verdict: not worse on any category both runs measured, but not yet decided: the gate has no run on cites_too_narrowly, contradicts_its_fact, judgement_premise, nth_sign, ranking_not_cited, synthesis_does_not_follow, unstated_claim, untagged_unsupported.

