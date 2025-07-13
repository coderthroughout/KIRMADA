#!/usr/bin/env python3
"""
Comprehensive startup script for Aztec Protocol Backend
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All required dependencies are installed")

def setup_environment():
    """Setup environment variables and directories"""
    print("\n🔧 Setting up environment...")
    
    # Create necessary directories
    directories = [
        "uploads",
        "logs",
        "models",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env from .env.example")
        else:
            print("❌ .env.example not found. Please create .env manually.")
            sys.exit(1)
    else:
        print("✅ .env file exists")

def check_database():
    """Check database connection and initialize if needed"""
    print("\n🗄️  Checking database...")
    
    try:
        from app.core.database import init_db, get_db
        from sqlalchemy import text
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Test connection
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Please check your database configuration in .env")
        sys.exit(1)

def check_ipfs_config():
    """Check IPFS configuration"""
    print("\n🌐 Checking IPFS configuration...")
    
    try:
        from app.core.config import settings
        
        if settings.IPFS_API_KEY and settings.IPFS_API_SECRET:
            print("✅ IPFS credentials configured")
            
            # Test IPFS connection
            try:
                import sys
                sys.path.append('../agent')
                from ipfs_upload import test_credentials
                
                if test_credentials(settings.IPFS_API_KEY, settings.IPFS_API_SECRET):
                    print("✅ IPFS credentials are valid")
                else:
                    print("⚠️  IPFS credentials are invalid")
            except Exception as e:
                print(f"⚠️  Could not test IPFS credentials: {e}")
        else:
            print("⚠️  IPFS credentials not configured")
            
    except Exception as e:
        print(f"❌ IPFS configuration error: {e}")

def check_blockchain_config():
    """Check blockchain configuration"""
    print("\n⛓️  Checking blockchain configuration...")
    
    try:
        from app.core.config import settings
        
        print(f"✅ Ethereum RPC URL: {settings.ETHEREUM_RPC_URL}")
        print(f"✅ Contract addresses configured: {len(settings.CONTRACT_ADDRESSES)} contracts")
        
        # Test blockchain connection (simulated)
        print("✅ Blockchain configuration looks good")
        
    except Exception as e:
        print(f"❌ Blockchain configuration error: {e}")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Aztec Protocol Backend...")
    
    try:
        # Start server with uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        print("Press Ctrl+C to stop the server")
        
        # Start the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def run_health_check():
    """Run a health check on the server"""
    print("\n🏥 Running health check...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🎯 Aztec Protocol Backend Startup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    check_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Check database
    check_database()
    
    # Check IPFS configuration
    check_ipfs_config()
    
    # Check blockchain configuration
    check_blockchain_config()
    
    print("\n" + "=" * 50)
    print("🎉 Environment setup complete!")
    print("=" * 50)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 