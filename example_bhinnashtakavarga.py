"""
Example: Bhinnashtakavarga (Individual Planet Ashtakavarga)
============================================================
Demonstrates individual Ashtakavarga charts for each of the 7 planets.
Each chart shows benefic points (bindus) in 12 signs from 8 sources.
"""

import sys
sys.path.insert(0, '.')

from logic.ashtakavarga import (
    get_bhinnashtakavarga, 
    get_all_bhinnashtakavarga,
    get_bhinnashtakavarga_with_sources,
    get_sarvashtakavarga_points
)
from logic.time import AstroTime
from datetime import datetime
import pytz

# Test birth data: 04/05/1991, 10:50 AM, Vellore
lat, lon = 12.9165, 79.1325  # Vellore coordinates
tz = pytz.timezone('Asia/Kolkata')
dt = tz.localize(datetime(1991, 5, 4, 10, 50, 0))
astro_time = AstroTime(dt, lat, lon)

print("\n" + "="*80)
print("BHINNASHTAKAVARGA (BAV) - Individual Planet Ashtakavarga")
print("="*80)
print(f"\nBirth Date: 04/05/1991")
print(f"Birth Time: 10:50 AM")
print(f"Birth Place: Vellore\n")

# Get all BAV charts at once
all_bav = get_all_bhinnashtakavarga(astro_time)

# Signs
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

# Display summary table for all planets
print("-"*80)
print("SUMMARY: Bhinnashtakavarga Points for All Planets")
print("-"*80)
print(f"\n{'Sign':<12} | {'Sun':<5} {'Moon':<5} {'Mars':<5} {'Merc':<5} {'Jupi':<5} {'Venu':<5} {'Satu':<5} | {'Total':<5}")
print("-"*80)

# Get Sarvashtakavarga for comparison
sav = get_sarvashtakavarga_points(astro_time)

for i in range(1, 13):
    sign_name = signs[i-1]
    sun_pts = all_bav['Sun'][i]
    moon_pts = all_bav['Moon'][i]
    mars_pts = all_bav['Mars'][i]
    merc_pts = all_bav['Mercury'][i]
    jupi_pts = all_bav['Jupiter'][i]
    venu_pts = all_bav['Venus'][i]
    satu_pts = all_bav['Saturn'][i]
    total = sav[i]
    
    print(f"{sign_name:<12} | {sun_pts:^5} {moon_pts:^5} {mars_pts:^5} {merc_pts:^5} {jupi_pts:^5} {venu_pts:^5} {satu_pts:^5} | {total:^5}")

print("-"*80)

# Calculate totals for each planet
print("\nTotal Bindus per Planet:")
for planet_name, bav_data in all_bav.items():
    total_bindus = sum(bav_data.values())
    print(f"  {planet_name:10} : {total_bindus:3} bindus")

# Show detailed BAV for one planet (e.g., Sun)
print("\n" + "="*80)
print("DETAILED: Sun's Bhinnashtakavarga (with source contributions)")
print("="*80 + "\n")

sun_bav_detailed = get_bhinnashtakavarga_with_sources("Sun", astro_time)

print(f"{'Sign':<12} | Su Mo Ma Me Ju Ve Sa As | Total")
print("-"*50)

for i in range(1, 13):
    sign_name = signs[i-1]
    sources = sun_bav_detailed[i]
    
    su = sources['Sun']
    mo = sources['Moon']
    ma = sources['Mars']
    me = sources['Mercury']
    ju = sources['Jupiter']
    ve = sources['Venus']
    sa = sources['Saturn']
    asc = sources['Ascendant']
    
    total = su + mo + ma + me + ju + ve + sa + asc
    
    # Use dots for 1, space for 0
    su_mark = '●' if su else '·'
    mo_mark = '●' if mo else '·'
    ma_mark = '●' if ma else '·'
    me_mark = '●' if me else '·'
    ju_mark = '●' if ju else '·'
    ve_mark = '●' if ve else '·'
    sa_mark = '●' if sa else '·'
    asc_mark = '●' if asc else '·'
    
    print(f"{sign_name:<12} |  {su_mark}  {mo_mark}  {ma_mark}  {me_mark}  {ju_mark}  {ve_mark}  {sa_mark}  {asc_mark}  |   {total}")

print("-"*50)

# Interpretation
print("\n" + "="*80)
print("INTERPRETATION GUIDE")
print("="*80)
print("""
Higher BAV points in a sign indicate:
- Stronger benefic influence of that planet in that house
- Better results during transits through that sign
- Favorable timing for activities related to that house

Typical ranges:
- 0-2 bindus: Weak/unfavorable
- 3-4 bindus: Moderate
- 5-6 bindus: Strong/favorable  
- 7-8 bindus: Very strong (rare)

Usage in predictions:
- Transits through high-point signs yield better results
- Low-point signs may require extra effort/caution
- Combine with Dasa periods for timing events
""")

print("\n" + "="*80)
print("KEY INSIGHTS FOR THIS CHART")
print("="*80)

# Find strongest and weakest signs for each planet
for planet_name, bav_data in all_bav.items():
    max_points = max(bav_data.values())
    min_points = min(bav_data.values())
    
    strong_signs = [signs[i-1] for i, pts in bav_data.items() if pts == max_points]
    weak_signs = [signs[i-1] for i, pts in bav_data.items() if pts == min_points]
    
    print(f"\n{planet_name}:")
    print(f"  Strongest in: {', '.join(strong_signs)} ({max_points} bindus)")
    print(f"  Weakest in: {', '.join(weak_signs)} ({min_points} bindus)")

print("\n" + "="*80)
