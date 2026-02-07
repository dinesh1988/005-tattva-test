"""
Muhurtha (Electional Astrology) Module

Provides auspicious timing calculations for daily activities and life events.
For daily predictions, this module determines favorable/unfavorable times
based on Tithi, Nakshatra, Weekday, and Hora.

Reference: Library/Logic/Calculate/Muhurtha.cs (10,853 lines in VedAstro C#)
"""

from datetime import datetime, time as dt_time, timedelta
from typing import Dict, List, Tuple
from logic.panchang import get_tithi, get_yoga, TITHIS, YOGA_DATA
from logic.nakshatra import NAKSHATRAS

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
