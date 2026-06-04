"""
GET /monthly/{profile_id}?year=&month=
=======================================
Lightweight day-score strip for calendar view.

For each day of the month computes: overall score (1-5), moon sign, tara status.
Uses cached daily predictions where available, otherwise runs fast moon-only calc.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import calendar
import pytz
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query, Depends

from logic.calculate import get_planet_longitude
from logic.time import AstroTime
from logic.consts import Planet
from logic.rasi import get_rasi
from logic.nakshatra import get_nakshatra, get_tara_bala
from logic.rasi import get_gochara_house
from api.database import get_db, get_profile_by_id, get_daily_prediction

router = APIRouter(prefix="/monthly", tags=["monthly"])

# Tara → numeric score
_TARA_SCORE = {
    "Janma": 3,
    "Sampat": 5,
    "Vipat": 1,
    "Kshema": 4,
    "Pratyak": 2,
    "Sadhana": 4,
    "Naidhana": 1,
    "Mitra": 4,
    "Parama Mitra": 5,
}

# Mood house → score modifier (-1 / 0 / +1)
_MOOD_MODIFIER = {
    1: 0, 2: 0, 3: 1, 4: -1, 5: 1, 6: 0,
    7: 0, 8: -1, 9: 1, 10: 1, 11: 1, 12: -1,
}

_FUEL_MODIFIER = {
    1: 1, 2: 0, 3: 1, 4: 0, 5: 1, 6: 0,
    7: 0, 8: -1, 9: 1, 10: 1, 11: 1, 12: -1,
}


def _fast_day_score(profile: dict, date_str: str, tz_name: str) -> dict:
    """Fast day score using only Moon transit — no LLM, no full prediction."""
    tz = pytz.timezone(tz_name)
    pred_dt = datetime.strptime(date_str, "%Y-%m-%d")
    pred_dt = tz.localize(pred_dt.replace(hour=12, minute=0, second=0))

    astro = AstroTime(pred_dt, lat=profile["latitude"], lon=profile["longitude"])
    moon_lon = get_planet_longitude(Planet.Moon, astro)
    moon_sign, moon_sign_num = get_rasi(moon_lon)
    nak_name, nak_num, _, _ = get_nakshatra(moon_lon)

    lagna_num = profile["lagna"]["sign_num"]
    birth_moon_num = profile["planets"]["Moon"]["sign_num"]
    birth_nak_num = profile["planets"]["Moon"]["nakshatra_num"]

    mood_house = get_gochara_house(lagna_num, moon_sign_num)
    fuel_house = get_gochara_house(birth_moon_num, moon_sign_num)
    tara_name_raw, _ = get_tara_bala(birth_nak_num, nak_num)
    tara_base = tara_name_raw.split("(")[0].strip()

    tara_score = _TARA_SCORE.get(tara_base, 3)
    score_raw = tara_score + _MOOD_MODIFIER.get(mood_house, 0) + _FUEL_MODIFIER.get(fuel_house, 0)
    score = max(1, min(5, score_raw))

    return {
        "date": date_str,
        "score": score,
        "moon_sign": moon_sign,
        "moon_nakshatra": nak_name,
        "tara": tara_base,
    }


@router.get("/{profile_id}", summary="Monthly calendar day scores")
async def get_monthly(
    profile_id: str,
    year: int = Query(..., description="4-digit year"),
    month: int = Query(..., ge=1, le=12, description="Month 1-12"),
    db=Depends(get_db),
):
    profile = await get_profile_by_id(profile_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    tz_name = profile.get("timezone", "Asia/Kolkata")
    _, days_in_month = calendar.monthrange(year, month)

    days = []
    for day in range(1, days_in_month + 1):
        date_str = f"{year:04d}-{month:02d}-{day:02d}"

        # Use cached daily prediction if available
        cached = await get_daily_prediction(profile_id, date_str, db)
        if cached:
            mood_house = cached.get("mood", {}).get("house", 6)
            fuel_level = cached.get("fuel", {}).get("level", "Moderate")
            tara_base = cached.get("luck", {}).get("tara", "Kshema")
            # Map fuel level to modifier
            _fuel_str = {"Maximum": 1, "Good": 0, "High": 1, "Moderate": 0, "Intense": 0, "Low-Moderate": -1, "Low": -1}
            tara_score = _TARA_SCORE.get(tara_base, 3)
            score = max(1, min(5, tara_score + _MOOD_MODIFIER.get(mood_house, 0) + _fuel_str.get(fuel_level, 0)))
            days.append({
                "date": date_str,
                "score": score,
                "moon_sign": cached.get("transit_moon", {}).get("sign", ""),
                "moon_nakshatra": cached.get("transit_moon", {}).get("nakshatra", ""),
                "tara": tara_base,
            })
        else:
            try:
                day_data = _fast_day_score(profile, date_str, tz_name)
            except Exception:
                day_data = {"date": date_str, "score": 3, "moon_sign": "", "moon_nakshatra": "", "tara": ""}
            days.append(day_data)

    return {
        "profile_id": profile_id,
        "year": year,
        "month": month,
        "days": days,
    }
