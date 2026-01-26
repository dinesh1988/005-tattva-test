"""
Test the deployed complete profile API endpoint with real birth data
"""
import csv
import json
import requests
from datetime import datetime
import pytz

API_URL = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"

def parse_vedastro_time(birth_time_str):
    """Parse VedAstro time format to extract birth data"""
    try:
        birth_data = json.loads(birth_time_str)
        
        # Parse StdTime: "19:55 26/06/1954 +01:00"
        time_str = birth_data['StdTime']
        
        # Split into time and timezone
        parts = time_str.rsplit(' ', 1)
        dt_str = parts[0]
        tz_offset = parts[1] if len(parts) > 1 else "+00:00"
        
        # Parse datetime
        dt = datetime.strptime(dt_str, "%H:%M %d/%m/%Y")
        
        # Extract location
        location = birth_data['Location']
        
        return {
            'birth_date': dt.strftime("%Y-%m-%d"),
            'birth_time': dt.strftime("%H:%M"),
            'birth_place': location['Name']
        }
    except Exception as e:
        return None, f"Parse error: {e}"

def test_complete_profile_api(name, birth_data):
    """Call the complete profile API endpoint"""
    try:
        payload = {
            'name': name,
            'birth_date': birth_data['birth_date'],
            'birth_time': birth_data['birth_time'],
            'birth_place': birth_data['birth_place']
        }
        
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Request error: {e}"

def main():
    print("=" * 80)
    print("TESTING COMPLETE PROFILE API WITH REAL BIRTH DATA")
    print("=" * 80)
    print(f"API Endpoint: {API_URL}")
    print()
    
    # Read PersonList dataset
    dataset_path = '../HuggingFace/PersonList-15k.csv'
    
    # Statistics
    total_tested = 0
    successful = 0
    parse_errors = 0
    api_errors = 0
    
    # Store results
    success_examples = []
    error_examples = []
    
    with open(dataset_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for i, row in enumerate(reader):
            # Test first 10 records
            if i >= 10:
                break
            
            name = row['Name']
            birth_time_json = row['BirthTime']
            
            print(f"\n{i+1}. Testing: {name}")
            print("-" * 60)
            
            # Parse birth data
            birth_data = parse_vedastro_time(birth_time_json)
            
            if isinstance(birth_data, tuple):  # Error case
                parse_errors += 1
                error_examples.append({
                    'name': name,
                    'error': birth_data[1]
                })
                print(f"   ✗ Parse Error: {birth_data[1]}")
                total_tested += 1
                continue
            
            print(f"   Birth Date: {birth_data['birth_date']}")
            print(f"   Birth Time: {birth_data['birth_time']}")
            print(f"   Birth Place: {birth_data['birth_place']}")
            
            # Call API
            success, result = test_complete_profile_api(name, birth_data)
            total_tested += 1
            
            if success:
                successful += 1
                print(f"   ✓ SUCCESS!")
                
                # Extract key info
                exec_summary = result.get('executive_summary', {})
                print(f"   Personality: {exec_summary.get('personality_overview', 'N/A')[:60]}...")
                print(f"   Active Yogas: {exec_summary.get('active_yogas_count', 0)}")
                print(f"   Key Strengths: {exec_summary.get('key_strengths', 'N/A')[:60]}...")
                
                success_examples.append({
                    'name': name,
                    'personality': exec_summary.get('personality_overview', 'N/A')[:100],
                    'yogas': exec_summary.get('active_yogas_count', 0)
                })
            else:
                api_errors += 1
                error_examples.append({
                    'name': name,
                    'error': result
                })
                print(f"   ✗ API ERROR: {result}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tested: {total_tested}")
    print(f"✓ Successful: {successful} ({(successful/total_tested*100):.1f}%)" if total_tested > 0 else "No tests run")
    print(f"✗ Parse Errors: {parse_errors}")
    print(f"✗ API Errors: {api_errors}")
    print()
    
    if success_examples:
        print("✓ SUCCESS EXAMPLES:")
        for ex in success_examples[:3]:
            print(f"  • {ex['name']}: {ex['yogas']} active yogas")
            print(f"    {ex['personality'][:80]}...")
        print()
    
    if error_examples:
        print("✗ ERROR EXAMPLES:")
        for ex in error_examples[:3]:
            print(f"  • {ex['name']}: {ex['error'][:80]}...")
        print()
    
    # Overall assessment
    if total_tested > 0:
        success_rate = (successful / total_tested) * 100
        if success_rate >= 80:
            print("🎉 EXCELLENT: API is working well with real data!")
        elif success_rate >= 50:
            print("⚠️ MODERATE: Some issues need investigation")
        else:
            print("❌ CRITICAL: Major issues with the API endpoint")

if __name__ == "__main__":
    main()
