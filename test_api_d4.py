import requests
import json

url = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"
data = {
    "name": "Test User",
    "birth_date": "1991-05-04",
    "birth_time": "10:50",
    "birth_place": "Vellore"
}

print("\n=== D4 Chaturthamsa Chart ===")
print(f"Birth Date: {data['birth_date']}")
print(f"Birth Time: {data['birth_time']}")
print(f"Birth Place: {data['birth_place']}\n")

response = requests.post(url, json=data)
result = response.json()

print(f"API Status: {response.status_code}")

if 'planets' in result['birth_chart']:
    # Collect planets by D4 house
    d4_houses = {i: [] for i in range(1, 13)}
    
    print(f"\n{'='*70}")
    print(f"D4 CHATURTHAMSA CHART (Property/Fortune)")
    print(f"{'='*70}\n")
    
    # First show planetary positions
    print(f"Planetary Positions:\n")
    for planet_data in result['birth_chart']['planets']:
        planet = planet_data['planet']
        rasi = planet_data['rasi']
        long = planet_data['longitude']
        d4 = planet_data.get('d4_chaturthamsa', 'N/A')
        d4_num = planet_data.get('d4_num', 'N/A')
        
        if d4_num != 'N/A':
            d4_houses[d4_num].append(planet)
        
        deg_in_sign = long % 30
        print(f"{planet:10} | D1: {rasi:20} {deg_in_sign:5.2f}° → D4: {d4:20} (House {d4_num:2})")
    
    # Now display as a chart
    print(f"\n{'='*70}")
    print(f"D4 CHART LAYOUT (North Indian Style)")
    print(f"{'='*70}\n")
    
    # North Indian chart layout
    houses_layout = [
        [12, 1, 2, 3],
        [11, None, None, 4],
        [10, None, None, 5],
        [9, 8, 7, 6]
    ]
    
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    for row in houses_layout:
        line1 = []
        line2 = []
        line3 = []
        
        for house_num in row:
            if house_num is None:
                line1.append("               ")
                line2.append("               ")
                line3.append("               ")
            else:
                sign_name = signs[house_num - 1][:3]
                planets_in_house = d4_houses[house_num]
                
                # Format planets (max 2 per line)
                if len(planets_in_house) == 0:
                    planet_str1 = ""
                    planet_str2 = ""
                elif len(planets_in_house) == 1:
                    planet_str1 = planets_in_house[0][:3]
                    planet_str2 = ""
                elif len(planets_in_house) == 2:
                    planet_str1 = planets_in_house[0][:3]
                    planet_str2 = planets_in_house[1][:3]
                else:
                    planet_str1 = planets_in_house[0][:3] + "," + planets_in_house[1][:3]
                    planet_str2 = ",".join([p[:3] for p in planets_in_house[2:]])
                
                line1.append(f" {sign_name:^13}")
                line2.append(f" {planet_str1:^13}")
                line3.append(f" {planet_str2:^13}")
        
        print("┌" + "─"*15 + "┬" + "─"*15 + "┬" + "─"*15 + "┬" + "─"*15 + "┐")
        print("│" + "│".join(line1) + "│")
        print("│" + "│".join(line2) + "│")
        print("│" + "│".join(line3) + "│")
    
    print("└" + "─"*15 + "┴" + "─"*15 + "┴" + "─"*15 + "┴" + "─"*15 + "┘")
    
else:
    print("\nNo 'planets' key found!")
    print(json.dumps(result, indent=2))
