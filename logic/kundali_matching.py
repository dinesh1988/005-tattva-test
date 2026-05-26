"""
Kundali Matching / Ashtakuta Compatibility Module

Implements the 10-factor Vedic compatibility analysis between two birth charts.
The 8 scored Kutas total a maximum of 36 points, converted to a percentage.

Ported from: Library/Logic/Factory/MatchReportFactory.cs

Factors:
  1. Varna   (1 pt)  - spiritual/ego compatibility
  2. Vasya   (2 pt)  - magnetic control / amenability
  3. Dina    (3 pt)  - day-to-day living
  4. Yoni    (4 pt)  - sexual compatibility
  5. Graha Maitri (5 pt) - mental / happiness compatibility
  6. Gana    (6 pt)  - temperament compatibility
  7. Rasi    (7 pt)  - rasi compatibility
  8. Nadi    (8 pt)  - nervous energy / constitution
  --- (unscored but important) ---
  9. Rajju        - marital longevity
 10. Mahendra     - well-being and prosperity
 11. Stree Deergha - husband's longevity
 12. Vedha Kuta   - hostile nakshatra pairs
 13. Kuja Dosha   - Mars affliction
 14. Bad Constellations - evil nakshatra warnings
 15. Sex Energy   - libido compatibility
"""

from typing import Dict, List, Tuple, Optional
from .consts import Planet
from .calculate import get_planet_longitude, get_lagnam
from .time import AstroTime
from .nakshatra import get_nakshatra, NAKSHATRAS
from .lordship import get_lord_of_sign
from .planet_relations import get_natural_relationship
from .house_queries import get_planet_house, get_planet_sign_num, get_planets_in_house
from .dignity import is_planet_exalted_sign, is_planet_debilitated

# ==================== ENUM-LIKE CONSTANTS ====================

NATURE_GOOD = "Good"
NATURE_BAD = "Bad"
NATURE_NEUTRAL = "Neutral"

# Nakshatra index 0-26 (matches NAKSHATRAS list order)
_NAK_IDX = {name: i for i, name in enumerate(NAKSHATRAS)}

# ==================== NAKSHATRA DATA TABLES ====================

# Nadi (constitution) for each nakshatra (0-based index)
# Vatha=wind, Pitha=bile, Sleshma=phlegm
_NADI = {
    0: "Vatha",   # Ashwini
    1: "Pitha",   # Bharani
    2: "Sleshma", # Krittika
    3: "Sleshma", # Rohini
    4: "Pitha",   # Mrigashira
    5: "Vatha",   # Ardra
    6: "Vatha",   # Punarvasu
    7: "Pitha",   # Pushya
    8: "Sleshma", # Ashlesha
    9: "Sleshma", # Magha
    10: "Pitha",  # Purva Phalguni
    11: "Vatha",  # Uttara Phalguni
    12: "Vatha",  # Hasta
    13: "Pitha",  # Chitra
    14: "Sleshma", # Swati
    15: "Sleshma", # Vishakha
    16: "Pitha",  # Anuradha
    17: "Vatha",  # Jyeshtha
    18: "Vatha",  # Mula
    19: "Pitha",  # Purva Ashadha
    20: "Sleshma", # Uttara Ashadha
    21: "Sleshma", # Shravana
    22: "Pitha",  # Dhanishta
    23: "Vatha",  # Shatabhisha
    24: "Vatha",  # Purva Bhadrapada
    25: "Pitha",  # Uttara Bhadrapada
    26: "Sleshma", # Revati
}

# Gana (temperament) for each nakshatra (0-based index)
# Deva=divine, Manusha=human, Rakshasa=demon
_GANA = {
    0: "Deva",     # Ashwini
    1: "Manusha",  # Bharani
    2: "Rakshasa", # Krittika
    3: "Manusha",  # Rohini
    4: "Deva",     # Mrigashira
    5: "Manusha",  # Ardra
    6: "Deva",     # Punarvasu
    7: "Deva",     # Pushya
    8: "Rakshasa", # Ashlesha
    9: "Rakshasa", # Magha
    10: "Manusha", # Purva Phalguni
    11: "Manusha", # Uttara Phalguni
    12: "Deva",    # Hasta
    13: "Rakshasa", # Chitra
    14: "Deva",    # Swati
    15: "Rakshasa", # Vishakha
    16: "Deva",    # Anuradha
    17: "Rakshasa", # Jyeshtha
    18: "Rakshasa", # Mula
    19: "Manusha", # Purva Ashadha
    20: "Manusha", # Uttara Ashadha
    21: "Deva",    # Shravana
    22: "Rakshasa", # Dhanishta
    23: "Rakshasa", # Shatabhisha
    24: "Manusha", # Purva Bhadrapada
    25: "Manusha", # Uttara Bhadrapada
    26: "Deva",    # Revati
}

# Varna (spiritual grade / caste) for each rasi (0-based, 0=Aries)
# BrahminScholar=4, KshatriyaWarrior=3, VaisyaWorkmen=2, SudraServant=1
_VARNA_RASI = {
    0: 3,   # Aries      - Kshatriya
    1: 2,   # Taurus     - Vaisya
    2: 4,   # Gemini     - Brahmin
    3: 1,   # Cancer     - Sudra
    4: 3,   # Leo        - Kshatriya
    5: 4,   # Virgo      - Brahmin
    6: 2,   # Libra      - Vaisya
    7: 3,   # Scorpio    - Kshatriya
    8: 4,   # Sagittarius - Brahmin
    9: 1,   # Capricorn  - Sudra
    10: 1,  # Aquarius   - Sudra
    11: 4,  # Pisces     - Brahmin
}
_VARNA_NAMES = {4: "Brahmin", 3: "Kshatriya", 2: "Vaisya", 1: "Sudra"}

# Yoni (animal) for each nakshatra (0-based)
# (animal_name, gender)  — gender refers to the nakshatra's own gender
# Animal index matches the KP compatibility matrix (1-based: Horse=1..Lion=14)
_YONI = {
    0:  ("Horse",    "Male"),    # Ashwini
    1:  ("Elephant", "Female"),  # Bharani
    2:  ("Sheep",    "Female"),  # Krittika
    3:  ("Serpent",  "Male"),    # Rohini
    4:  ("Serpent",  "Female"),  # Mrigashira
    5:  ("Dog",      "Female"),  # Ardra
    6:  ("Cat",      "Female"),  # Punarvasu
    7:  ("Sheep",    "Male"),    # Pushya
    8:  ("Cat",      "Male"),    # Ashlesha
    9:  ("Rat",      "Male"),    # Magha
    10: ("Rat",      "Female"),  # Purva Phalguni
    11: ("Cow",      "Female"),  # Uttara Phalguni
    12: ("Buffalo",  "Male"),    # Hasta
    13: ("Tiger",    "Female"),  # Chitra
    14: ("Buffalo",  "Female"),  # Swati
    15: ("Tiger",    "Male"),    # Vishakha
    16: ("Hare",     "Female"),  # Anuradha
    17: ("Hare",     "Male"),    # Jyeshtha
    18: ("Dog",      "Male"),    # Mula
    19: ("Monkey",   "Male"),    # Purva Ashadha
    20: ("Mongoose", "Male"),    # Uttara Ashadha
    21: ("Monkey",   "Female"),  # Shravana
    22: ("Lion",     "Female"),  # Dhanishta
    23: ("Horse",    "Female"),  # Shatabhisha
    24: ("Lion",     "Male"),    # Purva Bhadrapada
    25: ("Cow",      "Male"),    # Uttara Bhadrapada
    26: ("Elephant", "Male"),    # Revati
}

# Yoni animal compatibility matrix (1-based indexes matching order below)
# Horse=1, Elephant=2, Sheep=3, Serpent=4, Dog=5, Cat=6, Rat=7, Cow=8,
# Buffalo=9, Tiger=10, Hare=11, Monkey=12, Mongoose=13, Lion=14
_ANIMAL_IDX = {
    "Horse": 1, "Elephant": 2, "Sheep": 3, "Serpent": 4, "Dog": 5,
    "Cat": 6, "Rat": 7, "Cow": 8, "Buffalo": 9, "Tiger": 10,
    "Hare": 11, "Monkey": 12, "Mongoose": 13, "Lion": 14,
}
# 15x15 matrix (index 0 unused)
_YONI_COMPAT = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,4,2,2,3,2,2,2,1,0,1,3,3,2,1],  # Horse
    [0,2,4,3,3,2,2,2,2,3,1,2,3,2,0],  # Elephant
    [0,2,3,4,2,1,2,1,3,3,1,2,0,3,1],  # Sheep
    [0,3,3,2,4,2,1,1,1,1,2,2,2,0,2],  # Serpent
    [0,2,2,1,2,4,2,1,2,2,1,0,2,1,1],  # Dog
    [0,2,2,2,1,2,4,0,2,2,1,3,3,2,1],  # Cat
    [0,2,2,1,1,1,0,4,2,2,2,2,2,1,2],  # Rat
    [0,1,2,3,1,2,2,2,4,3,0,3,2,2,1],  # Cow
    [0,0,3,3,1,2,2,2,3,4,1,2,2,2,1],  # Buffalo
    [0,1,1,1,2,1,1,2,0,1,4,1,1,2,1],  # Tiger
    [0,1,2,2,2,0,3,2,3,2,1,4,2,2,1],  # Hare
    [0,3,3,0,2,2,3,2,2,2,1,2,4,3,2],  # Monkey
    [0,2,2,3,0,1,2,1,2,2,2,2,3,4,2],  # Mongoose
    [0,1,0,1,2,1,1,2,1,2,1,1,2,2,4],  # Lion
]

# Rajju groups (marital body) for each nakshatra (0-based)
_RAJJU = {
    0: "Pada",   # Ashwini
    1: "Kati",   # Bharani
    2: "Udara",  # Krittika
    3: "Kanta",  # Rohini
    4: "Sira",   # Mrigashira
    5: "Kanta",  # Ardra
    6: "Udara",  # Punarvasu
    7: "Kati",   # Pushya
    8: "Pada",   # Ashlesha
    9: "Pada",   # Magha
    10: "Kati",  # Purva Phalguni
    11: "Udara", # Uttara Phalguni
    12: "Kanta", # Hasta
    13: "Sira",  # Chitra
    14: "Kanta", # Swati
    15: "Udara", # Vishakha
    16: "Kati",  # Anuradha
    17: "Pada",  # Jyeshtha
    18: "Pada",  # Mula
    19: "Kati",  # Purva Ashadha
    20: "Udara", # Uttara Ashadha
    21: "Kanta", # Shravana
    22: "Sira",  # Dhanishta
    23: "Kanta", # Shatabhisha
    24: "Udara", # Purva Bhadrapada
    25: "Kati",  # Uttara Bhadrapada
    26: "Pada",  # Revati
}

# Vasya (who controls whom) — for each sign (0=Aries) list of signs it controls
_VASYA = {
    0:  [4, 7],    # Aries   controls Leo, Scorpio
    1:  [3, 5],    # Taurus  controls Cancer, Libra
    2:  [8],       # Gemini  controls Virgo
    3:  [7, 8],    # Cancer  controls Scorpio, Sagittarius
    4:  [5],       # Leo     controls Libra
    5:  [11, 2],   # Virgo   controls Pisces, Gemini
    6:  [9, 8],    # Libra   controls Capricorn, Virgo
    7:  [3],       # Scorpio controls Cancer
    8:  [11],      # Sagittarius controls Pisces
    9:  [0, 10],   # Capricorn controls Aries, Aquarius
    10: [0],       # Aquarius controls Aries
    11: [9],       # Pisces  controls Capricorn
}

# Vedha (hostile nakshatra pairs) — 0-based indexes
_VEDHA_PAIRS = [
    (0, 17),   # Ashwini – Jyeshtha
    (1, 16),   # Bharani – Anuradha
    (2, 15),   # Krittika – Vishakha
    (3, 14),   # Rohini – Swati
    (5, 21),   # Ardra – Shravana
    (6, 20),   # Punarvasu – Uttara Ashadha
    (7, 19),   # Pushya – Purva Ashadha
    (8, 18),   # Ashlesha – Mula
    (9, 26),   # Magha – Revati
    (10, 25),  # Purva Phalguni – Uttara Bhadrapada
    (11, 24),  # Uttara Phalguni – Purva Bhadrapada
    (12, 23),  # Hasta – Shatabhisha
    (4, 22),   # Mrigashira – Dhanishta
]

# ==================== HELPER FUNCTIONS ====================

def _nakshatra_idx(time: AstroTime) -> Tuple[int, float]:
    """Returns 0-based nakshatra index and percentage traversed for Moon."""
    moon_long = get_planet_longitude(Planet.Moon, time)
    _, nak_num, pct, _ = get_nakshatra(moon_long)
    return nak_num - 1, pct  # convert to 0-based


def _moon_sign_idx(time: AstroTime) -> int:
    """Returns 0-based sign index for Moon."""
    return get_planet_sign_num(Planet.Moon, time) - 1  # convert to 0-based


def _count_nak_to_nak(from_idx: int, to_idx: int) -> int:
    """Count nakshatras from -> to (inclusive, wraps at 27)."""
    if to_idx >= from_idx:
        return to_idx - from_idx + 1
    return (27 - from_idx) + to_idx + 1


def _count_sign_to_sign(from_idx: int, to_idx: int) -> int:
    """Count signs from -> to (inclusive, 1-12, wraps at 12)."""
    if to_idx >= from_idx:
        return to_idx - from_idx + 1
    return (12 - from_idx) + to_idx + 1


def _lagna_sign_idx(time: AstroTime) -> int:
    """Returns 0-based lagna (ascendant) sign index."""
    lagna_long = get_lagnam(time)
    return int(lagna_long / 30) % 12


def _is_vedha_pair(a: int, b: int) -> bool:
    """Check if two nakshatra indexes (0-based) form a hostile Vedha pair."""
    for x, y in _VEDHA_PAIRS:
        if (a == x and b == y) or (a == y and b == x):
            return True
    return False


# ==================== INDIVIDUAL KUTA CALCULATIONS ====================

def _calc_nadi(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    male_nadi = _NADI[male_nak]
    female_nadi = _NADI[female_nak]

    if male_nadi != female_nadi:
        return {
            "name": "Nadi Kuta",
            "description": "nervous energy compatibility (important)",
            "points": 8, "max_points": 8,
            "nature": NATURE_GOOD,
            "info": "agreement between the couple will be good",
            "male_info": male_nadi,
            "female_info": female_nadi,
        }
    else:
        # Exception: same Janma lord or friends
        male_sign_idx = _moon_sign_idx(male_time)
        female_sign_idx = _moon_sign_idx(female_time)
        male_lord = get_lord_of_sign(male_sign_idx + 1)
        female_lord = get_lord_of_sign(female_sign_idx + 1)
        relation = get_natural_relationship(male_lord, female_lord)
        same_lord = male_lord == female_lord
        is_friend = relation in ("BestFriend", "Friend")
        if same_lord or is_friend:
            return {
                "name": "Nadi Kuta", "description": "nervous energy compatibility (important)",
                "points": 0, "max_points": 8, "nature": NATURE_NEUTRAL,
                "info": "bad, but neutralized by friendly Janma Rasi lord",
                "male_info": male_nadi, "female_info": female_nadi,
            }
        return {
            "name": "Nadi Kuta", "description": "nervous energy compatibility (important)",
            "points": 0, "max_points": 8, "nature": NATURE_BAD,
            "info": "same constitution — should belong to different type",
            "male_info": male_nadi, "female_info": female_nadi,
        }


def _calc_gana(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    male_gana = _GANA[male_nak]
    female_gana = _GANA[female_nak]

    male_to_female = _count_nak_to_nak(male_nak, female_nak)
    man_is_manusha_deva = male_gana in ("Deva", "Manusha")
    girl_is_rakshasa = female_gana == "Rakshasa"
    female_is_manusha_deva = female_gana in ("Deva", "Manusha")
    male_is_rakshasa = male_gana == "Rakshasa"

    if male_gana == female_gana:
        nature, info = NATURE_GOOD, f"both are {female_gana} Gana"
    elif man_is_manusha_deva and girl_is_rakshasa:
        nature, info = NATURE_BAD, "Manusha/Deva boy cannot marry a Rakshasa girl"
    elif female_is_manusha_deva and male_is_rakshasa:
        nature, info = NATURE_BAD, "Rakshasa boy and Deva/Manusha girl — passable but not ideal"
    else:
        nature, info = NATURE_BAD, "quarrels and disharmony"

    # Exception: female star > 14 from male
    if male_to_female > 14 and nature == NATURE_BAD:
        nature, info = NATURE_NEUTRAL, "evil ignored — female star is more than 14th from male's"

    return {
        "name": "Gana Kuta", "description": "temperament and character compatibility",
        "points": 6 if nature == NATURE_GOOD else 0, "max_points": 6,
        "nature": nature, "info": info,
        "male_info": male_gana, "female_info": female_gana,
    }


def _calc_varna(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_sign = _moon_sign_idx(male_time)
    female_sign = _moon_sign_idx(female_time)
    male_grade = _VARNA_RASI[male_sign]
    female_grade = _VARNA_RASI[female_sign]

    if female_grade > male_grade:
        nature, info = NATURE_BAD, "girl has higher Varna — not a good match for boy of lesser development"
    else:
        nature, info = NATURE_GOOD, "boy higher or equal Varna is good"

    return {
        "name": "Varna", "description": "spiritual/ego compatibility",
        "points": 1 if nature == NATURE_GOOD else 0, "max_points": 1,
        "nature": nature, "info": info,
        "male_info": _VARNA_NAMES[male_grade], "female_info": _VARNA_NAMES[female_grade],
    }


def _calc_yoni(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    male_animal, male_gender = _YONI[male_nak]
    female_animal, female_gender = _YONI[female_nak]

    ma = _ANIMAL_IDX[male_animal]
    fa = _ANIMAL_IDX[female_animal]
    grade = _YONI_COMPAT[ma][fa]

    if grade <= 2:
        nature, info = NATURE_BAD, "hostile yoni pair — should be avoided"
    else:
        same_animal = male_animal == female_animal
        same_gender = male_gender == female_gender
        both_male = male_gender == "Male" and female_gender == "Male"
        both_female = male_gender == "Female" and female_gender == "Female"
        is_friendly = grade == 3

        if same_animal and not same_gender:
            nature, info = NATURE_GOOD, "same yoni, opposite gender — favourable to fullest extent"
        elif same_animal and not both_male:
            nature, info = NATURE_GOOD, "same yoni, same gender (not both male) — better than normal"
        elif is_friendly and both_female:
            nature, info = NATURE_GOOD, "friendly yoni, both female — fair happiness and agreement"
        elif is_friendly and male_gender != female_gender:
            nature, info = NATURE_GOOD, "friendly yoni, opposite genders — passable"
        elif both_male:
            nature, info = NATURE_BAD, "both male constellations — constant quarrels"
        else:
            nature, info = NATURE_GOOD, "compatible yoni"

    return {
        "name": "Yoni Kuta", "description": "sex compatibility",
        "points": 4 if nature == NATURE_GOOD else 0, "max_points": 4,
        "nature": nature, "info": info,
        "male_info": f"{male_animal} ({male_gender})", "female_info": f"{female_animal} ({female_gender})",
    }


def _calc_graha_maitri(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_sign = _moon_sign_idx(male_time)
    female_sign = _moon_sign_idx(female_time)
    male_lord = get_lord_of_sign(male_sign + 1)
    female_lord = get_lord_of_sign(female_sign + 1)
    m_to_f = get_natural_relationship(male_lord, female_lord)
    f_to_m = get_natural_relationship(female_lord, male_lord)

    # When both lords are the same planet, GrahaMaitri obtains in full (upstream fix Jan 4 2026)
    if male_lord == female_lord:
        return {
            "name": "Graha Maitri", "description": "happiness and mental compatibility (important)",
            "points": 5, "max_points": 5,
            "nature": NATURE_GOOD, "info": "Both lords are the same planet — Rasi Kuta obtains in full",
            "male_info": f"{male_lord.name} (SamePlanet)", "female_info": f"{female_lord.name} (SamePlanet)",
        }

    is_m_friend = m_to_f in ("BestFriend", "Friend")
    is_f_friend = f_to_m in ("BestFriend", "Friend")
    is_m_enemy  = m_to_f in ("BitterEnemy", "Enemy")
    is_f_enemy  = f_to_m in ("BitterEnemy", "Enemy")
    is_m_neutral = m_to_f == "Neutral"
    is_f_neutral = f_to_m == "Neutral"

    if is_m_friend and is_f_friend:
        nature, info = NATURE_GOOD, "Rasi Kuta obtains in full — both lords are friends"
    elif (is_m_friend or is_f_friend) and (is_m_neutral or is_f_neutral):
        nature, info = NATURE_GOOD, "one is friend, other is neutral — passable"
    elif is_m_neutral and is_f_neutral:
        nature, info = NATURE_BAD, "both neutral — Rasi Kuta is very ordinary"
    elif is_m_enemy and is_f_enemy:
        nature, info = NATURE_BAD, "both are enemies — alliance must be avoided"
    else:
        nature, info = NATURE_BAD, "no good connection between these horoscopes"

    return {
        "name": "Graha Maitri", "description": "happiness and mental compatibility (important)",
        "points": 5 if nature == NATURE_GOOD else 0, "max_points": 5,
        "nature": nature, "info": info,
        "male_info": f"{male_lord.name} ({m_to_f})", "female_info": f"{female_lord.name} ({f_to_m})",
    }


def _calc_rasi(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_sign = _moon_sign_idx(male_time)    # 0-based
    female_sign = _moon_sign_idx(female_time)

    f_to_m = _count_sign_to_sign(female_sign, male_sign)
    m_to_f = _count_sign_to_sign(male_sign, female_sign)

    nature = NATURE_NEUTRAL
    info = ""

    if f_to_m == 2 or m_to_f == 12:
        nature, info = NATURE_BAD, "evil results will follow"
    if f_to_m == 12 or m_to_f == 2:
        nature, info = NATURE_GOOD, "longevity for the couple"
    if f_to_m == 3:
        nature, info = NATURE_BAD, "misery and sorrow"
    if m_to_f == 3:
        nature, info = NATURE_GOOD, "happiness"
    if f_to_m == 4:
        nature, info = NATURE_BAD, "great poverty"
    if m_to_f == 4:
        nature, info = NATURE_GOOD, "great wealth"
    if f_to_m == 5:
        nature, info = NATURE_BAD, "unhappiness"
    if m_to_f == 5:
        nature, info = NATURE_GOOD, "enjoyment and prosperity"
    if m_to_f == 7 and f_to_m == 7:
        nature, info = NATURE_GOOD, "health, agreement and happiness"
    if f_to_m == 6:
        nature, info = NATURE_BAD, "loss of children"
    if m_to_f == 6:
        nature, info = NATURE_GOOD, "progeny will prosper"

    # Same Janma Rasi
    if male_sign == female_sign:
        male_nak, _ = _nakshatra_idx(male_time)
        female_nak, _ = _nakshatra_idx(female_time)
        if male_nak < female_nak:
            nature, info = NATURE_GOOD, "male star precedes female — marriage proves happy"
        elif female_nak < male_nak:
            nature, info = NATURE_BAD, "female star precedes male — alliance should be rejected"
        else:
            nature, info = NATURE_BAD, "same nakshatra — alliance should be rejected"

    # Exception: same lord or lords are friends cancels bad
    if nature == NATURE_BAD:
        ml = get_lord_of_sign(male_sign + 1)
        fl = get_lord_of_sign(female_sign + 1)
        if ml == fl or get_natural_relationship(ml, fl) in ("BestFriend", "Friend"):
            nature, info = NATURE_NEUTRAL, "bad neutralized by friendly Janma Rasi lords"

    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    return {
        "name": "Rasi Kuta", "description": "rasi compatibility",
        "points": 7 if nature == NATURE_GOOD else 0, "max_points": 7,
        "nature": nature, "info": info if info else "neutral rasi placement",
        "male_info": SIGNS[male_sign], "female_info": SIGNS[female_sign],
    }


def _calc_dina(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """Dina Kuta — count male nak from female nak, divide by 9, remainder 2/4/6/8/0 is good."""
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    count = _count_nak_to_nak(female_nak, male_nak)
    remainder = count % 9
    good = remainder in (0, 2, 4, 6, 8)
    return {
        "name": "Dina Kuta", "description": "day-to-day living compatibility",
        "points": 3 if good else 0, "max_points": 3,
        "nature": NATURE_GOOD if good else NATURE_BAD,
        "info": f"count {count}, remainder {remainder} — {'favourable' if good else 'unfavourable'}",
        "male_info": NAKSHATRAS[male_nak], "female_info": NAKSHATRAS[female_nak],
    }


def _calc_vasya(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_sign = _moon_sign_idx(male_time)
    female_sign = _moon_sign_idx(female_time)
    male_controls_female = female_sign in _VASYA.get(male_sign, [])
    female_controls_male = male_sign in _VASYA.get(female_sign, [])
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    if male_controls_female:
        nature, info = NATURE_GOOD, "male controls female"
    elif female_controls_male:
        nature, info = NATURE_GOOD, "female controls male"
    else:
        nature, info = NATURE_BAD, "neither controls the other"
    return {
        "name": "Vasya Kuta", "description": "degree of magnetic control",
        "points": 2 if nature == NATURE_GOOD else 0, "max_points": 2,
        "nature": nature, "info": info,
        "male_info": SIGNS[male_sign], "female_info": SIGNS[female_sign],
    }


def _calc_mahendra(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """Male nak counted from female nak should be 4,7,10,13,16,19,22,25."""
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    count = _count_nak_to_nak(female_nak, male_nak)
    good = count in (4, 7, 10, 13, 16, 19, 22, 25)
    return {
        "name": "Mahendra", "description": "well-being and longevity",
        "points": 0, "max_points": 0,  # unscored
        "nature": NATURE_GOOD if good else NATURE_BAD,
        "info": f"count {count} — {'promotes well-being and longevity' if good else 'no longevity benefit'}",
        "male_info": NAKSHATRAS[male_nak], "female_info": NAKSHATRAS[female_nak],
    }


def _calc_stree_deergha(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """Male nak should be >= 9 from female nak."""
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    count = _count_nak_to_nak(female_nak, male_nak)
    good = count >= 9
    return {
        "name": "Stree Deergha", "description": "husband's well-being and longevity",
        "points": 0, "max_points": 0,  # unscored
        "nature": NATURE_GOOD if good else NATURE_BAD,
        "info": f"constellation count is {count} — {'favourable (>= 9)' if good else 'unfavourable (< 9)'}",
        "male_info": NAKSHATRAS[male_nak], "female_info": NAKSHATRAS[female_nak],
    }


def _calc_rajju(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    male_group = _RAJJU[male_nak]
    female_group = _RAJJU[female_nak]

    _RAJJU_EFFECTS = {
        "Sira":  "Sira (head) — husband's death is likely",
        "Kanta": "Kanta (neck) — the wife may die",
        "Udara": "Udara (stomach) — the children may die",
        "Kati":  "Kati (waist) — poverty may ensue",
        "Pada":  "Pada (foot) — the couple may always be wandering",
    }

    if male_group == female_group:
        nature, info = NATURE_BAD, _RAJJU_EFFECTS.get(male_group, "same Rajju group")
    else:
        nature, info = NATURE_GOOD, "both constellations are in different Rajju groups"

    return {
        "name": "Rajju", "description": "strength and duration of married life (important)",
        "points": 0, "max_points": 0,  # unscored but critical
        "nature": nature, "info": info,
        "male_info": male_group, "female_info": female_group,
    }


def _calc_vedha(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_nak, _ = _nakshatra_idx(male_time)
    female_nak, _ = _nakshatra_idx(female_time)
    is_hostile = _is_vedha_pair(male_nak, female_nak)
    return {
        "name": "Vedha Kuta", "description": "hostile nakshatra pair check",
        "points": 0, "max_points": 0,
        "nature": NATURE_BAD if is_hostile else NATURE_GOOD,
        "info": "hostile constellation pair found — avoid" if is_hostile else "no hostile nakshatra pair",
        "male_info": NAKSHATRAS[male_nak], "female_info": NAKSHATRAS[female_nak],
    }


def _calc_kuja_dosha(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """Mangal / Kuja Dosha — checks Mars, Saturn, Rahu, Ketu, Sun in houses 2,4,7,8,12."""
    def _dosha_score(time: AstroTime) -> float:
        DOSA_PLANETS = [Planet.Mars, Planet.Saturn, Planet.Rahu, Planet.Ketu, Planet.Sun]
        DOSA_HOUSES_78 = {7, 8}
        DOSA_HOUSES_2412 = {2, 4, 12}
        total = 0.0
        for planet in DOSA_PLANETS:
            house = get_planet_house(planet, time)
            sign_num = get_planet_sign_num(planet, time)
            sign_idx = sign_num - 1

            in_78   = house in DOSA_HOUSES_78
            in_2412 = house in DOSA_HOUSES_2412
            if not in_78 and not in_2412:
                continue

            is_mars = planet == Planet.Mars
            is_saturn_rahu_ketu = planet in (Planet.Saturn, Planet.Rahu, Planet.Ketu)
            is_sun = planet == Planet.Sun

            # Mars exceptions that cancel dosha
            if is_mars:
                if house == 2 and sign_idx in (2, 5):  # Gemini, Virgo
                    continue
                if house == 12 and sign_idx in (1, 5):  # Taurus, Libra
                    continue
                if house == 4 and sign_idx in (0, 7):   # Aries, Scorpio
                    continue
                if house == 7 and sign_idx in (9, 3):   # Capricorn, Cancer
                    continue
                if house == 8 and sign_idx in (8, 11):  # Sagittarius, Pisces
                    continue
                if sign_idx in (10, 4):                 # Aquarius, Leo
                    continue

            exalted = is_planet_exalted_sign(planet, time)
            debilitated = is_planet_debilitated(planet, time)

            # Simplified relationship via dignity
            if debilitated:    score_mult = 1.0
            elif exalted:      score_mult = 0.5
            else:              score_mult = 0.8  # neutral/friendly approximation

            if in_78:
                base = 100 if is_mars else (75 if is_saturn_rahu_ketu else 50)
            else:
                base = 50  if is_mars else (37.5 if is_saturn_rahu_ketu else 25)

            total += base * score_mult

        return total

    m_score = _dosha_score(male_time)
    f_score = _dosha_score(female_time)
    diff = abs(m_score - f_score)
    threshold = 5

    if diff <= threshold:
        nature = NATURE_GOOD
        info = "dosha in both charts is equal or nearly so — good match"
    elif f_score > m_score:
        nature = NATURE_BAD
        info = "charts cannot be matched — female chart has more dosha"
    else:
        exceed_pct = (m_score - f_score) / max(f_score, 1) * 100
        if exceed_pct < 25:
            nature = NATURE_GOOD
            info = "passable — male dosha exceeds female by less than 25%"
        else:
            nature = NATURE_BAD
            info = "charts cannot be matched — male dosha exceeds female by more than 25%"

    return {
        "name": "Kuja Dosha", "description": "Mars affliction — may affect spouse's health/longevity",
        "points": 0, "max_points": 0,
        "nature": nature, "info": info,
        "male_info": f"{m_score:.1f}", "female_info": f"{f_score:.1f}",
    }


def _calc_bad_constellations(male_time: AstroTime, female_time: AstroTime) -> Dict:
    male_moon = get_planet_longitude(Planet.Moon, male_time)
    female_moon = get_planet_longitude(Planet.Moon, female_time)
    _, male_nak, male_pct, male_pada = get_nakshatra(male_moon)
    _, female_nak, female_pct, female_pada = get_nakshatra(female_moon)
    m_name = NAKSHATRAS[male_nak - 1]
    f_name = NAKSHATRAS[female_nak - 1]

    issues = []
    # Moola 1st pada for either
    if (m_name == "Mula" and male_pada == 1) or (f_name == "Mula" and female_pada == 1):
        issues.append("Mula 1st pada — may cause death of father-in-law")
    # Ashlesha 1st pada for female
    if f_name == "Ashlesha" and female_pada == 1:
        issues.append("Ashlesha 1st pada (female) — evil to husband's mother")
    # Jyeshtha 1st pada for female
    if f_name == "Jyeshtha" and female_pada == 1:
        issues.append("Jyeshtha 1st pada (female) — evil to husband's elder brother")
    # Vishakha 4th pada for female
    if f_name == "Vishakha" and female_pada == 4:
        issues.append("Vishakha 4th pada (female) — evil to husband's younger brother")

    if issues:
        return {
            "name": "Bad Constellations", "description": "checks for inauspicious nakshatra placements",
            "points": 0, "max_points": 0, "nature": NATURE_BAD,
            "info": "; ".join(issues),
            "male_info": f"{m_name} pada {male_pada}", "female_info": f"{f_name} pada {female_pada}",
        }
    return {
        "name": "Bad Constellations", "description": "checks for inauspicious nakshatra placements",
        "points": 0, "max_points": 0, "nature": NATURE_GOOD,
        "info": "no evil nakshatra placement found",
        "male_info": f"{m_name} pada {male_pada}", "female_info": f"{f_name} pada {female_pada}",
    }


def _calc_sex_energy(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """Mars or Venus in 7th = strong sex; Mercury or Jupiter in 7th = under-sexed."""
    def _strong_sex(time: AstroTime) -> bool:
        pl7 = get_planets_in_house(7, time)
        return Planet.Mars in pl7 or Planet.Venus in pl7

    def _under_sex(time: AstroTime) -> bool:
        pl7 = get_planets_in_house(7, time)
        return Planet.Mercury in pl7 or Planet.Jupiter in pl7

    m_strong = _strong_sex(male_time)
    f_strong = _strong_sex(female_time)
    m_under  = _under_sex(male_time)
    f_under  = _under_sex(female_time)

    m_label = "Strong Sex" if m_strong else ("Under-Sexed" if m_under else "Normal")
    f_label = "Strong Sex" if f_strong else ("Under-Sexed" if f_under else "Normal")

    if m_strong and f_strong:
        nature, info = NATURE_GOOD, "both horoscopes have Mars/Venus in 7th (strong sex)"
    elif m_under and f_under:
        nature, info = NATURE_GOOD, "both horoscopes have Mercury/Jupiter in 7th (under-sexed)"
    elif m_under and f_strong:
        nature, info = NATURE_BAD, "male under-sexed, female strong sex — incompatible"
    elif m_strong and f_under:
        nature, info = NATURE_BAD, "male strong sex, female under-sexed — incompatible"
    else:
        nature, info = NATURE_NEUTRAL, "no strong sex indicators in 7th house"

    return {
        "name": "Sex Energy", "description": "sexual compatibility based on 7th house planets",
        "points": 0, "max_points": 0,
        "nature": nature, "info": info,
        "male_info": m_label, "female_info": f_label,
    }


# ==================== EXCEPTION RULES ====================

def _apply_exceptions(factors: List[Dict]) -> List[Dict]:
    """Apply C# exception rules that can neutralize bad predictions."""
    by_name = {f["name"]: f for f in factors}

    graha_good = by_name.get("Graha Maitri", {}).get("nature") == NATURE_GOOD
    rasi_good  = by_name.get("Rasi Kuta",    {}).get("nature") == NATURE_GOOD
    dina_good  = by_name.get("Dina Kuta",    {}).get("nature") == NATURE_GOOD
    mahendra_good = by_name.get("Mahendra",  {}).get("nature") == NATURE_GOOD
    rajju_good = by_name.get("Rajju",        {}).get("nature") == NATURE_GOOD

    result = []
    for f in factors:
        f = dict(f)  # shallow copy
        # 1. Stree Deergha bad neutralized if Rasi Kuta + Graha Maitri are good
        if f["name"] == "Stree Deergha" and f["nature"] == NATURE_BAD:
            if rasi_good and graha_good:
                f["nature"] = NATURE_NEUTRAL
                f["info"] = "bad Stree Deergha neutralized by good Rasi Kuta and Graha Maitri"
        # 2. Rajju bad neutralized if Graha Maitri + Rasi + Dina + Mahendra are good
        if f["name"] == "Rajju" and f["nature"] == NATURE_BAD:
            if graha_good and rasi_good and dina_good and mahendra_good:
                f["nature"] = NATURE_NEUTRAL
                f["info"] = "bad Rajju neutralized by good Graha Maitri, Rasi, Dina, and Mahendra"
        # 3. Nadi bad neutralized if Rasi Kuta + Rajju are good
        if f["name"] == "Nadi Kuta" and f["nature"] == NATURE_BAD:
            if rasi_good and rajju_good:
                f["nature"] = NATURE_NEUTRAL
                f["info"] = "bad Nadi neutralized by good Rasi Kuta and Rajju"
        result.append(f)
    return result


# ==================== SCORE SUMMARY ====================

def _score_summary(pct: float) -> Dict:
    if pct >= 75:
        return {"heart_icon": "❤️", "score_color": "green", "score_summary": "Excellent match"}
    elif pct >= 60:
        return {"heart_icon": "🧡", "score_color": "orange", "score_summary": "Good match"}
    elif pct >= 45:
        return {"heart_icon": "💛", "score_color": "yellow", "score_summary": "Average match — needs consideration"}
    else:
        return {"heart_icon": "💔", "score_color": "red", "score_summary": "Below average — careful consideration needed"}


# ==================== MAIN PUBLIC API ====================

def get_kundali_matching(male_time: AstroTime, female_time: AstroTime) -> Dict:
    """
    Calculate Ashtakuta compatibility between male and female birth charts.

    Parameters
    ----------
    male_time : AstroTime  — birth data for the male
    female_time : AstroTime — birth data for the female

    Returns
    -------
    dict with keys:
      - factors       : list of individual kuta results
      - raw_points    : total scored points (out of 36)
      - kuta_score    : percentage score (0–100, rounded to nearest 5)
      - summary       : { heart_icon, score_color, score_summary }
      - embeddings    : list[float] for ML use
    """
    calculators = [
        _calc_graha_maitri,
        _calc_rajju,
        _calc_nadi,
        _calc_vasya,
        _calc_dina,
        _calc_gana,
        _calc_mahendra,
        _calc_stree_deergha,
        _calc_rasi,
        _calc_vedha,
        _calc_varna,
        _calc_yoni,
        _calc_kuja_dosha,
        _calc_bad_constellations,
        _calc_sex_energy,
    ]

    factors = []
    for calc in calculators:
        try:
            factors.append(calc(male_time, female_time))
        except Exception as e:
            factors.append({
                "name": calc.__name__.replace("_calc_", ""),
                "description": "",
                "points": 0, "max_points": 0,
                "nature": NATURE_NEUTRAL,
                "info": f"Calculation error: {e}",
                "male_info": "", "female_info": "",
            })

    factors = _apply_exceptions(factors)

    # Count points (only scored kutas, only if Good)
    SCORED = {
        "Dina Kuta": 3, "Gana Kuta": 6, "Nadi Kuta": 8,
        "Rasi Kuta": 7, "Graha Maitri": 5, "Vasya Kuta": 2,
        "Varna": 1, "Yoni Kuta": 4,
    }
    raw_points = sum(
        SCORED[f["name"]] for f in factors
        if f["name"] in SCORED and f["nature"] == NATURE_GOOD
    )
    raw_pct = (raw_points / 36.0) * 100.0
    kuta_score = round(raw_pct / 5.0) * 5  # round to nearest 5

    # Embeddings (same order as C# CalculateEmbeddings)
    factor_map = {f["name"]: f for f in factors}
    embeddings = [
        SCORED["Dina Kuta"]    if factor_map.get("Dina Kuta",    {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Gana Kuta"]    if factor_map.get("Gana Kuta",    {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Nadi Kuta"]    if factor_map.get("Nadi Kuta",    {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Rasi Kuta"]    if factor_map.get("Rasi Kuta",    {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Graha Maitri"] if factor_map.get("Graha Maitri", {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Vasya Kuta"]   if factor_map.get("Vasya Kuta",   {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Varna"]        if factor_map.get("Varna",        {}).get("nature") == NATURE_GOOD else 0.0,
        SCORED["Yoni Kuta"]    if factor_map.get("Yoni Kuta",    {}).get("nature") == NATURE_GOOD else 0.0,
    ]

    return {
        "factors": factors,
        "raw_points": raw_points,
        "kuta_score": kuta_score,
        "summary": _score_summary(kuta_score),
        "embeddings": embeddings,
    }
