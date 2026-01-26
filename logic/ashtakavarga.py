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
