"""
GET /dasha/{profile_id}?date=YYYY-MM-DD
=======================================
Returns the active Maha Dasa + Bhukti (antardasa) for a given date,
plus a `cache_until` ISO datetime (end of current bhukti).

Reads from stored profile — no re-computation of natal chart.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query, Depends

from logic.dasa import get_vimshottari_dasa, get_vimshottari_dasa_schedule, DASA_LORDS
from api.database import get_db, get_profile_by_id

router = APIRouter(prefix="/dasha", tags=["dasha"])


def _find_active_period(schedule: dict, target: datetime) -> dict:
    """Walk dasha schedule to find the active maha-dasa and bhukti."""
    target_str = target.strftime("%Y-%m-%d")
    for maha in schedule.get("maha_dasas", []):
        if maha["start_date"] <= target_str < maha["end_date"]:
            active_bhukti = None
            for bhukti in maha.get("bhuktis", []):
                if bhukti["start_date"] <= target_str < bhukti["end_date"]:
                    active_bhukti = bhukti
                    break
            return {
                "maha_dasa": maha["dasa_lord"],
                "maha_dasa_start": maha["start_date"],
                "maha_dasa_end": maha["end_date"],
                "bhukti": active_bhukti["bhukti_lord"] if active_bhukti else None,
                "bhukti_start": active_bhukti["start_date"] if active_bhukti else None,
                "bhukti_end": active_bhukti["end_date"] if active_bhukti else None,
                "cache_until": active_bhukti["end_date"] if active_bhukti else maha["end_date"],
            }
    return {}


@router.get("/{profile_id}", summary="Active dasha lords for a given date")
async def get_dasha(
    profile_id: str,
    date: str = Query(default="", description="YYYY-MM-DD (defaults to today)"),
    db=Depends(get_db),
):
    profile = await get_profile_by_id(profile_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.utcnow()

    # Prefer pre-computed schedule stored in profile
    schedule = profile.get("dasha_schedule")
    if not schedule:
        # Recompute from stored natal data
        moon = profile["planets"]["Moon"]
        birth_dt = datetime.strptime(
            f"{profile['birth_date']} {profile['birth_time']}", "%Y-%m-%d %H:%M"
        )
        schedule = get_vimshottari_dasa_schedule(
            moon["nakshatra_num"],
            moon["nakshatra_percentage"],
            birth_dt,
        )

    active = _find_active_period(schedule, target_date)
    if not active:
        raise HTTPException(status_code=422, detail="Date outside computed dasha range")

    # Add lord attributes (symbol, years)
    lord_meta = {name: yrs for name, yrs in DASA_LORDS}
    active["maha_dasa_years"] = lord_meta.get(active["maha_dasa"], 0)

    return {
        "profile_id": profile_id,
        "date": target_date.strftime("%Y-%m-%d"),
        **active,
    }
