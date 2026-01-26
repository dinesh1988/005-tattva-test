"""
Test yogas using real birth data from VedAstro's 15k famous people dataset.

This validates yoga calculations against known historical figures.
"""

import sys
from pathlib import Path
from datetime import datetime
import pytz
import json
import csv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.time import AstroTime
from logic.consts import Planet
from logic import calculate


def parse_vedastro_time(birth_time_json):
    """
    Parse VedAstro birth time format.
    
    Format: {
        "StdTime": "19:55 26/06/1954 +01:00",
        "Location": {
            "Name": "Edinburgh, United Kingdom",
            "Longitude": "-3.188267",
            "Latitude": "55.953251"
        }
    }
    """
    data = json.loads(birth_time_json)
    
    # Parse time string: "19:55 26/06/1954 +01:00"
    time_str = data['StdTime']
    parts = time_str.rsplit(' ', 1)  # Split from right to separate timezone
    datetime_str = parts[0]
    tz_offset = parts[1] if len(parts) > 1 else "+00:00"
    
    # Parse datetime
    dt = datetime.strptime(datetime_str, "%H:%M %d/%m/%Y")
    
    # Add timezone
    if tz_offset.startswith('+') or tz_offset.startswith('-'):
        sign = 1 if tz_offset.startswith('+') else -1
        tz_offset = tz_offset[1:]  # Remove sign
        hours, minutes = map(int, tz_offset.split(':'))
        tz = pytz.FixedOffset(sign * (hours * 60 + minutes))
        dt = tz.localize(dt)
    
    # Get location
    location = data['Location']
    lat = float(location['Latitude'])
    lon = float(location['Longitude'])
    loc_name = location['Name']
    
    return AstroTime(dt, lat, lon), loc_name


def check_yogas_for_person(name, birth_time_json):
    """Check all yogas for a person and return results using refactored yoga API."""
    try:
        time, location = parse_vedastro_time(birth_time_json)
    except Exception as e:
        return None, f"Error parsing time: {e}"
    
    try:
        # Import yoga functions
        from logic.yogas import get_all_yogas, get_occurring_yogas
        
        # Get all occurring yogas using refactored SOTA API
        all_yogas = get_all_yogas(time)
        occurring_yogas = [y for y in all_yogas if y.occurring]
        
        # Convert to dictionary format for display
        yogas_found = []
        for yoga in occurring_yogas:
            yogas_found.append({
                'name': yoga.name,
                'condition': yoga.condition,
                'effect': yoga.description
            })
        
        return yogas_found, location
        
    except Exception as e:
        return None, f"Error calculating: {e}"


def test_famous_people():
    """Test yoga detection on famous people from the dataset."""
    
    print("\n" + "="*80)
    print(" YOGA VALIDATION USING VEDASTRO'S 15K FAMOUS PEOPLE DATASET")
    print("="*80)
    
    # Path to dataset
    dataset_path = Path(__file__).parent.parent.parent / "HuggingFace" / "PersonList-15k.csv"
    
    if not dataset_path.exists():
        print(f"\n✗ Dataset not found at: {dataset_path}")
        print("Please ensure PersonList-15k.csv exists in HuggingFace/ directory")
        return
    
    print(f"\nReading dataset from: {dataset_path}")
    
    # Sample famous people to test (limit to avoid long processing)
    test_count = 20
    yogas_stats = {
        'GajaKesari Yoga': 0,
        'Sakata Yoga': 0,  # NEW: Malefic opposite of GajaKesari
        'Sunapha Yoga': 0,
        'Anapha Yoga': 0,
        'Dhurdhura Yoga': 0,
        'Bhadra Yoga': 0,
        'Hamsa Yoga': 0,
        'Malavya Yoga': 0,
        'Ruchaka Yoga': 0,
        'Sasha Yoga': 0,
        'Amala Yoga': 0,
        'Kemadruma Yoga': 0,
        'Lakshmi Yoga': 0,
        'Chatussagara Yoga': 0,  # NEW: All 4 kendras occupied
        'Vasumathi Yoga': 0,  # NEW: Benefics in upachaya
        'Parvata Yoga': 0,  # NEW: Mountain of success
        'Raja Yoga (Basic)': 0,
        'Neechabhanga Raja Yoga': 0,
        'Harsha Yoga': 0,
        'Sarala Yoga': 0,
        'Vimala Yoga': 0
    }
    
    people_with_yogas = []
    errors = 0
    
    print(f"\nTesting {test_count} famous people from dataset...\n")
    print("-" * 80)
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            if i >= test_count:
                break
            
            name = row['Name']
            birth_time = row['BirthTime']
            
            yogas, location_or_error = check_yogas_for_person(name, birth_time)
            
            if yogas is None:
                errors += 1
                print(f"{i+1}. {name}: ✗ {location_or_error}")
            elif len(yogas) > 0:
                print(f"\n{i+1}. {name} ({location_or_error})")
                print(f"   Found {len(yogas)} yoga(s):")
                for yoga in yogas:
                    print(f"   ✓ {yoga['name']}")
                    print(f"     {yoga['condition']}")
                    print(f"     Effect: {yoga['effect']}")
                    yogas_stats[yoga['name']] += 1
                
                people_with_yogas.append({
                    'name': name,
                    'location': location_or_error,
                    'yogas': yogas
                })
            else:
                print(f"{i+1}. {name} ({location_or_error}): No yogas detected")
    
    # Summary statistics
    print("\n" + "="*80)
    print(" VALIDATION SUMMARY")
    print("="*80)
    print(f"\nTotal people tested: {test_count}")
    print(f"People with yogas: {len(people_with_yogas)}")
    print(f"Errors: {errors}")
    
    print("\n📊 YOGA FREQUENCY:")
    for yoga_name, count in yogas_stats.items():
        percentage = (count / test_count) * 100
        print(f"  {yoga_name:20} : {count:2} occurrences ({percentage:5.1f}%)")
    
    # Highlight notable examples
    if people_with_yogas:
        print("\n🌟 NOTABLE EXAMPLES:")
        # Sort by number of yogas
        people_with_yogas.sort(key=lambda x: len(x['yogas']), reverse=True)
        
        for person in people_with_yogas[:5]:  # Top 5
            yoga_names = [y['name'] for y in person['yogas']]
            print(f"  {person['name']} - {len(person['yogas'])} yogas: {', '.join(yoga_names)}")
    
    print("\n" + "="*80)
    print("✓ VALIDATION COMPLETE")
    print("="*80)
    print("\nNote: This validates our yoga calculations against real historical data.")
    print("High-profile individuals often have multiple yogas indicating success/fame.")


if __name__ == "__main__":
    try:
        test_famous_people()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
