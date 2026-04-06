"""
Muhurtha (Electional Astrology) Module

Provides auspicious timing calculations for daily activities and life events.
For daily predictions, this module determines favorable/unfavorable times
based on Tithi, Nakshatra, Weekday, and Hora.

Reference: Library/Logic/Calculate/Muhurtha.cs (10,853 lines in VedAstro C#)
"""

import math
from datetime import datetime, time as dt_time, timedelta
from typing import Dict, List, Tuple
from logic.panchang import get_tithi, get_yoga, TITHIS, YOGA_DATA
from logic.nakshatra import NAKSHATRAS, TARAS, get_nakshatra
from logic.consts import Planet
from logic.house_queries import get_planet_house, get_planets_in_house, get_lagna_sign_num
from logic.calculate import get_planet_longitude
from logic.time import AstroTime
from logic.rasi import get_rasi
from logic.ashtakavarga import get_all_bhinnashtakavarga
from logic.dasa import get_vimshottari_dasa, get_vimshottari_dasa_schedule
from logic.lordship import get_lord_of_house
from logic.shadbala import get_all_planet_shadbala, get_bhava_bala

# ==================== TITHI CLASSIFICATIONS ====================

# Nanda Tithis (Auspicious for Marriages, Religious ceremonies)
NANDA_TITHIS = [1, 6, 11]  # Pratipada, Shashthi, Ekadashi

# Bhadra Tithis (Auspicious for stable/permanent activities)
BHADRA_TITHIS = [2, 7, 12]  # Dwitiya, Saptami, Dwadashi

# Jaya Tithis (Victory, Success-oriented activities)
JAYA_TITHIS = [3, 8, 13]  # Tritiya, Ashtami, Trayodashi

# Rikta Tithis (Inauspicious - Empty/Hollow - Avoid important work)
RIKTA_TITHIS = [4, 9, 14]  # Chaturthi, Navami, Chaturdashi

# Purna Tithis (Full/Complete - Very auspicious)
PURNA_TITHIS = [5, 10, 15]  # Panchami, Dashami, Purnima/Amavasya

# Specific Tithi recommendations
TRAVEL_FAVORABLE_TITHIS = [2, 3, 5, 7, 10, 11, 12, 13]  # Bhadra, Jaya, Purna
MARRIAGE_FAVORABLE_TITHIS = [2, 3, 5, 7, 10, 11, 12, 13]  # Avoid Rikta
BUSINESS_FAVORABLE_TITHIS = [2, 3, 5, 6, 7, 10, 11, 12, 13]
MEDICAL_FAVORABLE_TITHIS = [3, 5, 7, 10, 12, 13]  # Jaya and stable tithis

# Tithis to AVOID for important activities
INAUSPICIOUS_TITHIS = [4, 6, 8, 9, 14, 30]  # Rikta + Ashtami + Amavasya


# ==================== NAKSHATRA CLASSIFICATIONS ====================

# Good for Travel (Safe, prosperous journeys)
TRAVEL_FAVORABLE_NAKSHATRAS = [
    "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", 
    "Hasta", "Chitra", "Swati", "Anuradha", "Shravana", "Revati"
]

# Good for Marriage (Love, harmony, stability)
MARRIAGE_FAVORABLE_NAKSHATRAS = [
    "Rohini", "Mrigashira", "Uttara Phalguni", "Hasta", "Swati", 
    "Anuradha", "Uttara Ashadha", "Uttara Bhadrapada", "Revati"
]

# Good for Business/Financial activities
BUSINESS_FAVORABLE_NAKSHATRAS = [
    "Ashwini", "Rohini", "Punarvasu", "Pushya", "Uttara Phalguni", 
    "Hasta", "Chitra", "Swati", "Anuradha", "Shravana", "Revati"
]

# Good for Medical/Healing activities
MEDICAL_FAVORABLE_NAKSHATRAS = [
    "Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya", 
    "Hasta", "Anuradha", "Revati"
]

# Good for Education/Learning
EDUCATION_FAVORABLE_NAKSHATRAS = [
    "Ashwini", "Rohini", "Punarvasu", "Pushya", "Hasta", 
    "Chitra", "Swati", "Shravana", "Revati"
]

# Good for Spiritual/Religious activities
SPIRITUAL_FAVORABLE_NAKSHATRAS = [
    "Rohini", "Punarvasu", "Pushya", "Uttara Phalguni", "Hasta", 
    "Anuradha", "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati"
]

# Inauspicious Nakshatras (Avoid important activities)
INAUSPICIOUS_NAKSHATRAS = [
    "Bharani", "Ardra", "Ashlesha", "Magha", "Mula", "Jyeshtha"
]


# ==================== WEEKDAY RECOMMENDATIONS ====================

# Planetary Rulers of each day
WEEKDAY_RULERS = {
    0: "Sun",      # Monday
    1: "Moon",     # Tuesday  
    2: "Mars",     # Wednesday
    3: "Mercury",  # Thursday
    4: "Jupiter",  # Friday
    5: "Venus",    # Saturday
    6: "Saturn"    # Sunday
}

# Activity recommendations per weekday
WEEKDAY_ACTIVITIES = {
    0: {  # Sunday (Sun)
        "favorable": ["Government work", "Leadership activities", "Father-related matters", "Spiritual practices", "Health checkups"],
        "unfavorable": ["Financial transactions", "Starting new partnerships"]
    },
    1: {  # Monday (Moon)
        "favorable": ["Travel", "Water-related activities", "Mother-related matters", "Emotional healing", "Real estate", "Buying vehicles"],
        "unfavorable": ["Surgery", "Lending money", "Legal battles"]
    },
    2: {  # Tuesday (Mars)
        "favorable": ["Sports", "Physical activities", "Surgery", "Legal matters", "Property disputes", "Military activities"],
        "unfavorable": ["Marriage", "Peace negotiations", "Starting education"]
    },
    3: {  # Wednesday (Mercury)
        "favorable": ["Business", "Education", "Communication", "Writing", "Signing contracts", "Buying electronics"],
        "unfavorable": ["Surgery", "Confrontations"]
    },
    4: {  # Thursday (Jupiter)
        "favorable": ["Education", "Religious ceremonies", "Marriage", "Buying property", "Starting new ventures", "Spiritual practices"],
        "unfavorable": ["Legal disputes", "Unethical activities"]
    },
    5: {  # Friday (Venus)
        "favorable": ["Marriage", "Romance", "Arts", "Fashion", "Beauty treatments", "Buying jewelry", "Social events"],
        "unfavorable": ["Surgery", "Harsh decisions", "Battles"]
    },
    6: {  # Saturday (Saturn)
        "favorable": ["Long-term planning", "Labor work", "Agriculture", "Construction", "Dealing with elderly", "Discipline"],
        "unfavorable": ["Marriage", "Celebrations", "Starting joyful activities"]
    }
}


# ==================== ACTIVITY CATEGORIES ====================

ACTIVITY_CATEGORIES = {
    "travel": {
        "name": "Travel & Journeys",
        "favorable_tithis": TRAVEL_FAVORABLE_TITHIS,
        "favorable_nakshatras": TRAVEL_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [1, 3, 4, 5],  # Monday, Wednesday, Thursday, Friday
        "avoid_yogas": ["Vishkumbha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vyatipata", "Parigha", "Vaidhriti"]
    },
    "marriage": {
        "name": "Marriage & Engagements",
        "favorable_tithis": MARRIAGE_FAVORABLE_TITHIS,
        "favorable_nakshatras": MARRIAGE_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [1, 3, 4, 5],  # Monday, Wednesday, Thursday, Friday
        "avoid_yogas": ["Vishkumbha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vyatipata", "Parigha", "Vaidhriti"]
    },
    "business": {
        "name": "Business & Financial",
        "favorable_tithis": BUSINESS_FAVORABLE_TITHIS,
        "favorable_nakshatras": BUSINESS_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [3, 4, 5],  # Wednesday, Thursday, Friday
        "avoid_yogas": ["Vishkumbha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Parigha", "Vaidhriti"]
    },
    "medical": {
        "name": "Medical & Health",
        "favorable_tithis": MEDICAL_FAVORABLE_TITHIS,
        "favorable_nakshatras": MEDICAL_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [0, 1, 4],  # Sunday, Monday, Thursday
        "avoid_yogas": ["Atiganda", "Shula", "Ganda", "Vyaghata", "Vyatipata", "Parigha", "Vaidhriti"]
    },
    "education": {
        "name": "Education & Learning",
        "favorable_tithis": [2, 3, 5, 7, 10, 11, 12],
        "favorable_nakshatras": EDUCATION_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [3, 4],  # Wednesday, Thursday
        "avoid_yogas": ["Vishkumbha", "Atiganda", "Vyaghata", "Parigha", "Vaidhriti"]
    },
    "spiritual": {
        "name": "Spiritual & Religious",
        "favorable_tithis": [1, 5, 8, 11, 14, 15, 30],  # Include Ashtami, Ekadashi, Purnima, Amavasya
        "favorable_nakshatras": SPIRITUAL_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [0, 1, 4],  # Sunday, Monday, Thursday
        "avoid_yogas": []  # Most yogas are ok for spiritual activities
    },
    "general": {
        "name": "General Activities",
        "favorable_tithis": TRAVEL_FAVORABLE_TITHIS,  # Use travel as baseline
        "favorable_nakshatras": TRAVEL_FAVORABLE_NAKSHATRAS,
        "favorable_weekdays": [0, 1, 3, 4, 5],  # All except Tuesday, Saturday
        "avoid_yogas": ["Vishkumbha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vyatipata", "Parigha", "Vaidhriti"]
    }
}


# ==================== MAIN FUNCTIONS ====================

def evaluate_muhurtha(
    sun_long: float,
    moon_long: float,
    moon_nakshatra: str,
    weekday: int,
    activity_type: str = "general"
) -> Dict:
    """
    Evaluates the auspiciousness of a moment for a specific activity.
    
    Args:
        sun_long: Sun longitude in degrees
        moon_long: Moon longitude in degrees
        moon_nakshatra: Current Moon nakshatra name
        weekday: Day of week (0=Sunday, 6=Saturday)
        activity_type: One of: travel, marriage, business, medical, education, spiritual, general
    
    Returns:
        Dictionary with auspiciousness score and recommendations
    """
    # Get current panchang
    tithi_name, tithi_num, tithi_percent = get_tithi(sun_long, moon_long)
    yoga_name, yoga_num = get_yoga(sun_long, moon_long)
    
    # Get activity criteria
    activity = ACTIVITY_CATEGORIES.get(activity_type, ACTIVITY_CATEGORIES["general"])
    
    # Score calculation (0-100)
    score = 0
    reasons_good = []
    reasons_bad = []
    
    # 1. Tithi Check (30 points)
    tithi_index = (tithi_num - 1) % 15 + 1  # Convert to 1-15 scale
    if tithi_index in activity["favorable_tithis"]:
        score += 30
        reasons_good.append(f"Favorable Tithi: {tithi_name}")
    elif tithi_num in INAUSPICIOUS_TITHIS:
        score -= 20
        reasons_bad.append(f"Inauspicious Tithi: {tithi_name}")
    else:
        score += 10
        
    # 2. Nakshatra Check (30 points)
    if moon_nakshatra in activity["favorable_nakshatras"]:
        score += 30
        reasons_good.append(f"Favorable Nakshatra: {moon_nakshatra}")
    elif moon_nakshatra in INAUSPICIOUS_NAKSHATRAS:
        score -= 20
        reasons_bad.append(f"Inauspicious Nakshatra: {moon_nakshatra}")
    else:
        score += 10
        
    # 3. Yoga Check (20 points)
    yoga_nature = next((y[2] for y in YOGA_DATA if y[0] == yoga_name), "Mishra")
    if yoga_name in activity.get("avoid_yogas", []):
        score -= 15
        reasons_bad.append(f"Unfavorable Yoga: {yoga_name}")
    elif yoga_nature == "Shubha":
        score += 20
        reasons_good.append(f"Auspicious Yoga: {yoga_name}")
    elif yoga_nature == "Ashubha":
        score -= 10
        reasons_bad.append(f"Inauspicious Yoga: {yoga_name}")
    else:
        score += 5
        
    # 4. Weekday Check (20 points)
    if weekday in activity["favorable_weekdays"]:
        score += 20
        weekday_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        reasons_good.append(f"Favorable Day: {weekday_names[weekday]}")
    else:
        score += 5
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    # Determine overall recommendation
    if score >= 70:
        recommendation = "Highly Auspicious"
        emoji = "✅"
    elif score >= 50:
        recommendation = "Moderately Auspicious"
        emoji = "👍"
    elif score >= 30:
        recommendation = "Neutral"
        emoji = "⚪"
    else:
        recommendation = "Inauspicious"
        emoji = "⚠️"
    
    return {
        "activity": activity["name"],
        "score": score,
        "recommendation": recommendation,
        "emoji": emoji,
        "reasons_good": reasons_good,
        "reasons_bad": reasons_bad,
        "panchang": {
            "tithi": tithi_name,
            "nakshatra": moon_nakshatra,
            "yoga": yoga_name,
            "weekday": weekday
        }
    }


def get_daily_activity_recommendations(
    sun_long: float,
    moon_long: float,
    moon_nakshatra: str,
    weekday: int
) -> Dict[str, Dict]:
    """
    Get recommendations for all activity types for a given day.
    
    Returns:
        Dictionary with activity types as keys and evaluation results as values
    """
    recommendations = {}
    
    for activity_type in ACTIVITY_CATEGORIES.keys():
        recommendations[activity_type] = evaluate_muhurtha(
            sun_long, moon_long, moon_nakshatra, weekday, activity_type
        )
    
    return recommendations


def get_best_activities_for_day(
    sun_long: float,
    moon_long: float,
    moon_nakshatra: str,
    weekday: int,
    threshold: int = 50
) -> List[Dict]:
    """
    Get list of activities that are favorable (score >= threshold) for the day.
    
    Args:
        threshold: Minimum score to consider activity favorable (default 50)
    
    Returns:
        List of favorable activities sorted by score (highest first)
    """
    all_activities = get_daily_activity_recommendations(
        sun_long, moon_long, moon_nakshatra, weekday
    )
    
    favorable = [
        {
            "activity": act_data["activity"],
            "score": act_data["score"],
            "recommendation": act_data["recommendation"]
        }
        for act_type, act_data in all_activities.items()
        if act_data["score"] >= threshold
    ]
    
    # Sort by score descending
    favorable.sort(key=lambda x: x["score"], reverse=True)
    
    return favorable


def get_activities_to_avoid(
    sun_long: float,
    moon_long: float,
    moon_nakshatra: str,
    weekday: int,
    threshold: int = 30
) -> List[Dict]:
    """
    Get list of activities that should be avoided (score < threshold) for the day.
    
    Args:
        threshold: Maximum score to consider activity unfavorable (default 30)
    
    Returns:
        List of unfavorable activities sorted by score (lowest first)
    """
    all_activities = get_daily_activity_recommendations(
        sun_long, moon_long, moon_nakshatra, weekday
    )
    
    unfavorable = [
        {
            "activity": act_data["activity"],
            "score": act_data["score"],
            "recommendation": act_data["recommendation"]
        }
        for act_type, act_data in all_activities.items()
        if act_data["score"] < threshold
    ]
    
    # Sort by score ascending (worst first)
    unfavorable.sort(key=lambda x: x["score"])
    
    return unfavorable


def get_day_quality_summary(
    sun_long: float,
    moon_long: float,
    moon_nakshatra: str,
    weekday: int
) -> Dict:
    """
    Get overall quality assessment of the day across all activities.
    
    Returns:
        Summary with average score, best/worst activities, and general advice
    """
    all_activities = get_daily_activity_recommendations(
        sun_long, moon_long, moon_nakshatra, weekday
    )
    
    scores = [act["score"] for act in all_activities.values()]
    avg_score = sum(scores) / len(scores)
    
    # Find best and worst activities
    activities_list = [
        (act_type, act_data["score"], act_data["activity"])
        for act_type, act_data in all_activities.items()
    ]
    activities_list.sort(key=lambda x: x[1], reverse=True)
    
    best_activity = activities_list[0]
    worst_activity = activities_list[-1]
    
    # Overall day quality
    if avg_score >= 70:
        day_quality = "Excellent Day"
        advice = "This is a highly auspicious day. Most activities will be favorable."
    elif avg_score >= 50:
        day_quality = "Good Day"
        advice = "This is a moderately auspicious day. Choose activities wisely."
    elif avg_score >= 30:
        day_quality = "Average Day"
        advice = "This is a neutral day. Be cautious with important decisions."
    else:
        day_quality = "Challenging Day"
        advice = "This is an inauspicious day. Avoid starting new ventures."
    
    # Get panchang details
    tithi_name, tithi_num, tithi_percent = get_tithi(sun_long, moon_long)
    yoga_name, yoga_num = get_yoga(sun_long, moon_long)
    
    return {
        "overall_score": round(avg_score, 1),
        "day_quality": day_quality,
        "advice": advice,
        "best_for": best_activity[2],
        "avoid": worst_activity[2],
        "panchang": {
            "tithi": tithi_name,
            "nakshatra": moon_nakshatra,
            "yoga": yoga_name
        },
        "all_scores": {act[2]: act[1] for act in activities_list}
    }


# ==================== CONVENIENCE FUNCTIONS ====================

def is_auspicious_for_travel(tithi_num: int, nakshatra: str) -> bool:
    """Quick check if day is good for travel."""
    tithi_ok = (tithi_num - 1) % 15 + 1 in TRAVEL_FAVORABLE_TITHIS
    nakshatra_ok = nakshatra in TRAVEL_FAVORABLE_NAKSHATRAS
    return tithi_ok and nakshatra_ok


def is_auspicious_for_marriage(tithi_num: int, nakshatra: str) -> bool:
    """Quick check if day is good for marriage."""
    tithi_ok = (tithi_num - 1) % 15 + 1 in MARRIAGE_FAVORABLE_TITHIS
    nakshatra_ok = nakshatra in MARRIAGE_FAVORABLE_NAKSHATRAS
    return tithi_ok and nakshatra_ok


def get_weekday_lord_activities(weekday: int) -> Dict:
    """Get favorable and unfavorable activities for a specific weekday."""
    return WEEKDAY_ACTIVITIES.get(weekday, WEEKDAY_ACTIVITIES[0])


# =============================================================================
# CHANDRABALA — Moon Strength for Transit
# =============================================================================
# Ported from Core.cs ~line 2380
#
# Count from birth Moon sign to transit Moon sign (Vedic inclusive counting).
# Result positions 1,3,6,7,10,11 = Good (Bala); all others = Bad.

_CHANDRABALA_GOOD_POSITIONS = {1, 3, 6, 7, 10, 11}

def get_chandrabala(birth_moon_sign_num: int, transit_moon_sign_num: int) -> Dict:
    """
    Calculates Chandrabala (Moon's strength) for choosing auspicious times.

    Args:
        birth_moon_sign_num:   Janma Rasi — Moon sign number at birth (1-12).
        transit_moon_sign_num: Current/transit Moon sign number (1-12).

    Returns:
        {
            "position":    int  (1-12, Vedic inclusive count),
            "is_good":     bool,
            "description": str
        }

    Ported from Core.cs, VedAstro C# library.
    """
    # Vedic inclusive count: same sign = position 1
    diff = (transit_moon_sign_num - birth_moon_sign_num) % 12
    position = diff + 1  # 1-12

    is_good = position in _CHANDRABALA_GOOD_POSITIONS

    if is_good:
        description = f"Chandrabala is good (position {position}). Auspicious for activities."
    else:
        description = f"Chandrabala is weak (position {position}). Avoid important new beginnings."

    return {
        "position": position,
        "is_good": is_good,
        "description": description,
    }


# =============================================================================
# PANCHAKA — Five-fold danger classification
# =============================================================================
# Ported from Core.cs Panchaka logic
#
# total = lunar_day_num + nakshatra_num + weekday_num + lagna_sign_num
# remainder = total % 9
# 0=Shubha, 1=Mrityu, 2=Agni, 3=Shubha, 4=Raja, 5=Shubha, 6=Chora, 7=Shubha, 8=Roga

_PANCHAKA_MAP: Dict[int, str] = {
    0: "Shubha",
    1: "Mrityu",   # Death — avoid
    2: "Agni",     # Fire/destruction — avoid
    3: "Shubha",   # Auspicious
    4: "Raja",     # Royal/powerful — generally ok
    5: "Shubha",   # Auspicious
    6: "Chora",    # Theft/deceit — avoid
    7: "Shubha",   # Auspicious
    8: "Roga",     # Disease — avoid
}

_PANCHAKA_IS_BAD = {"Mrityu", "Agni", "Chora", "Roga"}

# Weekday numbers per Vedic system: Sunday=1, Monday=2, ... Saturday=7
# Python weekday(): Monday=0 → Vedic Sunday=1 offset
def _python_weekday_to_vedic(python_weekday: int) -> int:
    """Convert Python weekday (Mon=0…Sun=6) to Vedic day number (Sun=1…Sat=7)."""
    return (python_weekday + 1) % 7 + 1  # Sun=1, Mon=2, Tue=3, … Sat=7


def get_panchaka(
    lunar_day_num: int,
    nakshatra_num: int,
    python_weekday: int,
    lagna_sign_num: int,
) -> Dict:
    """
    Calculates Panchaka Dosha for a given moment.

    Args:
        lunar_day_num:   Tithi number 1-30.
        nakshatra_num:   Moon nakshatra number 1-27.
        python_weekday:  Python weekday (Monday=0 … Sunday=6).
        lagna_sign_num:  Lagna (Ascendant) sign number 1-12.

    Returns:
        {
            "total":       int,
            "remainder":   int  (0-8),
            "panchaka":    str  (e.g. 'Shubha', 'Mrityu', ...),
            "is_dosha":    bool (True when inauspicious),
            "description": str
        }

    Ported from Core.cs Panchaka function.
    """
    vedic_weekday = _python_weekday_to_vedic(python_weekday)
    total = lunar_day_num + nakshatra_num + vedic_weekday + lagna_sign_num
    remainder = total % 9
    panchaka_name = _PANCHAKA_MAP[remainder]
    is_dosha = panchaka_name in _PANCHAKA_IS_BAD

    _DESCRIPTIONS = {
        "Mrityu": "Mrityu Panchaka — danger to life. Avoid travel, surgery, and risky activities.",
        "Agni":   "Agni Panchaka — risk of fire and accidents. Avoid use of fire and electricity.",
        "Raja":   "Raja Panchaka — mild caution. Fine for most activities; avoid legal disputes.",
        "Chora":  "Chora Panchaka — risk of theft or betrayal. Safeguard valuables.",
        "Roga":   "Roga Panchaka — risk of illness. Avoid exposure and maintain hygiene.",
        "Shubha": "Shubha — no Panchaka Dosha. Moment is free of this particular blemish.",
    }

    return {
        "total": total,
        "remainder": remainder,
        "panchaka": panchaka_name,
        "is_dosha": is_dosha,
        "description": _DESCRIPTIONS[panchaka_name],
    }


# =============================================================================
# GHATAKA CHAKRA — Inauspicious sign/time combinations keyed to birth Moon sign
# =============================================================================
# Ported from Core.cs lines 1784-1822
#
# For each birth Moon sign, five inauspicious markers are defined:
#   (ghataka_moon_sign, tithi_group, weekday_name, moon_nakshatra, ghataka_lagna)
#
# If ANY of the five matches the current moment, it is a Ghataka period.

_GHATAKA_TABLE: Dict[str, tuple] = {
    # birth_moon_sign: (ghataka_moon_sign, tithi_group, weekday, moon_nakshatra, ghataka_lagna)
    "Aries":       ("Aries",       "Nanda",  "Sunday",    "Magha",      "Aries"),
    "Taurus":      ("Virgo",       "Purna",  "Saturday",  "Hasta",      "Taurus"),
    "Gemini":      ("Aquarius",    "Bhadra", "Monday",    "Swati",      "Cancer"),
    "Cancer":      ("Leo",         "Bhadra", "Wednesday", "Anuradha",   "Libra"),
    "Leo":         ("Capricorn",   "Jaya",   "Saturday",  "Mula",       "Capricorn"),
    "Virgo":       ("Gemini",      "Purna",  "Saturday",  "Sravana",    "Pisces"),
    "Libra":       ("Sagittarius", "Rikta",  "Thursday",  "Satabhisha", "Virgo"),
    "Scorpio":     ("Taurus",      "Nanda",  "Friday",    "Revati",     "Taurus"),
    "Sagittarius": ("Pisces",      "Jaya",   "Friday",    "Ashwini",    "Sagittarius"),
    "Capricorn":   ("Leo",         "Rikta",  "Tuesday",   "Rohini",     "Aquarius"),
    "Aquarius":    ("Sagittarius", "Jaya",   "Thursday",  "Ardra",      "Gemini"),
    "Pisces":      ("Aquarius",    "Purna",  "Thursday",  "Ashlesha",   "Leo"),
}

# Tithi group membership — matches Core.cs tithi group names
_TITHI_GROUPS: Dict[str, List[int]] = {
    "Nanda":  [1, 6, 11],
    "Bhadra": [2, 7, 12],
    "Jaya":   [3, 8, 13],
    "Rikta":  [4, 9, 14],
    "Purna":  [5, 10, 15],
}

def _tithi_group_of(tithi_num: int) -> str:
    """Returns the Nanda/Bhadra/Jaya/Rikta/Purna group of a tithi number (1-30)."""
    normalized = (tithi_num - 1) % 15 + 1  # collapse Krishnapaksha to 1-15
    for group_name, members in _TITHI_GROUPS.items():
        if normalized in members:
            return group_name
    return "Unknown"

_WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
# Python weekday Mon=0 … Sun=6 → index offset
def _python_weekday_to_name(python_weekday: int) -> str:
    """Convert Python weekday (Mon=0…Sun=6) to day name."""
    # Python: Mon=0, Tue=1, ..., Sun=6
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[python_weekday % 7]

# Short sign names extracted from RASIS list (strip the Sanskrit part)
_SIGN_NUM_TO_SHORT: Dict[int, str] = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer",
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces",
}
_SHORT_TO_SIGN_NUM = {v: k for k, v in _SIGN_NUM_TO_SHORT.items()}


def get_ghataka_chakra(
    birth_moon_sign_num: int,
    transit_moon_sign_num: int,
    tithi_num: int,
    python_weekday: int,
    moon_nakshatra: str,
    lagna_sign_num: int,
) -> Dict:
    """
    Determines if the current moment falls under a Ghataka (inauspicious) period
    for a person born with the given Moon sign.

    Args:
        birth_moon_sign_num:    Janma Rasi sign number 1-12.
        transit_moon_sign_num:  Current transit Moon sign number 1-12.
        tithi_num:              Current tithi number 1-30.
        python_weekday:         Python weekday (Mon=0 … Sun=6).
        moon_nakshatra:         Current Moon nakshatra name (e.g. 'Rohini').
        lagna_sign_num:         Current Lagna sign number 1-12.

    Returns:
        {
            "is_ghataka":        bool,
            "triggered_factors": List[str],   # which of the 5 factors match
            "ghataka_for_sign":  str,          # birth Moon sign name
            "table_entry":       Dict          # the Ghataka table row
        }

    Ported from Core.cs GhatakaChakra logic, lines 1784-1822.
    """
    birth_sign_name = _SIGN_NUM_TO_SHORT.get(birth_moon_sign_num, "")
    if birth_sign_name not in _GHATAKA_TABLE:
        return {
            "is_ghataka": False,
            "triggered_factors": [],
            "ghataka_for_sign": birth_sign_name,
            "table_entry": {},
        }

    gh_moon_sign, gh_tithi_group, gh_weekday, gh_nakshatra, gh_lagna = _GHATAKA_TABLE[birth_sign_name]

    transit_sign_name  = _SIGN_NUM_TO_SHORT.get(transit_moon_sign_num, "")
    current_tithi_group = _tithi_group_of(tithi_num)
    current_weekday_name = _python_weekday_to_name(python_weekday)
    lagna_sign_name    = _SIGN_NUM_TO_SHORT.get(lagna_sign_num, "")

    triggered: List[str] = []
    if transit_sign_name == gh_moon_sign:
        triggered.append(f"Moon in Ghataka sign ({gh_moon_sign})")
    if current_tithi_group == gh_tithi_group:
        triggered.append(f"Tithi group is Ghataka ({gh_tithi_group})")
    if current_weekday_name == gh_weekday:
        triggered.append(f"Weekday is Ghataka ({gh_weekday})")
    if moon_nakshatra == gh_nakshatra:
        triggered.append(f"Moon Nakshatra is Ghataka ({gh_nakshatra})")
    if lagna_sign_name == gh_lagna:
        triggered.append(f"Lagna is Ghataka sign ({gh_lagna})")

    return {
        "is_ghataka": len(triggered) > 0,
        "triggered_factors": triggered,
        "ghataka_for_sign": birth_sign_name,
        "table_entry": {
            "ghataka_moon_sign": gh_moon_sign,
            "ghataka_tithi_group": gh_tithi_group,
            "ghataka_weekday": gh_weekday,
            "ghataka_nakshatra": gh_nakshatra,
            "ghataka_lagna": gh_lagna,
        },
    }


# =============================================================================
# ELECTIONAL ASTROLOGY — Individual Event Calculators
# =============================================================================
# These functions port specific calculator methods from Muhurtha.cs.
# They check individual auspicious/inauspicious conditions for muhurtha selection.
#
# Python weekday convention used throughout:
#   Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6


# =============================================================================
# KARANA CALCULATION
# =============================================================================
# A tithi has two karanas (half-tithis). 11 karanas total: 4 fixed + 7 movable.
# Ported from Core.cs Karana() method.

_KARANA_TABLE_EC: Dict[int, Tuple[str, str]] = {
    1:  ("Kimstughna", "Bava"),
    2:  ("Balava",     "Kaulava"),
    3:  ("Taitila",    "Garaja"),
    4:  ("Vanija",     "Vishti"),
    5:  ("Bava",       "Balava"),
    6:  ("Kaulava",    "Taitila"),
    7:  ("Garaja",     "Vanija"),
    8:  ("Vishti",     "Bava"),
    9:  ("Balava",     "Kaulava"),
    10: ("Taitila",    "Garaja"),
    11: ("Vanija",     "Vishti"),
    12: ("Bava",       "Balava"),
    13: ("Kaulava",    "Taitila"),
    14: ("Garaja",     "Vanija"),
    15: ("Vishti",     "Bava"),
    16: ("Balava",     "Kaulava"),
    17: ("Taitila",    "Garaja"),
    18: ("Vanija",     "Vishti"),
    19: ("Bava",       "Balava"),
    20: ("Kaulava",    "Taitila"),
    21: ("Garaja",     "Vanija"),
    22: ("Vishti",     "Bava"),
    23: ("Balava",     "Kaulava"),
    24: ("Taitila",    "Garaja"),
    25: ("Vanija",     "Vishti"),
    26: ("Bava",       "Balava"),
    27: ("Kaulava",    "Taitila"),
    28: ("Garaja",     "Vanija"),
    29: ("Vishti",     "Shakuni"),
    30: ("Chatushpada", "Nagava"),
}


def get_karana(sun_long: float, moon_long: float) -> str:
    """
    Returns the Karana name for the given sun/moon longitudes.

    A karana is a half-tithi. Ported from Core.cs Karana().
    """
    moon_adj = moon_long if moon_long > sun_long else moon_long + 360.0
    raw = (moon_adj - sun_long) / 12.0
    tithi_idx = max(1, min(30, math.ceil(raw)))
    frac = raw - math.floor(raw)
    half = 0 if frac <= 0.5 else 1
    return _KARANA_TABLE_EC[tithi_idx][half]


# =============================================================================
# TARABALA — Extended with Cycle (Strong / Middling / Weak)
# =============================================================================
# Each of the 9 taras repeats 3 times across the 27 nakshatras.
# Cycle 1 (distance 1-9) = Strong, Cycle 2 (10-18) = Middling, Cycle 3 (19-27) = Weak.
# Ported from Muhurtha.cs TarabalaJanmaStrong … TarabalaParamaMitraWeak.

def get_tarabala_with_cycle(birth_nak_num: int, transit_nak_num: int) -> Tuple[str, int, int]:
    """
    Returns (tara_name, tara_num 1-9, cycle 1-3).

    cycle 1 = Strong (distance 1-9), cycle 2 = Middling (10-18), cycle 3 = Weak (19-27).
    """
    distance = transit_nak_num - birth_nak_num + 1
    if distance <= 0:
        distance += 27
    cycle = (distance - 1) // 9 + 1
    tara_num = (distance - 1) % 9 + 1
    tara_name = TARAS[tara_num - 1]
    return tara_name, tara_num, cycle


def _check_tara(birth: int, transit: int, tara: int, cycle: int) -> bool:
    _, t, c = get_tarabala_with_cycle(birth, transit)
    return t == tara and c == cycle


# Strong (cycle 1)
def is_tarabala_janma_strong(b: int, t: int) -> bool:        return _check_tara(b, t, 1, 1)
def is_tarabala_sampat_strong(b: int, t: int) -> bool:       return _check_tara(b, t, 2, 1)
def is_tarabala_vipat_strong(b: int, t: int) -> bool:        return _check_tara(b, t, 3, 1)
def is_tarabala_kshema_strong(b: int, t: int) -> bool:       return _check_tara(b, t, 4, 1)
def is_tarabala_pratyak_strong(b: int, t: int) -> bool:      return _check_tara(b, t, 5, 1)
def is_tarabala_sadhana_strong(b: int, t: int) -> bool:      return _check_tara(b, t, 6, 1)
def is_tarabala_naidhana_strong(b: int, t: int) -> bool:     return _check_tara(b, t, 7, 1)
def is_tarabala_mitra_strong(b: int, t: int) -> bool:        return _check_tara(b, t, 8, 1)
def is_tarabala_paramam_mitra_strong(b: int, t: int) -> bool: return _check_tara(b, t, 9, 1)

# Middling (cycle 2)
def is_tarabala_janma_middling(b: int, t: int) -> bool:        return _check_tara(b, t, 1, 2)
def is_tarabala_sampat_middling(b: int, t: int) -> bool:       return _check_tara(b, t, 2, 2)
def is_tarabala_vipat_middling(b: int, t: int) -> bool:        return _check_tara(b, t, 3, 2)
def is_tarabala_kshema_middling(b: int, t: int) -> bool:       return _check_tara(b, t, 4, 2)
def is_tarabala_pratyak_middling(b: int, t: int) -> bool:      return _check_tara(b, t, 5, 2)
def is_tarabala_sadhana_middling(b: int, t: int) -> bool:      return _check_tara(b, t, 6, 2)
def is_tarabala_naidhana_middling(b: int, t: int) -> bool:     return _check_tara(b, t, 7, 2)
def is_tarabala_mitra_middling(b: int, t: int) -> bool:        return _check_tara(b, t, 8, 2)
def is_tarabala_paramam_mitra_middling(b: int, t: int) -> bool: return _check_tara(b, t, 9, 2)

# Weak (cycle 3)
def is_tarabala_janma_weak(b: int, t: int) -> bool:        return _check_tara(b, t, 1, 3)
def is_tarabala_sampat_weak(b: int, t: int) -> bool:       return _check_tara(b, t, 2, 3)
def is_tarabala_vipat_weak(b: int, t: int) -> bool:        return _check_tara(b, t, 3, 3)
def is_tarabala_kshema_weak(b: int, t: int) -> bool:       return _check_tara(b, t, 4, 3)
def is_tarabala_pratyak_weak(b: int, t: int) -> bool:      return _check_tara(b, t, 5, 3)
def is_tarabala_sadhana_weak(b: int, t: int) -> bool:      return _check_tara(b, t, 6, 3)
def is_tarabala_naidhana_weak(b: int, t: int) -> bool:     return _check_tara(b, t, 7, 3)
def is_tarabala_mitra_weak(b: int, t: int) -> bool:        return _check_tara(b, t, 8, 3)
def is_tarabala_paramam_mitra_weak(b: int, t: int) -> bool: return _check_tara(b, t, 9, 3)


# =============================================================================
# YOGA EVENTS
# =============================================================================

# ── AmritaSiddhaYoga ──────────────────────────────────────────────────────────
# Sun→Hasta, Mon→Shravana, Tue→Ashwini, Wed→Anuradha,
# Thu→Pushya, Fri→Revati, Sat→Rohini.
# Ported from Muhurtha.cs IsAmritaSiddhaYogaOccuring().

_AMRITA_SIDDHA_NAK: Dict[int, str] = {
    0: "Shravana",   # Monday
    1: "Ashwini",    # Tuesday
    2: "Anuradha",   # Wednesday
    3: "Pushya",     # Thursday
    4: "Revati",     # Friday
    5: "Rohini",     # Saturday
    6: "Hasta",      # Sunday
}


def is_amrita_siddha_yoga(python_weekday: int, nakshatra: str) -> bool:
    """True when Moon nakshatra matches the AmritaSiddha fixed assignment for the weekday."""
    return _AMRITA_SIDDHA_NAK.get(python_weekday, "") == nakshatra


# ── BadNithyaYoga ────────────────────────────────────────────────────────────
# Ported from Muhurtha.cs IsBadNithyaYogaOccuring().

_BAD_NITHYA_YOGAS = frozenset({"Atiganda", "Shula", "Ganda", "Vyatipata", "Vaidhriti"})


def is_bad_nithya_yoga(yoga_name: str) -> bool:
    """True when the current Nithya Yoga is one of the five inauspicious yogas."""
    return yoga_name in _BAD_NITHYA_YOGAS


# ── UgraYoga ─────────────────────────────────────────────────────────────────
# Ported from Muhurtha.cs IsUgraYogaOccuring().

_UGRA_YOGA_TITHIS = frozenset({3, 4, 5, 6, 7, 9, 10, 12, 13})
_UGRA_YOGA_NAKSHATRAS = frozenset({
    "Rohini", "Uttara Phalguni", "Shravana", "Mrigashira",
    "Revati", "Krittika", "Pushya", "Anuradha", "Magha",
})


def is_ugra_yoga(tithi_num: int, nakshatra: str) -> bool:
    """True when tithi and nakshatra combine to form the inauspicious Ugra Yoga."""
    norm = (tithi_num - 1) % 15 + 1
    return norm in _UGRA_YOGA_TITHIS and nakshatra in _UGRA_YOGA_NAKSHATRAS


# ── SiddhaYoga ───────────────────────────────────────────────────────────────
# Complex per-weekday tithi+nakshatra conditions for the auspicious Siddha Yoga.
# Ported from Muhurtha.cs IsSiddhaYogaOccuring() and its inner week-day helpers.
#
# Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6

_SY_SUN_TITHIS = frozenset({1, 4, 6, 7, 12})
_SY_SUN_NAKS   = frozenset({"Pushya", "Hasta", "Uttara Phalguni", "Uttara Ashadha", "Mula", "Shravana"})

_SY_MON_TITHIS = frozenset({2, 7, 12})
_SY_MON_NAKS   = frozenset({
    "Rohini", "Mrigashira", "Punarvasu", "Chitra",
    "Shravana", "Shatabhisha", "Dhanishta", "Purva Bhadrapada",
})

_SY_TUE_NAKS = frozenset({
    "Ashwini", "Mrigashira", "Chitra", "Anuradha",
    "Mula", "Uttara Phalguni", "Dhanishta", "Purva Bhadrapada",
})

_SY_WED_NAKS = frozenset({
    "Rohini", "Mrigashira", "Ardra", "Uttara Phalguni",
    "Uttara Ashadha", "Anuradha",
})

_SY_THU_TITHIS = frozenset({4, 5, 7, 9, 13, 14})
_SY_THU_NAKS   = frozenset({
    "Magha", "Pushya", "Punarvasu", "Swati",
    "Purva Ashadha", "Purva Bhadrapada", "Revati", "Ashwini",
})

_SY_FRI_NAKS = frozenset({
    "Ashwini", "Bharani", "Ardra", "Uttara Phalguni",
    "Chitra", "Swati", "Purva Ashadha", "Revati",
})

_SY_SAT_NAKS = frozenset({
    "Swati", "Rohini", "Vishakha", "Anuradha",
    "Dhanishta", "Shatabhisha",
})


def is_siddha_yoga(tithi_num: int, python_weekday: int, nakshatra: str) -> bool:
    """
    Returns True when Tithi + Weekday + Nakshatra produce Siddha Yoga.
    Ported from Muhurtha.cs IsSiddhaYogaOccuring().
    """
    grp = _tithi_group_of(tithi_num)
    norm = (tithi_num - 1) % 15 + 1

    if python_weekday == 6:   # Sunday
        return norm in _SY_SUN_TITHIS and nakshatra in _SY_SUN_NAKS

    if python_weekday == 0:   # Monday
        return norm in _SY_MON_TITHIS and nakshatra in _SY_MON_NAKS

    if python_weekday == 1:   # Tuesday
        return nakshatra in _SY_TUE_NAKS or grp == "Jaya"

    if python_weekday == 2:   # Wednesday
        if (grp in {"Bhadra", "Jaya"}) and nakshatra in _SY_WED_NAKS:
            return True
        return grp == "Bhadra"

    if python_weekday == 3:   # Thursday
        return (norm in _SY_THU_TITHIS and nakshatra in _SY_THU_NAKS) or grp == "Purna"

    if python_weekday == 4:   # Friday
        if (grp in {"Bhadra", "Nanda"}) and nakshatra in _SY_FRI_NAKS:
            return True
        return grp == "Nanda"

    if python_weekday == 5:   # Saturday
        if (grp in {"Bhadra", "Rikta"}) and nakshatra in _SY_SAT_NAKS:
            return True
        return grp == "Rikta"

    return False


# =============================================================================
# DOSHA EVENTS  (require AstroTime for live planet positions)
# =============================================================================

_MALEFIC_PLANETS = [Planet.Sun, Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu]


def is_bhrigu_shatka(time: AstroTime) -> bool:
    """True when Venus is in House 6 — Bhrigu Shatka Dosha.
    Ported from Muhurtha.cs IsBhriguShatkaOccuring()."""
    return get_planet_house(Planet.Venus, time) == 6


def is_kujasthama(time: AstroTime) -> bool:
    """True when Mars is in House 8 — Kujasthama Dosha.
    Ported from Muhurtha.cs IsKujasthamaOccuring()."""
    return get_planet_house(Planet.Mars, time) == 8


def is_karthari_dosha(time: AstroTime) -> bool:
    """True when malefic planets occupy both House 2 AND House 12 (scissors formation).
    Ported from Muhurtha.cs IsKarthariDoshaOccuring()."""
    h2_planets  = get_planets_in_house(2, time)
    h12_planets = get_planets_in_house(12, time)
    return (any(p in _MALEFIC_PLANETS for p in h2_planets) and
            any(p in _MALEFIC_PLANETS for p in h12_planets))


def is_shashtashta_riphagata_chandra(time: AstroTime) -> bool:
    """True when Moon is in House 6, 8, or 12.
    Ported from Muhurtha.cs IsShashtashtaRiphagataChandra()."""
    return get_planet_house(Planet.Moon, time) in {6, 8, 12}


def is_sagraha_chandra_dosha(time: AstroTime) -> bool:
    """True when Moon shares its house with any other planet — Sagraha Chandra Dosha.
    Ported from Muhurtha.cs IsSagrahaChandra()."""
    moon_house = get_planet_house(Planet.Moon, time)
    others = [Planet.Sun, Planet.Mars, Planet.Mercury, Planet.Jupiter,
              Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
    return any(get_planet_house(p, time) == moon_house for p in others)


# =============================================================================
# KARANA EVENTS
# =============================================================================
# Ported from Muhurtha.cs IsTaitulaKarana, IsBavaKarana, IsVishtiKaranaOccuring, etc.

def is_taitila_karana(sun_long: float, moon_long: float) -> bool:
    """True when current Karana is Taitila — auspicious for marriage."""
    return get_karana(sun_long, moon_long) == "Taitila"


def is_bava_karana(sun_long: float, moon_long: float) -> bool:
    """True when current Karana is Bava — auspicious for stable/permanent work."""
    return get_karana(sun_long, moon_long) == "Bava"


def is_sakuna_karana(sun_long: float, moon_long: float) -> bool:
    """True when current Karana is Shakuni — auspicious for mantras."""
    return get_karana(sun_long, moon_long) == "Shakuni"


def is_bhadra_karana(sun_long: float, moon_long: float) -> bool:
    """True when current Karana is Vishti (Bhadra) — inauspicious, avoid important work."""
    return get_karana(sun_long, moon_long) == "Vishti"


# =============================================================================
# DIRECTIONAL TRAVEL — Inauspicious Weekdays per Direction
# =============================================================================
# Ported from Muhurtha.cs IsBadWeekdayForTravelEast / South / West / North.
# Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6

def is_bad_weekday_for_travel_east(python_weekday: int) -> bool:
    """Saturday or Monday are inauspicious for eastward travel."""
    return python_weekday in {0, 5}


def is_bad_weekday_for_travel_south(python_weekday: int) -> bool:
    """Thursday is inauspicious for southward travel."""
    return python_weekday == 3


def is_bad_weekday_for_travel_west(python_weekday: int) -> bool:
    """Sunday or Friday are inauspicious for westward travel."""
    return python_weekday in {4, 6}


def is_bad_weekday_for_travel_north(python_weekday: int) -> bool:
    """Wednesday or Tuesday are inauspicious for northward travel."""
    return python_weekday in {1, 2}


# =============================================================================
# PERSONAL ELECTIONAL EVENTS
# =============================================================================

def is_ekadashi(tithi_num: int) -> bool:
    """True when the current tithi is Ekadashi (11th lunar day)."""
    return (tithi_num - 1) % 15 + 1 == 11


# ── Good Hair-Cutting ────────────────────────────────────────────────────────
# Ported from Muhurtha.cs IsGoodHairCuttingOccuring().

_HAIR_CUT_GOOD_NAKS = frozenset({
    "Pushya", "Punarvasu", "Revati", "Hasta", "Shravana", "Dhanishta",
    "Mrigashira", "Ashwini", "Chitra", "Jyeshtha", "Shatabhisha", "Swati",
})
_HAIR_CUT_BAD_TITHIS = frozenset({4, 6, 14, 1, 15})


def is_good_hair_cutting(tithi_num: int, nakshatra: str) -> bool:
    """True when the moment is suitable for hair-cutting (nakshatra + tithi check)."""
    norm = (tithi_num - 1) % 15 + 1
    return nakshatra in _HAIR_CUT_GOOD_NAKS and norm not in _HAIR_CUT_BAD_TITHIS


# ── Good Nail-Cutting ────────────────────────────────────────────────────────
# Ported from Muhurtha.cs IsGoodNailCuttingOccuring().

_NAIL_CUT_BAD_TITHIS   = frozenset({8, 9, 14, 1, 15})
_NAIL_CUT_BAD_WEEKDAYS = frozenset({4, 5})   # Friday, Saturday


def is_good_nail_cutting(tithi_num: int, python_weekday: int) -> bool:
    """True when the moment is suitable for nail-cutting (weekday + tithi check)."""
    norm = (tithi_num - 1) % 15 + 1
    return python_weekday not in _NAIL_CUT_BAD_WEEKDAYS and norm not in _NAIL_CUT_BAD_TITHIS


# ── Good for Taking Injections / Minor Procedures ────────────────────────────
# Ported from Muhurtha.cs IsGoodTakingInjectionsOccuring().
# Conditions: Saturday or Monday; lagna in Aries/Taurus/Cancer/Virgo;
#             8th house empty; Mercury not in Pisces (debilitated).

_INJECTION_WEEKDAYS = frozenset({0, 5})   # Monday, Saturday
_INJECTION_LAGNA    = frozenset({1, 2, 4, 6})  # Aries, Taurus, Cancer, Virgo


def is_good_taking_injections(time: AstroTime) -> bool:
    """True when the moment is auspicious for receiving injections or minor procedures."""
    if time.datetime.weekday() not in _INJECTION_WEEKDAYS:
        return False
    if get_lagna_sign_num(time) not in _INJECTION_LAGNA:
        return False
    if get_planets_in_house(8, time):
        return False
    # Mercury debilitated in Pisces (sign 12)
    merc_long = get_planet_longitude(Planet.Mercury, time)
    _, merc_sign = get_rasi(merc_long)
    if merc_sign == 12:
        return False
    return True


# =============================================================================
# COMMERCE EVENTS
# =============================================================================
# Ported from simple Muhurtha.cs commerce checks (weekday/sign based).

def is_good_weekday_for_selling(python_weekday: int) -> bool:
    """True when weekday is favorable for selling (Monday, Wednesday, Thursday)."""
    return python_weekday in {0, 2, 3}


def is_good_moon_sign_for_selling(moon_sign_num: int) -> bool:
    """True when Moon is in Taurus (2), Cancer (4), or Pisces (12) — auspicious for sales."""
    return moon_sign_num in {2, 4, 12}


def is_bad_for_buying_tools_utensils_jewellery(nakshatra: str, tithi_num: int) -> bool:
    """True when nakshatra + tithi make buying tools/utensils/jewellery inauspicious."""
    bad_naks   = {"Ashlesha", "Mula", "Jyeshtha"}
    bad_tithis = {8, 9, 1}
    norm = (tithi_num - 1) % 15 + 1
    return nakshatra in bad_naks and norm in bad_tithis


# =============================================================================
# AGRICULTURE EVENTS
# =============================================================================

# Auspicious nakshatras for sowing: fixed, movable, soft, and light types.
_SOWING_GOOD_NAKS = frozenset({
    "Rohini", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada",   # fixed
    "Punarvasu", "Swati", "Shravana", "Dhanishta", "Shatabhisha",          # movable
    "Mrigashira", "Chitra", "Anuradha", "Revati",                          # soft
    "Ashwini", "Pushya", "Hasta",                                          # light
})
_SOWING_BAD_TITHIS = frozenset({4, 8, 9, 14})  # Rikta + Ashtami


def is_good_for_sowing(nakshatra: str) -> bool:
    """True when the current nakshatra is auspicious for sowing seeds."""
    return nakshatra in _SOWING_GOOD_NAKS


def is_bad_for_starting_agriculture(tithi_num: int) -> bool:
    """True when the tithi is inauspicious for starting agricultural work."""
    norm = (tithi_num - 1) % 15 + 1
    return norm in _SOWING_BAD_TITHIS or tithi_num == 30  # also Amavasya


# =============================================================================
# BUILDING / CONSTRUCTION EVENTS
# =============================================================================

_BUILD_GOOD_TITHIS   = frozenset({2, 3, 5, 7, 10, 11, 12, 13})
_BUILD_GOOD_WEEKDAYS = frozenset({0, 2, 3, 4})   # Mon, Wed, Thu, Fri
_BUILD_BAD_WEEKDAYS  = frozenset({1, 5})          # Tue, Sat
_BUILD_BAD_TITHIS    = frozenset({14, 15, 30})    # Chaturdashi, Purnima, Amavasya


def is_good_lunar_day_for_building(tithi_num: int) -> bool:
    """True when the tithi is auspicious for beginning construction."""
    norm = (tithi_num - 1) % 15 + 1
    return norm in _BUILD_GOOD_TITHIS


def is_good_weekday_for_building(python_weekday: int) -> bool:
    """True when the weekday is favorable for construction (Mon/Wed/Thu/Fri)."""
    return python_weekday in _BUILD_GOOD_WEEKDAYS


def is_bad_weekday_for_building(python_weekday: int) -> bool:
    """True when the weekday is unfavorable for construction (Tuesday or Saturday)."""
    return python_weekday in _BUILD_BAD_WEEKDAYS


def is_bad_lunar_phase_for_building(tithi_num: int) -> bool:
    """True when the tithi is inauspicious for construction (14th, 15th, or Amavasya)."""
    return tithi_num in _BUILD_BAD_TITHIS


# =============================================================================
# MASTER FUNCTION — Get All Electional Events
# =============================================================================

_WD_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_all_electional_events(
    time: AstroTime,
    birth_nakshatra_num: int = None,
    birth_time: AstroTime = None,
) -> List[Dict]:
    """
    Evaluates all individual electional (muhurtha) events for the given moment.

    Returns a list of dicts with keys:
        name        : str  — event identifier (matches C# EventName enum)
        category    : str  — "yoga" | "dosha" | "karana" | "travel" | "personal"
                             | "commerce" | "agriculture" | "building" | "tarabala"
        occurring   : bool — whether the condition is active right now
        description : str  — human-readable explanation

    Args:
        time               : AstroTime for the moment to evaluate.
        birth_nakshatra_num: Janma Nakshatra number 1-27. Required for Tarabala
                             events; omit (or pass None) to skip them.

    Ported from ~194 individual EventCalculator methods in Muhurtha.cs.
    """
    # ── Pre-compute panchang values ───────────────────────────────────────────
    sun_long  = get_planet_longitude(Planet.Sun,  time)
    moon_long = get_planet_longitude(Planet.Moon, time)

    tithi_name, tithi_num, _ = get_tithi(sun_long, moon_long)
    yoga_name, _             = get_yoga(sun_long, moon_long)

    nak_name, nak_num, _, _  = get_nakshatra(moon_long)
    _, moon_sign_num          = get_rasi(moon_long)

    python_weekday = time.datetime.weekday()
    wd = _WD_ABBR[python_weekday]

    karana_name = get_karana(sun_long, moon_long)

    events: List[Dict] = []

    def _add(name: str, category: str, occurring: bool,
             desc_true: str, desc_false: str = "") -> None:
        events.append({
            "name": name,
            "category": category,
            "occurring": occurring,
            "description": desc_true if occurring else (desc_false or f"{name} is not occurring."),
        })

    # ── Yoga Events ───────────────────────────────────────────────────────────
    v = is_amrita_siddha_yoga(python_weekday, nak_name)
    _add("AmritaSiddhaYoga", "yoga", v,
         f"Amrita Siddha Yoga is occurring — {nak_name} on {wd}. Highly auspicious.",
         "Amrita Siddha Yoga is not occurring.")

    v = is_siddha_yoga(tithi_num, python_weekday, nak_name)
    _add("SiddhaYoga", "yoga", v,
         f"Siddha Yoga is occurring (tithi {tithi_num}, {nak_name}, {wd}). Auspicious for important activities.",
         "Siddha Yoga is not occurring.")

    v = is_bad_nithya_yoga(yoga_name)
    _add("BadNithyaYoga", "yoga", v,
         f"{yoga_name} is an inauspicious Nithya Yoga. Avoid important new starts.",
         f"{yoga_name} is not an inauspicious Nithya Yoga.")

    v = is_ugra_yoga(tithi_num, nak_name)
    _add("UgraYoga", "yoga", v,
         f"Ugra Yoga is occurring (tithi {tithi_num} + {nak_name}). Avoid auspicious activities.",
         "Ugra Yoga is not occurring.")

    # ── Dosha Events ──────────────────────────────────────────────────────────
    v = is_bhrigu_shatka(time)
    _add("BhriguShatka", "dosha", v,
         "Venus is in House 6 — Bhrigu Shatka Dosha. Unfavourable for financial and relationship matters.",
         "Bhrigu Shatka is not active (Venus is not in House 6).")

    v = is_kujasthama(time)
    _add("Kujasthama", "dosha", v,
         "Mars is in House 8 — Kujasthama Dosha. Unfavourable for marriage and partnerships.",
         "Kujasthama is not active (Mars is not in House 8).")

    v = is_karthari_dosha(time)
    _add("KarthariDosha", "dosha", v,
         "Malefic planets flank both House 2 and House 12 — Karthari Dosha. Avoid important activities.",
         "Karthari Dosha is not occurring.")

    v = is_shashtashta_riphagata_chandra(time)
    _add("ShashtashtaRiphagataChandra", "dosha", v,
         "Moon is in the 6th, 8th, or 12th house. Unfavourable period for emotional and health matters.",
         "Moon is not in the 6th/8th/12th house — no Shashtashta Riphagata Dosha.")

    v = is_sagraha_chandra_dosha(time)
    _add("SagrahaChandra", "dosha", v,
         "Moon shares its house with another planet — Sagraha Chandra Dosha. Use caution.",
         "Moon is not conjoined with any planet — no Sagraha Chandra Dosha.")

    # ── Karana Events ─────────────────────────────────────────────────────────
    _add("TaitilaKarana", "karana", karana_name == "Taitila",
         f"Current Karana is Taitila — auspicious for marriage and social activities.",
         f"Current Karana is {karana_name} (not Taitila).")

    _add("BavaKarana", "karana", karana_name == "Bava",
         "Current Karana is Bava — auspicious for stable, permanent undertakings.",
         f"Current Karana is {karana_name} (not Bava).")

    _add("ShakuniKarana", "karana", karana_name == "Shakuni",
         "Current Karana is Shakuni — auspicious for mantras and spiritual practices.",
         f"Current Karana is {karana_name} (not Shakuni).")

    _add("BhadraKarana", "karana", karana_name == "Vishti",
         "Current Karana is Vishti (Bhadra) — inauspicious, avoid important activities.",
         f"Current Karana is {karana_name} (not Vishti/Bhadra).")

    # ── Ekadashi ──────────────────────────────────────────────────────────────
    _add("EkadashiOccuring", "personal", is_ekadashi(tithi_num),
         f"Today is Ekadashi (11th lunar day). Auspicious for fasting and spiritual practice.",
         f"Today is not Ekadashi (current tithi: {tithi_name}).")

    # ── Directional Travel ────────────────────────────────────────────────────
    _add("BadWeekdayForTravelEast",  "travel",
         is_bad_weekday_for_travel_east(python_weekday),
         f"{wd} is inauspicious for eastward travel.",
         f"{wd} is acceptable for eastward travel.")

    _add("BadWeekdayForTravelSouth", "travel",
         is_bad_weekday_for_travel_south(python_weekday),
         f"{wd} is inauspicious for southward travel.",
         f"{wd} is acceptable for southward travel.")

    _add("BadWeekdayForTravelWest",  "travel",
         is_bad_weekday_for_travel_west(python_weekday),
         f"{wd} is inauspicious for westward travel.",
         f"{wd} is acceptable for westward travel.")

    _add("BadWeekdayForTravelNorth", "travel",
         is_bad_weekday_for_travel_north(python_weekday),
         f"{wd} is inauspicious for northward travel.",
         f"{wd} is acceptable for northward travel.")

    # ── Personal Electional ───────────────────────────────────────────────────
    v = is_good_hair_cutting(tithi_num, nak_name)
    _add("GoodHairCutting", "personal", v,
         f"{nak_name} on tithi {tithi_num} is good for hair-cutting.",
         f"Not an ideal time for hair-cutting ({nak_name}, tithi {tithi_num}).")

    v = is_good_nail_cutting(tithi_num, python_weekday)
    _add("GoodNailCutting", "personal", v,
         f"Acceptable time for nail-cutting (tithi {tithi_num}, {wd}).",
         f"Not ideal for nail-cutting — avoid Friday/Saturday and tithis 8/9/14/1/15.")

    try:
        v = is_good_taking_injections(time)
        _add("GoodTakingInjections", "personal", v,
             "Auspicious for receiving injections or minor medical procedures.",
             "Not ideal for injections — weekday, lagna, or 8th house conditions not met.")
    except Exception:
        pass  # Skip gracefully if lagna calculation is unavailable

    # ── Commerce ──────────────────────────────────────────────────────────────
    _add("GoodWeekdayForSelling",  "commerce",
         is_good_weekday_for_selling(python_weekday),
         f"{wd} is a good day for selling.",
         f"{wd} is not the most favourable day for selling.")

    _add("GoodMoonSignForSelling", "commerce",
         is_good_moon_sign_for_selling(moon_sign_num),
         f"Moon in sign {moon_sign_num} is auspicious for selling (Taurus/Cancer/Pisces favoured).",
         f"Moon in sign {moon_sign_num} is not particularly favourable for selling.")

    _add("BadForBuyingToolsUtensilsJewellery", "commerce",
         is_bad_for_buying_tools_utensils_jewellery(nak_name, tithi_num),
         f"{nak_name} on tithi {tithi_num} is inauspicious for buying tools, utensils, or jewellery.",
         "No contra-indicator for buying tools/utensils/jewellery at this time.")

    # ── Agriculture ───────────────────────────────────────────────────────────
    _add("GoodForSowing", "agriculture",
         is_good_for_sowing(nak_name),
         f"{nak_name} is a favourable nakshatra for sowing seeds.",
         f"{nak_name} is not a preferred nakshatra for sowing.")

    _add("BadForStartingAgriculture", "agriculture",
         is_bad_for_starting_agriculture(tithi_num),
         f"Tithi {tithi_num} ({tithi_name}) is inauspicious for starting agricultural work.",
         f"Tithi {tithi_num} ({tithi_name}) is not contra-indicated for agricultural work.")

    # ── Building ──────────────────────────────────────────────────────────────
    _add("GoodLunarDayForBuilding", "building",
         is_good_lunar_day_for_building(tithi_num),
         f"Tithi {tithi_num} is auspicious for starting construction.",
         f"Tithi {tithi_num} is not among the most favoured for construction.")

    _add("GoodWeekdayForBuilding", "building",
         is_good_weekday_for_building(python_weekday),
         f"{wd} is favourable for construction activities.",
         f"{wd} is not the most favourable weekday for construction.")

    _add("BadWeekdayForBuilding",  "building",
         is_bad_weekday_for_building(python_weekday),
         f"{wd} (Tuesday/Saturday) is unfavourable for construction.",
         f"{wd} is not among the bad weekdays for construction.")

    _add("BadLunarPhaseForBuilding", "building",
         is_bad_lunar_phase_for_building(tithi_num),
         f"Tithi {tithi_num} (near full/new moon or Chaturdashi) is unfavourable for construction.",
         f"Tithi {tithi_num} is not a bad lunar phase for construction.")

    # ── Tarabala (only when birth nakshatra is provided) ─────────────────────
    if birth_nakshatra_num is not None:
        tara_name, tara_num, cycle = get_tarabala_with_cycle(birth_nakshatra_num, nak_num)
        cycle_name = {1: "Strong", 2: "Middling", 3: "Weak"}[cycle]

        # Good taras: Sampat(2), Kshema(4), Sadhana(6), Mitra(8), Parama Mitra(9)
        good_taras = {2, 4, 6, 8, 9}
        # Unfavourable taras: Janma(1), Vipat(3), Pratyak(5), Naidhana(7)
        bad_taras  = {1, 3, 5, 7}

        base_desc = f"Transit Moon is in {tara_name} Tara ({cycle_name} cycle, tara {tara_num})."

        _add("TarabalaFavorable", "tarabala",
             tara_num in good_taras,
             base_desc + " Favourable Tarabala.",
             base_desc + " Not a favourable Tara for this individual.")

        _add("TarabalaUnfavorable", "tarabala",
             tara_num in bad_taras,
             base_desc + " Unfavourable Tarabala — use caution.",
             base_desc + " Tarabala is not in an unfavourable Tara.")

    # ── [P9] Ashtakavarga Gochara Bindu ──────────────────────────────────────
    # 63 events: 7 planets × 9 bindu levels (0–8).
    # True when a planet's Bhinnashtakavarga score in its current transit sign
    # equals exactly N bindus (using the natal birth chart BAV).
    if birth_time is not None:
        _bav = get_all_bhinnashtakavarga(birth_time)
        for _p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            _p_enum = getattr(Planet, _p_name)
            _p_long = get_planet_longitude(_p_enum, time)
            _, _transit_sign = get_rasi(_p_long)
            _bindu = _bav[_p_name].get(_transit_sign, 0)
            for _n in range(9):
                _add(
                    f"{_p_name}Transit{_n}Bindu",
                    "ashtakavarga_bindu",
                    _bindu == _n,
                    f"{_p_name} transits a sign with {_n} BAV bindus — affects the strength of transit results.",
                    f"{_p_name} is not in a {_n}-bindu sign (current transit sign has {_bindu} bindus).",
                )

    # ── [P9] Dasa-Based Events ────────────────────────────────────────────────
    # 15 events based on current Vimshottari Dasa/Bhukti relative to natal chart.
    if birth_time is not None:
        # Birth nakshatra position
        _b_moon_long = get_planet_longitude(Planet.Moon, birth_time)
        _, _b_nak_num, _b_nak_pct, _ = get_nakshatra(_b_moon_long)

        # Strip timezone for dasa arithmetic (all comparisons use naive datetimes)
        _birth_dt = birth_time.datetime.replace(tzinfo=None) if birth_time.datetime.tzinfo else birth_time.datetime
        _transit_dt = time.datetime.replace(tzinfo=None) if time.datetime.tzinfo else time.datetime

        # Current maha dasa and bhukti lords as strings (e.g. "Jupiter", "Saturn")
        _maha_lord, _bhukti_lord = get_vimshottari_dasa(_b_nak_num, _b_nak_pct, _birth_dt, _transit_dt)

        # Dasa count from birth: 1 = birth dasa, 2 = next dasa, …
        _sched = get_vimshottari_dasa_schedule(_b_nak_num, _b_nak_pct, _birth_dt)
        _dasa_count = 9  # fallback
        for _di, _md in enumerate(_sched.get("maha_dasas", [])):
            _md_start = datetime.strptime(_md["start_date"], "%Y-%m-%d")
            _md_end   = datetime.strptime(_md["end_date"],   "%Y-%m-%d")
            if _md_start <= _transit_dt < _md_end:
                _dasa_count = _di + 1
                break

        # Lords of natal houses (as planet name strings)
        _lord1 = get_lord_of_house(1,  birth_time).name
        _lord2 = get_lord_of_house(2,  birth_time).name
        _lord3 = get_lord_of_house(3,  birth_time).name
        _lord5 = get_lord_of_house(5,  birth_time).name
        _lord6 = get_lord_of_house(6,  birth_time).name
        _lord8 = get_lord_of_house(8,  birth_time).name
        _lord9 = get_lord_of_house(9,  birth_time).name

        # Natal house of Sun and house lords (for same-house conjunction check)
        _sun_birth_house  = get_planet_house(Planet.Sun, birth_time)
        _lord2_birth_house = get_planet_house(get_lord_of_house(2,  birth_time), birth_time)
        _lord5_birth_house = get_planet_house(get_lord_of_house(5,  birth_time), birth_time)
        _lord9_birth_house = get_planet_house(get_lord_of_house(9,  birth_time), birth_time)
        _lord10_birth_house = get_planet_house(get_lord_of_house(10, birth_time), birth_time)

        # Helper: natal house of a dasa/bhukti lord (handles all 9 vimshottari planets)
        _DASA_PLANET_MAP = {
            "Sun": Planet.Sun, "Moon": Planet.Moon, "Mars": Planet.Mars,
            "Mercury": Planet.Mercury, "Jupiter": Planet.Jupiter,
            "Venus": Planet.Venus, "Saturn": Planet.Saturn,
            "Rahu": Planet.Rahu, "Ketu": Planet.Ketu,
        }

        def _birth_house_of(planet_name: str) -> int:
            p = _DASA_PLANET_MAP.get(planet_name)
            return get_planet_house(p, birth_time) if p is not None else 0

        _maha_birth_house   = _birth_house_of(_maha_lord)
        _bhukti_birth_house = _birth_house_of(_bhukti_lord)

        # Sun natal sign for exaltation/debilitation checks
        _sun_birth_long = get_planet_longitude(Planet.Sun, birth_time)
        _, _sun_birth_sign = get_rasi(_sun_birth_long)      # 1=Aries … 12=Pisces

        _add("Lord6And8Dasa", "dasa",
             _maha_lord in (_lord6, _lord8),
             f"Lord of 6th or 8th house ({_maha_lord}) is the current maha dasa lord — generally inauspicious.",
             f"Current maha dasa lord ({_maha_lord}) is not lord of house 6 or 8.")

        _add("Lord5And9Dasa", "dasa",
             _maha_lord in (_lord5, _lord9),
             f"Lord of 5th or 9th house ({_maha_lord}) is the current maha dasa lord — auspicious.",
             f"Current maha dasa lord ({_maha_lord}) is not lord of house 5 or 9.")

        _add("Lord5And9DasaBhukti", "dasa",
             (_maha_lord == _lord5 and _bhukti_lord == _lord9) or
             (_maha_lord == _lord9 and _bhukti_lord == _lord5),
             f"Maha dasa lord ({_maha_lord}) and bhukti lord ({_bhukti_lord}) are lords of houses 5 and 9 — highly auspicious.",
             f"Current dasa/bhukti ({_maha_lord}/{_bhukti_lord}) is not the 5th–9th lord combination.")

        _bad_bhukti_dasa = (
            (_bhukti_birth_house == 6  and _maha_birth_house == 8) or
            (_bhukti_birth_house == 12 and _maha_birth_house == 2)
        )
        _add("BhuktiDasaLordInBadHouses", "dasa",
             _bad_bhukti_dasa,
             f"Bhukti lord ({_bhukti_lord}) natally in house {_bhukti_birth_house} and dasa lord ({_maha_lord}) in house {_maha_birth_house} — inauspicious combination.",
             f"Dasa/bhukti lords are not in a bad house pairing.")

        _add("LagnaLordDasa", "dasa",
             _maha_lord == _lord1,
             f"Ascendant lord ({_maha_lord}) is the current maha dasa lord — favourable for self-expression and vitality.",
             f"Current maha dasa lord ({_maha_lord}) is not the ascendant lord.")

        _add("Lord2Dasa", "dasa",
             _maha_lord == _lord2,
             f"Lord of 2nd house ({_maha_lord}) is the current maha dasa lord — favourable for wealth and finances.",
             f"Current maha dasa lord ({_maha_lord}) is not lord of house 2.")

        _add("Lord3Dasa", "dasa",
             _maha_lord == _lord3,
             f"Lord of 3rd house ({_maha_lord}) is the current maha dasa lord.",
             f"Current maha dasa lord ({_maha_lord}) is not lord of house 3.")

        _add("Saturn4thDasa", "dasa",
             _maha_lord == "Saturn" and _dasa_count == 4,
             f"Saturn is the current maha dasa lord and this is the 4th dasa from birth — generally unfavourable.",
             f"Saturn 4th dasa condition not met (dasa lord: {_maha_lord}, count: {_dasa_count}).")

        _add("Jupiter6thDasa", "dasa",
             _maha_lord == "Jupiter" and _dasa_count == 6,
             f"Jupiter is the current maha dasa lord and this is the 6th dasa from birth — generally unfavourable.",
             f"Jupiter 6th dasa condition not met (dasa lord: {_maha_lord}, count: {_dasa_count}).")

        # ElevatedSunDasa: C# marks isSunElevated as TODO/false; implemented here as Sun in exaltation (Aries = sign 1)
        _add("ElevatedSunDasa", "dasa",
             _maha_lord == "Sun" and _sun_birth_sign == 1,
             "Sun dasa while Sun is elevated (exalted in Aries) — wisdom, wealth, and fame.",
             f"Elevated Sun dasa condition not met (dasa lord: {_maha_lord}, Sun natal sign: {_sun_birth_sign}).")

        # SunWithLord9Or10Dasa: Sun dasa AND Sun is in own house OR same house as lord of 9 or 10
        _sun_in_own_house   = _sun_birth_sign == 5       # Leo = sign 5 (Sun's own sign)
        _sun_with_lord9     = _sun_birth_house == _lord9_birth_house
        _sun_with_lord10    = _sun_birth_house == _lord10_birth_house
        _add("SunWithLord9Or10Dasa", "dasa",
             _maha_lord == "Sun" and (_sun_in_own_house or _sun_with_lord9 or _sun_with_lord10),
             "Sun dasa while Sun occupies its own house or is conjunct lord of 9th or 10th — leadership and prosperity.",
             f"Sun with lord 9/10 dasa condition not met (dasa lord: {_maha_lord}).")

        _add("SunWithLord5Dasa", "dasa",
             _maha_lord == "Sun" and (_sun_birth_house == _lord5_birth_house),
             "Sun dasa while Sun is conjunct lord of 5th house — birth of children and creative success.",
             f"Sun with lord 5 dasa condition not met (dasa lord: {_maha_lord}).")

        _add("SunWithLord2Dasa", "dasa",
             _maha_lord == "Sun" and (_sun_birth_house == _lord2_birth_house),
             "Sun dasa while Sun is conjunct lord of 2nd house — wealth and property gains.",
             f"Sun with lord 2 dasa condition not met (dasa lord: {_maha_lord}).")

        # SunBadPositionDasa: C# TODO; implemented as Sun debilitated (Libra=7) or in bad natal house (6/8/12)
        _sun_debilitated  = _sun_birth_sign == 7          # Libra
        _sun_in_bad_house = _sun_birth_house in (6, 8, 12)
        _add("SunBadPositionDasa", "dasa",
             _maha_lord == "Sun" and (_sun_debilitated or _sun_in_bad_house),
             "Sun dasa while Sun is debilitated or in 6th/8th/12th house — disease, loss, and reverses.",
             f"Sun bad position dasa condition not met (dasa lord: {_maha_lord}).")

        # ExaltedSunDasa: Sun dasa AND Sun currently transits Aries (exaltation sign = 1)
        _, _sun_transit_sign = get_rasi(sun_long)
        _add("ExaltedSunDasa", "dasa",
             _maha_lord == "Sun" and _sun_transit_sign == 1,
             "Sun dasa while Sun is currently transiting its exaltation sign (Aries) — sudden gains and auspicious travels.",
             f"Exalted Sun dasa condition not met (dasa lord: {_maha_lord}, transit sign: {_sun_transit_sign}).")

    # ── [P9] Planet Strength Flags ────────────────────────────────────────────
    # 7 events: exactly one is True — the planet with the highest Shadbala total
    # at the transit moment.  Mirrors AllPlanetOrderedByStrength(time)[0] from C#.
    _planet_sdb = get_all_planet_shadbala(time.datetime, time.lat, time.lon)
    _strongest_planet = max(_planet_sdb, key=lambda p: _planet_sdb[p]["total_rupas"])
    for _ps_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        _add(
            f"{_ps_name}IsStrong",
            "strength",
            _strongest_planet == _ps_name,
            f"{_ps_name} is the strongest planet by Shadbala at this moment.",
            f"{_ps_name} is not the strongest planet (strongest: {_strongest_planet}).",
        )

    # ── [P9] House Strength Flags ─────────────────────────────────────────────
    # 12 events: exactly one is True — the house with the highest Bhava Bala total
    # at the transit moment.  Mirrors AllHousesOrderedByStrength(time)[0] from C#.
    _house_strengths = {
        h: get_bhava_bala(h, time.julian_day, time.lat, time.lon)["total"]
        for h in range(1, 13)
    }
    _strongest_house = max(_house_strengths, key=_house_strengths.get)
    for _hs_num in range(1, 13):
        _add(
            f"House{_hs_num}IsStrong",
            "strength",
            _strongest_house == _hs_num,
            f"House {_hs_num} is the strongest house by Bhava Bala at this moment.",
            f"House {_hs_num} is not the strongest house (strongest: House {_strongest_house}).",
        )

    return events


# ==================== DEMO ====================

if __name__ == "__main__":
    # Example: June 7, 1988, 8:40 PM, Chennai
    from logic.calculate import get_planet_longitude
    from logic.consts import Planet
    from logic.time import AstroTime
    from datetime import datetime
    import pytz
    
    # Create datetime (IST)
    ist = pytz.timezone('Asia/Kolkata')
    dt = ist.localize(datetime(1988, 6, 7, 20, 40, 0))
    
    # Create AstroTime
    time = AstroTime(dt, 13.0827, 80.2707)  # Chennai coordinates
    
    # Get planet positions
    sun_long = get_planet_longitude(Planet.Sun, time)
    moon_long = get_planet_longitude(Planet.Moon, time)
    
    from logic.nakshatra import get_nakshatra
    moon_nak, _, _, _ = get_nakshatra(moon_long)
    
    weekday = dt.weekday()  # 0=Monday in Python, need to convert
    weekday = (weekday + 1) % 7  # Convert to 0=Sunday format
    
    print("="*60)
    print("MUHURTHA ANALYSIS - Daily Predictions")
    print("="*60)
    print(f"Date: June 7, 1988")
    print(f"Weekday: {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][weekday]}")
    print()
    
    # Day Quality Summary
    summary = get_day_quality_summary(sun_long, moon_long, moon_nak, weekday)
    print(f"Overall Day Quality: {summary['day_quality']} (Score: {summary['overall_score']}/100)")
    print(f"Advice: {summary['advice']}")
    print(f"Best For: {summary['best_for']}")
    print(f"Avoid: {summary['avoid']}")
    print()
    print(f"Panchang:")
    print(f"  Tithi: {summary['panchang']['tithi']}")
    print(f"  Nakshatra: {summary['panchang']['nakshatra']}")
    print(f"  Yoga: {summary['panchang']['yoga']}")
    print()
    
    # Favorable Activities
    print("FAVORABLE ACTIVITIES (Score >= 50):")
    print("-" * 60)
    favorable = get_best_activities_for_day(sun_long, moon_long, moon_nak, weekday, threshold=50)
    for i, activity in enumerate(favorable, 1):
        print(f"{i}. {activity['activity']}: {activity['score']}/100 - {activity['recommendation']}")
    print()
    
    # Activities to Avoid
    print("ACTIVITIES TO AVOID (Score < 30):")
    print("-" * 60)
    avoid = get_activities_to_avoid(sun_long, moon_long, moon_nak, weekday, threshold=30)
    if avoid:
        for i, activity in enumerate(avoid, 1):
            print(f"{i}. {activity['activity']}: {activity['score']}/100 - {activity['recommendation']}")
    else:
        print("None - All activities have acceptable scores")
    print()
    
    # Detailed Analysis for specific activity
    print("DETAILED ANALYSIS - TRAVEL:")
    print("-" * 60)
    travel_eval = evaluate_muhurtha(sun_long, moon_long, moon_nak, weekday, "travel")
    print(f"Score: {travel_eval['score']}/100 {travel_eval['emoji']}")
    print(f"Recommendation: {travel_eval['recommendation']}")
    print(f"\nPositive Factors:")
    for reason in travel_eval['reasons_good']:
        print(f"  + {reason}")
    if travel_eval['reasons_bad']:
        print(f"\nNegative Factors:")
        for reason in travel_eval['reasons_bad']:
            print(f"  - {reason}")
