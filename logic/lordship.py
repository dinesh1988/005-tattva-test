"""
House Lordship Calculator
Determines which planet rules which house based on birth chart.

In Vedic astrology, each zodiac sign has a ruling planet (lord).
Since houses occupy zodiac signs (determined by Lagna), we can find
the lord of any house by finding which sign that house occupies.
"""

from typing import Dict
from enum import IntEnum
from logic.consts import Planet
from logic.time import AstroTime
from logic.calculate import get_lagnam


class ZodiacSign(IntEnum):
    """Zodiac signs as indices (0-11)"""
    ARIES = 0
    TAURUS = 1
    GEMINI = 2
    CANCER = 3
    LEO = 4
    VIRGO = 5
    LIBRA = 6
    SCORPIO = 7
    SAGITTARIUS = 8
    CAPRICORN = 9
    AQUARIUS = 10
    PISCES = 11


# Zodiac sign to ruling planet mapping
# Based on traditional Vedic astrology
SIGN_LORDS = {
    ZodiacSign.ARIES: Planet.Mars,         # 0 -> Mars
    ZodiacSign.TAURUS: Planet.Venus,       # 1 -> Venus
    ZodiacSign.GEMINI: Planet.Mercury,     # 2 -> Mercury
    ZodiacSign.CANCER: Planet.Moon,        # 3 -> Moon
    ZodiacSign.LEO: Planet.Sun,            # 4 -> Sun
    ZodiacSign.VIRGO: Planet.Mercury,      # 5 -> Mercury
    ZodiacSign.LIBRA: Planet.Venus,        # 6 -> Venus
    ZodiacSign.SCORPIO: Planet.Mars,       # 7 -> Mars
    ZodiacSign.SAGITTARIUS: Planet.Jupiter,# 8 -> Jupiter
    ZodiacSign.CAPRICORN: Planet.Saturn,   # 9 -> Saturn
    ZodiacSign.AQUARIUS: Planet.Saturn,    # 10 -> Saturn
    ZodiacSign.PISCES: Planet.Jupiter,     # 11 -> Jupiter
}

# Reverse mapping: Planet to signs it rules
PLANET_RULERSHIPS = {
    Planet.Sun: [ZodiacSign.LEO],
    Planet.Moon: [ZodiacSign.CANCER],
    Planet.Mars: [ZodiacSign.ARIES, ZodiacSign.SCORPIO],
    Planet.Mercury: [ZodiacSign.GEMINI, ZodiacSign.VIRGO],
    Planet.Jupiter: [ZodiacSign.SAGITTARIUS, ZodiacSign.PISCES],
    Planet.Venus: [ZodiacSign.TAURUS, ZodiacSign.LIBRA],
    Planet.Saturn: [ZodiacSign.CAPRICORN, ZodiacSign.AQUARIUS],
}


def get_lord_of_sign(sign: int) -> Planet:
    """
    Get the ruling planet of a zodiac sign.
    
    Args:
        sign: Zodiac sign index (0-11)
        
    Returns:
        Planet enum representing the lord
        
    Example:
        >>> get_lord_of_sign(0)  # Aries
        <Planet.Mars: 4>
        >>> get_lord_of_sign(4)  # Leo
        <Planet.Sun: 0>
    """
    if sign < 0 or sign > 11:
        raise ValueError(f"Invalid sign index: {sign}. Must be 0-11.")
    
    return SIGN_LORDS[sign]


def get_lord_of_house(house_number: int, time: AstroTime) -> Planet:
    """
    Get the ruling planet (lord) of a house.
    
    The lord of a house is determined by:
    1. Find which zodiac sign that house occupies (based on Lagna)
    2. Find the ruling planet of that sign
    
    Args:
        house_number: House number (1-12)
        time: Birth time
        
    Returns:
        Planet that rules the house
        
    Example:
        If Lagna (House 1) is in Aries (sign 0), then lord of House 1 is Mars
        House 2 would be in Taurus (sign 1), so lord of House 2 is Venus
        
    Reference:
        BV Raman - "Graha & Bhava Balas"
        The lord of a bhava (house) is the planet ruling the sign 
        in which the bhavamadhya (middle of house) falls.
    """
    if house_number < 1 or house_number > 12:
        raise ValueError(f"Invalid house number: {house_number}. Must be 1-12.")
    
    # Get Lagna sign (House 1 sign)
    lagna_longitude = get_lagnam(time)
    lagna_sign = int(lagna_longitude / 30) % 12
    
    # Calculate which sign the requested house occupies
    # Houses follow signs sequentially from Lagna
    house_sign = (lagna_sign + house_number - 1) % 12
    
    # Get the lord of that sign
    return get_lord_of_sign(house_sign)


def get_all_house_lords(time: AstroTime) -> Dict[int, Planet]:
    """
    Get lords of all 12 houses for a given birth time.
    
    Args:
        time: Birth time
        
    Returns:
        Dictionary mapping house number (1-12) to ruling planet
        
    Example:
        {
            1: Planet.Mars,      # Lagna in Aries
            2: Planet.Venus,     # 2nd house in Taurus
            3: Planet.Mercury,   # 3rd house in Gemini
            ...
        }
    """
    lords = {}
    for house in range(1, 13):
        lords[house] = get_lord_of_house(house, time)
    return lords


def get_house_sign(house_number: int, time: AstroTime) -> int:
    """
    Get which zodiac sign a house occupies.
    
    Args:
        house_number: House number (1-12)
        time: Birth time
        
    Returns:
        Zodiac sign index (0-11)
    """
    if house_number < 1 or house_number > 12:
        raise ValueError(f"Invalid house number: {house_number}. Must be 1-12.")
    
    lagna_longitude = get_lagnam(time)
    lagna_sign = int(lagna_longitude / 30) % 12
    house_sign = (lagna_sign + house_number - 1) % 12
    
    return house_sign


def is_planet_house_lord(planet: Planet, house_number: int, time: AstroTime) -> bool:
    """
    Check if a planet is the lord of a specific house.
    
    Args:
        planet: Planet to check
        house_number: House number (1-12)
        time: Birth time
        
    Returns:
        True if planet is lord of the house, False otherwise
    """
    lord = get_lord_of_house(house_number, time)
    return lord == planet


def get_houses_ruled_by_planet(planet: Planet, time: AstroTime) -> list:
    """
    Get all houses ruled by a specific planet.
    
    Args:
        planet: Planet enum
        time: Birth time
        
    Returns:
        List of house numbers (1-12) ruled by the planet
        
    Example:
        If Mars rules Aries (sign 0) and Scorpio (sign 7),
        and Lagna is in Aries, then Mars rules:
        - House 1 (Aries)
        - House 8 (Scorpio, 8 signs from Aries)
    """
    ruled_houses = []
    for house in range(1, 13):
        if get_lord_of_house(house, time) == planet:
            ruled_houses.append(house)
    return ruled_houses


# Zodiac sign names for display
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


def get_sign_name(sign_index: int) -> str:
    """Get name of zodiac sign from index"""
    return SIGN_NAMES[sign_index]


def print_house_lordship_chart(time: AstroTime):
    """
    Print a formatted table showing house lordships.
    Useful for debugging and understanding a birth chart.
    """
    print("\n" + "="*60)
    print("HOUSE LORDSHIP CHART")
    print("="*60)
    
    lords = get_all_house_lords(time)
    
    print(f"\n{'House':<8} {'Sign':<15} {'Lord':<10}")
    print("-" * 60)
    
    for house in range(1, 13):
        sign = get_house_sign(house, time)
        sign_name = get_sign_name(sign)
        lord = lords[house]
        print(f"{house:<8} {sign_name:<15} {lord.name:<10}")
    
    print("="*60)
