"""
GET /gochar/sky?date=YYYY-MM-DD
  -> planetary positions, nakshatras, tithi  (universal, cache by date)

GET /gochar/local?date=YYYY-MM-DD&lat=&lon=&tz=
  -> sunrise, hora, choghadiya  (cache by date + lat/lon)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytz
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from logic.calculate import get_planet_longitude, is_planet_retrograde
from logic.time import AstroTime
from logic.consts import Planet
from logic.nakshatra import get_nakshatra, NAKSHATRAS
from logic.rasi import get_rasi, RASIS
from logic.panchang import get_tithi, get_yoga, get_karana, TITHIS, YOGAS
from logic.sunrise import get_sun_times

router = APIRouter(prefix="/gochar", tags=["gochar"])

_ALL_PLANETS = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu,
]

# Choghadiya periods (day split into 8 parts after sunrise)
_CHOGHADIYA_WEEKDAY = {
    # Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
    # Day choghadiya sequence per weekday
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],
}

_CHOGHADIYA_NIGHT = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],
}

_CHOGHADIYA_NATURE = {
    "Amrit": "Excellent",
    "Shubh": "Good",
    "Labh": "Good",
    "Char": "Neutral",
    "Udveg": "Bad",
    "Rog": "Bad",
    "Kaal": "Bad",
}


def _choghadiya_periods(sunrise: datetime, sunset: datetime, next_sunrise: datetime, weekday: int) -> list:
    """Compute 16 choghadiya slots (8 day + 8 night)."""
    from datetime import timedelta

    day_duration = (sunset - sunrise).total_seconds()
    night_duration = (next_sunrise - sunset).total_seconds()
    day_slot = day_duration / 8
    night_slot = night_duration / 8

    day_names = _CHOGHADIYA_WEEKDAY[weekday]
    night_names = _CHOGHADIYA_NIGHT[weekday]

    periods = []
    for i in range(8):
        start = sunrise + timedelta(seconds=i * day_slot)
        end = sunrise + timedelta(seconds=(i + 1) * day_slot)
        periods.append({
            "name": day_names[i],
            "nature": _CHOGHADIYA_NATURE[day_names[i]],
            "start": start.isoformat(),
            "end": end.isoformat(),
            "is_day": True,
        })
    for i in range(8):
        start = sunset + timedelta(seconds=i * night_slot)
        end = sunset + timedelta(seconds=(i + 1) * night_slot)
        periods.append({
            "name": night_names[i],
            "nature": _CHOGHADIYA_NATURE[night_names[i]],
            "start": start.isoformat(),
            "end": end.isoformat(),
            "is_day": False,
        })
    return periods


def _hora_periods(sunrise: datetime, sunset: datetime, next_sunrise: datetime, weekday: int) -> list:
    """Compute 24 planetary hora periods (12 day + 12 night)."""
    from datetime import timedelta

    # Hora lord order by weekday (Saturday start)
    _HORA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    # Day-start lord per weekday (Sun=0 -> Sun, Mon=1 -> Moon, ...)
    _DAY_START = {0: 3, 1: 6, 2: 4, 3: 5, 4: 1, 5: 2, 6: 0}  # index into _HORA_LORDS

    start_idx = _DAY_START[weekday]
    day_duration = (sunset - sunrise).total_seconds()
    night_duration = (next_sunrise - sunset).total_seconds()
    day_slot = day_duration / 12
    night_slot = night_duration / 12

    periods = []
    for i in range(12):
        lord = _HORA_LORDS[(start_idx + i) % 7]
        start = sunrise + timedelta(seconds=i * day_slot)
        end = sunrise + timedelta(seconds=(i + 1) * day_slot)
        periods.append({"lord": lord, "start": start.isoformat(), "end": end.isoformat(), "is_day": True})
    night_start_idx = (start_idx + 12) % 7
    for i in range(12):
        lord = _HORA_LORDS[(night_start_idx + i) % 7]
        start = sunset + timedelta(seconds=i * night_slot)
        end = sunset + timedelta(seconds=(i + 1) * night_slot)
        periods.append({"lord": lord, "start": start.isoformat(), "end": end.isoformat(), "is_day": False})
    return periods


@router.get("/sky", summary="Planetary positions and panchang for a date (universal)")
def get_sky(
    date: str = Query(default="", description="YYYY-MM-DD UTC (defaults to today)"),
):
    """
    Universal sky snapshot — same for everyone regardless of location.
    Uses midnight UTC as the reference moment.
    """
    if date:
        dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    else:
        dt = datetime.utcnow().replace(tzinfo=pytz.UTC)

    # Use Ujjain (standard Vedic reference meridian) for sky position
    astro = AstroTime(dt, lat=23.1765, lon=75.7885)

    sky = {}
    for planet in _ALL_PLANETS:
        lon_val = get_planet_longitude(planet, astro)
        sign_num = int(lon_val // 30) + 1
        nak_info = get_nakshatra(lon_val)
        retro = is_planet_retrograde(planet, astro) if planet not in (Planet.Rahu, Planet.Ketu) else False
        sky[planet.name] = {
            "longitude": round(lon_val, 4),
            "sign": RASIS[sign_num - 1] if 1 <= sign_num <= 12 else "Unknown",
            "sign_num": sign_num,
            "nakshatra": nak_info[0] if isinstance(nak_info, tuple) else nak_info.get("nakshatra", ""),
            "nakshatra_num": nak_info[1] if isinstance(nak_info, tuple) else nak_info.get("nakshatra_num", 0),
            "pada": nak_info[3] if isinstance(nak_info, tuple) else nak_info.get("pada", 0),
            "retrograde": retro,
        }

    sun_lon = get_planet_longitude(Planet.Sun, astro)
    moon_lon = get_planet_longitude(Planet.Moon, astro)

    tithi_raw = get_tithi(sun_lon, moon_lon)
    yoga_raw = get_yoga(sun_lon, moon_lon)
    karana_raw = get_karana(sun_lon, moon_lon)

    panchang = {
        "tithi": tithi_raw[0] if isinstance(tithi_raw, tuple) else tithi_raw.get("name", ""),
        "tithi_num": tithi_raw[1] if isinstance(tithi_raw, tuple) else tithi_raw.get("num", 0),
        "tithi_percent": round(tithi_raw[2], 1) if isinstance(tithi_raw, tuple) else 0,
        "yoga": yoga_raw[0] if isinstance(yoga_raw, tuple) else yoga_raw.get("name", ""),
        "yoga_num": yoga_raw[1] if isinstance(yoga_raw, tuple) else yoga_raw.get("num", 0),
        "karana": karana_raw.get("name", "") if isinstance(karana_raw, dict) else "",
    }

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "planets": sky,
        "panchang": panchang,
    }


@router.get("/local", summary="Sunrise, hora, and choghadiya for a location and date")
def get_local(
    date: str = Query(default="", description="YYYY-MM-DD (local date)"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    tz: str = Query(default="Asia/Kolkata", description="IANA timezone"),
):
    if date:
        local_dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=pytz.timezone(tz))
    else:
        local_dt = datetime.now(pytz.timezone(tz))

    try:
        sun_times = get_sun_times(date_local=local_dt, lat=lat, lon=lon, tz_name=tz)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not compute sun times: {e}")

    weekday = sun_times.sunrise.weekday()  # Mon=0 … Sun=6  → remap to Sun=0
    weekday_sun0 = (weekday + 1) % 7  # Python Mon=0 → Sun=0 Sun=0

    choghadiya = _choghadiya_periods(sun_times.sunrise, sun_times.sunset, sun_times.next_sunrise, weekday_sun0)
    hora = _hora_periods(sun_times.sunrise, sun_times.sunset, sun_times.next_sunrise, weekday_sun0)

    return {
        "date": local_dt.strftime("%Y-%m-%d"),
        "timezone": tz,
        "latitude": lat,
        "longitude": lon,
        "sunrise": sun_times.sunrise.isoformat(),
        "sunset": sun_times.sunset.isoformat(),
        "next_sunrise": sun_times.next_sunrise.isoformat(),
        "choghadiya": choghadiya,
        "hora": hora,
    }
