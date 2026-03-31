"""
Planet Relationship Module

Implements permanent (Naisargika), temporary (Tatkalika), and combined
planet-to-planet relationships as per Hindu Predictive Astrology (B.V. Raman, pg. 21).

Ported from: Library/Logic/Calculate/Core.cs
  - PlanetPermanentRelationshipWithPlanet()
  - PlanetTemporaryRelationshipWithPlanet()
  - PlanetTemporaryFriendList()
  - PlanetCombinedRelationshipWithPlanet()
  - PlanetRelationshipWithSign()
"""

from typing import List, Optional
from .consts import Planet
from .calculate import get_planet_longitude
from .time import AstroTime

# ==================== NATURAL (PERMANENT) RELATIONSHIPS ====================
# Source: Hindu Predictive Astrology by B.V. Raman, pg. 21
# Rahu and Ketu are excluded — no permanent relationship defined by Raman

_NATURAL_FRIENDS: dict[Planet, list[Planet]] = {
    Planet.Sun:     [Planet.Moon, Planet.Mars, Planet.Jupiter],
    Planet.Moon:    [Planet.Sun, Planet.Mercury],
    Planet.Mars:    [Planet.Sun, Planet.Moon, Planet.Jupiter],
    Planet.Mercury: [Planet.Sun, Planet.Venus],
    Planet.Jupiter: [Planet.Sun, Planet.Moon, Planet.Mars],
    Planet.Venus:   [Planet.Mercury, Planet.Saturn],
    Planet.Saturn:  [Planet.Mercury, Planet.Venus],
}

_NATURAL_ENEMIES: dict[Planet, list[Planet]] = {
    Planet.Sun:     [Planet.Saturn, Planet.Venus],
    Planet.Moon:    [],
    Planet.Mars:    [Planet.Mercury],
    Planet.Mercury: [Planet.Moon],
    Planet.Jupiter: [Planet.Mercury, Planet.Venus],
    Planet.Venus:   [Planet.Sun, Planet.Moon],
    Planet.Saturn:  [Planet.Sun, Planet.Moon, Planet.Mars],
}

# Neutral = not friend and not enemy (derived automatically)
_SEVEN_PLANETS = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]

# Sign lords for planet-to-sign relationship
# Index = sign number 1-12 (Aries=1 ... Pisces=12)
_SIGN_LORDS: dict[int, Planet] = {
    1:  Planet.Mars,    # Aries
    2:  Planet.Venus,   # Taurus
    3:  Planet.Mercury, # Gemini
    4:  Planet.Moon,    # Cancer
    5:  Planet.Sun,     # Leo
    6:  Planet.Mercury, # Virgo
    7:  Planet.Venus,   # Libra
    8:  Planet.Mars,    # Scorpio
    9:  Planet.Jupiter, # Sagittarius
    10: Planet.Saturn,  # Capricorn
    11: Planet.Saturn,  # Aquarius
    12: Planet.Jupiter, # Pisces
}


def get_natural_relationship(main_planet: Planet, secondary_planet: Planet) -> str:
    """
    Get the permanent (Naisargika) relationship between two planets.

    Returns one of: 'Friend', 'Enemy', 'Neutral', 'SamePlanet', 'Unknown'
    Rahu/Ketu — no permanent relationship defined, returns 'Unknown'.
    """
    if main_planet == secondary_planet:
        return "SamePlanet"

    # Rahu/Ketu excluded
    if main_planet in (Planet.Rahu, Planet.Ketu) or secondary_planet in (Planet.Rahu, Planet.Ketu):
        return "Unknown"

    friends = _NATURAL_FRIENDS.get(main_planet, [])
    if secondary_planet in friends:
        return "Friend"

    enemies = _NATURAL_ENEMIES.get(main_planet, [])
    if secondary_planet in enemies:
        return "Enemy"

    return "Neutral"


# ==================== TEMPORARY (TATKALIKA) RELATIONSHIPS ====================

def _sign_num(longitude: float) -> int:
    """Convert absolute longitude (0-360) to sign number 1-12."""
    return int(longitude / 30) + 1


def _sign_counted_from(base_sign: int, count: int) -> int:
    """
    Get the sign number that is `count` signs away from `base_sign` (1-indexed, wraps 1-12).
    Counting is inclusive: count=1 means the sign itself.
    """
    return ((base_sign - 1 + count - 1) % 12) + 1


def get_temporary_friends(planet: Planet, time: AstroTime) -> List[Planet]:
    """
    Get list of planets that are temporary (Tatkalika) friends of `planet` at the given time.

    Rule: Planets in the 2nd, 3rd, 4th, 10th, 11th, and 12th signs from the
    planet's sign become its temporary friends. All others are temporary enemies.

    Returns:
        List of Planet values that are temporary friends
    """
    # Get sign of main planet
    main_long = get_planet_longitude(planet, time)
    main_sign = _sign_num(main_long)

    # Friendly signs: 2, 3, 4, 10, 11, 12 counted from main planet sign
    friendly_sign_nums = {
        _sign_counted_from(main_sign, 2),
        _sign_counted_from(main_sign, 3),
        _sign_counted_from(main_sign, 4),
        _sign_counted_from(main_sign, 10),
        _sign_counted_from(main_sign, 11),
        _sign_counted_from(main_sign, 12),
    }

    friends = []
    for other in _SEVEN_PLANETS:
        if other == planet:
            continue
        other_long = get_planet_longitude(other, time)
        other_sign = _sign_num(other_long)
        if other_sign in friendly_sign_nums:
            friends.append(other)

    return friends


def get_temporary_relationship(main_planet: Planet, secondary_planet: Planet,
                                time: AstroTime) -> str:
    """
    Get the temporary (Tatkalika) relationship between two planets at a given time.

    Returns 'Friend', 'Enemy', or 'SamePlanet'.
    """
    if main_planet == secondary_planet:
        return "SamePlanet"

    friends = get_temporary_friends(main_planet, time)
    if secondary_planet in friends:
        return "Friend"
    return "Enemy"


# ==================== COMBINED RELATIONSHIPS ====================

def get_combined_relationship(main_planet: Planet, secondary_planet: Planet,
                               time: AstroTime) -> str:
    """
    Get the combined (Tatkalika + Naisargika) relationship between two planets.

    Combination rules (Panchadhā Maitri):
      Temp Friend  + Perm Friend  = BestFriend   (Adhi Mitra)
      Temp Friend  + Perm Enemy   = Neutral       (Sama)
      Temp Friend  + Perm Neutral = Friend        (Mitra)
      Temp Enemy   + Perm Enemy   = BitterEnemy   (Adhi Satru)
      Temp Enemy   + Perm Friend  = Neutral       (Sama)
      Temp Enemy   + Perm Neutral = Enemy         (Satru)

    Returns one of: 'BestFriend', 'Friend', 'Neutral', 'Enemy', 'BitterEnemy',
                    'SamePlanet', 'Unknown'
    """
    if main_planet == secondary_planet:
        return "SamePlanet"

    # Rahu/Ketu — no permanent relationship, use only temporary
    if main_planet in (Planet.Rahu, Planet.Ketu) or secondary_planet in (Planet.Rahu, Planet.Ketu):
        return get_temporary_relationship(main_planet, secondary_planet, time)

    perm = get_natural_relationship(main_planet, secondary_planet)
    temp = get_temporary_relationship(main_planet, secondary_planet, time)

    if temp == "Friend" and perm == "Friend":
        return "BestFriend"
    if temp == "Friend" and perm == "Enemy":
        return "Neutral"
    if temp == "Friend" and perm == "Neutral":
        return "Friend"
    if temp == "Enemy" and perm == "Enemy":
        return "BitterEnemy"
    if temp == "Enemy" and perm == "Friend":
        return "Neutral"
    if temp == "Enemy" and perm == "Neutral":
        return "Enemy"

    return "Unknown"


# ==================== PLANET-TO-SIGN RELATIONSHIP ====================

def get_planet_sign_relationship(planet: Planet, sign_num: int, time: AstroTime) -> str:
    """
    Get a planet's relationship with a sign based on its relationship with the sign's lord.

    Note: Moolatrikona, Exaltation, Debilitation are handled in dignity.py.
    Rahu/Ketu return 'Unknown'.

    sign_num: 1=Aries, 2=Taurus, ... 12=Pisces

    Returns one of: 'OwnSign', 'BestFriendSign', 'FriendSign', 'NeutralSign',
                    'EnemySign', 'BitterEnemySign', 'Unknown'
    """
    if planet in (Planet.Rahu, Planet.Ketu):
        return "Unknown"

    lord = _SIGN_LORDS.get(sign_num)
    if lord is None:
        return "Unknown"

    if planet == lord:
        return "OwnSign"

    combined = get_combined_relationship(planet, lord, time)
    mapping = {
        "BestFriend": "BestFriendSign",
        "Friend":     "FriendSign",
        "Neutral":    "NeutralSign",
        "Enemy":      "EnemySign",
        "BitterEnemy": "BitterEnemySign",
    }
    return mapping.get(combined, "Unknown")


def get_all_planet_relationships(time: AstroTime) -> dict:
    """
    Compute the full combined relationship grid for all 7 planets.

    Returns dict: {planet_name: {other_planet_name: combined_relationship_str}}
    """
    result = {}
    for p in _SEVEN_PLANETS:
        row = {}
        for q in _SEVEN_PLANETS:
            if p == q:
                row[q.name] = "SamePlanet"
            else:
                row[q.name] = get_combined_relationship(p, q, time)
        result[p.name] = row
    return result
