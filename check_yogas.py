#!/usr/bin/env python3
"""
VedAstro - Check Planetary Combinations and Yogas
Birth: June 7th 1988, 8:40 PM, Chennai

Note: This Python version calculates basic planetary positions and key combinations.
For the complete 370+ yoga calculations, use the .NET Library Console app.
"""

from datetime import datetime
import pytz
from logic.time import AstroTime
from logic.consts import Planet
from logic.nakshatra import get_nakshatra
from logic.calculate import get_planet_longitude, get_lagnam
from logic.rasi import RASIS, get_rasi
from logic.panchang import get_tithi, get_nitya_yoga_details
from logic.shadbala import get_all_planet_shadbala, is_planet_strong
from logic.varga import get_d9_navamsa

def main():
    print("=" * 80)
    print("VedAstro - Planetary Positions & Key Yogas Calculator")
    print("=" * 80)
    print()
    
    # Birth Details
    birth_place = "Vellore"
    tz = pytz.timezone('Asia/Kolkata')
    lat = 12.9165
    lon = 79.1325
    
    # April 5th 1991, 10:50 AM
    dt = datetime(1991, 4, 5, 10, 50, 0, tzinfo=tz)
    
    astro_time = AstroTime(dt, lat, lon)
    
    print(f"Birth Date : {dt.strftime('%B %d, %Y')}")
    print(f"Birth Time : {dt.strftime('%I:%M %p')}")
    print(f"Birth Place: {birth_place} ({lat}°N, {lon}°E)")
    print(f"Timezone   : IST (+05:30)")
    print(f"Ayanamsa   : Lahiri")
    print()
    
    # ========== PART 1: PLANETARY POSITIONS ==========
    print("=" * 80)
    print("PLANETARY POSITIONS")
    print("=" * 80)
    print()
    
    # Calculate Ascendant
    lagnam_long = get_lagnam(astro_time)
    lagnam_rasi_name, lagnam_rasi_num = get_rasi(lagnam_long)
    lagnam_nak, _, lagnam_perc, lagnam_pada = get_nakshatra(lagnam_long)
    
    print(f"{'Ascendant (Lagna)':<20} : {lagnam_rasi_name:<15} [{lagnam_long:.2f}°]")
    print(f"{'Lagna Nakshatra':<20} : {lagnam_nak} - Pada {lagnam_pada} ({lagnam_perc:.1f}%)")
    print()
    
    # Calculate all planet positions
    planets = [
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
    
    planet_data = {}
    
    for planet, name in planets:
        longitude = get_planet_longitude(planet, astro_time)
        rasi_name, rasi_num = get_rasi(longitude)
        nakshatra_name, nak_num, nak_perc, pada = get_nakshatra(longitude)
        
        planet_data[name] = {
            'longitude': longitude,
            'rasi': rasi_name,
            'rasi_num': rasi_num,
            'nakshatra': nakshatra_name,
            'nak_num': nak_num,
            'pada': pada
        }
        
        print(f"{name:<20} : {rasi_name:<15} in {nakshatra_name:<15} [{longitude:.2f}°]")
    
    print()
    
    # ========== PART 2: PANCHANG ELEMENTS ==========
    print("=" * 80)
    print("PANCHANG ELEMENTS")
    print("=" * 80)
    print()
    
    sun_long = planet_data['Sun']['longitude']
    moon_long = planet_data['Moon']['longitude']
    
    # Tithi
    tithi_name, tithi_num, tithi_perc = get_tithi(sun_long, moon_long)
    print(f"Tithi          : {tithi_name} ({tithi_perc:.1f}% complete)")
    
    # Yoga
    yoga_details = get_nitya_yoga_details(sun_long, moon_long)
    auspicious_mark = "[+]" if yoga_details['is_auspicious'] else "[-]"
    print(f"Nitya Yoga     : {yoga_details['name']} {auspicious_mark}")
    print(f"  Deity        : {yoga_details['deity']}")
    print(f"  Nature       : {yoga_details['nature']}")
    print(f"  Effect       : {yoga_details['effect']}")
    print()
    
    # ========== PART 3: KEY YOGA ANALYSIS ==========
    print("=" * 80)
    print("KEY YOGA ANALYSIS")
    print("=" * 80)
    print()
    
    moon_nak = planet_data['Moon']['nakshatra']
    print(f"Birth Nakshatra (Janma Nakshatra): {moon_nak}")
    print(f"Birth Rasi (Janma Rasi)          : {planet_data['Moon']['rasi']}")
    print()
    
    # ========== PART 4: HOUSE PLACEMENTS ==========
    print("=" * 80)
    print("HOUSE PLACEMENTS (From Ascendant)")
    print("=" * 80)
    print()
    
    # Calculate house for each planet
    lagna_rasi_num = lagnam_rasi_num
    
    for name, data in planet_data.items():
        # Calculate house: (planet_rasi - lagna_rasi + 1)
        # In Vedic astrology, house 1 starts from the Lagna rasi
        house_num = ((data['rasi_num'] - lagna_rasi_num) % 12) + 1
        if house_num <= 0:
            house_num += 12
            
        print(f"{name:<15} in House {house_num:2} ({data['rasi']})")
    
    print()
    
    # ========== PART 5: SHADBALA (PLANETARY STRENGTHS) ==========
    print("=" * 80)
    print("SHADBALA - PLANETARY STRENGTHS")
    print("=" * 80)
    print()
    
    try:
        shadbala_data = get_all_planet_shadbala(astro_time)
        
        print(f"{'Planet':<15} {'Total Shadbala':<20} {'Strength'}")
        print("-" * 60)
        
        for planet_name, bala_value in shadbala_data.items():
            # Check if planet is strong
            try:
                is_strong = is_planet_strong(planet_name, bala_value)
                strength_marker = "✓ Strong" if is_strong else "✗ Weak"
            except:
                strength_marker = "○ Moderate"
            
            print(f"{planet_name:<15} {bala_value:>8.2f} Rupas       {strength_marker}")
        
        print()
    except Exception as e:
        print(f"Note: Shadbala calculation requires additional data. Error: {e}")
        print()
    
    # ========== PART 6: SPECIAL COMBINATIONS ==========
    print("=" * 80)
    print("SPECIAL COMBINATIONS DETECTED")
    print("=" * 80)
    print()
    
    yogas_found = []
    
    # Check for Gaja Kesari Yoga (Jupiter and Moon in kendras)
    jupiter_rasi = planet_data['Jupiter']['rasi_num']
    moon_rasi = planet_data['Moon']['rasi_num']
    moon_jupiter_diff = abs(jupiter_rasi - moon_rasi)
    if moon_jupiter_diff in [0, 3, 6, 9]:  # Same house or kendra (1,4,7,10)
        yogas_found.append("✓ Gaja Kesari Yoga: Jupiter and Moon in mutual kendras (good for wealth & wisdom)")
    
    # Check for Chandra Mangala Yoga (Moon-Mars conjunction or aspect)
    mars_rasi = planet_data['Mars']['rasi_num']
    if mars_rasi == moon_rasi:
        yogas_found.append("✓ Chandra Mangala Yoga: Moon and Mars conjunct (wealth accumulation)")
    
    # Check for Neecha Bhanga (Debilitation cancellation)
    # Sun debilitated in Libra
    if planet_data['Sun']['rasi'] == 'Libra':
        # Check if Saturn (lord of Libra) is in kendra
        saturn_house = ((planet_data['Saturn']['rasi_num'] - lagna_rasi_num) % 12) + 1
        if saturn_house in [1, 4, 7, 10]:
            yogas_found.append("✓ Neecha Bhanga Raja Yoga: Sun's debilitation cancelled")
    
    # Moon debilitated in Scorpio
    if planet_data['Moon']['rasi'] == 'Scorpio':
        mars_house = ((planet_data['Mars']['rasi_num'] - lagna_rasi_num) % 12) + 1
        if mars_house in [1, 4, 7, 10]:
            yogas_found.append("✓ Neecha Bhanga Raja Yoga: Moon's debilitation cancelled")
    
    # Check for Pancha Mahapurusha Yogas
    # Hamsa Yoga - Jupiter in kendra in own/exaltation
    jupiter_house = ((planet_data['Jupiter']['rasi_num'] - lagna_rasi_num) % 12) + 1
    if jupiter_house in [1, 4, 7, 10]:
        if planet_data['Jupiter']['rasi'] in ['Sagittarius', 'Pisces', 'Cancer']:
            yogas_found.append("✓ Hamsa Yoga: Jupiter strong in kendra (great personality & wisdom)")
    
    # Malavya Yoga - Venus in kendra in own/exaltation
    venus_house = ((planet_data['Venus']['rasi_num'] - lagna_rasi_num) % 12) + 1
    if venus_house in [1, 4, 7, 10]:
        if planet_data['Venus']['rasi'] in ['Taurus', 'Libra', 'Pisces']:
            yogas_found.append("✓ Malavya Yoga: Venus strong in kendra (luxury & comfort)")
    
    # Sasha Yoga - Saturn in kendra in own/exaltation
    saturn_house = ((planet_data['Saturn']['rasi_num'] - lagna_rasi_num) % 12) + 1
    if saturn_house in [1, 4, 7, 10]:
        if planet_data['Saturn']['rasi'] in ['Capricorn', 'Aquarius', 'Libra']:
            yogas_found.append("✓ Sasha Yoga: Saturn strong in kendra (authority & discipline)")
    
    # Ruchaka Yoga - Mars in kendra in own/exaltation
    mars_house = ((planet_data['Mars']['rasi_num'] - lagna_rasi_num) % 12) + 1
    if mars_house in [1, 4, 7, 10]:
        if planet_data['Mars']['rasi'] in ['Aries', 'Scorpio', 'Capricorn']:
            yogas_found.append("✓ Ruchaka Yoga: Mars strong in kendra (courage & leadership)")
    
    # Bhadra Yoga - Mercury in kendra in own/exaltation
    mercury_house = ((planet_data['Mercury']['rasi_num'] - lagna_rasi_num) % 12) + 1
    if mercury_house in [1, 4, 7, 10]:
        if planet_data['Mercury']['rasi'] in ['Gemini', 'Virgo']:
            yogas_found.append("✓ Bhadra Yoga: Mercury strong in kendra (intelligence & communication)")
    
    # Display found yogas
    if yogas_found:
        for yoga in yogas_found:
            print(yoga)
        print()
    else:
        print("No major classical yogas detected at basic level.")
        print()
    
    # ========== SUMMARY ==========
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Classical Yogas Detected: {len(yogas_found)}")
    print()
    print("Note: This is a basic analysis. The complete VedAstro system")
    print("checks 370+ planetary combinations using the .NET Library.")
    print()
    print("To get the full analysis:")
    print("1. Use the Console project in the VedAstro solution")
    print("2. Or use the VedAstro API (requires subscription)")
    print("3. Or run the Desktop application")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure Swiss Ephemeris files are in the 'ephe' folder.")
