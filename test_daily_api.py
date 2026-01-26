#!/usr/bin/env python3
"""
Test script for daily_api.py
Runs the API server and makes a test request for Vellore birth chart
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

def test_daily_prediction():
    """Test daily prediction API with Vellore birth data."""
    
    # API endpoint (daily_api runs on port 8080)
    url = "http://127.0.0.1:8080/predict"
    
    # Birth data for Vellore
    payload = {
        "user_id": "test_vellore_user",
        "birth_date": "1991-04-05",
        "birth_time": "10:50",
        "birth_place": "Vellore, India",
        "prediction_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    print("=" * 80)
    print("Testing VedAstroPy Daily Prediction API")
    print("=" * 80)
    print()
    print(f"URL: {url}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))
    print()
    
    try:
        # Make POST request
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("=" * 80)
            print("DAILY PREDICTION RESPONSE")
            print("=" * 80)
            print()
            
            # Birth Chart Info
            if "birth_chart" in data:
                bc = data["birth_chart"]
                print("BIRTH CHART:")
                lagna_deg = bc.get('lagna_degree')
                lagna_str = f"{lagna_deg:.2f}°" if lagna_deg is not None else "N/A"
                print(f"  Lagna: {bc.get('lagna_sign')} ({lagna_str})")
                print(f"  Nakshatra: {bc.get('birth_nakshatra')} Pada {bc.get('nakshatra_pada')}")
                print()
            
            # Prediction Info
            if "prediction_info" in data:
                pi = data["prediction_info"]
                print("PREDICTION:")
                print(f"  Date: {pi.get('prediction_date')}")
                print()
            
            # Mood
            if "mood" in data:
                mood = data["mood"]
                print("MOOD:")
                print(f"  Moon in House {mood.get('house')}")
                print(f"  Name: {mood.get('name')}")
                print(f"  {mood.get('interpretation')}")
                print(f"  {mood.get('description')}")
                print()
            
            # Fuel
            if "fuel" in data:
                fuel = data["fuel"]
                print("FUEL (Energy Level):")
                print(f"  Sun in House {fuel.get('house')}")
                print(f"  Name: {fuel.get('name')}")
                print(f"  Level: {fuel.get('level')}")
                print(f"  {fuel.get('description')}")
                print()
            
            # Luck
            if "luck" in data:
                luck = data["luck"]
                print("LUCK (Tara Bala):")
                print(f"  Tara: {luck.get('tara_name')} (#{luck.get('tara_number')})")
                print(f"  Status: {luck.get('status')}")
                print(f"  {luck.get('description')}")
                print()
            
            # Full JSON response
            print("=" * 80)
            print("FULL RESPONSE JSON:")
            print("=" * 80)
            print(json.dumps(data, indent=2))
            
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Make sure the daily_api.py server is running:")
        print("  python daily_api.py")
        print()
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_daily_prediction()
