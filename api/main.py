"""
VedAstroPy API - Psychic Profile Service
=========================================
FastAPI service for generating and storing Psychic Profiles.

Run with: uvicorn api.main:app --reload --port 8000
"""

import sys
import os

# Load environment variables from .env file in VedAstroPy directory
from dotenv import load_dotenv
vedastro_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(vedastro_dir, '.env'))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
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
from logic.panchang import get_tithi, get_yoga, get_nitya_yoga_details
from logic.nakshatra import get_nakshatra, get_tara_bala, NAKSHATRAS
from logic.dasa import get_vimshottari_dasa, get_vimshottari_dasa_full
from logic.varga import get_all_vargas
from logic.numerology import get_full_numerology, get_name_number_prediction
from logic.daily_prediction import calculate_daily_prediction
from logic.rasi import RASIS

# Database imports
from api.database import (
    get_db, save_profile, get_profile_by_id, get_profiles_by_user,
    save_daily_prediction, get_daily_prediction
)

# =============================================================================
# FastAPI App Setup
# =============================================================================

app = FastAPI(
    title="VedAstroPy Psychic Profile API",
    description="""
    Generate unique Psychic Profiles based on Vedic Astrology formulas.
    
    ## The 3-Step Formula
    
    1. **Channel** (Moon Element) → How they receive psychic information
    2. **Superpower** (Nakshatra) → What specific ability they have  
    3. **Signal Strength** (Ketu House) → Intensity and activation conditions
    
    Creates 1,296 unique profile combinations (4 × 27 × 12)
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
            "service": "VedAstroPy API",
            "version": "0.6.0",
            "yogas": 21,
            "modules": 18
        }
    )

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API info."""
    return {
        "service": "VedAstroPy Psychic Profile API",
        "status": "running",
        "version": "0.6.0",
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
    import pytz
    
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
        tz = pytz.timezone(tz_name)
        date_parts = request.birth_date.split('-')
        time_parts = request.birth_time.split(':')
        birth_dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
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
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = birth_data.birth_date.split('-')
        time_parts = birth_data.birth_time.split(':')
        
        dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
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
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = birth_data.birth_date.split('-')
        time_parts = birth_data.birth_time.split(':')
        
        dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
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


@app.post("/api/v1/chart/panchang", tags=["Birth Chart"])
async def get_panchang_data(birth_data: BirthData):
    """
    Get Panchang (Hindu Calendar) data including Tithi, Yoga, Nakshatra.
    """
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = birth_data.birth_date.split('-')
        time_parts = birth_data.birth_time.split(':')
        
        dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
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
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = birth_data.birth_date.split('-')
        time_parts = birth_data.birth_time.split(':')
        
        birth_dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
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
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = birth_data.birth_date.split('-')
        time_parts = birth_data.birth_time.split(':')
        
        dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    
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
    import pytz
    
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
    try:
        tz = pytz.timezone(tz_name)
        date_parts = request.birth_date.split('-')
        time_parts = request.birth_time.split(':')
        
        birth_dt = datetime(
            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
            int(time_parts[0]), int(time_parts[1]), 0,
            tzinfo=tz
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time: {e}")
    
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
