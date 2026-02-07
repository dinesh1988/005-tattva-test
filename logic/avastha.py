"""
Avastha - Planetary States in Vedic Astrology
Various conditions that affect a planet's ability to deliver results
"""

from typing import Dict, Tuple, List

# Planet relationships for dignity calculations
# Format: {planet: {friend: [...], neutral: [...], enemy: [...]}}
PLANET_RELATIONSHIPS = {
    'Sun': {'friends': ['Moon', 'Mars', 'Jupiter'], 'neutrals': ['Mercury'], 'enemies': ['Venus', 'Saturn']},
    'Moon': {'friends': ['Sun', 'Mercury'], 'neutrals': ['Mars', 'Jupiter', 'Venus', 'Saturn'], 'enemies': []},
    'Mars': {'friends': ['Sun', 'Moon', 'Jupiter'], 'neutrals': ['Venus', 'Saturn'], 'enemies': ['Mercury']},
    'Mercury': {'friends': ['Sun', 'Venus'], 'neutrals': ['Mars', 'Jupiter', 'Saturn'], 'enemies': ['Moon']},
    'Jupiter': {'friends': ['Sun', 'Moon', 'Mars'], 'neutrals': ['Saturn'], 'enemies': ['Mercury', 'Venus']},
    'Venus': {'friends': ['Mercury', 'Saturn'], 'neutrals': ['Mars', 'Jupiter'], 'enemies': ['Sun', 'Moon']},
    'Saturn': {'friends': ['Mercury', 'Venus'], 'neutrals': ['Jupiter'], 'enemies': ['Sun', 'Moon', 'Mars']},
}

# Sign lordships
SIGN_LORDS = {
    0: 'Mars', 1: 'Venus', 2: 'Mercury', 3: 'Moon',
    4: 'Sun', 5: 'Mercury', 6: 'Venus', 7: 'Mars',
    8: 'Jupiter', 9: 'Saturn', 10: 'Saturn', 11: 'Jupiter'
}

# Exaltation signs and degrees
EXALTATION = {
    'Sun': (0, 10),      # Aries at 10°
    'Moon': (1, 3),      # Taurus at 3°
    'Mars': (9, 28),     # Capricorn at 28°
    'Mercury': (5, 15),  # Virgo at 15°
    'Jupiter': (3, 5),   # Cancer at 5°
    'Venus': (11, 27),   # Pisces at 27°
    'Saturn': (6, 20),   # Libra at 20°
    'Rahu': (1, 20),     # Taurus at 20° (some texts)
    'Ketu': (7, 20),     # Scorpio at 20° (some texts)
}

# Debilitation signs (opposite of exaltation)
DEBILITATION = {
    'Sun': 6,      # Libra
    'Moon': 7,     # Scorpio
    'Mars': 3,     # Cancer
    'Mercury': 11, # Pisces
    'Jupiter': 9,  # Capricorn
    'Venus': 5,    # Virgo
    'Saturn': 0,   # Aries
    'Rahu': 7,     # Scorpio
    'Ketu': 1,     # Taurus
}

# Own signs (Swakshetra)
OWN_SIGNS = {
    'Sun': [4],           # Leo
    'Moon': [3],          # Cancer
    'Mars': [0, 7],       # Aries, Scorpio
    'Mercury': [2, 5],    # Gemini, Virgo
    'Jupiter': [8, 11],   # Sagittarius, Pisces
    'Venus': [1, 6],      # Taurus, Libra
    'Saturn': [9, 10],    # Capricorn, Aquarius
}

# Moolatrikona signs and degree ranges
MOOLATRIKONA = {
    'Sun': (4, 0, 20),      # Leo 0-20°
    'Moon': (1, 4, 20),     # Taurus 4-20°
    'Mars': (0, 0, 12),     # Aries 0-12°
    'Mercury': (5, 16, 20), # Virgo 16-20°
    'Jupiter': (8, 0, 10),  # Sagittarius 0-10°
    'Venus': (6, 0, 15),    # Libra 0-15°
    'Saturn': (10, 0, 20),  # Aquarius 0-20°
}


def get_sign_from_longitude(longitude: float) -> int:
    """Get sign index (0-11) from longitude"""
    return int(longitude / 30) % 12


def get_degree_in_sign(longitude: float) -> float:
    """Get degree within sign (0-30)"""
    return longitude % 30


# =============================================================================
# 1. BALA AVASTHA (Age-based States)
# =============================================================================
# Based on degree within sign, planets have different "ages"
# Odd signs: 0-6° Bala, 6-12° Kumara, 12-18° Yuva, 18-24° Vriddha, 24-30° Mrita
# Even signs: reversed

BALA_AVASTHAS = ['Bala', 'Kumara', 'Yuva', 'Vriddha', 'Mrita']
BALA_MEANINGS = {
    'Bala': ('Infant', 'Very weak results, 25% strength'),
    'Kumara': ('Youth', 'Moderate results, 50% strength'),
    'Yuva': ('Adult', 'Full results, 100% strength'),
    'Vriddha': ('Old', 'Declining results, 50% strength'),
    'Mrita': ('Dead', 'Minimal results, 0% strength'),
}

def get_bala_avastha(longitude: float) -> Tuple[str, str, float]:
    """
    Calculate Bala Avastha (age-based state) of a planet.
    
    Returns:
        Tuple of (avastha_name, meaning, strength_percentage)
    """
    sign = get_sign_from_longitude(longitude)
    degree = get_degree_in_sign(longitude)
    is_odd_sign = sign % 2 == 0  # Aries=0 is odd, Taurus=1 is even
    
    # Calculate segment (each 6 degrees)
    segment = int(degree / 6)
    if segment > 4:
        segment = 4
    
    # Reverse for even signs
    if not is_odd_sign:
        segment = 4 - segment
    
    avastha = BALA_AVASTHAS[segment]
    meaning, strength_desc = BALA_MEANINGS[avastha]
    
    # Strength percentages
    strengths = {'Bala': 25.0, 'Kumara': 50.0, 'Yuva': 100.0, 'Vriddha': 50.0, 'Mrita': 0.0}
    
    return avastha, meaning, strengths[avastha]


# =============================================================================
# 2. JAGRADADI AVASTHA (Alertness States)
# =============================================================================
# Based on whether planet is in own/exalted sign, friend's sign, or enemy's sign

JAGRADADI_AVASTHAS = {
    'Jagrat': ('Awake', 'Full alertness, planet gives full results'),
    'Swapna': ('Dreaming', 'Half alertness, planet gives partial results'),
    'Sushupti': ('Sleeping', 'No alertness, planet gives minimal results'),
}

def get_jagradadi_avastha(planet: str, longitude: float) -> Tuple[str, str]:
    """
    Calculate Jagradadi Avastha (alertness state).
    
    - Jagrat (Awake): Planet in own sign or exaltation
    - Swapna (Dreaming): Planet in friend's sign or neutral sign
    - Sushupti (Sleeping): Planet in enemy's sign or debilitation
    """
    if planet in ['Rahu', 'Ketu']:
        return 'Swapna', 'Dreaming (Nodes follow special rules)'
    
    sign = get_sign_from_longitude(longitude)
    sign_lord = SIGN_LORDS[sign]
    
    # Check exaltation
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'Jagrat', JAGRADADI_AVASTHAS['Jagrat'][1]
    
    # Check own sign
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 'Jagrat', JAGRADADI_AVASTHAS['Jagrat'][1]
    
    # Check debilitation
    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return 'Sushupti', JAGRADADI_AVASTHAS['Sushupti'][1]
    
    # Check relationship with sign lord
    if planet in PLANET_RELATIONSHIPS:
        rel = PLANET_RELATIONSHIPS[planet]
        if sign_lord in rel['friends']:
            return 'Swapna', JAGRADADI_AVASTHAS['Swapna'][1]
        elif sign_lord in rel['enemies']:
            return 'Sushupti', JAGRADADI_AVASTHAS['Sushupti'][1]
        else:
            return 'Swapna', JAGRADADI_AVASTHAS['Swapna'][1]
    
    return 'Swapna', JAGRADADI_AVASTHAS['Swapna'][1]


# =============================================================================
# 3. DEEPTADI AVASTHA (Luminosity/Dignity States)
# =============================================================================
# Nine states based on planetary dignity

DEEPTADI_AVASTHAS = {
    'Deepta': ('Blazing/Exalted', 'Excellent results, planet at peak power'),
    'Swastha': ('Own Sign', 'Very good results, comfortable'),
    'Mudita': ('Friend\'s Sign', 'Good results, supported'),
    'Shanta': ('Moolatrikona', 'Peaceful, beneficial results'),
    'Shakta': ('Aspected by benefic', 'Empowered, good results'),
    'Peedita': ('Aspected by malefic', 'Afflicted, reduced results'),
    'Deena': ('Enemy Sign', 'Weak, poor results'),
    'Khala': ('Combust', 'Hidden, results delayed'),
    'Kopa': ('Debilitated', 'Angry, negative results'),
}

def get_deeptadi_avastha(planet: str, longitude: float, sun_longitude: float = None) -> Tuple[str, str]:
    """
    Calculate Deeptadi Avastha (dignity state).
    
    Primary states (mutual exclusive):
    - Deepta: Exalted
    - Kopa: Debilitated  
    - Swastha: Own sign
    - Shanta: Moolatrikona
    - Mudita: Friend's sign
    - Deena: Enemy's sign
    """
    if planet in ['Rahu', 'Ketu']:
        # Nodes have special dignity rules
        sign = get_sign_from_longitude(longitude)
        if planet == 'Rahu' and sign in [1, 2]:  # Taurus, Gemini
            return 'Swastha', 'Comfortable position for Rahu'
        elif planet == 'Ketu' and sign in [7, 8]:  # Scorpio, Sagittarius
            return 'Swastha', 'Comfortable position for Ketu'
        return 'Mudita', 'Neutral position for nodes'
    
    sign = get_sign_from_longitude(longitude)
    degree = get_degree_in_sign(longitude)
    
    # Check exaltation (Deepta)
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'Deepta', DEEPTADI_AVASTHAS['Deepta'][1]
    
    # Check debilitation (Kopa)
    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return 'Kopa', DEEPTADI_AVASTHAS['Kopa'][1]
    
    # Check Moolatrikona (Shanta)
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        if sign == mt_sign and mt_start <= degree <= mt_end:
            return 'Shanta', DEEPTADI_AVASTHAS['Shanta'][1]
    
    # Check own sign (Swastha)
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 'Swastha', DEEPTADI_AVASTHAS['Swastha'][1]
    
    # Check combustion (Khala) - only if Sun longitude provided
    if sun_longitude is not None and planet != 'Sun':
        sun_diff = abs(longitude - sun_longitude)
        if sun_diff > 180:
            sun_diff = 360 - sun_diff
        
        # Combustion ranges vary by planet
        combust_ranges = {
            'Moon': 12, 'Mars': 17, 'Mercury': 14, 
            'Jupiter': 11, 'Venus': 10, 'Saturn': 15
        }
        if planet in combust_ranges and sun_diff <= combust_ranges[planet]:
            return 'Khala', DEEPTADI_AVASTHAS['Khala'][1]
    
    # Check friend/enemy sign
    sign_lord = SIGN_LORDS[sign]
    if planet in PLANET_RELATIONSHIPS:
        rel = PLANET_RELATIONSHIPS[planet]
        if sign_lord in rel['friends']:
            return 'Mudita', DEEPTADI_AVASTHAS['Mudita'][1]
        elif sign_lord in rel['enemies']:
            return 'Deena', DEEPTADI_AVASTHAS['Deena'][1]
    
    # Neutral
    return 'Mudita', 'Neutral sign placement'


# =============================================================================
# 4. LAJJITADI AVASTHA (Emotional States)
# =============================================================================
# Based on conjunctions and aspects

LAJJITADI_AVASTHAS = {
    'Lajjita': ('Ashamed', 'Planet in 5th house with Rahu/Ketu/Saturn/Mars'),
    'Garvita': ('Proud', 'Planet in exaltation or Moolatrikona'),
    'Kshudita': ('Hungry', 'Planet in enemy sign or conjunct enemy'),
    'Trushita': ('Thirsty', 'Planet in watery sign aspected by enemy'),
    'Mudita': ('Delighted', 'Planet conjunct or aspected by friend'),
    'Kshobhita': ('Agitated', 'Planet conjunct Sun or aspected by malefics'),
}

def get_lajjitadi_avastha(
    planet: str, 
    longitude: float,
    house_num: int = None,
    conjunct_planets: List[str] = None
) -> Tuple[str, str]:
    """
    Calculate Lajjitadi Avastha (emotional state).
    Simplified version based on dignity and conjunctions.
    """
    if conjunct_planets is None:
        conjunct_planets = []
    
    sign = get_sign_from_longitude(longitude)
    
    # Garvita - exalted or moolatrikona
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'Garvita', LAJJITADI_AVASTHAS['Garvita'][1]
    
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        degree = get_degree_in_sign(longitude)
        if sign == mt_sign and mt_start <= degree <= mt_end:
            return 'Garvita', LAJJITADI_AVASTHAS['Garvita'][1]
    
    # Lajjita - in 5th with malefics
    if house_num == 5 and any(p in conjunct_planets for p in ['Rahu', 'Ketu', 'Saturn', 'Mars']):
        return 'Lajjita', LAJJITADI_AVASTHAS['Lajjita'][1]
    
    # Kshobhita - conjunct Sun
    if 'Sun' in conjunct_planets and planet != 'Sun':
        return 'Kshobhita', LAJJITADI_AVASTHAS['Kshobhita'][1]
    
    # Kshudita - enemy sign
    sign_lord = SIGN_LORDS[sign]
    if planet in PLANET_RELATIONSHIPS:
        if sign_lord in PLANET_RELATIONSHIPS[planet]['enemies']:
            return 'Kshudita', LAJJITADI_AVASTHAS['Kshudita'][1]
        if sign_lord in PLANET_RELATIONSHIPS[planet]['friends']:
            return 'Mudita', LAJJITADI_AVASTHAS['Mudita'][1]
    
    return 'Mudita', 'Neutral emotional state'


# =============================================================================
# 5. SHAYANADI AVASTHA (12 States based on Nakshatra)
# =============================================================================

SHAYANADI_AVASTHAS = [
    ('Shayana', 'Lying down', 'Inactive, lazy results'),
    ('Upavesha', 'Sitting', 'Waiting, delayed results'),
    ('Netrapani', 'Eyes in hands', 'Seeking, searching'),
    ('Prakasha', 'Illuminating', 'Clear, visible results'),
    ('Gamana', 'Going', 'Moving towards results'),
    ('Agamana', 'Coming', 'Results approaching'),
    ('Sabha', 'Assembly', 'Public, social results'),
    ('Agama', 'Arrival', 'Results materializing'),
    ('Bhojana', 'Eating', 'Enjoying results'),
    ('Nrityalipsa', 'Dancing', 'Celebrating, joyful'),
    ('Kautuka', 'Curious', 'Exploring new results'),
    ('Nidraa', 'Sleeping', 'Dormant, no results'),
]

def get_shayanadi_avastha(longitude: float) -> Tuple[str, str, str]:
    """
    Calculate Shayanadi Avastha based on nakshatra position.
    Each nakshatra pada corresponds to one of 12 states.
    
    Returns:
        Tuple of (avastha_name, meaning, effect)
    """
    # Get nakshatra pada (1-108 padas total, then mod 12)
    pada_total = int(longitude / 3.333333)  # Each pada is 3°20'
    avastha_index = pada_total % 12
    
    name, meaning, effect = SHAYANADI_AVASTHAS[avastha_index]
    return name, meaning, effect


# =============================================================================
# COMPREHENSIVE AVASTHA ANALYSIS
# =============================================================================

def get_all_avasthas(
    planet: str,
    longitude: float,
    sun_longitude: float = None,
    house_num: int = None,
    conjunct_planets: List[str] = None
) -> Dict:
    """
    Get all avasthas for a planet.
    
    Returns:
        Dict with all avastha information
    """
    bala_name, bala_meaning, bala_strength = get_bala_avastha(longitude)
    jagrat_name, jagrat_desc = get_jagradadi_avastha(planet, longitude)
    deeptadi_name, deeptadi_desc = get_deeptadi_avastha(planet, longitude, sun_longitude)
    lajjit_name, lajjit_desc = get_lajjitadi_avastha(planet, longitude, house_num, conjunct_planets)
    shayan_name, shayan_meaning, shayan_effect = get_shayanadi_avastha(longitude)
    
    return {
        'planet': planet,
        'longitude': longitude,
        'bala_avastha': {
            'name': bala_name,
            'meaning': bala_meaning,
            'strength': bala_strength
        },
        'jagradadi_avastha': {
            'name': jagrat_name,
            'description': jagrat_desc
        },
        'deeptadi_avastha': {
            'name': deeptadi_name,
            'description': deeptadi_desc
        },
        'lajjitadi_avastha': {
            'name': lajjit_name,
            'description': lajjit_desc
        },
        'shayanadi_avastha': {
            'name': shayan_name,
            'meaning': shayan_meaning,
            'effect': shayan_effect
        }
    }


def get_dignity_status(planet: str, longitude: float) -> Tuple[str, int]:
    """
    Get simple dignity status for a planet.
    
    Returns:
        Tuple of (status_name, strength_score)
        Strength: Exalted=5, Moolatrikona=4, Own=3, Friend=2, Neutral=1, Enemy=0, Debilitated=-1
    """
    if planet in ['Rahu', 'Ketu']:
        return 'Neutral', 1
    
    sign = get_sign_from_longitude(longitude)
    degree = get_degree_in_sign(longitude)
    
    # Exalted
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'Exalted', 5
    
    # Debilitated
    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return 'Debilitated', -1
    
    # Moolatrikona
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        if sign == mt_sign and mt_start <= degree <= mt_end:
            return 'Moolatrikona', 4
    
    # Own sign
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 'Own Sign', 3
    
    # Friend/Enemy
    sign_lord = SIGN_LORDS[sign]
    if planet in PLANET_RELATIONSHIPS:
        rel = PLANET_RELATIONSHIPS[planet]
        if sign_lord in rel['friends']:
            return 'Friend Sign', 2
        elif sign_lord in rel['enemies']:
            return 'Enemy Sign', 0
    
    return 'Neutral', 1
