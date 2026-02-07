import swisseph as swe
from datetime import datetime
import pytz

class AstroTime:
    def __init__(self, dt: datetime, lat: float, lon: float):
        """
        dt: datetime object (should be timezone aware or UTC)
        lat: Latitude of the place
        lon: Longitude of the place
        """
        self.datetime = dt
        self.lat = lat
        self.lon = lon
        
        # Ensure datetime is UTC for Julian Day calculation
        if dt.tzinfo is None:
            # Assume UTC if no timezone provided, or handle as needed
            dt_utc = dt.replace(tzinfo=pytz.UTC)
        else:
            dt_utc = dt.astimezone(pytz.UTC)
            
        self.dt_utc = dt_utc

        # Calculate Julian Day (UT)
        self.julian_day = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0
        )



        
        # Delta T adjustment (Ephemeris Time vs Universal Time)
        # swe.julday returns UT. For planetary positions, we often need ET (TT).
        # However, pyswisseph's calc_ut takes UT, so we might not need manual Delta T if using calc_ut.
        # If using calc(), we need ET.
        # Let's stick to calc_ut for simplicity as it handles Delta T internally.
