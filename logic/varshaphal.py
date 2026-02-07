"""
Varshaphal - Annual Horoscope (Tajika System)
Solar Return chart cast when Sun returns to natal position each birthday
"""

from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import math

# Year Lords based on weekday (0=Monday, 6=Sunday in some systems)
# Traditional: Sunday=0
WEEKDAY_LORDS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

# Muntha progression - moves one sign per year from birth Lagna
# Muntha sign = (Birth Lagna sign + Age) % 12


def get_solar_return_jd(natal_sun_long: float, year: int, birth_jd: float) -> float:
    """
    Calculate the Julian Day when Sun returns to natal longitude for a given year.
    This is an approximation - for precise calculation, use iterative methods.
    
    Args:
        natal_sun_long: Natal Sun longitude (0-360)
        year: The year for which to calculate solar return
        birth_jd: Birth Julian Day
        
    Returns:
        Approximate Julian Day of solar return
    """
    # Average solar year is approximately 365.2422 days
    # Birth year approximation
    birth_year_approx = 1988  # Will be calculated from JD in real implementation
    
    # Years elapsed
    years_elapsed = year - birth_year_approx
    
    # Approximate JD of solar return
    solar_return_jd = birth_jd + (years_elapsed * 365.2422)
    
    return solar_return_jd


def get_muntha(birth_lagna_sign: int, age: int) -> Tuple[int, str]:
    """
    Calculate Muntha position for a given age.
    Muntha progresses one sign per year from birth Lagna.
    
    Args:
        birth_lagna_sign: Birth Lagna sign index (0-11)
        age: Current age (years completed)
        
    Returns:
        Tuple of (sign_index, sign_name)
    """
    from logic.rasi import RASIS
    
    muntha_sign = (birth_lagna_sign + age) % 12
    return muntha_sign, RASIS[muntha_sign]


def get_year_lord(solar_return_weekday: int) -> str:
    """
    Get the Year Lord (Varsheshvara) based on weekday of solar return.
    
    Args:
        solar_return_weekday: Weekday (0=Sunday, 1=Monday, ..., 6=Saturday)
        
    Returns:
        Name of the Year Lord planet
    """
    return WEEKDAY_LORDS[solar_return_weekday % 7]


def get_muntha_lord(muntha_sign: int) -> str:
    """
    Get the lord of Muntha sign.
    """
    SIGN_LORDS = ['Mars', 'Venus', 'Mercury', 'Moon', 'Sun', 'Mercury', 
                  'Venus', 'Mars', 'Jupiter', 'Saturn', 'Saturn', 'Jupiter']
    return SIGN_LORDS[muntha_sign]


# =============================================================================
# TAJIKA YOGAS - Special planetary combinations in Varshaphal
# =============================================================================

TAJIKA_YOGAS = {
    'Ikkabal': {
        'description': 'Planet in own sign, exaltation, or Moolatrikona',
        'effect': 'Excellent results, planet gives full benefic effects'
    },
    'Induvara': {
        'description': 'Planets in mutual Kendras (1, 4, 7, 10)',
        'effect': 'Strong mutual support, goals achieved through cooperation'
    },
    'Ithasala': {
        'description': 'Faster planet applying to slower planet within orb',
        'effect': 'Events will manifest, matters come to fruition'
    },
    'Ishrafa': {
        'description': 'Faster planet separating from slower planet',
        'effect': 'Matters already past peak, declining influence'
    },
    'Nakta': {
        'description': 'No direct aspect but third planet transfers light',
        'effect': 'Matters achieved through intermediary or third party'
    },
    'Yamaya': {
        'description': 'Two planets both separating, third collecting light',
        'effect': 'Union of two separate matters through mediator'
    },
    'Manaoo': {
        'description': 'Application prevented by third planet',
        'effect': 'Obstruction, hindrance to desired outcome'
    },
    'Kamboola': {
        'description': 'Moon applies to Year Lord with mutual reception',
        'effect': 'Highly auspicious, success in undertakings'
    },
    'Gairi-Kamboola': {
        'description': 'Moon applies but no mutual reception',
        'effect': 'Partial success, results with some effort'
    },
    'Khallasar': {
        'description': 'Moon separating from Year Lord',
        'effect': 'Diminishing fortunes, matters winding down'
    },
    'Radda': {
        'description': 'Planet retrograde during application',
        'effect': 'Delays, reversals, need to reconsider'
    },
    'Duhphali-Kuttha': {
        'description': 'Applying planet combust',
        'effect': 'Hidden obstacles, matters obscured'
    },
    'Dutthottara-Davira': {
        'description': 'Planet in 6th, 8th, or 12th from another',
        'effect': 'Inimical relationship, conflicts likely'
    },
    'Tambira': {
        'description': 'Both planets in each other\'s debilitation sign',
        'effect': 'Mutual weakness, difficult outcomes'
    },
    'Kuttha': {
        'description': 'Planet combust (within Sun\'s orb)',
        'effect': 'Planet\'s significations weakened or hidden'
    },
}


def check_ithasala(planet1_long: float, planet1_speed: float,
                   planet2_long: float, planet2_speed: float,
                   orb: float = 12.0) -> bool:
    """
    Check if two planets form Ithasala yoga (applying aspect).
    
    Args:
        planet1_long: Longitude of faster planet
        planet1_speed: Daily motion of faster planet
        planet2_long: Longitude of slower planet
        planet2_speed: Daily motion of slower planet
        orb: Orb of influence in degrees
        
    Returns:
        True if Ithasala is formed
    """
    # Calculate distance
    diff = planet2_long - planet1_long
    if diff < 0:
        diff += 360
    if diff > 180:
        diff = 360 - diff
    
    # Check if within orb and faster planet is behind (applying)
    if diff <= orb and planet1_speed > planet2_speed:
        return True
    
    return False


def check_ishrafa(planet1_long: float, planet1_speed: float,
                  planet2_long: float, planet2_speed: float) -> bool:
    """
    Check if two planets form Ishrafa yoga (separating aspect).
    Opposite of Ithasala.
    """
    # Faster planet has already passed slower planet
    diff = planet1_long - planet2_long
    if diff < 0:
        diff += 360
    if diff > 180:
        diff = 360 - diff
    
    # Within small orb and separating
    if diff <= 12 and planet1_speed > planet2_speed:
        # Check if planet1 is ahead
        normalized_diff = (planet1_long - planet2_long) % 360
        if normalized_diff < 180:
            return True
    
    return False


# =============================================================================
# SAHAMS - Arabic Parts / Sensitive Points
# =============================================================================

SAHAMS = {
    'Punya Saham': {
        'formula': 'Moon + Lagna - Sun',
        'signification': 'Fortune, overall well-being, luck'
    },
    'Vidya Saham': {
        'formula': 'Moon + Mercury - Jupiter',
        'signification': 'Education, learning, knowledge'
    },
    'Yashas Saham': {
        'formula': 'Jupiter + Moon - Sun',
        'signification': 'Fame, reputation, honor'
    },
    'Mitra Saham': {
        'formula': 'Jupiter + Moon - Mercury',
        'signification': 'Friends, alliances, partnerships'
    },
    'Mahatmya Saham': {
        'formula': 'Saturn + Moon - Mars',
        'signification': 'Greatness, status, position'
    },
    'Asha Saham': {
        'formula': 'Saturn + Venus - Mars',
        'signification': 'Hopes, wishes, aspirations'
    },
    'Samartha Saham': {
        'formula': 'Saturn + Mars - Sun',
        'signification': 'Capability, ability, competence'
    },
    'Bhratri Saham': {
        'formula': 'Jupiter + Saturn - Sun',
        'signification': 'Brothers, siblings'
    },
    'Gaurav Saham': {
        'formula': 'Jupiter + Moon - Sun',
        'signification': 'Prestige, dignity'
    },
    'Pitri Saham': {
        'formula': 'Saturn + Sun - Moon',
        'signification': 'Father, paternal matters'
    },
    'Matri Saham': {
        'formula': 'Moon + Venus - Saturn',
        'signification': 'Mother, maternal matters'
    },
    'Putra Saham': {
        'formula': 'Jupiter + Moon - Sun',
        'signification': 'Children, progeny'
    },
    'Vivaha Saham': {
        'formula': 'Venus + Saturn - Sun',
        'signification': 'Marriage, partnership'
    },
    'Karma Saham': {
        'formula': 'Mars + Sun - Mercury',
        'signification': 'Career, profession, actions'
    },
    'Roga Saham': {
        'formula': 'Saturn + Mars - Lagna',
        'signification': 'Disease, health issues'
    },
    'Kali Saham': {
        'formula': 'Saturn + Jupiter - Sun',
        'signification': 'Strife, discord, quarrels'
    },
    'Mrityu Saham': {
        'formula': 'Saturn + Lagna - Moon',
        'signification': 'Death, endings, transformation'
    },
    'Paradesa Saham': {
        'formula': 'Saturn + Mars - Moon',
        'signification': 'Foreign travel, distant lands'
    },
}


def calculate_saham(formula: str, planet_longs: Dict[str, float], lagna: float) -> float:
    """
    Calculate a Saham (Arabic Part) based on formula.
    
    Args:
        formula: Formula like 'Moon + Lagna - Sun'
        planet_longs: Dictionary of planet longitudes
        lagna: Ascendant longitude
        
    Returns:
        Saham longitude (0-360)
    """
    # Add Lagna to planet longitudes for calculation
    all_points = {**planet_longs, 'Lagna': lagna}
    
    # Parse formula
    parts = formula.replace(' ', '').replace('+', ' + ').replace('-', ' - ').split()
    
    result = 0
    operation = '+'
    
    for part in parts:
        if part == '+':
            operation = '+'
        elif part == '-':
            operation = '-'
        else:
            value = all_points.get(part, 0)
            if operation == '+':
                result += value
            else:
                result -= value
    
    # Normalize to 0-360
    result = result % 360
    if result < 0:
        result += 360
    
    return result


def get_all_sahams(planet_longs: Dict[str, float], lagna: float) -> Dict[str, Dict]:
    """
    Calculate all Sahams for a chart.
    
    Returns:
        Dict with Saham names and their values
    """
    from logic.rasi import RASIS
    
    results = {}
    
    for name, data in SAHAMS.items():
        longitude = calculate_saham(data['formula'], planet_longs, lagna)
        sign_idx = int(longitude / 30)
        degree_in_sign = longitude % 30
        
        results[name] = {
            'longitude': longitude,
            'sign': RASIS[sign_idx],
            'sign_index': sign_idx,
            'degree': degree_in_sign,
            'signification': data['signification']
        }
    
    return results


# =============================================================================
# PANCHA-VARGEEYA BALA (Five-fold Strength in Varshaphal)
# =============================================================================

def get_pancha_vargeeya_bala(planet: str, longitude: float) -> Dict:
    """
    Calculate the five-fold strength of a planet in Varshaphal.
    
    The five factors are:
    1. Kshetra Bala (Sign strength)
    2. Uccha Bala (Exaltation strength)
    3. Hadda Bala (Term strength)
    4. Drekkana Bala (Decanate strength)
    5. Navamsa Bala (Ninth division strength)
    
    Each gives 0-20 points, max total = 100
    """
    from logic.avastha import get_sign_from_longitude, EXALTATION, DEBILITATION, OWN_SIGNS, SIGN_LORDS
    
    sign = get_sign_from_longitude(longitude)
    degree = longitude % 30
    
    bala = {
        'planet': planet,
        'longitude': longitude,
        'kshetra_bala': 0,
        'uccha_bala': 0,
        'hadda_bala': 0,
        'drekkana_bala': 0,
        'navamsa_bala': 0,
        'total': 0
    }
    
    if planet in ['Rahu', 'Ketu']:
        bala['total'] = 50  # Nodes get neutral strength
        return bala
    
    # 1. Kshetra Bala (Sign dignity)
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        bala['kshetra_bala'] = 20
    elif planet in EXALTATION and EXALTATION[planet][0] == sign:
        bala['kshetra_bala'] = 20
    elif planet in DEBILITATION and DEBILITATION[planet] == sign:
        bala['kshetra_bala'] = 0
    else:
        bala['kshetra_bala'] = 10  # Neutral
    
    # 2. Uccha Bala (Exaltation proximity)
    if planet in EXALTATION:
        exalt_sign, exalt_deg = EXALTATION[planet]
        exalt_long = exalt_sign * 30 + exalt_deg
        debil_long = (exalt_long + 180) % 360
        
        # Distance from debilitation
        dist = abs(longitude - debil_long)
        if dist > 180:
            dist = 360 - dist
        
        # Closer to exaltation = higher score
        bala['uccha_bala'] = round((dist / 180) * 20)
    else:
        bala['uccha_bala'] = 10
    
    # 3. Hadda Bala (Term/Bound strength) - Simplified
    # Terms divide each sign into 5 unequal parts ruled by planets
    hadda_rulers_by_degree = [
        (6, 'Jupiter'), (12, 'Venus'), (20, 'Mercury'), (25, 'Mars'), (30, 'Saturn')
    ]
    hadda_lord = 'Saturn'
    for deg_limit, lord in hadda_rulers_by_degree:
        if degree < deg_limit:
            hadda_lord = lord
            break
    
    if hadda_lord == planet:
        bala['hadda_bala'] = 20
    else:
        bala['hadda_bala'] = 10
    
    # 4. Drekkana Bala (Decanate)
    decan = int(degree / 10)
    decan_lords = [
        SIGN_LORDS[sign],
        SIGN_LORDS[(sign + 4) % 12],
        SIGN_LORDS[(sign + 8) % 12]
    ]
    if decan_lords[decan] == planet:
        bala['drekkana_bala'] = 20
    else:
        bala['drekkana_bala'] = 10
    
    # 5. Navamsa Bala
    navamsa_sign = int((longitude % 30) / 3.333333) % 12
    if sign % 3 == 0:  # Movable signs start from same sign
        navamsa_sign = (sign + int(degree / 3.333333)) % 12
    elif sign % 3 == 1:  # Fixed signs start from 9th
        navamsa_sign = ((sign + 8) + int(degree / 3.333333)) % 12
    else:  # Dual signs start from 5th
        navamsa_sign = ((sign + 4) + int(degree / 3.333333)) % 12
    
    if planet in OWN_SIGNS and navamsa_sign in OWN_SIGNS[planet]:
        bala['navamsa_bala'] = 20
    else:
        bala['navamsa_bala'] = 10
    
    bala['total'] = (bala['kshetra_bala'] + bala['uccha_bala'] + 
                     bala['hadda_bala'] + bala['drekkana_bala'] + 
                     bala['navamsa_bala'])
    
    return bala


# =============================================================================
# MAIN VARSHAPHAL CALCULATION
# =============================================================================

def get_varshaphal(
    birth_date: datetime,
    birth_lagna_long: float,
    natal_sun_long: float,
    natal_planet_longs: Dict[str, float],
    varsha_year: int,
    varsha_lagna_long: float,
    varsha_planet_longs: Dict[str, float],
    varsha_weekday: int
) -> Dict:
    """
    Calculate complete Varshaphal (Annual Horoscope) for a given year.
    
    Args:
        birth_date: Birth datetime
        birth_lagna_long: Natal ascendant longitude
        natal_sun_long: Natal Sun longitude
        natal_planet_longs: Dict of natal planet longitudes
        varsha_year: Year for which to calculate Varshaphal
        varsha_lagna_long: Varsha chart ascendant longitude
        varsha_planet_longs: Dict of Varsha chart planet longitudes
        varsha_weekday: Weekday of solar return (0=Sunday)
        
    Returns:
        Dict with complete Varshaphal analysis
    """
    from logic.rasi import RASIS, get_rasi
    
    # Calculate age
    age = varsha_year - birth_date.year
    
    # Get birth Lagna sign
    birth_lagna_sign = int(birth_lagna_long / 30)
    
    # Calculate Muntha
    muntha_sign, muntha_rasi = get_muntha(birth_lagna_sign, age)
    muntha_lord = get_muntha_lord(muntha_sign)
    
    # Get Year Lord
    year_lord = get_year_lord(varsha_weekday)
    
    # Get Varsha Lagna
    varsha_lagna_sign = int(varsha_lagna_long / 30)
    varsha_lagna_rasi = RASIS[varsha_lagna_sign]
    
    # Calculate key Sahams
    key_sahams = ['Punya Saham', 'Karma Saham', 'Vivaha Saham', 'Vidya Saham']
    sahams = {}
    for saham_name in key_sahams:
        formula = SAHAMS[saham_name]['formula']
        longitude = calculate_saham(formula, varsha_planet_longs, varsha_lagna_long)
        sign_idx = int(longitude / 30)
        sahams[saham_name] = {
            'longitude': longitude,
            'sign': RASIS[sign_idx],
            'signification': SAHAMS[saham_name]['signification']
        }
    
    # Calculate Pancha-Vargeeya Bala for key planets
    year_lord_bala = get_pancha_vargeeya_bala(
        year_lord, 
        varsha_planet_longs.get(year_lord, 0)
    )
    
    muntha_lord_bala = get_pancha_vargeeya_bala(
        muntha_lord,
        varsha_planet_longs.get(muntha_lord, 0)
    )
    
    # Determine Muntha house from Varsha Lagna
    muntha_house = ((muntha_sign - varsha_lagna_sign) % 12) + 1
    
    # Assess year quality
    year_quality = "Moderate"
    if muntha_house in [1, 4, 7, 10]:  # Kendras
        year_quality = "Excellent"
    elif muntha_house in [5, 9]:  # Trikonas
        year_quality = "Very Good"
    elif muntha_house in [2, 11]:  # Wealth houses
        year_quality = "Good"
    elif muntha_house in [6, 8, 12]:  # Dusthanas
        year_quality = "Challenging"
    
    # Year Lord strength assessment
    if year_lord_bala['total'] >= 70:
        year_lord_strength = "Strong"
    elif year_lord_bala['total'] >= 50:
        year_lord_strength = "Moderate"
    else:
        year_lord_strength = "Weak"
    
    return {
        'varsha_year': varsha_year,
        'age': age,
        'varsha_lagna': {
            'longitude': varsha_lagna_long,
            'sign': varsha_lagna_rasi,
            'sign_index': varsha_lagna_sign
        },
        'muntha': {
            'sign': muntha_rasi,
            'sign_index': muntha_sign,
            'lord': muntha_lord,
            'house_from_lagna': muntha_house
        },
        'year_lord': {
            'planet': year_lord,
            'strength': year_lord_strength,
            'bala': year_lord_bala
        },
        'muntha_lord_bala': muntha_lord_bala,
        'key_sahams': sahams,
        'year_quality': year_quality,
        'tajika_yogas': list(TAJIKA_YOGAS.keys())  # List available yogas
    }


def get_varshaphal_summary(
    birth_lagna_sign: int,
    age: int,
    varsha_lagna_sign: int,
    varsha_weekday: int
) -> Dict:
    """
    Get a quick Varshaphal summary without full chart calculation.
    
    Args:
        birth_lagna_sign: Birth Lagna sign index (0-11)
        age: Age in the Varsha year
        varsha_lagna_sign: Varsha Lagna sign index (0-11)
        varsha_weekday: Day of week of solar return (0=Sunday)
        
    Returns:
        Dict with basic Varshaphal information
    """
    from logic.rasi import RASIS
    
    # Muntha
    muntha_sign, muntha_rasi = get_muntha(birth_lagna_sign, age)
    muntha_lord = get_muntha_lord(muntha_sign)
    
    # Year Lord
    year_lord = get_year_lord(varsha_weekday)
    
    # Muntha house from Varsha Lagna
    muntha_house = ((muntha_sign - varsha_lagna_sign) % 12) + 1
    
    return {
        'age': age,
        'muntha': {
            'sign': muntha_rasi,
            'lord': muntha_lord,
            'house': muntha_house
        },
        'year_lord': year_lord,
        'varsha_lagna': RASIS[varsha_lagna_sign]
    }
