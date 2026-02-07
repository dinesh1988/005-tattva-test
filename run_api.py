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

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print("=" * 50)
    print("VedAstroPy Psychic Profile API")
    print("=" * 50)
    print("Starting server...")
    print(f"API Docs: http://{host}:{port}/docs")
    print(f"ReDoc:    http://{host}:{port}/redoc")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host=host,
        port=port,
        log_level="info"
    )
