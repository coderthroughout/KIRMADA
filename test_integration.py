#!/usr/bin/env python3
"""
Test frontend-backend integration
"""

import requests
import time

def test_integration():
    """Test if frontend and backend are properly connected"""
    print("🔗 Testing Frontend-Backend Integration...")
    print("=" * 50)
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: Running on http://localhost:8000")
        else:
            print(f"❌ Backend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend: Not accessible - {e}")
        return False
    
    # Test frontend accessibility
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: Running on http://localhost:3000")
        else:
            print(f"❌ Frontend: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend: Not accessible - {e}")
        return False
    
    # Test API endpoints
    try:
        response = requests.get("http://localhost:8000/api/v1/", timeout=5)
        if response.status_code == 200:
            print("✅ API: Endpoints accessible")
        else:
            print(f"❌ API: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API: Not accessible - {e}")
        return False
    
    print("\n🎉 Integration Test Results:")
    print("✅ Backend: http://localhost:8000")
    print("✅ Frontend: http://localhost:3000")
    print("✅ API: http://localhost:8000/api/v1/")
    print("\n📱 You can now:")
    print("   • Open http://localhost:3000 in your browser")
    print("   • Register/login through the authentication system")
    print("   • Browse all pages and use the full application")
    print("   • View real-time data from the backend")
    print("   • Access training results and analytics")
    
    return True

if __name__ == "__main__":
    test_integration() 