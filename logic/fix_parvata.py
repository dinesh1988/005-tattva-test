#!/usr/bin/env python3
"""Fix the import in Parvata Yoga function"""

with open('yogas.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the wrong import
content = content.replace('from .avastha import is_in_dignity', 
                          'from .avastha import get_dignity_status')

# Replace the function call is_in_dignity with proper get_dignity_status usage
# The usage is: dignity_status, dignity_score = get_dignity_status(lord.name, lord_long)
# and check if dignity_score >= 3 (own sign or better)

# Find and replace the is_in_dignity(lord, time) calls
old_usage = """                # Check dignity (own sign, exaltation, or moolatrikona)
                in_dignity = is_in_dignity(lord, time)
                
                if in_dignity:"""

new_usage = """                # Check dignity (own sign, exaltation, or moolatrikona)
                dignity_status, dignity_score = get_dignity_status(lord.name, lord_long)
                # Dignity: Exalted=5, Moolatrikona=4, Own=3 (all considered good)
                in_dignity = dignity_score >= 3
                
                if in_dignity:"""

content = content.replace(old_usage, new_usage)

with open('yogas.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: Fixed Parvata Yoga import and usage")
