"""Fixed tables of Jyotish. Everything here is a convention from a named text;
where sources differ the module says so and the engine exposes a setting."""

from __future__ import annotations

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Classical nine grahas, in the order used throughout the engine.
GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN = GRAHAS[:7]

# Sign lords (primary). Scorpio/Aquarius co-lords Ketu/Rahu are a Jaimini convention
# and are handled where the Jaimini module needs them.
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
OWN_SIGNS = {p: [s for s, l in SIGN_LORD.items() if l == p] for p in SEVEN}

# Sign classes.
MOVABLE = {0, 3, 6, 9}
FIXED = {1, 4, 7, 10}
DUAL = {2, 5, 8, 11}
FIRE = {0, 4, 8}
EARTH = {1, 5, 9}
AIR = {2, 6, 10}
WATER = {3, 7, 11}


def is_odd_sign(sign: int) -> bool:
    """Aries = 0 is an odd (male) sign; Taurus = 1 is even."""
    return sign % 2 == 0


# Exaltation sign and deep-exaltation degree (BPHS 3.49-50); debilitation is the 7th sign.
EXALTATION = {
    "Sun": (0, 10.0), "Moon": (1, 3.0), "Mars": (9, 28.0), "Mercury": (5, 15.0),
    "Jupiter": (3, 5.0), "Venus": (11, 27.0), "Saturn": (6, 20.0),
}
# Moolatrikona: sign and degree range (BPHS 3.51-54).
MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0), "Moon": (1, 3.0, 30.0), "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 15.0, 20.0), "Jupiter": (8, 0.0, 10.0), "Venus": (6, 0.0, 15.0),
    "Saturn": (10, 0.0, 20.0),
}

# Natural (naisargika) friendships, BPHS ch. 3. Rahu/Ketu left out: schools differ.
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}

# Combustion orbs in degrees (BPHS 3.59-61); second value when retrograde where given.
COMBUST_ORB = {
    "Moon": (12.0, 12.0), "Mars": (17.0, 17.0), "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0), "Venus": (10.0, 8.0), "Saturn": (15.0, 15.0),
}

# Parashari special aspects: houses from the planet (7th for all).
SPECIAL_ASPECTS = {"Mars": [4, 8], "Jupiter": [5, 9], "Saturn": [3, 10]}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "PurvaPhalguni", "UttaraPhalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyestha", "Mula", "PurvaAshadha",
    "UttaraAshadha", "Shravana", "Dhanishtha", "Shatabhisha", "PurvaBhadra",
    "UttaraBhadra", "Revati",
]
NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'

# --- the 27 nakshatras' attributes (SPEC Layer 2, nakshatra layer) ---------------------------
# One row per nakshatra, Ashwini first: deity, gana, yoni (animal) and the animal's sex, nadi (dosha),
# tri-nadi segment, gender (the modern listing), direction, activity. Each column's source is in NAK_ATTRIBUTE_SOURCES; none has been
# read against its edition yet (checked: false), and where texts are known to differ the note
# says so. Nadi and the tri-nadi segment are one classification under two names (adi = vata,
# madhya = pitta, antya = kapha), kept as two columns because the koota tables use the first and
# the Nadi texts the second.
NAK_ATTRIBUTE_SOURCES = {
    "deity": {"text": "Brihat Samhita", "edition": "M. Ramakrishna Bhat 1981", "chapter": 98, "checked": False},
    "activity": {"text": "Brihat Samhita", "edition": "M. Ramakrishna Bhat 1981", "chapter": 98, "checked": False,
                 "note": "the seven classes: dhruva (fixed), chara (movable), ugra (fierce), mishra (mixed), "
                         "kshipra (swift), mridu (soft), tikshna (sharp)"},
    "gana": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
             "chapter": 6, "checked": False, "note": "the marriage koota tables"},
    "yoni": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
             "chapter": 6, "checked": False},
    "nadi": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
             "chapter": 6, "checked": False},
    "tri_nadi": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
                 "chapter": 6, "checked": False, "note": "the same three groups as nadi, by segment"},
    "direction": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
                  "chapter": 11, "checked": False,
                  "note": "seven nakshatras to each quarter from Krittika (east); with Abhijit the west has seven, "
                          "without it six"},
    "yoni_sex": {"text": "Muhurta Chintamani", "edition": "G.C. Sharma (edition to be confirmed by the reader)",
                 "chapter": 6, "checked": False,
                 "note": "the Yoni koota's male or female animal: every animal has one of each (the mongoose a male "
                         "alone), so the column is checkable against itself"},
    "gender": {"text": "not yet located in a classical text", "edition": None, "checked": False,
               "note": "the listing of the modern compilations: eight male (Ashwini, Punarvasu, Pushya, Hasta, Anuradha, "
                       "Shravana, Purva and Uttara Bhadrapada), three neuter where the texts differ (Mrigashira, Mula, "
                       "Shatabhisha), sixteen female. The first table (2026-10-22) mixed this with the yoni's sex and "
                       "matched neither (review 2026-10-23, F8); the koota's sex is yoni_sex"},
}
_NAK_ROWS = [
    # deity, gana, yoni, yoni_sex, nadi, tri_nadi, gender, direction, activity
    ("Ashwini Kumaras", "deva", "horse", "male", "vata", "adi", "male", "north", "kshipra"),
    ("Yama", "manushya", "elephant", "male", "pitta", "madhya", "female", "north", "ugra"),
    ("Agni", "rakshasa", "sheep", "female", "kapha", "antya", "female", "east", "mishra"),
    ("Brahma", "manushya", "serpent", "male", "kapha", "antya", "female", "east", "dhruva"),
    ("Soma", "deva", "serpent", "female", "pitta", "madhya", "neuter", "east", "mridu"),
    ("Rudra", "manushya", "dog", "female", "vata", "adi", "female", "east", "tikshna"),
    ("Aditi", "deva", "cat", "female", "vata", "adi", "male", "east", "chara"),
    ("Brihaspati", "deva", "sheep", "male", "pitta", "madhya", "male", "east", "kshipra"),
    ("Sarpas", "rakshasa", "cat", "male", "kapha", "antya", "female", "east", "tikshna"),
    ("Pitris", "rakshasa", "rat", "male", "kapha", "antya", "female", "south", "ugra"),
    ("Bhaga", "manushya", "rat", "female", "pitta", "madhya", "female", "south", "ugra"),
    ("Aryaman", "manushya", "cow", "male", "vata", "adi", "female", "south", "dhruva"),
    ("Savitar", "deva", "buffalo", "female", "vata", "adi", "male", "south", "kshipra"),
    ("Tvashtar", "rakshasa", "tiger", "female", "pitta", "madhya", "female", "south", "mridu"),
    ("Vayu", "deva", "buffalo", "male", "kapha", "antya", "female", "south", "chara"),
    ("Indragni", "rakshasa", "tiger", "male", "kapha", "antya", "female", "south", "mishra"),
    ("Mitra", "deva", "deer", "female", "pitta", "madhya", "male", "west", "mridu"),
    ("Indra", "rakshasa", "deer", "male", "vata", "adi", "female", "west", "tikshna"),
    ("Nirriti", "rakshasa", "dog", "male", "vata", "adi", "neuter", "west", "tikshna"),
    ("Apas", "manushya", "monkey", "male", "pitta", "madhya", "female", "west", "ugra"),
    ("Vishvedevas", "manushya", "mongoose", "male", "kapha", "antya", "female", "west", "dhruva"),
    ("Vishnu", "deva", "monkey", "female", "kapha", "antya", "male", "west", "chara"),
    ("Vasus", "rakshasa", "lion", "female", "pitta", "madhya", "female", "north", "chara"),
    ("Varuna", "rakshasa", "horse", "female", "vata", "adi", "neuter", "north", "chara"),
    ("Aja Ekapada", "manushya", "lion", "male", "vata", "adi", "male", "north", "ugra"),
    ("Ahirbudhnya", "manushya", "cow", "female", "pitta", "madhya", "male", "north", "dhruva"),
    ("Pushan", "deva", "elephant", "female", "kapha", "antya", "female", "north", "mridu"),
]
NAK_ATTRIBUTE_KEYS = ("deity", "gana", "yoni", "yoni_sex", "nadi", "tri_nadi", "gender", "direction", "activity")
NAK_ATTRIBUTES = [dict(zip(NAK_ATTRIBUTE_KEYS, row)) for row in _NAK_ROWS]
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20'

# Vimshottari order and years; nakshatra lords repeat this cycle three times from Ashwini.
VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
                     "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
VIMSHOTTARI_TOTAL = 120


def nakshatra_lord(idx: int) -> str:
    return VIMSHOTTARI_ORDER[idx % 9]


# Navatara: the nine-fold cycle counted from the Moon's nakshatra (Janma = 1).
TARA_NAMES = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhaka", "Vadha", "Mitra", "Atimitra"]
TARA_ADVERSE = {"Vipat", "Pratyak", "Vadha"}
# Special taras by absolute count from Janma, a setting (Meta.special_taras): the lists differ on
# where Jati and Desha fall. "desha_27" is the common modern list (Jagannatha Hora's among them):
# Jati 26, Desha 27. "desha_12" is SPEC rev 101's worked example: Desha 12, Jati 27. Neither is read
# in a named edition yet (review 2026-10-23); the engine's default is the first, the reference app's
# family, and the SPEC's reading is kept as the second so that nothing it says is lost.
SPECIAL_TARA_SCHEMES = {
    "desha_27": {1: "janma", 10: "karma", 16: "sanghatika", 18: "samudaya", 19: "adhana", 23: "vinasha",
                 25: "manasa", 26: "jati", 27: "desha"},
    "desha_12": {1: "janma", 10: "karma", 12: "desha", 16: "sanghatika", 18: "samudaya", 19: "adhana",
                 23: "vinasha", 25: "manasa", 27: "jati"},
}
DEFAULT_SPECIAL_TARAS = "desha_27"
SPECIAL_TARAS = SPECIAL_TARA_SCHEMES[DEFAULT_SPECIAL_TARAS]

# Baladi avastha spans (BPHS 45.3-4): forward in odd signs, reversed in even signs.
BALADI = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]

# Marana Karaka Sthana (Jaimini tradition as taught by Rath): planet -> house.
MARANA_KARAKA_STHANA = {"Sun": 12, "Moon": 8, "Mars": 7, "Mercury": 7, "Jupiter": 3,
                        "Venus": 6, "Saturn": 1, "Rahu": 9}

# Pushkara navamsa degree ranges per element (Jataka Parijata) and Pushkara bhaga degrees.
PUSHKARA_NAVAMSA = {
    "fire": [(20.0, 23.333), (26.667, 30.0)],
    "earth": [(6.667, 10.0), (13.333, 16.667)],
    "air": [(16.667, 20.0), (23.333, 26.667)],
    "water": [(0.0, 3.333), (6.667, 10.0)],
}
PUSHKARA_BHAGA = {0: 21, 1: 14, 2: 18, 3: 8, 4: 24, 5: 19, 6: 24, 7: 11, 8: 23, 9: 14, 10: 19, 11: 9}

# Gandanta: the last 3°20' of a water sign and the first 3°20' of a fire sign.
GANDANTA_SPAN = 3.3333

# Nitya-yoga lords follow the Vimshottari cycle starting from Saturn.
YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma",
    "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
    "Shukla", "Brahma", "Indra", "Vaidhriti",
]
YOGA_LORD_ORDER = ["Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter"]

TITHI_LORD_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu",
                    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]  # Sunday = 0
KARANA_NAMES = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
                "Shakuni", "Chatushpada", "Naga", "Kimstughna"]

# --- Ashtakavarga -------------------------------------------------------------------
# Benefic places (bindus), BPHS ch. 66: for each target's Bhinnashtakavarga, the houses
# counted from each contributor (contributor's sign = 1) where the contributor gives a
# bindu. Contributors are the seven planets and the lagna ("Asc"); the nodes contribute
# nothing (BPHS), although some modern software adds them. The row totals are the
# classical counts in ASHTAKAVARGA_TOTALS and are checked at import, which catches a
# mistyped cell but not two compensating ones.
ASHTAKAVARGA_CONTRIBUTORS = SEVEN + ["Asc"]
ASHTAKAVARGA_BENEFIC = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11), "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11), "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11), "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11), "Asc": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11), "Moon": (1, 3, 6, 7, 10, 11),
        "Mars": (2, 3, 5, 6, 9, 10, 11), "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 4, 7, 8, 10, 11, 12), "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11), "Asc": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11), "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11), "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12), "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11), "Asc": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12), "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11), "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12), "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11), "Asc": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11), "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11), "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11), "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12), "Asc": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12), "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 5, 6, 9, 11, 12), "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11), "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11), "Asc": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11), "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12), "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12), "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11), "Asc": (1, 3, 4, 6, 10, 11),
    },
    # The lagna's own table (BPHS 66.61-68). The Sanskrit of these verses is compressed
    # and editions render it differently; this is the commonly published form, 49 bindus.
    # It is not part of the Sarvashtakavarga.
    "Asc": {
        "Sun": (3, 4, 6, 10, 11, 12), "Moon": (3, 6, 10, 11, 12),
        "Mars": (1, 3, 6, 10, 11), "Mercury": (1, 2, 4, 6, 8, 10, 11),
        "Jupiter": (1, 2, 4, 5, 6, 7, 9, 10, 11), "Venus": (1, 2, 3, 4, 5, 8, 9),
        "Saturn": (1, 3, 4, 6, 10, 11), "Asc": (3, 6, 10, 11),
    },
}
ASHTAKAVARGA_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56,
                       "Venus": 52, "Saturn": 39, "Asc": 49}
SARVASHTAKAVARGA_TOTAL = 337   # the seven planets' tables; lagna and nodes excluded
for _t, _rows in ASHTAKAVARGA_BENEFIC.items():
    assert sum(len(v) for v in _rows.values()) == ASHTAKAVARGA_TOTALS[_t], _t
assert sum(ASHTAKAVARGA_TOTALS[p] for p in SEVEN) == SARVASHTAKAVARGA_TOTAL

# Ekadhipatya Shodhana (BPHS 68.1-6) runs on the pairs of signs with one lord; Cancer and
# Leo are exempt. Two points the texts leave open, both settings (Meta):
#  - occupants: BPHS says "planets"; the seven are used, the nodes are not (some software
#    counts them). Setting: Meta.ekadhipatya_nodes.
#  - a zero sign: BPHS states a zero exemption for Trikona (67.4) but none for Ekadhipatya,
#    so by its case table an occupied sign with 0 clears its vacant partner. Raman-school
#    teaching skips the pair when either sign is 0. Setting: Meta.ekadhipatya_zero_exempt.
# A third reading (both vacant and unequal: zero the smaller, keep the larger) appears in
# some modern write-ups; it is not what BPHS 68 says and is not implemented.
EKADHIPATYA_PAIRS = {"Mars": (0, 7), "Venus": (1, 6), "Mercury": (2, 5),
                     "Jupiter": (8, 11), "Saturn": (9, 10)}

# Pinda multipliers (BPHS 69.1-4). Rasi: Taurus, Leo 10; Gemini, Scorpio 8; Aries, Libra 7;
# Capricorn, Virgo 5; the rest by their number (Cancer 4, Sagittarius 9, Aquarius 11,
# Pisces 12). Graha: Jupiter 10, Mars 8, Venus 7, the rest 5.
RASI_GUNAKARA = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]
GRAHA_GUNAKARA = {"Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5, "Jupiter": 10,
                  "Venus": 7, "Saturn": 5}

# Kakshya: each sign in eight parts of 3°45', lorded in the order of the planetary spheres
# from the outermost, ending with the lagna (B.V. Raman, Ashtakavarga System of
# Prediction, Kakshya chapter; the verse locus in the classical texts is not checked here).
KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Asc"]

# --- Shadbala (BPHS ch. 27), all values in virupas (60 virupas = 1 rupa) ----------------
# Required minimum per planet (BPHS 27, in rupas: 6.5, 6, 5, 7, 6.5, 5.5, 5).
SHADBALA_REQUIRED = {"Sun": 390.0, "Moon": 360.0, "Mars": 300.0, "Mercury": 420.0,
                     "Jupiter": 390.0, "Venus": 330.0, "Saturn": 300.0}
# Naisargika: 60 * k / 7 in the order Saturn (1) ... Sun (7). Exact, not the truncated
# two-decimal figures some tables print.
NAISARGIKA = {p: 60.0 * k / 7.0 for p, k in
              (("Sun", 7), ("Moon", 6), ("Venus", 5), ("Jupiter", 4), ("Mercury", 3),
               ("Mars", 2), ("Saturn", 1))}

# Saptavargaja: the seven vargas and the virupas per dignity in each. Moolatrikona is read
# in D1 only, by its degree range; exaltation plays no part (it is Uchcha bala's job).
# Two scales are in use (setting Meta.saptavargaja_scale):
#  - "bphs": 45, 30, 20, 15, 10, 4, 2 (BPHS 27 as commonly translated);
#  - "raman": 45, 30, 22.5, 15, 7.5, 3.75, 1.875 (halving from own; B.V. Raman, Graha and
#    Bhava Balas). Neither verse locus is checked here.
SAPTAVARGA = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
SAPTAVARGAJA_SCALES = {
    "bphs": {"moolatrikona": 45.0, "own": 30.0, "great_friend": 20.0, "friend": 15.0,
             "neutral": 10.0, "enemy": 4.0, "great_enemy": 2.0},
    "raman": {"moolatrikona": 45.0, "own": 30.0, "great_friend": 22.5, "friend": 15.0,
              "neutral": 7.5, "enemy": 3.75, "great_enemy": 1.875},
}

# Drekkana bala: 15 virupas to a planet in the decanate of its sex (setting
# Meta.drekkana_bala). BPHS 27: male (Sun, Mars, Jupiter) 1st, female (Moon, Venus) 2nd,
# neuter (Mercury, Saturn) 3rd. Phaladeepika (Mantreswara) puts the neuters in the middle
# and the females at the end: male 1st, neuter 2nd, female 3rd.
DREKKANA_BALA_DECANATE = {
    "bphs": {"Sun": 0, "Mars": 0, "Jupiter": 0, "Moon": 1, "Venus": 1, "Mercury": 2, "Saturn": 2},
    "phaladeepika": {"Sun": 0, "Mars": 0, "Jupiter": 0, "Mercury": 1, "Saturn": 1, "Moon": 2, "Venus": 2},
}

# Dig bala: the point of full strength (60); the opposite point gives 0.
DIG_STRONG_POINT = {"Sun": "mc", "Mars": "mc", "Jupiter": "asc", "Mercury": "asc",
                    "Saturn": "desc", "Moon": "ic", "Venus": "ic"}

# Nathonnata (diva-ratri) bala: strong at midday, strong at midnight, always full.
NATHONNATA_DAY = {"Sun", "Jupiter", "Venus"}
NATHONNATA_NIGHT = {"Moon", "Mars", "Saturn"}

# Tribhaga: the lord of the third of the day or night in which birth falls gets 60;
# Jupiter always gets 60.
TRIBHAGA_DAY = ["Mercury", "Sun", "Saturn"]
TRIBHAGA_NIGHT = ["Moon", "Venus", "Mars"]

# Abda, Masa, Vara, Hora bala: the lord of the year, month, weekday and hour.
KALA_LORD_BALA = {"abda": 15.0, "masa": 30.0, "vara": 45.0, "hora": 60.0}
# Abda and Masa lords from the Ahargana counted from the Kali epoch (JD 588465.5,
# a Friday) in 360-day years and 30-day months: the lord is the weekday lord of the
# day the current year or month began. Some software uses the weekday of the Sun's
# ingress into Aries (and into its current sign) instead; that variant is not implemented.
KALI_EPOCH_JDN = 588466
# Hora lords descend the Chaldean order from the weekday lord at sunrise. Horas are
# equal 60-minute hours from sunrise (BPHS: one hora = 2.5 ghatis); unequal day/night
# horas are not implemented.
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

# Ayana bala: (24 + d) / 48 * 60, d being the declination in degrees counted positive
# north for the Sun, Mars, Jupiter and Venus, positive south for the Moon and Saturn, and
# always positive for Mercury. The declination is the kranti from the sayana longitude
# (ecliptic latitude ignored), with obliquity set by Meta.ayana_obliquity: "bphs" uses
# the classical parama kranti of 24 degrees; "true" uses the mean obliquity of date. The
# Sun's ayana bala is doubled (Meta.ayana_sun_double).
AYANA_NORTH = {"Sun", "Mars", "Jupiter", "Venus"}
AYANA_SOUTH = {"Moon", "Saturn"}
PARAMA_KRANTI = 24.0

# Chesta bala for Mars to Saturn: the cheshta kendra, seeghrochcha minus the mean of the
# planet's mean and true longitudes, folded to 0-180 and divided by 3. Seeghrochcha is the
# mean Sun for Mars, Jupiter and Saturn, and the planet's own heliocentric mean longitude
# for Mercury and Venus, whose mean planet is the mean Sun. The mean longitudes are modern
# (Meeus, Astronomical Algorithms, table 31.A, mean equinox of date), not Surya Siddhanta
# mean motions, so values can differ by a few virupas from software using the latter.
MEAN_LONGITUDE = {  # degrees at J2000 and per Julian century
    "Mercury": (252.250906, 149474.0722491), "Venus": (181.979801, 58519.2130302),
    "Sun": (280.466457, 36000.7698278), "Mars": (355.433000, 19141.6964471),
    "Jupiter": (34.351519, 3036.3027748), "Saturn": (50.077444, 1223.5110686),
}
# Sun and Moon: BPHS 27 makes the Sun's chesta its ayana bala and the Moon's its paksha
# bala ("bphs"); some software gives both 0 since they never retrograde ("zero").
# Setting Meta.chesta_luminaries.

# Paksha bala: elongation of the Moon from the Sun folded to 0-180, divided by 3, to the
# benefics; 60 minus that to the malefics. The Moon takes the benefic value, doubled
# (Meta.paksha_moon_double). Mercury is malefic when it shares a sign with the Sun, Mars,
# Saturn, Rahu or Ketu ("association", BPHS) or always benefic ("benefic").
# Setting Meta.mercury_nature. The Moon is benefic for Drik bala when waxing.
PAKSHA_BENEFICS = {"Jupiter", "Venus"}
PAKSHA_MALEFICS = {"Sun", "Mars", "Saturn"}
MERCURY_SPOILERS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Yuddha: two of Mars, Mercury, Jupiter, Venus, Saturn within 1 degree are at war. The
# difference of their Sthana + Dig + Kala (before Yuddha) totals, divided by the
# difference of their disc diameters, is added to the stronger and taken from the weaker.
# The diameters (arc-seconds) are as Raman prints them for Shadbala; they are not checked
# against the text here.
YUDDHA_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
YUDDHA_ORB = 1.0
BIMBA_DIAMETER = {"Mars": 9.4, "Mercury": 6.6, "Jupiter": 190.4, "Venus": 16.6, "Saturn": 158.0}

# --- Yogini dasha ---------------------------------------------------------------------
# Eight yoginis, their planets and years (36 in all). The first is found from the Moon's
# nakshatra: (nakshatra number, Ashwini = 1, + 3) mod 8, with 0 read as 8 (Sankata), and
# its balance is the Moon's unelapsed share of the nakshatra. Antardashas start with the
# maha yogini and run in order, each maha_years * antar_years / 36. (BPHS, Yogini dasha
# chapter; verse locus not checked here.)
YOGINIS = [("Mangala", "Moon", 1), ("Pingala", "Sun", 2), ("Dhanya", "Jupiter", 3),
           ("Bhramari", "Mars", 4), ("Bhadrika", "Mercury", 5), ("Ulka", "Saturn", 6),
           ("Siddha", "Venus", 7), ("Sankata", "Rahu", 8)]
YOGINI_TOTAL = 36

# --- Chara (Jaimini) dasha --------------------------------------------------------------
# Odd-footed (savya, vishamapada) signs: Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius.
# The other six are even-footed (apasavya, samapada). Every variant uses these groups.
SAVYA = {0, 1, 2, 6, 7, 8}
# Scorpio and Aquarius have two lords for Chara dasha.
CHARA_CO_LORD = {7: "Ketu", 10: "Rahu"}
# Exaltation of the nodes for Rath's Phalita dashas (Narayana Dasa, Sagar, pp. 41-42,
# following Mantreswara): Rahu in Gemini, Ketu in Sagittarius, debilitated opposite. The
# other variants' sources are silent on the nodes, so they get no exaltation adjustment.
RATH_NODE_EXALTATION = {"Rahu": 2, "Ketu": 8}

# --- Transits (gochara) ----------------------------------------------------------------
# Gochara is read from the natal Moon's sign (Phaladeepika 26.1, Sastri 1937). Good houses
# and their Vedha places, Phaladeepika 26.3-8 as printed in that edition: a transit in a
# good house is obstructed while another planet transits its Vedha place. The nodes are
# "similar to the Sun" (26.2), so they take the Sun's places; the Vedha verses themselves
# do not name them. All planets are good in the 11th (26.2).
GOCHARA_VEDHA = {
    "Sun": {11: 5, 3: 9, 10: 4, 6: 12},
    "Moon": {7: 2, 1: 5, 6: 12, 11: 8, 10: 4, 3: 9},
    "Mars": {3: 12, 11: 5, 6: 9},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 11: 8, 9: 10, 5: 4, 7: 3},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 12: 6, 11: 3},
    "Saturn": {3: 12, 11: 5, 6: 9},
    "Rahu": {11: 5, 3: 9, 10: 4, 6: 12},
    "Ketu": {11: 5, 3: 9, 10: 4, 6: 12},
}
# No Vedha between father and son: Saturn does not obstruct the Sun nor the Sun Saturn
# (26.3, 26.5); likewise the Moon and Mercury (26.4, 26.6). Rahu and Ketu are exempted from
# each other by the engine, not the text: every Vedha place in the Sun's table is the 7th
# from its good house, so with the nodes always 7th apart each would obstruct the other
# for ever.
VEDHA_EXEMPT = [{"Sun", "Saturn"}, {"Moon", "Mercury"}, {"Rahu", "Ketu"}]
# Vipareeta Vedha (a transit in a Vedha place relieved while a planet transits the good
# house it belongs to) is the same table read backwards. It is not in Phaladeepika 26;
# its source is unverified.

# Murthi Nirnaya: the transiting Moon's house from the natal Moon when a slow planet enters
# a sign grades that whole transit. Source unverified (not in Phaladeepika).
MURTHI = {1: "gold", 6: "gold", 11: "gold", 2: "silver", 5: "silver", 9: "silver",
          3: "copper", 7: "copper", 10: "copper", 4: "iron", 8: "iron", 12: "iron"}

# Ashtakavarga grading of a transit by the bindus of the transiting planet's own BAV in
# the sign (Phaladeepika 23.11, Sastri 1937): 1 loss, 2 expenditure, 3-4 fear, 5-8 rising
# fortune. The verse's reading of 0 bindus concerns longevity, which the engine does not
# time (SPEC scope), so 0 is reported only as "severe".
def ashtakavarga_grade(bindus: int) -> str:
    return "severe" if bindus <= 1 else "adverse" if bindus <= 4 else "favourable"

# --- Bhava Bala (BPHS 27.26-31, Santhanam 1984) -------------------------------------------
# Dig bala of a bhava: the bhava madhya's distance from a cardinal point, by the madhya's
# sign, folded to 0-180 and divided by 3. The verse names the point to deduct; signs not
# split are whole. Key: (sign, half) with half 0 = first 15°, 1 = second; None = whole sign.
BHAVA_DIG_POINT = {   # "desc": human signs; "ic": quadrupeds; "asc": Cancer, Scorpio; "mc": watery
    5: "desc", 2: "desc", 6: "desc", 10: "desc", (8, 0): "desc",
    0: "ic", 1: "ic", 4: "ic", (9, 0): "ic", (8, 1): "ic",
    3: "asc", 7: "asc",
    (9, 1): "mc", 11: "mc",
}
# 27.30-31: occupants add or remove a rupa; 15 virupas by the rising type of the bhava's
# sign and the time of birth (head-rising at day, dual at twilight, back-rising at night).
BHAVA_OCCUPANT = {"Jupiter": 60.0, "Mercury": 60.0, "Saturn": -60.0, "Mars": -60.0, "Sun": -60.0}
BHAVA_TIME_BONUS = 15.0
# Rising types (setting Meta.rising_signs). "bphs": BPHS ch. 4 (Santhanam 1984, vv. 6-24):
# head-rising Gemini, Leo, Virgo, Libra, Sagittarius, Aquarius; back-rising Aries, Taurus,
# Cancer, Capricorn; Pisces both. Ch. 4 does not give Scorpio's; it is taken as head-rising
# with the other texts. "phaladeepika": Phaladeepika 1.8 (Sastri 1937): back-rising Aries,
# Taurus, Cancer, Sagittarius, Capricorn; both ways Gemini, Pisces; head-rising the rest.
# A sign rising both ways counts for the day bonus and for the night bonus.
RISING_SIGNS = {
    "bphs": {"head": {2, 4, 5, 6, 7, 8, 10}, "back": {0, 1, 3, 9}, "both": {11}},
    "phaladeepika": {"head": {4, 5, 6, 7, 10}, "back": {0, 1, 3, 8, 9}, "both": {2, 11}},
}
DUAL_SIGNS = {2, 5, 8, 11}

# --- Vimsopaka (BPHS 7.17-25, Santhanam 1984) --------------------------------------------
# Full strength of each varga in each scheme; each scheme sums to 20.
VIMSOPAKA_SCHEMES = {
    "shadvarga": {"D1": 6, "D2": 2, "D3": 4, "D9": 5, "D12": 2, "D30": 1},
    "saptavarga": {"D1": 5, "D2": 2, "D3": 3, "D7": 2.5, "D9": 4.5, "D12": 2, "D30": 1},
    "dasavarga": {"D1": 3, "D2": 1.5, "D3": 1.5, "D7": 1.5, "D9": 1.5, "D10": 1.5, "D12": 1.5,
                  "D16": 1.5, "D30": 1.5, "D60": 5},
    "shodasavarga": {"D1": 3.5, "D2": 1, "D3": 1, "D4": 0.5, "D7": 0.5, "D9": 3, "D10": 0.5,
                     "D12": 0.5, "D16": 2, "D20": 0.5, "D24": 0.5, "D27": 0.5, "D30": 1,
                     "D40": 0.5, "D45": 0.5, "D60": 4},
}
# Varga Viswa (7.21-25): own 20, extreme friend 18, friend 15, equal 10, enemy 7, sworn
# enemy 5, by the five-fold compound relation with the varga sign's lord (temporal half
# from D1). A moolatrikona sign is an own sign. 7.21-25 gives no separate value for
# exaltation (7.9-12 speaks of full strength in exaltation for a different, rule-of-three
# reckoning), so an exalted planet is scored by its relation to the sign's lord.
VARGA_VISWA = {"own": 20, "great_friend": 18, "friend": 15, "neutral": 10, "enemy": 7,
               "great_enemy": 5}
# 7.25: below 5 not capable of good results, 5-10 some good, 10-15 mediocre, above 15 fully.
def vimsopaka_label(score: float) -> str:
    return "weak" if score < 5 else "some" if score < 10 else "mediocre" if score <= 15 else "full"

# --- KP vote v2: matter and denial houses per area (SPEC Layer 5, "Varga term and KP vote") -
# A cusp sub-lord promises the area when its significations meet the matter houses M and not
# the denial houses N. Source: K.S. Krishnamurti, KP Readers (house groupings per matter);
# checked: false — not yet read in a named edition. Where N is the 12th from each house of M
# it is Krishnamurti's own principle that the 12th to a house denies it. The 4th cusp is read
# twice: for mother and home (property) and for the mind (peace of mind). Occupation is
# counted in the KP houses (Placidus cusps, Meta.kp_house_system); ownership by sign.
KP_MATTER_SOURCE = {"text": "KP Readers", "edition": "K.S. Krishnamurti", "checked": False}
KP_MATTER = {
    "personality": {"cusp": 1, "matter": [1, 5, 9, 11], "denial": [6, 8, 12]},
    "mother_home": {"cusp": 4, "matter": [4, 11, 12], "denial": [3, 5, 10]},    # property acquired / sold
    "children": {"cusp": 5, "matter": [2, 5, 11], "denial": [1, 4, 10]},
    "health": {"cusp": 6, "matter": [1, 5, 11], "denial": [6, 8, 12]},          # recovery / disease
    "marriage": {"cusp": 7, "matter": [2, 7, 11], "denial": [1, 6, 10]},
    "career": {"cusp": 10, "matter": [2, 6, 10, 11], "denial": [1, 5, 9]},
    "mind": {"cusp": 4, "matter": [4, 11], "denial": [6, 8, 12]},               # peace of mind
}
