#!/usr/bin/env python3
"""Update test file to include new yogas in stats dictionary"""

with open('test_yogas_with_real_data.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the yogas_stats dictionary and replace it
in_dict = False
dict_start = None
dict_end = None

for i, line in enumerate(lines):
    if 'yogas_stats = {' in line:
        in_dict = True
        dict_start = i
    elif in_dict and line.strip() == '}':
        dict_end = i
        break

if dict_start is None or dict_end is None:
    print("ERROR: Could not find yogas_stats dictionary")
    exit(1)

# Create new dictionary lines
new_dict_lines = [
    "    yogas_stats = {\n",
    "        'GajaKesari Yoga': 0,\n",
    "        'Sakata Yoga': 0,  # NEW: Malefic opposite of GajaKesari\n",
    "        'Sunapha Yoga': 0,\n",
    "        'Anapha Yoga': 0,\n",
    "        'Dhurdhura Yoga': 0,\n",
    "        'Bhadra Yoga': 0,\n",
    "        'Hamsa Yoga': 0,\n",
    "        'Malavya Yoga': 0,\n",
    "        'Ruchaka Yoga': 0,\n",
    "        'Sasha Yoga': 0,\n",
    "        'Amala Yoga': 0,\n",
    "        'Kemadruma Yoga': 0,\n",
    "        'Lakshmi Yoga': 0,\n",
    "        'Chatussagara Yoga': 0,  # NEW: All 4 kendras occupied\n",
    "        'Vasumathi Yoga': 0,  # NEW: Benefics in upachaya\n",
    "        'Parvata Yoga': 0,  # NEW: Mountain of success\n",
    "        'Raja Yoga (Basic)': 0,\n",
    "        'Neechabhanga Raja Yoga': 0,\n",
    "        'Harsha Yoga': 0,\n",
    "        'Sarala Yoga': 0,\n",
    "        'Vimala Yoga': 0\n",
    "    }\n"
]

# Replace the old dictionary
new_lines = lines[:dict_start] + new_dict_lines + lines[dict_end+1:]

# Write back
with open('test_yogas_with_real_data.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: Updated test file with 4 new yoga entries (21 total)")
