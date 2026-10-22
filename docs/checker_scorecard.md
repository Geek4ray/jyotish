# Checker benchmark

Run 2026-10-22 at commit `b0eb697` by `scripts/checker_bench.py` on `tests/fixtures/checker_bench.jsonl` (119 rows: 45 accept, 74 reject). The positive class is reject.

## The code validator alone

| category | n | caught / false rejects | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- |
| overall | 119 | 16 of 74 | 1.000 | 0.216 | 0.356 |
| accepted | 45 | 0 false rejects | 1.000 | 1.000 | 1.000 |
| dasha_lord_changed | 6 | 0 of 6 | 1.000 | 0.000 | 0.000 |
| dignity_changed | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| family_not_cited | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| forbidden_word | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| house_changed | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| negated | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| planet_swapped | 9 | 1 of 9 | 1.000 | 0.111 | 0.200 |
| refers_to_another_claim | 2 | 0 of 2 | 1.000 | 0.000 | 0.000 |
| sign_changed | 5 | 0 of 5 | 1.000 | 0.000 | 0.000 |
| tag_not_offered | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| tier_word | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| unsupported_clause | 9 | 0 of 9 | 1.000 | 0.000 | 0.000 |
| untagged | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| wrong_dignity | 1 | 0 of 1 | 1.000 | 0.000 | 0.000 |

The validator reads tags and words, not meaning: it is meant to catch the tag and wording categories (family_not_cited, forbidden_word, tag_not_offered, tier_word, untagged) and to leave the semantic ones to the checker.

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
- `known_bad-1` (refers_to_another_claim, missed): The same conjunction joins the Sun as 4th lord with Mercury as 2nd and 5th lord in the 10th, forming a kendra-trikona raja yoga that points to authority, reputation and career standing [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12].  
  reason: (none given)
- `known_bad-2` (refers_to_another_claim, missed): Counted from the Sun, Mars falls in the 10th and again forms Ruchaka yoga, with the same weakening from Saturn's aspect, the tara and the marana karaka placement [rule:yoga.ruchaka] [text:Phaladeepika/Sastri-1937/6/1].  
  reason: (none given)
- `known_bad-4` (wrong_dignity, missed): The varga vote leans narrowly for career in the D10: Saturn, Mars and Venus score well there, while Jupiter and the Sun score poorly and Mercury and the Moon are neutral [vote:career.varga].  
  reason: (none given)

## Validator + semantic checker (live)

Model claude-opus-5-5, checker effort high; 103 checker calls, 340790 input and 63545 output tokens, 54 s. Cost: the token counts at the account's current price (not computed here).

| category | n | caught / false rejects | precision | recall | F1 |
| --- | --- | --- | --- | --- | --- |
| overall | 119 | 72 of 74 | 1.000 | 0.973 | 0.986 |
| accepted | 45 | 0 false rejects | 1.000 | 1.000 | 1.000 |
| dasha_lord_changed | 6 | 6 of 6 | 1.000 | 1.000 | 1.000 |
| dignity_changed | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| family_not_cited | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| forbidden_word | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| house_changed | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| negated | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| planet_swapped | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| refers_to_another_claim | 2 | 0 of 2 | 1.000 | 0.000 | 0.000 |
| sign_changed | 5 | 5 of 5 | 1.000 | 1.000 | 1.000 |
| tag_not_offered | 2 | 2 of 2 | 1.000 | 1.000 | 1.000 |
| tier_word | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| unsupported_clause | 9 | 9 of 9 | 1.000 | 1.000 | 1.000 |
| untagged | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |
| wrong_dignity | 1 | 1 of 1 | 1.000 | 1.000 | 1.000 |

Misses and false rejects, with the checker's reason:

- `known_bad-1` (refers_to_another_claim, missed): The same conjunction joins the Sun as 4th lord with Mercury as 2nd and 5th lord in the 10th, forming a kendra-trikona raja yoga that points to authority, reputation and career standing [rule:yoga.kendra_trikona_raja] [text:BPHS/Santhanam-1984/34/11-12].  
  reason: supported
- `known_bad-2` (refers_to_another_claim, missed): Counted from the Sun, Mars falls in the 10th and again forms Ruchaka yoga, with the same weakening from Saturn's aspect, the tara and the marana karaka placement [rule:yoga.ruchaka] [text:Phaladeepika/Sastri-1937/6/1].  
  reason: supported

