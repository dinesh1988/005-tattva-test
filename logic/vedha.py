from __future__ import annotations

from typing import Dict, Any


def calculate_vedha_status(natal_moon_sign_num: int, current_planetary_positions: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    """Calculates Gochara status with Vedha (obstruction) checks.

    Args:
        natal_moon_sign_num: 1-12 sign number (Aries=1..Pisces=12)
        current_planetary_positions: {"PlanetName": sign_number_1_12}

    Returns:
        Dict keyed by planet name, each with: status, reason, current_house, vedha_house, blockers.
    """

    # Define Favorable Houses and their specific Vedha (Blocker) Houses
    # Format: { Planet: { Good_House: Blocker_House } }
    vedha_rules = {
        "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
        "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
        "Mars": {3: 12, 6: 9, 11: 5},
        "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
        "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
        "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
        "Saturn": {3: 12, 6: 9, 11: 5},
        "Rahu": {3: 12, 6: 9, 11: 5},
        "Ketu": {3: 12, 6: 9, 11: 5},
    }

    results: Dict[str, Dict[str, Any]] = {}

    # 1) Map current planets to houses relative to natal Moon
    transit_houses: Dict[str, int] = {}
    for planet, sign_num in current_planetary_positions.items():
        house = (sign_num - natal_moon_sign_num) + 1
        if house <= 0:
            house += 12
        transit_houses[planet] = house

    # 2) Evaluate each planet for favorable/blocked/unfavorable
    for planet, current_house in transit_houses.items():
        rules = vedha_rules.get(planet)
        if not rules or current_house not in rules:
            results[planet] = {
                "status": "Unfavorable",
                "reason": f"Transiting House {current_house} is not favorable.",
                "current_house": current_house,
                "vedha_house": None,
                "blockers": [],
                "exempt": False,
            }
            continue

        vedha_house = rules[current_house]

        blockers = [p_name for p_name, h_num in transit_houses.items() if h_num == vedha_house]
        if not blockers:
            results[planet] = {
                "status": "Favorable",
                "reason": f"Transiting favorable House {current_house} with no obstruction.",
                "current_house": current_house,
                "vedha_house": vedha_house,
                "blockers": [],
                "exempt": False,
            }
            continue

        # 3) Exceptions (father-son style)
        is_exempt = False
        effective_blockers = list(blockers)

        # Exception A: Sun and Saturn do not block each other
        if planet == "Sun" and "Saturn" in effective_blockers:
            if len(effective_blockers) == 1:
                is_exempt = True
            else:
                effective_blockers = [b for b in effective_blockers if b != "Saturn"]

        if planet == "Saturn" and "Sun" in effective_blockers:
            if len(effective_blockers) == 1:
                is_exempt = True
            else:
                effective_blockers = [b for b in effective_blockers if b != "Sun"]

        # Exception B: Moon and Mercury do not block each other
        if planet == "Moon" and "Mercury" in effective_blockers:
            if len(effective_blockers) == 1:
                is_exempt = True
            else:
                effective_blockers = [b for b in effective_blockers if b != "Mercury"]

        if planet == "Mercury" and "Moon" in effective_blockers:
            if len(effective_blockers) == 1:
                is_exempt = True
            else:
                effective_blockers = [b for b in effective_blockers if b != "Moon"]

        if is_exempt or len(effective_blockers) == 0:
            results[planet] = {
                "status": "Favorable (Exempt)",
                "reason": f"Obstruction by {blockers[0]} ignored due to special relationship." if len(blockers) == 1 else "Obstructions ignored due to special relationships.",
                "current_house": current_house,
                "vedha_house": vedha_house,
                "blockers": blockers,
                "exempt": True,
            }
        else:
            results[planet] = {
                "status": "Blocked",
                "reason": f"Good result of House {current_house} blocked by {', '.join(effective_blockers)} in House {vedha_house}.",
                "current_house": current_house,
                "vedha_house": vedha_house,
                "blockers": blockers,
                "effective_blockers": effective_blockers,
                "exempt": False,
            }

    return results
