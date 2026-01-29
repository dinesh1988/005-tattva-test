"""
Test Vimshottari Dasa Schedule Generator
Shows complete 120-year timeline with all Maha Dasas and Bhuktis
"""

from datetime import datetime
from logic.dasa import get_vimshottari_dasa_schedule

# Test with birth data: 04/05/1991, 10:50 AM
# Moon Nakshatra: Bharani (Nakshatra #2), 73.41% traversed
birth_date = datetime(1991, 5, 4, 10, 50)
moon_nakshatra_num = 2  # Bharani
moon_nakshatra_pct = 73.41

print("=" * 80)
print("VIMSHOTTARI DASA SCHEDULE - Complete 120-Year Timeline")
print("=" * 80)
print(f"Birth Date: {birth_date.strftime('%Y-%m-%d %H:%M')}")
print(f"Moon Nakshatra: Bharani (#2), {moon_nakshatra_pct}% traversed")
print()

schedule = get_vimshottari_dasa_schedule(moon_nakshatra_num, moon_nakshatra_pct, birth_date)

print(f"Birth Dasa: {schedule['birth_dasa']}")
print(f"Balance at Birth: {schedule['birth_dasa_balance_years']} years")
print("=" * 80)
print()

# Display all Maha Dasas
for i, maha_dasa in enumerate(schedule['maha_dasas'], 1):
    is_birth = " ⭐ BIRTH DASA" if maha_dasa['is_birth_dasa'] else ""
    print(f"{i}. {maha_dasa['dasa_lord']} MAHA DASA ({maha_dasa['duration_years']} years){is_birth}")
    print(f"   Period: {maha_dasa['start_date']} to {maha_dasa['end_date']}")
    print(f"   Bhuktis (Sub-Periods):")
    
    # Display first 3 and last bhukti as sample
    for j, bhukti in enumerate(maha_dasa['bhuktis'][:3], 1):
        is_birth_bhukti = " ⭐ BIRTH BHUKTI" if bhukti['is_birth_bhukti'] else ""
        print(f"      {j}. {bhukti['bhukti_lord']}: {bhukti['start_date']} to {bhukti['end_date']} ({bhukti['duration_years']} yrs){is_birth_bhukti}")
    
    if len(maha_dasa['bhuktis']) > 4:
        print(f"      ... ({len(maha_dasa['bhuktis']) - 4} more bhuktis)")
    
    last_bhukti = maha_dasa['bhuktis'][-1]
    print(f"      9. {last_bhukti['bhukti_lord']}: {last_bhukti['start_date']} to {last_bhukti['end_date']} ({last_bhukti['duration_years']} yrs)")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Maha Dasas: {len(schedule['maha_dasas'])}")
total_bhuktis = sum(len(md['bhuktis']) for md in schedule['maha_dasas'])
print(f"Total Bhuktis: {total_bhuktis}")
print(f"Timeline: {schedule['maha_dasas'][0]['start_date']} to {schedule['maha_dasas'][-1]['end_date']}")

# Find current period (as of 2026-01-28)
current_date = datetime(2026, 1, 28)
print(f"\nCurrent Date Analysis: {current_date.strftime('%Y-%m-%d')}")
for maha_dasa in schedule['maha_dasas']:
    start = datetime.strptime(maha_dasa['start_date'], '%Y-%m-%d')
    end = datetime.strptime(maha_dasa['end_date'], '%Y-%m-%d')
    if start <= current_date < end:
        print(f"✅ Current Maha Dasa: {maha_dasa['dasa_lord']} ({maha_dasa['start_date']} to {maha_dasa['end_date']})")
        for bhukti in maha_dasa['bhuktis']:
            bhukti_start = datetime.strptime(bhukti['start_date'], '%Y-%m-%d')
            bhukti_end = datetime.strptime(bhukti['end_date'], '%Y-%m-%d')
            if bhukti_start <= current_date < bhukti_end:
                print(f"✅ Current Bhukti: {bhukti['bhukti_lord']} ({bhukti['start_date']} to {bhukti['end_date']})")
                break
        break
