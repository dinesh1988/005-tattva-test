"""
Planetary Dignity Module

Calculates the positional strength (dignity) of planets:
  - Exaltation (Uccha) — sign and exact degree
  - Debilitation (Neecha) — sign and exact degree
  - Moolatrikona — prescribed strong-zone within a sign
  - Own Sign (Swa) — planet in its own domicile
  - Combined dignity grade

Ported from: Library/Logic/Calculate/Core.cs
  - IsPlanetExaltedSign()
  - IsPlanetExaltedDegree()
  - IsPlanetDebilitated()
  - IsPlanetInMoolatrikona()
"""

from typing import Optional
from .consts import Planet
from .calculate import get_planet_longitude
from .time import AstroTime
from .rasi import get_rasi

# ==================== SIGN NUMBER HELPERS ====================
# Aries=1, Taurus=2, ... Pisces=12

_SIGN_NAME_TO_NUM = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
    "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
    "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12,
}

def _sign_num(name: str) -> int:
    return _SIGN_NAME_TO_NUM[name]

# ==================== EXALTATION TABLE ====================
# (exaltation_sign_num, exact_degree_within_sign)
# Source: B.V. Raman's Hindu Predictive Astrology, standard Vedic tables
# Confirmed against Library/Logic/Calculate/Core.cs IsPlanetExaltedSign / IsPlanetExaltedDegree

EXALTATION_POINTS: dict[Planet, tuple[int, float]] = {
    Planet.Sun:     (_sign_num("Aries"),       10.0),
    Planet.Moon:    (_sign_num("Taurus"),        3.0),
    Planet.Mars:    (_sign_num("Capricorn"),     28.0),
    Planet.Mercury: (_sign_num("Virgo"),         15.0),
    Planet.Jupiter: (_sign_num("Cancer"),         5.0),
    Planet.Venus:   (_sign_num("Pisces"),        27.0),
    Planet.Saturn:  (_sign_num("Libra"),         20.0),
    Planet.Rahu:    (_sign_num("Taurus"),         1.0),  # whole-sign exaltation
    Planet.Ketu:    (_sign_num("Scorpio"),         1.0), # whole-sign exaltation
}

# Debilitation = opposite sign (sign_num + 6, wrapping 1-12), same degree
def _debilitation_sign(planet: Planet) -> int:
    exalt_sign, _ = EXALTATION_POINTS[planet]
    return ((exalt_sign - 1 + 6) % 12) + 1

# ==================== OWN SIGN TABLE ====================
# Each planet may own one or two signs

_OWN_SIGNS: dict[Planet, list[int]] = {
    Planet.Sun:     [_sign_num("Leo")],
    Planet.Moon:    [_sign_num("Cancer")],
    Planet.Mars:    [_sign_num("Aries"), _sign_num("Scorpio")],
    Planet.Mercury: [_sign_num("Gemini"), _sign_num("Virgo")],
    Planet.Jupiter: [_sign_num("Sagittarius"), _sign_num("Pisces")],
    Planet.Venus:   [_sign_num("Taurus"), _sign_num("Libra")],
    Planet.Saturn:  [_sign_num("Capricorn"), _sign_num("Aquarius")],
    Planet.Rahu:    [],  # no own sign
    Planet.Ketu:    [],  # no own sign
}

# ==================== MOOLATRIKONA TABLE ====================
# (sign_num, start_degree_in_sign, end_degree_in_sign)
# Confirmed from Core.cs lines 1269-1380

MOOLATRIKONA_ZONES: dict[Planet, tuple[int, float, float]] = {
    Planet.Sun:     (_sign_num("Leo"),         0.0,  20.0),
    Planet.Moon:    (_sign_num("Taurus"),       4.0,  30.0),
    Planet.Mars:    (_sign_num("Aries"),        0.0,  18.0),
    Planet.Mercury: (_sign_num("Virgo"),       16.0,  20.0),
    Planet.Jupiter: (_sign_num("Sagittarius"),  0.0,  13.0),
    Planet.Venus:   (_sign_num("Libra"),        0.0,  10.0),
    Planet.Saturn:  (_sign_num("Aquarius"),     0.0,  20.0),
}
# Rahu and Ketu have no moolatrikona zone

# ==================== CORE FUNCTIONS ====================

def _get_sign_and_degree(planet: Planet, time: AstroTime) -> tuple[int, float]:
    """Returns (sign_num 1-12, degree_within_sign 0-30)."""
    long = get_planet_longitude(planet, time)
    _, sign_num = get_rasi(long)
    degree_in_sign = long % 30.0
    return sign_num, degree_in_sign


def is_planet_exalted_sign(planet: Planet, time: AstroTime) -> bool:
    """
    Returns True if the planet is in its exaltation sign (Uccha Rasi).
    Ported from Core.cs IsPlanetExaltedSign().
    """
    if planet not in EXALTATION_POINTS:
        return False
    exalt_sign, _ = EXALTATION_POINTS[planet]
    sign_num, _ = _get_sign_and_degree(planet, time)
    return sign_num == exalt_sign


def is_planet_exalted_degree(planet: Planet, time: AstroTime, orb: float = 1.0) -> bool:
    """
    Returns True if the planet is within `orb` degrees of its exact exaltation point.
    Ported from Core.cs IsPlanetExaltedDegree().
    """
    if planet not in EXALTATION_POINTS:
        return False
    exalt_sign, exalt_deg = EXALTATION_POINTS[planet]
    sign_num, deg_in_sign = _get_sign_and_degree(planet, time)
    if sign_num != exalt_sign:
        return False
    return abs(deg_in_sign - exalt_deg) <= orb


def is_planet_debilitated(planet: Planet, time: AstroTime) -> bool:
    """
    Returns True if the planet is in its debilitation sign (Neecha Rasi).
    Ported from Core.cs IsPlanetDebilitated().
    """
    if planet not in EXALTATION_POINTS:
        return False
    debit_sign = _debilitation_sign(planet)
    sign_num, _ = _get_sign_and_degree(planet, time)
    return sign_num == debit_sign


def is_planet_debilitated_degree(planet: Planet, time: AstroTime, orb: float = 1.0) -> bool:
    """
    Returns True if the planet is within `orb` degrees of its exact debilitation point
    (same degree as exaltation, but in the opposite sign).
    """
    if planet not in EXALTATION_POINTS:
        return False
    _, exact_deg = EXALTATION_POINTS[planet]
    debit_sign = _debilitation_sign(planet)
    sign_num, deg_in_sign = _get_sign_and_degree(planet, time)
    if sign_num != debit_sign:
        return False
    return abs(deg_in_sign - exact_deg) <= orb


def is_planet_in_own_sign(planet: Planet, time: AstroTime) -> bool:
    """Returns True if the planet occupies one of its own signs (Swa Rasi)."""
    own_signs = _OWN_SIGNS.get(planet, [])
    if not own_signs:
        return False
    sign_num, _ = _get_sign_and_degree(planet, time)
    return sign_num in own_signs


def is_planet_in_moolatrikona(planet: Planet, time: AstroTime) -> bool:
    """
    Returns True if the planet is within its Moolatrikona zone.
    Ported from Core.cs (Moolatrikona check logic, lines 1269-1380).
    """
    if planet not in MOOLATRIKONA_ZONES:
        return False
    mt_sign, mt_start, mt_end = MOOLATRIKONA_ZONES[planet]
    sign_num, deg_in_sign = _get_sign_and_degree(planet, time)
    if sign_num != mt_sign:
        return False
    return mt_start <= deg_in_sign <= mt_end


# ==================== COMBINED DIGNITY ====================

# Ordered from strongest to weakest
_DIGNITY_LEVELS = [
    "ExaltedDegree",    # within orb of exact exaltation point
    "Exalted",          # in exaltation sign
    "OwnSign",          # in own domicile
    "Moolatrikona",     # in moolatrikona zone
    "Neutral",          # none of the above, not debilitated
    "Debilitated",      # in debilitation sign
    "DebilitatedDegree",# within orb of exact debilitation point
]


def get_planet_dignity(planet: Planet, time: AstroTime, orb: float = 1.0) -> str:
    """
    Returns the dignity level of a planet at the given time.

    Priority (strongest → weakest):
      ExaltedDegree → Exalted → OwnSign → Moolatrikona → Neutral → Debilitated → DebilitatedDegree

    Note: OwnSign and Moolatrikona can overlap — OwnSign wins in that case because
    most authorities treat own sign as stronger than moolatrikona for non-Sun planets.
    Exception: Sun's Moolatrikona is Leo (its own sign), degrees 0-20°; the rest is OwnSign.
    This is handled by checking Moolatrikona after OwnSign overlap resolution.
    """
    # Exaltation checks first
    if is_planet_exalted_degree(planet, time, orb):
        return "ExaltedDegree"
    if is_planet_exalted_sign(planet, time):
        return "Exalted"
    # Debilitation checks
    if is_planet_debilitated_degree(planet, time, orb):
        return "DebilitatedDegree"
    if is_planet_debilitated(planet, time):
        return "Debilitated"
    # Own sign and moolatrikona
    in_own = is_planet_in_own_sign(planet, time)
    in_mt = is_planet_in_moolatrikona(planet, time)
    if in_own and in_mt:
        # When moolatrikona overlaps own sign, moolatrikona takes precedence
        # (classical rule: Sun in Leo 0-20° is MT, 20-30° is OwnSign)
        return "Moolatrikona"
    if in_mt:
        return "Moolatrikona"
    if in_own:
        return "OwnSign"
    return "Neutral"


def get_dignity_score(planet: Planet, time: AstroTime, orb: float = 1.0) -> int:
    """
    Returns a numeric dignity score for easy comparison.
    Higher is stronger.
      ExaltedDegree = 7, Exalted = 6, OwnSign = 5, Moolatrikona = 4,
      Neutral = 3, Debilitated = 2, DebilitatedDegree = 1
    """
    _SCORES = {
        "ExaltedDegree": 7,
        "Exalted": 6,
        "OwnSign": 5,
        "Moolatrikona": 4,
        "Neutral": 3,
        "Debilitated": 2,
        "DebilitatedDegree": 1,
    }
    return _SCORES[get_planet_dignity(planet, time, orb)]


def get_all_planet_dignities(time: AstroTime) -> dict:
    """
    Returns dignity for all 9 planets at the given time.
    {'Sun': 'Exalted', 'Moon': 'Neutral', ...}
    """
    all_planets = [
        Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
        Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu
    ]
    return {p.name: get_planet_dignity(p, time) for p in all_planets}
