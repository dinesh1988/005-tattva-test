"""
Bhava Chalit Chart — Sripati House System
==========================================
Calculates the Sripati (Bhava Chalit) house cusps and redistributes all 9 planets
into Chalit houses (which may differ from their Rasi/D1 houses).

Ported from Core.cs AllHouseLongitudes() and GetPlanetChartPosition().
"""

from .calculate import get_sripati_cusps, get_planet_longitude
from .time import AstroTime
from .consts import Planet

_ALL_PLANETS = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu,
]

_PLANET_NAMES = {
    Planet.Sun: "Sun", Planet.Moon: "Moon", Planet.Mars: "Mars",
    Planet.Mercury: "Mercury", Planet.Jupiter: "Jupiter",
    Planet.Venus: "Venus", Planet.Saturn: "Saturn",
    Planet.Rahu: "Rahu", Planet.Ketu: "Ketu",
}

_RASI_NAMES = [
    "", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _sign_num(longitude: float) -> int:
    """Return the sign number (1-12) for a sidereal longitude."""
    return int(longitude / 30.0) % 12 + 1


def _planet_chalit_house(planet_long: float, cusps: dict) -> int:
    """
    Determine which Bhava (Chalit house 1-12) a planet falls in,
    given Sripati house cusps.

    Sripati cusps are the *midpoints* of each house sector.
    The 'beginning' (junction) of each house is the midpoint between
    adjacent house midpoints.

    Returns house number 1-12.
    """
    # Build junction longitudes (beginning of each house)
    midpoints = [cusps[str(i)] for i in range(1, 13)]

    junctions = []
    for i in range(12):
        prev_mid = midpoints[i]
        next_mid = midpoints[(i + 1) % 12]
        # Arc may cross 360°
        arc = (next_mid - prev_mid) % 360
        junction = (prev_mid + arc / 2.0) % 360
        junctions.append(junction)

    # junctions[i] = start of house (i+1)
    long = planet_long % 360
    for i in range(12):
        start = junctions[i]
        end   = junctions[(i + 1) % 12]
        arc   = (end - start) % 360
        dist  = (long - start) % 360
        if dist < arc:
            return i + 1

    return 1  # fallback


def get_bhava_chalit(time: AstroTime) -> dict:
    """
    Calculate Bhava Chalit (Sripati) house cusps and planet redistribution.

    Returns:
        {
            "cusps": {"1": lon, ..., "12": lon},   # Sripati house midpoint longitudes
            "cusps_rasi": {"1": "Aries", ...},      # Rasi for each cusp
            "planet_chalit_house": {"Sun": 3, ...}, # Each planet's Chalit house
            "planet_rasi_house": {"Sun": 3, ...},   # Each planet's Rasi (D1) house (for comparison)
            "differs_from_rasi": ["Mercury", ...]   # Planets that moved to a different house
        }
    """
    cusps = get_sripati_cusps(time)

    # Ascendant defines house 1 starting sign → house N sign = (asc_sign + N - 1) % 12
    asc_sign = _sign_num(cusps["1"])

    chalit_houses: dict = {}
    rasi_houses: dict = {}

    for planet in _ALL_PLANETS:
        pname = _PLANET_NAMES[planet]
        p_long = get_planet_longitude(planet, time)

        # Chalit house
        ch = _planet_chalit_house(p_long, cusps)
        chalit_houses[pname] = ch

        # Rasi (D1) house — simple 30° division from the same Sripati ASC
        p_sign = _sign_num(p_long)
        rasi_house = ((p_sign - asc_sign) % 12) + 1
        rasi_houses[pname] = rasi_house

    differs = [p for p in chalit_houses if chalit_houses[p] != rasi_houses[p]]

    cusps_rasi = {h: _RASI_NAMES[_sign_num(cusps[h])] for h in cusps}

    return {
        "cusps": cusps,
        "cusps_rasi": cusps_rasi,
        "planet_chalit_house": chalit_houses,
        "planet_rasi_house": rasi_houses,
        "differs_from_rasi": differs,
    }
