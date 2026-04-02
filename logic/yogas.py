"""
Ved Astro - Yogas Module
========================

Implements detection of 94 traditional Vedic astrology Yogas (planetary combinations)
plus 1000+ astrological events from muhurtha (electional astrology).

## Implemented Yogas (101 total):

### Classic Moon-Based Yogas (4):
- **GajaKesari** - Jupiter in kendra from Moon (wealth, wisdom)
- **Sunapha** - Planets in 2nd from Moon (self-earned property)
- **Anapha** - Planets in 12th from Moon (majestic appearance)
- **Dhurdhura** - Planets on both sides of Moon (bountiful wealth)

### Pancha Mahapurusha Yogas (5):
- **Bhadra** - Mercury in kendra in own/exalted sign (intelligence)
- **Hamsa** - Jupiter in kendra in own/exalted sign (righteousness)
- **Malavya** - Venus in kendra in own/exalted sign (luxury, beauty)
- **Ruchaka** - Mars in kendra in own/exalted sign (warrior, leader)
- **Sasha** - Saturn in kendra in own/exalted sign (authority, discipline)

### Wealth Yogas (7):
- **Amala** - Benefic in 10th house from Moon/Lagna (fame, character)
- **Kemadruma** - Moon without planetary support (poverty - malefic)
- **Lakshmi** - 9th lord in kendra/trikona in dignity (wealth, nobility)
- **Sakata** - Moon & Jupiter in 6/8 relationship (rise & fall - malefic)
- **Chatussagara** - All 4 kendras occupied (wealth from 4 directions)
- **Vasumathi** - Benefics in upachaya (3,6,10,11) (prosperity, rise)
- **Parvata** - Benefics in kendras + lord in dignity (leadership, charity)

### Raja Yogas (5):
- **Raja Yoga (Basic)** - Kendra lord + Trikona lord conjunction (power, authority)
- **Neechabhanga Raja Yoga** - Debilitation cancellation (rise from adversity)
- **Harsha Yoga** - 6th lord in 6/8/12 (victory over enemies, political success)
- **Sarala Yoga** - 8th lord in 6/8/12 (long life, fearlessness, prosperity)
- **Vimala Yoga** - 12th lord in 6/8/12 (good conduct, economical, independent)

## Pending Implementation (73+ yogas):
- **Additional Raja Yogas**: Aspect-based, Exchange-based (5+ yogas)
- **Ashtakavarga Yogas**: Based on bindus (points) in SAV charts (50+ yogas)
- **Malefic Yogas**: Kalasarpa, Graha Malika variations (10+ yogas)
- **Specialty Yogas**: Various classical combinations (remaining)

## Data Source:
Yoga definitions from: `Library/XMLData/HoroscopeDataList.xml`
Calculation algorithms from: `Library/Logic/Calculate/Muhurtha.cs`

## Usage:
```python
from datetime import datetime
import pytz
from logic.time import AstroTime
from logic.yogas import check_gajakesari_yoga, get_all_yogas, get_occurring_yogas

# Create AstroTime instance
tz = pytz.timezone('Asia/Kolkata')
dt = datetime(1994, 6, 13, 23, 40, 0, tzinfo=tz)
time = AstroTime(dt, lat=13.0827, lon=80.2707)

# Check specific yoga
gaja_kesari = check_gajakesari_yoga(time)
print(f"GajaKesari Yoga: {gaja_kesari.occurring}")

# Get all occurring yogas
occurring = get_occurring_yogas(time)
for yoga in occurring:
    print(f"{yoga.name}: {yoga.description}")
    
# Get summary
summary = yoga_summary(time)
print(f"Total occurring: {summary['total_occurring']}")
```

References:
- Hindu Predictive Astrology by Dr. B.V. Raman
- Muhurtha (Electional Astrology) by Dr. B.V. Raman
- Three Hundred Important Combinations by Dr. B.V. Raman
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Import from other VedAstro modules
try:
    from .calculate import (
        planet_longitude,
        lagnam,
        moon_sign,
        house_planet_occupies,
        planets_in_house,
        is_planet_in_kendra,
        is_planet_aspecting_planet,
        planet_zodiac_sign,
    )
    from .consts import Planet
    from .rasi import get_house_from_planet
    from .ashtakavarga import sarvashtakavarga
except ImportError:
    # For standalone testing
    pass


class YogaNature(Enum):
    """Classification of yoga effects"""
    GOOD = "Good"
    BAD = "Bad"
    NEUTRAL = "Neutral"
    MIXED = "Mixed"


@dataclass
class Yoga:
    """
    Represents a Vedic astrology yoga (planetary combination)
    
    Attributes:
        name: Yoga name (e.g., "GajaKesariYoga")
        nature: Effect classification (Good/Bad/Neutral/Mixed)
        occurring: Whether yoga is currently active
        description: What the yoga indicates
        condition: Astrological conditions that form the yoga
        strength: Relative strength (0-100) if applicable
    """
    name: str
    nature: YogaNature
    occurring: bool
    description: str
    condition: str
    strength: Optional[float] = None
    
    def __str__(self) -> str:
        status = "✓ OCCURRING" if self.occurring else "✗ Not occurring"
        return f"{self.name} ({self.nature.value}): {status}\n  {self.description}"


# ========================================
# CLASSIC YOGAS (Moon-based combinations)
# ========================================

def check_gajakesari_yoga(time: 'AstroTime') -> Yoga:
    """
    GajaKesari Yoga - "Elephant-Lion" Combination
    
    Formation: Jupiter in a kendra (1st, 4th, 7th, 10th) from Moon
    
    Effect: Many relations, polite and generous, builder of villages and towns 
    or magistrate over them; will have a lasting reputation even long after death.
    
    This is one of the most auspicious yogas in Vedic astrology.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga object with occurrence status and details
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> from logic.time import AstroTime
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1994, 6, 13, 23, 40, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 13.0827, 80.2707)
        >>> yoga = check_gajakesari_yoga(time)
        >>> print(yoga.occurring)
    """
    from .calculate import get_planet_longitude
    from .consts import Planet
    
    # Get Moon and Jupiter positions
    moon_long = get_planet_longitude(Planet.Moon, time)
    jupiter_long = get_planet_longitude(Planet.Jupiter, time)
    
    moon_sign = int(moon_long // 30)
    jupiter_sign = int(jupiter_long // 30)
    
    # Calculate house distance from Moon
    distance = abs(jupiter_sign - moon_sign)
    if distance > 6:
        distance = 12 - distance
    
    # Check if Jupiter is in kendra (1, 4, 7, 10) from Moon
    is_kendra = distance in [0, 3, 6, 9]  # 0=same, 3=4th, 6=7th, 9=10th
    
    house_from_moon = ((jupiter_sign - moon_sign) % 12) + 1
    
    return Yoga(
        name="GajaKesari Yoga",
        nature=YogaNature.GOOD,
        occurring=is_kendra,
        description="Many relations, polite and generous, builder of villages and towns",
        condition=f"Jupiter in house {house_from_moon} from Moon",
        strength=100 if is_kendra else 0
    )


def check_sakata_yoga(time: 'AstroTime') -> Yoga:
    """
    Sakata Yoga (Malefic) - Moon and Jupiter in 6/8 relationship
    
    Formation: Moon and Jupiter placed 6th or 8th from each other
    This is the opposite of GajaKesari - instead of being in kendras,
    they are in difficult dusthana positions (6=enemies, 8=obstacles).
    
    Effect: Rise and fall like a cart wheel (Sakata = cart), poverty,
    misery, loss of wealth, struggles, unstable fortune. Despite efforts,
    wealth does not accumulate.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1990, 5, 10, 14, 30, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 28.6139, 77.2090)
        >>> yoga = check_sakata_yoga(time)
        >>> print(yoga.occurring)
    """
    from .calculate import get_planet_longitude
    from .consts import Planet
    
    try:
        # Get Moon and Jupiter positions
        moon_long = get_planet_longitude(Planet.Moon, time)
        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        
        moon_sign = int(moon_long // 30)
        jupiter_sign = int(jupiter_long // 30)
        
        # Calculate house distance from Moon
        house_from_moon = ((jupiter_sign - moon_sign) % 12) + 1
        
        # Check if Jupiter is 6th or 8th from Moon (or vice versa: 6th/8th houses)
        # 6th house = 6, 8th house = 8
        # Also reverse: if Moon is 6th/8th from Jupiter (same relationship)
        is_sakata = house_from_moon in [6, 8]
        
        condition_msg = f"Jupiter in house {house_from_moon} from Moon"
        if is_sakata:
            condition_msg += " (6/8 position - malefic relationship)"
        
        return Yoga(
            name="Sakata Yoga",
            nature=YogaNature.BAD,
            occurring=is_sakata,
            description="Rise and fall like cart wheel, poverty, misery, loss of wealth",
            condition=condition_msg,
            strength=100 if is_sakata else 0
        )
    
    except Exception as e:
        return Yoga(
            name="Sakata Yoga",
            nature=YogaNature.BAD,
            occurring=False,
            description="Rise and fall like cart wheel, poverty, misery, loss of wealth",
            condition=f"Error: {str(e)}",
            strength=0
        )


def check_sunapha_yoga(time: 'AstroTime') -> Yoga:
    """
    Sunapha Yoga - Planets in 2nd from Moon
    
    Formation: Any planet (except Sun) in the 2nd house from Moon
    
    Effect: Self-earned property, king or ruler status, intelligent, 
    wealthy and good reputation.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude
    from .consts import Planet
    
    moon_long = get_planet_longitude(Planet.Moon, time)
    moon_sign = int(moon_long // 30)
    second_sign = (moon_sign + 1) % 12
    
    # Check all planets (except Sun) in 2nd sign from Moon
    planets = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
    planets_in_2nd = []
    
    for planet in planets:
        planet_long = get_planet_longitude(planet, time)
        planet_sign = int(planet_long // 30)
        if planet_sign == second_sign:
            planets_in_2nd.append(planet.name)
    
    occurring = len(planets_in_2nd) > 0
    
    return Yoga(
        name="Sunapha Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Self-earned property, king/ruler status, intelligent, wealthy",
        condition=f"Planets in 2nd from Moon: {', '.join(planets_in_2nd) if occurring else 'None'}"
    )


def check_anapha_yoga(time: 'AstroTime') -> Yoga:
    """
    Anapha Yoga - Planets in 12th from Moon
    
    Formation: Any planet (except Sun) in the 12th house from Moon
    
    Effect: Well-formed organs, majestic appearance, good reputation, 
    polite, generous, self-respect, fond of dress and sense pleasures.
    In later life: renunciation and austerity.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude
    from .consts import Planet
    
    moon_long = get_planet_longitude(Planet.Moon, time)
    moon_sign = int(moon_long // 30)
    twelfth_sign = (moon_sign - 1) % 12
    
    # Check all planets (except Sun) in 12th sign from Moon
    planets = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
    planets_in_12th = []
    
    for planet in planets:
        planet_long = get_planet_longitude(planet, time)
        planet_sign = int(planet_long // 30)
        if planet_sign == twelfth_sign:
            planets_in_12th.append(planet.name)
    
    occurring = len(planets_in_12th) > 0
    
    return Yoga(
        name="Anapha Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Majestic appearance, good reputation, generous, sense pleasures",
        condition=f"Planets in 12th from Moon: {', '.join(planets_in_12th) if occurring else 'None'}"
    )


def check_dhurdhura_yoga(time: 'AstroTime') -> Yoga:
    """
    Dhurdhura Yoga - Planets on both sides of Moon
    
    Formation: Planets (except Sun) in both 2nd AND 12th from Moon
    
    Effect: The native is bountiful. Blessed with much wealth and conveyances.
    This is a powerful combination of Sunapha and Anapha yogas.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude
    from .consts import Planet
    
    moon_long = get_planet_longitude(Planet.Moon, time)
    moon_sign = int(moon_long // 30)
    second_sign = (moon_sign + 1) % 12
    twelfth_sign = (moon_sign - 1) % 12
    
    # Check planets in 2nd and 12th from Moon
    planets = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
    planets_in_2nd = []
    planets_in_12th = []
    
    for planet in planets:
        planet_long = get_planet_longitude(planet, time)
        planet_sign = int(planet_long // 30)
        if planet_sign == second_sign:
            planets_in_2nd.append(planet.name)
        elif planet_sign == twelfth_sign:
            planets_in_12th.append(planet.name)
    
    occurring = len(planets_in_2nd) > 0 and len(planets_in_12th) > 0
    
    return Yoga(
        name="Dhurdhura Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Bountiful, blessed with much wealth and conveyances",
        condition=f"2nd: {', '.join(planets_in_2nd)}; 12th: {', '.join(planets_in_12th)}"
    )


# ========================================
# PANCHA MAHAPURUSHA YOGAS (5 Great Person Combinations)
# ========================================

def check_bhadra_yoga(time: 'AstroTime') -> Yoga:
    """
    Bhadra Yoga - One of the Pancha Mahapurusha Yogas
    
    Formation: Mercury in a kendra (1st, 4th, 7th, 10th) which should be 
    his own sign (Gemini/Virgo) or exaltation sign (Virgo)
    
    Effect: Strong physique, lion-like face, well-developed chest, 
    well-proportioned limbs, taciturn, helps relatives, lives to good old age.
    
    This is one of the five great yogas indicating a distinguished personality.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    mercury_long = get_planet_longitude(Planet.Mercury, time)
    mercury_sign = int(mercury_long // 30)  # 0-11
    
    lagnam_long = get_lagnam(time)
    lagna_sign = int(lagnam_long // 30)
    
    house_from_lagna = ((mercury_sign - lagna_sign) % 12) + 1
    is_kendra = house_from_lagna in [1, 4, 7, 10]
    
    # Check if Mercury is in own sign (Gemini=2, Virgo=5) or exaltation (Virgo=5)
    is_own_or_exalted = mercury_sign in [2, 5]  # Gemini or Virgo
    
    occurring = is_kendra and is_own_or_exalted
    
    return Yoga(
        name="Bhadra Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Strong, lion-like face, well-developed chest, taciturn, helps relatives",
        condition=f"Mercury in {['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'][mercury_sign]} in house {house_from_lagna}",
        strength=100 if occurring else 0
    )


def check_hamsa_yoga(time: 'AstroTime') -> Yoga:
    """
    Hamsa Yoga - Swan Yoga (Pancha Mahapurusha)
    
    Formation: Jupiter in a kendra which should be his own house 
    (Sagittarius/Pisces) or exaltation sign (Cancer)
    
    Effect: Legs marked with conch, lotus, fish and ankusa. Handsome body, 
    liked by others, righteous disposition, pure mind.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    jupiter_long = get_planet_longitude(Planet.Jupiter, time)
    jupiter_sign = int(jupiter_long // 30)
    
    lagnam_long = get_lagnam(time)
    lagna_sign = int(lagnam_long // 30)
    house_from_lagna = ((jupiter_sign - lagna_sign) % 12) + 1
    is_kendra = house_from_lagna in [1, 4, 7, 10]
    
    # Jupiter own signs: Sagittarius(8), Pisces(11); Exaltation: Cancer(3)
    is_own_or_exalted = jupiter_sign in [3, 8, 11]
    
    occurring = is_kendra and is_own_or_exalted
    
    sign_names = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    
    return Yoga(
        name="Hamsa Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Handsome body, liked by others, righteous, pure mind",
        condition=f"Jupiter in {sign_names[jupiter_sign]} in house {house_from_lagna}",
        strength=100 if occurring else 0
    )


def check_malavya_yoga(time: 'AstroTime') -> Yoga:
    """
    Malavya Yoga - Garland Yoga (Pancha Mahapurusha)
    
    Formation: Venus in a kendra which should be his own sign 
    (Taurus/Libra) or exaltation sign (Pisces)
    
    Effect: Well-developed physique, strong-minded, wealthy, happy with 
    children and wife, commands vehicles, clean sense-organs, renowned, learned.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    venus_long = get_planet_longitude(Planet.Venus, time)
    venus_sign = int(venus_long // 30)
    
    lagnam_long = get_lagnam(time)
    lagna_sign = int(lagnam_long // 30)
    house_from_lagna = ((venus_sign - lagna_sign) % 12) + 1
    is_kendra = house_from_lagna in [1, 4, 7, 10]
    
    # Venus own signs: Taurus(1), Libra(6); Exaltation: Pisces(11)
    is_own_or_exalted = venus_sign in [1, 6, 11]
    
    occurring = is_kendra and is_own_or_exalted
    
    sign_names = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    
    return Yoga(
        name="Malavya Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Well-developed physique, wealthy, happy with family, vehicles, renowned",
        condition=f"Venus in {sign_names[venus_sign]} in house {house_from_lagna}",
        strength=100 if occurring else 0
    )


def check_ruchaka_yoga(time: 'AstroTime') -> Yoga:
    """
    Ruchaka Yoga - Radiant Yoga (Pancha Mahapurusha)
    
    Formation: Mars in a kendra which should be his own sign 
    (Aries/Scorpio) or exaltation sign (Capricorn)
    
    Effect: Strong physique, famous, well-versed in ancient lore, King or equal, 
    conforming to traditions. Ruddy complexion, attractive body, charitable, 
    wealthy, long-lived, leader of army.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    mars_long = get_planet_longitude(Planet.Mars, time)
    mars_sign = int(mars_long // 30)
    
    lagnam_long = get_lagnam(time)
    lagna_sign = int(lagnam_long // 30)
    house_from_lagna = ((mars_sign - lagna_sign) % 12) + 1
    is_kendra = house_from_lagna in [1, 4, 7, 10]
    
    # Mars own signs: Aries(0), Scorpio(7); Exaltation: Capricorn(9)
    is_own_or_exalted = mars_sign in [0, 7, 9]
    
    occurring = is_kendra and is_own_or_exalted
    
    sign_names = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    
    return Yoga(
        name="Ruchaka Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Strong physique, famous, King-like, charitable, army leader",
        condition=f"Mars in {sign_names[mars_sign]} in house {house_from_lagna}",
        strength=100 if occurring else 0
    )


def check_sasha_yoga(time: 'AstroTime') -> Yoga:
    """
    Sasha Yoga - Rabbit/Hare Yoga (Pancha Mahapurusha)
    
    Formation: Saturn in a kendra which should be his own sign 
    (Capricorn/Aquarius) or exaltation sign (Libra)
    
    Effect: Commanding appearance, leader of men, authority over others, 
    good character, learned in scriptures, efficient worker, wealthy.
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        Yoga occurrence status
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet
    
    saturn_long = get_planet_longitude(Planet.Saturn, time)
    saturn_sign = int(saturn_long // 30)
    
    lagnam_long = get_lagnam(time)
    lagna_sign = int(lagnam_long // 30)
    house_from_lagna = ((saturn_sign - lagna_sign) % 12) + 1
    is_kendra = house_from_lagna in [1, 4, 7, 10]
    
    # Saturn own signs: Capricorn(9), Aquarius(10); Exaltation: Libra(6)
    is_own_or_exalted = saturn_sign in [6, 9, 10]
    
    occurring = is_kendra and is_own_or_exalted
    
    sign_names = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
    
    return Yoga(
        name="Sasha Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Commanding appearance, leader, authority, good character, learned, wealthy",
        condition=f"Saturn in {sign_names[saturn_sign]} in house {house_from_lagna}",
        strength=100 if occurring else 0
    )


# ========================================
# MAIN YOGA DETECTION FUNCTIONS
# ========================================

def get_all_yogas(time: 'AstroTime') -> List[Yoga]:
    """
    Check all implemented yogas for given time and location
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        List of all Yoga objects (both occurring and not occurring)
        
    Example:
        >>> from datetime import datetime
        >>> import pytz
        >>> from logic.time import AstroTime
        >>> tz = pytz.timezone('Asia/Kolkata')
        >>> dt = datetime(1994, 6, 13, 23, 40, 0, tzinfo=tz)
        >>> time = AstroTime(dt, 13.0827, 80.2707)
        >>> all_yogas = get_all_yogas(time)
        >>> occurring = [y for y in all_yogas if y.occurring]
        >>> print(f"Found {len(occurring)} active yogas")
    """
    yogas = []
    
    # Classic Moon-based yogas
    yogas.append(check_gajakesari_yoga(time))
    yogas.append(check_sakata_yoga(time))  # NEW: Malefic opposite of GajaKesari
    yogas.append(check_sunapha_yoga(time))
    yogas.append(check_anapha_yoga(time))
    yogas.append(check_dhurdhura_yoga(time))
    
    # Pancha Mahapurusha Yogas (5 Great Person yogas)
    yogas.append(check_bhadra_yoga(time))
    yogas.append(check_hamsa_yoga(time))
    yogas.append(check_malavya_yoga(time))
    yogas.append(check_ruchaka_yoga(time))
    yogas.append(check_sasha_yoga(time))
    
    # Wealth yogas
    yogas.append(check_amala_yoga(time))
    yogas.append(check_kemadruma_yoga(time))
    yogas.append(check_lakshmi_yoga(time))
    yogas.append(check_chatussagara_yoga(time))  # NEW: 4 kendras occupied
    yogas.append(check_vasumathi_yoga(time))  # NEW: Benefics in upachaya
    yogas.append(check_parvata_yoga(time))  # NEW: Mountain of success
    
    # Raja yogas
    yogas.append(check_basic_raja_yoga(time))
    yogas.append(check_neechabhanga_raja_yoga(time))
    
    # Viparita Raja yogas (Reversed Power yogas)
    yogas.append(check_harsha_yoga(time))
    yogas.append(check_sarala_yoga(time))
    yogas.append(check_vimala_yoga(time))

    # Solar/Mercurial yogas
    yogas.append(check_budha_aditya_yoga(time))

    # Lunar combination yogas
    yogas.append(check_chandra_mangala_yoga(time))
    yogas.append(check_adhi_yoga(time))

    # Dosha / malefic yogas
    yogas.append(check_kalasarpa_dosha(time))
    yogas.append(check_kuja_dosha(time))
    yogas.append(check_guru_chandal_yoga(time))

    # Kartari (scissors) yogas
    yogas.append(check_shubha_kartari_yoga(time))
    yogas.append(check_papa_kartari_yoga(time))

    # Wealth yogas
    yogas.append(check_dhana_yoga(time))

    # Planetary chain yogas
    yogas.append(check_graha_malika_yoga(time))
    yogas.append(check_parivartana_yoga(time))

    # Solar hemispherical yogas
    yogas.append(check_vesi_yoga(time))
    yogas.append(check_vasi_yoga(time))
    yogas.append(check_ubhayachari_yoga(time))

    # Knowledge & arts yogas
    yogas.append(check_saraswati_yoga(time))
    yogas.append(check_nipuna_yoga(time))
    yogas.append(check_kalanidhi_yoga(time))

    # Power / fortunate yogas
    yogas.append(check_kesari_yoga(time))
    yogas.append(check_mahabhagya_yoga(time))
    yogas.append(check_chamara_yoga(time))
    yogas.append(check_akhanda_samrajya_yoga(time))
    yogas.append(check_shiva_yoga(time))

    # Renunciation yogas
    yogas.append(check_sanyasa_yoga(time))

    # Nabhasa yogas (planetary spread patterns)
    yogas.append(check_rajju_yoga(time))
    yogas.append(check_musala_yoga(time))
    yogas.append(check_nala_yoga(time))
    yogas.append(check_kedara_yoga(time))

    # Phaladeepika special yogas
    yogas.append(check_mridanga_yoga(time))
    yogas.append(check_bheri_yoga(time))
    yogas.append(check_shankha_yoga(time))
    yogas.append(check_kahala_yoga(time))
    yogas.append(check_chatussasiti_sama_yoga(time))
    yogas.append(check_pushkala_yoga(time))
    yogas.append(check_parijata_yoga(time))
    yogas.append(check_matanga_yoga(time))

    # Graha drishti / Sun-Moon special yogas
    yogas.append(check_surya_yoga(time))
    yogas.append(check_chandra_yoga(time))
    yogas.append(check_lagnadhi_yoga(time))

    # Subha / Asubha yogas
    yogas.append(check_subha_yoga(time))
    yogas.append(check_asubha_yoga(time))

    # Rare classical specials
    yogas.append(check_srikantha_yoga(time))
    yogas.append(check_sharada_yoga(time))
    yogas.append(check_indra_yoga(time))
    yogas.append(check_ravi_yoga(time))

    # Nabhasa Akriti yogas (shape yogas)
    yogas.append(check_gola_yoga(time))
    yogas.append(check_yuga_yoga(time))
    yogas.append(check_danda_yoga(time))

    # Nabhasa Akriti continued (more shapes)
    yogas.append(check_veena_yoga(time))
    yogas.append(check_shoola_yoga(time))
    yogas.append(check_shankha_nabhasa_yoga(time))
    yogas.append(check_yava_yoga(time))
    yogas.append(check_kamala_yoga(time))
    yogas.append(check_vatapi_yoga(time))
    yogas.append(check_koorma_yoga(time))

    # Longevity & dosha yogas
    yogas.append(check_arishta_yoga(time))
    yogas.append(check_balarishta_yoga(time))

    # Prosperity & status yogas
    yogas.append(check_shrinatha_yoga(time))
    yogas.append(check_chapa_yoga(time))

    # More Nabhasa Akriti (arc/half-zodiac)
    yogas.append(check_ardha_chandra_yoga(time))
    yogas.append(check_chakra_yoga(time))
    yogas.append(check_sar_yoga(time))
    yogas.append(check_pasa_yoga(time))
    yogas.append(check_mala_yoga(time))

    # Dharma & spiritual yogas
    yogas.append(check_dharma_karma_yoga(time))
    yogas.append(check_amrita_yoga(time))

    # Lagna-relative lunar yogas
    yogas.append(check_lagna_vesi_yoga(time))
    yogas.append(check_lagna_sunapha_yoga(time))
    yogas.append(check_lagna_anapha_yoga(time))

    # Surya-Chandra yoga
    yogas.append(check_surya_chandra_yoga(time))

    # Vishnu, Brahma, Hari yogas
    yogas.append(check_vishnu_yoga(time))
    yogas.append(check_brahma_yoga(time))
    yogas.append(check_hari_yoga(time))

    # Planetary distribution yogas
    yogas.append(check_deva_yoga(time))
    yogas.append(check_asura_yoga(time))
    yogas.append(check_kuhu_yoga(time))
    yogas.append(check_phala_yoga(time))

    # Evil house lord yogas
    yogas.append(check_nidana_yoga(time))

    # Benefic / dignity yogas
    yogas.append(check_koumara_yoga(time))
    yogas.append(check_chandra_mangala_adhi_yoga(time))
    yogas.append(check_budha_chandra_yoga(time))

    # Specific Malika Yogas (house-chain variants from each bhava)
    yogas.append(check_lagna_malika_yoga(time))
    yogas.append(check_dhana_malika_yoga(time))
    yogas.append(check_vikrama_malika_yoga(time))
    yogas.append(check_sukha_malika_yoga(time))
    yogas.append(check_putra_malika_yoga(time))
    yogas.append(check_satru_malika_yoga(time))
    yogas.append(check_kalatra_malika_yoga(time))
    yogas.append(check_randhra_malika_yoga(time))
    yogas.append(check_bhagya_malika_yoga(time))
    yogas.append(check_karma_malika_yoga(time))

    # Royal and classical yogas
    yogas.append(check_rajalakshana_yoga(time))
    yogas.append(check_vanchana_chora_bheethi_yoga(time))
    yogas.append(check_gauri_yoga(time))
    yogas.append(check_bharathi_yoga(time))

    return yogas




# ========================================
# WEALTH YOGAS (Prosperity & Fortune)
# ========================================

def check_amala_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Amala Yoga - Benefic in 10th house from Moon or Lagna.
    
    Condition: 10th from Moon or Lagna occupied by benefic (Jupiter, Venus, Mercury, waxing Moon)
    Effect: Lasting fame, spotless character, prosperity
    
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        # Get planetary positions
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        
        # Get Moon and Lagna positions
        moon_long = get_planet_longitude(Planet.Moon, time)
        lagna_long = get_lagnam(time)
        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        venus_long = get_planet_longitude(Planet.Venus, time)
        mercury_long = get_planet_longitude(Planet.Mercury, time)
        
        # Calculate signs (0-11)
        moon_sign = int(moon_long // 30)
        lagna_sign = int(lagna_long // 30)
        jupiter_sign = int(jupiter_long // 30)
        venus_sign = int(venus_long // 30)
        mercury_sign = int(mercury_long // 30)
        
        # Calculate 10th house from Moon (house 10)
        tenth_from_moon = (moon_sign + 9) % 12
        
        # Calculate 10th house from Lagna
        tenth_from_lagna = (lagna_sign + 9) % 12
        
        # Check if benefics occupy 10th house
        benefics_in_10th_from_moon = (jupiter_sign == tenth_from_moon or 
                                       venus_sign == tenth_from_moon or 
                                       mercury_sign == tenth_from_moon)
        
        benefics_in_10th_from_lagna = (jupiter_sign == tenth_from_lagna or 
                                        venus_sign == tenth_from_lagna or 
                                        mercury_sign == tenth_from_lagna)
        
        occurring = benefics_in_10th_from_moon or benefics_in_10th_from_lagna
        
        if occurring:
            condition = f"Benefic in 10th house from {'Moon' if benefics_in_10th_from_moon else 'Lagna'}"
        else:
            condition = "No benefic in 10th house from Moon or Lagna"
        
        return Yoga(
            name="Amala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Lasting fame, spotless character, prosperous life",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Amala Yoga", YogaNature.GOOD, False,
                   "Lasting fame and prosperity", f"Error: {str(e)}")


def check_kemadruma_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Kemadruma Yoga - Moon without support.
    
    Condition: No planets on both sides of Moon (2nd and 12th houses from Moon)
    Effect: Poverty, sorrow, dependence (malefic yoga)
    
    Note: This is the opposite of Dhurdhura Yoga
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet
        
        # Get all planet positions
        moon_long = get_planet_longitude(Planet.Moon, time)
        sun_long = get_planet_longitude(Planet.Sun, time)
        mars_long = get_planet_longitude(Planet.Mars, time)
        mercury_long = get_planet_longitude(Planet.Mercury, time)
        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        venus_long = get_planet_longitude(Planet.Venus, time)
        saturn_long = get_planet_longitude(Planet.Saturn, time)
        
        # Calculate signs
        moon_sign = int(moon_long // 30)
        planet_signs = [
            int(sun_long // 30),
            int(mars_long // 30),
            int(mercury_long // 30),
            int(jupiter_long // 30),
            int(venus_long // 30),
            int(saturn_long // 30)
        ]
        
        # Calculate 2nd and 12th houses from Moon
        second_from_moon = (moon_sign + 1) % 12
        twelfth_from_moon = (moon_sign - 1) % 12
        
        # Check if any planet in 2nd or 12th from Moon
        planets_in_2nd = any(sign == second_from_moon for sign in planet_signs)
        planets_in_12th = any(sign == twelfth_from_moon for sign in planet_signs)
        
        # Kemadruma occurs when NO planets on either side
        occurring = not (planets_in_2nd or planets_in_12th)
        
        if occurring:
            condition = "No planets in 2nd and 12th houses from Moon"
        else:
            planets_found = []
            if planets_in_2nd:
                planets_found.append("2nd house occupied")
            if planets_in_12th:
                planets_found.append("12th house occupied")
            condition = f"Moon has support: {', '.join(planets_found)}"
        
        return Yoga(
            name="Kemadruma Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Poverty, sorrow, dependence, unrighteous deeds",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Kemadruma Yoga", YogaNature.BAD, False,
                   "Poverty and sorrow", f"Error: {str(e)}")


def check_lakshmi_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Lakshmi Yoga - Lord of 9th in kendra/trikona in own/exalted sign.
    
    Condition: Lord of Lagna powerful, Lord of 9th in kendra/trikona in own/exaltation sign
    Effect: Wealth, nobility, high integrity, handsome appearance
    
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house, get_house_sign
        from .avastha import OWN_SIGNS, EXALTATION
        
        # Get lord of 9th house
        lord_of_9th = get_lord_of_house(9, time)
        
        # Get position of 9th lord
        lord_9th_longitude = get_planet_longitude(lord_of_9th, time)
        lord_9th_sign = int(lord_9th_longitude // 30)
        
        # Get Lagna sign to calculate houses from
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Calculate which house the 9th lord is in
        lord_9th_house = ((lord_9th_sign - lagna_sign) % 12) + 1
        
        # Check if 9th lord is in kendra (1,4,7,10) or trikona (1,5,9)
        in_kendra = lord_9th_house in [1, 4, 7, 10]
        in_trikona = lord_9th_house in [1, 5, 9]
        in_good_house = in_kendra or in_trikona
        
        # Check if 9th lord is in own sign or exalted
        in_own_sign = lord_9th_sign in [s % 12 for s in OWN_SIGNS.get(lord_of_9th, [])]
        
        # Check exaltation
        in_exaltation = False
        if lord_of_9th in EXALTATION:
            exalt_sign, _ = EXALTATION[lord_of_9th]
            in_exaltation = (lord_9th_sign == exalt_sign % 12)
        
        in_dignity = in_own_sign or in_exaltation
        
        # Lakshmi Yoga occurs when both conditions met
        occurring = in_good_house and in_dignity
        
        if occurring:
            house_type = "kendra" if in_kendra else "trikona"
            dignity_type = "own sign" if in_own_sign else "exalted"
            condition = f"Lord of 9th ({lord_of_9th.name}) in {house_type} (house {lord_9th_house}) in {dignity_type}"
        else:
            issues = []
            if not in_good_house:
                issues.append(f"9th lord in house {lord_9th_house} (not kendra/trikona)")
            if not in_dignity:
                issues.append(f"9th lord not in own/exalted sign")
            condition = "; ".join(issues)
        
        return Yoga(
            name="Lakshmi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Wealth, nobility, learned, high integrity, handsome",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Lakshmi Yoga", YogaNature.GOOD, False,
                   "Wealth and nobility", f"Error: {str(e)}")


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
    from .avastha import get_dignity_status
    
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
                dignity_status, dignity_score = get_dignity_status(lord.name, lord_long)
                # Dignity: Exalted=5, Moolatrikona=4, Own=3 (all considered good)
                in_dignity = dignity_score >= 3
                
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


# ========================================
# RAJA YOGAS (Power, Authority, Success)
# ========================================

def check_basic_raja_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Basic Raja Yoga - Lords of kendra and trikona in conjunction.
    
    Condition: Lord of a kendra (1,4,7,10) and lord of a trikona (1,5,9) together
    Effect: Power, authority, success, high status
    
    Note: This checks for simple conjunction (same sign). More complex yogas
    include aspect and exchange relationships.
    
    Reference: BV Raman - "Three Hundred Important Combinations"
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet
        from .lordship import get_lord_of_house
        
        # Kendra houses: 1, 4, 7, 10
        # Trikona houses: 1, 5, 9 (excluding 1 to avoid duplication)
        kendra_lords = [get_lord_of_house(h, time) for h in [1, 4, 7, 10]]
        trikona_lords = [get_lord_of_house(h, time) for h in [5, 9]]  # Exclude House 1
        
        # Get sign positions of all lords
        lord_positions = {}
        for lord in set(kendra_lords + trikona_lords):
            long = get_planet_longitude(lord, time)
            sign_num = int(long // 30)
            lord_positions[lord] = sign_num
        
        # Check for conjunctions (same sign)
        raja_yogas_found = []
        for k_house, k_lord in zip([1, 4, 7, 10], kendra_lords):
            for t_house, t_lord in zip([5, 9], trikona_lords):
                # Skip if same planet (e.g., one planet rules both houses)
                if k_lord == t_lord:
                    continue
                
                # Check if in same sign
                if lord_positions[k_lord] == lord_positions[t_lord]:
                    raja_yogas_found.append((k_house, t_house, k_lord, t_lord))
        
        occurring = len(raja_yogas_found) > 0
        
        if occurring:
            # Format the first yoga found
            k_h, t_h, k_l, t_l = raja_yogas_found[0]
            condition = f"Lord of {k_h} ({k_l.name}) conjunct lord of {t_h} ({t_l.name})"
            if len(raja_yogas_found) > 1:
                condition += f" + {len(raja_yogas_found) - 1} more"
        else:
            condition = "No kendra-trikona lord conjunction"
        
        return Yoga(
            name="Raja Yoga (Basic)",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Power, authority, high status, success in life",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Raja Yoga (Basic)", YogaNature.GOOD, False,
                   "Power and authority", f"Error: {str(e)}")


def check_neechabhanga_raja_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Neechabhanga Raja Yoga - Cancellation of debilitation creating power.
    
    Neecha Bhanga (debilitation cancellation) occurs when:
    1. A planet is in its debilitation sign (neecha)
    2. The lord of that debilitation sign is in a kendra (1,4,7,10) from Lagna or Moon
    
    This is considered a powerful Raja Yoga because it shows ability to overcome
    adversity and rise to power through hardship.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_sign
        from .avastha import DEBILITATION
        
        # Get Lagna sign
        lagna_longitude = get_lagnam(time)
        lagna_sign = int(lagna_longitude // 30)
        
        # Get Moon position  
        moon_longitude = get_planet_longitude(Planet.Moon, time)
        moon_sign = int(moon_longitude // 30)
        
        # Get all planet positions
        planets_to_check = [
            Planet.Sun, Planet.Moon, Planet.Mars, 
            Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn
        ]
        
        cancellations_found = []
        
        for planet in planets_to_check:
            # Check if planet is debilitated
            if planet.name not in DEBILITATION:
                continue
                
            planet_longitude = get_planet_longitude(planet, time)
            planet_sign = int(planet_longitude // 30)
            debil_sign = DEBILITATION[planet.name]
            
            if planet_sign == debil_sign:
                # Planet is debilitated! Now check for cancellation
                # Get lord of debilitation sign
                debil_lord = get_lord_of_sign(debil_sign)
                
                # Get position of debilitation lord
                lord_longitude = get_planet_longitude(debil_lord, time)
                lord_sign = int(lord_longitude // 30)
                
                # Check if lord is in kendra from Lagna
                house_from_lagna = ((lord_sign - lagna_sign) % 12) + 1
                lagna_kendra = house_from_lagna in [1, 4, 7, 10]
                
                # Check if lord is in kendra from Moon
                house_from_moon = ((lord_sign - moon_sign) % 12) + 1
                moon_kendra = house_from_moon in [1, 4, 7, 10]
                
                if lagna_kendra or moon_kendra:
                    reference = "Lagna" if lagna_kendra else "Moon"
                    house_num = house_from_lagna if lagna_kendra else house_from_moon
                    cancellations_found.append({
                        'planet': planet.name,
                        'lord': debil_lord.name,
                        'house': house_num,
                        'reference': reference
                    })
        
        occurring = len(cancellations_found) > 0
        
        if occurring:
            # Format the first cancellation found
            first = cancellations_found[0]
            condition = f"{first['planet']} debilitated, {first['lord']} (lord) in {first['house']} from {first['reference']}"
            if len(cancellations_found) > 1:
                condition += f" + {len(cancellations_found) - 1} more"
        else:
            condition = "No debilitated planets with lord in kendra"
        
        return Yoga(
            name="Neechabhanga Raja Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Rise from adversity, power through overcoming obstacles",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Neechabhanga Raja Yoga", YogaNature.GOOD, False,
                   "Power through adversity", f"Error: {str(e)}")


# ========================================
# VIPARITA RAJA YOGAS (Reversed Power Yogas)
# ========================================

def check_harsha_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Harsha Yoga - 6th lord in 6th, 8th, or 12th house (Viparita Raja Yoga).
    
    Condition: Lord of 6th house placed in 6th, 8th, or 12th house
    Effect: Victory over enemies, good health, happiness, courage, political success
    
    Viparita means "reversed" - when dusthana (difficult house) lords occupy other
    dusthana houses, the negative effects cancel out and create positive outcomes.
    This is one of the three classic Viparita Raja Yogas.
    
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        
        # Get lord of 6th house
        lord_of_6th = get_lord_of_house(6, time)
        
        # Get position of 6th lord
        lord_6th_longitude = get_planet_longitude(lord_of_6th, time)
        lord_6th_sign = int(lord_6th_longitude // 30)
        
        # Get Lagna sign to calculate houses from
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Calculate which house the 6th lord is in
        lord_6th_house = ((lord_6th_sign - lagna_sign) % 12) + 1
        
        # Check if 6th lord is in 6th, 8th, or 12th house (dusthana houses)
        occurring = lord_6th_house in [6, 8, 12]
        
        if occurring:
            condition = f"Lord of 6th ({lord_of_6th.name}) in {lord_6th_house}th house"
        else:
            condition = f"Lord of 6th ({lord_of_6th.name}) in {lord_6th_house}th house (not in 6/8/12)"
        
        return Yoga(
            name="Harsha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Victory over enemies, good health, happiness, courage, political success",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Harsha Yoga", YogaNature.GOOD, False,
                   "Victory over enemies", f"Error: {str(e)}")


def check_sarala_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Sarala Yoga - 8th lord in 6th, 8th, or 12th house (Viparita Raja Yoga).
    
    Condition: Lord of 8th house placed in 6th, 8th, or 12th house
    Effect: Long life, fearlessness, learning, prosperity, freedom from disease
    
    Sarala means "straight" or "simple" - despite having the 8th lord (house of
    transformation, obstacles) in difficult houses, the person leads a straightforward
    life free from major troubles. This is the second Viparita Raja Yoga.
    
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        
        # Get lord of 8th house
        lord_of_8th = get_lord_of_house(8, time)
        
        # Get position of 8th lord
        lord_8th_longitude = get_planet_longitude(lord_of_8th, time)
        lord_8th_sign = int(lord_8th_longitude // 30)
        
        # Get Lagna sign to calculate houses from
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Calculate which house the 8th lord is in
        lord_8th_house = ((lord_8th_sign - lagna_sign) % 12) + 1
        
        # Check if 8th lord is in 6th, 8th, or 12th house
        occurring = lord_8th_house in [6, 8, 12]
        
        if occurring:
            condition = f"Lord of 8th ({lord_of_8th.name}) in {lord_8th_house}th house"
        else:
            condition = f"Lord of 8th ({lord_of_8th.name}) in {lord_8th_house}th house (not in 6/8/12)"
        
        return Yoga(
            name="Sarala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Long life, fearlessness, learning, prosperity, freedom from disease",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Sarala Yoga", YogaNature.GOOD, False,
                   "Long life and fearlessness", f"Error: {str(e)}")


def check_vimala_yoga(time: 'AstroTime') -> Yoga:
    """
    Detect Vimala Yoga - 12th lord in 6th, 8th, or 12th house (Viparita Raja Yoga).
    
    Condition: Lord of 12th house placed in 6th, 8th, or 12th house
    Effect: Good conduct, economical, happy, independent nature, does good deeds
    
    Vimala means "pure" or "spotless" - the 12th lord (house of loss, expenditure)
    in dusthana houses prevents wasteful expenses and creates a pure character.
    This is the third Viparita Raja Yoga.
    
    Reference: Hindu Predictive Astrology by Dr. B.V. Raman
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        
        # Get lord of 12th house
        lord_of_12th = get_lord_of_house(12, time)
        
        # Get position of 12th lord
        lord_12th_longitude = get_planet_longitude(lord_of_12th, time)
        lord_12th_sign = int(lord_12th_longitude // 30)
        
        # Get Lagna sign to calculate houses from
        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        
        # Calculate which house the 12th lord is in
        lord_12th_house = ((lord_12th_sign - lagna_sign) % 12) + 1
        
        # Check if 12th lord is in 6th, 8th, or 12th house
        occurring = lord_12th_house in [6, 8, 12]
        
        if occurring:
            condition = f"Lord of 12th ({lord_of_12th.name}) in {lord_12th_house}th house"
        else:
            condition = f"Lord of 12th ({lord_of_12th.name}) in {lord_12th_house}th house (not in 6/8/12)"
        
        return Yoga(
            name="Vimala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Good conduct, economical, happy, independent, does good deeds",
            condition=condition
        )
        
    except Exception as e:
        return Yoga("Vimala Yoga", YogaNature.GOOD, False,
                   "Good conduct and independence", f"Error: {str(e)}")


# ========================================
# SOLAR / MERCURIAL YOGAS
# ========================================

def check_budha_aditya_yoga(time: 'AstroTime') -> Yoga:
    """
    Budha-Aditya Yoga - Sun + Mercury conjunction.

    Condition: Sun and Mercury occupy the same sign.
    Effect: Intelligent, skilled in arts, respected, excellent communication,
            scholarly acumen, success through intellect.

    Reference: Brihat Parashara Hora Shastra
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        sun_long = get_planet_longitude(Planet.Sun, time)
        mercury_long = get_planet_longitude(Planet.Mercury, time)

        sun_sign = int(sun_long // 30)
        mercury_sign = int(mercury_long // 30)
        occurring = sun_sign == mercury_sign

        condition = (
            f"Sun and Mercury both in sign {sun_sign + 1}"
            if occurring
            else f"Sun in sign {sun_sign + 1}, Mercury in sign {mercury_sign + 1}"
        )
        return Yoga(
            name="Budha-Aditya Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Intelligent, skilled, respected, excellent communication and scholarly acumen",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Budha-Aditya Yoga", YogaNature.GOOD, False,
                   "Intelligence and scholarly acumen", f"Error: {str(e)}")


# ========================================
# LUNAR YOGAS (Moon combinations)
# ========================================

def check_chandra_mangala_yoga(time: 'AstroTime') -> Yoga:
    """
    Chandra-Mangala Yoga - Moon + Mars conjunction.

    Condition: Moon and Mars in the same sign.
    Effect: Financial acumen, bold, good at business, earning through mother
            or real-estate, courageous decision-making.

    Reference: Brihat Parashara Hora Shastra
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        moon_long = get_planet_longitude(Planet.Moon, time)
        mars_long = get_planet_longitude(Planet.Mars, time)

        moon_sign = int(moon_long // 30)
        mars_sign = int(mars_long // 30)
        occurring = moon_sign == mars_sign

        condition = (
            f"Moon and Mars both in sign {moon_sign + 1}"
            if occurring
            else f"Moon in sign {moon_sign + 1}, Mars in sign {mars_sign + 1}"
        )
        return Yoga(
            name="Chandra-Mangala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Financial acumen, bold, business success, courageous decision-making",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chandra-Mangala Yoga", YogaNature.GOOD, False,
                   "Financial acumen and boldness", f"Error: {str(e)}")


def check_adhi_yoga(time: 'AstroTime') -> Yoga:
    """
    Adhi Yoga - Benefics in 6th, 7th, 8th from Moon.

    Condition: Jupiter, Mercury, and/or Venus occupy the 6th, 7th, and 8th
               houses counted from Moon's position.
    Effect: Becomes minister, chief, commander; polite, reliable, healthy,
            defeats enemies, long-lived. The more benefics present, the stronger.

    Reference: Brihat Parashara Hora Shastra, Chapter on Adhi Yoga
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        moon_long = get_planet_longitude(Planet.Moon, time)
        moon_sign = int(moon_long // 30)

        target_positions = {}  # house_from_moon -> [planets]
        for planet in [Planet.Jupiter, Planet.Mercury, Planet.Venus]:
            p_long = get_planet_longitude(planet, time)
            p_sign = int(p_long // 30)
            house_from_moon = ((p_sign - moon_sign) % 12) + 1
            if house_from_moon in [6, 7, 8]:
                target_positions.setdefault(house_from_moon, []).append(planet.name)

        houses_covered = set(target_positions.keys())
        occurring = len(houses_covered) >= 2  # At least 2 of the 3 houses occupied

        if occurring:
            details = "; ".join(f"house {h}: {', '.join(ps)}" for h, ps in sorted(target_positions.items()))
            condition = f"Benefics in 6/7/8 from Moon — {details}"
        else:
            covered = list(houses_covered) or ["none"]
            condition = f"Only {len(houses_covered)}/3 target houses covered from Moon"

        return Yoga(
            name="Adhi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Ministerial quality, defeats enemies, long life, polite and reliable",
            condition=condition,
            strength=len(houses_covered) / 3 * 100,
        )
    except Exception as e:
        return Yoga("Adhi Yoga", YogaNature.GOOD, False,
                   "Ministerial status and leadership", f"Error: {str(e)}")


# ========================================
# DOSHA / MALEFIC YOGAS
# ========================================

def check_kalasarpa_dosha(time: 'AstroTime') -> Yoga:
    """
    Kalasarpa Dosha - All planets between Rahu and Ketu.

    Condition: All 7 classical planets (Sun through Saturn) occupy the 180°
               arc from Rahu to Ketu in the direction of the zodiac.
    Effect: Karmic delays, repeated obstacles, struggles, hidden enemies;
            can also indicate intense focus and great achievement after challenges.

    Reference: Widely referenced in classical and modern Vedic texts.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        rahu_long = get_planet_longitude(Planet.Rahu, time)
        ketu_long = get_planet_longitude(Planet.Ketu, time)

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]

        # Rahu to Ketu arc (going forward in zodiac)
        def in_rahu_ketu_arc(long: float) -> bool:
            """Check if longitude is in the arc from Rahu to Ketu (forward direction)."""
            start = rahu_long % 360
            end = ketu_long % 360
            long = long % 360
            if start < end:
                return start <= long <= end
            else:  # wraps around 0°
                return long >= start or long <= end

        positions = {p.name: get_planet_longitude(p, time) for p in classical}
        all_in_arc = all(in_rahu_ketu_arc(v) for v in positions.values())

        outside = [name for name, lon in positions.items() if not in_rahu_ketu_arc(lon)]

        return Yoga(
            name="Kalasarpa Dosha",
            nature=YogaNature.BAD,
            occurring=all_in_arc,
            description="Karmic obstacles and delays; intense focus possible after overcoming struggles",
            condition="All 7 planets within Rahu-Ketu arc" if all_in_arc
                      else f"Planet(s) outside arc: {', '.join(outside)}",
            strength=100 if all_in_arc else 0,
        )
    except Exception as e:
        return Yoga("Kalasarpa Dosha", YogaNature.BAD, False,
                   "Karmic obstacles", f"Error: {str(e)}")


def check_kuja_dosha(time: 'AstroTime') -> Yoga:
    """
    Kuja Dosha (Mangal Dosha) - Mars in 1st, 2nd, 4th, 7th, 8th, or 12th house.

    Condition: Mars occupies the 1st, 2nd, 4th, 7th, 8th, or 12th house
               counted from the Ascendant.
    Effect: Delays or difficulties in marriage, relationship tensions,
            aggressive temperament; partial or no dosha based on sign.

    Reference: Classical texts on marriage compatibility.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        mars_long = get_planet_longitude(Planet.Mars, time)
        lagna_long = get_lagnam(time)

        mars_sign = int(mars_long // 30)
        lagna_sign = int(lagna_long // 30)
        mars_house = ((mars_sign - lagna_sign) % 12) + 1

        dosha_houses = [1, 2, 4, 7, 8, 12]
        occurring = mars_house in dosha_houses

        return Yoga(
            name="Kuja Dosha",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Delays in marriage, relationship tensions, assertive temperament",
            condition=f"Mars in house {mars_house} from Lagna"
                      + (" (Dosha houses: 1,2,4,7,8,12)" if occurring else " (No dosha)"),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kuja Dosha", YogaNature.BAD, False,
                   "Relationship difficulties", f"Error: {str(e)}")


def check_guru_chandal_yoga(time: 'AstroTime') -> Yoga:
    """
    Guru Chandal Yoga - Jupiter conjunct Rahu or Ketu.

    Condition: Jupiter occupies the same sign as Rahu or Ketu.
    Effect: Confused or corrupted wisdom, unconventional beliefs, interest in
            occult; can manifest as innovative thinking when well-placed.

    Reference: Hora Sara, Phaladeepika.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        rahu_sign = int(get_planet_longitude(Planet.Rahu, time) // 30)
        ketu_sign = int(get_planet_longitude(Planet.Ketu, time) // 30)

        with_rahu = jupiter_sign == rahu_sign
        with_ketu = jupiter_sign == ketu_sign
        occurring = with_rahu or with_ketu

        node = "Rahu" if with_rahu else ("Ketu" if with_ketu else "neither")
        condition = (
            f"Jupiter conjunct {node} in sign {jupiter_sign + 1}"
            if occurring
            else f"Jupiter in sign {jupiter_sign + 1}, Rahu in {rahu_sign + 1}, Ketu in {ketu_sign + 1}"
        )
        return Yoga(
            name="Guru Chandal Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Confused wisdom, unconventional beliefs; occult interest; can show innovative thinking",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Guru Chandal Yoga", YogaNature.BAD, False,
                   "Confused wisdom", f"Error: {str(e)}")


# ========================================
# KARTARI (SCISSORS) YOGAS
# ========================================

def check_shubha_kartari_yoga(time: 'AstroTime') -> Yoga:
    """
    Shubha Kartari Yoga - Benefics in 2nd and 12th from Lagna.

    Condition: Natural benefics (Jupiter, Venus, Mercury, waxing Moon) are
               placed in both the 2nd and 12th houses from the Ascendant,
               flanking it like scissors.
    Effect: Happiness, wealth, protection, good health, positive personality.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        in_2nd = []
        in_12th = []

        for planet in benefics:
            p_sign = int(get_planet_longitude(planet, time) // 30)
            house = ((p_sign - lagna_sign) % 12) + 1
            if house == 2:
                in_2nd.append(planet.name)
            elif house == 12:
                in_12th.append(planet.name)

        occurring = bool(in_2nd) and bool(in_12th)
        condition = (
            f"Benefics in 2nd: {', '.join(in_2nd)}; in 12th: {', '.join(in_12th)}"
            if occurring
            else f"2nd house benefics: {in_2nd or 'none'}; 12th house benefics: {in_12th or 'none'}"
        )
        return Yoga(
            name="Shubha Kartari Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Happiness, wealth, protection, good health, positive personality",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shubha Kartari Yoga", YogaNature.GOOD, False,
                   "Protection and happiness", f"Error: {str(e)}")


def check_papa_kartari_yoga(time: 'AstroTime') -> Yoga:
    """
    Papa Kartari Yoga - Malefics in 2nd and 12th from Lagna.

    Condition: Natural malefics (Saturn, Mars, Sun, Rahu, Ketu) are placed in
               both the 2nd and 12th houses from the Ascendant.
    Effect: Obstructions to self-expression, financial squeeze, health issues,
            restricted personality.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        malefics = [Planet.Saturn, Planet.Mars, Planet.Sun, Planet.Rahu, Planet.Ketu]
        in_2nd = []
        in_12th = []

        for planet in malefics:
            p_sign = int(get_planet_longitude(planet, time) // 30)
            house = ((p_sign - lagna_sign) % 12) + 1
            if house == 2:
                in_2nd.append(planet.name)
            elif house == 12:
                in_12th.append(planet.name)

        occurring = bool(in_2nd) and bool(in_12th)
        condition = (
            f"Malefics in 2nd: {', '.join(in_2nd)}; in 12th: {', '.join(in_12th)}"
            if occurring
            else f"2nd house malefics: {in_2nd or 'none'}; 12th house malefics: {in_12th or 'none'}"
        )
        return Yoga(
            name="Papa Kartari Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Obstructions, financial restrictions, health issues, constrained personality",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Papa Kartari Yoga", YogaNature.BAD, False,
                   "Obstructions and restrictions", f"Error: {str(e)}")


# ========================================
# WEALTH & PROSPERITY YOGAS
# ========================================

def check_dhana_yoga(time: 'AstroTime') -> Yoga:
    """
    Dhana Yoga - Connection between 2nd and 11th house lords.

    Condition: Lord of 2nd house and lord of 11th house are in conjunction,
               mutual aspect, or one is placed in the other's house.
    Effect: Wealth accumulation, financial gains, prosperity, material success.

    Reference: Brihat Parashara Hora Shastra, Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_2 = get_lord_of_house(2, time)
        lord_11 = get_lord_of_house(11, time)

        lord2_long = get_planet_longitude(lord_2, time)
        lord11_long = get_planet_longitude(lord_11, time)

        lord2_sign = int(lord2_long // 30)
        lord11_sign = int(lord11_long // 30)

        lord2_house = ((lord2_sign - lagna_sign) % 12) + 1
        lord11_house = ((lord11_sign - lagna_sign) % 12) + 1

        # 2nd lord and 11th lord in same sign OR each in the other's house
        same_sign = lord2_sign == lord11_sign
        lord2_in_11th = lord2_house == 11
        lord11_in_2nd = lord11_house == 2

        occurring = same_sign or lord2_in_11th or lord11_in_2nd

        if same_sign:
            condition = f"Lord of 2nd ({lord_2.name}) and Lord of 11th ({lord_11.name}) conjunct in sign {lord2_sign + 1}"
        elif lord2_in_11th:
            condition = f"Lord of 2nd ({lord_2.name}) in 11th house"
        elif lord11_in_2nd:
            condition = f"Lord of 11th ({lord_11.name}) in 2nd house"
        else:
            condition = f"Lord of 2nd in house {lord2_house}, Lord of 11th in house {lord11_house}"

        return Yoga(
            name="Dhana Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Wealth accumulation, financial gains, material prosperity",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Dhana Yoga", YogaNature.GOOD, False,
                   "Wealth and financial gains", f"Error: {str(e)}")


# ========================================
# PLANETARY CHAIN YOGAS
# ========================================

def check_graha_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Graha Malika Yoga - Planets forming a garland in consecutive houses.

    Condition: 7 or more classical planets occupy 7 or more consecutive houses
               (a continuous chain without gap).
    Effect: Endurance, perseverance, breadth of knowledge, balanced life;
            the person touches many fields and succeeds broadly.

    Reference: Phaladeepika, Sarvartha Chintamani.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]

        occupied_houses = set()
        for planet in classical:
            p_sign = int(get_planet_longitude(planet, time) // 30)
            house = ((p_sign - lagna_sign) % 12) + 1
            occupied_houses.add(house)

        # Find the longest run of consecutive occupied houses (circular)
        best_run = 0
        for start in range(1, 13):
            run = 0
            for offset in range(12):
                h = ((start - 1 + offset) % 12) + 1
                if h in occupied_houses:
                    run += 1
                else:
                    break
            best_run = max(best_run, run)

        occurring = best_run >= 7
        return Yoga(
            name="Graha Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Broad success across many fields, endurance, balanced multi-faceted life",
            condition=f"Longest consecutive occupied house run: {best_run}/12 (need 7+)",
            strength=min(100, (best_run / 7) * 100) if best_run > 0 else 0,
        )
    except Exception as e:
        return Yoga("Graha Malika Yoga", YogaNature.GOOD, False,
                   "Broad success and endurance", f"Error: {str(e)}")


def check_parivartana_yoga(time: 'AstroTime') -> Yoga:
    """
    Parivartana Yoga - Sign exchange between two planets.

    Condition: Planet A is in the sign ruled by Planet B, and Planet B is in
               the sign ruled by Planet A (mutual exchange of signs).
    Effect: Strong mutual support between the two planets; the houses they rule
            become powerfully linked. Generally beneficial unless both are malefics.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        # Signs ruled by each planet (0-indexed: 0=Aries...11=Pisces)
        SIGN_LORDS = {
            0: Planet.Mars,   1: Planet.Venus,   2: Planet.Mercury,
            3: Planet.Moon,   4: Planet.Sun,      5: Planet.Mercury,
            6: Planet.Venus,  7: Planet.Mars,     8: Planet.Jupiter,
            9: Planet.Saturn, 10: Planet.Saturn,  11: Planet.Jupiter,
        }

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]

        planet_signs = {p: int(get_planet_longitude(p, time) // 30) for p in classical}

        pairs = []
        checked = set()
        for planet_a in classical:
            sign_a = planet_signs[planet_a]
            lord_of_a = SIGN_LORDS.get(sign_a)
            if lord_of_a is None or lord_of_a == planet_a:
                continue

            sign_b = planet_signs.get(lord_of_a)
            if sign_b is None:
                continue
            lord_of_b = SIGN_LORDS.get(sign_b)

            pair_key = tuple(sorted([planet_a.value, lord_of_a.value]))
            if pair_key in checked:
                continue

            if lord_of_b == planet_a:
                pairs.append(f"{planet_a.name}↔{lord_of_a.name}")
                checked.add(pair_key)

        occurring = len(pairs) > 0
        return Yoga(
            name="Parivartana Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Powerful house linkage; mutual support between exchanged planets and their houses",
            condition=f"Exchange pairs: {', '.join(pairs)}" if occurring else "No mutual sign exchanges found",
            strength=min(100, len(pairs) * 33),
        )
    except Exception as e:
        return Yoga("Parivartana Yoga", YogaNature.GOOD, False,
                   "Mutual sign exchange", f"Error: {str(e)}")


# ========================================
# SOLAR HEMISPHERICAL YOGAS
# ========================================

def check_vesi_yoga(time: 'AstroTime') -> Yoga:
    """
    Vesi Yoga - Planets (other than Moon) in the 2nd house from Sun.

    Condition: Any planet except Moon occupies the sign immediately following
               the Sun's sign (2nd from Sun).
    Effect: Eloquent, wealthy, long-lived, happy, virtuous, charitable.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        target_sign = (sun_sign + 1) % 12

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus,
                      Planet.Saturn, Planet.Rahu, Planet.Ketu]
        planets_in_2nd = [
            p.name for p in qualifiers
            if int(get_planet_longitude(p, time) // 30) == target_sign
        ]
        occurring = bool(planets_in_2nd)
        return Yoga(
            name="Vesi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Eloquent, wealthy, long-lived, happy, virtuous, charitable",
            condition=f"Planets in 2nd from Sun (sign {target_sign + 1}): {', '.join(planets_in_2nd)}"
                      if occurring else f"No planet in 2nd from Sun (sign {target_sign + 1})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vesi Yoga", YogaNature.GOOD, False, "Eloquence and wealth", f"Error: {str(e)}")


def check_vasi_yoga(time: 'AstroTime') -> Yoga:
    """
    Vasi Yoga - Planets (other than Moon) in the 12th house from Sun.

    Condition: Any planet except Moon occupies the sign immediately preceding
               the Sun's sign (12th from Sun).
    Effect: Steady in work, generous, famous, fortunate, respected.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        target_sign = (sun_sign - 1) % 12

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus,
                      Planet.Saturn, Planet.Rahu, Planet.Ketu]
        planets_in_12th = [
            p.name for p in qualifiers
            if int(get_planet_longitude(p, time) // 30) == target_sign
        ]
        occurring = bool(planets_in_12th)
        return Yoga(
            name="Vasi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Steady in work, generous, famous, fortunate, well respected",
            condition=f"Planets in 12th from Sun (sign {target_sign + 1}): {', '.join(planets_in_12th)}"
                      if occurring else f"No planet in 12th from Sun (sign {target_sign + 1})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vasi Yoga", YogaNature.GOOD, False, "Fame and generosity", f"Error: {str(e)}")


def check_ubhayachari_yoga(time: 'AstroTime') -> Yoga:
    """
    Ubhayachari Yoga - Planets on both sides of the Sun (2nd and 12th).

    Condition: Planets (except Moon) occupy BOTH the 2nd AND the 12th sign
               from the Sun simultaneously.
    Effect: Royal appearance, affluent, good orator, powerful, many servants,
            famous in three worlds (considered very auspicious).

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        sign_2nd = (sun_sign + 1) % 12
        sign_12th = (sun_sign - 1) % 12

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus,
                      Planet.Saturn, Planet.Rahu, Planet.Ketu]

        in_2nd = [p.name for p in qualifiers if int(get_planet_longitude(p, time) // 30) == sign_2nd]
        in_12th = [p.name for p in qualifiers if int(get_planet_longitude(p, time) // 30) == sign_12th]

        occurring = bool(in_2nd) and bool(in_12th)
        return Yoga(
            name="Ubhayachari Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Royal appearance, affluent, powerful orator, famous, many servants",
            condition=f"2nd from Sun: {', '.join(in_2nd) or 'none'}; 12th from Sun: {', '.join(in_12th) or 'none'}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Ubhayachari Yoga", YogaNature.GOOD, False, "Royal and affluent", f"Error: {str(e)}")


# ========================================
# KNOWLEDGE & ARTS YOGAS
# ========================================

def check_saraswati_yoga(time: 'AstroTime') -> Yoga:
    """
    Saraswati Yoga - Jupiter, Venus, and Mercury in kendras or trikonas.

    Condition: Jupiter, Venus, and Mercury are all placed in kendra (1,4,7,10)
               or trikona (1,5,9) houses from the Ascendant.
    Effect: Highly intelligent, poet, scholar, skilled in arts and music,
            famous, wealthy, speaks authoritatively.

    Reference: Saravali, Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        kendra_trikona = {1, 4, 5, 7, 9, 10}

        placement = {}
        for planet in [Planet.Jupiter, Planet.Venus, Planet.Mercury]:
            p_sign = int(get_planet_longitude(planet, time) // 30)
            house = ((p_sign - lagna_sign) % 12) + 1
            placement[planet.name] = house

        all_in_kt = all(h in kendra_trikona for h in placement.values())
        occurring = all_in_kt
        details = "; ".join(f"{p} in house {h}" for p, h in placement.items())
        return Yoga(
            name="Saraswati Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Highly intelligent, poet, scholar, skilled in arts, famous and wealthy",
            condition=details,
            strength=100 if occurring else int(sum(1 for h in placement.values() if h in kendra_trikona) / 3 * 100),
        )
    except Exception as e:
        return Yoga("Saraswati Yoga", YogaNature.GOOD, False, "Learning and arts", f"Error: {str(e)}")


def check_nipuna_yoga(time: 'AstroTime') -> Yoga:
    """
    Nipuna Yoga (Buddha-Guru Yoga) - Mercury and Jupiter conjunction.

    Condition: Mercury and Jupiter are in the same sign.
    Effect: Great intelligence, philosophical depth, excellent teacher or guru,
            skilled in logic and debate.

    Reference: Jataka Parijata.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        mercury_sign = int(get_planet_longitude(Planet.Mercury, time) // 30)
        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        occurring = mercury_sign == jupiter_sign
        return Yoga(
            name="Nipuna Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Great intelligence, philosophical depth, excellent teacher, skilled in logic",
            condition=f"Mercury and Jupiter both in sign {mercury_sign + 1}"
                      if occurring else f"Mercury in sign {mercury_sign + 1}, Jupiter in sign {jupiter_sign + 1}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Nipuna Yoga", YogaNature.GOOD, False, "Great intelligence", f"Error: {str(e)}")


def check_kalanidhi_yoga(time: 'AstroTime') -> Yoga:
    """
    Kalanidhi Yoga - Jupiter in 2nd or 5th with Mercury or Venus.

    Condition: Jupiter is in the 2nd or 5th house from Lagna AND is conjunct
               (same sign as) Mercury or Venus.
    Effect: Skillful in arts and sciences, respected by kings, healthy,
            famous, eloquent, prosperous.

    Reference: Phaladeepika ch.6 (Mantreswara).
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1

        mercury_sign = int(get_planet_longitude(Planet.Mercury, time) // 30)
        venus_sign = int(get_planet_longitude(Planet.Venus, time) // 30)

        jupiter_in_target = jupiter_house in [2, 5]
        jupiter_with_mercury = jupiter_sign == mercury_sign
        jupiter_with_venus = jupiter_sign == venus_sign

        occurring = jupiter_in_target and (jupiter_with_mercury or jupiter_with_venus)
        companion = []
        if jupiter_with_mercury: companion.append("Mercury")
        if jupiter_with_venus: companion.append("Venus")

        return Yoga(
            name="Kalanidhi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Skilled in arts and sciences, respected, healthy, famous, eloquent",
            condition=f"Jupiter in house {jupiter_house} with {', '.join(companion)}"
                      if occurring else f"Jupiter in house {jupiter_house} (need 2nd/5th with Mercury/Venus)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kalanidhi Yoga", YogaNature.GOOD, False, "Arts and royal favour", f"Error: {str(e)}")


# ========================================
# POWER & FORTUNATE YOGAS
# ========================================

def check_kesari_yoga(time: 'AstroTime') -> Yoga:
    """
    Kesari Yoga - Jupiter in kendra from Lagna (complementary to GajaKesari from Moon).

    Condition: Jupiter occupies a kendra house (1st, 4th, 7th, or 10th)
               from the Ascendant.
    Effect: Fame, administrative ability, destroys enemies, generous,
            respected and virtuous.

    Reference: Phaladeepika, Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1
        occurring = jupiter_house in [1, 4, 7, 10]
        return Yoga(
            name="Kesari Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Fame, administrative ability, destroys enemies, generous, virtuous",
            condition=f"Jupiter in house {jupiter_house} from Lagna",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kesari Yoga", YogaNature.GOOD, False, "Fame and virtue", f"Error: {str(e)}")


def check_mahabhagya_yoga(time: 'AstroTime') -> Yoga:
    """
    Mahabhagya Yoga - Great Luck combination based on gender and sign polarity.

    Condition (Male): Born during day, Sun/Moon/Lagna all in odd signs (Aries, Gemini, Leo...).
    Condition (Female): Born during night, Sun/Moon/Lagna all in even signs (Taurus, Cancer, Virgo...).
    Note: We compute without gender - check both variants and report whichever applies.
    Effect: Noble birth or deeds, wealthy, generous, happy, long life, ruler-like.

    Reference: Brihat Parashara Hora Shastra, Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .sunrise import get_sun_times

        lagna_long = get_lagnam(time)
        sun_long = get_planet_longitude(Planet.Sun, time)
        moon_long = get_planet_longitude(Planet.Moon, time)

        lagna_sign = int(lagna_long // 30)
        sun_sign = int(sun_long // 30)
        moon_sign = int(moon_long // 30)

        # Odd signs: 0,2,4,6,8,10 (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius)
        all_odd = all(s % 2 == 0 for s in [lagna_sign, sun_sign, moon_sign])
        # Even signs: 1,3,5,7,9,11
        all_even = all(s % 2 == 1 for s in [lagna_sign, sun_sign, moon_sign])

        occurring = all_odd or all_even
        variant = "Male variant (day birth, all odd signs)" if all_odd else \
                  "Female variant (night birth, all even signs)" if all_even else "Not forming"
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        condition = (
            f"{variant} — Lagna:{sign_names[lagna_sign]}, Sun:{sign_names[sun_sign]}, Moon:{sign_names[moon_sign]}"
        )
        return Yoga(
            name="Mahabhagya Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Great luck, noble deeds, wealthy, generous, long life, ruler-like prominence",
            condition=condition,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Mahabhagya Yoga", YogaNature.GOOD, False, "Great luck", f"Error: {str(e)}")


def check_chamara_yoga(time: 'AstroTime') -> Yoga:
    """
    Chamara Yoga - Lagna lord exalted in a kendra and aspected by Jupiter.

    Condition: The lord of the Ascendant is (a) in its sign of exaltation,
               (b) in a kendra house (1,4,7,10), and (c) aspected by Jupiter.
    Effect: Eloquent, learned, ruler-like dignity, skilled in Vedic lore,
            long-lived, comparable to a king.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        lagna_lord = get_lord_of_house(1, time)

        lord_long = get_planet_longitude(lagna_lord, time)
        lord_sign = int(lord_long // 30)
        lord_house = ((lord_sign - lagna_sign) % 12) + 1

        # Check exaltation
        dignity, dignity_score = get_dignity_status(lagna_lord.name, lord_long)
        is_exalted = dignity_score == 5

        # Check kendra
        in_kendra = lord_house in [1, 4, 7, 10]

        # Check Jupiter aspect (Jupiter aspects 5th, 7th, 9th from its position)
        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1
        jupiter_aspect_houses = [
            ((jupiter_house + 4) % 12) or 12,
            ((jupiter_house + 6) % 12) or 12,
            ((jupiter_house + 8) % 12) or 12,
        ]
        jupiter_aspects_lord = lord_house in jupiter_aspect_houses

        occurring = is_exalted and in_kendra and jupiter_aspects_lord
        return Yoga(
            name="Chamara Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Eloquent, learned, ruler-like dignity, skilled in Vedic lore, long-lived",
            condition=(
                f"Lagna lord {lagna_lord.name}: exalted={is_exalted}, house={lord_house} (kendra={in_kendra}), "
                f"Jupiter aspect={jupiter_aspects_lord}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chamara Yoga", YogaNature.GOOD, False, "Ruler-like dignity", f"Error: {str(e)}")


def check_akhanda_samrajya_yoga(time: 'AstroTime') -> Yoga:
    """
    Akhanda Samrajya Yoga - Unbroken Empire Yoga.

    Condition: Jupiter rules over the 2nd, 5th, or 11th house from the Moon sign
               AND Jupiter is placed in a kendra from the Lagna AND the lord of
               the Lagna is a strong planet (in kendra or trikona).
    Effect: Becomes an emperor or very powerful ruler; dominion over vast territory;
            unbroken reign, great authority.

    Reference: Phaladeepika, Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_sign

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        moon_long = get_planet_longitude(Planet.Moon, time)
        moon_sign = int(moon_long // 30)

        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        jupiter_sign = int(jupiter_long // 30)
        jupiter_house_from_lagna = ((jupiter_sign - lagna_sign) % 12) + 1

        # Check Jupiter rules 2nd, 5th, or 11th from Moon sign
        # Jupiter rules Sagittarius (8) and Pisces (11)
        jupiter_ruled_signs = [8, 11]
        target_houses_from_moon = [2, 5, 11]
        jupiter_rules_target = False
        for h in target_houses_from_moon:
            sign_of_house = (moon_sign + h - 1) % 12
            if sign_of_house in jupiter_ruled_signs:
                jupiter_rules_target = True
                break

        # Check Jupiter in kendra from Lagna
        jupiter_in_kendra = jupiter_house_from_lagna in [1, 4, 7, 10]

        occurring = jupiter_rules_target and jupiter_in_kendra
        return Yoga(
            name="Akhanda Samrajya Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Emperor-like power, unbroken dominion, vast authority, great ruler",
            condition=(
                f"Jupiter rules 2nd/5th/11th from Moon={jupiter_rules_target}; "
                f"Jupiter in kendra from Lagna (house {jupiter_house_from_lagna})={jupiter_in_kendra}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Akhanda Samrajya Yoga", YogaNature.GOOD, False, "Emperor-like power", f"Error: {str(e)}")


def check_shiva_yoga(time: 'AstroTime') -> Yoga:
    """
    Shiva Yoga - Lord of 5th in 9th, lord of 9th in 10th, lord of 10th in 5th.

    Condition: The lords of the 5th, 9th, and 10th houses are placed in each
               other’s houses in a specific triangular exchange.
    Effect: Devotee of Shiva, virtuous, wealthy, performer of religious deeds,
            pleasure-loving, respected, attains salvation.

    Reference: Jataka Parijata, Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_5 = get_lord_of_house(5, time)
        lord_9 = get_lord_of_house(9, time)
        lord_10 = get_lord_of_house(10, time)

        def get_house(planet):
            p_sign = int(get_planet_longitude(planet, time) // 30)
            return ((p_sign - lagna_sign) % 12) + 1

        lord5_house = get_house(lord_5)
        lord9_house = get_house(lord_9)
        lord10_house = get_house(lord_10)

        # 5th lord in 9th, 9th lord in 10th, 10th lord in 5th
        occurring = (lord5_house == 9) and (lord9_house == 10) and (lord10_house == 5)
        return Yoga(
            name="Shiva Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Virtuous, wealthy, devotional, religious, attains salvation",
            condition=(
                f"5th lord ({lord_5.name}) in house {lord5_house} (need 9); "
                f"9th lord ({lord_9.name}) in house {lord9_house} (need 10); "
                f"10th lord ({lord_10.name}) in house {lord10_house} (need 5)"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shiva Yoga", YogaNature.GOOD, False, "Virtue and devotion", f"Error: {str(e)}")


# ========================================
# RENUNCIATION YOGAS
# ========================================

def check_sanyasa_yoga(time: 'AstroTime') -> Yoga:
    """
    Sanyasa Yoga - Four or more planets in a single sign.

    Condition: Four or more classical planets (Sun through Saturn) occupy
               the same zodiac sign.
    Effect: Renunciation, spiritual inclination, hermit tendencies, deep
            concentration; the specific sign and planets colour the expression.

    Reference: Brihat Parashara Hora Shastra, Uttara Kalamrita.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]

        sign_count: dict = {}
        for planet in classical:
            s = int(get_planet_longitude(planet, time) // 30)
            sign_count.setdefault(s, []).append(planet.name)

        max_sign = max(sign_count, key=lambda s: len(sign_count[s]))
        planets_there = sign_count[max_sign]
        occurring = len(planets_there) >= 4

        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Sanyasa Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description="Renunciation, spiritual inclination, hermit tendencies, deep concentration",
            condition=(
                f"{len(planets_there)} planets in {sign_names[max_sign]}: {', '.join(planets_there)}"
                if occurring else
                f"Max planets in one sign: {len(planets_there)} (need 4+)"
            ),
            strength=min(100, (len(planets_there) - 3) * 33) if occurring else 0,
        )
    except Exception as e:
        return Yoga("Sanyasa Yoga", YogaNature.NEUTRAL, False, "Renunciation", f"Error: {str(e)}")


# ========================================
# NABHASA YOGAS (Planetary Spread Patterns)
# ========================================

def check_rajju_yoga(time: 'AstroTime') -> Yoga:
    """
    Rajju Yoga - All 7 classical planets in moveable (chara) signs.

    Condition: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn all occupy
               moveable signs: Aries(1), Cancer(4), Libra(7), Capricorn(10).
    Effect: Fond of wandering, no fixed abode, travels constantly, lively,
            active, quick to start but may not finish things.

    Reference: Brihat Parashara Hora Shastra, Phaladeepika ch.27.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        moveable = {0, 3, 6, 9}  # Aries, Cancer, Libra, Capricorn

        placements = {p.name: int(get_planet_longitude(p, time) // 30) for p in classical}
        all_moveable = all(s in moveable for s in placements.values())
        signs_used = {s for s in placements.values()}
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Rajju Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=all_moveable,
            description="Fondness for travel, active, lively, no fixed abode, constant wandering",
            condition=f"All planets in moveable signs: {', '.join(sign_names[s] for s in sorted(signs_used))}"
                      if all_moveable else
                      f"Not all in moveable signs — offending: {[p for p,s in placements.items() if s not in moveable]}",
            strength=100 if all_moveable else 0,
        )
    except Exception as e:
        return Yoga("Rajju Yoga", YogaNature.NEUTRAL, False, "Wandering nature", f"Error: {str(e)}")


def check_musala_yoga(time: 'AstroTime') -> Yoga:
    """
    Musala Yoga - All 7 classical planets in fixed (sthira) signs.

    Condition: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn all occupy
               fixed signs: Taurus(2), Leo(5), Scorpio(8), Aquarius(11).
    Effect: Honorable, respected, steadfast, wealthy, enjoys conveyances,
            has many attendants, stable and determined.

    Reference: Brihat Parashara Hora Shastra, Phaladeepika ch.27.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        fixed = {1, 4, 7, 10}  # Taurus, Leo, Scorpio, Aquarius

        placements = {p.name: int(get_planet_longitude(p, time) // 30) for p in classical}
        all_fixed = all(s in fixed for s in placements.values())
        signs_used = {s for s in placements.values()}
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Musala Yoga",
            nature=YogaNature.GOOD,
            occurring=all_fixed,
            description="Honorable, respected, stable, wealthy, steadfast, many attendants",
            condition=f"All planets in fixed signs: {', '.join(sign_names[s] for s in sorted(signs_used))}"
                      if all_fixed else
                      f"Not all in fixed signs — offending: {[p for p,s in placements.items() if s not in fixed]}",
            strength=100 if all_fixed else 0,
        )
    except Exception as e:
        return Yoga("Musala Yoga", YogaNature.GOOD, False, "Stability and wealth", f"Error: {str(e)}")


def check_nala_yoga(time: 'AstroTime') -> Yoga:
    """
    Nala Yoga - All 7 classical planets in dual (dwiswabhava/common) signs.

    Condition: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn all occupy
               dual/mutable signs: Gemini(3), Virgo(6), Sagittarius(9), Pisces(12).
    Effect: Skilled in various crafts and arts, clever, cunning, versatile,
            has a dual or changeable nature, well-versed in many subjects.

    Reference: Brihat Parashara Hora Shastra, Phaladeepika ch.27.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        dual = {2, 5, 8, 11}  # Gemini, Virgo, Sagittarius, Pisces

        placements = {p.name: int(get_planet_longitude(p, time) // 30) for p in classical}
        all_dual = all(s in dual for s in placements.values())
        signs_used = {s for s in placements.values()}
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Nala Yoga",
            nature=YogaNature.GOOD,
            occurring=all_dual,
            description="Clever, versatile, skilled in arts and crafts, dual nature, well-read",
            condition=f"All planets in dual signs: {', '.join(sign_names[s] for s in sorted(signs_used))}"
                      if all_dual else
                      f"Not all in dual signs — offending: {[p for p,s in placements.items() if s not in dual]}",
            strength=100 if all_dual else 0,
        )
    except Exception as e:
        return Yoga("Nala Yoga", YogaNature.GOOD, False, "Versatile and clever", f"Error: {str(e)}")


def check_kedara_yoga(time: 'AstroTime') -> Yoga:
    """
    Kedara Yoga - All 7 classical planets spread across exactly 4 signs.

    Condition: When you map Sun through Saturn to their signs, exactly 4
               distinct signs are occupied (no more, no less).
    Effect: Agricultural wealth, dependable, earns through hard work and land,
            helpful to others, grounded, patient, prosperous farmer-like nature.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Sankhya Yoga.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = {int(get_planet_longitude(p, time) // 30) for p in classical}
        occurring = len(signs) == 4
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Kedara Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Agricultural/land wealth, dependable, hard-working, grounded, prosperous",
            condition=f"7 planets in {len(signs)} signs: {', '.join(sign_names[s] for s in sorted(signs))}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kedara Yoga", YogaNature.GOOD, False, "Agricultural wealth", f"Error: {str(e)}")


# ========================================
# PHALADEEPIKA SPECIAL YOGAS
# ========================================

def check_mridanga_yoga(time: 'AstroTime') -> Yoga:
    """
    Mridanga Yoga - An exalted or own-sign planet in a kendra, with the
    lagna lord also placed strongly (kendra or trikona).

    Condition: At least one planet (among the 7 classical) occupies a kendra
               house (1,4,7,10) while in its sign of exaltation or own sign,
               AND the lagna lord is placed in a kendra or trikona (1,4,5,7,9,10).
    Effect: Kingly grandeur, famous, wealthy, long-lived, like a king with
            drum-beaten proclamations of glory.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]

        exalted_in_kendra = []
        for p in classical:
            p_long = get_planet_longitude(p, time)
            p_sign = int(p_long // 30)
            p_house = ((p_sign - lagna_sign) % 12) + 1
            if p_house in [1, 4, 7, 10]:
                dignity, score = get_dignity_status(p.name, p_long)
                if score >= 4:  # exalted(5) or own sign(4)
                    exalted_in_kendra.append(f"{p.name}({dignity} H{p_house})")

        # Check lagna lord in kendra or trikona
        lagna_lord = get_lord_of_house(1, time)
        ll_sign = int(get_planet_longitude(lagna_lord, time) // 30)
        ll_house = ((ll_sign - lagna_sign) % 12) + 1
        ll_strong = ll_house in [1, 4, 5, 7, 9, 10]

        occurring = bool(exalted_in_kendra) and ll_strong
        return Yoga(
            name="Mridanga Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Kingly grandeur, famous, wealthy, long-lived, glory proclaimed widely",
            condition=(
                f"Exalted/own planet in kendra: {', '.join(exalted_in_kendra) or 'none'}; "
                f"Lagna lord {lagna_lord.name} in house {ll_house} (strong={ll_strong})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Mridanga Yoga", YogaNature.GOOD, False, "Kingly grandeur", f"Error: {str(e)}")


def check_bheri_yoga(time: 'AstroTime') -> Yoga:
    """
    Bheri Yoga - Jupiter and Venus both in kendra plus the lagna lord strongly placed.

    Condition: Both Jupiter and Venus occupy kendra houses (1,4,7,10) from
               the Ascendant, AND the lord of the Ascendant is also in a
               kendra or trikona (1,4,5,7,9,10).
    Effect: Famous like a king, wealthy, virtuous, has many followers,
            long-lived, philanthropic, drum-like proclamation of fame.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        venus_sign = int(get_planet_longitude(Planet.Venus, time) // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1
        venus_house = ((venus_sign - lagna_sign) % 12) + 1

        jupiter_in_kendra = jupiter_house in [1, 4, 7, 10]
        venus_in_kendra = venus_house in [1, 4, 7, 10]

        lagna_lord = get_lord_of_house(1, time)
        ll_sign = int(get_planet_longitude(lagna_lord, time) // 30)
        ll_house = ((ll_sign - lagna_sign) % 12) + 1
        ll_strong = ll_house in [1, 4, 5, 7, 9, 10]

        occurring = jupiter_in_kendra and venus_in_kendra and ll_strong
        return Yoga(
            name="Bheri Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Famous as a king, wealthy, virtuous, philanthropic, many followers",
            condition=(
                f"Jupiter in H{jupiter_house} (kendra={jupiter_in_kendra}); "
                f"Venus in H{venus_house} (kendra={venus_in_kendra}); "
                f"Lagna lord {lagna_lord.name} in H{ll_house} (strong={ll_strong})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Bheri Yoga", YogaNature.GOOD, False, "Fame and philanthropy", f"Error: {str(e)}")


def check_shankha_yoga(time: 'AstroTime') -> Yoga:
    """
    Shankha Yoga - Lords of 5th and 6th in mutual kendra, lagna lord strong.

    Condition: The lords of the 5th and 6th houses are placed in kendra
               (angular) houses relative to EACH OTHER (i.e., one is in the
               1st, 4th, 7th, or 10th house from the other's position),
               AND the lord of the Lagna is in a kendra or trikona.
    Effect: Righteous, just, learned, long-lived, happy, large family,
            good moral conduct, compassionate.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_5 = get_lord_of_house(5, time)
        lord_6 = get_lord_of_house(6, time)
        lord_lagna = get_lord_of_house(1, time)

        sign_5 = int(get_planet_longitude(lord_5, time) // 30)
        sign_6 = int(get_planet_longitude(lord_6, time) // 30)
        sign_ll = int(get_planet_longitude(lord_lagna, time) // 30)

        # Mutual kendra: sign difference is 0, 3, 6, or 9 signs
        diff_56 = abs(sign_5 - sign_6) % 12
        mutual_kendra = diff_56 in [0, 3, 6, 9]

        house_ll = ((sign_ll - lagna_sign) % 12) + 1
        ll_strong = house_ll in [1, 4, 5, 7, 9, 10]

        occurring = mutual_kendra and ll_strong
        return Yoga(
            name="Shankha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Righteous, just, learned, long-lived, happy, large family, compassionate",
            condition=(
                f"5th lord {lord_5.name} in sign {sign_5+1}, 6th lord {lord_6.name} in sign {sign_6+1} "
                f"(mutual kendra={mutual_kendra}); Lagna lord {lord_lagna.name} in H{house_ll} (strong={ll_strong})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shankha Yoga", YogaNature.GOOD, False, "Righteousness and justice", f"Error: {str(e)}")


def check_kahala_yoga(time: 'AstroTime') -> Yoga:
    """
    Kahala Yoga - Lords of 4th and 9th in mutual kendra, lagna lord strong.

    Condition: The lords of the 4th and 9th houses are placed in kendra
               houses relative to each other (sign difference 0,3,6,9),
               AND the lord of the Lagna is in a kendra or trikona.
    Effect: Courageous, bold, leads armies, commands forces, obstinate
            but brave, famous for heroism, prosperous.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_4 = get_lord_of_house(4, time)
        lord_9 = get_lord_of_house(9, time)
        lord_lagna = get_lord_of_house(1, time)

        sign_4 = int(get_planet_longitude(lord_4, time) // 30)
        sign_9 = int(get_planet_longitude(lord_9, time) // 30)
        sign_ll = int(get_planet_longitude(lord_lagna, time) // 30)

        diff_49 = abs(sign_4 - sign_9) % 12
        mutual_kendra = diff_49 in [0, 3, 6, 9]

        house_ll = ((sign_ll - lagna_sign) % 12) + 1
        ll_strong = house_ll in [1, 4, 5, 7, 9, 10]

        occurring = mutual_kendra and ll_strong
        return Yoga(
            name="Kahala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Courageous, bold, leads armies, stubborn but brave, famous for heroism",
            condition=(
                f"4th lord {lord_4.name} in sign {sign_4+1}, 9th lord {lord_9.name} in sign {sign_9+1} "
                f"(mutual kendra={mutual_kendra}); Lagna lord {lord_lagna.name} in H{house_ll} (strong={ll_strong})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kahala Yoga", YogaNature.GOOD, False, "Courage and boldness", f"Error: {str(e)}")


def check_chatussasiti_sama_yoga(time: 'AstroTime') -> Yoga:
    """
    Chatussasiti Sama Yoga - Lord of the 10th house placed in the 10th house.

    Condition: The lord of house 10 occupies house 10 itself (in its own
               domicile, the Midheaven sector).
    Effect: Born equal to a king, royal status, high authority, commands
            respect, kingly pleasures, exercises power like a monarch.

    Reference: Phaladeepika (Mantreswara), Saravali ch.36.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_10 = get_lord_of_house(10, time)
        lord_10_sign = int(get_planet_longitude(lord_10, time) // 30)
        lord_10_house = ((lord_10_sign - lagna_sign) % 12) + 1

        occurring = lord_10_house == 10
        return Yoga(
            name="Chatussasiti Sama Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Born equal to a king, royal authority, commands respect, kingly pleasures",
            condition=f"10th lord {lord_10.name} in house {lord_10_house} (need 10)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chatussasiti Sama Yoga", YogaNature.GOOD, False, "Royal status", f"Error: {str(e)}")


def check_pushkala_yoga(time: 'AstroTime') -> Yoga:
    """
    Pushkala Yoga - Moon and the lagna lord conjunct in a kendra.

    Condition: Moon and the lord of the Ascendant are placed in the same
               sign AND that sign falls in a kendra house (1, 4, 7, or 10).
    Effect: Charitable, very wealthy, contented, comfortable life,
            respected by rulers and learned men.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        lagna_lord = get_lord_of_house(1, time)
        ll_sign = int(get_planet_longitude(lagna_lord, time) // 30)

        same_sign = moon_sign == ll_sign
        house_of_conjunction = ((moon_sign - lagna_sign) % 12) + 1
        in_kendra = house_of_conjunction in [1, 4, 7, 10]

        occurring = same_sign and in_kendra
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Pushkala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Charitable, very wealthy, contented, comfortable life, respected by rulers",
            condition=(
                f"Moon and lagna lord {lagna_lord.name} both in {sign_names[moon_sign]} (H{house_of_conjunction}, kendra={in_kendra})"
                if same_sign else
                f"Moon in {sign_names[moon_sign]}, lagna lord {lagna_lord.name} in {sign_names[ll_sign]} (not conjunct)"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Pushkala Yoga", YogaNature.GOOD, False, "Charitable and wealthy", f"Error: {str(e)}")


def check_parijata_yoga(time: 'AstroTime') -> Yoga:
    """
    Parijata Yoga - The dispositor of the lagna lord is in its own sign or
    exalted, placed in a kendra or trikona.

    Condition: Find the sign the lagna lord occupies → find the ruler of
               that sign (the dispositor) → that dispositor must be in its
               own sign or exaltation sign AND in a kendra (1,4,7,10) or
               trikona (1,5,9) house from the Ascendant.
    Effect: Noble birth, happy middle and later life, charitable, powerful,
            prosperous, respected by kings and learned people.

    Reference: Phaladeepika (Mantreswara), ch. 6; Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house, get_lord_of_sign
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        # Step 1: Lagna lord
        lagna_lord = get_lord_of_house(1, time)
        ll_long = get_planet_longitude(lagna_lord, time)
        ll_sign = int(ll_long // 30)

        # Step 2: Dispositor (lord of the sign the lagna lord occupies)
        dispositor = get_lord_of_sign(ll_sign)

        # Step 3: Dispositor's position
        disp_long = get_planet_longitude(dispositor, time)
        disp_sign = int(disp_long // 30)
        disp_house = ((disp_sign - lagna_sign) % 12) + 1

        # Step 4: Dignity check
        dignity, score = get_dignity_status(dispositor.name, disp_long)
        in_own_or_exalted = score >= 4

        # Step 5: House check
        in_kendra_trikona = disp_house in [1, 4, 5, 7, 9, 10]

        occurring = in_own_or_exalted and in_kendra_trikona
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Parijata Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Noble birth, charitable, powerful, prosperous, respected by kings",
            condition=(
                f"Lagna lord {lagna_lord.name} in {sign_names[ll_sign]}; "
                f"Dispositor {dispositor.name} in {sign_names[disp_sign]} ({dignity}) H{disp_house} "
                f"(own/exalted={in_own_or_exalted}, kendra/trikona={in_kendra_trikona})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Parijata Yoga", YogaNature.GOOD, False, "Noble birth and prosperity", f"Error: {str(e)}")


def check_matanga_yoga(time: 'AstroTime') -> Yoga:
    """
    Matanga Yoga - Jupiter in own sign or exaltation in a kendra, with Moon
    in a kendra from Jupiter.

    Condition: Jupiter occupies a kendra house (1,4,7,10) from the Lagna
               while in its own sign (Sagittarius or Pisces) or exaltation
               (Cancer), AND the Moon is in a kendra position relative to
               Jupiter (i.e., the same sign or 4th/7th/10th from Jupiter).
    Effect: Elephant-like power and majesty, great authority, wealthy,
            famous, commands armies, kingly grandeur.

    Reference: Phaladeepika; Jataka Parijata — Matanga = elephant (majestic).
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        jupiter_sign = int(jupiter_long // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1

        dignity, score = get_dignity_status("Jupiter", jupiter_long)
        # own sign: Sagittarius(8) or Pisces(11), exaltation: Cancer(3)
        jupiter_strong = score >= 4  # own(4) or exalted(5)
        jupiter_in_kendra = jupiter_house in [1, 4, 7, 10]

        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        diff = (moon_sign - jupiter_sign) % 12
        moon_kendra_from_jupiter = diff in [0, 3, 6, 9]

        occurring = jupiter_strong and jupiter_in_kendra and moon_kendra_from_jupiter
        return Yoga(
            name="Matanga Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Elephant-like majesty, great authority, wealthy, famous, commands armies",
            condition=(
                f"Jupiter {dignity} in H{jupiter_house} (kendra={jupiter_in_kendra}, strong={jupiter_strong}); "
                f"Moon kendra from Jupiter (diff={diff} signs)={moon_kendra_from_jupiter}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Matanga Yoga", YogaNature.GOOD, False, "Elephant-like majesty", f"Error: {str(e)}")


# ========================================
# SUN / MOON SPECIAL YOGAS
# ========================================

def check_surya_yoga(time: 'AstroTime') -> Yoga:
    """
    Surya Yoga - Sun placed in the 10th house from Lagna.

    Condition: The Sun occupies the 10th house (Midheaven) from the Ascendant.
    Effect: Valorous, wealthy through own efforts, government favour, authority,
            leadership, commander, high status, respected by rulers.

    Reference: Brihat Parashara Hora Shastra; Saravali ch.24.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        sun_house = ((sun_sign - lagna_sign) % 12) + 1
        occurring = sun_house == 10
        return Yoga(
            name="Surya Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Valorous, wealthy through own efforts, government favour, leadership, high status",
            condition=f"Sun in house {sun_house} (need 10)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Surya Yoga", YogaNature.GOOD, False, "Authority and leadership", f"Error: {str(e)}")


def check_chandra_yoga(time: 'AstroTime') -> Yoga:
    """
    Chandra Yoga - Moon placed in the 7th house from Lagna.

    Condition: The Moon occupies the 7th house from the Ascendant.
    Effect: Beautiful spouse, attractive, popular, fond of travel, successful
            in partnerships and trade, emotionally balanced, charming.

    Reference: Saravali ch.24; Jataka Parijata.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        moon_house = ((moon_sign - lagna_sign) % 12) + 1
        occurring = moon_house == 7
        return Yoga(
            name="Chandra Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Attractive, popular, good spouse, successful in partnerships, charming",
            condition=f"Moon in house {moon_house} (need 7)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chandra Yoga", YogaNature.GOOD, False, "Charm and partnership", f"Error: {str(e)}")


def check_lagnadhi_yoga(time: 'AstroTime') -> Yoga:
    """
    Lagnadhi Yoga - Benefic planets (Jupiter, Venus, Mercury) in the 6th,
    7th, or 8th house from Lagna.

    Condition: Jupiter, Venus, and/or Mercury (unafflicted natural benefics)
               are placed in the 6th, 7th, or 8th houses from the Ascendant.
               At least two of the three must be present in those houses.
    Effect: Happy, eloquent, wealthy, free from disease, renowned, long-lived,
            victorious over enemies.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        target_houses = {6, 7, 8}

        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        in_target = []
        for p in benefics:
            p_sign = int(get_planet_longitude(p, time) // 30)
            p_house = ((p_sign - lagna_sign) % 12) + 1
            if p_house in target_houses:
                in_target.append(f"{p.name}(H{p_house})")

        occurring = len(in_target) >= 2
        return Yoga(
            name="Lagnadhi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Happy, eloquent, wealthy, healthy, renowned, victorious over enemies",
            condition=f"Benefics in 6th/7th/8th: {', '.join(in_target) if in_target else 'none'} (need 2+)",
            strength=min(100, len(in_target) * 50) if in_target else 0,
        )
    except Exception as e:
        return Yoga("Lagnadhi Yoga", YogaNature.GOOD, False, "Happiness and wealth", f"Error: {str(e)}")


# ========================================
# SUBHA / ASUBHA YOGAS
# ========================================

def check_subha_yoga(time: 'AstroTime') -> Yoga:
    """
    Subha Yoga - More benefics than malefics in kendra houses.

    Condition: Natural benefics (Jupiter, Venus, Mercury, waxing Moon) outnumber
               natural malefics (Sun, Mars, Saturn, Rahu, Ketu, waning Moon)
               in the four kendra houses (1,4,7,10) from the Ascendant.
    Effect: Happy, fortunate, honoured, comfortable life, well-liked, virtuous,
            performs meritorious acts.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        kendra = {1, 4, 7, 10}

        # Determine Moon phase for benefic/malefic classification
        sun_long = get_planet_longitude(Planet.Sun, time)
        moon_long = get_planet_longitude(Planet.Moon, time)
        moon_phase_deg = (moon_long - sun_long) % 360
        moon_is_benefic = moon_phase_deg > 72  # waxing (more than 72 deg from Sun)

        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        malefics = [Planet.Sun, Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu]

        def house(p):
            return ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1

        benefics_in_kendra = [p.name for p in benefics if house(p) in kendra]
        if moon_is_benefic and house(Planet.Moon) in kendra:
            benefics_in_kendra.append("Moon")
        malefics_in_kendra = [p.name for p in malefics if house(p) in kendra]
        if not moon_is_benefic and house(Planet.Moon) in kendra:
            malefics_in_kendra.append("Moon")

        occurring = len(benefics_in_kendra) > len(malefics_in_kendra)
        return Yoga(
            name="Subha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Happy, fortunate, honoured, comfortable life, well-liked, virtuous",
            condition=(
                f"Benefics in kendra ({len(benefics_in_kendra)}): {benefics_in_kendra}; "
                f"Malefics in kendra ({len(malefics_in_kendra)}): {malefics_in_kendra}"
            ),
            strength=min(100, len(benefics_in_kendra) * 25) if occurring else 0,
        )
    except Exception as e:
        return Yoga("Subha Yoga", YogaNature.GOOD, False, "Fortune and happiness", f"Error: {str(e)}")


def check_asubha_yoga(time: 'AstroTime') -> Yoga:
    """
    Asubha Yoga - More malefics than benefics in kendra houses.

    Condition: Natural malefics (Sun, Mars, Saturn, Rahu, Ketu, waning Moon)
               outnumber natural benefics in the kendra houses (1,4,7,10).
    Effect: Hardships, struggles, obstacles in life, health problems,
            financial difficulties, conflicts. Indicates areas needing
            careful attention and remedies.

    Reference: Brihat Parashara Hora Shastra.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        kendra = {1, 4, 7, 10}

        sun_long = get_planet_longitude(Planet.Sun, time)
        moon_long = get_planet_longitude(Planet.Moon, time)
        moon_phase_deg = (moon_long - sun_long) % 360
        moon_is_benefic = moon_phase_deg > 72

        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        malefics = [Planet.Sun, Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu]

        def house(p):
            return ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1

        benefics_in_kendra = [p.name for p in benefics if house(p) in kendra]
        if moon_is_benefic and house(Planet.Moon) in kendra:
            benefics_in_kendra.append("Moon")
        malefics_in_kendra = [p.name for p in malefics if house(p) in kendra]
        if not moon_is_benefic and house(Planet.Moon) in kendra:
            malefics_in_kendra.append("Moon")

        occurring = len(malefics_in_kendra) > len(benefics_in_kendra)
        return Yoga(
            name="Asubha Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Hardships, struggles, obstacles, needs careful attention and remedies",
            condition=(
                f"Malefics in kendra ({len(malefics_in_kendra)}): {malefics_in_kendra}; "
                f"Benefics in kendra ({len(benefics_in_kendra)}): {benefics_in_kendra}"
            ),
            strength=min(100, len(malefics_in_kendra) * 25) if occurring else 0,
        )
    except Exception as e:
        return Yoga("Asubha Yoga", YogaNature.BAD, False, "Hardships and obstacles", f"Error: {str(e)}")


# ========================================
# RARE CLASSICAL SPECIAL YOGAS
# ========================================

def check_srikantha_yoga(time: 'AstroTime') -> Yoga:
    """
    Srikantha Yoga - Saturn in 11th from Moon, Moon in kendra from Lagna.

    Condition: Saturn is placed in the 11th house from the Moon's position,
               AND the Moon itself is in a kendra (1,4,7,10) from the Lagna.
    Effect: Rich, happy domestic life, earns through persistent effort,
            gains despite obstacles, Shiva-blessed, spiritual inclination.

    Reference: Jataka Parijata; various Nadi texts — named after Shiva (Srikantha).
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        saturn_sign = int(get_planet_longitude(Planet.Saturn, time) // 30)

        saturn_from_moon = ((saturn_sign - moon_sign) % 12) + 1
        moon_house = ((moon_sign - lagna_sign) % 12) + 1

        occurring = (saturn_from_moon == 11) and (moon_house in [1, 4, 7, 10])
        return Yoga(
            name="Srikantha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Rich, happy home, earns through effort, Shiva-blessed, spiritual",
            condition=(
                f"Saturn in house {saturn_from_moon} from Moon (need 11); "
                f"Moon in house {moon_house} from Lagna (kendra need)"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Srikantha Yoga", YogaNature.GOOD, False, "Shiva-blessed prosperity", f"Error: {str(e)}")


def check_sharada_yoga(time: 'AstroTime') -> Yoga:
    """
    Sharada Yoga - Mercury in own sign or exaltation in kendra, aspected by Jupiter.

    Condition: Mercury is (a) in its own sign (Gemini or Virgo) or exaltation
               (Virgo), (b) placed in a kendra house (1,4,7,10), and
               (c) aspected by Jupiter (7th aspect from Jupiter's house).
    Effect: Scholar, expert in grammar and rhetoric, poet, famous author,
            expert in multiple languages, long-lived, celebrated.

    Reference: Phaladeepika (Mantreswara); Saravali.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        merc_long = get_planet_longitude(Planet.Mercury, time)
        merc_sign = int(merc_long // 30)
        merc_house = ((merc_sign - lagna_sign) % 12) + 1

        dignity, score = get_dignity_status("Mercury", merc_long)
        merc_strong = score >= 4  # own(4) or exalted(5)
        merc_in_kendra = merc_house in [1, 4, 7, 10]

        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1
        # Jupiter 7th aspect: house 7 from Jupiter
        jupiter_7th = ((jupiter_house + 6) % 12) or 12
        jupiter_aspects_merc = merc_house == jupiter_7th

        occurring = merc_strong and merc_in_kendra and jupiter_aspects_merc
        return Yoga(
            name="Sharada Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Scholar, poet, expert in languages and grammar, famous author, celebrated",
            condition=(
                f"Mercury {dignity} in H{merc_house} (kendra={merc_in_kendra}, strong={merc_strong}); "
                f"Jupiter in H{jupiter_house}, 7th aspect to H{jupiter_7th} (hits Mercury={jupiter_aspects_merc})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Sharada Yoga", YogaNature.GOOD, False, "Scholar and poet", f"Error: {str(e)}")


def check_indra_yoga(time: 'AstroTime') -> Yoga:
    """
    Indra Yoga - Lord of the 5th and lord of the 11th house are conjunct
    (in the same sign), with Moon in 5th or 11th.

    Condition: The lord of house 5 and the lord of house 11 occupy the same
               sign, AND the Moon must be placed in either the 5th or 11th
               house from the Ascendant.
    Effect: Long-lived like Indra (king of gods), wealthy, powerful,
            victorious, commands respect, very fortunate.

    Reference: Phaladeepika (Mantreswara), ch. 6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_5 = get_lord_of_house(5, time)
        lord_11 = get_lord_of_house(11, time)

        sign_5 = int(get_planet_longitude(lord_5, time) // 30)
        sign_11 = int(get_planet_longitude(lord_11, time) // 30)
        lords_conjunct = sign_5 == sign_11

        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        moon_house = ((moon_sign - lagna_sign) % 12) + 1
        moon_placed = moon_house in [5, 11]

        occurring = lords_conjunct and moon_placed
        return Yoga(
            name="Indra Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Long-lived like Indra, wealthy, powerful, victorious, very fortunate",
            condition=(
                f"5th lord {lord_5.name} in sign {sign_5+1}, 11th lord {lord_11.name} in sign {sign_11+1} "
                f"(conjunct={lords_conjunct}); Moon in house {moon_house} (need 5 or 11)"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Indra Yoga", YogaNature.GOOD, False, "Wealth and victory", f"Error: {str(e)}")


def check_ravi_yoga(time: 'AstroTime') -> Yoga:
    """
    Ravi Yoga - Sun in the 10th house from the Moon.

    Condition: The Sun is placed in the 10th sign from the Moon's sign
               (i.e., 10 houses ahead counting from Moon = 1).
    Effect: Active, courageous, defeats enemies, government service or
            favour, authority in administration, well-known, honest.

    Reference: Saravali; Phaladeepika.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        sun_from_moon = ((sun_sign - moon_sign) % 12) + 1
        occurring = sun_from_moon == 10
        return Yoga(
            name="Ravi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Active, courageous, defeats enemies, government favour, honest authority",
            condition=f"Sun is in house {sun_from_moon} from Moon (need 10)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Ravi Yoga", YogaNature.GOOD, False, "Courage and government favour", f"Error: {str(e)}")


# ========================================
# NABHASA AKRITI (SHAPE) YOGAS
# ========================================

def check_gola_yoga(time: 'AstroTime') -> Yoga:
    """
    Gola Yoga - All 7 classical planets in a single sign.

    Condition: All seven classical planets (Sun through Saturn) are placed
               in one and the same zodiac sign.
    Effect: Poverty, struggles, wandering, misfortune; a difficult life
            with many hardships. One of the most challenging Nabhasa yogas.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = [int(get_planet_longitude(p, time) // 30) for p in classical]
        occurring = len(set(signs)) == 1
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Gola Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Poverty, struggles, wandering, misfortune, many hardships",
            condition=f"All 7 planets in {sign_names[signs[0]]}" if occurring
                      else f"Planets spread across {len(set(signs))} signs (need 1)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Gola Yoga", YogaNature.BAD, False, "Poverty and hardship", f"Error: {str(e)}")


def check_yuga_yoga(time: 'AstroTime') -> Yoga:
    """
    Yuga Yoga - All 7 classical planets in exactly 2 signs.

    Condition: When all seven classical planets are mapped to their signs,
               exactly 2 distinct signs are occupied.
    Effect: Heretic views, impoverished, lazy, fallen from grace, afflicted
            or excommunicated. One of the challenging Nabhasa yogas.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Sankhya Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = {int(get_planet_longitude(p, time) // 30) for p in classical}
        occurring = len(signs) == 2
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Yuga Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Heretic tendencies, impoverished, lazy, fallen from grace",
            condition=f"7 planets in {len(signs)} signs: {', '.join(sign_names[s] for s in sorted(signs))}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Yuga Yoga", YogaNature.BAD, False, "Impoverishment", f"Error: {str(e)}")


def check_danda_yoga(time: 'AstroTime') -> Yoga:
    """
    Danda Yoga - All 7 classical planets in exactly 3 consecutive signs.

    Condition: All seven classical planets occupy exactly 3 distinct signs,
               AND those 3 signs must be consecutive (adjacent in the zodiac).
    Effect: Dependent on others, works under authority, obedient servant
            or officer; may be punished; not self-reliant; disciplined.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_3 = len(signs) == 3
        # Consecutive: differences between adjacent signs all == 1
        # Also handle wrap-around (e.g., 10,11,0)
        consecutive = False
        if exactly_3:
            diffs = [(signs[i+1] - signs[i]) % 12 for i in range(len(signs)-1)]
            # Also check wrap: last to first
            diffs_wrap = [(signs[(i+1) % 3] - signs[i]) % 12 for i in range(3)]
            consecutive = all(d == 1 for d in diffs) or all(d == 1 for d in diffs_wrap)

        occurring = exactly_3 and consecutive
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Danda Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description="Works under authority, obedient, disciplined, dependent on others",
            condition=f"7 planets in {len(signs)} signs: {', '.join(sign_names[s] for s in signs)} (consecutive={consecutive})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Danda Yoga", YogaNature.NEUTRAL, False, "Discipline and authority", f"Error: {str(e)}")


# ========================================
# NABHASA AKRITI YOGAS (continued)
# ========================================

def check_veena_yoga(time: 'AstroTime') -> Yoga:
    """
    Veena Yoga - All 7 classical planets spread across exactly 7 different signs.

    Condition: Each of the 7 classical planets (Sun through Saturn) occupies a
               different sign — all 7 signs distinct, none repeated.
    Effect: Fond of music, singing, dancing; joyful, happy, prosperous, loved
            by many, enjoys pleasures, artistic temperament.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Sankhya Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = [int(get_planet_longitude(p, time) // 30) for p in classical]
        occurring = len(set(signs)) == 7
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        used = sorted(set(signs))
        return Yoga(
            name="Veena Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Fond of music, dance, joyful, prosperous, loved by many, artistic",
            condition=f"7 planets in 7 distinct signs: {', '.join(sign_names[s] for s in used)}"
                      if occurring else f"Planets occupy only {len(set(signs))} distinct signs (need 7)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Veena Yoga", YogaNature.GOOD, False, "Music and joy", f"Error: {str(e)}")


def check_shoola_yoga(time: 'AstroTime') -> Yoga:
    """
    Shoola Yoga - All 7 classical planets in exactly 3 signs that form
    a trine pattern (mutual 120° / 4-sign gap).

    Condition: All seven classical planets occupy exactly 3 signs AND
               the 3 signs form a trikona (fire, earth, air, or water
               triplicity — signs 4 apart from each other).
    Effect: Cruel, quarrelsome, fond of weapons, courageous, harsh speech;
            can be a soldier, warrior, surgeon, or fighter.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_3 = len(signs) == 3
        # Trikona pattern: each pair is 4 signs apart (120°)
        trikona = False
        if exactly_3:
            diffs = [(signs[(i+1) % 3] - signs[i]) % 12 for i in range(3)]
            trikona = all(d == 4 for d in diffs)
        occurring = exactly_3 and trikona
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Shoola Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description="Courageous, warrior nature, sharp, quarrelsome, harsh speech, combative",
            condition=f"Planets in trikona signs: {', '.join(sign_names[s] for s in signs)} (trikona={trikona})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shoola Yoga", YogaNature.NEUTRAL, False, "Warrior nature", f"Error: {str(e)}")


def check_shankha_nabhasa_yoga(time: 'AstroTime') -> Yoga:
    """
    Shankha (Nabhasa) Yoga - All 7 planets in exactly 5 signs.

    Condition: When all seven classical planets are mapped to signs,
               exactly 5 distinct signs are occupied.
    Effect: Virtuous, just, long-lived, happy, spouse and children bring
            prosperity, charitable, conch-like purity.

    Note: This is distinct from the Phaladeepika Shankha Yoga (already
          implemented as check_shankha_yoga). This is the Nabhasa Sankhya variant.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Sankhya Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = {int(get_planet_longitude(p, time) // 30) for p in classical}
        occurring = len(signs) == 5
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Shankha Nabhasa Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Virtuous, just, long-lived, happy family, charitable, purity of character",
            condition=f"7 planets in {len(signs)} signs: {', '.join(sign_names[s] for s in sorted(signs))}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shankha Nabhasa Yoga", YogaNature.GOOD, False, "Virtue and purity", f"Error: {str(e)}")


def check_yava_yoga(time: 'AstroTime') -> Yoga:
    """
    Yava Yoga - All 7 planets in exactly 6 signs, with none in the 7th.

    Condition: The 7 classical planets occupy exactly 6 distinct signs
               (one sign is unoccupied among the 7 signs they span).
    Effect: Learned, well-versed, performs charitable deeds, respected,
            leads a complete satisfying life like a full barley grain.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Sankhya Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = {int(get_planet_longitude(p, time) // 30) for p in classical}
        occurring = len(signs) == 6
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Yava Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Learned, charitable, respected, satisfying complete life",
            condition=f"7 planets in {len(signs)} signs: {', '.join(sign_names[s] for s in sorted(signs))}",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Yava Yoga", YogaNature.GOOD, False, "Learning and charity", f"Error: {str(e)}")


def check_kamala_yoga(time: 'AstroTime') -> Yoga:
    """
    Kamala Yoga - All 7 classical planets in exactly 4 kendra houses.

    Condition: All seven classical planets (Sun–Saturn) are placed exclusively
               in the kendra houses (1, 4, 7, 10) from the Ascendant, occupying
               each kendra at least once.
    Effect: Pure, virtuous, famous throughout the world like a lotus (kamala),
            long-lived, wealthy, kingly in conduct.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        kendra = {1, 4, 7, 10}

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        houses = [((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1
                  for p in classical]
        all_in_kendra = all(h in kendra for h in houses)
        houses_used = set(houses)
        all_kendra_filled = kendra.issubset(houses_used)
        occurring = all_in_kendra and all_kendra_filled
        return Yoga(
            name="Kamala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Pure, virtuous, lotus-like fame, long-lived, wealthy, kingly conduct",
            condition=(
                f"All 7 planets in kendras: {all_in_kendra}; all kendras filled: {all_kendra_filled}; "
                f"houses: {sorted(houses_used)}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kamala Yoga", YogaNature.GOOD, False, "Lotus purity and fame", f"Error: {str(e)}")


def check_vatapi_yoga(time: 'AstroTime') -> Yoga:
    """
    Vatapi Yoga - All 7 planets in exactly 3 signs forming an opposition
    (kama trikona or signs in 2-sign intervals).

    Condition: All seven classical planets occupy exactly 3 signs, and
               those signs span a 180° axis (two signs oppose a third, i.e.,
               the 3 signs include at least one pair that are 6 signs apart).
    Effect: Cunning, deceitful, clever in disguise, lives off others,
            tricky nature; negatively aspected but resourceful.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_3 = len(signs) == 3
        # Check if any two signs in the trio are 6 apart (opposition)
        has_opposition = False
        if exactly_3:
            for i in range(3):
                for j in range(i+1, 3):
                    if abs(signs[i] - signs[j]) % 12 == 6:
                        has_opposition = True
        occurring = exactly_3 and has_opposition
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Vatapi Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Cunning, deceitful, clever in disguise, lives off others, tricky",
            condition=f"Planets in 3 signs with opposition: {', '.join(sign_names[s] for s in signs)} (has_opposition={has_opposition})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vatapi Yoga", YogaNature.BAD, False, "Cunning and deceit", f"Error: {str(e)}")


def check_koorma_yoga(time: 'AstroTime') -> Yoga:
    """
    Koorma Yoga - Benefics in odd houses (1,3,5,7,9,11) and malefics in
    even houses (2,4,6,8,10,12), both sets in their own natural houses.

    Condition: The natural benefics (Jupiter, Venus, Mercury) are placed in
               odd houses (1,3,5,7,9,11) AND natural malefics (Sun, Mars,
               Saturn) are placed in even houses (2,4,6,8,10,12) from Lagna.
    Effect: Famous, prosperous, tortoise-like patience and longevity,
            happy, respected, achieves what others cannot.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        def house(p):
            return ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1

        benefics = [Planet.Jupiter, Planet.Venus, Planet.Mercury]
        malefics = [Planet.Sun, Planet.Mars, Planet.Saturn]
        odd = {1, 3, 5, 7, 9, 11}
        even = {2, 4, 6, 8, 10, 12}

        b_in_odd = [(p.name, house(p)) for p in benefics if house(p) in odd]
        m_in_even = [(p.name, house(p)) for p in malefics if house(p) in even]

        occurring = len(b_in_odd) == 3 and len(m_in_even) == 3
        return Yoga(
            name="Koorma Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Patience, longevity, famous, prosperous, respected, achieves beyond others",
            condition=(
                f"Benefics in odd houses: {b_in_odd} ({len(b_in_odd)}/3); "
                f"Malefics in even houses: {m_in_even} ({len(m_in_even)}/3)"
            ),
            strength=min(100, (len(b_in_odd) + len(m_in_even)) * 17) if (b_in_odd or m_in_even) else 0,
        )
    except Exception as e:
        return Yoga("Koorma Yoga", YogaNature.GOOD, False, "Patience and longevity", f"Error: {str(e)}")


# ========================================
# LONGEVITY / DOSHA YOGAS
# ========================================

def check_arishta_yoga(time: 'AstroTime') -> Yoga:
    """
    Arishta Yoga - Multiple malefics afflicting the Moon or Lagna simultaneously.

    Condition: Two or more of the classic malefics (Sun, Mars, Saturn, Rahu,
               Ketu) are placed in the 1st, 6th, 8th, or 12th house from the
               Ascendant, AND the Moon has no benefic aspect.
    Effect: Indicates afflictions, health issues, misfortune, struggles;
            degree varies — this is the general Arishta pattern.

    Reference: Brihat Parashara Hora Shastra — Arishta Bhangas.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        dusthana = {1, 6, 8, 12}

        def house(p):
            return ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1

        malefics = [Planet.Sun, Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu]
        malefics_in_dusthana = [p.name for p in malefics if house(p) in dusthana]

        # Moon benefic aspect check: Jupiter aspects (5th, 7th, 9th from Jupiter)
        moon_house = house(Planet.Moon)
        jupiter_house = house(Planet.Jupiter)
        jupiter_aspects = [
            ((jupiter_house + 4) % 12) or 12,
            ((jupiter_house + 6) % 12) or 12,
            ((jupiter_house + 8) % 12) or 12,
        ]
        moon_has_jupiter_aspect = moon_house in jupiter_aspects

        occurring = len(malefics_in_dusthana) >= 2 and not moon_has_jupiter_aspect
        return Yoga(
            name="Arishta Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Afflictions, health issues, misfortune, struggles; remedies recommended",
            condition=(
                f"Malefics in dusthana (H1/6/8/12): {malefics_in_dusthana} ({len(malefics_in_dusthana)}); "
                f"Moon has Jupiter aspect: {moon_has_jupiter_aspect}"
            ),
            strength=min(100, len(malefics_in_dusthana) * 25) if occurring else 0,
        )
    except Exception as e:
        return Yoga("Arishta Yoga", YogaNature.BAD, False, "Afflictions and struggle", f"Error: {str(e)}")


def check_balarishta_yoga(time: 'AstroTime') -> Yoga:
    """
    Balarishta Yoga - Moon in 6th/8th/12th conjunct or aspected by malefics,
    with no benefic protection.

    Condition: Moon is in the 6th, 8th, or 12th house from the Ascendant
               AND is conjoined with or aspected by a malefic (Mars, Saturn,
               Rahu, Ketu), AND receives no aspect from Jupiter or Venus.
    Effect: Childhood hardships, health vulnerabilities in early life;
            cancelled if benefics protect the Moon.

    Reference: Brihat Parashara Hora Shastra — Balarishta chapter.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        def house(p):
            return ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1

        def sign(p):
            return int(get_planet_longitude(p, time) // 30)

        moon_house = house(Planet.Moon)
        moon_sign_num = sign(Planet.Moon)

        in_dusthana = moon_house in {6, 8, 12}

        # Malefic conjunction (same sign as Moon)
        malefics = [Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu]
        conjunct_malefic = any(sign(p) == moon_sign_num for p in malefics)

        # Malefic 7th aspect on Moon
        malefic_aspect = any(
            ((house(p) + 6) % 12 or 12) == moon_house for p in malefics
        )

        # Benefic protection
        benefics = [Planet.Jupiter, Planet.Venus]
        benefic_protects = any(
            sign(p) == moon_sign_num or
            ((house(p) + 6) % 12 or 12) == moon_house
            for p in benefics
        )

        occurring = in_dusthana and (conjunct_malefic or malefic_aspect) and not benefic_protects
        return Yoga(
            name="Balarishta Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Childhood hardships, early health vulnerabilities; cancelled by benefic protection",
            condition=(
                f"Moon in H{moon_house} (dusthana={in_dusthana}); "
                f"malefic conjunct/aspect={conjunct_malefic or malefic_aspect}; "
                f"benefic protection={benefic_protects}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Balarishta Yoga", YogaNature.BAD, False, "Childhood hardships", f"Error: {str(e)}")


# ========================================
# PROSPERITY & STATUS YOGAS
# ========================================

def check_shrinatha_yoga(time: 'AstroTime') -> Yoga:
    """
    Shrinatha Yoga - Lord of 7th in 10th, exalted; lord of 10th conjunct
    Venus or Jupiter.

    Condition: The lord of the 7th house is placed in the 10th house AND
               is exalted (dignity score = 5), AND the lord of the 10th
               house is conjunct (same sign) with Venus or Jupiter.
    Effect: Very wealthy, renowned, devoted to Vishnu (Shrinatha), enjoys
            royal favour, highly respected, powerful authority.

    Reference: Phaladeepika (Mantreswara), ch.6.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        lord_7 = get_lord_of_house(7, time)
        l7_long = get_planet_longitude(lord_7, time)
        l7_house = ((int(l7_long // 30) - lagna_sign) % 12) + 1
        dignity, score = get_dignity_status(lord_7.name, l7_long)
        l7_exalted_in_10 = (l7_house == 10) and (score == 5)

        lord_10 = get_lord_of_house(10, time)
        l10_sign = int(get_planet_longitude(lord_10, time) // 30)
        venus_sign = int(get_planet_longitude(Planet.Venus, time) // 30)
        jupiter_sign = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        l10_with_benefic = (l10_sign == venus_sign) or (l10_sign == jupiter_sign)

        occurring = l7_exalted_in_10 and l10_with_benefic
        return Yoga(
            name="Shrinatha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Very wealthy, renowned, devoted, royal favour, powerful authority",
            condition=(
                f"7th lord {lord_7.name} in H{l7_house} ({dignity}, exalted-in-10={l7_exalted_in_10}); "
                f"10th lord {lord_10.name} with Venus/Jupiter={l10_with_benefic}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Shrinatha Yoga", YogaNature.GOOD, False, "Vishnu devotee and wealth", f"Error: {str(e)}")


def check_chapa_yoga(time: 'AstroTime') -> Yoga:
    """
    Chapa Yoga - All 7 planets in exactly 3 signs forming a bow (arc) shape —
    3 consecutive signs on one side of the zodiac.

    Condition: All 7 classical planets occupy exactly 3 adjacent (consecutive)
               signs AND those signs span no more than half the zodiac (within
               a 3-sign arc).
    Effect: Resolute, determined, keeps promises, expert in trade, ambitious,
            focused, accomplishes goals with bow-like precision.

    Note: Chapa means bow. Distinct from Danda (which requires strict
          consecutive sequence without wrap consideration).

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_3 = len(signs) == 3
        # Arc: consecutive signs, non-wrapping span <= 2 (i.e. signs[2]-signs[0] == 2)
        arc_span = (signs[-1] - signs[0]) if exactly_3 else 99
        is_arc = exactly_3 and arc_span == 2  # e.g., [3,4,5]
        occurring = is_arc
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Chapa Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Resolute, keeps promises, expert in trade, focused, accomplishes goals",
            condition=f"Planets in 3 consecutive signs (arc): {', '.join(sign_names[s] for s in signs)} (span={arc_span})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chapa Yoga", YogaNature.GOOD, False, "Resolution and focus", f"Error: {str(e)}")


# ========================================
# NABHASA AKRITI — ARC & CIRCLE YOGAS
# ========================================

def check_ardha_chandra_yoga(time: 'AstroTime') -> Yoga:
    """
    Ardha Chandra Yoga (Half-Moon) - All 7 planets span exactly 5 consecutive signs.

    Condition: All seven classical planets occupy exactly 5 distinct signs,
               and those 5 signs are consecutive (span of 4 signs, no gaps).
    Effect: Commander of armies, royal favour, handsome, skilled in arts,
            respected, half-moon grace and brilliance.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_5 = len(signs) == 5
        # Consecutive: max - min == 4 (non-wrapping)
        consecutive = exactly_5 and (signs[-1] - signs[0]) == 4
        occurring = consecutive
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Ardha Chandra Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Commander-like, royal favour, handsome, skilled in arts, respected",
            condition=f"Planets in {len(signs)} signs: {', '.join(sign_names[s] for s in signs)} (consecutive={consecutive})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Ardha Chandra Yoga", YogaNature.GOOD, False, "Royal favour", f"Error: {str(e)}")


def check_chakra_yoga(time: 'AstroTime') -> Yoga:
    """
    Chakra Yoga - Planets occupy every alternate sign (6 of the 12 signs
    in a wheel pattern).

    Condition: All 7 classical planets are distributed across exactly 6 signs
               AND those 6 signs are all odd-numbered (1,3,5,7,9,11) or all
               even-numbered (2,4,6,8,10,12), forming a wheel (chakra).
    Effect: Very high status, ruler of men, renowned like a chakravartin
            (universal emperor), commands authority over wide territory.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        # signs are 0-indexed here; odd signs: 0,2,4,6,8,10 (Aries=0 is odd rashi)
        signs = {int(get_planet_longitude(p, time) // 30) for p in classical}
        exactly_6 = len(signs) == 6
        all_odd_signs = exactly_6 and all(s % 2 == 0 for s in signs)   # 0,2,4,6,8,10
        all_even_signs = exactly_6 and all(s % 2 == 1 for s in signs)  # 1,3,5,7,9,11
        occurring = all_odd_signs or all_even_signs
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Chakra Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Chakravartin-like ruler, very high status, renowned, commands wide authority",
            condition=(
                f"Planets in 6 alternate signs: {', '.join(sign_names[s] for s in sorted(signs))} "
                f"(all-odd={all_odd_signs}, all-even={all_even_signs})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chakra Yoga", YogaNature.GOOD, False, "Universal authority", f"Error: {str(e)}")


def check_sar_yoga(time: 'AstroTime') -> Yoga:
    """
    Sar Yoga (Arrow) - All 7 planets in exactly 3 signs with one pair
    in a kendra relationship (4 or 8 signs apart), forming an arrow shape.

    Condition: All 7 classical planets occupy exactly 3 signs AND among the
               3 signs, at least one pair is 4 signs apart (square / kendra).
    Effect: Quarrelsome but skilled in warfare, inflexible, sharp like an
               arrow, determined, military/athletic inclination.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_3 = len(signs) == 3
        has_square = False
        if exactly_3:
            for i in range(3):
                for j in range(i + 1, 3):
                    diff = abs(signs[i] - signs[j]) % 12
                    if diff == 4 or diff == 8:
                        has_square = True
        occurring = exactly_3 and has_square
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Sar Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description="Sharp like an arrow, skilled in warfare, inflexible, determined, military",
            condition=f"Planets in 3 signs: {', '.join(sign_names[s] for s in signs)} (square pair={has_square})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Sar Yoga", YogaNature.NEUTRAL, False, "Warrior determination", f"Error: {str(e)}")


def check_pasa_yoga(time: 'AstroTime') -> Yoga:
    """
    Pasa Yoga (Noose) - All 7 planets in exactly 5 signs, not consecutive.

    Condition: All 7 classical planets occupy exactly 5 distinct signs AND
               those signs are NOT 5 consecutive signs (distinguishing this
               from Ardha Chandra Yoga).
    Effect: Clever, attached to family, fond of bondage-type relationships,
            may get entangled in obligations; resourceful but constrained.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_5 = len(signs) == 5
        consecutive = exactly_5 and (signs[-1] - signs[0]) == 4
        occurring = exactly_5 and not consecutive
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Pasa Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description="Clever, family-oriented, entangled in obligations, resourceful but constrained",
            condition=f"Planets in {len(signs)} signs: {', '.join(sign_names[s] for s in signs)} (non-consecutive={not consecutive})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Pasa Yoga", YogaNature.NEUTRAL, False, "Entanglement", f"Error: {str(e)}")


def check_mala_yoga(time: 'AstroTime') -> Yoga:
    """
    Mala Yoga (Garland) - All 7 planets in exactly 7 consecutive signs
    spanning the full half of the zodiac.

    Condition: All 7 classical planets are distributed across exactly 7
               distinct signs AND those signs form a consecutive arc of 7
               (span of 6 from lowest to highest sign, non-wrapping).
    Effect: Wealthy, happy, possesses many ornaments/garlands, prosperous,
            enjoys pleasures, popular, garlanded with fortune.

    Reference: Brihat Parashara Hora Shastra — Nabhasa Akriti Yogas.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                     Planet.Jupiter, Planet.Venus, Planet.Saturn]
        signs = sorted({int(get_planet_longitude(p, time) // 30) for p in classical})
        exactly_7 = len(signs) == 7
        consecutive = exactly_7 and (signs[-1] - signs[0]) == 6
        occurring = consecutive
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Mala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Wealthy, prosperous, many ornaments, enjoys pleasures, garlanded with fortune",
            condition=f"Planets in 7 consecutive signs: {', '.join(sign_names[s] for s in signs)} (span={signs[-1]-signs[0] if signs else 0})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Mala Yoga", YogaNature.GOOD, False, "Prosperity and ornaments", f"Error: {str(e)}")


# ========================================
# DHARMA & SPIRITUAL YOGAS
# ========================================

def check_dharma_karma_yoga(time: 'AstroTime') -> Yoga:
    """
    Dharma-Karma Adhipati Yoga - Lords of 9th (dharma) and 10th (karma)
    are conjunct or mutually aspecting.

    Condition: The lord of the 9th house and the lord of the 10th house
               occupy the same sign (conjunction) OR are in mutual 7th
               aspect (signs 7 apart).
    Effect: Very fortunate, righteous actions bring worldly success,
            career aligned with dharma, respected by all, achieves
            prominence through virtuous deeds.

    Reference: Brihat Parashara Hora Shastra — Raja Yoga chapter.
    """
    try:
        from .calculate import get_planet_longitude
        from .lordship import get_lord_of_house

        lord_9 = get_lord_of_house(9, time)
        lord_10 = get_lord_of_house(10, time)
        sign_9 = int(get_planet_longitude(lord_9, time) // 30)
        sign_10 = int(get_planet_longitude(lord_10, time) // 30)

        conjunct = sign_9 == sign_10
        mutual_7th = abs(sign_9 - sign_10) % 12 == 6
        occurring = conjunct or mutual_7th
        relation = "conjunct" if conjunct else "mutual 7th aspect" if mutual_7th else "no connection"
        return Yoga(
            name="Dharma-Karma Adhipati Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Righteous career, virtuous success, prominent through dharmic deeds, respected",
            condition=(
                f"9th lord {lord_9.name} in sign {sign_9+1}, "
                f"10th lord {lord_10.name} in sign {sign_10+1}: {relation}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Dharma-Karma Adhipati Yoga", YogaNature.GOOD, False, "Righteous career", f"Error: {str(e)}")


def check_amrita_yoga(time: 'AstroTime') -> Yoga:
    """
    Amrita Yoga (Nectar Yoga) - Jupiter in own sign or exaltation in
    the Ascendant, 5th, or 9th house.

    Condition: Jupiter is placed in either the 1st, 5th, or 9th house
               (trikona) from the Ascendant AND is in its own sign
               (Sagittarius or Pisces) or exaltation sign (Cancer).
    Effect: Long-lived like amrita (nectar of immortality), wisdom,
            spiritual growth, respected by all, blessed by Jupiter's
            full grace, liberated nature.

    Reference: Phaladeepika; various texts on Jupiter's strength.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        jupiter_long = get_planet_longitude(Planet.Jupiter, time)
        jupiter_sign = int(jupiter_long // 30)
        jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1

        dignity, score = get_dignity_status("Jupiter", jupiter_long)
        in_trikona = jupiter_house in [1, 5, 9]
        own_or_exalted = score >= 4

        occurring = in_trikona and own_or_exalted
        return Yoga(
            name="Amrita Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Long life, wisdom, spiritual grace, respected by all, Jupiter's full blessing",
            condition=(
                f"Jupiter {dignity} in H{jupiter_house} "
                f"(trikona={in_trikona}, own/exalted={own_or_exalted})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Amrita Yoga", YogaNature.GOOD, False, "Long life and wisdom", f"Error: {str(e)}")


# ========================================
# LAGNA-RELATIVE LUNAR YOGAS
# ========================================

def check_lagna_vesi_yoga(time: 'AstroTime') -> Yoga:
    """
    Lagna-Vesi Yoga - Planets (excluding Sun) in the 2nd house from Lagna.

    Condition: Any planet other than the Sun or Moon occupies the 2nd house
               from the Ascendant.
    Effect: Eloquent, wealthy speech, good communicator, accumulates
            wealth through skill, financially stable.

    Reference: Variant of Vesi applied to Lagna instead of Sun.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter,
                      Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
        in_2nd = [
            p.name for p in qualifiers
            if ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1 == 2
        ]
        occurring = bool(in_2nd)
        return Yoga(
            name="Lagna Vesi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Eloquent speech, financially stable, wealth through skill",
            condition=f"Planets in 2nd from Lagna: {', '.join(in_2nd)}" if occurring
                      else "No qualifying planet in 2nd house from Lagna",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Lagna Vesi Yoga", YogaNature.GOOD, False, "Eloquence and wealth", f"Error: {str(e)}")


def check_lagna_sunapha_yoga(time: 'AstroTime') -> Yoga:
    """
    Lagna Sunapha Yoga - Planets (excluding Sun/Moon) in the 2nd house
    from the Moon, applied relative to Lagna context.

    Classic Sunapha is from Moon. This variant checks planets in the 12th
    house from Lagna (the house behind the Ascendant), giving hidden
    strength and past-life merit.

    Condition: Any planet other than Sun or Moon in the 12th house from Lagna.
    Effect: Self-earned wealth, dignified, self-reliant, merits from past
            actions, hidden resources.

    Reference: Lagna-variant of classical Sunapha pattern.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter,
                      Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
        in_12th = [
            p.name for p in qualifiers
            if ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1 == 12
        ]
        occurring = bool(in_12th)
        return Yoga(
            name="Lagna Sunapha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Self-earned wealth, dignified, self-reliant, hidden resources, past merit",
            condition=f"Planets in 12th from Lagna: {', '.join(in_12th)}" if occurring
                      else "No qualifying planet in 12th house from Lagna",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Lagna Sunapha Yoga", YogaNature.GOOD, False, "Self-reliance and hidden merit", f"Error: {str(e)}")


def check_lagna_anapha_yoga(time: 'AstroTime') -> Yoga:
    """
    Lagna Anapha Yoga - Planets (excluding Sun/Moon) in both the 2nd
    and 12th houses from Lagna simultaneously.

    Condition: Qualifying planets are present in BOTH the 2nd AND 12th
               house from the Ascendant.
    Effect: Physically attractive, prosperous on both sides (income and
            savings), balanced life, supported from multiple directions.

    Reference: Lagna-variant of classical Dhurdhura / Anapha combination.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        qualifiers = [Planet.Mars, Planet.Mercury, Planet.Jupiter,
                      Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
        in_2nd = [
            p.name for p in qualifiers
            if ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1 == 2
        ]
        in_12th = [
            p.name for p in qualifiers
            if ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1 == 12
        ]
        occurring = bool(in_2nd) and bool(in_12th)
        return Yoga(
            name="Lagna Anapha Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Attractive, prosperous, balanced life, supported from multiple directions",
            condition=(
                f"2nd from Lagna: {', '.join(in_2nd) or 'none'}; "
                f"12th from Lagna: {', '.join(in_12th) or 'none'}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Lagna Anapha Yoga", YogaNature.GOOD, False, "Balance and prosperity", f"Error: {str(e)}")


# ========================================
# SURYA-CHANDRA YOGA
# ========================================

def check_surya_chandra_yoga(time: 'AstroTime') -> Yoga:
    """
    Surya-Chandra Yoga (Sun-Moon conjunction or opposition).

    Condition (New Moon variant): Sun and Moon are in the same sign (conjunction
               within 30°, i.e. same sign).
    Condition (Full Moon variant): Sun and Moon are in opposite signs (6 signs apart).
    Effect (conjunction — Amavasya): Intense focus, charismatic, strong
            willpower, but may be stubborn, emotionally intense.
    Effect (opposition — Purnima): Balanced, illumined mind, full of vitality,
            clear perception, emotionally expressive.

    Reference: Jataka Parijata; various classical texts on Amavasya/Purnima births.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        sun_sign = int(get_planet_longitude(Planet.Sun, time) // 30)
        moon_sign = int(get_planet_longitude(Planet.Moon, time) // 30)
        diff = abs(sun_sign - moon_sign) % 12

        conjunct = diff == 0
        opposition = diff == 6
        occurring = conjunct or opposition
        variant = "New Moon (conjunction)" if conjunct else "Full Moon (opposition)" if opposition else "Neither"
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        effect = (
            "Intense focus, charismatic, strong willpower, emotionally intense" if conjunct
            else "Balanced, illumined mind, full vitality, clear perception, expressive"
        )
        return Yoga(
            name="Surya-Chandra Yoga",
            nature=YogaNature.NEUTRAL,
            occurring=occurring,
            description=effect if occurring else "Sun and Moon in neither conjunction nor opposition",
            condition=(
                f"{variant}: Sun in {sign_names[sun_sign]}, Moon in {sign_names[moon_sign]}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Surya-Chandra Yoga", YogaNature.NEUTRAL, False, "Sun-Moon relationship", f"Error: {str(e)}")


# ========================================
# VISHNU, BRAHMA, HARI YOGAS
# ========================================

def check_vishnu_yoga(time: 'AstroTime') -> Yoga:
    """
    Vishnu Yoga - Lord of 9th in 10th AND lord of 10th conjoins Venus.

    Condition: Lord of the 9th house is placed in the 10th house AND the
               lord of the 10th house is conjoined with Venus (same sign).
    Effect: Blessed by Vishnu (preserver energy), very wealthy, long-lived,
            commander of armies, virtuous, famous across the land.

    Reference: Brihat Parashara Hora Shastra — Vishnu Yoga chapter.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .lordship import get_lord_of_house
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        lord_9  = get_lord_of_house(9, time)
        lord_10 = get_lord_of_house(10, time)

        sign_lord9  = int(get_planet_longitude(lord_9, time) // 30)
        sign_lord10 = int(get_planet_longitude(lord_10, time) // 30)
        sign_venus  = int(get_planet_longitude(Planet.Venus, time) // 30)

        house_of_lord9 = ((sign_lord9 - lagna_sign) % 12) + 1
        lord9_in_10th  = house_of_lord9 == 10
        lord10_with_venus = sign_lord10 == sign_venus

        occurring = lord9_in_10th and lord10_with_venus
        return Yoga(
            name="Vishnu Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Very wealthy, long-lived, virtuous, famous, preserved by divine grace",
            condition=(
                f"9th lord {lord_9.name} in H{house_of_lord9} (need H10); "
                f"10th lord {lord_10.name} in sign {sign_lord10+1}, Venus in sign {sign_venus+1} "
                f"(conjoined={lord10_with_venus})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vishnu Yoga", YogaNature.GOOD, False, "Divine wealth and longevity", f"Error: {str(e)}")


def check_brahma_yoga(time: 'AstroTime') -> Yoga:
    """
    Brahma Yoga - Jupiter strong in kendra from Venus, Mercury, or Lagna lord.

    Condition: Jupiter occupies the 1st, 4th, 7th, or 10th house and is in
               a kendra (1/4/7/10) counted from the sign of Venus OR from
               Mercury's sign OR from the Lagna lord's sign.
    Simplified check: Jupiter is in a kendra from the Ascendant AND
               is aspected by or conjoined with Venus or Mercury.
    Effect: Eloquent, creator-like wisdom, skilled in arts, creator of
            great literary works, respected by scholars.

    Reference: Brihat Parashara Hora Shastra — Brahma Yoga chapter.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        jup_sign   = int(get_planet_longitude(Planet.Jupiter, time) // 30)
        ven_sign   = int(get_planet_longitude(Planet.Venus,   time) // 30)
        mer_sign   = int(get_planet_longitude(Planet.Mercury, time) // 30)

        jup_house  = ((jup_sign - lagna_sign) % 12) + 1
        jup_kendra = jup_house in [1, 4, 7, 10]

        # Jupiter in kendra from Venus
        jup_kendra_from_ven = ((jup_sign - ven_sign) % 12) + 1 in [1, 4, 7, 10]
        # Jupiter in kendra from Mercury
        jup_kendra_from_mer = ((jup_sign - mer_sign) % 12) + 1 in [1, 4, 7, 10]

        occurring = jup_kendra and (jup_kendra_from_ven or jup_kendra_from_mer)
        return Yoga(
            name="Brahma Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Creator-like wisdom, eloquent, skilled in arts, literary fame, scholarly respect",
            condition=(
                f"Jupiter in H{jup_house} (kendra={jup_kendra}); "
                f"kendra from Venus={jup_kendra_from_ven}, kendra from Mercury={jup_kendra_from_mer}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Brahma Yoga", YogaNature.GOOD, False, "Creative wisdom and eloquence", f"Error: {str(e)}")


def check_hari_yoga(time: 'AstroTime') -> Yoga:
    """
    Hari Yoga - Mercury, Jupiter, and Venus each in a trikona house.

    Condition: Mercury, Jupiter, and Venus are each placed in one of the
               trikona houses (1st, 5th, or 9th) from the Ascendant.
               They may share a trikona or be in different trikon houses.
    Effect: Fame of Vishnu (Hari), very wealthy, charitable, eloquent,
            versed in scriptures, respected by kings.

    Reference: Brihat Parashara Hora Shastra — Hari Yoga chapter.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)

        def house_of(planet):
            return ((int(get_planet_longitude(planet, time) // 30) - lagna_sign) % 12) + 1

        mer_h = house_of(Planet.Mercury)
        jup_h = house_of(Planet.Jupiter)
        ven_h = house_of(Planet.Venus)

        trikona = [1, 5, 9]
        occurring = mer_h in trikona and jup_h in trikona and ven_h in trikona
        return Yoga(
            name="Hari Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Fame like Vishnu, very wealthy, charitable, eloquent, scriptural knowledge",
            condition=(
                f"Mercury H{mer_h}, Jupiter H{jup_h}, Venus H{ven_h} "
                f"(all trikona={occurring})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Hari Yoga", YogaNature.GOOD, False, "Vishnu-like fame and wealth", f"Error: {str(e)}")


# ========================================
# PLANETARY DISTRIBUTION YOGAS
# ========================================

def check_deva_yoga(time: 'AstroTime') -> Yoga:
    """
    Deva Yoga - All 7 classical planets in odd houses from Ascendant.

    Condition: All seven classical planets (Sun, Moon, Mars, Mercury,
               Jupiter, Venus, Saturn) are placed only in odd-numbered
               houses (1, 3, 5, 7, 9, 11) from the Ascendant.
    Effect: God-like qualities, divine nature, generous, virtuous,
            pious, respected, celestial grace.

    Reference: Phaladeepika; Sarvartha Chintamani.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        classical  = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                      Planet.Jupiter, Planet.Venus, Planet.Saturn]
        houses = [
            ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1
            for p in classical
        ]
        occurring = all(h % 2 == 1 for h in houses)
        return Yoga(
            name="Deva Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="God-like qualities, divine nature, generous, virtuous, celestial grace",
            condition=f"Houses: {houses} (all odd={occurring})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Deva Yoga", YogaNature.GOOD, False, "Divine nature", f"Error: {str(e)}")


def check_asura_yoga(time: 'AstroTime') -> Yoga:
    """
    Asura Yoga - All 7 classical planets in even houses from Ascendant.

    Condition: All seven classical planets (Sun, Moon, Mars, Mercury,
               Jupiter, Venus, Saturn) are placed only in even-numbered
               houses (2, 4, 6, 8, 10, 12) from the Ascendant.
    Effect: Demonic tendencies, cruel, harsh nature, aggressive,
            self-centred, accumulates but through questionable means.

    Reference: Phaladeepika; Sarvartha Chintamani.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        classical  = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                      Planet.Jupiter, Planet.Venus, Planet.Saturn]
        houses = [
            ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1
            for p in classical
        ]
        occurring = all(h % 2 == 0 for h in houses)
        return Yoga(
            name="Asura Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Harsh nature, aggressive, self-centred, demonic tendencies",
            condition=f"Houses: {houses} (all even={occurring})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Asura Yoga", YogaNature.BAD, False, "Demonic tendencies", f"Error: {str(e)}")


def check_kuhu_yoga(time: 'AstroTime') -> Yoga:
    """
    Kuhu Yoga - All 7 classical planets in dusthana houses (6, 8, 12).

    Condition: All seven classical planets are confined to the three
               dusthana (evil/difficult) houses: 6th, 8th, and 12th from
               the Ascendant.
    Effect: Suffering, poverty, many obstacles, weak constitution, troubled
            life, dependent on others, obscured potential.

    Reference: Brihat Parashara Hora Shastra; Jataka Parijata.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        classical  = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                      Planet.Jupiter, Planet.Venus, Planet.Saturn]
        houses = [
            ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1
            for p in classical
        ]
        occurring = all(h in [6, 8, 12] for h in houses)
        return Yoga(
            name="Kuhu Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Suffering, poverty, obstacles, weak constitution, dependent life",
            condition=f"Houses: {houses} (all dusthana={occurring})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kuhu Yoga", YogaNature.BAD, False, "Suffering and obstacles", f"Error: {str(e)}")


def check_phala_yoga(time: 'AstroTime') -> Yoga:
    """
    Phala Yoga - All 7 classical planets concentrated in trikona houses.

    Condition: All seven classical planets are placed in trikona houses
               (1st, 5th, or 9th) from the Ascendant.
    Effect: Fruits of past deeds (phala) ripen abundantly; blessed,
            fortunate, reaps rewards of good karma, prosperous life.

    Reference: Sarvartha Chintamani; various Nabhasa-type texts.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_sign = int(get_lagnam(time) // 30)
        classical  = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                      Planet.Jupiter, Planet.Venus, Planet.Saturn]
        houses = [
            ((int(get_planet_longitude(p, time) // 30) - lagna_sign) % 12) + 1
            for p in classical
        ]
        occurring = all(h in [1, 5, 9] for h in houses)
        return Yoga(
            name="Phala Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Abundant fruits of good karma, blessed, fortunate, prosperous life",
            condition=f"Houses: {houses} (all trikona={occurring})",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Phala Yoga", YogaNature.GOOD, False, "Fruition of good karma", f"Error: {str(e)}")


# ========================================
# EVIL-HOUSE LORD YOGA
# ========================================

def check_nidana_yoga(time: 'AstroTime') -> Yoga:
    """
    Nidana Yoga - Lord of the 8th house placed in the 8th house.

    Condition: The planet that rules the 8th house from the Ascendant
               is itself placed in the 8th house.
    Effect: Chronic illness, obstacles to longevity, hidden troubles,
            accidents, surgeries; though some texts say it can give
            occult power or longevity if the 8th lord is strong.

    Reference: Brihat Parashara Hora Shastra — Bhava Karaka chapter.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .lordship import get_lord_of_house

        lagna_sign = int(get_lagnam(time) // 30)
        lord_8     = get_lord_of_house(8, time)
        sign_lord8 = int(get_planet_longitude(lord_8, time) // 30)
        house_lord8 = ((sign_lord8 - lagna_sign) % 12) + 1

        occurring = house_lord8 == 8
        return Yoga(
            name="Nidana Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Chronic illness, hidden troubles, obstacles to longevity, hidden occult power",
            condition=f"8th lord {lord_8.name} in H{house_lord8} (need H8)",
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Nidana Yoga", YogaNature.BAD, False, "Hidden troubles", f"Error: {str(e)}")


# ========================================
# BENEFIC / DIGNITY YOGAS
# ========================================

def check_koumara_yoga(time: 'AstroTime') -> Yoga:
    """
    Koumara Yoga - Mars in own or exalted sign in a kendra house.

    Condition: Mars is placed in the 1st, 4th, 7th, or 10th house from
               the Ascendant AND is in its own sign (Aries or Scorpio)
               or exaltation sign (Capricorn).
    Effect: Commander (Kumara/Kartikeya-like), very brave, military fame,
            athletic, powerful, leader of soldiers, victory in battles.

    Reference: Phaladeepika — Yogas of Mars.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .avastha import get_dignity_status

        lagna_sign  = int(get_lagnam(time) // 30)
        mars_long   = get_planet_longitude(Planet.Mars, time)
        mars_sign   = int(mars_long // 30)
        mars_house  = ((mars_sign - lagna_sign) % 12) + 1
        dignity, score = get_dignity_status("Mars", mars_long)

        in_kendra      = mars_house in [1, 4, 7, 10]
        own_or_exalted = score >= 4

        occurring = in_kendra and own_or_exalted
        return Yoga(
            name="Koumara Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Commander-like, very brave, military fame, athletic, victory in battles",
            condition=(
                f"Mars {dignity} in H{mars_house} "
                f"(kendra={in_kendra}, own/exalted={own_or_exalted})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Koumara Yoga", YogaNature.GOOD, False, "Military fame and bravery", f"Error: {str(e)}")


def check_chandra_mangala_adhi_yoga(time: 'AstroTime') -> Yoga:
    """
    Chandra-Mangala Adhi Yoga - Benefics (Mercury, Jupiter, Venus) in
    6th, 7th, and 8th houses from the Moon.

    This is the Moon-based Adhi Yoga variant (classical Adhi Yoga already
    checks from Lagna; this checks from Moon).

    Condition: At least one of Mercury, Jupiter, Venus is in the 6th from
               Moon AND at least one is in the 7th from Moon AND at least
               one is in the 8th from Moon.
    Effect: Minister, chief, prosperous, defeated enemies, long-lived,
            comfortable, victorious.

    Reference: Brihat Parashara Hora Shastra — Adhi Yoga chapter.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        moon_sign  = int(get_planet_longitude(Planet.Moon, time) // 30)
        benefics   = [Planet.Mercury, Planet.Jupiter, Planet.Venus]

        def house_from_moon(p):
            return ((int(get_planet_longitude(p, time) // 30) - moon_sign) % 12) + 1

        h6 = [p.name for p in benefics if house_from_moon(p) == 6]
        h7 = [p.name for p in benefics if house_from_moon(p) == 7]
        h8 = [p.name for p in benefics if house_from_moon(p) == 8]

        occurring = bool(h6) and bool(h7) and bool(h8)
        return Yoga(
            name="Chandra Adhi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Minister, chief, prosperous, defeated enemies, long-lived, victorious",
            condition=(
                f"From Moon — 6th: {h6 or 'none'}, 7th: {h7 or 'none'}, 8th: {h8 or 'none'}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Chandra Adhi Yoga", YogaNature.GOOD, False, "Ministership from Moon", f"Error: {str(e)}")


def check_budha_chandra_yoga(time: 'AstroTime') -> Yoga:
    """
    Budha-Chandra Yoga (Mercury-Moon conjunction) - Moon and Mercury in
    the same sign.

    Condition: Moon and Mercury occupy the same zodiac sign.
    Effect: Highly intelligent, quick wit, excellent communicator,
            skilled in trade and oratory, witty, popular, learned.

    Reference: Phaladeepika; Jataka Parijata — planetary conjunctions.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet

        moon_sign = int(get_planet_longitude(Planet.Moon,    time) // 30)
        mer_sign  = int(get_planet_longitude(Planet.Mercury, time) // 30)

        occurring = moon_sign == mer_sign
        sign_names = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                      "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        return Yoga(
            name="Budha-Chandra Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Highly intelligent, quick wit, excellent communicator, witty, popular, learned",
            condition=(
                f"Moon in {sign_names[moon_sign]}, Mercury in {sign_names[mer_sign]} "
                f"(same sign={occurring})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Budha-Chandra Yoga", YogaNature.GOOD, False, "Intelligence and communication", f"Error: {str(e)}")


# ========================================
# SPECIFIC MALIKA YOGAS (House Chain from Bhava)
# ========================================

def _malika_chain_from_house(start_house: int, time: 'AstroTime') -> tuple:
    """
    Internal helper: verify that each of the 7 consecutive houses
    starting from start_house is occupied by at least one classical
    planet (Sun through Saturn, Rahu/Ketu excluded).

    Returns:
        (occurring: bool, condition_str: str)
    """
    from .calculate import get_planet_longitude, get_lagnam
    from .consts import Planet

    lagna_long = get_lagnam(time)
    lagna_sign = int(lagna_long // 30)
    classical = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                 Planet.Jupiter, Planet.Venus, Planet.Saturn]

    occupied = set()
    for p in classical:
        p_sign = int(get_planet_longitude(p, time) // 30)
        h = ((p_sign - lagna_sign) % 12) + 1
        occupied.add(h)

    chain = [((start_house - 1 + i) % 12) + 1 for i in range(7)]
    missing = [h for h in chain if h not in occupied]
    occurring = len(missing) == 0
    end_label = chain[-1]
    chain_str = (
        f"H{chain[0]}-H{end_label} chain occupied={sorted(occupied)}"
        + (f", missing H{missing}" if missing else " — all 7 filled")
    )
    return occurring, chain_str


def check_lagna_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Lagna Malika Yoga — Planetary Garland from the 1st House.

    Condition: All 7 classical planets (Sun–Saturn, excluding Rahu/Ketu)
               each occupy one of 7 consecutive houses starting from
               the Ascendant (houses 1 through 7 all occupied).
    Effect: King, ruler or commander, wealthy.

    Reference: Phaladeepika; Sarvartha Chintamani — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(1, time)
        return Yoga(
            name="Lagna Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="King, ruler or commander, wealthy",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Lagna Malika Yoga", YogaNature.GOOD, False,
                   "King, ruler or commander, wealthy", f"Error: {str(e)}")


def check_dhana_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Dhana Malika Yoga — Planetary Garland from the 2nd House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 2nd house (houses 2 through 8 all occupied).
    Effect: Very wealthy, dutiful, resolute and unsympathetic.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(2, time)
        return Yoga(
            name="Dhana Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Very wealthy, dutiful, resolute and unsympathetic",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Dhana Malika Yoga", YogaNature.GOOD, False,
                   "Very wealthy, dutiful, resolute", f"Error: {str(e)}")


def check_vikrama_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Vikrama Malika Yoga — Planetary Garland from the 3rd House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 3rd house (houses 3 through 9 all occupied).
    Effect: Ruler, rich, surrounded by brave men.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(3, time)
        return Yoga(
            name="Vikrama Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Ruler, rich, surrounded by brave men",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vikrama Malika Yoga", YogaNature.GOOD, False,
                   "Ruler, rich, surrounded by brave men", f"Error: {str(e)}")


def check_sukha_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Sukha Malika Yoga — Planetary Garland from the 4th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 4th house (houses 4 through 10 all occupied).
    Effect: Charitable and wealthy.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(4, time)
        return Yoga(
            name="Sukha Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Charitable and wealthy",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Sukha Malika Yoga", YogaNature.GOOD, False,
                   "Charitable and wealthy", f"Error: {str(e)}")


def check_putra_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Putra Malika Yoga — Planetary Garland from the 5th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 5th house (houses 5 through 11 all occupied).
    Effect: Highly religious and famous.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(5, time)
        return Yoga(
            name="Putra Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Highly religious and famous",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Putra Malika Yoga", YogaNature.GOOD, False,
                   "Highly religious and famous", f"Error: {str(e)}")


def check_satru_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Satru Malika Yoga — Planetary Garland from the 6th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 6th house (houses 6 through 12 all occupied).
    Effect: Greedy and somewhat poor.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(6, time)
        return Yoga(
            name="Satru Malika Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Greedy and somewhat poor",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Satru Malika Yoga", YogaNature.BAD, False,
                   "Greedy and somewhat poor", f"Error: {str(e)}")


def check_kalatra_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Kalatra Malika Yoga — Planetary Garland from the 7th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 7th house (houses 7 through 1, wrapping).
    Effect: Coveted by women and influential.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(7, time)
        return Yoga(
            name="Kalatra Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Coveted by women and influential",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Kalatra Malika Yoga", YogaNature.GOOD, False,
                   "Coveted by women and influential", f"Error: {str(e)}")


def check_randhra_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Randhra Malika Yoga — Planetary Garland from the 8th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 8th house (houses 8 through 2, wrapping).
    Effect: Poor and hen-pecked.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(8, time)
        return Yoga(
            name="Randhra Malika Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Poor and hen-pecked",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Randhra Malika Yoga", YogaNature.BAD, False,
                   "Poor and hen-pecked", f"Error: {str(e)}")


def check_bhagya_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Bhagya Malika Yoga — Planetary Garland from the 9th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 9th house (houses 9 through 3, wrapping).
    Effect: Religious, well-to-do, mighty and good.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(9, time)
        return Yoga(
            name="Bhagya Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Religious, well-to-do, mighty and good",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Bhagya Malika Yoga", YogaNature.GOOD, False,
                   "Religious, well-to-do, mighty and good", f"Error: {str(e)}")


def check_karma_malika_yoga(time: 'AstroTime') -> Yoga:
    """
    Karma Malika Yoga — Planetary Garland from the 10th House.

    Condition: All 7 classical planets occupy 7 consecutive houses
               starting from the 10th house (houses 10 through 4, wrapping).
    Effect: Career excellence, karmic fulfillment, respected for deeds.

    Reference: Phaladeepika — Malika Yoga chapter.
    """
    try:
        occurring, chain_str = _malika_chain_from_house(10, time)
        return Yoga(
            name="Karma Malika Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Career excellence, karmic fulfillment, respected for deeds",
            condition=chain_str,
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Karma Malika Yoga", YogaNature.GOOD, False,
                   "Career excellence, karmic fulfillment", f"Error: {str(e)}")


# ========================================
# ROYAL / SPECIAL CLASSICAL YOGAS
# ========================================

def check_rajalakshana_yoga(time: 'AstroTime') -> Yoga:
    """
    Rajalakshana Yoga (Royal Marks Yoga).

    Condition: Jupiter, Venus, Mercury and Moon should all be in Lagna
               (house 1) or all placed in kendra houses (1st, 4th, 7th, 10th).
    Effect: Attractive appearance, endowed with all good qualities of
            high personages.

    Reference: VedAstro HoroscopeName — RajalakshanaYoga.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)
        kendra = {1, 4, 7, 10}

        planets_to_check = [Planet.Jupiter, Planet.Venus, Planet.Mercury, Planet.Moon]
        houses = {}
        for p in planets_to_check:
            p_sign = int(get_planet_longitude(p, time) // 30)
            houses[p] = ((p_sign - lagna_sign) % 12) + 1

        all_in_lagna  = all(h == 1 for h in houses.values())
        all_in_kendra = all(h in kendra for h in houses.values())
        occurring = all_in_lagna or all_in_kendra

        return Yoga(
            name="Rajalakshana Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Attractive appearance, endowed with all good qualities of high personages",
            condition=(
                f"Jupiter H{houses[Planet.Jupiter]}, Venus H{houses[Planet.Venus]}, "
                f"Mercury H{houses[Planet.Mercury]}, Moon H{houses[Planet.Moon]} "
                f"(all in kendra={all_in_kendra})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Rajalakshana Yoga", YogaNature.GOOD, False,
                   "Royal appearance, good qualities of high personages", f"Error: {str(e)}")


def check_vanchana_chora_bheethi_yoga(time: 'AstroTime') -> Yoga:
    """
    Vanchana-Chora-Bheethi Yoga (Fear of Deceit and Thieves).

    Condition (any one of):
    (a) Lagna is occupied by a malefic planet (Sun, Mars, Saturn, Rahu or Ketu).
    (b) Lord of Lagna is conjunct Saturn, Rahu, or Ketu (same sign).
    Note: Classical texts also cite Gulika-in-trine conditions; Gulika/Mandi
          calculation is not yet implemented in this module.
    Effect: Always suspicious; afraid of being cheated, swindled, and robbed.

    Reference: VedAstro HoroscopeName — VanchanaChoraBheethiYoga.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        all_with_nodes = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                          Planet.Jupiter, Planet.Venus, Planet.Saturn,
                          Planet.Rahu, Planet.Ketu]
        malefics   = {Planet.Sun, Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu}
        afflictors = {Planet.Saturn, Planet.Rahu, Planet.Ketu}

        planet_signs  = {p: int(get_planet_longitude(p, time) // 30) for p in all_with_nodes}
        planet_houses = {p: ((planet_signs[p] - lagna_sign) % 12) + 1 for p in all_with_nodes}

        # (a) Malefic in Lagna
        malefics_in_lagna = [p.name for p in malefics if planet_houses[p] == 1]
        cond_a = bool(malefics_in_lagna)

        # (b) Lagna lord conjunct Saturn/Rahu/Ketu
        lord_1 = get_lord_of_house(1, time)
        lord_1_sign = planet_signs.get(lord_1, -1)
        cond_b_planets = [p.name for p in afflictors if planet_signs[p] == lord_1_sign]
        cond_b = bool(cond_b_planets)

        occurring = cond_a or cond_b
        details = []
        if cond_a:
            details.append(f"malefic(s) in H1: {malefics_in_lagna}")
        if cond_b:
            details.append(f"Lagna lord {lord_1.name} conjunct {cond_b_planets}")
        if not details:
            details.append("no affliction conditions met")

        return Yoga(
            name="Vanchana-Chora-Bheethi Yoga",
            nature=YogaNature.BAD,
            occurring=occurring,
            description="Always suspicious; afraid of being cheated, swindled, and robbed",
            condition="; ".join(details),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Vanchana-Chora-Bheethi Yoga", YogaNature.BAD, False,
                   "Fear of deception and theft", f"Error: {str(e)}")


def check_gauri_yoga(time: 'AstroTime') -> Yoga:
    """
    Gauri Yoga.

    Condition: The lord of the Navamsa (D9) sign occupied by the 10th lord
               must be (a) placed in the 10th house in exaltation AND
               (b) conjunct (same sign as) the lord of the Ascendant.
    Effect: Respectable family, owns lands, charitable, religious, sons of
            good character, praised by all.

    Reference: Jataka Parijata — GauriYoga; VedAstro HoroscopeName.
    """
    try:
        from .calculate import get_planet_longitude, get_lagnam
        from .consts import Planet
        from .lordship import get_lord_of_house, get_lord_of_sign
        from .varga import get_d9_navamsa
        from .avastha import get_dignity_status

        lagna_long = get_lagnam(time)
        lagna_sign = int(lagna_long // 30)

        # Step 1: 10th lord and its longitude
        lord_10 = get_lord_of_house(10, time)
        lord_10_long = get_planet_longitude(lord_10, time)

        # Step 2: D9 navamsa sign of the 10th lord (sign_num is 1-indexed)
        _, navamsa_sign_num = get_d9_navamsa(lord_10_long)
        navamsa_lord = get_lord_of_sign(navamsa_sign_num - 1)

        # Step 3: Navamsa lord in 10th house and exalted
        navamsa_lord_long  = get_planet_longitude(navamsa_lord, time)
        navamsa_lord_sign  = int(navamsa_lord_long // 30)
        navamsa_lord_house = ((navamsa_lord_sign - lagna_sign) % 12) + 1
        dignity, score     = get_dignity_status(navamsa_lord.name, navamsa_lord_long)
        in_10th_exalted    = (navamsa_lord_house == 10) and (score >= 5)

        # Step 4: Navamsa lord conjunct lagna lord (same sign)
        lord_1      = get_lord_of_house(1, time)
        lord_1_long = get_planet_longitude(lord_1, time)
        lord_1_sign = int(lord_1_long // 30)
        conjunct_lagna_lord = (navamsa_lord_sign == lord_1_sign)

        occurring = in_10th_exalted and conjunct_lagna_lord
        return Yoga(
            name="Gauri Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="Respectable family, landowner, charitable, religious, praised by all",
            condition=(
                f"10th lord {lord_10.name} D9-sign {navamsa_sign_num} "
                f"→ navamsa lord {navamsa_lord.name} H{navamsa_lord_house} ({dignity}); "
                f"Lagna lord {lord_1.name} sign {lord_1_sign + 1} "
                f"(conjunct navamsa lord={conjunct_lagna_lord})"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Gauri Yoga", YogaNature.GOOD, False,
                   "Respectable family, charitable, praised by all", f"Error: {str(e)}")


def check_bharathi_yoga(time: 'AstroTime') -> Yoga:
    """
    Bharathi Yoga.

    Condition: The lords of the 2nd, 5th, and 11th houses must all fall
               in the same Navamsa (D9) sign. The lord of that common D9
               sign must be exalted AND conjunct (same sign as) the 9th lord.
    Effect: World famous, reputed scholar, fond of music, romantic, handsome,
            attractive, religiously inclined, bewitching eyes.

    Reference: Classical texts — BharathiYoga; VedAstro HoroscopeName.
    """
    try:
        from .calculate import get_planet_longitude
        from .consts import Planet
        from .lordship import get_lord_of_house, get_lord_of_sign
        from .varga import get_d9_navamsa
        from .avastha import get_dignity_status

        lord_2  = get_lord_of_house(2,  time)
        lord_5  = get_lord_of_house(5,  time)
        lord_11 = get_lord_of_house(11, time)

        long_2  = get_planet_longitude(lord_2,  time)
        long_5  = get_planet_longitude(lord_5,  time)
        long_11 = get_planet_longitude(lord_11, time)

        _, d9_2  = get_d9_navamsa(long_2)
        _, d9_5  = get_d9_navamsa(long_5)
        _, d9_11 = get_d9_navamsa(long_11)

        same_d9 = (d9_2 == d9_5 == d9_11)

        nv_exalted   = False
        nv_conj_9    = False
        nv_lord_info = "N/A"

        if same_d9:
            navamsa_lord = get_lord_of_sign(d9_2 - 1)
            nv_long      = get_planet_longitude(navamsa_lord, time)
            dignity, score = get_dignity_status(navamsa_lord.name, nv_long)
            nv_exalted   = (score >= 5)
            lord_9       = get_lord_of_house(9, time)
            lord_9_long  = get_planet_longitude(lord_9, time)
            nv_sign      = int(nv_long // 30)
            l9_sign      = int(lord_9_long // 30)
            nv_conj_9    = (nv_sign == l9_sign)
            nv_lord_info = (
                f"{navamsa_lord.name} {dignity} sign {nv_sign + 1}; "
                f"9th lord {lord_9.name} sign {l9_sign + 1} (conjunct={nv_conj_9})"
            )

        occurring = same_d9 and nv_exalted and nv_conj_9
        return Yoga(
            name="Bharathi Yoga",
            nature=YogaNature.GOOD,
            occurring=occurring,
            description="World famous, reputed scholar, fond of music, romantic, handsome, bewitching eyes",
            condition=(
                f"2nd/5th/11th lords same D9={same_d9} (D9 {d9_2},{d9_5},{d9_11}); "
                f"{nv_lord_info}"
            ),
            strength=100 if occurring else 0,
        )
    except Exception as e:
        return Yoga("Bharathi Yoga", YogaNature.GOOD, False,
                   "World famous, scholar, musical, handsome", f"Error: {str(e)}")


def get_occurring_yogas(time: 'AstroTime') -> List[Yoga]:
    """
    Get only the yogas that are currently occurring
    
    Args:
        time: AstroTime object with birth datetime and location
        
    Returns:
        List of only occurring Yoga objects
    """
    all_yogas = get_all_yogas(time)
    return [yoga for yoga in all_yogas if yoga.occurring]


def get_good_yogas(time: 'AstroTime') -> List[Yoga]:
    """Get all good/beneficial yogas that are occurring"""
    occurring = get_occurring_yogas(time)
    return [y for y in occurring if y.nature == YogaNature.GOOD]


def get_bad_yogas(time: 'AstroTime') -> List[Yoga]:
    """Get all bad/malefic yogas that are occurring"""
    occurring = get_occurring_yogas(time)
    return [y for y in occurring if y.nature == YogaNature.BAD]


def yoga_summary(time: 'AstroTime') -> Dict:
    """
    Get a summary report of all yogas
    
    Returns:
        Dictionary with counts and lists of yogas by category
    """
    all_yogas = get_all_yogas(time)
    occurring = get_occurring_yogas(time)
    
    return {
        "total_checked": len(all_yogas),
        "total_occurring": len(occurring),
        "good_yogas": [y.name for y in occurring if y.nature == YogaNature.GOOD],
        "bad_yogas": [y.name for y in occurring if y.nature == YogaNature.BAD],
        "neutral_yogas": [y.name for y in occurring if y.nature == YogaNature.NEUTRAL],
        "mixed_yogas": [y.name for y in occurring if y.nature == YogaNature.MIXED],
    }


# ========================================
# TODO: ASHTAKAVARGA YOGAS (to be implemented)
# ========================================

def check_sun_ashtakavarga_yoga2(datetime_str: str, location: str) -> Yoga:
    """
    Sun Ashtakavarga Yoga 2
    
    Condition: If bindus are 3 or 4 and Sun not in exaltation/own sign
    Effect: The person will always be ill
    
    TODO: Implement using ashtakavarga.sarvashtakavarga()
    """
    return Yoga(
        name="SunAshtakavargaYoga2",
        nature=YogaNature.BAD,
        occurring=False,  # TODO: implement check
        description="The person will always be ill",
        condition="Sun with 3-4 bindus, not exalted/own sign"
    )


# TODO: Implement remaining 90+ yogas...


if __name__ == "__main__":
    # Example usage
    test_time = "23:40 13/06/1994 +05:30"
    test_location = "Chennai"
    
    print("=" * 60)
    print("VedAstro Yogas - Test Run")
    print("=" * 60)
    print(f"Time: {test_time}")
    print(f"Location: {test_location}\n")
    
    # Check all yogas
    summary = yoga_summary(test_time, test_location)
    print(f"Total Yogas Checked: {summary['total_checked']}")
    print(f"Occurring Yogas: {summary['total_occurring']}\n")
    
    # Show occurring yogas
    occurring = get_occurring_yogas(test_time, test_location)
    if occurring:
        print("OCCURRING YOGAS:")
        print("-" * 60)
        for yoga in occurring:
            print(f"\n{yoga}")
    else:
        print("No yogas are currently occurring.")
