
RASIS = [
    "Aries (Mesha)", "Taurus (Vrishabha)", "Gemini (Mithuna)", "Cancer (Karka)", 
    "Leo (Simha)", "Virgo (Kanya)", "Libra (Tula)", "Scorpio (Vrishchika)", 
    "Sagittarius (Dhanu)", "Capricorn (Makara)", "Aquarius (Kumbha)", "Pisces (Meena)"
]

# Short names for Jaimini/compact display
RASI_NAMES = RASIS  # Alias for compatibility

def get_rasi(longitude: float) -> tuple[str, int]:
    """
    Returns (Rasi Name, Rasi Number 1-12) from a longitude.
    """
    # Normalize longitude
    longitude = longitude % 360
    index = int(longitude / 30)
    return RASIS[index], index + 1

def get_gochara_house(birth_rasi_num: int, transit_rasi_num: int) -> int:
    """
    Calculates the house of the transit planet relative to the birth rasi (Janma Rasi).
    Returns a number between 1 and 12.
    """
    # Vedic Astrology counts inclusively. 
    # If Birth is Aries (1) and Transit is Aries (1), it's the 1st House.
    # If Birth is Aries (1) and Transit is Taurus (2), it's the 2nd House.
    
    diff = transit_rasi_num - birth_rasi_num
    
    # Adjust for negative difference (wrapping around the zodiac)
    if diff < 0:
        diff += 12
        
    # Add 1 because counting starts from the birth sign itself
    return diff + 1
