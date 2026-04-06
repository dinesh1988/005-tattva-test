"""
Upagraha (Shadow Planet) Positions
====================================
Calculates the positions of Upagrahas (sub-planets):
  - Gulika (Son of Saturn, start of Mandi's segment)
  - Mandi  (Saturn's portion start)

Both are computed by dividing the day or night into 8 equal parts according
to the weekday lord sequence, then finding the Lagna (rising sign longitude)
at that exact moment.

Classic Vedic formula:
- Day = sunrise to sunset  (8 parts)
- Night = sunset to next sunrise (8 parts)

Mandi part index by weekday (1-indexed, day birth):
  Sun=7, Mon=6, Tue=5, Wed=4, Thu=3, Fri=2, Sat=1

Mandi part index by weekday (1-indexed, night birth):
  Sun=4, Mon=3, Tue=2, Wed=1, Thu=8, Fri=7, Sat=6

Gulika = start of (Mandi_part - 1), i.e., one part earlier than Mandi.
The position of each upagraha = the Lagna longitude at the moment it begins.

Ported from classic Vedic texts; no C# counterpart (position calc absent from
VedAstro C# — only aspect rules are present there).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytz
import swisseph as swe  # type: ignore

from .time import AstroTime

# ---------------------------------------------------------------------------
# Ephemeris path
# ---------------------------------------------------------------------------
_current_dir = os.path.dirname(os.path.abspath(__file__))
_ephe_path = os.path.join(os.path.dirname(_current_dir), "ephe")
swe.set_ephe_path(_ephe_path)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Mandi day-part index (1-indexed) for day birth, keyed by Python weekday Mon=0..Sun=6
_MANDI_DAY_PART = {
    6: 7,  # Sunday
    0: 6,  # Monday
    1: 5,  # Tuesday
    2: 4,  # Wednesday
    3: 3,  # Thursday
    4: 2,  # Friday
    5: 1,  # Saturday
}

# Mandi day-part index (1-indexed) for night birth, keyed by Python weekday Mon=0..Sun=6
_MANDI_NIGHT_PART = {
    6: 4,  # Sunday
    0: 3,  # Monday
    1: 2,  # Tuesday
    2: 1,  # Wednesday
    3: 8,  # Thursday
    4: 7,  # Friday
    5: 6,  # Saturday
}

_SIGN_NAMES = [
    "", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _jd_ut_to_lagna(jd_ut: float, lat: float, lon: float) -> float:
    """Return sidereal Lagna longitude at the given Julian Day."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    tropical_asc = ascmc[0]
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    sidereal_asc = (tropical_asc - ayanamsa) % 360
    return sidereal_asc


def _sunrise_sunset_jd(jd_local_midnight: float, lat: float, lon: float) -> tuple:
    """Return (sunrise_jd, sunset_jd, next_sunrise_jd) as Julian Days UT."""
    geopos = (lon, lat, 0.0)
    rsmi_rise = swe.CALC_RISE | swe.BIT_DISC_CENTER
    rsmi_set  = swe.CALC_SET  | swe.BIT_DISC_CENTER

    _, tret_rise = swe.rise_trans(jd_local_midnight, swe.SUN, rsmi_rise, geopos)
    _, tret_set  = swe.rise_trans(jd_local_midnight, swe.SUN, rsmi_set,  geopos)

    # Next sunrise: search from after sunset
    _, tret_next_rise = swe.rise_trans(tret_set[0], swe.SUN, rsmi_rise, geopos)

    return tret_rise[0], tret_set[0], tret_next_rise[0]


def _local_midnight_jd(dt: datetime, tz_name: str) -> float:
    """Return the Julian Day UT for midnight of the local date."""
    tz = pytz.timezone(tz_name)
    if dt.tzinfo is None:
        dt_local = tz.localize(dt)
    else:
        dt_local = dt.astimezone(tz)

    midnight_local = tz.localize(
        datetime(dt_local.year, dt_local.month, dt_local.day, 0, 0, 0)
    )
    midnight_utc = midnight_local.astimezone(pytz.UTC)
    return swe.julday(
        midnight_utc.year, midnight_utc.month, midnight_utc.day,
        midnight_utc.hour + midnight_utc.minute / 60.0 + midnight_utc.second / 3600.0,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_upagraha_positions(time: AstroTime, tz_name: str = "UTC") -> dict:
    """
    Calculate Gulika and Mandi positions (sidereal Lagna at their start moment).

    Args:
        time:    AstroTime for the birth moment (used for lat/lon and birth JD).
        tz_name: IANA timezone name of the birth location.

    Returns:
        {
            "mandi": {
                "longitude":   float,          # sidereal degrees
                "sign":        str,             # e.g. "Scorpio"
                "sign_degree": float,           # degree within sign
                "is_day_birth": bool,
                "mandi_start_jd": float
            },
            "gulika": {
                "longitude":   float,
                "sign":        str,
                "sign_degree": float,
                "gulika_start_jd": float
            }
        }
    """
    jd = time.julian_day
    lat = time.lat
    lon = time.lon

    # Find local midnight JD for birth date
    dt = time.datetime  # should be timezone-aware
    midnight_jd = _local_midnight_jd(dt, tz_name)

    sunrise_jd, sunset_jd, next_sunrise_jd = _sunrise_sunset_jd(midnight_jd, lat, lon)

    day_dur   = sunset_jd - sunrise_jd          # in days
    night_dur = next_sunrise_jd - sunset_jd     # in days

    # Is birth during day or night?
    is_day = sunrise_jd <= jd <= sunset_jd

    weekday = dt.weekday()  # Mon=0..Sun=6

    if is_day:
        part_dur   = day_dur / 8.0
        base_jd    = sunrise_jd
        mandi_part = _MANDI_DAY_PART[weekday]
    else:
        part_dur   = night_dur / 8.0
        base_jd    = sunset_jd
        mandi_part = _MANDI_NIGHT_PART[weekday]

    # Mandi starts at the beginning of its assigned part (0-indexed: mandi_part - 1)
    mandi_start_jd  = base_jd + (mandi_part - 1) * part_dur
    # Gulika starts one part before Mandi
    gulika_start_jd = base_jd + (mandi_part - 2) * part_dur

    # Handle wrap-around (part 8 → Gulika would be in the previous cycle)
    if gulika_start_jd < base_jd:
        gulika_start_jd = base_jd  # clamp to period start

    mandi_long  = _jd_ut_to_lagna(mandi_start_jd,  lat, lon)
    gulika_long = _jd_ut_to_lagna(gulika_start_jd, lat, lon)

    def _sign_info(l: float) -> tuple:
        sign_num   = int(l / 30.0) % 12 + 1
        sign_name  = _SIGN_NAMES[sign_num]
        deg_in_sign = l % 30.0
        return sign_name, round(deg_in_sign, 4)

    m_sign, m_deg = _sign_info(mandi_long)
    g_sign, g_deg = _sign_info(gulika_long)

    return {
        "mandi": {
            "longitude":      round(mandi_long, 4),
            "sign":           m_sign,
            "sign_degree":    m_deg,
            "is_day_birth":   is_day,
            "mandi_start_jd": mandi_start_jd,
        },
        "gulika": {
            "longitude":       round(gulika_long, 4),
            "sign":            g_sign,
            "sign_degree":     g_deg,
            "gulika_start_jd": gulika_start_jd,
        },
    }
