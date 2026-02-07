
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", 
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", 
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def get_nakshatra(longitude: float) -> tuple[str, int, float, int]:
    """
    Calculates the Nakshatra from a given longitude (Nirayana).
    Returns: (Nakshatra Name, Nakshatra Number (1-27), Percentage Traversed, Pada (1-4))
    """
    # Each Nakshatra is 13 degrees 20 minutes = 13.3333... degrees
    # 360 / 27 = 13.333333333333334
    
    nakshatra_span = 360.0 / 27.0
    
    # Normalize longitude just in case
    longitude = longitude % 360
    
    index = int(longitude / nakshatra_span)
    name = NAKSHATRAS[index]
    
    # Calculate percentage traversed in the Nakshatra
    degrees_in_nakshatra = longitude % nakshatra_span
    percentage = (degrees_in_nakshatra / nakshatra_span) * 100
    
    # Calculate Pada (1-4)
    # 0-25% = 1, 25-50% = 2, 50-75% = 3, 75-100% = 4
    pada = int(percentage / 25) + 1
    
    return name, index + 1, percentage, pada

TARAS = [
    "Janma (Birth)", "Sampat (Wealth)", "Vipat (Danger)", "Kshema (Well-being)", 
    "Pratyak (Obstacles)", "Sadhana (Achievement)", "Naidhana (Death/Danger)", 
    "Mitra (Friend)", "Parama Mitra (Best Friend)"
]

def get_tara_bala(birth_nakshatra_num: int, transit_nakshatra_num: int) -> tuple[str, int]:
    """
    Calculates Tara Bala between birth nakshatra and transit nakshatra.
    Returns (Tara Name, Tara Number 1-9)
    """
    # Calculate distance (inclusive)
    distance = transit_nakshatra_num - birth_nakshatra_num + 1
    
    if distance <= 0:
        distance += 27
        
    tara_num = distance % 9
    if tara_num == 0:
        tara_num = 9
        
    return TARAS[tara_num - 1], tara_num
