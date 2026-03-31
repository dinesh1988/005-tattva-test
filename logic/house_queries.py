"""
House Queries Module

Determines which sign / house each planet occupies, and provides
fast lookup for "which planets are in house X?" queries.

In Vedic astrology (whole-sign house system) the Lagna sign IS house 1,
the next sign is house 2, etc.  All calculations use Nirayana longitudes.

Ported from: Library/Logic/Calculate/Core.cs
  - PlanetSignNum()
  - HouseNumOfPlanet()        (PlanetHouseNum in some versions)
  - PlanetsInSign()
  - PlanetsInHouse()
  - AllPlanetHouseNums()
"""

from typing import List, Optional
from .consts import Planet
from .calculate import get_planet_longitude, get_lagnam
from .time import AstroTime
from .rasi import get_rasi

# ==================== PLANET LISTS ====================

ALL_9_PLANETS: List[Planet] = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu,
]

ALL_7_PLANETS: List[Planet] = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn,
]


# ==================== SIGN QUERIES ====================

def get_planet_sign_num(planet: Planet, time: AstroTime) -> int:
    """
    Returns the sign number (1-12, Aries=1) occupied by the planet.
    Ported from Core.cs PlanetSignNum().
    """
    long = get_planet_longitude(planet, time)
    _, sign_num = get_rasi(long)
    return sign_num


def get_planet_sign_name(planet: Planet, time: AstroTime) -> str:
    """Returns the sign name (e.g. 'Aries (Mesha)') occupied by the planet."""
    long = get_planet_longitude(planet, time)
    sign_name, _ = get_rasi(long)
    return sign_name


def get_planets_in_sign(sign_num: int, time: AstroTime,
                        planets: Optional[List[Planet]] = None) -> List[Planet]:
    """
    Returns a list of planets currently in the given sign (1-12).
    Ported from Core.cs PlanetsInSign().

    Args:
        sign_num: Target sign 1-12
        time: Chart time
        planets: Planets to check (defaults to all 9)
    """
    if planets is None:
        planets = ALL_9_PLANETS
    return [p for p in planets if get_planet_sign_num(p, time) == sign_num]


# ==================== HOUSE QUERIES ====================

def get_lagna_sign_num(time: AstroTime) -> int:
    """Returns the Lagna (Ascendant) sign number, 1-12."""
    lagna_long = get_lagnam(time)
    _, sign_num = get_rasi(lagna_long)
    return sign_num


def get_planet_house(planet: Planet, time: AstroTime) -> int:
    """
    Returns the whole-sign house number (1-12) the planet occupies
    relative to the Lagna.  House 1 = Lagna sign, House 2 = next sign, etc.

    Ported from Core.cs HouseNumOfPlanet().
    """
    lagna_sign = get_lagna_sign_num(time)
    planet_sign = get_planet_sign_num(planet, time)
    diff = (planet_sign - lagna_sign) % 12
    return diff + 1  # House 1 = Lagna, thus +1


def get_planets_in_house(house_num: int, time: AstroTime,
                          planets: Optional[List[Planet]] = None) -> List[Planet]:
    """
    Returns a list of planets in the specified whole-sign house (1-12).
    Ported from Core.cs PlanetsInHouse().

    Args:
        house_num: House 1-12 (1 = Lagna)
        time: Chart time
        planets: Planets to check (defaults to all 9)
    """
    if planets is None:
        planets = ALL_9_PLANETS
    return [p for p in planets if get_planet_house(p, time) == house_num]


def get_house_sign_num(house_num: int, time: AstroTime) -> int:
    """
    Returns which sign number (1-12) corresponds to the given house.
    In the whole-sign system: house_sign = (lagna_sign + house_num - 2) % 12 + 1
    """
    lagna_sign = get_lagna_sign_num(time)
    return ((lagna_sign - 1 + house_num - 1) % 12) + 1


# ==================== BULK QUERIES ====================

def get_all_planet_houses(time: AstroTime,
                           planets: Optional[List[Planet]] = None) -> dict:
    """
    Returns a dict mapping each planet to its house number.
    {'Sun': 10, 'Moon': 4, 'Mars': 7, ...}

    Ported from Core.cs AllPlanetHouseNums() concept.
    """
    if planets is None:
        planets = ALL_9_PLANETS
    return {p.name: get_planet_house(p, time) for p in planets}


def get_all_planet_signs(time: AstroTime,
                          planets: Optional[List[Planet]] = None) -> dict:
    """
    Returns a dict mapping each planet to its sign number (1-12).
    {'Sun': 5, 'Moon': 2, ...}
    """
    if planets is None:
        planets = ALL_9_PLANETS
    return {p.name: get_planet_sign_num(p, time) for p in planets}


def get_house_occupancy_map(time: AstroTime,
                             planets: Optional[List[Planet]] = None) -> dict:
    """
    Returns a dict mapping each house number (1-12) to the list of planet names
    occupying it.  Empty houses map to an empty list.
    {1: ['Sun'], 2: [], ..., 10: ['Mars', 'Saturn'], ...}
    """
    if planets is None:
        planets = ALL_9_PLANETS
    result: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p in planets:
        house = get_planet_house(p, time)
        result[house].append(p.name)
    return result
