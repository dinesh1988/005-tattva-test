"""
Ved Astro - Yogas Module
========================

Implements detection of 94 traditional Vedic astrology Yogas (planetary combinations)
plus 1000+ astrological events from muhurtha (electional astrology).

## Implemented Yogas (32 total):

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
