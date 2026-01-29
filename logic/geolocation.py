"""
Geolocation - Convert place names to latitude/longitude coordinates
"""

from typing import Tuple, Optional, Dict

# =============================================================================
# BUILT-IN CITY DATABASE (No internet required)
# =============================================================================

CITIES: Dict[str, Tuple[float, float, str]] = {
    # Format: 'City': (latitude, longitude, timezone)
    
    # INDIA - Major Cities
    'Chennai': (13.0827, 80.2707, 'Asia/Kolkata'),
    'Mumbai': (19.0760, 72.8777, 'Asia/Kolkata'),
    'Delhi': (28.6139, 77.2090, 'Asia/Kolkata'),
    'New Delhi': (28.6139, 77.2090, 'Asia/Kolkata'),
    'Bangalore': (12.9716, 77.5946, 'Asia/Kolkata'),
    'Bengaluru': (12.9716, 77.5946, 'Asia/Kolkata'),
    'Kolkata': (22.5726, 88.3639, 'Asia/Kolkata'),
    'Hyderabad': (17.3850, 78.4867, 'Asia/Kolkata'),
    'Pune': (18.5204, 73.8567, 'Asia/Kolkata'),
    'Ahmedabad': (23.0225, 72.5714, 'Asia/Kolkata'),
    'Jaipur': (26.9124, 75.7873, 'Asia/Kolkata'),
    'Lucknow': (26.8467, 80.9462, 'Asia/Kolkata'),
    'Kanpur': (26.4499, 80.3319, 'Asia/Kolkata'),
    'Nagpur': (21.1458, 79.0882, 'Asia/Kolkata'),
    'Indore': (22.7196, 75.8577, 'Asia/Kolkata'),
    'Bhopal': (23.2599, 77.4126, 'Asia/Kolkata'),
    'Patna': (25.5941, 85.1376, 'Asia/Kolkata'),
    'Vadodara': (22.3072, 73.1812, 'Asia/Kolkata'),
    'Surat': (21.1702, 72.8311, 'Asia/Kolkata'),
    'Coimbatore': (11.0168, 76.9558, 'Asia/Kolkata'),
    'Madurai': (9.9252, 78.1198, 'Asia/Kolkata'),
    'Varanasi': (25.3176, 82.9739, 'Asia/Kolkata'),
    'Thiruvananthapuram': (8.5241, 76.9366, 'Asia/Kolkata'),
    'Kochi': (9.9312, 76.2673, 'Asia/Kolkata'),
    'Visakhapatnam': (17.6868, 83.2185, 'Asia/Kolkata'),
    'Chandigarh': (30.7333, 76.7794, 'Asia/Kolkata'),
    'Amritsar': (31.6340, 74.8723, 'Asia/Kolkata'),
    'Agra': (27.1767, 78.0081, 'Asia/Kolkata'),
    'Mysore': (12.2958, 76.6394, 'Asia/Kolkata'),
    'Mangalore': (12.9141, 74.8560, 'Asia/Kolkata'),
    'Vellore': (12.85, 79.0333, 'Asia/Kolkata'),
    'Ujjain': (23.1765, 75.7885, 'Asia/Kolkata'),
    'Nashik': (19.9975, 73.7898, 'Asia/Kolkata'),
    'Guwahati': (26.1445, 91.7362, 'Asia/Kolkata'),
    'Ranchi': (23.3441, 85.3096, 'Asia/Kolkata'),
    'Raipur': (21.2514, 81.6296, 'Asia/Kolkata'),
    'Dehradun': (30.3165, 78.0322, 'Asia/Kolkata'),
    'Shimla': (31.1048, 77.1734, 'Asia/Kolkata'),
    'Srinagar': (34.0837, 74.7973, 'Asia/Kolkata'),
    'Pondicherry': (11.9416, 79.8083, 'Asia/Kolkata'),
    'Puducherry': (11.9416, 79.8083, 'Asia/Kolkata'),
    'Tirupati': (13.6288, 79.4192, 'Asia/Kolkata'),
    'Tiruchirappalli': (10.7905, 78.7047, 'Asia/Kolkata'),
    
    # USA - Major Cities
    'New York': (40.7128, -74.0060, 'America/New_York'),
    'Los Angeles': (34.0522, -118.2437, 'America/Los_Angeles'),
    'Chicago': (41.8781, -87.6298, 'America/Chicago'),
    'Houston': (29.7604, -95.3698, 'America/Chicago'),
    'Phoenix': (33.4484, -112.0740, 'America/Phoenix'),
    'San Francisco': (37.7749, -122.4194, 'America/Los_Angeles'),
    'Seattle': (47.6062, -122.3321, 'America/Los_Angeles'),
    'Boston': (42.3601, -71.0589, 'America/New_York'),
    'Miami': (25.7617, -80.1918, 'America/New_York'),
    'Denver': (39.7392, -104.9903, 'America/Denver'),
    'Atlanta': (33.7490, -84.3880, 'America/New_York'),
    'Dallas': (32.7767, -96.7970, 'America/Chicago'),
    'Washington DC': (38.9072, -77.0369, 'America/New_York'),
    'San Diego': (32.7157, -117.1611, 'America/Los_Angeles'),
    'Las Vegas': (36.1699, -115.1398, 'America/Los_Angeles'),
    'Novi': (42.4806, -83.4755, 'America/Detroit'),
    'Detroit': (42.3314, -83.0458, 'America/Detroit'),
    
    # UK & Europe
    'London': (51.5074, -0.1278, 'Europe/London'),
    'Manchester': (53.4808, -2.2426, 'Europe/London'),
    'Birmingham': (52.4862, -1.8904, 'Europe/London'),
    'Edinburgh': (55.9533, -3.1883, 'Europe/London'),
    'Glasgow': (55.8642, -4.2518, 'Europe/London'),
    'Paris': (48.8566, 2.3522, 'Europe/Paris'),
    'Berlin': (52.5200, 13.4050, 'Europe/Berlin'),
    'Munich': (48.1351, 11.5820, 'Europe/Berlin'),
    'Frankfurt': (50.1109, 8.6821, 'Europe/Berlin'),
    'Amsterdam': (52.3676, 4.9041, 'Europe/Amsterdam'),
    'Brussels': (50.8503, 4.3517, 'Europe/Brussels'),
    'Rome': (41.9028, 12.4964, 'Europe/Rome'),
    'Milan': (45.4642, 9.1900, 'Europe/Rome'),
    'Madrid': (40.4168, -3.7038, 'Europe/Madrid'),
    'Barcelona': (41.3851, 2.1734, 'Europe/Madrid'),
    'Vienna': (48.2082, 16.3738, 'Europe/Vienna'),
    'Zurich': (47.3769, 8.5417, 'Europe/Zurich'),
    'Geneva': (46.2044, 6.1432, 'Europe/Zurich'),
    'Stockholm': (59.3293, 18.0686, 'Europe/Stockholm'),
    'Oslo': (59.9139, 10.7522, 'Europe/Oslo'),
    'Copenhagen': (55.6761, 12.5683, 'Europe/Copenhagen'),
    'Dublin': (53.3498, -6.2603, 'Europe/Dublin'),
    'Lisbon': (38.7223, -9.1393, 'Europe/Lisbon'),
    'Athens': (37.9838, 23.7275, 'Europe/Athens'),
    'Moscow': (55.7558, 37.6173, 'Europe/Moscow'),
    'St Petersburg': (59.9311, 30.3609, 'Europe/Moscow'),
    
    # Middle East
    'Dubai': (25.2048, 55.2708, 'Asia/Dubai'),
    'Abu Dhabi': (24.4539, 54.3773, 'Asia/Dubai'),
    'Riyadh': (24.7136, 46.6753, 'Asia/Riyadh'),
    'Jeddah': (21.4858, 39.1925, 'Asia/Riyadh'),
    'Kuwait City': (29.3759, 47.9774, 'Asia/Kuwait'),
    'Doha': (25.2854, 51.5310, 'Asia/Qatar'),
    'Muscat': (23.5880, 58.3829, 'Asia/Muscat'),
    'Tehran': (35.6892, 51.3890, 'Asia/Tehran'),
    'Tel Aviv': (32.0853, 34.7818, 'Asia/Jerusalem'),
    'Jerusalem': (31.7683, 35.2137, 'Asia/Jerusalem'),
    'Beirut': (33.8938, 35.5018, 'Asia/Beirut'),
    'Cairo': (30.0444, 31.2357, 'Africa/Cairo'),
    
    # Asia Pacific
    'Singapore': (1.3521, 103.8198, 'Asia/Singapore'),
    'Hong Kong': (22.3193, 114.1694, 'Asia/Hong_Kong'),
    'Tokyo': (35.6762, 139.6503, 'Asia/Tokyo'),
    'Osaka': (34.6937, 135.5023, 'Asia/Tokyo'),
    'Seoul': (37.5665, 126.9780, 'Asia/Seoul'),
    'Beijing': (39.9042, 116.4074, 'Asia/Shanghai'),
    'Shanghai': (31.2304, 121.4737, 'Asia/Shanghai'),
    'Guangzhou': (23.1291, 113.2644, 'Asia/Shanghai'),
    'Shenzhen': (22.5431, 114.0579, 'Asia/Shanghai'),
    'Bangkok': (13.7563, 100.5018, 'Asia/Bangkok'),
    'Kuala Lumpur': (3.1390, 101.6869, 'Asia/Kuala_Lumpur'),
    'Jakarta': (6.2088, 106.8456, 'Asia/Jakarta'),
    'Manila': (14.5995, 120.9842, 'Asia/Manila'),
    'Hanoi': (21.0285, 105.8542, 'Asia/Ho_Chi_Minh'),
    'Ho Chi Minh City': (10.8231, 106.6297, 'Asia/Ho_Chi_Minh'),
    'Taipei': (25.0330, 121.5654, 'Asia/Taipei'),
    
    # Australia & New Zealand
    'Sydney': (-33.8688, 151.2093, 'Australia/Sydney'),
    'Melbourne': (-37.8136, 144.9631, 'Australia/Melbourne'),
    'Brisbane': (-27.4698, 153.0251, 'Australia/Brisbane'),
    'Perth': (-31.9505, 115.8605, 'Australia/Perth'),
    'Adelaide': (-34.9285, 138.6007, 'Australia/Adelaide'),
    'Auckland': (-36.8509, 174.7645, 'Pacific/Auckland'),
    'Wellington': (-41.2865, 174.7762, 'Pacific/Auckland'),
    
    # Canada
    'Toronto': (43.6532, -79.3832, 'America/Toronto'),
    'Vancouver': (49.2827, -123.1207, 'America/Vancouver'),
    'Montreal': (45.5017, -73.5673, 'America/Montreal'),
    'Calgary': (51.0447, -114.0719, 'America/Edmonton'),
    'Ottawa': (45.4215, -75.6972, 'America/Toronto'),
    
    # South America
    'Sao Paulo': (-23.5505, -46.6333, 'America/Sao_Paulo'),
    'Rio de Janeiro': (-22.9068, -43.1729, 'America/Sao_Paulo'),
    'Buenos Aires': (-34.6037, -58.3816, 'America/Argentina/Buenos_Aires'),
    'Lima': (-12.0464, -77.0428, 'America/Lima'),
    'Bogota': (4.7110, -74.0721, 'America/Bogota'),
    'Santiago': (-33.4489, -70.6693, 'America/Santiago'),
    
    # Africa
    'Johannesburg': (-26.2041, 28.0473, 'Africa/Johannesburg'),
    'Cape Town': (-33.9249, 18.4241, 'Africa/Johannesburg'),
    'Lagos': (6.5244, 3.3792, 'Africa/Lagos'),
    'Nairobi': (-1.2921, 36.8219, 'Africa/Nairobi'),
    'Casablanca': (33.5731, -7.5898, 'Africa/Casablanca'),
    
    # South Asia (Neighbors)
    'Colombo': (6.9271, 79.8612, 'Asia/Colombo'),
    'Kathmandu': (27.7172, 85.3240, 'Asia/Kathmandu'),
    'Dhaka': (23.8103, 90.4125, 'Asia/Dhaka'),
    'Karachi': (24.8607, 67.0011, 'Asia/Karachi'),
    'Lahore': (31.5204, 74.3587, 'Asia/Karachi'),
    'Islamabad': (33.6844, 73.0479, 'Asia/Karachi'),
}


def get_coordinates(place_name: str) -> Optional[Tuple[float, float]]:
    """
    Get latitude and longitude for a place name from built-in database.
    
    Args:
        place_name: City name (case-insensitive)
        
    Returns:
        Tuple of (latitude, longitude) or None if not found
    
    Example:
        >>> get_coordinates("Chennai")
        (13.0827, 80.2707)
    """
    # Try exact match (case-insensitive)
    for city, (lat, lon, _) in CITIES.items():
        if city.lower() == place_name.lower():
            return (lat, lon)
    
    # Try partial match
    place_lower = place_name.lower()
    for city, (lat, lon, _) in CITIES.items():
        if place_lower in city.lower() or city.lower() in place_lower:
            return (lat, lon)
    
    return None


def get_location(place_name: str) -> Optional[Dict]:
    """
    Get full location details for a place name.
    
    Args:
        place_name: City name (case-insensitive)
        
    Returns:
        Dict with lat, lon, timezone, and name; or None if not found
    
    Example:
        >>> get_location("Chennai")
        {'name': 'Chennai', 'latitude': 13.0827, 'longitude': 80.2707, 'timezone': 'Asia/Kolkata'}
    """
    for city, (lat, lon, tz) in CITIES.items():
        if city.lower() == place_name.lower():
            return {
                'name': city,
                'latitude': lat,
                'longitude': lon,
                'timezone': tz
            }
    
    # Partial match
    place_lower = place_name.lower()
    for city, (lat, lon, tz) in CITIES.items():
        if place_lower in city.lower() or city.lower() in place_lower:
            return {
                'name': city,
                'latitude': lat,
                'longitude': lon,
                'timezone': tz
            }
    
    return None


def get_timezone(place_name: str) -> Optional[str]:
    """
    Get timezone for a place name.
    
    Args:
        place_name: City name
        
    Returns:
        Timezone string (e.g., 'Asia/Kolkata') or None
    """
    location = get_location(place_name)
    return location['timezone'] if location else None


def search_cities(query: str) -> list:
    """
    Search for cities matching a query.
    
    Args:
        query: Search string
        
    Returns:
        List of matching city names
    """
    query_lower = query.lower()
    matches = []
    for city in CITIES.keys():
        if query_lower in city.lower():
            matches.append(city)
    return sorted(matches)


def list_cities_by_country(country_hint: str) -> list:
    """
    List cities in a country/region based on timezone.
    
    Args:
        country_hint: Country name or timezone region (e.g., 'India', 'Asia/Kolkata')
        
    Returns:
        List of city names
    """
    hint_lower = country_hint.lower()
    
    # Map common country names to timezone patterns
    country_tz_map = {
        'india': 'Asia/Kolkata',
        'usa': 'America/',
        'us': 'America/',
        'uk': 'Europe/London',
        'australia': 'Australia/',
        'japan': 'Asia/Tokyo',
        'china': 'Asia/Shanghai',
        'germany': 'Europe/Berlin',
        'france': 'Europe/Paris',
        'uae': 'Asia/Dubai',
        'canada': 'America/',
    }
    
    tz_pattern = country_tz_map.get(hint_lower, hint_lower)
    
    matches = []
    for city, (_, _, tz) in CITIES.items():
        if tz_pattern.lower() in tz.lower():
            matches.append(city)
    
    return sorted(matches)


# =============================================================================
# ONLINE GEOCODING (Optional - requires geopy)
# =============================================================================

def geocode_online(place_name: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates using online geocoding service (requires geopy).
    Falls back to built-in database if geopy not available.
    
    Args:
        place_name: Any place name or address
        
    Returns:
        Tuple of (latitude, longitude) or None
    """
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut, GeocoderServiceError
        
        geolocator = Nominatim(user_agent="vedastropy")
        try:
            location = geolocator.geocode(place_name, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderTimedOut, GeocoderServiceError):
            pass
    except ImportError:
        pass
    
    # Fallback to built-in database
    return get_coordinates(place_name)


def get_coordinates_smart(place_name: str, use_online: bool = False) -> Optional[Tuple[float, float]]:
    """
    Smart coordinate lookup - tries built-in first, then online if enabled.
    
    Args:
        place_name: Place name or address
        use_online: If True, try online geocoding for unknown places
        
    Returns:
        Tuple of (latitude, longitude) or None
    """
    # Try built-in first
    coords = get_coordinates(place_name)
    if coords:
        return coords
    
    # Try online if enabled
    if use_online:
        return geocode_online(place_name)
    
    return None
