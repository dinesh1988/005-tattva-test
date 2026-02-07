"""
Shadbala - Six-fold Planetary Strength Calculator
=================================================
Implements the classical Vedic astrology Shadbala system based on
Brihat Parashara Hora Shastra and Graha & Bhava Balas by B.V. Raman.

Shadbala (Six Sources of Strength):
1. Sthana Bala (Positional Strength)
2. Dig Bala (Directional Strength)
3. Kaala Bala (Temporal Strength)
4. Cheshta Bala (Motional Strength)
5. Naisargika Bala (Natural Strength)
6. Drik Bala (Aspectual Strength)

Unit: Shashtiamsa (1/60 of a Rupa)
60 Shashtiamsas = 1 Rupa

Reference: B.V. Raman's "Graha and Bhava Balas"
"""

import swisseph as swe
from datetime import datetime
import math
from typing import Dict, List, Tuple, Optional, Any, Union

# Planet constants
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
PLANET_IDS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mars': swe.MARS,
    'Mercury': swe.MERCURY,
    'Jupiter': swe.JUPITER,
    'Venus': swe.VENUS,
    'Saturn': swe.SATURN,
    'Rahu': swe.MEAN_NODE,  # Mean North Node
    'Ketu': swe.TRUE_NODE   # Will calculate as 180° from Rahu
}

# Sign names
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Exaltation degrees (deep exaltation point)
EXALTATION_DEGREES = {
    'Sun': 10,        # 10° Aries
    'Moon': 33,       # 3° Taurus
    'Mars': 298,      # 28° Capricorn
    'Mercury': 165,   # 15° Virgo
    'Jupiter': 95,    # 5° Cancer
    'Venus': 357,     # 27° Pisces
    'Saturn': 200     # 20° Libra
}

# Debilitation degrees (deep debilitation point = exaltation + 180°)
DEBILITATION_DEGREES = {
    'Sun': 190,       # 10° Libra
    'Moon': 213,      # 3° Scorpio
    'Mars': 118,      # 28° Cancer
    'Mercury': 345,   # 15° Pisces
    'Jupiter': 275,   # 5° Capricorn
    'Venus': 177,     # 27° Virgo
    'Saturn': 20      # 20° Aries
}

# Naisargika Bala (Natural Strength) - based on luminosity
# Sun (brightest) to Saturn (darkest)
NAISARGIKA_BALA = {
    'Sun': 60.00,
    'Moon': 51.43,
    'Venus': 42.86,
    'Jupiter': 34.29,
    'Mercury': 25.71,
    'Mars': 17.14,
    'Saturn': 8.57
}

# Dig Bala strong houses (10th = 0 for calculation)
# Planet gets full strength (60 shashtiamsas) when at strong point
# Zero strength at opposite house
DIG_BALA_STRONG_HOUSE = {
    'Sun': 10,      # 10th house (Zenith/MC)
    'Moon': 4,      # 4th house (Nadir/IC)
    'Mars': 10,     # 10th house
    'Mercury': 1,   # 1st house (Ascendant)
    'Jupiter': 1,   # 1st house
    'Venus': 4,     # 4th house
    'Saturn': 7     # 7th house (Descendant)
}

# Required minimum Shadbala Rupas for each planet to be considered strong
# Source: B.V. Raman's "Graha and Bhava Balas"
STRENGTH_REQUIREMENTS = {
    'Sun': 5.0,
    'Moon': 6.0,
    'Mars': 5.0,
    'Mercury': 7.0,
    'Jupiter': 6.5,
    'Venus': 5.5,
    'Saturn': 5.0
}

# Planet gender for Drekkana Bala
PLANET_GENDER = {
    'Sun': 'male',
    'Moon': 'female',
    'Mars': 'male',
    'Mercury': 'neutral',
    'Jupiter': 'male',
    'Venus': 'female',
    'Saturn': 'neutral'
}

# Weekday lords (0=Monday in Swiss Ephemeris week calculation)
WEEKDAY_LORDS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']

# Circulation times in years (for Cheshta Bala calculation)
CIRCULATION_TIMES = {
    'Saturn': 29.46,
    'Jupiter': 11.86,
    'Mars': 1.88,
    'Venus': 0.615,
    'Mercury': 0.24,
    'Sun': 1.0,
    'Moon': 0.0748  # ~27.3 days
}


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def get_planet_longitude(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """Get sidereal longitude of a planet."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    elif ayanamsa.upper() == 'KRISHNAMURTI':
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    planet_id = PLANET_IDS.get(planet)
    if planet_id is None:
        return 0.0
    
    # Special handling for Ketu
    if planet == 'Ketu':
        rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
        return (rahu_pos[0][0] + 180) % 360
    
    pos = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL)
    return pos[0][0]


def get_ascendant(jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> float:
    """Calculate sidereal ascendant longitude."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    houses = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    return houses[1][0]  # Ascendant


def get_house_cusps(jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> List[float]:
    """Get all 12 house cusps (Placidus system)."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    houses = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    return list(houses[0])  # 12 house cusps


def get_planet_house(planet_long: float, house_cusps: List[float]) -> int:
    """Determine which house a planet occupies based on cusps."""
    for i in range(12):
        cusp_start = house_cusps[i]
        cusp_end = house_cusps[(i + 1) % 12]
        
        if cusp_start < cusp_end:
            if cusp_start <= planet_long < cusp_end:
                return i + 1
        else:  # Wraps around 360°
            if planet_long >= cusp_start or planet_long < cusp_end:
                return i + 1
    return 1


def get_sign(longitude: float) -> int:
    """Get sign number (1-12) from longitude."""
    return int(longitude / 30) + 1


def get_sign_name(longitude: float) -> str:
    """Get sign name from longitude."""
    return SIGNS[int(longitude / 30)]


# =============================================================================
# 1. STHANA BALA (Positional Strength)
# =============================================================================

def get_ochcha_bala(planet: str, longitude: float) -> float:
    """
    Uchcha Bala (Exaltation Strength)
    
    The distance between the planet's longitude and its debilitation point,
    divided by 3, gives its exaltation strength.
    Maximum: 60 shashtiamsas (at exaltation point)
    Minimum: 0 shashtiamsas (at debilitation point)
    """
    if planet not in DEBILITATION_DEGREES:
        return 0.0
    
    debil_point = DEBILITATION_DEGREES[planet]
    
    # Distance from debilitation point
    distance = abs(longitude - debil_point)
    if distance > 180:
        distance = 360 - distance
    
    # Divide by 3 to get shashtiamsas (max 60)
    ochcha_bala = distance / 3.0
    
    return min(60.0, ochcha_bala)


def get_saptavargaja_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Saptavargaja Bala (Seven Division Strength)
    
    Strength from placement in 7 divisional charts:
    Rasi, Hora, Drekkana, Saptamsha, Navamsha, Dwadashamsha, Trimshamsha
    
    Points based on relationship with dispositor:
    - Own sign/Moolatrikona: 30 shashtiamsas
    - Great friend: 22.5 shashtiamsas
    - Friend: 15 shashtiamsas
    - Neutral: 7.5 shashtiamsas
    - Enemy: 3.75 shashtiamsas
    - Great enemy: 1.875 shashtiamsas
    """
    # Simplified implementation - checks Rasi position mainly
    # Full implementation would check all 7 vargas
    
    longitude = get_planet_longitude(planet, jd, ayanamsa)
    sign_num = get_sign(longitude)
    sign_name = SIGNS[sign_num - 1]
    
    # Own sign rulers
    own_signs = {
        'Sun': ['Leo'],
        'Moon': ['Cancer'],
        'Mars': ['Aries', 'Scorpio'],
        'Mercury': ['Gemini', 'Virgo'],
        'Jupiter': ['Sagittarius', 'Pisces'],
        'Venus': ['Taurus', 'Libra'],
        'Saturn': ['Capricorn', 'Aquarius']
    }
    
    # Moolatrikona signs
    moolatrikona = {
        'Sun': 'Leo',
        'Moon': 'Taurus',
        'Mars': 'Aries',
        'Mercury': 'Virgo',
        'Jupiter': 'Sagittarius',
        'Venus': 'Libra',
        'Saturn': 'Aquarius'
    }
    
    # Calculate base strength for Rasi
    base_points = 7.5  # Neutral
    
    if planet in own_signs and sign_name in own_signs[planet]:
        base_points = 30.0  # Own sign
    elif planet in moolatrikona and sign_name == moolatrikona[planet]:
        base_points = 30.0  # Moolatrikona
    
    # Multiply by 7 divisions factor (simplified - typically averages around 3-4x)
    # In full implementation, each varga is calculated separately
    saptavargaja = base_points * 4  # Simplified multiplier
    
    return min(180.0, saptavargaja)  # Max possible is 45 * 7 = 315, but typical max ~180


def get_ojayugmarasyamsa_bala(planet: str, longitude: float, navamsa_longitude: float) -> float:
    """
    Ojayugmarasyamsa Bala (Odd/Even Sign Strength)
    
    In odd Rasi and Navamsa: Sun, Mars, Jupiter, Mercury, Saturn get 15 shashtiamsas each
    In even Rasi and Navamsa: Moon, Venus get 15 shashtiamsas each
    Maximum: 30 shashtiamsas (15 from Rasi + 15 from Navamsa)
    """
    rasi_sign = get_sign(longitude)
    navamsa_sign = get_sign(navamsa_longitude)
    
    rasi_odd = rasi_sign % 2 == 1
    navamsa_odd = navamsa_sign % 2 == 1
    
    strength = 0.0
    
    # Male planets (odd signs give strength)
    if planet in ['Sun', 'Mars', 'Jupiter', 'Mercury', 'Saturn']:
        if rasi_odd:
            strength += 15.0
        if navamsa_odd:
            strength += 15.0
    # Female planets (even signs give strength)
    elif planet in ['Moon', 'Venus']:
        if not rasi_odd:
            strength += 15.0
        if not navamsa_odd:
            strength += 15.0
    
    return strength


def get_kendra_bala(house: int) -> float:
    """
    Kendradi Bala (Angular House Strength)
    
    Planets in Kendras (1,4,7,10): 60 shashtiamsas
    Planets in Panapara (2,5,8,11): 30 shashtiamsas
    Planets in Apoklima (3,6,9,12): 15 shashtiamsas
    """
    kendras = [1, 4, 7, 10]
    panaparas = [2, 5, 8, 11]
    apoklimas = [3, 6, 9, 12]
    
    if house in kendras:
        return 60.0
    elif house in panaparas:
        return 30.0
    elif house in apoklimas:
        return 15.0
    return 15.0


def get_drekkana_bala(planet: str, longitude: float) -> float:
    """
    Drekkana Bala (Decanate Strength)
    
    Based on planet gender and which third of sign (drekkana):
    - 1st drekkana (0°-10°): Male planets get 60 shashtiamsas
    - 2nd drekkana (10°-20°): Female planets get 60 shashtiamsas
    - 3rd drekkana (20°-30°): Neutral/hermaphrodite planets get 60 shashtiamsas
    """
    degree_in_sign = longitude % 30
    
    if degree_in_sign < 10:
        drekkana = 1  # First third
    elif degree_in_sign < 20:
        drekkana = 2  # Second third
    else:
        drekkana = 3  # Third third
    
    gender = PLANET_GENDER.get(planet, 'neutral')
    
    if drekkana == 1 and gender == 'male':
        return 60.0
    elif drekkana == 2 and gender == 'female':
        return 60.0
    elif drekkana == 3 and gender == 'neutral':
        return 60.0
    
    return 0.0


def get_sthana_bala(planet: str, jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, float]:
    """
    Calculate complete Sthana Bala (Positional Strength)
    
    Sthana Bala = Uchcha + Saptavargaja + Ojayugmarasyamsa + Kendra + Drekkana
    """
    longitude = get_planet_longitude(planet, jd, ayanamsa)
    house_cusps = get_house_cusps(jd, lat, lon, ayanamsa)
    house = get_planet_house(longitude, house_cusps)
    
    # Calculate Navamsa longitude for Ojayugmarasyamsa Bala
    navamsa_offset = (longitude % 30) * 12 / 30
    navamsa_longitude = (navamsa_offset * 30) % 360
    
    ochcha = get_ochcha_bala(planet, longitude)
    saptavargaja = get_saptavargaja_bala(planet, jd, ayanamsa)
    ojayugma = get_ojayugmarasyamsa_bala(planet, longitude, navamsa_longitude)
    kendra = get_kendra_bala(house)
    drekkana = get_drekkana_bala(planet, longitude)
    
    total = ochcha + saptavargaja + ojayugma + kendra + drekkana
    
    return {
        'ochcha_bala': round(ochcha, 2),
        'saptavargaja_bala': round(saptavargaja, 2),
        'ojayugmarasyamsa_bala': round(ojayugma, 2),
        'kendra_bala': round(kendra, 2),
        'drekkana_bala': round(drekkana, 2),
        'total': round(total, 2)
    }


# =============================================================================
# 2. DIG BALA (Directional Strength)
# =============================================================================

def get_dig_bala(planet: str, jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Dig Bala (Directional Strength)
    
    Jupiter and Mercury are strong in Lagna (1st house)
    Sun and Mars are strong in the 10th house
    Saturn is strong in the 7th house
    Moon and Venus are strong in the 4th house
    
    Maximum strength (60 shashtiamsas) at the strong house.
    Zero strength at the opposite house.
    """
    if planet not in DIG_BALA_STRONG_HOUSE:
        return 0.0
    
    longitude = get_planet_longitude(planet, jd, ayanamsa)
    house_cusps = get_house_cusps(jd, lat, lon, ayanamsa)
    ascendant = house_cusps[0]
    
    strong_house = DIG_BALA_STRONG_HOUSE[planet]
    
    # Calculate the longitude of strong house cusp
    if strong_house == 1:
        strong_point = ascendant
    elif strong_house == 4:
        strong_point = house_cusps[3]  # IC
    elif strong_house == 7:
        strong_point = house_cusps[6]  # Descendant
    elif strong_house == 10:
        strong_point = house_cusps[9]  # MC
    else:
        strong_point = house_cusps[strong_house - 1]
    
    # Weak point is opposite (180°)
    weak_point = (strong_point + 180) % 360
    
    # Distance from weak point
    distance = abs(longitude - weak_point)
    if distance > 180:
        distance = 360 - distance
    
    # Convert to shashtiamsas (divide by 3)
    dig_bala = distance / 3.0
    
    return min(60.0, round(dig_bala, 2))


# =============================================================================
# 3. KAALA BALA (Temporal Strength)
# =============================================================================

def get_nathonnatha_bala(planet: str, jd: float, lat: float, lon: float) -> float:
    """
    Nathonnatha Bala (Day/Night Strength)
    
    Midnight to midday: Sun, Jupiter, Venus gain strength (max 60 at noon)
    Midday to midnight: Moon, Mars, Saturn gain strength (max 60 at midnight)
    Mercury always gets 60 shashtiamsas
    """
    if planet == 'Mercury':
        return 60.0
    
    # Get local apparent time
    # Simplified: using hour angle from midnight
    ut_hour = (jd % 1) * 24
    
    # Convert to local time (approximate)
    local_hour = (ut_hour + lon / 15) % 24
    
    # Distance from midnight (0 or 24) or noon (12)
    if planet in ['Sun', 'Jupiter', 'Venus']:
        # Strong at noon (12), weak at midnight (0/24)
        distance_from_weak = abs(local_hour - 0) if local_hour <= 12 else abs(24 - local_hour)
        strength = (distance_from_weak / 12) * 60
    else:  # Moon, Mars, Saturn
        # Strong at midnight (0/24), weak at noon (12)
        distance_from_weak = abs(local_hour - 12)
        strength = (distance_from_weak / 12) * 60
    
    return min(60.0, round(strength, 2))


def get_paksha_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Paksha Bala (Lunar Phase Strength)
    
    Based on Moon's distance from Sun:
    - Shukla Paksha (waxing): Moon, Jupiter, Venus, Mercury gain strength
    - Krishna Paksha (waning): Sun, Mars, Saturn gain strength
    
    Distance from Sun to Moon (waxing) or Moon to Sun (waning) / 3 = Paksha Bala
    Maximum: 60 shashtiamsas
    """
    sun_long = get_planet_longitude('Sun', jd, ayanamsa)
    moon_long = get_planet_longitude('Moon', jd, ayanamsa)
    
    # Calculate tithi (lunar day)
    moon_sun_distance = (moon_long - sun_long) % 360
    
    # Waxing if Moon is ahead of Sun (0-180°)
    is_waxing = moon_sun_distance <= 180
    
    # Benefics (Moon, Jupiter, Venus, Mercury) strong in Shukla Paksha
    benefics = ['Moon', 'Jupiter', 'Venus', 'Mercury']
    
    if is_waxing:
        distance = moon_sun_distance
    else:
        distance = 360 - moon_sun_distance
    
    paksha_bala = distance / 3.0
    
    # Adjust based on planet type
    if planet in benefics and is_waxing:
        return min(60.0, round(paksha_bala, 2))
    elif planet not in benefics and not is_waxing:
        return min(60.0, round(paksha_bala, 2))
    else:
        # Opposite phase - reduced strength
        return min(60.0, round((180 - distance) / 3.0, 2))


def get_tribhaga_bala(planet: str, jd: float, lat: float, lon: float) -> float:
    """
    Tribhaga Bala (1/3 Day/Night Strength)
    
    Day divided into 3 parts:
    - 1st third: Mercury gets 60 shashtiamsas
    - 2nd third: Sun gets 60 shashtiamsas
    - 3rd third: Saturn gets 60 shashtiamsas
    
    Night divided into 3 parts:
    - 1st third: Moon gets 60 shashtiamsas
    - 2nd third: Venus gets 60 shashtiamsas
    - 3rd third: Mars gets 60 shashtiamsas
    
    Jupiter always gets 60 shashtiamsas
    """
    if planet == 'Jupiter':
        return 60.0
    
    # Simplified day/night calculation
    ut_hour = (jd % 1) * 24
    local_hour = (ut_hour + lon / 15) % 24
    
    # Approximate: day = 6-18, night = 18-6
    is_day = 6 <= local_hour < 18
    
    if is_day:
        day_progress = (local_hour - 6) / 12  # 0 to 1
        if day_progress < 1/3:
            return 60.0 if planet == 'Mercury' else 0.0
        elif day_progress < 2/3:
            return 60.0 if planet == 'Sun' else 0.0
        else:
            return 60.0 if planet == 'Saturn' else 0.0
    else:
        # Night time
        if local_hour >= 18:
            night_progress = (local_hour - 18) / 12
        else:
            night_progress = (local_hour + 6) / 12
        
        if night_progress < 1/3:
            return 60.0 if planet == 'Moon' else 0.0
        elif night_progress < 2/3:
            return 60.0 if planet == 'Venus' else 0.0
        else:
            return 60.0 if planet == 'Mars' else 0.0


def get_abda_bala(planet: str, jd: float) -> float:
    """
    Abda Bala (Year Lord Strength)
    
    The planet that is lord of the year of birth gets 15 shashtiamsas.
    Year lord calculated based on weekday at beginning of solar year.
    """
    # Simplified: use weekday lord
    weekday = int(jd + 1.5) % 7  # 0=Sunday
    weekday_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    year_lord = weekday_order[weekday]
    
    return 15.0 if planet == year_lord else 0.0


def get_masa_bala(planet: str, jd: float) -> float:
    """
    Masa Bala (Month Lord Strength)
    
    The planet that is lord of the month of birth gets 30 shashtiamsas.
    """
    # Simplified calculation based on lunar month
    weekday = int(jd + 1.5) % 7
    weekday_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    # Use lunar month approximation
    lunar_month = int((jd % 29.5) / 29.5 * 7) % 7
    month_lord = weekday_order[lunar_month]
    
    return 30.0 if planet == month_lord else 0.0


def get_vara_bala(planet: str, jd: float) -> float:
    """
    Vara Bala (Weekday Lord Strength)
    
    The planet that is lord of the weekday of birth gets 45 shashtiamsas.
    """
    weekday = int(jd + 1.5) % 7  # 0=Sunday
    weekday_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    vara_lord = weekday_order[weekday]
    
    return 45.0 if planet == vara_lord else 0.0


def get_hora_bala(planet: str, jd: float) -> float:
    """
    Hora Bala (Hour Lord Strength)
    
    The planet that is lord of the hora (hour) of birth gets 60 shashtiamsas.
    Hora lords follow Chaldean order from weekday lord.
    """
    weekday = int(jd + 1.5) % 7
    hour = int((jd % 1) * 24)
    
    # Chaldean order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
    chaldean_order = ['Saturn', 'Jupiter', 'Mars', 'Sun', 'Venus', 'Mercury', 'Moon']
    
    # Start from weekday lord position in Chaldean order
    weekday_order = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    start_lord = weekday_order[weekday]
    start_index = chaldean_order.index(start_lord)
    
    # Calculate hora lord
    hora_index = (start_index + hour) % 7
    hora_lord = chaldean_order[hora_index]
    
    return 60.0 if planet == hora_lord else 0.0


def get_ayana_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Ayana Bala (Declination Strength)
    
    Based on planet's declination (north/south of celestial equator).
    All planets get 30 shashtiamsas at equator.
    
    Sun, Mars, Jupiter, Venus: gain when in northern declination
    Moon, Saturn: gain when in southern declination
    """
    longitude = get_planet_longitude(planet, jd, ayanamsa)
    
    # Approximate declination from longitude
    # Max declination ~23.5° at 90° and 270° longitude
    declination = 23.5 * math.sin(math.radians(longitude))
    
    # Base 30 at equator
    base = 30.0
    
    # Northern planets
    if planet in ['Sun', 'Mars', 'Jupiter', 'Venus']:
        if declination > 0:
            strength = base + (abs(declination) / 23.5) * 30
        else:
            strength = base - (abs(declination) / 23.5) * 30
    # Southern planets
    elif planet in ['Moon', 'Saturn']:
        if declination < 0:
            strength = base + (abs(declination) / 23.5) * 30
        else:
            strength = base - (abs(declination) / 23.5) * 30
    else:
        strength = base
    
    return max(0, min(60.0, round(strength, 2)))


def get_yuddha_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Yuddha Bala (Planetary War Strength)
    
    Two planets are in war when within 1° of each other.
    Winner (northern latitude) gains, loser loses strength.
    Sun and Moon never participate in war.
    
    Returns additional/subtracted strength based on war outcome.
    """
    if planet in ['Sun', 'Moon']:
        return 0.0
    
    planet_long = get_planet_longitude(planet, jd, ayanamsa)
    
    # Check for conjunction with other planets
    for other in PLANETS:
        if other == planet or other in ['Sun', 'Moon']:
            continue
        
        other_long = get_planet_longitude(other, jd, ayanamsa)
        distance = abs(planet_long - other_long)
        if distance > 180:
            distance = 360 - distance
        
        # War if within 1 degree
        if distance < 1.0:
            # Simplified: planet with greater longitude wins
            if planet_long > other_long:
                return 60.0  # Winner
            else:
                return -60.0  # Loser
    
    return 0.0


def get_kaala_bala(planet: str, jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, float]:
    """
    Calculate complete Kaala Bala (Temporal Strength)
    
    Kaala Bala = Nathonnatha + Paksha + Tribhaga + Abda + Masa + Vara + Hora + Ayana + Yuddha
    """
    nathonnatha = get_nathonnatha_bala(planet, jd, lat, lon)
    paksha = get_paksha_bala(planet, jd, ayanamsa)
    tribhaga = get_tribhaga_bala(planet, jd, lat, lon)
    abda = get_abda_bala(planet, jd)
    masa = get_masa_bala(planet, jd)
    vara = get_vara_bala(planet, jd)
    hora = get_hora_bala(planet, jd)
    ayana = get_ayana_bala(planet, jd, ayanamsa)
    yuddha = get_yuddha_bala(planet, jd, ayanamsa)
    
    total = nathonnatha + paksha + tribhaga + abda + masa + vara + hora + ayana + yuddha
    
    return {
        'nathonnatha_bala': round(nathonnatha, 2),
        'paksha_bala': round(paksha, 2),
        'tribhaga_bala': round(tribhaga, 2),
        'abda_bala': round(abda, 2),
        'masa_bala': round(masa, 2),
        'vara_bala': round(vara, 2),
        'hora_bala': round(hora, 2),
        'ayana_bala': round(ayana, 2),
        'yuddha_bala': round(yuddha, 2),
        'total': round(total, 2)
    }


# =============================================================================
# 4. CHESHTA BALA (Motional Strength)
# =============================================================================

def get_cheshta_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Cheshta Bala (Motional Strength)
    
    Strength from retrograde motion. Planets gain strength when retrograde.
    Sun and Moon never retrograde, so they get special calculation.
    
    For other planets:
    Vakra (retrograde): 60 shashtiamsas
    Anuvakra (re-retrograde): 30 shashtiamsas
    Vikala (standstill): 15 shashtiamsas
    Manda (slow): 7.5 shashtiamsas
    Sama (moderate): 15 shashtiamsas
    Chara (fast): 30 shashtiamsas
    Atichara (very fast): 45 shashtiamsas
    """
    if planet in ['Sun', 'Moon']:
        # Special calculation for Sun and Moon
        return 30.0  # Average value
    
    planet_id = PLANET_IDS.get(planet)
    if planet_id is None:
        return 0.0
    
    # Get planet's speed
    pos = swe.calc_ut(jd, planet_id, swe.FLG_SPEED)
    speed = pos[0][3]  # Speed in longitude
    
    # Retrograde if speed is negative
    if speed < 0:
        return 60.0  # Retrograde - maximum strength
    elif abs(speed) < 0.01:
        return 15.0  # Stationary
    elif speed < 0.5:
        return 7.5   # Slow
    elif speed < 1.0:
        return 15.0  # Moderate
    elif speed < 1.5:
        return 30.0  # Fast
    else:
        return 45.0  # Very fast


# =============================================================================
# 5. NAISARGIKA BALA (Natural Strength)
# =============================================================================

def get_naisargika_bala(planet: str) -> float:
    """
    Naisargika Bala (Natural/Inherent Strength)
    
    Based on planet's luminosity. Constant values:
    Sun: 60, Moon: 51.43, Venus: 42.86, Jupiter: 34.29
    Mercury: 25.71, Mars: 17.14, Saturn: 8.57
    """
    return NAISARGIKA_BALA.get(planet, 0.0)


# =============================================================================
# 6. DRIK BALA (Aspectual Strength)
# =============================================================================

def get_drik_bala(planet: str, jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Drik Bala (Aspect Strength)
    
    Strength gained/lost from aspects of other planets.
    Benefic aspects (Jupiter, Venus, waxing Moon, well-placed Mercury) add strength.
    Malefic aspects (Saturn, Mars, Rahu, Ketu, waning Moon) reduce strength.
    
    Special aspects:
    - Jupiter: full aspect on 5th and 9th
    - Mars: full aspect on 4th and 8th
    - Saturn: full aspect on 3rd and 10th
    """
    planet_long = get_planet_longitude(planet, jd, ayanamsa)
    
    total_drik = 0.0
    benefics = ['Jupiter', 'Venus']
    malefics = ['Saturn', 'Mars']
    
    for other in PLANETS:
        if other == planet:
            continue
        
        other_long = get_planet_longitude(other, jd, ayanamsa)
        
        # Calculate aspect distance (houses)
        distance = (other_long - planet_long) % 360
        house_distance = int(distance / 30) + 1
        
        # Check for aspect
        aspect_strength = 0.0
        
        # All planets aspect 7th (opposition)
        if 165 <= distance <= 195:  # 7th house aspect
            aspect_strength = 1.0
        
        # Special aspects
        if other == 'Jupiter':
            # Jupiter aspects 5th and 9th
            if 105 <= distance <= 135 or 225 <= distance <= 255:
                aspect_strength = 1.0
        elif other == 'Mars':
            # Mars aspects 4th and 8th
            if 75 <= distance <= 105 or 195 <= distance <= 225:
                aspect_strength = 1.0
        elif other == 'Saturn':
            # Saturn aspects 3rd and 10th
            if 45 <= distance <= 75 or 255 <= distance <= 285:
                aspect_strength = 1.0
        
        if aspect_strength > 0:
            if other in benefics:
                total_drik += 15 * aspect_strength
            elif other in malefics:
                total_drik -= 15 * aspect_strength
    
    # Drik Bala can be negative
    return round(total_drik, 2)


# =============================================================================
# SHADBALA PINDA (Total Strength)
# =============================================================================

def get_shadbala_pinda(planet: str, jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Calculate complete Shadbala Pinda (Total Six-fold Strength)
    
    Shadbala Pinda = Sthana Bala + Dig Bala + Kaala Bala + Cheshta Bala + Naisargika Bala + Drik Bala
    
    Result is in Shashtiamsas. Divide by 60 to get Rupas.
    """
    # Calculate all six balas
    sthana = get_sthana_bala(planet, jd, lat, lon, ayanamsa)
    dig = get_dig_bala(planet, jd, lat, lon, ayanamsa)
    kaala = get_kaala_bala(planet, jd, lat, lon, ayanamsa)
    cheshta = get_cheshta_bala(planet, jd, ayanamsa)
    naisargika = get_naisargika_bala(planet)
    drik = get_drik_bala(planet, jd, ayanamsa)
    
    # Total in shashtiamsas
    total_shashtiamsas = sthana['total'] + dig + kaala['total'] + cheshta + naisargika + drik
    
    # Convert to Rupas (1 Rupa = 60 shashtiamsas)
    total_rupas = total_shashtiamsas / 60.0
    
    # Check if planet is strong
    required = STRENGTH_REQUIREMENTS.get(planet, 5.0)
    is_strong = total_rupas >= required
    
    return {
        'planet': planet,
        'sthana_bala': sthana,
        'dig_bala': dig,
        'kaala_bala': kaala,
        'cheshta_bala': round(cheshta, 2),
        'naisargika_bala': round(naisargika, 2),
        'drik_bala': round(drik, 2),
        'total_shashtiamsas': round(total_shashtiamsas, 2),
        'total_rupas': round(total_rupas, 2),
        'required_rupas': required,
        'is_strong': is_strong,
        'strength_ratio': round(total_rupas / required * 100, 1)
    }


def get_all_planet_shadbala(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Dict]:
    """
    Calculate Shadbala for all 7 planets.
    
    Args:
        dt: Birth datetime
        lat: Latitude
        lon: Longitude
        ayanamsa: Ayanamsa system (default: LAHIRI)
    
    Returns:
        Dictionary with Shadbala for each planet
    """
    jd = datetime_to_jd(dt)
    results = {}
    
    for planet in PLANETS:
        results[planet] = get_shadbala_pinda(planet, jd, lat, lon, ayanamsa)
    
    return results


def get_shadbala_summary(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Get a summary of Shadbala for all planets.
    
    Returns sorted list by strength and overall analysis.
    """
    all_shadbala = get_all_planet_shadbala(dt, lat, lon, ayanamsa)
    
    # Create sorted list by total rupas
    sorted_planets = sorted(
        all_shadbala.items(),
        key=lambda x: x[1]['total_rupas'],
        reverse=True
    )
    
    # Count strong/weak planets
    strong_planets = [p for p, data in sorted_planets if data['is_strong']]
    weak_planets = [p for p, data in sorted_planets if not data['is_strong']]
    
    # Calculate average strength
    avg_rupas = sum(data['total_rupas'] for _, data in sorted_planets) / len(sorted_planets)
    
    return {
        'planets': {p: data for p, data in sorted_planets},
        'strongest_planet': sorted_planets[0][0],
        'weakest_planet': sorted_planets[-1][0],
        'strong_planets': strong_planets,
        'weak_planets': weak_planets,
        'average_rupas': round(avg_rupas, 2),
        'ranking': [p for p, _ in sorted_planets]
    }


def get_planet_strength_percentage(planet: str, dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> float:
    """
    Get planet's strength as percentage (0-100%).
    
    Based on ratio of actual strength to required strength.
    """
    jd = datetime_to_jd(dt)
    shadbala = get_shadbala_pinda(planet, jd, lat, lon, ayanamsa)
    return min(100.0, shadbala['strength_ratio'])


def is_planet_strong(planet: str, dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> bool:
    """
    Check if a planet meets minimum Shadbala requirements.
    """
    jd = datetime_to_jd(dt)
    shadbala = get_shadbala_pinda(planet, jd, lat, lon, ayanamsa)
    return shadbala['is_strong']


# =============================================================================
# HOUSE STRENGTH (Bhava Bala)
# =============================================================================

def get_bhava_bala(house: int, jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, float]:
    """
    Calculate Bhava Bala (House Strength)
    
    Bhava Bala = Bhavadhipathi Bala + Bhava Digbala + Bhava Drishti Bala
    
    1. Bhavadhipathi Bala: Strength of house lord
    2. Bhava Digbala: Strength from sign type
    3. Bhava Drishti Bala: Aspect strength on house
    """
    # Sign rulers for each house (depends on ascendant)
    house_cusps = get_house_cusps(jd, lat, lon, ayanamsa)
    house_sign = get_sign(house_cusps[house - 1])
    
    # Sign lords
    sign_lords = {
        1: 'Mars', 2: 'Venus', 3: 'Mercury', 4: 'Moon',
        5: 'Sun', 6: 'Mercury', 7: 'Venus', 8: 'Mars',
        9: 'Jupiter', 10: 'Saturn', 11: 'Saturn', 12: 'Jupiter'
    }
    
    house_lord = sign_lords[house_sign]
    
    # Get house lord's Shadbala
    lord_shadbala = get_shadbala_pinda(house_lord, jd, lat, lon, ayanamsa)
    bhavadhipathi_bala = lord_shadbala['total_rupas'] * 10  # Scale factor
    
    # Bhava Digbala based on sign type
    # Movable signs strong in angles, fixed in succedent, dual in cadent
    sign_qualities = {
        1: 'movable', 2: 'fixed', 3: 'dual', 4: 'movable',
        5: 'fixed', 6: 'dual', 7: 'movable', 8: 'fixed',
        9: 'dual', 10: 'movable', 11: 'fixed', 12: 'dual'
    }
    
    quality = sign_qualities[house_sign]
    
    if quality == 'movable' and house in [1, 4, 7, 10]:
        digbala = 60
    elif quality == 'fixed' and house in [2, 5, 8, 11]:
        digbala = 60
    elif quality == 'dual' and house in [3, 6, 9, 12]:
        digbala = 60
    else:
        digbala = 30
    
    total = bhavadhipathi_bala + digbala
    
    return {
        'house': house,
        'sign': SIGNS[house_sign - 1],
        'lord': house_lord,
        'bhavadhipathi_bala': round(bhavadhipathi_bala, 2),
        'bhava_digbala': digbala,
        'total': round(total, 2)
    }


def get_shadbala_ratios(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, float]:
    """
    Get simple Shadbala strength ratios for all planets.
    
    Returns strength ratio (actual/required) for each planet.
    Ratio > 1.0 = Strong, < 1.0 = Weak
    
    Example:
        {
            "Sun": 1.2,  # Strong (20% above required)
            "Moon": 0.9, # Weak (10% below required)
            "Mars": 1.5  # Very Strong (50% above required)
        }
    """
    jd = datetime_to_jd(dt)
    ratios = {}
    
    for planet in PLANETS:
        shadbala = get_shadbala_pinda(planet, jd, lat, lon, ayanamsa)
        # Calculate ratio: actual_rupas / required_rupas
        ratio = shadbala['total_rupas'] / shadbala['required_rupas']
        ratios[planet.lower()] = round(ratio, 2)
    
    return ratios


def get_full_shadbala_report(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Generate comprehensive Shadbala report.
    """
    summary = get_shadbala_summary(dt, lat, lon, ayanamsa)
    jd = datetime_to_jd(dt)
    
    # Add house strengths
    house_strengths = {}
    for house in range(1, 13):
        house_strengths[house] = get_bhava_bala(house, jd, lat, lon, ayanamsa)
    
    return {
        'datetime': dt.isoformat(),
        'location': {'latitude': lat, 'longitude': lon},
        'ayanamsa': ayanamsa,
        'planet_shadbala': summary['planets'],
        'ranking': summary['ranking'],
        'strongest_planet': summary['strongest_planet'],
        'weakest_planet': summary['weakest_planet'],
        'strong_planets': summary['strong_planets'],
        'weak_planets': summary['weak_planets'],
        'average_strength_rupas': summary['average_rupas'],
        'house_strengths': house_strengths
    }
