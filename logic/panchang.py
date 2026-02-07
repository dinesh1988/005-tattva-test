
TITHIS = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

# Complete Nitya Yoga data: (Name, Deity, Nature, Effect Description)
# Nature: Shubha (Auspicious), Ashubha (Inauspicious), Mishra (Mixed)
YOGA_DATA = [
    ("Vishkumbha", "Yama", "Ashubha", "Obstacles, delays, unfavorable for new ventures"),
    ("Priti", "Vishnu", "Shubha", "Love, affection, favorable for relationships"),
    ("Ayushman", "Chandra", "Shubha", "Long life, health, favorable for medical matters"),
    ("Saubhagya", "Brahma", "Shubha", "Good fortune, prosperity, auspicious beginnings"),
    ("Shobhana", "Brihaspati", "Shubha", "Beauty, splendor, favorable for ceremonies"),
    ("Atiganda", "Chandra", "Ashubha", "Danger, obstacles, avoid risky activities"),
    ("Sukarma", "Indra", "Shubha", "Good deeds rewarded, favorable for work"),
    ("Dhriti", "Jala", "Shubha", "Steadfastness, patience, good for long-term plans"),
    ("Shula", "Sarpa", "Ashubha", "Pain, suffering, avoid medical procedures"),
    ("Ganda", "Agni", "Ashubha", "Obstacles, knots, avoid important decisions"),
    ("Vriddhi", "Surya", "Shubha", "Growth, increase, favorable for investments"),
    ("Dhruva", "Bhumi", "Shubha", "Stability, permanence, good for foundations"),
    ("Vyaghata", "Vayu", "Ashubha", "Destruction, opposition, avoid conflicts"),
    ("Harshana", "Bhaga", "Shubha", "Joy, happiness, celebrations favored"),
    ("Vajra", "Varuna", "Mishra", "Strength, power, good for assertive actions"),
    ("Siddhi", "Ganesha", "Shubha", "Success, accomplishment, highly auspicious"),
    ("Vyatipata", "Rudra", "Ashubha", "Calamity, misfortune, avoid travel"),
    ("Variyan", "Kubera", "Shubha", "Excellence, wealth, business favored"),
    ("Parigha", "Vishwakarma", "Ashubha", "Obstruction, blockage, delays likely"),
    ("Shiva", "Mitra", "Shubha", "Auspiciousness, blessings, spiritual activities"),
    ("Siddha", "Kartikeya", "Shubha", "Achievement, victory, goals accomplished"),
    ("Sadhya", "Savitri", "Shubha", "Accomplishment, tasks completed easily"),
    ("Shubha", "Lakshmi", "Shubha", "Auspiciousness, fortune, all activities favored"),
    ("Shukla", "Parvati", "Shubha", "Purity, brightness, ceremonies favored"),
    ("Brahma", "Ashwini Kumars", "Shubha", "Creation, new beginnings, highly auspicious"),
    ("Indra", "Pitris", "Shubha", "Leadership, power, authority matters favored"),
    ("Vaidhriti", "Diti", "Ashubha", "Unfavorable, inauspiciousness, avoid new starts"),
]

YOGAS = [y[0] for y in YOGA_DATA]


# Karana names (11 total: 7 movable + 4 fixed)
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Nagava", "Kimstughna",
]


def get_karana(sun_long: float, moon_long: float) -> dict:
    """Calculate Karana based on the half-tithi (6°) of Moon-Sun elongation.

    Notes:
      - There are 60 half-tithis (30 tithis x 2).
      - Fixed karanas occur at specific half-tithi indices:
        1: Kimstughna, 58: Shakuni, 59: Chatushpada, 60: Nagava
      - The remaining 56 halves repeat the 7 movable karanas starting from Bava.

    Returns:
        dict with name, type (movable/fixed), and half_index (1-60)
    """

    # Normalize longitudes
    sun_long = sun_long % 360
    moon_long = moon_long % 360

    # Difference (Moon - Sun)
    diff = moon_long - sun_long
    if diff < 0:
        diff += 360

    # Each tithi is 12°, each karana is 6° (half tithi)
    half_index = int(diff / 6.0) + 1  # 1..60
    if half_index < 1:
        half_index = 1
    if half_index > 60:
        half_index = 60

    if half_index == 1:
        return {"name": "Kimstughna", "type": "fixed", "half_index": half_index}
    if half_index == 58:
        return {"name": "Shakuni", "type": "fixed", "half_index": half_index}
    if half_index == 59:
        return {"name": "Chatushpada", "type": "fixed", "half_index": half_index}
    if half_index == 60:
        return {"name": "Nagava", "type": "fixed", "half_index": half_index}

    movable = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
    idx = (half_index - 2) % 7
    return {"name": movable[idx], "type": "movable", "half_index": half_index}

def get_tithi(sun_long: float, moon_long: float) -> tuple[str, int, float]:
    """
    Calculates the Tithi based on the longitudinal difference between Moon and Sun.
    Returns (Tithi Name, Tithi Number 1-30, Percentage Left)
    """
    # Normalize longitudes
    sun_long = sun_long % 360
    moon_long = moon_long % 360
    
    # Calculate difference (Moon - Sun)
    diff = moon_long - sun_long
    if diff < 0:
        diff += 360
        
    # Each Tithi is 12 degrees
    tithi_span = 12.0
    tithi_index = int(diff / tithi_span)
    
    # Percentage traversed in current Tithi
    degrees_in_tithi = diff % tithi_span
    percentage = (degrees_in_tithi / tithi_span) * 100
    
    return TITHIS[tithi_index], tithi_index + 1, percentage

def get_yoga(sun_long: float, moon_long: float) -> tuple[str, int]:
    """
    Calculates the Nitya Yoga based on the sum of Moon and Sun longitudes.
    Returns (Yoga Name, Yoga Number 1-27)
    """
    # Normalize longitudes
    sun_long = sun_long % 360
    moon_long = moon_long % 360
    
    # Calculate sum
    total = sun_long + moon_long
    total = total % 360
    
    # Each Yoga is 13 degrees 20 minutes (same as Nakshatra span)
    yoga_span = 360.0 / 27.0
    
    yoga_index = int(total / yoga_span)
    
    return YOGAS[yoga_index], yoga_index + 1


def get_nitya_yoga_details(sun_long: float, moon_long: float) -> dict:
    """
    Get detailed Nitya Yoga information including deity, nature, and effects.
    
    Returns:
        dict with yoga details including percentage traversed
    """
    # Normalize longitudes
    sun_long = sun_long % 360
    moon_long = moon_long % 360
    
    # Calculate sum
    total = sun_long + moon_long
    total = total % 360
    
    # Each Yoga is 13°20' (13.333... degrees)
    yoga_span = 360.0 / 27.0
    
    yoga_index = int(total / yoga_span)
    
    # Calculate percentage traversed
    degrees_in_yoga = total % yoga_span
    percentage = (degrees_in_yoga / yoga_span) * 100
    
    # Get yoga data
    name, deity, nature, effect = YOGA_DATA[yoga_index]
    
    return {
        'name': name,
        'number': yoga_index + 1,
        'deity': deity,
        'nature': nature,
        'effect': effect,
        'percentage': percentage,
        'is_auspicious': nature == 'Shubha'
    }


def get_yoga_for_muhurta(yoga_index: int) -> dict:
    """
    Get yoga information by index for Muhurta calculations.
    
    Args:
        yoga_index: 0-26 index
        
    Returns:
        dict with yoga details
    """
    name, deity, nature, effect = YOGA_DATA[yoga_index % 27]
    
    return {
        'name': name,
        'number': (yoga_index % 27) + 1,
        'deity': deity,
        'nature': nature,
        'effect': effect,
        'is_auspicious': nature == 'Shubha'
    }


# Auspicious yogas for quick reference
SHUBHA_YOGAS = [i for i, y in enumerate(YOGA_DATA) if y[2] == 'Shubha']
ASHUBHA_YOGAS = [i for i, y in enumerate(YOGA_DATA) if y[2] == 'Ashubha']
MISHRA_YOGAS = [i for i, y in enumerate(YOGA_DATA) if y[2] == 'Mishra']
