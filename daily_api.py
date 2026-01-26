"""
Daily Prediction API - Standalone
=================================
Simple FastAPI server for daily predictions.
Flutter app calls this once per day.

Features:
- In-memory cache (one prediction per user per day)
- Raw birth input (API calculates lagna, nakshatra, etc.)
- Returns Mood, Fuel, Luck for the day
"""

import sys
import os
from datetime import datetime, date
from typing import Optional
import pytz

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Import calculation modules
from logic.geolocation import get_location
from logic.time import AstroTime
from logic.calculate import get_planet_longitude, get_lagnam
from logic.consts import Planet
from logic.nakshatra import get_nakshatra
from logic.rasi import RASIS, get_rasi
from logic.daily_prediction import calculate_daily_prediction

# =============================================================================
# IN-MEMORY CACHE
# =============================================================================
# Structure: { "user_id_YYYY-MM-DD": prediction_dict }
PREDICTION_CACHE: dict = {}


def get_cache_key(user_id: str, pred_date: str) -> str:
    """Generate cache key from user_id and date."""
    return f"{user_id}_{pred_date}"


def get_cached_prediction(user_id: str, pred_date: str) -> Optional[dict]:
    """Get prediction from cache if exists."""
    key = get_cache_key(user_id, pred_date)
    return PREDICTION_CACHE.get(key)


def save_to_cache(user_id: str, pred_date: str, prediction: dict) -> None:
    """Save prediction to cache."""
    key = get_cache_key(user_id, pred_date)
    PREDICTION_CACHE[key] = prediction
    print(f"[CACHE] Saved: {key}")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================
class DailyPredictionRequest(BaseModel):
    """Request body for daily prediction."""
    user_id: str = Field(..., description="Unique user identifier")
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)")
    birth_time: str = Field(..., description="Birth time (HH:MM)")
    birth_place: str = Field(..., description="Birth place name (e.g., 'Chennai, India')")
    prediction_date: Optional[str] = Field(None, description="Date to predict (YYYY-MM-DD). Defaults to today.")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "birth_date": "1988-06-07",
                "birth_time": "20:40",
                "birth_place": "Chennai, India",
                "prediction_date": "2026-01-04"
            }
        }


class MoodInfo(BaseModel):
    house: int
    name: str
    interpretation: str
    description: str


class FuelInfo(BaseModel):
    house: int
    name: str
    level: str
    description: str


class LuckInfo(BaseModel):
    tara_name: str
    tara_number: int
    status: str
    description: str


class TransitMoonInfo(BaseModel):
    longitude: float
    sign: str
    sign_number: int
    nakshatra: str
    nakshatra_number: int


class BirthChartInfo(BaseModel):
    """Birth chart details."""
    lagna_sign: str
    lagna_number: int
    moon_nakshatra: str
    moon_nakshatra_number: int
    moon_padam: int


class DailyPredictionResponse(BaseModel):
    """Response body for daily prediction."""
    success: bool
    cached: bool
    date: str
    user_id: str
    birth_chart: BirthChartInfo
    transit_moon: TransitMoonInfo
    mood: MoodInfo
    fuel: FuelInfo
    luck: LuckInfo
    overall: str


# =============================================================================
# FASTAPI APP
# =============================================================================
app = FastAPI(
    title="Daily Prediction API",
    description="Vedic astrology daily predictions based on Moon transit",
    version="1.0.0"
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Daily Prediction API", "version": "1.0.0"}


@app.get("/health")
def health():
    """Health check."""
    return {"status": "healthy"}


@app.post("/predict", response_model=DailyPredictionResponse)
def get_daily_prediction(request: DailyPredictionRequest):
    """
    Get daily prediction for a user.
    
    Flow:
    1. Check cache for existing prediction (same user + same date)
    2. If cached, return immediately
    3. If not cached, calculate and store in cache
    """
    try:
        # Default prediction date to today
        pred_date = request.prediction_date or date.today().isoformat()
        
        # -----------------------------------------------------------------
        # STEP 1: Check cache
        # -----------------------------------------------------------------
        cached = get_cached_prediction(request.user_id, pred_date)
        if cached:
            print(f"[CACHE HIT] {request.user_id} for {pred_date}")
            return DailyPredictionResponse(
                success=True,
                cached=True,
                date=cached["date"],
                user_id=request.user_id,
                birth_chart=BirthChartInfo(**cached["birth_chart"]),
                transit_moon=TransitMoonInfo(**cached["transit_moon"]),
                mood=MoodInfo(**cached["mood"]),
                fuel=FuelInfo(**cached["fuel"]),
                luck=LuckInfo(**cached["luck"]),
                overall=cached["overall_prediction"]
            )
        
        print(f"[CACHE MISS] Calculating for {request.user_id} on {pred_date}")
        
        # -----------------------------------------------------------------
        # STEP 2: Get birth location
        # -----------------------------------------------------------------
        try:
            location = get_location(request.birth_place)
            lat = location["latitude"]
            lon = location["longitude"]
            tz_name = location["timezone"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid birth place: {request.birth_place}. Error: {str(e)}")
        
        # -----------------------------------------------------------------
        # STEP 3: Parse birth datetime
        # -----------------------------------------------------------------
        try:
            tz = pytz.timezone(tz_name)
            date_parts = request.birth_date.split("-")
            time_parts = request.birth_time.split(":")
            
            birth_dt = datetime(
                int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                int(time_parts[0]), int(time_parts[1]), 0,
                tzinfo=tz
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format. Use YYYY-MM-DD and HH:MM. Error: {str(e)}")
        
        # -----------------------------------------------------------------
        # STEP 4: Calculate birth chart data
        # -----------------------------------------------------------------
        birth_time_obj = AstroTime(dt=birth_dt, lat=lat, lon=lon)
        
        # Get birth Moon longitude
        birth_moon_long = get_planet_longitude(Planet.Moon, birth_time_obj)
        
        # Get birth nakshatra
        birth_nak_name, birth_nak_num, _, birth_nak_pada = get_nakshatra(birth_moon_long)
        
        # Get birth Lagna (Ascendant)
        birth_lagna_long = get_lagnam(birth_time_obj)
        birth_lagna_sign, birth_lagna_num = get_rasi(birth_lagna_long)
        
        # -----------------------------------------------------------------
        # STEP 5: Calculate daily prediction
        # -----------------------------------------------------------------
        prediction = calculate_daily_prediction(
            birth_datetime=birth_dt,
            birth_lat=lat,
            birth_lon=lon,
            birth_lagna_num=birth_lagna_num,
            birth_nakshatra_num=birth_nak_num,
            birth_moon_longitude=birth_moon_long,
            prediction_date=pred_date,
            timezone=tz_name
        )
        
        # Add birth chart info to prediction
        prediction["birth_chart"] = {
            "lagna_sign": birth_lagna_sign,
            "lagna_number": birth_lagna_num,
            "moon_nakshatra": birth_nak_name,
            "moon_nakshatra_number": birth_nak_num,
            "moon_padam": birth_nak_pada
        }
        
        # -----------------------------------------------------------------
        # STEP 6: Save to cache
        # -----------------------------------------------------------------
        save_to_cache(request.user_id, pred_date, prediction)
        
        # -----------------------------------------------------------------
        # STEP 7: Return response
        # -----------------------------------------------------------------
        return DailyPredictionResponse(
            success=True,
            cached=False,
            date=prediction["date"],
            user_id=request.user_id,
            birth_chart=BirthChartInfo(**prediction["birth_chart"]),
            transit_moon=TransitMoonInfo(**prediction["transit_moon"]),
            mood=MoodInfo(**prediction["mood"]),
            fuel=FuelInfo(**prediction["fuel"]),
            luck=LuckInfo(**prediction["luck"]),
            overall=prediction["overall_prediction"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/cache/stats")
def cache_stats():
    """Get cache statistics."""
    return {
        "total_entries": len(PREDICTION_CACHE),
        "keys": list(PREDICTION_CACHE.keys())
    }


@app.delete("/cache/clear")
def clear_cache():
    """Clear all cached predictions."""
    PREDICTION_CACHE.clear()
    return {"status": "cleared", "message": "Cache cleared successfully"}


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Daily Prediction API")
    print("=" * 50)
    print("Endpoints:")
    print("  POST /predict  - Get daily prediction")
    print("  GET  /health   - Health check")
    print("  GET  /cache/stats - Cache statistics")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
