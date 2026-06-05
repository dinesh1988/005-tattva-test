"""
GET /daily/{profile_id}?date=YYYY-MM-DD
========================================
Gochar × natal overlay — mood, fuel (energy), luck for the day.
Combines Moon transit against natal Lagna and Moon (Chandra Lagna),
plus Tarabala for the day.

Cached per (profile_id + date) in DB if available.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from logic.daily_prediction import calculate_daily_prediction
from api.database import get_profile_by_id, get_daily_prediction, save_daily_prediction

router = APIRouter(prefix="/daily", tags=["daily"])


def _profile_to_daily_args(profile: dict, date_str: str) -> dict:
    birth_dt = datetime.strptime(
        f"{profile['birth_date']} {profile['birth_time']}", "%Y-%m-%d %H:%M"
    )
    moon = profile["planets"]["Moon"]
    return dict(
        birth_datetime=birth_dt,
        birth_lat=profile["latitude"],
        birth_lon=profile["longitude"],
        birth_lagna_num=profile["lagna"]["sign_num"],
        birth_nakshatra_num=moon["nakshatra_num"],
        birth_moon_longitude=moon["longitude"],
        prediction_date=date_str,
        timezone=profile.get("timezone", "Asia/Kolkata"),
    )


@router.get("/{profile_id}", summary="Daily mood/energy/luck prediction")
async def get_daily(
    profile_id: str,
    date: str = Query(default="", description="YYYY-MM-DD (defaults to today UTC)"),
):
    profile = await get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    date_str = date or datetime.utcnow().strftime("%Y-%m-%d")
    user_id = profile.get("user_id", profile_id)

    # Check cache
    cached = get_daily_prediction(user_id, date_str)
    if cached:
        return {**cached, "cached": True}

    # Compute
    try:
        args = _profile_to_daily_args(profile, date_str)
        prediction = calculate_daily_prediction(**args)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")

    result = {
        "profile_id": profile_id,
        "date": date_str,
        **prediction,
        "cached": False,
    }

    # Persist to DB (fire-and-forget style — ignore save errors)
    try:
        save_daily_prediction(result, user_id, date_str)
    except Exception:
        pass

    return result
