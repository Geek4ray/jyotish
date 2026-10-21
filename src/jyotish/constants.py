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
# Special taras by absolute count from Janma. Sources differ on Jati/Desha at 26/27;
# this follows the Brihat Samhita ordering and is a setting.
SPECIAL_TARAS = {1: "janma", 10: "karma", 16: "sanghatika", 18: "samudaya", 19: "adhana",
                 23: "vinasha", 25: "manasa", 26: "jati", 27: "desha"}

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
