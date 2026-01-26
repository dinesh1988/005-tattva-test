#!/usr/bin/env python3
"""
Call VedAstroPy API directly to verify lagna
Birth: April 5, 1991, 10:50 AM, Vellore
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import pytz
from logic.time import AstroTime
from logic.calculate import get_planet_longitude, get_lagnam
from logic.consts import Planet
from logic.nakshatra import get_nakshatra
from logic.geolocation import get_location

def get_chart_data():
    print("=" * 80)
    print("VedAstroPy API - Birth Chart Calculation")
    print("=" * 80)
    print()
    
    # Birth data
    birth_date = "1991-04-05"
    birth_time = "10:50"
    birth_place = "Vellore"
    
    print(f"Birth Date : {birth_date}")
    print(f"Birth Time : {birth_time}")
    print(f"Birth Place: {birth_place}")
    print()
    
    # Use specific coordinates
    lat = 12.51
    lon = 79.2
    tz_name = "Asia/Kolkata"
    print(f"Coordinates: {lat}°N, {lon}°E")
    print(f"Timezone   : {tz_name}")
    
    print()
    
    # Parse datetime
    tz = pytz.timezone(tz_name)
    date_parts = birth_date.split('-')
    time_parts = birth_time.split(':')
    
    dt = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
        int(time_parts[0]), int(time_parts[1]), 0,
        tzinfo=tz
    )
    
    # Create AstroTime
    astro_time = AstroTime(dt, lat, lon)
    
    print(f"Julian Day : {astro_time.julian_day}")
    print()
    
    # Define signs
    SIGNS = ['Aries (Mesha)', 'Taurus (Vrishabha)', 'Gemini (Mithuna)', 
             'Cancer (Karka)', 'Leo (Simha)', 'Virgo (Kanya)',
             'Libra (Tula)', 'Scorpio (Vrishchika)', 'Sagittarius (Dhanu)', 
             'Capricorn (Makara)', 'Aquarius (Kumbha)', 'Pisces (Meena)']
    
    # Get Ascendant (Lagna)
    print("-" * 80)
    print("ASCENDANT (LAGNA)")
    print("-" * 80)
    print()
    
    lagna = get_lagnam(astro_time)
    nak_name, nak_num, nak_percentage, pada = get_nakshatra(lagna)
    
    lagna_sign = SIGNS[int(lagna / 30)]
    degree_in_sign = lagna % 30
    
    print(f"Longitude       : {lagna:.4f}°")
    print(f"Sign            : {lagna_sign}")
    print(f"Degree in Sign  : {degree_in_sign:.4f}°")
    print(f"Nakshatra       : {nak_name}")
    print(f"Nakshatra Pada  : {pada}")
    print(f"Nakshatra %     : {nak_percentage:.2f}%")
    print()
    
    # Get all planet positions
    print("-" * 80)
    print("ALL PLANETARY POSITIONS")
    print("-" * 80)
    print()
    
    planets_data = {}
    planet_list = [
        (Planet.Sun, "Sun"),
        (Planet.Moon, "Moon"),
        (Planet.Mars, "Mars"),
        (Planet.Mercury, "Mercury"),
        (Planet.Jupiter, "Jupiter"),
        (Planet.Venus, "Venus"),
        (Planet.Saturn, "Saturn"),
        (Planet.Rahu, "Rahu"),
        (Planet.Ketu, "Ketu")
    ]
    
    for planet, name in planet_list:
        longitude = get_planet_longitude(planet, astro_time)
        nakshatra_name, nak_num, nak_percentage, pada = get_nakshatra(longitude)
        
        sign = SIGNS[int(longitude / 30)]
        degree = longitude % 30
        
        planets_data[name] = {
            "longitude": longitude,
            "sign": sign,
            "degree_in_sign": degree,
            "nakshatra": nakshatra_name,
            "nakshatra_pada": pada
        }
        
        print(f"{name:<12} : {longitude:>7.2f}° | {sign:<25} | {nakshatra_name:<20} Pada {pada}")
    
    print()
    
    # House placement from Lagna
    print("-" * 80)
    print("HOUSE PLACEMENTS (From Lagna)")
    print("-" * 80)
    print()
    
    lagna_sign_num = int(lagna / 30) + 1
    
    for name, data in planets_data.items():
        planet_sign_num = int(data['longitude'] / 30) + 1
        house_num = ((planet_sign_num - lagna_sign_num) % 12) + 1
        if house_num <= 0:
            house_num += 12
        
        print(f"{name:<12} in House {house_num:>2} ({data['sign']})")
    
    print()
    
    # Lagna Lord
    print("-" * 80)
    print("LAGNA LORD")
    print("-" * 80)
    print()
    
    lagna_lords = {
        "Aries (Mesha)": "Mars",
        "Taurus (Vrishabha)": "Venus",
        "Gemini (Mithuna)": "Mercury",
        "Cancer (Karka)": "Moon",
        "Leo (Simha)": "Sun",
        "Virgo (Kanya)": "Mercury",
        "Libra (Tula)": "Venus",
        "Scorpio (Vrishchika)": "Mars",
        "Sagittarius (Dhanu)": "Jupiter",
        "Capricorn (Makara)": "Saturn",
        "Aquarius (Kumbha)": "Saturn",
        "Pisces (Meena)": "Jupiter"
    }
    
    lagna_lord = lagna_lords.get(lagna_sign, "Unknown")
    print(f"Lagna Sign: {lagna_sign}")
    print(f"Lagna Lord: {lagna_lord}")
    
    if lagna_lord in planets_data:
        lord_data = planets_data[lagna_lord]
        lord_sign_num = int(lord_data['longitude'] / 30) + 1
        lord_house = ((lord_sign_num - lagna_sign_num) % 12) + 1
        print(f"Lagna Lord Position: House {lord_house} in {lord_data['sign']}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        get_chart_data()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
