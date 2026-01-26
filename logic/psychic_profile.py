"""
Psychic Profile Generator
=========================
A formula-based system to generate consistent psychic profiles from birth charts.

The 3-Step Formula:
1. Input Channel (How they receive info) → Moon Element
2. Superpower (What they can do) → Nakshatra
3. Signal Strength (Intensity/Depth) → Ketu's House

This creates unique combinations: 4 channels × 27 superpowers × 12 strengths = 1,296 profiles
"""

from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import swisseph as swe

# =============================================================================
# STEP 1: PSYCHIC CHANNELS (Moon Element)
# =============================================================================

# Sign to Element mapping
SIGN_ELEMENTS = {
    'Aries': 'Fire', 'Taurus': 'Earth', 'Gemini': 'Air', 'Cancer': 'Water',
    'Leo': 'Fire', 'Virgo': 'Earth', 'Libra': 'Air', 'Scorpio': 'Water',
    'Sagittarius': 'Fire', 'Capricorn': 'Earth', 'Aquarius': 'Air', 'Pisces': 'Water'
}

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Psychic Channels by Element
PSYCHIC_CHANNELS = {
    'Water': {
        'name': 'Clairsentience',
        'short': 'The Feeler',
        'definition': 'Feeling. They absorb emotions physically; sponges for the room\'s vibe.',
        'mechanism': 'Emotional absorption through the aura',
        'strengths': ['Reading emotions', 'Sensing danger', 'Empathic healing', 'Crowd dynamics'],
        'weaknesses': ['Emotional overwhelm', 'Boundary issues', 'Energy vampires'],
        'signs': ['Cancer', 'Scorpio', 'Pisces'],
        'symbol': '💧',
        'color': 'Deep Blue'
    },
    'Fire': {
        'name': 'Claircognizance',
        'short': 'The Knower',
        'definition': 'Knowing. Sudden gut downloads; instant truth detection without logic.',
        'mechanism': 'Direct knowledge transmission to the solar plexus',
        'strengths': ['Lie detection', 'Instant insights', 'Leadership intuition', 'Danger sensing'],
        'weaknesses': ['Cannot explain how they know', 'Impatience with skeptics', 'Overconfidence'],
        'signs': ['Aries', 'Leo', 'Sagittarius'],
        'symbol': '🔥',
        'color': 'Golden Orange'
    },
    'Air': {
        'name': 'Telepathy',
        'short': 'The Mind Reader',
        'definition': 'Hearing/Thinking. Reading thoughts, patterns, and systemic logic.',
        'mechanism': 'Mental frequency attunement',
        'strengths': ['Thought reading', 'Pattern recognition', 'Communication with guides', 'Mental influence'],
        'weaknesses': ['Mental noise', 'Overthinking', 'Difficulty distinguishing own thoughts'],
        'signs': ['Gemini', 'Libra', 'Aquarius'],
        'symbol': '💨',
        'color': 'Electric Violet'
    },
    'Earth': {
        'name': 'Psychometry',
        'short': 'The Sensor',
        'definition': 'Sensing. Touching objects/places to read their history; physical somatic signals.',
        'mechanism': 'Energy imprint reading through physical contact',
        'strengths': ['Object reading', 'Location history', 'Physical intuition', 'Body wisdom'],
        'weaknesses': ['Needs physical contact', 'Slow activation', 'Can\'t turn it off with touch'],
        'signs': ['Taurus', 'Virgo', 'Capricorn'],
        'symbol': '🌍',
        'color': 'Forest Green'
    }
}


# =============================================================================
# STEP 2: SUPERPOWERS (Nakshatra-based)
# =============================================================================

NAKSHATRA_SUPERPOWERS = {
    1: {  # Ashwini
        'nakshatra': 'Ashwini',
        'superpower': 'Miraculous Healing',
        'archetype': 'The Divine Physician',
        'ability': 'Spontaneous healing abilities; can sense illness before symptoms appear',
        'specialty': 'Emergency intuition, instant diagnosis, healing touch',
        'deity': 'Ashwini Kumaras (Divine Physicians)',
        'activation': 'During emergencies or when someone is in physical distress'
    },
    2: {  # Bharani
        'nakshatra': 'Bharani',
        'superpower': 'Death Sensing',
        'archetype': 'The Soul Guide',
        'ability': 'Can sense when death is near; communicates with souls in transition',
        'specialty': 'End-of-life intuition, past life access, rebirth visions',
        'deity': 'Yama (Lord of Death)',
        'activation': 'Near hospitals, graveyards, or during life transitions'
    },
    3: {  # Krittika
        'nakshatra': 'Krittika',
        'superpower': 'Truth Burning',
        'archetype': 'The Purifier',
        'ability': 'Can instantly detect lies; their presence burns away illusions',
        'specialty': 'Lie detection, cutting through deception, revealing hidden truths',
        'deity': 'Agni (Fire God)',
        'activation': 'When someone speaks falsely in their presence'
    },
    4: {  # Rohini
        'nakshatra': 'Rohini',
        'superpower': 'Manifestation',
        'archetype': 'The Creator',
        'ability': 'Thoughts manifest into reality unusually fast; creative visualization mastery',
        'specialty': 'Wish fulfillment, abundance attraction, beauty creation',
        'deity': 'Brahma (Creator)',
        'activation': 'During creative visualization or strong emotional desire'
    },
    5: {  # Mrigashira
        'nakshatra': 'Mrigashira',
        'superpower': 'Tracking',
        'archetype': 'The Seeker',
        'ability': 'Can find anything or anyone; psychic GPS for lost objects and people',
        'specialty': 'Finding lost items, tracking missing persons, dowsing',
        'deity': 'Soma (Moon God)',
        'activation': 'When searching for something with emotional attachment'
    },
    6: {  # Ardra
        'nakshatra': 'Ardra',
        'superpower': 'Storm Sensing',
        'archetype': 'The Tempest',
        'ability': 'Senses emotional and physical storms before they arrive; chaos intuition',
        'specialty': 'Weather prediction, emotional storm warning, transformation sensing',
        'deity': 'Rudra (Storm God)',
        'activation': 'Before major upheavals, storms, or emotional breakdowns'
    },
    7: {  # Punarvasu
        'nakshatra': 'Punarvasu',
        'superpower': 'Renewal Vision',
        'archetype': 'The Restorer',
        'ability': 'Can see how things will regenerate; knows what will return',
        'specialty': 'Recovery prediction, return sensing, renewal timing',
        'deity': 'Aditi (Mother of Gods)',
        'activation': 'After loss or destruction, seeing the path to restoration'
    },
    8: {  # Pushya
        'nakshatra': 'Pushya',
        'superpower': 'Nourishment Sensing',
        'archetype': 'The Nurturer',
        'ability': 'Knows exactly what someone needs to heal or grow; spiritual nutrition',
        'specialty': 'Healing prescriptions, growth guidance, what feeds the soul',
        'deity': 'Brihaspati (Jupiter)',
        'activation': 'When someone is depleted or seeking growth'
    },
    9: {  # Ashlesha
        'nakshatra': 'Ashlesha',
        'superpower': 'Hypnosis',
        'archetype': 'The Serpent',
        'ability': 'Can entrance others with gaze or voice; accesses the reptilian brain',
        'specialty': 'Mesmerism, kundalini sensing, accessing primal fears and desires',
        'deity': 'Nagas (Serpent Deities)',
        'activation': 'During deep eye contact or when speaking with intention'
    },
    10: {  # Magha
        'nakshatra': 'Magha',
        'superpower': 'Ancestral Communication',
        'archetype': 'The Throne Keeper',
        'ability': 'Direct line to ancestors; receives guidance from the departed',
        'specialty': 'Ancestor contact, royal lineage reading, inherited karma sensing',
        'deity': 'Pitris (Ancestors)',
        'activation': 'During rituals, at family gatherings, or near ancestral places'
    },
    11: {  # Purva Phalguni
        'nakshatra': 'Purva Phalguni',
        'superpower': 'Love Attraction',
        'archetype': 'The Enchanter',
        'ability': 'Can sense and attract romantic connections; love magnetism',
        'specialty': 'Matchmaking intuition, attraction sensing, pleasure prediction',
        'deity': 'Bhaga (God of Fortune)',
        'activation': 'In social situations or when focusing on someone romantically'
    },
    12: {  # Uttara Phalguni
        'nakshatra': 'Uttara Phalguni',
        'superpower': 'Contract Reading',
        'archetype': 'The Binder',
        'ability': 'Senses the truth behind agreements; knows if commitments will be kept',
        'specialty': 'Partnership intuition, promise sensing, loyalty detection',
        'deity': 'Aryaman (God of Contracts)',
        'activation': 'During negotiations, marriage discussions, or business deals'
    },
    13: {  # Hasta
        'nakshatra': 'Hasta',
        'superpower': 'Craft Mastery',
        'archetype': 'The Artisan',
        'ability': 'Hands carry healing and creative power; touch-based psychic ability',
        'specialty': 'Healing hands, psychic crafting, manual channeling',
        'deity': 'Savitar (Sun God)',
        'activation': 'When working with hands or touching someone intentionally'
    },
    14: {  # Chitra
        'nakshatra': 'Chitra',
        'superpower': 'Illusion Crafting',
        'archetype': 'The Architect',
        'ability': 'Can create and see through illusions; understands maya',
        'specialty': 'Glamour magic, illusion detection, reality architecture',
        'deity': 'Vishwakarma (Divine Architect)',
        'activation': 'When creating art or seeing through deception'
    },
    15: {  # Swati
        'nakshatra': 'Swati',
        'superpower': 'Wind Whispers',
        'archetype': 'The Independent',
        'ability': 'Receives messages through the wind; environmental psychic signals',
        'specialty': 'Air element communication, scattered thought gathering, independence sensing',
        'deity': 'Vayu (Wind God)',
        'activation': 'Outdoors in windy conditions or during scattered moments'
    },
    16: {  # Vishakha
        'nakshatra': 'Vishakha',
        'superpower': 'Goal Magnetism',
        'archetype': 'The Achiever',
        'ability': 'Can sense the path to any goal; psychic GPS for success',
        'specialty': 'Victory prediction, obstacle sensing, triumph timing',
        'deity': 'Indra-Agni',
        'activation': 'When intensely focused on a goal or ambition'
    },
    17: {  # Anuradha
        'nakshatra': 'Anuradha',
        'superpower': 'Devotion Sensing',
        'archetype': 'The Devotee',
        'ability': 'Can sense loyalty and devotion levels; knows true friends',
        'specialty': 'Friendship reading, devotion detection, group dynamics sensing',
        'deity': 'Mitra (God of Friendship)',
        'activation': 'In group settings or when evaluating relationships'
    },
    18: {  # Jyeshtha
        'nakshatra': 'Jyeshtha',
        'superpower': 'Power Detection',
        'archetype': 'The Elder',
        'ability': 'Can sense power dynamics and hierarchies; knows who really rules',
        'specialty': 'Authority sensing, power play detection, leadership reading',
        'deity': 'Indra (King of Gods)',
        'activation': 'In hierarchical situations or power struggles'
    },
    19: {  # Mula
        'nakshatra': 'Mula',
        'superpower': 'Root Cause Vision',
        'archetype': 'The Destroyer',
        'ability': 'Can see the root cause of any problem; gets to the bottom of everything',
        'specialty': 'Origin sensing, destruction prediction, foundational reading',
        'deity': 'Nirriti (Goddess of Destruction)',
        'activation': 'When investigating or during crisis situations'
    },
    20: {  # Purva Ashadha
        'nakshatra': 'Purva Ashadha',
        'superpower': 'Invincibility Sensing',
        'archetype': 'The Invincible',
        'ability': 'Knows when victory is certain; senses undefeatable moments',
        'specialty': 'Victory timing, invulnerability windows, triumph prediction',
        'deity': 'Apas (Water Deity)',
        'activation': 'Before battles, competitions, or confrontations'
    },
    21: {  # Uttara Ashadha
        'nakshatra': 'Uttara Ashadha',
        'superpower': 'Final Victory',
        'archetype': 'The Universal',
        'ability': 'Can sense ultimate outcomes; knows the final result of any endeavor',
        'specialty': 'End-game sensing, ultimate truth, final outcome prediction',
        'deity': 'Vishvadevas (Universal Gods)',
        'activation': 'When long-term outcomes need to be known'
    },
    22: {  # Shravana
        'nakshatra': 'Shravana',
        'superpower': 'Divine Hearing',
        'archetype': 'The Listener',
        'ability': 'Can hear what others cannot; receives divine messages through sound',
        'specialty': 'Clairaudience, sound sensitivity, message decoding',
        'deity': 'Vishnu (Preserver)',
        'activation': 'In silence or when listening intently to someone'
    },
    23: {  # Dhanishta
        'nakshatra': 'Dhanishta',
        'superpower': 'Wealth Sensing',
        'archetype': 'The Drummer',
        'ability': 'Can sense where wealth and abundance flow; prosperity intuition',
        'specialty': 'Money sensing, abundance timing, prosperity pathways',
        'deity': 'Vasus (Elemental Gods)',
        'activation': 'During financial decisions or opportunity evaluation'
    },
    24: {  # Shatabhisha
        'nakshatra': 'Shatabhisha',
        'superpower': 'Veiling/Unveiling',
        'archetype': 'The Mystic',
        'ability': 'Can hide in plain sight or reveal what is hidden; mystery mastery',
        'specialty': 'Secret detection, invisibility, revelation timing',
        'deity': 'Varuna (God of Cosmic Order)',
        'activation': 'When secrets need to be kept or exposed'
    },
    25: {  # Purva Bhadrapada
        'nakshatra': 'Purva Bhadrapada',
        'superpower': 'Fire Walking',
        'archetype': 'The Scorcher',
        'ability': 'Can transform through extreme experiences; crisis alchemy',
        'specialty': 'Transformation sensing, fire mastery, extreme situation navigation',
        'deity': 'Aja Ekapada (One-footed Goat)',
        'activation': 'During extreme stress or transformative crises'
    },
    26: {  # Uttara Bhadrapada
        'nakshatra': 'Uttara Bhadrapada',
        'superpower': 'Depth Diving',
        'archetype': 'The Depths',
        'ability': 'Can access the deepest unconscious; goes where others cannot',
        'specialty': 'Deep meditation, unconscious access, kundalini mastery',
        'deity': 'Ahir Budhnya (Serpent of the Deep)',
        'activation': 'In deep meditation or when facing the unconscious'
    },
    27: {  # Revati
        'nakshatra': 'Revati',
        'superpower': 'Safe Passage',
        'archetype': 'The Guide',
        'ability': 'Guides souls to safety; knows safe paths through any danger',
        'specialty': 'Journey protection, safe passage sensing, guardian intuition',
        'deity': 'Pushan (God of Safe Journeys)',
        'activation': 'During travel or when guiding others through transitions'
    }
}


# =============================================================================
# STEP 3: SIGNAL STRENGTH (Ketu House Position)
# =============================================================================

KETU_SIGNAL_STRENGTH = {
    1: {
        'house': 1,
        'title': 'The Natural',
        'intensity': 'Always On',
        'percentage': 95,
        'description': 'Born with the ability permanently activated. Cannot turn it off.',
        'manifestation': 'Identity is fused with psychic ability',
        'challenge': 'Difficulty knowing where they end and the ability begins',
        'gift': 'Effortless access; no activation needed',
        'symbol': '👁️'
    },
    2: {
        'house': 2,
        'title': 'The Voice',
        'intensity': 'Speech Activated',
        'percentage': 70,
        'description': 'Abilities activate through speech and voice.',
        'manifestation': 'Speaking truths they didn\'t consciously know',
        'challenge': 'Accidentally revealing secrets when speaking',
        'gift': 'Prophetic speech, especially about resources',
        'symbol': '🗣️'
    },
    3: {
        'house': 3,
        'title': 'The Messenger',
        'intensity': 'Communication Triggered',
        'percentage': 65,
        'description': 'Abilities activate during communication, writing, or with siblings.',
        'manifestation': 'Through writing, messages, and short journeys',
        'challenge': 'Information overload from too many signals',
        'gift': 'Automatic writing, channeled communication',
        'symbol': '✉️'
    },
    4: {
        'house': 4,
        'title': 'The Heart Knower',
        'intensity': 'Home Activated',
        'percentage': 85,
        'description': 'Deep internal peace and intuition. Strongest at home or in private.',
        'manifestation': 'Through emotional safety and domestic settings',
        'challenge': 'Ability weakens in public or unfamiliar places',
        'gift': 'Profound inner knowing, ancestral home connections',
        'symbol': '🏠'
    },
    5: {
        'house': 5,
        'title': 'The Oracle Child',
        'intensity': 'Creative Surge',
        'percentage': 75,
        'description': 'Abilities manifest through creativity, children, or playful states.',
        'manifestation': 'Through art, play, romance, and creative expression',
        'challenge': 'Must stay playful to access abilities',
        'gift': 'Prophetic creativity, children as messengers',
        'symbol': '🎭'
    },
    6: {
        'house': 6,
        'title': 'The Healer',
        'intensity': 'Service Activated',
        'percentage': 60,
        'description': 'Abilities activate through service, health work, or problem-solving.',
        'manifestation': 'Through helping others, especially with health',
        'challenge': 'May absorb others\' illnesses',
        'gift': 'Diagnostic intuition, healing through service',
        'symbol': '⚕️'
    },
    7: {
        'house': 7,
        'title': 'The Mirror',
        'intensity': 'Partnership Triggered',
        'percentage': 70,
        'description': 'Abilities activate through relationships and partnerships.',
        'manifestation': 'Through close one-on-one connections',
        'challenge': 'Needs a partner to fully activate abilities',
        'gift': 'Reading partners deeply, relationship prophecy',
        'symbol': '🪞'
    },
    8: {
        'house': 8,
        'title': 'The Occultist',
        'intensity': 'Crisis Activated',
        'percentage': 90,
        'description': 'Talking to the dead, dark mysteries. Strongest during crisis and transformation.',
        'manifestation': 'Through death, sex, crisis, and transformation',
        'challenge': 'May be drawn to dangerous situations to activate',
        'gift': 'Mediumship, past life access, occult mastery',
        'symbol': '💀'
    },
    9: {
        'house': 9,
        'title': 'The Sage',
        'intensity': 'Wisdom Triggered',
        'percentage': 75,
        'description': 'Abilities activate through teaching, travel, or philosophical inquiry.',
        'manifestation': 'Through higher learning, foreign lands, and dharma',
        'challenge': 'May seem preachy or self-righteous about visions',
        'gift': 'Prophetic teaching, guru-level intuition',
        'symbol': '📚'
    },
    10: {
        'house': 10,
        'title': 'The Public Oracle',
        'intensity': 'Career Activated',
        'percentage': 80,
        'description': 'Abilities manifest through career and public life.',
        'manifestation': 'Through professional settings and public roles',
        'challenge': 'Cannot hide abilities; always publicly visible',
        'gift': 'Professional psychic, public prophecy',
        'symbol': '🏛️'
    },
    11: {
        'house': 11,
        'title': 'The Network',
        'intensity': 'Group Activated',
        'percentage': 70,
        'description': 'Abilities activate in groups, networks, and for collective causes.',
        'manifestation': 'Through friendships, organizations, and dreams',
        'challenge': 'May lose individual signal in group noise',
        'gift': 'Collective prophecy, group mind access',
        'symbol': '🌐'
    },
    12: {
        'house': 12,
        'title': 'The Dreamwalker',
        'intensity': 'Sleep/Meditation Activated',
        'percentage': 95,
        'description': 'Prophetic dreams, sleep learning. Strongest in altered states.',
        'manifestation': 'Through dreams, meditation, and isolation',
        'challenge': 'Abilities may not work while fully awake',
        'gift': 'Dream prophecy, astral travel, moksha intuition',
        'symbol': '🌙'
    }
}


# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def get_moon_longitude(jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """Get sidereal longitude of Moon."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
    return pos[0][0]


def get_ketu_longitude(jd: float, ayanamsa: str = 'LAHIRI') -> float:
    """Get sidereal longitude of Ketu (180° from Rahu)."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE, swe.FLG_SIDEREAL)
    return (rahu_pos[0][0] + 180) % 360


def get_ascendant(jd: float, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> float:
    """Get sidereal ascendant."""
    if ayanamsa.upper() == 'LAHIRI':
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    houses = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    return houses[1][0]


def get_house_from_longitude(planet_long: float, asc_long: float) -> int:
    """Calculate house number (1-12) from planet longitude and ascendant."""
    # House 1 starts from ascendant
    distance = (planet_long - asc_long) % 360
    house = int(distance / 30) + 1
    return house


def get_nakshatra_number(longitude: float) -> int:
    """Get nakshatra number (1-27) from longitude."""
    return int(longitude / (360 / 27)) + 1


def get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign name from longitude."""
    return SIGNS[int(longitude / 30)]


def get_element_from_sign(sign: str) -> str:
    """Get element from zodiac sign."""
    return SIGN_ELEMENTS.get(sign, 'Fire')


# =============================================================================
# PSYCHIC CHANNEL (Step 1)
# =============================================================================

def get_psychic_channel(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Step 1: Determine the Psychic Channel from Moon's element.
    
    The zodiac element of the Moon dictates the mechanism of their intuition.
    """
    jd = datetime_to_jd(dt)
    moon_long = get_moon_longitude(jd, ayanamsa)
    moon_sign = get_sign_from_longitude(moon_long)
    moon_element = get_element_from_sign(moon_sign)
    
    channel = PSYCHIC_CHANNELS[moon_element]
    
    return {
        'moon_longitude': round(moon_long, 4),
        'moon_sign': moon_sign,
        'element': moon_element,
        'channel_name': channel['name'],
        'channel_short': channel['short'],
        'definition': channel['definition'],
        'mechanism': channel['mechanism'],
        'strengths': channel['strengths'],
        'weaknesses': channel['weaknesses'],
        'symbol': channel['symbol'],
        'color': channel['color']
    }


# =============================================================================
# SUPERPOWER (Step 2)
# =============================================================================

def get_superpower(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Step 2: Determine the Superpower from Moon's Nakshatra.
    
    Each of the 27 Nakshatras maps to a specific psychic archetype.
    """
    jd = datetime_to_jd(dt)
    moon_long = get_moon_longitude(jd, ayanamsa)
    nakshatra_num = get_nakshatra_number(moon_long)
    
    power = NAKSHATRA_SUPERPOWERS[nakshatra_num]
    
    return {
        'moon_longitude': round(moon_long, 4),
        'nakshatra_number': nakshatra_num,
        'nakshatra_name': power['nakshatra'],
        'superpower': power['superpower'],
        'archetype': power['archetype'],
        'ability': power['ability'],
        'specialty': power['specialty'],
        'deity': power['deity'],
        'activation': power['activation']
    }


# =============================================================================
# SIGNAL STRENGTH (Step 3)
# =============================================================================

def get_signal_strength(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Step 3: Determine Signal Strength from Ketu's house position.
    
    Ketu is the Karaka (significator) of liberation and psychic ability.
    Its house placement determines where the ability manifests best.
    """
    jd = datetime_to_jd(dt)
    ketu_long = get_ketu_longitude(jd, ayanamsa)
    asc_long = get_ascendant(jd, lat, lon, ayanamsa)
    ketu_house = get_house_from_longitude(ketu_long, asc_long)
    
    strength = KETU_SIGNAL_STRENGTH[ketu_house]
    
    return {
        'ketu_longitude': round(ketu_long, 4),
        'ketu_house': ketu_house,
        'title': strength['title'],
        'intensity': strength['intensity'],
        'percentage': strength['percentage'],
        'description': strength['description'],
        'manifestation': strength['manifestation'],
        'challenge': strength['challenge'],
        'gift': strength['gift'],
        'symbol': strength['symbol']
    }


# =============================================================================
# FULL PSYCHIC PROFILE
# =============================================================================

def get_psychic_profile(dt: datetime, lat: float, lon: float, ayanamsa: str = 'LAHIRI') -> Dict[str, Any]:
    """
    Generate complete Psychic Profile using the 3-step formula:
    
    1. Channel (Moon Element) - How they receive psychic information
    2. Superpower (Nakshatra) - What specific ability they have
    3. Signal Strength (Ketu House) - Intensity and activation conditions
    
    Returns a complete psychic profile with all components.
    """
    channel = get_psychic_channel(dt, lat, lon, ayanamsa)
    superpower = get_superpower(dt, lat, lon, ayanamsa)
    signal = get_signal_strength(dt, lat, lon, ayanamsa)
    
    # Calculate overall psychic potency (average of factors)
    base_potency = signal['percentage']
    
    # Boost for water moons (natural psychics)
    if channel['element'] == 'Water':
        potency_boost = 10
    elif channel['element'] == 'Fire':
        potency_boost = 5
    else:
        potency_boost = 0
    
    # Boost for key nakshatras (Ashlesha, Mula, Revati are traditionally psychic)
    psychic_nakshatras = [9, 19, 27]  # Ashlesha, Mula, Revati
    if superpower['nakshatra_number'] in psychic_nakshatras:
        potency_boost += 10
    
    overall_potency = min(100, base_potency + potency_boost)
    
    # Generate the profile title
    profile_title = f"{channel['channel_short']} {superpower['archetype']}"
    
    # Generate the profile description
    profile_description = (
        f"A {channel['channel_name']} psychic with the gift of {superpower['superpower']}. "
        f"{signal['description']} "
        f"Their ability activates {superpower['activation'].lower()}."
    )
    
    return {
        'title': profile_title,
        'description': profile_description,
        'overall_potency': overall_potency,
        'potency_level': _get_potency_level(overall_potency),
        
        # The 3 Components
        'channel': channel,
        'superpower': superpower,
        'signal_strength': signal,
        
        # Combined Insights
        'how_it_works': f"Through {channel['mechanism'].lower()}, {superpower['ability'].lower()}",
        'best_use': superpower['specialty'],
        'activation_trigger': superpower['activation'],
        'manifestation': signal['manifestation'],
        'main_challenge': f"{channel['weaknesses'][0]}; {signal['challenge']}",
        'main_gift': f"{superpower['superpower']} ({signal['gift']})",
        
        # Symbols
        'symbols': f"{channel['symbol']} {signal['symbol']}",
        'color': channel['color']
    }


def _get_potency_level(percentage: int) -> str:
    """Convert percentage to descriptive level."""
    if percentage >= 90:
        return "Extremely High (Master Level)"
    elif percentage >= 80:
        return "Very High (Adept Level)"
    elif percentage >= 70:
        return "High (Practitioner Level)"
    elif percentage >= 60:
        return "Moderate (Developing)"
    elif percentage >= 50:
        return "Moderate (Latent)"
    else:
        return "Low (Dormant)"


def get_psychic_compatibility(profile1: Dict, profile2: Dict) -> Dict[str, Any]:
    """
    Check psychic compatibility between two profiles.
    
    Determines if two psychics would work well together.
    """
    # Element compatibility
    element_compat = {
        ('Water', 'Water'): 95,  # Deep emotional connection
        ('Water', 'Earth'): 85,  # Grounding meets feeling
        ('Water', 'Fire'): 50,   # Steam - intense but unstable
        ('Water', 'Air'): 60,    # Mist - confusion possible
        ('Fire', 'Fire'): 80,    # Power duo
        ('Fire', 'Air'): 90,     # Fuels each other
        ('Fire', 'Earth'): 55,   # Frustration possible
        ('Air', 'Air'): 85,      # Mental synergy
        ('Air', 'Earth'): 60,    # Different wavelengths
        ('Earth', 'Earth'): 90,  # Stable and grounded
    }
    
    elem1 = profile1['channel']['element']
    elem2 = profile2['channel']['element']
    
    # Get compatibility (order doesn't matter)
    key = tuple(sorted([elem1, elem2]))
    compat_score = element_compat.get(key, 70)
    
    # Check if superpowers complement
    complementary = False
    if 'Heal' in profile1['superpower']['superpower'] or 'Heal' in profile2['superpower']['superpower']:
        complementary = True
        compat_score += 5
    
    return {
        'compatibility_score': min(100, compat_score),
        'element_match': f"{elem1} + {elem2}",
        'complementary_powers': complementary,
        'combined_title': f"{profile1['title']} & {profile2['title']}",
        'synergy': 'High' if compat_score >= 80 else 'Moderate' if compat_score >= 60 else 'Challenging'
    }


def get_psychic_profile_summary(dt: datetime, lat: float, lon: float, name: str = "Native", ayanamsa: str = 'LAHIRI') -> str:
    """
    Generate a formatted text summary of the psychic profile.
    """
    profile = get_psychic_profile(dt, lat, lon, ayanamsa)
    
    summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              PSYCHIC PROFILE: {name.upper():<28} ║
╠══════════════════════════════════════════════════════════════╣
║  Title: {profile['title']:<51} ║
║  Potency: {profile['overall_potency']}% - {profile['potency_level']:<36} ║
╠══════════════════════════════════════════════════════════════╣
║  CHANNEL: {profile['channel']['channel_name']:<49} ║
║  Element: {profile['channel']['element']:<49} ║
║  "{profile['channel']['definition'][:55]:<55}" ║
╠══════════════════════════════════════════════════════════════╣
║  SUPERPOWER: {profile['superpower']['superpower']:<46} ║
║  Archetype: {profile['superpower']['archetype']:<47} ║
║  Nakshatra: {profile['superpower']['nakshatra_name']:<47} ║
╠══════════════════════════════════════════════════════════════╣
║  SIGNAL: {profile['signal_strength']['title']:<50} ║
║  Ketu House: {profile['signal_strength']['ketu_house']:<46} ║
║  Intensity: {profile['signal_strength']['intensity']:<47} ║
╠══════════════════════════════════════════════════════════════╣
║  Symbols: {profile['symbols']:<49} ║
║  Color: {profile['color']:<51} ║
╚══════════════════════════════════════════════════════════════╝
"""
    return summary
