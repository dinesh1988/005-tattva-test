"""
Test the categorized functional nature format
"""
from logic.functional_nature import get_functional_nature_categorized

# Test for Sagittarius Ascendant (same as our test case)
lagna = 9  # Sagittarius

result = get_functional_nature_categorized(lagna)

print(f"\n{'='*60}")
print(f"FUNCTIONAL NATURE - Sagittarius Ascendant (Categorized)")
print(f"{'='*60}\n")

print(f"👑 Yogakaraka: {result['yogakaraka']}")
print(f"\n✅ Benefics (Bring Fortune): {', '.join(result['benefics'])}")
print(f"\n⚠️ Malefics (Cause Trouble): {', '.join(result['malefics'])}")
print(f"\n⚖️ Neutrals (Mixed Results): {', '.join(result['neutrals'])}")

print(f"\n{'='*60}")
print("\nPREDICTION USAGE:")
print(f"- During {result['benefics'][0]} Dasa → Expect POSITIVE results ✅")
print(f"- During {result['malefics'][0]} Dasa → Be CAUTIOUS ⚠️")
if result['yogakaraka']:
    print(f"- During {result['yogakaraka']} Dasa → BEST period 👑")
