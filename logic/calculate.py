import swisseph as swe
import os
from .consts import Planet
from .time import AstroTime

# Set path to ephemeris files
# Assuming 'ephe' folder is in the parent directory of 'logic'
current_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(os.path.dirname(current_dir), 'ephe')
swe.set_ephe_path(ephe_path)

def get_planet_longitude(planet: Planet, time: AstroTime):
    """
    Calculates the Nirayana (Sidereal) Longitude of a planet.
    """
    
    # Map Custom Enum to SwissEph ID
    swe_id = -1
    if planet == Planet.Sun: swe_id = swe.SUN
    elif planet == Planet.Moon: swe_id = swe.MOON
    elif planet == Planet.Mars: swe_id = swe.MARS
    elif planet == Planet.Mercury: swe_id = swe.MERCURY
    elif planet == Planet.Jupiter: swe_id = swe.JUPITER
    elif planet == Planet.Venus: swe_id = swe.VENUS
    elif planet == Planet.Saturn: swe_id = swe.SATURN
    elif planet == Planet.Rahu: swe_id = swe.MEAN_NODE # Using Mean Node for Rahu
    elif planet == Planet.Ketu: swe_id = swe.MEAN_NODE # Ketu is opposite Rahu
    
    if swe_id == -1:
        raise ValueError(f"Planet {planet} not supported yet.")

    # 1. Get Tropical (Sayana) Position
    # FLG_SWIEPH: Use Swiss Ephemeris
    # FLG_SPEED: Calculate speed (not strictly needed for longitude but good practice)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # calc_ut takes Julian Day in UT
    output = swe.calc_ut(time.julian_day, swe_id, flags)
    
    # output is ((long, lat, dist, speed_long, speed_lat, speed_dist), rflag)
    sayana_long = output[0][0] # Longitude is the first element of the first tuple
    
    # Handle Ketu (Opposite of Rahu)
    if planet == Planet.Ketu:
        sayana_long = (sayana_long + 180) % 360

    # 2. Get Ayanamsa (Lahiri is standard in Vedic)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(time.julian_day)

    # 3. Calculate Sidereal (Nirayana) Longitude
    nirayana_long = (sayana_long - ayanamsa) % 360
    
    # Normalize to 0-360
    if nirayana_long < 0:
        nirayana_long += 360
        
    return nirayana_long

def get_lagnam(time: AstroTime):
    """
    Calculates the Nirayana (Sidereal) Ascendant (Lagnam).
    """
    # swe.houses returns (cusps, ascmc)
    # ascmc = (ascendant, mc, armc, vertex, equasc, coasc, mooncross, nodecross)
    # We need the Ascendant (index 0)
    
    # Note: swe.houses requires lat/lon. AstroTime has them.
    # 'P' is Placidus, but for Ascendant point it doesn't matter which system is used
    # as the Ascendant is the intersection of Ecliptic and Horizon.
    
    cusps, ascmc = swe.houses(time.julian_day, time.lat, time.lon, b'P')
    tropical_ascendant = ascmc[0]
    
    # Get Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(time.julian_day)
    
    # Calculate Sidereal Ascendant
    nirayana_ascendant = (tropical_ascendant - ayanamsa) % 360
    
    if nirayana_ascendant < 0:
        nirayana_ascendant += 360
        
    return nirayana_ascendant
