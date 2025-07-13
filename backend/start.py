#!/usr/bin/env python3
"""
Startup script for Aztec Protocol Backend
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.logging import setup_logging

def main():
    """Start the Aztec Protocol Backend"""
    
    # Setup logging
    setup_logging()
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    print("🚀 Starting Aztec Protocol Backend...")
    print(f"📍 Host: {settings.HOST}")
    print(f"🔌 Port: {settings.PORT}")
    print(f"🔧 Debug: {settings.DEBUG}")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🔗 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"📈 Health Check: http://{settings.HOST}:{settings.PORT}/health")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main() 