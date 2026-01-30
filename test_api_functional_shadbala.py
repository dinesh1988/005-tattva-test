"""
Test Functional Nature and Shadbala features through the API
"""

import requests
import json

# API endpoint
API_URL = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"

# Test birth data
birth_data = {
    "name": "Test User",
    "birth_date": "1991-05-04",
    "birth_time": "10:50",
    "birth_place": "Vellore",
    "latitude": 12.9165,
    "longitude": 79.1325,
    "timezone": "Asia/Kolkata"
}

print("=" * 80)
print("TESTING FUNCTIONAL NATURE & SHADBALA VIA API")
print("=" * 80)
print(f"\nAPI URL: {API_URL}")
print(f"Birth Data: {birth_data['birth_date']} {birth_data['birth_time']} at {birth_data['birth_place']}")
print("\nSending request...")

try:
    response = requests.post(API_URL, json=birth_data, timeout=30)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check for functional nature
        print("\n" + "=" * 80)
        print("1. FUNCTIONAL NATURE")
        print("=" * 80)
        
        if 'functional_nature' in data:
            functional_nature = data['functional_nature']
            print(f"\n✓ Functional Nature data found!")
            print(f"  Ascendant: {data['birth_chart']['lagna']['rasi']}")
            print(f"\n  Sample (Jupiter):")
            if 'Jupiter' in functional_nature:
                jupiter = functional_nature['Jupiter']
                print(f"    Nature: {jupiter.get('nature', 'N/A')}")
                print(f"    Houses: {jupiter.get('houses_ruled', 'N/A')}")
                print(f"    Reason: {jupiter.get('reason', 'N/A')}")
                print(f"    Impact: {jupiter.get('strength_impact', 'N/A')}")
        else:
            print("\n✗ Functional Nature NOT found in response")
        
        # Check for shadbala
        print("\n" + "=" * 80)
        print("2. SHADBALA")
        print("=" * 80)
        
        if 'shadbala' in data:
            shadbala = data['shadbala']
            print(f"\n✓ Shadbala data found!")
            print(f"  Strongest: {shadbala.get('strongest_planet', 'N/A')}")
            print(f"  Weakest: {shadbala.get('weakest_planet', 'N/A')}")
            print(f"  Average: {shadbala.get('average_rupas', 'N/A')} Rupas")
            print(f"  Ranking: {', '.join(shadbala.get('ranking', []))}")
            
            if 'planets' in shadbala:
                print(f"\n  Sample (Saturn):")
                if 'Saturn' in shadbala['planets']:
                    saturn = shadbala['planets']['Saturn']
                    print(f"    Total: {saturn.get('total_rupas', 0):.2f} Rupas")
                    print(f"    Required: {saturn.get('required_rupas', 0):.2f} Rupas")
                    print(f"    Percentage: {saturn.get('strength_ratio', 0):.1f}%")
                    print(f"    Strong: {saturn.get('is_strong', False)}")
        else:
            print("\n✗ Shadbala NOT found in response")
        
        # Overall summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        has_fn = 'functional_nature' in data
        has_sb = 'shadbala' in data
        print(f"\nFunctional Nature: {'✓ WORKING' if has_fn else '✗ MISSING'}")
        print(f"Shadbala: {'✓ WORKING' if has_sb else '✗ MISSING'}")
        print(f"\nOverall Status: {'🎉 SUCCESS - Both features working!' if (has_fn and has_sb) else '⚠️ INCOMPLETE'}")
        
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"\n✗ Exception occurred: {str(e)}")

print("\n" + "=" * 80)
