"""
Ashtakavarga Storage Helper Functions
======================================
Converts Ashtakavarga calculations into storage-ready JSON format.
"""

from logic.ashtakavarga import get_all_bhinnashtakavarga, get_sarvashtakavarga_points
from logic.time import AstroTime
from logic.rasi import RASIS

def get_ashtakavarga_for_storage(astro_time: AstroTime) -> dict:
    """
    Returns Ashtakavarga data in storage-ready format.
    
    This is computationally intensive, so should be calculated once
    and stored in the database for quick retrieval during transits.
    
    Returns:
        {
            "sarvashtakavarga": {"Aries": 28, "Taurus": 31, ...},
            "bhinnashtakavarga": {
                "Sun": {"Aries": 4, "Taurus": 6, ...},
                "Moon": {"Aries": 4, "Taurus": 5, ...},
                ...
            }
        }
    """
    
    # Get SAV (Total points per sign)
    sav_numeric = get_sarvashtakavarga_points(astro_time)
    sarvashtakavarga = {RASIS[i-1]: sav_numeric[i] for i in range(1, 13)}
    
    # Get BAV (Individual planet points per sign)
    bav_numeric = get_all_bhinnashtakavarga(astro_time)
    bhinnashtakavarga = {}
    
    for planet, points_dict in bav_numeric.items():
        bhinnashtakavarga[planet] = {RASIS[i-1]: points_dict[i] for i in range(1, 13)}
    
    return {
        "sarvashtakavarga": sarvashtakavarga,
        "bhinnashtakavarga": bhinnashtakavarga
    }


def get_sarvashtakavarga_named(astro_time: AstroTime) -> dict[str, int]:
    """
    Returns Sarvashtakavarga with sign names instead of numbers.
    
    Returns:
        {"Aries": 28, "Taurus": 31, "Gemini": 22, ...}
    
    Usage:
        When Moon enters Taurus tomorrow, query this to see "31" (Excellent)
        without recalculation.
    """
    sav_numeric = get_sarvashtakavarga_points(astro_time)
    return {RASIS[i-1]: sav_numeric[i] for i in range(1, 13)}


def get_bhinnashtakavarga_named(astro_time: AstroTime) -> dict[str, dict[str, int]]:
    """
    Returns Bhinnashtakavarga with sign names instead of numbers.
    
    Returns:
        {
            "Sun": {"Aries": 4, "Taurus": 6, ...},
            "Moon": {"Aries": 4, "Taurus": 5, ...},
            ...
        }
    """
    bav_numeric = get_all_bhinnashtakavarga(astro_time)
    bav_named = {}
    
    for planet, points_dict in bav_numeric.items():
        bav_named[planet] = {RASIS[i-1]: points_dict[i] for i in range(1, 13)}
    
    return bav_named


def get_transit_quality(sign_name: str, sarvashtakavarga: dict[str, int]) -> str:
    """
    Get transit quality assessment based on SAV points.
    
    Args:
        sign_name: Sign name (e.g., "Taurus")
        sarvashtakavarga: Pre-calculated SAV dictionary
        
    Returns:
        Quality rating: "Excellent", "Good", "Average", "Challenging"
    """
    points = sarvashtakavarga.get(sign_name, 0)
    
    if points >= 30:
        return "Excellent"
    elif points >= 25:
        return "Good"
    elif points >= 20:
        return "Average"
    else:
        return "Challenging"


def get_planet_transit_quality(planet_name: str, sign_name: str, bhinnashtakavarga: dict) -> str:
    """
    Get specific planet's transit quality in a sign.
    
    Args:
        planet_name: Planet name (e.g., "Moon")
        sign_name: Sign name (e.g., "Taurus")
        bhinnashtakavarga: Pre-calculated BAV dictionary
        
    Returns:
        Quality rating based on bindus (points)
    """
    points = bhinnashtakavarga.get(planet_name, {}).get(sign_name, 0)
    
    if points >= 5:
        return "Excellent"
    elif points >= 4:
        return "Good"
    elif points >= 3:
        return "Average"
    else:
        return "Challenging"


# Example usage
if __name__ == "__main__":
    from datetime import datetime
    import pytz
    
    # Test data: 04/05/1991, 10:50 AM, Vellore
    lat, lon = 12.9165, 79.1325
    tz = pytz.timezone('Asia/Kolkata')
    dt = tz.localize(datetime(1991, 5, 4, 10, 50, 0))
    astro_time = AstroTime(dt, lat, lon)
    
    # Get storage-ready format
    av_data = get_ashtakavarga_for_storage(astro_time)
    
    print("\n=== STORAGE-READY ASHTAKAVARGA DATA ===\n")
    print("SARVASHTAKAVARGA (Total Points):")
    print(av_data["sarvashtakavarga"])
    
    print("\n\nBHINNASHTAKAVARGA (Individual Planet Points):")
    print(av_data["bhinnashtakavarga"])
    
    # Example: Check Moon's transit quality in Taurus
    print("\n\n=== TRANSIT QUALITY QUERIES ===")
    sav = av_data["sarvashtakavarga"]
    bav = av_data["bhinnashtakavarga"]
    
    print(f"\nGeneral transit quality in Taurus: {get_transit_quality('Taurus', sav)} ({sav['Taurus']} points)")
    print(f"Moon's transit quality in Taurus: {get_planet_transit_quality('Moon', 'Taurus', bav)} ({bav['Moon']['Taurus']} bindus)")
    
    # Show all signs
    print("\n\nALL SIGNS (SAV Points):")
    for sign, points in sav.items():
        quality = get_transit_quality(sign, sav)
        print(f"  {sign:12} : {points:2} points - {quality}")
