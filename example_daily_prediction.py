"""
Example: Daily Prediction using Muhurtha Module

This example shows how to generate daily predictions combining:
- Muhurtha (Activity timing)
- Pancha Pakshi (Favorable hours)
- Panchang (Day quality)
"""

from logic.calculate import get_planet_longitude
from logic.consts import Planet
from logic.time import AstroTime
from logic.muhurtha import get_day_quality_summary, get_best_activities_for_day, get_activities_to_avoid
from logic.pancha_pakshi import get_daily_summary
from logic.nakshatra import get_nakshatra
from datetime import datetime
import pytz


def get_daily_prediction(birth_dt, birth_lat, birth_lon, prediction_date=None):
    """
    Generate a complete daily prediction
    
    Args:
        birth_dt: Birth datetime (timezone aware)
        birth_lat: Birth latitude
        birth_lon: Birth longitude
        prediction_date: Date for prediction (defaults to today)
    """
    if prediction_date is None:
        prediction_date = datetime.now(birth_dt.tzinfo)
    
    # Create AstroTime for prediction date
    pred_time = AstroTime(prediction_date, birth_lat, birth_lon)
    
    # Get current planetary positions
    sun_long = get_planet_longitude(Planet.Sun, pred_time)
    moon_long = get_planet_longitude(Planet.Moon, pred_time)
    moon_nak, _, _, _ = get_nakshatra(moon_long)
    
    weekday = (prediction_date.weekday() + 1) % 7  # Convert to 0=Sunday
    
    # 1. MUHURTHA - Activity timing
    print("="*70)
    print(f"DAILY PREDICTION FOR {prediction_date.strftime('%A, %B %d, %Y')}")
    print("="*70)
    print()
    
    # Day Quality Summary
    summary = get_day_quality_summary(sun_long, moon_long, moon_nak, weekday)
    print(f"[*] OVERALL DAY QUALITY: {summary['day_quality']}")
    print(f"   Score: {summary['overall_score']}/100")
    print(f"   Advice: {summary['advice']}")
    print()
    
    print(f"[+] PANCHANG:")
    print(f"   Tithi: {summary['panchang']['tithi']}")
    print(f"   Nakshatra: {summary['panchang']['nakshatra']}")
    print(f"   Yoga: {summary['panchang']['yoga']}")
    print()
    
    # Best Activities
    print("[OK] FAVORABLE ACTIVITIES:")
    favorable = get_best_activities_for_day(sun_long, moon_long, moon_nak, weekday, threshold=50)
    if favorable:
        for i, act in enumerate(favorable[:5], 1):  # Top 5
            print(f"   {i}. {act['activity']}: {act['score']}/100")
    else:
        print("   None today - Be cautious with new ventures")
    print()
    
    # Activities to Avoid
    avoid = get_activities_to_avoid(sun_long, moon_long, moon_nak, weekday, threshold=30)
    if avoid:
        print("[!] AVOID TODAY:")
        for i, act in enumerate(avoid[:3], 1):  # Top 3 worst
            print(f"   {i}. {act['activity']}: {act['score']}/100")
        print()
    
    # 2. PANCHA PAKSHI - Favorable hours
    print("[TIME] FAVORABLE TIME PERIODS (Pancha Pakshi):")
    birth_time = AstroTime(birth_dt, birth_lat, birth_lon)
    birth_moon = get_planet_longitude(Planet.Moon, birth_time)
    birth_nak_name, birth_nak_num, _, _ = get_nakshatra(birth_moon)
    
    # Need birth sun for tithi
    birth_sun = get_planet_longitude(Planet.Sun, birth_time)
    from logic.panchang import get_tithi
    _, birth_tithi_num, _ = get_tithi(birth_sun, birth_moon)
    
    # Get day summary
    pakshi_summary = get_daily_summary(birth_nak_num, birth_tithi_num, prediction_date)
    print(f"   Bird: {pakshi_summary['birth_bird']}")
    print(f"   Ruling Periods: {pakshi_summary['summary']['ruling_periods']}/10")
    print(f"   Eating Periods: {pakshi_summary['summary']['eating_periods']}/10")
    print(f"   Favorable Total: {pakshi_summary['summary']['favorable_periods']}/10")
    print()
    
    print("="*70)
    print(f"[*] SUMMARY: {summary['best_for']} is favored today.")
    print(f"   Focus on: {favorable[0]['activity'] if favorable else 'Routine tasks'}")
    print("="*70)


if __name__ == "__main__":
    # Example: Person born June 7, 1988, 8:40 PM in Chennai
    ist = pytz.timezone('Asia/Kolkata')
    birth_datetime = ist.localize(datetime(1988, 6, 7, 20, 40, 0))
    birth_lat = 13.0827  # Chennai
    birth_lon = 80.2707
    
    # Get prediction for today
    get_daily_prediction(birth_datetime, birth_lat, birth_lon)
    
    print("\n\n")
    
    # Get prediction for a specific date
    prediction_date = ist.localize(datetime(2026, 1, 26, 12, 0, 0))
    print("=" * 70)
    print("PREDICTION FOR SPECIFIC DATE:")
    print("=" * 70)
    get_daily_prediction(birth_datetime, birth_lat, birth_lon, prediction_date)
