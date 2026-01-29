from .consts import Planet
from .calculate import get_planet_longitude, get_lagnam
from .rasi import get_rasi
from .time import AstroTime

# Benefic Points Data
# Key: (Main Planet, Source Planet)
# Value: List of Houses (1-based) where points are gained
BENEFIC_POINTS = {
    # SUN
    ("Sun", "Sun"): [1, 2, 4, 7, 8, 9, 10, 11],
    ("Sun", "Mars"): [1, 2, 4, 7, 8, 9, 10, 11],
    ("Sun", "Saturn"): [1, 2, 4, 7, 8, 9, 10, 11],
    ("Sun", "Jupiter"): [5, 6, 9, 11],
    ("Sun", "Moon"): [3, 6, 10, 11],
    ("Sun", "Mercury"): [3, 5, 6, 9, 10, 11, 12],
    ("Sun", "Ascendant"): [3, 4, 6, 10, 11, 12],
    ("Sun", "Venus"): [6, 7, 12],

    # MOON
    ("Moon", "Ascendant"): [3, 6, 10, 11],
    ("Moon", "Mars"): [2, 3, 5, 6, 9, 10, 11],
    ("Moon", "Moon"): [1, 3, 6, 7, 10, 11],
    ("Moon", "Sun"): [3, 6, 7, 8, 10, 11],
    ("Moon", "Saturn"): [3, 5, 6, 11],
    ("Moon", "Mercury"): [1, 3, 4, 5, 7, 8, 10, 11],
    ("Moon", "Jupiter"): [1, 4, 7, 8, 10, 11, 12],
    ("Moon", "Venus"): [3, 4, 5, 7, 9, 10, 11],

    # MARS
    ("Mars", "Sun"): [3, 5, 6, 10, 11],
    ("Mars", "Ascendant"): [1, 3, 6, 10, 11],
    ("Mars", "Moon"): [3, 6, 11],
    ("Mars", "Mars"): [1, 2, 4, 7, 8, 10, 11],
    ("Mars", "Saturn"): [1, 4, 7, 8, 9, 10, 11],
    ("Mars", "Mercury"): [3, 5, 6, 11],
    ("Mars", "Venus"): [6, 8, 11, 12],
    ("Mars", "Jupiter"): [6, 10, 11, 12],

    # MERCURY
    ("Mercury", "Venus"): [1, 2, 3, 4, 5, 8, 9, 11],
    ("Mercury", "Mars"): [1, 2, 4, 7, 8, 9, 10, 11],
    ("Mercury", "Saturn"): [1, 2, 4, 7, 8, 9, 10, 11],
    ("Mercury", "Jupiter"): [6, 8, 11, 12],
    ("Mercury", "Sun"): [5, 6, 9, 11, 12],
    ("Mercury", "Mercury"): [1, 3, 5, 6, 9, 10, 11, 12],
    ("Mercury", "Moon"): [2, 4, 6, 8, 10, 11],
    ("Mercury", "Ascendant"): [1, 2, 4, 6, 8, 10, 11],

    # JUPITER
    ("Jupiter", "Mars"): [1, 2, 4, 7, 8, 10, 11],
    ("Jupiter", "Jupiter"): [1, 2, 3, 4, 7, 8, 10, 11],
    ("Jupiter", "Sun"): [1, 2, 3, 4, 7, 8, 9, 10, 11],
    ("Jupiter", "Venus"): [2, 5, 6, 9, 10, 11],
    ("Jupiter", "Moon"): [2, 5, 7, 9, 11],
    ("Jupiter", "Saturn"): [3, 5, 6, 12],
    ("Jupiter", "Mercury"): [1, 2, 4, 5, 6, 9, 10, 11],
    ("Jupiter", "Ascendant"): [1, 2, 4, 5, 6, 7, 9, 10, 11],

    # VENUS
    ("Venus", "Ascendant"): [1, 2, 3, 4, 5, 8, 9, 11],
    ("Venus", "Moon"): [1, 2, 3, 4, 5, 8, 9, 11, 12],
    ("Venus", "Venus"): [1, 2, 3, 4, 5, 8, 9, 10, 11],
    ("Venus", "Saturn"): [3, 4, 5, 8, 9, 10, 11],
    ("Venus", "Sun"): [8, 11, 12],
    ("Venus", "Jupiter"): [5, 8, 9, 10, 11],
    ("Venus", "Mercury"): [3, 5, 6, 9, 11],
    ("Venus", "Mars"): [3, 5, 6, 9, 11, 12],

    # SATURN
    ("Saturn", "Saturn"): [3, 5, 6, 11],
    ("Saturn", "Mars"): [3, 5, 6, 10, 11, 12],
    ("Saturn", "Sun"): [1, 2, 4, 7, 8, 10, 11],
    ("Saturn", "Ascendant"): [1, 3, 4, 6, 10, 11],
    ("Saturn", "Mercury"): [6, 8, 9, 10, 11, 12],
    ("Saturn", "Moon"): [3, 6, 11],
    ("Saturn", "Venus"): [6, 11, 12],
    ("Saturn", "Jupiter"): [5, 6, 11, 12]
}

def get_sarvashtakavarga_points(astro_time: AstroTime) -> dict[int, int]:
    """
    Calculates the Sarvashtakavarga points for all 12 signs.
    Returns a dictionary {SignNumber (1-12): Points}
    """
    
    # 1. Calculate Rasi Numbers for all Planets + Ascendant
    positions = {}
    
    # Planets
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]:
        long = get_planet_longitude(planet, astro_time)
        _, rasi_num = get_rasi(long)
        positions[planet.name] = rasi_num
        
    # Ascendant
    lagnam_long = get_lagnam(astro_time)
    _, lagnam_num = get_rasi(lagnam_long)
    positions["Ascendant"] = lagnam_num
    
    # 2. Initialize Points Dictionary
    sarvashtaka = {i: 0 for i in range(1, 13)}
    
    # 3. Calculate Points
    # Iterate through each Main Planet (the one receiving the points)
    main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    for main_planet in main_planets:
        # Iterate through each Source Planet (the one giving the points)
        for source_planet, source_rasi in positions.items():
            
            key = (main_planet, source_planet)
            if key in BENEFIC_POINTS:
                benefic_houses = BENEFIC_POINTS[key]
                
                for house in benefic_houses:
                    # Calculate target sign
                    # Target = (SourceRasi + House - 1) % 12
                    # If result is 0, it means 12 (Pisces)
                    target_sign = (source_rasi + house - 1) % 12
                    if target_sign == 0:
                        target_sign = 12
                        
                    sarvashtaka[target_sign] += 1
                    
    return sarvashtaka


def get_bhinnashtakavarga(planet_name: str, astro_time: AstroTime) -> dict[int, int]:
    """
    Calculates the Bhinnashtakavarga (individual Ashtakavarga) for a specific planet.
    Shows how this planet gains benefic points from all sources across 12 signs.
    
    Args:
        planet_name: Name of planet ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        astro_time: AstroTime object
        
    Returns:
        Dictionary {SignNumber (1-12): Points} for this planet only
    """
    
    # 1. Calculate Rasi Numbers for all Planets + Ascendant
    positions = {}
    
    # Planets
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]:
        long = get_planet_longitude(planet, astro_time)
        _, rasi_num = get_rasi(long)
        positions[planet.name] = rasi_num
        
    # Ascendant
    lagnam_long = get_lagnam(astro_time)
    _, lagnam_num = get_rasi(lagnam_long)
    positions["Ascendant"] = lagnam_num
    
    # 2. Initialize Points Dictionary for this planet only
    bav = {i: 0 for i in range(1, 13)}
    
    # 3. Calculate Points from all sources
    for source_planet, source_rasi in positions.items():
        key = (planet_name, source_planet)
        if key in BENEFIC_POINTS:
            benefic_houses = BENEFIC_POINTS[key]
            
            for house in benefic_houses:
                # Calculate target sign
                target_sign = (source_rasi + house - 1) % 12
                if target_sign == 0:
                    target_sign = 12
                    
                bav[target_sign] += 1
                    
    return bav


def get_all_bhinnashtakavarga(astro_time: AstroTime) -> dict[str, dict[int, int]]:
    """
    Calculates Bhinnashtakavarga for all 7 planets.
    
    Returns:
        Dictionary with planet names as keys, each containing {SignNumber: Points}
        Example: {
            "Sun": {1: 3, 2: 4, 3: 5, ...},
            "Moon": {1: 4, 2: 3, 3: 6, ...},
            ...
        }
    """
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    return {planet: get_bhinnashtakavarga(planet, astro_time) for planet in planets}


def get_bhinnashtakavarga_with_sources(planet_name: str, astro_time: AstroTime) -> dict[int, dict[str, int]]:
    """
    Calculates detailed Bhinnashtakavarga showing contribution from each source planet.
    
    Args:
        planet_name: Name of planet ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        astro_time: AstroTime object
        
    Returns:
        Dictionary {SignNumber (1-12): {SourcePlanet: PointCount}}
        Example: {
            1: {"Sun": 1, "Moon": 0, "Mars": 1, "Mercury": 0, ...},
            2: {"Sun": 1, "Moon": 1, "Mars": 0, "Mercury": 1, ...},
            ...
        }
    """
    
    # 1. Calculate Rasi Numbers for all Planets + Ascendant
    positions = {}
    
    # Planets
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]:
        long = get_planet_longitude(planet, astro_time)
        _, rasi_num = get_rasi(long)
        positions[planet.name] = rasi_num
        
    # Ascendant
    lagnam_long = get_lagnam(astro_time)
    _, lagnam_num = get_rasi(lagnam_long)
    positions["Ascendant"] = lagnam_num
    
    # 2. Initialize detailed structure
    source_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ascendant"]
    bav_detailed = {i: {source: 0 for source in source_names} for i in range(1, 13)}
    
    # 3. Calculate Points from each source
    for source_planet, source_rasi in positions.items():
        key = (planet_name, source_planet)
        if key in BENEFIC_POINTS:
            benefic_houses = BENEFIC_POINTS[key]
            
            for house in benefic_houses:
                # Calculate target sign
                target_sign = (source_rasi + house - 1) % 12
                if target_sign == 0:
                    target_sign = 12
                    
                bav_detailed[target_sign][source_planet] = 1
                    
    return bav_detailed
