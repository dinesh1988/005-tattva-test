"""
VedAstroPy API Server Runner
============================
Run this script to start the API server.

Usage: python run_api.py
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from api.main import app
    
    print("=" * 50)
    print("VedAstroPy Psychic Profile API")
    print("=" * 50)
    print("Starting server...")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("ReDoc:    http://127.0.0.1:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000,
        log_level="info"
    )
