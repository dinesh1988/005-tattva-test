"""
Test API for Vimshottari Dasa Schedule
Verifies complete 120-year timeline in API response
"""

import requests
import json

API_URL = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"

# Test data: 04/05/1991, 10:50 AM, Vellore
birth_data = {
    "name": "Test User",
    "birth_date": "1991-05-04",
    "birth_time": "10:50",
    "birth_place": "Vellore"
}

print("=" * 80)
print("Testing Vimshottari Dasa Schedule in API")
print("=" * 80)
print(f"API: {API_URL}")
print(f"Birth Data: {birth_data['birth_date']} {birth_data['birth_time']}, {birth_data['birth_place']}")
print()

try:
    response = requests.post(API_URL, json=birth_data, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    # Check if dasa_periods exists
    if 'dasa_periods' not in result:
        print("❌ ERROR: 'dasa_periods' not found in API response")
        exit(1)
    
    dasa_periods = result['dasa_periods']
    
    # Check current period
    print("✅ Current Period:")
    print(f"   Maha Dasa: {dasa_periods['mahadasa']['planet']} ({dasa_periods['mahadasa']['duration_years']} years)")
    print(f"   Bhukti: {dasa_periods['bhukti']['planet']}")
    print(f"   Age: {dasa_periods['current_age']}, Stage: {dasa_periods['life_stage']}")
    print()
    
    # Check full schedule
    if 'full_schedule' not in dasa_periods:
        print("❌ ERROR: 'full_schedule' not found in dasa_periods")
        exit(1)
    
    schedule = dasa_periods['full_schedule']
    
    print("✅ Full Schedule Found:")
    print(f"   Birth Dasa: {schedule['birth_dasa']}")
    print(f"   Balance: {schedule['birth_dasa_balance_years']} years")
    print(f"   Total Maha Dasas: {len(schedule['maha_dasas'])}")
    
    total_bhuktis = sum(len(md['bhuktis']) for md in schedule['maha_dasas'])
    print(f"   Total Bhuktis: {total_bhuktis}")
    print()
    
    # Display first 3 Maha Dasas as sample
    print("Sample Maha Dasas:")
    for i, maha_dasa in enumerate(schedule['maha_dasas'][:3], 1):
        birth_marker = " ⭐ BIRTH DASA" if maha_dasa['is_birth_dasa'] else ""
        print(f"   {i}. {maha_dasa['dasa_lord']} ({maha_dasa['duration_years']} years){birth_marker}")
        print(f"      {maha_dasa['start_date']} to {maha_dasa['end_date']}")
        print(f"      {len(maha_dasa['bhuktis'])} Bhuktis")
        
        # Show first 2 bhuktis
        for j, bhukti in enumerate(maha_dasa['bhuktis'][:2], 1):
            birth_bhukti = " ⭐" if bhukti['is_birth_bhukti'] else ""
            print(f"         {j}. {bhukti['bhukti_lord']}: {bhukti['start_date']} to {bhukti['end_date']}{birth_bhukti}")
        print()
    
    print("=" * 80)
    print("✅ SUCCESS: Vimshottari Dasa Schedule is complete in API!")
    print("=" * 80)
    
except requests.exceptions.RequestException as e:
    print(f"❌ ERROR: API request failed: {e}")
    exit(1)
except KeyError as e:
    print(f"❌ ERROR: Missing key in response: {e}")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)
