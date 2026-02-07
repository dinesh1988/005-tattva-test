from datetime import datetime, timedelta

# Dasa Lords in order (Vimshottari)
# (Lord Name, Duration in Years)
DASA_LORDS = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
]

def get_vimshottari_dasa_schedule(moon_nakshatra_num: int, moon_nakshatra_percentage: float, 
                                  birth_date: datetime) -> dict:
    """
    Generates the complete 120-year Vimshottari Dasa schedule from birth.
    
    Returns:
    - All 9 Maha Dasas with start/end dates
    - All Bhuktis (sub-periods) within each Maha Dasa
    - Balance of birth Dasa
    - Complete timeline for life planning
    """
    
    # 1. Identify Birth Dasa Lord
    lord_index = (moon_nakshatra_num - 1) % 9
    lord_name, lord_years = DASA_LORDS[lord_index]
    
    # 2. Calculate Balance of Birth Dasa
    remaining_percentage = 100.0 - moon_nakshatra_percentage
    balance_years = (remaining_percentage / 100.0) * lord_years
    balance_days = balance_years * 365.2425
    
    # 3. Calculate start date of birth Dasa (retroactively)
    elapsed_years = (moon_nakshatra_percentage / 100.0) * lord_years
    elapsed_days = elapsed_years * 365.2425
    birth_dasa_start_date = birth_date - timedelta(days=elapsed_days)
    
    # 4. Build complete schedule
    schedule = {
        "birth_dasa": lord_name,
        "birth_dasa_balance_years": round(balance_years, 2),
        "maha_dasas": []
    }
    
    current_date = birth_dasa_start_date
    current_lord_index = lord_index
    
    # Generate all 9 Maha Dasas (one full cycle)
    for cycle in range(9):
        maha_lord_name, maha_lord_years = DASA_LORDS[current_lord_index]
        maha_dasa_days = maha_lord_years * 365.2425
        maha_dasa_end_date = current_date + timedelta(days=maha_dasa_days)
        
        # Calculate all Bhuktis within this Maha Dasa
        bhuktis = []
        bhukti_start_date = current_date
        bhukti_lord_index = current_lord_index  # Bhukti starts with Maha Dasa lord
        
        for bhukti_cycle in range(9):
            bhukti_lord_name, bhukti_lord_years = DASA_LORDS[bhukti_lord_index]
            
            # Formula: (Maha Dasa Years × Bhukti Lord Years) / 120
            bhukti_duration_years = (maha_lord_years * bhukti_lord_years) / 120.0
            bhukti_duration_days = bhukti_duration_years * 365.2425
            bhukti_end_date = bhukti_start_date + timedelta(days=bhukti_duration_days)
            
            # Check if this period includes birth
            is_birth_period = birth_date >= bhukti_start_date and birth_date < bhukti_end_date
            
            bhuktis.append({
                "bhukti_lord": bhukti_lord_name,
                "start_date": bhukti_start_date.strftime("%Y-%m-%d"),
                "end_date": bhukti_end_date.strftime("%Y-%m-%d"),
                "duration_years": round(bhukti_duration_years, 2),
                "is_birth_bhukti": is_birth_period
            })
            
            bhukti_start_date = bhukti_end_date
            bhukti_lord_index = (bhukti_lord_index + 1) % 9
        
        # Check if birth falls in this Maha Dasa
        is_birth_dasa = birth_date >= current_date and birth_date < maha_dasa_end_date
        
        schedule["maha_dasas"].append({
            "dasa_lord": maha_lord_name,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": maha_dasa_end_date.strftime("%Y-%m-%d"),
            "duration_years": maha_lord_years,
            "is_birth_dasa": is_birth_dasa,
            "bhuktis": bhuktis
        })
        
        current_date = maha_dasa_end_date
        current_lord_index = (current_lord_index + 1) % 9
    
    return schedule

def get_vimshottari_dasa(moon_nakshatra_num: int, moon_nakshatra_percentage: float, birth_date: datetime, current_date: datetime) -> tuple[str, str]:
    """
    Calculates the current Vimshottari Maha Dasa and Bhukti (Antardasa).
    Returns (Maha Dasa Lord, Bhukti Lord)
    """
    
    # 1. Identify Birth Dasa Lord
    # Nakshatra 1 (Ashwini) -> Ketu (Index 0)
    # Nakshatra 2 (Bharani) -> Venus (Index 1)
    # ...
    # Cycle repeats every 9 Nakshatras
    # (num - 1) because nakshatra_num is 1-based
    lord_index = (moon_nakshatra_num - 1) % 9
    lord_name, lord_years = DASA_LORDS[lord_index]
    
    # 2. Calculate Balance of Dasa at Birth
    # Percentage passed is how much of the Nakshatra the Moon has traversed.
    # Balance is the remaining part.
    remaining_percentage = 100.0 - moon_nakshatra_percentage
    balance_years = (remaining_percentage / 100.0) * lord_years
    
    # 3. Traverse forward to Current Date
    age_days = (current_date - birth_date).days
    age_years = age_days / 365.2425 # Using Gregorian average year
    
    # Check if we are still in Birth Dasa
    if age_years < balance_years:
        # We are in the birth Dasa. Now find the Bhukti.
        # The elapsed time in this Dasa is (balance_years - remaining_balance) ?? 
        # No, elapsed time from start of Dasa is (Total Dasa Years - Balance Years) + Age Years
        # Wait, simpler: 
        # Time elapsed in current Dasa = (Total Years * (Percentage Traversed / 100)) + Age Years
        # Actually, let's just treat the timeline linearly.
        
        # Time from START of the Birth Dasa to NOW
        time_from_start_of_dasa = (lord_years * (moon_nakshatra_percentage / 100.0)) + age_years
        
        return _calculate_bhukti(lord_index, time_from_start_of_dasa)
        
    # Move to next Dasas
    years_passed_since_birth = balance_years
    current_index = lord_index
    
    # Loop through Dasas until we find the current one
    while True:
        current_index = (current_index + 1) % 9
        lord_name, lord_years = DASA_LORDS[current_index]
        
        if years_passed_since_birth + lord_years > age_years:
            # We are in this Dasa
            time_in_current_dasa = age_years - years_passed_since_birth
            return _calculate_bhukti(current_index, time_in_current_dasa)

        years_passed_since_birth += lord_years
        
        if years_passed_since_birth > 120 + age_years: # Safety break
             return "End of Cycle", "End of Cycle"


def get_vimshottari_dasa_full(moon_nakshatra_num: int, moon_nakshatra_percentage: float, 
                              birth_date: datetime, current_date: datetime) -> dict:
    """
    Calculates the complete Vimshottari Dasa breakdown including:
    - Maha Dasa (Main Period)
    - Bhukti/Antardasa (Sub-Period)
    - Pratyantara (Sub-Sub Period)
    - Sookshma (Sub-Sub-Sub Period)
    - Prana (Sub-Sub-Sub-Sub Period)
    
    Returns a dictionary with all 5 levels.
    """
    
    # 1. Identify Birth Dasa Lord
    lord_index = (moon_nakshatra_num - 1) % 9
    lord_name, lord_years = DASA_LORDS[lord_index]
    
    # 2. Calculate Balance of Dasa at Birth
    remaining_percentage = 100.0 - moon_nakshatra_percentage
    balance_years = (remaining_percentage / 100.0) * lord_years
    
    # 3. Traverse forward to Current Date
    age_days = (current_date - birth_date).days
    age_years = age_days / 365.2425
    
    # Find current Maha Dasa
    if age_years < balance_years:
        time_from_start_of_dasa = (lord_years * (moon_nakshatra_percentage / 100.0)) + age_years
        maha_dasa_index = lord_index
    else:
        years_passed = balance_years
        current_index = lord_index
        
        while True:
            current_index = (current_index + 1) % 9
            _, dasa_years = DASA_LORDS[current_index]
            
            if years_passed + dasa_years > age_years:
                time_from_start_of_dasa = age_years - years_passed
                maha_dasa_index = current_index
                break
            
            years_passed += dasa_years
            if years_passed > 240:  # Safety
                return {"error": "Calculation overflow"}
    
    # Now calculate all 5 levels
    return _calculate_all_levels(maha_dasa_index, time_from_start_of_dasa)


def _calculate_all_levels(maha_dasa_index: int, time_in_maha_dasa: float) -> dict:
    """
    Calculate Maha Dasa, Bhukti, Pratyantara, Sookshma, and Prana.
    """
    maha_name, maha_years = DASA_LORDS[maha_dasa_index]
    
    # --- Level 1: Maha Dasa ---
    result = {
        "maha_dasa": maha_name,
        "maha_dasa_years": maha_years
    }
    
    # --- Level 2: Bhukti (Antardasa) ---
    bhukti_index = maha_dasa_index
    bhukti_accumulated = 0.0
    
    for _ in range(9):
        b_name, b_years = DASA_LORDS[bhukti_index]
        bhukti_duration = (maha_years * b_years) / 120.0
        
        if bhukti_accumulated + bhukti_duration > time_in_maha_dasa:
            time_in_bhukti = time_in_maha_dasa - bhukti_accumulated
            result["bhukti"] = b_name
            result["bhukti_duration_years"] = bhukti_duration
            
            # --- Level 3: Pratyantara ---
            pratyantara_index = bhukti_index
            pratyantara_accumulated = 0.0
            
            for _ in range(9):
                p_name, p_years = DASA_LORDS[pratyantara_index]
                pratyantara_duration = (bhukti_duration * p_years) / 120.0
                
                if pratyantara_accumulated + pratyantara_duration > time_in_bhukti:
                    time_in_pratyantara = time_in_bhukti - pratyantara_accumulated
                    result["pratyantara"] = p_name
                    result["pratyantara_duration_days"] = pratyantara_duration * 365.2425
                    
                    # --- Level 4: Sookshma ---
                    sookshma_index = pratyantara_index
                    sookshma_accumulated = 0.0
                    
                    for _ in range(9):
                        s_name, s_years = DASA_LORDS[sookshma_index]
                        sookshma_duration = (pratyantara_duration * s_years) / 120.0
                        
                        if sookshma_accumulated + sookshma_duration > time_in_pratyantara:
                            time_in_sookshma = time_in_pratyantara - sookshma_accumulated
                            result["sookshma"] = s_name
                            result["sookshma_duration_days"] = sookshma_duration * 365.2425
                            
                            # --- Level 5: Prana ---
                            prana_index = sookshma_index
                            prana_accumulated = 0.0
                            
                            for _ in range(9):
                                pr_name, pr_years = DASA_LORDS[prana_index]
                                prana_duration = (sookshma_duration * pr_years) / 120.0
                                
                                if prana_accumulated + prana_duration > time_in_sookshma:
                                    result["prana"] = pr_name
                                    result["prana_duration_hours"] = prana_duration * 365.2425 * 24
                                    return result
                                
                                prana_accumulated += prana_duration
                                prana_index = (prana_index + 1) % 9
                            
                            result["prana"] = "Unknown"
                            return result
                        
                        sookshma_accumulated += sookshma_duration
                        sookshma_index = (sookshma_index + 1) % 9
                    
                    result["sookshma"] = "Unknown"
                    result["prana"] = "Unknown"
                    return result
                
                pratyantara_accumulated += pratyantara_duration
                pratyantara_index = (pratyantara_index + 1) % 9
            
            result["pratyantara"] = "Unknown"
            result["sookshma"] = "Unknown"
            result["prana"] = "Unknown"
            return result
        
        bhukti_accumulated += bhukti_duration
        bhukti_index = (bhukti_index + 1) % 9
    
    result["bhukti"] = "Unknown"
    return result


def _calculate_bhukti(dasa_lord_index: int, time_elapsed_in_dasa: float) -> tuple[str, str]:
    """
    Determines the Bhukti based on time elapsed within a Maha Dasa.
    """
    dasa_name, dasa_years = DASA_LORDS[dasa_lord_index]
    
    # Bhukti starts with the Dasa Lord itself
    bhukti_index = dasa_lord_index 
    bhukti_years_accumulated = 0.0
    
    for _ in range(9):
        b_name, b_years = DASA_LORDS[bhukti_index]
        
        # Formula: (Maha Dasa Years * Bhukti Lord Years) / 120
        bhukti_duration = (dasa_years * b_years) / 120.0
        
        if bhukti_years_accumulated + bhukti_duration > time_elapsed_in_dasa:
            return dasa_name, b_name
        
        bhukti_years_accumulated += bhukti_duration
        bhukti_index = (bhukti_index + 1) % 9
        
    return dasa_name, "Unknown"
