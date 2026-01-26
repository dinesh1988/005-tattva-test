"""
Simple yoga test - manually check yoga conditions.

This test demonstrates how to check for yogas by:
1. Getting planet longitudes
2. Calculating house positions
3. Checking yoga conditions

Run: python tests/test_yogas_simple.py
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.time import AstroTime
from logic.consts import Planet
from logic import calculate


def create_time(date_str, lat, lon, tz_offset="+05:30"):
    """
    Create AstroTime object from string.
    
    Args:
        date_str: "23:40 13/06/1994" format
        lat: Latitude (e.g., 13.0827 for Chennai)
        lon: Longitude (e.g., 80.2707 for Chennai)
        tz_offset: Timezone offset string (e.g., "+05:30")
    """
    # Parse datetime
    dt = datetime.strptime(date_str, "%H:%M %d/%m/%Y")
    
    # Add timezone
    hours, minutes = map(int, tz_offset.replace('+', '').split(':'))
    tz = pytz.FixedOffset(hours * 60 + minutes)
    dt = tz.localize(dt)
    
    return AstroTime(dt, lat, lon)


def test_chart_1():
    """Test Chart 1: 23:40 13/06/1994, Chennai"""
    print("\n" + "="*70)
    print("TEST CHART 1: Birth at Chennai")
    print("="*70)
    print("Time: 23:40, Date: 13/06/1994, Location: Chennai")
    print("Latitude: 13.0827°N, Longitude: 80.2707°E, Timezone: +05:30")
    
    # Create time object (Chennai coordinates)
    time = create_time("23:40 13/06/1994", 13.0827, 80.2707)
    
    # Get planetary positions
    sun_long = calculate.get_planet_longitude(Planet.Sun, time)
    moon_long = calculate.get_planet_longitude(Planet.Moon, time)
    mars_long = calculate.get_planet_longitude(Planet.Mars, time)
    mercury_long = calculate.get_planet_longitude(Planet.Mercury, time)
    jupiter_long = calculate.get_planet_longitude(Planet.Jupiter, time)
    venus_long = calculate.get_planet_longitude(Planet.Venus, time)
    saturn_long = calculate.get_planet_longitude(Planet.Saturn, time)
    lagna_long = calculate.get_lagnam(time)
    
    # Convert to signs (0-11: Aries to Pisces)
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    print("\nPLANETARY POSITIONS:")
    print(f"Lagna:   {signs[int(lagna_long // 30)]:12} at {lagna_long:.2f}°")
    print(f"Sun:     {signs[int(sun_long // 30)]:12} at {sun_long:.2f}°")
    print(f"Moon:    {signs[int(moon_long // 30)]:12} at {moon_long:.2f}°")
    print(f"Mars:    {signs[int(mars_long // 30)]:12} at {mars_long:.2f}°")
    print(f"Mercury: {signs[int(mercury_long // 30)]:12} at {mercury_long:.2f}°")
    print(f"Jupiter: {signs[int(jupiter_long // 30)]:12} at {jupiter_long:.2f}°")
    print(f"Venus:   {signs[int(venus_long // 30)]:12} at {venus_long:.2f}°")
    print(f"Saturn:  {signs[int(saturn_long // 30)]:12} at {saturn_long:.2f}°")
    
    # Calculate signs
    moon_sign = int(moon_long // 30)
    jupiter_sign = int(jupiter_long // 30)
    mercury_sign = int(mercury_long // 30)
    venus_sign = int(venus_long // 30)
    mars_sign = int(mars_long // 30)
    saturn_sign = int(saturn_long // 30)
    lagna_sign = int(lagna_long // 30)
    
    # CHECK YOGAS
    print("\n" + "-"*70)
    print("YOGA DETECTION:")
    print("-"*70)
    
    # 1. GAJAKESARI YOGA
    print("\n1. GajaKesari Yoga (Jupiter in kendra from Moon):")
    moon_jupiter_house = ((jupiter_sign - moon_sign) % 12) + 1
    print(f"   Moon: {signs[moon_sign]}, Jupiter: {signs[jupiter_sign]}")
    print(f"   Jupiter in house {moon_jupiter_house} from Moon")
    if moon_jupiter_house in [1, 4, 7, 10]:
        print("   ✓ GAJAKESARI YOGA PRESENT")
        print("   Effect: Wealth, wisdom, reputation, success")
    else:
        print("   ✗ Not present")
    
    # 2. BHADRA YOGA (Mercury in kendra in own/exalted sign)
    print("\n2. Bhadra Yoga (Mercury in kendra in own/exalted sign):")
    mercury_house = ((mercury_sign - lagna_sign) % 12) + 1
    mercury_in_kendra = mercury_house in [1, 4, 7, 10]
    mercury_own_exalted = mercury_sign in [2, 5]  # Gemini=2, Virgo=5
    print(f"   Mercury: {signs[mercury_sign]}, House: {mercury_house} from Lagna")
    print(f"   In kendra: {mercury_in_kendra}, In own/exalted sign: {mercury_own_exalted}")
    if mercury_in_kendra and mercury_own_exalted:
        print("   ✓ BHADRA YOGA PRESENT")
        print("   Effect: Intelligence, learning, eloquence")
    else:
        print("   ✗ Not present")
    
    # 3. HAMSA YOGA (Jupiter in kendra in own/exalted sign)
    print("\n3. Hamsa Yoga (Jupiter in kendra in own/exalted sign):")
    jupiter_house = ((jupiter_sign - lagna_sign) % 12) + 1
    jupiter_in_kendra = jupiter_house in [1, 4, 7, 10]
    jupiter_own_exalted = jupiter_sign in [3, 8, 11]  # Cancer=3, Sagittarius=8, Pisces=11
    print(f"   Jupiter: {signs[jupiter_sign]}, House: {jupiter_house} from Lagna")
    print(f"   In kendra: {jupiter_in_kendra}, In own/exalted sign: {jupiter_own_exalted}")
    if jupiter_in_kendra and jupiter_own_exalted:
        print("   ✓ HAMSA YOGA PRESENT")
        print("   Effect: Righteousness, spirituality, happiness")
    else:
        print("   ✗ Not present")
    
    # 4. MALAVYA YOGA (Venus in kendra in own/exalted sign)
    print("\n4. Malavya Yoga (Venus in kendra in own/exalted sign):")
    venus_house = ((venus_sign - lagna_sign) % 12) + 1
    venus_in_kendra = venus_house in [1, 4, 7, 10]
    venus_own_exalted = venus_sign in [1, 6, 11]  # Taurus=1, Libra=6, Pisces=11
    print(f"   Venus: {signs[venus_sign]}, House: {venus_house} from Lagna")
    print(f"   In kendra: {venus_in_kendra}, In own/exalted sign: {venus_own_exalted}")
    if venus_in_kendra and venus_own_exalted:
        print("   ✓ MALAVYA YOGA PRESENT")
        print("   Effect: Luxury, beauty, artistic talents")
    else:
        print("   ✗ Not present")
    
    # 5. RUCHAKA YOGA (Mars in kendra in own/exalted sign)
    print("\n5. Ruchaka Yoga (Mars in kendra in own/exalted sign):")
    mars_house = ((mars_sign - lagna_sign) % 12) + 1
    mars_in_kendra = mars_house in [1, 4, 7, 10]
    mars_own_exalted = mars_sign in [0, 7, 9]  # Aries=0, Scorpio=7, Capricorn=9
    print(f"   Mars: {signs[mars_sign]}, House: {mars_house} from Lagna")
    print(f"   In kendra: {mars_in_kendra}, In own/exalted sign: {mars_own_exalted}")
    if mars_in_kendra and mars_own_exalted:
        print("   ✓ RUCHAKA YOGA PRESENT")
        print("   Effect: Warrior spirit, leadership, courage")
    else:
        print("   ✗ Not present")
    
    # 6. SASHA YOGA (Saturn in kendra in own/exalted sign)
    print("\n6. Sasha Yoga (Saturn in kendra in own/exalted sign):")
    saturn_house = ((saturn_sign - lagna_sign) % 12) + 1
    saturn_in_kendra = saturn_house in [1, 4, 7, 10]
    saturn_own_exalted = saturn_sign in [6, 9, 10]  # Libra=6, Capricorn=9, Aquarius=10
    print(f"   Saturn: {signs[saturn_sign]}, House: {saturn_house} from Lagna")
    print(f"   In kendra: {saturn_in_kendra}, In own/exalted sign: {saturn_own_exalted}")
    if saturn_in_kendra and saturn_own_exalted:
        print("   ✓ SASHA YOGA PRESENT")
        print("   Effect: Authority, discipline, long life")
    else:
        print("   ✗ Not present")


def test_chart_2():
    """Test Chart 2: India Independence"""
    print("\n\n" + "="*70)
    print("TEST CHART 2: India Independence Day")
    print("="*70)
    print("Time: 00:00 (midnight), Date: 15/08/1947, Location: Delhi")
    print("Latitude: 28.6139°N, Longitude: 77.2090°E, Timezone: +05:30")
    
    # Delhi coordinates
    time = create_time("00:00 15/08/1947", 28.6139, 77.2090)
    
    # Get key positions
    moon_long = calculate.get_planet_longitude(Planet.Moon, time)
    jupiter_long = calculate.get_planet_longitude(Planet.Jupiter, time)
    lagna_long = calculate.get_lagnam(time)
    
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    print(f"\nLagna:   {signs[int(lagna_long // 30)]}")
    print(f"Moon:    {signs[int(moon_long // 30)]}")
    print(f"Jupiter: {signs[int(jupiter_long // 30)]}")
    
    moon_sign = int(moon_long // 30)
    jupiter_sign = int(jupiter_long // 30)
    moon_jupiter_house = ((jupiter_sign - moon_sign) % 12) + 1
    
    print(f"\nGajaKesari Check: Jupiter in house {moon_jupiter_house} from Moon")
    if moon_jupiter_house in [1, 4, 7, 10]:
        print("✓ GAJAKESARI YOGA PRESENT in India's birth chart!")
    else:
        print("✗ Not present")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" VEDASTRO YOGA DETECTION TEST")
    print(" Manual calculation of yoga conditions")
    print("="*70)
    
    try:
        test_chart_1()
        test_chart_2()
        
        print("\n\n" + "="*70)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nHow to use this:")
        print("1. Modify create_time() parameters for your birth details")
        print("2. Run: python tests/test_yogas_simple.py")
        print("3. Check which yogas are present in your chart")
        print("\nNext step: Update yogas.py functions to use AstroTime API")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
