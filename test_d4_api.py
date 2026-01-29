"""Test D4 calculations from the API"""
import sys
sys.path.insert(0, '.')

from logic.calculate import get_planet_longitude
from logic.varga import get_d4_chaturthamsa
from logic.time import AstroTime
from logic.consts import Planet
from datetime import datetime
import pytz

# Test date: 1990-05-15 14:30 Mumbai
lat, lon = 19.0760, 72.8777  # Mumbai
tz = pytz.timezone('Asia/Kolkata')
dt = tz.localize(datetime(1990, 5, 15, 14, 30, 0))

astro_time = AstroTime(dt, lat, lon)

print("\n=== Testing D4 Chaturthamsa ===\n")

planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, 
           Planet.Jupiter, Planet.Venus, Planet.Saturn]

for planet in planets:
    longitude = get_planet_longitude(planet, astro_time)
    sign_num = int(longitude / 30) + 1
    degree_in_sign = longitude % 30
    
    d4_sign, d4_num = get_d4_chaturthamsa(longitude)
    
    print(f"{planet.value:8} | Long: {longitude:6.2f}° | Deg in sign: {degree_in_sign:5.2f}° | D4: {d4_sign:20} ({d4_num})")

print("\n=== Element Pattern Test ===\n")
print("Aries (Cardinal):")
for deg in [5, 10, 17, 25]:
    result = get_d4_chaturthamsa(deg)
    print(f"  {deg}° -> {result}")

print("\nTaurus (Fixed):")
for deg in [35, 40, 47, 55]:
    result = get_d4_chaturthamsa(deg)
    print(f"  {deg}° -> {result}")
