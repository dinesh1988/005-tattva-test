"""
Pancha Pakshi - Five Bird System
Ancient Tamil predictive system based on 5 birds and their activities
"""

from typing import Dict, Tuple, List
from datetime import datetime
from enum import IntEnum

# =============================================================================
# ENUMS
# =============================================================================

class Bird(IntEnum):
    """The five birds of Pancha Pakshi"""
    VULTURE = 0   # Kazhugu
    OWL = 1       # Andhai
    CROW = 2      # Kakam
    COCK = 3      # Kozhi
    PEACOCK = 4   # Mayil


class Activity(IntEnum):
    """Five activities/states of each bird"""
    RULING = 0    # Best - Full power
    EATING = 1    # Good - Gaining strength
    WALKING = 2   # Moderate - Active
    SLEEPING = 3  # Weak - Dormant
    DYING = 4     # Worst - No power


# Activity names and effects
ACTIVITY_INFO = {
    Activity.RULING: ('Ruling', 'Excellent', 'Full power, highly favorable for all activities'),
    Activity.EATING: ('Eating', 'Good', 'Gaining strength, favorable for gains and nourishment'),
    Activity.WALKING: ('Walking', 'Moderate', 'Active but neutral, proceed with caution'),
    Activity.SLEEPING: ('Sleeping', 'Weak', 'Dormant energy, avoid important activities'),
    Activity.DYING: ('Dying', 'Worst', 'No power, highly unfavorable, avoid new ventures'),
}

# Bird names
BIRD_NAMES = {
    Bird.VULTURE: ('Vulture', 'Kazhugu'),
    Bird.OWL: ('Owl', 'Andhai'),
    Bird.CROW: ('Crow', 'Kakam'),
    Bird.COCK: ('Cock', 'Kozhi'),
    Bird.PEACOCK: ('Peacock', 'Mayil'),
}


# =============================================================================
# BIRTH BIRD CALCULATION
# =============================================================================

# Birth bird based on Nakshatra (0-26) and Paksha (Shukla=0, Krishna=1)
# Format: NAKSHATRA_BIRD[nakshatra_index][paksha] = bird
NAKSHATRA_BIRD = {
    # Ashwini to Bharani (0-1)
    0: {0: Bird.VULTURE, 1: Bird.CROW},      # Ashwini
    1: {0: Bird.OWL, 1: Bird.COCK},          # Bharani
    2: {0: Bird.CROW, 1: Bird.PEACOCK},      # Krittika
    3: {0: Bird.COCK, 1: Bird.VULTURE},      # Rohini
    4: {0: Bird.PEACOCK, 1: Bird.OWL},       # Mrigashira
    
    # Ardra to Pushya (5-7)
    5: {0: Bird.VULTURE, 1: Bird.CROW},      # Ardra
    6: {0: Bird.OWL, 1: Bird.COCK},          # Punarvasu
    7: {0: Bird.CROW, 1: Bird.PEACOCK},      # Pushya
    8: {0: Bird.COCK, 1: Bird.VULTURE},      # Ashlesha
    
    # Magha to Uttara Phalguni (9-11)
    9: {0: Bird.PEACOCK, 1: Bird.OWL},       # Magha
    10: {0: Bird.VULTURE, 1: Bird.CROW},     # Purva Phalguni
    11: {0: Bird.OWL, 1: Bird.COCK},         # Uttara Phalguni
    12: {0: Bird.CROW, 1: Bird.PEACOCK},     # Hasta
    13: {0: Bird.COCK, 1: Bird.VULTURE},     # Chitra
    
    # Swati to Anuradha (14-16)
    14: {0: Bird.PEACOCK, 1: Bird.OWL},      # Swati
    15: {0: Bird.VULTURE, 1: Bird.CROW},     # Vishakha
    16: {0: Bird.OWL, 1: Bird.COCK},         # Anuradha
    17: {0: Bird.CROW, 1: Bird.PEACOCK},     # Jyeshtha
    18: {0: Bird.COCK, 1: Bird.VULTURE},     # Mula
    
    # Purva Ashadha to Shravana (19-21)
    19: {0: Bird.PEACOCK, 1: Bird.OWL},      # Purva Ashadha
    20: {0: Bird.VULTURE, 1: Bird.CROW},     # Uttara Ashadha
    21: {0: Bird.OWL, 1: Bird.COCK},         # Shravana
    22: {0: Bird.CROW, 1: Bird.PEACOCK},     # Dhanishta
    23: {0: Bird.COCK, 1: Bird.VULTURE},     # Shatabhisha
    
    # Purva Bhadrapada to Revati (24-26)
    24: {0: Bird.PEACOCK, 1: Bird.OWL},      # Purva Bhadrapada
    25: {0: Bird.VULTURE, 1: Bird.CROW},     # Uttara Bhadrapada
    26: {0: Bird.OWL, 1: Bird.COCK},         # Revati
}


def get_paksha(tithi_num: int) -> int:
    """
    Get Paksha from Tithi number.
    
    Args:
        tithi_num: Tithi number 1-30
        
    Returns:
        0 for Shukla Paksha (1-15), 1 for Krishna Paksha (16-30)
    """
    return 0 if tithi_num <= 15 else 1


def get_birth_bird(nakshatra_num: int, tithi_num: int) -> Bird:
    """
    Calculate birth bird based on Moon's nakshatra and tithi.
    
    Args:
        nakshatra_num: Nakshatra number 1-27
        tithi_num: Tithi number 1-30
        
    Returns:
        Bird enum value
    """
    nak_idx = (nakshatra_num - 1) % 27
    paksha = get_paksha(tithi_num)
    return NAKSHATRA_BIRD[nak_idx][paksha]


# =============================================================================
# YAMA (Time Period) CALCULATION
# =============================================================================

def get_yama(hour: int, is_day: bool) -> int:
    """
    Get current Yama (1-5) based on hour.
    
    Day is divided into 5 Yamas (sunrise to sunset)
    Night is divided into 5 Yamas (sunset to sunrise)
    
    Simplified: Each Yama ≈ 2.4 hours (12 hours / 5)
    
    Args:
        hour: Hour of day (0-23)
        is_day: True if daytime (6 AM - 6 PM approx)
        
    Returns:
        Yama number 1-5
    """
    if is_day:
        # Day Yamas: 6-8:24, 8:24-10:48, 10:48-13:12, 13:12-15:36, 15:36-18
        day_minutes = (hour - 6) * 60
        yama = min(5, max(1, (day_minutes // 144) + 1))
    else:
        # Night Yamas: 18-20:24, 20:24-22:48, 22:48-1:12, 1:12-3:36, 3:36-6
        if hour >= 18:
            night_minutes = (hour - 18) * 60
        else:
            night_minutes = (hour + 6) * 60
        yama = min(5, max(1, (night_minutes // 144) + 1))
    
    return yama


def is_daytime(hour: int) -> bool:
    """Check if hour is daytime (6 AM to 6 PM)"""
    return 6 <= hour < 18


# =============================================================================
# ACTIVITY LOOKUP TABLES
# =============================================================================

# Day activity sequence for each bird by weekday
# Format: DAY_ACTIVITY[weekday][bird] = [activity for yama 1-5]
# Weekday: 0=Sunday, 1=Monday, ..., 6=Saturday

DAY_ACTIVITY = {
    # Sunday
    0: {
        Bird.VULTURE: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.OWL: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.CROW: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.COCK: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
        Bird.PEACOCK: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
    },
    # Monday
    1: {
        Bird.VULTURE: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
        Bird.OWL: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.CROW: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.COCK: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.PEACOCK: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
    },
    # Tuesday
    2: {
        Bird.VULTURE: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
        Bird.OWL: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
        Bird.CROW: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.COCK: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.PEACOCK: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
    },
    # Wednesday
    3: {
        Bird.VULTURE: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.OWL: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
        Bird.CROW: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
        Bird.COCK: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.PEACOCK: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
    },
    # Thursday
    4: {
        Bird.VULTURE: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.OWL: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.CROW: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
        Bird.COCK: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
        Bird.PEACOCK: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
    },
    # Friday
    5: {
        Bird.VULTURE: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.OWL: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.CROW: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.COCK: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
        Bird.PEACOCK: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
    },
    # Saturday
    6: {
        Bird.VULTURE: [Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING],
        Bird.OWL: [Activity.RULING, Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING],
        Bird.CROW: [Activity.EATING, Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING],
        Bird.COCK: [Activity.WALKING, Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING],
        Bird.PEACOCK: [Activity.SLEEPING, Activity.DYING, Activity.RULING, Activity.EATING, Activity.WALKING],
    },
}

# Night activities - shifted by 2 positions from day
NIGHT_ACTIVITY = {
    weekday: {
        bird: [activities[(i + 2) % 5] for i in range(5)]
        for bird, activities in birds.items()
    }
    for weekday, birds in DAY_ACTIVITY.items()
}


# =============================================================================
# MAIN CALCULATION FUNCTIONS
# =============================================================================

def get_bird_activity(bird: Bird, weekday: int, yama: int, is_day: bool) -> Activity:
    """
    Get the current activity of a bird.
    
    Args:
        bird: Bird enum value
        weekday: Day of week (0=Sunday to 6=Saturday)
        yama: Yama period (1-5)
        is_day: True for daytime, False for night
        
    Returns:
        Activity enum value
    """
    activity_table = DAY_ACTIVITY if is_day else NIGHT_ACTIVITY
    return activity_table[weekday][bird][yama - 1]


def get_all_bird_activities(weekday: int, yama: int, is_day: bool) -> Dict[Bird, Activity]:
    """
    Get activities of all five birds for current time.
    
    Returns:
        Dict mapping Bird to Activity
    """
    return {
        bird: get_bird_activity(bird, weekday, yama, is_day)
        for bird in Bird
    }


def get_ruling_bird(weekday: int, yama: int, is_day: bool) -> Bird:
    """
    Get the bird that is currently in RULING state.
    
    Returns:
        Bird that is ruling, or None if none found
    """
    for bird in Bird:
        if get_bird_activity(bird, weekday, yama, is_day) == Activity.RULING:
            return bird
    return None


def get_pancha_pakshi(
    birth_nakshatra_num: int,
    birth_tithi_num: int,
    query_datetime: datetime
) -> Dict:
    """
    Complete Pancha Pakshi analysis.
    
    Args:
        birth_nakshatra_num: Birth Moon nakshatra (1-27)
        birth_tithi_num: Birth tithi (1-30)
        query_datetime: Time to check activities
        
    Returns:
        Dict with birth bird, current activity, and predictions
    """
    # Calculate birth bird
    birth_bird = get_birth_bird(birth_nakshatra_num, birth_tithi_num)
    bird_name, bird_tamil = BIRD_NAMES[birth_bird]
    
    # Get current time parameters
    weekday = (query_datetime.weekday() + 1) % 7  # Convert Mon=0 to Sun=0
    hour = query_datetime.hour
    is_day = is_daytime(hour)
    yama = get_yama(hour, is_day)
    
    # Get birth bird's current activity
    current_activity = get_bird_activity(birth_bird, weekday, yama, is_day)
    activity_name, activity_quality, activity_effect = ACTIVITY_INFO[current_activity]
    
    # Get all birds' activities
    all_activities = get_all_bird_activities(weekday, yama, is_day)
    
    # Get ruling bird
    ruling_bird = get_ruling_bird(weekday, yama, is_day)
    ruling_bird_name = BIRD_NAMES[ruling_bird][0] if ruling_bird else "Unknown"
    
    # Calculate favorability score (0-100)
    activity_scores = {
        Activity.RULING: 100,
        Activity.EATING: 75,
        Activity.WALKING: 50,
        Activity.SLEEPING: 25,
        Activity.DYING: 0,
    }
    favorability = activity_scores[current_activity]
    
    # Prediction
    if current_activity == Activity.RULING:
        prediction = "Highly favorable time. Your energy is at peak. Initiate important activities."
    elif current_activity == Activity.EATING:
        prediction = "Good time for gains, nourishment, and accumulation. Favorable for business."
    elif current_activity == Activity.WALKING:
        prediction = "Moderate period. Good for routine activities. Avoid major decisions."
    elif current_activity == Activity.SLEEPING:
        prediction = "Rest period. Avoid starting new ventures. Good for reflection and planning."
    else:  # DYING
        prediction = "Unfavorable period. Avoid important activities. Lay low and wait."
    
    return {
        'birth_bird': {
            'bird': birth_bird,
            'name': bird_name,
            'tamil_name': bird_tamil,
        },
        'query_time': {
            'datetime': query_datetime,
            'weekday': weekday,
            'weekday_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][weekday],
            'yama': yama,
            'is_day': is_day,
            'period': 'Day' if is_day else 'Night',
        },
        'current_activity': {
            'activity': current_activity,
            'name': activity_name,
            'quality': activity_quality,
            'effect': activity_effect,
        },
        'ruling_bird': {
            'name': ruling_bird_name,
            'bird': ruling_bird,
        },
        'favorability': favorability,
        'prediction': prediction,
        'all_birds': {
            BIRD_NAMES[bird][0]: ACTIVITY_INFO[activity][0]
            for bird, activity in all_activities.items()
        }
    }


def get_favorable_periods(
    birth_nakshatra_num: int,
    birth_tithi_num: int,
    date: datetime,
    min_activity: Activity = Activity.EATING
) -> List[Dict]:
    """
    Find favorable periods for a given day.
    
    Args:
        birth_nakshatra_num: Birth Moon nakshatra (1-27)
        birth_tithi_num: Birth tithi (1-30)
        date: Date to check
        min_activity: Minimum acceptable activity level (RULING or EATING)
        
    Returns:
        List of favorable time periods
    """
    birth_bird = get_birth_bird(birth_nakshatra_num, birth_tithi_num)
    weekday = (date.weekday() + 1) % 7
    
    favorable = []
    
    # Check day periods
    for yama in range(1, 6):
        activity = get_bird_activity(birth_bird, weekday, yama, is_day=True)
        if activity <= min_activity:  # Lower enum = better activity
            # Calculate approximate time range
            start_hour = 6 + (yama - 1) * 2.4
            end_hour = start_hour + 2.4
            favorable.append({
                'period': 'Day',
                'yama': yama,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'activity': ACTIVITY_INFO[activity][0],
                'quality': ACTIVITY_INFO[activity][1],
            })
    
    # Check night periods
    for yama in range(1, 6):
        activity = get_bird_activity(birth_bird, weekday, yama, is_day=False)
        if activity <= min_activity:
            start_hour = 18 + (yama - 1) * 2.4
            if start_hour >= 24:
                start_hour -= 24
            end_hour = start_hour + 2.4
            if end_hour >= 24:
                end_hour -= 24
            favorable.append({
                'period': 'Night',
                'yama': yama,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'activity': ACTIVITY_INFO[activity][0],
                'quality': ACTIVITY_INFO[activity][1],
            })
    
    return favorable


def get_daily_summary(
    birth_nakshatra_num: int,
    birth_tithi_num: int,
    date: datetime
) -> Dict:
    """
    Get complete daily Pancha Pakshi summary.
    
    Returns:
        Dict with all 10 yama activities (5 day + 5 night)
    """
    birth_bird = get_birth_bird(birth_nakshatra_num, birth_tithi_num)
    bird_name = BIRD_NAMES[birth_bird][0]
    weekday = (date.weekday() + 1) % 7
    weekday_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][weekday]
    
    day_activities = []
    night_activities = []
    
    for yama in range(1, 6):
        # Day
        day_act = get_bird_activity(birth_bird, weekday, yama, is_day=True)
        day_activities.append({
            'yama': yama,
            'activity': ACTIVITY_INFO[day_act][0],
            'quality': ACTIVITY_INFO[day_act][1],
        })
        
        # Night
        night_act = get_bird_activity(birth_bird, weekday, yama, is_day=False)
        night_activities.append({
            'yama': yama,
            'activity': ACTIVITY_INFO[night_act][0],
            'quality': ACTIVITY_INFO[night_act][1],
        })
    
    # Count favorable periods
    ruling_count = sum(1 for d in day_activities + night_activities if d['activity'] == 'Ruling')
    eating_count = sum(1 for d in day_activities + night_activities if d['activity'] == 'Eating')
    
    return {
        'date': date.date(),
        'weekday': weekday_name,
        'birth_bird': bird_name,
        'day_activities': day_activities,
        'night_activities': night_activities,
        'summary': {
            'ruling_periods': ruling_count,
            'eating_periods': eating_count,
            'favorable_periods': ruling_count + eating_count,
        }
    }
