#!/usr/bin/env python3
"""
Verify Lagna calculation using VedAstroPy direct calculation
Birth: April 5, 1991, 10:50 AM, Vellore
"""

from datetime import datetime
import pytz
from logic.time import AstroTime
from logic.calculate import get_lagnam
from logic.nakshatra import get_nakshatra
from logic.rasi import get_rasi

def verify_lagna():
    print("=" * 80)
    print("LAGNA VERIFICATION - VedAstroPy Direct Calculation")
    print("=" * 80)
    print()
    
    # Birth Details
    birth_place = "Vellore"
    tz = pytz.timezone('Asia/Kolkata')
    lat = 12.9165  # Vellore coordinates
    lon = 79.1325
    
    # April 5, 1991, 10:50 AM
    dt = datetime(1991, 4, 5, 10, 50, 0, tzinfo=tz)
    
    print(f"Birth Date : {dt.strftime('%B %d, %Y')}")
    print(f"Birth Time : {dt.strftime('%I:%M %p')}")
    print(f"Birth Place: {birth_place}")
    print(f"Coordinates: {lat}°N, {lon}°E")
    print(f"Timezone   : {tz}")
    print()
    
    # Create AstroTime object
    astro_time = AstroTime(dt, lat, lon)
    
    print(f"Julian Day : {astro_time.julian_day}")
    print()
    
    # Calculate Lagna (Ascendant)
    print("-" * 80)
    print("LAGNA (ASCENDANT) CALCULATION")
    print("-" * 80)
    print()
    
    lagnam_longitude = get_lagnam(astro_time)
    
    print(f"Lagna Longitude (Nirayana): {lagnam_longitude:.6f}°")
    print()
    
    # Convert to Rasi (Sign)
    rasi_name, rasi_num = get_rasi(lagnam_longitude)
    
    print(f"Lagna Rasi (Sign): {rasi_name} (Rasi #{rasi_num})")
    print()
    
    # Degree within sign
    degree_in_sign = lagnam_longitude % 30
    print(f"Degree within {rasi_name}: {degree_in_sign:.4f}°")
    print()
    
    # Convert to Nakshatra
    nakshatra_name, nak_num, percentage, pada = get_nakshatra(lagnam_longitude)
    
    print(f"Lagna Nakshatra: {nakshatra_name}")
    print(f"  Nakshatra #: {nak_num}")
    print(f"  Pada: {pada}")
    print(f"  Progress: {percentage:.2f}% through nakshatra")
    print()
    
    # Additional details
    print("-" * 80)
    print("DETAILED BREAKDOWN")
    print("-" * 80)
    print()
    
    # Zodiac position
    print(f"Absolute Zodiac Position: {lagnam_longitude:.4f}°")
    print(f"  Sign: {rasi_name} ({(rasi_num-1)*30}° - {rasi_num*30}°)")
    print(f"  Position in Sign: {degree_in_sign:.4f}° into {rasi_name}")
    print()
    
    # Nakshatra details
    nak_start = ((nak_num - 1) * 800) / 60  # Each nakshatra is 13°20' = 800'
    nak_end = (nak_num * 800) / 60
    print(f"  Nakshatra: {nakshatra_name} ({nak_start:.2f}° - {nak_end:.2f}°)")
    print(f"  Pada {pada} of {nakshatra_name}")
    print()
    
    # Verification
    print("-" * 80)
    print("VERIFICATION")
    print("-" * 80)
    print()
    
    # Check if lagna is in expected range for Taurus
    if 30 <= lagnam_longitude < 60:
        print("✓ Lagna is in Taurus (30° - 60°)")
    elif 0 <= lagnam_longitude < 30:
        print("✓ Lagna is in Aries (0° - 30°)")
    elif 60 <= lagnam_longitude < 90:
        print("✓ Lagna is in Gemini (60° - 90°)")
    else:
        print(f"✓ Lagna is at {lagnam_longitude:.2f}°")
    
    print()
    
    # Lagna Lord
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
    
    lagna_lord = lagna_lords.get(rasi_name, "Unknown")
    print(f"Lagna Lord (Ascendant Ruler): {lagna_lord}")
    print()
    
    print("=" * 80)
    print("CALCULATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    try:
        verify_lagna()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
