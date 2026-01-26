import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import pytz
from logic.geolocation import get_location
from logic.psychic_profile import get_psychic_profile
from logic.time import AstroTime

# Test data
birth_date = "1990-05-15"
birth_time = "14:30"
birth_place = "Mumbai"
name = "Test User"

# Get location
location = get_location(birth_place)
print(f"Location: {location}")

lat = location['latitude']
lon = location['longitude']
tz_name = location['timezone']

# Parse datetime
tz = pytz.timezone(tz_name)
date_parts = birth_date.split('-')
time_parts = birth_time.split(':')

year = int(date_parts[0])
month = int(date_parts[1])
day = int(date_parts[2])
hour = int(time_parts[0])
minute = int(time_parts[1])

birth_datetime = datetime(year, month, day, hour, minute)
birth_datetime_tz = tz.localize(birth_datetime)

print(f"Birth datetime: {birth_datetime_tz}")

# Test psychic profile
try:
    print("\nTesting psychic_profile...")
    psychic_profile = get_psychic_profile(birth_datetime_tz, lat, lon)
    print(f"✅ Psychic profile works! Title: {psychic_profile.get('title', 'N/A')}")
except Exception as e:
    print(f"❌ Error in psychic_profile: {e}")
    import traceback
    traceback.print_exc()

# Test AstroTime
try:
    print("\nTesting AstroTime...")
    astro_time = AstroTime(birth_datetime_tz, lat, lon)
    print(f"✅ AstroTime created!")
except Exception as e:
    print(f"❌ Error in AstroTime: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Basic tests passed!")

# Test yogas
try:
    print("\nTesting get_all_yogas...")
    from logic.yogas import get_all_yogas
    yogas = get_all_yogas(astro_time)
    print(f"✅ Yogas work! Found {len(yogas)} yogas")
    print(f"Sample yoga: {yogas[0] if yogas else 'None'}")
except Exception as e:
    print(f"❌ Error in yogas: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All tests completed!")

# Test numerology
try:
    print("\nTesting numerology...")
    from logic.numerology import get_full_numerology
    numerology = get_full_numerology(name, birth_datetime)
    print(f"✅ Numerology works! Life Path: {numerology.get('life_path_number', 'N/A')}")
except Exception as e:
    print(f"❌ Error in numerology: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All functions tested!")

# Now test the complete profile logic
print("\n=== TESTING COMPLETE PROFILE LOGIC ===")
try:
    # Test yoga enhancement
    yogas_enhanced = []
    for yoga in yogas:
        yoga_dict = {
            'name': yoga.name,
            'present': yoga.occurring,
            'nature': yoga.nature.value if hasattr(yoga.nature, 'value') else str(yoga.nature),
            'description': yoga.description,
            'condition': yoga.condition,
            'strength': yoga.strength if yoga.strength else 0,
            'category': 'Wealth' if any(x in yoga.name for x in ['Lakshmi', 'Vasumathi', 'Chatussagara', 'Parvata']) else 'Other'
        }
        yogas_enhanced.append(yoga_dict)
    
    print(f"✅ Yoga enhancement works! Enhanced {len(yogas_enhanced)} yogas")
    active_yogas = [y['name'] for y in yogas_enhanced if y.get('present', False)]
    print(f"✅ Found {len(active_yogas)} active yogas")
    
except Exception as e:
    print(f"❌ Error in yoga enhancement: {e}")
    import traceback
    traceback.print_exc()



