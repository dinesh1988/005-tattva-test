"""
Test Functional Nature and Shadbala features
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.functional_nature import get_functional_nature
from logic.shadbala import get_shadbala_summary
from datetime import datetime
import pytz

# Test birth data: Vellore, 04/05/1991, 10:50 AM
def test_local():
    print("=" * 80)
    print("FUNCTIONAL NATURE & SHADBALA TEST")
    print("=" * 80)
    
    # Create datetime
    tz = pytz.timezone('Asia/Kolkata')
    dt = datetime(1991, 5, 4, 10, 50, 0, tzinfo=tz)
    lat = 12.9165  # Vellore
    lon = 79.1325
    
    # Test Functional Nature (for Sagittarius ascendant = sign 9)
    print("\n1. FUNCTIONAL NATURE OF PLANETS")
    print("-" * 80)
    lagna_num = 9  # Sagittarius
    functional_nature = get_functional_nature(lagna_num)
    
    for planet, data in functional_nature.items():
        print(f"\n{planet}:")
        print(f"  Nature: {data['nature']}")
        print(f"  Houses Ruled: {data['houses_ruled']}")
        print(f"  Reason: {data['reason']}")
        print(f"  Strength Impact: {data['strength_impact']}")
    
    # Test Shadbala
    print("\n\n2. SHADBALA (PLANETARY STRENGTH)")
    print("-" * 80)
    shadbala_summary = get_shadbala_summary(dt, lat, lon)
    
    print(f"\nStrongest Planet: {shadbala_summary['strongest_planet']}")
    print(f"Weakest Planet: {shadbala_summary['weakest_planet']}")
    print(f"Average Strength: {shadbala_summary['average_rupas']} Rupas")
    print(f"\nRanking: {', '.join(shadbala_summary['ranking'])}")
    
    print("\n\nDetailed Strength for each planet:")
    for planet, data in shadbala_summary['planets'].items():
        print(f"\n{planet}:")
        print(f"  Total: {data.get('total_rupas', 0):.2f} Rupas")
        print(f"  Required: {data.get('required_rupas', 0):.2f} Rupas")
        print(f"  Percentage: {data.get('strength_ratio', 0):.1f}%")
        print(f"  Status: {'✓ Strong' if data.get('is_strong', False) else '✗ Weak'}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_local()
