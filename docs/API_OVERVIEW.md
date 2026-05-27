# Tattva API — Plain English Overview
_Last updated: May 26, 2026 (commit 4a79b19)_

> **AI instruction**: Update this file whenever a new endpoint is added or an existing one changes.  
> One sentence per endpoint. No code. No jargon.

---

## Health & Status

| Endpoint | What it does |
|---|---|
| `GET /health` | Tells the server host (Cloud Run / Azure) that the app is alive. |
| `GET /` | Returns the app name, version, and a list of all available routes. |

---

## Utilities

| Endpoint | What it does |
|---|---|
| `GET /api/v1/location/{city}` | Takes a city name and returns its latitude, longitude, and timezone — used by every other endpoint when coordinates are not provided directly. |
| `GET /api/v1/datetime` | Returns the current UTC time along with a full list of timezone offsets — useful for clients that need to know "what time is it now everywhere". |

---

## Birth Chart  _(immutable — same birth data always returns the same result)_

| Endpoint | What it does |
|---|---|
| `POST /api/v1/chart/planets` | Given a birth date, time, and place — returns where every planet (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu) and the Ascendant were in the sky at birth, expressed as sign, degree, and nakshatra. |
| `POST /api/v1/chart/interpretations` | Returns classical B.V. Raman text descriptions for what it means to have each planet in its particular natal house (e.g. "Sun in the 7th house means..."). |
| `POST /api/v1/chart/planet-in-sign` | Returns classical text for what it means to have each planet in its particular zodiac sign at birth (e.g. "Moon in Aquarius means..."). |
| `POST /api/v1/chart/house-lord-in-house` | For each of the 12 astrological houses, tells you which planet rules it and where that planet is sitting — with classical interpretation text. |
| `POST /api/v1/chart/rising-sign` | Returns the Lagna (Ascendant sign) and a classical description of how it shapes personality, appearance, and life direction. |

---

## Psychic Profile  _(VedAstro's custom system)_

| Endpoint | What it does |
|---|---|
| `POST /api/v1/profile/generate` | Takes birth data, runs the full psychic profile calculation (Channel + Superpower + Signal Strength), saves it to the database, and returns the result. |
| `POST /api/v1/profile/complete` | Same calculation as above but does **not** save — purely stateless, for one-off use. |
| `GET /api/v1/profile/{profile_id}` | Retrieves a previously saved profile by its ID. |
| `GET /api/v1/profiles/user/{user_id}` | Lists all saved profiles belonging to a specific user. |
| `POST /api/v1/profile/compatibility` | Takes two saved profile IDs (male + female) and scores their Kundali compatibility using the classical 8-kuta (Ashtakuta) system — returns a score out of 36. |
| `GET /api/v1/profile/me?user_id=` | Returns the stored natal + phase profile for a user: Moon sign, Lagna, atmakaraka, birth nakshatra, current mahadasha/bhukti with end dates, life phase, disposition, and focus. Does **not** recompute — reads from the database. Returns 404 if no record exists yet. |
| `PUT /api/v1/profile/birth-data?user_id=` | Corrects a user's birth data, recomputes the full natal profile and current dasa periods, clears their cached daily predictions, and saves the updated record. The user's saved `user_focus` is preserved across corrections. |

---

## Daily Timing & Gochara  _(time-sensitive — not cached)_

| Endpoint | What it does |
|---|---|
| `POST /api/v1/panchang/gochara` | Returns the current sky state: where every planet is right now, today's panchang (tithi, nakshatra, yoga, karana), hora table (planetary hours), and choghadiya time periods. |
| `POST /api/v1/prediction/gochara` | Personal transit reading — takes your birth data, finds where each planet is transiting relative to your natal Moon sign, and rates each transit as good/bad with classical text. |
| `POST /api/v1/prediction/daily-5step` | The flagship daily score: combines 5 Vedic timing layers (day lord, Tara Bala, Moon gochara, Ashtakavarga strength, Vedha obstruction check) into a single daily quality score. |

---

## Reference Data  _(static lookup tables — never changes)_

| Endpoint | What it does |
|---|---|
| `GET /api/v1/channels` | Returns all 12 psychic channel definitions (one per Moon sign element/quality combination). |
| `GET /api/v1/superpowers` | Returns all 27 nakshatra superpower archetypes — one per birth nakshatra. |
| `GET /api/v1/signal-strengths` | Returns all 12 signal strength types based on which house Ketu occupies in the natal chart. |

---

## What inputs are needed?

Most endpoints only need three things:

1. **Birth date** — `"1988-06-07"`
2. **Birth time** — `"20:40"`
3. **Birth place** — `"Chennai"` (or latitude/longitude if you already have it)

Daily timing endpoints additionally need:
- **Current place** — where the person is right now (for sunrise/timezone)
- **Current date/time** — defaults to right now if omitted
