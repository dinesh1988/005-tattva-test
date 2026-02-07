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
    - **Yogas**: 21+ yoga combinations including Raj, Dhana, and Pancha Mahapurusha yogas
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
    """Request for compatibility check."""
    profile1_id: str = Field(..., description="First profile ID")
    profile2_id: str = Field(..., description="Second profile ID")


class CompatibilityResponse(BaseModel):
    """Compatibility result."""
    compatibility_score: int
    element_match: str
    complementary_powers: bool
    combined_title: str
    synergy: str


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
            "yogas": 21,
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
        "yogas_implemented": 21,
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
    Check psychic compatibility between two profiles.
    
    Returns compatibility score and synergy analysis.
    """
    profile1 = await get_profile_by_id(request.profile1_id)
    profile2 = await get_profile_by_id(request.profile2_id)
    
    if not profile1 or not profile2:
        raise HTTPException(status_code=404, detail="One or both profiles not found")
    
    # Convert back to internal format for compatibility check
    # This is a simplified version - you'd reconstruct the full profile
    result = {
        'compatibility_score': 75,  # Placeholder - implement full logic
        'element_match': f"{profile1['channel']['element']} + {profile2['channel']['element']}",
        'complementary_powers': False,
        'combined_title': f"{profile1['title']} & {profile2['title']}",
        'synergy': 'High'
    }
    
    return CompatibilityResponse(**result)


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
        'weekday': birth_datetime.strftime('%A'),
        'weekday_planet': {'Monday': 'Moon', 'Tuesday': 'Mars', 'Wednesday': 'Mercury', 
                           'Thursday': 'Jupiter', 'Friday': 'Venus', 'Saturday': 'Saturn', 
                           'Sunday': 'Sun'}[birth_datetime.strftime('%A')]
    }
    
    # 4. DASA PERIODS with timing
    # Get current date for dasa calculation
    current_dt = datetime.now(birth_datetime_tz.tzinfo)
    # Use nakshatra values already calculated above
    maha_dasa_planet, bhukti_planet = get_vimshottari_dasa(nakshatra_num, nakshatra_pct, birth_datetime_tz, current_dt)
    
    # Calculate full 120-year Vimshottari Dasa schedule
    dasa_schedule = get_vimshottari_dasa_schedule(nakshatra_num, nakshatra_pct, birth_datetime_tz)
    
    current_year = datetime.now().year
    birth_year = birth_datetime.year
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
    numerology = get_full_numerology(birth_data.name, birth_datetime)
    
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
# Run with: uvicorn api.main:app --reload
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
