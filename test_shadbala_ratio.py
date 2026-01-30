"""Test the new Shadbala ratio format"""

from datetime import datetime
from logic.shadbala import get_shadbala_ratios
import json

# Test with Sagittarius ascendant (same as before)
birth_datetime = datetime(1991, 5, 4, 10, 50)  # May 4, 1991, 10:50 AM
lat = 12.916667  # Vellore
lon = 79.133333

# Get shadbala ratios
shadbala = get_shadbala_ratios(birth_datetime, lat, lon)

print("=" * 60)
print("SHADBALA - Planetary Strength Ratios")
print("=" * 60)
print()
print(json.dumps(shadbala, indent=2))
print()
print("=" * 60)
print()
print("INTERPRETATION:")
print("-" * 60)
for planet, ratio in shadbala.items():
    strength = "💪 STRONG" if ratio >= 1.0 else "⚠️ WEAK"
    percentage = f"{(ratio - 1) * 100:+.0f}%" if ratio >= 1.0 else f"{(ratio - 1) * 100:.0f}%"
    print(f"{planet.capitalize():10} {ratio:.2f}  {strength}  ({percentage})")
print()
print("=" * 60)
print()
print("PREDICTION USAGE:")
print("-" * 60)
print("If Mars transits a sensitive point:")
mars_ratio = shadbala.get('mars', 1.0)
if mars_ratio >= 1.3:
    print(f"  → Mars is VERY STRONG ({mars_ratio:.2f}) → Bad effect is SEVERE ❌")
elif mars_ratio >= 1.0:
    print(f"  → Mars is STRONG ({mars_ratio:.2f}) → Bad effect is MODERATE ⚠️")
else:
    print(f"  → Mars is WEAK ({mars_ratio:.2f}) → Bad effect is MINIMAL ✅")
print()
print("If Jupiter transits a sensitive point:")
jupiter_ratio = shadbala.get('jupiter', 1.0)
if jupiter_ratio >= 1.3:
    print(f"  → Jupiter is VERY STRONG ({jupiter_ratio:.2f}) → Good effect is EXCELLENT ✨")
elif jupiter_ratio >= 1.0:
    print(f"  → Jupiter is STRONG ({jupiter_ratio:.2f}) → Good effect is GOOD 👍")
else:
    print(f"  → Jupiter is WEAK ({jupiter_ratio:.2f}) → Good effect is LIMITED 😐")
print("=" * 60)
