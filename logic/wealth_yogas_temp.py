# Temporary file with new wealth yoga functions to be added to yogas.py

def check_chatussagara_yoga(time: 'AstroTime') -> Yoga:
    """
    Chatussagara Yoga - All Four Kendras Occupied (Four Oceans)
    
    Formation: Planets occupying all four kendra houses (1st, 4th, 7th, 10th)
    "Chatussagara" literally means "four oceans" - representing completeness
    and abundance from all directions.
    
    Effect: Highly learned, powerful, commander of forces, wealth from
    multiple sources, well-rounded success, virtuous, famous. This yoga
    indicates support from all four directions of life.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1985, 3, 20, 10, 15, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 19.0760, 72.8777)
        >>> yoga = check_chatussagara_yoga(time)
        >>> print(yoga.occurring)
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    try:
        # Get Lagna to determine house positions
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Track which kendra houses have planets
        kendras_occupied = {1: False, 4: False, 7: False, 10: False}
        
        # Check all planets (excluding Rahu/Ketu for traditional calculation)
        planets_to_check = [
            Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
            Planet.Jupiter, Planet.Venus, Planet.Saturn
        ]
        
        planet_details = []
        
        for planet in planets_to_check:
            planet_long = get_planet_longitude(planet, time)
            planet_sign = int(planet_long // 30)
            house = ((planet_sign - lagna_sign) % 12) + 1
            
            # Mark kendra as occupied if planet is there
            if house in kendras_occupied:
                kendras_occupied[house] = True
                planet_details.append(f"{planet.name} in {house}th")
        
        # Check if all four kendras are occupied
        all_kendras_occupied = all(kendras_occupied.values())
        
        if all_kendras_occupied:
            condition = f"All 4 kendras occupied: {', '.join(planet_details[:4])}"
        else:
            occupied_kendras = [k for k, v in kendras_occupied.items() if v]
            condition = f"Only {len(occupied_kendras)} kendras occupied: {occupied_kendras}"
        
        return Yoga(
            name="Chatussagara Yoga",
            nature=YogaNature.GOOD,
            occurring=all_kendras_occupied,
            description="Highly learned, powerful, commander, wealth from multiple sources",
            condition=condition,
            strength=100 if all_kendras_occupied else len([v for v in kendras_occupied.values() if v]) * 25
        )
    
    except Exception as e:
        return Yoga(
            name="Chatussagara Yoga",
            nature=YogaNature.GOOD,
            occurring=False,
            description="Highly learned, powerful, commander, wealth from multiple sources",
            condition=f"Error: {str(e)}",
            strength=0
        )


def check_vasumathi_yoga(time: 'AstroTime') -> Yoga:
    """
    Vasumathi Yoga - Benefics in Upachaya Houses
    
    Formation: Benefic planets (Jupiter, Venus, Mercury, or waxing Moon)
    occupying upachaya houses (3rd, 6th, 10th, 11th). These are "growth"
    houses where planets improve over time.
    
    Effect: Prosperous, wealth accumulation, rise in life, increasing fortune,
    success through efforts. This yoga indicates steady growth of wealth.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1988, 7, 15, 9, 45, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 12.9716, 77.5946)
        >>> yoga = check_vasumathi_yoga(time)
        >>> print(yoga.occurring)
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    try:
        # Get Lagna to determine house positions
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Upachaya houses (growth houses): 3, 6, 10, 11
        upachaya_houses = [3, 6, 10, 11]
        
        # Get Moon phase to determine if waxing (benefic) or waning (malefic)
        sun_long = get_planet_longitude(Planet.Sun, time)
        moon_long = get_planet_longitude(Planet.Moon, time)
        elongation = (moon_long - sun_long) % 360
        is_moon_waxing = 0 < elongation < 180
        
        # Benefic planets: Jupiter, Venus, Mercury, + waxing Moon
        benefics_to_check = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        if is_moon_waxing:
            benefics_to_check.append(Planet.Moon)
        
        benefics_in_upachaya = []
        
        for planet in benefics_to_check:
            planet_long = get_planet_longitude(planet, time)
            planet_sign = int(planet_long // 30)
            house = ((planet_sign - lagna_sign) % 12) + 1
            
            if house in upachaya_houses:
                benefics_in_upachaya.append(f"{planet.name} in {house}th")
        
        # Yoga forms if any benefic is in upachaya houses
        occurring = len(benefics_in_upachaya) > 0
        
        if occurring:
            condition = f"{len(benefics_in_upachaya)} benefic(s) in upachaya: {', '.join(benefics_in_upachaya)}"
        else:
            condition = "No benefics in upachaya houses (3,6,10,11)"
        
        # Strength based on number of benefics in upachaya
        strength = min(100, len(benefics_in_upachaya) * 25)
        
        return Yoga(
            name="Vasumathi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Prosperous, wealth accumulation, rise in life, increasing fortune",
            condition=condition,
            strength=strength
        )
    
    except Exception as e:
        return Yoga(
            name="Vasumathi Yoga",
            nature=YogaNature.GOOD,
            occurring=False,
            description="Prosperous, wealth accumulation, rise in life",
            condition=f"Error: {str(e)}",
            strength=0
        )


def check_parvata_yoga(time: 'AstroTime') -> Yoga:
    """
    Parvata Yoga - Mountain of Success
    
    Formation: Benefics in kendras (1,4,7,10) AND either the lord of the
    ascendant or lord of 7th house in a kendra or trikona (1,5,9) with dignity.
    
    Effect: Charitable, wealthy, head of community, leader, generous, happy,
    famous, commands respect. "Parvata" means mountain - indicates stable,
    towering success.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1980, 11, 25, 8, 30, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 28.7041, 77.1025)
        >>> yoga = check_parvata_yoga(time)
        >>> print(yoga.occurring)
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .lordship import get_lord_of_house
    from .consts import Planet
    from .avastha import is_in_dignity
    
    try:
        # Get Lagna
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Part 1: Check if benefics are in kendras (1,4,7,10)
        kendra_houses = [1, 4, 7, 10]
        trikona_and_kendra = [1, 4, 5, 7, 9, 10]  # For lord check
        
        # Check benefics in kendras
        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        benefics_in_kendras = []
        
        for planet in benefics:
            planet_long = get_planet_longitude(planet, time)
            planet_sign = int(planet_long // 30)
            house = ((planet_sign - lagna_sign) % 12) + 1
            
            if house in kendra_houses:
                benefics_in_kendras.append(f"{planet.name} in {house}th")
        
        # Need at least one benefic in kendra
        has_benefics_in_kendra = len(benefics_in_kendras) > 0
        
        # Part 2: Check if lagna lord or 7th lord is in kendra/trikona with dignity
        lagna_lord = get_lord_of_house(1, time)
        seventh_lord = get_lord_of_house(7, time)
        
        lord_conditions_met = False
        lord_details = []
        
        for house_num, lord in [(1, lagna_lord), (7, seventh_lord)]:
            lord_long = get_planet_longitude(lord, time)
            lord_sign = int(lord_long // 30)
            lord_house = ((lord_sign - lagna_sign) % 12) + 1
            
            # Check if in kendra or trikona
            if lord_house in trikona_and_kendra:
                # Check dignity (own sign, exaltation, or moolatrikona)
                in_dignity = is_in_dignity(lord, time)
                
                if in_dignity:
                    lord_conditions_met = True
                    lord_details.append(f"{lord.name} (lord of {house_num}) in {lord_house}th with dignity")
        
        # Both conditions must be met
        occurring = has_benefics_in_kendra and lord_conditions_met
        
        if occurring:
            condition = f"Benefics in kendras: {', '.join(benefics_in_kendras)}. Lord condition: {', '.join(lord_details)}"
        elif has_benefics_in_kendra:
            condition = f"Benefics in kendras but lord not in kendra/trikona with dignity"
        elif lord_conditions_met:
            condition = f"Lord in good position but no benefics in kendras"
        else:
            condition = "Neither condition met"
        
        return Yoga(
            name="Parvata Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Charitable, wealthy, head of community, leader, generous, famous",
            condition=condition,
            strength=100 if occurring else 0
        )
    
    except Exception as e:
        return Yoga(
            name="Parvata Yoga",
            nature=YogaNature.GOOD,
            occurring=False,
            description="Charitable, wealthy, head of community",
            condition=f"Error: {str(e)}",
            strength=0
        )
