"""
Jaimini Astrology - Chara Dasa System
Sign-based dasa system from Maharishi Jaimini's Upadesa Sutras
"""

from typing import List, Tuple, Dict
from logic.rasi import get_rasi, RASI_NAMES

# Sign lords (traditional + Jaimini considers outer planets for some)
SIGN_LORDS = {
    0: 4,   # Aries -> Mars (planet index 4 in swisseph: Sun=0, Moon=1, Mercury=2, Venus=3, Mars=4, Jupiter=5, Saturn=6)
    1: 3,   # Taurus -> Venus
    2: 2,   # Gemini -> Mercury
    3: 1,   # Cancer -> Moon
    4: 0,   # Leo -> Sun
    5: 2,   # Virgo -> Mercury
    6: 3,   # Libra -> Venus
    7: 4,   # Scorpio -> Mars
    8: 5,   # Sagittarius -> Jupiter
    9: 6,   # Capricorn -> Saturn
    10: 6,  # Aquarius -> Saturn
    11: 5,  # Pisces -> Jupiter
}

# Odd signs (count direct) vs Even signs (count reverse)
ODD_SIGNS = [0, 2, 4, 6, 8, 10]    # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
EVEN_SIGNS = [1, 3, 5, 7, 9, 11]   # Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces

# Dual signs (have special rules)
DUAL_SIGNS = [2, 5, 8, 11]  # Gemini, Virgo, Sagittarius, Pisces


def get_sign_from_longitude(longitude: float) -> int:
    """Get sign index (0-11) from longitude"""
    return int(longitude / 30) % 12


def is_odd_sign(sign_index: int) -> bool:
    """Check if sign is odd (movable/fixed counting direction)"""
    return sign_index in ODD_SIGNS


def count_signs(from_sign: int, to_sign: int, is_odd: bool) -> int:
    """
    Count signs from one to another.
    For odd signs: count direct (clockwise)
    For even signs: count reverse (anti-clockwise)
    """
    if is_odd:
        # Direct count
        if to_sign >= from_sign:
            return to_sign - from_sign + 1
        else:
            return 12 - from_sign + to_sign + 1
    else:
        # Reverse count
        if from_sign >= to_sign:
            return from_sign - to_sign + 1
        else:
            return from_sign + 12 - to_sign + 1


def get_dasa_years(dasa_sign: int, lord_sign: int) -> int:
    """
    Calculate Chara Dasa years for a sign.
    Years = count from dasa sign to its lord's sign - 1
    Maximum 12 years, minimum 1 year
    """
    is_odd = is_odd_sign(dasa_sign)
    count = count_signs(dasa_sign, lord_sign, is_odd)
    years = count - 1
    
    # Ensure within bounds (1-12)
    if years < 1:
        years = 1
    if years > 12:
        years = 12
    
    return years


def get_chara_dasa_sequence(lagna_sign: int) -> List[int]:
    """
    Get the sequence of signs for Chara Dasa.
    Starting from Lagna, sequence depends on odd/even nature of Lagna.
    """
    sequence = []
    
    if is_odd_sign(lagna_sign):
        # Direct sequence from Lagna
        for i in range(12):
            sequence.append((lagna_sign + i) % 12)
    else:
        # Reverse sequence from Lagna
        for i in range(12):
            sequence.append((lagna_sign - i) % 12)
    
    return sequence


def get_chara_dasa(
    lagna_longitude: float,
    planet_longitudes: Dict[str, float],
    birth_jd: float,
    current_jd: float
) -> Dict:
    """
    Calculate Chara Dasa for a given birth chart.
    
    Args:
        lagna_longitude: Ascendant longitude
        planet_longitudes: Dict with planet names and their longitudes
        birth_jd: Julian day of birth
        current_jd: Current Julian day
        
    Returns:
        Dict with dasa information
    """
    lagna_sign = get_sign_from_longitude(lagna_longitude)
    
    # Get lord positions for all signs
    lord_positions = {}
    planet_to_sign = {
        0: get_sign_from_longitude(planet_longitudes.get('Sun', 0)),
        1: get_sign_from_longitude(planet_longitudes.get('Moon', 0)),
        2: get_sign_from_longitude(planet_longitudes.get('Mercury', 0)),
        3: get_sign_from_longitude(planet_longitudes.get('Venus', 0)),
        4: get_sign_from_longitude(planet_longitudes.get('Mars', 0)),
        5: get_sign_from_longitude(planet_longitudes.get('Jupiter', 0)),
        6: get_sign_from_longitude(planet_longitudes.get('Saturn', 0)),
    }
    
    # Calculate dasa periods
    sequence = get_chara_dasa_sequence(lagna_sign)
    dasa_periods = []
    
    for sign in sequence:
        lord_planet = SIGN_LORDS[sign]
        lord_sign = planet_to_sign[lord_planet]
        years = get_dasa_years(sign, lord_sign)
        
        dasa_periods.append({
            'sign': sign,
            'sign_name': RASI_NAMES[sign],
            'years': years,
            'lord_planet': lord_planet,
            'lord_sign': lord_sign
        })
    
    # Calculate elapsed time and find current dasa
    days_elapsed = current_jd - birth_jd
    years_elapsed = days_elapsed / 365.25
    
    cumulative_years = 0
    current_dasa = None
    current_dasa_start = 0
    
    for period in dasa_periods:
        if cumulative_years + period['years'] > years_elapsed:
            current_dasa = period
            current_dasa_start = cumulative_years
            break
        cumulative_years += period['years']
    
    # If we've gone through all dasas, cycle back
    if current_dasa is None:
        total_cycle = sum(p['years'] for p in dasa_periods)
        years_in_cycle = years_elapsed % total_cycle
        cumulative_years = 0
        for period in dasa_periods:
            if cumulative_years + period['years'] > years_in_cycle:
                current_dasa = period
                current_dasa_start = cumulative_years
                break
            cumulative_years += period['years']
    
    # Calculate time remaining in current dasa
    years_into_dasa = years_elapsed - current_dasa_start
    if years_into_dasa < 0:
        years_into_dasa = 0
    years_remaining = current_dasa['years'] - (years_into_dasa % current_dasa['years'])
    
    return {
        'lagna_sign': lagna_sign,
        'lagna_name': RASI_NAMES[lagna_sign],
        'sequence': sequence,
        'dasa_periods': dasa_periods,
        'current_dasa': current_dasa,
        'years_elapsed': years_elapsed,
        'years_into_dasa': years_into_dasa % current_dasa['years'],
        'years_remaining': years_remaining
    }


def get_chara_dasa_antardasa(
    dasa_sign: int,
    lagna_sign: int,
    planet_longitudes: Dict[str, float],
    dasa_years: float,
    time_into_dasa: float
) -> Dict:
    """
    Calculate Antardasa (sub-period) within a Chara Dasa.
    
    Antardasa sequence:
    - For odd dasa signs: direct from dasa sign
    - For even dasa signs: reverse from dasa sign
    """
    is_odd = is_odd_sign(dasa_sign)
    
    # Get antardasa sequence
    antardasa_sequence = []
    for i in range(12):
        if is_odd:
            antardasa_sequence.append((dasa_sign + i) % 12)
        else:
            antardasa_sequence.append((dasa_sign - i) % 12)
    
    # Each antardasa gets proportional time
    antardasa_duration = dasa_years / 12
    
    # Find current antardasa
    antardasa_index = int(time_into_dasa / antardasa_duration) % 12
    current_antardasa_sign = antardasa_sequence[antardasa_index]
    time_into_antardasa = time_into_dasa % antardasa_duration
    
    return {
        'sequence': antardasa_sequence,
        'duration_each': antardasa_duration,
        'current_sign': current_antardasa_sign,
        'current_name': RASI_NAMES[current_antardasa_sign],
        'time_into_antardasa': time_into_antardasa,
        'time_remaining': antardasa_duration - time_into_antardasa
    }


# Jaimini Karakas (Significators)
KARAKA_NAMES = [
    'Atmakaraka',      # Soul significator (highest degree planet)
    'Amatyakaraka',    # Minister/Career
    'Bhratrikaraka',   # Siblings
    'Matrikaraka',     # Mother
    'Putrakaraka',     # Children
    'Gnatikaraka',     # Relatives/Enemies
    'Darakaraka',      # Spouse (lowest degree planet)
]


def get_chara_karakas(planet_longitudes: Dict[str, float]) -> List[Dict]:
    """
    Calculate Jaimini Chara Karakas based on planetary degrees.
    The planet with highest degree (ignoring sign) becomes Atmakaraka.
    Excludes Rahu/Ketu from karaka calculation.
    
    Args:
        planet_longitudes: Dict with planet names and their longitudes
        
    Returns:
        List of karakas in order from Atmakaraka to Darakaraka
    """
    # Get degrees within sign for each planet (excluding nodes)
    planets_for_karaka = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    
    planet_degrees = []
    for planet in planets_for_karaka:
        if planet in planet_longitudes:
            longitude = planet_longitudes[planet]
            degree_in_sign = longitude % 30  # Degree within sign (0-30)
            planet_degrees.append({
                'planet': planet,
                'longitude': longitude,
                'degree': degree_in_sign
            })
    
    # Sort by degree (highest first)
    planet_degrees.sort(key=lambda x: x['degree'], reverse=True)
    
    # Assign karakas
    karakas = []
    for i, karaka_name in enumerate(KARAKA_NAMES):
        if i < len(planet_degrees):
            karakas.append({
                'karaka': karaka_name,
                'planet': planet_degrees[i]['planet'],
                'degree': planet_degrees[i]['degree'],
                'longitude': planet_degrees[i]['longitude']
            })
    
    return karakas


def get_arudha_lagna(
    house_num: int,
    house_sign: int,
    lord_sign: int
) -> int:
    """
    Calculate Arudha (Pada) for a house.
    Arudha = Count from lord's position as many signs as lord is from house.
    
    Args:
        house_num: House number (1-12)
        house_sign: Sign index of the house (0-11)
        lord_sign: Sign index where the lord is placed (0-11)
        
    Returns:
        Sign index of the Arudha
    """
    # Count from house to lord
    if lord_sign >= house_sign:
        distance = lord_sign - house_sign + 1
    else:
        distance = 12 - house_sign + lord_sign + 1
    
    # Project same distance from lord
    arudha_sign = (lord_sign + distance - 1) % 12
    
    # Special rule: Arudha cannot be in the same sign as house or 7th from it
    if arudha_sign == house_sign:
        arudha_sign = (arudha_sign + 9) % 12  # 10th from house
    elif arudha_sign == (house_sign + 6) % 12:
        arudha_sign = (arudha_sign + 9) % 12  # 10th from 7th = 4th from house
    
    return arudha_sign


def get_all_arudhas(
    lagna_sign: int,
    planet_longitudes: Dict[str, float]
) -> Dict[str, Dict]:
    """
    Calculate all 12 Arudha Padas (A1 to A12).
    
    Args:
        lagna_sign: Ascendant sign index (0-11)
        planet_longitudes: Dict with planet names and their longitudes
        
    Returns:
        Dict with all Arudha Padas
    """
    # Map planets to their sign positions
    planet_signs = {
        'Sun': get_sign_from_longitude(planet_longitudes.get('Sun', 0)),
        'Moon': get_sign_from_longitude(planet_longitudes.get('Moon', 0)),
        'Mars': get_sign_from_longitude(planet_longitudes.get('Mars', 0)),
        'Mercury': get_sign_from_longitude(planet_longitudes.get('Mercury', 0)),
        'Jupiter': get_sign_from_longitude(planet_longitudes.get('Jupiter', 0)),
        'Venus': get_sign_from_longitude(planet_longitudes.get('Venus', 0)),
        'Saturn': get_sign_from_longitude(planet_longitudes.get('Saturn', 0)),
    }
    
    # House cusps (equal house from Lagna)
    house_signs = [(lagna_sign + i) % 12 for i in range(12)]
    
    arudhas = {}
    arudha_names = [
        ('A1', 'Arudha Lagna', 'Self-image'),
        ('A2', 'Dhana Pada', 'Wealth'),
        ('A3', 'Vikrama Pada', 'Siblings'),
        ('A4', 'Matri Pada', 'Mother/Property'),
        ('A5', 'Mantra Pada', 'Children'),
        ('A6', 'Roga Pada', 'Enemies/Disease'),
        ('A7', 'Dara Pada', 'Spouse'),
        ('A8', 'Mrityu Pada', 'Death/Inheritance'),
        ('A9', 'Pitri Pada', 'Father/Guru'),
        ('A10', 'Rajya Pada', 'Career'),
        ('A11', 'Labha Pada', 'Gains'),
        ('A12', 'Upapada', 'Spouse Family'),
    ]
    
    for i, (code, name, signification) in enumerate(arudha_names):
        house_sign = house_signs[i]
        lord_planet_idx = SIGN_LORDS[house_sign]
        
        # Map planet index to name
        planet_idx_to_name = {0: 'Sun', 1: 'Moon', 2: 'Mercury', 3: 'Venus', 
                              4: 'Mars', 5: 'Jupiter', 6: 'Saturn'}
        lord_name = planet_idx_to_name[lord_planet_idx]
        lord_sign = planet_signs[lord_name]
        
        arudha_sign = get_arudha_lagna(i + 1, house_sign, lord_sign)
        
        arudhas[code] = {
            'name': name,
            'signification': signification,
            'house': i + 1,
            'house_sign': house_sign,
            'house_sign_name': RASI_NAMES[house_sign],
            'lord': lord_name,
            'lord_sign': lord_sign,
            'arudha_sign': arudha_sign,
            'arudha_sign_name': RASI_NAMES[arudha_sign]
        }
    
    return arudhas
