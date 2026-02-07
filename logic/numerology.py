"""
Numerology - Vedic Number Science
Based on Chaldean System for name calculations
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from enum import IntEnum
import re

# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class LifeAspect(IntEnum):
    """Life aspects for prediction scoring"""
    FINANCE = 0
    ROMANCE = 1
    EDUCATION = 2
    HEALTH = 3


# Planet names for ruling numbers
PLANET_NAMES = {
    1: 'Sun',
    2: 'Moon', 
    3: 'Jupiter',
    4: 'Rahu',
    5: 'Mercury',
    6: 'Venus',
    7: 'Ketu',
    8: 'Saturn',
    9: 'Mars',
}


# Chaldean alphabet values (standard letters)
CHALDEAN_VALUES = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 8, 'g': 3, 'h': 5,
    'i': 1, 'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 7, 'p': 8,
    'q': 1, 'r': 2, 's': 3, 't': 4, 'u': 6, 'v': 6, 'w': 6, 'x': 5,
    'y': 1, 'z': 7
}

# Initial letter values (when letter stands alone - different pronunciation)
INITIAL_VALUES = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 8, 'g': 3, 'h': 5,
    'i': 10, 'j': 10, 'k': 20, 'l': 30, 'm': 40, 'n': 50, 'o': 70, 'p': 80,
    'q': 100, 'r': 200, 's': 30, 't': 400, 'u': 6, 'v': 6, 'w': 6, 'x': 5,
    'y': 10, 'z': 7
}


# =============================================================================
# CORE NUMBER CALCULATIONS
# =============================================================================

def reduce_to_single_digit(num: int) -> int:
    """Reduce a number to single digit (1-9) by summing digits."""
    while num > 9:
        num = sum(int(d) for d in str(num))
    return num


def get_birth_number(birth_date: datetime) -> int:
    """
    Calculate Birth Number from day of birth.
    
    The birth number denotes ruling power, body structure and character.
    Example: 17th -> 1+7 = 8
    
    Args:
        birth_date: Date of birth
        
    Returns:
        Birth number (1-9)
    """
    day = birth_date.day
    return reduce_to_single_digit(day)


def get_destiny_number(birth_date: datetime) -> int:
    """
    Calculate Destiny Number from full birth date.
    
    The destiny number denotes life events, relationships, future and fate.
    Example: 17/10/1931 -> 1+7+1+0+1+9+3+1 = 23 -> 2+3 = 5
    
    Args:
        birth_date: Full date of birth
        
    Returns:
        Destiny number (1-9)
    """
    date_str = birth_date.strftime('%d%m%Y')
    total = sum(int(d) for d in date_str)
    return reduce_to_single_digit(total)


def get_name_number(name: str) -> int:
    """
    Calculate Name Number using Chaldean System.
    
    The numerical values are based on wave length of sound and impact of letters.
    Handles: pure names, initials, mixed alphanumeric (house/flight numbers)
    
    Args:
        name: Full name or identifier
        
    Returns:
        Name number (raw total, not reduced)
    """
    # Case 1: Pure number (e.g., house number)
    if name.isdigit():
        return int(name)
    
    # Case 2: Mix of numbers and letters (e.g., "32A", "MH370")
    has_digits = bool(re.search(r'\d', name))
    has_letters = bool(re.search(r'[a-zA-Z]', name))
    
    if has_digits and has_letters:
        return _mixed_alphanumeric_to_number(name)
    
    # Case 3: Pure alphabetic name
    return _name_to_number(name)


def _mixed_alphanumeric_to_number(text: str) -> int:
    """Handle mixed alphanumeric like house/flight numbers."""
    total = 0
    
    # Add digit values
    for char in text:
        if char.isdigit():
            total += int(char)
    
    # Add letter values
    for char in text.lower():
        if char in CHALDEAN_VALUES:
            total += CHALDEAN_VALUES[char]
    
    return total


def _name_to_number(full_name: str) -> int:
    """
    Calculate name number for alphabetic names with initials.
    
    Notes from ancient texts:
    - Only spelling and initials matter
    - Titles like Mr., Mrs. have no value
    - Dr. (Doctor) should be included
    """
    # Remove dots
    full_name = full_name.replace('.', '')
    
    # Remove non-alphabetic except spaces
    full_name = re.sub(r'[^a-zA-Z\s]', '', full_name)
    
    # Make lowercase
    full_name = full_name.lower().strip()
    
    # Split into name parts
    parts = full_name.split()
    
    total = 0
    for part in parts:
        if not part:
            continue
            
        # Single letter = initial (use special values)
        if len(part) == 1:
            total += INITIAL_VALUES.get(part, 0)
        else:
            # Full name part - add each letter
            for char in part:
                total += CHALDEAN_VALUES.get(char, 0)
    
    return total


def get_root_number(num: int) -> int:
    """Get root number (1-9) from any number."""
    return reduce_to_single_digit(num)


def get_ruling_planet(num: int) -> str:
    """Get ruling planet for a number (1-9)."""
    root = reduce_to_single_digit(num)
    return PLANET_NAMES.get(root, 'Unknown')


# =============================================================================
# NAME NUMBER PREDICTIONS
# =============================================================================

# Comprehensive predictions based on Chaldean numerology texts
NAME_PREDICTIONS = {
    # SUN (1) Numbers
    10: {
        'planet': 'Sun',
        'prediction': "This number indicates the primal force. Those named under this number will be dignified and popular. Confidence and patience coexist but fortunes change frequently like a revolving wheel. Must be honest to gain popularity and lead happy lives with no paucity of funds.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 10, LifeAspect.HEALTH: 30}
    },
    19: {
        'planet': 'Sun',
        'prediction': "The Rising Sun number - mastery over the Three Worlds. Progress increases with age. Position, status, happiness, success and wealth will be gradually on the rise. Being well-disciplined, they look young and remain active even in advanced age.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    28: {
        'planet': 'Sun',
        'prediction': "Progress and comforts in early life but frequent struggles later. May have to start life afresh many times. Progress fast but lose everything due to cruel fate. Unexpected losses due to friends and relatives. Money lent rarely returns. Unlucky number.",
        'scores': {LifeAspect.FINANCE: 20, LifeAspect.ROMANCE: 10, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    37: {
        'planet': 'Sun',
        'prediction': "Very lucky number. Lifts ordinary persons to prominent positions. Success in love and patronage of elite. Good friends from both sexes. Easy accumulation of money and wealth. Active interest in fine arts. Luxurious life with pleasing manners.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    46: {
        'planet': 'Sun',
        'prediction': "The Crowned Head - when prudence, intelligence and knowledge are used wisely, brings the crown of life. Can raise even ordinary person to ruler's position. Wealth and status increase with age. Must be honest in all walks of life.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 70}
    },
    55: {
        'planet': 'Sun',
        'prediction': "Creation and destruction by single power. Victory over enemies. Epitome of will-power and intuition. Astonish others by knowledge. Wisdom and intelligence bright as lightning. Knowledge in various subjects acquired easily.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 90, LifeAspect.HEALTH: 60}
    },
    64: {
        'planet': 'Sun',
        'prediction': "Creates equal friends and foes. Extraordinary will power, intelligence and knowledge. Achieve things considered impossible. High government positions. Words cast powerful influence.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 50}
    },
    73: {
        'planet': 'Sun',
        'prediction': "Strengthens mental faculties. Bestows fame, wealth and power. Support from authorities. Material possessions in plenty. If spiritual, peaceful and comfortable life with pure heart.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    82: {
        'planet': 'Sun',
        'prediction': "Most powerful number - can elevate ordinary person to ruler status. Duty-conscious with unceasing efforts. Own lands, gold mines and precious gems. Magnetic eyes. Physical and mental feats possible when power understood.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    91: {
        'planet': 'Sun',
        'prediction': "Strong determination and profitable journeys. Maritime trade brings wealth. Success in meditation and concentration. Comfortable living awaits.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    100: {
        'planet': 'Sun',
        'prediction': "Success in all efforts but not many opportunities. Plenty of money. Long and comfortable life without major achievements.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    
    # MOON (2) Numbers
    11: {
        'planet': 'Moon',
        'prediction': "Come up in life by sheer faith in God. Profit easily by various means. May face unforeseen problems as tests of faith. Family and friends may let them down. With faith, attain great heights.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    20: {
        'planet': 'Moon',
        'prediction': "Spiritual number - drumbeat heralding triumph. Work for liberation and social reforms. Can provide relief to masses. Excel in medicine with toxic substances. When selfish, highly destructive.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 40}
    },
    29: {
        'planet': 'Moon',
        'prediction': "Often need court to settle disputes. Family problems, let down by friends. Mental agony with life partner. Deep troubles with opposite sex. Life full of ups and downs.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 30}
    },
    38: {
        'planet': 'Moon',
        'prediction': "Honest, peace loving and gentle. Earn help of influential. Rapid development from humble beginnings. May face dangers and get cheated. Deaths may be sudden and unexpected.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    47: {
        'planet': 'Moon',
        'prediction': "Come up very fast in life. Very concerned about own progress. Very lucky in money matters. Many tend to lose eyesight. Abstain from hunting and eating flesh.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 40}
    },
    56: {
        'planet': 'Moon',
        'prediction': "Full of wonders. Brings fortune and fame but used in occultism. Can free from all ties and break bondage. May lose wealth and fame suddenly.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 20}
    },
    65: {
        'planet': 'Moon',
        'prediction': "Divine grace and spiritual progress. Earn help of wealthy patrons. Blissful marital life. May be injured in accidents with cuts or bruises.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    74: {
        'planet': 'Moon',
        'prediction': "Great affinity towards religion. Run short of money often. Introduce social and religious reforms. Best suited for hermits and priests. Always worried.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 20}
    },
    83: {
        'planet': 'Moon',
        'prediction': "Prestigious posts earning respect and adoration. Life of splendour and authority. Successful.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    92: {
        'planet': 'Moon',
        'prediction': "Signifies gold, silver, land, wealth and yogic power. May acquire power of astral projection through yogic breathing.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    
    # JUPITER (3) Numbers
    3: {
        'planet': 'Jupiter',
        'prediction': "Hard work, intelligence, success and comfortable life. Highly educated with gradual progress.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 90, LifeAspect.HEALTH: 50}
    },
    12: {
        'planet': 'Jupiter',
        'prediction': "Natural ability to attract people by power of speech. Sacrifice for welfare of others by shouldering their burdens.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 50}
    },
    21: {
        'planet': 'Jupiter',
        'prediction': "Self-centered, concerned about own happiness. Rise steadily to pinnacle of success. Tactful behaviour solves problems. Struggle early but achieve success. Retain good positions permanently.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    30: {
        'planet': 'Jupiter',
        'prediction': "Live in world of fantasy. Wise thinkers. Less interest in making money. Gain mystic powers through mind control.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 40}
    },
    39: {
        'planet': 'Jupiter',
        'prediction': "Sincere and hardworking. Name and fame enjoyed by others. Work for welfare of others. Not as healthy, prone to skin diseases.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 30}
    },
    48: {
        'planet': 'Jupiter',
        'prediction': "Interested in religious matters. Face opposition in society. Do public welfare work. Create problems attempting beyond capacity. Fate against them.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 20}
    },
    57: {
        'planet': 'Jupiter',
        'prediction': "Victory in beginning but gradual downfall. Life progresses fast then halts suddenly. Achieve great heights then revert to original position.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    66: {
        'planet': 'Jupiter',
        'prediction': "Dynamism and oratorical skills. Perfection in fine arts. Government patronage. Comfortable life.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    75: {
        'planet': 'Jupiter',
        'prediction': "Sudden fame. Good friends made quickly. Unexpectedly popular. Fame and comforts come searching. Good poets and writers.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    84: {
        'planet': 'Jupiter',
        'prediction': "Early struggles and worries. Earn enemies unnecessarily. Travelling benefits. Don't get rewards for efforts. Improve spiritually.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 30}
    },
    93: {
        'planet': 'Jupiter',
        'prediction': "Capable of marvelous things. Lucky to have desires fulfilled. Excel in histrionics. Earn through many businesses. Lead dignified lives.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    
    # RAHU (4) Numbers
    4: {
        'planet': 'Rahu',
        'prediction': "Popular but does not bring deserved luck. Needless fears, sickness and opposition. Well-informed but work as subordinates.",
        'scores': {LifeAspect.FINANCE: 30, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    13: {
        'planet': 'Rahu',
        'prediction': "Considered unlucky in Western countries. Unexpected sorrowful events. Bitter experiences due to opposite sex. Life full of struggles. Not desirable.",
        'scores': {LifeAspect.FINANCE: 20, LifeAspect.ROMANCE: 10, LifeAspect.EDUCATION: 30, LifeAspect.HEALTH: 20}
    },
    22: {
        'planet': 'Rahu',
        'prediction': "Instigates base feelings. Drawn to gambling, drinking, speculation. May move towards self-destruction. Good administrators with courage. Often face humiliations.",
        'scores': {LifeAspect.FINANCE: 30, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 20}
    },
    31: {
        'planet': 'Rahu',
        'prediction': "Don't care for profit or loss, want freedom. Interest in astrology and philosophy. By 31 lose possessions, regain by 37. Even death sensed intuitively.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 30}
    },
    40: {
        'planet': 'Rahu',
        'prediction': "Earn good helpful friends. Fine jewellery and wealth. Fame and prosperity. But negative qualities noticed. Eventually lives turn fruitless. Lose all money.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 20}
    },
    49: {
        'planet': 'Rahu',
        'prediction': "Abundant riches. Fame spreads far and wide. Eventful lives, travel a lot. Permanent prosperity, excellent properties, sudden fortunes. Kindles imagination.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 40}
    },
    58: {
        'planet': 'Rahu',
        'prediction': "Outstanding popularity. Great achievers. Pious and orthodox. Outwardly lucky but have unwanted fears within.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 40}
    },
    67: {
        'planet': 'Rahu',
        'prediction': "Exemplary artists. Patronized by power barons. Love and affection make them endearing. Cannot achieve if selfish. Helps attract and conquer others.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 50}
    },
    76: {
        'planet': 'Rahu',
        'prediction': "Lose worldly possessions at some point. Very popular. Successful in philanthropy. Make money in new ways. Last years in solitude.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 30, LifeAspect.HEALTH: 30}
    },
    85: {
        'planet': 'Rahu',
        'prediction': "Come up the hard way. Overcome afflictions and help others. New ideas about religion and nature. Shine in medicine. Attain distinction and honour.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    94: {
        'planet': 'Rahu',
        'prediction': "Execute good services for mankind. Bring reforms in society. Comfort and fame come and go. Fame remembered after demise. Fortunate number.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    
    # MERCURY (5) Numbers
    5: {
        'planet': 'Mercury',
        'prediction': "Power to charm, exude dynamism, luxurious life with fame. Spend lavishly. Should cultivate perseverance.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    14: {
        'planet': 'Mercury',
        'prediction': "Suitable for trade. Surrounded by people. Successful in various trades. Risk from thunder, lightning, water and fire. Be careful in vehicles. Very lucky for business.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    23: {
        'planet': 'Mercury',
        'prediction': "Luckiest of all Mercury numbers. Success in all endeavors. Achieve things others won't imagine. Patronage of high positions. Most sought-after executives.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    32: {
        'planet': 'Mercury',
        'prediction': "Mass appeal with unique ideas. Makes anyone prominent. Epitome of wisdom and intuition. Above-average intelligence. Become geniuses. Youthful even in old age.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 90, LifeAspect.HEALTH: 60}
    },
    41: {
        'planet': 'Mercury',
        'prediction': "Charming and controlling. Renowned achievers with high ideals. World-famous. When heady with success, get into things beyond capability. Lead successful lives.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    50: {
        'planet': 'Mercury',
        'prediction': "Very intelligent, analyze everything thoroughly. Excel in education. Some shine as teachers. Lucky after age 50. Live longer.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 90, LifeAspect.HEALTH: 70}
    },
    59: {
        'planet': 'Mercury',
        'prediction': "Research-minded. Writings full of humour - Humour Kings. Become rich by writing. Permanent fortunes. May suffer nervous diseases.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    68: {
        'planet': 'Mercury',
        'prediction': "Lucky to certain extent. Pleasant life may suddenly halt. Get involved in schemes they cannot execute. Greed spoils career. Not quite fortunate.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 30}
    },
    77: {
        'planet': 'Mercury',
        'prediction': "Sincere effort, self confidence, hard work. Support brings profits, fame, honour. Enchanting life. Benefits from faith in God. Chances to travel abroad.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    86: {
        'planet': 'Mercury',
        'prediction': "Come up gradually the hard way. Get what they deserve. Earn favour of rich. Lead comfortable, happy lives with good savings.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    95: {
        'planet': 'Mercury',
        'prediction': "Disciplined life with daring events and honour. Successful in trade. Amass wealth trading new things. Excellent orators, popular in business.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    
    # VENUS (6) Numbers
    6: {
        'planet': 'Venus',
        'prediction': "Peaceful life, satisfied mind, good standard of living. Being single digit, limited power.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 80}
    },
    15: {
        'planet': 'Venus',
        'prediction': "Determination to succeed. Charming appearance, forceful speech. Ideal for material success. Fame, wealth and distinction. Luxurious life.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 70}
    },
    24: {
        'planet': 'Venus',
        'prediction': "Receive many government favours. Reach high positions easily. Marry those higher in status. Rise from lowest rank to very high position in uniformed services.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 70}
    },
    33: {
        'planet': 'Venus',
        'prediction': "Simultaneous divine grace and prosperity. Spiritual enlightenment. Abundant wealth and properties. Everlasting wealth.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 80}
    },
    42: {
        'planet': 'Venus',
        'prediction': "Even if poor initially, attain prominent position. May be greedy. Thrifty and smart in saving. Strength of mind and grace flourish.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 70}
    },
    51: {
        'planet': 'Venus',
        'prediction': "Most powerful Venus number. Sudden progress. Commoners become prominent suddenly. Body and mind bubbling with energy. Signifies abundant wealth accumulation.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    60: {
        'planet': 'Venus',
        'prediction': "Peace, prosperity, fine arts appreciation, balanced mind, wisdom. Skilled conversationalists with logical arguments. Happy family life. Fortunate.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 70}
    },
    69: {
        'planet': 'Venus',
        'prediction': "Like uncrowned king in any business. Majestic appearance, very prosperous. Awe-inspiring status. Incomparable in charming others.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 70}
    },
    78: {
        'planet': 'Venus',
        'prediction': "Most righteous. Great leaning towards religion. Good poets who spell-bind listeners. Generous, fond of social service. May lose all except Divine grace.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 50}
    },
    87: {
        'planet': 'Venus',
        'prediction': "Gives mystic powers. Money earned by devious means. Can relate to criminals if birth numbers unfavorable.",
        'scores': {LifeAspect.FINANCE: 30, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 10}
    },
    96: {
        'planet': 'Venus',
        'prediction': "Prosperity with higher education. All desires fulfilled. Excel in fine arts. Charm women easily. Fortunate number.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 90, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    105: {
        'planet': 'Venus',
        'prediction': "Fortunes, satisfactory environment, great fame, wealth accumulation. Good progeny.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    
    # KETU (7) Numbers
    7: {
        'planet': 'Ketu',
        'prediction': "High principles and virtuous qualities with divine grace. Unexpected changes. Efforts may not produce desired results.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 30}
    },
    16: {
        'planet': 'Ketu',
        'prediction': "Speedy progress and sudden downfall. The Shattered Tower. Better to change to other lucky number. Induces new imaginative thoughts.",
        'scores': {LifeAspect.FINANCE: 20, LifeAspect.ROMANCE: 10, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    25: {
        'planet': 'Ketu',
        'prediction': "Good results in the end. Many trials in life. Victory gives self-confidence and spiritual growth. Worldly-wise with clarity of thought. End with respect after trials.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    34: {
        'planet': 'Ketu',
        'prediction': "Lucky in a way. Displays best qualities attractively. Cannot be considered fortunate. Some problem in family life. Mind succumbs to sensuous pleasures.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 40}
    },
    43: {
        'planet': 'Ketu',
        'prediction': "Revolutionary life. Produces new enemies. Tendency to resign often. Extraordinary imagination, speaking and writing. Somewhat unlucky.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 30}
    },
    52: {
        'planet': 'Ketu',
        'prediction': "Revolutionary qualities. May bring world renown. Charm many. On spiritual path, attain great powers. End comes abruptly leaving work unaccomplished.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 40}
    },
    61: {
        'planet': 'Ketu',
        'prediction': "Quit comfortable life for new avenues. Successes and failures in succession. Later years fruitful. Unhappy family life. Earn great fame.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 40}
    },
    70: {
        'planet': 'Ketu',
        'prediction': "Extreme nature. Comfortable life gets disturbed. Frequent problems. Later years fruitful and blessed. Does not possess much power.",
        'scores': {LifeAspect.FINANCE: 30, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    79: {
        'planet': 'Ketu',
        'prediction': "Suffer badly initially. Rise quickly by cleverness and will power. Settle comfortably. Popular support. Become great personalities.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    88: {
        'planet': 'Ketu',
        'prediction': "Spiritual progress. Generous and compassionate. Affectionate to all creatures. Become popular.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    97: {
        'planet': 'Ketu',
        'prediction': "Proficiency in scriptures and fine arts. Eminence in spiritual career. Successful and prosperous through astounding achievements.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    
    # SATURN (8) Numbers
    8: {
        'planet': 'Saturn',
        'prediction': "Great success in spiritual life. If no control over pleasures, success delayed. After big struggle may succeed. Face unexpected dangers.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    17: {
        'planet': 'Saturn',
        'prediction': "Demonic qualities pursuing goals. Many problems and trials. Persistently struggle without giving up. Permanent prosperity and great fame in end. Can give mystic powers.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    26: {
        'planet': 'Saturn',
        'prediction': "Poverty in old age, fruitless efforts. Great losses due to friends and partners. Reduces life span. Enemies may murder. Not desirable.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    35: {
        'planet': 'Saturn',
        'prediction': "Seems fortunate but suffer losses from friends. Become rich then lose all. Unexpected accidents. Helps earn through illegal means. Severe stomach pain.",
        'scores': {LifeAspect.FINANCE: 30, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 20}
    },
    44: {
        'planet': 'Saturn',
        'prediction': "Earn money easily. Industries with many people. Cinema, printing, mining. One day everything may halt. Danger from fire. May spend time in prison.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 20, LifeAspect.EDUCATION: 40, LifeAspect.HEALTH: 30}
    },
    53: {
        'planet': 'Saturn',
        'prediction': "Success and failure early in life. Become steadier and well-known with age. Get into problems beyond control. Convert failure to success. Lucky in old age.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    62: {
        'planet': 'Saturn',
        'prediction': "Great fame, victories, comfortable life. Great dangers and failures alternately. Serious enmity. Family life not pleasant. Can charm everyone including enemies.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    71: {
        'planet': 'Saturn',
        'prediction': "Obstacles initially, later prosperity. Good counsellors due to intelligence. May be considered fortunate.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    80: {
        'planet': 'Saturn',
        'prediction': "Strange mystic powers. Research in theology successful. Nature changes to help them. Lives full of dangers but comfortable. Miracles happen. Fortunate.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 50}
    },
    89: {
        'planet': 'Saturn',
        'prediction': "Benefits but problems initially. Helping tendency. Acquire land, houses, jewellery. Women attracted easily. Fearless lives. Fire accidents possible initially.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 50}
    },
    98: {
        'planet': 'Saturn',
        'prediction': "Intelligent but lives filled with worries and desires. May not benefit from intelligence. Difficulties and chronic diseases.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 30}
    },
    
    # MARS (9) Numbers
    9: {
        'planet': 'Mars',
        'prediction': "Wisdom and capability. Travel, struggles against odds, victory in end. Long life of luxury when finally succeed.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 60, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 80}
    },
    18: {
        'planet': 'Mars',
        'prediction': "Decline of divinity. Problems, procrastination, dangerous enemies. Selfishness leads to antisocial activities. Life devoid of peace. Jealousy, malice, dangers. Not desirable.",
        'scores': {LifeAspect.FINANCE: 20, LifeAspect.ROMANCE: 10, LifeAspect.EDUCATION: 30, LifeAspect.HEALTH: 20}
    },
    27: {
        'planet': 'Mars',
        'prediction': "Clear mind, intelligence, hard work. Accumulation of wealth, influence, high rank. Rise very high in uniformed services. Very fortunate. Spirituality and magical powers.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    36: {
        'planet': 'Mars',
        'prediction': "Raise poor to enviable status. Success when away from birthplace. Travel extensively. Problems within family. May be surrounded by disloyal people.",
        'scores': {LifeAspect.FINANCE: 70, LifeAspect.ROMANCE: 50, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 40}
    },
    45: {
        'planet': 'Mars',
        'prediction': "Lucky number. Struggle at lower levels then raised to higher status. Good conversationalists. Achieve goals at any cost. Retain smile hiding problems. Comfortable life, fame, wealth. Diseases cured.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 80}
    },
    54: {
        'planet': 'Mars',
        'prediction': "Success step by step with failures. Begin with prestige then stubbornness causes loss. Greed worst enemy. Later years successful. Under control of others.",
        'scores': {LifeAspect.FINANCE: 50, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 60, LifeAspect.HEALTH: 30}
    },
    63: {
        'planet': 'Mars',
        'prediction': "Lucky number but leads to wrong ways. Described as related to thieves in ancient texts.",
        'scores': {LifeAspect.FINANCE: 40, LifeAspect.ROMANCE: 30, LifeAspect.EDUCATION: 20, LifeAspect.HEALTH: 10}
    },
    72: {
        'planet': 'Mars',
        'prediction': "Best of all number 9. Struggle early, enjoy all comforts later. Mind filled with joy. Wealth remains for generations. Money keeps coming. Permanent wealth.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
    81: {
        'planet': 'Mars',
        'prediction': "Fortunate life. Development, good position, wealth. Luck could change if not careful. Opportunities to become teachers.",
        'scores': {LifeAspect.FINANCE: 80, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 80, LifeAspect.HEALTH: 60}
    },
    90: {
        'planet': 'Mars',
        'prediction': "Full power of number 9. Go to any extent to fulfill desires. Victory certain. Very wealthy and famous. Not desirable for spiritual pursuits.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 70, LifeAspect.EDUCATION: 50, LifeAspect.HEALTH: 40}
    },
    99: {
        'planet': 'Mars',
        'prediction': "Lure to devious ways. Success with enmity. Attacked by enemies. Not a good number. But blessed with education, wealth, prosperity.",
        'scores': {LifeAspect.FINANCE: 60, LifeAspect.ROMANCE: 40, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 50}
    },
    108: {
        'planet': 'Mars',
        'prediction': "High positions and success. Everything according to desire. Good efforts result in success. Very lucky number.",
        'scores': {LifeAspect.FINANCE: 90, LifeAspect.ROMANCE: 80, LifeAspect.EDUCATION: 70, LifeAspect.HEALTH: 60}
    },
}


def get_name_number_prediction(name: str) -> Dict:
    """
    Get comprehensive numerology prediction for a name.
    
    Args:
        name: Full name or identifier
        
    Returns:
        Dict with name number, prediction, and life aspect scores
    """
    name_number = get_name_number(name)
    root_number = get_root_number(name_number)
    ruling_planet = get_ruling_planet(name_number)
    
    # Look up prediction
    if name_number in NAME_PREDICTIONS:
        pred = NAME_PREDICTIONS[name_number]
        return {
            'name': name,
            'name_number': name_number,
            'root_number': root_number,
            'ruling_planet': ruling_planet,
            'prediction': pred['prediction'],
            'scores': {
                'finance': pred['scores'][LifeAspect.FINANCE],
                'romance': pred['scores'][LifeAspect.ROMANCE],
                'education': pred['scores'][LifeAspect.EDUCATION],
                'health': pred['scores'][LifeAspect.HEALTH],
            },
            'overall_score': sum(pred['scores'].values()) // 4,
            'lucky': sum(pred['scores'].values()) // 4 >= 60,
        }
    
    # Generic prediction based on root number
    return {
        'name': name,
        'name_number': name_number,
        'root_number': root_number,
        'ruling_planet': ruling_planet,
        'prediction': f"Name number {name_number} reduces to {root_number}, ruled by {ruling_planet}.",
        'scores': {
            'finance': 50,
            'romance': 50,
            'education': 50,
            'health': 50,
        },
        'overall_score': 50,
        'lucky': False,
    }


def get_full_numerology(name: str, birth_date: datetime) -> Dict:
    """
    Get complete numerology analysis.
    
    Args:
        name: Full name
        birth_date: Date of birth
        
    Returns:
        Dict with birth number, destiny number, name number and analysis
    """
    birth_num = get_birth_number(birth_date)
    destiny_num = get_destiny_number(birth_date)
    name_num = get_name_number(name)
    name_pred = get_name_number_prediction(name)
    
    # Check compatibility between numbers
    friendly_pairs = [
        (1, 1), (1, 4), (1, 5), (1, 7),
        (2, 2), (2, 7), (2, 9),
        (3, 3), (3, 6), (3, 9),
        (4, 1), (4, 4), (4, 5), (4, 7), (4, 8),
        (5, 1), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8),
        (6, 3), (6, 5), (6, 6), (6, 9),
        (7, 1), (7, 2), (7, 4), (7, 5), (7, 7),
        (8, 4), (8, 5), (8, 8),
        (9, 2), (9, 3), (9, 6), (9, 9),
    ]
    
    birth_destiny_compat = (birth_num, destiny_num) in friendly_pairs or \
                           (destiny_num, birth_num) in friendly_pairs
    
    name_root = get_root_number(name_num)
    name_birth_compat = (name_root, birth_num) in friendly_pairs or \
                        (birth_num, name_root) in friendly_pairs
    
    return {
        'birth_number': {
            'number': birth_num,
            'planet': PLANET_NAMES[birth_num],
            'meaning': 'Denotes ruling power, body structure, character and desires',
        },
        'destiny_number': {
            'number': destiny_num,
            'planet': PLANET_NAMES[destiny_num],
            'meaning': 'Denotes life events, relationships, future and fate',
        },
        'name_number': {
            'number': name_num,
            'root': name_root,
            'planet': PLANET_NAMES[name_root],
            'prediction': name_pred['prediction'],
            'scores': name_pred['scores'],
        },
        'compatibility': {
            'birth_destiny': birth_destiny_compat,
            'name_birth': name_birth_compat,
            'harmonious': birth_destiny_compat and name_birth_compat,
        },
        'lucky_numbers': get_lucky_numbers(birth_num),
        'lucky_days': get_lucky_days(birth_num),
        'lucky_colors': get_lucky_colors(birth_num),
    }


def get_lucky_numbers(birth_number: int) -> list:
    """Get lucky numbers based on birth number."""
    lucky_map = {
        1: [1, 4, 10, 13, 19, 28],
        2: [2, 7, 11, 16, 20, 25],
        3: [3, 6, 9, 12, 21, 27],
        4: [1, 4, 10, 13, 22, 31],
        5: [5, 14, 23, 32, 41, 50],
        6: [3, 6, 9, 15, 24, 33],
        7: [2, 7, 16, 25, 34, 43],
        8: [4, 8, 13, 17, 22, 26],
        9: [3, 6, 9, 18, 27, 36],
    }
    return lucky_map.get(birth_number, [])


def get_lucky_days(birth_number: int) -> list:
    """Get lucky days based on birth number."""
    day_map = {
        1: ['Sunday'],
        2: ['Monday'],
        3: ['Thursday'],
        4: ['Sunday', 'Saturday'],
        5: ['Wednesday'],
        6: ['Friday'],
        7: ['Monday'],
        8: ['Saturday'],
        9: ['Tuesday', 'Thursday'],
    }
    return day_map.get(birth_number, [])


def get_lucky_colors(birth_number: int) -> list:
    """Get lucky colors based on birth number."""
    color_map = {
        1: ['Gold', 'Orange', 'Yellow'],
        2: ['White', 'Cream', 'Silver'],
        3: ['Yellow', 'Orange', 'Pink'],
        4: ['Blue', 'Grey', 'Khaki'],
        5: ['Green', 'Turquoise', 'Light Brown'],
        6: ['Blue', 'Pink', 'Rose'],
        7: ['White', 'Light Green', 'Yellow'],
        8: ['Black', 'Dark Blue', 'Grey'],
        9: ['Red', 'Crimson', 'Pink'],
    }
    return color_map.get(birth_number, [])
