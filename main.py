from datetime import datetime
import pytz
from logic.time import AstroTime
from logic.consts import Planet
from logic.nakshatra import get_nakshatra, get_tara_bala
from logic.dasa import get_vimshottari_dasa, get_vimshottari_dasa_full
from logic.ashtakavarga import get_sarvashtakavarga_points
from logic.panchang import get_tithi, get_yoga, get_nitya_yoga_details
from logic.rasi import RASIS, get_rasi, get_gochara_house
from logic.varga import VARGA_CHARTS, get_d9_navamsa
from logic.kakshya import get_kakshya
from logic.jaimini import get_chara_dasa, get_chara_karakas, get_all_arudhas, get_chara_dasa_antardasa
from logic.avastha import get_all_avasthas, get_dignity_status, get_bala_avastha, get_deeptadi_avastha
from logic.varshaphal import get_varshaphal_summary, get_muntha, get_year_lord, TAJIKA_YOGAS, SAHAMS
from logic.geolocation import get_location, get_coordinates, search_cities
from logic.pancha_pakshi import (
    get_pancha_pakshi, get_birth_bird, get_daily_summary, 
    get_favorable_periods, BIRD_NAMES, ACTIVITY_INFO
)
from logic.shadbala import (
    get_all_planet_shadbala, get_shadbala_summary, get_full_shadbala_report,
    get_shadbala_pinda, is_planet_strong, STRENGTH_REQUIREMENTS
)
import sys

# Import the main engine (SwissEph)
from logic.calculate import get_planet_longitude, get_lagnam
ENGINE = "SwissEph"

def main():
    print(f"VedAstro Python Engine Demo (Using {ENGINE})")
    
    # 1. Define a Time and Location
    # DOB: June 7th 1988, 8:40 PM, Chennai
    
    # Get coordinates from city name using geolocation
    birth_place = "Chennai"
    location = get_location(birth_place)
    
    if location:
        lat = location['latitude']
        lon = location['longitude']
        tz = pytz.timezone(location['timezone'])
        print(f"Birth Place: {location['name']}")
        print(f"Coordinates: {lat}°N, {lon}°E")
        print(f"Timezone: {location['timezone']}")
    else:
        # Fallback to manual coordinates
        tz = pytz.timezone('Asia/Kolkata')
        lat = 13.0827
        lon = 80.2707
    
    dt = datetime(1988, 6, 7, 20, 40, 0, tzinfo=tz)
    
    astro_time = AstroTime(dt, lat, lon)
    print(f"Time: {dt}")
    print(f"Julian Day: {astro_time.julian_day}")
    print(f"Time: {dt}")
    if ENGINE == "SwissEph":
        print(f"Julian Day: {astro_time.julian_day}")
    
    # 2. Calculate Planet Longitudes
    try:
        # Calculate Lagnam (Ascendant)
        lagnam_long = get_lagnam(astro_time)
        lagnam_nak, _, lagnam_perc, lagnam_pada = get_nakshatra(lagnam_long)
        print(f"Lagnam (Ascendant): {lagnam_long:.4f}")
        print(f"Lagnam Nakshatra: {lagnam_nak} ({lagnam_perc:.2f}%) - Pada {lagnam_pada}")
        print("-" * 30)

        sun_long = get_planet_longitude(Planet.Sun, astro_time)
        moon_long = get_planet_longitude(Planet.Moon, astro_time)
        jupiter_long = get_planet_longitude(Planet.Jupiter, astro_time)
        
        print(f"Sun Longitude: {sun_long:.4f}")
        print(f"Moon Longitude: {moon_long:.4f}")
        
        # Calculate Nakshatra for Moon
        nakshatra_name, nakshatra_num, percentage, pada = get_nakshatra(moon_long)
        print(f"Moon Nakshatra: {nakshatra_name} ({percentage:.2f}%) - Pada {pada}")
        
        print(f"Jupiter Longitude: {jupiter_long:.4f}")

        rahu_long = get_planet_longitude(Planet.Rahu, astro_time)
        ketu_long = get_planet_longitude(Planet.Ketu, astro_time)
        print(f"Rahu Longitude: {rahu_long:.4f}")
        print(f"Ketu Longitude: {ketu_long:.4f}")

        # 3. Calculate Tara Bala (Transit)
        print("-" * 30)
        print("3. Tara Bala Calculation")
        
        # Simulate Transit Time (e.g., Current Time)
        transit_dt = datetime.now(tz)
        transit_astro_time = AstroTime(transit_dt, lat, lon)
        
        transit_moon_long = get_planet_longitude(Planet.Moon, transit_astro_time)
        transit_nak_name, transit_nak_num, _, _ = get_nakshatra(transit_moon_long)
        
        print(f"Transit Time: {transit_dt}")
        print(f"Transit Moon Nakshatra: {transit_nak_name}")
        
        tara_name, tara_num = get_tara_bala(nakshatra_num, transit_nak_num)
        print(f"Tara Bala: {tara_name} (Tara {tara_num})")

        # 4. Calculate Vimshottari Dasa
        print("-" * 30)
        print("4. Vimshottari Dasa Calculation")
        
        # Calculate for Current Time
        # Note: dt is Birth Time, transit_dt is Current Time
        dasa_lord, bhukti_lord = get_vimshottari_dasa(nakshatra_num, percentage, dt, transit_dt)
        print(f"Current Dasa: {dasa_lord} Maha Dasa - {bhukti_lord} Bhukti")
        
        # Full Dasa Breakdown (including Sookshma & Prana)
        full_dasa = get_vimshottari_dasa_full(nakshatra_num, percentage, dt, transit_dt)
        print(f"\nFull Dasa Breakdown:")
        print(f"  Maha Dasa   : {full_dasa['maha_dasa']} ({full_dasa['maha_dasa_years']} years)")
        print(f"  Bhukti      : {full_dasa['bhukti']} ({full_dasa['bhukti_duration_years']:.2f} years)")
        print(f"  Pratyantara : {full_dasa['pratyantara']} ({full_dasa['pratyantara_duration_days']:.1f} days)")
        print(f"  Sookshma    : {full_dasa['sookshma']} ({full_dasa['sookshma_duration_days']:.2f} days)")
        print(f"  Prana       : {full_dasa['prana']} ({full_dasa['prana_duration_hours']:.2f} hours)")

        # 5. Calculate Ashtakavarga Points
        print("-" * 30)
        print("5. Ashtakavarga Points (Sarvashtakavarga)")
        
        av_points = get_sarvashtakavarga_points(astro_time)
        
        # Print in a nice format
        for i in range(1, 13):
            sign_name = RASIS[i-1]
            points = av_points[i]
            print(f"{sign_name}: {points}")

        # 6. Panchang Elements
        print("-" * 30)
        print("6. Panchang Elements")
        
        tithi_name, tithi_num, tithi_perc = get_tithi(sun_long, moon_long)
        print(f"Tithi: {tithi_name} ({tithi_perc:.2f}% traversed)")
        
        # Detailed Nitya Yoga
        yoga_details = get_nitya_yoga_details(sun_long, moon_long)
        print(f"\nNitya Yoga: {yoga_details['name']} (Yoga {yoga_details['number']})")
        print(f"  Deity    : {yoga_details['deity']}")
        print(f"  Nature   : {yoga_details['nature']} ({'[+] Auspicious' if yoga_details['is_auspicious'] else '[-] Inauspicious'})")
        print(f"  Effect   : {yoga_details['effect']}")
        print(f"  Progress : {yoga_details['percentage']:.1f}% traversed")

        # 7. Lagna Gochara (Transit Positions from Lagna)
        print("-" * 30)
        print("7. Lagna Gochara (Planet Transits from Ascendant)")
        
        # Get the natal Lagna rasi
        _, birth_lagna_rasi_num = get_rasi(lagnam_long)
        print(f"Birth Lagna Rasi: {RASIS[birth_lagna_rasi_num - 1]}")
        print()
        
        # Calculate current transit positions for all planets
        planets_for_gochara = [
            (Planet.Sun, "Sun"),
            (Planet.Moon, "Moon"),
            (Planet.Mars, "Mars"),
            (Planet.Mercury, "Mercury"),
            (Planet.Jupiter, "Jupiter"),
            (Planet.Venus, "Venus"),
            (Planet.Saturn, "Saturn"),
            (Planet.Rahu, "Rahu"),
            (Planet.Ketu, "Ketu"),
        ]
        
        print(f"Transit Time: {transit_dt}")
        print()
        
        for planet, name in planets_for_gochara:
            transit_long = get_planet_longitude(planet, transit_astro_time)
            transit_rasi_name, transit_rasi_num = get_rasi(transit_long)
            gochara_house = get_gochara_house(birth_lagna_rasi_num, transit_rasi_num)
            print(f"{name:8} -> {transit_rasi_name:22} (House {gochara_house:2} from Lagna)")

        # 8. Chandra Gochara (Transit Positions from Moon / Janma Rasi)
        print("-" * 30)
        print("8. Chandra Gochara (Planet Transits from Janma Rasi)")
        
        # Get the natal Moon rasi (Janma Rasi)
        _, birth_moon_rasi_num = get_rasi(moon_long)
        print(f"Janma Rasi (Birth Moon): {RASIS[birth_moon_rasi_num - 1]}")
        print()
        
        print(f"Transit Time: {transit_dt}")
        print()
        
        for planet, name in planets_for_gochara:
            transit_long = get_planet_longitude(planet, transit_astro_time)
            transit_rasi_name, transit_rasi_num = get_rasi(transit_long)
            gochara_house = get_gochara_house(birth_moon_rasi_num, transit_rasi_num)
            print(f"{name:8} -> {transit_rasi_name:22} (House {gochara_house:2} from Moon)")

        # 9. Varga Chakras (Divisional Charts)
        print("-" * 30)
        print("9. Varga Chakras (Divisional Charts)")
        print()
        
        # Show key divisional charts for Moon
        print("Moon Varga Positions:")
        key_vargas = ["D-1", "D-9", "D-10", "D-12", "D-24", "D-60"]
        for varga_key in key_vargas:
            name, meaning, func = VARGA_CHARTS[varga_key]
            sign_name, sign_num = func(moon_long)
            print(f"  {varga_key:5} ({name:15}) [{meaning:18}]: {sign_name}")
        
        print()
        print("Lagna Varga Positions:")
        for varga_key in key_vargas:
            name, meaning, func = VARGA_CHARTS[varga_key]
            sign_name, sign_num = func(lagnam_long)
            print(f"  {varga_key:5} ({name:15}) [{meaning:18}]: {sign_name}")
        
        print()
        print("All Planets in Navamsa (D-9):")
        all_planets = [
            (lagnam_long, "Lagna"),
            (sun_long, "Sun"),
            (moon_long, "Moon"),
            (get_planet_longitude(Planet.Mars, astro_time), "Mars"),
            (get_planet_longitude(Planet.Mercury, astro_time), "Mercury"),
            (jupiter_long, "Jupiter"),
            (get_planet_longitude(Planet.Venus, astro_time), "Venus"),
            (get_planet_longitude(Planet.Saturn, astro_time), "Saturn"),
            (rahu_long, "Rahu"),
            (ketu_long, "Ketu"),
        ]
        for longitude, planet_name in all_planets:
            navamsa_sign, _ = get_d9_navamsa(longitude)
            print(f"  {planet_name:8} -> {navamsa_sign}")

        # 10. Kakshya (Sub-divisions for Transit Analysis)
        print("-" * 30)
        print("10. Kakshya (Transit Sub-divisions)")
        print()
        print("Current Transit Kakshya Positions:")
        print(f"Transit Time: {transit_dt}")
        print()
        
        for planet, name in planets_for_gochara:
            transit_long = get_planet_longitude(planet, transit_astro_time)
            transit_rasi_name, _ = get_rasi(transit_long)
            kakshya_lord, kakshya_num, kakshya_perc = get_kakshya(transit_long)
            print(f"  {name:8} in {transit_rasi_name:22} -> Kakshya {kakshya_num} ({kakshya_lord:8}) [{kakshya_perc:5.1f}%]")

        # 11. Jaimini Astrology (Chara Dasa & Karakas)
        print("-" * 30)
        print("11. Jaimini Astrology")
        print()
        
        # Collect planet longitudes for Jaimini calculations
        planet_longs = {
            'Sun': sun_long,
            'Moon': moon_long,
            'Mars': get_planet_longitude(Planet.Mars, astro_time),
            'Mercury': get_planet_longitude(Planet.Mercury, astro_time),
            'Jupiter': jupiter_long,
            'Venus': get_planet_longitude(Planet.Venus, astro_time),
            'Saturn': get_planet_longitude(Planet.Saturn, astro_time),
        }
        
        # Chara Karakas
        print("Chara Karakas (Significators):")
        karakas = get_chara_karakas(planet_longs)
        for k in karakas:
            print(f"  {k['karaka']:15} -> {k['planet']:8} ({k['degree']:.2f}°)")
        print()
        
        # Chara Dasa
        print("Chara Dasa (Sign-based Dasa):")
        chara_dasa = get_chara_dasa(lagnam_long, planet_longs, astro_time.julian_day, transit_astro_time.julian_day)
        
        print(f"  Lagna: {chara_dasa['lagna_name']}")
        print(f"  Current Dasa: {chara_dasa['current_dasa']['sign_name']} ({chara_dasa['current_dasa']['years']} years)")
        print(f"  Years into Dasa: {chara_dasa['years_into_dasa']:.2f}")
        print(f"  Years remaining: {chara_dasa['years_remaining']:.2f}")
        print()
        
        # Antardasa
        antardasa = get_chara_dasa_antardasa(
            chara_dasa['current_dasa']['sign'],
            chara_dasa['lagna_sign'],
            planet_longs,
            chara_dasa['current_dasa']['years'],
            chara_dasa['years_into_dasa']
        )
        print(f"  Current Antardasa: {antardasa['current_name']} ({antardasa['duration_each']*12:.1f} months)")
        print(f"  Months remaining: {antardasa['time_remaining']*12:.1f}")
        print()
        
        # Dasa Sequence
        print("Full Chara Dasa Sequence:")
        for i, period in enumerate(chara_dasa['dasa_periods']):
            marker = "<-- Current" if period['sign'] == chara_dasa['current_dasa']['sign'] else ""
            print(f"  {i+1:2}. {period['sign_name']:22} ({period['years']:2} years) {marker}")
        print()
        
        # Key Arudhas
        print("Key Arudha Padas:")
        arudhas = get_all_arudhas(chara_dasa['lagna_sign'], planet_longs)
        key_arudhas = ['A1', 'A7', 'A10', 'A12']  # Lagna, Spouse, Career, Upapada
        for code in key_arudhas:
            a = arudhas[code]
            print(f"  {a['name']:15} ({code}): {a['arudha_sign_name']}")

        # 12. Avastha (Planetary States)
        print("-" * 30)
        print("12. Avastha (Planetary States)")
        print()
        
        # Get all planet longitudes for avastha
        avastha_planets = [
            ('Sun', sun_long),
            ('Moon', moon_long),
            ('Mars', get_planet_longitude(Planet.Mars, astro_time)),
            ('Mercury', get_planet_longitude(Planet.Mercury, astro_time)),
            ('Jupiter', jupiter_long),
            ('Venus', get_planet_longitude(Planet.Venus, astro_time)),
            ('Saturn', get_planet_longitude(Planet.Saturn, astro_time)),
        ]
        
        print("Dignity & Bala Avastha:")
        print(f"  {'Planet':8} {'Dignity':14} {'Bala Avastha':10} {'Strength':>8}")
        print(f"  {'-'*8} {'-'*14} {'-'*10} {'-'*8}")
        for name, long in avastha_planets:
            dignity, score = get_dignity_status(name, long)
            bala, _, strength = get_bala_avastha(long)
            print(f"  {name:8} {dignity:14} {bala:10} {strength:>7.0f}%")
        print()
        
        print("Deeptadi Avastha (Luminosity States):")
        for name, long in avastha_planets:
            deeptadi, desc = get_deeptadi_avastha(name, long, sun_long)
            print(f"  {name:8} -> {deeptadi:10} ({desc[:40]})")

        # 13. Varshaphal - Annual Horoscope (Tajika System)
        print("-" * 30)
        print("13. Varshaphal (Annual Horoscope - Tajika System)")
        
        # Calculate Varshaphal for current year
        current_year = transit_dt.year
        birth_year = dt.year
        age = current_year - birth_year
        
        # Get birth Lagna sign index
        birth_lagna_sign_idx = int(lagnam_long / 30)
        
        # For demo, use current transit Lagna as Varsha Lagna
        # In real calculation, this would be calculated for exact solar return moment
        varsha_lagna_long = get_lagnam(transit_astro_time)
        varsha_lagna_sign_idx = int(varsha_lagna_long / 30)
        
        # Weekday of solar return (approximation - using transit day)
        varsha_weekday = transit_dt.weekday()  # 0=Monday in Python
        # Convert to 0=Sunday
        varsha_weekday_sun = (varsha_weekday + 1) % 7
        
        print(f"\nVarshaphal for Year {current_year} (Age {age})")
        print()
        
        # Get summary
        varsha_summary = get_varshaphal_summary(
            birth_lagna_sign_idx, age, varsha_lagna_sign_idx, varsha_weekday_sun
        )
        
        print(f"Varsha Lagna: {RASIS[varsha_lagna_sign_idx]}")
        print(f"Year Lord (Varsheshvara): {varsha_summary['year_lord']}")
        print()
        
        print(f"Muntha Position:")
        print(f"  Sign : {varsha_summary['muntha']['sign']}")
        print(f"  Lord : {varsha_summary['muntha']['lord']}")
        print(f"  House: {varsha_summary['muntha']['house']} from Varsha Lagna")
        print()
        
        # Muntha house interpretation
        muntha_house = varsha_summary['muntha']['house']
        if muntha_house in [1, 4, 7, 10]:
            muntha_result = "Excellent - Muntha in Kendra (angular house)"
        elif muntha_house in [5, 9]:
            muntha_result = "Very Good - Muntha in Trikona (trine)"
        elif muntha_house in [2, 11]:
            muntha_result = "Good - Muntha in wealth house"
        elif muntha_house in [3, 6]:
            muntha_result = "Average - Muntha in upachaya"
        else:
            muntha_result = "Challenging - Muntha in dusthana"
        print(f"Year Prediction: {muntha_result}")
        print()
        
        # Display some Tajika Yogas
        print("Key Tajika Yogas (Varshaphal specific combinations):")
        key_yogas = ['Ithasala', 'Ishrafa', 'Kamboola', 'Radda']
        for yoga in key_yogas:
            print(f"  {yoga}: {TAJIKA_YOGAS[yoga]['effect'][:60]}")
        print()
        
        # Display some Sahams
        print("Key Sahams (Arabic Parts):")
        key_sahams = ['Punya Saham', 'Karma Saham', 'Vivaha Saham']
        for saham in key_sahams:
            print(f"  {saham}: {SAHAMS[saham]['signification']}")
        
        # =====================================================================
        # 14. PANCHA PAKSHI - FIVE BIRD SYSTEM
        # =====================================================================
        print("\n" + "=" * 60)
        print("14. PANCHA PAKSHI - FIVE BIRD SYSTEM")
        print("=" * 60)
        
        # Get tithi number (1-30)
        tithi_deg = (moon_long - sun_long) % 360
        tithi_num = int(tithi_deg / 12) + 1
        
        # Current time for checking activity
        query_time = datetime.now(tz)
        
        # Get Pancha Pakshi analysis
        pakshi = get_pancha_pakshi(nakshatra_num, tithi_num, query_time)
        
        print(f"Birth Bird: {pakshi['birth_bird']['name']} ({pakshi['birth_bird']['tamil_name']})")
        print()
        print(f"Current Time Analysis ({query_time.strftime('%Y-%m-%d %H:%M')}):")
        print(f"  Day: {pakshi['query_time']['weekday_name']}")
        print(f"  Period: {pakshi['query_time']['period']}, Yama: {pakshi['query_time']['yama']}")
        print()
        print(f"Your Bird's Activity: {pakshi['current_activity']['name']}")
        print(f"  Quality: {pakshi['current_activity']['quality']}")
        print(f"  Effect: {pakshi['current_activity']['effect']}")
        print(f"  Favorability Score: {pakshi['favorability']}/100")
        print()
        print(f"Prediction: {pakshi['prediction']}")
        print()
        print(f"Current Ruling Bird: {pakshi['ruling_bird']['name']}")
        print()
        
        # All birds status
        print("All Birds Current Status:")
        for bird_name, activity in pakshi['all_birds'].items():
            print(f"  {bird_name}: {activity}")
        print()
        
        # Daily Summary
        daily = get_daily_summary(nakshatra_num, tithi_num, query_time)
        print(f"Today's Overview for {daily['birth_bird']}:")
        print(f"  Ruling periods: {daily['summary']['ruling_periods']}")
        print(f"  Eating periods: {daily['summary']['eating_periods']}")
        print(f"  Total favorable: {daily['summary']['favorable_periods']}/10")

        # =====================================================================
        # 15. NUMEROLOGY - VEDIC NUMBER SCIENCE
        # =====================================================================
        print("\n" + "=" * 60)
        print("15. NUMEROLOGY - VEDIC NUMBER SCIENCE (Chaldean)")
        print("=" * 60)
        
        from logic.numerology import (
            get_birth_number, get_destiny_number, get_name_number,
            get_name_number_prediction, get_full_numerology
        )
        
        # Use a sample name (can be customized)
        sample_name = "John Doe"
        
        print(f"\nBirth Date: {dt.strftime('%d %B %Y')}")
        print()
        
        birth_num = get_birth_number(dt)
        destiny_num = get_destiny_number(dt)
        
        print(f"Birth Number: {birth_num}")
        print(f"  - Derived from day of birth (7th)")
        print(f"  - Denotes ruling power, body structure, character")
        print()
        
        print(f"Destiny Number: {destiny_num}")
        print(f"  - Derived from full date (07/06/1988)")
        print(f"  - Denotes life events, relationships, fate")
        print()
        
        # Name Number Analysis
        name_num = get_name_number(sample_name)
        name_pred = get_name_number_prediction(sample_name)
        
        print(f"Name Analysis for '{sample_name}':")
        print(f"  Name Number: {name_pred['name_number']}")
        print(f"  Root Number: {name_pred['root_number']}")
        print(f"  Ruling Planet: {name_pred['ruling_planet']}")
        print()
        print(f"  Life Aspect Scores:")
        print(f"    Finance:   {name_pred['scores']['finance']:>3}/100")
        print(f"    Romance:   {name_pred['scores']['romance']:>3}/100")
        print(f"    Education: {name_pred['scores']['education']:>3}/100")
        print(f"    Health:    {name_pred['scores']['health']:>3}/100")
        print(f"  Overall: {name_pred['overall_score']}/100 ({'Lucky' if name_pred['lucky'] else 'Challenging'})")
        print()
        
        # Wrap prediction text
        pred_text = name_pred['prediction']
        if len(pred_text) > 70:
            words = pred_text.split()
            lines = []
            current_line = []
            for word in words:
                if len(' '.join(current_line + [word])) > 70:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    current_line.append(word)
            if current_line:
                lines.append(' '.join(current_line))
            print("  Prediction:")
            for line in lines:
                print(f"    {line}")
        else:
            print(f"  Prediction: {pred_text}")
        print()
        
        # Full numerology with compatibility
        full_num = get_full_numerology(sample_name, dt)
        print(f"Number Compatibility:")
        print(f"  Birth-Destiny: {'Harmonious' if full_num['compatibility']['birth_destiny'] else 'Challenging'}")
        print(f"  Name-Birth: {'Harmonious' if full_num['compatibility']['name_birth'] else 'Challenging'}")
        print()
        
        print(f"Lucky Elements (based on Birth Number {birth_num}):")
        print(f"  Lucky Numbers: {', '.join(map(str, full_num['lucky_numbers']))}")
        print(f"  Lucky Days: {', '.join(full_num['lucky_days'])}")
        print(f"  Lucky Colors: {', '.join(full_num['lucky_colors'])}")

        # ============================================================
        # 16. SHADBALA - Six-fold Planetary Strength
        # ============================================================
        print()
        print("=" * 60)
        print("16. SHADBALA - Six-fold Planetary Strength")
        print("=" * 60)
        print()
        
        # Get Shadbala summary for all planets
        shadbala_summary = get_shadbala_summary(dt, lat, lon)
        
        print("Planetary Strength Analysis (in Rupas)")
        print("-" * 60)
        print(f"{'Planet':<10} {'Total':>8} {'Required':>10} {'Status':>10} {'%':>8}")
        print("-" * 60)
        
        for planet in shadbala_summary['ranking']:
            data = shadbala_summary['planets'][planet]
            status = "STRONG" if data['is_strong'] else "Weak"
            print(f"{planet:<10} {data['total_rupas']:>8.2f} {data['required_rupas']:>10.1f} {status:>10} {data['strength_ratio']:>7.1f}%")
        
        print("-" * 60)
        print()
        
        # Strongest and weakest planets
        print(f"Strongest Planet: {shadbala_summary['strongest_planet']}")
        print(f"Weakest Planet:   {shadbala_summary['weakest_planet']}")
        print(f"Average Strength: {shadbala_summary['average_rupas']:.2f} Rupas")
        print()
        
        # Strong/Weak planets lists
        if shadbala_summary['strong_planets']:
            print(f"Strong Planets: {', '.join(shadbala_summary['strong_planets'])}")
        if shadbala_summary['weak_planets']:
            print(f"Weak Planets:   {', '.join(shadbala_summary['weak_planets'])}")
        print()
        
        # Detailed breakdown for the strongest planet
        strongest = shadbala_summary['strongest_planet']
        strongest_data = shadbala_summary['planets'][strongest]
        
        print(f"Detailed Shadbala for {strongest} (Strongest Planet):")
        print(f"  1. Sthana Bala (Positional):   {strongest_data['sthana_bala']['total']:>8.2f} shashtiamsas")
        print(f"  2. Dig Bala (Directional):     {strongest_data['dig_bala']:>8.2f} shashtiamsas")
        print(f"  3. Kaala Bala (Temporal):      {strongest_data['kaala_bala']['total']:>8.2f} shashtiamsas")
        print(f"  4. Cheshta Bala (Motional):    {strongest_data['cheshta_bala']:>8.2f} shashtiamsas")
        print(f"  5. Naisargika Bala (Natural):  {strongest_data['naisargika_bala']:>8.2f} shashtiamsas")
        print(f"  6. Drik Bala (Aspectual):      {strongest_data['drik_bala']:>8.2f} shashtiamsas")
        print(f"     ----------------------------------------")
        print(f"     Total:                      {strongest_data['total_shashtiamsas']:>8.2f} shashtiamsas")
        print(f"                                 {strongest_data['total_rupas']:>8.2f} Rupas")
        print()
        
        # Sthana Bala breakdown
        sthana = strongest_data['sthana_bala']
        print(f"  Sthana Bala Breakdown:")
        print(f"    - Ochcha (Exaltation):     {sthana['ochcha_bala']:>6.2f}")
        print(f"    - Saptavargaja (Vargas):   {sthana['saptavargaja_bala']:>6.2f}")
        print(f"    - Ojayugma (Odd/Even):     {sthana['ojayugmarasyamsa_bala']:>6.2f}")
        print(f"    - Kendra (Angular):        {sthana['kendra_bala']:>6.2f}")
        print(f"    - Drekkana (Decanate):     {sthana['drekkana_bala']:>6.2f}")

        # ============================================================
        # 17. PSYCHIC PROFILE - Formula-Based Intuition Analysis
        # ============================================================
        print()
        print("=" * 60)
        print("17. PSYCHIC PROFILE - Formula-Based Intuition Analysis")
        print("=" * 60)
        print()
        
        from logic.psychic_profile import (
            get_psychic_profile, get_psychic_channel, get_superpower,
            get_signal_strength
        )
        
        # Get the complete psychic profile
        profile = get_psychic_profile(dt, lat, lon)
        
        # Display the profile (ASCII-safe)
        print("+--------------------------------------------------------------+")
        print(f"|              PSYCHIC PROFILE: {'NATIVE':<28} |")
        print("+--------------------------------------------------------------+")
        print(f"|  Title: {profile['title']:<51} |")
        print(f"|  Potency: {profile['overall_potency']}% - {profile['potency_level']:<36} |")
        print("+--------------------------------------------------------------+")
        
        # Step 1: Channel (Moon Element)
        print("FORMULA BREAKDOWN:")
        print("-" * 60)
        print()
        print(f"STEP 1: INPUT CHANNEL (Moon Element -> How they receive)")
        print(f"  Moon Sign: {profile['channel']['moon_sign']}")
        print(f"  Element: {profile['channel']['element']}")
        print(f"  Channel: {profile['channel']['channel_name']}")
        print(f"  Definition: \"{profile['channel']['definition']}\"")
        print(f"  Mechanism: {profile['channel']['mechanism']}")
        print()
        
        # Step 2: Superpower (Nakshatra)
        print(f"STEP 2: SUPERPOWER (Nakshatra -> What they can do)")
        print(f"  Nakshatra: {profile['superpower']['nakshatra_name']} (#{profile['superpower']['nakshatra_number']})")
        print(f"  Superpower: {profile['superpower']['superpower']}")
        print(f"  Archetype: {profile['superpower']['archetype']}")
        print(f"  Ability: {profile['superpower']['ability']}")
        print(f"  Specialty: {profile['superpower']['specialty']}")
        print(f"  Deity: {profile['superpower']['deity']}")
        print()
        
        # Step 3: Signal Strength (Ketu House)
        print(f"STEP 3: SIGNAL STRENGTH (Ketu House -> Intensity/Depth)")
        print(f"  Ketu House: {profile['signal_strength']['ketu_house']}")
        print(f"  Title: {profile['signal_strength']['title']}")
        print(f"  Intensity: {profile['signal_strength']['intensity']} ({profile['signal_strength']['percentage']}%)")
        print(f"  Description: {profile['signal_strength']['description']}")
        print(f"  Manifestation: {profile['signal_strength']['manifestation']}")
        print(f"  Gift: {profile['signal_strength']['gift']}")
        print(f"  Challenge: {profile['signal_strength']['challenge']}")
        print()
        
        # Combined Result
        print("-" * 60)
        print("COMBINED PSYCHIC PROFILE:")
        print("-" * 60)
        print(f"  Title: {profile['title']}")
        print(f"  Overall Potency: {profile['overall_potency']}% ({profile['potency_level']})")
        print(f"  Color Aura: {profile['color']}")
        print()
        print(f"  How It Works: {profile['how_it_works']}")
        print(f"  Best Use: {profile['best_use']}")
        print(f"  Activation: {profile['activation_trigger']}")
        print()
        print(f"  Main Gift: {profile['main_gift']}")
        print(f"  Main Challenge: {profile['main_challenge']}")
        print()
        
        # Channel strengths/weaknesses
        print("CHANNEL DETAILS:")
        print(f"  Strengths: {', '.join(profile['channel']['strengths'])}")
        print(f"  Weaknesses: {', '.join(profile['channel']['weaknesses'])}")
        print()
        
        # Unique profile combinations
        total_combinations = 4 * 27 * 12  # channels x superpowers x houses
        print(f"Note: This system creates {total_combinations:,} unique psychic profiles")
        print(f"      (4 channels x 27 superpowers x 12 signal strengths)")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have downloaded the Swiss Ephemeris files (.se1) into the 'ephe' folder!")

if __name__ == "__main__":
    main()
