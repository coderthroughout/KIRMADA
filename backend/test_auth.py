#!/usr/bin/env python3
"""
Auth endpoint test script
"""

import requests
import json

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Auth endpoints...")
    
    # Test auth register endpoint
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data)
        print(f"Register endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        elif response.status_code == 400:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Register endpoint error: {e}")
    
    # Test auth token endpoint
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{base_url}/api/v1/auth/token", data=login_data)
        print(f"Token endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            return response.json().get("access_token")
        elif response.status_code == 401:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Token endpoint error: {e}")
    
    return None

if __name__ == "__main__":
    token = test_auth_endpoints()
    if token:
        print(f"\n✅ Authentication successful! Token: {token[:20]}...")
    else:
        print("\n❌ Authentication failed") 