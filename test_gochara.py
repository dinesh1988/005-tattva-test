from logic.gochara import get_gochara_predictions, get_gochara_summary
from logic.time import AstroTime
from datetime import datetime
import pytz

tz = pytz.timezone('Asia/Kolkata')
birth_dt = tz.localize(datetime(1988, 6, 7, 20, 40))
birth = AstroTime(dt=birth_dt, lat=13.0827, lon=80.2707)

transit_dt = tz.localize(datetime(2025, 6, 15, 12, 0))
transit = AstroTime(dt=transit_dt, lat=13.0827, lon=80.2707)

preds = get_gochara_predictions(birth, transit)
summary = get_gochara_summary(birth, transit)

print("Summary:", summary)
print()
for p in preds:
    print(f"{p['planet']:10s} H{p['gochara_house']:2d}  {p['nature']:7s}  {p['description'][:70]}")
