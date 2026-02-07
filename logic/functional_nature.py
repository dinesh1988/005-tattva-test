"""
Functional Benefic/Malefic Nature of Planets
Determines whether each planet is beneficial, malefic, or neutral for a specific ascendant
"""

# House lordship mapping: planet -> list of signs it rules
PLANET_LORDSHIPS = {
    'Sun': [5],      # Leo
    'Moon': [4],     # Cancer
    'Mars': [1, 8],  # Aries, Scorpio
    'Mercury': [3, 6],  # Gemini, Virgo
    'Jupiter': [9, 12],  # Sagittarius, Pisces
    'Venus': [2, 7],  # Taurus, Libra
    'Saturn': [10, 11],  # Capricorn, Aquarius
}

# Functional nature rules based on house lordship from ascendant
# Trikona lords (1,5,9) = Benefic
# Kendra lords (1,4,7,10) = Neutral to Benefic (except if natural malefic ruling only kendra)
# Dusthana lords (6,8,12) = Malefic
# Upachaya lords (3,6,10,11) = Mixed
# Yogakaraka = Ruling both Kendra and Trikona

def get_functional_nature(lagna_num: int) -> dict:
    """
    Calculate functional nature of all planets for a given ascendant.
    
    Args:
        lagna_num: Ascendant sign number (1=Aries, 2=Taurus, ..., 12=Pisces)
    
    Returns:
        Dictionary with planet names and their functional classifications
    """
    
    result = {}
    
    for planet, ruled_signs in PLANET_LORDSHIPS.items():
        # Calculate which houses this planet rules from the ascendant
        ruled_houses = []
        for sign in ruled_signs:
            # House = (Sign - Lagna + 1) mod 12, with 1-based indexing
            house = ((sign - lagna_num) % 12) + 1
            if house == 0:
                house = 12
            ruled_houses.append(house)
        
        # Determine functional nature based on house lordship
        nature = classify_functional_nature(planet, ruled_houses, lagna_num)
        
        result[planet] = {
            'nature': nature['classification'],
            'houses_ruled': sorted(ruled_houses),
            'reason': nature['reason'],
            'strength_impact': nature['strength_impact']
        }
    
    # Add Rahu and Ketu (shadow planets, no lordship but important)
    result['Rahu'] = {
        'nature': 'Neutral/Variable',
        'houses_ruled': [],
        'reason': 'Acts like Saturn; gives results of its dispositor and conjunctions',
        'strength_impact': 'Depends on placement and associations'
    }
    
    result['Ketu'] = {
        'nature': 'Neutral/Variable',
        'houses_ruled': [],
        'reason': 'Acts like Mars; gives results of its dispositor and conjunctions',
        'strength_impact': 'Depends on placement and associations'
    }
    
    return result


def classify_functional_nature(planet: str, houses: list, lagna_num: int) -> dict:
    """
    Classify planet's functional nature based on houses ruled.
    
    Returns:
        Dictionary with classification, reason, and strength impact
    """
    
    # Natural benefics and malefics
    natural_benefics = ['Jupiter', 'Venus', 'Mercury', 'Moon']
    natural_malefics = ['Sun', 'Mars', 'Saturn']
    
    is_natural_benefic = planet in natural_benefics
    
    # Trikona (Trines): 1, 5, 9 - Most benefic
    # Kendra (Angles): 1, 4, 7, 10 - Neutral to benefic
    # Dusthana (Evil): 6, 8, 12 - Malefic
    # Upachaya (Growth): 3, 6, 10, 11 - Mixed
    
    trikona_houses = [1, 5, 9]
    kendra_houses = [1, 4, 7, 10]
    dusthana_houses = [6, 8, 12]
    
    rules_trikona = any(h in trikona_houses for h in houses)
    rules_kendra = any(h in kendra_houses for h in houses)
    rules_dusthana = any(h in dusthana_houses for h in houses)
    
    # Check for Yogakaraka (ruling both Kendra and Trikona)
    rules_both = rules_trikona and rules_kendra
    
    # Special case: Saturn for Taurus and Libra (rules 9th and 10th = Yogakaraka)
    if planet == 'Saturn' and lagna_num in [2, 7]:  # Taurus or Libra
        return {
            'classification': 'Yogakaraka (Great Benefic)',
            'reason': f'Rules both 9th (Trikona) and 10th (Kendra) houses - strongest benefic',
            'strength_impact': '+++ (Extremely positive)'
        }
    
    # Mars for Cancer and Leo ascendants
    if planet == 'Mars':
        if lagna_num == 4:  # Cancer: rules 5th and 10th
            return {
                'classification': 'Yogakaraka (Great Benefic)',
                'reason': 'Rules both 5th (Trikona) and 10th (Kendra) houses',
                'strength_impact': '+++ (Extremely positive)'
            }
        elif lagna_num == 5:  # Leo: rules 4th and 9th
            return {
                'classification': 'Yogakaraka (Great Benefic)',
                'reason': 'Rules both 4th (Kendra) and 9th (Trikona) houses',
                'strength_impact': '+++ (Extremely positive)'
            }
    
    # Venus for Capricorn and Aquarius
    if planet == 'Venus':
        if lagna_num == 10:  # Capricorn: rules 5th and 10th
            return {
                'classification': 'Yogakaraka (Great Benefic)',
                'reason': 'Rules both 5th (Trikona) and 10th (Kendra) houses',
                'strength_impact': '+++ (Extremely positive)'
            }
        elif lagna_num == 11:  # Aquarius: rules 4th and 9th
            return {
                'classification': 'Yogakaraka (Great Benefic)',
                'reason': 'Rules both 4th (Kendra) and 9th (Trikona) houses',
                'strength_impact': '+++ (Extremely positive)'
            }
    
    # General Yogakaraka (rare for other planets)
    if rules_both and not rules_dusthana:
        return {
            'classification': 'Yogakaraka (Great Benefic)',
            'reason': f'Rules both Kendra and Trikona houses ({houses})',
            'strength_impact': '+++ (Extremely positive)'
        }
    
    # Ruling only Dusthana = Malefic
    if rules_dusthana and not (rules_trikona or rules_kendra):
        return {
            'classification': 'Functional Malefic',
            'reason': f'Rules only dusthana (evil) houses: {[h for h in houses if h in dusthana_houses]}',
            'strength_impact': '-- (Negative)'
        }
    
    # Ruling Trikona = Benefic
    if rules_trikona and not rules_dusthana:
        return {
            'classification': 'Functional Benefic',
            'reason': f'Rules trikona (trine) houses: {[h for h in houses if h in trikona_houses]}',
            'strength_impact': '++ (Positive)'
        }
    
    # Natural malefic ruling only Kendra = Neutral/Slightly malefic
    if not is_natural_benefic and rules_kendra and not rules_trikona:
        return {
            'classification': 'Neutral (Kendradhipati Dosha)',
            'reason': f'Natural malefic ruling only kendra house(s): {houses}',
            'strength_impact': '0 (Neutral to slightly negative)'
        }
    
    # Natural benefic ruling Kendra = Benefic
    if is_natural_benefic and rules_kendra:
        return {
            'classification': 'Functional Benefic',
            'reason': f'Natural benefic ruling kendra house(s): {houses}',
            'strength_impact': '+ (Positive)'
        }
    
    # Mixed lordship (Trikona + Dusthana or Kendra + Dusthana)
    if rules_dusthana and (rules_trikona or rules_kendra):
        good_houses = [h for h in houses if h in trikona_houses or h in kendra_houses]
        bad_houses = [h for h in houses if h in dusthana_houses]
        return {
            'classification': 'Mixed (Benefic + Malefic)',
            'reason': f'Rules both good {good_houses} and dusthana {bad_houses} houses',
            'strength_impact': '+/- (Mixed results)'
        }
    
    # Default: Neutral
    return {
        'classification': 'Neutral',
        'reason': f'Rules houses {houses} - neither strongly benefic nor malefic',
        'strength_impact': '0 (Neutral)'
    }


def get_ascendant_name(lagna_num: int) -> str:
    """Get ascendant sign name from number."""
    signs = ['', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    return signs[lagna_num] if 1 <= lagna_num <= 12 else 'Unknown'


def get_functional_nature_categorized(lagna_num: int) -> dict:
    """
    Get functional nature in categorized format (benefics, malefics, neutrals, yogakaraka).
    This format is optimized for prediction algorithms.
    
    Args:
        lagna_num: Ascendant sign number (1=Aries, 2=Taurus, ..., 12=Pisces)
    
    Returns:
        Dictionary with categorized planet lists:
        {
            "benefics": ["Mars", "Sun"],
            "malefics": ["Venus", "Saturn"],
            "neutrals": ["Mercury", "Jupiter"],
            "yogakaraka": "Mars"  # or null if none
        }
    """
    detailed = get_functional_nature(lagna_num)
    
    benefics = []
    malefics = []
    neutrals = []
    yogakaraka = None
    
    for planet, info in detailed.items():
        nature = info['nature']
        
        # Skip shadow planets for main categories
        if planet in ['Rahu', 'Ketu']:
            neutrals.append(planet)
            continue
        
        # Yogakaraka is the strongest benefic
        if 'Yogakaraka' in nature:
            yogakaraka = planet
            benefics.append(planet)
        # Functional Benefic
        elif 'Functional Benefic' in nature:
            benefics.append(planet)
        # Functional Malefic
        elif 'Functional Malefic' in nature or 'Malefic' in nature:
            malefics.append(planet)
        # Mixed or Neutral
        elif 'Mixed' in nature or 'Neutral' in nature:
            neutrals.append(planet)
        else:
            # Default to neutral if unclear
            neutrals.append(planet)
    
    return {
        'benefics': benefics,
        'malefics': malefics,
        'neutrals': neutrals,
        'yogakaraka': yogakaraka
    }
