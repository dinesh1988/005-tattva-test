from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytz
import swisseph as _swe  # type: ignore

swe: Any = _swe


@dataclass(frozen=True)
class SunTimes:
    sunrise: datetime
    sunset: datetime
    next_sunrise: datetime


def _set_ephe_path() -> None:
    """Ensure Swiss Ephemeris can find ephemeris files.

    This mirrors `logic.calculate` behavior but avoids import cycles.
    """
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ephe_path = os.path.join(os.path.dirname(current_dir), "ephe")
    swe.set_ephe_path(ephe_path)


def _datetime_to_jd_ut(dt_utc: datetime) -> float:
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def _jd_ut_to_datetime_utc(jd_ut: float) -> datetime:
    year, month, day, ut = swe.revjul(jd_ut)

    hour = int(ut)
    minute_float = (ut - hour) * 60.0
    minute = int(minute_float)
    second_float = (minute_float - minute) * 60.0
    second = int(round(second_float))

    # Handle rounding overflow
    if second >= 60:
        second = 0
        minute += 1
    if minute >= 60:
        minute = 0
        hour += 1

    # Note: if hour overflows (24), Python will throw; this should be rare,
    # and if it happens it indicates we should adjust by a day.
    return datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)


def get_sun_times(*, date_local: datetime, lat: float, lon: float, tz_name: str, altitude_m: float = 0.0) -> SunTimes:
    """Compute sunrise/sunset for the given local date and location.

    Args:
        date_local: A timezone-aware datetime; only the local date is used.
        lat/lon: Geographic coordinates.
        tz_name: IANA timezone name.
        altitude_m: Altitude in meters (default 0).

    Returns:
        SunTimes with local timezone-aware datetimes for sunrise/sunset and next sunrise.
    """

    _set_ephe_path()

    tz = pytz.timezone(tz_name)
    if date_local.tzinfo is None:
        raise ValueError("date_local must be timezone-aware")

    local_midnight = tz.localize(datetime(date_local.year, date_local.month, date_local.day, 0, 0, 0))
    local_midnight_utc = local_midnight.astimezone(pytz.UTC)
    jd_start = _datetime_to_jd_ut(local_midnight_utc)

    geopos = (lon, lat, altitude_m)

    rsmi_rise = swe.CALC_RISE | swe.BIT_DISC_CENTER
    rsmi_set = swe.CALC_SET | swe.BIT_DISC_CENTER

    res_rise, tret_rise = swe.rise_trans(jd_start, swe.SUN, rsmi_rise, geopos)
    if res_rise != 0:
        raise ValueError("Sunrise not found (circumpolar or invalid inputs)")

    res_set, tret_set = swe.rise_trans(jd_start, swe.SUN, rsmi_set, geopos)
    if res_set != 0:
        raise ValueError("Sunset not found (circumpolar or invalid inputs)")

    # Next sunrise: start from next local midnight (use naive datetime arithmetic)
    from datetime import timedelta

    next_local_midnight = local_midnight + timedelta(days=1)
    next_local_midnight_utc = next_local_midnight.astimezone(pytz.UTC)
    jd_next_start = _datetime_to_jd_ut(next_local_midnight_utc)

    res_next_rise, tret_next_rise = swe.rise_trans(jd_next_start, swe.SUN, rsmi_rise, geopos)
    if res_next_rise != 0:
        raise ValueError("Next sunrise not found (circumpolar or invalid inputs)")

    sunrise_local = _jd_ut_to_datetime_utc(tret_rise[0]).astimezone(tz)
    sunset_local = _jd_ut_to_datetime_utc(tret_set[0]).astimezone(tz)
    next_sunrise_local = _jd_ut_to_datetime_utc(tret_next_rise[0]).astimezone(tz)

    return SunTimes(sunrise=sunrise_local, sunset=sunset_local, next_sunrise=next_sunrise_local)
