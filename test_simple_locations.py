"""
Test the complete profile API with simple, known locations
"""
import requests
import json

API_URL = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"

# Test cases with well-known cities
test_cases = [
    {
        "name": "Test Mumbai",
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "birth_place": "Mumbai, India"
    },
    {
        "name": "Test London",
        "birth_date": "1985-08-20",
        "birth_time": "10:00",
        "birth_place": "London, UK"
    },
    {
        "name": "Test New York",
        "birth_date": "1992-12-01",
        "birth_time": "15:45",
        "birth_place": "New York, USA"
    },
    {
        "name": "Test Delhi",
        "birth_date": "1988-03-10",
        "birth_time": "08:30",
        "birth_place": "Delhi, India"
    },
    {
        "name": "Test Singapore",
        "birth_date": "1995-07-25",
        "birth_time": "12:00",
        "birth_place": "Singapore"
    }
]

def test_api(test_case):
    """Test a single case"""
    try:
        print(f"\nTesting: {test_case['name']}")
        print(f"Location: {test_case['birth_place']}")
        print("-" * 60)
        
        response = requests.post(API_URL, json=test_case, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ SUCCESS!")
            
            # Print key information
            exec_summary = result.get('executive_summary', {})
            print(f"\nExecutive Summary:")
            print(f"  Personality: {exec_summary.get('personality_overview', 'N/A')[:80]}")
            print(f"  Active Yogas: {exec_summary.get('active_yogas_count', 0)}")
            print(f"  Key Strengths: {exec_summary.get('key_strengths', 'N/A')[:60]}")
            
            # Check data completeness
            has_birth_chart = 'birth_chart' in result
            has_panchang = 'panchang' in result
            has_dasa = 'dasa_periods' in result
            has_yogas = 'yogas' in result
            has_numerology = 'numerology' in result
            
            print(f"\nData Completeness:")
            print(f"  Birth Chart: {'✓' if has_birth_chart else '✗'}")
            print(f"  Panchang: {'✓' if has_panchang else '✗'}")
            print(f"  Dasa Periods: {'✓' if has_dasa else '✗'}")
            print(f"  Yogas: {'✓' if has_yogas else '✗'} ({len(result.get('yogas', []))} total)")
            print(f"  Numerology: {'✓' if has_numerology else '✗'}")
            
            return True, result
        else:
            error_text = response.text[:300]
            print(f"✗ HTTP {response.status_code}")
            print(f"Error: {error_text}")
            return False, error_text
            
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        return False, str(e)

def main():
    print("=" * 80)
    print("TESTING COMPLETE PROFILE API WITH SIMPLE LOCATIONS")
    print("=" * 80)
    print(f"Endpoint: {API_URL}\n")
    
    successes = 0
    failures = 0
    
    for test_case in test_cases:
        success, result = test_api(test_case)
        if success:
            successes += 1
        else:
            failures += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(test_cases)}")
    print(f"✓ Passed: {successes} ({successes/len(test_cases)*100:.0f}%)")
    print(f"✗ Failed: {failures} ({failures/len(test_cases)*100:.0f}%)")
    
    if successes == len(test_cases):
        print("\n🎉 ALL TESTS PASSED!")
    elif successes > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: {successes}/{len(test_cases)} working")
    else:
        print("\n❌ ALL TESTS FAILED - API has critical issues")

if __name__ == "__main__":
    main()
