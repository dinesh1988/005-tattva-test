"""
POST /profile
=============
One-time natal computation. Stores result per person — never recomputed
unless explicitly requested with ?force=true.

Input:  birth date/time/place + user_id
Output: natal chart, yogas, dashas, ashtakavarga, psychic profile, numerology
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytz
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from logic.calculate import get_planet_longitude, get_lagnam, is_planet_retrograde
from logic.time import AstroTime
from logic.consts import Planet
from logic.nakshatra import get_nakshatra
from logic.dasa import get_vimshottari_dasa_schedule
from logic.rasi import get_rasi, RASIS
from logic.ashtakavarga import get_all_bhinnashtakavarga, get_sarvashtakavarga_points
from logic.yogas import get_all_yogas
from logic.psychic_profile import get_psychic_profile
from logic.numerology import get_full_numerology
from logic.functional_nature import get_functional_nature_categorized
from logic.varga import get_all_vargas
from logic.geolocation import get_location, get_coordinates
from api.database import save_profile, get_profile_by_id, get_profiles_by_user

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileRequest(BaseModel):
    user_id: str = Field(..., description="Firebase UID or anonymous ID")
    name: str = Field(..., description="Person's name")
    birth_date: str = Field(..., description="YYYY-MM-DD")
    birth_time: str = Field(..., description="HH:MM (24h)")
    birth_city: str = Field(..., description="City name for geolocation")
    birth_country: str = Field("", description="Country hint for disambiguation")
    timezone: str = Field("", description="IANA timezone override (e.g. Asia/Kolkata)")


def _build_natal(req: ProfileRequest) -> dict:
    """Core natal computation — called once per profile."""
    # Resolve location
    query = f"{req.birth_city}, {req.birth_country}".strip(", ")
    loc = get_location(query)
    if not loc:
        raise HTTPException(status_code=422, detail=f"Could not resolve location: {query}")

    lat = loc["latitude"]
    lon = loc["longitude"]
    tz_name = req.timezone or loc.get("timezone", "UTC")
    tz = pytz.timezone(tz_name)

    date_parts = req.birth_date.split("-")
    time_parts = req.birth_time.split(":")
    dt = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
        int(time_parts[0]), int(time_parts[1]), 0,
        tzinfo=tz,
    )

    astro = AstroTime(dt, lat, lon)

    # Lagna
    lagna_lon = get_lagnam(astro)
    lagna_sign_num = int(lagna_lon // 30) + 1
    lagna_sign = RASIS[lagna_sign_num - 1] if 1 <= lagna_sign_num <= 12 else "Unknown"

    # Planets
    planets_data = {}
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        lon_val = get_planet_longitude(planet, astro)
        sign_num = int(lon_val // 30) + 1
        sign = RASIS[sign_num - 1] if 1 <= sign_num <= 12 else "Unknown"
        house = ((sign_num - lagna_sign_num) % 12) + 1
        nak_name, nak_num, nak_pct, nak_pada = get_nakshatra(lon_val)
        retro = is_planet_retrograde(planet, astro) if planet not in (Planet.Rahu, Planet.Ketu) else False
        planets_data[planet.name] = {
            "longitude": round(lon_val, 4),
            "sign": sign,
            "sign_num": sign_num,
            "house": house,
            "nakshatra": nak_name,
            "nakshatra_num": nak_num,
            "pada": nak_pada,
            "nakshatra_percentage": round(nak_pct, 2),
            "retrograde": retro,
        }

    moon = planets_data["Moon"]
    moon_nak_num = moon["nakshatra_num"]
    moon_nak_pct = moon["nakshatra_percentage"]

    # Dasha schedule
    dasha_schedule = get_vimshottari_dasa_schedule(moon_nak_num, moon_nak_pct, dt)

    # Ashtakavarga
    try:
        bav = get_all_bhinnashtakavarga(astro, lagna_sign_num)
        sav = get_sarvashtakavarga_points(astro, lagna_sign_num)
    except Exception:
        bav = {}
        sav = {}

    # Yogas
    try:
        yogas = get_all_yogas(astro, lagna_sign_num)
    except Exception:
        yogas = []

    # Psychic profile
    try:
        psychic = get_psychic_profile(
            moon_sign=moon["sign"],
            moon_nakshatra=moon["nakshatra"],
            ketu_sign=planets_data.get("Ketu", {}).get("sign", ""),
        )
    except Exception:
        psychic = {}

    # Numerology
    try:
        numerology = get_full_numerology(req.name, req.birth_date)
    except Exception:
        numerology = {}

    # Functional nature
    try:
        func_nature = get_functional_nature_categorized(lagna_sign_num)
    except Exception:
        func_nature = {}

    # Divisional charts
    try:
        vargas = get_all_vargas(astro)
    except Exception:
        vargas = {}

    return {
        "name": req.name,
        "birth_date": req.birth_date,
        "birth_time": req.birth_time,
        "birth_city": loc.get("name", req.birth_city),
        "timezone": tz_name,
        "latitude": lat,
        "longitude": lon,
        "lagna": {"sign": lagna_sign, "sign_num": lagna_sign_num, "longitude": round(lagna_lon, 4)},
        "planets": planets_data,
        "dasha_schedule": dasha_schedule,
        "ashtakavarga": {"bhinna": bav, "sarva": sav},
        "yogas": yogas,
        "psychic_profile": psychic,
        "numerology": numerology,
        "functional_nature": func_nature,
        "vargas": vargas,
    }


@router.post("", summary="Compute and store natal profile (one-time)")
async def create_profile(req: ProfileRequest, force: bool = False):
    # Return existing profile unless force=true
    if not force:
        existing = await get_profiles_by_user(req.user_id)
        # Match by birth date + city
        for p in existing:
            if p.get("birth_date") == req.birth_date and p.get("birth_city", "").lower() == req.birth_city.lower():
                return {"profile_id": p["id"], "cached": True, "profile": p}

    natal = _build_natal(req)
    profile_id = await save_profile(natal, req.user_id)
    natal["id"] = profile_id
    return {"profile_id": profile_id, "cached": False, "profile": natal}


@router.get("/{profile_id}", summary="Fetch stored profile by ID")
async def get_profile(profile_id: str):
    profile = await get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/user/{user_id}", summary="List all profiles for a user")
async def list_profiles(user_id: str):
    profiles = await get_profiles_by_user(user_id)
    return {"profiles": profiles, "count": len(profiles)}
