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
