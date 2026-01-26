"""
Kakshya (Kaksha) - Sub-divisions within each sign for Ashtakavarga transit analysis.

Each sign (30°) is divided into 8 Kakshyas of 3°45' (3.75°) each.
The lords of these 8 Kakshyas are fixed in order:
1. Saturn    (0°00' - 3°45')
2. Jupiter   (3°45' - 7°30')
3. Mars      (7°30' - 11°15')
4. Sun       (11°15' - 15°00')
5. Venus     (15°00' - 18°45')
6. Mercury   (18°45' - 22°30')
7. Moon      (22°30' - 26°15')
8. Lagna     (26°15' - 30°00')

When a planet transits through a sign, the Kakshya it occupies indicates
whose "zone" or influence it is under. This is used to fine-tune transit predictions.
"""

# Kakshya Lords in order (each spans 3°45' = 3.75°)
KAKSHYA_LORDS = [
    "Saturn",   # 1st Kakshya: 0° - 3°45'
    "Jupiter",  # 2nd Kakshya: 3°45' - 7°30'
    "Mars",     # 3rd Kakshya: 7°30' - 11°15'
    "Sun",      # 4th Kakshya: 11°15' - 15°
    "Venus",    # 5th Kakshya: 15° - 18°45'
    "Mercury",  # 6th Kakshya: 18°45' - 22°30'
    "Moon",     # 7th Kakshya: 22°30' - 26°15'
    "Lagna",    # 8th Kakshya: 26°15' - 30°
]

KAKSHYA_SPAN = 3.75  # 3°45' in decimal degrees


def get_kakshya(longitude: float) -> tuple[str, int, float]:
    """
    Determines the Kakshya (sub-division) for a given longitude.
    
    Args:
        longitude: The planet's longitude (0-360°)
    
    Returns:
        (Kakshya Lord Name, Kakshya Number 1-8, Percentage traversed in Kakshya)
    """
    longitude = longitude % 360
    degree_in_sign = longitude % 30
    
    # Determine which Kakshya (0-7)
    kakshya_index = int(degree_in_sign / KAKSHYA_SPAN)
    
    # Ensure index is within bounds (edge case for exactly 30°)
    if kakshya_index > 7:
        kakshya_index = 7
    
    # Calculate percentage traversed within this Kakshya
    kakshya_start = kakshya_index * KAKSHYA_SPAN
    degree_in_kakshya = degree_in_sign - kakshya_start
    percentage = (degree_in_kakshya / KAKSHYA_SPAN) * 100.0
    
    return KAKSHYA_LORDS[kakshya_index], kakshya_index + 1, percentage


def get_kakshya_details(longitude: float) -> dict:
    """
    Returns detailed Kakshya information for a given longitude.
    
    Returns a dictionary with:
        - lord: The Kakshya lord
        - number: Kakshya number (1-8)
        - percentage: Percentage traversed in this Kakshya
        - start_degree: Starting degree of this Kakshya within the sign
        - end_degree: Ending degree of this Kakshya within the sign
    """
    longitude = longitude % 360
    degree_in_sign = longitude % 30
    
    kakshya_index = int(degree_in_sign / KAKSHYA_SPAN)
    if kakshya_index > 7:
        kakshya_index = 7
    
    kakshya_start = kakshya_index * KAKSHYA_SPAN
    kakshya_end = (kakshya_index + 1) * KAKSHYA_SPAN
    degree_in_kakshya = degree_in_sign - kakshya_start
    percentage = (degree_in_kakshya / KAKSHYA_SPAN) * 100.0
    
    return {
        "lord": KAKSHYA_LORDS[kakshya_index],
        "number": kakshya_index + 1,
        "percentage": percentage,
        "start_degree": kakshya_start,
        "end_degree": kakshya_end,
        "degree_in_kakshya": degree_in_kakshya
    }


def get_all_planets_kakshya(planet_longitudes: dict) -> dict:
    """
    Calculate Kakshya for multiple planets.
    
    Args:
        planet_longitudes: Dictionary of {planet_name: longitude}
    
    Returns:
        Dictionary of {planet_name: kakshya_info}
    """
    result = {}
    for planet, longitude in planet_longitudes.items():
        lord, number, percentage = get_kakshya(longitude)
        result[planet] = {
            "kakshya_lord": lord,
            "kakshya_num": number,
            "percentage": percentage
        }
    return result
