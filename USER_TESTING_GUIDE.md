# Tattva API - User Testing Guide

## Quick Start - Test in Your Browser

**Easiest Method:** Use the interactive API documentation

1. Open: https://tattva-api-387275429365.us-central1.run.app/docs
2. Find the `/api/v1/profile/complete` endpoint
3. Click **"Try it out"**
4. Fill in the request body:
   ```json
   {
     "name": "Your Name",
     "birth_date": "1990-05-15",
     "birth_time": "14:30",
     "birth_place": "Mumbai"
   }
   ```
5. Click **"Execute"**
6. See your complete astrological profile!

---

## Method 1: Using cURL (Command Line)

### For Windows PowerShell:
```powershell
$body = @{
    name = "John Doe"
    birth_date = "1990-05-15"
    birth_time = "14:30"
    birth_place = "Mumbai"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete" `
  -Method Post `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json -Depth 10
```

### For Linux/Mac Terminal:
```bash
curl -X POST "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "birth_date": "1990-05-15",
    "birth_time": "14:30",
    "birth_place": "Mumbai"
  }' | jq '.'
```

---

## Method 2: Using Python

### Install Requirements:
```bash
pip install requests
```

### Test Script:
```python
import requests
import json

# API endpoint
url = "https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete"

# Your birth data
data = {
    "name": "John Doe",
    "birth_date": "1990-05-15",
    "birth_time": "14:30",
    "birth_place": "Mumbai"
}

# Make request
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    
    # Print executive summary
    print("Executive Summary:")
    print(f"Personality: {result['executive_summary']['personality_overview']}")
    print(f"Active Yogas: {result['executive_summary']['active_yogas_count']}")
    print(f"Current Dasa: {result['executive_summary']['current_dasa_planet']}")
    print(f"Life Stage: {result['executive_summary']['life_stage']}")
    
    # Print birth chart
    print("\nBirth Chart:")
    print(f"Lagna (Ascendant): {result['birth_chart']['lagna']['sign']}")
    print(f"Sun Sign: {result['birth_chart']['planets'][0]['rasi']}")
    print(f"Moon Sign: {result['birth_chart']['planets'][1]['rasi']}")
    
    # Print active yogas
    print(f"\nActive Yogas ({result['executive_summary']['active_yogas_count']}):")
    active_yogas = [y for y in result['yogas'] if y['present']]
    for yoga in active_yogas[:5]:
        print(f"  • {yoga['name']} ({yoga['nature']})")
        print(f"    {yoga['description']}")
    
    # Save full response
    with open('my_profile.json', 'w') as f:
        json.dump(result, f, indent=2)
    print("\nFull profile saved to my_profile.json")
else:
    print(f"Error {response.status_code}: {response.text}")
```

---

## Method 3: Using Postman

1. Open Postman (or download from https://postman.com)
2. Create a new **POST** request
3. URL: `https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete`
4. Headers: 
   - `Content-Type: application/json`
5. Body (select **raw** and **JSON**):
   ```json
   {
     "name": "John Doe",
     "birth_date": "1990-05-15",
     "birth_time": "14:30",
     "birth_place": "Mumbai"
   }
   ```
6. Click **Send**
7. View response in the "Body" tab

---

## Method 4: Using JavaScript/Fetch

### For Web Applications:
```javascript
async function getAstrologicalProfile() {
  const url = 'https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete';
  
  const data = {
    name: 'John Doe',
    birth_date: '1990-05-15',
    birth_time: '14:30',
    birth_place: 'Mumbai'
  };
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      const result = await response.json();
      
      console.log('Personality:', result.executive_summary.personality_overview);
      console.log('Active Yogas:', result.executive_summary.active_yogas_count);
      console.log('Lagna:', result.birth_chart.lagna.sign);
      
      return result;
    } else {
      console.error('Error:', response.status, await response.text());
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}

// Call the function
getAstrologicalProfile();
```

---

## Input Parameters

### Required Fields:
| Field | Type | Format | Example |
|-------|------|--------|---------|
| `name` | string | Any text | "John Doe" |
| `birth_date` | string | YYYY-MM-DD | "1990-05-15" |
| `birth_time` | string | HH:MM (24-hour) | "14:30" |
| `birth_place` | string | City name or "City, Country" | "Mumbai" or "London, UK" |

### Supported Cities:
✅ **Works well with major cities:**
- Mumbai, Delhi, Bangalore, Chennai (India)
- London, Edinburgh (UK)
- New York, Los Angeles, Houston, Dallas (USA)
- Singapore, Tokyo, Dubai
- Most capital cities worldwide

⚠️ **For smaller cities:** Use "City, State, Country" format or provide coordinates

---

## Sample Birth Data for Testing

### Test Case 1: Mumbai Birth
```json
{
  "name": "Test Mumbai",
  "birth_date": "1990-05-15",
  "birth_time": "14:30",
  "birth_place": "Mumbai"
}
```

### Test Case 2: London Birth
```json
{
  "name": "Test London",
  "birth_date": "1985-08-20",
  "birth_time": "10:00",
  "birth_place": "London"
}
```

### Test Case 3: New York Birth
```json
{
  "name": "Test NewYork",
  "birth_date": "1992-12-01",
  "birth_time": "15:45",
  "birth_place": "New York"
}
```

---

## Understanding the Response

### Key Sections:

1. **Executive Summary** - Quick overview with personality, yogas, dasa
2. **Birth Chart** - Lagna and 9 planets with interpretations
3. **Panchang** - Tithi, Nakshatra, Yoga calculations
4. **Dasa Periods** - Current Mahadasa and Bhukti planets
5. **Yogas** - All 21 yogas with active/inactive status
6. **Numerology** - Life path, destiny, soul urge numbers
7. **Prediction Framework** - AI-ready structured data for predictions

### Sample Response Structure:
```json
{
  "executive_summary": {
    "personality_overview": "Leo rising with Taurus Sun...",
    "active_yogas_count": 5,
    "key_strengths": "...",
    "current_dasa_planet": "Jupiter",
    "life_stage": "Youth"
  },
  "birth_chart": {
    "lagna": {
      "sign": "Leo",
      "degree": 15.5,
      "interpretation": {...}
    },
    "planets": [
      {
        "planet": "Sun",
        "longitude": 45.23,
        "rasi": "Taurus",
        "nakshatra": "Rohini",
        "pada": 2,
        "interpretation": {...}
      }
      // ... 8 more planets
    ]
  },
  "yogas": [
    {
      "name": "GajaKesari Yoga",
      "present": true,
      "nature": "Good",
      "description": "Moon and Jupiter in mutual kendras",
      "category": "Raja",
      "strength": 75
    }
    // ... 20 more yogas
  ]
  // ... more sections
}
```

---

## Troubleshooting

### Error: "Could not find location"
**Solution:** Try these formats:
- Just city name: `"Mumbai"`
- City with country: `"London, UK"`
- Add state for US cities: `"Houston, TX, USA"`

### Error: 422 Unprocessable Entity
**Solution:** Check your JSON format:
- All fields are required
- Date must be YYYY-MM-DD format
- Time must be HH:MM format (24-hour)
- Use double quotes for JSON strings

### Error: 500 Internal Server Error
**Solution:** 
- Check if location is valid
- Verify date/time formats
- Contact API support with your request details

---

## Rate Limits

Currently: **No rate limits** for testing

For production use, consider:
- Caching results for repeated requests
- Implementing client-side rate limiting
- Contact for enterprise access

---

## API Documentation

**Interactive Docs:** https://tattva-api-387275429365.us-central1.run.app/docs  
**Health Check:** https://tattva-api-387275429365.us-central1.run.app/health

### Other Available Endpoints:

| Endpoint | Description |
|----------|-------------|
| `/health` | Check API status |
| `/api/v1/profile/generate` | Generate psychic profile |
| `/api/v1/chart/planets` | Get planetary positions |
| `/api/v1/chart/panchang` | Get panchang data |
| `/api/v1/chart/dasa` | Get dasa periods |
| `/api/v1/numerology/full` | Get numerology analysis |

---

## Example: Building a Simple Web Page

```html
<!DOCTYPE html>
<html>
<head>
    <title>Tattva Astrology</title>
</head>
<body>
    <h1>Get Your Astrological Profile</h1>
    
    <form id="birthForm">
        <input type="text" id="name" placeholder="Your Name" required><br>
        <input type="date" id="birth_date" required><br>
        <input type="time" id="birth_time" required><br>
        <input type="text" id="birth_place" placeholder="Birth Place" required><br>
        <button type="submit">Get Profile</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('birthForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const data = {
                name: document.getElementById('name').value,
                birth_date: document.getElementById('birth_date').value,
                birth_time: document.getElementById('birth_time').value,
                birth_place: document.getElementById('birth_place').value
            };
            
            const response = await fetch(
                'https://tattva-api-387275429365.us-central1.run.app/api/v1/profile/complete',
                {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                }
            );
            
            const result = await response.json();
            
            document.getElementById('result').innerHTML = `
                <h2>Your Profile</h2>
                <p><strong>Personality:</strong> ${result.executive_summary.personality_overview}</p>
                <p><strong>Active Yogas:</strong> ${result.executive_summary.active_yogas_count}</p>
                <p><strong>Lagna:</strong> ${result.birth_chart.lagna.sign}</p>
            `;
        });
    </script>
</body>
</html>
```

---

## Support

- **API Issues:** Check logs at https://console.cloud.google.com/run?project=tattva-api-8461
- **Questions:** Create issue on GitHub
- **Feature Requests:** Submit pull request

---

## Next Steps

1. ✅ Test the API with your birth data
2. ✅ Review the complete response
3. ✅ Integrate into your application
4. ✅ Build prediction logic on top of the data
5. ✅ Share feedback for improvements

**Happy Testing!** 🎉
