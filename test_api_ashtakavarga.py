"""Test Ashtakavarga in API response"""
import requests
import json

url = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"
data = {
    "name": "Test User",
    "birth_date": "1991-05-04",
    "birth_time": "10:50",
    "birth_place": "Vellore"
}

print("\n=== Testing Ashtakavarga in API ===\n")

response = requests.post(url, json=data)
result = response.json()

if 'ashtakavarga' in result:
    av = result['ashtakavarga']
    
    print("✅ Ashtakavarga data found in API response!\n")
    
    print("BAV (Bhinnashtakavarga) - Points per planet across 12 signs:")
    print(f"  Sun     : {av['bav']['sun']}")
    print(f"  Moon    : {av['bav']['moon']}")
    print(f"  Mars    : {av['bav']['mars']}")
    print(f"  Mercury : {av['bav']['mercury']}")
    print(f"  Jupiter : {av['bav']['jupiter']}")
    print(f"  Venus   : {av['bav']['venus']}")
    print(f"  Saturn  : {av['bav']['saturn']}")
    
    print(f"\nSAV (Sarvashtakavarga) - Total points per sign:")
    print(f"  Total Points: {av['sav']['total_points']}")
    print(f"  Interpretation: {av['sav']['interpretation']}")
    
    # Show sign mapping
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    print("\n\nSign-wise SAV breakdown:")
    sav_points = av['sav']['total_points']
    for i, (sign, points) in enumerate(zip(signs, sav_points)):
        quality = "Excellent" if points >= 30 else "Good" if points >= 25 else "Average" if points >= 20 else "Challenging"
        print(f"  {sign:12} : {points:2} points - {quality}")
    
    print("\n\nExample Transit Query:")
    print("  Q: When Moon enters Taurus tomorrow, what's the quality?")
    taurus_idx = 1  # Taurus is index 1 (0=Aries, 1=Taurus, etc.)
    moon_bav = av['bav']['moon'][taurus_idx]
    total_sav = av['sav']['total_points'][taurus_idx]
    print(f"  A: Moon has {moon_bav} bindus in Taurus, Total SAV = {total_sav} points")
    print(f"     Quality: {'Good' if total_sav >= 25 else 'Average' if total_sav >= 20 else 'Challenging'}")
    
else:
    print("❌ Ashtakavarga data NOT found in API response")
    print("\nAvailable keys:", list(result.keys()))
