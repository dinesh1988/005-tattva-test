"""
Varga Chakras (Divisional Charts) - Shodashvarga (16 Divisional Charts)
Each Varga divides a sign into specific portions to reveal different life aspects.
"""

from logic.rasi import RASIS

def get_d1_rasi(longitude: float) -> tuple[str, int]:
    """
    D-1 Rasi Chart (Main Birth Chart)
    Each sign = 30°
    """
    longitude = longitude % 360
    index = int(longitude / 30)
    return RASIS[index], index + 1


def get_d2_hora(longitude: float) -> tuple[str, int]:
    """
    D-2 Hora Chart (Wealth)
    Each sign divided into 2 parts of 15° each.
    Odd signs: 0-15° = Leo, 15-30° = Cancer
    Even signs: 0-15° = Cancer, 15-30° = Leo
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1  # 1-12
    degree_in_sign = longitude % 30
    
    is_odd_sign = (sign_num % 2 == 1)
    first_half = (degree_in_sign < 15)
    
    if is_odd_sign:
        hora_sign = 5 if first_half else 4  # Leo or Cancer
    else:
        hora_sign = 4 if first_half else 5  # Cancer or Leo
    
    return RASIS[hora_sign - 1], hora_sign


def get_d3_drekkana(longitude: float) -> tuple[str, int]:
    """
    D-3 Drekkana Chart (Siblings/Courage)
    Each sign divided into 3 parts of 10° each.
    1st Drekkana (0-10°): Same sign
    2nd Drekkana (10-20°): 5th from sign
    3rd Drekkana (20-30°): 9th from sign
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    if degree_in_sign < 10:
        drekkana_sign = sign_num
    elif degree_in_sign < 20:
        drekkana_sign = ((sign_num - 1 + 4) % 12) + 1  # 5th from sign
    else:
        drekkana_sign = ((sign_num - 1 + 8) % 12) + 1  # 9th from sign
    
    return RASIS[drekkana_sign - 1], drekkana_sign


def get_d4_chaturthamsa(longitude: float) -> tuple[str, int]:
    """
    D-4 Chaturthamsa Chart (Property/Fortune)
    Each sign divided into 4 parts of 7°30' each.
    Follows element pattern: Cardinal -> Fixed -> Mutable -> Cardinal
    
    Pattern:
    - Cardinal signs (Ari,Can,Lib,Cap): Cycle through all 4 cardinal signs
    - Fixed signs (Tau,Leo,Sco,Aqu): Cycle through all 4 fixed signs
    - Mutable signs (Gem,Vir,Sag,Pis): Cycle through all 4 mutable signs
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 7.5)  # 0, 1, 2, or 3
    
    # Determine sign type (Cardinal=1, Fixed=2, Mutable=3)
    sign_type = ((sign_num - 1) % 3) + 1
    
    # Cardinal signs: Aries(1), Cancer(4), Libra(7), Capricorn(10)
    # Fixed signs: Taurus(2), Leo(5), Scorpio(8), Aquarius(11)
    # Mutable signs: Gemini(3), Virgo(6), Sagittarius(9), Pisces(12)
    
    if sign_type == 1:  # Cardinal signs
        cardinal_signs = [1, 4, 7, 10]  # Ari, Can, Lib, Cap
        chaturthamsa_sign = cardinal_signs[part]
    elif sign_type == 2:  # Fixed signs
        fixed_signs = [2, 5, 8, 11]  # Tau, Leo, Sco, Aqu
        chaturthamsa_sign = fixed_signs[part]
    else:  # Mutable signs (sign_type == 3)
        mutable_signs = [3, 6, 9, 12]  # Gem, Vir, Sag, Pis
        chaturthamsa_sign = mutable_signs[part]
    
    return RASIS[chaturthamsa_sign - 1], chaturthamsa_sign


def get_d5_panchamsa(longitude: float) -> tuple[str, int]:
    """
    D-5 Panchamsa Chart (Spiritual Merit/Fame/Power)
    Each sign divided into 5 parts of 6° each.
    Odd signs: Start from Aries -> Leo -> Sagittarius -> Aries -> Leo
    Even signs: Start from Taurus -> Virgo -> Capricorn -> Taurus -> Virgo
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 6)  # 0-4
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        # Odd signs cycle through Fire signs: Aries(1), Leo(5), Sag(9)
        start_signs = [1, 5, 9, 1, 5]
    else:
        # Even signs cycle through Earth signs: Taurus(2), Virgo(6), Cap(10)
        start_signs = [2, 6, 10, 2, 6]
    
    panchamsa_sign = start_signs[part]
    
    return RASIS[panchamsa_sign - 1], panchamsa_sign


def get_d6_shashtamsa(longitude: float) -> tuple[str, int]:
    """
    D-6 Shashtamsa Chart (Health/Enemies/Debts)
    Each sign divided into 6 parts of 5° each.
    Starts from the sign itself.
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 5)  # 0-5
    shashtamsa_sign = ((sign_num - 1 + part) % 12) + 1
    
    return RASIS[shashtamsa_sign - 1], shashtamsa_sign


def get_d7_saptamsa(longitude: float) -> tuple[str, int]:
    """
    D-7 Saptamsa Chart (Children)
    Each sign divided into 7 parts of 4°17'8.57" each.
    Odd signs: Start from same sign
    Even signs: Start from 7th sign
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/7))  # 0-6
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        start_sign = sign_num
    else:
        start_sign = ((sign_num - 1 + 6) % 12) + 1  # 7th from sign
    
    saptamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[saptamsa_sign - 1], saptamsa_sign


def get_d8_ashtamsa(longitude: float) -> tuple[str, int]:
    """
    D-8 Ashtamsa Chart (Longevity/Sudden Events/Accidents)
    Each sign divided into 8 parts of 3°45' each.
    Movable signs: Start from Aries
    Fixed signs: Start from Sagittarius
    Dual signs: Start from Leo
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 3.75)  # 0-7
    
    quality = (sign_num - 1) % 3  # 0=Movable, 1=Fixed, 2=Dual
    
    if quality == 0:  # Movable
        start_sign = 1  # Aries
    elif quality == 1:  # Fixed
        start_sign = 9  # Sagittarius
    else:  # Dual
        start_sign = 5  # Leo
    
    ashtamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[ashtamsa_sign - 1], ashtamsa_sign


def get_d9_navamsa(longitude: float) -> tuple[str, int]:
    """
    D-9 Navamsa Chart (Spouse/Dharma) - Most important after D-1
    Each sign divided into 9 parts of 3°20' each.
    Fire signs (Ari, Leo, Sag): Start from Aries
    Earth signs (Tau, Vir, Cap): Start from Capricorn
    Air signs (Gem, Lib, Aqu): Start from Libra
    Water signs (Can, Sco, Pis): Start from Cancer
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/9))  # 0-8
    
    # Determine element of the sign
    element = (sign_num - 1) % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
    
    if element == 0:  # Fire
        start_sign = 1  # Aries
    elif element == 1:  # Earth
        start_sign = 10  # Capricorn
    elif element == 2:  # Air
        start_sign = 7  # Libra
    else:  # Water
        start_sign = 4  # Cancer
    
    navamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[navamsa_sign - 1], navamsa_sign


def get_d10_dasamsa(longitude: float) -> tuple[str, int]:
    """
    D-10 Dasamsa Chart (Career/Profession)
    Each sign divided into 10 parts of 3° each.
    Odd signs: Start from same sign
    Even signs: Start from 9th sign
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 3)  # 0-9
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        start_sign = sign_num
    else:
        start_sign = ((sign_num - 1 + 8) % 12) + 1  # 9th from sign
    
    dasamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[dasamsa_sign - 1], dasamsa_sign


def get_d11_ekadasamsa(longitude: float) -> tuple[str, int]:
    """
    D-11 Ekadasamsa/Rudramsa Chart (Death/Destruction/Dangers)
    Each sign divided into 11 parts of 2°43'38" each.
    Starts from the sign itself.
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/11))  # 0-10
    ekadasamsa_sign = ((sign_num - 1 + part) % 12) + 1
    
    return RASIS[ekadasamsa_sign - 1], ekadasamsa_sign


def get_d12_dwadasamsa(longitude: float) -> tuple[str, int]:
    """
    D-12 Dwadasamsa Chart (Parents)
    Each sign divided into 12 parts of 2°30' each.
    Starts from the sign itself.
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 2.5)  # 0-11
    dwadasamsa_sign = ((sign_num - 1 + part) % 12) + 1
    
    return RASIS[dwadasamsa_sign - 1], dwadasamsa_sign


def get_d16_shodasamsa(longitude: float) -> tuple[str, int]:
    """
    D-16 Shodasamsa Chart (Vehicles/Comforts/Happiness)
    Each sign divided into 16 parts of 1°52'30" each.
    Movable signs: Start from Aries
    Fixed signs: Start from Leo
    Dual signs: Start from Sagittarius
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/16))  # 0-15
    
    # Determine sign quality (Movable=0, Fixed=1, Dual=2)
    quality = (sign_num - 1) % 3
    
    if quality == 0:  # Movable (Aries, Cancer, Libra, Capricorn)
        start_sign = 1  # Aries
    elif quality == 1:  # Fixed (Taurus, Leo, Scorpio, Aquarius)
        start_sign = 5  # Leo
    else:  # Dual (Gemini, Virgo, Sagittarius, Pisces)
        start_sign = 9  # Sagittarius
    
    shodasamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[shodasamsa_sign - 1], shodasamsa_sign


def get_d20_vimsamsa(longitude: float) -> tuple[str, int]:
    """
    D-20 Vimsamsa Chart (Spiritual Progress/Upasana)
    Each sign divided into 20 parts of 1°30' each.
    Movable signs: Start from Aries
    Fixed signs: Start from Sagittarius
    Dual signs: Start from Leo
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 1.5)  # 0-19
    
    quality = (sign_num - 1) % 3
    
    if quality == 0:  # Movable
        start_sign = 1  # Aries
    elif quality == 1:  # Fixed
        start_sign = 9  # Sagittarius
    else:  # Dual
        start_sign = 5  # Leo
    
    vimsamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[vimsamsa_sign - 1], vimsamsa_sign


def get_d24_chaturvimsamsa(longitude: float) -> tuple[str, int]:
    """
    D-24 Chaturvimsamsa/Siddhamsa Chart (Education/Learning)
    Each sign divided into 24 parts of 1°15' each.
    Odd signs: Start from Leo
    Even signs: Start from Cancer
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 1.25)  # 0-23
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        start_sign = 5  # Leo
    else:
        start_sign = 4  # Cancer
    
    siddhamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[siddhamsa_sign - 1], siddhamsa_sign


def get_d27_bhamsa(longitude: float) -> tuple[str, int]:
    """
    D-27 Saptavimsamsa/Bhamsa Chart (Strength/Weakness)
    Each sign divided into 27 parts of 1°6'40" each.
    Fire signs: Start from Aries
    Earth signs: Start from Cancer
    Air signs: Start from Libra
    Water signs: Start from Capricorn
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/27))  # 0-26
    
    element = (sign_num - 1) % 4
    
    if element == 0:  # Fire
        start_sign = 1  # Aries
    elif element == 1:  # Earth
        start_sign = 4  # Cancer
    elif element == 2:  # Air
        start_sign = 7  # Libra
    else:  # Water
        start_sign = 10  # Capricorn
    
    bhamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[bhamsa_sign - 1], bhamsa_sign


def get_d30_trimsamsa(longitude: float) -> tuple[str, int]:
    """
    D-30 Trimsamsa Chart (Evils/Misfortunes)
    Special division - not equal parts.
    Odd signs: Mars(5°), Saturn(5°), Jupiter(8°), Mercury(7°), Venus(5°)
    Even signs: Venus(5°), Mercury(7°), Jupiter(8°), Saturn(5°), Mars(5°)
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        # Mars=Aries, Saturn=Aquarius, Jupiter=Sagittarius, Mercury=Gemini, Venus=Libra
        if degree_in_sign < 5:
            trimsamsa_sign = 1  # Aries (Mars)
        elif degree_in_sign < 10:
            trimsamsa_sign = 11  # Aquarius (Saturn)
        elif degree_in_sign < 18:
            trimsamsa_sign = 9  # Sagittarius (Jupiter)
        elif degree_in_sign < 25:
            trimsamsa_sign = 3  # Gemini (Mercury)
        else:
            trimsamsa_sign = 7  # Libra (Venus)
    else:
        # Venus=Taurus, Mercury=Virgo, Jupiter=Pisces, Saturn=Capricorn, Mars=Scorpio
        if degree_in_sign < 5:
            trimsamsa_sign = 2  # Taurus (Venus)
        elif degree_in_sign < 12:
            trimsamsa_sign = 6  # Virgo (Mercury)
        elif degree_in_sign < 20:
            trimsamsa_sign = 12  # Pisces (Jupiter)
        elif degree_in_sign < 25:
            trimsamsa_sign = 10  # Capricorn (Saturn)
        else:
            trimsamsa_sign = 8  # Scorpio (Mars)
    
    return RASIS[trimsamsa_sign - 1], trimsamsa_sign


def get_d40_khavedamsa(longitude: float) -> tuple[str, int]:
    """
    D-40 Khavedamsa Chart (Auspicious/Inauspicious Effects - Maternal Legacy)
    Each sign divided into 40 parts of 0°45' each.
    Odd signs: Start from Aries
    Even signs: Start from Libra
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 0.75)  # 0-39
    is_odd_sign = (sign_num % 2 == 1)
    
    if is_odd_sign:
        start_sign = 1  # Aries
    else:
        start_sign = 7  # Libra
    
    khavedamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[khavedamsa_sign - 1], khavedamsa_sign


def get_d45_akshavedamsa(longitude: float) -> tuple[str, int]:
    """
    D-45 Akshavedamsa Chart (General Well-being - Paternal Legacy)
    Each sign divided into 45 parts of 0°40' each.
    Movable signs: Start from Aries
    Fixed signs: Start from Leo
    Dual signs: Start from Sagittarius
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / (30/45))  # 0-44
    
    quality = (sign_num - 1) % 3  # 0=Movable, 1=Fixed, 2=Dual
    
    if quality == 0:  # Movable
        start_sign = 1  # Aries
    elif quality == 1:  # Fixed
        start_sign = 5  # Leo
    else:  # Dual
        start_sign = 9  # Sagittarius
    
    akshavedamsa_sign = ((start_sign - 1 + part) % 12) + 1
    
    return RASIS[akshavedamsa_sign - 1], akshavedamsa_sign


def get_d60_shashtiamsa(longitude: float) -> tuple[str, int]:
    """
    D-60 Shashtiamsa Chart (Past Life Karma) - Most subtle division
    Each sign divided into 60 parts of 0°30' each.
    Starts from the sign itself.
    """
    longitude = longitude % 360
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    part = int(degree_in_sign / 0.5)  # 0-59
    shashtiamsa_sign = ((sign_num - 1 + part) % 12) + 1
    
    return RASIS[shashtiamsa_sign - 1], shashtiamsa_sign


# Dictionary of all Varga charts with their meanings
VARGA_CHARTS = {
    "D-1": ("Rasi", "Main Chart", get_d1_rasi),
    "D-2": ("Hora", "Wealth", get_d2_hora),
    "D-3": ("Drekkana", "Siblings/Courage", get_d3_drekkana),
    "D-4": ("Chaturthamsa", "Property/Fortune", get_d4_chaturthamsa),
    "D-5": ("Panchamsa", "Spiritual Merit/Fame", get_d5_panchamsa),
    "D-6": ("Shashtamsa", "Health/Enemies", get_d6_shashtamsa),
    "D-7": ("Saptamsa", "Children", get_d7_saptamsa),
    "D-8": ("Ashtamsa", "Longevity/Accidents", get_d8_ashtamsa),
    "D-9": ("Navamsa", "Spouse/Dharma", get_d9_navamsa),
    "D-10": ("Dasamsa", "Career", get_d10_dasamsa),
    "D-11": ("Ekadasamsa", "Death/Dangers", get_d11_ekadasamsa),
    "D-12": ("Dwadasamsa", "Parents", get_d12_dwadasamsa),
    "D-16": ("Shodasamsa", "Vehicles/Comforts", get_d16_shodasamsa),
    "D-20": ("Vimsamsa", "Spirituality", get_d20_vimsamsa),
    "D-24": ("Chaturvimsamsa", "Education", get_d24_chaturvimsamsa),
    "D-27": ("Bhamsa", "Strength/Weakness", get_d27_bhamsa),
    "D-30": ("Trimsamsa", "Evils/Misfortunes", get_d30_trimsamsa),
    "D-40": ("Khavedamsa", "Maternal Legacy", get_d40_khavedamsa),
    "D-45": ("Akshavedamsa", "Paternal Legacy", get_d45_akshavedamsa),
    "D-60": ("Shashtiamsa", "Past Life Karma", get_d60_shashtiamsa),
}


def get_all_vargas(longitude: float) -> dict:
    """
    Calculate all Varga positions for a given longitude.
    Returns a dictionary with Varga name as key and (sign_name, sign_num) as value.
    """
    result = {}
    for varga_key, (name, meaning, func) in VARGA_CHARTS.items():
        sign_name, sign_num = func(longitude)
        result[varga_key] = {
            "name": name,
            "meaning": meaning,
            "sign": sign_name,
            "sign_num": sign_num
        }
    return result
