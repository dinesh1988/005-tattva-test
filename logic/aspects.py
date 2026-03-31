"""
Planet Aspects (Graha Drishti) Module

Implements the special aspect rules for planets in Vedic astrology.

All planets aspect the 7th sign from their position (full sight).
Special additional aspects:
  - Saturn: 3rd and 10th signs
  - Jupiter: 5th and 9th signs
  - Mars: 4th and 8th signs

Ported from: Library/Logic/Calculate/Core.cs
  - SignsPlanetIsAspecting()
  - PlanetsInAspect()
  - PlanetsAspectingPlanet()
  - HousesInAspect()

Reference: Hindu Predictive Astrology, B.V. Raman
"""

from typing import List
from .consts import Planet
from .calculate import get_planet_longitude
from .time import AstroTime

ALL_9_PLANETS = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                 Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]

RASI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def _sign_num(longitude: float) -> int:
    """Convert 0-360 longitude to sign number 1-12."""
    return int(longitude / 30) + 1


def _sign_counted_from(base_sign: int, count: int) -> int:
    """1-indexed sign counting with wrap-around 1-12."""
    return ((base_sign - 1 + count - 1) % 12) + 1


def get_signs_planet_is_aspecting(planet: Planet, time: AstroTime) -> List[int]:
    """
    Get list of sign numbers aspected by the given planet.

    All planets aspect the 7th sign from their location.
    Special aspects:
      Saturn  → 3rd and 10th
      Jupiter → 5th and 9th
      Mars    → 4th and 8th

    Returns list of sign numbers (1=Aries ... 12=Pisces).
    """
    long = get_planet_longitude(planet, time)
    planet_sign = _sign_num(long)

    aspected = []

    if planet == Planet.Saturn:
        aspected.append(_sign_counted_from(planet_sign, 3))
        aspected.append(_sign_counted_from(planet_sign, 10))

    if planet == Planet.Jupiter:
        aspected.append(_sign_counted_from(planet_sign, 5))
        aspected.append(_sign_counted_from(planet_sign, 9))

    if planet == Planet.Mars:
        aspected.append(_sign_counted_from(planet_sign, 4))
        aspected.append(_sign_counted_from(planet_sign, 8))

    # All planets aspect 7th
    aspected.append(_sign_counted_from(planet_sign, 7))

    return aspected


def is_planet_aspecting_sign(planet: Planet, sign_num: int, time: AstroTime) -> bool:
    """Check if a planet is aspecting a specific sign number (1-12)."""
    return sign_num in get_signs_planet_is_aspecting(planet, time)


def is_planet_aspecting_planet(transmitter: Planet, receiver: Planet, time: AstroTime) -> bool:
    """
    Check if `transmitter` planet is aspecting the sign occupied by `receiver` planet.
    """
    receiver_long = get_planet_longitude(receiver, time)
    receiver_sign = _sign_num(receiver_long)
    return is_planet_aspecting_sign(transmitter, receiver_sign, time)


def get_planets_in_aspect(planet: Planet, time: AstroTime) -> List[Planet]:
    """
    Get all other planets that `planet` is transmitting an aspect to.
    Returns planets whose signs are aspected by this planet.
    """
    aspected_signs = set(get_signs_planet_is_aspecting(planet, time))
    result = []
    for other in ALL_9_PLANETS:
        if other == planet:
            continue
        other_long = get_planet_longitude(other, time)
        other_sign = _sign_num(other_long)
        if other_sign in aspected_signs:
            result.append(other)
    return result


def get_planets_aspecting_planet(receiving_planet: Planet, time: AstroTime) -> List[Planet]:
    """
    Get all planets that are transmitting an aspect to `receiving_planet`.
    """
    receiver_long = get_planet_longitude(receiving_planet, time)
    receiver_sign = _sign_num(receiver_long)

    result = []
    for other in ALL_9_PLANETS:
        if other == receiving_planet:
            continue
        if is_planet_aspecting_sign(other, receiver_sign, time):
            result.append(other)
    return result


def get_planets_aspecting_sign(sign_num: int, time: AstroTime) -> List[Planet]:
    """
    Get all planets aspecting a given sign number (1-12).
    """
    result = []
    for planet in ALL_9_PLANETS:
        if is_planet_aspecting_sign(planet, sign_num, time):
            result.append(planet)
    return result


def get_full_aspect_grid(time: AstroTime) -> dict:
    """
    Build a full 9x9 aspect matrix.

    Returns dict: {transmitter_name: {receiver_name: bool}}
    """
    result = {}
    for transmitter in ALL_9_PLANETS:
        row = {}
        for receiver in ALL_9_PLANETS:
            if transmitter == receiver:
                row[receiver.name] = False
            else:
                row[receiver.name] = is_planet_aspecting_planet(transmitter, receiver, time)
        result[transmitter.name] = row
    return result
