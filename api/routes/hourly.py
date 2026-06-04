"""
GET /hourly/{profile_id}?date=YYYY-MM-DD
=========================================
Full day hora + choghadiya table for the person's birth location.
Returns 16 choghadiya and 24 hora slots the client can filter by current hour.

This endpoint is thin — it delegates to the gochar/local helpers and tags
each slot with a personalized overlay (is it favorable for this lagna?).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytz
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends

from logic.sunrise import get_sun_times
from api.database import get_db, get_profile_by_id
from api.routes.gochar import _choghadiya_periods, _hora_periods

router = APIRouter(prefix="/hourly", tags=["hourly"])

# Choghadiya nature by lagna (benefic planets for each lagna)
# Simplified: lords favorable to the lagna get boosted
_LAGNA_FAVORED_HORA_LORDS = {
    1: ["Sun", "Mars", "Jupiter"],          # Aries
    2: ["Venus", "Saturn", "Mercury"],      # Taurus
    3: ["Mercury", "Saturn", "Venus"],      # Gemini
    4: ["Moon", "Mars", "Jupiter"],         # Cancer
    5: ["Sun", "Mars", "Jupiter"],          # Leo
    6: ["Mercury", "Venus", "Saturn"],      # Virgo
    7: ["Venus", "Saturn", "Mercury"],      # Libra
    8: ["Mars", "Jupiter", "Moon"],         # Scorpio
    9: ["Jupiter", "Sun", "Mars"],          # Sagittarius
    10: ["Saturn", "Venus", "Mercury"],     # Capricorn
    11: ["Saturn", "Venus", "Mercury"],     # Aquarius
    12: ["Jupiter", "Mars", "Moon"],        # Pisces
}


@router.get("/{profile_id}", summary="Full day hora and choghadiya table for person's location")
async def get_hourly(
    profile_id: str,
    date: str = Query(default="", description="YYYY-MM-DD local date (defaults to today)"),
    db=Depends(get_db),
):
    profile = await get_profile_by_id(profile_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    tz_name = profile.get("timezone", "Asia/Kolkata")
    lat = profile["latitude"]
    lon = profile["longitude"]
    lagna_num = profile["lagna"]["sign_num"]

    tz = pytz.timezone(tz_name)
    if date:
        local_dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=tz)
    else:
        local_dt = datetime.now(tz)

    try:
        sun_times = get_sun_times(date_local=local_dt, lat=lat, lon=lon, tz_name=tz_name)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not compute sun times: {e}")

    weekday = sun_times.sunrise.weekday()
    weekday_sun0 = (weekday + 1) % 7  # remap Mon=0 to Sun=0

    choghadiya = _choghadiya_periods(sun_times.sunrise, sun_times.sunset, sun_times.next_sunrise, weekday_sun0)
    hora = _hora_periods(sun_times.sunrise, sun_times.sunset, sun_times.next_sunrise, weekday_sun0)

    # Tag hora slots with personal favorability
    favored = _LAGNA_FAVORED_HORA_LORDS.get(lagna_num, [])
    for slot in hora:
        slot["favorable_for_lagna"] = slot["lord"] in favored

    return {
        "profile_id": profile_id,
        "date": local_dt.strftime("%Y-%m-%d"),
        "timezone": tz_name,
        "sunrise": sun_times.sunrise.isoformat(),
        "sunset": sun_times.sunset.isoformat(),
        "next_sunrise": sun_times.next_sunrise.isoformat(),
        "choghadiya": choghadiya,
        "hora": hora,
    }
