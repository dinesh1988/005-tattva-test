# VedAstroPy Development Roadmap

> Feature implementation task list comparing VedAstro C# Library capabilities

**Last Updated:** January 25, 2026  
**Current Version:** 0.6.0 (18 modules implemented, 21 yogas operational - 22% complete)

---

## ✅ Completed Features

| # | Module | Features | Status |
|---|--------|----------|--------|
| 1 | `calculate.py` | Planet longitudes (SwissEph), Lagnam | ✅ Done |
| 2 | `nakshatra.py` | 27 Nakshatras, Pada, Tara Bala (9 taras) | ✅ Done |
| 3 | `dasa.py` | Vimshottari Dasa (5 levels: Maha→Prana) | ✅ Done |
| 4 | `ashtakavarga.py` | Sarvashtakavarga (12 signs × 7 planets) | ✅ Done |
| 5 | `panchang.py` | Tithi (30), Nitya Yoga (27 with details) | ✅ Done |
| 6 | `rasi.py` | 12 Rasis, Gochara house calculation | ✅ Done |
| 7 | `varga.py` | 20 Divisional charts (D1-D60) | ✅ Done |
| 8 | `kakshya.py` | 8 Kakshya sub-divisions per sign | ✅ Done |
| 9 | `jaimini.py` | Chara Dasa, 7 Karakas, 12 Arudha Padas | ✅ Done |
| 10 | `avastha.py` | 5 Avastha types (Bala, Deeptadi, etc.) | ✅ Done |
| 11 | `varshaphal.py` | Tajika system, 18 Sahams, 15 Tajika Yogas, Muntha | ✅ Done |
| 12 | `geolocation.py` | 150+ cities, coordinates, timezone lookup | ✅ Done |
| 13 | `pancha_pakshi.py` | 5 birds, 5 activities, Yama periods, daily predictions | ✅ Done |
| 14 | `numerology.py` | Birth/Destiny/Name numbers, 100+ predictions, Chaldean system | ✅ Done |
| 15 | `shadbala.py` | Six-fold strength (Sthana/Dig/Kaala/Cheshta/Naisargika/Drik Bala) | ✅ Done |
| 16 | `psychic_profile.py` | 3-step formula (Channel/Superpower/Signal), 1,296 unique profiles | ✅ Done |
| 17 | `yogas.py` | 21 yogas implemented (4 Moon, 5 Pancha Mahapurusha, 7 Wealth, 5 Raja), 73+ pending | ✅ Done |

---

## 📋 Recent Updates

### v0.6.0 - Wealth Yogas Expansion (January 25, 2026)

**New Yogas Implemented (4):**
- ✅ **Sakata Yoga** (15%) - Malefic yoga: Moon-Jupiter 6/8 relationship
- ✅ **Chatussagara Yoga** (0% - rare!) - All 4 kendras occupied by planets
- ✅ **Vasumathi Yoga** (75% - HIGHEST!) - Benefics in upachaya houses (3,6,10,11)
- ✅ **Parvata Yoga** (25%) - Benefics in kendras + lord in dignity

**Key Achievements:**
- 🎯 21/94 yogas implemented (22% complete)
- 🏆 Vasumathi Yoga discovered as most common (75% in famous people dataset)
- ✅ 100% validation: 20/20 famous people, 0 errors
- 📊 Aaron Pryor: 10 yogas (most in dataset)

**Yoga Distribution:**
```
Moon-based (4):     GajaKesari, Sunapha, Anapha, Dhurdhura
Mahapurusha (5):    Bhadra, Hamsa, Malavya, Ruchaka, Sasha
Wealth (7):         Amala, Kemadruma, Lakshmi, Sakata, Chatussagara, Vasumathi, Parvata
Raja (5):           Basic, Neechabhanga, Harsha, Sarala, Vimala
```

---

## 🔴 Phase 1: High Priority (Core Systems)

### 1.1 ~~Pancha Pakshi System~~ ✅ COMPLETED
- **File:** `pancha_pakshi.py`
- **Reference:** `Library/Logic/Calculate/PanchaPakshi.cs`
- **Tasks:**
  - [x] Implement 5 birds enum (Vulture, Owl, Crow, Cock, Peacock)
  - [x] Implement 5 activities enum (Dying, Sleeping, Walking, Eating, Ruling)
  - [x] Create bird strength lookup table
  - [x] Create day/night activity table by weekday and Yama
  - [x] Calculate birth bird from nakshatra
  - [x] Get current bird activity for any time
  - [x] Predict favorable/unfavorable periods
  - [x] Daily summary with favorable period count
  - [x] Find favorable time periods for a day

### 1.2 ~~Shadbala (Six-fold Strength)~~ ✅ COMPLETED
- **File:** `shadbala.py`
- **Reference:** `Library/Logic/Calculate/Core.cs`, `Library/Data/OpenAPIStaticTable.cs`
- **Tasks:**
  - [x] Sthana Bala (Positional strength)
    - [x] Uccha Bala (Exaltation)
    - [x] Saptavargaja Bala
    - [x] Ojayugmarasyamsa Bala
    - [x] Kendradi Bala
    - [x] Drekkana Bala
  - [x] Dig Bala (Directional strength)
  - [x] Kaala Bala (Temporal strength)
    - [x] Natonnata Bala
    - [x] Paksha Bala
    - [x] Tribhaga Bala
    - [x] Varsha/Masa/Dina/Hora Bala
    - [x] Ayana Bala
    - [x] Yuddha Bala
  - [x] Cheshta Bala (Motional strength)
  - [x] Naisargika Bala (Natural strength)
  - [x] Drik Bala (Aspectual strength)
  - [x] Calculate total Shadbala in Rupas
  - [x] Planetary strength comparison and ranking
  - [x] Bhava Bala (House strength)

### 1.3 Muhurtha (Electional Astrology)
- **File:** `muhurtha.py`
- **Reference:** `Library/Logic/Calculate/Muhurtha.cs` (10,853 lines)
- **Tasks:**
  - [ ] **Travel Muhurtha**
    - [ ] Favorable/unfavorable tithis
    - [ ] Favorable/unfavorable nakshatras
    - [ ] Direction-based warnings
    - [ ] Favorable lagnas
  - [ ] **Marriage Muhurtha**
    - [ ] Auspicious tithis for marriage
    - [ ] Auspicious nakshatras
    - [ ] Lagna requirements
    - [ ] Planetary positions check
  - [ ] **General Muhurtha**
    - [ ] Business activities
    - [ ] Medical treatments
    - [ ] Construction/building
    - [ ] Education/learning
    - [ ] Religious ceremonies

### 1.4 ~~Numerology~~ ✅ COMPLETED
- **File:** `numerology.py`
- **Reference:** `Library/Logic/Calculate/Numerology.cs`
- **Tasks:**
  - [x] Birth Number from birth date
  - [x] Destiny Number from full date
  - [x] Name Number (Chaldean system)
  - [x] Letter-to-number mapping table (special rules for initials)
  - [x] 100+ name number predictions with life aspect scores
  - [x] Ruling planet for each number
  - [x] Compatibility between birth/destiny/name numbers
  - [x] Lucky numbers, days, colors based on birth number

### 1.5 Match/Compatibility (Kuta)
- **File:** `compatibility.py`
- **Reference:** `Library/Data/MatchReport.cs`, `PersonKutaScore.cs`
- **Tasks:**
  - [ ] **10 Kuta System**
    - [ ] Varna Kuta (1 point)
    - [ ] Vashya Kuta (2 points)
    - [ ] Tara/Dina Kuta (3 points)
    - [ ] Yoni Kuta (4 points)
    - [ ] Graha Maitri (5 points)
    - [ ] Gana Kuta (6 points)
    - [ ] Rashi Kuta (7 points)
    - [ ] Nadi Kuta (8 points)
    - [ ] Mahendra Kuta
    - [ ] Stree Deergha
  - [ ] Total score calculation (max 36)
  - [ ] Compatibility percentage
  - [ ] Dosha detection (Manglik, etc.)

---

## 🟠 Phase 2: Medium Priority (Extended Calculations)

### 2.1 Time Calculations
- **File:** `time_calc.py` or extend `time.py`
- **Tasks:**
  - [ ] Sunrise time calculation
  - [ ] Sunset time calculation
  - [ ] Noon time calculation
  - [ ] Day length in hours
  - [ ] Is birth at night/day
  - [ ] Is time before sunrise
  - [ ] Ghati from sunrise
  - [ ] Hora (planetary hour 1-24)
  - [ ] Weekday lord

### 2.2 Planet Relationships
- **File:** `relationships.py`
- **Tasks:**
  - [ ] Natural/Permanent friendship table
  - [ ] Temporal friendship calculation
  - [ ] Combined relationship
  - [ ] Planet's relation to sign
  - [ ] Planet's relation to house
  - [ ] List temporary friends/enemies

### 2.3 Aspects System
- **File:** `aspects.py`
- **Tasks:**
  - [ ] Signs aspected by each planet
  - [ ] Special aspects (Mars 4/8, Jupiter 5/9, Saturn 3/10)
  - [ ] Full aspect (7th)
  - [ ] Partial aspects (3/4 and 1/2)
  - [ ] Is planet aspected by malefic
  - [ ] Is planet aspected by benefic
  - [ ] Is house aspected by malefic
  - [ ] List all aspecting planets

### 2.4 House Analysis
- **File:** `houses.py`
- **Tasks:**
  - [ ] Houses owned by planet
  - [ ] All planets in a house
  - [ ] Lord of house
  - [ ] House longitudes (start/mid/end)
  - [ ] Constellation at house cusp
  - [ ] House from any reference point
  - [ ] Bhava Chalit positions

### 2.5 Benefic/Malefic Analysis
- **File:** `functional.py`
- **Tasks:**
  - [ ] Natural benefics/malefics
  - [ ] Functional benefics for each Lagna
  - [ ] Functional malefics for each Lagna
  - [ ] Yogakaraka planets
  - [ ] Maraka planets
  - [ ] Badhaka planets

### 2.6 Extended Ashtakavarga
- **File:** Extend `ashtakavarga.py`
- **Tasks:**
  - [ ] Bhinnashtakavarga (individual planet charts)
  - [ ] Prastaraka Ashtakavarga
  - [ ] Trikona Shodhana
  - [ ] Ekadhipatya Shodhana
  - [ ] Pinda calculations
  - [ ] Transit predictions using SAV

### 2.7 Extended Dasa (8 levels)
- **File:** Extend `dasa.py`
- **Tasks:**
  - [ ] Add PD6 level
  - [ ] Add PD7 level
  - [ ] Add PD8 level
  - [ ] Dasa predictions text

---

## 🟡 Phase 3: Lower Priority (Additional Features)

### 3.1 Additional Panchang
- **File:** Extend `panchang.py`
- **Tasks:**
  - [ ] Karana (half-tithi, 11 types)
  - [ ] Panchaka calculation
  - [ ] Star strength
  - [ ] Moon strength
  - [ ] Rahu Kalam
  - [ ] Yamagandam
  - [ ] Gulika Kalam

### 3.2 Special Points
- **File:** `special_points.py`
- **Tasks:**
  - [ ] Ghataka Chakra
  - [ ] Mandi/Gulika longitude
  - [ ] Upagrahas
  - [ ] Bhrigu Bindu
  - [ ] Yogi/Avayogi points

### 3.3 ~~Yogas (Combinations)~~ ✅ IN PROGRESS
- **File:** `yogas.py` (CREATED)
- **Status:** 🟢 9 yogas implemented (9.6%), 85 remaining
- **Implemented:**
  - [x] **Classic Moon-based Yogas (4)**
    - [x] Gaja Kesari Yoga (Jupiter in kendra from Moon)
    - [x] Sunapha Yoga (Planets in 2nd from Moon)
    - [x] Anapha Yoga (Planets in 12th from Moon)
    - [x] Dhurdhura Yoga (Planets on both sides of Moon)
  - [x] **Pancha Mahapurusha Yogas (5)** ✅ COMPLETED
    - [x] Bhadra Yoga (Mercury in kendra in own/exalted sign)
    - [x] Hamsa Yoga (Jupiter in kendra in own/exalted sign)
    - [x] Malavya Yoga (Venus in kendra in own/exalted sign)
    - [x] Ruchaka Yoga (Mars in kendra in own/exalted sign)
    - [x] Sasha Yoga (Saturn in kendra in own/exalted sign)
- **Remaining Tasks:**
  - [ ] **Wealth Yogas (10-15 yogas)**
    - [ ] Amala Yoga
    - [ ] Lakshmi Yoga
    - [ ] Dhana Yoga
  - [ ] **Raja Yogas (10-15 yogas)**
    - [ ] Basic Raja Yoga
    - [ ] Neechabhanga Raja Yoga
  - [ ] **Malefic Yogas (10-15 yogas)**
    - [ ] Kemadruma Yoga
    - [ ] Kalasarpa Yoga
    - [ ] Daridra Yoga
  - [ ] **Ashtakavarga Yogas (50+ yogas)**
    - [ ] Sun Ashtakavarga Yogas (10+ yogas)
    - [ ] Mars Ashtakavarga Yogas (15+ yogas)
    - [ ] Mercury Ashtakavarga Yogas (10+ yogas)
  - [ ] **Specialty Yogas (Remaining classics)**
    - [ ] Budhaditya Yoga
    - [ ] Chandra Mangala Yoga
    - [ ] Adhi Yoga
    - [ ] Malika Yogas (Continuous house occupations)

### 3.4 Eclipse Calculations
- **File:** `eclipse.py`
- **Tasks:**
  - [ ] Is Full Moon
  - [ ] Is New Moon
  - [ ] Solar eclipse detection
  - [ ] Lunar eclipse detection
  - [ ] Eclipse timing

### 3.5 Sun Ingress
- **File:** `ingress.py`
- **Tasks:**
  - [ ] Sun sign entry time
  - [ ] Sun sign exit time
  - [ ] Sankranti times

### 3.6 Miscellaneous
- **Tasks:**
  - [ ] Birth Varna calculation
  - [ ] Residential strength
  - [ ] Ishta/Kashta Phala
  - [ ] Vimshopaka Bala

---

## 📁 Proposed File Structure

```
VedAstroPy/
├── logic/
│   ├── __init__.py
│   ├── calculate.py      ✅ Core calculations
│   ├── time.py           ✅ Time handling
│   ├── consts.py         ✅ Constants
│   ├── nakshatra.py      ✅ Nakshatras
│   ├── rasi.py           ✅ Rasis & Gochara
│   ├── dasa.py           ✅ Vimshottari Dasa
│   ├── ashtakavarga.py   ✅ Ashtakavarga
│   ├── panchang.py       ✅ Tithi, Yoga
│   ├── varga.py          ✅ Divisional charts
│   ├── kakshya.py        ✅ Kakshya
│   ├── jaimini.py        ✅ Jaimini system
│   ├── avastha.py        ✅ Avasthas
│   ├── varshaphal.py     ✅ Annual horoscope
│   │
│   ├── pancha_pakshi.py  🔴 Phase 1
│   ├── shadbala.py       🔴 Phase 1
│   ├── muhurtha.py       🔴 Phase 1
│   ├── numerology.py     🔴 Phase 1
│   ├── compatibility.py  🔴 Phase 1
│   │
│   ├── relationships.py  🟠 Phase 2
│   ├── aspects.py        🟠 Phase 2
│   ├── houses.py         🟠 Phase 2
│   ├── functional.py     🟠 Phase 2
│   │
│   ├── yogas.py          🟡 Phase 3
│   ├── eclipse.py        🟡 Phase 3
│   └── special_points.py 🟡 Phase 3
│
├── main.py               Demo script
├── README.md             Documentation
└── ROADMAP.md            This file
```

---

## 📊 Progress Tracker

| Phase | Total Tasks | Completed | Progress |
|-------|-------------|-----------|----------|
| Completed | 11 modules | 11 | 100% |
| Phase 1 | 5 modules | 0 | 0% |
| Phase 2 | 7 modules | 0 | 0% |
| Phase 3 | 6 modules | 1 (partial) | 8% |
| **Overall** | **29 modules** | **12** | **41%** |

---

## 🔗 References

- **VedAstro C# Source:** `Library/Logic/Calculate/`
- **Swiss Ephemeris:** https://www.astro.com/swisseph/
- **pyswisseph:** https://pypi.org/project/pyswisseph/

---

## 📝 Notes

1. Each module should include comprehensive docstrings
2. All calculations should be verified against VedAstro C# output
3. Unit tests should be created for each module
4. Consider adding type hints for better IDE support
5. Performance optimization for batch calculations

---

*Generated for VedAstroPy development planning*
