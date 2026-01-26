"""
Standalone Numerology API
Provides numerology readings with in-memory caching
Port: 8081
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from datetime import datetime
from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

# Import numerology logic
from logic.numerology import get_full_numerology, get_name_number_prediction

# =============================================================================
# IN-MEMORY CACHE
# =============================================================================
# Structure: { "name_YYYY-MM-DD": numerology_dict }
NUMEROLOGY_CACHE: dict = {}


def get_cache_key(name: str, birth_date: str) -> str:
    """Generate cache key from name and birth date."""
    # Normalize name (lowercase, remove extra spaces)
    normalized_name = " ".join(name.lower().split())
    return f"{normalized_name}_{birth_date}"


def get_cached_numerology(name: str, birth_date: str) -> Optional[dict]:
    """Get numerology from cache if exists."""
    key = get_cache_key(name, birth_date)
    return NUMEROLOGY_CACHE.get(key)


def save_to_cache(name: str, birth_date: str, numerology: dict) -> None:
    """Save numerology to cache."""
    key = get_cache_key(name, birth_date)
    NUMEROLOGY_CACHE[key] = numerology
    print(f"[CACHE] Saved: {key}")


# =============================================================================
# PYDANTIC MODELS
# =============================================================================
class NumerologyRequest(BaseModel):
    """Request body for numerology reading."""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="Full name")
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "name": "John Doe",
                "birth_date": "1988-06-07"
            }
        }


class NumberInfo(BaseModel):
    """Number information."""
    number: int
    planet: str
    meaning: str


class NameNumberInfo(BaseModel):
    """Name number information."""
    number: int
    root: int
    planet: str
    prediction: str
    scores: Dict[str, int]


class CompatibilityInfo(BaseModel):
    """Compatibility information."""
    birth_destiny: bool
    name_birth: bool
    harmonious: bool


class NumerologyResponse(BaseModel):
    """Response body for numerology reading."""
    success: bool
    cached: bool
    user_id: str
    name: str
    birth_date: str
    birth_number: NumberInfo
    destiny_number: NumberInfo
    name_number: NameNumberInfo
    compatibility: CompatibilityInfo
    lucky_numbers: list[int]
    lucky_days: list[str]
    lucky_colors: list[str]


# =============================================================================
# FASTAPI APP
# =============================================================================
app = FastAPI(
    title="Numerology API",
    description="Standalone API for Vedic numerology readings",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"service": "Numerology API", "status": "running", "port": 8081}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/predict", response_model=NumerologyResponse)
async def get_numerology_reading(request: NumerologyRequest):
    """
    Get complete numerology reading.
    
    Args:
        request: NumerologyRequest with user_id, name, birth_date
        
    Returns:
        NumerologyResponse with birth/destiny/name numbers, compatibility, lucky details
    """
    try:
        # -----------------------------------------------------------------
        # STEP 1: Check cache
        # -----------------------------------------------------------------
        cached = get_cached_numerology(request.name, request.birth_date)
        if cached:
            print(f"[CACHE HIT] {request.name} ({request.birth_date})")
            return NumerologyResponse(
                success=True,
                cached=True,
                user_id=request.user_id,
                name=request.name,
                birth_date=request.birth_date,
                birth_number=NumberInfo(**cached["birth_number"]),
                destiny_number=NumberInfo(**cached["destiny_number"]),
                name_number=NameNumberInfo(**cached["name_number"]),
                compatibility=CompatibilityInfo(**cached["compatibility"]),
                lucky_numbers=cached["lucky_numbers"],
                lucky_days=cached["lucky_days"],
                lucky_colors=cached["lucky_colors"]
            )
        
        print(f"[CACHE MISS] Calculating for {request.name} ({request.birth_date})")
        
        # -----------------------------------------------------------------
        # STEP 2: Parse birth date
        # -----------------------------------------------------------------
        try:
            birth_dt = datetime.strptime(request.birth_date, "%Y-%m-%d")
        except ValueError as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid birth_date format. Use YYYY-MM-DD. Error: {str(e)}"
            )
        
        # -----------------------------------------------------------------
        # STEP 3: Calculate numerology
        # -----------------------------------------------------------------
        numerology = get_full_numerology(request.name, birth_dt)
        
        # -----------------------------------------------------------------
        # STEP 4: Save to cache
        # -----------------------------------------------------------------
        save_to_cache(request.name, request.birth_date, numerology)
        
        # -----------------------------------------------------------------
        # STEP 5: Return response
        # -----------------------------------------------------------------
        return NumerologyResponse(
            success=True,
            cached=False,
            user_id=request.user_id,
            name=request.name,
            birth_date=request.birth_date,
            birth_number=NumberInfo(**numerology["birth_number"]),
            destiny_number=NumberInfo(**numerology["destiny_number"]),
            name_number=NameNumberInfo(**numerology["name_number"]),
            compatibility=CompatibilityInfo(**numerology["compatibility"]),
            lucky_numbers=numerology["lucky_numbers"],
            lucky_days=numerology["lucky_days"],
            lucky_colors=numerology["lucky_colors"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return {
        "total_entries": len(NUMEROLOGY_CACHE),
        "keys": list(NUMEROLOGY_CACHE.keys())
    }


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached numerology readings."""
    NUMEROLOGY_CACHE.clear()
    return {"status": "cleared", "message": "Cache cleared successfully"}


# =============================================================================
# RUN SERVER
# =============================================================================
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081, log_level="info")
