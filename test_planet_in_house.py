"""Quick test for planet_in_house module."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from logic.planet_in_house import get_all_planet_in_house_interpretations
from logic.time import AstroTime
from datetime import datetime

t = AstroTime(dt=datetime(1988, 6, 7, 20, 40), lat=13.0827, lon=80.2707)
results = get_all_planet_in_house_interpretations(t)
print(f"Got {len(results)} interpretations")
for r in results:
    desc_preview = r['description'][:70].replace('\n', ' ')
    print(f"  {r['planet']:8} House {r['house']:2}  {desc_preview}...")
assert len(results) == 9, "Expected 9 planets"
assert all(r['description'] for r in results), "All planets should have descriptions"
print("\nAll assertions passed!")
