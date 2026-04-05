"""
Tattva API - Vedic Astrology Service
=====================================
FastAPI service for Vedic Astrology calculations including birth charts,
yogas, panchang, dasa periods, and psychic profiles.

Run with: uvicorn api.main:app --reload --port 8000
"""

import sys
import os

# Load environment variables from .env file in VedAstroPy directory
from dotenv import load_dotenv
vedastro_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(vedastro_dir, '.env'))

API_VERSION_DEFAULT = "0.6.0"
APP_VERSION = os.getenv("VERSION", API_VERSION_DEFAULT)
BUILD_ID = os.getenv("BUILD_ID")
ENVIRONMENT = os.getenv("ENVIRONMENT")

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic.psychic_profile import (
    get_psychic_profile, 
    get_psychic_channel, 
    get_superpower, 
    get_signal_strength,
    get_psychic_compatibility
)
from logic.geolocation import get_location, get_coordinates
from logic.calculate import get_planet_longitude, get_lagnam
from logic.time import AstroTime
from logic.consts import Planet
from logic.panchang import get_tithi, get_yoga, get_nitya_yoga_details, get_karana
from logic.nakshatra import get_nakshatra, get_tara_bala, NAKSHATRAS
from logic.sunrise import get_sun_times
from logic.dasa import get_vimshottari_dasa, get_vimshottari_dasa_full, get_vimshottari_dasa_schedule
from logic.varga import get_all_vargas
from logic.numerology import get_full_numerology, get_name_number_prediction
from logic.daily_prediction import calculate_daily_prediction
from logic.rasi import RASIS, get_rasi, get_gochara_house
from logic.ashtakavarga import get_all_bhinnashtakavarga, get_sarvashtakavarga_points
from logic.functional_nature import get_functional_nature, get_functional_nature_categorized
from logic.shadbala import get_shadbala_summary, get_shadbala_ratios
from logic.vedha import calculate_vedha_status
from logic.gochara import get_gochara_predictions, get_gochara_summary, get_gochara_prediction

# Database imports
from api.database import (
    get_db, save_profile, get_profile_by_id, get_profiles_by_user,
    save_daily_prediction, get_daily_prediction
)

# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title="Tattva - Vedic Astrology API",
    description="""
    Comprehensive Vedic Astrology API providing birth chart calculations, 
    yoga predictions, panchang, dasa periods, divisional charts, numerology,
    and psychic profile analysis.
    
    ## Key Features
    
    - **Birth Charts**: Planetary positions, Lagna, house placements
    - **Yogas**: 115 yoga combinations including Raj, Dhana, Pancha Mahapurusha, Malika, and many more
    - **Panchang**: Tithi, Nakshatra, Yoga, Karana calculations
    - **Dasa Periods**: Vimshottari Dasa system with sub-periods
    - **Divisional Charts**: D1 through D60 varga calculations
    - **Numerology**: Pythagorean and Chaldean systems
    - **Psychic Profiles**: 1,296 unique combinations based on Moon, Nakshatra, and Ketu
    - **Daily Predictions**: Transit-based mood, energy, and luck forecasts
    
    Built with Swiss Ephemeris for precise astronomical calculations.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _parse_local_datetime(date_str: str, time_str: str, tz_name: str) -> datetime:
    import pytz

    try:
        tz = pytz.timezone(tz_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone '{tz_name}': {e}")

    try:
        date_parts = date_str.split("-")
        time_parts = time_str.split(":")

        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2]) if len(time_parts) > 2 and time_parts[2] else 0

        naive_dt = datetime(year, month, day, hour, minute, second)
        return tz.localize(naive_dt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {e}")


# =============================================================================
# Request/Response Models
# =============================================================================

class BirthData(BaseModel):
    """Birth data input for profile generation."""
    name: str = Field(..., description="Person's name", example="John Doe")
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)", example="1988-06-07")
    birth_time: str = Field(..., description="Birth time (HH:MM)", example="20:40")
    birth_place: str = Field(..., description="Birth city name", example="Chennai")
    latitude: Optional[float] = Field(None, description="Override latitude")
    longitude: Optional[float] = Field(None, description="Override longitude")
    timezone: Optional[str] = Field(None, description="Override timezone", example="Asia/Kolkata")
    user_id: Optional[str] = Field(None, description="User ID for saving to database")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "birth_date": "1988-06-07",
                "birth_time": "20:40",
                "birth_place": "Chennai",
                "user_id": "user123"
            }
        }


class ChannelResponse(BaseModel):
    """Psychic channel information."""
    moon_sign: str
    element: str
    channel_name: str
    channel_short: str
    definition: str
    mechanism: str
    strengths: List[str]
    weaknesses: List[str]
    color: str


class SuperpowerResponse(BaseModel):
    """Superpower information."""
    nakshatra_number: int
    nakshatra_name: str
    superpower: str
    archetype: str
    ability: str
    specialty: str
    deity: str
    activation: str


class SignalStrengthResponse(BaseModel):
    """Signal strength information."""
    ketu_house: int
    title: str
    intensity: str
    percentage: int
    description: str
    manifestation: str
    challenge: str
    gift: str


class PsychicProfileResponse(BaseModel):
    """Complete psychic profile response."""
    id: Optional[str] = None
    name: str
    birth_data: dict
    title: str
    description: str
    overall_potency: int
    potency_level: str
    channel: ChannelResponse
    superpower: SuperpowerResponse
    signal_strength: SignalStrengthResponse
    how_it_works: str
    best_use: str
    activation_trigger: str
    main_gift: str
    main_challenge: str
    color: str
    created_at: Optional[str] = None


class CompatibilityRequest(BaseModel):
    """Request for Kundali / Ashtakuta compatibility check."""
    male_profile_id: str = Field(..., description="Profile ID for the male partner")
    female_profile_id: str = Field(..., description="Profile ID for the female partner")
    # Legacy aliases (kept for backward compatibility)
    profile1_id: Optional[str] = Field(None, description="Alias for male_profile_id (deprecated)")
    profile2_id: Optional[str] = Field(None, description="Alias for female_profile_id (deprecated)")


class CompatibilityResponse(BaseModel):
    """Kundali compatibility result."""
    compatibility_score: int
    element_match: str
    complementary_powers: bool
    combined_title: str
    synergy: str
    # Kundali Ashtakuta results
    kuta_score: Optional[int] = None
    raw_points: Optional[int] = None
    score_summary: Optional[str] = None
    heart_icon: Optional[str] = None
    factors: Optional[list] = None


class LocationResponse(BaseModel):
    """Location lookup response."""
    name: str
    latitude: float
    longitude: float
    timezone: str
    country: Optional[str] = None


class DailyPredictionRequest(BaseModel):
    """Request for daily prediction."""
    user_id: str = Field(..., description="User ID for caching")
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)", example="1988-06-07")
    birth_time: str = Field(..., description="Birth time (HH:MM)", example="20:40")
    birth_place: str = Field(..., description="Birth city", example="Chennai")
    lagna_sign: str = Field(..., description="Lagna/Ascendant sign", example="Sagittarius")
    birth_nakshatra: str = Field(..., description="Birth nakshatra", example="Purva Bhadrapada")
    prediction_date: Optional[str] = Field(None, description="Date to predict (YYYY-MM-DD), defaults to today")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = Field(None, example="Asia/Kolkata")


class DailyPredictionResponse(BaseModel):
    """Daily prediction response."""
    date: str
    cached: bool = Field(..., description="Whether result was retrieved from cache")
    transit_moon: dict
    mood: dict
    fuel: dict
    luck: dict
    overall_prediction: str


class GocharaPanchangRequest(BaseModel):
    """Request for daily sky state + timing tables."""

    place: Optional[str] = Field(None, description="City name (used if lat/lon not provided)", example="Chennai")
    latitude: Optional[float] = Field(None, description="Latitude override")
    longitude: Optional[float] = Field(None, description="Longitude override")
    timezone: Optional[str] = Field(None, description="IANA timezone name", example="Asia/Kolkata")

    date: Optional[str] = Field(None, description="Local date YYYY-MM-DD (defaults to today)")
    time: Optional[str] = Field(None, description="Local time HH:MM[:SS] (defaults to now)")

    natal_nakshatra: str = Field(
        "Purva Bhadrapada",
        description="Natal nakshatra name for Tara Bala baseline",
        example="Purva Bhadrapada",
    )


class GocharaPredictionRequest(BaseModel):
    """Request for personal Gochara (transit) predictions.

    Provide birth data so the natal Moon sign can be determined, then
    specify the transit date/time and location for current planet positions.
    """

    # Birth data
    birth_date: str = Field(..., description="Birth date YYYY-MM-DD", example="1988-06-07")
    birth_time: str = Field(..., description="Birth time HH:MM[:SS]", example="20:40")
    birth_place: Optional[str] = Field(None, description="Birth city name", example="Chennai")
    birth_latitude: Optional[float] = Field(None, description="Birth latitude override")
    birth_longitude: Optional[float] = Field(None, description="Birth longitude override")
    birth_timezone: Optional[str] = Field(None, description="Birth timezone (IANA)", example="Asia/Kolkata")

    # Transit date/time + location (defaults to now)
    transit_place: Optional[str] = Field(None, description="Transit city name (defaults to birth place)")
    transit_latitude: Optional[float] = Field(None, description="Transit latitude override")
    transit_longitude: Optional[float] = Field(None, description="Transit longitude override")
    transit_timezone: Optional[str] = Field(None, description="Transit timezone (IANA)")
    transit_date: Optional[str] = Field(None, description="Transit date YYYY-MM-DD (defaults to today)")
    transit_time: Optional[str] = Field(None, description="Transit time HH:MM[:SS] (defaults to now)")


class DailyFiveStepRequest(BaseModel):
    """Request for the 5-step daily workflow.

    This endpoint uses:
      - Current location for sunrise/vara lord and current transits
      - Birth data for natal Moon and Ashtakavarga (BAV)
    """

    # Birth data (for natal baseline)
    birth_date: str = Field(..., description="Birth date (YYYY-MM-DD)", example="1988-06-07")
    birth_time: str = Field(..., description="Birth time (HH:MM[:SS])", example="20:40")
    birth_place: Optional[str] = Field(None, description="Birth city name")
    birth_latitude: Optional[float] = Field(None, description="Birth latitude override")
    birth_longitude: Optional[float] = Field(None, description="Birth longitude override")
    birth_timezone: Optional[str] = Field(None, description="Birth timezone override", example="Asia/Kolkata")

    # Current location (required)
    current_place: Optional[str] = Field(None, description="Current city name", example="Morrisville")
    current_latitude: Optional[float] = Field(None, description="Current latitude override")
    current_longitude: Optional[float] = Field(None, description="Current longitude override")
    current_timezone: Optional[str] = Field(None, description="Current timezone override", example="America/New_York")

    # When to evaluate (defaults to now in current timezone)
    date: Optional[str] = Field(None, description="Local date YYYY-MM-DD (defaults to today at current location)")
    time: Optional[str] = Field(None, description="Local time HH:MM[:SS] (defaults to now at current location)")

    # Step 2 baseline (defaults to Purva Bhadrapada)
    baseline_nakshatra: str = Field(
        "Purva Bhadrapada",
        description="Baseline nakshatra for Tara Bala distance (Step 2)",
        example="Purva Bhadrapada",
    )


# =============================================================================
# API Endpoints
# =============================================================================
# Health Check Endpoints
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for Cloud Run."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "Tattva API",
            "version": APP_VERSION,
            "build_id": BUILD_ID,
            "environment": ENVIRONMENT,
            "yogas": 115,
            "modules": 18
        }
    )

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "service": "Tattva Vedic Astrology API",
        "status": "running",
        "version": APP_VERSION,
        "build_id": BUILD_ID,
        "environment": ENVIRONMENT,
        "total_combinations": 1296,
        "yogas_implemented": 115,
        "modules": 18,
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/api/v1/test-daily", tags=["Debug"])
async def test_daily_endpoint(request: DailyPredictionRequest):
    """Test endpoint to debug daily prediction."""
    import traceback
    
    try:
        print("Step 1: Received request")
        print(f"Request data: {request}")
        
        # Determine prediction date
        prediction_date = request.prediction_date or datetime.now().strftime("%Y-%m-%d")
        print(f"Step 2: Prediction date: {prediction_date}")
        
        # Get location
        if request.latitude and request.longitude:
            lat, lon = request.latitude, request.longitude
            tz_name = request.timezone or "UTC"
        else:
            location = get_location(request.birth_place)
            lat = location['latitude']
            lon = location['longitude']
            tz_name = request.timezone or location['timezone']
        print(f"Step 3: Location: lat={lat}, lon={lon}, tz={tz_name}")
        
        # Parse birth datetime
        birth_dt = _parse_local_datetime(request.birth_date, request.birth_time, tz_name)
        print(f"Step 4: Birth datetime: {birth_dt}")
        
        # Create AstroTime
        birth_time_obj = AstroTime(dt=birth_dt, lat=lat, lon=lon)
        print("Step 5: AstroTime created")
        
        # Calculate birth moon
        birth_moon_long = get_planet_longitude(Planet.Moon, birth_time_obj)
        print(f"Step 6: Birth moon longitude: {birth_moon_long}")
        
        # Get nakshatra
        birth_nak_name, birth_nak_num, _, _ = get_nakshatra(birth_moon_long)
        print(f"Step 7: Nakshatra: {birth_nak_name} ({birth_nak_num})")
        
        # Get lagna number
        lagna_num = None
        for i, rasi in enumerate(RASIS):
            if request.lagna_sign.lower() in rasi.lower():
                lagna_num = i + 1
                break
        print(f"Step 8: Lagna num: {lagna_num}")
        
        # Calculate prediction
        prediction = calculate_daily_prediction(
            birth_datetime=birth_dt,
            birth_lat=lat,
            birth_lon=lon,
            birth_lagna_num=lagna_num,
            birth_nakshatra_num=birth_nak_num,
            birth_moon_longitude=birth_moon_long,
            prediction_date=prediction_date,
            timezone=tz_name
        )
        print(f"Step 9: Prediction calculated: {prediction['date']}")
        
        return {"status": "success", "prediction": prediction}
        
    except Exception as e:
        tb = traceback.format_exc()
        print(f"ERROR in test-daily:\n{tb}")
        return {"status": "error", "message": str(e), "traceback": tb}


@app.get("/api/v1/location/{city}", response_model=LocationResponse, tags=["Utilities"])
async def lookup_location(city: str):
    """
    Look up coordinates and timezone for a city.
    
    Useful for getting location data before generating a profile.
    """
    location = get_location(city)
    if not location:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    
    return LocationResponse(
        name=location['name'],
        latitude=location['latitude'],
        longitude=location['longitude'],
        timezone=location['timezone'],
        country=location.get('country')
    )


@app.post("/api/v1/profile/generate", response_model=PsychicProfileResponse, tags=["Psychic Profile"])
async def generate_profile(birth_data: BirthData, save: bool = False):
    """
    Generate a Psychic Profile from birth data.
    
    ## The Formula
    
    - **Step 1**: Moon Element → Psychic Channel (Clairsentience/Claircognizance/Telepathy/Psychometry)
    - **Step 2**: Nakshatra → Superpower (27 unique abilities)
    - **Step 3**: Ketu House → Signal Strength (12 intensity levels)
    
    Set `save=true` to store the profile in the database.
    """
    # Get location
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(
                status_code=400, 
                detail=f"Could not find location '{birth_data.birth_place}'. Please provide latitude/longitude."
            )
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
    
    # Parse datetime
    dt = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    
    # Generate profile
    try:
        profile = get_psychic_profile(dt, lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating profile: {str(e)}")
    
    # Build response
    response = PsychicProfileResponse(
        name=birth_data.name,
        birth_data={
            "date": birth_data.birth_date,
            "time": birth_data.birth_time,
            "place": birth_data.birth_place,
            "latitude": lat,
            "longitude": lon,
            "timezone": tz_name
        },
        title=profile['title'],
        description=profile['description'],
        overall_potency=profile['overall_potency'],
        potency_level=profile['potency_level'],
        channel=ChannelResponse(
            moon_sign=profile['channel']['moon_sign'],
            element=profile['channel']['element'],
            channel_name=profile['channel']['channel_name'],
            channel_short=profile['channel']['channel_short'],
            definition=profile['channel']['definition'],
            mechanism=profile['channel']['mechanism'],
            strengths=profile['channel']['strengths'],
            weaknesses=profile['channel']['weaknesses'],
            color=profile['channel']['color']
        ),
        superpower=SuperpowerResponse(
            nakshatra_number=profile['superpower']['nakshatra_number'],
            nakshatra_name=profile['superpower']['nakshatra_name'],
            superpower=profile['superpower']['superpower'],
            archetype=profile['superpower']['archetype'],
            ability=profile['superpower']['ability'],
            specialty=profile['superpower']['specialty'],
            deity=profile['superpower']['deity'],
            activation=profile['superpower']['activation']
        ),
        signal_strength=SignalStrengthResponse(
            ketu_house=profile['signal_strength']['ketu_house'],
            title=profile['signal_strength']['title'],
            intensity=profile['signal_strength']['intensity'],
            percentage=profile['signal_strength']['percentage'],
            description=profile['signal_strength']['description'],
            manifestation=profile['signal_strength']['manifestation'],
            challenge=profile['signal_strength']['challenge'],
            gift=profile['signal_strength']['gift']
        ),
        how_it_works=profile['how_it_works'],
        best_use=profile['best_use'],
        activation_trigger=profile['activation_trigger'],
        main_gift=profile['main_gift'],
        main_challenge=profile['main_challenge'],
        color=profile['color']
    )
    
    # Save to database if requested
    if save and birth_data.user_id:
        try:
            saved_id = await save_profile(response.dict(), birth_data.user_id)
            response.id = saved_id
            response.created_at = datetime.utcnow().isoformat()
        except Exception as e:
            # Log error but don't fail the request
            print(f"Warning: Could not save to database: {e}")
    
    return response


@app.get("/api/v1/profile/{profile_id}", response_model=PsychicProfileResponse, tags=["Psychic Profile"])
async def get_profile(profile_id: str):
    """
    Retrieve a saved Psychic Profile by ID.
    """
    profile = await get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.get("/api/v1/profiles/user/{user_id}", response_model=List[PsychicProfileResponse], tags=["Psychic Profile"])
async def get_user_profiles(user_id: str, limit: int = 10):
    """
    Get all profiles for a specific user.
    """
    profiles = await get_profiles_by_user(user_id, limit)
    return profiles


@app.post("/api/v1/profile/compatibility", response_model=CompatibilityResponse, tags=["Psychic Profile"])
async def check_compatibility(request: CompatibilityRequest):
    """
    Check Kundali (Ashtakuta) compatibility between two birth profiles.

    Scores all 8 classic Kutas (max 36 points) and evaluates 7 additional
    qualitative factors including Rajju, Vedha, Kuja Dosha, and Bad Constellations.
    Returns a 0–100 percentage score rounded to the nearest 5.
    """
    from logic.kundali_matching import get_kundali_matching

    male_id   = request.male_profile_id   or request.profile1_id
    female_id = request.female_profile_id or request.profile2_id

    if not male_id or not female_id:
        raise HTTPException(status_code=400, detail="Both male_profile_id and female_profile_id are required")

    male_profile   = await get_profile_by_id(male_id)
    female_profile = await get_profile_by_id(female_id)

    if not male_profile or not female_profile:
        raise HTTPException(status_code=404, detail="One or both profiles not found")

    def _profile_to_astrotime(profile: dict) -> AstroTime:
        bd = profile.get("birth_data", {})
        dt = _parse_local_datetime(
            bd["date"], bd["time"], bd.get("timezone", "UTC")
        )
        return AstroTime(dt=dt, lat=bd["latitude"], lon=bd["longitude"])

    try:
        male_time   = _profile_to_astrotime(male_profile)
        female_time = _profile_to_astrotime(female_profile)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=422, detail=f"Profile missing required birth data: {e}")

    try:
        match = get_kundali_matching(male_time, female_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating Kundali match: {e}")

    summary = match["summary"]
    return CompatibilityResponse(
        compatibility_score=match["kuta_score"],
        element_match=f"{male_profile.get('channel', {}).get('element', '')} + {female_profile.get('channel', {}).get('element', '')}",
        complementary_powers=match["kuta_score"] >= 60,
        combined_title=f"{male_profile.get('title', '')} & {female_profile.get('title', '')}",
        synergy=summary["score_summary"],
        kuta_score=match["kuta_score"],
        raw_points=match["raw_points"],
        score_summary=summary["score_summary"],
        heart_icon=summary["heart_icon"],
        factors=match["factors"],
    )


@app.post("/api/v1/profile/complete", tags=["Complete Profile"])
async def get_complete_profile(birth_data: BirthData):
    """
    Get complete astrological profile optimized for LLM prediction engines.
    
    **LLM-Friendly Format:**
    - ✅ Executive summary in plain English
    - ✅ Interpretive descriptions for all data points
    - ✅ Natural language explanations
    - ✅ Prediction-ready insights with life area mappings
    - ✅ Timing indicators and triggers
    - ✅ Strength/weakness analysis
    - ✅ Combination effects and synergies
    
    **Perfect for AI/algorithmic prediction systems!**
    """
    import pytz
    from logic.yogas import get_all_yogas
    from logic.lordship import get_lord_of_house
    from logic.psychic_profile import get_house_from_longitude
    from logic.varga import (
        get_d2_hora, get_d3_drekkana, get_d4_chaturthamsa, get_d5_panchamsa,
        get_d6_shashtamsa, get_d7_saptamsa, get_d8_ashtamsa, get_d9_navamsa,
        get_d10_dasamsa, get_d11_ekadasamsa, get_d12_dwadasamsa, get_d16_shodasamsa,
        get_d20_vimsamsa, get_d24_chaturvimsamsa, get_d27_bhamsa, get_d30_trimsamsa,
        get_d40_khavedamsa, get_d45_akshavedamsa, get_d60_shashtiamsa
    )
    
    # Helper function for rasi interpretations
    def get_rasi_interpretation(rasi_name, planet_name=None):
        interpretations = {
            'Aries': {'element': 'Fire', 'quality': 'Cardinal', 'traits': ['Bold', 'Pioneering', 'Energetic', 'Impulsive'], 'areas': ['Leadership', 'Initiative', 'Action']},
            'Taurus': {'element': 'Earth', 'quality': 'Fixed', 'traits': ['Stable', 'Practical', 'Sensual', 'Stubborn'], 'areas': ['Finance', 'Resources', 'Comfort']},
            'Gemini': {'element': 'Air', 'quality': 'Mutable', 'traits': ['Curious', 'Communicative', 'Versatile', 'Scattered'], 'areas': ['Communication', 'Learning', 'Siblings']},
            'Cancer': {'element': 'Water', 'quality': 'Cardinal', 'traits': ['Emotional', 'Nurturing', 'Protective', 'Moody'], 'areas': ['Home', 'Family', 'Emotions']},
            'Leo': {'element': 'Fire', 'quality': 'Fixed', 'traits': ['Confident', 'Creative', 'Generous', 'Proud'], 'areas': ['Creativity', 'Romance', 'Self-expression']},
            'Virgo': {'element': 'Earth', 'quality': 'Mutable', 'traits': ['Analytical', 'Perfectionist', 'Service-oriented', 'Critical'], 'areas': ['Health', 'Work', 'Details']},
            'Libra': {'element': 'Air', 'quality': 'Cardinal', 'traits': ['Diplomatic', 'Harmonious', 'Indecisive', 'Social'], 'areas': ['Relationships', 'Partnership', 'Balance']},
            'Scorpio': {'element': 'Water', 'quality': 'Fixed', 'traits': ['Intense', 'Transformative', 'Secretive', 'Powerful'], 'areas': ['Transformation', 'Intimacy', 'Occult']},
            'Sagittarius': {'element': 'Fire', 'quality': 'Mutable', 'traits': ['Optimistic', 'Philosophical', 'Adventurous', 'Blunt'], 'areas': ['Higher learning', 'Travel', 'Wisdom']},
            'Capricorn': {'element': 'Earth', 'quality': 'Cardinal', 'traits': ['Ambitious', 'Disciplined', 'Reserved', 'Practical'], 'areas': ['Career', 'Authority', 'Structure']},
            'Aquarius': {'element': 'Air', 'quality': 'Fixed', 'traits': ['Innovative', 'Humanitarian', 'Detached', 'Rebellious'], 'areas': ['Innovation', 'Community', 'Ideals']},
            'Pisces': {'element': 'Water', 'quality': 'Mutable', 'traits': ['Compassionate', 'Intuitive', 'Escapist', 'Artistic'], 'areas': ['Spirituality', 'Creativity', 'Service']}
        }
        return interpretations.get(rasi_name, {})
    
    # Helper for planet meanings
    def get_planet_interpretation(planet_name, rasi_name):
        planet_meanings = {
            'Sun': {'signifies': 'Soul, ego, vitality, father, authority', 'life_areas': ['Career', 'Recognition', 'Health', 'Leadership']},
            'Moon': {'signifies': 'Mind, emotions, mother, nurturing', 'life_areas': ['Emotions', 'Mental state', 'Home', 'Public']},
            'Mars': {'signifies': 'Energy, courage, siblings, property', 'life_areas': ['Action', 'Conflict', 'Sports', 'Real estate']},
            'Mercury': {'signifies': 'Intelligence, communication, business', 'life_areas': ['Learning', 'Business', 'Writing', 'Trade']},
            'Jupiter': {'signifies': 'Wisdom, expansion, teacher, fortune', 'life_areas': ['Higher education', 'Philosophy', 'Children', 'Wealth']},
            'Venus': {'signifies': 'Love, beauty, luxury, relationships', 'life_areas': ['Romance', 'Arts', 'Comfort', 'Marriage']},
            'Saturn': {'signifies': 'Discipline, karma, delays, longevity', 'life_areas': ['Career', 'Responsibility', 'Obstacles', 'Longevity']},
            'Rahu': {'signifies': 'Obsession, foreign, innovation, material desires', 'life_areas': ['Ambition', 'Technology', 'Foreign lands', 'Unconventional']},
            'Ketu': {'signifies': 'Spirituality, detachment, past life, moksha', 'life_areas': ['Spirituality', 'Liberation', 'Losses', 'Enlightenment']}
        }
        base = planet_meanings.get(planet_name, {})
        rasi_info = get_rasi_interpretation(rasi_name)
        return {**base, 'placement_effect': f"{planet_name} in {rasi_name} blends {base.get('signifies', '')} with {rasi_info.get('element', '')} element energy"}
    
    # Get location coordinates
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
        place_name = birth_data.birth_place
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find location '{birth_data.birth_place}'"
            )
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
        place_name = location['name']
    
    # Parse birth datetime
    birth_datetime_tz = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    astro_time = AstroTime(birth_datetime_tz, lat, lon)
    
    # 1. PSYCHIC PROFILE
    psychic_profile = get_psychic_profile(birth_datetime_tz, lat, lon)
    
    # 2. BIRTH CHART - Enhanced with interpretations
    # First get Lagna longitude for house calculations
    lagna_long = get_lagnam(astro_time)
    lagna_rasi_num = int(lagna_long / 30) + 1
    lagna_rasi = RASIS[lagna_rasi_num - 1]
    
    planets_data = []
    moon_sign = None
    sun_sign = None
    
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, 
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        longitude = get_planet_longitude(planet, astro_time)
        rasi_num = int(longitude / 30) + 1
        rasi_name = RASIS[rasi_num - 1]
        nakshatra = get_nakshatra(longitude)
        
        # Calculate house position
        house = get_house_from_longitude(longitude, lagna_long)
        
        # Calculate divisional charts - All 20 Vargas (Shodashvarga)
        d2_sign, d2_num = get_d2_hora(longitude)
        d3_sign, d3_num = get_d3_drekkana(longitude)
        d4_sign, d4_num = get_d4_chaturthamsa(longitude)
        d5_sign, d5_num = get_d5_panchamsa(longitude)
        d6_sign, d6_num = get_d6_shashtamsa(longitude)
        d7_sign, d7_num = get_d7_saptamsa(longitude)
        d8_sign, d8_num = get_d8_ashtamsa(longitude)
        d9_sign, d9_num = get_d9_navamsa(longitude)
        d10_sign, d10_num = get_d10_dasamsa(longitude)
        d11_sign, d11_num = get_d11_ekadasamsa(longitude)
        d12_sign, d12_num = get_d12_dwadasamsa(longitude)
        d16_sign, d16_num = get_d16_shodasamsa(longitude)
        d20_sign, d20_num = get_d20_vimsamsa(longitude)
        d24_sign, d24_num = get_d24_chaturvimsamsa(longitude)
        d27_sign, d27_num = get_d27_bhamsa(longitude)
        d30_sign, d30_num = get_d30_trimsamsa(longitude)
        d40_sign, d40_num = get_d40_khavedamsa(longitude)
        d45_sign, d45_num = get_d45_akshavedamsa(longitude)
        d60_sign, d60_num = get_d60_shashtiamsa(longitude)
        
        if planet == Planet.Moon:
            moon_sign = rasi_name
        if planet == Planet.Sun:
            sun_sign = rasi_name
        
        planet_interp = get_planet_interpretation(planet.name, rasi_name)
        rasi_interp = get_rasi_interpretation(rasi_name)
        
        # Unpack nakshatra tuple: (name, number, percentage, pada)
        nakshatra_name, nakshatra_num, nakshatra_pct, nakshatra_pada = nakshatra
        
        planets_data.append({
            'planet': planet.name,
            'longitude': round(longitude, 2),
            'rasi': rasi_name,
            'rasi_num': rasi_num,
            'house': house,
            'd2_hora': d2_sign,
            'd2_num': d2_num,
            'd3_drekkana': d3_sign,
            'd3_num': d3_num,
            'd4_chaturthamsa': d4_sign,
            'd4_num': d4_num,
            'd5_panchamsa': d5_sign,
            'd5_num': d5_num,
            'd6_shashtamsa': d6_sign,
            'd6_num': d6_num,
            'd7_saptamsa': d7_sign,
            'd7_num': d7_num,
            'd8_ashtamsa': d8_sign,
            'd8_num': d8_num,
            'd9_navamsa': d9_sign,
            'd9_num': d9_num,
            'd10_dasamsa': d10_sign,
            'd10_num': d10_num,
            'd11_ekadasamsa': d11_sign,
            'd11_num': d11_num,
            'd12_dwadasamsa': d12_sign,
            'd12_num': d12_num,
            'd16_shodasamsa': d16_sign,
            'd16_num': d16_num,
            'd20_vimsamsa': d20_sign,
            'd20_num': d20_num,
            'd24_chaturvimsamsa': d24_sign,
            'd24_num': d24_num,
            'd27_bhamsa': d27_sign,
            'd27_num': d27_num,
            'd30_trimsamsa': d30_sign,
            'd30_num': d30_num,
            'd40_khavedamsa': d40_sign,
            'd40_num': d40_num,
            'd45_akshavedamsa': d45_sign,
            'd45_num': d45_num,
            'd60_shashtiamsa': d60_sign,
            'd60_num': d60_num,
            'nakshatra': nakshatra_name,
            'pada': nakshatra_pada,
            'interpretation': {
                'signifies': planet_interp.get('signifies', ''),
                'life_areas': planet_interp.get('life_areas', []),
                'placement': planet_interp.get('placement_effect', ''),
                'element': rasi_interp.get('element', ''),
                'traits': rasi_interp.get('traits', [])
            }
        })
    
    # Lagna interpretation (already calculated above)
    lagna_interp = get_rasi_interpretation(lagna_rasi)
    
    lagna_data = {
        'longitude': round(lagna_long, 2),
        'rasi': lagna_rasi,
        'rasi_num': lagna_rasi_num,
        'interpretation': {
            'description': f"{lagna_rasi} rising indicates a personality that is {', '.join(lagna_interp.get('traits', [])[:3])}.",
            'element': lagna_interp.get('element', ''),
            'quality': lagna_interp.get('quality', ''),
            'life_focus': lagna_interp.get('areas', []),
            'traits': lagna_interp.get('traits', []),
            'ruling_planet': get_lord_of_house(1, astro_time).name
        }
    }
    
    # 3. PANCHANG with interpretations
    # Get Sun and Moon longitudes for panchang calculations
    sun_long = get_planet_longitude(Planet.Sun, astro_time)
    moon_long = get_planet_longitude(Planet.Moon, astro_time)
    
    # Calculate panchang elements
    tithi_name, tithi_num, tithi_pct = get_tithi(sun_long, moon_long)
    nakshatra_name, nakshatra_num, nakshatra_pct, nakshatra_pada = get_nakshatra(moon_long)
    yoga_name, yoga_num = get_yoga(sun_long, moon_long)
    
    panchang = {
        'tithi': {
            'name': tithi_name,
            'number': tithi_num,
            'percentage': round(tithi_pct, 2),
            'interpretation': f"Tithi indicates lunar phase energy affecting emotional and mental states."
        },
        'nakshatra': {
            'name': nakshatra_name,
            'number': nakshatra_num,
            'pada': nakshatra_pada,
            'percentage': round(nakshatra_pct, 2),
            'interpretation': f"Birth nakshatra determines core personality traits, life path, and karmic tendencies."
        },
        'yoga': {
            'name': yoga_name,
            'number': yoga_num,
            'interpretation': "Daily yoga indicates auspicious combinations affecting success and fortune."
        },
        'weekday': birth_datetime_tz.strftime('%A'),
        'weekday_planet': {'Monday': 'Moon', 'Tuesday': 'Mars', 'Wednesday': 'Mercury', 
                           'Thursday': 'Jupiter', 'Friday': 'Venus', 'Saturday': 'Saturn', 
                           'Sunday': 'Sun'}[birth_datetime_tz.strftime('%A')]
    }
    
    # 4. DASA PERIODS with timing
    # Get current date for dasa calculation
    current_dt = datetime.now(birth_datetime_tz.tzinfo)
    # Use nakshatra values already calculated above
    maha_dasa_planet, bhukti_planet = get_vimshottari_dasa(nakshatra_num, nakshatra_pct, birth_datetime_tz, current_dt)
    
    # Calculate full 120-year Vimshottari Dasa schedule
    dasa_schedule = get_vimshottari_dasa_schedule(nakshatra_num, nakshatra_pct, birth_datetime_tz)
    
    current_year = datetime.now().year
    birth_year = birth_datetime_tz.year
    age = current_year - birth_year
    
    dasa_interpretation = {
        'mahadasa': {
            'planet': maha_dasa_planet,
            'duration_years': 6 if maha_dasa_planet == 'Sun' else 10 if maha_dasa_planet == 'Moon' else 7 if maha_dasa_planet == 'Mars' else 18 if maha_dasa_planet == 'Rahu' else 16 if maha_dasa_planet == 'Jupiter' else 19 if maha_dasa_planet == 'Saturn' else 17 if maha_dasa_planet == 'Mercury' else 20 if maha_dasa_planet == 'Venus' else 7  # Ketu
        },
        'bhukti': {
            'planet': bhukti_planet
        },
        'current_age': age,
        'life_stage': 'Youth' if age < 30 else 'Middle Age' if age < 60 else 'Elder',
        'prediction_note': f"Currently in {maha_dasa_planet} Mahadasa - this planet's significations are dominant in life now.",
        'full_schedule': dasa_schedule  # Complete 120-year timeline
    }
    
    # 5. YOGAS with detailed interpretations
    yogas = get_all_yogas(astro_time)
    yogas_enhanced = []
    for yoga in yogas:
        # Convert Yoga object to dict with enhancements
        yoga_dict = {
            'name': yoga.name,
            'present': yoga.occurring,
            'nature': yoga.nature.value if hasattr(yoga.nature, 'value') else str(yoga.nature),
            'description': yoga.description,
            'condition': yoga.condition,
            'strength': yoga.strength if yoga.strength else 0,
            'category': 'Wealth' if any(x in yoga.name for x in ['Lakshmi', 'Vasumathi', 'Chatussagara', 'Parvata']) else 
                        'Raja' if 'Raja' in yoga.name else
                        'Moon' if any(x in yoga.name for x in ['GajaKesari', 'Sunapha', 'Anapha', 'Dhurdhura']) else
                        'Mahapurusha' if any(x in yoga.name for x in ['Bhadra', 'Hamsa', 'Malavya', 'Ruchaka', 'Sasha']) else 'Other',
            'life_impact': f"Affects {yoga.nature.value if hasattr(yoga.nature, 'value') else 'general'} aspects of life",
            'timing': 'Active throughout life, especially during related dasa periods',
            'prediction_value': 'High' if yoga.occurring else 'Low'
        }
        yogas_enhanced.append(yoga_dict)
    
    # 6. NUMEROLOGY
    from logic.numerology import get_full_numerology
    numerology = get_full_numerology(birth_data.name, birth_datetime_tz)
    
    # 7. ASHTAKAVARGA (Computationally intensive - store this!)
    # Get BAV (Bhinnashtakavarga) for all 7 planets
    bav_data = get_all_bhinnashtakavarga(astro_time)
    
    # Get SAV (Sarvashtakavarga) total points
    sav_data = get_sarvashtakavarga_points(astro_time)
    
    # Format as arrays (Aries to Pisces = indices 0-11)
    ashtakavarga = {
        "bav": {
            "sun": [bav_data["Sun"][i] for i in range(1, 13)],
            "moon": [bav_data["Moon"][i] for i in range(1, 13)],
            "mars": [bav_data["Mars"][i] for i in range(1, 13)],
            "mercury": [bav_data["Mercury"][i] for i in range(1, 13)],
            "jupiter": [bav_data["Jupiter"][i] for i in range(1, 13)],
            "venus": [bav_data["Venus"][i] for i in range(1, 13)],
            "saturn": [bav_data["Saturn"][i] for i in range(1, 13)]
        },
        "sav": {
            "total_points": [sav_data[i] for i in range(1, 13)],
            "interpretation": "Points 28+ = Good transit, <25 = Challenging transit"
        }
    }
    
    # 8. FUNCTIONAL NATURE (Benefic/Malefic by Ascendant)
    functional_nature_detailed = get_functional_nature(lagna_rasi_num)
    functional_nature = get_functional_nature_categorized(lagna_rasi_num)
    
    # 9. SHADBALA (Planetary Strength in Rupas)
    # Convert astro_time back to datetime for shadbala calculation
    shadbala_detailed = get_shadbala_summary(birth_datetime_tz, lat, lon)
    shadbala = get_shadbala_ratios(birth_datetime_tz, lat, lon)  # Simple ratios for predictions
    
    # 10. EXECUTIVE SUMMARY for LLMs
    active_yogas = [y['name'] for y in yogas_enhanced if y.get('present', False)]
    
    executive_summary = {
        'personality_overview': f"{birth_data.name} is a {lagna_rasi} rising individual with {sun_sign} Sun and {moon_sign} Moon. Their personality blends {lagna_interp.get('element', '')} element qualities with {', '.join(lagna_interp.get('traits', [])[:2])} traits.",
        'core_strengths': lagna_interp.get('traits', [])[:3],
        'life_path_focus': lagna_interp.get('areas', []),
        'psychic_archetype': psychic_profile['title'],
        'active_yogas_count': len(active_yogas),
        'dominant_yogas': active_yogas[:5],
        'current_dasa_planet': dasa_interpretation.get('mahadasa', {}).get('planet', 'Unknown'),
        'life_stage': 'Youth' if age < 30 else 'Middle Age' if age < 60 else 'Elder',
        'numerology_summary': f"Life Path {numerology.get('life_path_number', 0)} indicates {numerology.get('life_path_meaning', '')}",
        'prediction_readiness': {
            'data_quality': 'Complete',
            'prediction_confidence': 'High',
            'key_factors': ['Yogas', 'Dasa', 'Lagna', 'Nakshatra'],
            'timing_available': True
        }
    }
    
    # 8. PREDICTION FRAMEWORK for AI
    prediction_framework = {
        'immediate_influences': {
            'current_dasa': dasa_interpretation.get('mahadasa', {}),
            'current_antardasa': dasa_interpretation.get('bhukti', {}),
            'active_yogas': active_yogas[:3]
        },
        'life_area_predictions': {
            'career': {
                'significators': ['Sun', 'Saturn', '10th house'],
                'relevant_planets': [p for p in planets_data if p['planet'] in ['Sun', 'Saturn']],
                'relevant_yogas': [y for y in yogas_enhanced if y.get('category') == 'Raja'][:5]
            },
            'relationships': {
                'significators': ['Venus', 'Moon', '7th house'],
                'relevant_planets': [p for p in planets_data if p['planet'] in ['Venus', 'Moon']],
                'relevant_yogas': []  # Add relationship-specific yogas later
            },
            'wealth': {
                'significators': ['Jupiter', 'Venus', '2nd house', '11th house'],
                'relevant_planets': [p for p in planets_data if p['planet'] in ['Jupiter', 'Venus']],
                'relevant_yogas': [y for y in yogas_enhanced if y.get('category') == 'Wealth'][:5]
            },
            'health': {
                'significators': ['Sun', 'Moon', '6th house', 'Lagna'],
                'relevant_planets': [p for p in planets_data if p['planet'] in ['Sun', 'Moon']],
                'lagna_strength': lagna_data
            },
            'spirituality': {
                'significators': ['Jupiter', 'Ketu', '9th house', '12th house'],
                'relevant_planets': [p for p in planets_data if p['planet'] in ['Jupiter', 'Ketu']],
                'psychic_profile': {
                    'title': psychic_profile.get('title', ''),
                    'description': psychic_profile.get('description', '')
                }
            }
        },
        'timing_triggers': {
            'current_year': current_year,
            'age': age,
            'dasa_end_year': 'N/A',  # Would need full dasa calculation for end date
            'critical_ages': [21, 28, 35, 42, 49, 56, 63],  # Saturn returns and other milestones
            'next_milestone': next((a for a in [21, 28, 35, 42, 49, 56, 63] if a > age), None)
        }
    }
    
    # Compile complete LLM-optimized profile
    return {
        'name': birth_data.name,
        'birth_data': {
            'date': birth_data.birth_date,
            'time': birth_data.birth_time,
            'place': place_name,
            'latitude': lat,
            'longitude': lon,
            'timezone': tz_name,
            'age': age
        },
        'executive_summary': executive_summary,
        'psychic_profile': {
            'title': psychic_profile['title'],
            'description': psychic_profile['description'],
            'channel': psychic_profile['channel'],
            'superpower': psychic_profile['superpower'],
            'signal_strength': psychic_profile['signal_strength'],
            'overall_potency': psychic_profile['overall_potency'],
            'how_it_works': psychic_profile.get('how_it_works', ''),
            'best_use': psychic_profile.get('best_use', ''),
            'activation_trigger': psychic_profile.get('activation_trigger', '')
        },
        'birth_chart': {
            'lagna': lagna_data,
            'sun_sign': sun_sign,
            'moon_sign': moon_sign,
            'planets': planets_data
        },
        'panchang': panchang,
        'dasa': dasa_interpretation,
        'yogas': yogas_enhanced,
        'numerology': numerology,
        'ashtakavarga': ashtakavarga,
        'functional_nature': functional_nature,
        'functional_nature_detailed': functional_nature_detailed,
        'shadbala': shadbala,  # Simple ratios for prediction algorithms
        'shadbala_detailed': shadbala_detailed,  # Detailed strength analysis
        'prediction_framework': prediction_framework,
        'generated_at': datetime.now().isoformat(),
        'llm_instructions': {
            'usage': 'This profile is optimized for LLM prediction engines',
            'prediction_approach': 'Combine yogas, dasa periods, and planetary positions for life area predictions',
            'timing_method': 'Use current_dasa and timing_triggers for temporal predictions',
            'strength_assessment': 'Evaluate active_yogas_count and planetary strengths',
            'life_areas': ['career', 'relationships', 'wealth', 'health', 'spirituality']
        }
    }


@app.get("/api/v1/channels", tags=["Reference Data"])
async def get_all_channels():
    """
    Get all 4 psychic channels with descriptions.
    """
    from logic.psychic_profile import PSYCHIC_CHANNELS
    return PSYCHIC_CHANNELS


@app.get("/api/v1/superpowers", tags=["Reference Data"])
async def get_all_superpowers():
    """
    Get all 27 nakshatra-based superpowers.
    """
    from logic.psychic_profile import NAKSHATRA_SUPERPOWERS
    return NAKSHATRA_SUPERPOWERS


@app.get("/api/v1/signal-strengths", tags=["Reference Data"])
async def get_all_signal_strengths():
    """
    Get all 12 Ketu house signal strengths.
    """
    from logic.psychic_profile import KETU_SIGNAL_STRENGTH
    return KETU_SIGNAL_STRENGTH


# =============================================================================
# Birth Chart Endpoints
# =============================================================================

@app.post("/api/v1/chart/planets", tags=["Birth Chart"])
async def get_planet_positions(birth_data: BirthData):
    """
    Get positions of all planets for a birth chart.
    
    Returns planetary longitudes, signs, nakshatras, and houses.
    """
    # Get location
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{birth_data.birth_place}'")
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
    
    # Parse datetime
    dt = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    
    # Create AstroTime
    astro_time = AstroTime(dt, lat, lon)
    
    # Get all planet positions
    planets_data = {}
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, 
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        try:
            longitude = get_planet_longitude(planet, astro_time)
            nakshatra_name, nak_num, nak_percentage, pada = get_nakshatra(longitude)
            
            planets_data[planet.name] = {
                "longitude": round(longitude, 4),
                "sign": SIGNS[int(longitude / 30)],
                "degree_in_sign": round(longitude % 30, 4),
                "nakshatra": nakshatra_name,
                "nakshatra_number": nak_num,
                "nakshatra_pada": pada,
                "nakshatra_percentage": round(nak_percentage, 2)
            }
        except Exception as e:
            planets_data[planet.name] = {"error": str(e)}
    
    # Get Ascendant
    try:
        lagna = get_lagnam(astro_time)
        nak_name, nak_num, nak_percentage, pada = get_nakshatra(lagna)
        planets_data["Ascendant"] = {
            "longitude": round(lagna, 4),
            "sign": SIGNS[int(lagna / 30)],
            "degree_in_sign": round(lagna % 30, 4),
            "nakshatra": nak_name,
            "nakshatra_number": nak_num,
            "nakshatra_pada": pada
        }
    except Exception as e:
        planets_data["Ascendant"] = {"error": str(e)}
    
    return {
        "name": birth_data.name,
        "birth_data": {
            "date": birth_data.birth_date,
            "time": birth_data.birth_time,
            "place": birth_data.birth_place,
            "latitude": lat,
            "longitude": lon,
            "timezone": tz_name
        },
        "planets": planets_data
    }


# SIGNS constant for reference
SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


@app.post("/api/v1/panchang/gochara", tags=["Gochara Panchang"])
async def get_gochara_panchang(request: GocharaPanchangRequest):
    """Daily sky state + personal timing tables.

    Returns:
      - Current planetary positions (9 grahas)
      - Daily panchang: tithi, nakshatra, yoga, karana, vara
      - Hora table (planetary hours, computed from sunrise)
      - Choghadiya table (day/night 8-part periods)
      - Tara Bala summary + full 1..9 table (default natal: Purva Bhadrapada)
    """

    import pytz

    # Resolve location + timezone
    if request.latitude is not None and request.longitude is not None:
        lat = request.latitude
        lon = request.longitude
        tz_name = request.timezone or "UTC"
        place_name = request.place or "(custom coordinates)"
    else:
        if not request.place:
            raise HTTPException(status_code=400, detail="Provide either (latitude, longitude) or place")
        location = get_location(request.place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{request.place}'")
        lat = location['latitude']
        lon = location['longitude']
        tz_name = request.timezone or location['timezone']
        place_name = location.get('name') or request.place

    try:
        tz = pytz.timezone(tz_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid timezone '{tz_name}': {e}")

    now_local = datetime.now(tz)
    date_str = request.date or now_local.strftime("%Y-%m-%d")
    time_str = request.time or now_local.strftime("%H:%M:%S")
    dt_local = _parse_local_datetime(date_str, time_str, tz_name)

    astro_time = AstroTime(dt_local, lat, lon)

    # Planetary positions (9 grahas)
    planets_data = {}
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        try:
            longitude = get_planet_longitude(planet, astro_time)
            nak_name, nak_num, nak_pct, pada = get_nakshatra(longitude)
            planets_data[planet.name] = {
                "longitude": round(longitude, 4),
                "sign": SIGNS[int(longitude / 30)],
                "degree_in_sign": round(longitude % 30, 4),
                "nakshatra": nak_name,
                "nakshatra_number": nak_num,
                "nakshatra_pada": pada,
                "nakshatra_percentage": round(nak_pct, 2),
            }
        except Exception as e:
            planets_data[planet.name] = {"error": str(e)}

    # Panchang
    sun_long = get_planet_longitude(Planet.Sun, astro_time)
    moon_long = get_planet_longitude(Planet.Moon, astro_time)
    tithi_name, tithi_num, tithi_pct = get_tithi(sun_long, moon_long)
    yoga_details = get_nitya_yoga_details(sun_long, moon_long)
    moon_nak_name, moon_nak_num, moon_nak_pct, moon_pada = get_nakshatra(moon_long)
    karana = get_karana(sun_long, moon_long)

    vara_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    vara_name = vara_names[dt_local.weekday()]

    # Tara Bala
    natal_lookup = {n.lower(): i + 1 for i, n in enumerate(NAKSHATRAS)}
    natal_key = request.natal_nakshatra.strip().lower()
    natal_nak_num = natal_lookup.get(natal_key)
    if natal_nak_num is None:
        raise HTTPException(status_code=400, detail=f"Unknown natal_nakshatra '{request.natal_nakshatra}'")

    tara_name, tara_num = get_tara_bala(natal_nak_num, moon_nak_num)
    tara_good = {2, 4, 6, 8, 9}
    tara_bad = {3, 5, 7}
    if tara_num in tara_good:
        tara_quality = "good"
    elif tara_num in tara_bad:
        tara_quality = "challenging"
    else:
        tara_quality = "neutral"

    tara_table = []
    for i in range(1, 10):
        transit_nums = [((natal_nak_num + (i - 1) - 1 + offset) % 27) + 1 for offset in (0, 9, 18)]
        tara_table.append({
            "tara_number": i,
            "tara_name": get_tara_bala(natal_nak_num, transit_nums[0])[0],
            "transit_nakshatras": [{"number": n, "name": NAKSHATRAS[n - 1]} for n in transit_nums],
            "quality": "good" if i in tara_good else ("challenging" if i in tara_bad else "neutral"),
        })

    # Sunrise-based tables (hora + choghadiya)
    try:
        sun_times = get_sun_times(date_local=dt_local, lat=lat, lon=lon, tz_name=tz_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute sunrise/sunset: {e}")

    chaldean_order = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    weekday_lords = {  # Python weekday: Mon=0..Sun=6
        0: "Moon",
        1: "Mars",
        2: "Mercury",
        3: "Jupiter",
        4: "Venus",
        5: "Saturn",
        6: "Sun",
    }

    start_lord = weekday_lords[sun_times.sunrise.weekday()]
    start_index = chaldean_order.index(start_lord)

    day_len = sun_times.sunset - sun_times.sunrise
    night_len = sun_times.next_sunrise - sun_times.sunset
    day_hora = day_len / 12
    night_hora = night_len / 12

    hora_table = []
    for i in range(12):
        start = sun_times.sunrise + (day_hora * i)
        end = sun_times.sunrise + (day_hora * (i + 1))
        lord = chaldean_order[(start_index + i) % 7]
        hora_table.append({
            "index": i + 1,
            "period": "day",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "lord": lord,
        })
    for i in range(12):
        start = sun_times.sunset + (night_hora * i)
        end = sun_times.sunset + (night_hora * (i + 1))
        lord = chaldean_order[(start_index + 12 + i) % 7]
        hora_table.append({
            "index": 12 + i + 1,
            "period": "night",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "lord": lord,
        })

    # Choghadiya sequences (common North Indian table)
    # Keys are Python weekday (Mon=0..Sun=6)
    day_choghadiya = {
        6: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],  # Sunday
        0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],  # Monday
        1: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],  # Tuesday
        2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],  # Wednesday
        3: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],  # Thursday
        4: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],  # Friday
        5: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],  # Saturday
    }
    night_choghadiya = {
        6: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],  # Sunday
        0: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],  # Monday
        1: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],  # Tuesday
        2: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],  # Wednesday
        3: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],  # Thursday
        4: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],  # Friday
        5: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],  # Saturday
    }

    choghadiya_good = {"Amrit", "Shubh", "Labh", "Char"}
    choghadiya_bad = {"Kaal", "Rog", "Udveg"}

    choghadiya_table = []
    day_segment = day_len / 8
    night_segment = night_len / 8

    wd = sun_times.sunrise.weekday()
    for i, name in enumerate(day_choghadiya[wd]):
        start = sun_times.sunrise + (day_segment * i)
        end = sun_times.sunrise + (day_segment * (i + 1))
        choghadiya_table.append({
            "period": "day",
            "index": i + 1,
            "name": name,
            "quality": "good" if name in choghadiya_good else ("bad" if name in choghadiya_bad else "neutral"),
            "start": start.isoformat(),
            "end": end.isoformat(),
        })
    for i, name in enumerate(night_choghadiya[wd]):
        start = sun_times.sunset + (night_segment * i)
        end = sun_times.sunset + (night_segment * (i + 1))
        choghadiya_table.append({
            "period": "night",
            "index": i + 1,
            "name": name,
            "quality": "good" if name in choghadiya_good else ("bad" if name in choghadiya_bad else "neutral"),
            "start": start.isoformat(),
            "end": end.isoformat(),
        })

    return {
        "datetime": dt_local.isoformat(),
        "date": date_str,
        "time": time_str,
        "place": place_name,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz_name,
        "sun": {
            "sunrise": sun_times.sunrise.isoformat(),
            "sunset": sun_times.sunset.isoformat(),
            "next_sunrise": sun_times.next_sunrise.isoformat(),
        },
        "planets": planets_data,
        "panchang": {
            "vara": {"name": vara_name},
            "tithi": {
                "name": tithi_name,
                "number": tithi_num,
                "percentage_elapsed": round(tithi_pct, 2),
                "percentage_remaining": round(100.0 - tithi_pct, 2),
            },
            "karana": karana,
            "yoga": {
                "name": yoga_details['name'],
                "number": yoga_details['number'],
                "deity": yoga_details['deity'],
                "nature": yoga_details['nature'],
                "effect": yoga_details['effect'],
                "percentage_elapsed": round(yoga_details['percentage'], 2),
            },
            "nakshatra": {
                "name": moon_nak_name,
                "number": moon_nak_num,
                "pada": moon_pada,
                "percentage_elapsed": round(moon_nak_pct, 2),
            },
        },
        "hora": {
            "start_lord": start_lord,
            "table": hora_table,
        },
        "choghadiya": {
            "table": choghadiya_table,
        },
        "tara_bala": {
            "natal": {"name": NAKSHATRAS[natal_nak_num - 1], "number": natal_nak_num},
            "transit_moon": {"name": moon_nak_name, "number": moon_nak_num},
            "result": {"tara_name": tara_name, "tara_number": tara_num, "quality": tara_quality},
            "table": tara_table,
        },
    }



@app.post("/api/v1/prediction/gochara", tags=["Daily Prediction"])
async def get_gochara_predictions_endpoint(request: GocharaPredictionRequest):
    """Personal Gochara (transit) predictions based on natal Moon sign.

    For each of the 9 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus,
    Saturn, Rahu, Ketu) this endpoint returns:
    - The gochara house (1–12, counted from natal Moon sign)
    - The overall nature (Good / Bad / Neutral)
    - Per life-area natures: Mind, Studies, Family, Money, Love, Body
    - Full Vedic interpretation text

    Also returns an aggregate summary with good/bad counts and net score.
    """
    import pytz

    # ── Birth location ───────────────────────────────────────────────────────
    if request.birth_latitude is not None and request.birth_longitude is not None:
        b_lat = request.birth_latitude
        b_lon = request.birth_longitude
        b_tz = request.birth_timezone or "UTC"
    elif request.birth_place:
        loc = get_location(request.birth_place)
        if not loc:
            raise HTTPException(status_code=400, detail=f"Could not find birth place '{request.birth_place}'")
        b_lat = loc['latitude']
        b_lon = loc['longitude']
        b_tz = request.birth_timezone or loc['timezone']
    else:
        raise HTTPException(status_code=400, detail="Provide birth_place or birth_latitude/birth_longitude")

    birth_dt = _parse_local_datetime(request.birth_date, request.birth_time, b_tz)
    birth_astro_time = AstroTime(dt=birth_dt, lat=b_lat, lon=b_lon)

    # ── Transit location ─────────────────────────────────────────────────────
    if request.transit_latitude is not None and request.transit_longitude is not None:
        t_lat = request.transit_latitude
        t_lon = request.transit_longitude
        t_tz = request.transit_timezone or "UTC"
        transit_place_name = "(custom coordinates)"
    elif request.transit_place:
        loc = get_location(request.transit_place)
        if not loc:
            raise HTTPException(status_code=400, detail=f"Could not find transit place '{request.transit_place}'")
        t_lat = loc['latitude']
        t_lon = loc['longitude']
        t_tz = request.transit_timezone or loc['timezone']
        transit_place_name = loc.get('name') or request.transit_place
    else:
        # Default to birth location
        t_lat, t_lon, t_tz = b_lat, b_lon, b_tz
        transit_place_name = request.birth_place or "(birth location)"

    try:
        t_pytz = pytz.timezone(t_tz)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid transit timezone '{t_tz}': {e}")

    now_local = datetime.now(t_pytz)
    t_date = request.transit_date or now_local.strftime("%Y-%m-%d")
    t_time = request.transit_time or now_local.strftime("%H:%M:%S")
    transit_dt = _parse_local_datetime(t_date, t_time, t_tz)
    transit_astro_time = AstroTime(dt=transit_dt, lat=t_lat, lon=t_lon)

    # ── Natal Moon sign ──────────────────────────────────────────────────────
    from logic.house_queries import get_planet_sign_num as _sign_num
    birth_moon_sign_num = _sign_num(Planet.Moon, birth_astro_time)
    birth_moon_sign_name = SIGNS[birth_moon_sign_num - 1]

    # ── Compute gochara predictions ──────────────────────────────────────────
    predictions = get_gochara_predictions(birth_astro_time, transit_astro_time)
    summary = get_gochara_summary(birth_astro_time, transit_astro_time)

    return {
        "birth": {
            "date": request.birth_date,
            "time": request.birth_time,
            "place": request.birth_place,
            "latitude": b_lat,
            "longitude": b_lon,
            "timezone": b_tz,
        },
        "transit": {
            "date": t_date,
            "time": t_time,
            "place": transit_place_name,
            "latitude": t_lat,
            "longitude": t_lon,
            "timezone": t_tz,
        },
        "natal_moon": {
            "sign_number": birth_moon_sign_num,
            "sign_name": birth_moon_sign_name,
        },
        "summary": summary,
        "predictions": predictions,
    }


@app.post("/api/v1/prediction/daily-5step", tags=["Daily Prediction"])
async def get_daily_five_step(request: DailyFiveStepRequest):
    """Implements the 5-step daily workflow.

    Step 1: Sunrise at current location -> Vara Lord
    Step 2: Tara Bala from baseline nakshatra -> Safety Score
    Step 3: Moon gochara relative to natal Moon -> Mood Score
    Step 4: BAV strength for transiting planets in their current signs -> Effectiveness
    Step 5: Vedha check -> Active vs Obstructed (placeholder until vedhanka table is ported)
    """

    import pytz

    def _resolve_location(place: str | None, lat: float | None, lon: float | None, tz_override: str | None, *, label: str) -> tuple[str, float, float, str]:
        if lat is not None and lon is not None:
            tz_name = tz_override or "UTC"
            return place or f"({label} coordinates)", lat, lon, tz_name
        if not place:
            raise HTTPException(status_code=400, detail=f"Provide either {label}_latitude/{label}_longitude or {label}_place")
        location = get_location(place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{place}'")
        tz_name = tz_override or location['timezone']
        return location.get('name') or place, location['latitude'], location['longitude'], tz_name

    # Current location is required
    current_place_name, current_lat, current_lon, current_tz_name = _resolve_location(
        request.current_place,
        request.current_latitude,
        request.current_longitude,
        request.current_timezone,
        label="current",
    )

    # Birth location is required for accurate natal Moon + BAV
    birth_place_name, birth_lat, birth_lon, birth_tz_name = _resolve_location(
        request.birth_place,
        request.birth_latitude,
        request.birth_longitude,
        request.birth_timezone,
        label="birth",
    )

    # Determine evaluation datetime in CURRENT timezone
    try:
        current_tz = pytz.timezone(current_tz_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid current timezone '{current_tz_name}': {e}")

    now_local = datetime.now(current_tz)
    date_str = request.date or now_local.strftime("%Y-%m-%d")
    time_str = request.time or now_local.strftime("%H:%M:%S")
    dt_local = _parse_local_datetime(date_str, time_str, current_tz_name)

    # Transit time uses current location (lat/lon doesn't materially affect longitudes here, but keep consistent)
    transit_time = AstroTime(dt_local, current_lat, current_lon)

    # Natal time uses birth datetime + birth location
    birth_dt = _parse_local_datetime(request.birth_date, request.birth_time, birth_tz_name)
    natal_time = AstroTime(birth_dt, birth_lat, birth_lon)

    # Step 1: sunrise/sunset + vara lord
    # Hindu day (vara) changes at sunrise, not at midnight.
    sun_times = get_sun_times(date_local=dt_local, lat=current_lat, lon=current_lon, tz_name=current_tz_name)
    if dt_local < sun_times.sunrise:
        sun_times = get_sun_times(date_local=dt_local - timedelta(days=1), lat=current_lat, lon=current_lon, tz_name=current_tz_name)

    weekday_lords_at_sunrise = {
        0: "Moon",      # Monday
        1: "Mars",      # Tuesday
        2: "Mercury",   # Wednesday
        3: "Jupiter",   # Thursday
        4: "Venus",     # Friday
        5: "Saturn",    # Saturday
        6: "Sun",       # Sunday
    }
    vara_lord = weekday_lords_at_sunrise[sun_times.sunrise.weekday()]

    # Step 2: Tara Bala from baseline nakshatra to transit Moon nakshatra
    baseline_lookup = {n.lower(): i + 1 for i, n in enumerate(NAKSHATRAS)}
    baseline_key = request.baseline_nakshatra.strip().lower()
    baseline_nak_num = baseline_lookup.get(baseline_key)
    if baseline_nak_num is None:
        raise HTTPException(status_code=400, detail=f"Unknown baseline_nakshatra '{request.baseline_nakshatra}'")

    transit_moon_long = get_planet_longitude(Planet.Moon, transit_time)
    transit_moon_nak_name, transit_moon_nak_num, _, _ = get_nakshatra(transit_moon_long)

    tara_name, tara_num = get_tara_bala(baseline_nak_num, transit_moon_nak_num)
    tara_good = {2, 4, 6, 8, 9}
    tara_bad = {3, 5, 7}
    if tara_num in tara_good:
        safety = "Success"
    elif tara_num in tara_bad:
        safety = "Danger"
    else:
        safety = "Safe"

    # Step 3: Moon relative to natal Moon (Chandra gochara house)
    natal_moon_long = get_planet_longitude(Planet.Moon, natal_time)
    natal_moon_sign, natal_moon_sign_num = get_rasi(natal_moon_long)
    transit_moon_sign, transit_moon_sign_num = get_rasi(transit_moon_long)

    chandra_house = get_gochara_house(natal_moon_sign_num, transit_moon_sign_num)
    if chandra_house in {6, 8, 12}:
        mood_score = "Anxiety"
    elif chandra_house in {1, 5, 9, 11}:
        mood_score = "Flow"
    else:
        mood_score = "Neutral"

    # Step 4: BAV strength for transiting planets in their current signs
    bav = get_all_bhinnashtakavarga(natal_time)  # computed from natal positions
    transiting_planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]
    bav_strength = {}
    for p in transiting_planets:
        p_long = get_planet_longitude(p, transit_time)
        _, p_sign_num = get_rasi(p_long)
        points = bav[p.name][p_sign_num]
        if points >= 5:
            effectiveness = "High"
        elif points == 4:
            effectiveness = "Medium"
        else:
            effectiveness = "Low"
        bav_strength[p.name] = {
            "transit_sign": RASIS[p_sign_num - 1],
            "transit_sign_number": p_sign_num,
            "bav_points": points,
            "effectiveness": effectiveness,
        }

    # Step 5: Vedha check (as per provided rules table)
    vedha_planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
    current_planetary_positions = {}
    for p in vedha_planets:
        p_long = get_planet_longitude(p, transit_time)
        _, p_sign_num = get_rasi(p_long)
        current_planetary_positions[p.name] = p_sign_num

    vedha_by_planet = calculate_vedha_status(natal_moon_sign_num, current_planetary_positions)
    vedha = {
        "implemented": True,
        "basis": "From natal Moon sign",
        "by_planet": vedha_by_planet,
        "any_blocked": any(v.get("status") == "Blocked" for v in vedha_by_planet.values()),
    }

    return {
        "datetime": dt_local.isoformat(),
        "current_location": {
            "place": current_place_name,
            "latitude": current_lat,
            "longitude": current_lon,
            "timezone": current_tz_name,
        },
        "birth_location": {
            "place": birth_place_name,
            "latitude": birth_lat,
            "longitude": birth_lon,
            "timezone": birth_tz_name,
        },
        "steps": {
            "1_location_sync": {
                "sunrise": sun_times.sunrise.isoformat(),
                "sunset": sun_times.sunset.isoformat(),
                "vara_lord": vara_lord,
            },
            "2_tara_bala": {
                "baseline_nakshatra": {"name": NAKSHATRAS[baseline_nak_num - 1], "number": baseline_nak_num},
                "transit_moon_nakshatra": {"name": transit_moon_nak_name, "number": transit_moon_nak_num},
                "tara": {"name": tara_name, "number": tara_num},
                "safety_score": safety,
            },
            "3_gochar_moon": {
                "natal_moon": {"sign": natal_moon_sign, "sign_number": natal_moon_sign_num},
                "transit_moon": {"sign": transit_moon_sign, "sign_number": transit_moon_sign_num},
                "house_from_natal_moon": chandra_house,
                "mood_score": mood_score,
            },
            "4_bav_strength": bav_strength,
            "5_vedha_check": vedha,
        },
    }


@app.post("/api/v1/chart/panchang", tags=["Birth Chart"])
async def get_panchang_data(birth_data: BirthData):
    """
    Get Panchang (Hindu Calendar) data including Tithi, Yoga, Nakshatra.
    """
    # Get location
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{birth_data.birth_place}'")
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
    
    # Parse datetime
    dt = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    
    # Create AstroTime
    astro_time = AstroTime(dt, lat, lon)
    
    # Get Sun and Moon positions
    sun_long = get_planet_longitude(Planet.Sun, astro_time)
    moon_long = get_planet_longitude(Planet.Moon, astro_time)
    
    # Calculate Panchang elements
    tithi_name, tithi_num, tithi_percentage = get_tithi(sun_long, moon_long)
    yoga_details = get_nitya_yoga_details(sun_long, moon_long)
    moon_nakshatra, moon_nak_num, moon_nak_pct, moon_pada = get_nakshatra(moon_long)
    
    return {
        "date": birth_data.birth_date,
        "time": birth_data.birth_time,
        "place": birth_data.birth_place,
        "panchang": {
            "tithi": {
                "name": tithi_name,
                "number": tithi_num,
                "percentage_elapsed": round(tithi_percentage, 2)
            },
            "yoga": {
                "name": yoga_details['name'],
                "number": yoga_details['number'],
                "deity": yoga_details['deity'],
                "nature": yoga_details['nature'],
                "effect": yoga_details['effect'],
                "percentage_elapsed": round(yoga_details['percentage'], 2)
            },
            "nakshatra": {
                "name": moon_nakshatra,
                "number": moon_nak_num,
                "pada": moon_pada,
                "percentage_elapsed": round(moon_nak_pct, 2)
            }
        }
    }


@app.post("/api/v1/chart/dasa", tags=["Birth Chart"])
async def get_dasa_periods(birth_data: BirthData, current_date: Optional[str] = None):
    """
    Get Vimshottari Dasa (planetary periods) for birth chart.
    
    Returns current Maha Dasa (main period) and Bhukti (sub-period).
    """
    # Get location
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{birth_data.birth_place}'")
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
    
    # Parse birth datetime
    birth_dt = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    
    # Parse current date or use today
    if current_date:
        try:
            current_dt = datetime.strptime(current_date, "%Y-%m-%d")
        except:
            raise HTTPException(status_code=400, detail="Current date must be in YYYY-MM-DD format")
    else:
        current_dt = datetime.now()
    
    # Create AstroTime for birth
    astro_time = AstroTime(birth_dt, lat, lon)
    
    # Get Moon position
    moon_long = get_planet_longitude(Planet.Moon, astro_time)
    moon_nakshatra, moon_nak_num, moon_nak_pct, moon_pada = get_nakshatra(moon_long)
    
    # Calculate Dasa
    maha_dasa, bhukti = get_vimshottari_dasa(moon_nak_num, moon_nak_pct, birth_dt, current_dt)
    
    return {
        "birth_date": birth_data.birth_date,
        "current_date": current_dt.strftime("%Y-%m-%d"),
        "moon_nakshatra": moon_nakshatra,
        "moon_nakshatra_number": moon_nak_num,
        "current_dasa": {
            "maha_dasa": maha_dasa,
            "bhukti": bhukti
        }
    }


@app.post("/api/v1/chart/vargas", tags=["Birth Chart"])
async def get_divisional_charts(birth_data: BirthData, planet: str = "Moon"):
    """
    Get divisional charts (Vargas) for a specific planet.
    
    Includes D1 (Rasi), D9 (Navamsa), D10 (Dasamsa), and all 16 standard vargas.
    """
    # Get location
    if birth_data.latitude and birth_data.longitude:
        lat = birth_data.latitude
        lon = birth_data.longitude
        tz_name = birth_data.timezone or "UTC"
    else:
        location = get_location(birth_data.birth_place)
        if not location:
            raise HTTPException(status_code=400, detail=f"Could not find location '{birth_data.birth_place}'")
        lat = location['latitude']
        lon = location['longitude']
        tz_name = birth_data.timezone or location['timezone']
    
    # Parse datetime
    dt = _parse_local_datetime(birth_data.birth_date, birth_data.birth_time, tz_name)
    
    # Create AstroTime
    astro_time = AstroTime(dt, lat, lon)
    
    # Get planet longitude
    try:
        planet_enum = Planet[planet]
        longitude = get_planet_longitude(planet_enum, astro_time)
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Invalid planet: {planet}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating planet position: {str(e)}")
    
    # Get all vargas
    vargas = get_all_vargas(longitude)
    
    return {
        "planet": planet,
        "longitude": round(longitude, 4),
        "vargas": vargas
    }


# =============================================================================
# Numerology Endpoints
# =============================================================================

@app.post("/api/v1/numerology/full", tags=["Numerology"])
async def get_numerology_reading(name: str, birth_date: str):
    """
    Get complete numerology reading including birth number, destiny number, and name analysis.
    
    Birth date format: YYYY-MM-DD
    """
    try:
        dt = datetime.strptime(birth_date, "%Y-%m-%d")
    except:
        raise HTTPException(status_code=400, detail="Birth date must be in YYYY-MM-DD format")
    
    try:
        result = get_full_numerology(name, dt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating numerology: {str(e)}")


@app.post("/api/v1/numerology/name", tags=["Numerology"])
async def get_name_analysis(name: str):
    """
    Get numerology analysis for a name only.
    """
    try:
        result = get_name_number_prediction(name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing name: {str(e)}")


# =============================================================================
# Reference Data - Nakshatras
# =============================================================================

@app.get("/api/v1/nakshatras", tags=["Reference Data"])
async def get_all_nakshatras():
    """
    Get list of all 27 Nakshatras.
    """
    return {"nakshatras": NAKSHATRAS}


@app.post("/api/v1/nakshatra/tara-bala", tags=["Reference Data"])
async def calculate_tara_bala(birth_nakshatra: int, transit_nakshatra: int):
    """
    Calculate Tara Bala (compatibility) between two nakshatras.
    
    Args:
        birth_nakshatra: Birth nakshatra number (1-27)
        transit_nakshatra: Transit nakshatra number (1-27)
    """
    tara, num = get_tara_bala(birth_nakshatra, transit_nakshatra)
    return {"tara": tara, "tara_number": num}


@app.post("/api/v1/prediction/daily", response_model=DailyPredictionResponse, tags=["Daily Prediction"])
async def get_daily_prediction_endpoint(request: DailyPredictionRequest):
    """
    Get daily prediction based on transit Moon position.
    
    **Cache-First Strategy:**
    - First request of the day: Calculate and store in Firestore
    - Subsequent requests: Retrieve from cache (same day)
    - Next day: Fresh calculation
    
    **Calculates:**
    1. **Mood** (Lagna Gochara) - House position from Lagna
    2. **Fuel** (Chandra Gochara) - Energy level from Birth Moon
    3. **Luck** (Tarabala) - Favorable/unfavorable status
    """
    # Determine prediction date
    prediction_date = request.prediction_date or datetime.now().strftime("%Y-%m-%d")
    
    # Check cache first
    cached_prediction = get_daily_prediction(request.user_id, prediction_date)
    
    if cached_prediction:
        # Return cached result
        return DailyPredictionResponse(
            cached=True,
            **{k: v for k, v in cached_prediction.items() if k not in ['id', 'user_id', 'created_at', 'type']}
        )
    
    # Cache miss - calculate fresh prediction
    
    # Get location coordinates
    if request.latitude and request.longitude:
        lat = request.latitude
        lon = request.longitude
        tz_name = request.timezone or "UTC"
    else:
        location = get_location(request.birth_place)
        if not location:
            raise HTTPException(
                status_code=400,
                detail=f"Could not find location '{request.birth_place}'"
            )
        lat = location['latitude']
        lon = location['longitude']
        tz_name = request.timezone or location['timezone']
    
    # Parse birth datetime
    birth_dt = _parse_local_datetime(request.birth_date, request.birth_time, tz_name)
    
    # Get birth chart data
    birth_time = AstroTime(dt=birth_dt, lat=lat, lon=lon)
    
    # Calculate birth Moon longitude
    birth_moon_long = get_planet_longitude(Planet.Moon, birth_time)
    
    # Get birth nakshatra number
    try:
        birth_nak_name, birth_nak_num, _, _ = get_nakshatra(birth_moon_long)
        # Try to match user-provided nakshatra with calculated or list
        if request.birth_nakshatra.lower() not in birth_nak_name.lower():
            # User provided different nakshatra, find its number from list
            found = False
            for i, nak in enumerate(NAKSHATRAS):
                if request.birth_nakshatra.lower() in nak.lower():
                    birth_nak_num = i + 1
                    found = True
                    break
            if not found:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid nakshatra: {request.birth_nakshatra}. Valid options: {', '.join(NAKSHATRAS)}"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nakshatra calculation error: {str(e)}")
    
    # Get Lagna number from sign name
    try:
        lagna_num = None
        for i, rasi in enumerate(RASIS):
            if request.lagna_sign.lower() in rasi.lower():
                lagna_num = i + 1
                break
        if lagna_num is None:
            raise ValueError(f"Invalid lagna sign: {request.lagna_sign}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Calculate daily prediction
    try:
        prediction = calculate_daily_prediction(
            birth_datetime=birth_dt,
            birth_lat=lat,
            birth_lon=lon,
            birth_lagna_num=lagna_num,
            birth_nakshatra_num=birth_nak_num,
            birth_moon_longitude=birth_moon_long,
            prediction_date=prediction_date,
            timezone=tz_name
        )
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"Calculation error:\n{tb}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
    
    # Save to cache
    try:
        save_daily_prediction(prediction, request.user_id, prediction_date)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Could not cache prediction: {e}")
    
    return DailyPredictionResponse(cached=False, **prediction)


@app.get("/api/v1/prediction/daily/{user_id}/{date}", tags=["Daily Prediction"])
async def get_cached_daily_prediction(user_id: str, date: str):
    """
    Retrieve a cached daily prediction by user ID and date.
    
    Args:
        user_id: User ID
        date: Date in YYYY-MM-DD format
    """
    prediction = get_daily_prediction(user_id, date)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found for this date")
    return prediction


# =============================================================================
# Planet Relationships, Aspects, Dignity, House Queries, Muhurtha Extensions
# =============================================================================

from logic.planet_relations import (
    get_natural_relationship,
    get_combined_relationship,
    get_all_planet_relationships,
)
from logic.aspects import (
    get_signs_planet_is_aspecting,
    is_planet_aspecting_planet,
    get_planets_aspecting_planet,
    get_full_aspect_grid,
)
from logic.dignity import get_planet_dignity, get_all_planet_dignities
from logic.house_queries import (
    get_planet_house,
    get_all_planet_houses,
    get_house_occupancy_map,
)
from logic.muhurtha import (
    get_chandrabala,
    get_panchaka,
    get_ghataka_chakra,
)
from logic.nakshatra import get_nakshatra
from logic.panchang import get_tithi


# ---- Helper: build AstroTime from query params ----
def _make_astro_time(dt_str: str, lat: float, lon: float) -> AstroTime:
    """Parse ISO datetime string (UTC) into AstroTime."""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid datetime format: {dt_str}. Use ISO 8601 (e.g. 1988-06-07T20:40:00+05:30)")
    return AstroTime(dt, lat, lon)


# ------------------------------------------------------------------
# 1. Planet-to-Planet Relationships  GET /api/v1/relationships
# ------------------------------------------------------------------
@app.get("/api/v1/relationships", tags=["Planet Relationships"])
async def get_planet_relationships(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the full 9×9 combined (natural + temporary) planet relationship grid.

    - **dt**: ISO 8601 datetime string (e.g. `1988-06-07T20:40:00+05:30`)
    - **lat**: Geographic latitude
    - **lon**: Geographic longitude
    """
    time = _make_astro_time(dt, lat, lon)
    return {"relationships": get_all_planet_relationships(time)}


# ------------------------------------------------------------------
# 2. Graha Drishti (Aspects)  GET /api/v1/aspects
# ------------------------------------------------------------------
@app.get("/api/v1/aspects", tags=["Planet Aspects"])
async def get_aspect_grid(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the full Graha Drishti (planetary aspect) grid.
    Each cell [transmitter][receiver] is `true` if the transmitter aspects the receiver.

    Special aspects: Saturn→3rd,10th; Jupiter→5th,9th; Mars→4th,8th; all planets→7th.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    return {"aspects": get_full_aspect_grid(time)}


@app.get("/api/v1/aspects/planet/{planet_name}", tags=["Planet Aspects"])
async def get_aspects_for_planet(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns which planets are aspected by the given planet, and which planets aspect it.

    - **planet_name**: e.g. `Sun`, `Moon`, `Mars`, `Jupiter`, `Saturn`, `Mercury`, `Venus`, `Rahu`, `Ketu`
    """
    try:
        planet = Planet[planet_name]
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown planet: {planet_name}")
    time = _make_astro_time(dt, lat, lon)
    aspecting = get_signs_planet_is_aspecting(planet, time)  # sign nums
    aspected_by = [p.name for p in get_planets_aspecting_planet(planet, time)]
    return {
        "planet": planet_name,
        "aspects_signs": aspecting,
        "aspected_by_planets": aspected_by,
    }


# ------------------------------------------------------------------
# 3. Planetary Dignity  GET /api/v1/dignity
# ------------------------------------------------------------------
@app.get("/api/v1/dignity", tags=["Planet Dignity"])
async def get_dignity_all(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the dignity of all 9 planets at the given time.

    Dignity levels (strongest → weakest):
    `ExaltedDegree`, `Exalted`, `OwnSign`, `Moolatrikona`, `Neutral`, `Debilitated`, `DebilitatedDegree`

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    return {"dignities": get_all_planet_dignities(time)}


@app.get("/api/v1/dignity/{planet_name}", tags=["Planet Dignity"])
async def get_dignity_single(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """Returns the dignity of a single planet."""
    try:
        planet = Planet[planet_name]
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown planet: {planet_name}")
    time = _make_astro_time(dt, lat, lon)
    return {"planet": planet_name, "dignity": get_planet_dignity(planet, time)}


# ------------------------------------------------------------------
# 4. House Queries  GET /api/v1/houses
# ------------------------------------------------------------------
@app.get("/api/v1/houses", tags=["House Queries"])
async def get_all_houses(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns which whole-sign house each planet occupies, plus a full
    house→planet occupancy map.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    return {
        "planet_houses": get_all_planet_houses(time),
        "house_occupancy": get_house_occupancy_map(time),
    }


@app.get("/api/v1/houses/planet/{planet_name}", tags=["House Queries"])
async def get_house_for_planet(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """Returns which house (1-12) the given planet occupies."""
    try:
        planet = Planet[planet_name]
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown planet: {planet_name}")
    time = _make_astro_time(dt, lat, lon)
    return {"planet": planet_name, "house": get_planet_house(planet, time)}


# ------------------------------------------------------------------
# 5. Chandrabala  GET /api/v1/muhurtha/chandrabala
# ------------------------------------------------------------------
@app.get("/api/v1/muhurtha/chandrabala", tags=["Muhurtha"])
async def api_chandrabala(
    birth_moon_sign: int,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Calculates Chandrabala — Moon's positional strength for selecting auspicious times.

    - **birth_moon_sign**: Janma Rasi sign number (1=Aries … 12=Pisces)
    - **dt**: ISO 8601 datetime string for the transit moment
    - **lat / lon**: Geographic coordinates for the transit moment
    """
    time = _make_astro_time(dt, lat, lon)
    transit_moon_long = get_planet_longitude(Planet.Moon, time)
    from logic.rasi import get_rasi as _get_rasi
    _, transit_moon_sign = _get_rasi(transit_moon_long)
    result = get_chandrabala(birth_moon_sign, transit_moon_sign)
    result["birth_moon_sign"] = birth_moon_sign
    result["transit_moon_sign"] = transit_moon_sign
    return result


# ------------------------------------------------------------------
# 6. Panchaka  GET /api/v1/muhurtha/panchaka
# ------------------------------------------------------------------
@app.get("/api/v1/muhurtha/panchaka", tags=["Muhurtha"])
async def api_panchaka(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Calculates Panchaka Dosha for the given moment.

    Returns the Panchaka type (`Shubha`, `Mrityu`, `Agni`, `Raja`, `Chora`, `Roga`)
    and whether a dosha is present.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates (used for Lagna calculation)
    """
    time = _make_astro_time(dt, lat, lon)
    sun_long  = get_planet_longitude(Planet.Sun,  time)
    moon_long = get_planet_longitude(Planet.Moon, time)
    from logic.rasi import get_rasi as _get_rasi
    from logic.calculate import get_lagnam as _get_lagnam
    _, lagna_sign_num = _get_rasi(_get_lagnam(time))
    tithi_name, tithi_num, _ = get_tithi(sun_long, moon_long)
    nak_name, nak_num, _, _ = get_nakshatra(moon_long)
    python_weekday = time.datetime.weekday()
    result = get_panchaka(tithi_num, nak_num, python_weekday, lagna_sign_num)
    result["tithi"] = tithi_name
    result["nakshatra"] = nak_name
    return result


# ------------------------------------------------------------------
# 7. Ghataka Chakra  GET /api/v1/muhurtha/ghataka
# ------------------------------------------------------------------
@app.get("/api/v1/muhurtha/ghataka", tags=["Muhurtha"])
async def api_ghataka(
    birth_moon_sign: int,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Determines whether the current moment is a Ghataka (inauspicious) period
    for a person born with the given Moon sign.

    Checks five factors from the Ghataka Chakra table:
    transit Moon sign, tithi group, weekday, Moon nakshatra, and Lagna sign.

    - **birth_moon_sign**: Janma Rasi sign number (1=Aries … 12=Pisces)
    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    sun_long  = get_planet_longitude(Planet.Sun,  time)
    moon_long = get_planet_longitude(Planet.Moon, time)
    from logic.rasi import get_rasi as _get_rasi
    from logic.calculate import get_lagnam as _get_lagnam
    _, transit_moon_sign = _get_rasi(moon_long)
    _, lagna_sign_num    = _get_rasi(_get_lagnam(time))
    _, tithi_num, _ = get_tithi(sun_long, moon_long)
    nak_name, _, _, _ = get_nakshatra(moon_long)
    python_weekday = time.datetime.weekday()
    return get_ghataka_chakra(
        birth_moon_sign,
        transit_moon_sign,
        tithi_num,
        python_weekday,
        nak_name,
        lagna_sign_num,
    )


# =============================================================================
# Shadbala, Yogas, Avastha Extensions
# =============================================================================

from logic.shadbala import get_shadbala_summary, get_shadbala_pinda, datetime_to_jd
from logic.yogas import get_all_yogas, get_occurring_yogas, yoga_summary
from logic.avastha import get_all_avasthas

# ------------------------------------------------------------------
# 8. Shadbala (all 7 planets)  GET /api/v1/shadbala
# ------------------------------------------------------------------
@app.get("/api/v1/shadbala", tags=["Shadbala"])
async def get_all_shadbala(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns Shadbala (six-fold strength) summary for all 7 classical planets.

    Includes Sthana, Dig, Kaala, Cheshta, Naisargika, and Drik bala.
    Each planet is evaluated against its required minimum Rupa thresholds.

    - **dt**: ISO 8601 datetime string (e.g. `1988-06-07T20:40:00+05:30`)
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    return get_shadbala_summary(time.datetime, lat, lon)


# ------------------------------------------------------------------
# 9. Shadbala (single planet)  GET /api/v1/shadbala/{planet_name}
# ------------------------------------------------------------------
@app.get("/api/v1/shadbala/{planet_name}", tags=["Shadbala"])
async def get_single_planet_shadbala(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns full Shadbala breakdown for a single planet.

    - **planet_name**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    valid = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    name = planet_name.capitalize()
    if name not in valid:
        raise HTTPException(status_code=422, detail=f"Planet must be one of: {valid}")
    time = _make_astro_time(dt, lat, lon)
    jd = datetime_to_jd(time.datetime)
    return get_shadbala_pinda(name, jd, lat, lon)


# ------------------------------------------------------------------
# 10. Yogas (all + occurring flag)  GET /api/v1/yogas
# ------------------------------------------------------------------
@app.get("/api/v1/yogas", tags=["Yogas"])
async def get_yogas(
    dt: str,
    lat: float,
    lon: float,
    only_occurring: bool = False,
):
    """
    Returns all 21 implemented Vedic yogas with their occurrence status.

    Includes Pancha Mahapurusha, GajaKesari, Raja, Dhana, and Viparita yogas.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    - **only_occurring**: If true, returns only currently active yogas
    """
    time = _make_astro_time(dt, lat, lon)
    yogas = get_occurring_yogas(time) if only_occurring else get_all_yogas(time)
    return [
        {
            "name": y.name,
            "nature": y.nature.value,
            "occurring": y.occurring,
            "description": y.description,
            "condition": y.condition,
            "strength": y.strength,
        }
        for y in yogas
    ]


# ------------------------------------------------------------------
# 11. Yoga Summary  GET /api/v1/yogas/summary
# ------------------------------------------------------------------
@app.get("/api/v1/yogas/summary", tags=["Yogas"])
async def get_yoga_summary(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns a concise count-based summary of all yogas.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    return yoga_summary(time)


# ------------------------------------------------------------------
# 12. Avastha (all planets)  GET /api/v1/avastha
# ------------------------------------------------------------------
@app.get("/api/v1/avastha", tags=["Avastha"])
async def get_all_planet_avastha(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns all five avastha (planetary state) categories for every planet.

    Avastha types: Bala (age), Jagradadi (alertness), Deeptadi (brightness),
    Lajjitadi (dignity), and Shayanadi (posture).

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    time = _make_astro_time(dt, lat, lon)
    from logic.calculate import get_planet_longitude as _gpl
    from logic.consts import Planet
    from logic.house_queries import get_planet_house as _gph, get_planets_in_sign as _gpis, get_planet_sign_num as _gpsn

    all_planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
    sun_long = _gpl(Planet.Sun, time)

    result = {}
    for p in all_planets:
        long = _gpl(p, time)
        house = _gph(p, time)
        sign_num = _gpsn(p, time)
        conjuncts = [other.name for other in all_planets
                     if other != p and _gpsn(other, time) == sign_num]
        result[p.name] = get_all_avasthas(p.name, long, sun_long, house, conjuncts)
    return result


# ------------------------------------------------------------------
# 13. Avastha (single planet)  GET /api/v1/avastha/{planet_name}
# ------------------------------------------------------------------
@app.get("/api/v1/avastha/{planet_name}", tags=["Avastha"])
async def get_single_planet_avastha(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns all avastha states for a single planet.

    - **planet_name**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.calculate import get_planet_longitude as _gpl
    from logic.consts import Planet
    from logic.house_queries import get_planet_house as _gph, get_planet_sign_num as _gpsn

    name_map = {p.name.lower(): p for p in Planet}
    p = name_map.get(planet_name.lower())
    if p is None:
        raise HTTPException(status_code=422, detail=f"Unknown planet: {planet_name}")

    time = _make_astro_time(dt, lat, lon)
    all_planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]
    sun_long = _gpl(Planet.Sun, time)
    long = _gpl(p, time)
    house = _gph(p, time)
    sign_num = _gpsn(p, time)
    conjuncts = [other.name for other in all_planets
                 if other != p and _gpsn(other, time) == sign_num]
    return get_all_avasthas(p.name, long, sun_long, house, conjuncts)


# =============================================================================
# Jaimini Astrology
# =============================================================================

@app.get("/api/v1/jaimini/karakas", tags=["Jaimini"])
def jaimini_karakas(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns Chara Karakas (temporal significators) for the birth chart.

    Ranks the 7 classical planets by longitude degree within sign to assign
    Atmakaraka, Amatyakaraka, Bhratrukaraka, Matrukaraka, Putrakaraka,
    Gnatikaraka, and Darakaraka.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.jaimini import get_chara_karakas

    time = _make_astro_time(dt, lat, lon)
    planet_longs = {
        p.name: get_planet_longitude(p, time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    return {"karakas": get_chara_karakas(planet_longs)}


@app.get("/api/v1/jaimini/chara-dasa", tags=["Jaimini"])
def jaimini_chara_dasa(
    dt: str,
    lat: float,
    lon: float,
    current_dt: Optional[str] = None,
):
    """
    Returns Chara Dasa (sign-based) timeline and current sub-period.

    - **dt**: Birth datetime (ISO 8601)
    - **lat / lon**: Birth coordinates
    - **current_dt**: Reference datetime for current dasa (defaults to now)
    """
    from logic.jaimini import get_chara_dasa, get_chara_dasa_antardasa
    from logic.shadbala import datetime_to_jd
    from datetime import timezone

    time = _make_astro_time(dt, lat, lon)
    planet_longs = {
        p.name: get_planet_longitude(p, time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    lagna_long = get_lagnam(time)
    birth_jd = datetime_to_jd(time.datetime)

    if current_dt:
        cur_time = _make_astro_time(current_dt, lat, lon)
        current_jd = datetime_to_jd(cur_time.datetime)
    else:
        current_jd = datetime_to_jd(datetime.now(timezone.utc))

    dasa = get_chara_dasa(lagna_long, planet_longs, birth_jd, current_jd)

    # Compute antardasa for the current dasa period
    cd = dasa["current_dasa"]
    lagna_sign = dasa["lagna_sign"]
    antardasa = get_chara_dasa_antardasa(
        cd["sign"], lagna_sign, planet_longs,
        cd["years"], dasa["years_into_dasa"]
    )

    return {
        "lagna_sign": dasa["lagna_sign"],
        "lagna_name": dasa["lagna_name"],
        "years_elapsed": dasa["years_elapsed"],
        "years_into_dasa": dasa["years_into_dasa"],
        "years_remaining": dasa["years_remaining"],
        "current_dasa": dasa["current_dasa"],
        "current_antardasa": antardasa,
        "dasa_periods": dasa["dasa_periods"],
    }


@app.get("/api/v1/jaimini/arudhas", tags=["Jaimini"])
def jaimini_arudhas(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns all 12 Arudha Padas (A1–A12) for the birth chart.

    Arudha Lagna (A1) represents the perceived self; each Arudha reflects
    the public image of that house's significations.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.jaimini import get_all_arudhas

    time = _make_astro_time(dt, lat, lon)
    planet_longs = {
        p.name: get_planet_longitude(p, time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    lagna_long = get_lagnam(time)
    lagna_sign = int(lagna_long / 30)
    return {"arudhas": get_all_arudhas(lagna_sign, planet_longs)}


# =============================================================================
# Varshaphal (Solar Return / Annual Horoscope)
# =============================================================================

@app.get("/api/v1/varshaphal", tags=["Varshaphal"])
def varshaphal(
    dt: str,
    lat: float,
    lon: float,
    year: Optional[int] = None,
):
    """
    Returns the Varshaphal (annual horoscope / solar return) for a given year.

    Computes the solar return chart for the requested year and derives the
    Muntha, Year Lord, and key Sahams.

    - **dt**: Birth datetime (ISO 8601)
    - **lat / lon**: Birth coordinates
    - **year**: Target Varsha year (defaults to current year)
    """
    from logic.varshaphal import get_varshaphal
    from logic.shadbala import datetime_to_jd
    from datetime import timezone

    birth_time = _make_astro_time(dt, lat, lon)
    birth_dt = birth_time.datetime
    birth_jd = datetime_to_jd(birth_dt)
    natal_sun_long = get_planet_longitude(Planet.Sun, birth_time)
    natal_planet_longs = {
        p.name: get_planet_longitude(p, birth_time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    birth_lagna_long = get_lagnam(birth_time)

    target_year = year if year is not None else datetime.now(timezone.utc).year

    # Compute solar return JD (avoids the buggy get_solar_return_jd stub)
    solar_return_jd = birth_jd + (target_year - birth_dt.year) * 365.2422
    solar_return_dt = datetime.fromtimestamp(
        (solar_return_jd - 2440587.5) * 86400, tz=timezone.utc
    )

    varsha_time = AstroTime(solar_return_dt, lat, lon)
    varsha_lagna_long = get_lagnam(varsha_time)
    varsha_planet_longs = {
        p.name: get_planet_longitude(p, varsha_time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    # Weekday: Python weekday() returns 0=Monday; Varshaphal uses 0=Sunday
    varsha_weekday = (solar_return_dt.weekday() + 1) % 7

    result = get_varshaphal(
        birth_dt, birth_lagna_long, natal_sun_long,
        natal_planet_longs, target_year,
        varsha_lagna_long, varsha_planet_longs, varsha_weekday,
    )
    return result


# =============================================================================
# Lordship (House Lords)
# =============================================================================

@app.get("/api/v1/lordship", tags=["Lordship"])
def lordship_all(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the ruling planet and sign for each of the 12 houses.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.lordship import get_all_house_lords, get_house_sign, SIGN_NAMES as _SIGN_NAMES

    time = _make_astro_time(dt, lat, lon)
    lords = get_all_house_lords(time)
    result = {}
    for house_num, planet in lords.items():
        sign_idx = get_house_sign(house_num, time)
        result[str(house_num)] = {
            "lord": planet.name,
            "sign_index": sign_idx,
            "sign": _SIGN_NAMES[sign_idx],
        }
    return {"houses": result}


@app.get("/api/v1/lordship/{planet_name}", tags=["Lordship"])
def lordship_by_planet(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the houses ruled by a given planet.

    - **planet_name**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn
    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.lordship import get_houses_ruled_by_planet

    name_map = {p.name.lower(): p for p in Planet}
    p = name_map.get(planet_name.lower())
    if p is None:
        raise HTTPException(status_code=422, detail=f"Unknown planet: {planet_name}")

    time = _make_astro_time(dt, lat, lon)
    houses = get_houses_ruled_by_planet(p, time)
    return {"planet": p.name, "houses_ruled": houses}


# =============================================================================
# Kakshya (Sub-lord Divisions)
# =============================================================================

@app.get("/api/v1/kakshya", tags=["Kakshya"])
def kakshya_all(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns Kakshya (sub-lord) division for all 9 planets.

    Each sign is split into 8 sub-divisions of 3°45' with fixed lords:
    Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.
    Used in KP-style transit fine-tuning.

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.kakshya import get_all_planets_kakshya

    time = _make_astro_time(dt, lat, lon)
    planet_longs = {
        p.name: get_planet_longitude(p, time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn,
                  Planet.Rahu, Planet.Ketu]
    }
    return {"kakshya": get_all_planets_kakshya(planet_longs)}


# =============================================================================
# Pancha Pakshi (Five Bird System)
# =============================================================================

@app.get("/api/v1/pancha-pakshi", tags=["Pancha Pakshi"])
def pancha_pakshi_analysis(
    dt: str,
    lat: float,
    lon: float,
    query_dt: Optional[str] = None,
):
    """
    Returns Pancha Pakshi (Five Bird System) analysis.

    Birth bird is derived from the birth Moon nakshatra and tithi.
    The analysis shows your bird's activity at the query time and
    lists all favorable periods for that day.

    - **dt**: Birth datetime (ISO 8601)
    - **lat / lon**: Birth coordinates
    - **query_dt**: Moment to analyse (ISO 8601, defaults to now)
    """
    from logic.pancha_pakshi import get_pancha_pakshi, get_favorable_periods, Activity
    from datetime import timezone

    birth_time = _make_astro_time(dt, lat, lon)
    moon_long = get_planet_longitude(Planet.Moon, birth_time)
    sun_long  = get_planet_longitude(Planet.Sun,  birth_time)
    _, birth_nak_num, _, _ = get_nakshatra(moon_long)   # 1-27
    _, birth_tithi_num, _  = get_tithi(sun_long, moon_long)  # 1-30

    if query_dt:
        qtime = _make_astro_time(query_dt, lat, lon)
        query_datetime = qtime.datetime
    else:
        query_datetime = datetime.now(timezone.utc)

    result = get_pancha_pakshi(birth_nak_num, birth_tithi_num, query_datetime)

    # Serialize enums to JSON-safe values
    result["birth_bird"]["bird"] = int(result["birth_bird"]["bird"])
    result["current_activity"]["activity"] = int(result["current_activity"]["activity"])
    if result["ruling_bird"]["bird"] is not None:
        result["ruling_bird"]["bird"] = int(result["ruling_bird"]["bird"])
    result["query_time"]["datetime"] = query_datetime.isoformat()

    result["favorable_periods"] = get_favorable_periods(
        birth_nak_num, birth_tithi_num, query_datetime, Activity.EATING
    )
    return result


# =============================================================================
# Wealth Yogas (Chatussagara, Vasumathi, Parvata)
# =============================================================================

@app.get("/api/v1/yogas/wealth", tags=["Yogas"])
def wealth_yogas(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Returns the three classical wealth / success yogas.

    - **Chatussagara** — all four kendras occupied (four oceans of plenty)
    - **Vasumathi** — benefics in upachaya houses (steady wealth growth)
    - **Parvata** — benefics in kendras + lagna/7th lord dignified (towering success)

    - **dt**: ISO 8601 datetime string
    - **lat / lon**: Geographic coordinates
    """
    from logic.wealth_yogas_temp import (
        check_chatussagara_yoga, check_vasumathi_yoga, check_parvata_yoga
    )

    time = _make_astro_time(dt, lat, lon)
    results = []
    for fn in [check_chatussagara_yoga, check_vasumathi_yoga, check_parvata_yoga]:
        y = fn(time)
        results.append({
            "name": y.name,
            "occurring": y.occurring,
            "strength": y.strength,
            "description": y.description,
            "condition": y.condition,
            "nature": y.nature.value,
        })
    return {"wealth_yogas": results}


# =============================================================================
# Ashtakavarga Endpoints
# =============================================================================

@app.get("/api/v1/ashtakavarga", tags=["Ashtakavarga"])
async def get_ashtakavarga_chart(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Ashtakavarga analysis for a birth chart.

    Returns Sarvashtakavarga (total benefic points per sign, sum of all planets)
    and Bhinnashtakavarga (individual breakdown for each of the 7 classical planets).
    """
    from logic.ashtakavarga import get_sarvashtakavarga_points, get_all_bhinnashtakavarga
    sign_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    time = _make_astro_time(dt, lat, lon)
    sarva = get_sarvashtakavarga_points(time)
    bhinna = get_all_bhinnashtakavarga(time)
    return {
        "sarvashtakavarga": {sign_names[k - 1]: v for k, v in sarva.items()},
        "bhinnashtakavarga": {
            planet: {sign_names[k - 1]: v for k, v in pts.items()}
            for planet, pts in bhinna.items()
        },
    }


@app.get("/api/v1/ashtakavarga/{planet_name}", tags=["Ashtakavarga"])
async def get_planet_ashtakavarga(
    planet_name: str,
    dt: str,
    lat: float,
    lon: float,
):
    """
    Bhinnashtakavarga for a single planet with per-source-planet breakdown.

    Valid planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
    """
    from logic.ashtakavarga import get_bhinnashtakavarga, get_bhinnashtakavarga_with_sources
    valid = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    if planet_name not in valid:
        raise HTTPException(status_code=400, detail=f"Planet must be one of: {', '.join(valid)}")
    sign_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                  'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    time = _make_astro_time(dt, lat, lon)
    points = get_bhinnashtakavarga(planet_name, time)
    detailed = get_bhinnashtakavarga_with_sources(planet_name, time)
    return {
        "planet": planet_name,
        "bhinnashtakavarga": {sign_names[k - 1]: v for k, v in points.items()},
        "by_source": {sign_names[k - 1]: v for k, v in detailed.items()},
    }


# =============================================================================
# Functional Nature Endpoint
# =============================================================================

@app.get("/api/v1/functional-nature", tags=["Functional Nature"])
async def get_functional_nature_endpoint(
    dt: str,
    lat: float,
    lon: float,
):
    """
    Functional benefic/malefic nature of all planets for this chart's ascendant.

    Returns per-planet classification (Yogakaraka, Functional Benefic, Functional Malefic,
    Mixed, Neutral) and categorized lists for use in prediction algorithms.
    """
    from logic.functional_nature import (
        get_functional_nature, get_functional_nature_categorized, get_ascendant_name
    )
    from logic.calculate import get_lagnam
    time = _make_astro_time(dt, lat, lon)
    lagna_long = get_lagnam(time)
    lagna_num = int(lagna_long // 30) + 1
    return {
        "ascendant": get_ascendant_name(lagna_num),
        "ascendant_number": lagna_num,
        "planets": get_functional_nature(lagna_num),
        "categorized": get_functional_nature_categorized(lagna_num),
    }


# =============================================================================
# Vedha (Transit Obstruction) Endpoint
# =============================================================================

@app.get("/api/v1/vedha", tags=["Vedha"])
async def get_vedha_status(
    birth_dt: str,
    birth_lat: float,
    birth_lon: float,
    transit_dt: Optional[str] = None,
    transit_lat: Optional[float] = None,
    transit_lon: Optional[float] = None,
):
    """
    Gochara Vedha (transit obstruction) analysis.

    Checks all 9 planets in transit against the natal Moon sign to determine
    which are in favorable houses and whether any Vedha (obstruction) applies.
    Returns a per-planet status: Favorable, Blocked, Favorable (Exempt), or Unfavorable.
    """
    from logic.vedha import calculate_vedha_status
    from logic.calculate import get_planet_longitude, get_lagnam
    from logic.rasi import get_rasi
    from logic.consts import Planet

    birth_time = _make_astro_time(birth_dt, birth_lat, birth_lon)
    moon_long = get_planet_longitude(Planet.Moon, birth_time)
    _, natal_moon_sign = get_rasi(moon_long)

    t_lat = transit_lat if transit_lat is not None else birth_lat
    t_lon = transit_lon if transit_lon is not None else birth_lon
    if transit_dt:
        transit_time = _make_astro_time(transit_dt, t_lat, t_lon)
    else:
        from datetime import timezone as _tz
        transit_time = _make_astro_time(
            __import__('datetime').datetime.now(_tz.utc).isoformat(), t_lat, t_lon
        )

    transit_positions = {}
    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        long = get_planet_longitude(planet, transit_time)
        _, sign_num = get_rasi(long)
        transit_positions[planet.name] = sign_num

    result = calculate_vedha_status(natal_moon_sign, transit_positions)
    favorable = [p for p, v in result.items() if "Favorable" in v["status"]]
    blocked = [p for p, v in result.items() if v["status"] == "Blocked"]
    unfavorable = [p for p, v in result.items() if v["status"] == "Unfavorable"]
    return {
        "natal_moon_sign": natal_moon_sign,
        "summary": {"favorable": favorable, "blocked": blocked, "unfavorable": unfavorable},
        "planets": result,
    }


# =============================================================================
# MCP Server (mounted at /mcp)
# POST /mcp/  →  streamable-http (stateless, Cloud Run safe)
# Compatible with Claude Desktop, VS Code, and any MCP client
# =============================================================================

import sys as _sys
import os as _os
import contextlib as _contextlib
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from mcp_server import mcp as _mcp

_mcp_http_app = _mcp.http_app(transport="streamable-http", path="/", stateless_http=True)

# Compose MCP lifespan with any existing app lifespan
_original_lifespan = app.router.lifespan_context

@_contextlib.asynccontextmanager
async def _combined_lifespan(application):
    async with _contextlib.AsyncExitStack() as _stack:
        if _original_lifespan is not None:
            await _stack.enter_async_context(_original_lifespan(application))
        await _stack.enter_async_context(_mcp_http_app.lifespan(_mcp_http_app))
        yield

app.router.lifespan_context = _combined_lifespan
app.mount("/mcp", _mcp_http_app)


# =============================================================================
# Run with: uvicorn api.main:app --reload
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
