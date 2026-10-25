# Checker benchmark: zai-org/GLM-4.7 at checker effort none

Run 2026-10-26 at commit `4fbd284` by `scripts/checker_bench.py` on `tests/fixtures/checker_bench.jsonl` (147 rows: 61 accept, 86 reject). The positive class is reject.

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

Checker zai-org/GLM-4.7 on api.deepinfra.com (openai-compatible, structured output by json_schema), checker effort none; 124 checker calls, 215107 input and 44016 output tokens, 313 s; cost USD 0.17 at jyotish.costs's prices. Every row was checked.

| category | n | caught / false rejects | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- |
| overall | 147 | 76 of 86 | 0.809 | 0.884 | 0.844 |
| accepted | 61 | 18 false rejects | 0.000 | 1.000 | 0.000 |
| cites_too_narrowly | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| contradicts_its_fact | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| dasha_lord_changed | 6 | 5 of 6 | 1.000 | 0.833 | 0.909 |
| dignity_changed | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| family_not_cited | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| forbidden_word | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| house_changed | 9 | 8 of 9 | 1.000 | 0.889 | 0.941 |
| judgement_premise | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| negated | 9 | 6 of 9 | 1.000 | 0.667 | 0.800 |
| nth_sign | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| planet_swapped | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| ranking_not_cited | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| refers_to_another_claim | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| sign_changed | 5 | 5 of 5 | 1.000 | 1.000 | 1.000 |
| synthesis_does_not_follow | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |
| tag_not_offered | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| tier_word | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| unstated_claim | 2 | 1 of 2 | 1.000 | 0.500 | 0.667 |
| unsupported_clause | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| untagged | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| untagged_unsupported | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| wrong_dignity | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |

Misses and false rejects, with the checker's reason:

- `accept-02` (accepted, false reject): Mars forms Ruchaka yoga, tied to courage and leadership, counted from the Sun in the 10th, a career house, though in a reduced form [rule:yoga.ruchaka].  
  reason: 'Mars forms Ruchaka yoga': The finding calls this 'rule:yoga.ruchaka', but the sentence's phrasing asserts the yoga's existence. However, the data contains modifiers ('aspected_by: [Saturn]', 'marana_karaka_sthana') reducing the yoga's scale, and 'fires' entries list nodes rather than confirming the final result state. Because of this uncertainty and the ambiguity of 'forms', this is unsupported.
- `accept-04` (accepted, false reject): The Sun, lord of the 4th, joins Mercury, lord of the 2nd and the 5th, in the 10th, a career house, forming Kendra-Trikona Raja yoga [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12].  
  reason: 'The Sun is the lord of the 4th house.': The data lists the lordships for the finding, the finding states no facts, and no stated fact includes the Sun’s lordship of the 4th.; 'Mercury is the lord of the 2nd house.': The data lists the lordships for the finding, the finding states no facts, and no stated fact includes Mercury’s lordship of the 2nd.
- `accept-05` (accepted, false reject): The Sun and Mercury sit together in the 10th, a career house, forming Budhaditya yoga, with its strength trimmed because Mercury is in a weak degree state [rule:yoga.budhaditya] [text:Phaladeepika/Sastri-1937/18/1].  
  reason: 'because Mercury is in a weak degree state': Finding states 'avastha in [bala, mrita] (Mercury)'. Glossary defines Bala avastha as infant state and Mrita avastha as last of five degree states. It does not define 'weak degree state'. The 'because' clause is an unsupported interpretation/gloss of the specific avasthas listed.
- `accept-08` (accepted, false reject): Mars forms Ruchaka yoga from the lagna and from the Sun, sitting in the 7th, the 10th's Bhavat Bhavam, and in the 10th from the Sun, a career house, though it is reduced by Saturn's aspect, an adverse tara from the Moon and Mars standing in a marana karaka sthana [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].  
  reason: "the 7th is the 10th's Bhavat Bhavam": Glossary defines Bhavat Bhavam as the house as far from a given house as that house is from the ascendant. The 7th is the 10th's Bhavat Bhavam only if the 10th is the 4th (counting 10th->Ascendant->7th), which is not stated in the data.; 'the 10th from the Sun is a career house': The data's glossary and area_houses define the 10th house (from the lagna) as career, but do not state that the 10th from the Sun is a career house.
- `accept-14` (accepted, false reject): The dasamsa, the career chart, favours career: Mars and Saturn both fall in Capricorn with good dignity, the Sun, Jupiter and Venus are mildly well placed, and the Moon and Mercury are neutral [vote:career.varga].  
  reason: 'The Sun is mildly well placed': vote:career.varga.Sun.varga_dignity_label; 'Jupiter is mildly well placed': vote:career.varga.Jupiter.varga_dignity_label
- `accept-19` (accepted, false reject): The soft spot is the 10th itself, lowest of its houses by house strength, with its ruler Saturn short of its required strength, while Ruchaka yoga is held back by an aspect from Saturn and an awkward house placement [vote:career.house] [vote:career.lord] [rule:yoga.ruchaka].  
  reason: 'The soft spot is the 10th itself': The sentence uses a generic frame; this is unsupported as the 10th is not cited as a weak spot or 'soft spot' in the vote or findings.; 'The 10th is the lowest of its houses by house strength': Unsupported: the data (vote:career.house derivation) lists the 10th house from Lagna as having -1.0 relative strength, but the 10th from Moon (0.06) and the 10th from Sun (-0.04) are present; the judgement of 'lowest of its houses' across its bases is not asserted by the data.
- `accept-26` (accepted, false reject): The house test favours marriage: the 2nd, the 8th and the 11th, marriage houses, are strong, the 7th, a marriage house, is middling, and the 1st from the Sun, the 7th's Bhavat Bhavam, is the weakest [vote:marriage.house].  
  reason: 'the 2nd, the 8th and the 11th are strong': The 2nd, 8th, and 11th show mixed results; the 2nd is weak from the Moon, the 8th is weak from the Moon, and the 11th is weak from the Moon. The data does not state they are strong collectively.; 'the 7th is middling': The data states strength values (6.7, 8.51, 7.37) and relative scores (-0.27, 0.34, -0.04) for the 7th house, but does not define the category 'middling' or apply it.
- `accept-27` (accepted, false reject): The panchanga test favours marriage: Mars, ruler of the birth tithi and nakshatra, rules the 7th, a marriage house, and the 7th and 2nd from the Moon, and stands above its required strength [vote:marriage.panchanga].  
  reason: 'Mars stands above its required strength': Unsupported.
- `accept-38` (accepted, false reject): The panchanga test is favourable: Mars, ruler of the birth tithi and nakshatra, rules the 3rd from the Sun, and the Moon, ruler of the vara, rules the 3rd, both above their required strength [vote:longevity.panchanga].  
  reason: 'the Moon rules the 3rd': The derivation states the Moon rules the 3rd from the lagna, while the sentence implies it rules the same house as Mars (the 3rd from the Sun) or simply the absolute 3rd, conflicting with the data.
- `accept-40` (accepted, false reject): The lord test is favourable: Venus, lord of the 1st, is exalted in the 11th, Jupiter, lord of the 8th, sits in an enemy's sign in the 1st above its required strength, and the Moon, lord of the 3rd, is neutral in the 6th [vote:longevity.lord].  
  reason: 'Jupiter is above its required strength': The data lists a shadbala_ratio of 1.22 and a glossary definition for Shadbala, but does not define the "required strength" threshold or state that 1.22 is above it.
- `accept-41` (accepted, false reject): The divisional-chart test is favourable: the Moon is vargottama in Libra and Saturn falls in Capricorn in the navamsa, while Jupiter in Virgo in the trimsamsa is poorly placed [vote:longevity.varga].  
  reason: 'the Moon [vargottama] is in Libra': Sentence attaches 'in Libra' to the vargottama Moon, but the data states the vargottama Moon is in Libra only in the navamsa (D9), not that it is in Libra in the birth chart (which would be required for the vargottama condition to attach to Libra)
- `accept-43` (accepted, false reject): The tradition reads the 1st for the self, the body, temperament and general well-being [vote:longevity.house].  
  reason: 'The tradition reads the 1st house.': The sentence asserts a general traditional reading of the 1st house. The cited finding (vote:longevity.house) and its data concern a vote for longevity and define the 1st in relation to longevity, but do not state that the tradition reads the 1st house in itself, nor do they identify the school (Parashari) as covering this specific reading in the sentence's terms.; 'The tradition reads [the 1st for the self, the body, temperament and general well-being] for longevity.': The finding votes 'for' longevity (verdict.house: for) and lists the 1st as a 'longevity house' in area_houses. However, the sentence is structurally ambiguous: it can be read as asserting that the traditional meanings (self, body, etc.) *are* the meanings for longevity. The data states the 1st is a house *of* longevity, but the glossary defines the 1st as the self/body/etc., not that the self/body/etc. are the readings for longevity. This specific attachment of the 1st's meanings to the area of longevity is not stated by the data.
- `accept-44` (accepted, false reject): The dissenting test is the Jaimini one, the school that reads image points and its own significators, which counts Mars in the 7th and Saturn in the 1st as placements where a planet cannot give its good results [vote:longevity.arudha].  
  reason: "the relative clause 'which counts Mars in the 7th and Saturn in the 1st as placements where a planet cannot give its good results' attaches to 'the Jaimini school'": grammatical ambiguity
- `accept-45` (accepted, false reject): Of the six tests that apply, five agree and one is against [vote:longevity.house] [vote:longevity.lord] [vote:longevity.karaka] [vote:longevity.varga] [vote:longevity.arudha] [vote:longevity.panchanga].  
  reason: 'six tests apply': The data states there are 7 tests.
- `house_changed-8` (house_changed, missed): Mars forms Ruchaka yoga from the lagna and from the Sun, sitting in the 7th, the 1st's Bhavat Bhavam, and in the 10th from the Sun, a career house, though it is reduced by Saturn's aspect, an adverse tara from the Moon and Mars standing in a marana karaka sthana [rule:yoga.ruchaka] [text:BPHS/Santhanam-1984/75/1-2].  
  reason: supported
- `negated-1` (negated, missed): Mars does not form Ruchaka yoga, tied to courage and leadership, counted from the Sun in the 10th, a career house, though in a reduced form [rule:yoga.ruchaka].  
  reason: supported
- `negated-2` (negated, missed): The Sun and Mercury do not sit together in the 10th, a career house, forming Budhaditya yoga, with its strength trimmed because Mercury is in a weak degree state [rule:yoga.budhaditya] [text:Phaladeepika/Sastri-1937/18/1].  
  reason: supported
- `negated-4` (negated, missed): Mercury, lord of the 5th, does not sit in the 10th, a career house [rule:place.l5_h10].  
  reason: supported
- `dasha_lord_changed-5` (dasha_lord_changed, missed): Ketu, the Moon's south node, sits in the 8th, while Saturn and Jupiter share the 1st and Venus, ruler of the 1st, sits exalted, in the sign where the texts hold a planet at its peak, in the 11th, and the current major period of Saturn activates Venus through its nakshatra [rule:place.ketu_h8] [vote:longevity.karaka] [vote:longevity.lord] [chain:longevity.lord].  
  reason: supported
- `known_bad-4` (wrong_dignity, missed): The varga vote leans narrowly for career in the D10: Saturn, Mars and Venus score well there, while Jupiter and the Sun score poorly and Mercury and the Moon are neutral [vote:career.varga].  
  reason: supported
- `b-varga-longevity` (accepted, false reject): The varga vote is for longevity: in the navamsa the Moon is vargottama in Libra and scores 1.0 and Saturn in its own sign Capricorn scores 0.5, while in the trimsamsa Jupiter in Virgo scores -0.25 and the other planets score 0 or 0.25 [vote:longevity.varga].  
  reason: 'the other planets score 0 or 0.25': Planets in derivation have scores of 0.25 (Mars, Mercury, Venus, Saturn D30); none are listed as 0. Others (Sun) are not present or unverified.
- `b-stability-longevity` (accepted, false reject): The trimsamsa signs of Jupiter, Mars and Venus hold under two of the three ayanamsas, which bears on the varga vote [fact:stability.placements.D30.Jupiter] [fact:stability.placements.D30.Mars] [fact:stability.placements.D30.Venus] [fact:stability.ayanamsas] [vote:longevity.varga].  
  reason: 'The holding under two of the three ayanamsas bears on the varga vote': synthesis
- `b-nth-sign-fixed` (accepted, false reject): The timing join's full targets for career are Aquarius, the 10th house from the lagna, and Taurus, the sign of the A10 [fact:timing.career.windows.0.targets.full] [fact:jaimini.arudhas.A10] [fact:houses.lagna.10].  
  reason: "The timing join's full targets for career are Aquarius": The data lists 'Aquarius' and 'Taurus' as the targets for full targets for career, but does not assert that 'The timing join's full targets for career are Aquarius' as a standalone proposition independent of 'Taurus'. The sentence structure implies these are separate targets rather than a compound subject belonging to the career targets.
- `b-arudha` (cites_too_narrowly, missed): The arudha vote is 0, so the A10 gives no verdict on how the career appears [fact:areas.career.votes.arudha.vote].  
  reason: supported
- `b-votes-fact` (unstated_claim, missed): The votes for this area weigh houses, lords, karakas, vargas, the arudha and the panchanga, and this reading draws no medical statement from them [fact:areas.longevity.votes].  
  reason: supported
- `kind-judgement-premise` (judgement_premise, missed): I give the lord family more weight than the arudha vote, since the arudha vote is against career [fact:areas.career.contributions.largest_term] [fact:areas.career.votes.arudha.vote].  
  reason: supported
- `kind-synthesis-does-not-follow` (synthesis_does_not_follow, missed): Mars is in its own sign in the 7th house from the lagna, so Mars rules the 10th house from the lagna [fact:planets.Mars.dignity] [fact:houses.lagna.7].  
  reason: supported
- `kind-untagged-framing` (accepted, false reject): Three areas follow, career first.  
  reason: 'Three areas follow': The data has an empty `findings` list and states no facts.; 'Career is first': The data has an empty `findings` list and states no facts.

## Against the gate in use

The rule (docs/models.md): this checker may gate client readings only if its recall is not worse on any category than the gate in use, zai-org/GLM-4.7 (docs/checker_scorecard_zai-org-glm-4.7.md).

| category | recall here | recall of the gate | not worse |
| --- | --- | --- | --- |
| cites_too_narrowly | 0.500 | 1.000 | no |
| contradicts_its_fact | 1.000 | 1.000 | yes |
| dasha_lord_changed | 0.833 | 1.000 | no |
| dignity_changed | 1.000 | 1.000 | yes |
| family_not_cited | 1.000 | 1.000 | yes |
| forbidden_word | 1.000 | 1.000 | yes |
| house_changed | 0.889 | 1.000 | no |
| judgement_premise | 0.500 | 1.000 | no |
| negated | 0.667 | 1.000 | no |
| nth_sign | 1.000 | 1.000 | yes |
| planet_swapped | 1.000 | 1.000 | yes |
| ranking_not_cited | 1.000 | 1.000 | yes |
| refers_to_another_claim | 1.000 | 1.000 | yes |
| sign_changed | 1.000 | 1.000 | yes |
| synthesis_does_not_follow | 0.000 | 1.000 | no |
| tag_not_offered | 1.000 | 1.000 | yes |
| tier_word | 1.000 | 1.000 | yes |
| unstated_claim | 0.500 | 1.000 | no |
| unsupported_clause | 1.000 | 1.000 | yes |
| untagged | 1.000 | 1.000 | yes |
| untagged_unsupported | 1.000 | 1.000 | yes |
| wrong_dignity | 0.000 | 1.000 | no |

Verdict: worse on cites_too_narrowly, dasha_lord_changed, house_changed, judgement_premise, negated, synthesis_does_not_follow, unstated_claim, wrong_dignity: it does not pass the rule, and client readings keep the gate in use.

