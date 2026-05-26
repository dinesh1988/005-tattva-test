import sys
sys.path.insert(0, ".")
from logic.time import AstroTime
from logic.kundali_matching import _moon_sign_idx, get_kundali_matching
from logic.lordship import get_lord_of_sign
from datetime import datetime, timedelta

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Find two dates where both have the same moon sign lord (not necessarily same sign)
base = datetime(1990, 1, 1, 6, 0)
pairs = []
for d1 in range(0, 60):
    for d2 in range(d1+1, d1+30):
        t1 = AstroTime(dt=base + timedelta(days=d1), lat=13.0, lon=77.6)
        t2 = AstroTime(dt=base + timedelta(days=d2), lat=13.0, lon=77.6)
        i1 = _moon_sign_idx(t1)
        i2 = _moon_sign_idx(t2)
        l1 = get_lord_of_sign(i1)
        l2 = get_lord_of_sign(i2)
        if l1 == l2 and i1 != i2:  # same lord, different sign (e.g. Aries/Scorpio -> Mars)
            pairs.append((d1, d2, SIGNS[i1], SIGNS[i2], l1.name))
            break
    if pairs:
        break

print("Found pair:", pairs[0])
d1, d2, s1, s2, lord = pairs[0]
male   = AstroTime(dt=base + timedelta(days=d1), lat=13.0, lon=77.6)
female = AstroTime(dt=base + timedelta(days=d2), lat=13.0, lon=77.6)

result = get_kundali_matching(male, female)
gm = next(f for f in result["factors"] if f["name"] == "Graha Maitri")
print("=== Same-lord test (", s1, "lord=", lord, "vs", s2, "lord=", lord, ") ===")
print("Points:", gm["points"], "/", gm["max_points"], " nature:", gm["nature"])
print("Info:", gm["info"])
assert gm["points"] == 5, "FAIL: expected 5/5 for same lord"
print("PASS: same-lord case returns 5/5")

