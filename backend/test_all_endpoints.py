#!/usr/bin/env python3
"""
Comprehensive API endpoint test script
"""

import requests
import json

def test_all_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Aztec Protocol Backend - All Endpoints")
    print("=" * 60)
    
    # First, get a token
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{base_url}/api/v1/auth/token", data=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return
    
    # Test all endpoints
    endpoints = [
        ("GET", "/api/v1/agents", "Agents"),
        ("GET", "/api/v1/models", "Models"), 
        ("GET", "/api/v1/proofs", "Proofs"),
        ("GET", "/api/v1/rounds", "Rounds"),
        ("GET", "/api/v1/blockchain/status", "Blockchain Status"),
        ("GET", "/api/v1/blockchain/contracts", "Contract Addresses"),
        ("GET", "/api/v1/ipfs/status", "IPFS Status"),
    ]
    
    for method, endpoint, name in endpoints:
        try:
            response = requests.request(method, f"{base_url}{endpoint}", headers=headers)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {name}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   📊 Found {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   📊 Data received")
        except Exception as e:
            print(f"❌ {name} error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print(f"📚 API Documentation: {base_url}/docs")
    print(f"🔗 Health Check: {base_url}/health")

if __name__ == "__main__":
    test_all_endpoints() 