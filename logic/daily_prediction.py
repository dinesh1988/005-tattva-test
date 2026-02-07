"""
Daily Prediction Engine
=======================
Calculates daily predictions based on transit Moon position.

Formula:
1. Mood (Lagna Gochara) - House position of transit Moon from Lagna
2. Fuel (Chandra Gochara) - House position of transit Moon from Birth Moon
3. Luck (Tarabala) - Relationship between birth nakshatra and transit nakshatra
"""

from datetime import datetime
import pytz
from .calculate import get_planet_longitude
from .consts import Planet
from .time import AstroTime
from .nakshatra import get_nakshatra, get_tara_bala
from .rasi import get_rasi, get_gochara_house


# Mood interpretations by house (Lagna Gochara)
MOOD_INTERPRETATIONS = {
    1: {"name": "Self Focus", "mood": "Personal / New Beginnings", "description": "Focus on self-improvement, appearance, and personal goals"},
    2: {"name": "Resource Building", "mood": "Financial / Accumulation", "description": "Focus on finances, family, and building resources"},
    3: {"name": "Communication", "mood": "Social / Expressive", "description": "Active communication, short travels, sibling connections"},
    4: {"name": "Home & Comfort", "mood": "Domestic / Emotional", "description": "Focus on home, mother, emotional security, and comfort"},
    5: {"name": "Creative Expression", "mood": "Creative / Playful", "description": "Romance, creativity, children, entertainment, and joy"},
    6: {"name": "Service & Health", "mood": "Problem-Solving / Healing", "description": "Health focus, service, overcoming obstacles, daily routines"},
    7: {"name": "Partnership", "mood": "Collaborative / Social", "description": "Focus on partnerships, marriage, contracts, and others"},
    8: {"name": "Transformation", "mood": "Offline / Detective", "description": "Privacy, secrets, research, transformation, and isolation"},
    9: {"name": "Wisdom Seeking", "mood": "Philosophical / Learning", "description": "Higher learning, travel, philosophy, and spiritual pursuits"},
    10: {"name": "Career Drive", "mood": "Ambitious / Professional", "description": "Career focus, public image, authority, and achievements"},
    11: {"name": "Goals & Network", "mood": "Social / Aspirational", "description": "Friendships, networking, goals, and gains"},
    12: {"name": "Retreat & Rest", "mood": "Introspective / Spiritual", "description": "Solitude, meditation, expenses, foreign lands, and spirituality"}
}

# Fuel/Energy levels by house (Chandra Lagna Gochara)
FUEL_INTERPRETATIONS = {
    1: {"name": "Peak Energy", "level": "Maximum", "description": "High vitality, confidence, and personal power"},
    2: {"name": "Stable Energy", "level": "Good", "description": "Steady energy for financial and family matters"},
    3: {"name": "Active Energy", "level": "High", "description": "Mental alertness, communication power"},
    4: {"name": "Comfortable Energy", "level": "Moderate", "description": "Emotional stability, peaceful energy"},
    5: {"name": "Creative Energy", "level": "High", "description": "Joyful, playful, romantic energy"},
    6: {"name": "High Voltage", "level": "Intense", "description": "Fixer energy - service, health, problem-solving"},
    7: {"name": "Partnership Energy", "level": "Good", "description": "Collaborative, relationship-focused energy"},
    8: {"name": "Deep Energy", "level": "Low-Moderate", "description": "Reserved, introspective, transformative"},
    9: {"name": "Expansive Energy", "level": "High", "description": "Optimistic, adventurous, learning energy"},
    10: {"name": "Ambitious Energy", "level": "High", "description": "Career-driven, achievement-focused"},
    11: {"name": "Social Energy", "level": "High", "description": "Networking, goal-oriented, friendly"},
    12: {"name": "Retreat Energy", "level": "Low", "description": "Rest, meditation, spiritual recharge"}
}

# Luck status by Tara
LUCK_INTERPRETATIONS = {
    "Janma": {"status": "Yellow Light", "description": "Neutral, be cautious, mixed results"},
    "Sampat": {"status": "Green Light", "description": "Obstacles removed, effort yields results, prosperity"},
    "Vipat": {"status": "Red Light", "description": "Danger, avoid important actions, delays expected"},
    "Kshema": {"status": "Green Light", "description": "Well-being, comfort, peaceful outcomes"},
    "Pratyak": {"status": "Red Light", "description": "Obstacles, resistance, avoid risks"},
    "Sadhana": {"status": "Green Light", "description": "Achievement, success through effort"},
    "Naidhana": {"status": "Red Light", "description": "Critical danger, avoid major decisions"},
    "Mitra": {"status": "Green Light", "description": "Friendly support, helpful connections"},
    "Parama Mitra": {"status": "Green Light", "description": "Best friend energy, maximum support"}
}


def calculate_daily_prediction(
    birth_datetime: datetime,
    birth_lat: float,
    birth_lon: float,
    birth_lagna_num: int,
    birth_nakshatra_num: int,
    birth_moon_longitude: float,
    prediction_date: str,
    timezone: str = "Asia/Kolkata"
) -> dict:
    """
    Calculate daily prediction for a given date.
    
    Args:
        birth_datetime: Birth date and time
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        birth_lagna_num: Birth Lagna/Ascendant sign number (1-12)
        birth_nakshatra_num: Birth nakshatra number (1-27)
        birth_moon_longitude: Birth Moon longitude (for calculating birth moon sign)
        prediction_date: Date to predict for (YYYY-MM-DD)
        timezone: Timezone for the prediction date
        
    Returns:
        Dictionary with mood, fuel, luck calculations
    """
    # Parse prediction date (use noon for transit calculations)
    tz = pytz.timezone(timezone)
    pred_dt = datetime.strptime(prediction_date, "%Y-%m-%d")
    pred_dt = tz.localize(pred_dt.replace(hour=12, minute=0, second=0))
    
    # Create AstroTime for transit calculation
    transit_time = AstroTime(dt=pred_dt, lat=birth_lat, lon=birth_lon)
    
    # 1. Get Transit Moon position
    transit_moon_long = get_planet_longitude(Planet.Moon, transit_time)
    transit_moon_sign, transit_moon_sign_num = get_rasi(transit_moon_long)
    transit_moon_nak_name, transit_moon_nak_num, _, _ = get_nakshatra(transit_moon_long)
    
    # 2. Get Birth Moon sign
    birth_moon_sign, birth_moon_sign_num = get_rasi(birth_moon_longitude)
    
    # 3. Calculate Mood (Lagna Gochara)
    mood_house = get_gochara_house(birth_lagna_num, transit_moon_sign_num)
    mood_data = MOOD_INTERPRETATIONS[mood_house]
    
    # 4. Calculate Fuel (Chandra Lagna Gochara)
    fuel_house = get_gochara_house(birth_moon_sign_num, transit_moon_sign_num)
    fuel_data = FUEL_INTERPRETATIONS[fuel_house]
    
    # 5. Calculate Luck (Tarabala)
    tara_name, tara_num = get_tara_bala(birth_nakshatra_num, transit_moon_nak_num)
    # Extract base tara name (remove parentheses)
    tara_base = tara_name.split('(')[0].strip()
    luck_data = LUCK_INTERPRETATIONS.get(tara_base, {"status": "Unknown", "description": "Unknown tara"})
    
    # 6. Generate overall prediction summary
    overall = f"{mood_data['mood']} with {fuel_data['level']} energy and {luck_data['status']}"
    
    return {
        "date": prediction_date,
        "transit_moon": {
            "sign": transit_moon_sign,
            "sign_number": transit_moon_sign_num,
            "nakshatra": transit_moon_nak_name,
            "nakshatra_number": transit_moon_nak_num,
            "longitude": round(transit_moon_long, 2)
        },
        "mood": {
            "house": mood_house,
            "name": mood_data["name"],
            "interpretation": mood_data["mood"],
            "description": mood_data["description"]
        },
        "fuel": {
            "house": fuel_house,
            "name": fuel_data["name"],
            "level": fuel_data["level"],
            "description": fuel_data["description"]
        },
        "luck": {
            "tara_name": tara_name,
            "tara_number": tara_num,
            "status": luck_data["status"],
            "description": luck_data["description"]
        },
        "overall_prediction": overall
    }
