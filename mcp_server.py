"""
Tattva MCP Server
=================
Exposes Vedic Astrology calculations as MCP tools via fastmcp.
Imports logic directly (no HTTP overhead) for maximum speed.

Run with:
    python -m mcp_server          (stdio transport, for Claude Desktop / VS Code)
    fastmcp run mcp_server.py     (convenience wrapper)
"""

import os
import sys
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

# Load .env from VedAstroPy directory
_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_dir, ".env"))

# Ensure local modules are importable
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from fastmcp import FastMCP

from logic.geolocation import get_location
from logic.calculate import get_planet_longitude, get_lagnam
from logic.time import AstroTime
from logic.consts import Planet
from logic.nakshatra import get_nakshatra, get_tara_bala, NAKSHATRAS
from logic.panchang import get_tithi, get_nitya_yoga_details, get_karana
from logic.rasi import RASIS, get_rasi, get_gochara_house
from logic.dasa import get_vimshottari_dasa
from logic.varga import get_all_vargas
from logic.numerology import get_full_numerology, get_name_number_prediction
from logic.psychic_profile import get_psychic_profile
from logic.ashtakavarga import get_all_bhinnashtakavarga
from logic.sunrise import get_sun_times
from logic.vedha import calculate_vedha_status
from logic.shadbala import get_shadbala_summary, get_shadbala_pinda, datetime_to_jd
from logic.yogas import get_all_yogas, yoga_summary
from logic.avastha import get_all_avasthas

import pytz

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="Tattva Vedic Astrology",
    instructions=(
        "Tools for Vedic astrology calculations: birth charts, psychic profiles, "
        "panchang, dasa periods, divisional charts, numerology, and 5-step daily workflow."
    ),
)

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_location(
    place: Optional[str],
    latitude: Optional[float],
    longitude: Optional[float],
    timezone: Optional[str],
) -> tuple[str, float, float, str]:
    """Return (place_name, lat, lon, tz_name). Raises ValueError on failure."""
    if latitude is not None and longitude is not None:
        return place or "(custom)", latitude, longitude, timezone or "UTC"
    if not place:
        raise ValueError("Provide either (latitude, longitude) or place name.")
    loc = get_location(place)
    if not loc:
        raise ValueError(f"Could not find location '{place}'.")
    return loc["name"], loc["latitude"], loc["longitude"], timezone or loc["timezone"]


def _parse_dt(date_str: str, time_str: str, tz_name: str) -> datetime:
    """Parse a localised datetime from date/time strings."""
    tz = pytz.timezone(tz_name)
    y, m, d = (int(x) for x in date_str.split("-"))
    parts = time_str.split(":")
    h, mn = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    return tz.localize(datetime(y, m, d, h, mn, s))


# ---------------------------------------------------------------------------
# Tool 1 – Location lookup
# ---------------------------------------------------------------------------

@mcp.tool()
def lookup_location(city: str) -> dict:
    """
    Look up geographic coordinates and timezone for a city name.

    Args:
        city: City name (e.g. "Chennai", "New York").

    Returns:
        dict with name, latitude, longitude, timezone, country.
    """
    loc = get_location(city)
    if not loc:
        return {"error": f"City '{city}' not found."}
    return {
        "name": loc["name"],
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "timezone": loc["timezone"],
        "country": loc.get("country"),
    }


# ---------------------------------------------------------------------------
# Tool 2 – Planetary positions (birth chart)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_planet_positions(
    birth_date: str,
    birth_time: str,
    birth_place: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[str] = None,
) -> dict:
    """
    Return all 9 graha positions plus Ascendant for a birth chart.

    Args:
        birth_date: Birth date as YYYY-MM-DD.
        birth_time: Birth time as HH:MM or HH:MM:SS (24-hour local time).
        birth_place: City name (used when lat/lon not provided).
        latitude: Latitude override.
        longitude: Longitude override.
        timezone: IANA timezone override (e.g. "Asia/Kolkata").

    Returns:
        Dict with ascendant and planets; each entry has longitude, sign,
        degree_in_sign, nakshatra, nakshatra_number, nakshatra_pada.
    """
    try:
        place, lat, lon, tz_name = _resolve_location(birth_place, latitude, longitude, timezone)
    except ValueError as e:
        return {"error": str(e)}

    dt = _parse_dt(birth_date, birth_time, tz_name)
    at = AstroTime(dt, lat, lon)

    result: dict = {"place": place, "birth_date": birth_date, "birth_time": birth_time, "planets": {}}

    for planet in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                   Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        try:
            lon_deg = get_planet_longitude(planet, at)
            nak_name, nak_num, nak_pct, pada = get_nakshatra(lon_deg)
            result["planets"][planet.name] = {
                "longitude": round(lon_deg, 4),
                "sign": SIGNS[int(lon_deg / 30)],
                "degree_in_sign": round(lon_deg % 30, 4),
                "nakshatra": nak_name,
                "nakshatra_number": nak_num,
                "nakshatra_pada": pada,
            }
        except Exception as exc:
            result["planets"][planet.name] = {"error": str(exc)}

    try:
        lagna = get_lagnam(at)
        nak_name, nak_num, nak_pct, pada = get_nakshatra(lagna)
        result["ascendant"] = {
            "longitude": round(lagna, 4),
            "sign": SIGNS[int(lagna / 30)],
            "degree_in_sign": round(lagna % 30, 4),
            "nakshatra": nak_name,
            "nakshatra_number": nak_num,
            "nakshatra_pada": pada,
        }
    except Exception as exc:
        result["ascendant"] = {"error": str(exc)}

    return result


# ---------------------------------------------------------------------------
# Tool 3 – Panchang
# ---------------------------------------------------------------------------

@mcp.tool()
def get_panchang(
    date: str,
    time: str,
    place: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[str] = None,
) -> dict:
    """
    Return Panchang for any date/time/location: Tithi, Nakshatra, Yoga, Karana.

    Args:
        date: Date as YYYY-MM-DD.
        time: Time as HH:MM or HH:MM:SS (24-hour local).
        place: City name.
        latitude: Latitude override.
        longitude: Longitude override.
        timezone: IANA timezone override.

    Returns:
        Dict with tithi, yoga, nakshatra, karana.
    """
    try:
        place_name, lat, lon, tz_name = _resolve_location(place, latitude, longitude, timezone)
    except ValueError as e:
        return {"error": str(e)}

    dt = _parse_dt(date, time, tz_name)
    at = AstroTime(dt, lat, lon)

    sun_long = get_planet_longitude(Planet.Sun, at)
    moon_long = get_planet_longitude(Planet.Moon, at)

    tithi_name, tithi_num, tithi_pct = get_tithi(sun_long, moon_long)
    yoga = get_nitya_yoga_details(sun_long, moon_long)
    nak_name, nak_num, nak_pct, pada = get_nakshatra(moon_long)
    karana = get_karana(sun_long, moon_long)

    return {
        "datetime": dt.isoformat(),
        "place": place_name,
        "tithi": {"name": tithi_name, "number": tithi_num, "percentage_elapsed": round(tithi_pct, 2)},
        "nakshatra": {"name": nak_name, "number": nak_num, "pada": pada, "percentage_elapsed": round(nak_pct, 2)},
        "yoga": {
            "name": yoga["name"],
            "number": yoga["number"],
            "deity": yoga["deity"],
            "nature": yoga["nature"],
            "effect": yoga["effect"],
        },
        "karana": karana,
    }


# ---------------------------------------------------------------------------
# Tool 4 – Vimshottari Dasa
# ---------------------------------------------------------------------------

@mcp.tool()
def get_dasa(
    birth_date: str,
    birth_time: str,
    birth_place: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[str] = None,
    current_date: Optional[str] = None,
) -> dict:
    """
    Return the current Vimshottari Maha Dasa and Bhukti (sub-period).

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        birth_place: City name.
        latitude: Latitude override.
        longitude: Longitude override.
        timezone: IANA timezone override.
        current_date: Date to evaluate (YYYY-MM-DD, defaults to today).

    Returns:
        Dict with moon_nakshatra, maha_dasa, bhukti.
    """
    try:
        place, lat, lon, tz_name = _resolve_location(birth_place, latitude, longitude, timezone)
    except ValueError as e:
        return {"error": str(e)}

    birth_dt = _parse_dt(birth_date, birth_time, tz_name)
    eval_dt = datetime.strptime(current_date, "%Y-%m-%d") if current_date else datetime.now()

    at = AstroTime(birth_dt, lat, lon)
    moon_long = get_planet_longitude(Planet.Moon, at)
    nak_name, nak_num, nak_pct, _ = get_nakshatra(moon_long)

    maha_dasa, bhukti = get_vimshottari_dasa(nak_num, nak_pct, birth_dt, eval_dt)

    return {
        "birth_date": birth_date,
        "current_date": eval_dt.strftime("%Y-%m-%d"),
        "moon_nakshatra": {"name": nak_name, "number": nak_num},
        "maha_dasa": maha_dasa,
        "bhukti": bhukti,
    }


# ---------------------------------------------------------------------------
# Tool 5 – Divisional charts (Vargas)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_vargas(
    birth_date: str,
    birth_time: str,
    planet: str = "Moon",
    birth_place: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[str] = None,
) -> dict:
    """
    Return divisional chart positions (D1–D60) for a planet.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        planet: Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu).
        birth_place: City name.
        latitude: Latitude override.
        longitude: Longitude override.
        timezone: IANA timezone override.

    Returns:
        Dict with planet, longitude, and all varga positions.
    """
    try:
        place, lat, lon, tz_name = _resolve_location(birth_place, latitude, longitude, timezone)
    except ValueError as e:
        return {"error": str(e)}

    dt = _parse_dt(birth_date, birth_time, tz_name)
    at = AstroTime(dt, lat, lon)

    try:
        planet_enum = Planet[planet]
    except KeyError:
        return {"error": f"Invalid planet '{planet}'. Choose from: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu"}

    lon_deg = get_planet_longitude(planet_enum, at)
    vargas = get_all_vargas(lon_deg)

    return {"planet": planet, "longitude": round(lon_deg, 4), "vargas": vargas}


# ---------------------------------------------------------------------------
# Tool 6 – Psychic profile
# ---------------------------------------------------------------------------

@mcp.tool()
def generate_psychic_profile(
    birth_date: str,
    birth_time: str,
    name: str,
    birth_place: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    timezone: Optional[str] = None,
) -> dict:
    """
    Generate a Psychic Profile: Psychic Channel (Moon sign element),
    Superpower (Nakshatra archetype), and Signal Strength (Ketu house).
    Produces 1 of 1,296 unique combinations.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        name: Person's name.
        birth_place: City name.
        latitude: Latitude override.
        longitude: Longitude override.
        timezone: IANA timezone override.

    Returns:
        Full psychic profile dict.
    """
    try:
        place, lat, lon, tz_name = _resolve_location(birth_place, latitude, longitude, timezone)
    except ValueError as e:
        return {"error": str(e)}

    dt = _parse_dt(birth_date, birth_time, tz_name)

    try:
        profile = get_psychic_profile(dt, lat, lon)
    except Exception as exc:
        return {"error": str(exc)}

    return {"name": name, **profile}


# ---------------------------------------------------------------------------
# Tool 7 – Numerology
# ---------------------------------------------------------------------------

@mcp.tool()
def get_numerology(name: str, birth_date: str) -> dict:
    """
    Return a full numerology reading (birth number, destiny number, name analysis).

    Args:
        name: Person's full name.
        birth_date: Birth date YYYY-MM-DD.

    Returns:
        Complete numerology report.
    """
    try:
        dt = datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "birth_date must be in YYYY-MM-DD format"}

    try:
        return get_full_numerology(name, dt)
    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
def analyze_name_numerology(name: str) -> dict:
    """
    Return numerology analysis for a name only (no birth date required).

    Args:
        name: Name to analyse.

    Returns:
        Name number and prediction.
    """
    try:
        return get_name_number_prediction(name)
    except Exception as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Tool 8 – Tara Bala
# ---------------------------------------------------------------------------

@mcp.tool()
def calculate_tara_bala(birth_nakshatra_number: int, transit_nakshatra_number: int) -> dict:
    """
    Calculate Tara Bala compatibility between two nakshatras.

    Args:
        birth_nakshatra_number: Birth nakshatra number (1–27).
        transit_nakshatra_number: Transit nakshatra number (1–27).

    Returns:
        tara name, tara number, and quality (good / challenging / neutral).
    """
    tara_name, tara_num = get_tara_bala(birth_nakshatra_number, transit_nakshatra_number)
    tara_good = {2, 4, 6, 8, 9}
    tara_bad = {3, 5, 7}
    quality = "good" if tara_num in tara_good else ("challenging" if tara_num in tara_bad else "neutral")
    return {"tara_name": tara_name, "tara_number": tara_num, "quality": quality}


# ---------------------------------------------------------------------------
# Tool 9 – Reference: nakshatras
# ---------------------------------------------------------------------------

@mcp.tool()
def list_nakshatras() -> dict:
    """Return the ordered list of all 27 nakshatras."""
    return {"nakshatras": list(NAKSHATRAS)}


# ---------------------------------------------------------------------------
# Tool 10 – 5-Step daily workflow
# ---------------------------------------------------------------------------

@mcp.tool()
def daily_five_step(
    birth_date: str,
    birth_time: str,
    current_place: Optional[str] = None,
    birth_place: Optional[str] = None,
    birth_latitude: Optional[float] = None,
    birth_longitude: Optional[float] = None,
    birth_timezone: Optional[str] = None,
    current_latitude: Optional[float] = None,
    current_longitude: Optional[float] = None,
    current_timezone: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    baseline_nakshatra: str = "Purva Bhadrapada",
) -> dict:
    """
    Run the 5-step Vedic daily workflow and return an integrated timing report.

    Step 1 – Vara Lord: sunrise at current location determines the day ruler.
    Step 2 – Tara Bala: safety score from baseline nakshatra vs transit Moon.
    Step 3 – Chandra Gochara: mood from transit Moon house relative to natal Moon.
    Step 4 – BAV Strength: effectiveness of each transiting planet in its sign.
    Step 5 – Vedha: obstruction check from natal Moon sign.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        current_place: Current city name.
        birth_place: Birth city name.
        birth_latitude: Birth latitude override.
        birth_longitude: Birth longitude override.
        birth_timezone: Birth IANA timezone override.
        current_latitude: Current latitude override.
        current_longitude: Current longitude override.
        current_timezone: Current IANA timezone override.
        date: Evaluation date YYYY-MM-DD (defaults to today).
        time: Evaluation time HH:MM[:SS] (defaults to now).
        baseline_nakshatra: Natal nakshatra for Step 2 (default Purva Bhadrapada).

    Returns:
        Dict with all 5 step results.
    """
    from datetime import timedelta

    try:
        _, cur_lat, cur_lon, cur_tz_name = _resolve_location(
            current_place, current_latitude, current_longitude, current_timezone
        )
        _, bth_lat, bth_lon, bth_tz_name = _resolve_location(
            birth_place, birth_latitude, birth_longitude, birth_timezone
        )
    except ValueError as e:
        return {"error": str(e)}

    cur_tz = pytz.timezone(cur_tz_name)
    now_local = datetime.now(cur_tz)
    eval_date = date or now_local.strftime("%Y-%m-%d")
    eval_time = time or now_local.strftime("%H:%M:%S")

    dt_local = _parse_dt(eval_date, eval_time, cur_tz_name)
    transit_time = AstroTime(dt_local, cur_lat, cur_lon)

    birth_dt = _parse_dt(birth_date, birth_time, bth_tz_name)
    natal_time = AstroTime(birth_dt, bth_lat, bth_lon)

    # Step 1 – Vara Lord
    sun_times = get_sun_times(date_local=dt_local, lat=cur_lat, lon=cur_lon, tz_name=cur_tz_name)
    if dt_local < sun_times.sunrise:
        sun_times = get_sun_times(
            date_local=dt_local - timedelta(days=1), lat=cur_lat, lon=cur_lon, tz_name=cur_tz_name
        )

    weekday_lords = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn", 6: "Sun"}
    vara_lord = weekday_lords[sun_times.sunrise.weekday()]

    # Step 2 – Tara Bala
    baseline_lookup = {n.lower(): i + 1 for i, n in enumerate(NAKSHATRAS)}
    baseline_num = baseline_lookup.get(baseline_nakshatra.strip().lower())
    if baseline_num is None:
        return {"error": f"Unknown baseline_nakshatra '{baseline_nakshatra}'"}

    transit_moon_long = get_planet_longitude(Planet.Moon, transit_time)
    t_moon_nak_name, t_moon_nak_num, _, _ = get_nakshatra(transit_moon_long)

    tara_name, tara_num = get_tara_bala(baseline_num, t_moon_nak_num)
    tara_good = {2, 4, 6, 8, 9}
    tara_bad = {3, 5, 7}
    safety = "Success" if tara_num in tara_good else ("Danger" if tara_num in tara_bad else "Safe")

    # Step 3 – Chandra Gochara
    natal_moon_long = get_planet_longitude(Planet.Moon, natal_time)
    natal_moon_sign, natal_moon_sign_num = get_rasi(natal_moon_long)
    transit_moon_sign, transit_moon_sign_num = get_rasi(transit_moon_long)
    chandra_house = get_gochara_house(natal_moon_sign_num, transit_moon_sign_num)
    if chandra_house in {6, 8, 12}:
        mood = "Anxiety"
    elif chandra_house in {1, 5, 9, 11}:
        mood = "Flow"
    else:
        mood = "Neutral"

    # Step 4 – BAV Strength
    bav = get_all_bhinnashtakavarga(natal_time)
    bav_strength: dict = {}
    for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury, Planet.Jupiter, Planet.Venus, Planet.Saturn]:
        p_long = get_planet_longitude(p, transit_time)
        _, p_sign_num = get_rasi(p_long)
        points = bav[p.name][p_sign_num]
        bav_strength[p.name] = {
            "transit_sign": RASIS[p_sign_num - 1],
            "bav_points": points,
            "effectiveness": "High" if points >= 5 else ("Medium" if points == 4 else "Low"),
        }

    # Step 5 – Vedha
    current_positions: dict = {}
    for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
              Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu]:
        p_long = get_planet_longitude(p, transit_time)
        _, p_sign_num = get_rasi(p_long)
        current_positions[p.name] = p_sign_num

    vedha_by_planet = calculate_vedha_status(natal_moon_sign_num, current_positions)

    return {
        "datetime": dt_local.isoformat(),
        "step_1_vara": {
            "vara_lord": vara_lord,
            "sunrise": sun_times.sunrise.isoformat(),
            "sunset": sun_times.sunset.isoformat(),
        },
        "step_2_tara_bala": {
            "baseline_nakshatra": NAKSHATRAS[baseline_num - 1],
            "transit_moon_nakshatra": t_moon_nak_name,
            "tara_name": tara_name,
            "tara_number": tara_num,
            "safety_score": safety,
        },
        "step_3_chandra_gochara": {
            "natal_moon_sign": natal_moon_sign,
            "transit_moon_sign": transit_moon_sign,
            "house_from_natal_moon": chandra_house,
            "mood_score": mood,
        },
        "step_4_bav_strength": bav_strength,
        "step_5_vedha": {
            "natal_moon_sign": natal_moon_sign,
            "by_planet": vedha_by_planet,
            "any_blocked": any(v.get("status") == "Blocked" for v in vedha_by_planet.values()),
        },
    }


# ---------------------------------------------------------------------------
# Tool 11 – Shadbala (six-fold planetary strength)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_shadbala(
    birth_date: str,
    birth_time: str,
    birth_place: Optional[str] = None,
    birth_latitude: Optional[float] = None,
    birth_longitude: Optional[float] = None,
    birth_timezone: Optional[str] = None,
    planet: Optional[str] = None,
) -> dict:
    """
    Calculate Shadbala (six-fold strength) for birth chart planets.

    When planet is omitted, returns a summary for all 7 classical planets with
    ranking, strongest/weakest planet, and total rupas per planet.
    When planet is specified, returns the full breakdown of all 6 balas
    (Sthana, Dig, Kaala, Cheshta, Naisargika, Drik) and whether the planet
    meets the classical minimum strength threshold.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        birth_place: Birth city name (used if lat/lon not given).
        birth_latitude: Birth latitude override.
        birth_longitude: Birth longitude override.
        birth_timezone: IANA timezone override.
        planet: Optional planet name (Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn).

    Returns:
        Shadbala summary for all planets, or detailed breakdown for one planet.
    """
    try:
        _, lat, lon, tz_name = _resolve_location(
            birth_place, birth_latitude, birth_longitude, birth_timezone
        )
    except ValueError as e:
        return {"error": str(e)}

    birth_dt = _parse_dt(birth_date, birth_time, tz_name)

    if planet:
        jd = datetime_to_jd(birth_dt)
        return get_shadbala_pinda(planet, jd, lat, lon)

    return get_shadbala_summary(birth_dt, lat, lon)


# ---------------------------------------------------------------------------
# Tool 12 – Birth yogas
# ---------------------------------------------------------------------------

@mcp.tool()
def get_birth_yogas(
    birth_date: str,
    birth_time: str,
    birth_place: Optional[str] = None,
    birth_latitude: Optional[float] = None,
    birth_longitude: Optional[float] = None,
    birth_timezone: Optional[str] = None,
    only_occurring: bool = False,
) -> dict:
    """
    Identify Vedic birth yogas (planetary combinations) in a horoscope.

    Checks 21 classical yogas including Pancha Mahapurusha (Hamsa, Malavya,
    Bhadra, Ruchaka, Sasha), GajaKesari, Viparita Raja yogas, wealth yogas
    (Lakshmi, Chatussagara, Vasumathi, Parvata), and lunar yogas.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        birth_place: Birth city name (used if lat/lon not given).
        birth_latitude: Birth latitude override.
        birth_longitude: Birth longitude override.
        birth_timezone: IANA timezone override.
        only_occurring: If True, return only yogas that are present (default False = all 21).

    Returns:
        summary dict + list of yogas with name, nature, occurring, description, condition.
    """
    try:
        _, lat, lon, tz_name = _resolve_location(
            birth_place, birth_latitude, birth_longitude, birth_timezone
        )
    except ValueError as e:
        return {"error": str(e)}

    birth_dt = _parse_dt(birth_date, birth_time, tz_name)
    time = AstroTime(birth_dt, lat, lon)

    summary = yoga_summary(time)
    all_yogas = get_all_yogas(time)
    yoga_list = [y for y in all_yogas if y.occurring] if only_occurring else all_yogas

    return {
        "summary": summary,
        "yogas": [
            {
                "name": y.name,
                "nature": y.nature.value,
                "occurring": y.occurring,
                "description": y.description,
                "condition": y.condition,
                "strength": y.strength,
            }
            for y in yoga_list
        ],
    }


# ---------------------------------------------------------------------------
# Tool 13 – Avastha (planetary states)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_planet_avastha(
    birth_date: str,
    birth_time: str,
    birth_place: Optional[str] = None,
    birth_latitude: Optional[float] = None,
    birth_longitude: Optional[float] = None,
    birth_timezone: Optional[str] = None,
    planet: Optional[str] = None,
) -> dict:
    """
    Calculate planetary Avastha (5 types of states) for a birth chart.

    Avastha reveals how a planet delivers its results:
    - Bala Avastha: age/maturity (Bala/Kumara/Yuva/Vriddha/Mrita)
    - Jagradadi Avastha: alertness level (Jagrat/Swapna/Sushupti)
    - Deeptadi Avastha: brightness based on solar proximity
    - Lajjitadi Avastha: dignity/conjunction state
    - Shayanadi Avastha: posture by nakshatra pada

    When planet is omitted, returns avastha for all 9 planets.
    When planet is specified, returns avastha for that planet only.

    Args:
        birth_date: Birth date YYYY-MM-DD.
        birth_time: Birth time HH:MM[:SS].
        birth_place: Birth city name (used if lat/lon not given).
        birth_latitude: Birth latitude override.
        birth_longitude: Birth longitude override.
        birth_timezone: IANA timezone override.
        planet: Optional planet name (Sun/Moon/Mars/Mercury/Jupiter/Venus/Saturn/Rahu/Ketu).

    Returns:
        Dict of avastha results keyed by planet name.
    """
    try:
        _, lat, lon, tz_name = _resolve_location(
            birth_place, birth_latitude, birth_longitude, birth_timezone
        )
    except ValueError as e:
        return {"error": str(e)}

    birth_dt = _parse_dt(birth_date, birth_time, tz_name)
    time = AstroTime(birth_dt, lat, lon)

    planets_to_check = (
        [p for p in Planet if p.name.lower() == planet.lower()]
        if planet
        else list(Planet)
    )

    if planet and not planets_to_check:
        return {"error": f"Unknown planet '{planet}'"}

    sun_longitude = get_planet_longitude(Planet.Sun, time)
    result = {}
    for p in planets_to_check:
        lon_p = get_planet_longitude(p, time)
        house_num = None
        conjuncts = []
        try:
            from logic.house_queries import get_planet_house
            house_num = get_planet_house(p, time)
            conjuncts = [
                op.name for op in Planet
                if op != p and abs(get_planet_longitude(op, time) - lon_p) < 10
            ]
        except Exception:
            pass
        result[p.name] = get_all_avasthas(p.name, lon_p, sun_longitude, house_num, conjuncts)

    return result if not planet else result.get(planets_to_check[0].name, {})


# ---------------------------------------------------------------------------
# Jaimini Astrology
# ---------------------------------------------------------------------------

@mcp.tool()
def get_jaimini(
    dt: str,
    lat: float,
    lon: float,
    query: str = "all",
    current_dt: str = "",
) -> dict:
    """
    Jaimini astrology: Chara Karakas, Chara Dasa, and Arudha Padas.

    Args:
        dt: Birth datetime in ISO 8601 format (e.g. "1990-06-15T10:30:00")
        lat: Birth latitude in decimal degrees
        lon: Birth longitude in decimal degrees
        query: What to return — "karakas", "chara_dasa", "arudhas", or "all" (default)
        current_dt: Reference datetime for current Chara Dasa (ISO 8601, defaults to now)

    Returns:
        Dict with requested Jaimini data. "karakas" gives the 7 temporal significators
        ranked by degree. "chara_dasa" gives the current sign-dasa and antardasa.
        "arudhas" gives the 12 Arudha Padas.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.calculate import get_planet_longitude, get_lagnam
    from logic.jaimini import get_chara_karakas, get_chara_dasa, get_chara_dasa_antardasa, get_all_arudhas
    from logic.shadbala import datetime_to_jd
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    classical_planets = [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                         Planet.Jupiter, Planet.Venus, Planet.Saturn]
    planet_longs = {p.name: get_planet_longitude(p, time) for p in classical_planets}
    lagna_long = get_lagnam(time)

    result = {}

    if query in ("karakas", "all"):
        result["karakas"] = get_chara_karakas(planet_longs)

    if query in ("chara_dasa", "all"):
        birth_jd = datetime_to_jd(birth_dt)
        if current_dt:
            cur_dt = datetime.fromisoformat(current_dt)
            if cur_dt.tzinfo is None:
                cur_dt = cur_dt.replace(tzinfo=timezone.utc)
            current_jd = datetime_to_jd(cur_dt)
        else:
            current_jd = datetime_to_jd(datetime.now(timezone.utc))
        dasa = get_chara_dasa(lagna_long, planet_longs, birth_jd, current_jd)
        cd = dasa["current_dasa"]
        antardasa = get_chara_dasa_antardasa(
            cd["sign"], dasa["lagna_sign"], planet_longs,
            cd["years"], dasa["years_into_dasa"]
        )
        result["chara_dasa"] = {
            "lagna_sign": dasa["lagna_sign"],
            "lagna_name": dasa["lagna_name"],
            "years_elapsed": dasa["years_elapsed"],
            "years_into_dasa": dasa["years_into_dasa"],
            "years_remaining": dasa["years_remaining"],
            "current_dasa": dasa["current_dasa"],
            "current_antardasa": antardasa,
            "dasa_periods": dasa["dasa_periods"],
        }

    if query in ("arudhas", "all"):
        lagna_sign = int(lagna_long / 30)
        result["arudhas"] = get_all_arudhas(lagna_sign, planet_longs)

    return result


# ---------------------------------------------------------------------------
# Varshaphal (Solar Return / Annual Horoscope)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_varshaphal(
    dt: str,
    lat: float,
    lon: float,
    year: int = 0,
) -> dict:
    """
    Varshaphal (annual horoscope / solar return) for a given year.

    Computes the solar return chart and derives the Muntha, Year Lord,
    and key Sahams for the requested Varsha year.

    Args:
        dt: Birth datetime in ISO 8601 format (e.g. "1990-06-15T10:30:00")
        lat: Birth latitude in decimal degrees
        lon: Birth longitude in decimal degrees
        year: Target Varsha year (0 = current year)

    Returns:
        Dict with varsha_year, age, varsha_lagna, muntha, year_lord,
        muntha_lord_bala, key_sahams, and year_quality.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.calculate import get_planet_longitude, get_lagnam
    from logic.varshaphal import get_varshaphal as _get_varshaphal
    from logic.shadbala import datetime_to_jd
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    birth_time = AstroTime(birth_dt, lat, lon)
    birth_jd = datetime_to_jd(birth_dt)

    natal_sun_long = get_planet_longitude(Planet.Sun, birth_time)
    natal_planet_longs = {
        p.name: get_planet_longitude(p, birth_time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn]
    }
    birth_lagna_long = get_lagnam(birth_time)

    target_year = year if year else datetime.now(timezone.utc).year

    # Compute solar return JD directly (avoids buggy get_solar_return_jd stub)
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
    # Python weekday(): 0=Monday → convert to Varshaphal convention: 0=Sunday
    varsha_weekday = (solar_return_dt.weekday() + 1) % 7

    return _get_varshaphal(
        birth_dt, birth_lagna_long, natal_sun_long,
        natal_planet_longs, target_year,
        varsha_lagna_long, varsha_planet_longs, varsha_weekday,
    )


# ---------------------------------------------------------------------------
# Lordship (House Lords)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_house_lords(
    dt: str,
    lat: float,
    lon: float,
    planet: str = "",
) -> dict:
    """
    Returns house lordship information for the birth chart.

    Args:
        dt: Birth datetime in ISO 8601 format (e.g. "1990-06-15T10:30:00")
        lat: Birth latitude in decimal degrees
        lon: Birth longitude in decimal degrees
        planet: Optional planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn).
                When provided, returns only the houses ruled by that planet.
                When omitted, returns the lord and sign for all 12 houses.

    Returns:
        When planet is empty: {"houses": {"1": {"lord": "Mars", "sign": "Aries"}, ...}}
        When planet is given: {"planet": "Mars", "houses_ruled": [1, 8]}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.lordship import get_all_house_lords, get_house_sign, get_houses_ruled_by_planet, SIGN_NAMES as _SIGN_NAMES
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    if planet:
        name_map = {p.name.lower(): p for p in Planet}
        p = name_map.get(planet.lower())
        if p is None:
            return {"error": f"Unknown planet: {planet}"}
        houses = get_houses_ruled_by_planet(p, time)
        return {"planet": p.name, "houses_ruled": houses}

    lords = get_all_house_lords(time)
    result = {}
    for house_num, lord_planet in lords.items():
        sign_idx = get_house_sign(house_num, time)
        result[str(house_num)] = {
            "lord": lord_planet.name,
            "sign_index": sign_idx,
            "sign": _SIGN_NAMES[sign_idx],
        }
    return {"houses": result}


# ---------------------------------------------------------------------------
# Planet Relationships
# ---------------------------------------------------------------------------

@mcp.tool()
def get_planet_relationships(
    dt: str,
    lat: float,
    lon: float,
) -> dict:
    """
    Returns the full 9×9 combined (natural + temporary) planet relationship grid.

    Combined relationship is the sum of natural and temporal relationships,
    giving values like GreatFriend, Friend, Neutral, Enemy, GreatEnemy.

    Args:
        dt: Birth/transit datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees

    Returns:
        {"relationships": {planet: {other_planet: relationship_label, ...}, ...}}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.planet_relations import get_all_planet_relationships
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)
    return {"relationships": get_all_planet_relationships(time)}


# ---------------------------------------------------------------------------
# Planet Aspects (Graha Drishti)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_planet_aspects(
    dt: str,
    lat: float,
    lon: float,
    planet: str = "",
) -> dict:
    """
    Returns Graha Drishti (planetary aspect) information.

    Special aspects: Saturn→3rd,10th; Jupiter→5th,9th; Mars→4th,8th; all→7th.

    Args:
        dt: Birth/transit datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees
        planet: Optional planet name (Sun, Moon, Mars, ...). When given, returns
                which signs that planet aspects and which planets aspect it.
                When empty, returns the full 9x9 aspect grid.

    Returns:
        Full grid {"aspects": {planet: {other: true/false}}} or
        single-planet {"planet": "Mars", "aspects_signs": [...], "aspected_by_planets": [...]}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.aspects import (
        get_full_aspect_grid,
        get_signs_planet_is_aspecting,
        get_planets_aspecting_planet,
    )
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    if planet:
        try:
            p = Planet[planet]
        except KeyError:
            return {"error": f"Unknown planet: {planet}"}
        return {
            "planet": planet,
            "aspects_signs": get_signs_planet_is_aspecting(p, time),
            "aspected_by_planets": [x.name for x in get_planets_aspecting_planet(p, time)],
        }

    return {"aspects": get_full_aspect_grid(time)}


# ---------------------------------------------------------------------------
# Planet Dignity
# ---------------------------------------------------------------------------

@mcp.tool()
def get_chart_dignities(
    dt: str,
    lat: float,
    lon: float,
    planet: str = "",
) -> dict:
    """
    Returns planetary dignity for the birth chart.

    Dignity levels (strongest → weakest):
    ExaltedDegree, Exalted, OwnSign, Moolatrikona, Neutral, Debilitated, DebilitatedDegree.

    Args:
        dt: Birth datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees
        planet: Optional planet name. When given, returns only that planet's dignity.
                When empty, returns all 9 planets.

    Returns:
        {"dignities": {planet: level}} or {"planet": "...", "dignity": level}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.dignity import get_planet_dignity as _gpd, get_all_planet_dignities
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    if planet:
        try:
            p = Planet[planet]
        except KeyError:
            return {"error": f"Unknown planet: {planet}"}
        return {"planet": planet, "dignity": _gpd(p, time)}

    return {"dignities": get_all_planet_dignities(time)}


# ---------------------------------------------------------------------------
# House Positions
# ---------------------------------------------------------------------------

@mcp.tool()
def get_house_positions(
    dt: str,
    lat: float,
    lon: float,
    planet: str = "",
) -> dict:
    """
    Returns whole-sign house positions for the birth chart.

    Args:
        dt: Birth datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees
        planet: Optional planet name. When given, returns just that planet's house.
                When empty, returns all planets' houses plus house occupancy map.

    Returns:
        {"planet_houses": {...}, "house_occupancy": {...}} or {"planet": "...", "house": N}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.house_queries import get_planet_house, get_all_planet_houses, get_house_occupancy_map
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    if planet:
        try:
            p = Planet[planet]
        except KeyError:
            return {"error": f"Unknown planet: {planet}"}
        return {"planet": planet, "house": get_planet_house(p, time)}

    return {
        "planet_houses": get_all_planet_houses(time),
        "house_occupancy": get_house_occupancy_map(time),
    }


# ---------------------------------------------------------------------------
# Muhurtha (Electional Astrology)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_muhurtha(
    dt: str,
    lat: float,
    lon: float,
    birth_moon_sign: int = 0,
    query: str = "all",
) -> dict:
    """
    Returns Muhurtha (electional astrology) assessments.

    Args:
        dt: Transit/query datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees
        birth_moon_sign: Janma Rasi (1=Aries … 12=Pisces). Required for
                         chandrabala and ghataka. Pass 0 to skip those.
        query: Which check to run — "chandrabala", "panchaka", "ghataka", or "all" (default)

    Returns:
        Dict with requested muhurtha data.
        "chandrabala": Moon's positional strength (score 1-12).
        "panchaka": Panchaka Dosha type and whether present.
        "ghataka": Ghataka factors and total inauspicious count.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.calculate import get_planet_longitude, get_lagnam
    from logic.nakshatra import get_nakshatra
    from logic.panchang import get_tithi
    from logic.rasi import get_rasi
    from logic.muhurtha import get_chandrabala, get_panchaka, get_ghataka_chakra
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    sun_long  = get_planet_longitude(Planet.Sun,  time)
    moon_long = get_planet_longitude(Planet.Moon, time)
    _, transit_moon_sign = get_rasi(moon_long)
    _, lagna_sign_num    = get_rasi(get_lagnam(time))
    _, tithi_num, _ = get_tithi(sun_long, moon_long)
    nak_name, nak_num, _, _ = get_nakshatra(moon_long)
    python_weekday = birth_dt.weekday()

    result = {}

    if query in ("chandrabala", "all") and birth_moon_sign:
        cb = get_chandrabala(birth_moon_sign, transit_moon_sign)
        cb["birth_moon_sign"] = birth_moon_sign
        cb["transit_moon_sign"] = transit_moon_sign
        result["chandrabala"] = cb

    if query in ("panchaka", "all"):
        pk = get_panchaka(tithi_num, nak_num, python_weekday, lagna_sign_num)
        pk["tithi_num"] = tithi_num
        pk["nakshatra"] = nak_name
        result["panchaka"] = pk

    if query in ("ghataka", "all") and birth_moon_sign:
        result["ghataka"] = get_ghataka_chakra(
            birth_moon_sign, transit_moon_sign,
            tithi_num, python_weekday, nak_name, lagna_sign_num
        )

    return result


# ---------------------------------------------------------------------------
# Kakshya (Sub-lord Divisions)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_kakshya(
    dt: str,
    lat: float,
    lon: float,
) -> dict:
    """
    Returns Kakshya (KP-style sub-lord) division for all 9 planets.

    Each sign is split into 8 sub-divisions of 3°45' with fixed lords:
    Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.
    The Kakshya lord fine-tunes transit predictions in KP astrology.

    Args:
        dt: Birth/transit datetime in ISO 8601 format
        lat: Geographic latitude in decimal degrees
        lon: Geographic longitude in decimal degrees

    Returns:
        {"kakshya": {planet: {"kakshya_lord": "...", "kakshya_num": N, "percentage": X}}}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.calculate import get_planet_longitude
    from logic.kakshya import get_all_planets_kakshya
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    planet_longs = {
        p.name: get_planet_longitude(p, time)
        for p in [Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
                  Planet.Jupiter, Planet.Venus, Planet.Saturn,
                  Planet.Rahu, Planet.Ketu]
    }
    return {"kakshya": get_all_planets_kakshya(planet_longs)}


# ---------------------------------------------------------------------------
# Pancha Pakshi (Five Bird System)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_pancha_pakshi_analysis(
    dt: str,
    lat: float,
    lon: float,
    query_dt: str = "",
) -> dict:
    """
    Returns Pancha Pakshi (Five Bird System) analysis for the birth chart.

    Birth bird is derived from the birth Moon nakshatra and tithi.
    Shows the bird's activity at the query time and favorable periods for the day.

    Args:
        dt: Birth datetime in ISO 8601 format (e.g. "1990-06-15T10:30:00")
        lat: Birth latitude in decimal degrees
        lon: Birth longitude in decimal degrees
        query_dt: Moment to analyse (ISO 8601, defaults to now)

    Returns:
        Dict with birth_bird, current_activity, favorability (0-100),
        prediction, ruling_bird, all_birds activities, and favorable_periods.
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.consts import Planet
    from logic.calculate import get_planet_longitude
    from logic.nakshatra import get_nakshatra
    from logic.panchang import get_tithi
    from logic.pancha_pakshi import get_pancha_pakshi, get_favorable_periods, Activity
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

    moon_long = get_planet_longitude(Planet.Moon, time)
    sun_long  = get_planet_longitude(Planet.Sun,  time)
    _, birth_nak_num, _, _ = get_nakshatra(moon_long)   # 1-27
    _, birth_tithi_num, _  = get_tithi(sun_long, moon_long)  # 1-30

    if query_dt:
        qdt = datetime.fromisoformat(query_dt)
        if qdt.tzinfo is None:
            qdt = qdt.replace(tzinfo=timezone.utc)
    else:
        qdt = datetime.now(timezone.utc)

    result = get_pancha_pakshi(birth_nak_num, birth_tithi_num, qdt)

    # Serialize enums to JSON-safe ints
    result["birth_bird"]["bird"] = int(result["birth_bird"]["bird"])
    result["current_activity"]["activity"] = int(result["current_activity"]["activity"])
    if result["ruling_bird"]["bird"] is not None:
        result["ruling_bird"]["bird"] = int(result["ruling_bird"]["bird"])
    result["query_time"]["datetime"] = qdt.isoformat()

    result["favorable_periods"] = get_favorable_periods(
        birth_nak_num, birth_tithi_num, qdt, Activity.EATING
    )
    return result


# ---------------------------------------------------------------------------
# Wealth Yogas (Chatussagara, Vasumathi, Parvata)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_wealth_yogas(
    dt: str,
    lat: float,
    lon: float,
) -> dict:
    """
    Returns the three classical wealth and success yogas.

    - Chatussagara Yoga: All four kendras occupied (four oceans of plenty).
      Indicates power, wealth from multiple sources, well-rounded success.
    - Vasumathi Yoga: Benefics in upachaya houses (3, 6, 10, 11).
      Indicates steady wealth accumulation and rise in life.
    - Parvata Yoga: Benefics in kendras AND lagna/7th lord dignified.
      Indicates towering, stable success and community leadership.

    Args:
        dt: Birth datetime in ISO 8601 format (e.g. "1990-06-15T10:30:00")
        lat: Birth latitude in decimal degrees
        lon: Birth longitude in decimal degrees

    Returns:
        {"wealth_yogas": [{name, occurring, strength, description, condition, nature}, ...]}
    """
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logic.time import AstroTime
    from logic.wealth_yogas_temp import (
        check_chatussagara_yoga, check_vasumathi_yoga, check_parvata_yoga
    )
    from datetime import datetime, timezone

    birth_dt = datetime.fromisoformat(dt)
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=timezone.utc)
    time = AstroTime(birth_dt, lat, lon)

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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
