# C# → Python Feature Gap Analysis
_Last updated: April 4, 2026_

---

## Already Ported (Complete)

| Feature | Python Module |
|---|---|
| 115 Yogas | `logic/yogas.py` |
| Ashtakavarga (BAV + SAV) | `logic/ashtakavarga.py` |
| Vimshottari Dasa schedule | `logic/dasa.py` |
| Vargas D1–D60 | `logic/varga.py` |
| Nakshatra + Tarabala | `logic/nakshatra.py` |
| Panchang (tithi / yoga / karana / nitya yoga) | `logic/panchang.py` |
| Pancha Pakshi bird system | `logic/pancha_pakshi.py` |
| Numerology | `logic/numerology.py` |
| Jaimini (chara dasa, karakas, arudha lagna) | `logic/jaimini.py` |
| Shadbala (all 6 sub-balas + bhava bala) | `logic/shadbala.py` |
| Avastha | `logic/avastha.py` |
| Aspects | `logic/aspects.py` |
| Dignity | `logic/dignity.py` |
| Vedha | `logic/vedha.py` |
| Kakshya | `logic/kakshya.py` |
| Varshaphal | `logic/varshaphal.py` |
| Functional Nature | `logic/functional_nature.py` |
| House Lordship | `logic/lordship.py` |
| Planet Relations (natural + temporary) | `logic/planet_relations.py` |
| Psychic Profile | `logic/psychic_profile.py` |
| Geolocation | `logic/geolocation.py` |
| Sunrise / Sunset | `logic/sunrise.py` |
| Muhurtha basics (tithi/nakshatra/weekday/hora) | `logic/muhurtha.py` (724 lines) |

---

## Missing — High Priority

### 1. Kundali Matching / Ashtakuta Compatibility — ENTIRELY ABSENT

**C# source**: `Library/Data/MatchReport.cs`, `Library/Data/MatchSummaryData.cs`, `Library/Data/GhatakaRow.cs`

The 8-factor Ashtakuta compatibility system:

| Kuta | Max Points |
|---|---|
| Varna (caste compatibility) | 1 |
| Vashya (dominance) | 2 |
| Tara (nakshatra compatibility) | 3 |
| Yoni (sexual compatibility) | 4 |
| Graha Maitri (lord compatibility) | 5 |
| Gana (temperament) | 6 |
| Bhakuta (sign compatibility) | 7 |
| Nadi (constitution/health) | 8 |
| **Total** | **36** |

Also includes:
- Ghataka dosha checks (using `GhatakaRow.cs` data)
- Mangal dosha matching

> **Note**: The current API endpoint `/api/v1/profile/compatibility` returns a **hardcoded placeholder score of 75** — not real Ashtakuta logic.

---

### 2. Gochara / Transit House Predictions — ENTIRELY ABSENT

**C# source**: `Library/Data/Enum/EventName.cs` (`#region GOCHARA_TRANSITS`)

84 named predictions: `SunGocharaInHouse1` → `KetuGocharaInHouse12` — each with full interpretive text covering effects on career, health, relationships, finances.

> `get_gochara_house()` math already exists in `logic/rasi.py` — only the interpretation layer is missing.

---

### 3. Planet-in-House Interpretations — ENTIRELY ABSENT

**C# source**: `Library/Data/Enum/HoroscopeName.cs`

108 entries: `SunInHouse1`, `MoonInHouse2` … `KetuInHouse12`.  
Each carries full natal chart interpretation text. No Python equivalent module exists.

---

### 4. Planet-in-Sign Interpretations — ENTIRELY ABSENT

**C# source**: `Library/Data/Enum/HoroscopeName.cs`

84 entries: `SunInAries` … `SaturnInPisces`.  
Full sign-placement predictions. No Python equivalent module exists.

---

### 5. House Lord in House Interpretations — ENTIRELY ABSENT

**C# source**: `Library/Data/Enum/HoroscopeName.cs`

144+ entries: `House1LordInHouse1Fortified`, `House2LordInHouse5`, etc. (all 12×12 combinations plus fortified/afflicted variants).  
Deep interpretive predictions for every lord placement. No Python equivalent.

---

### 6. Rising Sign (Lagna) Predictions — ENTIRELY ABSENT

**C# source**: `Library/Data/Enum/HoroscopeName.cs`

12 entries: `AriesRising` … `PiscesRising`.  
Personality, physical appearance, life-path interpretations. No Python equivalent.

---

## Missing — Partial (Muhurtha Gaps)

**C# `Muhurtha.cs`** is **7,834 lines**; Python `muhurtha.py` is **724 lines**.

### Missing Muhurtha Events by Category

| Category | Missing Events | Count |
|---|---|---|
| Tarabala sub-types | Janma/Sampat/Vipat/Kshema/Pratyak/Sadhana/Naidhana/Mitra/ParamaMitra × 3 strengths (Strong/Middling/Weak) | 27 |
| Yoga events | SiddhaYoga, AmritaSiddhaYoga, PanchangaSuddhi, UgraYoga, BadNithyaYoga | 5 |
| Dosha events | BhriguShatka, Kujasthama, KarthariDosha, ShashtashtaRiphagataChandra, SagrahaChandra | 5 |
| Karana events | TaitulaKarana, SakunaKarana, BavaKarana, BhadraKarana | 4 |
| Electional: personal | GoodHairCutting, GoodNailCutting, GoodTakingInjections | 3 |
| Electional: commerce | GoodSellingForProfit, GoodWeekdayForSelling, GoodMoonSignForSelling, BadForBuyingToolsUtensilsJewellery, GoodForBuyingBrassVessels, GoodForBuyingCopperVessels, GoodForBuyingSteelIronVessels, GoodForBuyingSilverVessels, GoodForBuyingJewellery | 9 |
| Agriculture timing | GoodAnySeedsSowing + 15 crop-specific timings (garlic, sugarcane, fruit trees, flowers, grains, onion, pepper, potato, pumpkin, etc.) + GoodYogaForAllAgriculture, BadForStartingAllAgriculture, BadLagnaForAllAgriculture | 19 |
| Building/construction | BadLunarMonthForBuilding, GoodSunSignForBuilding, BadSunSignForBuilding, GoodLunarDayForBuilding, GoodWeekDayForBuilding, BadLunarPhaseForBuilding, BadWeekDayForBuilding, BadWeekDayForRepairs, GoodYogaForRepairs, GoodYogaForRepairs2 | 10 |
| Planet strength flags | SunIsStrong … SaturnIsStrong | 7 |
| House strength flags | House1IsStrong … House12IsStrong | 12 |
| Ashtakavarga Gochara Bindu | 7 planets × 9 bindu levels (0–8) = SunTransit8Bindu … SaturnTransit0Bindu | 63 |
| Directional travel | BadWeekdayForTravelEast, South, West, North | 4 |
| Dasa-based events | Lord6And8Dasa, Lord5And9Dasa, BhuktiDasaLordInBadHouses, LagnaLordDasa, Saturn4thDasa, Jupiter6thDasa, Lord2Dasa, Lord3Dasa, Lord5And9DasaBhukti, ElevatedSunDasa, SunWithLord9Or10Dasa, SunWithLord5Dasa, SunWithLord2Dasa, SunBadPositionDasa, ExaltedSunDasa | 15 |
| Yama time-slots | Yama1, Yama2, Yama3, Yama4, Yama5 | 5 |
| Miscellaneous | EkadashiOccuring, SuryaSankramana, Papashadvargas, IsNotAuspiciousDay, UdayasthaSuddhi, LagnaThyajya | 6 |

**Total missing Muhurtha events: ~194**

---

## Missing — Dasa Period Interpretations

**C# source**: `Library/Data/Enum/EventName.cs` (`#region DASA_PERIODS`)

Python calculates *which* dasa/bhukti is active but has **no interpretive text output**.

| Level | Count | Example |
|---|---|---|
| PD1 Mahadasa × Birth Sign (108 entries) | 108 | `AriesSunPD1`, `CancerMoonPD1` |
| PD2 Bhukti combinations (81 entries) | 81 | `SunMoonPD2`, `JupiterSaturnPD2` |
| PD3 Antardasa combinations (81 entries) | 81 | `SunSunPD3`, `MoonMarsPD3` |

---

## Not Applicable

| C# File | Reason |
|---|---|
| `Library/Logic/CalculateKP-ORI.cs` | File is **empty** in C# repo — KP system was never implemented |
| `Library/Logic/Calculate/NLPTools.cs` | NLP/ML tooling — not core astrology |
| `Library/Logic/Calculate/MLDatasetTools.cs` | Dataset generation — not runtime astrology |
| `Library/Logic/Calculate/NearestCentroidClassification.cs` | ML classifier — not astrology |
| `Library/Logic/Calculate/ChatAPI.cs` | Replicated by Python FastAPI layer |
| `Library/Logic/Calculate/PersonManagerTools.cs` | User/person account management |

---

## Recommended Porting Order

| Priority | Feature | Effort | Value |
|---|---|---|---|
| 1 | **Kundali Matching (Ashtakuta)** | Medium | Very High — most requested compatibility feature |
| 2 | **Gochara transit predictions** | Medium | High — daily/weekly forecast use-case |
| 3 | **Planet-in-House + Planet-in-Sign interpretations** | High (data) | High — core natal reading |
| 4 | **House Lord in House interpretations** | High (data) | High — detailed natal reading |
| 5 | **Advanced Muhurtha events** (~194 missing) | Medium | High — electional astrology |
| 6 | **Dasa period interpretations** | High (content) | Medium — requires curated text per combination |
| 7 | **Rising Sign (Lagna) predictions** | Low | Medium — 12 entries, self-contained |
