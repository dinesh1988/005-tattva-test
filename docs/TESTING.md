# Testing and Validation Guide

This guide explains how to test and validate yoga implementations using VedAstro's datasets.

## Overview

VedAstro provides **15,000+ famous people birth records** that can be used to validate astrological calculations. This real-world data ensures that yoga detection logic is accurate and matches expected patterns.

## Available Test Files

### 1. test_yogas_simple.py
**Purpose**: Manual calculation test with hardcoded birth data  
**Use When**: 
- Testing basic planetary calculations
- Debugging specific yoga logic
- Learning how yogas are calculated step-by-step

**Run**:
```bash
cd VedAstroPy
python tests/test_yogas_simple.py
```

**What it tests**:
- Planetary longitude calculations
- House positions from lagna
- Kendra (angular house) detection
- Yoga conditions (GajaKesari, Pancha Mahapurusha)

**Example Output**:
```
PLANETARY POSITIONS:
Lagna:   Aquarius     at 317.68°
Moon:    Cancer       at 110.13°
Jupiter: Libra        at 191.49°

YOGA DETECTION:
✓ GAJAKESARI YOGA PRESENT (Jupiter in 4th from Moon)
✓ SASHA YOGA PRESENT (Saturn in kendra in own sign)
```

### 2. test_yogas_with_real_data.py
**Purpose**: Batch validation using 15k famous people dataset  
**Use When**:
- Validating yoga implementations against historical data
- Testing statistical frequency of yogas
- Finding notable examples of yogas in action

**Run**:
```bash
cd VedAstroPy
python tests/test_yogas_with_real_data.py
```

**What it validates**:
- Yoga occurrence rates match expected patterns
- Famous/successful people have appropriate yogas
- Calculations work across different timezones and locations
- Error handling with diverse birth data formats

**Example Output**:
```
A. J. Cronin (Cardross, United Kingdom)
   Found 4 yoga(s):
   ✓ GajaKesari Yoga - Jupiter in house 10 from Moon
   ✓ Hamsa Yoga - Jupiter in Cancer in house 1
   ✓ Ruchaka Yoga - Mars in Aries in house 10
   ✓ Sasha Yoga - Saturn in Libra in house 4

VALIDATION SUMMARY:
Total people tested: 20
People with yogas: 10 (50%)
Errors: 0

📊 YOGA FREQUENCY:
GajaKesari Yoga: 30% (most common - wealth/wisdom indicator)
Malavya Yoga: 25% (luxury/beauty - Venus)
```

## Available Datasets

### 1. PersonList-15k.csv
**Location**: `HuggingFace/PersonList-15k.csv`  
**Size**: 15,000+ records  
**Format**:
```csv
RowKey,BirthTime,Gender,Name,Notes
A.A.Gill1954,"{
  ""StdTime"": ""19:55 26/06/1954 +01:00"",
  ""Location"": {
    ""Name"": ""Edinburgh, United Kingdom"",
    ""Longitude"": ""-3.188267"",
    ""Latitude"": ""55.953251""
  }
}",Male,A. A. Gill,British journalist
```

**Also available on**: [HuggingFace](https://huggingface.co/datasets/vedastro-org/15000-Famous-People-Birth-Date-Location)

### 2. MarriageInfoDataset.csv
**Location**: `HuggingFace/MarriageInfoDataset.csv`  
**Purpose**: Validate relationship/marriage yogas  
**Also available on**: [HuggingFace](https://huggingface.co/datasets/vedastro-org/15000-Famous-People-Marriage-Divorce-Info)

### 3. alpaca_bvraman_horoscope_data.json
**Location**: `HuggingFace/alpaca_bvraman_horoscope_data.json`  
**Size**: 3,087 entries  
**Purpose**: BV Raman's interpretations for AI training and validation

## How to Add Tests for New Yogas

### Step 1: Add Yoga Detection Function
In `VedAstroPy/logic/yogas.py`:
```python
def check_new_yoga(time: AstroTime) -> Yoga:
    """
    Detect NewYoga - description of what it is.
    
    Condition: Specific planetary combination
    Effect: Result/impact of this yoga
    """
    # Get planetary positions
    planet_long = calculate.get_planet_longitude(Planet.Jupiter, time)
    lagna_long = calculate.get_lagnam(time)
    
    # Calculate yoga condition
    occurring = # your logic here
    
    return Yoga(
        name="New Yoga",
        nature=YogaNature.GOOD,
        occurring=occurring,
        description="Effect of this yoga",
        condition="Condition that forms this yoga"
    )
```

### Step 2: Add to test_yogas_simple.py
Add manual check:
```python
print("\n7. New Yoga Check:")
# Add planetary position checks
# Calculate yoga conditions
# Print results
```

### Step 3: Add to test_yogas_with_real_data.py
Add to `check_yogas_for_person()`:
```python
# 7. New Yoga
new_yoga_condition = # calculate here
if new_yoga_condition:
    yogas_found.append({
        'name': 'New Yoga',
        'condition': f'Specific condition met',
        'effect': 'Impact description'
    })
```

Update `yogas_stats` dictionary:
```python
yogas_stats = {
    # ... existing yogas
    'New Yoga': 0
}
```

### Step 4: Run Tests
```bash
# Test basic calculations
python tests/test_yogas_simple.py

# Validate with real data (test 20 people)
python tests/test_yogas_with_real_data.py
```

### Step 5: Analyze Results
Expected patterns:
- **Rare yogas** (< 5%): Very specific conditions (e.g., Ruchaka)
- **Common yogas** (20-40%): Broader conditions (e.g., GajaKesari)
- **Universal yogas** (> 50%): Basic combinations

If frequency is unexpected:
1. Check calculation logic for errors
2. Verify sign/house calculations
3. Compare with C# implementation in `Library/Logic/Calculate/Muhurtha.cs`
4. Cross-reference with XML definition in `Library/XMLData/HoroscopeDataList.xml`

## Validation Best Practices

### 1. Start Small
Test with 10-20 records first:
```python
for i, row in enumerate(reader):
    if i >= 20:  # Small sample
        break
```

### 2. Use Known Examples
Test against famous people where yogas are documented:
- **A. J. Cronin**: Scottish novelist (4 yogas detected)
- **Mahatma Gandhi**: Expected to have Raja yogas
- **Albert Einstein**: Expected to have Budhaditya yoga

### 3. Check Error Handling
```python
if yogas is None:
    errors += 1
    print(f"✗ Error: {location_or_error}")
```

### 4. Statistical Validation
```python
# Calculate frequency
percentage = (count / total_tested) * 100

# Flag anomalies
if percentage > 80 or percentage < 1:
    print(f"⚠️ Unusual frequency: {percentage}%")
```

### 5. Cross-Reference Sources
For each yoga implementation:
1. Read XML definition: `Library/XMLData/HoroscopeDataList.xml`
2. Study C# logic: `Library/Logic/Calculate/Muhurtha.cs`
3. Consult BV Raman books referenced in code
4. Validate with real birth charts

## Test Data Format

### VedAstro Time Format
```json
{
  "StdTime": "19:55 26/06/1954 +01:00",
  "Location": {
    "Name": "Edinburgh, United Kingdom",
    "Longitude": "-3.188267",
    "Latitude": "55.953251"
  }
}
```

### AstroTime Object Creation
```python
from logic.time import AstroTime
from datetime import datetime
import pytz

# Parse time string
dt = datetime.strptime("19:55 26/06/1954", "%H:%M %d/%m/%Y")

# Add timezone
tz = pytz.FixedOffset(60)  # +01:00
dt = tz.localize(dt)

# Create AstroTime
time = AstroTime(dt, 55.953251, -3.188267)
```

## Interpreting Test Results

### Success Indicators
✅ **No errors** during calculation  
✅ **50-70% of famous people** have at least one yoga  
✅ **GajaKesari most common** (wealth/success indicator)  
✅ **Multiple yogas** in highly successful individuals  
✅ **Rare yogas** (< 10%) have specific conditions

### Red Flags
🚩 **100% occurrence** - Logic too broad  
🚩 **0% occurrence** - Logic too restrictive or broken  
🚩 **Parse errors** - Time format handling issue  
🚩 **Calculation exceptions** - Missing planetary data or invalid coordinates  

## Continuous Validation

### When to Re-run Tests
- After adding new yoga implementations
- After modifying planetary calculation logic
- After updating avastha/dignity data (EXALTATION, OWN_SIGNS)
- Before committing changes to Git
- Before publishing to PyPI

### Regression Testing
Keep baseline results:
```python
# Save first successful run
baseline = {
    'GajaKesari': 30.0,
    'Hamsa': 15.0,
    'Malavya': 25.0,
    # ...
}

# Compare future runs
if abs(current_percentage - baseline[yoga_name]) > 5:
    print(f"⚠️ Deviation detected: {yoga_name}")
```

## Example: Complete Test Workflow

```bash
# 1. Implement new yoga in yogas.py
code VedAstroPy/logic/yogas.py

# 2. Add manual test
code VedAstroPy/tests/test_yogas_simple.py

# 3. Run basic test
python tests/test_yogas_simple.py

# 4. Add to batch validation
code VedAstroPy/tests/test_yogas_with_real_data.py

# 5. Run validation (small sample)
python tests/test_yogas_with_real_data.py

# 6. If results look good, test larger sample
# Edit test_count = 100 in test file
python tests/test_yogas_with_real_data.py

# 7. Update ROADMAP.md with new yoga count
code VedAstroPy/ROADMAP.md

# 8. Commit changes
git add .
git commit -m "feat: add NewYoga implementation with validation"
```

## Troubleshooting

### Issue: "Dataset not found"
**Solution**: Ensure you're in VedAstro-master directory
```bash
ls HuggingFace/PersonList-15k.csv
```

### Issue: "Parse error" or "Time format error"
**Solution**: Check time string format, handle edge cases
```python
try:
    time, location = parse_vedastro_time(birth_time_json)
except Exception as e:
    return None, f"Error: {e}"
```

### Issue: Yoga frequency seems wrong
**Solution**: 
1. Test with known charts manually
2. Compare with C# implementation
3. Check sign number calculations (0-11 vs 1-12)
4. Verify kendra house calculation

### Issue: Slow test execution
**Solution**: Reduce sample size or parallelize
```python
test_count = 10  # Start small
# Later: Use multiprocessing for large batches
```

## Further Resources

- **C# Reference**: `Library/Logic/Calculate/Muhurtha.cs` - Original yoga calculations
- **Yoga Definitions**: `Library/XMLData/HoroscopeDataList.xml` - Yoga metadata
- **Book Reference**: Hindu Predictive Astrology by Dr. B.V. Raman (pg. 254+)
- **Dataset**: [VedAstro HuggingFace](https://huggingface.co/vedastro-org)

## Summary

Testing ensures yoga implementations are:
1. **Accurate** - Match astrological principles
2. **Reliable** - Work with diverse birth data
3. **Validated** - Confirmed with historical records
4. **Maintainable** - Easy to verify after changes

By using real birth data from 15,000+ famous people, we can confidently validate that our yoga detection algorithms work correctly and match real-world patterns of success, fame, and life events.
